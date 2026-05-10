# Changelog

All notable changes are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning: [SemVer](https://semver.org/).

**Versioning policy:**
- MAJOR: breaking changes to `classification.jsonl` schema or CLI contracts.
- MINOR: new entity types, new fields in `run_summary.json`, new output files, new CLI options.
- PATCH: rule additions/fixes, test additions, documentation updates.

---

## [Unreleased]

### Changed (Phase 1 — Hygiene, 2026-05-10)
- chore(hygiene): scrubbed `C:\Users\G\` username from 17 tracked files using per-context placeholders (`<USERNAME>`, `$(HOME)`, `~/Desktop/...`); 95 replacements total. See `.planning/phases/01-hygiene/01-SUMMARY.md`.
- chore(hygiene): consolidated dual `.gitignore` (root + `spec_classifier/`) into a single root file; coverage retained.
- chore(hygiene): removed dead `commits.txt` (51 MB untracked artifact).

### Changed (Phase 2 — Docs, 2026-05-10)
- docs: translated `spec_classifier/CLAUDE.md` from Russian to English (preserving technical terms and embedded YAML/code-block sub-comments).
- docs: rewrote root `CLAUDE.md` as a thin pointer (~80–100 lines) containing the 5 critical business rules; deduplicated the E-code table, alias-table semantics, pipeline-stages section, and dev-cycle scenarios from root (they live only in `spec_classifier/CLAUDE.md` now).
- docs: archived `spec_classifier/CURRENT_STATE.md` to `.planning/archive/CURRENT_STATE-2026-05-10.md`. Live status now tracked in `.planning/STATE.md` (GSD).
- docs: refreshed `CHANGELOG.md` — unified to English; one logical change per entry; grouped by milestone.

### Added
- build(launcher): unified run scripts into `run.ps1` + PyQt6 GUI (`teresa_gui.py`) + double-click launcher (`teresa.bat`). Replaces legacy `run_audit.ps1`, `scripts/run_full.ps1`, `scripts/run_tests.ps1`. Wired Lenovo + Huawei into auto-detection (`0080f45`).
- feat(HPEAdapter): `get_extra_cols()` returns 5 HPE-specific annotated Excel columns (Config Name, Lead Time, Extended Price, Product Type, Factory Integrated)
- feat(CiscoAdapter): `get_extra_cols()` returns 2 Cisco-specific columns (line_number, service_duration_months)
- feat(batch_audit): config_name → module_name alias in `_ALIASES` dict; HPE LLM payload now carries module context (was always empty string, causing ~78% AI_MISMATCH baseline).
- feat(batch_audit): "product_#" added to SKU column detection (`_ALIASES` and `_AL`); HPE audit_summary now shows populated SKU column.
- feat(batch_audit): "config_name" added to Module Name column detection in audit_summary writer; HPE audit_summary now shows populated Module Name column.
- feat(batch_audit): E18 check — LOGISTIC rows with physical keyword (cord/cable/rail/bracket/mount/kit/rack/pdu/ups) and no device_type are now flagged.
- feat(annotated_writer): row_kind column added to annotated xlsx output ("ITEM"/"HEADER"); batch_audit HEADER guard is now functional.
- feat(tests): tests/test_batch_audit.py — ≥60 test cases covering E1–E18, known-case suppression, vendor detection, issue_color, E18 edges.
- feat(tests): tests/test_cluster_audit.py — 30 test cases covering _detect_vendor_from_path, _is_empty, _collect_xlsx_files, normalize_text, analyze_clusters, heuristic_mapping, write_cluster_summary, print_dry_run_report, build_parser.
- feat(tests): tests/test_hpe_rules_unit.py expanded — 25 parametrized device_type/hw_type cases covering all 25 unique HPE device_types.
- feat(excel_writer): cleaned_spec for HPE now includes 5 vendor extension columns: Config Name, Lead Time, Extended Price, Product Type, Factory Integrated. Dell/Cisco output unchanged.
- feat(excel_writer): Source Row and Rule ID columns added to cleaned_spec.xlsx for all vendors.
- feat(hpe_rules): note_rules: [] placeholder section added to hpe_rules.yaml (consistent with dell_rules.yaml and cisco_rules.yaml).
- feat(cluster_audit): sku_examples and module_examples columns added to cluster_summary.xlsx.
- docs: CLAUDE.md — project context file for Cowork and Claude Desktop.
- docs: prompts/ — prompt library with 8 step templates + COWORK_OPUS_FULL_AUDIT.md.

### Changed
- refactor(LenovoParser): removed positional constants `_HEADER_ROW`/`_DATA_START_ROW` and column indices; header is now located by scanning the first 30 rows for markers (Part number / Product Description / Qty / Price / Export Control); columns mapped via `col_map` (HPE-style); falls back to alternative sheets when `Quote` is missing or unheadered; `can_parse()` updated. Row-dict contract unchanged; goldens L1…L11 identical.
- refactor(LenovoAdapter): `get_source_sheet_name()` now returns the sheet name actually used by the most recent `parse()` call (no longer the hard-coded `'Quote'`). Parser additionally exports `parse_excel_with_sheet(filepath) -> (rows, header_row_index, sheet_name)`; the adapter caches `sheet_name` per instance and forwards it to `annotated_writer` so the secondary Excel read uses the same sheet (matters when falling back to `'Quote w availability'` or a renamed sheet). Before the first `parse()` call the method returns `None` (legacy `annotated_writer` behavior — sheet index 0). Test: `test_adapter_get_source_sheet_name_reflects_actual_sheet`.
- refactor(annotated_writer): `VENDOR_EXTRA_COLS` hardcoded registry removed; replaced with per-adapter `generate_annotated_source_excel(extra_cols=)` parameter sourced from `adapter.get_extra_cols()`
- refactor(VendorAdapter): `get_extra_cols()` concrete method added (default `[]`); DellAdapter inherits default
- refactor(batch_audit): `DEVICE_TYPE_MAP` constant removed — loaded dynamically from vendor YAML files via `_load_device_type_maps()` (R1)
- refactor(batch_audit): `detect_vendor_from_path()` now accepts `known_vendors` parameter; loop over config-driven list replaces hardcoded if/elif chain (R2)
- refactor(batch_audit): `--vendor choices` built dynamically from `config.yaml` vendor_rules keys (R3)
- refactor(batch_audit): E4 state-mismatch logic extracted into `E4_STATE_VALIDATORS` dict + `_check_e4()` function; no vendor-specific if/elif in `validate_row()` (R4)
- refactor(batch_audit): `LLM_SYSTEM` prompt vendor list templated via `_build_llm_system(known_vendors)` (R5)
- refactor(cluster_audit): `_load_config()` / `_get_known_vendors()` added; `_detect_vendor_from_path()` generic loop over known_vendors; `--vendor choices` dynamic (R6)
- docs: hw_type_taxonomy.md — power_cord hw_type synced to cable (device_type_map); LEGACY frozenset entries removed; annotated column count updated to 5 (added row_kind).
- docs: TESTING_GUIDE, CONTRIBUTING — HPE added (tests, golden hp1–hp8, prohibition on hpe_rules changes without golden update, src/vendors/hpe/ tree).
- docs: RUN_PATHS_AND_IO_LAYOUT — fixed CLI flags and removed phantom audit/ subdirectory.

### Changed (taxonomy refactor — PR-1 → PR-5)
- feat(taxonomy): `HW_TYPE_VOCAB` +`storage_enclosure` (PR-1, `1d0e1fc`) — 25→26 values; sync'd in `src/core/classifier.py` and `batch_audit.py`.
- fix(rules): xfusion calibration (BASE-XF-001/DT-XF-021 G-prefix; +HW-XF-008C-RAID-CARD-RISER + DT-XF-008C); dell DT-D-014-HDD anchored Label-lookahead; cisco BUNDLE_ROOT_SKU_EXCLUSIONS parser fix (PR-2, `a8eab5d`).
- feat(taxonomy users): hpe `drive_cage→backplane`; xfusion `DT-XF-022-BACKPLANE`; huawei `DT-HU-008` → `storage_enclosure`; `batch_audit._LLM_SYSTEM_BODY` +storage_enclosure +backplane +bezel +motherboard; `DEVICE_TYPE_TRUST` +storage_enclosure (PR-3, `2f327d1`).
- feat(lenovo): motherboard support (`HW-L-040 + DT-L-040` + map `motherboard:chassis`); `BASE-L-001`/`DT-L-001` negative-lookahead `^(?!7S)[A-Z0-9]{4}CTO` (XClarity FOD); HDD Type Label digit-suffix; `DEVICE_TYPE_ALIASES["motherboard"]=chassis`; `DEVICE_TYPE_TRUST` +motherboard (PR-4a, `e73538e`).
- feat(lenovo): GPU Base (`BASE-L-020`) / BlueField (`HW-L-041`) / Network Card (`HW-L-042`) / Fan Board (`HW-L-043`) / Bracket (`HW-L-044`) — 5 new HW + 5 DT rules (PR-4b, `2e9e91c`).
- feat(lenovo): Bezel (`HW-L-045-BEZEL` + `DT-L-045-BEZEL` + map `bezel:accessory`, Lenovo-local); OCP NIC interposer / PCIe switch board / FPC; `DEVICE_TYPE_ALIASES["drive_cage"]: chassis→backplane` (deferred PR-3 §7f); `DEVICE_TYPE_TRUST` +bezel; 11 Lenovo goldens; `tests/test_regression_lenovo.py` (PR-4c, `06d64c1`).
- docs(taxonomy refactor): `hw_type_taxonomy.md` v1.2.0→v2.1.0 (storage_enclosure + cross-vendor divergences section), `DATA_CONTRACTS.md` (26 values + Lenovo/xFusion/Huawei device_type lists), `USER_GUIDE.md` (vendor sections + new dt rows), `README.md` (title + Vendor Support all 6), `CLAUDE.md` (drive_cage alias + vendors), `batch_audit.py` docstring (E1-E18 counter; `DEVICE_TYPE_ALIASES` semantic note) (PR-5, this commit).

### Fixed
- fix(dell_rules): `DT-D-027-RAID` pattern expanded to cover BOSS and Storage Controller variants; resolves `device_mismatch:raid_controller→accessory` REAL_BUG from audit 30.03
- fix(.gitignore): `config.local.yaml` added to `spec_classifier/.gitignore`
- fix(.gitignore): outer `.gitignore` rewritten as clean UTF-8 LF (was mixed UTF-16LE with NUL bytes)
- fix(taxonomy P1-7→PR-recovery): power_cord hw_type was briefly mapped to `cable` then restored to `None` per business rule. Final state: `device_type=power_cord`, `hw_type=None`. Source: `c3c7cb6 fix(taxonomy): restore power_cord hw_type=None`. Removed power_cord→cable from all 3 vendor YAML device_type_maps, batch_audit DEVICE_TYPE_MAP, 11 golden files (27 rows), 5 unit test files. Added `_E8_NO_HW_TYPE_DEVICES` exclusion set in batch_audit.py to suppress false E8 on power_cord/enablement_kit rows. See `spec_classifier/CLAUDE.md` § Business Rules.
- fix(taxonomy P1-7): hw_type_rules.applies_to narrowed from [HW, BASE] to [HW] in all three vendor YAML files and hw_type_taxonomy.md (code was correct, taxonomy was wrong).
- Cisco NXK-AF-PE 'Dummy PID Airflow' → CONFIG (CONFIG-C-001 extended to cover all Dummy PID rows; HW-C-021-AIRFLOW and DT-C-021-AIRFLOW removed).
- Dell E16 suppressed for 412-AASK and 470-BCHP (NIC/BOSS blank fillers, not drive bay).
- E14: removed the `airflow selection` token from the pattern (Cisco Dummy PID Airflow → CONFIG, not blank_filler). SKU-exclusion for NXK-AF-PE (Dummy PID Airflow → intentionally CONFIG without device_type).
- Cisco C-RFID-1R: device_type management → accessory (RFID tag — physical label, not management).
- Dell "No Bezel", "No HBM", "No Quick Sync", "No Systems Documentation" → CONFIG (CONFIG-NOBEZEL-001, CONFIG-NOHBM-001, CONFIG-NOQUICKSYNC-001, CONFIG-NODOC-001).
- Dell DT-D-031-NO-BEZEL removed (was an erroneous fix from plan 2).
- Cisco CAB-GUIDE-1RU → HW/accessory (HW-C-024-CAB-GUIDE, DT-C-015-CAB-GUIDE).
- Dell 631-AACK "No Systems Documentation" → CONFIG (removed Documentation token from LOGISTIC-001, removed LOGISTIC-002).
- device_type mismatches: HPE proliant catch-all (BASE-H-DT-001 → BASE-H-DT-999); Dell heatsink/chassis/bezel/backplane/fan_foam classification order; all-vendors power_cord missing hw_type (E8+E9); Dell BOSS-N1 device_type (DT-D-033-BOSS-N1); Cisco M2USB → storage_ssd (DT-C-011-M2USB-SSD).
- fix(batch_audit): E6 false positive — added "BASE" to allowed entity set; BASE rows with device_type set by BASE-*-DT-* rules no longer emit E6 (was: 132 false positives across all vendors).
- fix(batch_audit): E10 false positive — removed device_type sub-check from BASE guard; device_type on BASE is valid per BASE-*-DT-* YAML rules.
- fix(conftest): pytest_sessionfinish skip guard — no longer fires during --co (collect-only) mode; added early-return when passed+skipped+failed==0 (deselect/no-run edge case).
- fix(hpe_rules): Air Baffle Kit heatsink→accessory (HW-H-074); Cable Management Arm cable→accessory (HW-H-042).
- fix(batch_audit): known-case FP suppression — KNOWN_FP_CASES with vendor+keyword check, not global transition patterns.
- fix(batch_audit): detect_vendor_from_path returns "unknown" for unrecognized paths (was: silently returning "dell").
- fix(batch_audit + cluster_audit): hasattr guard for sys.stdout/stderr.reconfigure (Windows encoding fix).
- fix(conftest): silent-skip risk warning when input_root exists but contains no recognizable .xlsx fixtures.
- fix(docs): RUN_PATHS — --input-dir → --output-dir; removed phantom audit/ subdirectory and cluster_rules_suggestions.json.

### Known issues (deferred)
- Cisco C9300L-STACK-KIT2= remains entity=BASE — fix requires changes to classifier.py; deferred to a separate plan.

### Removed
- chore(repo): `TAXONOMY_EXPANSION_DIAGNOSTIC.md` (untracked diagnostic artifact from cycle PR-0; superseded by PR-1..PR-5 commits).

---

## [1.3.0] — 2026-03-03

### Added
- feat(hpe): src/vendors/hpe/ — parser, normalizer, adapter (HPEAdapter)
- feat(hpe): rules/hpe_rules.yaml — 82 device_type rules, BASE/SERVICE/LOGISTIC/SOFTWARE/CONFIG sections
- feat(hpe): HPEAdapter registered in VENDOR_REGISTRY (main.py)
- feat(hpe): config.yaml — hpe: rules/hpe_rules.yaml
- feat(hpe): annotated_writer.py — 5 HPE vendor extension columns in VENDOR_EXTRA_COLS; skip-optimization over first 10 rows removed
- feat(hpe): Makefile — HP_FILES, generate_golden_hpe, test-regression-hpe, test-unknown-hpe
- feat(tests): HPE unit tests — test_hpe_parser.py, test_hpe_normalizer.py, test_hpe_rules_unit.py

### Fixed
- fix(main): --output-dir default=None so config.local.yaml → paths.output_root is applied correctly
- fix(hpe): HW-H-GLOBAL-038 — optical drive (DVD-RW) → HW/STORAGE
- fix(Makefile): HPE path aligned with Dell/Cisco — $(INPUT)/$$f.xlsx instead of $(INPUT)/hpe/$$f.xlsx
- fix(hpe): added hw_rules section to hpe_rules.yaml — 37 catch-all rules HW-H-GLOBAL-001…037; eliminates UNKNOWN for CPU/RAM/storage/NIC/PSU/fan/transceiver/cable/riser/rail/GPU and others.
- fix(hpe): added hw_type_rules.applies_to: [HW] — hw_type now populated for all HW rows
- fix: redirect diag/runs and ruff/mypy caches to temp_root (scripts/run_full.ps1, scripts/clean.ps1)
- fix(json_writer): added option_id to unknown_rows.csv
- fix(excel_writer): added Group Name, Group ID to cleaned_spec.xlsx
- fix(branded_spec): rows before first BASE preserved in preamble block instead of silent drop
- fix(conftest): skip guard — CI fail at 0 tests instead of false green
- fix(branded_spec): added price (option_price) column to output
- fix(rules_engine): _get_field_value supports option_id for rule matching
- fix(hpe): HPENormalizedRow inherits from NormalizedRow
- fix(normalizer): qty default changed from 0 to 1 for empty/missing values
- fix(.gitignore): `test_data/*.xlsx` expanded to `test_data/` (entire directory)

### Changed
- docs(P1-6): batch docs update — DOCS_INDEX heading → "Dell + Cisco CCW + HPE"; USER_GUIDE §1/2/7/8 + HPE section; CLI_CONFIG_REFERENCE §3 +HPE example, §4 vendor_rules +hpe; RUN_PATHS_AND_IO_LAYOUT INPUT subfolder hpe/, OUTPUT section HPE, HPE command example; TECHNICAL_OVERVIEW §2/3/7/8/10 +HPE; DATA_CONTRACTS §2 device_type +HPE, §4 +HPE vendor extensions; hw_type updated to 25 values (v2.0.0) across all documents.
- refactor(Makefile): INPUT variable instead of test_data/ and input/hpe/; generate_golden_dell extracted as separate target; all three vendors via $(INPUT)/.
- docs: ONE_BUTTON_RUN.md — diag path updated to temp_root/diag/runs/<timestamp>/
- docs: CONTRIBUTING.md — diag/ marked as gitignored, written to temp_root
- refactor(tests): all Dell/Cisco tests migrated from `test_data/` to `get_input_root_dell()` / `get_input_root_cisco()` — uniform convention with HPE; test_stats_hw_type.py included

---

## [1.2.2] — 2026-03-01

### Added
- feat: one-button run — scripts/run_full.ps1, run_tests.ps1, clean.ps1; config layering (config.local.yaml); docs/dev/ONE_BUTTON_RUN.md.

### Changed
- docs: DATA_CONTRACTS §2 — device_type described as extensible per-vendor dictionary (Dell/Cisco examples); source of truth — `device_type_rules` in `rules/<vendor>_rules.yaml`; new values when adding a vendor — MINOR per section 7. No hardcoded list in code.
- docs: parser.py and rules_engine.RuleSet — docstrings updated to vendor-agnostic phrasing (column-based / sentinel column / vendor YAML); no logic changes.
- Makefile: added CCW_FILES (ccw_1, ccw_2); generate_golden — second loop over CCW_FILES with --vendor cisco; targets test-regression-cisco, test-unknown-cisco, generate_golden_cisco; test target unifies Dell and Cisco regression and unknown-threshold.
- annotated_writer.py: comments and docstring updated to vendor-agnostic phrasing (removed 'Cisco CCW' references for header_row_index=None); no logic changes.
- config: _load_config() merges config.local.yaml on top of config.yaml (deep merge).
- .gitignore: config.local.yaml, temporary/, diag/, .coverage, htmlcov/, .ruff_cache/, .mypy_cache/.
- README: section 'One-button run (Windows)'; DOCS_INDEX: ONE_BUTTON_RUN.md; Makefile title → 'Spec Classifier — Makefile'.

---

## [1.2.1] — 2026-03-01

### Added
- feat: add can_parse() to VendorAdapter — batch gracefully skips wrong-vendor files (OUT-001).
- feat: batch summary: processed/skipped/failed counts + exit code only on real failures.

### Fixed
- fix: DellAdapter.can_parse() uses positive signature — "Module Name" in first 20 rows of first sheet; no longer accepts any xlsx (e.g. Cisco ccw_1.xlsx in Dell batch) (P0).
- fix: parse_excel() returns (rows, header_row_index); DellAdapter.parse() delegates to it only — no triple Excel read (BUG-002).
- fix: run.log now captures all pipeline stages; FileHandler isolated per file in batch (OUT-002).
- fix: replace deprecated datetime.utcnow() with timezone-aware alternative (OUT-003).

### Changed
- config: paths default to `input` / `output`; remove dead `rules_file` key; Dell get_rules_file fallback to `rules/dell_rules.yaml` only (LEAK-001, LEAK-009).
- docs: replace all `C:\Users\<USERNAME>\Desktop\...` with relative paths in README.md, RUN_PATHS_AND_IO_LAYOUT.md, TECHNICAL_OVERVIEW.md, CLI_CONFIG_REFERENCE.md; examples use `input/`, `output/`, `mkdir`; add note on config.local.yaml for absolute paths (LEAK-002, LEAK-003, LEAK-004).
- docs: TECHNICAL_OVERVIEW §1 — pipeline for vendor specifications (Dell, Cisco CCW); source reference — code in src/, main.py, tests/, config.yaml (remove dell_mvp).
- refactor: delegate vendor_stats to adapter.get_vendor_stats(), main.py vendor-agnostic (CODE-002).
- fix: remove Dell parser fallback from generic annotated_writer; header_row_index from adapter (CODE-003).
- chore: bump cisco_rules.yaml version to 1.1.0 (CODE-006).
- refactor: introduce VENDOR_REGISTRY as single registration point for vendors (CODE-005).
- refactor: unify run_pipeline_in_memory in test helpers to use adapter pattern (CODE-004).
- chore: reorganize docs/ — move archive materials to docs/archive/ (FILES-001–004).
- fix: remove hardcoded Windows user paths from argparse defaults (CODE-001).
- fix: remove external client name from branded_spec_writer docstring (DOC-006).
- docs: document recommended INPUT folder structure for multi-vendor batch runs.
- docs: six doc files H1 → '… — spec_classifier' (LEAK-005); core docstrings vendor-agnostic (LEAK-006); hw_type_taxonomy vendors: Dell · Cisco CCW (active) · HPE/Lenovo/xFusion/Huawei (planned) (DOC-010).
- refactor: annotated_writer — replace has_cisco_fields with VENDOR_EXTRA_COLS registry (LEAK-007).
- refactor: test_smoke, test_annotated_writer, test_excel_writer use adapter via _get_adapter (LEAK-008).
- docs: RULES_AUTHORING_GUIDE — rule_id naming convention section (format, vendor table, NNN, reserved) (DOC-011).
- docs: NEW_VENDOR_GUIDE.md — self-contained guide for adding a vendor (9 steps, positive signature, VENDOR_EXTRA_COLS, checklist) (DOC-012).

---

## [1.2.0] — 2026-02-28

### Added (Multivendor — Cisco CCW)
- VendorAdapter ABC (`src/vendors/base.py`); DellAdapter and CiscoAdapter.
- Cisco CCW parser (`src/vendors/cisco/parser.py`): sheet "Price Estimate", line_number hierarchy, last-non-empty data-end detection.
- CiscoNormalizedRow (`src/vendors/cisco/normalizer.py`): bundle_id, is_bundle_root, parent_line_number, module_name, service_duration_months, vendor extension fields.
- `rules/cisco_rules.yaml`: unknown_count = 0 on ccw_1 (26 rows) and ccw_2 (82 rows).
- `--vendor {dell,cisco}` CLI flag; `vendor_rules` config section.
- `vendor_stats` in `run_summary.json`: always present (`{}` for Dell, populated for Cisco).
- Annotated writer now vendor-agnostic: accepts `header_row_index` from adapter.
- Branded spec skipped for Cisco.
- Golden files: `golden/ccw_1_expected.jsonl`, `golden/ccw_2_expected.jsonl`.
- Cisco test suite: test_cisco_parser, test_cisco_normalizer, test_regression_cisco, test_unknown_threshold_cisco.
- Batch mode (`--batch-dir`): process all .xlsx in a directory; creates per-run folders and a TOTAL aggregation folder.
- TOTAL folder aggregation: `<stem>_annotated.xlsx`, `<stem>_branded.xlsx`, `<stem>_cleaned_spec.xlsx` copied from each run into `run-YYYY-MM-DD__HH-MM-SS-TOTAL/`.
- Readable run folder naming: `run-YYYY-MM-DD__HH-MM-SS-<stem>` (was `run_YYYYMMDD_HHMMSS`).
- Branded spec output: `<stem>_branded.xlsx` per run (grouped by BASE server + entity type sections).
- Annotated export expanded to 4 columns: Entity Type, State, device_type, hw_type.
- `run_summary.json` extended: `device_type_counts`, `hw_type_counts`, `hw_type_null_count`, `rules_file_hash`, `input_file`, `run_timestamp`.
- Full documentation restructure: `docs/product/`, `docs/user/`, `docs/schemas/`, `docs/rules/`, `docs/dev/`, `docs/roadmap/`, `docs/prompts/`.
- `run_manager.py`: `get_session_stamp()`, `create_total_folder()`, `copy_to_total()`.

### Changed
- docs: sync DATA_CONTRACTS hw_type list with HW_TYPE_VOCAB in classifier.py (DOC-001).
- docs: fix taxonomy header count to match actual HW_TYPE_VOCAB size (DOC-002).
- **Repo layout:** Removed legacy `dell_spec_classifier/` shim folder. `spec_classifier/` is the only canonical project root. Run CLI and tests from inside `spec_classifier/` (see README).

### Fixed
- Inconsistency between core CLI run naming and batch wrapper naming — now unified in core.
- Annotated header-row detection when a Solution Info preamble is present.

---

## [1.1.1] — 2026-02-25

### Added
- Full `hw_type` classification pipeline (three-layer: device_type_map → rule_id_map → regex).
- `hw_type` statistics in `run_summary.json` (`hw_type_counts`, `hw_type_null_count`).
- Annotated Excel output with `hw_type` column.

### Fixed
- Unresolved HW rows now produce `hw_type: null` + warning instead of crashing.
- Regression synchronization with golden after hw_type addition.

---

## [1.1.0] — 2026-02-25

### Fixed
- DEC-003: "Blanks" plural recognized; state overridden to PRESENT.
- DEC-001/002: "No Cable" / "No Cables Required" classified as CONFIG + ABSENT.
- DEC-004: Optics and transceivers classified as `hw_type=network_adapter`.
- DEC-005: PERC Controller rows now have `device_type=raid_controller`.
- DEC-006: BOSS-N1 controller card → `storage_controller`; "No BOSS Card" →
  CONFIG + ABSENT (DEC-006).
- DEC-007: state from "No" prefix ("No Quick Sync", "No Bezel") → ABSENT.
- DEC-008: Storage devices (NVMe, SSD, HDD, BOSS) classified as `hw_type=storage_drive`.
