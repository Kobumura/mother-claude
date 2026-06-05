# Onboarding Prompt: Set Up Your Own Mother CLAUDE

This is a ready-to-paste prompt for anyone adopting Mother CLAUDE for the first time.

**How to use it:** open a fresh Claude Code session in the parent folder that holds
your project repos, then copy everything in the code block below and paste it in.
Your Claude will study this template, interview you about *your* setup, and build a
personalized version — it will **not** copy anyone else's project-specific content.

The prompt has it read the foundational article up front (the *why*), then read the
article matching each optional module right before building it — so it learns the
reasoning, not just the mechanics, without drowning the session in all seven
articles at once.

---

```
I want to set up "Mother CLAUDE" — a three-tier documentation system that makes
you (and any future Claude session) productive on my codebase immediately instead
of re-learning context every session. I want a version personalized to MY repos,
not a copy of someone else's.

Work through this in phases. Do NOT start creating files until we've finished the
interview in Phase 2.

── PHASE 1: Learn the system — the WHY, not just the HOW ──
1. Fetch and study the public template repo: https://github.com/Kobumura/mother-claude
   Read at minimum: README.md, DOCUMENTATION-ARCHITECTURE.md, the templates/
   folder, hooks/README.md, and the agents/ folder.
2. Then read articles/devto/part1-documentation-system.md in that repo. This is the
   foundational reasoning behind the whole system — read it so you understand WHY
   the architecture is shaped this way, not just how to reproduce it.
3. Note that the repo has a 7-part article series in articles/devto/. You do NOT
   need to read them all now (that would waste context). Instead, read the one that
   matches each optional module I choose, right before you build that module:
       part2-session-handoffs      → session handoffs
       part3-automated-handoffs    → auto handoff hooks
       part4-instant-retrospectives→ retrospectives / checkpoint checklist
       part5-permission-effect     → auto-approve hook
       part6-clean-your-room       → docs hygiene
       part7-custom-agents         → custom agents
4. When you've done 1–2, summarize back to me in ~10 lines: the three tiers, what
   "lean at load, deep on demand" means, and what optional pieces exist. Wait for
   me to confirm before continuing.

── PHASE 2: Interview me (this is the important part) ──
The template was built for someone else's projects, so a lot of it is specific to
them (their issue tracker, project names, team setup, OS, file paths). DO NOT copy
any of that. Instead, ask me about MY setup. Ask in small batches and adapt your
follow-ups to my answers. Cover at least:

  • My projects: how many repos, what each one is, the tech stack of each
    (React Native? Node? Python? PHP? something else?), and where they live on disk.
  • My OS and shell (affects how hooks get installed).
  • Issue tracking: do I use Jira, Linear, GitHub Issues, something else, or
    nothing? (Don't assume Jira.) If I use one, how should you reference tickets?
  • Team: am I solo, or do multiple people / machines work these repos? (Decides
    whether I need parallel-work coordination and user-detection rules.)
  • Which optional modules I want, and tailored to my stack:
      - Session handoffs (auto-generated at context limits / session end)
      - Session-start hook that loads the last handoff automatically
      - Auto-approve hook for safe operations
      - Instant retrospectives / a checkpoint checklist at every commit
      - A code style guide  → ask which languages and my conventions
      - A testing guide      → ask my test runners and conventions
      - Custom agents (e.g. a retro agent, a docs-writer) → which ones
      - Any deep shared docs I keep re-explaining (APIs, data model, deploy, etc.)
  • Commit/PR preferences (e.g. do I want AI attribution in commits or not?).

── PHASE 3: Build MY Mother CLAUDE ──
Based on my answers, and reading the matching article from the Phase 1 map before
building each optional module so the reasoning informs the implementation:
1. Create a dedicated shared docs repo (my "Mother CLAUDE") — propose a name and
   location and confirm with me.
2. Generate a LEAN shared CLAUDE.md (<100 lines) containing only the standards I
   actually said I want, in my terms — not the template's example content.
3. Add a lean per-project CLAUDE.md to each of my repos whose first line points to
   the shared repo for cross-project context.
4. Create only the deep shared docs and templates I asked for, in shared/.
5. If I opted into any hooks, install them following the template's hooks/README.md,
   adjusted for MY OS, and show me how to verify they fire.

── PHASE 4: Make it load every session ──
1. Verify the session-start loading works (or, if I skipped the hook, tell me the
   exact ritual: "at the start of each session, read this repo's CLAUDE.md, which
   points to the shared CLAUDE.md").
2. Give me a short "how to use this every day" cheat sheet: what loads
   automatically, what to say to pull in a deep doc, and when handoffs/retros fire.

Throughout: keep CLAUDE.md files lean, put detail in on-demand docs, and ask me
whenever you're unsure rather than copying a default from the template.
```
