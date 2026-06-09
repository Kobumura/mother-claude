# A self-coordinating AI dev team: the operating model

How to run a team of autonomous AI coding agents that ships software while keeping
the human at the product altitude instead of in the mechanical loop. This is the
durable structure behind it — the roles, the coordination substrate, and the
hard-won rules. (Companion piece: "What broke the first time we ran three AI
workers on one repo.")

## The core idea

A human becomes the bottleneck the moment they hand-carry packets between agents —
relaying questions, copy-pasting status from one terminal to another, reviewing and
merging every change by hand. So you push the **mechanical** work — coordinating,
reconciling, merging, keeping the queue fed — onto autonomous agents, and reserve
the human for the two things only they can do: **deciding what to build** and
**judging whether it's right.**

## Four roles

| Role | Count | Mode | Owns |
|---|---|---|---|
| **Workers** | several | autonomous loop | Drain the task queue → open pull requests |
| **Planner** | one, with the human | interactive | Spec features → create well-formed ready tasks ("new work IN") |
| **Groomer** | one | autonomous loop | Merge objective PRs, reconcile the board, clear the review column ("existing work THROUGH") |
| **Human** | — | human | Product direction + final verification |

The flow in one line: **the planner feeds the queue, the workers drain it, the
groomer moves it through, and the human decides and verifies.**

## The issue tracker is the coordination layer

No agent messages another directly. They coordinate entirely through **task status**
in the shared tracker, which doubles as the work queue:

`Backlog → Ready → In Progress → Needs Input → In Review → Changes Requested → Done`

- **Ready** — fully specified, with a clear Definition of Done. Workers pick *only*
  from here (and Changes Requested). This is the gate.
- **Needs Input** — a blocked worker parks it here with its question; the
  groomer/human answers in a comment and it returns to a pickable state.
- **In Review** — change is green in CI, awaiting a human/groomer decision.
- **Changes Requested** — already shipped/PR'd, but a reviewer wants a fix. A worker
  re-picks it, **skips the "is this already done?" check** (an existing commit is
  expected), reads the latest comment, and does the fix. This status exists so the
  worker never has to do commit-vs-comment archaeology to tell "fix this" from
  "already done."

## The life of one task

1. **Human + planner** spec a feature into a **self-contained ready task**: context,
   scope, acceptance criteria (including the tests expected), and pointers — with the
   **scope written in the description**, not buried in a comment.
2. A **worker** claims the top of the queue (**claim → reconcile → build**: claim
   first to lock it, *then* confirm it isn't already shipped against the task's
   current scope, *then* build), working in its **own isolated checkout** on a
   **per-task branch**.
3. The worker opens a **pull request**; CI runs on it.
4. The **groomer** reviews the green PR:
   - **Objective and complete** (logic/tests, with the required tests present) →
     **auto-merge** → Done.
   - **Visual / incomplete / a judgment call** → route to Changes Requested or leave
     in review, and **ping the human** with exactly what to verify.
5. The **human verifies** the escalated few → the groomer closes them out.

## How they avoid colliding

- **Task status = the single source of truth** for "what to do."
- **Claim-first** — the earliest claim comment wins (agents often share one tracker
  login, so the comment, not the assignee, is the tiebreak).
- **One isolated checkout per worker + one branch/PR per task** — no entangled edits;
  version control reconciles at merge, which is exactly where it's designed to.
- **A one-way chat feed** — the groomer posts FYI summaries each pass; it @-mentions
  the human *only* when they're genuinely needed. The human watches without being in
  the middle.
- **A shared standards doc every agent reads at startup**, plus a **playbook** that
  captures the tracker/CI plumbing so no agent re-derives it each time.

## The trust dial

Treat it as a **refinement stage**. The groomer auto-merges **objective** work
(tests pass, no UI judgment) but escalates anything visual or product-shaped to the
human. As the gates — CI, required tests, self-review, an independent reviewer agent
— prove they catch what they should, more work graduates to fully autonomous. Visual
and product decisions stay with the human indefinitely.

## The rules that make it hold

- **Scope in the description, not a comment** — an empty "ready" task is the root
  cause of workers confidently building the wrong thing.
- **Claim → reconcile → build** — never reconcile before claiming; it lets a peer
  grab the task mid-analysis and skips cleaning stale tasks from the queue.
- **A re-scoped task can be the deferred "part 2"** — reconcile against the *current*
  scope (description + recent comments), not merely "does a commit exist."
- **Never merge work that's missing its required tests.**
- **One branch per task — never commit on the worker's idle home branch.**
- **No AI authorship attribution** in commits/PRs/tasks (a neutral contributor handle
  is fine).

## Why it works

None of this is about making the agents smarter. It's about a **shared source of
truth** (the tracker), **isolation** (a checkout and branch per agent), **a review
gate** (PRs + CI), and **a clear escalation path** (objective work flows on its own;
judgment goes to the human). Get those four right and the team mostly runs itself —
the human moves up to deciding *what* to build and confirming it's good, which is the
only place they were ever irreplaceable.
