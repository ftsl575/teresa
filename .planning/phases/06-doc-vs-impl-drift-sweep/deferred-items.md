# Phase 6 Deferred Items (out-of-scope discoveries during Plan 06-06 execution)

## ROADMAP.md stale Phase 4 row

**Discovered:** During Plan 06-06 T3 / metadata commit prep on 2026-05-11.

**Issue:** `.planning/ROADMAP.md` Progress table shows:
```
| 4. Cache Redirect | v1.1 | 0/3 | Planning complete | - |
```
But Phase 4 actually completed all 3 plans (commits `46c88d2`, `9cf94dd`, `f61d996`, `8eb8302`; SUMMARY files for 04-01 / 04-02 / 04-03 all exist; `04-VERIFICATION.md` exists). The row should read `3/3 | Complete | 2026-05-10`.

**Why deferred:** Per executor SCOPE BOUNDARY rule — only auto-fix issues directly caused by the current task's changes. This is a pre-existing roadmap-bookkeeping drift from Phase 4 closure, not introduced by Plan 06-06. The Phase 6 row was correctly updated to `6/6 | Complete | 2026-05-11` as part of this plan.

**Recommended fix:** A standalone roadmap-bookkeeping touch-up (or roll into the v1.1 milestone-close `/gsd-complete-milestone` step). Should also re-verify Phase 5 row (currently `1/1 | Complete | 2026-05-10` — looks correct).

**Severity:** LOW — bookkeeping only; does not affect execution gates or verification gates. v1.1 milestone close will surface it naturally.
