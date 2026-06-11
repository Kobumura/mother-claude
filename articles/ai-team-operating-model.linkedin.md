LINKEDIN VERSION -- "A Self-Coordinating AI Dev Team: The Operating Model"

How to use: paste the text below into a LinkedIn *Article* (Write article), bold the
section titles in the editor, and set the 20-second "antiquated and weak" clip as the
cover/lead media. No Markdown -- it's already plain text. (For a short native *post*
instead, lead with the clip + the first three paragraphs and link the article.)

==================================================================

Good morning, Angels.

"Your methodologies are antiquated and weak. Your procedures of approval ensure that only the least radical ideas are rewarded. Meanwhile your competition is innovating."
-- Alex, Charlie's Angels

A human manually approving every change IS that procedure of approval: the slowest, least radical path. So we stopped making humans the packet routers in the middle of every operation. We run a team of autonomous AI coding agents instead, and keep our own hands on the two things that genuinely need a human -- deciding what to build, and confirming it's right.

Here's the thesis, with everything below as the proof: the agents aren't coordinated by intelligence. They're coordinated by structure.

By the numbers: in the past week the team landed code on 52 tickets in a single repo -- every one a real PR through CI -- while we spent the week at product altitude. That's an ordinary active week, not a stunt: the model has been running in sprints like it for months.

The core idea

We become the bottleneck the moment we hand-carry packets between agents -- relaying questions, copy-pasting status from one terminal to another, reviewing and merging every change by hand. So we push the mechanical work -- coordinating, reconciling, merging, keeping the queue fed -- onto the agents, and reserve ourselves for the two things only a human can do: deciding what to build, and judging whether it's right.

Four roles

- Workers (several, autonomous loop): drain the task queue, open pull requests.
- Dispatcher (one, interactive, with the human): spec features into well-formed ready tasks. New work IN.
- Steward (one, autonomous loop): merge objective PRs, reconcile the board, clear the review column. Existing work THROUGH.
- Human: product direction and final verification.

The flow in one line: the dispatcher feeds the queue, the workers drain it, the steward moves it through, and the human decides and verifies.

The cast, if it helps the roles stick. "Once upon a time there were three very different little girls who grew up to be three very different women with three things in common: they're brilliant, they're beautiful, and they work for me. My name is Charlie." The workers are the Angels -- the operatives who run the missions. Charlie is the dispatcher -- the voice on the speaker handing out the assignments: "Good morning, Angels." Bosley is the steward -- the handler in the field who reviews every finished mission and brings it home.

The issue tracker is the coordination layer

No agent messages another directly. They coordinate entirely through task status in the shared tracker, which doubles as the work queue:

Backlog → Ready → In Progress → Needs Input → In Review → Changes Requested → Done

- Ready: fully specified, with a clear Definition of Done. Workers pick only from here (and Changes Requested). This is the gate.
- Needs Input: a blocked worker parks it here with its question; the steward or human answers in a comment and it returns to a pickable state.
- In Review: change is green in CI, awaiting a human or steward decision.
- Changes Requested: already shipped, but a reviewer wants a fix. A worker re-picks it, skips the "is this already done?" check (an existing commit is expected), reads the latest comment, and does the fix.

The life of one task

1. Human and dispatcher spec a feature into a self-contained ready task: context, scope, acceptance criteria (including the tests expected), and pointers -- with the scope written in the description, not buried in a comment.
2. A worker claims the top of the queue (claim first, then reconcile, then build), working in its own isolated checkout on a per-task branch.
3. The worker opens a pull request; CI runs on it.
4. The steward reviews the green PR. Objective and complete (logic plus the required tests) → auto-merge → Done. Visual, incomplete, or a judgment call → route to Changes Requested or leave in review, and ping the human with exactly what to verify.
5. The human verifies the escalated few; the steward closes them out.

How they avoid colliding

- Task status is the single source of truth for "what to do."
- Claim-first: the earliest claim comment wins.
- One isolated checkout per worker, one branch and PR per task: no entangled edits; version control reconciles at merge, which is exactly where it's designed to.
- A one-way chat feed: the steward posts FYI summaries each pass and pings the human only when they're genuinely needed.
- A lean standards core at startup, the depth on demand: every agent loads a small always-on core; the per-area detail is pulled in only when a task touches it, never dumped into every context.

The trust dial

Treat it as a refinement stage. The steward auto-merges objective work but escalates anything visual or product-shaped to the human. As the gates prove they catch what they should, more work graduates to fully autonomous. Visual and product decisions stay with the human indefinitely.

The electric fences

The pasture this worker hive grazes in is ringed with electric fences.

That's the part that makes it safe to turn them loose. The agents roam freely inside the field -- but the field is fenced by an exhaustive set of guardrails they cannot cross, enforced at the gate: CI, a pre-push hook, and the Steward's review.

- Engineering: reusability (reuse what exists, never duplicate it); separation of concerns (no god files, no business logic in the UI); type safety; no dead code.
- Testing: required tests ship with the code; no zero-assertion tests; mutation testing on the money-path services; contract tests against the API.
- Design: design tokens only; an accessibility budget.
- Security: no secrets in code; auth patterns off-limits to casual edits; dependency vulnerabilities scanned on every PR.
- Deployment: CI green, the right branch, never a shortcut to prod; sensitive code never auto-merges; migrations validated against the live schema; performance budgets.

And the fence line keeps growing: every incident that teaches us a new failure mode becomes a new wire the next morning.

Here's the load-bearing part: the fences aren't left to the grazers to respect on the honor system. The workers adhere to them -- and the Steward independently re-verifies that adherence before anything merges. Adherence is the worker's job; verification is the Steward's. That second, independent check -- not the agents' good intentions -- is what lets the trust dial climb without the work going feral.

Why it works

A smarter model doesn't solve coordination -- structure does. Verification solves trust, isolation solves collision, workflow solves ambiguity. It's about a shared source of truth (the tracker), isolation (a checkout and branch per agent), a review gate (PRs and CI), a clear escalation path (objective work flows on its own; judgment goes to the human), and the fences (guardrails the agents can't cross, independently verified by the Steward). Get those five right and the team mostly runs itself -- the human moves up to deciding what to build and confirming it's good, which is the only place they were ever irreplaceable.

Strip away the costumes and it's a familiar shape: a scrum team -- a backlog, a board, standups by status, reviews, a definition of done. The teammates just resolve their differences quickly and quietly, and -- every so often -- get zapped by the fence.

But the point was never autonomous coding. The agents write the code; the structure keeps them from stepping on each other; the human stays at product altitude -- deciding what matters, and confirming it's right. That's the operating model.

Good work, Angels.

--

The patterns, the agent definitions, the session hooks, and a live multi-AI "roundtable" tool are open source: github.com/Kobumura/mother-claude (CC BY 4.0). Fork it, adapt it, or use it as a reference for your own setup.
