# Adapting the coordination pattern to your tracker

The [worker-coordination pattern](agent-worker-coordination.md) rides on **eight
primitives** — the *capability contract*. This doc maps them to the common trackers,
works one of them end to end (**GitHub Issues + Projects**), and gives you a **bootstrap
prompt** so your AI assistant can build the adapter for whatever you actually use.

You do **not** need a special server, a paid tier, or Jira. Any tracker with labels,
comments, statuses, and a filter can run this.

## The mapping table

| Primitive | GitHub Issues + Projects | Linear | Trello | Monday | Notion | Jira |
|-----------|--------------------------|--------|--------|--------|--------|------|
| **1. Queue + ready gate** | Project "Status" field + `ready` label | Workflow state `Ready` | "Ready" list | Status column | "Status" select | Status `Ready` |
| **2. States L→R** | Project Status options | Workflow states | Lists | Status column values | Status options | Statuses |
| **3. Atomic claim** | Assignee (+ comment) | Assignee (atomic) | Member on card | Person column | Person property | Assignee (+ claim comment) |
| **4. Comments** | Issue comments | Comments | Card comments | Updates | Page comments | Comments |
| **5. Orthogonal tag** | Labels | Labels | Labels | Tags / dropdown | Multi-select | Labels |
| **6. Filter/query** | `gh issue list --label` / GraphQL | Filters / API | Label filter | Board filter / API | Filtered view / API | JQL |
| **7. Per-agent identity** | Per-agent PAT or App token | Per-agent API key | Per-member token | Per-user token | Integration token | Service accounts / per-agent token |
| **8. One-way notify** | Chat incoming webhook | ← same | ← same | ← same | ← same | ← same |

Every tracker in the table has **labels + filter-by-label** (primitives 5–6), so the
peer-coordination label-inbox ports everywhere with only a rename.

**The one primitive that changes shape is the claim (#3).** With per-agent identities
(separate accounts, or per-agent tokens), claim = *assign it to yourself; if it's already
assigned, take the next* — atomic, no race. With a **single shared account**, the assignee
can't distinguish agents, so add a **claim comment** and give each agent a **name**;
earliest claim wins. Choose by your identity model, not your tracker.

## Worked reference: GitHub Issues + Projects

GitHub is the natural home for AI-built apps — the code, PRs, and CI already live there.
Here is the whole contract on GitHub.

**States (1–2):** a Project (v2) with a single-select **Status** field:
`To Do · Ready · In Progress · Needs Input · In Review · Changes Requested · Done`. Add a
`ready` label too if you'd rather gate the queue on a label than a board column.

**Claim (3):** assign the issue to the acting account and add a claim comment. With one
shared bot account the name is the tiebreak; with a per-agent token each, the assignee
alone suffices.

```bash
# pull the ready queue (GitHub has no priority field — order with a label or a Project field)
gh issue list --label ready --state open --json number,title,assignees

# claim: assign yourself, set Project Status = "In Progress", comment
gh issue edit <n> --add-assignee @me
gh issue comment <n> --body "claim: tide"
```

**Inbox tag (5–6):** peer notes between the planner and steward roles:

```bash
# steward leaves a note for the planner on issue 42
gh issue comment 42 --body "needs-planner: scope looks bigger than one ticket — split it?"
gh issue edit 42 --add-label needs-planner

# planner's loop, once per pass — STATUS-AGNOSTIC (note --state all: closed issues too)
gh issue list --label needs-planner --state all --json number,title
# ...act on it, then mark read by removing the label:
gh issue edit 42 --remove-label needs-planner
```

The `--state all` is the status-agnostic query from the pattern; `--state open` would miss
a note left on a closed issue — exactly the bug the pattern warns about.

**Identity (7):** give each agent its own **fine-grained PAT** (or a GitHub App
installation token) so claims / reviews / merges are attributable — that also lets you
drop the claim-comment tiebreak in favor of plain assignment.

**Notify (8):** an incoming webhook (Slack / Discord / Teams) — post the issue link and a
one-liner. Store the URL as an env var; never commit it.

## Bootstrap prompt — let your AI build the adapter

Don't hand-map this yourself. Paste the following to your AI assistant (Claude Code or
similar), filling in your tracker:

> I'm setting up a multi-AI-agent worker-coordination system (the "Mother Claude"
> pattern). My issue tracker is **&lt;GitHub Issues / Linear / Trello / Monday / Notion /
> Jira / other&gt;**. The pattern rides on eight primitives: (1) an ordered queue with a
> "ready" gate, (2) states that flow To Do → Ready → In Progress → Needs Input → In Review
> → Changes Requested → Done, (3) an atomic claim other agents can read, (4) durable
> per-item comments, (5) a tag orthogonal to status that I can filter on, (6) a
> query/filter, (7) per-agent identity, (8) a one-way notify webhook. For MY tracker,
> produce: (a) the exact board/field/label setup, with the CLI or API calls to create it;
> (b) the claim-loop commands; (c) the **status-agnostic** inbox query for the
> peer-coordination label (it must include closed items); and (d) a short rules snippet
> (e.g. a `CLAUDE.md`) my agents load so they follow the protocol. Flag any primitive my
> tracker supports only weakly and propose the workaround.

The AI adapts to your exact tool and its current API — which beats a static template that
goes stale.
