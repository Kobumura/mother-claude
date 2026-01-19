# Checkpoint Checklist

> **The Instant Retrospective**: Ask these questions at every PR, every commit, every natural stopping point. Don't wait for problems to accumulate.

## The Meta Question

Before anything else, ask:

> **"If I had to hand this codebase to a new developer tomorrow, would they understand it without me explaining anything?"**

If the answer is "no," stop and fix it before moving forward.

---

## Pre-Flight Checklist (Before Building)

Run this BEFORE writing a new screen, component, or feature:

- [ ] **UI Primitives**: What components does this need? (Button, Input, Card, Modal, etc.)
  - Do styled versions exist in your component library?
  - If not: **Create them FIRST**, then build the screen
- [ ] **Translation Keys**: What user-facing strings are needed?
  - Are they in the localization files?
  - If not: **Add them FIRST**
- [ ] **Similar Screen**: Is there an existing screen to reference for patterns?
- [ ] **Data Requirements**: What data/state does this need? Do the hooks/services exist?
- [ ] **Config Location**: Where do similar configs live? (Don't hardcode if others use config/env)
- [ ] **User Context**: What screen is the user on when they need this feature?
- [ ] **Test IDs**: Does every interactive element have a `testID`? (for E2E testing)

The goal: Never build a screen that requires primitives you don't have. Build bottom-up, not top-down.

---

## Red Flags (Stop Immediately)

If you see yourself typing any of these, **STOP** and fix it:

| Red Flag | What To Do Instead |
|----------|-------------------|
| `style={{` in a screen file | Create/use a styled component |
| `#RRGGBB` or `#RGB` anywhere | Use theme token (`$primary`, `$color`) |
| Quoted English string in JSX | Use `t('NAMESPACE.KEY')` from localization |
| `any` type | Define a proper interface/type |
| Copy-pasting styles from another file | Extract to a shared component |
| `// TODO` without a ticket | Create the ticket or fix it now |
| Interactive element without `testID` | Add `testID="kebab-case-id"` |

These are the patterns that create invisible technical debt. Catch them in the moment.

---

## Architecture & Design

- [ ] **Single Responsibility**: Does each file/function do ONE thing well?
- [ ] **Separation of Concerns**: Is business logic separate from UI? Data fetching separate from display?
- [ ] **DRY (Don't Repeat Yourself)**: Are we repeating code that should be abstracted?
- [ ] **YAGNI (You Ain't Gonna Need It)**: Are we over-engineering for hypothetical future needs?
- [ ] **Configuration over Hardcoding**: Is this hardcoded when it should come from config/database?

## Code Quality

- [ ] **No Magic Numbers/Strings**: Are constants named and defined somewhere sensible?
- [ ] **No Inline Styles** (frontend): Using the theme/design system?
- [ ] **Localization Ready**: No hardcoded user-facing strings?
- [ ] **Type Safety**: No `any` types sneaking in? Strict mode enabled?
- [ ] **Naming Clarity**: Would someone understand what `handleClick` or `processData` does without reading the implementation?

## Error Handling & Edge Cases

- [ ] **Graceful Failures**: What happens when this fails? Does the user see a helpful message or a crash?
- [ ] **Null/Empty Handling**: What if the data is null? Empty array? Undefined?
- [ ] **Network Failures**: What if the API is down? Timeout? 500 error?
- [ ] **Loading States**: Does the user know something is happening?
- [ ] **Boundary Conditions**: First item? Last item? Zero items? Max items?

## Testing & Reliability

- [ ] **Testable**: Is this structured so it CAN be tested?
- [ ] **Tested**: Did we actually write tests?
- [ ] **Test Coverage**: Are the important paths covered, not just the happy path?
- [ ] **Regression Prevention**: If this broke before, is there a test to prevent it breaking again?

## Performance & Security

- [ ] **No Secrets in Code**: All keys/tokens in config files or environment variables?
- [ ] **No Blocking Operations**: Long operations are async?
- [ ] **Memory Leaks**: Cleaning up subscriptions, listeners, timers?
- [ ] **N+1 Queries**: Database calls in loops?
- [ ] **Bundle Size** (frontend): Adding a huge dependency for a small feature?

## Maintainability & Documentation

- [ ] **Self-Documenting**: Is the code clear enough that comments aren't needed?
- [ ] **Necessary Comments**: Complex logic explained? "Why" not just "what"?
- [ ] **Consistent Patterns**: Does this follow the patterns established elsewhere in the codebase?
- [ ] **Updated Docs**: If this changes behavior, are docs/READMEs updated?

---

## Project-Specific Questions

Add questions specific to your project. Examples:

### Mobile Apps
- [ ] **Platform Agnostic**: Works on iOS AND Android?
- [ ] **Native SDK Integration**: If adding a native SDK, is it initialized in native code (not just JS)?
- [ ] **Device Tested**: Verified on actual device/emulator, not just unit tests?

### API Projects
- [ ] **Backward Compatible**: Will existing clients break?
- [ ] **Documented Endpoint**: Is the API contract documented?
- [ ] **Rate Limited**: Should this endpoint have rate limiting?

### Admin/Dashboard Projects
- [ ] **Permission Checked**: Is this action properly authorized?
- [ ] **Audit Logged**: Should this action be logged for audit purposes?

### White-Label Projects
- [ ] **Multi-Brand Ready**: Will this work for Brand #2, Brand #3?
- [ ] **Config-Driven**: Is brand-specific behavior coming from config, not code?

---

## When to Run This Checklist

| Trigger | Depth |
|---------|-------|
| Every commit | Quick mental scan |
| Every PR | Full checklist review |
| End of work session | Retrospective + session handoff |
| Before release | Full checklist + QA |
| After bug fix | "How did this slip through?" analysis |

## The Accountability Question

At the end of every session, ask:

> **"What did we build today that we might regret in 6 months?"**

If something comes to mind, either fix it now or create a ticket to address it.

---

*"The best time to catch a problem is before it becomes a pattern."*

---

*For more context on instant retrospectives, see the article series at [dev.to/dorothyjb](https://dev.to/dorothyjb).*
