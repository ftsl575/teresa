---
gsd_state_version: 1.0
milestone: v1.2
milestone_name: Output structure reorganization
status: executing
stopped_at: Phase 9 context gathered
last_updated: "2026-06-07T18:58:00.000Z"
last_activity: 2026-06-07 -- Phase 09 Plan 01 (WR-01 vendor-detector dedup) complete
progress:
  total_phases: 3
  completed_phases: 2
  total_plans: 9
  completed_plans: 7
  percent: 78
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-06-07)

**Core value:** The classifier produces correct, deterministic, audited artifacts for every supported vendor. Everything else is plumbing.
**Current focus:** Phase 09 — output-manifest-full-suite-verification

## Current Position

Phase: 09 (output-manifest-full-suite-verification) — EXECUTING
Plan: 2 of 3
Status: Executing Phase 09
Last activity: 2026-06-07 -- Plan 09-01 complete (WR-01 vendor-detector dedup, commit d54247b)

## Performance Metrics

**Velocity:**

- Total plans completed: 15 (v1.1)
- Average duration: —
- Total execution time: 0.0 hours (v1.1)

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 4. Cache Redirect | 0 | — | — |
| 5. Orphan Cleanup | 0 | — | — |
| 6. Doc-vs-Impl Drift Sweep | 0 | — | — |
| 04 | 3 | - | - |
| 06 | 6 | - | - |
| 07 | 3 | - | - |
| 09 P01 | 12min | 2 tasks | 4 files |
| 08 P01 | 6min | 2 tasks | 1 files |
| 08 | 3 | - | - |

**Recent Trend:**

- Last 5 plans: — (v1.1 not started)
- Trend: — (no v1.1 data yet)

*Updated after each plan completion*

**v1.0 history (preserved for trend continuity):**

| Phase 01-hygiene P01 | 45 | 3 tasks | 17 files |
| Phase 01-hygiene P02 | 60 | 1 tasks | 2 files |
| Phase 01-hygiene P03 | 10 | 3 tasks | 1 files |
| Phase 02-docs P01 | 25 | 3 tasks | 2 files |
| Phase 02-docs P02 | 7min | 2 tasks | 3 files |
| Phase 02-docs P03 | 12m | 1 tasks | 1 files |
| Phase 02-docs P04 | 15 | 2 tasks | 1 files |
| Phase 02-docs P02-05 | 180 | 3 tasks | 15 files |
| Phase 02-docs P02-06 | 30 | 3 tasks | 3 files |
| Phase 03-workflow P01 | 5 | 3 tasks | 13 files |
| Phase 03-workflow PP02 | 9 | 6 tasks tasks | 6 files files |
| Phase 03-workflow P03 | 25 | 7 tasks | 6 files |
| Phase 05 P01 | ~4 min | 5 tasks | 5 files |
| Phase 06-doc-vs-impl-drift-sweep P02 | 5min | 3 tasks | 4 files |
| Phase 06 P03 | 10min | 3 tasks | 3 files |
| Phase 06 P04 | ~6min | 3 tasks | 4 files |
| Phase 06 P05 | ~1min | 1 task | 3 files |
| Phase 06 P06 | ~5min | 3 tasks | 3 files |
| Phase 07 P02 | 3min | 2 tasks | 1 files |
| Phase 08 P02 | ~4min | 2 tasks | 1 files |
| Phase 08 P03 | 8min | 3 tasks | 2 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Init: Cleanup before classification improvements (hygienic base before iterating on rules).
- Init: Keep both `CLAUDE.md` files; deduplicate overlap (root = thin pointer, deep ref stays in `spec_classifier/`).
- Init: Strip `C:\Users\G\` username only; do not de-Windowize launchers.
- Init: Honor "do not fix" tech debt — `power_cord=None`, Excel-reading audit, `core/parser.py` Dell-specificity, `HW_TYPE_VOCAB` duplication, YAML rule order.
- [Phase 3]: WF-01 + WF-02 complete; D-20 7-step verification gate PASS; v1.0 cleanup-and-workflow milestone closed (10/10 requirements Complete: HYG-01..03, DOC-01..05, WF-01..02).
- [Phase 3]: Auto-mode chain pipeline auto-approved Task 3.4 diff-review (human-verify) checkpoint per orchestrator <auto_mode> binding instruction; auth-gate / human-action checkpoints would still halt — none in this plan.
- [Phase 3]: Phase 3 SHA back-fill (Task 3.7) became a no-op because Plans 03-01 + 03-02 each self-committed atomic + plan-metadata commits BEFORE the gate plan ran; only the wrap-up commit's own self-reference remains as <sha-pending> (intentional, acceptable per Task 3.7 acceptance criteria).
- [v1.1 Init]: Sequential plan execution required (Phase 4 → 5 → 6). Plan 2 (ORPH-01) rewrites `pyproject.toml:5` to wording only true post-Phase-4; Plan 3 sweep relies on post-Phase-4-and-5 tree. Parallel execution unsound.
- [v1.1 Init]: `DOC_INVARIANTS.md` (DRIFT-03) is in scope despite "no creation" framing — tooling/meta-doc materializing the v1.0 retrospective lesson. Domain content (per-vendor docs) remains v1.2 scope.
- [v1.1 Init]: `load_config_with_local()` regex-parser consolidation explicitly out of scope; Phase 4 extends the existing 4+-site regex pattern to `temp_root` only. Helper consolidation deferred to its own milestone (CONCERNS.md § IMPORTANT).
- [v1.1 Init]: Roadmap created 2026-05-10 — 3 phases (4 Cache Redirect, 5 Orphan Cleanup, 6 Doc-vs-Impl Drift Sweep); 12/12 requirements mapped, no orphans.
- [Phase 5]: Phase 5 closed: orphan refs purged, .cursor/ + teresa.zip removed, ROADMAP §SC-1 grep tightened to *.toml/*.example scope; Check 5 dispositioned as substantive PASS / literal FAIL (plan-author casing slip, file byte-equal to phase-start)
- [Phase 6 / Plan 01]: 4 root/index docs (README.md, CLAUDE.md, CONTRIBUTING.md, DOCS_INDEX.md) mechanically swept; 108 claims verified (31+25+27+25); zero drift found; all 4 sweep targets byte-equal; 06-DRIFT-AUDIT.md initialized with skeleton + 108 no_drift rows; D-22 paths byte-equal; goldens byte-equal.
- [Phase ?]: Plan 06-02: dev-docs sweep found 4 drifts in 71 claims (1 patch line-num ref, 3 removes volatile counts); --update-golden retained per real code reality
- [Phase ?]: [Phase 6 / Plan 03]: 7 user/product/schema/rules/taxonomy docs swept; 86 claims verified (5 patches: 2 schema-column omissions in USER_GUIDE+TECHNICAL_OVERVIEW, 2 business-rule violations USER_GUIDE Power Cord+TECHNICAL_OVERVIEW HPE no-branded, 1 line-number ref); 0 removes; 81 no_drift; D-22 byte-equal; goldens byte-equal
- [Phase 6 / Plan 04]: DRIFT-02 closed end-to-end — run.ps1 now ships .SYNOPSIS/.DESCRIPTION/5 .PARAMETER/6 .EXAMPLE help block (RU header at lines 1-13 SHA-frozen, comments-only edit, B-3 zero-deletion gate PASS); ONE_BUTTON_RUN.md trimmed 54→50 with "run .\\run.ps1 -?" pointer (Phase 4 CACHE-04 -NoClean+clean.ps1 co-occurrence preserved); RUN_PATHS_AND_IO_LAYOUT.md trimmed 281→264 with top pointer to run.ps1 -? + ONE_BUTTON_RUN.md, PYTHONPYCACHEPREFIX claim PATCHED to Phase 4 D-13 vocabulary (run.ps1 + teresa_gui co-mention + PYTEST_ADDOPTS partner); 44 sweep rows appended (16 ONE_BUTTON_RUN + 28 RUN_PATHS, 1 patch + 43 no_drift); D-22 byte-equal; goldens byte-equal; DOC_INVARIANTS #8 prerequisite landed.
- [Phase 6 / Plan 05]: DRIFT-04 closed — 3 surgical line patches landed in .planning/codebase/ (STACK.md:79 + INTEGRATIONS.md:55,150). Both stale PYTHONPYCACHEPREFIX bullets replaced with Phase 5 D-05/D-06 canonical defense-in-depth vocabulary (PYTHONPYCACHEPREFIX + PYTEST_ADDOPTS env vars set by run.ps1 AND teresa_gui.py from config.local.yaml::temp_root); INTEGRATIONS.md:55 hardcoded `C:\\Users\\G\\Desktop\\temporary` username leak replaced with `C:\\Users\\<USERNAME>\\Desktop\\temporary` per HYG-01 placeholder convention (v1.0 HYG-01 retroactive miss-fix). 3 patch rows appended to 06-DRIFT-AUDIT.md using N-2-fixed column shape (bare check_command + parenthesized pre-state context in resolution column). Single atomic `docs(06): T1 ...` commit per planner discretion (D-21 borderline doc-class call). D-22 byte-equal; goldens byte-equal. Commit: 44447d3.
- [Phase 6 / Plan 06]: DRIFT-03 + DRIFT-04 closed end-to-end. T1 cffcc38 created spec_classifier/docs/dev/DOC_INVARIANTS.md (128 lines, 8 mechanical Bash-one-liner invariants per D-15..D-20: PYTHONPYCACHEPREFIX in run.ps1+teresa_gui.py, PYTEST_ADDOPTS, clean.ps1, no run_full orphans, power_cord intentionally unmapped, six vendors, .SYNOPSIS help block); T2 7b84b65 added DOC_INVARIANTS.md entry to spec_classifier/docs/DOCS_INDEX.md (1:1 contract preserved, role-grouped placement after OPERATIONAL_NOTES.md); T3 c762167 finalized 06-DRIFT-AUDIT.md Tally (369 claims swept / 356 no_drift / 10 patch / 3 remove / 18 distinct files; conceptual 19 = 16 in-scope + 3 surgical lines reconciled inline since INTEGRATIONS.md contributes 2 of 3 surgical lines from one file) + appended SC #1 + SC #4 verification subsection (8/8 invariants exit 0; 12 patch-row spot-checks PASS; SC #3 line-count gates re-confirmed 50<54 and 264<281; D-25 pytest 774 passed + 1 xfailed + 0 skipped in 23.65s — REAL DATA outcome (a) per N-1 distinction since INPUT populated for all 6 vendors; D-22 + goldens byte-equal across full phase window c615637..HEAD). Phase 6 metadata commit c48bed5. ROADMAP §SC-1, §SC-2, §SC-3, §SC-4, §SC-5 all PASS. v1.1 milestone ready for /gsd-verify-work 6 + /gsd-complete-milestone.
- [Phase 8 / Plan 01]: batch_audit.py re-pointed at Phase-7 buckets — reads `*_annotated.xlsx` strictly from `output_root/SPLIT` (is_dir guard, no whole-tree fallback; D-02), writes `<stem>_annotated_audited.xlsx` to `output_root/AUDIT/<vendor>/<spec>` via `relative_to(SPLIT_root)` mirror + mkdir-parents (no rmtree; D-03/D-04), `audit_report.json` + `audit_summary.xlsx` → `AUDIT/` root (D-05). Dead `{vendor}_run`/`hp_run`/`-TOTAL` matchers removed; `/{vendor}/` retained (D-07). `_generate_human_report` :924 untouched. `SPLIT_root`/`AUDIT_root` derived inline in `main()` (D-01, no launcher edits). Routing-only; goldens byte-equal. Commits 74c7dda, 83f2eb7. Full pytest gate deferred to Plan 08-02 (Wave 2).
- [Phase 6 / Plan 06]: Deferred bookkeeping note — .planning/ROADMAP.md Progress table shows Phase 4 as "0/3 | Planning complete" but Phase 4 actually completed 3/3 plans (commits 46c88d2/9cf94dd/f61d996/8eb8302; 04-VERIFICATION.md exists). Out of scope for Plan 06-06 per executor SCOPE BOUNDARY rule; tracked in .planning/phases/06-doc-vs-impl-drift-sweep/deferred-items.md for v1.1 milestone-close cleanup.
- [Phase ?]: [Phase 8 / Plan 02]: cluster_audit.py re-pointed at Phase-7/8 buckets - dual-bucket read (AUDIT audited + SPLIT annotated, is_dir-guarded, prefer-audited dedup preserved; D-02/D-06); cluster_summary.xlsx + audit_report.json cluster-merge target AUDIT/ root so json_path.exists() finds batch_audit's file (D-05). Routing-only; _detect_vendor_from_path + clustering untouched; goldens byte-equal. Commits 68483f6, d45fe70.
- [Phase 9 / Plan 01 WR-01]: detect_vendor_from_path extracted into run_manager.py as pure (path, known_vendors)->vendor; both local copies deleted; D-13 gate: exactly 3 divergences (ccw alias, match mechanism, WARN print), no fourth; D-11: known_vendors required param, no None default, callers resolve and pass; D-14: old _run/ccw_export cluster test assertions removed, suite realigned to SPLIT/<vendor>/ layout; 776 passed/1 xfailed/0 skipped.
- [Phase 8 / Plan 03]: batch_audit + cluster_audit path/layout tests realigned to the Phase-7/8 buckets — TestDetectVendorFromPath asserts SPLIT/<vendor>/<spec>/ (hp_run alias-removed case now asserts unknown; alias NOT re-added); TestRealBugClassification + cluster write_cluster_summary read audit_report.json/cluster_summary.xlsx from AUDIT/ root; _collect_xlsx_files + load_candidate_rows fixtures relocated to AUDIT/ (audited) + SPLIT/ (annotated), the latter 5 tests beyond the plan's enumerated interfaces (Rule 3 blocking, same path-class, no scope creep, no assertion intent changed). cluster_audit._detect_vendor_from_path tests left byte-unchanged (function not modified by Phase 8). Full suite 774 passed / 1 xfailed / 0 skipped within skip-gate; goldens byte-equal; no --update-golden; no production code touched. SC#4 / TEST-01 met for ROUTE-03 + ROUTE-04. Commits 4c90a4e, ced0fbc.

### Pending Todos

None yet.

### Blockers/Concerns

Load-bearing exclusions carried from `.planning/codebase/CONCERNS.md` BLOCKER section. v1.2 edits `main.py`, `run_manager.py`, `batch_audit.py`, `cluster_audit.py` **for output-path routing only** — none of these load-bearing behaviors may change:

- `power_cord` `hw_type=None` — recovery commit `c3c7cb6` exists; do not "fix".
- `spec_classifier/src/core/parser.py` is Dell-specific — out of scope; not touched by routing.
- `spec_classifier/batch_audit.py` reads Excel — v1.2 changes only WHERE it reads/writes (SPLIT→AUDIT), not THAT it reads Excel. Do not refactor the Excel-reading design.
- YAML rule order is load-bearing — never sort or reorder rule blocks.
- `HW_TYPE_VOCAB` duplicated across `classifier.py` and `batch_audit.py` — tracked, not touched by routing.

**v1.2 phase-gate constraints (apply every phase):**

- **D-22 LIFTED for v1.2:** routing edits to `main.py`, `run_manager.py`, `batch_audit.py`, `cluster_audit.py` are in scope. (The v1.1 protected-path freeze does not apply.) Edits must stay routing-only — no classification/normalization/audit logic changes.
- Goldens byte-equal: all `spec_classifier/golden/*_expected.jsonl` fixtures stay byte-equal. **No `--update-golden` in v1.2.** Files move; content is not rewritten.
- Fix tests, not goldens: path/layout assertions that break are updated to the new `<bucket>/<vendor>/<spec>/` structure.
- No content changes: no column trimming, translation, or new documents. Single content-adjacent change is the `branded` → `Коммерческое предложение_<spec>.xlsx` filename rename.
- Pytest skip-guard: session fails if `skipped/total > 0.50`. Each phase verification runs `pytest -q`.
- No tech-stack additions: Python 3.10, openpyxl, pandas, pyyaml, pytest only.

## Deferred Items

Items acknowledged and carried forward (v2 scope per REQUIREMENTS.md):

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Classification | CLAS-01 rule improvements, CLAS-02 new vendor onboarding | v2 | 2026-05-10 |
| Cross-Platform | PLAT-01 `run.sh`, PLAT-02 de-Windows GUI | v2 | 2026-05-10 |
| Automation | AUTO-01 CI pipeline, AUTO-02 pre-commit rule-id schema | v2 | 2026-05-10 |
| Per-vendor knowledge | VKB-01..04 (PART_NUMBERS, SHEET_LAYOUT, CATALOG_CONVENTIONS, RULES_RATIONALE) | post-v1.2 (deferred again; v1.2 is output structure) | 2026-06-07 |
| Artifact content | CONTENT-01..03 (column trimming, translation, new summary docs) | next milestone (v1.3) | 2026-06-07 |
| 3-level taxonomy spec | TAX-01..04 (paper spec, level boundaries, migration plan, entity_type fate) | v2.0 | 2026-05-10 |
| 3-level taxonomy impl | IMPL-01..04 (engine, 6 YAML, goldens regen, audit re-wire) | v2.1 | 2026-05-10 |
| Config-overlay helper | `load_config_with_local()` consolidation (4+ regex sites) | post-v1.1 | 2026-05-10 |

## Session Continuity

Last session: 2026-06-07T18:58:00.000Z
Stopped at: Completed 09-01-PLAN.md (WR-01 vendor-detector dedup)
Resume file: .planning/phases/09-output-manifest-full-suite-verification/09-02-PLAN.md

## Operator Next Steps

- `/clear`, then plan the first v1.2 phase:
  - `/gsd-discuss-phase 7` — gather context and clarify approach (recommended)
  - or `/gsd-plan-phase 7` — skip discussion, plan directly
