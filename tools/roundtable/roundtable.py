#!/usr/bin/env python3
"""
roundtable -- a live multi-way room: several AIs (Claude, Gemini, GPT, ...) + humans.

The AIs run FREE, bouncing off each other. The room pauses for the humans when:
  (a) a human types (incl. natural "stop"/"pause"/"wait"),
  (b) an AI ends its turn asking for human input (it emits @HUMANS),
  (c) one AI would just talk to itself (others erroring/absent), or
  (d) a backstop cap of consecutive AI turns is hit.
Everyone opens the same URL and can read + interject. A human message resumes the AIs.

An AI joins only if its API key is set. Add models by appending to the AIS list.

Models default to CHEAP; switch live, in-room (any AI name -- claude / gemini / gpt):
  /heavy  /cheap                      (all AIs)
  /claude heavy   /gemini cheap       (one AI's tier)
  /gpt use <model-id>                 (one AI, any model)
  /claude persona <text>              (re-role an AI live -- "be a ruthless critic")
  /summary                            (crystallize the decision into the transcript)
  /pause  /go  /help

Every message is written to transcript-*.md so you can hand the outcome to a coding
agent ("read transcript-X.md and implement what we decided").

Customize (all via .env -- no code changes -- unless noted):
  * Personalities  -> CLAUDE_PERSONA / GEMINI_PERSONA / OPENAI_PERSONA. Make them warm,
    snarky, a debate coach, a devil's advocate -- whatever you like.
  * Models & level -> <AI>_CHEAP / <AI>_HEAVY set the two model ids; <AI>_TIER sets the
    starting level. Live: the top-bar dropdown, or /<ai> use <model-id>.
  * In or out      -> the top-bar checkbox adds/removes an AI mid-conversation.
  * Add an AI      -> append to the AIS list below (name, key env-var, provider =
    anthropic|gemini|openai, cheap/heavy model ids, persona). A brand-new provider just
    needs a branch in call_model(). It joins automatically once its key is set.
  * Pace & cost    -> TURN_DELAY (seconds between AI turns), BACKSTOP (auto-pause after
    N AI turns with no human).
  * The look       -> edit static/style.css (colors, the roster pills) and refresh.
  * Access         -> ROOM_CODE; reach it over your LAN, an ngrok URL, or a Tailscale IP.

Run:
  pip install -r requirements.txt
  cp .env.example .env   # then add your keys + a room code
  python roundtable.py
  # open http://localhost:5005   (share via ngrok, or a Tailscale IP)
"""
import os, time, json, threading, queue, datetime
from flask import Flask, request, Response, jsonify

try:
    from dotenv import load_dotenv; load_dotenv()
except Exception:
    pass

def env(k, d=None): return os.environ.get(k, d)

# ---------------- participants ----------------
AIS = [
    {"name": "Claude", "key": "ANTHROPIC_API_KEY", "provider": "anthropic",
     "cheap": env("CLAUDE_CHEAP", "claude-sonnet-4-6"), "heavy": env("CLAUDE_HEAVY", "claude-opus-4-8"),
     "persona": env("CLAUDE_PERSONA", "You are Claude. Think clearly, synthesize, and propose.")},
    {"name": "Gemini", "key": "GEMINI_API_KEY", "provider": "gemini",
     "cheap": env("GEMINI_CHEAP", "gemini-2.5-flash"), "heavy": env("GEMINI_HEAVY", "gemini-2.5-pro"),
     "persona": env("GEMINI_PERSONA", "You are Gemini. Bring a curious, independent angle; stay warm and constructive.")},
    {"name": "GPT", "key": "OPENAI_API_KEY", "provider": "openai",
     "cheap": env("OPENAI_CHEAP", "gpt-4o-mini"), "heavy": env("OPENAI_HEAVY", "gpt-4o"),
     "persona": env("OPENAI_PERSONA", "You are GPT. Be pragmatic and clear; find the through-line and the next step.")},
]
AI = {a["name"]: a for a in AIS}
CMD2AI = {"/" + a["name"].lower(): a["name"] for a in AIS}; CMD2AI["/chatgpt"] = "GPT"
tier     = {a["name"]: env(a["name"].upper() + "_TIER", "cheap") for a in AIS}
override = {a["name"]: None for a in AIS}
enabled  = {a["name"]: True for a in AIS}   # in the conversation? (toggled live via the panel)

ROOM_CODE  = env("ROOM_CODE", "roundtable")     # CHANGE THIS
TURN_DELAY = float(env("TURN_DELAY", "3"))
BACKSTOP   = int(env("BACKSTOP", "20"))
PORT       = int(env("PORT", "5005"))
ASK_SIGNAL = "@HUMANS"
STOP_WORDS = ("stop", "pause", "wait", "hold on", "hold up", "quiet", "enough", "halt", "shush")

def active_ais():
    return [a["name"] for a in AIS if os.environ.get(a["key"]) and enabled.get(a["name"], True)]

def common_rules(who):
    others = ", ".join(n for n in active_ais() if n != who) or "the others"
    return ("\n\nThis is a LIVE group room with other AIs (" + others + ") and humans. "
            "Keep each turn conversational and SHORT -- a few sentences, ~120 words max, never an essay. "
            "Address people by name; have a real back-and-forth (agree, disagree, build). "
            f"When you genuinely need a human to decide, weigh in, or unblock, END your message with '{ASK_SIGNAL}' "
            "on its own line -- the room pauses and waits for them. Use it sparingly.")

TRANSCRIPT = env("TRANSCRIPT") or f"transcript-{datetime.datetime.now():%Y%m%d-%H%M%S}.md"

# ---------------- shared state ----------------
lock = threading.Lock()
conversation = []
subscribers = []
paused = True
turn_idx = 0
consec_ai = 0
last_real_speaker = None    # last AI that actually spoke (monologue guard)

def broadcast(ev):
    for q in list(subscribers):
        try: q.put_nowait(ev)
        except Exception:
            try: subscribers.remove(q)
            except Exception: pass

def add(name, text, kind="msg"):
    m = {"name": name, "text": text, "kind": kind, "t": time.time()}
    with lock: conversation.append(m)
    broadcast(m)
    try:
        with open(TRANSCRIPT, "a", encoding="utf-8") as f:
            stamp = datetime.datetime.now().strftime("%H:%M")
            f.write((f"`{stamp}` **{name}:** {text}\n\n") if kind == "msg" else (f"_{text}_\n\n"))
    except Exception:
        pass

# ---------------- presence (who's in the room) ----------------
present = {}; joined_at = {}; left_at = {}
plock = threading.Lock()
JOIN_BOLD = 6; LEFT_LINGER = 60
_roster_sig = [None]

def roster():
    now = time.time()
    ais = []
    for a in AIS:
        haskey = bool(os.environ.get(a["key"]))
        model = override.get(a["name"]) or AI[a["name"]][tier[a["name"]]]
        ais.append({"name": a["name"], "hasKey": haskey, "enabled": enabled.get(a["name"], True),
                    "tier": tier[a["name"]], "model": model,
                    "on": haskey and enabled.get(a["name"], True)})
    humans = []
    with plock:
        for n in list(present):
            humans.append({"name": n, "status": "joined" if now - joined_at.get(n, 0) < JOIN_BOLD else "here"})
        for n, t in list(left_at.items()):
            if now - t < LEFT_LINGER: humans.append({"name": n, "status": "left"})
            else: left_at.pop(n, None)
    return {"ais": ais, "humans": humans}

def broadcast_presence(force=False):
    r = roster(); sig = json.dumps(r, sort_keys=True)
    if force or sig != _roster_sig[0]:
        _roster_sig[0] = sig
        broadcast({"kind": "roster", "ais": r["ais"], "humans": r["humans"]})

def presence_join(name):
    with plock:
        present[name] = present.get(name, 0) + 1
        if present[name] == 1: joined_at[name] = time.time(); left_at.pop(name, None)
    broadcast_presence(force=True)

def presence_leave(name):
    with plock:
        present[name] = max(0, present.get(name, 1) - 1)
        if present[name] == 0: present.pop(name, None); left_at[name] = time.time(); joined_at.pop(name, None)
    broadcast_presence(force=True)

def presence_sweeper():
    while True:
        time.sleep(3); broadcast_presence()
threading.Thread(target=presence_sweeper, daemon=True).start()

# ---------------- model calls (clients cached + reused) ----------------
_clients = {}
def get_client(provider, key):
    c = _clients.get(provider)
    if c is None:
        if provider == "anthropic":
            from anthropic import Anthropic; c = Anthropic(api_key=key)
        elif provider == "gemini":
            from google import genai; c = genai.Client(api_key=key)
        elif provider == "openai":
            from openai import OpenAI; c = OpenAI(api_key=key)
        _clients[provider] = c
    return c

def call_model(provider, key_env, model, system, user):
    c = get_client(provider, os.environ[key_env])
    if provider == "anthropic":
        r = c.messages.create(model=model, max_tokens=500, system=system,
                              messages=[{"role": "user", "content": user}])
        return "".join(b.text for b in r.content if getattr(b, "type", "") == "text").strip()
    if provider == "gemini":
        r = c.models.generate_content(model=model, contents=system + "\n\n" + user)
        return (getattr(r, "text", "") or "").strip()
    if provider == "openai":
        r = c.chat.completions.create(model=model, max_tokens=500,
                  messages=[{"role": "system", "content": system}, {"role": "user", "content": user}])
        return (r.choices[0].message.content or "").strip()
    return f"[unknown provider {provider}]"

def transcript_text():
    with lock:
        return "\n\n".join(f"{m['name']}: {m['text']}" for m in conversation if m["kind"] == "msg")

def model_for(who): return override[who] or AI[who][tier[who]]

def ai_turn(who, extra=""):
    a = AI[who]
    system = a["persona"] + common_rules(who)
    user = (transcript_text() or "(no messages yet -- open the discussion)") + \
           f"\n\n[It's your turn, {who}. {extra or 'Respond to the conversation above.'}]"
    for attempt in range(2):
        try:
            return call_model(a["provider"], a["key"], model_for(who), system, user)
        except Exception as e:
            es = str(e)
            if attempt == 0 and ("503" in es or "UNAVAILABLE" in es or "overloaded" in es.lower() or "closed" in es.lower()):
                _clients.pop(a["provider"], None)   # rebuild a stale/closed client, then retry
                time.sleep(3); continue
            return f"[error calling {who} ({model_for(who)}): {e}]"

# ---------------- the free-running loop ----------------
def ai_loop():
    global paused, turn_idx, consec_ai, last_real_speaker
    err_streak = 0
    while True:
        act = active_ais()
        if paused or not act:
            time.sleep(0.4); continue
        who = act[turn_idx % len(act)]; turn_idx += 1
        if who == last_real_speaker:    # nobody else spoke since -> a monologue, not a conversation
            paused = True; last_real_speaker = None
            add("system", f"Only {who} is responding (the other AIs are erroring or absent). Paused -- type to continue.", "system")
            continue
        text = ai_turn(who)
        if text.startswith("[error calling"):
            err_streak += 1
            if err_streak == 1:
                add("system", text + f" -- skipping {who}'s turn; the others continue.", "system")
            if err_streak >= 2 * max(len(act), 1):
                paused = True; err_streak = 0
                add("system", "All AIs are erroring. Paused -- check keys / switch models, then /go.", "system")
            else:
                time.sleep(2)
            continue
        err_streak = 0
        asked = ASK_SIGNAL.lower() in text.lower()
        add(who, text.replace(ASK_SIGNAL, "").strip())
        consec_ai += 1; last_real_speaker = who
        if asked:
            paused = True
            add("system", f"\U0001F514 {who} is asking for your input -- type to weigh in.", "system")
        elif consec_ai >= BACKSTOP:
            paused = True
            add("system", f"The AIs have gone {BACKSTOP} turns. Type to steer, or /go to let them continue.", "system")
        else:
            time.sleep(TURN_DELAY)

threading.Thread(target=ai_loop, daemon=True).start()

# ---------------- web ----------------
app = Flask(__name__)

@app.route("/")
def index(): return PAGE

@app.route("/stream")
def stream():
    name = (request.args.get("name") or "guest").strip()[:24] or "guest"
    def gen():
        q = queue.Queue()
        with lock: hist = list(conversation)
        for m in hist: yield f"data: {json.dumps(m)}\n\n"
        subscribers.append(q)
        presence_join(name)
        try:
            while True: yield f"data: {json.dumps(q.get())}\n\n"
        except GeneratorExit:
            try: subscribers.remove(q)
            except Exception: pass
            presence_leave(name)
    return Response(gen(), mimetype="text/event-stream")

@app.route("/send", methods=["POST"])
def send():
    global paused, consec_ai, last_real_speaker
    d = request.get_json(force=True, silent=True) or {}
    if d.get("code") != ROOM_CODE:
        return jsonify({"ok": False, "error": "bad room code"}), 403
    name = (d.get("name") or "guest").strip()[:24] or "guest"
    text = (d.get("text") or "").strip()
    if not text: return jsonify({"ok": True})

    if text.startswith("/"):
        cmd = text.lower().split()
        if cmd[0] in ("/cheap", "/heavy"):
            t = cmd[0][1:]
            for n in AI: tier[n] = t; override[n] = None
            add("system", f"{name}: all AIs -> {t}", "system")
        elif len(cmd) == 2 and cmd[0] in CMD2AI and cmd[1] in ("cheap", "heavy"):
            n = CMD2AI[cmd[0]]; tier[n] = cmd[1]; override[n] = None
            add("system", f"{name}: {n} -> {cmd[1]}  ({AI[n][cmd[1]]})", "system")
        elif len(cmd) >= 3 and cmd[0] in CMD2AI and cmd[1] == "use":
            n = CMD2AI[cmd[0]]; mid = text.split(None, 2)[2].strip()
            override[n] = None if mid.lower() == "default" else mid
            add("system", f"{name}: {n} model -> {override[n] or ('default ' + AI[n][tier[n]])}", "system")
        elif len(cmd) >= 3 and cmd[0] in CMD2AI and cmd[1] == "persona":
            n = CMD2AI[cmd[0]]; p = text.split(None, 2)[2].strip()
            AI[n]["persona"] = p
            add("system", f"{name} re-roled {n} -> \"{p[:70]}{'...' if len(p) > 70 else ''}\"", "system")
        elif cmd[0] == "/summary":
            act = active_ais()
            if act:
                s = ai_turn(act[0], extra="Summarize the discussion's conclusions and concrete decisions as a crisp, actionable brief a coding agent could pick up and build from. No preamble.")
                add(act[0], "Summary -- " + s.replace(ASK_SIGNAL, "").strip())
            else:
                add("system", "No active AIs to summarize.", "system")
        elif cmd[0] == "/pause":
            paused = True; add("system", f"{name} paused the AIs. Send /go or a message to resume.", "system")
        elif cmd[0] == "/go":
            consec_ai = 0; last_real_speaker = None; paused = False; add("system", f"{name}: continue.", "system")
        elif cmd[0] in ("/help", "/?"):
            add("system", "Commands:  /cheap | /heavy  -  /<ai> cheap|heavy  -  /<ai> use <model-id>  -  /<ai> persona <text>  -  /summary  -  /pause | /go", "system")
        else:
            add("system", f"unknown command '{text}'. Try /help", "system")
        broadcast_presence(force=True)   # reflect any tier change in the panel
        return jsonify({"ok": True})

    # a short "stop/pause/wait" pauses instead of resuming
    low = text.lower()
    if len(text) <= 24 and any(w in low for w in STOP_WORDS):
        add(name, text); paused = True
        add("system", f"{name} paused the AIs. Type /go or a message to resume.", "system")
        return jsonify({"ok": True})

    add(name, text)
    consec_ai = 0; last_real_speaker = None; paused = False
    return jsonify({"ok": True})

@app.route("/config", methods=["POST"])
def config():
    d = request.get_json(force=True, silent=True) or {}
    if d.get("code") != ROOM_CODE:
        return jsonify({"ok": False, "error": "bad room code"}), 403
    who = (d.get("name") or "someone").strip()[:24] or "someone"
    ai = d.get("ai")
    if ai not in AI:
        return jsonify({"ok": False, "error": "unknown ai"}), 400
    if "enabled" in d:
        enabled[ai] = bool(d["enabled"])
        add("system", f"{who} {'added' if enabled[ai] else 'removed'} {ai} {'to' if enabled[ai] else 'from'} the conversation.", "system")
    if d.get("tier") in ("cheap", "heavy"):
        tier[ai] = d["tier"]; override[ai] = None
        add("system", f"{who} set {ai} to {d['tier']} ({AI[ai][d['tier']]}).", "system")
    broadcast_presence(force=True)
    return jsonify({"ok": True})

PAGE = """<!doctype html><html><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>roundtable</title><link rel="stylesheet" href="/static/style.css"></head><body>
<div id=roster></div>
<div id=log><div id=inner></div></div>
<div id=bar><input id=text placeholder="type to join...  (/help for commands)" autocomplete=off>
<button id=send>Send</button></div>
<script src="/static/app.js"></script></body></html>"""

if __name__ == "__main__":
    act = active_ais()
    print(f"roundtable -> http://localhost:{PORT}   (room code: {ROOM_CODE})")
    print("active AIs:", ", ".join(f"{n}={model_for(n)}" for n in act) or "(none -- set API keys in .env)")
    inactive = [a["name"] for a in AIS if a["name"] not in act]
    if inactive: print("inactive (no key):", ", ".join(inactive))
    print(f"transcript -> {TRANSCRIPT}")
    print("share remotely with:  ngrok http", PORT, " (or a Tailscale IP)")
    app.run(host="0.0.0.0", port=PORT, threaded=True)
