#!/usr/bin/env bash
# team-up.sh — bring up a team of autonomous AI worker sessions (macOS / Linux).
# Bash + tmux counterpart of team-up.ps1. Same model; full docs in README.md.
#
# ============================================================================
# EDIT BEFORE FIRST RUN  (or set the matching env vars / pass flags)
# ============================================================================
#   1. DOCS_REPO_NAME / docs path — the clone of your shared-docs (agent-protocol)
#      repo. Set TEAM_DOCS_PATH, pass --docs-path, or clone it next to this repo.
#      It must contain shared/agent-worker-protocol.md and a CLAUDE.md whose
#      project table maps repo folder name -> tracker project key.
#   2. PROJECT_KEY_DEFAULT — a short uppercase key per repo (e.g. "PROJ"). Pass
#      --project-key, or let the script look this repo's folder up in the docs CLAUDE.md.
#   3. JIRA_HOST — your Jira Cloud host (e.g. your-org.atlassian.net). Used by the
#      board-status preflight (needs JIRA_EMAIL + JIRA_TOKEN). Pass --skip-preflight to skip.
#   4. SLACK_WEBHOOK_VAR — env var holding your team's Slack incoming webhook (default
#      TEAM_SLACK_WEBHOOK).
#   5. WORKER_NAMES / DISPATCHER_NAME / STEWARD_NAME — neutral session handles. Rename freely.
#
# Requires: bash, git (with worktree), tmux, curl, and Claude Code on PATH (`claude`).
# Run from your PROJECT REPO ROOT:   bash /path/to/team-up.sh
# ============================================================================
set -euo pipefail

# ============================== CONFIG ==============================
DOCS_REPO_NAME="${DOCS_REPO_NAME:-shared-docs}"            # sibling folder guessed if TEAM_DOCS_PATH unset
JIRA_HOST="${JIRA_HOST:-your-org.atlassian.net}"           # your Jira Cloud host, no scheme
SLACK_WEBHOOK_VAR="${SLACK_WEBHOOK_VAR:-TEAM_SLACK_WEBHOOK}"
PROJECT_KEY_DEFAULT="${PROJECT_KEY_DEFAULT:-}"             # e.g. PROJ ("" = require lookup/flag)
DISPATCHER_NAME="${DISPATCHER_NAME:-dispatcher}"
STEWARD_NAME="${STEWARD_NAME:-steward}"
WORKER_NAMES=(worker-a worker-b worker-c worker-d worker-e worker-f worker-g worker-h)
DEFAULT_WORKER_COUNT="${DEFAULT_WORKER_COUNT:-3}"
# ===================================================================

# ---- flags ----
WORKERS=0 PROJECT_KEY="" DOCS_PATH="" SKIP_DISPATCHER=0 SKIP_PREFLIGHT=0
while [ $# -gt 0 ]; do
  case "$1" in
    --workers)         WORKERS="$2"; shift 2;;
    --project-key)     PROJECT_KEY="$2"; shift 2;;
    --docs-path)       DOCS_PATH="$2"; shift 2;;
    --skip-dispatcher) SKIP_DISPATCHER=1; shift;;
    --skip-preflight)  SKIP_PREFLIGHT=1; shift;;
    -h|--help) sed -n '2,30p' "$0"; exit 0;;
    *) echo "unknown arg: $1" >&2; exit 1;;
  esac
done

REPO="$(pwd)"
PROJECT_LEAF="$(basename "$REPO")"

# ---- resolve the docs clone (flag > env > sibling guess) ----
DOCS=""
for c in "$DOCS_PATH" "${TEAM_DOCS_PATH:-}" "$REPO/../$DOCS_REPO_NAME"; do
  [ -n "$c" ] && [ -f "$c/shared/agent-worker-protocol.md" ] && { DOCS="$(cd "$c" && pwd)"; break; }
done
[ -n "$DOCS" ] || { echo "Can't find the $DOCS_REPO_NAME clone. Pass --docs-path, set TEAM_DOCS_PATH, or clone it next to this repo." >&2; exit 1; }

# ---- resolve the project key (flag > docs CLAUDE.md project table > default) ----
KEY="$PROJECT_KEY"
if [ -z "$KEY" ] && [ -f "$DOCS/CLAUDE.md" ]; then
  KEY="$(grep -E "\b$PROJECT_LEAF\b" "$DOCS/CLAUDE.md" | grep -oE '\| *[A-Z]{2,6} *\|' | head -1 | tr -d ' |')" || true
fi
[ -n "$KEY" ] || KEY="$PROJECT_KEY_DEFAULT"
[ -n "$KEY" ] || { echo "Can't determine the project key for '$PROJECT_LEAF'. Add this repo to the project table in $DOCS/CLAUDE.md, set PROJECT_KEY_DEFAULT, or pass --project-key." >&2; exit 1; }

# ---- team composition ----
if [ "$WORKERS" -gt 0 ]; then
  team=(); for ((i=0;i<WORKERS;i++)); do team+=("${WORKER_NAMES[$((i % ${#WORKER_NAMES[@]}))]}"); done
else
  n=$(( DEFAULT_WORKER_COUNT < ${#WORKER_NAMES[@]} ? DEFAULT_WORKER_COUNT : ${#WORKER_NAMES[@]} ))
  team=("${WORKER_NAMES[@]:0:$n}")
fi

# ---- preflight: the board must carry all seven workflow statuses ----
if [ "$SKIP_PREFLIGHT" -eq 0 ]; then
  needed=("To Do" "Ready" "In Progress" "Needs Input" "In Review" "Changes Requested" "Done")
  if [ -n "${JIRA_EMAIL:-}" ] && [ -n "${JIRA_TOKEN:-}" ]; then
    resp="$(curl -fsS -u "$JIRA_EMAIL:$JIRA_TOKEN" "https://$JIRA_HOST/rest/api/3/project/$KEY/statuses" || true)"
    miss=()
    for s in "${needed[@]}"; do printf '%s' "$resp" | grep -q "\"name\":\"$s\"" || miss+=("$s"); done
    if [ "${#miss[@]}" -gt 0 ]; then
      echo "Jira board $KEY is missing required statuses: ${miss[*]}. Add them before launching — workers pick only from Ready. See onboarding.md Preflight." >&2; exit 1
    fi
    echo "Preflight: board $KEY carries all 7 statuses."
  else
    echo "Preflight: JIRA_EMAIL/JIRA_TOKEN not set — skipping board-status check."
  fi
  [ -n "${!SLACK_WEBHOOK_VAR:-}" ] || echo "Preflight WARNING: \$$SLACK_WEBHOOK_VAR is not set — Slack pings will fail."
fi

RUNBOOK="$DOCS/shared/onboarding-a-worker-machine.md"
[ -f "$RUNBOOK" ] || RUNBOOK="$DOCS/onboarding.md"   # public worker-system layout
echo "Team for $KEY: dispatcher $DISPATCHER_NAME$([ "$SKIP_DISPATCHER" -eq 1 ] && echo ' (skipped)'), steward $STEWARD_NAME, workers ${team[*]}"

boot_text() {  # role, name — single line, no embedded double quotes (it is inlined into a shell command)
  echo "You are the $1 for project $KEY, named $2. Read $RUNBOOK (absolute path), follow the $1 launch prompt there, and start. Do not wait on interactive prompts."
}

# ---- worktrees (steward + workers; dispatcher uses the main checkout) ----
# Namespaced per project so the same worker names can be reused across projects.
ensure_worktree() {
  local name="$1" dir="$REPO/../workers/$PROJECT_LEAF/$1"
  mkdir -p "$(dirname "$dir")"
  [ -d "$dir" ] || git -C "$REPO" worktree add "$dir" -b "team-$name" >/dev/null 2>&1 || true
  (cd "$dir" && pwd)
}

# ---- assemble roles as  name|dir|auto|boot ----
mkdir -p "$REPO/.team"
roles=()
[ "$SKIP_DISPATCHER" -eq 0 ] && roles+=("$DISPATCHER_NAME|$REPO|0|$(boot_text DISPATCHER "$DISPATCHER_NAME")")
roles+=("$STEWARD_NAME|$(ensure_worktree "$STEWARD_NAME")|1|$(boot_text STEWARD "$STEWARD_NAME")")
for w in "${team[@]}"; do roles+=("$w|$(ensure_worktree "$w")|1|$(boot_text WORKER "$w")"); done

# ---- launch one tmux window per role ----
command -v tmux >/dev/null || { echo "tmux not found — install it (e.g. 'brew install tmux'), or launch each role manually from .team/<name>.txt." >&2; exit 1; }
SESSION="team-$KEY"
if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "tmux session '$SESSION' already exists. Attach with: tmux attach -t $SESSION  (or kill it first: tmux kill-session -t $SESSION)" >&2; exit 1
fi

first=1
for r in "${roles[@]}"; do
  IFS='|' read -r name dir auto boot <<< "$r"
  printf '%s\n' "$boot" > "$REPO/.team/$name.txt"   # also written for manual paste
  flag=""; [ "$auto" = "1" ] && flag="--dangerously-skip-permissions "
  # Autonomous roles (steward/workers) skip permission prompts so loops never stall;
  # the dispatcher stays interactive (a human is present).
  cmd="claude ${flag}\"$boot\""
  if [ "$first" -eq 1 ]; then tmux new-session -d -s "$SESSION" -n "$name" -c "$dir"; first=0
  else tmux new-window -t "$SESSION" -n "$name" -c "$dir"; fi
  tmux send-keys -t "$SESSION:$name" "$cmd" C-m
done

echo "Team is up in tmux session '$SESSION'.  Attach:  tmux attach -t $SESSION"
echo "(Next/prev window: Ctrl-b n / Ctrl-b p. Detach: Ctrl-b d. Each boot prompt is also in .team/<name>.txt.)"
