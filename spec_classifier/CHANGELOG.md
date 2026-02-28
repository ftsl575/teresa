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

### Added
- feat: add can_parse() to VendorAdapter — batch gracefully skips wrong-vendor files (OUT-001).
- feat: batch summary: processed/skipped/failed counts + exit code only on real failures.

### Fixed
- fix: run.log now captures all pipeline stages; FileHandler isolated per file in batch (OUT-002).
- fix: replace deprecated datetime.utcnow() with timezone-aware alternative (OUT-003).

### Changed
- docs: fix output paths in TECHNICAL_OVERVIEW, add --output-dir default, update README title for multivendor, assign version 1.2.0 to unreleased section.
- refactor: delegate vendor_stats to adapter.get_vendor_stats(), main.py vendor-agnostic (CODE-002).
- fix: remove Dell parser fallback from generic annotated_writer; header_row_index from adapter (CODE-003).
- chore: bump cisco_rules.yaml version to 1.1.0 (CODE-006).
- refactor: introduce VENDOR_REGISTRY as single registration point for vendors (CODE-005).
- refactor: unify run_pipeline_in_memory in test helpers to use adapter pattern (CODE-004).
- chore: reorganize docs/ — move archive materials to docs/archive/ (FILES-001–004).
- chore: add CURRENT_STATE.md to root.
- chore: remove golden/.gitkeep.
- fix: remove hardcoded Windows user paths from argparse defaults (CODE-001).
- fix: remove external client name from branded_spec_writer docstring (DOC-006).
- docs: document recommended INPUT folder structure for multi-vendor batch runs.

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

### Changed
- docs: sync DATA_CONTRACTS hw_type list with HW_TYPE_VOCAB in classifier.py (DOC-001).
- docs: fix taxonomy header count to match actual HW_TYPE_VOCAB size (DOC-002).
- **Repo layout:** Removed legacy `dell_spec_classifier/` shim folder. `spec_classifier/` is the only canonical project root. Run CLI and tests from inside `spec_classifier/` (see README).

### Added
- Batch mode (`--batch-dir`): process all .xlsx in a directory; creates per-run folders
  and a TOTAL aggregation folder.
- TOTAL folder aggregation: `<stem>_annotated.xlsx`, `<stem>_branded.xlsx`,
  `<stem>_cleaned_spec.xlsx` copied from each run into `run-YYYY-MM-DD__HH-MM-SS-TOTAL/`.
- Readable run folder naming: `run-YYYY-MM-DD__HH-MM-SS-<stem>` (was `run_YYYYMMDD_HHMMSS`).
- Branded spec output: `<stem>_branded.xlsx` per run (grouped by BASE server + entity type sections).
- Annotated export expanded to 4 columns: Entity Type, State, device_type, hw_type.
- `run_summary.json` extended: `device_type_counts`, `hw_type_counts`, `hw_type_null_count`,
  `rules_file_hash`, `input_file`, `run_timestamp`.
- Full documentation restructure: `docs/product/`, `docs/user/`, `docs/schemas/`,
  `docs/rules/`, `docs/dev/`, `docs/roadmap/`, `docs/prompts/`.
- `run_manager.py`: `get_session_stamp()`, `create_total_folder()`, `copy_to_total()`.

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
- DEC-006: BOSS-N1 controller card → `storage_controller`; "No BOSS Card" → CONFIG + ABSENT.
- F1: Hard Drive / 10K rows classified as `hw_type=hdd`.
- SFP Modules: DAC/Twinax cables → `entity_type=HW`, `hw_type=cable`, `device_type=sfp_cable`.
- FRONT STORAGE / REAR STORAGE → `hw_type=chassis`.

---

## [1.0.0] — 2026-02-23

### Added
- Initial release: 8 entity types (BASE, HW, CONFIG, SOFTWARE, SERVICE, LOGISTIC, NOTE, UNKNOWN).
- `row_kind` detection (ITEM/HEADER).
- State detection: PRESENT, ABSENT, DISABLED.
- Full test coverage with regression tests (`golden/dl1–dl5_expected.jsonl`).
- SOFTWARE-001: Embedded Systems Management.
- SOFTWARE-002: Dell Secure Onboarding.
