# E2E Architecture — the layered pyramid

> **Where this sits among the three E2E docs — read the boundary first:**
> - **This doc** owns *strategy* — what the layers are, what each layer's job is, and why.
> - [`e2e-testing-standards.md`](e2e-testing-standards.md) owns *tactics* — testID naming,
>   selector priority, flow structure.
> - [`playbooks/maestro-playbook.md`](maestro-playbook.md) owns *Maestro
>   war-stories* — the specific failures running Maestro in CI and the fixes that worked.
>
> If you're about to write a layer definition in one of the other two, it belongs here instead;
> if you're about to restate a testID rule here, link to the standards doc instead.

## Why this exists

A multi-day effort to "fix the smoke suite" spiralled largely because there was **no shared
definition of E2E layers.** A "skip onboarding" camp and a "traverse onboarding" camp argued
past each other for days — and *both were right*, because they were defending **different
layers.** Name the layers and the false binary dissolves. That's the lesson this doc encodes.

## The layers — each has a distinct job; do not conflate them

### Layer 0 — the UI-test harness

A **double-guarded** seam (`isUITest && __DEV__`, dead in production) that mocks **every**
external side effect at launch — auth, GPS, maps, store/location discovery, third-party data
APIs, push registration. Not just the one side effect under test: a half-mocked flow hits real
infrastructure and flakes. The harness is the foundation every higher layer stands on.

The double guard is a **security stop** — even if the test flag leaks into a production build,
the `&& __DEV__` means the mock path cannot execute. (Mechanism detail — launch arguments,
single flag name — lives in the Maestro playbook §4.)

#### The must-mock registry (a first-class Layer-0 deliverable)

Some third-party APIs use **bot/emulator detection** (e.g. Kasada, Akamai, PerimeterX) and
**refuse to function on an emulator at all.** These are not "should mock" — they are *must mock
or the flow cannot run.* Maintain a per-app **registry** of these endpoints as an explicit
Layer-0 deliverable, so adopting a new flow starts from "which of these does it touch?" rather
than discovering the refusal as a flake.

The principle underneath: **you are testing *your* app, never the third party's code** — so the
third-party boundary is always stubbed with captured fixtures. The bot-detection vendors are
just the case where skipping the stub fails loudly instead of silently.

### Layer 1 — Smoke (the per-PR gate)

Boots in UI-test mode, **skips onboarding deterministically**, and asserts every primary
surface is reachable. Must be **fast and stable** — it gates every PR. Skipping onboarding
*here* is **correct layering, not a shortcut**: you never get onboarding coverage from the
smoke, and that's fine, because that coverage lives at Layer 2. A smoke that traverses
onboarding is a smoke that's slow and flaky for no gain.

### Layer 2 — Critical-journey flows

One flow per real user journey — **including a dedicated onboarding-traversal flow** that drives
the *real* wizard with mocked side-effects. **This is where onboarding regressions are caught.**
Runs nightly + pre-release, not on every PR. The "traverse onboarding" camp was right *about
this layer.*

### Layer 3 — Jest / RTL component + integration tests

The **bulk** of coverage. E2E gives confidence on critical journeys; it never gives "full
coverage" — that lives in the pyramid base. If you're reaching for another E2E flow to cover an
edge case, it probably belongs here instead.

---

## The one-line model

**Layer 0 makes the app testable. Layer 1 proves it boots (every PR). Layer 2 proves the
critical journeys work (nightly/pre-release). Layer 3 is where most coverage actually lives.**
"Skip vs. traverse onboarding" is a false binary — skip at Layer 1, traverse at Layer 2.

> **Provenance:** converged from a multi-day mobile E2E hardening effort (the skip-vs-traverse
> standoff, and retailer integrations whose bot-detection vendors refuse emulators), human-blessed
> as a must-have. Companion docs: `e2e-testing-standards.md`, `playbooks/maestro-playbook.md`.
