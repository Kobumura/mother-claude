# roundtable

A live, shareable room where **multiple AIs (Claude, Gemini, GPT…) and your humans**
talk together. The AIs run free, bouncing off each other; the room **pauses for the
humans** when someone types, an AI asks for input, or a cost-guard trips. Everyone
opens the same URL and can read + interject. No accounts, no bots — one small server.

Part of [mother-claude](../../) — an AI-as-teammate pattern: a place for models and
people to *think together*, then hand the outcome straight to a coding agent.

## Run it
```bash
pip install -r requirements.txt
cp .env.example .env          # add your API keys + a private room code
python roundtable.py
```
Open **http://localhost:5005**, enter a name + the room code, and start. (Claude +
Gemini join if their keys are set; GPT joins if you add an OpenAI key.)

## Get everyone in the same room
- **Same network:** share `http://<your-LAN-ip>:5005`
- **Different networks:** a tunnel (`ngrok http 5005`) or a mesh VPN like **Tailscale**
  (`http://<host-tailscale-ip>:5005` — keeps it private)
- *(On Windows you may need to allow the port through the firewall the first time.)*

## What it does
- AIs converse with a readable delay; **type anytime** to steer
- An AI that wants a human ends its turn with `@HUMANS` → the room pauses (🔔)
- **Cost guard:** auto-pauses after `BACKSTOP` AI turns with no human — and it's
  **free while paused** (zero model calls)
- **A down/erroring AI never freezes the room** — the others carry on
- **Live top-bar controls:** check each AI in/out of the conversation, set cheap/heavy per AI
- **Commands:** `/heavy` · `/<ai> cheap|heavy` · `/<ai> use <model-id>` ·
  `/<ai> persona <text>` · `/summary` · `/pause` · `/go`
- **Presence roster** (bold on arrival, italic on leaving) + **timestamps** in each
  viewer's own timezone
- A **transcript** of every message you can hand to a coding agent
  (*"read transcript-X.md and build what we decided"*)

The full how-to — customizing personas, swapping models, adding another AI, theming
the look — lives in the **docstring at the top of `roundtable.py`**. Open it and read
the header.

## Notes
- **Free-tier model quotas are tight** — two or three AIs make a lot of requests fast.
  On `429`/`limit: 0`, enable billing on the provider, raise `TURN_DELAY`, or use a
  lighter model.
- **Model IDs change** — if one 404s, set a current one in `.env` or `/<ai> use <id>`.

## License
**MIT** (this tool is code) — see `LICENSE`. The rest of mother-claude is CC BY 4.0.
