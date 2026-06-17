# AI-Slop Prevention — the pre-commit checklist

"AI slop" is plausible-looking code that is over-long, duplicated, over-guarded, weakly typed,
or mixes concerns. **Before every commit, stop and fix if you catch:**

- [ ] `any` added (TS) / undocumented untyped boundary (JS JSDoc)
- [ ] Inline styling literal (`style={{`) or raw hex/size outside the token system
- [ ] SQL built by string interpolation/concatenation (**security stop**)
- [ ] Business logic in a route handler / screen / layout (belongs in a service/hook)
- [ ] Logic copy-pasted instead of extracted to a shared helper
- [ ] A file over its size budget, or a function > 60 lines, without justification
- [ ] Over-defensive `|| {}` / `?? []` guards against shapes that can't occur
- [ ] `catch` that swallows the error; a function that silently returns `undefined`
- [ ] Comments restating the code instead of the *why*; commented-out code left in
- [ ] `// TODO` without a tracked-ticket (`PROJ-XXX`) reference
- [ ] `eslint-disable` / `@ts-ignore` without a `// why:` line

> Full standards: [`code-standards.md`](code-standards.md). The retro/checkpoint agent runs this
> list as part of [`checkpoint-checklist.md`](../checkpoint-checklist.md).
