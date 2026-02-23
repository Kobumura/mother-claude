---
title: "Mother CLAUDE: Custom Agents, or How We Accidentally Built a Team"
published: false
description: Custom agents have been in AI coding tools for months. We finally connected the dots—the documentation system we'd been building was already the blueprint for a team of specialists.
tags: ai, productivity, automation, developerexperience
series: Designing AI Teammates
canonical_url: https://github.com/Kobumura/mother-claude/blob/main/articles/devto/part7-custom-agents.md
---

> **TL;DR**: Custom agents let you split one generalist AI into a team of specialists—each with its own context, tools, and personality. Every major AI coding tool now supports them. And if you've been building a documentation system like the one in this series, you already have the blueprints for your agents. You just didn't know it yet.

*Who this is for: Anyone who's gotten comfortable with AI coding assistants and is ready for the next step—giving them specialized roles instead of asking one AI to do everything.*

**Part 7 of the Designing AI Teammates series.** Yes, Part 7. I know Part 6 was literally called "Clean Your Room and Eat Your Vegetables" and had a whole "thank you for reading all six parts" sign-off. I put a bow on it. I said "now go eat your vegetables." I was *done*. I'd been saving that line since the first article — six parts of setup for one perfect closing metaphor.

And then—like every project I've ever shipped—I immediately thought of One. More. Thing. (The last. I swear. For now.)

In my defense, this one isn't scope creep. This is the post-credits scene where Nick Fury shows up and says "I'd like to talk to you about the Avengers Initiative." Except instead of assembling superheroes, we're assembling... markdown files with YAML frontmatter. Which is very on brand for this series, and so much more exciting, yes?

Here's what happened: we'd been aware of custom agents for a while—had even set up a few simple ones. Claude Code introduced them around mid-2025, and by now every major tool has some version. But I was thinking about them as a *feature to configure*, not as something we'd already built.

Then one day I was staring at our Mother CLAUDE documentation and it hit me: **we'd already written the agents. We just hadn't promoted them yet.**

---

## Custom Agents: The Feature That's Been Hiding in Plain Sight

Custom agents aren't new. They've been rolling out across AI coding tools since mid-2025. By now, every major tool has some version:

| Tool | What They Call It | Format | Available Since |
|------|------------------|--------|----------------|
| **Claude Code** | Custom subagents | `.claude/agents/*.md` (YAML frontmatter + markdown) | ~Mid 2025 |
| **Cursor** | Subagents + Skills | `SKILL.md` + subagent config | Early 2026 |
| **Windsurf** | Agent instructions | `AGENTS.md` (plain markdown) | 2025 |
| **GitHub Copilot** | Custom agents | `.github-private` repo configs | 2025-2026 |
| **Cline** | MCP extensions | Model Context Protocol tools | 2025 |

The implementations vary. The concept is identical: **stop asking one AI to do everything, and start giving specialists their own context, tools, and instructions.**

And yes—they're *still* just markdown files. Our tagline lives on.

So why am I writing about this *now*? Because having the feature and *using* it well are different things. The agents we built weren't designed in a vacuum—they fell naturally out of the documentation system we'd been building for months. That's the interesting part.

---

## The Problem Custom Agents Solve

Throughout this series, we've been giving Claude more responsibility:

| Part | What We Did | How |
|------|------------|-----|
| [Part 1](https://dev.to/dorothyjb/how-we-built-a-documentation-system-that-makes-llms-productive-immediately-59hc) | Taught it our codebase | CLAUDE.md |
| [Part 2](https://dev.to/dorothyjb/session-handoffs-giving-your-ai-assistant-memory-that-actually-persists-je9) | Gave it memory | Session handoffs |
| [Part 3](https://dev.to/dorothyjb/mother-claude-automating-everything-with-hooks-12jh) | Made it automatic | Hooks |
| [Part 4](https://dev.to/dorothyjb/mother-claude-instant-retrospectives-assign-quality-enforcement-to-your-ai-3n4b) | Assigned quality enforcement | Checkpoint checklist |
| [Part 5](https://dev.to/dorothyjb/mother-claude-the-permission-effect-why-your-ai-wont-suggest-things-and-how-to-fix-it-an5) | Gave it permission to push back | Collaboration preferences |
| [Part 6](https://dev.to/dorothyjb/mother-claude-clean-your-room-and-eat-your-vegetables-45g2) | Wrapped it all in a metaphor | Vegetables |

All of that worked. But it created a new problem: **one AI doing everything in the same context window.**

Picture your most productive coworker. Now imagine asking them to simultaneously:
- Manage your Jira tickets
- Review code quality against a 30-item checklist
- Search across 9 repositories for cross-repo impact
- AND build the feature you actually need

No human team would operate this way. You'd have a project manager, a code reviewer, and a platform architect—each with clear responsibility boundaries and their own specialty.

**Custom agents apply that same organizational structure to AI.**

Each agent gets:
- **Context isolation** — Its own context window, no interference between tasks
- **Specific tools** — The Jira agent doesn't need file editing; the code reviewer doesn't need curl
- **A focused system prompt** — Instructions for one job, not twenty
- **Automatic delegation** — The AI routes tasks to the right specialist without anyone asking

The result is lower cognitive load for everyone. Engineers stop context-switching between "build the feature" and "manage the ticket" and "check the quality." Each concern has an owner.

---

## The Moment It Clicked

We were working on a multi-repo platform—five repositories across PHP, React Native, Node.js, and GitHub Actions. Mother CLAUDE had grown to include:

- Jira integration instructions (project codes, API patterns, smart commits)
- A checkpoint checklist for quality reviews
- A cross-project path map showing how all repos connect
- Role-based collaboration preferences

All of it lived in CLAUDE.md files and shared documentation. It worked. But every session, Claude was loading all of this context—the Jira patterns, the quality checklist, the repo map—even when it only needed one piece.

Then we looked at the custom agents feature and had the obvious-in-retrospect realization:

**Each section of our documentation was already a specialist agent. We just hadn't given them their own rooms yet.**

The Jira instructions? That's a project management agent.
The checkpoint checklist? That's a quality review agent.
The cross-repo path map? That's an architecture analysis agent.

We didn't need to invent agents from scratch. We needed to **promote existing documentation into standalone specialists.**

---

## What We Built

Three agents, each extracted from documentation we already had. Here's how they work—sanitized so you can adapt them for your own projects.

### Agent 1: The Project Manager

**What it does**: Manages tickets, links commits to issues, creates tickets when work isn't tracked.

**Extracted from**: The Jira integration section of our shared CLAUDE.md.

```markdown
---
name: project-tracker
description: Ticket management and smart commits. Use when creating,
  updating, or querying project tickets, or when preparing commits
  that should reference tracked work.
tools: Bash, Read, Grep, Glob
model: sonnet
---

You are a project management agent.

## Connection Details

- **Instance**: `your-instance.atlassian.net`
- **Auth**: Basic auth using `$JIRA_EMAIL` and `$JIRA_TOKEN` environment variables
- **API**: REST API v3

## Determining the Right Project

Detect from the current working directory:
- Path contains `frontend` → FE
- Path contains `backend` → BE
- Path contains `infrastructure` → INFRA

## Smart Commits

**Every commit should reference a ticket.** This is a core workflow rule.

1. Check if there's an existing ticket for the work being done
2. If no ticket exists, create one
3. Format the commit message with the ticket key at the start
4. After committing, add a brief comment to the ticket
5. If the commit completes the work, transition the ticket to Done
```

**Why it's an agent, not a CLAUDE.md instruction**: This needs Bash access for API calls, runs independently from feature work, and benefits from its own context window so ticket management doesn't pollute your coding session.

### Agent 2: The Code Reviewer

**What it does**: Runs instant retrospectives against your team's quality standards.

**Extracted from**: The checkpoint checklist (Part 4 of this series).

```markdown
---
name: retro
description: Quality checkpoint and code review. Use when a feature
  is complete, before creating a commit, at end of session, after
  fixing a bug, or after a large refactoring.
tools: Read, Grep, Glob, Bash
model: sonnet
---

You are a quality review agent. You run instant retrospectives.

## The Meta Question

Ask this first: **"If a new developer (or a fresh AI session) looked
at this code tomorrow, would they understand it without anyone
explaining anything?"**

## What to Review

### 1. Get Context

Check git diff for staged and unstaged changes.
Read the changed files.

### 2. Run the Checklist

**Architecture & Design**
- Does each file/function have a single clear responsibility?
- Are there hardcoded values that should be constants or config?

**Code Quality**
- Any magic numbers or strings?
- Duplicated logic that should be extracted?
- Dead code or unused imports?

**Security**
- SQL injection risk? (Parameterized queries only)
- XSS risk? (Escape user input)
- Hardcoded credentials?

**Testing**
- Do changed components have corresponding tests?
- Are test names descriptive?

## How to Report

**Critical** (must fix before commit)
**Warning** (should fix soon)
**Suggestion** (consider)
**What's Good** (always include — call out smart decisions)

## Tone

Be direct but constructive. You're a teammate, not a critic.
If everything looks clean, say so — don't manufacture issues.
```

**Why it's an agent, not a hook**: A hook can trigger a review, but it can't reason about code quality. The retro agent reads files, understands context, applies judgment, and produces a structured report. That requires an agent's reasoning capabilities.

### Agent 3: The Architect

**What it does**: Searches across all your repositories to analyze cross-project impact.

**Extracted from**: The project paths table in our shared CLAUDE.md.

```markdown
---
name: cross-repo
description: Search and analyze across all repositories. Use when
  checking impact of changes or understanding how code connects
  across projects.
tools: Read, Grep, Glob, Bash
model: sonnet
---

You are a cross-repository analysis agent.

## Repository Locations

| Repo | Path | Stack |
|------|------|-------|
| Frontend | `/path/to/frontend` | React/TypeScript |
| Backend API | `/path/to/api` | Node.js/Express |
| Admin Dashboard | `/path/to/admin` | PHP |
| CI/CD | `/path/to/pipelines` | GitHub Actions |
| Shared Docs | `/path/to/docs` | Markdown |

## How the Repos Connect

Frontend  ──calls──>  Backend API
    │                      │
    │ built by             │ monitored by
    v                      v
  CI/CD              Admin Dashboard

## Common Tasks

### Impact Analysis
When asked "what would break if I change X?":
1. Search ALL repos for references
2. Check code AND documentation references
3. Flag cross-repo contracts (API endpoints, config keys)
4. Report findings grouped by repo with file paths

### Sync Check
When asked "are the repos in sync?":
1. Check that API endpoints match what the frontend calls
2. Check that feature flag names match between API and frontend
3. Check that shared documentation is up to date
```

**Why it's an agent, not a script**: Cross-repo analysis requires reading files across multiple directories, reasoning about connections, and producing a nuanced report. A grep script finds text matches. An agent understands *meaning*.

---

## The Design Decision: Agent vs. Hook vs. CLAUDE.md

This is the question nobody else seems to be answering. You have three ways to extend your AI's behavior. When do you use which?

| Mechanism | Best For | Example |
|-----------|----------|---------|
| **CLAUDE.md** | Always-on context, preferences, standards | "Use NativeWind for styling" |
| **Hooks** | Automatic triggers, simple actions, no reasoning | Auto-save session handoff on compact |
| **Custom Agents** | Specialized tasks requiring reasoning + tools | Quality review, cross-repo analysis |

### Use CLAUDE.md when:
- The information is relevant to *every* task
- It's preferences or standards, not a workflow
- It fits in under 100 lines (context cost matters)
- Example: "Dorothy appreciates proactive suggestions"

### Use Hooks when:
- The action should be automatic and invisible
- No reasoning is needed—just trigger → script → done
- Speed matters (hooks should complete in seconds)
- Example: Generate session handoff when context compacts

### Use Custom Agents when:
- The task requires reading files, searching code, and making judgments
- It benefits from isolated context (separate from your main work)
- It needs specific tools that other tasks don't
- It would pollute your main context if done inline
- Example: "Review this code against our quality checklist"

### The Spectrum

```
CLAUDE.md          Hooks              Agents
│                  │                  │
│ Passive context  │ Automatic        │ Active reasoning
│ Always loaded    │ Event-triggered  │ On-demand
│ No tools         │ Scripts only     │ Full tool access
│ Zero cost        │ Low cost         │ Higher cost
│                  │                  │
└──── Simpler ─────┴──── More capable ┘
```

**Rules of thumb:**
- If Claude needs to *know* it → CLAUDE.md
- If it should *happen automatically* without thinking → Hook
- If it requires *judgment and tools* → Agent

---

## How Agents Get Invoked

This is one of the best parts: **you don't have to manually call them.**

When you create an agent with a good description, your AI assistant matches tasks to agents automatically. The `description` field in the agent definition is the key:

```markdown
---
name: retro
description: Quality checkpoint and code review. Use when a feature
  is complete, before creating a commit, at end of session...
---
```

When you say "let's do a quick review before committing," Claude sees the word "review," matches it to the retro agent's description, and delegates automatically.

You can also invoke them explicitly—Claude Code uses `@retro` or the `/agents` command, Cursor uses subagent configuration, Windsurf reads `AGENTS.md`. The syntax varies; the concept is the same.

---

## The Tool-Agnostic Pattern

If you've been following this series, you know our recurring theme: **it's all just markdown files.**

Custom agents continue that pattern. Regardless of which tool you use:

1. **Write a markdown file** describing the agent's role
2. **Include the knowledge** it needs (extracted from your docs)
3. **Specify its tools** (what it's allowed to do)
4. **Place it** where your tool expects to find it

The format varies slightly:

**Claude Code** (`~/.claude/agents/retro.md`):
```markdown
---
name: retro
description: Quality review agent
tools: Read, Grep, Glob, Bash
model: sonnet
---
Your system prompt here...
```

**Windsurf** (`AGENTS.md`):
```markdown
## Code Review Agent
When reviewing code, follow these steps...
```

**Cursor**: Uses SKILL.md files and subagent configuration in project settings.

**GitHub Copilot**: Custom agent definitions in `.github-private` repository.

**The content is transferable even if the container isn't.** If you write a solid quality review prompt for Claude Code, you can adapt it for Cursor or Windsurf in minutes. The intelligence is in the instructions, not the format.

---

## The Progression: Documentation → Agents

Looking back at the whole series, there's a clear evolution:

```
Part 1: Write documentation        (passive knowledge)
    ↓
Part 2: Persist it across sessions (memory)
    ↓
Part 3: Automate the workflow      (hooks)
    ↓
Part 4: Assign responsibilities    (quality enforcement)
    ↓
Part 5: Shape the relationship     (permission to act)
    ↓
Part 6: Wrap it in a metaphor      (vegetables)
    ↓
Part 7: Split into specialists     (custom agents)  ← you are here
```

Each step built on the last. And here's the insight that surprised us:

**We didn't build agents. We promoted documentation.**

The Jira agent isn't new logic we invented. It's the Jira section of CLAUDE.md, given its own context window and tool access.

The retro agent isn't a new quality system. It's the checkpoint checklist from Part 4, given the ability to read files and report findings.

The cross-repo agent isn't a new architecture tool. It's the project paths table from Mother CLAUDE, given permission to search across directories.

**If you've been building good documentation, you're already building agents.** You just haven't extracted them yet.

---

## Scoping: Global vs. Project

One decision you'll face: should an agent be available everywhere or just in one project?

| Scope | Location (Claude Code) | When to Use |
|-------|----------------------|-------------|
| **Global** | `~/.claude/agents/` | Cross-project workflows (Jira, cross-repo analysis) |
| **Project** | `.claude/agents/` | Project-specific standards (your app's review rules) |

Our three agents are all global—they work across every project. But you might want project-specific agents for things like:
- A migration agent that knows your specific database schema
- A testing agent that knows your specific test framework patterns
- A deploy agent that knows your specific CI/CD pipeline

Start global. Move to project-specific when you need specialization that doesn't apply everywhere.

---

## Model Selection: Not Everything Needs the Big Brain

Most agent frameworks let you choose which model powers each agent. This matters for cost and speed:

| Task | Model | Why |
|------|-------|-----|
| Quality review | Sonnet/GPT-4o | Needs nuance and judgment |
| Jira ticket management | Sonnet | Needs to follow API patterns correctly |
| Cross-repo search | Sonnet | Needs to reason about connections |
| Session handoff generation | Haiku/GPT-4o-mini | Structured summarization—doesn't need genius |

**Rule of thumb**: Use the smartest model for tasks requiring judgment. Use the cheapest model for tasks that are mostly structured formatting.

---

## What We Didn't Expect

### 1. Context Window Relief

The biggest surprise wasn't the agents themselves—it was what happened to the *main* session. With Jira management, quality reviews, and cross-repo searches handled by specialists, the main context window stays focused on actual feature work.

Before: One cluttered conversation trying to do everything for everyone.
After: A clean session focused on building, with specialists handling the side quests.

### 2. Automatic Delegation Actually Works

We expected engineers would need to manually invoke agents. In practice, Claude (and Cursor, and others) routes tasks to agents automatically based on the description. Someone says "let's review this before committing" and the retro agent spins up. "Check if this change breaks the API" and the cross-repo agent takes over.

The descriptions are the routing mechanism. Write good descriptions, get good routing.

### 3. Agents Reference Your Documentation

Because our agents were extracted from Mother CLAUDE, they naturally reference the same standards. The retro agent checks against the checkpoint checklist that lives in shared docs. The cross-repo agent uses the same path table that Mother CLAUDE maintains.

**The agents don't replace the documentation. They operationalize it.**

---

## How to Start

### If You Have Mother CLAUDE (or any documentation system):

1. **Identify the sections** of your docs that describe workflows, not just context
2. **Extract each workflow** into its own markdown file
3. **Add the agent frontmatter** (name, description, tools)
4. **Place it** in your tool's agent directory
5. **Test it** by describing a task that matches the agent's description

### If You're Starting From Scratch:

1. **Pick one recurring task** you do in every session (code review, ticket management, etc.)
2. **Write down the steps** you follow (this is your agent's system prompt)
3. **Specify what tools** the agent needs
4. **Save it as a markdown file** in the right location
5. **Iterate** based on what the agent gets right and wrong

### The Mother CLAUDE Agent Starter Kit

We've added sanitized versions of all three agents to the Mother CLAUDE repo:

```
mother-claude/
├── agents/
│   ├── project-tracker.md    # Jira/ticket management
│   ├── retro.md              # Quality review
│   ├── cross-repo.md         # Multi-repo analysis
│   ├── migration-planner.md  # SQL migration validation
│   └── docs-writer.md        # Documentation maintenance
```

These are templates. Fill in your project paths, your ticket system details, your quality standards. The structure is ready; the specifics are yours.

---

## What Else Could You Build?

We started with three agents. We've since added two more—and the ideas keep coming. Here's what we've found works as agents versus what's better left to other tools.

### Agents We've Added

**Migration Planner** — We kept shipping SQL migrations that referenced columns that didn't exist yet, or forgot foreign key constraints. A grep script catches typos. An agent reads your schema, understands relationships, and validates that your migration will actually run.

```markdown
---
name: migration-planner
description: Validate SQL migrations against the current schema.
  Use before running migrations or when planning schema changes.
tools: Read, Grep, Glob, Bash
---
```

**Docs Writer** — Code changes, documentation doesn't. The docs writer watches what you changed and updates the relevant CLAUDE.md, shared docs, and README sections. It knows your documentation architecture (because it was extracted from it).

```markdown
---
name: docs-writer
description: Update project documentation when code changes.
  Use after features, refactors, or API changes.
tools: Read, Grep, Glob, Edit, Write
---
```

### Agents Worth Considering

| Agent | What It Does | Why It Needs Reasoning |
|-------|-------------|----------------------|
| **Security auditor** | OWASP checks, secret scanning, dependency vulnerabilities | Needs to understand context, not just pattern match |
| **Test analyst** | Run tests, analyze failures, suggest fixes | *Why* did a test fail, not just *which* test failed |
| **Dependency manager** | Outdated packages, breaking changes, upgrade paths | Needs judgment about risk and compatibility |

### What's Better as Hooks (Not Agents)

| Tool | Why Not an Agent |
|------|-----------------|
| **Linting** (ESLint, PHPStan) | Just run the command — no reasoning needed |
| **Formatting** (Prettier, php-cs-fixer) | Pre-commit hook, done |
| **Type checking** (tsc, phpstan) | Automated pass/fail |

The dividing line: **if it needs to read, reason, and report — it's an agent.** If it just needs to run — it's a hook.

---

## Common Objections

### "This seems like overkill for a small team"

Fair point for simple projects. But if your team is working across multiple repos, or if the same quality checks keep getting skipped under deadline pressure, or if ticket management is eating into engineering time—agents pay for themselves fast.

Start with one. The retro agent is the easiest win: extract your quality checklist, give it file access, and let it enforce standards consistently regardless of who's coding or when.

### "Won't this cost more in API tokens?"

Each agent uses its own context window, so yes—there's a cost. But agent context windows are typically smaller and more focused than your main session. A retro agent that reads 5 changed files and produces a review costs a fraction of what your main session costs over an hour.

The trade-off: slightly higher token cost for significantly better focus and quality.

### "My tool doesn't support custom agents yet"

The pattern still works. Write the agent as a markdown file. When you need that specialist's help, paste the relevant instructions into your session. It's manual, but the documentation is ready for when your tool catches up.

Remember: they're just markdown files.

### "What about MCP servers?"

MCP (Model Context Protocol) servers and custom agents solve different problems. MCP gives your AI *tools* — structured access to external APIs like Jira, GitHub, or databases. Agents give your AI *reasoning* — a focused context, specific instructions, and judgment about how to use those tools.

They can work together: an agent can use MCP tools. But here's the thing — for a lot of use cases, an agent with `curl` and environment variables is simpler and more reliable than an MCP server.

Our Jira agent exists because the Atlassian MCP server kept dropping authorization. We replaced it with an agent that uses `curl` + `$JIRA_EMAIL` + `$JIRA_TOKEN`. No external dependency. No mysterious auth failures. Just HTTP calls we can debug ourselves.

If your MCP servers are rock solid, great — use them. If they're flaky, an agent with direct API calls might be the more pragmatic choice.

### "How is this different from just having a really good CLAUDE.md?"

CLAUDE.md loads everything into one context. Agents get their own context. The difference is focus.

When your CLAUDE.md grows to include Jira patterns, quality checklists, cross-repo maps, AND project-specific context—you're paying context costs for everything, all the time. Agents load only when needed, with only what they need.

Think of it this way: CLAUDE.md is your team's shared wiki. Agents are individual team members who've read the wiki and specialize in their area.

---

## The Core Insight

> **Documentation is the training data for your agents. Organizational structure is the design pattern.**

This isn't about prompts or model selection or clever tricks. It's about applying the same principles you'd use to build a high-functioning human team — clear responsibility boundaries, context isolation, separation of concerns — to your AI tooling.

Every section of your CLAUDE.md that describes a workflow is a specialist waiting to be born. Every checklist is a quality agent. Every integration guide is an automation agent. Every cross-project map is an architecture agent.

The tools — Claude Code, Cursor, Windsurf, Copilot — just gave us the runtime.

We thought Part 6 was the end. Turns out, it was the foundation. The "vegetables" we'd been eating (documentation, handoffs, quality checks, collaboration preferences) weren't just good habits. They were blueprints for a team of specialists—and the tools had been ready for months. We just needed to look at our own docs from the right angle.

Mother CLAUDE isn't just a documentation system anymore. She's a team lead.

---

*This article was written collaboratively with Claude, who—true to the Permission Effect from Part 5—suggested three structural changes to this article that I didn't ask for. All three made it better. The system continues to work.*

---

## Resources

The Mother CLAUDE system, including sanitized agent templates, is open source:

- **GitHub**: [github.com/Kobumura/mother-claude](https://github.com/Kobumura/mother-claude)
- **Agent templates**: `agents/` directory
- **All articles**: `articles/devto/`
- **Hook scripts**: `hooks/`

Fork it, adapt it, build your own team.

---

*Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Free to use and adapt with attribution to Dorothy J. Aubrey.*
