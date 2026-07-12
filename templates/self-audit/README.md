# Self-audit harness — keep your governance system as robust as it claims to be

A governance system like this one makes a promise: *capture expensive thinking once,
so cheaper models and future sessions reproduce top-tier quality for months.* These
three prompts are how you hold your own implementation to that promise — and find the
gaps before they cost you.

They are **thinking harnesses, not one-offs.** The same three lenses work on anything
that fans out to many consumers (a template, a shared library, a product direction),
not just your docs system. Run each in a fresh session opened **in your governance
repo** so the relative paths resolve, on the strongest model you have — the whole
point is to do the thinking once and let cheaper models run the result.

| File | Lens | Question it answers |
|------|------|---------------------|
| `system-audit.md` | Knowledge / governance-as-designed | *Is the system coherent, and does it keep its promise?* |
| `tooling-audit.md` | Operational tooling / how sessions actually run | *What toil should be automated, and is the skill/hook/agent layer clean?* |
| `ideation.md` | Generative / what it could become | *What are the non-obvious ways to make it dramatically better?* |

## Run order

1. `system-audit.md` and `tooling-audit.md` are independent — run them as two
   separate sessions (they're large and want their own context; parallel is fine).
2. Feed `ideation.md` to whichever session has the fuller picture **after** its
   audit completes. Grounded ideation beats cold brainstorming.

## Adapt before running

Each prompt is written generically. Before you run it, swap the placeholders for
your reality:

- `<your root instructions file>` — the "always-loaded" context file every session
  reads (e.g. an `AGENTS`/instructions/rules file at the repo root).
- `<your governance doc>` — the doc that states the rules for adding/tiering/
  publishing docs and the lesson-learning loop.
- `<your standards docs>`, `<your process docs>`, `<your lessons inbox>` — wherever
  those live in your tree.
- `<your public snapshot repo>` — the sanitized copy you publish, if you publish one
  (skip that section if you don't).
- `<your tracker>` / `<project keys>` — your issue tracker and its project keys.
- `<a cheaper model>` — the smaller/faster model you want to run the result on.

The prompts deliberately ask the model to **propose, not edit** — a governance repo
is usually canonical and multi-author, so you apply changes yourself after reading
the report.
