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

## Guardrails worth encoding

- Only pick tickets carrying the ready label.
- Never merge to the production branch — keep that human-gated.
- One ticket at a time per worker; In Review before claiming the next.
- If CI won't go green after a fair effort, use the blocked handoff rather than
  leaving work half-done.

## When to graduate to something heavier

This DIY setup is great to start. If you outgrow it, the next step is making the
**unit of work a pull request**: an agent opens a PR per ticket (e.g. a tracker-
or label-triggered CI agent). Then the PR *is* the verification artifact (you read
the diff), each run is isolated (collisions surface at merge), and nothing needs
babysitting. Keep your tracker as the planning board; let PRs be the execution
queue.
