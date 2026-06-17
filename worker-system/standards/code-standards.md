# Code Standards (All Projects)

> **Canonical principles live here; stack-specific application lives per-repo.** Each project
> carries a `docs/engineering/coding-standards.md` + `testing-standards.md` trio that adapts
> these principles to its stack (React Native design tokens, Express layer contract,
> Next/Tailwind v4 tokens, etc.), plus a dated audit baseline under `docs/audits/`. When the
> principles here and a repo-local doc disagree, the repo-local doc wins for that repo's stack
> specifics — but the principles (separation of concerns, no slop, type honesty, test assertion
> quality) are universal. New repos: clone the trio and adapt.
>
> The pre-commit gate is its own doc: [`ai-slop-checklist.md`](ai-slop-checklist.md).

## Styling (React Native)

- **Use NativeWind** (Tailwind CSS for React Native) as the default styling approach
- **No inline styles** — never use `style={{}}` in screen/component files
- **No hardcoded colors** — use theme tokens (Tailwind classes), not `#hex` values
- **Separate concerns** — styling lives in className props (NativeWind) or dedicated style files, never mixed into business logic

## Testing Requirements

Every project must have comprehensive tests. **Every new component gets a test file.**

### Test Suites by Project Type

| Project Type | Unit/Component | E2E / UI | Runner |
|-------------|---------------|----------|--------|
| React Native | Jest + React Testing Library | Maestro | `npm test` |
| Node.js API | Jest | Supertest (HTTP) | `npm test` |
| PHP | PHPUnit | — | `phpunit` |

### What "Comprehensive" Means

- **Unit tests**: Every utility function, hook, and service method
- **Component tests**: Every new React component gets a `.test.tsx` file alongside it
- **Integration tests**: API endpoints tested with actual request/response cycles
- **E2E tests** (mobile): Critical user flows tested with Maestro (use `testID` on every interactive element, kebab-case). See [`../playbooks/maestro-playbook.md`](../playbooks/maestro-playbook.md).

### Test File Conventions

- Test files live **next to** the file they test: `Button.tsx` → `Button.test.tsx`
- Use descriptive test names: `it('shows error message when login fails')` not `it('test 1')`
- Test the behavior, not the implementation — assert what the user sees, not internal state

### Quality Over Coverage %

Coverage % is a **floor, not a goal** — it proves a line ran, not that behavior is asserted.
Optimize for assertion quality and critical-path protection:

- **No slop tests.** A test that can't fail is worse than none. Banned: render-and-assert-
  nothing, blind `toMatchSnapshot`, over-mocking until the test only verifies the mock,
  `expect(true)`. Every test asserts an observable outcome.
- **Critical paths** (money, auth, entitlements, deletion, data integrity) target **≥85%** with
  invariant coverage — a blended global number must never hide a gap here.
- **Beyond unit tests:** add **integration/contract tests** where a client and server can drift,
  and **mutation testing** (e.g. Stryker) on money-path logic — the only reliable way to prove
  the suite would catch a real regression.
- **Migrations** that alter data carry a test asserting before/after row state, and a
  sentinel-guarded off-prod dry-run before shipping.
- **Flakes** are quarantined and tracked, never silently tolerated.

## Code Organization

- **Single responsibility** — one component/function per file, one concern per function
- **Business logic separate from UI** — hooks for logic, components for display
- **No magic numbers/strings** — use named constants
- **Type safety** — no `any` types in TypeScript; define proper interfaces

## Separation of Concerns — the layer contract (all stacks)

Every project has a layer contract; the names differ but the rule is the same: **one file does
one job, and concerns never bleed across layers.**

| Stack | Layers (data flows down, never up or sideways) |
|---|---|
| React Native | screens (compose) → components (render) → services (logic/fetch) → store/utils (state/pure). Services contain **no JSX/StyleSheet** and never import screens. |
| Node/Express | routes (wire + validate) → services (logic) → data layer (parameterized SQL). `req`/`res` stop at the route; SQL never lives in a handler. |
| Next.js | routes/layouts (compose + server-fetch) → components (render) → `lib/` (fetch/pure). Server-first; `'use client'` at the leaf. |
| PHP | controllers → services → data access (see [`../php-data-access.md`](../php-data-access.md)). |

Hard rule across all stacks: **the same logic is never copy-pasted across two entry points**
(a route and a worker, two screens) — both call the shared function.

## File Size & Complexity Budgets

Review triggers (a ratcheted linter can enforce later):

| Metric | Soft cap | Hard cap |
|---|---|---|
| File length | 400–500 lines | 800–1,000 lines (must split) |
| Function / handler | 60 lines | — |
| Route handler / screen render body | 40 lines of logic | — |
| Cyclomatic complexity | 15 | — |

Long files are where duplication, dead branches, and mixed concerns hide. Length is a smell,
not a style preference.
