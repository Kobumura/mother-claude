---
title: Mother CLAUDE: How We Built a Documentation System That Makes LLMs Productive Immediately
published: true
description: A three-tier documentation architecture that reduces AI assistant onboarding from hours to minutes. First test: Claude went from cold start to planning mode in under 5 minutes.
tags: ai, productivity, documentation, developerexperience
series: Designing AI Teammates
canonical_url: https://github.com/Kobumura/mother-claude/blob/main/articles/devto/part1-documentation-system.md
cover_image: https://dev-to-uploads.s3.amazonaws.com/uploads/articles/3i3yali4xcq7dama572r.png

---

> **TL;DR**: A three-tier documentation system that reduces LLM onboarding from hours to minutes across multi-repo, multi-language projects. First real-world test: Claude went from cold start to planning mode in under 5 minutes.

*Who this is for: Teams working across multiple repos or languages who want LLMs to be productive immediately without repeated onboarding or fragile session memory.*

*While this was built for Claude Code, the architecture applies to any LLM with limited persistent memory—Kiro, Cursor, Copilot, or whatever comes next.*

---

## The Problem

LittleTalks is built across **multiple projects in different languages**:

| Project | Language | Purpose |
|---------|----------|---------|
| littletalks-mobile | React Native | iOS & Android app |
| littletalks-api | Node.js/Express | Backend API |
| littletalks-admin | PHP | Admin dashboard |
| littlepipes | GitHub Actions | CI/CD platform |

These projects share business logic, integrations (RevenueCat, Twilio, analytics), standards, and data contracts. Working with Claude Code across them, we kept hitting the same issues:

1. **Context switching pain** - Starting a new session meant re-explaining project structure, conventions, and history
2. **Scattered documentation** - Important info spread across READMEs, code comments, and tribal knowledge
3. **Duplication and drift** - Same information (Jira setup, commit guidelines) copy-pasted across repos, getting out of sync
4. **Legacy project onboarding** - Rewriting old codebases required extensive explanation of "why things were built this way"

**The goal**: Get Claude productive immediately, whether it's a fresh session or a completely new project.

**Before**: First session spent explaining Jira setup, repo layout, commit conventions, and why certain patterns look duplicated across projects.

**After**: First session critiqued the documentation system itself and moved directly into planning.

---

## The Solution: Three-Tier Documentation Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     CONFLUENCE                          │
│  Business docs, marketing, non-technical                │
│  → Claude fetches on-demand via WebFetch                │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│              Shared Docs Repo (Mother CLAUDE)           │
│  Cross-project standards, deep technical guides         │
│  → Loaded at session start (lean) + on-demand (deep)    │
└─────────────────────────────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
│ Project CLAUDE.md │ │ Project CLAUDE.md │ │ Project CLAUDE.md │
│ Tech stack,       │ │ Tech stack,       │ │ Tech stack,       │
│ file structure,   │ │ file structure,   │ │ file structure,   │
│ dev commands      │ │ dev commands      │ │ dev commands      │
└───────────────────┘ └───────────────────┘ └───────────────────┘
```

### Tier 1: Mother CLAUDE (Shared Standards)

A dedicated repo (`littletalks-docs`) containing:
- **CLAUDE.md** (~70 lines) - Jira setup, screenshot locations, commit guidelines, project paths
- **shared/** - Deep technical docs (journey system, analytics, API contracts)
- **DOCUMENTATION-ARCHITECTURE.md** - Meta-documentation explaining the system itself

Every project's CLAUDE.md starts with:
```markdown
> **Shared standards**: See `littletalks-docs/CLAUDE.md` for Jira, screenshots, commit guidelines.
```

### Tier 2: Project CLAUDE.md (Lean & Specific)

Each project has its own CLAUDE.md that's:
- **Lean** (<100 lines) - Minimizes context cost
- **Specific** - Tech stack, file structure, dev commands for THIS project
- **Referenced** - Points to Mother CLAUDE for shared standards
- **Actionable** - Claude can start working immediately

### Tier 3: On-Demand Deep Docs

Detailed guides live in `shared/` and are read only when needed:
- Journey system architecture (1,251 lines)
- Analytics event tracking
- RevenueCat integration
- API contracts

This keeps session context lean while making deep knowledge accessible.

---

## Key Design Decisions

### 1. Single Source of Truth
When we moved docs to the shared repo, we left **pointer files** in the original locations:
```markdown
# Document Moved
This document has been moved to `littletalks-docs/shared/journey-system.md`
```

No duplication = no drift.

### 2. Security Built In
PHP projects deployed to web servers get `.htaccess` in their `docs/` folder:
```apache
Require all denied
```

This is documented in Mother CLAUDE so new projects know to add it.

### 3. Session Handoffs
A standardized template (`session-handoff-template.md`) ensures continuity:
- What was accomplished
- Current state
- Lessons learned
- Next steps
- Key files modified

Each project has a `docs/session_handoffs/` directory for these.

### 4. Self-Documenting
The `DOCUMENTATION-ARCHITECTURE.md` file explains the entire system. New Claudes can understand the architecture without human explanation.

---

## Known Failure Modes

This system breaks down if:

- **Project CLAUDE.md files grow beyond ~100 lines** - Context cost defeats the purpose
- **Deep docs are loaded eagerly instead of on demand** - Session bloat, slower responses
- **Shared standards are duplicated instead of referenced** - Drift returns
- **EVOLUTION.md exists but is left empty** - Templates without content don't help
- **No one asks Claude to critique the system** - Feedback loops die

The architecture is intentionally simple. Most failures come from violating the core principle: **lean at load, deep on demand**.

---

## The Legacy Project Challenge

Our biggest test: preparing a 2011-2020 football pool codebase for a greenfield rewrite.

### What We Prepared

**football-pool-legacy/** (reference archive):
- `CLAUDE.md` - Business logic locations, DO NOT MODIFY warning
- `EVOLUTION.md` - Historical context (essential for legacy projects):

```
EVOLUTION.md
├── Data volumes (~users, ~records, ~DB size)
├── Why features were built this way
├── What users complained about
├── What admins found tedious
├── Bugs that required manual fixes
├── Workarounds still in place
└── What not to repeat
```

> **For legacy systems, EVOLUTION.md is more important than CLAUDE.md.** Without it, Claude can understand *what* exists but not *why* it exists.

**football/** (greenfield):
- `CLAUDE.md` - Full requirements, phases, success criteria
- `docs/session_handoffs/` - Ready for continuity
- Pre-researched docs (ESPN score feeds)

### The Result

First Claude session on the football project:

> **Feedback on the Prep System**: 8/10
>
> The setup was genuinely helpful. CLAUDE.md gave immediate context. Legacy repo access was critical. The empty EVOLUTION.md and lack of "lessons learned" notes were the main gaps.

An 8/10 on first contact, with clear, actionable gaps—exactly the feedback loop we wanted. Claude went from cold start to planning mode in under 5 minutes, proposing database schema and asking clarifying questions about scoring rules. Zero time spent explaining Jira workflows, commit conventions, or project structure.

### First-Session Feedback Loop (Proof of Self-Documentation)

The very first question asked in the greenfield project was not about features or architecture, but about the documentation system itself:

> **Before we start—do you feel like the prep that Mother CLAUDE and the Claude that created your prep docs did a good job? Any suggestions for improvement?**

This was intentional. Because Mother CLAUDE is self-documenting—including instructions for setting up new projects and maintaining existing ones—the goal was to validate whether a *fresh Claude session* could:
- Understand the system without human explanation
- Critique its effectiveness
- Identify gaps worth addressing

Because Mother CLAUDE documents not just project standards but how the documentation system itself works, this question functioned as a real-world test of whether the architecture truly explained itself.

Claude's response (8/10) directly informed the improvements that followed, particularly around EVOLUTION.md content and historical context. The gaps identified became immediate action items, not theoretical improvements.

> **Design Principle**: Every new project should begin by asking Claude to critique the documentation system itself. If Claude cannot evaluate or improve the prep, the system is incomplete.

---

## The Legacy Project Prep Checklist

Based on feedback, we created a checklist for preparing legacy codebases:

### Required
- [ ] CLAUDE.md with Mother CLAUDE reference
- [ ] Path to legacy repo
- [ ] Jira project code
- [ ] Tech stack (old and new)

### Highly Recommended
- [ ] EVOLUTION.md with:
  - Data volumes (helps migration planning)
  - Feature history (why things were built)
  - User pain points (prioritization)
  - Admin pain points (what to fix)
  - Known bugs/workarounds
  - Old UI screenshots

### Pre-Research
- [ ] External API documentation
- [ ] Integration requirements
- [ ] SQL dumps (empty schema + full data)

---

## Lessons Learned

### What Worked
1. **Lean CLAUDE.md files** - <100 lines keeps context cost low
2. **Single source of truth** - No duplication across repos
3. **On-demand deep docs** - Don't load everything at session start
4. **Legacy repo access** - Claude examining actual code beats any description
5. **Self-documenting architecture** - The system explains itself

### What Could Be Better
1. **EVOLUTION.md needs content** - Empty templates don't help
2. **Historical context matters** - "Why was it built this way?" is valuable
3. **Data volumes help** - Claude needs to think about scale
4. **Screenshots calibrate expectations** - Even rough ones help

### The Meta Insight
**Documentation is a product**. It needs:
- User research (what does Claude need?)
- Iteration (improve based on feedback)
- Maintenance (keep it current)
- Self-documentation (explain how it works)

---

## Evolution: The Checkpoint Checklist (Instant Retrospectives)

After using this system in production across multiple projects, we identified a gap: **documentation tells Claude what exists, but not how to maintain quality as it builds.**

We added a **checkpoint checklist** (`shared/checkpoint-checklist.md`) that gets referenced at every PR and commit. It's built around one meta question:

> **"If I had to hand this codebase to a new developer tomorrow, would they understand it without me explaining anything?"**

The checklist covers:
- Architecture & design (single responsibility, DRY, configuration vs hardcoding)
- Code quality (no magic numbers, type safety, naming clarity)
- Error handling & edge cases
- Testing & reliability
- Performance & security
- Project-specific questions (white-label readiness, API compatibility, etc.)

This emerged from a greenfield rebuild where we wanted to prevent the technical debt accumulation that plagued the original project. We call it the **"Instant Retrospective"**—quality checkpoints at every natural stopping point, not just at the end of sprints or after incidents. The checklist lives alongside Mother CLAUDE and is referenced whenever Claude proposes or completes non-trivial changes.

*The next article in this series covers the Instant Retrospective approach in depth—including how we made Claude responsible for initiating these checkpoints automatically.*

---

## Try It Yourself

1. **Create a shared docs repo** with Mother CLAUDE
2. **Keep project CLAUDE.md lean** (<100 lines)
3. **Move shared docs** to single source of truth
4. **Add security** (.htaccess for web-deployed PHP)
5. **Create EVOLUTION.md** for legacy projects
6. **Get feedback** from Claude on first session
7. **Iterate** based on what's missing

---

## Why Not Just...?

**Why not just use README.md?**
READMEs are for humans browsing repos. CLAUDE.md is specifically structured for LLM context windows—lean, actionable, with clear references.

**Why not load everything into context at session start?**
Context windows are finite and expensive. Loading a 1,251-line journey system doc when you're fixing a CSS bug wastes tokens and slows responses.

**Why not rely on ChatGPT/Claude memory features?**
Memory features are session-specific and degrade over time. This system persists across sessions, machines, and even different AI tools.

**Why not just use wikis/Confluence for everything?**
Wikis are great for business docs. But technical docs that Claude reads frequently belong in git—version-controlled, close to code, and loadable without web fetching.

---

## The Core Insight

**LLMs don't need more prompts—they need better institutional memory.**

The system we built isn't about clever prompting. It's about treating documentation as infrastructure that survives beyond any single session, any single project, and any single AI tool.

---

## Appendix: Our Project Ecosystem

```
Kobumura (Company Projects):
├── littletalks-mobile      # React Native app
├── littletalks-admin       # PHP admin dashboard
├── littletalks-api         # Node.js backend
├── littlepipes             # CI/CD (PUBLIC repo)
└── littletalks-docs        # Shared docs (Mother CLAUDE)

Personal (Use shared standards):
├── WXING                   # Reference patterns
├── football                # Greenfield rewrite
└── football-pool-legacy    # Archive (2011-2020)
```

All projects reference the same Mother CLAUDE for consistency, while maintaining project-specific context in their own CLAUDE.md files.

---

*This system was built collaboratively between a human engineer and an AI collaborator—and designed so the collaboration survives beyond any single session. The 8/10 rating from a fresh Claude session validated the approach. The gaps it identified became immediate improvements. That's the feedback loop working as intended.*

*The architecture is open. The patterns are portable. The goal is simple: stop re-explaining, start building.*

---

*This article was written collaboratively with Claude, using the documentation system it describes.*

---

## Resources

The Mother CLAUDE documentation system is open source:

- **GitHub**: [github.com/Kobumura/mother-claude](https://github.com/Kobumura/mother-claude)

Feel free to fork it, adapt it, or use it as a reference for your own implementation.

---

*Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Free to use and adapt with attribution to Dorothy J. Aubrey.*
