# Current Project State Template

**Filename**: `CURRENT-PROJECT-STATE.md`
**Location**: Each project's `docs/` directory

This file captures the *current* state of the project — what's deployed, what's working, what's broken. Unlike session handoffs (which are append-only history), this file gets updated in place.

---

# Current Project State - [Project Name]

**Last Updated**: [YYYY-MM-DD]

## Deployment Status

| Environment | URL | Status | Last Deploy |
|-------------|-----|--------|-------------|
| Production | [URL] | ✅ Live | [Date] |
| Staging | [URL] | ✅ Live | [Date] |
| Local | localhost:3000 | — | — |

## Current Features

### Working
- [x] Feature 1 — [brief description]
- [x] Feature 2 — [brief description]
- [x] Feature 3 — [brief description]

### In Progress
- [ ] Feature 4 — [brief description, who's working on it]
- [ ] Feature 5 — [brief description]

### Planned
- [ ] Feature 6 — [brief description]
- [ ] Feature 7 — [brief description]

## Known Issues

| Issue | Impact | Workaround | Ticket |
|-------|--------|------------|--------|
| [Description] | [High/Medium/Low] | [If any] | [PROJ-123] |
| [Description] | [High/Medium/Low] | [If any] | [PROJ-124] |

## Immediate Priorities

1. **[Priority 1]** — [Why it's urgent]
2. **[Priority 2]** — [Why it matters]
3. **[Priority 3]** — [Context]

## Technical Debt

| Debt | Cost to Fix | Risk if Ignored | Ticket |
|------|-------------|-----------------|--------|
| [Description] | [Estimate] | [What breaks] | [PROJ-125] |

## External Dependencies

| Service | Status | Notes |
|---------|--------|-------|
| [API/Service name] | ✅ Operational | [Any notes] |
| [Database] | ✅ Operational | [Any notes] |
| [Third-party service] | ⚠️ Degraded | [Issue description] |

---

## Maintenance

Update this file when:
- A feature ships to production
- A new bug is discovered
- Priorities change
- External service status changes

*This is the "what's true right now" file. Keep it current.*
