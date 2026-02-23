# CLAUDE.md - [Project Name]

> **Shared standards**: See `[your-docs-repo]/CLAUDE.md` for shared commit guidelines, Jira setup, and cross-project standards.
> **Path**: `[path/to/your-docs-repo]`

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
│   ├── SESSION-INDEX.md      # Quick navigation to all handoffs
│   ├── session_handoffs/     # Session continuity
│   └── guides/               # Project-specific documentation
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

## Credentials & Environment

Sensitive data is stored in:
- `.env` files (git-ignored)
- Environment variables on CI/CD
- [Password manager / secrets service]

**Never commit**: API keys, database passwords, auth tokens

Reference credentials by location, not value:
```markdown
- Database password: (in .env as DB_PASSWORD)
- API key: (in CI/CD environment variables)
```

## Key Subsystems

*[Document major subsystems separately if they have their own patterns]*

### [Subsystem Name]
- **Purpose**: [What it does]
- **Key files**: [Where to look]
- **External dependencies**: [APIs, services]

## Testing & Verification

*[Include exact commands to test key features, not just theory]*

```bash
# Verify [feature] works
curl "https://your-api/endpoint?param=value"

# Run specific test suite
npm test -- --grep "feature name"
```

## Session Handoffs

**Location**: `docs/session_handoffs/`
**Index**: `docs/SESSION-INDEX.md`
**Template**: See `[your-docs-repo]/templates/session-handoff.md`

**When to create handoffs** (Claude should proactively initiate these):
- Approaching token/context limits
- At natural stopping points
- Before switching to different tasks

## Collaboration Notes

**You are a team member, not just a tool.** Act like it.

- [Your name] appreciates questions and proactive suggestions
- If something seems off, say so — don't wait to be asked
- Suggest improvements to the codebase, the documentation, and this file itself
- Don't wait for permission to flag problems — that IS your permission

*[Add your own preferences below]*
- [Working style, communication notes]
- [Domain expertise or areas where help is needed]
- [Any quirks about the dev environment]

---

## Guidelines for This File

**Keep it lean** (<100 lines for the core content):
- Only include what Claude needs at session start
- Put detailed docs in `docs/guides/` and reference on-demand

**Include**:
- Tech stack and key dependencies
- File structure overview
- Essential dev commands
- Key conventions
- How to handle credentials safely
- Collaboration context

**Don't include**:
- Full API documentation (link to it instead)
- Detailed architectural guides (put in `docs/guides/`)
- Information that changes frequently
- Actual credential values
