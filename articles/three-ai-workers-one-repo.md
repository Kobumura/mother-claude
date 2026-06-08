# What broke the first time we ran three AI workers on one repo

We pointed three autonomous AI coding agents ("workers") at a single repository
and let them drain a shared task queue in parallel, while a separate planning
session created the tasks. This is the field report: what held, what broke, and
the coordination rules that came out of it.

The headline is counterintuitive. **The parallelism was never the problem.** The
isolation model and the review gate worked on the first try. Every meaningful
failure traced to one thing — **the issue tracker had quietly drifted out of sync
with the code** — and parallelism took that drift, which is merely cosmetic with a
single developer, and made it *expensive*.

## The setup

- **One queue, status-as-state.** Tasks flow `To Do → Ready → In Progress → Needs
  Input → In Review → Done`. Workers pick only from **Ready**.
- **Claim to de-conflict.** Agents share one tracker login, so a worker claims a
  task with a comment carrying its **name** (the tiebreak) before working;
  earliest claim wins.
- **Isolation per worker.** Each worker runs in its **own working tree** (its own
  checkout on disk), branches per task, and opens a **pull request** into the
  shared integration branch. CI runs on the PR; a human/groomer merges.
- **Handoffs for memory.** When a worker pauses or blocks, it writes a short
  handoff (what's done, where the WIP lives, how to resume) so any worker can pick
  up cold.

## What worked (keep these)

- **A private working tree per worker is non-negotiable.** Two agents editing one
  checkout entangle their uncommitted changes in the same files — stale reads,
  clobbered saves, one worker's `add` sweeping another's WIP into its commit. We'd
  hit exactly that in a prior shared-checkout run. Separate trees let version
  control reconcile at **merge**, which is what it's for.
- **Branch → PR → CI, with a human merge gate.** A broken build becomes a red *PR
  check*, not a broken *integration branch* that blocks everyone. The PR diff
  doubles as the review artifact.
- **A claim tiebreak + signed work give traceability for free.** Name in the claim
  comment, name in the commit trailer. Workers reconstructed exactly who did what
  from the tracker and version history alone — which is how they later untangled a
  bad queue, with no extra coordination channel.
- **Verify-before-building catches duplicate work.** Reading the code before
  touching it caught two tasks whose code had already shipped — preventing a
  duplicate migration and a redundant PR.

## What broke: the queue lied

The single biggest failure: **most of the "Ready" queue was already done.** Of the
tasks marked ready to work, the majority had their code merged already; one was
half-finished with the remaining half described only in a commit message. Workers
spent the first third of their sessions doing forensic archaeology in the version
history just to determine whether there was any work left to do.

The root cause is mundane: **advancing the task when its code lands is a separate
manual step, and it kept getting dropped.** With one developer, a task sitting in
the wrong column is a cosmetic lag you fix whenever. With three concurrent
workers, it's a *correctness* problem — the queue is their source of truth for
"what to do," and it was wrong, so they re-derived and nearly rebuilt shipped work.

Secondary failures, all variations on the same drift:

- **The "ready means fully specified" gate wasn't enforced.** Tasks reached Ready
  with empty descriptions and no definition of done. Workers inferred scope from
  titles — precisely where an eager agent confidently builds the wrong thing.
- **End-to-end tests ran only after merge, not on the PR.** A UI task's PR looked
  green while its real validation hadn't run yet. The deeper blocker: no per-PR
  preview environment to test against.
- **Released claims left orphans.** A quick claim-then-release left a bare branch
  and working tree at the base commit — ambiguous between "active" and "abandoned"
  until someone wasted a round-trip deciding.
- **Near-identical worker names** (one character apart) are an attribution bug
  waiting to happen across claims, trailers, and handoffs.
- **Integration-branch vs production divergence went untracked** — work "done" on
  the integration branch but not yet in production, with nothing watching the gap.

## The rules that fixed it

Most of these are cheap — documentation and habit, not infrastructure:

1. **Reconcile against the code before building.** First action after claiming:
   search the history for the task id and grep for the feature's key symbols. If
   it already shipped, cite the commit and route the task to review — don't
   rebuild it. *Detection is the worker's job; the final close is the planner's*,
   so a half-done task can't be silently buried as "done."
2. **Move the task the moment its code lands** — and, the durable version,
   **automate it**: a task reference reaching the integration branch should
   auto-advance the task to "in review." This is the root-cause fix; everything
   else is mitigation. Prefer a no-code automation rule in your tracker fed by your
   existing version-control integration over a bespoke script.
3. **Gate entry into "Ready" on a real definition of done.** A task with an empty
   description doesn't get to be pickable. Bounce it back, don't guess.
4. **Reconciliation pass before spinning up workers** — diff merged task
   references against open task statuses and flag mismatches *before* N agents
   contend over phantom work, not after.
5. **Released claims clean up after themselves;** a bare branch at the base commit
   means "abandoned, reclaim freely."
6. **Names must be distinct at a glance.**
7. **Right-size the worker count to real queue depth.** N agents against a
   near-empty queue is pure coordination overhead — deepen the queue first.

## On "eyeball work"

A surprising amount of what feels like it needs a human is actually automatable,
and splitting it three ways helps:

- **Behavioral checks** ("does login still work?") → end-to-end tests — but run a
  smoke subset *on the PR*, against a preview environment, not only after merge.
- **Visual-regression checks** ("did this refactor shift any pixels?") →
  screenshot-snapshot tests that pixel-diff against a baseline and fail CI on
  unexpected change. This is the right tool for "this refactor should change
  nothing," and it needs no human.
- **Genuine design judgment** ("is this new layout good?") → still a human — but a
  browser-driving agent can *pre-stage* it: navigate the flows, capture the
  screenshots in each theme, and hand the human artifacts to glance at instead of
  a click-through to perform.

## The meta-lesson

None of the failures were caused by running agents in parallel. They were caused
by the **tracker and the code disagreeing**, which parallelism amplified from
cosmetic to costly. The coordination machinery — isolated working trees, a
status queue, a claim tiebreak, a PR gate, handoffs — was sound and mostly proved
itself on the first run. The misses were all **timing and enforcement**: the right
rules existed but landed mid-run or weren't gated. Keep your source of truth
honest and the system holds.
