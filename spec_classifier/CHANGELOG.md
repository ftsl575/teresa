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

### Changed
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
