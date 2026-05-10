# Phase 6: Doc-vs-Impl Drift Sweep - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-11
**Phase:** 6-doc-vs-impl-drift-sweep
**Areas discussed:** A (codebase-maps stale refs), B (`run.ps1 -?` pointer reality), C (sweep mechanism + claim definition), D (DOC_INVARIANTS.md design)

---

## Area A — Codebase-maps stale refs

**Context:** Phase 5 explicitly punted `.planning/codebase/STACK.md:79` and `INTEGRATIONS.md:150` (stale post-Phase-4 PYTHONPYCACHEPREFIX claims) to "Phase 6's drift sweep OR a post-v1.1 `/gsd-map-codebase` refresh". The 7-file `.planning/codebase/` map tree carries many other potentially-stale claims; Phase 6 has to decide whether to include any/all of it.

### Decision A.1 — Maps scope

| Option | Description | Selected |
|--------|-------------|----------|
| Surgical fix only (2 lines) | Fix STACK.md:79 and INTEGRATIONS.md:150 inline as part of Phase 6 — just those two specific stale PYTHONPYCACHEPREFIX claims. Do NOT extend the sweep to all 7 codebase maps. | |
| Full /codebase/ sweep too | Add all 7 .planning/codebase/*.md files to the in-scope sweep — they accumulate the same kind of "code does X" claims the docs/ tree does. Phase 6 becomes 16+7=23 files in scope. | |
| Defer entirely to /gsd-map-codebase | Phase 6 does NOT touch .planning/codebase/. The 2 stale lines and any broader drift get cleared in a separate /gsd-map-codebase invocation later. Phase 6 stays exactly to the ROADMAP-enumerated 16 files. | |
| Surgical fix + flag broader maps | Patch the 2 known stale lines as part of Phase 6, AND record a "broader codebase-maps refresh needed" deferred item for /gsd-map-codebase. | ✓ |

**User's choice:** Option 4 — surgical fix the 2 stale lines + capture broader maps refresh as deferred /gsd:map-codebase task.
**Notes:** Closes the known drift surgically without expanding sweep scope. Captured as D-01.

### Decision A.2 — Extra HYG-01 leak (INTEGRATIONS.md:55)

While scouting, noticed a third stale-ish line: `INTEGRATIONS.md:55` has hardcoded `C:\Users\G\Desktop\temporary` — an HYG-01 username leak that escaped v1.0 cleanup.

| Option | Description | Selected |
|--------|-------------|----------|
| Add to surgical set | Fix it inline alongside STACK.md:79 + INTEGRATIONS.md:150. Surgical set becomes 3 lines across 2 files. | ✓ |
| Leave for broader refresh | Don't expand the surgical set. The hardcoded path stays until /gsd-map-codebase runs. | |

**User's choice:** Add to surgical set.
**Notes:** Captured in D-02 (the 3 surgical lines).

---

## Area B — `run.ps1 -?` pointer reality (DRIFT-02)

**Context:** ROADMAP DRIFT-02 says trim CLI prose and replace with "a pointer to `run.ps1 -?`". But `run.ps1` has no comment-based help block (`<#.SYNOPSIS#>`), so `Get-Help .\run.ps1` and `.\run.ps1 -?` return only the `param()` introspection — no descriptions. The pointer goes nowhere useful at phase start.

### Decision B.1 — Pointer strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Add comment-based help to run.ps1 | Add a <#.SYNOPSIS#> block at the top of run.ps1 so 'run.ps1 -?' actually returns useful help. Then docs point at '-?' and DRIFT-02 wording becomes literally true. | |
| Make ONE_BUTTON_RUN.md the canonical CLI doc | Trim RUN_PATHS_AND_IO_LAYOUT.md's CLI prose to point at ONE_BUTTON_RUN.md. Don't add help to run.ps1. | |
| Both: help block + canonical-doc pointer | Add help block to run.ps1 AND keep ONE_BUTTON_RUN.md as canonical switch table. Both reader paths work. | ✓ |

**User's choice:** Both — help block + canonical-doc pointer.
**Notes:** Captured as D-04. Help block content (D-05) mirrors the existing RU header's 6 invocations.

### Decision B.2 — RU header disposition

| Option | Description | Selected |
|--------|-------------|----------|
| Coexist — leave RU, add EN help block | Add new <#.SYNOPSIS#> block adjacent to the existing RU header. RU stays per Phase 5 D-02 + D-18 historical-content convention. | ✓ |
| Translate — replace RU with EN help block | Delete the RU header and replace with the new <#.SYNOPSIS#> block in English. Cleaner long-term but actively removes a piece D-18 said to preserve. | |
| Decide per-line during planning | Punt the exact placement to the planner. CONTEXT.md just locks 'add EN help block; RU header treated per current historical-content convention'. | |

**User's choice:** Coexist.
**Notes:** Captured as D-06.

---

## Area C — Sweep mechanism + claim definition

### Decision C.1 — Sweep mechanism

| Option | Description | Selected |
|--------|-------------|----------|
| Hybrid — manual sweep, scripts subset | Phase 6 sweep is human-driven; audit log records every (file, line, claim, check, resolution) tuple. DOC_INVARIANTS.md (DRIFT-03) materializes the 5+ MOST drift-prone of those checks as one-liners for future automated re-sweep. | ✓ |
| Pure manual (Phase 5 precedent) | Phase 6 sweep entirely by hand. DOC_INVARIANTS.md stands separately as a doc-of-record. SC #1 re-sweep = re-read all 16+ files. Cheapest now, expensive every future time. | |
| Fully scripted batch sweep | Build a sweep.py / sweep.ps1 that ingests a claims list and runs all checks mechanically. Highest tooling cost; introduces a permanent tooling artifact. | |

**User's choice:** Hybrid — manual sweep with audit log, materialize top 5+ drift-prone checks into DOC_INVARIANTS.md.
**Notes:** Captured as D-10. Sets up the durable mechanism for v1.2+ without inflating Phase 6's tooling surface.

### Decision C.2 — Claim categories in scope

| Option | Description | Selected |
|--------|-------------|----------|
| Path/file existence + behavior claims | Test-Path / grep / runtime checkable. Highest load-bearing. The class that broke v1.0. | ✓ |
| Switch/CLI flag claims | grep in launcher / main.py. Medium load-bearing. Common in ONE_BUTTON_RUN.md, CLI_CONFIG_REFERENCE.md, etc. | ✓ |
| Volatile counts (test count, LOC, vendor count, doc count, rule_id counts) | wc / pytest --collect-only checkable. Drift fast. Most live in spec_classifier/CLAUDE.md (out of scope). Patching chases moving target. | |
| Line-number refs (file.py:N) | Line-shifted ones are stale. High noise. Apply remove > patch aggressively: rewrite as symbol/section refs. | ✓ |

**User's choice:** Categories 1, 2, 4 — path/behavior, CLI flags, line-number refs (remove > patch as symbol references).
**Notes:** Skip volatile counts — mostly in out-of-scope spec_classifier/CLAUDE.md, patching chases moving target. Captured as deferred for /gsd-map-codebase refresh (D-12).

### Decision C.3 — Audit log location

| Option | Description | Selected |
|--------|-------------|----------|
| Separate 06-DRIFT-AUDIT.md, referenced from SUMMARY | Dedicated audit log file with full (file, line, claim, check, resolution) table. SUMMARY stays terse. Mirrors per-phase artifact convention. | ✓ |
| Inline in 06-SUMMARY.md | Full table inline, even if SUMMARY hits 200+ lines. SC #5 wording reads literally. SUMMARY's role as narrative wrap-up gets diluted. | |
| Per-file audit comments inline + tally in SUMMARY | Each in-scope file gets a 1-line hidden HTML comment with sweep stats. SUMMARY shows tally. Scattered, not greppable, doc-edit churn. | |

**User's choice:** Separate file (06-DRIFT-AUDIT.md).
**Notes:** Captured as D-22. Becomes the 5th per-phase artifact sibling.

---

## Area D — `DOC_INVARIANTS.md` design

### Decision D.1 — Check language

| Option | Description | Selected |
|--------|-------------|----------|
| Bash one-liners (matches ROADMAP example) | All checks expressed as Bash one-liners using grep / test / wc / head. Matches ROADMAP §SC-2 example verbatim. Runs in Git Bash on Windows and on POSIX. Most portable. | ✓ |
| PowerShell one-liners | Native to Windows-first stance. Won't run in Git Bash without 'powershell -Command ...' wrapping. Re-sweep tooling Windows-only. | |
| Python one-liners (python -c '...') | Cross-shell, no shell-flavor pinning. Verbose for trivial greps. Awkward syntax for things grep handles in 5 chars. | |
| Mixed — pick the cleanest tool per check | Best per-line readability; worst portability story (re-sweep needs both Bash and PowerShell available). | |

**User's choice:** Bash one-liners.
**Notes:** Captured as D-16.

### Decision D.2 — Execution model

| Option | Description | Selected |
|--------|-------------|----------|
| Doc-of-record + manual run | DOC_INVARIANTS.md is a human-runnable reference. Each invariant is copy-pasteable. No CI, no pre-commit, no Python wrapper, no /scripts/ artifact. | ✓ |
| Doc + check-runner script (sweep-invariants.sh / .ps1) | DOC_INVARIANTS.md lists invariants AND ships with a thin runner. Single command for re-sweep; small permanent tooling artifact. Soft drift surface. | |
| Doc + pytest test | Adds a test (touches D-22 protected tests/ path; option blocks itself). | |
| Doc + git pre-commit hook | Pre-commit hook runs invariants on staged commits. v1.1 explicitly defers AUTO-02 (pre-commit hooks). | |

**User's choice:** Doc-of-record + manual run.
**Notes:** Captured as D-17. The doc IS the tool. Matches v1.1 no-tooling-additions stance.

### Decision D.3 — Invariant slate

| Option | Description | Selected |
|--------|-------------|----------|
| All 8 above | Covers Phase 4 wiring (#1-4), Phase 5 orphans (#5), historically-reverted business rule (#6), vendor-list cross-launcher consistency (#7), Phase 6's own deliverable (#8). Comfortably exceeds ≥5 floor. | ✓ |
| Core 5 (#1-5: cache + orphan) | Tightest scope; matches v1.1 drift surface exactly. Skips business-rule and self-protect invariants. | |
| Core 5 + business rule (#1-6) | Adds #6 power_cord rule but skips #7 vendor-consistency and #8 self-protect. | |
| All 8 + 1-2 you suggest | Take 8 plus invariants flagged as missing. | |

**User's choice:** All 8.
**Notes:** Captured as D-18. Invariants #1-7 verified to exit 0 against current tree by discuss-phase scout (2026-05-11). Invariant #8 (.SYNOPSIS) currently FAILs — it's Phase 6's own deliverable; planner must order D-05 help-block task before SC #4 verification gate. Captured as D-19.

---

## Claude's Discretion

Captured in CONTEXT.md § "Claude's Discretion" (under `<decisions>`):

- Exact placement of `<#...#>` block in `run.ps1` (above-vs-below RU header).
- Exact wording of trim pointers in RUN_PATHS_AND_IO_LAYOUT.md and ONE_BUTTON_RUN.md.
- Exact phrasing of the 3 surgical-patch replacement sentences (D-02 / D-03), bounded by Phase 5 D-05/D-06 vocabulary.
- DOC_INVARIANTS.md format (numbered subsections vs. single table); both satisfy SC #2.
- Commit subject prefix per task (`docs(06)` vs `chore(06)`); D-21 sets the default.
- "How to run them all" footer in DOC_INVARIANTS.md (composite invocation vs. instructions to run each line in sequence).

---

## Deferred Ideas

Captured in CONTEXT.md `<deferred>`:

- Broader 7-file `/gsd-map-codebase` refresh (closes Area A overflow + Area C volatile-counts overflow). Right milestone: v1.2.
- `spec_classifier/CLAUDE.md` and `spec_classifier/README.md` drift sweeps — same `/gsd-map-codebase` refresh.
- Translation of `run.ps1:1-13` Russian header to English — exempt under D-18; reopen at a future EN-only hygiene milestone.
- Pre-commit hook integration of DOC_INVARIANTS.md checks — AUTO-02 backlog (v2.0+).
- CI integration of DOC_INVARIANTS.md checks — depends on PLAT-01 (v2.0+).
- Sweep runner script under spec_classifier/scripts/ — D-23 explicitly rejects; reopen only if v2.0 CI demands a programmatic entry point.
- pytest test wrapping the invariants — needs D-22 carve-out; reopen at v2.x.
- DOCS_INDEX.md auto-generation from filesystem — candidate for invariant #9 in a future iteration.
- Renaming `_run_full` method in `teresa_gui.py` — Phase 5 D-03 false-positive; Phase 6 inherits.
- Volatile-count claims in IN-scope files — D-12 defers; encountered ones are removed (remove > patch heuristic), not patched.
- Adding DRIFT-05 for the surgical map patches / help block / audit log split — not done; documented adjustments captured in CONTEXT.md (mirrors Phase 5 D-04 stance).
