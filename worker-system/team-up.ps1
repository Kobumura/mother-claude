#requires -version 5
<#
  team-up.ps1 - bring up a team of autonomous AI worker sessions for the current project.

  ============================================================================
  EDIT BEFORE FIRST RUN
  ============================================================================
  This is a public, adaptable launcher. Out of the box it ships with neutral
  placeholders. Edit the CONFIG block a few lines below (or, after the first run,
  edit the generated `team.config.json`) to point it at your setup:

    1. $DocsRepoName / docs path - the clone of your shared-docs/agent-protocol
       repo. Set $env:TEAM_DOCS_PATH, pass -DocsPath, or clone it next to this
       repo. It must contain `shared/agent-worker-protocol.md` and a CLAUDE.md
       whose project table maps repo folder name -> Jira-style project key.
    2. $ProjectKeyDefault / project table - a short uppercase key per repo
       (e.g. "PROJ"). Either pass -ProjectKey, set it in team.config.json, or let
       the script look up this repo's folder name in your docs CLAUDE.md table.
    3. $JiraHost - your Jira Cloud host (e.g. your-org.atlassian.net). Used by the
       preflight that verifies the board carries the required workflow statuses.
       Requires $env:JIRA_EMAIL and $env:JIRA_TOKEN. Pass -SkipPreflight to skip.
    4. $SlackWebhookVarDefault - the env var that holds your team's Slack incoming
       webhook URL (default TEAM_SLACK_WEBHOOK). Set per project in
       team.config.json if different repos ping different channels.
    5. $WorkerNames - example worker handles ("worker-a"..). Rename freely; these
       are just neutral session codenames, not attribution.
    6. $DefaultDispatcherName / $DefaultStewardName - the planner and steward
       handles. Rename to whatever your team uses.

  Nothing else needs editing - the launch loop, terminal handling, worktree
  creation, config persistence and skip-permissions behavior are generic.
  ============================================================================

  WHAT IT DOES
  Run it from your PROJECT REPO ROOT:
      powershell <path-to-this-script>\team-up.ps1

  FIRST RUN takes no input on a known project: it resolves the project key from
  your docs CLAUDE.md project table, uses a default team, and writes
  `team.config.json`, which you can edit afterward to rename anyone or change the
  worker count. LATER RUNS read it (your edits stick).

  Resolution order (first match wins):
    docsPath   : -DocsPath param > team.config.json > $env:TEAM_DOCS_PATH > ..\<docs-repo>
    projectKey : -ProjectKey param > team.config.json > lookup of this repo path in
                 docs CLAUDE.md's project table > FAIL with instructions
    terminal   : -Terminal param > Warp (if installed) > Windows Terminal > plain windows

  Preflight (hard gate): the Jira board must carry all seven statuses
  (To Do, Ready, In Progress, Needs Input, In Review, Changes Requested, Done)
  or the claim loop cannot run. Verified via the Jira API ($env:JIRA_EMAIL/$env:JIRA_TOKEN).
  Also warns if the project's Slack webhook env var is unset.

  Roles:
    - Dispatcher/Planner : interactive command-center, runs in the main checkout.
      Pass -SkipDispatcher when a planner session is ALREADY running (launching a
      second one means two planners answering Needs Input - don't).
    - Steward/Groomer    : autonomous loop, its own git worktree
    - Workers            : autonomous loops, one git worktree each

  Terminals: Warp (opens a tab per autonomous role in your CURRENT Warp window via
  warp://action/new_tab; you then run `.\go` in each tab - Warp can't auto-run a
  command in a new tab on Windows), Windows Terminal, or separate PowerShell
  windows. Boot prompts also land in .team\<name>.txt for manual paste.
  Autonomous roles (steward/workers) launch claude with --dangerously-skip-permissions
  so loops never stall on a prompt; the dispatcher stays interactive without it.

  Overrides (optional):  -Workers 4  -ProjectKey PROJ  -DocsPath C:\path  -Terminal warp|wt|windows  -SkipDispatcher  -SkipPreflight
#>
param(
  [int]$Workers = 0,
  [string]$ProjectKey = "",
  [string]$DocsPath = "",
  [ValidateSet('auto','warp','wt','windows')][string]$Terminal = 'auto',
  [switch]$SkipDispatcher,
  [switch]$SkipPreflight
)
$ErrorActionPreference = "Stop"

# ============================================================================
# CONFIG - edit these to match your setup (see header for details)
# ============================================================================
# Folder name of your shared-docs clone, used when guessing a sibling directory
# (..\<DocsRepoName>) if -DocsPath / $env:TEAM_DOCS_PATH aren't set.
$DocsRepoName        = "shared-docs"             # <repo-path> placeholder: rename to your docs repo folder
# Your Jira Cloud host (no scheme). Used by the board-status preflight.
$JiraHost            = "your-org.atlassian.net"   # e.g. acme.atlassian.net
# Env var holding the team's Slack incoming webhook URL.
$SlackWebhookVarDefault = "TEAM_SLACK_WEBHOOK"
# Default Jira-style project key if it can't be resolved any other way ("" = require lookup/param).
$ProjectKeyDefault   = ""                         # e.g. "PROJ"
# Default role handles - neutral session codenames, not attribution.
$DefaultDispatcherName = "dispatcher"
$DefaultStewardName    = "steward"
# Pool of example worker handles. Rename freely; first N are picked for the default team.
$WorkerNames         = @("worker-a","worker-b","worker-c","worker-d","worker-e","worker-f","worker-g","worker-h")
# How many workers the default team starts with (when -Workers isn't passed and no config exists).
$DefaultWorkerCount  = 3
# ============================================================================

$repo    = (Get-Location).Path
$cfgPath = Join-Path $repo "team.config.json"

$cfg = $null
if (Test-Path $cfgPath) { $cfg = Get-Content $cfgPath -Raw | ConvertFrom-Json }

# ---- resolve the docs clone (param > config > env var > sibling guess) ----
$docs = $null
foreach ($candidate in @($DocsPath, $cfg.docsPath, $env:TEAM_DOCS_PATH, (Join-Path $repo "..\$DocsRepoName"))) {
  if ($candidate -and (Test-Path (Join-Path $candidate "shared\agent-worker-protocol.md"))) {
    $docs = (Resolve-Path $candidate).Path; break
  }
}
if (-not $docs) {
  throw "Can't find the $DocsRepoName clone. Pass -DocsPath, or setx TEAM_DOCS_PATH <path>, or clone it next to this repo."
}

# ---- resolve the Jira project key (param > config > CLAUDE.md project table > default) ----
$key = $ProjectKey
if (-not $key -and $cfg) { $key = $cfg.projectKey }
if (-not $key) {
  # Single source of truth: the project tables in your docs CLAUDE.md
  $repoLeaf = Split-Path $repo -Leaf
  foreach ($line in (Get-Content (Join-Path $docs "CLAUDE.md"))) {
    if ($line -match '^\|\s*\**([^|*]+?)\**\s*\|\s*([A-Z]{2,6})\s*\|' -and $line -match [regex]::Escape($repoLeaf)) {
      $key = $Matches[2]; break
    }
  }
}
if (-not $key) { $key = $ProjectKeyDefault }
if (-not $key) {
  throw "Can't determine the Jira project key for '$repo'. Add this repo to the project table in your docs CLAUDE.md (the single source of truth), set `$ProjectKeyDefault in the CONFIG block, or pass -ProjectKey."
}

# ---- first-run config ----
if (-not $cfg) {
  $n = [Math]::Min($DefaultWorkerCount, $WorkerNames.Count)
  $cfg = [pscustomobject]@{
    projectKey      = $key
    docsPath        = $docs
    slackWebhookVar = $SlackWebhookVarDefault    # override per project (e.g. PROJ_SLACK_WEBHOOK)
    terminal        = "auto"                     # warp | wt | windows | auto (asked/detected on first launch)
    dispatcher      = $DefaultDispatcherName
    steward         = $DefaultStewardName
    workers         = @($WorkerNames[0..($n-1)])
  }
  ($cfg | ConvertTo-Json) | Set-Content $cfgPath -Encoding utf8
  Write-Host "First run - meet the team. Edit team.config.json anytime to rename, resize, or set slackWebhookVar/terminal." -ForegroundColor Cyan
}
if ($Workers -gt 0) { $cfg.workers = @(0..($Workers-1) | ForEach-Object { $WorkerNames[$_ % $WorkerNames.Count] }) }
$teamWorkers = @($cfg.workers)

# ---- preflight: board statuses + webhook ----
if (-not $SkipPreflight) {
  $needed = @("To Do","Ready","In Progress","Needs Input","In Review","Changes Requested","Done")
  if ($env:JIRA_EMAIL -and $env:JIRA_TOKEN) {
    $auth = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("$($env:JIRA_EMAIL):$($env:JIRA_TOKEN)"))
    $resp = Invoke-RestMethod -Uri "https://$JiraHost/rest/api/3/project/$key/statuses" -Headers @{Authorization="Basic $auth"}
    $have = $resp | ForEach-Object { $_.statuses.name } | Sort-Object -Unique
    $missing = $needed | Where-Object { $have -notcontains $_ }
    if ($missing) {
      throw "Jira board $key is missing required statuses: $($missing -join ', '). Add them (board UI, or via the workflows API) before launching the team - workers pick only from Ready. See onboarding-a-worker-machine.md Preflight."
    }
    Write-Host "Preflight: board $key carries all 7 statuses." -ForegroundColor Green
  } else {
    Write-Host "Preflight: JIRA_EMAIL/JIRA_TOKEN not set - can't verify board statuses." -ForegroundColor Yellow
  }
  $whVar = if ($cfg.slackWebhookVar) { $cfg.slackWebhookVar } else { $SlackWebhookVarDefault }
  if (-not [Environment]::GetEnvironmentVariable($whVar, "User") -and -not [Environment]::GetEnvironmentVariable($whVar)) {
    Write-Host "Preflight WARNING: `$env:$whVar is not set - Slack pings will fail. (setx $whVar <url>, then restart terminals.)" -ForegroundColor Yellow
  }
}

$runbook = Join-Path $docs "shared\onboarding-a-worker-machine.md"
Write-Host ("Team for {0}: dispatcher {1}{2}, steward {3}, workers {4}" -f `
  $key, $cfg.dispatcher, $(if ($SkipDispatcher) {" (skipped - planner already running)"} else {""}), $cfg.steward, ($teamWorkers -join ", ")) -ForegroundColor Green

# ---- per-role boot prompts (also written to .team\<name>.txt for manual paste) ----
$teamDir = Join-Path $repo ".team"
New-Item -ItemType Directory -Force -Path $teamDir | Out-Null
function Boot-Text([string]$role, [string]$name) {
  # Single line, no embedded double quotes - it gets inlined into shell commands.
  return "You are the $role for project $key, named $name. Read $runbook (absolute path), follow the $role launch prompt there, and start. Do not wait on interactive prompts."
}

# ---- worktrees (steward + workers; dispatcher uses the main checkout) ----
# Namespaced per project (..\workers\<project>\<name>) so the same worker names
# can be reused across projects without collision.
$projectLeaf = Split-Path $repo -Leaf
function Ensure-Worktree([string]$name) {
  $dir = Join-Path $repo "..\workers\$projectLeaf\$name"
  New-Item -ItemType Directory -Force -Path (Split-Path $dir -Parent) | Out-Null
  # cmd /c so git's stderr chatter ("Preparing worktree...") can't become a
  # terminating NativeCommandError under ErrorActionPreference=Stop (PS 5.1)
  if (-not (Test-Path $dir)) { cmd /c "git -C ""$repo"" worktree add ""$dir"" -b team-$name 2>nul" | Out-Null }
  return (Resolve-Path $dir).Path
}

$roles = @()
if (-not $SkipDispatcher) {
  $roles += [pscustomobject]@{ title = "$($cfg.dispatcher) (dispatcher)"; dir = $repo; boot = (Boot-Text "DISPATCHER" $cfg.dispatcher); name = $cfg.dispatcher; auto = $false }
}
$roles += [pscustomobject]@{ title = "$($cfg.steward) (steward)"; dir = (Ensure-Worktree $cfg.steward); boot = (Boot-Text "STEWARD" $cfg.steward); name = $cfg.steward; auto = $true }
foreach ($w in $teamWorkers) {
  $roles += [pscustomobject]@{ title = "$w (worker)"; dir = (Ensure-Worktree $w); boot = (Boot-Text "WORKER" $w); name = $w; auto = $true }
}
foreach ($r in $roles) { Set-Content -Path (Join-Path $teamDir "$($r.name).txt") -Value $r.boot -Encoding utf8 }

# Autonomous roles (steward + workers) run claude with --dangerously-skip-permissions:
# they loop unattended and must never stall on a permission prompt. The dispatcher is
# interactive (a human is present), so it keeps normal permissions.
function Claude-Cmd([pscustomobject]$r) {
  $flag = if ($r.auto) { "--dangerously-skip-permissions " } else { "" }
  return "claude $flag`"$($r.boot)`""
}
# Each role dir gets a go.cmd so any tab/shell can (re)start the role with `.\go`.
foreach ($r in $roles) {
  if ($r.auto) { Set-Content -Path (Join-Path $r.dir "go.cmd") -Value "@echo off`r`n$(Claude-Cmd $r)" -Encoding ascii }
}

# ---- pick the terminal (param > config > ask the human > detect) ----
$warpInstalled = Test-Path "HKCU:\Software\Classes\warp"
$hasWt = [bool](Get-Command wt -ErrorAction SilentlyContinue)
$detected = if ($warpInstalled) { 'warp' } elseif ($hasWt) { 'wt' } else { 'windows' }
$term = $Terminal
if ($term -eq 'auto' -and $cfg.terminal -and $cfg.terminal -ne 'auto') { $term = $cfg.terminal }
if ($term -eq 'auto') {
  # Ask only when a human is actually at the console - a non-interactive run
  # (e.g. an AI session driving this script) must never hang on a prompt.
  $interactive = ($Host.Name -eq 'ConsoleHost') -and -not [Console]::IsInputRedirected
  if ($interactive) {
    $ans = Read-Host "Preferred terminal for the team tabs? warp / wt (Windows Terminal) / windows (plain PowerShell windows - works anywhere) [Enter = $detected]"
    $term = if ($ans -in @('warp','wt','windows')) { $ans } else { $detected }
  } else {
    $term = $detected
  }
  # Persist the choice so we never ask again (edit team.config.json to change it).
  $cfg | Add-Member -NotePropertyName terminal -NotePropertyValue $term -Force
  ($cfg | ConvertTo-Json) | Set-Content $cfgPath -Encoding utf8
}

if ($term -eq 'warp') {
  # What we LEARNED on Windows Warp:
  #  - warp://launch/<config> URIs are dead: the protocol handler is registered as
  #    `warp.exe "%0"` (the exe path, not the URI), and even invoking warp.exe
  #    directly with a launch URI does nothing - launch configs appear unshipped.
  #  - warp://action/new_tab?path=<dir> DOES work when passed to warp.exe directly,
  #    opening a tab in the user's current Warp window (which is what we want).
  #  - new_tab cannot auto-run a command, hence go.cmd: the human runs `.\go` once
  #    per tab.
  $warpExe = $null
  $reg = Get-ItemProperty "HKCU:\Software\Classes\warp\shell\open\command" -ErrorAction SilentlyContinue
  if ($reg -and $reg.'(default)' -match '"([^"]+warp\.exe)"') { $warpExe = $Matches[1] }
  if (-not $warpExe) { throw "Warp protocol registered but warp.exe not found - pass -Terminal wt or windows." }
  foreach ($r in $roles) {
    if ($r.auto) {
      & $warpExe "warp://action/new_tab?path=$($r.dir)"
      Start-Sleep -Milliseconds 600   # let each tab attach before the next
    }
  }
  Write-Host "Opened a Warp tab per autonomous role in your current window. In EACH new tab, run:  .\go" -ForegroundColor Cyan
  if (-not $SkipDispatcher) { Write-Host "Dispatcher is interactive - open your own tab in the main checkout and start claude normally (boot prompt: .team\$($cfg.dispatcher).txt)." -ForegroundColor Cyan }
}
elseif ($term -eq 'wt') {
  foreach ($r in $roles) {
    Start-Process wt -ArgumentList @("-w","0","new-tab","--title",$r.title,"-d",$r.dir,"powershell","-NoExit","-Command",(Claude-Cmd $r))
    Start-Sleep -Milliseconds 400   # let each tab attach before the next
  }
}
else {
  foreach ($r in $roles) {
    Start-Process powershell -WorkingDirectory $r.dir -ArgumentList @("-NoExit","-Command",(Claude-Cmd $r))
    Start-Sleep -Milliseconds 400
  }
}

Write-Host "Team is up. (If a tab didn't auto-start the assistant, its prompt is in .team\<name>.txt - paste it.)" -ForegroundColor Green
