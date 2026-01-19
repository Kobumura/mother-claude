# Documentation Architecture Guide

> **Meta-documentation**: This document explains how the Mother CLAUDE documentation system works and how to implement it in your organization.

## The Three-Tier System

```
┌─────────────────────────────────────────────────────────────────┐
│                    Tier 3: External Docs                        │
│  Business docs, wikis, Confluence, Notion                       │
│  Audience: Business partners, non-technical stakeholders        │
│  AI access: On-demand via WebFetch when explicitly needed       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                Tier 2: Shared Docs Repo                         │
│  "Mother CLAUDE" - Cross-project standards                      │
│  Audience: AI assistants, developers                            │
│                                                                  │
│  ├── CLAUDE.md              ← Shared context loaded at start    │
│  ├── shared/                ← Deep technical docs (on-demand)   │
│  └── templates/             ← Reusable templates                │
└─────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Project CLAUDE.md│  │ Project CLAUDE.md│  │ Project CLAUDE.md│
│   Tier 1:       │  │   Tier 1:       │  │   Tier 1:       │
│   Lean,         │  │   Lean,         │  │   Lean,         │
│   project-      │  │   project-      │  │   project-      │
│   specific      │  │   specific      │  │   specific      │
└─────────────────┘  └─────────────────┘  └─────────────────┘
   project-a           project-b           project-c
```

## How It Works

### Tier 1: Project CLAUDE.md Files
- **Loaded**: At session start for whichever project you're in
- **Contains**: Project-specific tech stack, file structure, dev commands
- **First line**: References Mother CLAUDE for shared context
- **Goal**: Keep LEAN (<100 lines) to minimize context cost

### Tier 2: Mother CLAUDE (Shared Docs Repo)
- **Loaded**: At session start (small, ~60-100 lines for the main CLAUDE.md)
- **Contains**: Shared standards, commit guidelines, cross-project context
- **Deep docs**: Loaded on-demand from `shared/` when working on that topic
- **Purpose**: Single source of truth for cross-project knowledge

### Tier 3: External Documentation
- **Loaded**: On-demand when explicitly needed
- **Contains**: Business docs, marketing, non-technical content
- **Access method**: WebFetch or manual reference
- **Why separate**: Not needed for most development work

## Core Principles

### 1. Lean at Load, Deep on Demand

**Problem**: Loading everything at session start wastes context and slows responses.

**Solution**:
- Keep `CLAUDE.md` files under 100 lines
- Put detailed guides in `shared/` or `docs/guides/`
- Reference them: "For analytics events, see `shared/analytics-events.md`"

### 2. Single Source of Truth

**Problem**: Same information copy-pasted across repos gets out of sync.

**Solution**:
- Shared standards live in ONE place (Mother CLAUDE)
- Projects reference, never duplicate
- When moving docs, leave pointer files

```markdown
# Document Moved
This document has been moved to `your-docs-repo/shared/journey-system.md`
```

### 3. Self-Documenting

**Problem**: New AI sessions don't understand how documentation works.

**Solution**:
- This architecture document explains the system
- First question to a new Claude: "Rate the documentation prep"
- Feedback loop improves the system

### 4. Tool-Agnostic

**Problem**: Documentation locked into one AI tool becomes useless when you switch.

**Solution**:
- All docs are plain markdown
- No tool-specific features
- Works with Claude, Cursor, Copilot, or whatever comes next

## When to Put Docs Where

| Document Type | Location | Example |
|--------------|----------|---------|
| Shared standards | Docs repo `CLAUDE.md` | Commit guidelines, Jira setup |
| Deep technical guides | Docs repo `shared/` | API contracts, journey system |
| Project-specific | Project's `CLAUDE.md` | Tech stack, dev commands |
| Project guides | Project's `docs/guides/` | Component patterns, testing |
| Session continuity | Project's `docs/session_handoffs/` | Work history, blockers |
| Business/non-technical | External wiki | Marketing, strategy |

## Adding New Documentation

### New Shared Doc (cross-project)
1. Create in docs repo `shared/`
2. Update `shared/README.md` with entry
3. If replacing existing doc in a project, leave pointer file

### New Project-Specific Doc
1. Create in that project's `docs/guides/`
2. Update project's CLAUDE.md if AI needs to know about it

### Moving Docs to Shared
1. Copy file to docs repo `shared/`
2. Replace original with pointer file
3. Update `shared/README.md`
4. Commit both repos

## Maintenance Rules

### Keep Project CLAUDE.md Lean
- Target: <100 lines
- If adding content, ask: "Does Claude need this at session start?"
- If no → put in `docs/` and reference on-demand

### Regular Review
- Quarterly: Review shared docs for staleness
- After major changes: Update affected documentation
- After new project: Ensure it follows the architecture

### Session Handoffs
- Template: `templates/session-handoff.md`
- Location: Each project's `docs/session_handoffs/`
- Filename: `YYYYMMDD-HHMM-brief-description.md`

## Legacy Project Prep Checklist

When preparing a legacy codebase for a rewrite:

### CLAUDE.md (Required)
- [ ] Reference to Mother CLAUDE for shared standards
- [ ] Project overview and purpose
- [ ] Tech stack (old and new)
- [ ] Path to legacy repo for reference
- [ ] Project tracking setup (Jira, Linear, etc.)

### EVOLUTION.md (Highly Recommended)
- [ ] **Data volumes** - Users, records, database size
- [ ] **Feature history** - When/why features were added
- [ ] **User pain points** - What did users complain about?
- [ ] **Admin pain points** - What was tedious to manage?
- [ ] **Known bugs/workarounds** - Manual fixes that were needed
- [ ] **Key design decisions** - Why things were built certain ways

### Pre-Research
- [ ] External API documentation
- [ ] Integration requirements
- [ ] SQL dumps (empty schema + full data)

### Success Metric
A well-prepped legacy project lets the AI be **productive immediately** instead of spending time discovering context. Target: AI gives 8+/10 rating on first session.

---

## For AI Sessions

When starting a new session:
1. Check which project you're in (working directory)
2. Read that project's CLAUDE.md (references Mother CLAUDE)
3. If working on shared features, read relevant `shared/` doc
4. Check `docs/session_handoffs/` for recent context
5. Use task tracking to manage your work

When creating documentation:
1. Ask: "Is this used by multiple projects?" → `shared/`
2. Ask: "Is this project-specific?" → project's `docs/guides/`
3. Ask: "Is this business/non-technical?" → external wiki
4. Keep `CLAUDE.md` files lean

---

*This architecture is designed to scale from solo developers to teams, from single projects to multi-repo ecosystems.*
