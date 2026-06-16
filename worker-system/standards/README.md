# standards/ — what the workers enforce

The quality bar the worker system holds the line on. Workers self-review against these; the
Scrum Master enforces them on every PR; the graduated-trust gate won't auto-merge work that
violates them.

| File | What it is |
|---|---|
| [code-standards.md](code-standards.md) | The canonical code standards — styling, testing, the layer contract (separation of concerns), file-size budgets, type honesty. |
| [ai-slop-checklist.md](ai-slop-checklist.md) | The pre-commit gate — the checklist that catches the failure modes AI code review misses (type escapes, inline styles, SQL injection, copy-paste, swallowed errors). |
| [e2e-testing-standards.md](e2e-testing-standards.md) | End-to-end testing conventions — testID naming, selector priority, flow structure, CI integration. |
| [maestro-playbook.md](maestro-playbook.md) | The hard-won operational playbook for Maestro mobile E2E — flake/brittleness patterns, simulator + bundler gotchas, mocking strategy, CI wiring. |

These are generic, adapt-to-your-stack standards. Each repo can extend them with a stack-specific
`coding-standards.md` / `testing-standards.md`; the repo-local doc wins on specifics, but the
universal principles here don't bend.
