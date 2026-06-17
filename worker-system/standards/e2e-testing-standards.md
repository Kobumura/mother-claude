# E2E Testing Standards

> **Applies to**: All UI projects (React Native, PHP dashboards, web apps)
> **Tool**: Maestro (mobile), can adapt patterns for Playwright/Cypress (web)

## Core Principle

**Every interactive element gets a test ID. Always prefer IDs over text for element selection.**

Text changes with localization, redesigns, and copy edits. IDs are stable. This one rule prevents 90% of flaky E2E tests.

---

## Test ID Naming Convention

### Format: `{component}-{element-type}` in **kebab-case**

```
Good:  email-input, signin-button, google-signin-button, home-screen
Bad:   emailInput, signInButton, sign_in_button, HomeScreen
```

### What Needs a Test ID

| Element Type | Example ID | Notes |
|-------------|-----------|-------|
| Screen containers | `login-screen`, `home-screen` | Wrap the outermost View/div |
| Buttons | `signin-button`, `subscribe-button` | Every tappable/clickable element |
| Text inputs | `email-input`, `password-input` | Every field |
| Links | `forgot-password-link`, `signup-link` | Navigation links |
| Lists | `conversations-list`, `settings-list` | Scrollable containers |
| Modals | `confirm-dialog`, `alert-modal` | Dialog containers |
| Toggles/switches | `dark-mode-toggle`, `notifications-toggle` | On/off controls |

### Platform-Specific Implementation

**React Native** — use the `testID` prop:
```tsx
<TextInput testID="email-input" value={email} />
<Button testID="signin-button" onPress={handleSignIn}>Sign In</Button>
<View testID="login-screen">...</View>
```

**PHP/HTML dashboards** — use the `data-testid` attribute:
```html
<input data-testid="api-key-input" type="text" name="api_key" />
<button data-testid="save-button" type="submit">Save</button>
<div data-testid="dashboard-overview">...</div>
```

**Web (React/Vue/etc.)** — use `data-testid`:
```tsx
<input data-testid="email-input" value={email} />
<button data-testid="signin-button" onClick={handleSignIn}>Sign In</button>
```

---

## Selector Priority

When writing test assertions, prefer selectors in this order:

1. **Test ID** (most reliable): `{ id: "email-input" }` or `[data-testid="email-input"]`
2. **Text content** (fallback): `{ text: "Sign In" }` — only when no ID exists
3. **Accessibility label** (last resort): `{ label: "Email" }` — fragile, avoid

Never rely on CSS classes, DOM structure, or element position for test selectors.

---

## Test Structure

### One Flow = One User Journey

Each test file should cover a single user journey, not a grab-bag of assertions.

```
tests/
├── flows/
│   ├── app-launch.yaml          # App starts and shows welcome
│   ├── login-email.yaml         # Email login end-to-end
│   ├── login-oauth-google.yaml  # Google OAuth flow
│   ├── signup-complete.yaml     # Full signup journey
│   └── navigation-smoke.yaml   # Can reach all main screens
├── utils/
│   └── login.yaml               # Reusable login helper
├── config.yaml                  # Global test configuration
└── README.md
```

### Use Tags for Subsets

Tag tests so you can run targeted subsets:

```yaml
tags:
  - smoke       # Quick health check (run on every build)
  - auth        # Authentication flows
  - payments    # Subscription/purchase flows
  - regression  # Tests for previously-caught bugs
```

```bash
# Run only smoke tests
maestro test flows/ --include-tags=smoke

# Run auth tests
maestro test flows/ --include-tags=auth
```

### Extract Reusable Utilities

Common actions (login, navigation setup) should be shared utilities, not duplicated:

```yaml
# utils/login.yaml
- tapOn:
    id: "email-input"
- inputText: ${TEST_EMAIL}
- tapOn:
    id: "password-input"
- inputText: ${TEST_PASSWORD}
- tapOn:
    id: "signin-button"
```

```yaml
# flows/some-test.yaml
- runFlow: utils/login.yaml
- assertVisible:
    id: "home-screen"
```

---

## Environment Variables

Keep credentials and config out of test files:

| Variable | Purpose | Example |
|----------|---------|---------|
| `APP_ID` | App package/bundle ID | `com.example.app` |
| `TEST_EMAIL` | Test account email | `<email>` |
| `TEST_PASSWORD` | Test account password | `testpassword123` |
| `BASE_URL` | Dashboard URL (web) | `https://staging.example.com` |

---

## CI Integration

Tests should run automatically in CI/CD:

- **Smoke tests**: Every build (fast, catch regressions)
- **Full suite**: Before release (comprehensive, catch edge cases)
- **Regression tests**: After bug fixes (prevent recurrence)

For mobile apps, tests run through your CI/CD pipeline as part of the build.

---

## Maintaining a Test ID Reference

Each project should maintain a `TEST_IDS.md` (or equivalent) listing all test IDs in use. This serves as:

1. A reference for test authors
2. A contract between UI and test code
3. Documentation of what's testable

Update it when adding new interactive elements. The retro agent checks for missing test IDs as part of quality review.

---

## Best Practices

1. **Add test IDs as you build, not after** — Retrofitting is painful and gets skipped
2. **Keep flows focused** — One user journey per test, not "test everything"
3. **Use tags** — Run subsets for speed, full suite for thoroughness
4. **Extract utils** — Don't duplicate login/setup across every flow
5. **Prefer IDs over text** — Stable across locales and copy changes
6. **Test the critical path first** — Login, core feature, purchase. Then edge cases.
7. **Name IDs for what they ARE, not what they DO** — `signin-button` not `click-to-login`

---

*See also: `checkpoint-checklist.md` for quality standards that include test ID verification.*
