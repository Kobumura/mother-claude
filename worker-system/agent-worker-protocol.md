# Agent Worker Protocol

How autonomous AI sessions ("workers") drain a project's ticket queue in parallel
without colliding, and hand off to a human when they need an answer. Planning +
ticket creation happens in a separate session; workers only execute already-specced
tickets.

This is a tool-agnostic framework. It assumes an issue tracker with configurable
statuses (examples below use a generic project key `PROJ` and a `jira`-style CLI;
substitute your tracker), a git host with pull requests and CI, and a one-way chat
webhook for notifications. The two planning/grooming roles are called **dispatcher**
(the planner — creates and specs tickets) and **steward** (the groomer — reviews,
merges, and signs off). Same roles, same rules whatever you name them locally.

For how the roles and stages fit together, see `operating-model.md`; for setting up a
worker machine, see `onboarding.md`.

## Worker identity (your name)

Each worker needs a name — it de-conflicts claims (all workers may share one tracker
login, so the name, not the tracker user, tells two workers apart) and lets a human
retrace who did what.

- Use the name given in your **launch prompt** (e.g. "worker-a", "worker-b").
- **If you don't know your name, ask** before claiming anything.
- If there genuinely is no name, fall back to your session id.
- Names must be **distinct at a glance** — more than one character apart from any
  other live worker. Two near-identical names side by side are an attribution bug
  waiting to happen (a skim misreads one's claim/commit/handoff as the other's). If
  your name collides, ask for a different one before claiming.

Keep the name **neutral** — a plain handle, never anything that reveals AI ("AI",
"bot", "assistant", or a model name). That is what keeps signing compatible with the
no-AI-attribution rule.

**Sign your work with your name**, everywhere you author something:
- The tracker — the `claim:` comment and the verify / blocked pings.
- Commits — a trailer line `Worker: <name>` (the git author stays the human).
- Session handoffs and any other doc you write — `— <name>`.
- **Never** AI attribution (no `Co-Authored-By`, no "Generated with ..."). A neutral
  codename is a handle, not AI credit.

## Ticket status & lifecycle

The board reads left to right:
**To Do → Ready → In Progress → Needs Input → In Review → Done**
— plus **Changes Requested**, a feedback loop from In Review back to a
worker-pickable state (the human shipped-then-found-an-issue case).

- **Ready** — the dispatcher (human or planning session) moves a ticket here once it
  is fully specced: clear Definition of Done, tests expected, no open questions.
  Workers pick **only** from **Ready**. Epics and vague tickets stay in To Do.
  **Entry gate (dispatcher/steward):** a ticket may **not** cross into Ready with an
  empty description / no DoD. An under-specced Ready ticket forces workers to guess
  scope — that's how a worker confidently builds the wrong thing. If you find an
  empty Ready ticket, bounce it back to To Do; don't build from a guessed scope.
  Every DoD states the **quality bar**, not just behavior: clean, DRY, properly
  abstracted, follows existing patterns, meaningful tests — so workers aim for the
  top-tier bar from the first keystroke, not just "feature + passing test."
  **Put scope in the DESCRIPTION, not just a comment — especially on a re-groom.**
  When you reopen/re-scope a partially-shipped ticket (e.g. "phase 1 merged, this
  ticket now covers the remaining X"), write that into the *description*. Scope that
  lives only in a comment is the root cause of mis-reconciles — a worker reads the
  commit, sees an empty description, and wrongly parks it as "done."
  **Pre-groom screen — confirm three things before promoting to Ready** (a cheap check
  that kills the common bounce classes): **(1) Repo/stack** — the code lives in the
  repo/stack this worker actually operates; grep the worker's tree for the named symbols
  first. Cross-repo logic → Needs Input, not Ready. **(2) No owner-only / shared-state
  change** — no new dependency, native rebuild, migration, or shared-tree mutation a
  worker can't safely make (those are owner-gated). **(3) No hot-file collision** — it
  doesn't edit a file an in-flight ticket is already editing (see *Batch-merge hygiene*);
  sequence or rebase instead. This screen tightens dispatcher grooming; the worker's
  **claim → reconcile → build** remains the second net — neither layer alone is enough.

> **Keep the queue honest — move the ticket the moment its code lands.** The
> board is the workers' source of truth for "what to do." If a ticket's code is
> merged but the ticket still says Ready, the next worker re-derives or re-builds
> shipped work — this failure recurs in practice (a near-redo, then several tickets
> stale in one queue). Advancing the ticket is a separate manual step that keeps
> getting dropped; the durable fix is **automation** (a ticket ref landing on the
> integration branch auto-transitions the ticket → In Review). Until that's wired,
> whoever merges advances the ticket, and the dispatcher runs a reconciliation pass
> (below) before provisioning workers.
- **In Progress** — claimed (see the claim loop), via a `claim: <name>` comment.
- **Needs Input** — a blocked worker moves it here, comments its question on the
  ticket, and stops. The human answers in the comment and moves it back to
  **Ready**. This + In Review are the human's "what needs me" columns.
- **In Review** — done + CI-green. It is a **holding status, NOT a synonym for
  "needs a human."** The steward's job is to *sort* the pile, not punt it:
  - **Close it to Done yourself** (with a citation) when it's **objective + merged +
    test-covered with no genuine judgment pending** — backend / data / CI / migration
    logic that its tests actually prove. Don't park objective work for the owner;
    that over-escalation defeats the autonomy.
  - **Leave it for the owner** only when it genuinely needs *their eyes*: **UX / visual**
    ("does it look right"), **product / scope judgment** ("is this the right
    behavior"), **sensitive** (auth / security / billing / data-deletion), or an
    **explicit verify request** — a verify ping, a "verify on dev" comment, or a DoD
    whose end-to-end behavior the unit tests don't prove (e.g. an external webhook
    round-trip).
  The two failure modes are symmetric: **never auto-close something with a *real*
  pending verification** (that's the owner's call), and **never escalate objective,
  tested work just because you're being cautious.** If it's objective and its tests
  prove it, close it.
  - **Automatable verification belongs in e2e, NEVER on the human.** If a ticket would
    punt to a "human glance" something the e2e suite can check — *it renders, the value
    shows, the column/count is right, the link works, the section appears for this entity
    type* — that ticket is **incomplete**: the dispatcher/steward **bounces it to add the
    e2e spec**, exactly like a missing unit test. The human's eyes are for what a computer
    genuinely can't judge — **aesthetic** ("does it *look/feel* right") and **product/scope**
    ("is this the right behavior") — not for confirming a render a machine verifies faster
    and more reliably. **Catch this proactively** — don't wait for the owner to notice they're
    being handed a manual check that should've been automated.
  - **An e2e spec must be VALIDATED GREEN on the dev site before handoff.** Until e2e runs
    pre-merge in CI (an in-CI booted-app gate; if today PR CI does *not* run e2e and only a
    post-merge gate does), a worker who authors an e2e spec and hands it off unvalidated lands
    it **red on first contact**. A red-on-first-contact spec is not done. So for any UI ticket,
    the DoD includes *its e2e spec passing on the dev site* — author it, run it green there,
    then hand off.
- **Changes Requested** — the human reviewed In Review work, found something off,
  and sent it back for a fix. **The code is already on the integration branch *by
  design* here** — so a worker picking this up **skips the phantom-check** (an
  existing commit is expected, not proof of done), reads the **latest comment** for
  the requested change, and does the fix → PR → In Review. This status exists
  precisely so the worker doesn't have to do commit-vs-comment archaeology to tell
  "fix this" apart from "already done." (The *answered-question* case is different —
  it has no shipped code, so it just goes Needs Input → Ready.)
- **Done** — reached **by the worker (self-close)** when the DoD is fully met by
  passing automated checks and there's no human judgment to make; otherwise **by
  the human** after In Review. Never close on un-run or failing checks.

## The claim loop

Run until the queue is empty:

1. **Pull the queue** — highest priority first, then manual backlog order, and
   take the **top** result:
   ```
   <tracker> search 'project = PROJ AND status in (Ready, "Changes Requested") ORDER BY priority DESC, Rank ASC'
   ```
   (Priority is the coarse band; Rank is the human's drag order within a band —
   dragging a ticket to the top of the column bumps it up the queue.) Both
   **Ready** and **Changes Requested** are pickable; the status tells you which
   mode you're in (fresh build vs. fix — see step 3).
2. **Claim the top — FIRST, before you read or evaluate it.** Claiming is cheap;
   reading and working are expensive, so claim *before* you invest any time
   (otherwise two workers study the same ticket and one wastes the effort). **But
   the bulk queue search lags the index** — a ticket you pulled may have been
   claimed + moved to In Progress by a peer minutes ago and still appear in your
   list. So **right before claiming, individually re-fetch it** (`<tracker> get
   <KEY> status` — individual gets are accurate even when bulk search isn't); if it's
   no longer in Ready/Changes Requested, or already carries an **earlier** `claim:`,
   **skip it without claiming** and take the next. (This is what stops a stale-pull
   double-build.) Otherwise post a comment **`claim: <name> · session <id>`** — your
   name **and** your session id — then transition to In Progress. **Re-read the
   ticket's comments** and find the **earliest** `claim:`. If its name isn't yours,
   another worker won — yield and take the next (you lost nothing but the cheap
   claim). If it's yours, you own it: post a **start** ping, then evaluate and work.
   - The name is the tiebreak — workers may share one tracker login, so "assignee"
     can't tell two workers apart. Record the **session id** too: it's durable and
     lets a human resume that exact session later to replay what this worker did (the
     name is for reading the feed; the session id is for going back).
3. **Reconcile against the code — is this already done?** *(Do this AFTER you've
   claimed the ticket in step 2 — claiming is always first. Do NOT reconcile
   before claiming: it seems efficient, but it lets a peer grab the ticket while
   you analyze, and it skips phantoms instead of parking them — so the next worker
   re-analyzes the same stale ticket. The order is always **claim → reconcile →
   build**.)*
   - **If the ticket is in `Changes Requested`, SKIP this whole step.** The code is
     on the integration branch by design; an existing commit is *expected*, not proof
     of done. Jump straight to the **latest comment** for the requested fix and do it.
     (Skipping the phantom-check here is the entire point of the status.)
   Otherwise (a fresh **Ready** ticket): now that it's yours, before you build
   anything, check whether the work already shipped (the Ready queue lags the code):
   ```
   git log --all --grep="PROJ-<n>"        # already a commit for this ticket?
   grep -rn "<key symbol from the title>"  # does the feature already exist?
   ```
   **Reconcile against the ticket's CURRENT scope — description AND recent comments
   (especially steward comments) — not just "does a commit exist."** A re-groomed
   ticket can BE the deferred *Part 2*: its phase-1 commit is shipped, but the ticket
   now covers the remaining work (a common mis-reconcile is parking on
   commit-existence, missing that it had been re-scoped to the remaining endpoints).
   Build the genuinely-missing part.
   If — after reading the current scope — the work is *genuinely all* shipped,
   **don't rebuild it**: move the ticket to **In Review** with a citation comment
   naming the commit (and what proves it shipped), ping, and take the next.
   **Detection is yours; the final close is the dispatcher's** — never self-close a
   phantom to Done. Parking it in In Review lets the dispatcher/human confirm the
   citation (a ~10-second check) and close, which guards against a half-done ticket
   being buried as "done." Five minutes here saves an hour of forensic git
   archaeology — and prevents two workers shipping the same thing.
   - **EXCEPTION — re-queued for a fix (don't bounce it):** a commit can exist AND
     the ticket still be legitimately in Ready, when a human verified the merged
     work, found something off, and sent it **back** to Ready with a fix note. The
     tell: the **latest comment** describes a defect / requested change (often with
     a screenshot), and/or the status history shows **In Review → Ready**. In that
     case the commit is the *original* build, not proof you're done — **read the
     latest comment and do the requested fix.** Do NOT reconcile-bounce it to In
     Review. The rule of thumb: the **newest human instruction wins** over the
     "a commit exists" heuristic.
4. **Branch off the fresh integration branch — in your own worktree.** You run in an
   isolated git worktree, never a shared checkout (see "Worktree & PR isolation").
   Start every ticket from the latest integration branch:
   ```
   git fetch origin dev && git checkout -B proj-<n>-<name> origin/dev
   ```
   **Branch *per ticket* — never commit on your `worker-<name>` home branch.** That
   branch is just the worktree's idle home; it must stay clean at the integration
   branch. Committing work there opens a stray PR from `worker-<name>` (a real
   duplicate-PR failure). Always `checkout -B proj-<n>-<name>` first.
   Then do the work to the ticket's Definition of Done, following the project's
   conventions (stack, migrations, commit rules):
   - **Reuse first** — grep for an existing helper / service / pattern before
     writing new; don't reinvent one that exists; refactor a shared piece when the
     change calls for it.
   - **Write all necessary tests *with* the code** — unit, regression, e2e per the
     project's testing standards. A ticket isn't done without them.
   - **Self-review your own diff** — kill duplication, tighten reuse, drop dead
     scaffolding. Tests gate correctness; this gates *quality*.
5. **Push your branch and open a PR to the integration branch — never push straight
   to it:**
   ```
   git push -u origin proj-<n>-<name>
   gh pr create --base dev --title "PROJ-<n>: <summary>" --body "<what changed + how to verify> — Worker: <name>"
   ```
   **CI runs on the PR.** A red build is now a red PR check — it can't break the
   integration branch for the rest of the team. Fix until the PR is green.
6. **Finish = green PR, handed off for merge.** Move the ticket to **In Review**,
   leave the full verify steps in a tracker comment, and post a **verify** ping with
   the **PR link + a short verify checklist** (what to click / check — so the human
   can act from chat). The steward/human reviews the PR diff and **merges to the
   integration branch** (which deploys). **Do not merge your own PR** during the
   refinement stage. (As the gates earn trust, objective tickets graduate to worker
   self-merge on green — see "Finishing: Done vs In Review".)
7. **Loop — immediately, without asking.** The moment you finish a ticket (PR open
   → In Review), go straight back to step 1 and claim the next top-of-queue ticket.
   **Picking the next ticket is NEVER a question** — it's always the top of `status
   in (Ready, "Changes Requested")`, exactly how you picked the first. Do not stop,
   summarize, or ask the human "which one next?" between tickets. (If you're running
   under a loop harness, treat the gap between tickets as a non-event, not a
   checkpoint.)
   - **Idle backoff — don't burn credits polling an empty queue.** When a pass finds
     **no work** (empty queue for a worker; no mergeable PRs / nothing to reconcile
     for the steward), **double your next poll delay** (base ~15 min → 30 → cap
     ~30–45 min). A pass that **did** work **resets to the base interval**. After
     **sustained idle** (~1 hour of consecutive empty passes at the cap), **stop
     entirely** — write a brief handoff and halt; the human restarts you when there's
     work again (which resets the schedule). The human can always pause manually;
     this only catches the case where they forget and walk away.

**If you yield or release a claim** (an earlier claim won, or the reconcile in
step 3 found it already shipped): comment the release on the ticket, and if you
made **no** code changes, delete the branch/worktree you created so it doesn't
linger. A **bare branch sitting at the integration base commit = abandoned** — any
worker may reclaim the ticket freely without checking whether someone's mid-flight.

## Worktree & PR isolation

Each worker runs in **its own git worktree** (its own working directory on disk),
never a shared checkout. This is non-negotiable: two sessions editing the same
checkout entangle their uncommitted work in the same files — stale reads, clobbered
saves, `git add` sweeping a peer's changes into your commit. A separate worktree
gives each worker a private working copy; git reconciles at **merge**, which is
exactly where it's designed to.

- **Setup (per worker, once):** the human creates a worktree per worker —
  `git worktree add ../workers/<name> -b worker-<name>` — and launches that worker
  session inside it. See `onboarding.md`.
- **Per ticket:** branch off the fresh integration branch (`checkout -B
  proj-<n>-<name> origin/dev`), work, push the branch, open a **PR to the integration
  branch**. Never push to it directly.
- **Why PRs:** CI runs on the PR, so a broken build is a red *PR check*, not a red
  *integration branch* that blocks everyone (the exact failure that bites a
  shared-tree run). The PR diff is also the review artifact for the quality gate.
- **Merge during refinement:** the steward/human reviews + merges PRs. Workers
  don't self-merge yet. As the gates earn trust, objective tickets graduate to
  worker self-merge on green.

## Finishing: Done vs In Review

Every ticket finishes as a **green PR** — the question is *who merges it*:
- **In Review (default, and ALL tickets during the refinement stage):** leave the
  PR open, move the ticket to In Review, ping with the PR link. The steward/human
  reviews the diff and merges to the integration branch → Done.
- **Self-merge (objective tickets only, once enabled):** when the DoD is fully met
  by passing CI and there's **no human-judgment element** (no UX / visual / product
  call), the worker may merge its own green PR → Done. Objective = unit/e2e tests
  that pass, dead-code removal, CI/config bumps. Anything where "does this look /
  behave / feel right?" matters → In Review. When in doubt, In Review.

Never merge on un-run or failing checks.

**Every human handoff (In Review or Needs Input) gets a tracker comment** with a
short description of what changed / the situation **and the exact steps the human
needs** — how to verify it (where to click, what to expect), or the decision / info
required to unblock. Make their job a checklist, not detective work.

## Code quality (not just correctness) — the senior-engineer bar

**The bar is top-tier, not "it passes CI."** Every change should clear review at a
strong engineering shop: clean and readable, **properly abstracted (DRY — but not
*premature*/speculative abstraction)**, no duplication, no dead code, clear naming
and structure, meaningful tests (real assertions + edge cases, not coverage
theater), failure paths handled, security-conscious.

**Green is necessary, not sufficient — the cardinal sin is making a test green by
weakening it.** The goal is *the app actually works, exercised the way a user would
use it* — not a green checkmark.
- A **red test means fix the APP first**, not the test. Relaxing, weakening, or
  deleting an assertion to get green is **prohibited** — never an accepted "fix." It's
  how "fix the app" quietly becomes "delete the evidence."
- **Changing a test is legitimate ONLY when the new behavior is independently
  confirmed correct** (spec / human sign-off / your own eyes) — never as the path of
  least resistance to green.
- **Know what the gate actually checks: the PR's unit suite may NOT exercise the UI.**
  Often only e2e does, and it may run *post*-merge on the deployed dev site rather than
  pre-merge. So a green check on a UI ticket can certify "the code didn't crash," not
  "the feature works" — the behavioral test still has to run, and UX still gets a
  human's eyes on dev (which is exactly why UX goes to In Review). Never read green as
  "done."

**The e2e-acceptance fence — a verify-found defect comes back WITH a passing assertion,
not a human re-eyeballing.** When the steward or owner finds a defect at verify time, the
bounce's acceptance **requires** an automated test (e2e/unit) that *fails on the bug and
passes on the fix*, **in the context that actually runs in CI** — and the test must
actually **PASS**, not merely exist. Prefer an automatable assertion (no console errors,
no overflow, a contract / wall-clock check) over a recurring human eyeball; reserve human
verify for genuine visual "feel" / product judgment that can't be automated. This converts
"the human keeps re-checking" into "CI proves it once" — it catches a still-incomplete
fix (e.g. a layout overflow) that would otherwise have reached the owner as "looks done."

CI gates *correctness* (tests + static analysis); it does **not** catch duplication,
missed reuse, or sloppy structure — those need a real review:

- **First line — workers self-review every diff before pushing** (step 4): run your
  review/simplify pass on your own diff; kill duplication, extract the obvious helper,
  drop dead scaffolding. Cheaper to catch here than at the gate.
- **The gate — the steward runs a code review on EVERY PR before merge.** This is
  mandatory, not a "periodic batch" — purpose-built for reuse / duplication /
  simplification / efficiency. A genuine quality finding (the same block copy-pasted
  N times instead of one helper; a missed reuse; a needless abstraction) **bounces
  the ticket to Changes Requested with the specifics — exactly like a missing
  test.** An objective PR is NOT auto-mergeable until it's clean, not just green.
  Calibrate to *real* issues, not nitpicks or premature abstraction. For a deeper
  pass, spawn a code-reviewer subagent on the diff.

- **Refactor as first-class work.** Senior engineers refactor as they go. When a
  change reveals structural debt — the same logic in a third place, a god-object, a
  leaky abstraction — **surface it to the planner** (a tracker comment on the related
  ticket, or a brief `tech-debt`-labelled stub for the planner to groom) the moment
  you see it. If a change *needs* a refactor to land clean, do the **refactor
  first**: the dispatcher schedules it ahead of the feature — never pile features on a
  shaky foundation. Boy-scout rule: leave touched code cleaner than you found it.
- **The planner owns the backlog — don't open parallel tickets.** Creating, scoping,
  grooming, prioritizing, promoting to Ready, reconciling, and closing-as-
  superseded/duplicate are the **planner's** job. Workers and the steward **route
  ticket-worthy findings to the planner** (tracker comment / Needs Input / a labelled
  stub) rather than authoring and scoping their own — one owner keeps the backlog
  coherent. (When two sessions both file for the same work you get duplicates the
  planner then has to dedup.) The steward still *closes* In Review → Done on the
  QA/merge axis (that's sign-off, not backlog management); filing a quick stub in a
  genuine pinch is fine, but the planner reconciles and grooms everything that lands.
- **Sensitive code never auto-merges — regardless of green CI.** Auth, security, DB
  migrations, billing/money, and data-deletion get a **human or a second adversarial
  review** before merge, even when objective and tested. The blast radius is too
  large to gate on tests alone — route these to In Review with a chat ping, don't
  self-merge.
- **UX changes DO get merged to the integration branch — they just don't auto-*close*.**
  A complete, green UX/visual PR (not sensitive) should be **merged** so the owner can
  verify it on the deployed dev site (when there's no preview deploy), and the ticket
  left **In Review** with a verify ping. The owner verifies on dev → Done (or →
  Changes Requested if off). **Do NOT freeze a UX pile unmerged** — that's integration
  debt *and* the owner can't even see it to verify. Only *incomplete* PRs (missing DoD
  tests / red CI) and *sensitive* code (above) wait for a pre-merge human review;
  everything else flows to the integration branch.
- **A red-CI / failing PR is ROUTED BACK to the workers — never parked or pondered.**
  When a PR's CI is failing (or it's CONFLICTING and won't merge), the steward
  **posts the failing check + the error on the ticket**, moves it to **Changes
  Requested**, and posts a brief chat FYI (no @-mention — it's a code fix, worker
  work, not a human judgment call). A worker re-claims and fixes it. Never merge a
  red PR; never sit on one "thinking about it." See it red → report it → send it back.
  **The steward writes the bounce — repro + root cause + crisp acceptance (including
  the required test, see *the e2e-acceptance fence* above) + evidence — but does not
  implement the fix; the keystrokes are the worker's.** (Carve-out: a live prod-security
  hole with workers down + an explicit dispatcher go.)
- **Keep styling and scripts in their own files — never inline in templates.** Follow
  the project's component/class conventions; avoid inline `<script>`/`<style>` blocks
  and raw *arbitrary* utility classes that don't compile into the committed stylesheet
  and render unstyled. Enforce via CI where you can.
- **Design-lens on non-trivial PRs.** A local review pass catches local cleanups; for
  anything structural, **spawn a code-reviewer subagent with a senior/staff lens**
  ("is this the right abstraction and layer? painful to live with later?"). Catch
  design mistakes, not just messy lines.

We're in a **refinement stage**: the extra independent review is a *calibration
scaffold* while we tune the gates (tests, static analysis, self-review, reviewer
agent). As they earn trust — catching what they should, with few escapes — we dial the
extra review back toward gates that run on their own. Going faster is only safe once
the gate is trusted; until then, keep the eyes on.

## Working disciplines (from the worker retros)

- **Confirm, don't infer.** When the cost of certainty is one command, pay it.
  Can't run a DB-backed test locally? Don't reason "CI is green so my test passed"
  — **grep the CI log** for that suite / test count. (A combined job can run static
  analysis *and* the whole suite — but confirm yours ran, don't assume.)
- **A dedup hit is a stop sign.** If a search surfaces an existing ticket for work
  you're about to file *or* park, that's a signal you're about to duplicate or
  mis-park — **resolve into that ticket**, don't file alongside it.
- **Front-load environment + creds discovery at session start** — *before* reaching
  for interactive auth. Check the env for existing tracker/host credentials before
  kicking off an OAuth flow; read the platform (e.g. Windows may lack `python3` /
  `jq` / `node` — use an HTTP/CLI pattern from your project's playbooks). Don't
  re-derive the plumbing every ticket: prefer your project's CLI wrapper + a
  known-good recipe.
- **Two plumbing gotchas that eat 20 minutes if you don't know them** (the tools
  WORK — these are read/resolution quirks, not failures):
  - **`gh` can't auto-resolve the repo inside a git worktree** → always pass
    `--repo <org>/<repo>`. A bare `gh pr list` returns *empty*, not an error, so it
    looks like "no PRs" when there are plenty.
  - **A *background* command's output can read as empty (encoding) even though the
    command succeeded and the data is there.** Don't pipe-to-file-then-read-wrong. Run
    the tracker/`gh`/`curl` call in the **foreground** (output returns decoded inline),
    or read the captured file with a tool that handles the encoding. A search returning
    "empty" is often a read-the-capture-wrong bug, not a broken query.
- **Work against `origin/<integration-branch>`, never a stale local tree.** The
  local/shared checkout lags origin: `git ls-files` / `git grep` with **no ref** read
  the *stale* tree and report merged files as MISSING, and a commit on stale local can
  silently **revert shipped work**. `git fetch` first, then be explicit — `git checkout
  -B <b> origin/dev`, `git grep <p> origin/dev`, `git show origin/dev:<path>`. Same
  family as *never act on stale state*.
- **Stage explicit paths — never `git add -A` / `git add .`.** Worker worktrees
  accumulate untracked machine/tool artifacts (e.g. an assistant config file sitting
  untracked across worktrees), and `git add -A` sweeps them into the PR and bounces it.
  `git status --short` before every commit; one PR = one concern.
- **Check live worktrees, not just claim comments, before real work.** A peer can
  have a complete, *uncommitted* implementation in a `git worktree` with no claim
  comment yet. `git worktree list` + `git diff` any matching worktree; if a peer
  has in-flight edits to the same files, **yield** rather than collide/redo.
- **Never move a ticket *backward* — re-check its status before any transition.** A
  lagging or parallel session can bounce an already-**Done** ticket back to In Review
  on a late handoff (a real failure: a hours-late PR handoff re-opened a ticket the
  steward had already signed off — making the board look like pending work that
  wasn't). Before transitioning a ticket (e.g. to In Review on handoff), **re-fetch
  its current status**; if it's already Done or further along than your action
  assumes, **leave it** — the work is accepted. Same family as
  re-verify-before-claim: never act on stale state.
- **Bundle an adjacent change only if the ticket's symptom can't resolve without
  it** — otherwise file a linked follow-up. And prefer the *general* fix over a
  per-instance patch (e.g. fix the upsert's handling, not just one key). When you do
  bundle, keep it a separable commit and say why in the PR.

## Steward sign-off (In Review → Done, without the human)

> **Verification + CI gate are STACK-SPECIFIC — see your project's conventions.** This
> coordination layer ports unchanged across projects, but *what "verified" means* does
> not. A web app whose e2e suite runs against a deployed dev **site** can have its
> steward auto-close; a mobile app has no site equivalent — the app runs on a
> **device**, so **device verify is the real close gate**, the autonomy dial sits
> **lower** by design, and the CI gate differs (e.g. type-check + unit + mobile-e2e
> vs. unit + static analysis). Read the sign-off rules below as the *shape*; your
> project supplies the *reality*.

**Drain each pass — don't dribble one item per wakeup.** A pass is not "handle one PR
and sleep." Each time you wake, process **every** mergeable PR and **every**
sign-offable In Review item — *loop until there's nothing left to do this pass* — and
only **then** back off. Clearing one item per wakeup lets the pile grow between sleeps;
the sleep cadence is for **idle gaps**, not for pacing through a full queue. **Sleep is
ONLY for when the queue is empty or every remaining item is genuinely *blocked*** (a
human decision, external CI, or a PR that must land first) — never to defer *doable*
work to a later tick, which just adds latency. ("Don't lower the QA bar" ≠ "stop while
unblocked work remains" — doing a PR now vs. in 25 minutes doesn't change the care you
apply to it.)

**Every pass = full-board sweep FIRST, then drain cheapest-first.** The failure mode
here is rarely *idleness* — it's working **depth-first while breadth piles up**: pouring
a whole pass into one hard ticket (or a conversation) while cheap green PRs accumulate
unreviewed, and *parking objective work in the human's In Review queue* so your lane
looks empty when it's actually full. Counter it **structurally**:

1. **Open every pass by sweeping the WHOLE board before drilling into anything.** Pull
   *all* open PRs and *all* In Review / Changes Requested, build the work list, *then*
   work it. Your scheduled-wakeup prompts must say **"sweep everything,"** never a
   named-ticket watchlist — a narrow prompt makes you follow the thread you already know
   and miss new arrivals.
2. **Cheapest-first; cap deep reviews at one per pass.** Merge trivial green PRs (deletes,
   docs, test-only, mechanical) immediately. Every PR still gets the standard review, but
   reserve **at most one** pass-slot for a heavy *adversarial* review (the big-subagent
   kind); if more queue, drain the cheap breadth first or run the heavy review in the
   **background** while merging. One hard ticket must never monopolize a pass while green
   PRs wait.
3. **Default In Review to "mine to close."** Assume an item is objectively closeable
   (tests green on dev / mechanical correctness / behavioral e2e) and make yourself
   *justify routing it to the human* — not the reverse. Only genuine **aesthetic or
   research-judgment** goes to the human. **Stack caveat:** where the verification gate is
   weak (no e2e, sparse coverage — per the project's conventions), UI/behavioral work
   still needs human eyes *or a new e2e/visual-regression test* until that coverage
   exists; the dial **rises as the gates grow**. Mechanical/objective work closes
   regardless.
4. **Backpressure trigger.** If open-PR count grows pass-over-pass, *or* the oldest open
   PR ages past ~1 hour, that's an explicit "I'm behind" signal: **drain hard**, and ping
   the human only if you genuinely can't keep up. Waking *more often* does NOT fix a
   per-pass-completeness problem — it just burns cache. The fix is always: **every pass =
   full sweep + drain to empty + close what's yours.**

The steward MAY sign a ticket off itself — In Review → Done — when **all four** hold:
1. **DoD met by checks that actually ran GREEN ON DEV** — not just a green PR check
   (a PR unit suite proves nothing about behavior — see the cardinal-sin rule). For
   anything **user-facing**, an **e2e spec exercised it and passed on the post-deploy
   dev run**.
2. **No aesthetic / UX / product judgment** in play (look, feel, layout, copy, colour,
   information design).
3. **Coverage is real** — asserts the observable outcome + the critical/negative case,
   not theater.
4. **Evidence cited on the ticket** (the *verification ledger*) — test names + e2e
   `spec:line` + the dev run id — as a reopen anchor.

**Always stays with the human (never auto-signed):** aesthetic / visual judgment
("does it *look* right"); product / scope calls ("is this the right behavior");
first-time **live integrations** the tests can't exercise (a real billing webhook,
a real OAuth round-trip); and **prod promotion of sensitive code** (auth / billing /
migrations / data-deletion) — closing a *dev*-verified ticket is fine, pushing to the
**production branch** stays human-gated.

**The loop (workaround until e2e runs pre-merge):** merge the green **objective** PR →
watch the dev deploy + e2e → **green ⇒ sign off** (close with the evidence) / **red ⇒
bounce** to Changes Requested. The *merge* is not the sign-off; the **dev e2e** is.
This is what resolves "can't verify until merged."

**The UI split is behavior vs. aesthetic — NOT "all UX → human."** If a UI ticket's
*behavior* is e2e-verified on dev, the steward signs it off; only the *"does it look
right"* aesthetic judgment goes to the human. (Lumping all UX onto the human is what
parks closeable work.)

**Batch-merge hygiene:** rebase + re-check each PR on the *accumulating* integration
branch before merging — a clean PR can break once peers land (a hot-file collision); a
deploy concurrency group keeps a batch of merges from thrashing dev e2e.

**`gh` CLEAN is necessary but NOT collision-safe — preview the real merged tree before
every merge.** `gh`'s `mergeable: MERGEABLE` / `mergeStateStatus: CLEAN` only means "no
textual conflict markers." It misses **semantic collisions**: two PRs that each *add* the
same line (→ a duplicate `import` after merge), or one that changes a model the other was
sized against (→ a behavioral seam) — both report CLEAN and both pass CI alone, yet break
together. Cheap guard, run on **every** merge:
```
git merge-tree --write-tree origin/dev <branch>               # inspect the ACTUAL merged result for dupes/breakage
git merge-base --is-ancestor <recent-relevant-merge> <branch>  # based on the recent merge, or stale?
```
Sequence tickets that touch the same hot file rather than parallelizing them, or require a
rebase-on-integration-branch immediately before handoff. Applies to the steward **and**
any self-merging session.

**Raise your hand if you're backing up — flag, never silently degrade.** The steward
is the only QA gate while we test whether one suffices. If PRs awaiting QA grow
pass-over-pass (arriving faster than you clear them), or the oldest unreviewed PR has
waited 2+ hours, **do NOT rubber-stamp to keep up** — post to chat, @-mention the
owner with the count waiting + the oldest's age + a recommendation (parallel QA help /
a dedicated reviewer). Same if one PR is too big to QA well solo. A self-reported
backlog is the signal to add capacity; a *silent* backlog is how the bar quietly drops.

## Retrospective at handover — the self-improvement loop

When you reach a stopping point or hand off (queue empty, context limit, end of
session, or told to stop), **write a session handoff that includes a real
retrospective** — *What went well · What didn't · What I'd change · Process gaps*.
This isn't a formality; it's the recurring retro that keeps the system honest.

The loop only closes if lessons travel beyond one handoff:
- **A ticket-specific lesson** → the handoff (the next worker reads it).
- **A *process* gap — a flaw in this protocol, the playbook, or the tooling** →
  surface it: file a `process`-labelled ticket or flag the dispatcher/steward to encode
  it into the shared docs. A lesson that lives in only one handoff dies there.
- **A lesson that likely generalizes *beyond this project*** → label the ticket with a
  cross-project label so a docs session can pull and synthesize it. If a worker session
  can't write to the shared docs repo directly, the label *is* the transport — a docs
  session pulls those labels and synthesizes. Write the lesson in the candidate schema
  (Target · Rule · Provenance · public?) so it's ready to cluster. The promotion bar is
  **convergence** — it becomes canonical when a second independent source confirms it, or
  a human blesses it.
- **Periodically the dispatcher/steward synthesizes** recent handoff retros: recurring
  pain → a protocol/playbook edit. That's how the team improves without a human
  hand-editing every rule.

The *code*-quality retro (run at every PR/commit, not just at the end) lives in your
project's checkpoint checklist.

## Chat pings (the activity feed)

**Naming convention — always write `PR #NN (PROJ-NN)`.** Spell out "PR" and pair it
with its ticket in every comment, ping, and handoff. A bare `#59` reads as *ticket 59*
to a human scanning the tracker. `#NN` = pull request; `PROJ-NN` = tracker ticket;
never leave a bare `#NN` to stand alone.

Workers post to chat via an **incoming webhook** (one-way: post only, can't read
replies). The URL is in `$TEAM_SLACK_WEBHOOK` per machine — never commit it.
**@-mention the owner only when you need them** (verify / blocked); starts and
self-closes are FYI with no @-mention, so the channel stays readable without
paging the human on every step. Prefix every message with your name. Post to
your team's coordination channel (e.g. `#your-coordination-channel`).

| Event | When | @-mention? | Example text |
|-------|------|-----------|--------------|
| **start**  | on claim (→ In Progress) | no  | `:arrow_forward: <name> started <KEY> - <summary>` |
| **done**   | self-closed (→ Done)     | no  | `:white_check_mark: <name> <KEY> done + closed - CI green, no review needed` |
| **verify** | → In Review              | yes | multi-line: one-liner **+ a short `Verify:` checklist + ticket/PR link** (example below) |
| **blocked**| → Needs Input            | yes | `@owner :warning: <name> <KEY> needs input - <question> - answer on the ticket: <ticket-url>` |

Use chat **`:shortcode:` emoji** (`:arrow_forward:` `:white_check_mark:` `:mag:`
`:warning:`) and plain **ASCII hyphens** `-`, never raw Unicode emoji or em-dashes
(`—`) — those can arrive as `?` through the webhook.

**Don't inline-quote complex payloads from the shell — write them to a temp file and pass
`--data @file`.** Single quotes or a bare `<word>` inside a single-quoted `curl --data`
break it (quote-break / stdin-redirect); **backticks** inside a double-quoted comment
trigger command substitution and silently drop words. For JSON (rich tracker comments,
chat blocks), build it in a small script and POST from the file, or keep inline payloads
strictly plain — no quotes, `<>`, or backticks.

The **verify ping carries the short verify checklist itself** (multi-line — most chat
renders `\n`), so the human can see *what to check* and act without clicking through.
Keep it to the 2–4 key steps; the FULL description/steps still live in the **tracker
comment** (durable, and what the resuming worker reads). Always include the **ticket
URL** + **PR link** on the actionable pings. Example verify ping:

```
@owner :mag: worker-a PROJ-186 ready to verify - live result preview - CI green
   Verify: open the formula builder -> build "Revenue (28d) / Ad Spend" -> confirm the live preview shows a $ value, and that it clears (dash, not error) on divide-by-zero. Light + dark.
   Ticket: https://<tracker>/browse/PROJ-186  |  PR: <pr-url>
```

**Chat is one-way** — a reply in chat does **not** reach the tracker. The human answers /
verifies on the **ticket** (and merges the PR); chat just tells them what + where.

**Consolidate verify pings into one rolling recap once the owner-verify pile exceeds ~3.**
Merge ≠ Done — the owner's visual/device/product verify is a separate gate, so the steward's
*Done-throughput is capped by the human's verify time* (expected, not a backlog failure).
Past ~3 pending, switch from per-ticket pings to **one rolling, documented recap** (start it
early, at ~3, not when it's a pile), and bundle items on the **same surface** into a single
verify pass.

```bash
curl -s -X POST -H 'Content-type: application/json' \
  --data '{"text":"<message from the table above>"}' \
  "$TEAM_SLACK_WEBHOOK"
```

### Owner mapping (who gets @-mentioned, keyed by project)

Maintain a small table mapping **each project (tracker key) to its owner's chat
handle**, and @-mention that owner on the actionable pings (verify / blocked) for
that project:

| Project (tracker key) | Owner       | Chat mention |
|-----------------------|-------------|--------------|
| PROJ                  | the owner   | `@owner`     |
| ...                   | ...         | ...          |

If a ticket names a different owner/assignee, tag them instead. (Most chat tools expose
a stable member ID via the user's profile menu — use that, not a display name.)

## When you're blocked (need a human answer)

You **cannot** hear a chat reply — the webhook is one-way and a worker has no
background listener. So never wait.

**Never pause on an interactive question, and never idle.** You're autonomous —
the harness will offer to ask the human inline, but that traps the decision in
your session and stalls you. Route **every** decision the same way: a genuine
scope fork, a product/UX judgment call, *or discovering a Ready ticket is actually
mis-scoped / epic-sized / blocked by a file collision with a peer*. The analysis
you'd put in an interactive prompt is exactly right — just put it in **the tracker**
instead and move on.

Hand off through the tracker, which the next worker reads on resume:

1. **Post a tracker comment on the ticket** — the durable answer channel. Include a
   short **description** of the situation, the specific question, and the **steps /
   decision / info needed** to unblock (offer options where you can). Make it a
   checklist, not detective work.
2. **Move the ticket to Needs Input** so no worker re-grabs it until a human
   answers.
3. **Chat-ping** the owner so they know which ticket to look at.
4. **Stop** working it. Take the next **Ready** ticket, or stop if none.

The human answers in the **tracker comment** and moves the ticket back to **Ready**.
The next worker re-claims it, reads the answer, and continues — no need to return
to any specific session.

## Guardrails (hard rules)

- **Only pick from the Ready queue.** Never grab epics, planning tickets, or
  flagged refactors (e.g. a project-wide terminology rename) — those stay in To Do.
- **Never merge to the production branch** — that's a human-gated step after
  verification.
- **Never** skip hooks, force-push, or amend. No AI attribution in commits — but a
  neutral `Worker: <name>` sign-off trailer is fine (see Worker identity).
- One ticket at a time per worker; move it to In Review before claiming the next.
- Migrations + stale PRs: a PR's base goes stale while it sits, so its migration
  number can collide with one merged meanwhile. If the runner keys on the unique
  *filename*, a number clash is cosmetic — but renumber it anyway for a clean tree.
  **The steward rebases a PR on the fresh integration branch before merging** —
  mandatory if it adds a migration or has been open more than a few hours — and
  renumbers a colliding migration. **Don't let PRs rot:** a long-open PR is drift
  waiting to conflict — merge it promptly or send it back. Follow your project's
  migrations README.

## Per-project specifics

Deploy model, CI shape, and migration conventions live in each project's own docs.
A project may keep a local copy of this protocol that defers to this doc as the
cross-project source of truth.
