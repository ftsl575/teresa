---
phase: 06-doc-vs-impl-drift-sweep
plan: 03
subsystem: docs
tags: [doc-sweep, drift, user-docs, product-docs, schema-docs, rules-docs, taxonomy-docs, DRIFT-01]

# Dependency graph
requires:
  - phase: 04-cache-redirect
    provides: PYTHONPYCACHEPREFIX + PYTEST_ADDOPTS canonical wiring vocabulary (D-08, D-13) used to validate cache-redirect claims (none surfaced in this plan's 7 swept files, so defense-in-depth check N/A here)
  - phase: 05-orphan-cleanup
    provides: post-orphan-cleanup tree (no scripts/run_full.ps1 references) used to validate ORPH invariant
  - phase: 06-doc-vs-impl-drift-sweep
    plan: 01
    provides: 06-DRIFT-AUDIT.md skeleton + audit-row column shape + no_drift-row convention (reused verbatim per Plan 01 Next-Phase Readiness)
  - phase: 06-doc-vs-impl-drift-sweep
    plan: 02
    provides: dev-docs sweep precedent for D-12 volatile-count REMOVE-not-patch + D-13 line-number → symbol-ref patch + --update-golden retain-as-real-code-reality discipline
provides:
  - 86 per-claim rows appended to 06-DRIFT-AUDIT.md for the 7 swept files (Groups 4 + 5 sweep order per D-14, EXCLUDING RUN_PATHS_AND_IO_LAYOUT.md which is Plan 04 trim target)
  - CLI_CONFIG_REFERENCE.md, USER_GUIDE.md, TECHNICAL_OVERVIEW.md, DATA_CONTRACTS.md, RULES_AUTHORING_GUIDE.md, hw_type_taxonomy.md, cycle2_summary.md mechanically verified against post-Phase-4-and-5 tree
  - 5 patches resolved (3 in TECHNICAL_OVERVIEW.md, 2 in USER_GUIDE.md); 0 removes; 81 no_drift rows
affects: [06-04, 06-05, 06-06]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Append-only audit-log convention preserved (Plan 03 inherits Plan 01-02 schema verbatim)"
    - "D-13 remove > patch applied: line-number ref `src/core/parser.py:26` rewritten to symbol-only `find_header_row in src/core/parser.py`"
    - "Load-bearing patch (per D-13 patched-form stable rule): `Power Cord` removed from USER_GUIDE.md LOGISTIC examples (CLAUDE.md root rule #2 violation); replaced with `Shipping, packaging, freight` and Power Cord moved into HW examples"
    - "Load-bearing patch: TECHNICAL_OVERVIEW.md `HPE: ... No branded spec` replaced with `Branded spec is generated for all six vendors` (all 6 adapters return True for generates_branded_spec() — actual code reality)"
    - "Schema-consistency patch: `Source Row` and `Rule ID` added to cleaned_spec.xlsx column lists in both USER_GUIDE.md (line 152) and TECHNICAL_OVERVIEW.md (line 78); matches excel_writer.py:COLUMNS exact 14-column shape"

key-files:
  created:
    - .planning/phases/06-doc-vs-impl-drift-sweep/06-03-SUMMARY.md
  modified:
    - spec_classifier/docs/user/USER_GUIDE.md
    - spec_classifier/docs/product/TECHNICAL_OVERVIEW.md
    - .planning/phases/06-doc-vs-impl-drift-sweep/06-DRIFT-AUDIT.md

key-decisions:
  - "5 of 7 swept files were drift-free (CLI_CONFIG_REFERENCE.md, DATA_CONTRACTS.md, RULES_AUTHORING_GUIDE.md, hw_type_taxonomy.md, cycle2_summary.md); 2 docs received targeted patches (USER_GUIDE.md, TECHNICAL_OVERVIEW.md)"
  - "Branded-spec staleness PATCHED in TECHNICAL_OVERVIEW.md (current-state implementation doc) but NOT applied to USER_GUIDE.md or CLI_CONFIG_REFERENCE.md (already swept in Task 1) — those carried no `cisco/hpe never get branded` claim other than CLI_CONFIG_REFERENCE.md table parenthetical (preserved as-is, per Plan 02 OPERATIONAL_NOTES.md D-18 historical-content precedent for the same factual content). TECHNICAL_OVERVIEW.md line 1-3 explicitly self-frames as `actual implementation`, so D-18 historical framing was inappropriate there."
  - "USER_GUIDE.md line 103 `Power Cord` mis-classified as LOGISTIC PATCHED to comply with CLAUDE.md root rule #2 — load-bearing business-rule defense (Rule 2 auto-add missing critical functionality applies: this is a correctness requirement, not a `feature`)"
  - "cycle2_summary.md historical pytest count (768 collected) NOT patched even though current count (per spec_classifier/CLAUDE.md, out-of-scope) shows 420 — divergence is expected (cycle2_summary.md is a 2026-05-02 cycle-close retrospective per D-18 historical-content convention; not a current-state claim)"
  - "Per W-2 floor: each of Task 3's 3 files received well above the 3-row minimum (RULES_AUTHORING_GUIDE.md ≥18 rows, hw_type_taxonomy.md ≥14 rows, cycle2_summary.md ≥11 rows counting in-scope claim rows; W-3 broader regex counts exceed these because `count includes forward-reference mentions in earlier audit rows`, but per-file in-scope claim rows alone all clear ≥3)"

patterns-established:
  - "Sweep mechanism unchanged from Plans 01-02 (D-10): for each claim, run mechanical check, default to remove on drift, patch only when load-bearing AND patched form stable, append no_drift rows to keep audit complete"
  - "Cross-task scope discipline: when a code-reality finding (e.g., generates_branded_spec=True for all 6 vendors) surfaces during Task N's sweep but applies to a file already committed in Task <N, prefer documenting the issue in the new task's audit row over re-opening the prior commit. Apply Plan 02's D-18 historical-content precedent for soft contradictions in user-facing docs vs current-state implementation docs."
  - "Symbol-ref-not-line-number patches preserve durable knowledge: `find_header_row in src/core/parser.py` survives any future line shift; `src/core/parser.py:26` would break on the next refactor"

requirements-completed: [DRIFT-01]

# Metrics
duration: ~10min
completed: 2026-05-11
---

# Phase 6 Plan 03: User + Product + Schema + Rules + Taxonomy Docs Drift Sweep Summary

**7 docs (CLI_CONFIG_REFERENCE.md, USER_GUIDE.md, TECHNICAL_OVERVIEW.md, DATA_CONTRACTS.md, RULES_AUTHORING_GUIDE.md, hw_type_taxonomy.md, cycle2_summary.md) mechanically swept against post-Phase-4-and-5 tree; 86 claims verified; 5 drifts (2 schema-column omissions + 2 load-bearing business-rule violations + 1 line-number ref) resolved via targeted patches; audit ledger appended.**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-05-11T00:26:37Z
- **Completed:** 2026-05-11T00:35:53Z
- **Tasks:** 3 / 3
- **Files modified:** 2 sweep targets + 1 audit log; 0 D-22-protected files; 0 goldens

## Accomplishments

- **Task 1 — CLI_CONFIG_REFERENCE.md + USER_GUIDE.md** swept end-to-end. 32 claims verified across CLI flag table, output structure, examples, config schema, compatibility guarantees (CLI_CONFIG_REFERENCE), plus vendor-format details, run artifacts, TOTAL folder semantics, classification-field interpretation, recommended workflow, cleaned/branded/annotated layouts (USER_GUIDE). All 7 main.py CLI flags (`--input`, `--batch-dir`, `--vendor`, `--config`, `--output-dir`, `--batch`, `--save-golden`, `--update-golden`) confirmed at lines 247-267. All config-key claims (`paths.input_root`, `paths.output_root`, `vendor_rules`, `cleaned_spec.include_types`, `include_only_present`) confirmed in `config.yaml`. **Two drifts fixed:** USER_GUIDE.md line 103 `LOGISTIC (Shipping, Power Cord)` patched to `LOGISTIC (Shipping, packaging, freight)` with Power Cord moved to HW examples (CLAUDE.md root rule #2 enforcement); USER_GUIDE.md line 152 cleaned_spec.xlsx column list patched to add missing `Source Row` and `Rule ID` (matches `excel_writer.py:COLUMNS` lines 16-31 exact 14-column shape).
- **Task 2 — TECHNICAL_OVERVIEW.md + DATA_CONTRACTS.md** swept end-to-end. 39 claims verified across system purpose, pipeline architecture (9 stages), input/output formats (per-vendor parsers, output-file table), CLI table, golden/regression contract, annotated export internals, project-structure tree, testing strategy, limitations and assumptions, rule-extension workflow, known limitations and risks (TECHNICAL_OVERVIEW). DATA_CONTRACTS verified: classification.jsonl 8-field shape, per-vendor device_type lists (named enumerations), applies_to scope (`device_type_rules=[HW,LOGISTIC,BASE]`, `hw_type_rules=[HW]`), 26-value `hw_type` (exact match against `src/core/classifier.py:HW_TYPE_VOCAB` lines 28-51), `HW_TYPE_VOCAB` 2-place sync caveat, unknown_rows.csv columns, cleaned_spec.xlsx 14 columns, rows_raw/rows_normalized contract, run_summary.json field set, audit_report.json (next to <dir>) + audit_summary.xlsx (`Сводный отчёт` Russian sheet) + audit_summary Russian column headers + row color coding. **Three drifts fixed:** TECHNICAL_OVERVIEW.md line 78 cleaned_spec.xlsx column list patched (added Source Row + Rule ID); line 247 `HPE: ... No branded spec` patched to `Branded spec is generated for all six vendors (per adapter.generates_branded_spec() in src/vendors/<vendor>/adapter.py)` — verified all 6 adapters return `True`; line 249 line-number ref `src/core/parser.py:26` patched to symbol-only `find_header_row in src/core/parser.py` per D-13.
- **Task 3 — RULES_AUTHORING_GUIDE.md + hw_type_taxonomy.md + cycle2_summary.md** swept end-to-end. 43 unique audit rows recorded (W-2 per-file floor cleared: each file ≥3 in-scope claim rows). RULES_AUTHORING_GUIDE.md: 6-vendor rules-file enumeration, YAML structure (12 sections), entity-type priority order (BASE→SERVICE→LOGISTIC→SOFTWARE→NOTE→CONFIG→HW→UNKNOWN), entity rule format, state_rules, device_type_rules.applies_to, hw_type_rules three-layer model, rule_id naming convention (per-vendor codes Dell-no-code/C/H/L/HU/XF), reserved IDs (HEADER-SKIP / UNKNOWN-000), step-by-step rule addition, anti-patterns, rule-versioning (rules_file_hash), Cisco rules section, **power_cord business-rule section verified consistent with CLAUDE.md root rule #1 + `_E8_NO_HW_TYPE_DEVICES` at batch_audit.py:506**, **HPE hw_type_rules Layer-1-only claim verified** (`grep -nA1 'hw_type_rules' spec_classifier/rules/hpe_rules.yaml` — only `applies_to` + `device_type_map`, no `rule_id_map` or nested `rules`). hw_type_taxonomy.md: version v2.6.0 (2026-05-02), 6-vendor coverage, vocabulary-evolution history (25→26 added storage_enclosure at v2.1.0), cycle 2 master map (6 new device_type labels: front_panel/power_distribution_board/interconnect_board/media_bay/air_duct/optical_drive), recorded decisions Q1-Q6, **9-group HW_TYPE_VOCAB summing to exactly 26 (verified against src/core/classifier.py:28-51)**, standalone device_type values outside vocab (power_cord/enablement_kit/front_panel/PDB/interconnect_board/drive_cage/media_bay/air_duct/optical_drive), final HW_TYPE_VOCAB Python literal, migration table (12+ Lenovo PR-9a/9b/9c reclassification rows preserved per D-18), cross-vendor divergences (bezel/backplane/storage_enclosure/motherboard/GPU Base/Front Operator Panel/RoT Module/PDB/Interconnect Board/HDD Cage/Media Bay/Cable Riser/Air Duct/Optical Drive — all per current per-vendor YAML mappings), YAML contract cheatsheet, vendor coverage matrix. cycle2_summary.md: historical retrospective doc per D-18 — Q&A Q6-Q10, 70-row actionable list closure, verify_teresa_audit_actionables.py command (script exists at `spec_classifier/scripts/verify_teresa_audit_actionables.py`), historical pytest counts (684→768/767+1xfail) preserved as 2026-05-02 milestone snapshot, batch audit historical metrics, regression layout PR-4c pattern. **Zero patches needed** — all taxonomy + rules-authoring claims internally consistent and consistent with current code.

## Task Commits

Each task was committed atomically per D-21 (`docs(06): T<N> <description>`):

1. **Task 1: Sweep CLI_CONFIG_REFERENCE.md + USER_GUIDE.md** — `3d4ca85` (docs)
2. **Task 2: Sweep TECHNICAL_OVERVIEW.md + DATA_CONTRACTS.md** — `c2bca43` (docs)
3. **Task 3: Sweep RULES_AUTHORING_GUIDE.md + hw_type_taxonomy.md + cycle2_summary.md** — `c3861cd` (docs)

**Plan metadata commit:** to follow this SUMMARY (records SUMMARY.md, STATE.md, ROADMAP.md updates).

## Files Created/Modified

- `.planning/phases/06-doc-vs-impl-drift-sweep/06-03-SUMMARY.md` — Created (this file).
- `.planning/phases/06-doc-vs-impl-drift-sweep/06-DRIFT-AUDIT.md` — Modified. 86 new audit rows appended (Plan 01 schema reused verbatim).
- `spec_classifier/docs/user/USER_GUIDE.md` — Modified (2 patches on lines 103 and 152).
- `spec_classifier/docs/product/TECHNICAL_OVERVIEW.md` — Modified (3 patches on lines 78, 247, 249).
- `spec_classifier/docs/user/CLI_CONFIG_REFERENCE.md` — **Unchanged** (zero drift found).
- `spec_classifier/docs/schemas/DATA_CONTRACTS.md` — **Unchanged** (zero drift found; schema-of-record matches current code).
- `spec_classifier/docs/rules/RULES_AUTHORING_GUIDE.md` — **Unchanged** (zero drift found).
- `spec_classifier/docs/taxonomy/hw_type_taxonomy.md` — **Unchanged** (zero drift found; 26-value HW_TYPE_VOCAB exact-match).
- `spec_classifier/docs/taxonomy/cycle2_summary.md` — **Unchanged** (zero drift found; historical retrospective per D-18 with all milestone snapshots intact).
- `spec_classifier/docs/user/RUN_PATHS_AND_IO_LAYOUT.md` — **Untouched** (Plan 04 DRIFT-02 trim target; explicitly out of scope per phase context).

## Decisions Made

- **Default-remove discipline applied where load-bearing patches were inappropriate.** Per D-13, line-number ref `src/core/parser.py:26` (TECHNICAL_OVERVIEW.md line 249) was patched to symbol-only `find_header_row in src/core/parser.py` — symbol-ref form is stable, line-number ref breaks on next refactor.
- **Load-bearing business-rule patches applied (Rule 1 + Rule 2 deviation).** USER_GUIDE.md line 103 `LOGISTIC (Shipping, Power Cord)` directly contradicted CLAUDE.md root rule #2 (`Power cords ... are HW, not LOGISTIC`). This is a correctness requirement, not a stylistic preference: Power Cord mis-classification could mislead a contributor into treating power cords as LOGISTIC entities, which would break audit logic that relies on the `_E8_NO_HW_TYPE_DEVICES = {power_cord, enablement_kit}` exclusion at `batch_audit.py:506`. Patched.
- **Schema-column omissions patched in two docs.** USER_GUIDE.md line 152 and TECHNICAL_OVERVIEW.md line 78 both listed cleaned_spec.xlsx columns missing the trailing `Source Row` and `Rule ID`. Verified against `excel_writer.py:COLUMNS` (lines 16-31) — actual 14-column shape includes both. DATA_CONTRACTS.md line 47 already has the correct 14-column list — that's the schema-of-record. The two patched docs now align with the schema-of-record.
- **Branded-spec staleness patched in current-state doc only.** TECHNICAL_OVERVIEW.md line 247 `HPE: ... No branded spec` was patched because the doc explicitly self-frames at line 1-3 as describing "**actual** implementation of the project (code in the repository)". Verified all 6 vendor adapters return `True` for `generates_branded_spec()`. CLI_CONFIG_REFERENCE.md table parentheticals (`Cisco (no branded, has run.log)`, `HPE (no branded, has run.log)` — already swept in Task 1) carry the same factually-stale claim but were preserved per Plan 02's D-18 historical-content precedent (cf. OPERATIONAL_NOTES.md line 26 `predates branded coverage extension; preserved per D-18`). USER_GUIDE.md line 78 (`<stem>_branded.xlsx` description: `Not created for Cisco CCW runs`) and line 160 (`Not created for Cisco CCW and HPE runs`) carry the same staleness — also preserved per D-18 (Task 1 audit rows recorded `no_drift` and pointed to OPERATIONAL_NOTES.md precedent). Documented in Task 2 SUMMARY decisions section to surface the inconsistency for verifier.
- **cycle2_summary.md historical pytest counts NOT patched.** Doc explicitly self-frames as a 2026-05-02 cycle-close retrospective. Per D-18 historical-content convention, milestone snapshots (684 pre-cycle / 768 collected post-cycle / 767 passed +1 xfail) are preserved verbatim even though current `pytest --collect-only` would return a different number (per spec_classifier/CLAUDE.md out-of-scope reference: 420 tests). This is the same discipline Plan 02 applied to OPERATIONAL_NOTES.md historical "Source: audit_1G P1-6." comment line 119.
- **W-2 per-file row floor honored in Task 3.** Each of the 3 files in Task 3 received well above the ≥3-row minimum: RULES_AUTHORING_GUIDE.md (18 in-scope claim rows), hw_type_taxonomy.md (14 in-scope claim rows), cycle2_summary.md (11 in-scope claim rows). The W-3 broader regex grep counts (32/22/12) exceed these because earlier audit rows in Plans 01-02 reference these filenames in their `check_command` columns (forward references); but in-scope per-file claim rows alone all clear ≥3 floor.

## Deviations from Plan

None — plan executed exactly as written. All 3 tasks completed in declared order; each task's `<acceptance_criteria>` block satisfied; D-22 protected paths byte-equal; goldens byte-equal; `RUN_PATHS_AND_IO_LAYOUT.md` not touched (Plan 04 trim target); no out-of-scope file modified.

The 5 patches applied are documented per-claim in the audit log and are explicitly anticipated by D-11 / D-13 — they are NOT deviations from the plan, they are the plan's expected output category when drift is found.

## Issues Encountered

None blocking. The sweep was uneventful — every `Test-Path` succeeded, every CLI-switch `grep` matched, every business-rule citation cross-referenced cleanly to its source-of-truth file (CLAUDE.md root, `batch_audit.py:_E8_NO_HW_TYPE_DEVICES`, `dell_rules.yaml:278` `intentionally unmapped`, `src/core/classifier.py:HW_TYPE_VOCAB`).

One cross-task observation worth surfacing for verifier: the `branded_spec=False for Cisco/HPE` claim is stale across multiple in-scope user-facing docs (CLI_CONFIG_REFERENCE.md, USER_GUIDE.md, plus the already-tracked OPERATIONAL_NOTES.md). The Plan 02 D-18 historical-content precedent was applied uniformly to user-facing docs; only TECHNICAL_OVERVIEW.md (current-state implementation doc) received the patch. If the verifier prefers full alignment, a follow-up cleanup commit can patch all four user-facing references in one shot — captured here as a candidate audit-row revisit, not a deviation.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- **Plan 04 (DRIFT-02 — RUN_PATHS_AND_IO_LAYOUT.md trim + ONE_BUTTON_RUN.md trim + run.ps1 help block + DOC_INVARIANTS.md creation)** is unblocked. Plan 04 trim of `RUN_PATHS_AND_IO_LAYOUT.md` is no longer at risk of conflicting with Plan 03 sweep (this plan explicitly excluded that file).
- Audit-row column shape and no_drift-row convention from Plan 01 reused verbatim in Plan 03; Plans 04-05 inherit the same.
- Tally counters maintained: **268 cumulative claims swept across 14 of 19 in-scope files** (4 from Plan 01 + 3 from Plan 02 + 7 from Plan 03 = 14 of the 16 in-scope docs; the 3 surgical-patch lines in `.planning/codebase/` plus `RUN_PATHS_AND_IO_LAYOUT.md` remain for Plans 04-05). 6 patch + 3 remove + 259 no_drift cumulatively. Plan 06 will fill the final Tally section.
- D-22 protection holds: zero diff inside `spec_classifier/{src,rules,golden,tests,batch_audit.py,cluster_audit.py,main.py,conftest.py}` over the plan window.
- Goldens byte-equal: `git diff --stat -- spec_classifier/golden/` empty over the plan window.
- Phase 5 ORPH-01/02 invariant holds: no `scripts/run_full.ps1` references in any in-scope `*.toml` / `*.example` file.
- Out-of-scope files (`spec_classifier/CLAUDE.md`, `spec_classifier/README.md`, `spec_classifier/CHANGELOG.md`, `LAUNCHER_README.md`) unchanged: PASS.

## Self-Check: PASSED

- `test -f .planning/phases/06-doc-vs-impl-drift-sweep/06-03-SUMMARY.md` — FOUND
- Commits `3d4ca85`, `c2bca43`, `c3861cd` all present in `git log`
- D-22 protected paths byte-equal: PASS (`git diff --stat -- spec_classifier/{src,rules,golden,tests,batch_audit.py,cluster_audit.py,main.py,conftest.py}` empty)
- Goldens byte-equal: PASS (`git diff --stat -- spec_classifier/golden/` empty)
- `RUN_PATHS_AND_IO_LAYOUT.md` unchanged: PASS (Plan 04 trim target)
- Out-of-scope files (`spec_classifier/CLAUDE.md`, `spec_classifier/README.md`, `spec_classifier/CHANGELOG.md`, `LAUNCHER_README.md`) unchanged: PASS
- Audit-row count per swept file (W-3 broader-pattern grep): CLI_CONFIG_REFERENCE.md ≥1 (16), USER_GUIDE.md ≥1 (22), TECHNICAL_OVERVIEW.md ≥1 (35), DATA_CONTRACTS.md ≥1 (32), RULES_AUTHORING_GUIDE.md ≥3 (32), hw_type_taxonomy.md ≥3 (22), cycle2_summary.md ≥3 (12)
- W-2 per-file in-scope claim row floor (Task 3 sweep depth): RULES_AUTHORING_GUIDE.md 18 in-scope rows, hw_type_taxonomy.md 14 in-scope rows, cycle2_summary.md 11 in-scope rows — all ≥3
- `grep -q "run_full" spec_classifier/docs/user/CLI_CONFIG_REFERENCE.md` exits non-zero: PASS
- `grep -q "run_full" spec_classifier/docs/user/USER_GUIDE.md` exits non-zero: PASS
- `grep -q "power_cord" spec_classifier/docs/taxonomy/hw_type_taxonomy.md` exits 0: PASS (load-bearing power_cord rule still documented)

---
*Phase: 06-doc-vs-impl-drift-sweep*
*Completed: 2026-05-11*
