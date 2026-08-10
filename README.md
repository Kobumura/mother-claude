# Mother CLAUDE

> **A governed operating model for AI-assisted software delivery** — durable context,
> autonomous worker sessions, explicit human decision rights, isolated execution, quality
> gates, and auditable provenance. Built and run in production, then genericized.

Mother CLAUDE started as a documentation architecture that makes AI assistants productive
immediately — and that layer is still here, underneath. What it grew into is an operating
model for running a **team of autonomous AI coding sessions** that ship real work while a
human keeps every decision that genuinely needs one.

## The system in one picture

```
                        HUMAN
          product / UX / risk / prod-promotion
                          │
                          ▼
                      DISPATCHER
              specs features → Ready tickets
                          │
                          ▼
         ┌────────── ISSUE TRACKER ──────────┐
         │   durable state + audit trail     │
         └──────┬────────┬────────┬──────────┘
                │        │        │
             worker    worker   worker
                │        │        │
              (each in an isolated git worktree)
                └────────┼────────┘
                         ▼
                      PR + CI
                         │
                         ▼
                       STEWARD
                  review / reconcile
                    │           │
              objective      judgment
                 │              │
                 ▼              ▼
               merge          HUMAN
                              verifies
```

- **Memory:** shared + project docs, session handoffs, evolution history
- **Coordination:** the issue tracker — durable, auditable, already trusted
- **Execution:** isolated git worktrees, one ticket per worker
- **Evidence:** tests + CI + the PR itself
- **Judgment:** graduated autonomy; the calls that matter stay human

## Three layers

1. **Memory layer** — the original three-tier documentation architecture: lean per-project
   context files, shared cross-project standards, deep docs loaded on demand, session
   handoffs. This is what makes any session productive in minutes.
2. **Work layer** — the issue tracker as the *only* coordination layer: roles, queues,
   claims, isolated worktrees, PRs. No session talks to another directly; status is the
   single source of truth, chat is for attention only, never state.
3. **Governance layer** — Definition of Done, tests and CI as objective evidence, steward
   review, escalation paths, graduated trust, and explicit human decision boundaries.

## The governance model — what AI is not allowed to decide

Autonomous sessions may make **reversible engineering decisions** constrained by documented
standards and tests. Everything else escalates:

- **Product direction and UX judgment** — always human.
- **Production promotion** — human-gated, after verification. Agents never merge to a
  production branch.
- **Architecture decisions with cross-system consequences**, dependency or infrastructure
  changes with shared blast radius.
- **Security and data-governance exceptions.**
- **Anything whose correctness can't be established by objective evidence** (tests, CI,
  reproduction) — if it takes taste to judge, a human judges it.

Each task runs on an isolated branch/worktree; objective work must pass tests and CI before
an autonomous merge; and every action is signed by a stable worker identity on the tracker,
in commit trailers, and in handoffs — **vendor-neutral, auditable provenance**, not tool
branding.

## Origins — and what it governs now

Mother CLAUDE started inside a single product: an AI-assisted mobile-app rebuild where
every new session began from zero — re-deriving the codebase, the standards, and the
reasons behind decisions that had already been made, while hard-won conventions evaporated
between sessions. The documentation system was built to stop paying that tax. The work and
governance layers grew later, when the AI sessions became a team and "productive
immediately" stopped being enough — the sessions also had to be *coordinated, bounded, and
auditable*.

The internal version now governs a portfolio of products across more than a dozen
repositories:

- a **white-label React Native mobile template** and **white-label API server** — the
  product line that grew out of the original app
- a **research-collaboration SaaS platform**
- a **marketing-analytics platform**
- a **dog-health monitoring SaaS** with companion mobile app
- a **CI/CD pipeline** that builds and ships the React Native apps to both stores
- plus the **legacy PHP applications** the standards were first hardened against

Same standards, same worker protocol, same gates everywhere — the operating model is the
constant; the stacks (React Native, Node/Express, Next.js, PHP) are the variables. The
system also governs itself: the repo ships the
[self-audit harness](templates/self-audit/) it is periodically run through.

## Run an autonomous AI team — the Worker System

Everything you need is in **[`worker-system/`](worker-system/)**. The **protocol is
tracker-agnostic**; the package ships a **reference implementation** wired for Jira + Slack +
GitHub, and [`templates/adapting-to-your-tracker.md`](templates/adapting-to-your-tracker.md)
maps the eight primitives it needs onto GitHub Issues, Linear, or anything else.

| File | What it is |
|---|---|
| [worker-system/README.md](worker-system/README.md) | **Start here** — package overview + getting-started path |
| [operating-model.md](worker-system/operating-model.md) | The four roles, the board-as-coordination-layer, the trust model |
| [agent-worker-protocol.md](worker-system/agent-worker-protocol.md) | The worker rules in full (claim loop, worktree/PR isolation) |
| [onboarding.md](worker-system/onboarding.md) | Set up a machine to run workers |
| [team-up.ps1](worker-system/team-up.ps1) / [team-up.sh](worker-system/team-up.sh) | One-command launchers (Windows / macOS+Linux) |
| [standards/](worker-system/standards/) | The quality bar the workers enforce |
| [templates/agent-worker-coordination.md](templates/agent-worker-coordination.md) | The coordination pattern, reduced to a tracker capability contract |
| [scripts/team-impact.py](worker-system/scripts/team-impact.py) | Measure the payoff — tickets per active day, before vs. after |

**Measured, not benchmarked:** in production across three products, during the first month
of sustained daily operation, tickets landed per active day ran **4.2× the prior baseline**
— and the baseline was already AI-assisted solo development, so that's the conservative
comparison. The measurement script is included; run your own before/after.

## Hard-won lessons (from running it, not designing it)

- Don't let agents share a mutable checkout — worktree isolation isn't optional.
- A shared dependency tree is shared mutable state; gate installs to an owner or isolate.
- Chat is not state. If it matters, it goes on the tracker.
- Claim → reconcile → build, in that order: claim first so another worker can't take the
  ticket while you're evaluating it; reconcile against git before you build so you don't
  rebuild what already landed.
- Never auto-merge work whose Definition of Done has no objective test.
- An autonomous system needs liveness supervision that is not one of its own sessions —
  the known failure modes (worker-halt/refill race, the supervision gap) are documented,
  not hidden, in [operating-model.md](worker-system/operating-model.md).

## The memory layer — the three-tier documentation architecture

The original core, still load-bearing:

```
Tier 3: On-demand deep docs      (loaded only when needed)
Tier 2: Mother CLAUDE (shared)   (cross-project standards, lean at session start)
Tier 1: Project CLAUDE.md        (lean, project-specific, references Tier 2)
```

1. **Lean at load, deep on demand** — keep context files under ~100 lines; load detail when needed.
2. **Single source of truth** — shared standards live in one place; projects reference, never duplicate.
3. **Self-documenting** — new AI sessions understand the system without a human explaining it.
4. **Tool-agnostic** — works with Claude, Cursor, Copilot, or whatever comes next.

**Quick start:** create a shared docs repo with your standards → add a lean `CLAUDE.md` to
each project → use session handoffs to keep context across sessions → run instant
retrospectives at every commit/PR.

## Templates

| Template | Purpose |
|----------|---------|
| [`templates/CLAUDE.md`](templates/CLAUDE.md) | Project-specific context file |
| [`templates/EVOLUTION.md`](templates/EVOLUTION.md) | Historical context for legacy projects |
| [`templates/session-handoff.md`](templates/session-handoff.md) | Context preservation across sessions |
| [`templates/session-index.md`](templates/session-index.md) | Quick navigation to all session handoffs |
| [`templates/current-project-state.md`](templates/current-project-state.md) | Living snapshot of what's deployed, working, broken |
| [`templates/checkpoint-checklist.md`](templates/checkpoint-checklist.md) | Quality gates at every commit |
| [`templates/agent-worker-coordination.md`](templates/agent-worker-coordination.md) | Tracker-agnostic coordination: the capability contract + label-inbox pattern |
| [`templates/adapting-to-your-tracker.md`](templates/adapting-to-your-tracker.md) | Map the eight tracker primitives onto GitHub Issues, Linear, etc. |
| [`templates/self-audit/`](templates/self-audit/) | Adversarial self-audit prompts — audit the knowledge, the tooling, then ideate |
| [`templates/charting-pattern.md`](templates/charting-pattern.md) | Chart.js + SVG sparklines for data visualization |

## The article series

The system is documented as it was built, in a series on dev.to
([dev.to/dorothyjb](https://dev.to/dorothyjb)):

1. **[Mother CLAUDE: How We Built a Documentation System That Makes LLMs Productive Immediately](https://dev.to/dorothyjb/how-we-built-a-documentation-system-that-makes-llms-productive-immediately-59hc)** — the three-tier architecture
2. **[Session Handoffs: Giving Your AI Assistant Memory That Actually Persists](https://dev.to/dorothyjb/session-handoffs-giving-your-ai-assistant-memory-that-actually-persists-je9)** — cross-session context preservation
3. **[Automated Handoffs](articles/devto/part3-automated-handoffs.md)** — hooks that write the handoff for you
4. **[Instant Retrospectives](articles/devto/part4-instant-retrospectives.md)** — AI-initiated quality checkpoints
5. **[The Permission Effect](articles/devto/part5-permission-effect.md)** — what changes when the assistant can act
6. **[Clean Your Room](articles/devto/part6-clean-your-room.md)** — codebase hygiene as an enabling layer
7. **[Custom Agents](articles/devto/part7-custom-agents.md)** — specialized agents on top of the system

## Key concepts

**Session handoffs** — LLM sessions are ephemeral; handoffs are structured documents
capturing what was accomplished, current state, lessons, and next steps. At session end the
AI writes one; at session start the AI reads it. They double as the decision-archaeology
record: *why* something was decided, not just what changed.

**Instant retrospectives** — quality checkpoints at every natural stopping point, not just
sprint end: *"If I handed this codebase to a new developer tomorrow, would they understand
it without me explaining anything?"*

**EVOLUTION.md** — for legacy projects, more important than `CLAUDE.md`: why features were
built the way they were, what users complained about, what not to repeat. Without it the AI
understands *what* exists but not *why*.

## Philosophy

**LLMs don't need more prompts — they need better institutional memory, and autonomy needs
governance before it needs scale.**

This system isn't clever prompting. It's documentation treated as infrastructure, an issue
tracker treated as a coordination bus, CI treated as evidence, and a human kept exactly
where human judgment matters — designed to survive beyond any single session, project, or
AI vendor.

## License

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) - Free to use and adapt with attribution to Dorothy J. Aubrey.

---

*Built collaboratively between a human engineer and AI assistants—and designed so the collaboration survives beyond any single session.*
