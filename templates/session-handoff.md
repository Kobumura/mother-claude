# Session Handoff Template

**Filename format**: `YYYYMMDD-HHMM-brief-description.md`
**Location**: Each project's `docs/session_handoffs/`

---

# Session Handoff - [Brief Title]

**Date**: [YYYY-MM-DD]
**Session Duration**: [X hours]

---

## 🎯 Session Overview

### Primary Mission
[Single sentence: what was the intended goal?]

### Major Accomplishments
- ✅ [Completed task 1]
- ✅ [Completed task 2]
- ✅ [Completed task 3]

---

## 🔧 Technical Discoveries

[What did you learn? Architecture insights, gotchas, patterns discovered — separate from what you built.]

- **[Topic]**: [What you learned]
- **[Topic]**: [What you learned]

---

## 📁 Key Files Modified

| File | Change |
|------|--------|
| `path/to/file.ts` | [What changed] |
| `path/to/other.ts` | [What changed] |

---

## 💡 Lessons Learned

- **What worked**: [Approach that succeeded]
- **What didn't**: [Approach that failed or caused issues]
- **Watch out for**: [Gotchas for future sessions]

---

## ⚡ Immediate Next Steps

1. [ ] [Clear, actionable task with ticket ref if applicable]
2. [ ] [Next task]
3. [ ] [Next task]

---

## 🚧 Blockers / Open Questions

- [Unresolved problem or decision needed]
- [Question that needs an answer before proceeding]

---

## 🏗️ Environment

- **Machine**: [Device name/type]
- **Platform**: [OS]
- **Working Directory**: [Path]

---

## 📊 Session Metrics

- **Duration**: [X hours]
- **Files Created**: [N]
- **Files Modified**: [N]
- **Commits**: [N]

---

## When to Create a Session Handoff

Claude should proactively initiate handoffs when:

| Trigger | Why |
|---------|-----|
| Approaching context limits | Don't lose accumulated understanding |
| Natural stopping points | Completed a feature or milestone |
| Before switching tasks | Context shift = context loss |
| End of work session | Future-you will thank you |
| Before major decisions | Document tradeoffs before choosing |

## Starting a New Session

1. Check `docs/session_handoffs/` for the most recent handoff
2. Read it for current state and pending tasks
3. Continue from where previous session ended

The transition takes seconds instead of 10-15 minutes of re-establishing context.

---

*For more context on session handoffs, see the [article on dev.to](https://dev.to/dorothyjb/session-handoffs-giving-your-ai-assistant-memory-that-actually-persists-4mp2).*
