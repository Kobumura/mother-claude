# Mother CLAUDE Hooks

Automation hooks for Claude Code that provide:
- **Automatic session handoffs** on context compaction and session end
- **Session context loading** at session start
- **Auto-approval** of safe operations to reduce permission fatigue

## Prerequisites

- **Python 3.8+** - The hooks are written in Python (primary/tested)
- **Anthropic API key** - For the handoff summarization (uses Claude Haiku)

If you don't have Python installed:
- **Windows**: `winget install Python.Python.3.12` or download from [python.org](https://www.python.org/downloads/)
- **Mac**: `brew install python` or download from [python.org](https://www.python.org/downloads/)
- **Linux**: `sudo apt install python3` (Ubuntu/Debian) or equivalent

### Node.js Alternative

We've included a Node.js version of the main script (`session_handoff.js`) that's been smoke tested. If you prefer Node:

```bash
npm install @anthropic-ai/sdk
```

Update `settings.json` to use `node ~/.claude/hooks/session_handoff.js` instead of Python.

**Note:** Only `session_handoff.js` has a Node version. The other scripts (`session_start.py`, `auto_approve.py`) are Python-only but simple enough to port if needed.

**Contributions welcome!** If you create Node versions of the other scripts, find bugs, or have improvements - please open a PR!

## Quick Setup

### 1. Install the Anthropic SDK

```bash
pip install anthropic
```

### 2. Set API Key

Create a separate API key for hooks at [console.anthropic.com](https://console.anthropic.com) (recommended for usage tracking).

**Linux/Mac:**
```bash
export ANTHROPIC_API_KEY_HOOKS="sk-ant-..."
# Add to ~/.bashrc or ~/.zshrc for persistence
```

**Windows PowerShell:**
```powershell
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY_HOOKS", "sk-ant-...", "User")
```

### 3. Copy Hook Scripts

Copy the Python scripts to your Claude hooks directory:

```bash
mkdir -p ~/.claude/hooks
cp *.py ~/.claude/hooks/
```

### 4. Configure Hooks

Copy the settings template and adjust paths for your system:

```bash
cp settings-template.json ~/.claude/settings.json
```

**Important:** Update the `python` path in settings.json if needed:
- Linux/Mac: `python` or `python3`
- Windows: Full path like `C:\\Users\\YOU\\AppData\\Local\\Programs\\Python\\Python312\\python.exe`

### 5. Restart Terminal

Environment variables and hooks are loaded at session start. Restart your terminal for changes to take effect.

---

## Hook Descriptions

### session_start.py

**Trigger:** `SessionStart`

Loads the most recent session handoff when you start a new Claude Code session. Outputs the handoff content to stdout so Claude sees it as context.

**Configuration:** Create `.claude/project.json` in any project to customize:
```json
{
  "handoffs_path": "docs/session_handoffs",
  "handoffs_to_load": 1
}
```

### session_handoff.py

**Triggers:** `PreCompact` (auto), `SessionEnd`

Automatically generates session handoff documents using Claude Haiku. Reads the conversation transcript, summarizes it, and saves to the project's session_handoffs directory.

**Cost:** ~$0.02-0.03 per handoff (Haiku is cheap)

**Output location:** Auto-detected in this order:
1. Path from `.claude/project.json`
2. `docs/session_handoffs/`
3. `session_handoffs/`
4. `.claude/session_handoffs/`

### auto_approve.py

**Trigger:** `PermissionRequest`

Automatically approves safe operations so you don't have to click "yes" constantly.

**Auto-approved by default:**
- All file operations (Read, Write, Edit)
- All search operations (Glob, Grep, WebSearch)
- Git operations (add, commit, push, pull, etc.)
- Package management (npm install, pip install)
- Build/test commands

**Never auto-approved:**
- `sudo`
- `git push --force`
- `git reset --hard`
- `rm -rf /`
- Piping to shell

**Customization:** Edit the `SAFE_BASH_PATTERNS` and `DANGEROUS_PATTERNS` lists in auto_approve.py.

---

## Project Configuration

Create `.claude/project.json` in any project root for project-specific settings:

```json
{
  "handoffs_path": "docs/session_handoffs",
  "handoffs_to_load": 2
}
```

| Setting | Default | Description |
|---------|---------|-------------|
| `handoffs_path` | `docs/session_handoffs` | Where to read/write handoffs |
| `handoffs_to_load` | `1` | How many handoffs to load at session start |

---

## Troubleshooting

### Hooks not firing

1. Check that `~/.claude/settings.json` exists and is valid JSON
2. Verify Python path in settings.json is correct
3. Restart your terminal (hooks load at session start)

### Session handoffs not generating

1. Check `ANTHROPIC_API_KEY_HOOKS` is set: `echo $ANTHROPIC_API_KEY_HOOKS`
2. Check the Anthropic API is accessible
3. Look for error output in Claude Code's verbose mode (Ctrl+O)

### Auto-approve not working

1. Verify the hook is in settings.json with `"matcher": "*"`
2. Check auto_approve.py is executable
3. The command might not match any pattern - add it to `SAFE_BASH_PATTERNS`

### IDE terminals don't see environment variable

If you set the environment variable while your IDE was running, the IDE's terminals won't see it. Restart the IDE entirely.

---

## Security Notes

- **API Key:** Use a separate API key for hooks so you can track usage and revoke if needed
- **Auto-approve:** Review the patterns in auto_approve.py - they're permissive by default
- **Never share:** Don't commit settings.json with API keys to version control

---

## License

CC BY 4.0 - Free to use and adapt with attribution to Dorothy J. Aubrey.
