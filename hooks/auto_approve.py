#!/usr/bin/env python3
"""
Mother CLAUDE Auto-Approve Hook

Automatically approves safe operations to reduce permission fatigue.
Returns JSON with {"allow": true} for safe operations.

SETUP:
1. Configure in ~/.claude/settings.json (see settings-template.json)
2. No additional dependencies required

CUSTOMIZATION:
- Add/remove patterns in SAFE_BASH_PATTERNS for your workflow
- Add/remove tools in always_safe list
- Add patterns to DANGEROUS_PATTERNS to block specific commands
"""

import json
import re
import sys

# Safe bash commands (patterns)
SAFE_BASH_PATTERNS = [
    # Git operations
    r'^git\s+(status|log|diff|branch|show|remote|fetch|ls-files|rev-parse)',
    r'^git\s+config',
    r'^git\s+add',
    r'^git\s+commit',
    r'^git\s+push',
    r'^git\s+pull',
    r'^git\s+checkout',
    r'^git\s+merge',
    r'^git\s+rebase(?!\s+-i)',  # rebase but not interactive
    r'^git\s+stash',
    r'^git\s+tag',

    # Directory listing
    r'^ls(\s|$)',
    r'^pwd$',
    r'^dir(\s|$)',

    # File reading
    r'^cat\s',
    r'^head\s',
    r'^tail\s',
    r'^less\s',
    r'^more\s',

    # Search commands
    r'^find\s',
    r'^grep\s',
    r'^rg\s',
    r'^ag\s',

    # Package management
    r'^npm\s+(list|ls|outdated|info|view|search|install|i|ci|update|run)',
    r'^pip\s+(list|show|freeze|install)',
    r'^composer\s+(show|info|install|update|require)',
    r'^yarn(\s|$)',

    # Build/test
    r'^npm\s+(test|run)',
    r'^pytest',
    r'^php\s+.*test',
    r'^phpunit',

    # Environment info
    r'^echo\s+\$',
    r'^env$',
    r'^printenv',
    r'^which\s',
    r'^where\s',
    r'^node\s+--version',
    r'^npm\s+--version',
    r'^python\s+--version',
    r'^php\s+--version',
    r'^git\s+--version',

    # Disk/system info
    r'^df(\s|$)',
    r'^du\s',
    r'^free(\s|$)',
    r'^uname',
    r'^whoami$',
    r'^hostname$',

    # Process viewing
    r'^ps(\s|$)',
    r'^top\s+-',

    # Network info (read-only)
    r'^ping\s+-c\s+\d',
    r'^curl\s+.*--head',
    r'^curl\s+-I\s',
]

# Dangerous patterns to NEVER auto-approve
DANGEROUS_PATTERNS = [
    r'\brm\s+-rf\s+/',  # rm -rf on root paths
    r'\bsudo\b',
    r'\bchmod\b',
    r'\bchown\b',
    r'\bmkfs\b',
    r'\bdd\s',
    r'>\s*/',  # redirect to root paths
    r'\|\s*sh\b',
    r'\|\s*bash\b',
    r'git\s+reset\s+--hard',
    r'git\s+clean\s+-f',
    r'git\s+push\s+.*--force',
]


def is_safe_bash_command(command: str) -> bool:
    """Check if a bash command is safe to auto-approve."""
    command = command.strip()

    # Check dangerous patterns first
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return False

    # Check if matches any safe pattern
    for pattern in SAFE_BASH_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return True

    return False


def main():
    try:
        hook_input = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(1)

    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})

    # Always safe tools - auto-approve
    # CUSTOMIZE THIS LIST based on your trust level
    always_safe = [
        "Read", "Glob", "Grep", "WebSearch", "TodoRead",
        "Write", "Edit", "NotebookEdit",  # File modifications
        "TodoWrite",
        "WebFetch",
    ]

    if tool_name in always_safe:
        print(json.dumps({"allow": True}))
        sys.exit(0)

    # Bash commands need inspection
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        if is_safe_bash_command(command):
            print(json.dumps({"allow": True}))
            sys.exit(0)

    # Not auto-approved - normal permission flow
    sys.exit(0)


if __name__ == "__main__":
    main()
