# The AI-Team Operating Model

How a self-coordinating team of autonomous AI sessions ships software with a human
at the product altitude instead of in the mechanical loop. This is the
tool-agnostic guide: four roles, a shared board as the coordination layer, and a
small set of hard-won rules that keep multiple autonomous sessions from colliding.

## The idea

Humans become the bottleneck the moment they hand-carry packets between sessions —
relaying questions, copy-pasting status, merging every PR by hand. So the
**mechanical** work (coordinating, reconciling, merging, queue-feeding) runs
autonomously, and the human only does what genuinely needs them: **deciding what to
build** and **verifying it looks/works right.**

## The four roles

| Role | Sessions | Mode | Owns |
|---|---|---|---|
| **Workers** | several (e.g. worker-a, worker-b, worker-c) | autonomous (looping) | Drain the queue → ship PRs |
| **Dispatcher** | one session, with the human | interactive | Spec features → create well-formed Ready tickets ("new work IN") |
| **Steward** | one session | autonomous (looping) | Merge objective PRs, reconcile the board, drain In Review ("existing work THROUGH") |
| **Human** (the product owner) | their command channel | human | Product direction + final verification |

**Dispatcher feeds the queue. Workers drain it. Steward moves it through. The human
decides + verifies.**

## The board IS the coordination layer

No session talks to another directly — everything coordinates through the shared
issue-tracker status:

`To Do → Ready → In Progress → Needs Input → In Review → Changes Requested → Done`

- **To Do** — backlog / epics / not-yet-specced.
- **Ready** — fully specced, DoD clear. Workers pick only from here (+ Changes Requested).
- **In Progress** — a worker claimed it.
- **Needs Input** — worker blocked; question on the ticket; steward/human answers.
- **In Review** — PR green, awaiting a human/steward call.
- **Changes Requested** — shipped/PR'd but a reviewer wants a fix; a worker re-picks
  it, **skips the rebuild-check** (a commit is expected), reads the latest comment,
  does the fix.
- **Done.**

## The life of one ticket

1. **Human + Dispatcher** spec a feature → a **self-contained Ready ticket** (Context ·
   Scope · Acceptance + tests · Pointers — *scope in the description*).
2. A **Worker** claims the top of Ready (**claim → reconcile → build**: claim first,
   then confirm it isn't already shipped against the ticket's *current scope*, then
   build), in its **own git worktree** on a **per-ticket branch**.
3. Worker opens a **PR into the integration branch**; CI runs on the PR.
4. **Steward** reviews the green PR:
   - **Objective + complete** (backend/tests, DoD tests present) → **auto-merges** → Done.
   - **UX / incomplete / judgment call** → **Changes Requested** or stays In Review +
     **pings the human** with verify steps.
5. **Human verifies** the escalated ones → steward closes to Done.

## How they don't collide

- **Issue-tracker statuses = the queue** — the single source of truth for "what to do."
- **Claim-first** — earliest `claim:` comment wins (a shared login makes the comment
  the tiebreak).
- **Worktree per worker + branch/PR per ticket** — no entangled edits; version control
  reconciles at merge, which is what it's for.
- **A team chat channel** (`#your-coordination-channel`) = the one-way activity feed:
  steward summaries (FYI, no mention) + @-pings only when the human is genuinely needed.
- **Your shared docs repo** = the shared law every session reads at start. The
  **playbook** (per-project plumbing docs) = the tracker/CI specifics so nobody
  re-derives them.

## The trust model (the dial)

A **refinement stage**: the steward auto-merges **objective** work (tests pass, no UX)
but escalates everything with visual/product judgment to the human. As the gates (CI,
tests, self-review, reviewer agent) keep earning trust, more graduates to autonomous —
but UX/product always stays the human's.

## The hard-won rules (why it works)

- **Scope in the description, not a comment** — empty Ready tickets cause mis-reconciles.
- **Claim → reconcile → build** — never reconcile before claiming (it lets a peer steal
  the ticket and skips phantom-parking).
- **A re-groomed ticket can be the deferred Part 2** — reconcile against the *current
  scope* (description + comments), not "does a commit exist."
- **Never merge work missing its DoD tests.**
- **Branch per ticket, never the home branch.**
- **The dispatcher resolves engineering-correctness forks itself — it does NOT park them
  on the human as "UX calls."** A fork that's an engineering question ("should the layout
  reflow on every load?" — no, that's a regression) is the dispatcher's to decide, spec, and
  move to Ready. Surface to the human only genuine product-direction / UX-vision / visual-feel
  / ops / prod-promotion / cost decisions — always **with a recommendation.** Ending a pass
  with "nothing actionable for me" is rarely true; owning the engineering decisions IS the job.
- **No AI attribution anywhere** (neutral worker codenames are fine). Sign work with a
  neutral session handle — it identifies a contributor, not a tool, so it aids traceability
  without revealing the assistant.

## Known failure modes (the supervision/liveness gap)

The board coordinates *work*, but nothing supervises the *sessions*. Two gaps bite, and
both are structural rather than project-local:

- **Worker-halt vs. queue-refill race.** Workers auto-halt after extended idle (the backoff
  described in the worker protocol doc — sibling file `agent-worker-protocol.md`). If Ready was
  empty when they halted and the dispatcher refills *after*, the halted workers never see the
  new tickets — the team sits idle with a **full Ready queue and no one to wake them.** The
  dispatcher/steward **cannot** relaunch a halted worker (a backgrounded CLI session hangs
  without a TTY; a single-shot run executes once and never loops) — so at a halt their job is
  **diagnose + flag the human, not respawn.** Mitigations (adopt ≥1): a worker re-checks Ready
  one final time before its terminal halt; a watchdog flags "Ready non-empty + zero In-Progress
  claims for N min"; or raise the idle threshold. A **scheduled cloud agent** is a good fit for
  that watchdog — it runs on its own cadence independent of the halted tabs, inspects the board,
  and pings the human to **restart their engines.** Until a liveness layer exists, the human
  restart is the only recovery — surface it fast (one ping), don't let the queue sit.
- **Loop cadence must be active-aware.** Tighten the dispatcher/steward loop interval when
  workers are actively producing PRs (a merge-ready PR slipping ~24 min behind a 45-min idle
  backoff is as costly as a dead tab); lengthen only when the queue is genuinely idle or
  blocked-on-human. A fixed long backoff *while work is flowing* is itself a bottleneck.

## Setup notes

- **Notifications** go to your team chat. Configure the incoming webhook in an
  environment variable (e.g. `TEAM_SLACK_WEBHOOK`, never committed) and @-mention the
  ticket owner (`@owner`) keyed by project.
- **Project keys** in the examples (e.g. `PROJ-123`) are placeholders — substitute your
  own tracker's project key.
- **Repo paths** shown as `<repo-path>` are wherever you've cloned the project locally.

---

See also: the worker protocol doc (sibling file `agent-worker-protocol.md`) for the
worker rules in full, and the worker-machine onboarding doc for machine setup and launch
prompts.
