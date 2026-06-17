# Maestro E2E Playbook

> **Companion to** [`e2e-testing-standards.md`](../e2e-testing-standards.md).
> That doc is the **conventions** (testID naming, selector priority, flow structure). This is the
> **war-stories** — the specific failures we hit running Maestro on real React Native apps in CI,
> and the fixes that actually worked. Mined from a production React Native app (2025). Read it
> before standing up Maestro on a new app.

The one-line summary: **element selectors over everything, assert-before-interact, mock every
side effect at launch, and never trust a green mocked flow to catch client/server drift.**

---

## 1. Flake & brittleness — the patterns that bite

- **Ban coordinate taps.** `tapOn: { point: "50%,30%" }` was the single biggest source of flake —
  it broke across runner resolutions, densities, aspect ratios, and iOS-vs-Android modal
  positioning. Replace every one with a `testID`/text selector. No exceptions.
- **Assert-before-interact.** Precede every `tapOn`/`inputText` with `assertVisible` of the *same*
  element, and bracket transitions with `waitForAnimationToEnd`. Explicit waits beat implicit
  timing; never tap an element that may not be rendered yet.
- **Always start from a known state.** Every flow opens with a fresh `launchApp` and an
  `assertVisible` of a landmark element. Flows must run in isolation — a logged-in or mid-flow app
  is a guaranteed intermittent failure.
- **Progressive blocker-clearing, guarded.** To clear keyboards/modals without blind taps, only act
  *when the target is not visible*, and escalate through safe fallbacks:
  ```yaml
  - runFlow:
      when: { notVisible: { id: "signup-next-button" } }
      commands:
        - hideKeyboard
        - tapOn: { text: "Escape", optional: true }   # system modals
        - scrollUntilVisible: { element: { id: "signup-next-button" }, direction: DOWN }
  ```
  ⚠️ **Never use a fallback tap target that can navigate** — an early version tapped a header region
  that sent the flow *backward*. Guard with `when: notVisible` so the fallback no-ops once the
  target appears.
- **`scrollUntilVisible` for anything below the fold.** Tall forms (OAuth buttons pushing the
  primary CTA off-screen) made naive taps miss. `scrollUntilVisible: { element: { id: ... },
  direction: DOWN, timeout: 5000 }` before tapping. (This also surfaces real app UX bugs — a screen
  with no ScrollView.)
- **Defensively dismiss OS/keyboard overlays.** CI and real devices inject overlays (clipboard
  prompts, Gboard tips, "deprecated method" warnings). Enumerate the ones your CI image shows and
  add guarded `when: { visible: <text> }` → `pressKey: Back` dismissals.
- **Use dynamic test data.** Hardcoded emails/phones cause "already exists" failures on re-run. Use
  Maestro built-ins: `test.${TIMESTAMP}@maestro.dev`, `inputRandomEmail`, `inputRandomText`,
  `${RAND_DIGITS_4}`. (Exception: the mocked-verification path may use a *fixed* test phone — see §4.)

## 2. iOS simulator + Metro in CI (the slow-and-fragile layer)

CI simulators are dramatically slower than local; the fix is **poll for readiness, never sleep a
fixed amount.**

- **Wait for Metro to finish bundling** — poll, don't sleep:
  ```bash
  for i in $(seq 1 60); do
    curl -s http://localhost:8081/status | grep -q "packager-status:running" && break
    sleep 2
  done
  ```
- **Confirm the simulator booted** before install/test: poll
  `xcrun simctl list devices | grep "<device>" | grep Booted` (~30× / sleep 3).
- **Pre-test health check:** Metro running + app installed (`xcrun simctl list apps booted | grep
  <appId>`) + a generous **~45s first-bundle settle** (RN's first load in CI is far longer than local).
- **Handle the iOS ATT dialog explicitly** — it appears in automation:
  `tapOn: { text: "Ask App Not to Track", optional: true }` then `waitForAnimationToEnd`.
  `optional: true` makes it a safe no-op on Android.
- **Collect artifacts on failure** (`if: failure()`): Metro logs (`~/.expo/metro-*.log`) and
  `xcrun simctl list devices`.
- **Local Metro on Windows dev hosts** (the counterpart pain): native watchers throw
  `UNKNOWN: ... watch`. Fixes: `CHOKIDAR_USEPOLLING=true`; kill the *full* set of stuck processes
  (`node`, `java`, `gradle` together); fall back to port 8082 when 8081 has zombies; `--reset-cache`
  after branch switches. **Never use `2>nul` redirects on Windows** — they create literal `nul`
  files that corrupt directory scans (we still have stray `nul`/`android/nul` artifacts from this).

## 3. Cross-platform — one flow file for both

- **A single flow runs on iOS and Android** when you lean on `testID` selectors (identical on both)
  plus `optional: true` for platform-only steps. We achieved this; don't fork files per platform.
- **Handle divergence with guards, not forks:** iOS ATT dialog (`optional: true`); Android
  clipboard/keyboard overlays (`when: visible` dismissals); include both `Escape` and `pressKey:
  Back` in the fallback chain. For a genuinely platform-specific step, use
  `runScript: { when: { platform: "iOS" } }` / `Android`.
- **Pin emulator floors:** Android **API 33+** (API 28 is incompatible), iOS **15+**.

## 4. Mocking — launch arguments, double-guarded

**Decision: launch arguments for core/auth flows; WireMock only later, for failure simulation.**
(Trade study: launch args ≈2 hrs, zero infra, fast, prod-safe; WireMock ≈6–8 hrs + a server/proxy to
maintain but gives real network-error/timeout coverage.)

- **The reusable mechanism:** install `react-native-launch-arguments`; at each network boundary read
  the flag and branch. **Double-guard the gate so mock code is dead in production:**
  ```js
  const launchArgs = LaunchArguments.value();
  const isMock = (launchArgs?.isUITest === "true" || launchArgs?.isUITest === true) && __DEV__;
  ```
  The `&& __DEV__` is a **security stop** — even if the flag leaks into a prod build, the mock path
  cannot execute.
- **Mock *every* external side effect, not just the one under test** — SMS/passcode, OAuth, push
  registration, user bootstrap. A half-mocked flow still hits real infra and flakes.
- **Activate at launch:** `launchApp: { appId: <id>, arguments: { isUITest: "true" } }`.
  Standardize on **one** flag name (`isUITest`) — ours drifted (`mockAPI`/`mockVerification` appear in
  places and are unused in source). Pick one, document it, grep out the rest.
- **Keep production UI fidelity.** Mocks short-circuit the *network* only — the test still drives the
  real verification UI (any valid-format code succeeds). You're testing real components, not a stub.
- **Mock to protect the database** — a fixed test phone + mock path means zero DB writes / no
  duplicate records per CI run.
- **Do not automate real OAuth.** Google/Apple flows are too complex to mock reliably mid-flow.
  Assert the button is present (`assertVisible: { id: "google-oauth-button" }`) to prove integration;
  test the actual OAuth path manually.

## 5. CI wiring

- **Two maturity phases.** *Phase 1 (manual)* = ~15 steps of simulator selection + Maestro install +
  build + the Metro/sim poll loops in §2; brittle, fragile device-name regex, but full control.
  *Phase 2* = replace it with the marketplace action:
  ```yaml
  - uses: mobile-dev-inc/action-maestro-test@v1
    with:
      flows: .maestro/
      ios-version: "18.0"
      include-tags: smoke
  ```
  which provisions the simulator, handles errors, and collects artifacts. **Verify Phase 2 actually
  shipped before recommending it** — in our repo it was planned, not confirmed.
- **Tag for staged gates:** `smoke` on every build, `auth`/critical pre-beta, full suite pre-store
  (mirrors the quality-gate ladder).
- **Optimizations:** iOS+Android matrix, skip on docs-only changes, cache simulator state.
- **Emit artifacts** (screenshots, logs, timing, hierarchy dump) and report pass/fail to Slack.
- ⚠️ The end-to-end pipeline YAML lives in your CI/CD system, not the app repo — source it from there
  rather than the stub workflow names the app's `.maestro/README.md` references.

## 6. testID & selector conventions (quick recap — full rules in e2e-testing-standards.md)

- **kebab-case `testID` on every interactive element:** `get-started-button`, `email-input`,
  `signup-next-button`, `verification-code-container`.
- **Selector priority:** `id` → `text` (only when no testID) → coordinates **never**.
- **Pair testID with a settle:** `assertVisible: { id }` → action → `waitForAnimationToEnd`.
- ⚠️ **Verify the testID reaches the native tree.** Some component-library buttons (e.g. native-base)
  don't forward `testID`. Confirm with `maestro hierarchy` / `maestro studio` before assuming a
  wrapper passes it through.
- **Debugging triad:** `maestro test <flow> --debug` (visual steps), `maestro hierarchy` (dump the
  element tree to find the real selector), `maestro studio` (interactive exploration).

## 7. Hard-won warnings

- 🔴 **A green mocked E2E does NOT catch client/server contract drift.** Our signup flow passed via
  the launch-arg mock while phone verification was broken in production for ~a month (frontend sent
  `code`, backend expected `passcode`). Mocks bypass exactly the integration that breaks. **Pair
  mock-based E2E with a real integration/contract test on every money/auth path** (this is why our
  standards require contract tests where a client and server can drift).
- **Don't present commented-out/stub flows as passing tests.** Keep them as labelled examples.
- **Quarantine flakes explicitly.** "Zero maintenance / 95% reliable" is a trap claim — track and
  quarantine flakes per the testing standards; don't inherit a no-process assumption.
- **Tooling pins:** Maestro 1.40.3+, Node 18+.

---

## Per-project TODOs (nail these down when adopting)

These are the gaps the source docs left open — resolve them for each app, don't copy-paste blind:

1. **Standardize the mock flag** to `isUITest` and remove `mockAPI`/`mockVerification` drift.
2. **Source the real CI pipeline from your CI/CD system** — the app-repo workflow names were stubs.
3. **Author the Android emulator CI boot/health snippet** (`adb`/`avd` equivalents of the §2 iOS
   poll loops) — referenced but never written down.
4. **WireMock is a decision, not an implementation** — if you adopt the hybrid, supply the proxy
   config + an example mock definition.
5. **Document the testID-forwarding fix** for component-library buttons that swallow `testID`.
6. **Add the flake-quarantine mechanism** explicitly to the project's test config.
