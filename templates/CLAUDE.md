# CLAUDE.md - [Project Name]

> **Shared standards**: See `[your-docs-repo]/CLAUDE.md` for shared commit guidelines, Jira setup, and cross-project standards.

## Project Overview

[One paragraph describing what this project is and does]

- **Tech Stack**: [e.g., React Native, TypeScript]
- **Production URL**: [if applicable]
- **Jira Project**: [PROJECT-KEY]

## File Structure

```
project-name/
├── src/
│   ├── components/    # Reusable UI components
│   ├── screens/       # App screens
│   ├── services/      # Business logic
│   └── utils/         # Helper functions
├── docs/
│   ├── guides/        # Project-specific documentation
│   └── session_handoffs/  # Session continuity
├── CLAUDE.md          # This file
└── [other key files]
```

## Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Run tests
npm test
```

## Key Conventions

- **Naming**: [e.g., PascalCase for components, camelCase for functions]
- **Testing**: [e.g., Jest for unit tests, Maestro for E2E]
- **State Management**: [e.g., Zustand, Redux, Context]

## Session Handoffs

**Location**: `docs/session_handoffs/`
**Template**: See `[your-docs-repo]/templates/session-handoff.md`

---

## Guidelines for This File

**Keep it lean** (<100 lines):
- Only include what Claude needs at session start
- Put detailed docs in `docs/guides/` and reference on-demand

**Include**:
- Tech stack and key dependencies
- File structure overview
- Essential dev commands
- Key conventions

**Don't include**:
- Full API documentation (link to it instead)
- Detailed architectural guides (put in `docs/guides/`)
- Information that changes frequently
