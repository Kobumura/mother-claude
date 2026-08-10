---
title: "/insights, or Why the Analytics Developer Had No Analytics"
published: true
description: "Visibility over vibes: I spent a month building an analytics product while running my AI collaboration completely blind. Then I ran /insights and the numbers held up a mirror."
tags: ai, productivity, analytics, developerexperience
series: AI Collaboration in Production
canonical_url: https://github.com/Kobumura/mother-claude/blob/master/articles/devto/ai-collaboration-in-production/insights.md
---

> **TL;DR**: You wouldn't run infrastructure without monitoring. You shouldn't run AI collaboration without it either. Claude Code's `/insights` command gives you a usage dashboard for your coding sessions -- token costs, tool patterns, session behavior. What it reveals about how you actually work with AI is more interesting than the numbers themselves.

*Who this is for: Anyone using AI coding assistants who wants to understand their own collaboration patterns -- not just ship features. Works with any tool that exposes usage data, but the examples here use Claude Code.*

I've spent the last year building the operational infrastructure for AI-assisted development -- [documentation systems](https://dev.to/dorothyjb/how-we-built-a-documentation-system-that-makes-llms-productive-immediately-59hc), automated [session handoffs](https://dev.to/dorothyjb/session-handoffs-giving-your-ai-assistant-memory-that-actually-persists-je9), [quality enforcement](https://dev.to/dorothyjb/mother-claude-instant-retrospectives-assign-quality-enforcement-to-your-ai-3n4b), [custom agents](https://dev.to/dorothyjb/mother-claude-custom-agents-or-how-we-accidentally-built-a-team-nak). All of it focused on making AI collaboration reliable and repeatable across sessions and projects, but none of it focused on measuring whether it actually does. This from me, the agile evangelista who murmurs "outcomes over outputs" while brushing her teeth every morning.

That's like building a SaaS analytics dashboard and forgetting to add analytics for yourself -- which, having spent the last month wiring up data sources for a monitoring product, is an irony I refuse to let pass without comment.

The cobbler's children had no shoes. The analytics developer had no analytics.

---

## The Problem

I've been running Claude Code as a full-fledged member of my engineering workflow for months. [Custom agents](https://dev.to/dorothyjb/mother-claude-custom-agents-or-how-we-accidentally-built-a-team-nak) handle ticket management and code review. [Hooks](https://dev.to/dorothyjb/mother-claude-automating-everything-with-hooks-12jh) auto-generate [session handoffs](https://dev.to/dorothyjb/session-handoffs-giving-your-ai-assistant-memory-that-actually-persists-je9). [Documentation](https://dev.to/dorothyjb/how-we-built-a-documentation-system-that-makes-llms-productive-immediately-59hc) loads at session start so Claude hits the ground running.

All of it works. I know because the code ships, the quality holds, and sessions start productive instead of cold.

But here's what I didn't know: **how am I actually using all of this?**

How much of a session is spent on feature work versus housekeeping? How often do custom agents get invoked? Which tools dominate? What does my token spend look like when I'm not paying attention?

I had no idea. I was flying the plane without looking at the instruments.

---

## What /insights Does

Claude Code has a built-in command I'd been ignoring for months: `/insights`. It generates a usage report covering your recent Claude Code activity -- sessions, tokens, tools, costs, and patterns.

I ran it expecting a dry table of numbers. What I got was a mirror.

---

## What the Numbers Reveal

The report breaks down several dimensions of your AI collaboration. The specific metrics evolve as the feature matures, but the categories that matter are consistent.

### Token Usage

How many tokens you're consuming per session, split between input (what Claude reads) and output (what Claude generates). This is your cost driver and your attention map.

**What surprised me**: My input tokens were consistently 4-5x my output tokens. That ratio tells a story -- Claude is reading far more than it's writing. Context loading, file scanning, documentation parsing, handoff ingestion. The "productive" output is a fraction of the total work.
![Image description](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/rdy5onrt4ia3y0aw4p2b.jpg)

If you're optimizing for cost, the answer isn't "make Claude write less." The answer is "make sure what Claude reads is worth reading." Every bloated file, every redundant doc section, every file Claude has to re-read because the first pass wasn't clear enough -- that's showing up in your input token count.

### Tool Usage

Which tools Claude reaches for most -- file reads, file edits, searches, bash commands, web fetches. This is your workflow fingerprint, and it's different for everyone.

**What surprised me**: File reads dominated everything by a wide margin. The ratio was roughly 5:1 reads to edits on a heavy coding day. Claude spends most of its tool budget *understanding* the codebase, not changing it.

If Claude is reading your codebase constantly -- and the numbers prove it is -- then every minute you spend [making code scannable](https://dev.to/dorothyjb/how-we-built-a-documentation-system-that-makes-llms-productive-immediately-59hc) saves multiples in token spend and session efficiency. Clear function names, logical file organization, and well-placed comments aren't just good practice. They're measurable cost optimization.

### Session Patterns

How long sessions last, how many turns they take, when compaction happens.

**What surprised me**: My most productive sessions were not the longest ones. The sessions where the most code shipped were in the 45-90 minute range -- long enough to build something significant, short enough that context stayed fresh. The 3+ hour marathons had more compactions, more re-orientation, and more wasted tokens recovering context that had been compressed away.

![Image description](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/tuzhs2wpxh9s61nk4yph.jpg)
[Session handoffs](https://dev.to/dorothyjb/session-handoffs-giving-your-ai-assistant-memory-that-actually-persists-je9) at natural stopping points aren't just good practice. They're cost optimization. A clean handoff at 90 minutes beats a compaction at 180 minutes in both token efficiency and output quality.

---

## The Meta-Realization

I spent the last month building an analytics dashboard -- wiring up RevenueCat, Google Analytics, Meta Ads, OneSignal, and a dozen other data sources. The whole point of the product is giving app developers visibility into what's actually happening with their business. Revenue, costs, user behavior. All in one place.

And I was doing this while running my AI collaboration completely blind.

There's a particular kind of professional humiliation that comes from building a monitoring tool while having zero monitoring yourself. I'm choosing to call it "quality motivation" instead of "embarrassing."

`/insights` is that same idea applied to your AI workflow -- visibility into how you actually work, not how you think you work.

---

## What I Changed After Looking at the Data

![Image description](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/kggesda64hmrdpyxogdr.jpg)
### 1. Shorter Sessions, More Handoffs

The data showed diminishing returns past 90 minutes. Not a cliff -- more of a slow leak. Tokens per useful output started climbing as compaction kicked in and context degraded. So I tightened up: deliberate stopping points, automatic handoff generation, and a fresh session for the next chunk of work.

I already knew this in theory, but seeing the numbers made it real.

### 2. Documentation as Token Optimization

When Claude reads 5 files for every file it edits, the return on clear code is higher than you'd think. I started paying more attention to function naming, file organization, and comments in hot paths where Claude kept re-reading the same functions across sessions.

This isn't about writing more documentation. It's about writing documentation that reduces re-reads. A clear function name saves a file read. A well-placed comment prevents Claude from scanning three other files for context.

### 3. Agent Cost Visibility

Running `/insights` after sessions that used custom agents showed context isolation in action. Each agent -- retro, Jira, cross-repo -- had its own token footprint, separate from the main session. The main session stayed lean because the specialized work had its own context budgets.

[Custom agents](https://dev.to/dorothyjb/mother-claude-custom-agents-or-how-we-accidentally-built-a-team-nak) don't just organize your workflow. They optimize your token spend. And `/insights` is how you prove it.

---

## The Broader Point

Here's what matters about `/insights` beyond any specific metric: it turns AI collaboration from a feeling into a measurement.

| Before /insights | After /insights |
|-----------------|-----------------|
| "That was a productive session" (was it?) | "That session used X tokens across Y tool calls" |
| "This is getting expensive" (is it?) | "My daily cost is $A, split between sessions and agents" |
| "Claude is great at this" (compared to what?) | "Feature sessions average M turns; debugging averages N" |

Most people using AI coding assistants are optimizing based on vibes. That's fine when you're starting out. It's less fine when you're running production workflows across multiple projects with custom agents and automated hooks.

At some point, you need data.

---

## How to Use /insights Effectively

**Run it weekly.** Don't obsess over per-session metrics. Look for trends: is your token spend creeping up? Are sessions getting longer without getting more productive? Is one tool dominating in ways that suggest inefficiency?

**Compare session types.** Feature development sessions should look different from debugging sessions. If they don't -- if debugging sessions use the same tool mix as feature work -- that might indicate you're not giving Claude enough context to debug efficiently.

**Check agent balance.** If you're using custom agents, `/insights` shows whether they're being invoked appropriately. An agent that never fires might have a bad description. An agent that fires constantly might be doing work that belongs in your base documentation instead.

**Establish team baselines.** If your team is using Claude Code, comparing insights across developers reveals workflow differences that would otherwise stay invisible. One developer burning tokens on excessive file reads often points to unclear code or missing documentation -- not a personal workflow problem. Another developer's short, focused sessions with clean handoff patterns become a template, not a mystery. The data turns individual habits into organizational learning.

---

## Common Objections

### "I don't care about token costs"

It's not about cost. **Token usage is a proxy for where Claude spends its attention.** High read-to-edit ratios might mean your code is hard to parse. Long sessions with many compactions might mean your handoff discipline has slipped. The metrics are a lens, not a bill.

### "This seems like navel-gazing"

If your workflow is productive and you're happy with it, you don't need to analyze it. But if you've ever wondered "why did that session feel unproductive?" or "why is this costing more than I expected?" -- the data answers those questions in seconds instead of speculation.

### "The numbers change too much to be useful"

A single session's numbers are noise. A week of sessions is signal. A month is a trend. Look for patterns, not absolutes.

### "I'd rather just code"

Running `/insights` takes 10 seconds. Reviewing the output takes 2 minutes. If those 2 minutes reveal a pattern that saves you 20 minutes of wasted context-rebuilding per session, the math works out in your favor by Friday.

---

## The Core Insight

> **Visibility over vibes.**

Most of us jumped into AI-assisted development headfirst and never looked back to see how we were actually using it. `/insights` is the rearview mirror -- it shows where the collaboration is working, where it's leaking, and where to tighten up based on data instead of gut feeling.

Monitor your code. Monitor your infrastructure. Monitor your AI collaboration. The pattern is the same everywhere.

The dashboard developer finally checked her own dashboard.

---

*This article was written collaboratively with Claude, as part of the AI collaboration system it describes measuring. The graphics are entirely Gemini; I could never approach something this great looking using only stick figures and dog paws.*

---

## Resources

- **Claude Code**: [claude.com/claude-code](https://claude.com/claude-code)
- **Mother CLAUDE** (the documentation system referenced above): [github.com/Kobumura/mother-claude](https://github.com/Kobumura/mother-claude)

---

*Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Free to use and adapt with attribution to Dorothy J. Aubrey.*
