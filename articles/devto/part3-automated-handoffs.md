---
title: "Mother CLAUDE: Automating Everything with Hooks"
published: false
description: How we used Claude Code hooks to automate session handoffs, context loading, and permission approvals—turning manual discipline into invisible infrastructure.
tags: ai, automation, productivity, developerexperience
series: Designing AI Teammates
canonical_url: https://github.com/Kobumura/mother-claude/blob/main/articles/devto/part3-automated-handoffs.md
---

> **TL;DR**: We built three hooks that automate the Mother CLAUDE workflow: (1) auto-generate session handoffs on context compaction, (2) load previous handoffs at session start, and (3) auto-approve safe operations. Manual discipline becomes invisible infrastructure.

*Who this is for: Anyone who wants AI memory that doesn't depend on human discipline. Anyone tired of clicking "yes" to approve safe operations.*

**Part 3 of the Designing AI Teammates series.** Part 1 covered documentation structure. Part 2 covered why session handoffs matter. This one covers automating the workflow with hooks. Part 4 will cover quality checkpoints.

---

## The Problem

Session handoffs work. We covered that in Part 2. The template captures:
- What was accomplished
- Key decisions made
- Files modified
- Next steps
- Open questions

The problem? **Humans forget to create them.**

You finish a productive session, you're in the flow, you close the terminal... and the handoff doesn't get written. The next session starts cold. All that context—gone.

We needed handoffs to happen automatically, without relying on human discipline at the end of a long session.

---

## The Solution: Claude Code Hooks

Claude Code has a hooks system that runs scripts at specific events. Two events matter for us:

| Hook | When It Fires | Why It Matters |
|------|---------------|----------------|
| **PreCompact** | Before context compression | Captures everything before detail is lost |
| **SessionEnd** | When you close the session | Captures final state |

The hook receives the full conversation transcript. We can parse it, send it to Claude Haiku for summarization, and save a structured handoff document—all automatically.

---

## The Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Claude Code Session                 │
│                                                     │
│  [Working...]  [Working...]  [Context getting full] │
│                                                     │
│                         │                           │
│                         ▼                           │
│              ┌──────────────────┐                   │
│              │  PreCompact Hook │                   │
│              └────────┬─────────┘                   │
│                       │                             │
└───────────────────────┼─────────────────────────────┘
                        │
                        ▼
              ┌──────────────────┐
              │ session_handoff  │
              │     .py          │
              │                  │
              │ 1. Read transcript
              │ 2. Parse conversation
              │ 3. Call Claude Haiku
              │ 4. Save handoff.md
              └────────┬─────────┘
                       │
                       ▼
         ┌─────────────────────────────┐
         │  docs/session_handoffs/      │
         │  20260121-1145-hooks-setup.md│
         └─────────────────────────────┘
```

---

## The Implementation

### Step 1: The Hook Script

A Python script that:
1. Receives hook input via stdin (includes transcript path)
2. Parses the JSONL transcript into readable conversation
3. Sends it to Claude Haiku with a structured prompt
4. Extracts a descriptive title for the filename
5. Saves to the project's `session_handoffs/` directory

```python
#!/usr/bin/env python3
"""
Mother CLAUDE Session Handoff Generator

Runs on PreCompact (auto) and SessionEnd events to automatically
generate session handoff documents using Claude Haiku.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
import anthropic

def parse_transcript(transcript_path: str) -> str:
    """Parse JSONL transcript into readable conversation."""
    messages = []
    with open(transcript_path, 'r', encoding='utf-8') as f:
        for line in f:
            entry = json.loads(line)
            if entry.get("type") == "human":
                content = extract_text(entry)
                messages.append(f"USER: {content[:3000]}")
            elif entry.get("type") == "assistant":
                content = extract_text(entry)
                messages.append(f"ASSISTANT: {content[:3000]}")

    # Return last 80 messages for context
    return "\n\n---\n\n".join(messages[-80:])

def generate_handoff(conversation: str, cwd: str, api_key: str):
    """Use Claude Haiku to generate a session handoff."""
    client = anthropic.Anthropic(api_key=api_key)

    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=4000,
        messages=[{
            "role": "user",
            "content": HANDOFF_PROMPT.format(
                conversation=conversation,
                project=Path(cwd).name,
                date=datetime.now().strftime("%Y-%m-%d")
            )
        }]
    )

    return response.content[0].text
```

### Step 2: The Prompt Template

The prompt asks for a comprehensive handoff matching our template:

```python
HANDOFF_TEMPLATE = """
Generate a session handoff document with these sections:

SHORT_TITLE: [2-4 words, hyphenated, for filename]

# Session Handoff - [Descriptive Title]

**Date**: {date}
**Focus**: [Main focus of this session]
**Status**: [Current state of the work]

## Quick Context
**What's Working:** [Specific things that are functional]
**What Needs Attention:** [Issues, blockers, pending decisions]

## Completed This Session
### [Feature/Task Name]
**Files Created/Modified:**
- `path/to/file.ext` - [What was done]

**Details:** [Technical specifics]

## Technical Discoveries
- **[Topic]**: [What was learned]

## Files Changed This Session
### New Files
### Modified Files

## Next Steps
1. [ ] [Actionable task]

## Open Questions
- [Unresolved decisions]
"""
```

### Step 3: Hook Configuration

In `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreCompact": [
      {
        "matcher": "auto",
        "hooks": [
          {
            "type": "command",
            "command": "python ~/.claude/hooks/session_handoff.py",
            "timeout": 120
          }
        ]
      }
    ],
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python ~/.claude/hooks/session_handoff.py",
            "timeout": 120
          }
        ]
      }
    ]
  }
}
```

### Step 4: API Key Setup

Store your Anthropic API key as an environment variable:

```bash
# Linux/Mac
export ANTHROPIC_API_KEY_HOOKS="sk-ant-..."

# Windows PowerShell
[System.Environment]::SetEnvironmentVariable(
    "ANTHROPIC_API_KEY_HOOKS",
    "sk-ant-...",
    "User"
)
```

Using a separate key (`ANTHROPIC_API_KEY_HOOKS`) lets you track usage for automated handoffs separately from your main Claude Code usage.

---

## The Result

### Before: Manual Handoffs

```
End of session:
- Forget to create handoff (60% of the time)
- Create hasty handoff (30% of the time)
- Create thorough handoff (10% of the time)

Next session:
- Spend 10-15 minutes re-establishing context
- Miss important details from previous session
- Repeat work already done
```

### After: Automatic Handoffs

```
End of session:
- Hook fires automatically
- Handoff created in ~30 seconds
- Saved to docs/session_handoffs/

Next session:
- Read most recent handoff
- Productive in 2-3 minutes
- Full context preserved
```

---

## Example Output

Here's an actual auto-generated handoff:

```markdown
# Session Handoff - Implementing Automated Session Handoffs

**Date**: 2026-01-21
**Focus**: Integrating Claude hooks to automatically generate session handoffs
**Status**: Feature complete, ready for testing

---

## Quick Context

**What's Working:**
- Claude hook script written in Python to summarize sessions
- Hooks configured to trigger on auto-compact and session end
- Handoff files being generated in the expected location

**What Needs Attention:**
- API key needs to be regenerated (was exposed during testing)
- Template may need refinement based on real-world usage

---

## Completed This Session

### Implement Hook-Driven Session Handoffs
**Files Created/Modified:**
- `~/.claude/hooks/session_handoff.py` - Python script to generate handoffs
- `~/.claude/settings.json` - Hook configuration

**Details:**
- Wrote a Python script using the Anthropic API to summarize transcripts
- Configured two hook triggers: PreCompact (auto) and SessionEnd
- Script auto-detects working directory to determine project context
- Handoff files saved to project's `docs/session_handoffs/`

---

## Technical Discoveries

- **Environment Variables**: Using separate API key for hooks allows
  tracking automated usage separately from interactive sessions
- **Hook Timing**: PreCompact fires BEFORE compression, so full context
  is still available for summarization

---

## Files Changed This Session

### New Files
- `~/.claude/hooks/session_handoff.py` - Handoff generation script

### Modified Files
- `~/.claude/settings.json` - Added hook configuration

---

## Next Steps

1. [ ] Regenerate API key (current one exposed in conversation)
2. [ ] Test on different projects to verify directory detection
3. [ ] Consider adding git commit info to handoffs

---

## Open Questions

- Should handoffs include actual code snippets from the session?
- How to handle very long sessions that exceed Haiku's context window?
```

---

## The Meta Moment: Using Claude to Summarize Claude

There's something delightfully recursive about this setup:

1. You work with Claude Code (Claude Opus/Sonnet)
2. Session ends or context fills
3. Hook sends transcript to Claude Haiku
4. Haiku summarizes what Opus/Sonnet did
5. Summary helps the next Opus/Sonnet session

**Claude is documenting its own work for its future self.**

This isn't just automation—it's AI infrastructure supporting AI collaboration.

---

## Why Two Triggers? (And the Bug We Found)

Our first implementation used two triggers:

| Trigger | When | Why |
|---------|------|-----|
| **PreCompact** | Context about to compress | Capture everything before detail is lost |
| **SessionEnd** | Session closes | Ensure final state is captured |

Simple, right? Both triggers run the same script. What could go wrong?

### The Problem We Discovered

A reader (okay, it was us during testing) noticed a flaw:

1. **PreCompact fires** → Rich, detailed handoff saved
2. **Context compresses** → Detail lost
3. **SessionEnd fires** → *Second* handoff saved (thinner, post-compression)
4. **Next session starts** → SessionStart loads the *most recent* handoff
5. **Oops** → You loaded the thin SessionEnd handoff, not the rich PreCompact one

**The good handoff got buried by the thin one.**

### The Fix: Smart Deduplication

We updated the script to track state:

```python
# PreCompact: save marker with transcript size
save_handoff_state(session_id, transcript_size)

# SessionEnd: check if PreCompact already ran
if should_skip_handoff(session_id, current_size, trigger):
    cleanup_state(session_id)
    sys.exit(0)  # Skip - no new work since PreCompact
```

The logic:
- **PreCompact** always generates a handoff and saves the transcript size
- **SessionEnd** checks: did PreCompact already run? Did the transcript grow significantly (>10%)?
  - If no significant new work → skip
  - If new work happened after compact → generate new handoff

This handles all scenarios:
- Compact then close immediately → SessionEnd skips (PreCompact got it)
- Compact, more work, then close → SessionEnd generates (new work to capture)
- Short session, just close → SessionEnd generates (only trigger)

**The lesson: test your hooks end-to-end.** The obvious solution (two triggers, same script) had a subtle interaction problem.

---

## Handling Large Sessions

Haiku has a smaller context window than Opus. For very long sessions:

1. The script takes the **last 80 messages** of the conversation
2. Each message is truncated to 3,000 characters
3. This keeps the most recent (and usually most relevant) context

For most sessions, this captures everything that matters. The early parts of very long sessions (initial exploration, early false starts) are often less valuable than the recent work anyway.

---

## Cost Considerations

Claude Haiku is cheap. A typical handoff:
- Input: ~50,000 tokens (conversation)
- Output: ~1,500 tokens (handoff)
- Cost: ~$0.02-0.03 per handoff

Even with multiple sessions per day, the monthly cost is negligible compared to the value of preserved context.

**Pro tip**: Create a separate API key for hooks. The Anthropic console shows usage per key, so you can track exactly how much your automated handoffs cost.

### Choosing a Model

As of this writing, we use Claude Haiku (`claude-3-haiku-20240307`) for handoff generation. It's cheap, fast, and good enough for structured summarization.

| Model | Cost per Handoff | Speed | When to Use |
|-------|-----------------|-------|-------------|
| Haiku | ~$0.02 | Fast | Default choice - summarization doesn't need genius |
| Sonnet | ~$0.15 | Medium | If you want richer, more nuanced summaries |
| Opus | ~$1+ | Slower | Overkill for handoffs - save it for real work |

To change models, edit `session_handoff.py`:

```python
# Default
model="claude-3-haiku-20240307"

# For richer summaries (costs more)
model="claude-sonnet-4-20250514"
```

Anthropic releases new models regularly. Check [docs.anthropic.com](https://docs.anthropic.com) for the latest model IDs. The hook script in our repo uses Haiku, but swap in whatever model suits your needs and budget.

---

## Extending the System

### Add Git Info

```python
import subprocess

def get_recent_commits():
    result = subprocess.run(
        ["git", "log", "--oneline", "-5"],
        capture_output=True, text=True
    )
    return result.stdout
```

### Add to Multiple Projects

The script auto-detects the project from `cwd` and finds the right `session_handoffs/` directory. It works across all your projects without configuration.

### Customize Per Project

If you need project-specific handoff formats, add a `.claude/handoff-config.json` to any project:

```json
{
  "template": "custom",
  "include_git": true,
  "extra_sections": ["Jira Tickets", "API Changes"]
}
```

---

## Known Limitations

### Can't Prevent Compaction
PreCompact hooks can run side effects but can't stop compaction. The handoff happens, then compaction proceeds. This is fine—we just want to capture context, not block the workflow.

### Timeout
Hooks have a 60-second default timeout (we set 120). Very long transcripts might need more time. The script handles timeouts gracefully—a failed handoff is better than a blocked session.

### API Dependency
Requires an Anthropic API key and internet connection. If the API is down, the hook fails silently. Consider adding local fallback summarization for offline work.

---

## How This Works with Agents

If you're using Claude Code's Task tool to spawn subagents (Explore, Plan, etc.), here's what you need to know:

| Event | Hook Fires? | Why |
|-------|-------------|-----|
| Main session starts | ✅ SessionStart | Loads previous handoff |
| Subagent spawned | ❌ None | Subagents are subprocesses, not new sessions |
| Subagent finishes | ❌ None* | Results return to main session |
| Main session ends | ✅ SessionEnd | Generates handoff including subagent work |

**This is actually the right behavior:**

1. The main session is the orchestrator—it has context and makes decisions
2. Subagents are workers—they do specific tasks and report back
3. The main session's handoff captures *everything*, including what subagents accomplished

You don't need separate handoffs for subagents because their work flows back to the main session. When the main session's handoff gets generated, it includes the full picture.

*\*Claude Code does have a `SubagentStop` hook if you want to capture subagent completions separately, but for most workflows the main session handoff is sufficient.*

---

## Bonus Hook #1: Auto-Load Previous Handoffs

Writing handoffs is half the equation. The other half: making sure Claude *reads* them.

### The SessionStart Hook

When you start a new Claude Code session, the `SessionStart` hook fires. We use it to automatically load the most recent handoff:

```python
# session_start.py - outputs previous handoff to stdout
handoffs = sorted(glob("docs/session_handoffs/*.md"))
if handoffs:
    print(f"Previous handoff: {handoffs[-1].name}")
    print(open(handoffs[-1]).read())
```

Claude sees this output as context at the start of every session. No manual loading required.

**Configuration:**

Add to `~/.claude/settings.json`:

```json
"SessionStart": [
  {
    "hooks": [
      {
        "type": "command",
        "command": "python ~/.claude/hooks/session_start.py",
        "timeout": 10
      }
    ]
  }
]
```

**Result:** Every new session starts with context from the previous one. The handoffs we auto-generate get auto-loaded. The circle is complete.

---

## Bonus Hook #2: Auto-Approve Safe Operations

If you've used Claude Code for more than an hour, you've clicked "yes" to approve `git status` approximately 47 times.

### The Permission Fatigue Problem

Claude Code asks permission for potentially dangerous operations. This is good! But it also asks for:
- `git status`
- `ls`
- `npm test`
- Reading files
- And dozens of other safe operations

### The PermissionRequest Hook

This hook intercepts permission requests and auto-approves safe ones:

```python
# auto_approve.py
always_safe = ["Read", "Glob", "Grep", "Write", "Edit"]

safe_bash = [
    r'^git\s+(status|log|diff|add|commit|push|pull)',
    r'^npm\s+(test|run|install)',
    r'^ls(\s|$)',
]

dangerous = [
    r'\bsudo\b',
    r'git\s+push\s+.*--force',
    r'git\s+reset\s+--hard',
]
```

**What gets auto-approved:**
- All file operations (Read, Write, Edit)
- Git operations (add, commit, push, pull)
- Package management (npm install, pip install)
- Build/test commands

**What still requires approval:**
- `sudo` anything
- `git push --force`
- `git reset --hard`
- Destructive operations

**Configuration:**

```json
"PermissionRequest": [
  {
    "matcher": "*",
    "hooks": [
      {
        "type": "command",
        "command": "python ~/.claude/hooks/auto_approve.py",
        "timeout": 5
      }
    ]
  }
]
```

**Result:** Claude flows. No more clicking "yes" fifty times a session. Dangerous operations still get caught.

---

## Project-Specific Configuration

Different projects might want different settings. Create `.claude/project.json` in any project root:

```json
{
  "handoffs_path": "docs/session_handoffs",
  "handoffs_to_load": 2
}
```

| Setting | Default | Description |
|---------|---------|-------------|
| `handoffs_path` | `docs/session_handoffs` | Where to read/write handoffs |
| `handoffs_to_load` | `1` | How many previous handoffs to load |

Both the session_handoff.py and session_start.py scripts check for this config.

---

## The Complete Hook Suite

Here's what we built:

| Hook | Trigger | What It Does |
|------|---------|--------------|
| **session_handoff.py** | PreCompact, SessionEnd | Auto-generates handoff documents |
| **session_start.py** | SessionStart | Loads previous handoff into context |
| **auto_approve.py** | PermissionRequest | Auto-approves safe operations |

**The full settings.json:**

```json
{
  "hooks": {
    "SessionStart": [{"hooks": [{"type": "command", "command": "python ~/.claude/hooks/session_start.py"}]}],
    "PreCompact": [{"matcher": "auto", "hooks": [{"type": "command", "command": "python ~/.claude/hooks/session_handoff.py"}]}],
    "SessionEnd": [{"hooks": [{"type": "command", "command": "python ~/.claude/hooks/session_handoff.py"}]}],
    "PermissionRequest": [{"matcher": "*", "hooks": [{"type": "command", "command": "python ~/.claude/hooks/auto_approve.py"}]}]
  }
}
```

---

## The Setup Checklist

1. [ ] **Install Python 3.8+** and the `anthropic` package (`pip install anthropic`)
2. [ ] **Copy hook scripts** to `~/.claude/hooks/`
3. [ ] **Configure hooks** in `~/.claude/settings.json`
4. [ ] **Set API key** as environment variable
5. [ ] **Restart terminal** (hooks load at session start)
6. [ ] **Verify** by starting a new session and checking for previous handoff

### Prefer Node.js?

We've included a smoke-tested Node.js version (`session_handoff.js`) in the repo. If you prefer Node:
- Install: `npm install @anthropic-ai/sdk`
- Update settings.json to use `node` instead of `python`

The Python version is our primary, daily-driver implementation. The Node version is provided as an alternative—if you find issues, please contribute fixes back to the repo!

---

## The Core Insight

**The best documentation is documentation that writes itself.**

Session handoffs are valuable. But relying on human discipline at the end of a long session is a recipe for forgotten context.

By automating handoffs:
- Memory persists without effort
- Every session is documented
- Context survives across sessions, machines, and time

**The goal isn't to replace human judgment. It's to ensure the conversation happens.**

---

*This system was built in a single afternoon—and documented by the very hook system it describes. The handoff you're reading about was generated by the hook that creates handoffs. That's the feedback loop working as intended.*

---

*This article was written collaboratively with Claude, using the automated handoff system it describes.*

---

## Resources

The complete hook suite and Mother CLAUDE system are open source:

- **GitHub**: [github.com/Kobumura/mother-claude](https://github.com/Kobumura/mother-claude)
- **All hooks**: `hooks/` directory
- **Settings template**: `hooks/settings-template.json`
- **Setup guide**: `hooks/README.md`

Feel free to fork it, adapt it, or use it as a reference for your own implementation.

---

*Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Free to use and adapt with attribution to Dorothy J. Aubrey.*
