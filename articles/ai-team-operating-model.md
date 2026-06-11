---
title: "A Self-Coordinating AI Dev Team: The Operating Model"
published: false
description: Point several autonomous AI coding agents at one repo and they collide. The fix isn't smarter agents -- it's an operating model: four roles, the issue tracker as the only coordination layer, and exhaustive guardrails the agents can't cross.
tags: ai, productivity, automation, developerexperience
series: Designing AI Teammates
canonical_url: https://github.com/Kobumura/mother-claude/blob/main/articles/ai-team-operating-model.md
---

*Good morning, Angels.*

![Three silhouetted operatives in the classic Charlie's Angels poses](images/ai-team-angels.jpg)

> **TL;DR**: Pointing several autonomous AI agents at one repository doesn't fail because the agents aren't smart enough -- it fails without structure. The structure is an operating model: four roles, the issue tracker as the *only* coordination layer, the human kept at the product altitude, and an exhaustive set of guardrails the agents can't cross -- adhered to by the workers *and* independently double-checked by the Steward. Here's the whole thing.

*Who this is for: anyone running -- or about to run -- more than one AI coding agent at a time, and wondering how to keep them from colliding or shipping confident nonsense.*

**Part of the *Designing AI Teammates* series.**

> *"Your methodologies are antiquated and weak. Your procedures of approval ensure
> that only the least radical ideas are rewarded. Meanwhile your competition is
> innovating."*
> -- Alex, *Charlie's Angels*

A human hand-approving every change *is* a procedure of approval that rewards the
slowest, least radical path. So we retired it: we run a team of autonomous AI coding
agents that ships software while we stay at the product altitude instead of down in the
mechanical loop.

**By the numbers:** in one recent week, our team closed roughly **140 tickets** on a
single repo -- the bulk of that whole month's output -- while we kept our hands on
exactly two things: deciding *what* to build, and confirming it was *right*.

Here's the thesis, and everything below is just the proof: **the agents aren't
coordinated by intelligence -- they're coordinated by structure.** What follows is that
structure -- the roles, the coordination substrate, the guardrails, and the hard-won
rules. (Companion piece: "What broke the first time we ran three AI workers on one repo.")

## The core idea

We become the bottleneck the moment we hand-carry packets between agents --
relaying questions, copy-pasting status from one terminal to another, reviewing and
merging every change by hand. So we push the **mechanical** work -- coordinating,
reconciling, merging, keeping the queue fed -- onto the agents, and reserve ourselves
for the two things only a human can do: **deciding what to build** and **judging whether
it's right.**

## Four roles

| Role | Count | Mode | Owns |
|---|---|---|---|
| **Workers** | several | autonomous loop | Drain the task queue → open pull requests |
| **Dispatcher** | one, with the human | interactive | Spec features → create well-formed ready tasks ("new work IN") |
| **Steward** | one | autonomous loop | Merge objective PRs, reconcile the board, clear the review column ("existing work THROUGH") |
| **Human** | -- | human | Product direction + final verification |

The flow in one line: **the dispatcher feeds the queue, the workers drain it, the
steward moves it through, and the human decides and verifies.**

> **The cast**, if it helps the roles stick: *"Once upon a time there were three very
> different little girls who grew up to be three very different women with three things
> in common: they're brilliant, they're beautiful, and they work for me. My name is
> Charlie."* The **workers** are the Angels -- the operatives who run the missions.
> **Charlie** is the dispatcher -- the voice on the speaker handing out the assignments:
> *"Good morning, Angels."* **Bosley** is the steward -- the handler in the field who
> reviews every finished mission and brings it home.

## The issue tracker is the coordination layer

No agent messages another directly. They coordinate entirely through **task status**
in the shared tracker, which doubles as the work queue:

`Backlog → Ready → In Progress → Needs Input → In Review → Changes Requested → Done`

- **Ready** -- fully specified, with a clear Definition of Done. Workers pick *only*
  from here (and Changes Requested). This is the gate.
- **Needs Input** -- a blocked worker parks it here with its question; the
  steward/human answers in a comment and it returns to a pickable state.
- **In Review** -- change is green in CI, awaiting a human/steward decision.
- **Changes Requested** -- already shipped/PR'd, but a reviewer wants a fix. A worker
  re-picks it, **skips the "is this already done?" check** (an existing commit is
  expected), reads the latest comment, and does the fix. This status exists so the
  worker never has to do commit-vs-comment archaeology to tell "fix this" from
  "already done."

## The life of one task

1. **Human + dispatcher** spec a feature into a **self-contained ready task**: context,
   scope, acceptance criteria (including the tests expected), and pointers -- with the
   **scope written in the description**, not buried in a comment.
2. A **worker** claims the top of the queue (**claim → reconcile → build**: claim
   first to lock it, *then* confirm it isn't already shipped against the task's
   current scope, *then* build), working in its **own isolated checkout** on a
   **per-task branch**.
3. The worker opens a **pull request**; CI runs on it.
4. The **steward** reviews the green PR:
   - **Objective and complete** (logic/tests, with the required tests present) →
     **auto-merge** → Done.
   - **Visual / incomplete / a judgment call** → route to Changes Requested or leave
     in review, and **ping the human** with exactly what to verify.
5. The **human verifies** the escalated few → the steward closes them out.

## How they avoid colliding

- **Task status = the single source of truth** for "what to do."
- **Claim-first** -- the earliest claim comment wins (agents often share one tracker
  login, so the comment, not the assignee, is the tiebreak).
- **One isolated checkout per worker + one branch/PR per task** -- no entangled edits;
  version control reconciles at merge, which is exactly where it's designed to.
- **A one-way chat feed** -- the steward posts FYI summaries each pass; it @-mentions
  the human *only* when they're genuinely needed. The human watches without being in
  the middle.
- **A lean standards core at startup, the depth on demand** -- every agent loads a small
  always-on core (the protocol + the rules that apply to everything); the per-area detail
  (engineering, testing, design) is pulled in *only when a task touches it*, never dumped
  into every context. A **playbook** captures the tracker/CI plumbing so no agent
  re-derives it each time.

## The trust dial

Treat it as a **refinement stage**. The steward auto-merges **objective** work
(tests pass, no UI judgment) but escalates anything visual or product-shaped to the
human. As the gates -- CI, required tests, self-review, an independent reviewer agent
-- prove they catch what they should, more work graduates to fully autonomous. Visual
and product decisions stay with the human indefinitely.

## The electric fences

> The pasture this worker hive grazes in is ringed with electric fences.

That's the part that makes it safe to turn them loose. The agents roam freely *inside*
the field -- but the field is fenced by an exhaustive set of guardrails they cannot
cross. Every one is codified -- a lean core the agents always carry, the rest pulled in
only when a task touches that area -- and enforced at the gate: CI, a pre-push hook, and
the Steward's review:

**Engineering**
- **Reusability** -- grep before you write; reuse what exists, never duplicate it (a
  copy-paste detector fails the build on new duplication).
- **Separation of concerns** -- layer boundaries hold (no service reaching into a
  screen, no circular dependencies); no god files past a hard line-count cap; no
  business logic smuggled into the UI.
- **Type safety** -- `strict` on, `any` banned, no unexplained `@ts-ignore`; every
  external boundary typed.
- **No dead code, no over-guarding** -- nothing unreachable, no defenses against shapes
  that can't occur.

**Testing**
- The **required tests ship with the code** -- unit, regression, and an end-to-end flow
  for anything user-facing; never a merge that's missing them.
- **No zero-assertion tests, no committed `.only`** -- a CI guard fails on either.
- **Mutation testing** on the money-path services -- coverage proves execution; the
  mutation score proves the tests would actually catch a regression.
- **Contract tests** against the API, so client and server can't drift apart.

**Design**
- **Design tokens only** -- no raw hex, spacing, or font sizes in screens; shared
  components extracted, not re-implemented.
- **Accessibility budget** -- labels, contrast, and touch targets asserted, not hoped for.

**Security**
- **No secrets in code** -- credentials live in a secret store, encrypted at rest.
- **Auth patterns are off-limits to casual edits** -- OAuth/PKCE/keychain flows;
  no injection vectors; dependency vulnerabilities scanned on every PR.

**Deployment**
- **CI green, the right branch, never a shortcut to prod** -- and sensitive code (auth,
  billing, migrations, data-deletion) never auto-merges.
- **Migrations validated against the live schema** before they run, with a rollback path
  on file.
- **Performance budgets** -- bundle size and key query counts can't regress silently.

…and the fence line keeps growing: every incident that teaches us a new failure mode
becomes a new wire the next morning.

And here's the load-bearing part: **the fences aren't left to the grazers to respect on
the honor system.** The workers adhere to them -- *and the Steward independently
re-verifies that adherence before anything merges.* A worker reports its tests pass, its
diff reuses the right helper, and the standards hold; the Steward confirms they actually
do, walking the fence line on every pass. **Adherence is the worker's job; verification
is the Steward's.** That second, independent check -- not the agents' good intentions -- is
what lets the trust dial climb without the work going feral.

Turn autonomous agents loose *without* the fences and they don't move slowly -- they move
fast, confidently, in the wrong direction. The guardrails aren't what slow the team
down; they're the only reason it's safe to let it run at all.

## The rules that make it hold

- **Scope in the description, not a comment** -- an empty "ready" task is the root
  cause of workers confidently building the wrong thing.
- **Claim → reconcile → build** -- never reconcile before claiming; it lets a peer
  grab the task mid-analysis and skips cleaning stale tasks from the queue.
- **A re-scoped task can be the deferred "part 2"** -- reconcile against the *current*
  scope (description + recent comments), not merely "does a commit exist."
- **Never merge work that's missing its required tests.**
- **One branch per task -- never commit on the worker's idle home branch.**
- **No AI authorship attribution** in commits/PRs/tasks (a neutral contributor handle
  is fine).

## Why it works

A smarter model doesn't solve coordination -- **structure** does. Verification solves
trust, isolation solves collision, workflow solves ambiguity. So none of this is about
making the agents smarter; it's about a **shared source of truth** (the tracker),
**isolation** (a checkout and branch per agent), **a review gate** (PRs + CI), **a clear
escalation path** (objective work flows on its own; judgment goes to the human), and
**the fences** (exhaustive guardrails the agents can't cross, independently verified by
the Steward). Get those five right and the team mostly runs itself -- the human moves up to deciding *what* to build and confirming it's good,
which is the only place they were ever irreplaceable.

---

Strip away the costumes and it's a familiar shape: a **scrum team** -- a backlog, a board,
standups by status, reviews, a definition of done. These teammates just resolve their
differences quickly and quietly, and -- every so often -- get *zapped* by the fence.

*Good work, Angels.*
