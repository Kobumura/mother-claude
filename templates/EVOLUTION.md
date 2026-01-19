# EVOLUTION.md - [Project Name]

> **Historical context for legacy projects.** For rewrites and migrations, this document is more important than CLAUDE.md. Without it, Claude can understand *what* exists but not *why* it exists.

## Project History

**Created**: [Year]
**Active Development**: [Year range]
**Status**: [Active / Maintenance / Archive / Being Rewritten]

## Data Volumes

Understanding scale helps with migration planning and architectural decisions.

| Metric | Current Value | Notes |
|--------|---------------|-------|
| Total Users | [e.g., 5,000] | |
| Active Users (monthly) | [e.g., 500] | |
| Primary Data Records | [e.g., 50,000 messages] | |
| Database Size | [e.g., 500MB] | |
| Peak Concurrent Users | [e.g., 50] | |

## Feature History

### Why Features Were Built This Way

| Feature | Why It Exists | Historical Context |
|---------|---------------|-------------------|
| [Feature A] | [Business need it solved] | [Constraints at the time, e.g., "Built in 2015 before React existed"] |
| [Feature B] | [Business need] | [Why this approach was chosen] |

### Features That Changed Over Time

- **[Feature X]**: Originally did [A], changed to [B] because [reason]
- **[Feature Y]**: Started as [simple], evolved into [complex] due to [user feedback]

## Pain Points

### User Complaints

Document what users complained about—this is your prioritization guide for the rewrite.

| Pain Point | Frequency | Impact | Notes |
|------------|-----------|--------|-------|
| [e.g., "Can't search old messages"] | High | High | Users ask for this monthly |
| [e.g., "Slow loading on mobile"] | Medium | Medium | Only affects large accounts |

### Admin Pain Points

What was tedious to manage? What manual interventions were needed?

- [e.g., "Password resets required direct database access"]
- [e.g., "Monthly reports had to be manually compiled from SQL queries"]

## Known Issues & Workarounds

### Bugs That Required Manual Fixes

| Issue | Workaround | Why Not Fixed Properly |
|-------|------------|----------------------|
| [e.g., "Duplicate records on network timeout"] | [Manual dedup script] | [No time / too risky to refactor] |

### Technical Debt

- [e.g., "No separation between business logic and UI"]
- [e.g., "Database has no foreign keys—referential integrity enforced in code"]
- [e.g., "Session management is homegrown, has known race conditions"]

## What Not to Repeat

Critical lessons learned—mistakes the rewrite should avoid.

1. **[Mistake]**: [What went wrong and why]
   - **Instead**: [What to do differently]

2. **[Mistake]**: [Description]
   - **Instead**: [Better approach]

## Screenshots / UI Reference

If available, include screenshots of the old UI. These calibrate expectations and help understand user mental models.

- `screenshots/dashboard.png` - Main dashboard layout
- `screenshots/user-form.png` - User editing experience

## External Dependencies

| Dependency | Purpose | Status | Notes |
|------------|---------|--------|-------|
| [API/Service] | [What it does] | [Active/Deprecated] | [Migration considerations] |

## Migration Considerations

### Data That Must Be Preserved
- [e.g., "All user accounts and credentials"]
- [e.g., "Transaction history for legal compliance"]

### Data That Can Be Regenerated
- [e.g., "Cached calculations"]
- [e.g., "Search indexes"]

### Breaking Changes to Avoid
- [e.g., "Users expect URLs to stay the same—maintain URL compatibility"]
- [e.g., "Mobile app v1.x still makes requests to /api/v1—keep it working"]

---

## For Claude Sessions

When working on a rewrite or migration:

1. Read this document first to understand the *why*
2. Reference the legacy codebase for specific implementation details
3. Prioritize fixing documented pain points
4. Avoid repeating documented mistakes
5. Preserve data and URLs listed as critical

---

*This document captures institutional memory that would otherwise be lost. Update it when you discover new historical context.*
