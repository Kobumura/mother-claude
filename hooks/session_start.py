#!/usr/bin/env python3
"""
Mother CLAUDE Session Start Hook

Loads the most recent session handoff when starting a new Claude session.
Outputs to stdout so Claude sees the previous context.

SETUP:
1. Configure in ~/.claude/settings.json (see settings-template.json)
2. No additional dependencies required
"""

import json
import os
import sys
from pathlib import Path


def find_handoff_directory(cwd: str) -> Path | None:
    """Find the session_handoffs directory for this project."""
    cwd_path = Path(cwd)

    # Check for project config first
    config_path = cwd_path / ".claude" / "project.json"
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if "handoffs_path" in config:
                    custom_path = cwd_path / config["handoffs_path"]
                    if custom_path.exists():
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

    return None


def get_recent_handoffs(handoff_dir: Path, count: int = 1) -> list[Path]:
    """Get the most recent handoff files."""
    handoffs = list(handoff_dir.glob("*.md"))

    # Filter out README or template files
    handoffs = [h for h in handoffs if not h.name.lower().startswith(('readme', 'template'))]

    # Sort by modification time, most recent first
    handoffs.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    return handoffs[:count]


def main():
    try:
        hook_input = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    cwd = hook_input.get("cwd", os.getcwd())

    # Find handoff directory
    handoff_dir = find_handoff_directory(cwd)
    if not handoff_dir:
        sys.exit(0)

    # Get config for how many to load (default 1)
    count = 1
    config_path = Path(cwd) / ".claude" / "project.json"
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                count = config.get("handoffs_to_load", 1)
        except (json.JSONDecodeError, IOError):
            pass

    # Get recent handoffs
    handoffs = get_recent_handoffs(handoff_dir, count)

    if not handoffs:
        sys.exit(0)

    # Output the handoff(s) to stdout - Claude will see this
    project_name = Path(cwd).name
    print(f"\n{'='*60}")
    print(f"SESSION CONTEXT: {project_name}")
    print(f"{'='*60}")

    for i, handoff_path in enumerate(handoffs):
        if i > 0:
            print(f"\n{'-'*40}\n")

        print(f"Previous handoff: {handoff_path.name}")
        print(f"{'-'*40}")

        try:
            with open(handoff_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Limit output to avoid overwhelming context
                if len(content) > 8000:
                    content = content[:8000] + "\n\n[... truncated for length ...]"
                print(content)
        except IOError as e:
            print(f"(Could not read: {e})")

    print(f"\n{'='*60}")
    print("TIP: Say 'load previous handoffs' if you need more context.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
