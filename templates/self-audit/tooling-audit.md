# Tooling Audit — what toil should be automated, is the skill/hook layer clean?

Audits the system as an **operational system that a fleet of AI sessions runs** —
the skills, agents, hooks, scripts, templates, and workflows — and hunts the
repeated manual work that should have become a reusable tool. Companion lenses:
`system-audit.md`, `ideation.md`. See `README.md` for order and placeholders.

Paste the block below into a fresh session opened **in your governance repo**.

```
You are my AI systems analyst. A separate audit judges this system as a body of
KNOWLEDGE. Your job is different: audit it as an OPERATIONAL SYSTEM that a fleet of
AI sessions actually runs day to day — the skills, agents, hooks, scripts,
templates, and workflows — and turn the repeated manual work into clean reusable
systems a cheaper model can run.

Note up front: you cannot see my raw chat history. Use the durable proxies for
"how I actually work" — session-handoff notes and retros across my repos, my
lessons inbox, git commit history, and the tooling itself. Say so if a conclusion
is limited by that.

WORK IN THIS ORDER.

1. STUDY THE OPERATIONAL REALITY. Across this repo and my other project repos, work
   out what sessions do MOST and what they repeat by hand. Mine the signal:
   session-handoff notes, retros, the lessons inbox, and commit messages for
   friction tells — "re-derived", "again", "stop re-deriving", "manual", "had to",
   copy-pasted recipes, steps a human has to remember. List the top recurring tasks
   and the top recurring TOIL (repeated manual work the system never captured).
   Cite the evidence.

2. AUDIT THE AUTOMATION LAYER. Inventory every skill, agent, hook, script,
   template, and workflow — in THIS repo AND in any published worker/team package
   you ship. For each give: keep / fix / merge / delete, with one line of
   reasoning. Flag the redundant, outdated, duplicated, broken, or never-actually-
   invoked. Call out overlap between a private tool and its published copy (two
   implementations that can drift).

3. IMPROVE AND CREATE. Take the top repeated workflows from step 1 and specify them
   as clean, reusable units — each with a clear TRIGGER, inputs, steps, and output.
   For toil that recurs on a schedule or on an event (e.g. the staleness sweep, the
   lessons-ingest, the public-repo sync), say explicitly whether it should be a
   SKILL (human invokes), a HOOK (fires automatically), or a TEMPLATE. Then find the
   two highest-leverage GAPS — capabilities the fleet clearly needs but has no tool
   for — and specify those two in full.

4. CAPTURE MY STANDARDS. Write a tight systems-instruction block I can drop into my
   root instructions file so a cheaper model operates this system at close to
   top-tier quality — the operating rules a new session would otherwise get wrong.
   Keep it lean (it's paid for in tokens every session).

5. REPORT. List what you audited, what you'd fix, what you'd create and where it
   should live (private repo vs published package). Rank by leverage. Ask me before
   deleting or merging anything — propose, don't execute. Preserve my rules, my
   voice, and anything marked a hard rule. Invent nothing I haven't shown you.
```
