#!/usr/bin/env node
/**
 * Mother CLAUDE Session Handoff Generator (Node.js version)
 *
 * This hook runs on PreCompact (auto) and SessionEnd events to automatically
 * generate session handoff documents using Claude Haiku.
 *
 * SETUP:
 * 1. npm install -g @anthropic-ai/sdk
 * 2. Set ANTHROPIC_API_KEY_HOOKS environment variable
 * 3. Configure in ~/.claude/settings.json (see settings-template.json)
 */

const Anthropic = require("@anthropic-ai/sdk");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const os = require("os");

const HOOKS_STATE_DIR = path.join(os.homedir(), ".claude", "hooks", ".state");

const HANDOFF_TEMPLATE = `
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
Include actual file paths, code details, and technical specifics from the conversation.

IMPORTANT:
- First line must be a SHORT_TITLE (2-4 words, lowercase, hyphenated) for the filename
- Extract SPECIFIC file names, paths, and technical details from the conversation
- Include code snippets if they were significant
- Be detailed about what was actually accomplished

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

### [Feature/Task Name 1]
**Files Created/Modified:**
- \`path/to/file.ext\` - [What was done]

**Details:**
[Specific technical details, configurations, code patterns used]

---

## Technical Discoveries

- **[Topic]**: [What was learned - gotchas, patterns, insights]

---

## Files Changed This Session

### New Files
- \`path/to/new/file.ext\` - [Purpose]

### Modified Files
- \`path/to/modified/file.ext\` - [What changed]

---

## Next Steps

1. [ ] [Specific actionable task]
2. [ ] [Next task]

---

## Open Questions

- [Unresolved decisions or questions]

---

## Environment

- **Platform**: {platform}
- **Working Directory**: {cwd}
`;

function getApiKey() {
  const key =
    process.env.ANTHROPIC_API_KEY_HOOKS || process.env.ANTHROPIC_API_KEY;
  if (!key) {
    console.error(
      "Error: ANTHROPIC_API_KEY_HOOKS or ANTHROPIC_API_KEY not set"
    );
    process.exit(1);
  }
  return key;
}

function getTranscriptSize(transcriptPath) {
  try {
    return fs.statSync(transcriptPath).size;
  } catch {
    return 0;
  }
}

function getStateFile(sessionId) {
  if (!fs.existsSync(HOOKS_STATE_DIR)) {
    fs.mkdirSync(HOOKS_STATE_DIR, { recursive: true });
  }
  const safeId = crypto
    .createHash("md5")
    .update(sessionId)
    .digest("hex")
    .slice(0, 16);
  return path.join(HOOKS_STATE_DIR, `handoff_${safeId}.json`);
}

function saveHandoffState(sessionId, transcriptSize) {
  const stateFile = getStateFile(sessionId);
  const state = {
    session_id: sessionId,
    transcript_size: transcriptSize,
    timestamp: new Date().toISOString(),
  };
  try {
    fs.writeFileSync(stateFile, JSON.stringify(state));
  } catch {
    // Non-critical
  }
}

function shouldSkipHandoff(sessionId, currentTranscriptSize, trigger) {
  if (trigger === "auto" || trigger === "PreCompact") {
    return false;
  }

  const stateFile = getStateFile(sessionId);
  if (!fs.existsSync(stateFile)) {
    return false;
  }

  try {
    const state = JSON.parse(fs.readFileSync(stateFile, "utf8"));
    const prevSize = state.transcript_size || 0;
    if (prevSize > 0) {
      const growth = (currentTranscriptSize - prevSize) / prevSize;
      if (growth < 0.1) {
        console.log(
          `SessionEnd: Skipping (transcript grew ${(growth * 100).toFixed(1)}% since PreCompact)`
        );
        return true;
      }
    }
    return false;
  } catch {
    return false;
  }
}

function cleanupState(sessionId) {
  try {
    fs.unlinkSync(getStateFile(sessionId));
  } catch {
    // File might not exist
  }
}

function parseTranscript(transcriptPath) {
  const messages = [];
  try {
    const content = fs.readFileSync(transcriptPath, "utf8");
    const lines = content.split("\n").filter((l) => l.trim());

    for (const line of lines) {
      try {
        const entry = JSON.parse(line);
        let text = "";

        if (entry.type === "human") {
          const content = entry.message?.content || "";
          if (Array.isArray(content)) {
            text = content
              .filter((c) => c.type === "text")
              .map((c) => c.text)
              .join("\n");
          } else {
            text = content;
          }
          if (text.trim()) {
            messages.push(`USER: ${text.slice(0, 3000)}`);
          }
        } else if (entry.type === "assistant") {
          const content = entry.message?.content || "";
          if (Array.isArray(content)) {
            text = content
              .filter((c) => c.type === "text")
              .map((c) => c.text)
              .join("\n");
          } else {
            text = content;
          }
          if (text.trim()) {
            messages.push(`ASSISTANT: ${text.slice(0, 3000)}`);
          }
        }
      } catch {
        continue;
      }
    }
  } catch (e) {
    console.error(`Warning: Error reading transcript: ${e.message}`);
    return "";
  }

  return messages.slice(-80).join("\n\n---\n\n");
}

function findHandoffDirectory(cwd) {
  const possiblePaths = [
    path.join(cwd, "docs", "session_handoffs"),
    path.join(cwd, "session_handoffs"),
    path.join(cwd, ".claude", "session_handoffs"),
  ];

  // Check for project config
  const configPath = path.join(cwd, ".claude", "project.json");
  if (fs.existsSync(configPath)) {
    try {
      const config = JSON.parse(fs.readFileSync(configPath, "utf8"));
      if (config.handoffs_path) {
        const customPath = path.join(cwd, config.handoffs_path);
        if (!fs.existsSync(customPath)) {
          fs.mkdirSync(customPath, { recursive: true });
        }
        return customPath;
      }
    } catch {
      // Ignore config errors
    }
  }

  for (const p of possiblePaths) {
    if (fs.existsSync(p)) {
      return p;
    }
  }

  // Default
  const defaultPath = possiblePaths[0];
  fs.mkdirSync(defaultPath, { recursive: true });
  return defaultPath;
}

function extractShortTitle(content) {
  const match = content.match(/SHORT_TITLE:\s*(.+)/);
  if (match) {
    return match[1]
      .trim()
      .toLowerCase()
      .replace(/[\[\]"']/g, "")
      .replace(/\s+/g, "-")
      .replace(/[^a-z0-9-]/g, "")
      .slice(0, 50);
  }
  return "session";
}

function removeShortTitleLine(content) {
  return content.replace(/SHORT_TITLE:\s*.+\n?/, "");
}

async function generateHandoff(conversation, cwd, trigger, apiKey) {
  const client = new Anthropic({ apiKey });
  const projectName = path.basename(cwd);
  const date = new Date().toISOString().split("T")[0];

  const prompt = HANDOFF_TEMPLATE.replace("{project_name}", projectName)
    .replace(/{trigger}/g, trigger)
    .replace(/{cwd}/g, cwd)
    .replace("{conversation}", conversation)
    .replace("{date}", date)
    .replace("{platform}", process.platform);

  try {
    const response = await client.messages.create({
      model: "claude-3-haiku-20240307",
      max_tokens: 4000,
      messages: [{ role: "user", content: prompt }],
    });

    let content = response.content[0].text;
    const shortTitle = extractShortTitle(content);
    content = removeShortTitleLine(content).trim();

    return { content, shortTitle };
  } catch (e) {
    console.error(`Error calling Claude API: ${e.message}`);
    return {
      content: `# Session Handoff (Auto-generated - API Error)\n\nError: ${e.message}\n\nTrigger: ${trigger}\nProject: ${projectName}`,
      shortTitle: "error",
    };
  }
}

async function main() {
  let hookInput;
  try {
    const inputData = fs.readFileSync(0, "utf8"); // Read from stdin
    hookInput = JSON.parse(inputData);
  } catch (e) {
    console.error(`Error parsing hook input: ${e.message}`);
    process.exit(1);
  }

  const sessionId = hookInput.session_id || "unknown";
  const transcriptPath = hookInput.transcript_path || "";
  const cwd = hookInput.cwd || process.cwd();
  const hookEvent = hookInput.hook_event_name || "unknown";
  const trigger = hookInput.trigger || hookEvent;

  const transcriptSize = getTranscriptSize(transcriptPath);

  if (shouldSkipHandoff(sessionId, transcriptSize, trigger)) {
    cleanupState(sessionId);
    process.exit(0);
  }

  const apiKey = getApiKey();
  const conversation = parseTranscript(transcriptPath);

  if (!conversation) {
    console.log("No conversation content found, skipping handoff generation");
    process.exit(0);
  }

  const { content, shortTitle } = await generateHandoff(
    conversation,
    cwd,
    trigger,
    apiKey
  );

  const now = new Date();
  const timestamp = `${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, "0")}${String(now.getDate()).padStart(2, "0")}-${String(now.getHours()).padStart(2, "0")}${String(now.getMinutes()).padStart(2, "0")}`;
  const filename = `${timestamp}-${shortTitle}.md`;

  const handoffDir = findHandoffDirectory(cwd);
  const outputPath = path.join(handoffDir, filename);

  try {
    fs.writeFileSync(outputPath, content);
    console.log(`Session handoff saved to: ${outputPath}`);
  } catch (e) {
    console.error(`Error saving handoff: ${e.message}`);
    process.exit(1);
  }

  if (trigger === "auto" || trigger === "PreCompact") {
    saveHandoffState(sessionId, transcriptSize);
  } else {
    cleanupState(sessionId);
  }
}

main();
