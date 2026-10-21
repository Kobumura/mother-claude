# Changelog

Releases are deliberate snapshots, not a live mirror. Between releases this repo is expected to
lag the system it describes.

## v1.0 (2026-10)

First tagged release. It covers everything published through August 2026 (the articles, the
worker-system package, hooks, agents, templates and the roundtable tool), plus:

- **New: `worker-system/standards/e2e-architecture.md`.** The layered E2E pyramid for mobile
  apps (harness, smoke, journeys, unit tests) and the registry of what each layer must mock.
- **New: `worker-system/standards/diagnosis-traps.md`.** Five checks to run before trusting a
  failure, for when the measurement is broken rather than the system.
- **Updated: `e2e-testing-standards.md`.** A screen-identity test ID on every render state, not
  just the happy path; production code must never import from the test tree; server-rendered
  page tests assert page integrity, never a bare HTTP 200.
- **Updated: `maestro-playbook.md`.** Dev overlays that silently eat taps, and "screenshot the
  device first" when an action reports COMPLETED but the next assertion fails. Also fixes the
  broken link to `e2e-testing-standards.md`.
