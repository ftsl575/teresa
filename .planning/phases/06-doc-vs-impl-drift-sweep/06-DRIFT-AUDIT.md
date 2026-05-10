# Phase 6 Drift Audit Log

**Created:** 2026-05-11
**Phase:** 06-doc-vs-impl-drift-sweep
**Sibling artifacts:** PLAN.md, CONTEXT.md, VERIFICATION.md, SUMMARY.md (per D-22)
**Sweep order:** D-14 — Group 1 (root) → Group 2 (DOCS_INDEX) → Group 3 (docs/dev) → Group 4 (docs/user) → Group 5 (other docs/) → Area A (.planning/codebase/ surgical patches).

## Purpose

Per-claim ledger for the Phase 6 mechanical drift sweep (DRIFT-01..04). Every "code does X" claim across the 16 in-scope files plus the 3 surgical-patch lines in `.planning/codebase/` is recorded here as one row, including `no_drift` rows so the log is a complete inventory of every claim considered (per Specifics + ROADMAP §SC-5 "every file checked, every claim flagged, and the resolution for each").

`resolution` ∈ `{remove, patch, no_drift}`. Default per D-13 is `remove`; `patch` only when the claim is load-bearing for the reader's mental model AND the patched form is itself stable (symbol/section ref, not a line number).

Categories swept (per D-11):
1. Path/file existence + behavior claims (highest load-bearing — class that broke v1.0).
2. Switch/CLI flag claims.
3. Line-number refs (`file.py:N`) — apply remove > patch aggressively; rewrite to symbol/section refs.

Categories DEFERRED per D-12 (folded into v1.2 `/gsd-map-codebase` refresh; if encountered in-scope, REMOVE):
- Volatile counts: test count, LOC counts, rule_id counts, vendor count.

## Audit Table

| file | line | claim_summary | check_command | resolution |
|------|------|---------------|---------------|------------|

<!-- Rows appended by Plans 01-05 below this line. -->

## Tally (filled by Plan 06)

- Total claims swept: TBD
- Resolutions: TBD remove / TBD patch / TBD no_drift
- Files touched: TBD of 19 (16 in-scope + 3 surgical map lines)
- Drift remaining post-phase: 0 (per ROADMAP §SC-1)
