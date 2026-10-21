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

### Test a Screen Identity on Every Render State — Not Just the Happy Path

A screen needs a screen-identity `testID` on **every** state it can render — empty, loading,
error, no-permission, no-camera — not only the populated/happy branch. CI emulators run in
reduced configurations (cameraless `-camera-back none`, no GMS, software GPU), so a `testID`
that exists only on the camera-active (or data-present) branch is **invisible in CI** and the
flow fails for an environment reason that looks like a real bug. Name them `{screen}-{state}`,
e.g. `scanner-screen-no-camera`, `home-screen-empty`. (The CI emulator ≠ your phone — see
`maestro-playbook.md` §3.)

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

## Test Isolation — production code must not depend on the test tree

- **App code must never import from `__tests__`.** Bundlers exclude the test tree from the
  release/offline build, so an app-reachable `import` from `__tests__` doesn't merely fail a
  test — it **breaks the production bundle** (the app can't load JS at all). And a green unit CI
  won't catch it, because **Jest never bundles** (see `checkpoint-checklist.md` → *CI Gates*).
- **Shared golden data** that *both* tests and runtime consume belongs in a neutral source dir
  (e.g. `src/fixtures/`), never `__tests__/`.
- **Enforce with a cheap guard test** that scans `src/` (excluding `src/__tests__`) for
  `__tests__` imports — it catches the break in fast Jest CI, not a 17-minute emulator run.

This is the Layer-0 isolation boundary in practice — full layer model in
[`e2e-architecture.md`](e2e-architecture.md).

---

## Assert Page Integrity — Never a Bare HTTP 200 (server-rendered pages)

For server-rendered pages (PHP, SSR), **a passing page test may never coexist with a server
fault in the response body.** A `200` only means the request reached a handler — a fatal at the
*bottom* of a page returns 200 with a stack trace appended to half-rendered HTML, and a
status-code assertion sails straight past it. Encode the rule as **shared helpers**, not prose
(prose is exactly how this slips):

- **`expectNoServerError(page)`** — fails on *hard* fault signatures only (`Fatal error`,
  `Uncaught …Error/Exception`, `Stack trace:`, `Parse error:`, framework 500 markers), so
  intentional 404/500 specs are unaffected.
- **`expectPageComplete(page)`** — asserts an end-of-document **sentinel** the layout emits right
  before `</body>`. A mid-page fatal truncates output before it, so its absence = truncation.

Wire `expectNoServerError` as an **auto fixture** on the shared test so coverage is universal,
not per-spec opt-in — but **skip it when the test already failed** so it never masks the real
cause; error-state specs opt out by importing the raw test. This is the server-rendered analog
of *"green unit CI ≠ runnable app"* (`checkpoint-checklist.md` → *CI Gates*): proof the request
arrived, never proof the page rendered. *(Provenance: an admin page returned 200 with a stack
trace on a truncated body; a whole feature was dead for days while unit tests, lint, and
top-of-page e2e all stayed green.)*

---

*See also: `checkpoint-checklist.md` for quality standards that include test ID verification.*
