# Mother CLAUDE

> **A three-tier documentation architecture that makes AI assistants productive immediately.**

Mother CLAUDE is a documentation system designed to solve the "context problem" with AI coding assistants. Instead of re-explaining your codebase every session, you build durable documentation that any AI can read and understand instantly.

## The Problem

Every time you start a new session with an AI assistant, you lose context:
- Project structure? Forgotten.
- Coding conventions? Gone.
- Why that weird workaround exists? Vanished.

You spend the first 10-15 minutes of every session re-establishing context that existed yesterday.

## The Solution

A three-tier documentation system:

```
┌─────────────────────────────────────────────────────────┐
│              Tier 3: On-Demand Deep Docs                │
│  Detailed guides loaded only when needed                │
│  → journey-system.md, api-contracts.md, etc.            │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│              Tier 2: Mother CLAUDE (Shared)             │
│  Cross-project standards, commit guidelines, Jira setup │
│  → Loaded at session start (lean) + on-demand (deep)    │
└─────────────────────────────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
│ Project CLAUDE.md │ │ Project CLAUDE.md │ │ Project CLAUDE.md │
│ Tier 1: Lean,     │ │ Tier 1: Lean,     │ │ Tier 1: Lean,     │
│ project-specific  │ │ project-specific  │ │ project-specific  │
└───────────────────┘ └───────────────────┘ └───────────────────┘
```

### Core Principles

1. **Lean at load, deep on demand** - Keep `CLAUDE.md` files under 100 lines. Load detailed docs only when needed.

2. **Single source of truth** - Shared standards live in one place. Projects reference, not duplicate.

3. **Self-documenting** - The system explains itself. New AI sessions understand without human explanation.

4. **Tool-agnostic** - Works with Claude, Cursor, Copilot, or whatever comes next.

## Quick Start

1. **Create a shared docs repo** with your organization's standards
2. **Add `CLAUDE.md` to each project** - lean, specific, references shared docs
3. **Use session handoffs** to maintain context across sessions
4. **Run instant retrospectives** at every commit/PR

## Templates

This repo includes templates to get you started:

| Template | Purpose |
|----------|---------|
| [`templates/CLAUDE.md`](templates/CLAUDE.md) | Project-specific context file |
| [`templates/EVOLUTION.md`](templates/EVOLUTION.md) | Historical context for legacy projects |
| [`templates/session-handoff.md`](templates/session-handoff.md) | Context preservation across sessions |
| [`templates/session-index.md`](templates/session-index.md) | Quick navigation to all session handoffs |
| [`templates/current-project-state.md`](templates/current-project-state.md) | Living snapshot of what's deployed, working, broken |
| [`templates/checkpoint-checklist.md`](templates/checkpoint-checklist.md) | Quality gates at every commit |

## The Article Series

This system is documented in a three-part series on dev.to:

1. **[Mother CLAUDE: How We Built a Documentation System That Makes LLMs Productive Immediately](https://dev.to/dorothyjb/how-we-built-a-documentation-system-that-makes-llms-productive-immediately-59hc)** - The three-tier architecture

2. **[Session Handoffs: Giving Your AI Assistant Memory That Actually Persists](https://dev.to/dorothyjb/session-handoffs-giving-your-ai-assistant-memory-that-actually-persists-4mp2)** - Cross-session context preservation

3. **Instant Retrospectives** (coming soon) - AI-initiated quality checkpoints

## Key Concepts

### Session Handoffs

LLM sessions are ephemeral. Session handoffs are structured documents that capture:
- What was accomplished
- Current state
- Lessons learned
- Next steps
- Key files modified

At session end, the AI creates a handoff. At session start, the AI reads it. Context restored in seconds.

### Instant Retrospectives

Quality checkpoints at every natural stopping point, not just at sprint end. The AI asks:

> "If I had to hand this codebase to a new developer tomorrow, would they understand it without me explaining anything?"

### EVOLUTION.md

For legacy projects, `EVOLUTION.md` is more important than `CLAUDE.md`. It captures:
- Why features were built the way they were
- What users complained about
- Bugs that required manual fixes
- What not to repeat

Without it, the AI can understand *what* exists but not *why* it exists.

## Philosophy

**LLMs don't need more prompts—they need better institutional memory.**

This system isn't about clever prompting. It's about treating documentation as infrastructure that survives beyond any single session, any single project, and any single AI tool.

## License

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) - Free to use and adapt with attribution to Dorothy J. Aubrey.

---

*Built collaboratively between a human engineer and AI assistants—and designed so the collaboration survives beyond any single session.*
