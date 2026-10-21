# Diagnosis Traps

**Before you trust a failure, check that the tool showing it to you is telling the truth.**
A broken measurement looks exactly like a broken system, and a confident diagnosis built on it
produces a wrong fix and a wrong ticket. Each trap below cost real time. Add new ones here
rather than starting a new doc.

| Trap | What it looks like | Check instead |
|---|---|---|
| **The environment isn't what you think** | A failure right after a restore, install, config swap or checkout looks like a code bug. A data-only restore against a mismatched schema made a months-old migration "fail". | Confirm the setup step finished and matches a known-good baseline before diagnosing. If someone says "this has worked for months", suspect the environment, not the code. |
| **A hand-rolled DNS query** | A raw query sent without the recursion-desired flag makes public resolvers (<ip>, <ip>) answer SERVFAIL, so DNS looks broken when it isn't. | Ask a second way before believing it: `dig` with defaults, or DNS-over-HTTPS (`https://dns.google/resolve?name=<host>&type=A`). |
| **Your machine's DNS cache** | After a DNS or server move, your laptop keeps the old IP for hours, so you're testing the old box. | Test the target box directly: `curl --resolve <host>:443:<ip> https://<host>/`. |
| **A changed status is an app change** | A site that returned 200 now returns a 302 to the login page, and it looks like infra broke. It was an app deploy. | Check the app's recent deploys and commits before chasing servers, DNS or certs. |
| **A log line that isn't a result** | A deploy log's list of files reads like a success banner. | Find the line that reports the outcome (exit code, "applied", "migrated") before acting on it. |

Related: reproduce a failure before accepting someone's root cause
([`agent-worker-protocol.md`](../agent-worker-protocol.md)), and never accept a bare 200 as
proof a page is right ([`e2e-testing-standards.md`](e2e-testing-standards.md)).
