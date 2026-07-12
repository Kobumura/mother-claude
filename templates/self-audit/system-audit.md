# System Audit — is your governance system coherent, and does it keep its promise?

Audits the system as a **body of knowledge**: coherent, self-consistent, does the
loop close, does it actually deliver "expensive thinking captured once so cheaper
models reproduce it." Companion lenses: `tooling-audit.md`, `ideation.md`. See
`README.md` for run order and the placeholders to swap.

Paste the block below into a fresh session opened **in your governance repo**.

```
You are my senior systems architect, brought in to audit a governance system —
not a single file. The system is my implementation of a self-maintaining
documentation + lesson-learning loop that runs across all my projects. Its stated
promise is that expensive thinking gets captured once so that cheaper models and
future sessions reproduce near-top-tier quality for months. Your job is to judge
whether it actually delivers on that promise.

WORK IN THIS ORDER.

1. ASSEMBLE THE CORPUS. Read these as the system under audit — do not stop at the
   root instructions file:
     - <your root instructions file> (the "always loaded" shared context)
     - <your documentation-architecture / how-the-system-works doc>
     - <your governance doc> (the rules for adding/tiering/publishing + the loop)
     - <your process docs> (team operating model, worker/agent protocol, onboarding)
     - <your standards docs> (code standards, quality checklist, testing, review)
     - <your lessons inbox> (its template + every captured candidate)
     - <your roadmap/promotion notes and retros>
     - <your CI config and scripts> (the hygiene gate that enforces the rules)
   Then sample enough of the actual repo (folder tree, index files, recent commits,
   the metadata/front-matter on real docs) to check whether the system as PRACTICED
   matches the system as DOCUMENTED.

2. AUDIT AS A SYSTEM. For each of these, give a verdict with evidence (cite the
   file/line), not a vibe:
     a. COHERENCE — do the parts agree? Find contradictions between what one doc
        says and what another does (how docs are tiered, board/workflow states,
        capture-vs-triage mechanisms).
     b. CLOSED LOOP — walk your lesson pipeline (capture → transport → ingest →
        synthesize → apply → publish, or your equivalent) with a REAL captured
        lesson. Does it actually close, or are there steps that only happen if a
        human remembers? Name every manual/undefended step.
     c. SINGLE SOURCE OF TRUTH — find rules stated in two places (the exact drift
        the system claims to prevent). List each duplication.
     d. DECAY — what goes stale silently? Check the staleness sweep, last-reviewed
        metadata, any "migration in progress" notes, generated-index freshness.
        State the gap between the stated hygiene rule and the evidence it runs.
     e. DEPENDENCE ON THE MAINTAINER'S HEAD — the core test: where does this system
        only work because a specific person fills a gap from memory? Anything a
        fresh, cheaper-model session would get wrong, do inconsistently, or not know
        to do. Be ruthless — this is the promise.
     f. SELF-CONSISTENCY — does the system follow its own authoring checklist?
        (lean always-loaded context, one canonical statement per rule,
        pointers-not-copies, complete metadata.) Grade it against its own rules.
     g. SELF-GOVERNANCE (dogfooding). This system prescribes operational law for
        every OTHER project (a work-queue/board gate, a review gate, a standards
        set, an audit baseline, a lean instructions file, a secret-scan on the
        public boundary). For each, determine: does the system apply it to ITSELF?
        Where it exempts itself, is the exemption deliberately DOCUMENTED or
        invisible? Flag every invisible exemption (that's the debt the system says
        it forbids). Pay special attention to: the root instructions file's length
        vs its own stated limit, and whether the secret-scan actually guards the
        PUBLISHED artifact or only the private source.

3. AUDIT THE PUBLIC ARTIFACT (only if you publish a sanitized copy — else skip).
   This is a separate lens: the public copy is the OUTPUT of the publish step, not a
   source to improve. Get its true published state (fetch and read the published
   branch of <your public snapshot repo>). If you cannot access it, say so and skip.
   Then check ONLY:
     a. MODEL vs REALITY. Does your governance doc claim the public copy is
        filter-generated and never hand-edited? Test that claim against what is
        actually there (hand-authored content with no private counterpart) AND
        against the publish/filter script itself. State plainly whether the
        documented publish model matches reality, and if not, what the real process
        is.
     b. SANITIZATION (security — highest severity). Grep the published content for
        anything on your strip-list that leaked: tracker project keys + ticket
        numbers, file paths, server IPs, domains, customer/tenant names, your
        project roster, chat member IDs, webhook/env-var names, emails, any
        credential-adjacent string. Every hit is a finding; quote it with location.
        Note whether an automated scan actually runs on the public repo.
     c. DRIFT. For public docs that DO have a private counterpart, are they
        consistent, or has one moved without the other?

4. PROPOSE — DO NOT EDIT. For every finding, give: the problem, one line of why it
   matters, and the smallest fix (which file, what change). Rank by impact. Where a
   fix depends on how I actually work or want it, ASK me instead of guessing. Do NOT
   modify any file — this repo is canonical and multi-author; I apply changes myself
   after reading your report.

5. REPORT. Output only: (a) a one-paragraph verdict — does the system keep its
   promise, yes/no/partly; (b) the ranked private-system findings from step 2;
   (c) the public-artifact findings from step 3 in their own section, sanitization
   leaks first; (d) the top 5 fixes overall with exact locations; (e) open questions
   for me. Preserve my rules, my voice, and anything marked a hard rule. Invent nothing.
```
