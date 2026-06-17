# The Worker System — a self-coordinating AI team

A field-tested model for running a **team of autonomous AI coding sessions** that ship
software while a human stays at the product altitude instead of in the mechanical loop.
The mechanical work — coordinating, reconciling, merging, feeding the queue — runs
autonomously; the human only does what genuinely needs them: **deciding what to build** and
**verifying it works.**

This is the generic, tool-agnostic version of a system that's been run in production. Adapt
the placeholders (`PROJ`, `<repo-path>`, `your-org`, `TEAM_SLACK_WEBHOOK`) to your setup.

## What's here

| File | What it is |
|---|---|
| **[operating-model.md](operating-model.md)** | **Start here.** The four roles (workers, dispatcher, steward, human), the issue-tracker board as the coordination layer, the life of a ticket, the trust model, and *why* it works. |
| **[agent-worker-protocol.md](agent-worker-protocol.md)** | The worker rules in full — the claim loop, claim→reconcile→build ordering, the blocked→handoff flow, worktree/PR isolation. |
| **[onboarding.md](onboarding.md)** | Set up a machine to run workers: pull the shared docs, wire the webhook, the session-start auto-refresh hook, and the per-project preflight checklist. |
| **[team-up.ps1](team-up.ps1)** | A launcher that spins up multiple worker/role sessions at once. Edit the CONFIG block at the top, then run. |
| **[scripts/team-impact.py](scripts/team-impact.py)** | Measure the payoff: tickets closed per *active* day/week, **before vs after** you turned the team on. |

## The idea in one picture

```
  dispatcher  →  [ To Do → Ready ] → workers → [ In Review ] → steward → Done
   (+ human)        feeds queue       drain it     PRs green     merges/escalates
                                                                     ↑
                                              human verifies the judgment calls
```

The **issue tracker is the only coordination layer** — no session talks to another directly.
Status is the single source of truth for "what to do next." Workers run in their own git
worktrees on per-ticket branches, so they never collide; version control reconciles at merge,
which is what it's for.

## Getting started

1. Read **operating-model.md** end to end — it's the whole mental model.
2. Stand up the board statuses and follow **onboarding.md** on one machine.
3. Launch a couple of workers with **team-up.ps1** and watch the queue drain.
4. After a week, run **scripts/team-impact.py** to see the before/after.

## A note on attribution

Workers sign their work with a neutral codename (e.g. `worker-a`) for traceability. That's a
contributor handle, not AI attribution — keep handles neutral and out of anything user-facing.
