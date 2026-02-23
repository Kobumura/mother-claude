#!/usr/bin/env python3
"""
Mother CLAUDE Session Handoff Generator

This hook runs on PreCompact (auto) and SessionEnd events to automatically
generate session handoff documents using Claude Haiku.

Reads the conversation transcript and creates a structured handoff file
following the Mother CLAUDE session handoff template.

SETUP:
1. pip install anthropic
2. Set ANTHROPIC_API_KEY_HOOKS environment variable
3. Configure in ~/.claude/settings.json (see settings-template.json)
"""

import hashlib
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# Directory for tracking session state (prevents duplicate handoffs)
HOOKS_STATE_DIR = Path.home() / ".claude" / "hooks" / ".state"

try:
    import anthropic
except ImportError:
    print("Error: anthropic SDK not installed. Run: pip install anthropic", file=sys.stderr)
    sys.exit(1)


HANDOFF_TEMPLATE = """
You are generating a session handoff document for an AI coding assistant.
This document will help the next Claude session understand what was accomplished and continue seamlessly.

**Project**: {project_name}
**Trigger**: {trigger}
**Working Directory**: {cwd}

Based on this conversation transcript, create a comprehensive session handoff document.

CONVERSATION TRANSCRIPT:
{conversation}

---

Generate a markdown document following this EXACT structure. Be thorough and specific.

CRITICAL INSTRUCTIONS:
- First line must be a SHORT_TITLE (2-4 words, lowercase, hyphenated) for the filename
- Extract SPECIFIC file names, paths, and technical details from the conversation
- **Capture DECISIONS and their RATIONALE** - not just what was done, but WHY
- Include Jira tickets, GitHub issues, or other references if mentioned (e.g., CD-123, #456)
- Use markdown TABLES for structured data (migrations, rules, phases, status tracking)
- Include brief code snippets or SQL schemas if they were significant
- For architecture decisions, explain the alternatives considered and why one was chosen

---

SHORT_TITLE: [2-4 word hyphenated title like "hooks-auto-handoffs" or "api-refactor-complete"]

# Session Handoff - [Descriptive Title]

**Date**: {date}
**Focus**: [One line describing the main focus of this session]
**Status**: [What state is the work in? e.g., "Feature complete, needs testing" or "In progress, blocked on X"]

---

## Quick Context

**What's Working:**
- [Specific things that are functional now]
- [Include file names and features]

**What Needs Attention:**
- [Issues, blockers, or things to watch]
- [Pending decisions]

---

## Completed This Session

[Use a table if there are multiple phases/tickets:]

| Phase | Ticket | Description | Status |
|-------|--------|-------------|--------|
| 1 | CD-XXX | [What] | Done/In Progress |

### [Feature/Task Name 1]
**Files Created/Modified:**
- `path/to/file.ext` - [What was done]

**Details:**
[Specific technical details, configurations, code patterns used]

---

## Key Decisions & Rationale

[This section is CRITICAL - capture the WHY behind architectural choices]

- **[Decision]**: [What was decided]
  - *Why*: [The reasoning - what alternatives were considered, why this approach won]

- **[Decision]**: [What was decided]
  - *Why*: [The reasoning]

---

## Technical Discoveries

- **[Topic]**: [What was learned - gotchas, patterns, insights]

---

## Files Changed This Session

### New Files
- `path/to/new/file.ext` - [Purpose]

### Modified Files
- `path/to/modified/file.ext` - [What changed]

---

## Next Steps

1. [ ] [Specific actionable task with ticket reference if applicable]
2. [ ] [Next task]

---

## Open Questions

[Include options if they were discussed:]

- **[Question]**: [The unresolved decision]
  - Option A: [Description]
  - Option B: [Description]

---

## Environment

- **Platform**: {platform}
- **Working Directory**: {cwd}
"""


def get_api_key():
    """Get API key from environment variable."""
    key = os.environ.get("ANTHROPIC_API_KEY_HOOKS") or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        print("Error: ANTHROPIC_API_KEY_HOOKS or ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    return key


def get_transcript_size(transcript_path: str) -> int:
    """Get the size of the transcript file in bytes."""
    try:
        return Path(transcript_path).stat().st_size
    except (FileNotFoundError, OSError):
        return 0


def get_state_file(session_id: str) -> Path:
    """Get the path to the state file for this session."""
    HOOKS_STATE_DIR.mkdir(parents=True, exist_ok=True)
    safe_id = hashlib.md5(session_id.encode()).hexdigest()[:16]
    return HOOKS_STATE_DIR / f"handoff_{safe_id}.json"


def save_handoff_state(session_id: str, transcript_size: int):
    """Save state after generating a handoff (called by PreCompact)."""
    state_file = get_state_file(session_id)
    state = {
        "session_id": session_id,
        "transcript_size": transcript_size,
        "timestamp": datetime.now().isoformat()
    }
    try:
        with open(state_file, 'w') as f:
            json.dump(state, f)
    except IOError:
        pass


def should_skip_handoff(session_id: str, current_transcript_size: int, trigger: str) -> bool:
    """
    Check if we should skip generating a handoff.

    Skip if:
    - This is SessionEnd trigger
    - A PreCompact handoff was already generated for this session
    - The transcript hasn't grown significantly (< 10% larger)
    """
    if trigger in ("auto", "PreCompact"):
        return False

    state_file = get_state_file(session_id)
    if not state_file.exists():
        return False

    try:
        with open(state_file, 'r') as f:
            state = json.load(f)
        prev_size = state.get("transcript_size", 0)
        if prev_size > 0:
            growth = (current_transcript_size - prev_size) / prev_size
            if growth < 0.10:
                print(f"SessionEnd: Skipping (transcript grew {growth:.1%} since PreCompact)")
                return True
        return False
    except (json.JSONDecodeError, IOError):
        return False


def cleanup_state(session_id: str):
    """Clean up state file after session ends."""
    try:
        get_state_file(session_id).unlink(missing_ok=True)
    except IOError:
        pass


def parse_transcript(transcript_path: str) -> str:
    """Parse JSONL transcript into readable conversation format."""
    messages = []

    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)

                    if entry.get("type") == "human":
                        content = entry.get("message", {}).get("content", "")
                        if isinstance(content, list):
                            text_parts = [c.get("text", "") for c in content if c.get("type") == "text"]
                            content = "\n".join(text_parts)
                        if content.strip():
                            messages.append(f"USER: {content[:3000]}")

                    elif entry.get("type") == "assistant":
                        content = entry.get("message", {}).get("content", "")
                        if isinstance(content, list):
                            text_parts = [c.get("text", "") for c in content if c.get("type") == "text"]
                            content = "\n".join(text_parts)
                        if content.strip():
                            messages.append(f"ASSISTANT: {content[:3000]}")

                except json.JSONDecodeError:
                    continue

    except FileNotFoundError:
        print(f"Warning: Transcript not found at {transcript_path}", file=sys.stderr)
        return ""
    except Exception as e:
        print(f"Warning: Error reading transcript: {e}", file=sys.stderr)
        return ""

    # Return last 80 messages for context
    recent_messages = messages[-80:]
    return "\n\n---\n\n".join(recent_messages)


def find_handoff_directory(cwd: str) -> Path:
    """Find or create the session_handoffs directory for this project."""
    cwd_path = Path(cwd)

    # Check for project config first
    config_path = cwd_path / ".claude" / "project.json"
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if "handoffs_path" in config:
                    custom_path = cwd_path / config["handoffs_path"]
                    custom_path.mkdir(parents=True, exist_ok=True)
                    return custom_path
        except (json.JSONDecodeError, IOError):
            pass

    # Auto-detect common locations
    possible_paths = [
        cwd_path / "docs" / "session_handoffs",
        cwd_path / "session_handoffs",
        cwd_path / ".claude" / "session_handoffs",
    ]

    for path in possible_paths:
        if path.exists():
            return path

    # Default to docs/session_handoffs
    default_path = cwd_path / "docs" / "session_handoffs"
    default_path.mkdir(parents=True, exist_ok=True)
    return default_path


def extract_short_title(content: str) -> str:
    """Extract the SHORT_TITLE from the generated content."""
    # Look for SHORT_TITLE: line (case-insensitive)
    match = re.search(r'SHORT_TITLE:\s*(.+)', content, re.IGNORECASE)
    if match:
        title = match.group(1).strip().lower()
        title = re.sub(r'[\[\]"\']', '', title)
        title = re.sub(r'\s+', '-', title)
        title = re.sub(r'[^a-z0-9-]', '', title)
        return title[:50]

    # Fallback: check if first line looks like a slug (hyphenated, no spaces)
    first_line = content.strip().split('\n')[0].strip()
    if re.match(r'^[a-z0-9-]+$', first_line) and '-' in first_line and len(first_line) < 60:
        return first_line[:50]

    return "session"


def remove_short_title_line(content: str) -> str:
    """Remove the SHORT_TITLE line from the content."""
    # Remove labeled SHORT_TITLE: line (case-insensitive)
    content = re.sub(r'SHORT_TITLE:\s*.+\n?', '', content, flags=re.IGNORECASE)

    # Also remove unlabeled slug on first line (if it looks like a slug)
    lines = content.strip().split('\n', 1)
    if lines:
        first_line = lines[0].strip()
        if re.match(r'^[a-z0-9-]+$', first_line) and '-' in first_line and len(first_line) < 60:
            content = lines[1] if len(lines) > 1 else ''

    return content.strip()


def generate_handoff(conversation: str, cwd: str, trigger: str, api_key: str) -> tuple[str, str]:
    """Use Claude Haiku to generate a session handoff document."""
    client = anthropic.Anthropic(api_key=api_key)
    project_name = Path(cwd).name
    date = datetime.now().strftime("%Y-%m-%d")
    platform = sys.platform

    prompt = HANDOFF_TEMPLATE.format(
        project_name=project_name,
        trigger=trigger,
        cwd=cwd,
        conversation=conversation,
        date=date,
        platform=platform
    )

    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=4000,
            metadata={"user_id": "mother-claude-hooks"},
            messages=[{"role": "user", "content": prompt}]
        )

        content = response.content[0].text
        short_title = extract_short_title(content)
        content = remove_short_title_line(content)

        return content.strip(), short_title

    except Exception as e:
        print(f"Error calling Claude API: {e}", file=sys.stderr)
        fallback = f"# Session Handoff (Auto-generated - API Error)\n\nError: {e}\n\nTrigger: {trigger}\nProject: {project_name}"
        return fallback, "error"


def main():
    try:
        hook_input = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error parsing hook input: {e}", file=sys.stderr)
        sys.exit(1)

    session_id = hook_input.get("session_id", "unknown")
    transcript_path = hook_input.get("transcript_path", "")
    cwd = hook_input.get("cwd", os.getcwd())
    hook_event = hook_input.get("hook_event_name", "unknown")
    trigger = hook_input.get("trigger", hook_event)

    # Get transcript size for deduplication logic
    transcript_size = get_transcript_size(transcript_path)

    # Check if we should skip (SessionEnd after PreCompact with no new work)
    if should_skip_handoff(session_id, transcript_size, trigger):
        cleanup_state(session_id)
        sys.exit(0)

    api_key = get_api_key()
    conversation = parse_transcript(transcript_path)

    if not conversation:
        print("No conversation content found, skipping handoff generation")
        sys.exit(0)

    handoff_content, short_title = generate_handoff(conversation, cwd, trigger, api_key)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    filename = f"{timestamp}-{short_title}.md"

    handoff_dir = find_handoff_directory(cwd)
    output_path = handoff_dir / filename

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(handoff_content)
        print(f"Session handoff saved to: {output_path}")
    except Exception as e:
        print(f"Error saving handoff: {e}", file=sys.stderr)
        sys.exit(1)

    # Save state for deduplication (PreCompact saves, SessionEnd cleans up)
    if trigger in ("auto", "PreCompact"):
        save_handoff_state(session_id, transcript_size)
    else:
        cleanup_state(session_id)


if __name__ == "__main__":
    main()
