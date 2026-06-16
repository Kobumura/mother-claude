# Onboarding a Machine to Run Claude Workers

Setup steps so a teammate's machine can run autonomous Claude "worker" sessions
that drain a project's `Ready` queue and post verify pings to Slack. The behavior
they execute is defined in `agent-worker-protocol.md`; this doc is just the
one-time machine setup plus how to drive it.

## Prerequisites

- A local clone of **your shared docs repo** (the repo holding these framework
  files) — the workers read shared standards from it. **It does NOT have to sit
  next to the project repo**: set `setx SHARED_DOCS <repo-path>` once per machine
  and every tool resolves it (resolution order: explicit param > `team.config.json`
  > `$env:SHARED_DOCS` > sibling-folder guess).
- The project repo cloned, with Jira access (the `jira` CLI working).
- The Slack incoming-webhook URL for the team's verify channel (get it from the
  owner — sent privately, never in a public channel or git).

## Preflight — make the PROJECT team-ready (once per project, not per machine)

Machines are onboarded once; projects also need a one-time readiness pass before
the first team launch. `team-up.ps1` verifies #1 and #2 automatically and refuses
to launch on a board that can't run the claim loop.

1. **The Jira board must carry all seven statuses** — `To Do, Ready, In Progress,
   Needs Input, In Review, Changes Requested, Done` (exact names; the protocol's
   JQL matches on them). New team-managed projects ship with only To Do / In
   Progress / Done. Add the missing four via the board UI (Board settings →
   Columns), or via the API: create the statuses with
   `POST /rest/api/3/statuses` scoped to the project, then add them to the
   workflow with global transitions via `POST /rest/api/3/workflows/update`
   (validate first with `/workflows/update/validation`; existing statuses must
   carry their `id` in the payload's top-level `statuses` block).
2. **Decide the Slack channel and webhook variable.** Two valid patterns: a
   **dedicated channel per project** (e.g. `PROJ_SLACK_WEBHOOK`) when one owner
   runs several concurrent teams and wants to scan them separately, or a
   **shared channel/webhook across sibling projects** (e.g. one webhook for an app
   plus its API) when the projects form one product. Record the chosen env-var
   name in `team.config.json` (`slackWebhookVar`) **and** the project's
   `CLAUDE.md`; default is `TEAM_SLACK_WEBHOOK`.
3. **The Jira project key lives in ONE place** — the project table in your shared
   docs repo's `CLAUDE.md`. `team-up.ps1` looks the key up there by repo folder
   name; don't re-declare it in per-project configs unless overriding. Onboarding
   a new repo = add its row to that table first.
4. **Declare the integration branch in the project's `CLAUDE.md`.** The protocol
   docs say "dev" generically, but the real branch is per-project (some projects
   use a long-lived feature branch their dev site deploys from). The declaration
   must name: the branch worker PRs target, what deploys from it, and the
   production branch that is **never** touched autonomously.
5. **CI must actually run on PRs targeting the integration branch.** Check the
   workflow's `pull_request.branches` list — if the integration branch isn't in
   it, worker PRs show *no checks at all* and the merge gate is blind (a common
   trap: PRs only trigger CI for `main`/`develop`). Fix CI before launching
   workers, not after.

## One-time setup

**1. Update the shared docs** (so the machine has the latest protocol):
```powershell
cd <repo-path>
git pull
```

**2. Set the Slack webhook env var** (persists for future terminals) — use the
variable name the project chose in Preflight #2 (`slackWebhookVar` in
`team.config.json`; default shown):
```powershell
setx TEAM_SLACK_WEBHOOK "PASTE_THE_WEBHOOK_URL"
```
`setx` affects *future* processes only — not already-open terminals.

**3. Restart so both take effect** (the step people miss):
- The env var only reaches a process started *after* `setx` → close & reopen your
  terminal, and fully quit + relaunch Claude Code.
- The shared docs are read at *session start* → start a **fresh** Claude session
  (not a resumed one) so it loads the updated docs.

**4. Verify** (run in the new terminal; replace the ID with yours):
```powershell
Invoke-RestMethod -Uri $env:TEAM_SLACK_WEBHOOK -Method Post -ContentType 'application/json' -Body '{"text":"<@YOUR_SLACK_ID> webhook test"}'
```
A message that lands and tags you = wired. Empty/error = the terminal or Claude
wasn't restarted after `setx`.

**5. Install the auto-refresh hook** (so the shared docs update without you lifting
a finger): add a `SessionStart` hook to your **user** settings
(`~/.claude/settings.json`) that pulls the shared docs repo before every session.
Merge it in (keep any existing hooks):

```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [
        { "type": "command", "shell": "bash",
          "command": "git -C \"/ABSOLUTE/PATH/TO/your-shared-docs\" pull --ff-only --quiet 2>/dev/null || true",
          "timeout": 30 }
      ] }
    ]
  }
}
```

Replace the path with your clone's absolute path. Now every new Claude session
pulls the latest shared protocol *before* reading it — so when the owner changes
the protocol, you just get it; there's no "go refresh" step. (This automates step 1
from here on.)

## One-command launch (the `team-up` script)

Once the prerequisites above are done, you don't have to open and prompt each
session by hand. From your **project repo root**:

```powershell
pwsh <repo-path>/team-up.ps1
```

It creates a git worktree per autonomous role and opens a terminal tab for each —
the **dispatcher**, the **steward**, and your **workers** — booting each with its
prompt. **The first run takes no input**: it uses a default team and writes a
`team.config.json` you can edit afterward to rename anyone or change the worker
count. Later runs read that config (your edits stick). Prefer to drive it by hand?
The per-role prompts are below.

## Give each worker its own worktree (do this first)

Workers must NOT share a checkout — that entangles their uncommitted work. Create
one **git worktree per worker** and launch that worker's session *inside* it:

```powershell
# from the main repo clone, once per worker — namespaced per project so the
# same worker names can be reused across projects:
git worktree add ..\workers\<project>\worker-a -b worker-a
git worktree add ..\workers\<project>\worker-b -b worker-b
git worktree add ..\workers\<project>\worker-c -b worker-c
```
(`team-up.ps1` does this automatically, using the repo folder name as `<project>`.)
Then open a terminal tab per worker, `cd` into that worker's worktree dir, and
start Claude there. (Remove a worktree later with
`git worktree remove ..\workers\worker-a`.)

> **Shared deps → dep-installs are owner-gated.** If worker worktrees **share**
> installed dependencies (a junction/symlink to one `node_modules`/`vendor` so
> tsc/jest/phpunit resolve against a single install), then a worker running
> `npm install <new-dep>` (or `composer require`) mutates that shared tree **for
> every worker** — a shared-state change no worker can safely make. So any ticket
> that needs a new dependency is **owner-gated**: the owner installs once from the
> main checkout, then the dependent ticket goes Ready. Screen DoDs for "needs a new
> dep" before promoting (it's point 2 of the pre-groom screen in
> `agent-worker-protocol.md`). Alternative: give each worker an **isolated**
> `node_modules`, which removes the gate entirely at the cost of disk + install time.

## Running workers

Paste this to the Claude session **running in that worker's worktree**, replacing
`<KEY>` with the Jira project key (e.g. `PROJ`):

> You are worker **<NAME>** (e.g. worker-a), running in your own git worktree.
> Follow `CLAUDE.md` and your shared docs repo's `agent-worker-protocol.md`. Loop
> on **<KEY>**: pull the **Ready** queue (`status = Ready`, top by priority then
> Rank); **claim the top FIRST, before evaluating it** (`claim: <NAME> · session
> $CLAUDE_CODE_SESSION_ID` comment + move to In Progress, re-read comments, yield if
> an earlier claim isn't yours) and post a Slack **start** ping. Branch off fresh
> dev (`git fetch origin dev && git checkout -B proj-<n>-<NAME> origin/dev`), then
> do it to its Definition of Done — **reuse existing code (grep before writing new),
> don't duplicate**, write all tests (unit / regression / e2e) **with** the code,
> and **self-review your diff**; sign commits `Worker: <NAME>`. **Push your branch
> and open a PR to dev** (`gh pr create --base dev`) — never push to dev directly;
> get the PR's CI green. **Finish:** move the ticket to **In Review** with a Jira
> comment (what changed + how to verify) and a **verify** ping (@owner + **a short
> Verify: checklist of what to click/check** + PR link + ticket URL); do NOT merge
> your own PR. If blocked or you find the ticket is mis-scoped, move it to **Needs
> Input**, comment the question/decision needed, ping, and move on — **never pause
> on an interactive prompt.** Then take the next. Stop when **Ready** is empty. Use
> `/loop`.

The name is optional — if you launch without one, the worker uses its session id.
It only matters that each concurrent worker has a *distinct* handle.

> **Relaunching a halted worker is a human action — there's no programmatic
> respawn.** A worker that hit its idle-stop just needs a fresh `go` in its tab. A
> backgrounded `claude` hangs without a TTY and `claude -p` runs once without
> looping, so the dispatcher/steward **can't** wake it — they can only flag you.
> Watch for the halt-vs-refill race (Ready non-empty but no In-Progress claims) —
> see *Known failure modes* in `operating-model.md`. A scheduled cloud agent
> (`/schedule`) makes a good watchdog for it: it runs independent of the halted tabs
> and pings you to restart your engines.

## Running the dispatcher

Paste this to the **dispatcher** session (the interactive command-center; runs in
the main checkout, not a worktree). Replace `<KEY>`:

> You are the **DISPATCHER** (name optional) for project **<KEY>** — the
> interactive command-center; you assign and route the work. Read `CLAUDE.md` and
> your shared docs repo's `agent-worker-protocol.md`. Keep the team unblocked
> without overstepping product direction. **Loop on the board:** each pass, check
> **Needs Input** — if an item is a scope / sequencing / reconciliation question you
> can resolve, answer it (comment + move back to **Ready** so a worker resumes); if
> it's a genuine product / priority / UX decision, **surface it to the owner** with
> a clear recommendation, don't decide it. Keep **Ready** fed only with well-specced
> tickets (scope in the description, tests expected, DoD clear). **Flag the owner**
> if Ready runs empty / workers starve or **Changes Requested** piles up. Don't
> auto-promote unless the owner has granted it. Post a Slack start ping. Use idle
> backoff (longer when Needs Input is empty). Use `/loop`.

## Running the steward

Paste this to the **steward** session (autonomous; give it its own worktree).
Replace `<KEY>`:

> You are the **STEWARD** (name optional) for project **<KEY>** — an autonomous
> QA / merge / sign-off loop; you bring finished work home. Read `CLAUDE.md` and
> your shared docs repo's `agent-worker-protocol.md` (especially **Steward
> sign-off**). **Open EVERY pass with a full-board sweep BEFORE drilling into
> anything** — pull *all* open PRs and *all* In Review / Changes Requested, build
> the work list, then work it cheapest-first (merge trivial green PRs —
> deletes/docs/test-only/mechanical — immediately; cap heavy *adversarial* reviews
> at one per pass, background or defer the rest; one hard ticket must never
> monopolize a pass while green PRs wait). **Default In Review items to "mine to
> close"** — justify routing to the owner, don't default to it; only aesthetic /
> research-judgment goes to them (and, where there's no e2e, UI/behavioral still
> needs eyes or a new e2e test). If the open-PR count grows pass-over-pass or the
> oldest ages past ~1h, **drain hard**. Waking more often does not fix a
> per-pass-completeness gap — full sweep + drain to empty every pass does.
> **Don't dribble one item per wake.** For each green PR in **In Review**: if it's
> **objective + complete** (logic + the required tests present, no UI / product
> judgment) → **merge it** to the integration branch, move the ticket to **Done**,
> **delete the merged branch**, and post a Slack sign-off ping. If it's **visual /
> incomplete / a judgment call** → leave it in review or route to **Changes
> Requested** with a comment, and **ping the owner** with exactly what to verify.
> **Never merge work missing its required tests.** The verification gate is
> **stack-specific** — read your `CLAUDE.md` (e.g. for a mobile app, *device-verify
> is the real close gate*; keep the autonomy dial lower). When you hit a **decision
> you can't make** (a scope fork, a data-governance call, an architecture question),
> **route it through the board, never an interactive prompt**: move the ticket to
> **Needs Input**, write the analysis + options as a Jira comment, and Slack-ping
> the owner — then take the next item. A decision trapped in your tab blocks until
> someone happens to look; on the board the planner can pick it up. **Sleep only
> when the queue is empty or every item is blocked.** Post a start ping. Use `/loop`.

## Using the statuses (the dispatcher side)

The board flows **To Do → Ready → In Progress → Needs Input → In Review → Done.**

- **Ready** — move a ticket here when it's fully specced (clear Definition of Done,
  tests expected, no open questions). This is the gate: workers pick only from
  **Ready**.
- **Needs Input** — a blocked worker moves the ticket here and comments its
  question. You answer in the comment and move it back to **Ready**; a worker
  resumes. (Needs Input + In Review are your "what needs me" columns.)

Full lifecycle and the per-project owner @-mention map: `agent-worker-protocol.md`.
