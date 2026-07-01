# Pattern: Multi-Agent Worker Coordination

How to run several autonomous AI coding agents ("workers") against one backlog in
parallel — draining a queue, staying out of each other's way, and handing off to
a human when they hit a question — without building any orchestration server.

Keep one session for **planning** (creating and specifying tickets) and point the
**workers** at the ready queue. The whole system rides on tools you already have:
your issue tracker, your chat tool, and git.

## The three coordination problems (and where each is solved)

| Problem | Solve it with | Why |
|---------|---------------|-----|
| Two workers grab the same ticket | **The issue tracker's status + assignee** | The tracker is already a queue with claim state. |
| A worker needs a human decision | **A comment on the ticket** (not chat) | The answer must be durable and attached to the work, so any worker can resume. |
| "Look at this" notifications | **A one-way chat webhook** | Cheap, free, and the right tool for *attention* (not for claims or answers). |

The key distinction: **authoritative state goes in the tracker/git (persistent,
atomic at push); chat is only for getting a human's attention.** Don't put claims
or answers in an ephemeral channel.

## The capability contract (works with any tracker)

Everything here rides on **eight primitives**. Any issue tracker that offers them can
run this system — GitHub Issues + Projects, Linear, Trello, Monday, Notion, Jira. Map
each primitive to your tool once (see *Adapting to your tracker*) and the protocol is
unchanged.

| # | Primitive | What it's for | Your tracker offers it as… |
|---|-----------|---------------|----------------------------|
| 1 | **Ordered queue with a "ready" gate** | workers pick only blessed work | a status/column + a `ready` label |
| 2 | **States that flow left→right** | To Do → Ready → In Progress → Needs Input → In Review → Done (+ a "changes requested" loop-back) | statuses / board columns |
| 3 | **An atomic claim other agents can read** | stop two workers on one ticket | assignee (+ a claim comment as tiebreak) |
| 4 | **Durable per-item comments** | handoffs, blocked questions, verify steps, attached to the work | issue comments |
| 5 | **A tag orthogonal to status, filterable** | peer notes + inbox polling that never lie about the work's state | labels + filter-by-label |
| 6 | **A query/filter** | pull the queue; poll your inbox tag | saved filter / `list --label` / search |
| 7 | **Per-agent identity** | know who claimed / reviewed / merged | separate accounts or per-agent tokens |
| 8 | **A one-way notify channel** | get a human's *attention* (not state) | chat incoming webhook (Slack/Discord/Teams) |

**One of these changes shape with your tracker — the claim (#3).** If all agents run
under **one shared tracker account**, the assignee field can't tell two workers apart;
the tiebreak is the **earliest `claim:` comment** and each agent carries a **name**. If
every agent has its **own identity** (separate accounts, or a tracker with atomic
assignment like Linear), the claim is simply *"assign it to yourself; if it's already
assigned, take the next"* — no comment race. Pick the mechanism your identity model
supports; the rest of the loop is identical.

Primitives 5 and 6 travel together — an inbox tag is only useful if you can **filter by
it**, and every major tracker can. That makes the peer-coordination label-inbox (below)
the most portable piece of the whole system.

## The claim loop

Each worker runs this until the queue is empty:

1. **Pull** the ready queue, highest priority first (e.g. `status = To Do AND
   label = agent-ready`). A dedicated label is the human's *throttle* — only
   blessed tickets are pickable, so workers never grab epics or half-specced work.
2. **Claim** the top ticket: assign it to yourself + move it to In Progress, then
   **re-read it**. If the assignee isn't you, another worker won — take the next.
   (Optimistic claim with read-back; good enough, no lock required.)
3. **Do the work to the ticket's Definition of Done**, with tests.
4. **Push** and get CI green.
5. **Move to In Review** and **notify** the owner.
6. **Loop.** Stop and report when the queue is empty.

## Notify on handoff

Post to a chat **incoming webhook** (Slack/Discord/Teams all have these — free, no
extra seat, outbound-only). Store the URL as an env var; never commit it. Tag the
**owner the ticket indicates**, defaulting per project — keep a small project →
person map so the right human is pinged.

```
POST <webhook>  { "text": "@owner TICKET-123 ready to verify — <one-line> — CI green" }
```

## When a worker is blocked

An incoming webhook is **one-way** — a worker can post but can't hear a reply, and
agents act in turns (no background listener). So a blocked worker must not wait:

1. **Post the question as a comment on the ticket** — the durable answer channel.
2. **Re-flag** the ticket: drop the ready label, add a `needs-input` label, move
   it back to the backlog so no worker re-grabs it.
3. **Ping** the owner in chat (so they know *which* ticket).
4. **Stop**; take the next ready ticket.

The human answers **in the ticket comment**, clears `needs-input`, re-adds the
ready label. Any worker re-claims it, reads the answer, and continues — the human
never has to track down a specific session.

## Peer coordination between two lead roles (the orthogonal-tag inbox)

Once you split the human-facing side into two standing roles — a **planner** (specs work
into Ready) and a **steward** (reviews, merges, keeps the queue flowing) — both roles
poll the board every loop and sometimes need to leave *each other* a note on a specific
ticket, without a human relaying it.

**Do NOT do this by moving the ticket's status.** A status is a claim about the *work's*
state; reusing it as a mailbox makes the status **lie**, and a lying status misfires the
other role's automation — a note parked in "In Review" gets swept up by the steward's
"merge the green ones" logic and **merged early**; a note dropped in "Needs Input" is
indistinguishable from a genuinely blocked ticket.

**Instead use a per-role tag orthogonal to status.** The sender leaves the note as a
**comment** and adds a label — `needs-planner` / `needs-steward`. The recipient's loop
runs **one extra query each pass** (`label = needs-<role>`), reads, acts, and **removes
the label as the "mark-read"** — but only once the note is *fully actioned*, not merely
seen. The status stays truthful, it's auditable, and it works even when both roles share
one tracker account (where an assignee field couldn't tell them apart).

Two things make it more than a convenience:
- **It's the only clean way to reach a *closed* ticket.** You can't signal a done ticket
  by moving its status without reopening it (which lies about its state); a label +
  comment leaves the closed record intact.
- **The inbox query must be status-agnostic.** Filter on the label *alone* — don't also
  exclude done/closed items, or you'll silently miss notes left on finished tickets.
  (This is the easy-to-miss part: the first version of one such watch filtered out
  closed items and dropped every note left on a done ticket.)

Keep the one-way notify channel (above) for what a human needs to see *now*; the
tag-inbox is for role-to-role notes that can wait a poll.

## Guardrails worth encoding

- Only pick tickets carrying the ready label.
- Never merge to the production branch — keep that human-gated.
- One ticket at a time per worker; In Review before claiming the next.
- If CI won't go green after a fair effort, use the blocked handoff rather than
  leaving work half-done.

## Adapting to your tracker

This protocol is written against the **capability contract** above, not any one tool. To
run it on yours, map the eight primitives once — see
**[`adapting-to-your-tracker.md`](adapting-to-your-tracker.md)** for a per-tracker mapping
table, a worked **GitHub Issues + Projects** reference setup, and a **bootstrap prompt**
you can hand your own AI assistant to generate the concrete board config, CLI recipes, and
agent instructions for your exact tool.

## When to graduate to something heavier

This DIY setup is great to start. If you outgrow it, the next step is making the
**unit of work a pull request**: an agent opens a PR per ticket (e.g. a tracker-
or label-triggered CI agent). Then the PR *is* the verification artifact (you read
the diff), each run is isolated (collisions surface at merge), and nothing needs
babysitting. Keep your tracker as the planning board; let PRs be the execution
queue.
