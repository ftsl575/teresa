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

### Fixed
- Cisco NXK-AF-PE "Dummy PID Airflow" → CONFIG
  (CONFIG-C-001 расширен на все Dummy PID; HW-C-021-AIRFLOW и DT-C-021-AIRFLOW удалены)
- Dell E16 подавлен для 412-AASK и 470-BCHP (NIC/BOSS blank fillers, не drive bay)
- E14: убран токен `airflow selection` из паттерна (Cisco Dummy PID Airflow → CONFIG, не blank_filler)
- E14: SKU-исключение для NXK-AF-PE (Dummy PID Airflow → намеренно CONFIG без device_type)
- Cisco C-RFID-1R: device_type management → accessory (RFID-метка — физическая наклейка, не management)
- Dell "No Bezel", "No HBM", "No Quick Sync", "No Systems Documentation" → CONFIG
  (CONFIG-NOBEZEL-001, CONFIG-NOHBM-001, CONFIG-NOQUICKSYNC-001, CONFIG-NODOC-001)
- Dell DT-D-031-NO-BEZEL удалён (был ошибочным фиксом из плана 2)
- Cisco CAB-GUIDE-1RU → HW/accessory (HW-C-024-CAB-GUIDE, DT-C-015-CAB-GUIDE)
- Dell 631-AACK "No Systems Documentation" → CONFIG
  (убран токен Documentation из LOGISTIC-001, удалён LOGISTIC-002)

### Known issues (deferred)
- Cisco C9300L-STACK-KIT2= остаётся entity=BASE — фикс требует изменения classifier.py,
  отложен до отдельного плана

### Fixed
- device_type mismatches: HPE proliant catch-all (BASE-H-DT-001 → BASE-H-DT-999),
  Dell heatsink/chassis/bezel/backplane/fan_foam classification order,
  all vendors power_cord missing hw_type (E8+E9),
  Dell BOSS-N1 device_type (DT-D-033-BOSS-N1),
  Cisco M2USB → storage_ssd (DT-C-011-M2USB-SSD)
- fix(batch_audit): E6 false positive — added "BASE" to allowed entity set; BASE rows with device_type set by BASE-*-DT-* rules no longer emit E6 (was: 132 false positives across all vendors).
- fix(batch_audit): E10 false positive — removed device_type sub-check from BASE guard; device_type on BASE is valid per BASE-*-DT-* YAML rules.

### Added
- feat(batch_audit): config_name → module_name alias in _ALIASES dict; HPE LLM payload now carries module context (was always empty string, causing ~78% AI_MISMATCH baseline).
- feat(batch_audit): "product_#" added to SKU column detection in audit_summary writer; HPE audit_summary now shows populated SKU column.
- feat(batch_audit): "config_name" added to Module Name column detection in audit_summary writer; HPE audit_summary now shows populated Module Name column.
- feat(batch_audit): E18 check — LOGISTIC rows with physical keyword (cord/cable/rail/bracket/mount/kit/rack/pdu/ups) and no device_type are now flagged.
- feat(annotated_writer): row_kind column added to annotated xlsx output ("ITEM"/"HEADER"); batch_audit HEADER guard is now functional.
- feat(tests): tests/test_batch_audit.py — ≥45 test cases covering E1–E18 via validate_row() and REAL_BUG/_generate_report logic.
- feat(tests): tests/test_cluster_audit.py — 30 test cases covering _detect_vendor_from_path, _is_empty, _collect_xlsx_files, normalize_text, analyze_clusters, heuristic_mapping, write_cluster_summary, print_dry_run_report, build_parser.
- feat(tests): tests/test_hpe_rules_unit.py expanded — 25 parametrized device_type/hw_type cases covering all 25 unique HPE device_types.
- feat(excel_writer): cleaned_spec for HPE now includes 5 vendor extension columns: Config Name, Lead Time, Extended Price, Product Type, Factory Integrated. Dell/Cisco output unchanged.
- feat(hpe_rules): note_rules: [] placeholder section added to hpe_rules.yaml (consistent with dell_rules.yaml and cisco_rules.yaml).

### Fixed
- fix: golden files updated after power_cord hw_type=None taxonomy change (11 golden + test_stats_hw_type.py cable count); reverted stray runtime schema validation in rules_engine.py.

### Added
- docs: CLAUDE.md — project context file for Cowork and Claude Desktop.
- docs: prompts/ — prompt library with 8 step templates + COWORK_OPUS_FULL_AUDIT.md.

### Changed
- fix(taxonomy/rules P1-7): power_cord hw_type mapping removed from all three vendor YAML files (dell_rules, cisco_rules, hpe_rules). power_cord rows: entity_type=HW, device_type=power_cord, hw_type=None (taxonomy decision is authoritative).
- fix(taxonomy P1-7): hw_type_rules.applies_to narrowed from [HW, BASE] to [HW] in all three vendor YAML files and hw_type_taxonomy.md (code was correct, taxonomy was wrong).
- fix(conftest): pytest_sessionfinish skip guard — no longer fires during --co (collect-only) mode; added early-return when passed+skipped+failed==0 (deselect/no-run edge case).

---

## [1.3.0] — 2026-03-03

### Added
- feat(hpe): src/vendors/hpe/ — parser, normalizer, adapter (HPEAdapter)
- feat(hpe): rules/hpe_rules.yaml — 82 device_type правила, BASE/SERVICE/LOGISTIC/SOFTWARE/CONFIG секции
- feat(hpe): HPEAdapter зарегистрирован в VENDOR_REGISTRY (main.py)
- feat(hpe): config.yaml — hpe: rules/hpe_rules.yaml
- feat(hpe): annotated_writer.py — 5 HPE vendor extension колонок в VENDOR_EXTRA_COLS; skip-оптимизация по первым 10 строкам удалена
- feat(hpe): Makefile — HP_FILES, generate_golden_hpe, test-regression-hpe, test-unknown-hpe
- feat(tests): HPE unit tests — test_hpe_parser.py, test_hpe_normalizer.py, test_hpe_rules_unit.py (audit_1G P1-5)

### Fixed
- fix(main): --output-dir default=None, чтобы config.local.yaml → paths.output_root применялся корректно
- fix(hpe): HW-H-GLOBAL-038 — optical drive (DVD-RW) → HW/STORAGE
- fix(Makefile): HPE путь выровнен с Dell/Cisco — $(INPUT)/$$f.xlsx вместо $(INPUT)/hpe/$$f.xlsx
- fix(hpe): добавлена секция hw_rules в hpe_rules.yaml — 37 catch-all правил HW-H-GLOBAL-001…037; устранён UNKNOWN для CPU/RAM/storage/NIC/PSU/fan/transceiver/cable/riser/rail/GPU и др.
- fix(hpe): добавлено hw_type_rules.applies_to: [HW] — hw_type теперь заполняется для всех HW rows
- fix: redirect diag/runs and ruff/mypy caches to temp_root (scripts/run_full.ps1, scripts/clean.ps1)

### Changed
- docs(P1-6): batch docs update — DOCS_INDEX заголовок → "Dell + Cisco CCW + HPE"; USER_GUIDE §1/2/7/8 + HPE раздел; CLI_CONFIG_REFERENCE §3 +HPE пример, §4 vendor_rules +hpe; RUN_PATHS_AND_IO_LAYOUT INPUT подпапка hpe/, OUTPUT секция HPE, пример команды HPE; TECHNICAL_OVERVIEW §2/3/7/8/10 +HPE; DATA_CONTRACTS §2 device_type +HPE, §4 +HPE vendor extensions; hw_type обновлён до 25 значений (v2.0.0) во всех документах
- refactor(Makefile): INPUT переменная вместо test_data/ и input/hpe/; generate_golden_dell выделен отдельной целью; все три вендора через $(INPUT)/
- docs: ONE_BUTTON_RUN.md — diag path updated to temp_root/diag/runs/<timestamp>/
- docs: CONTRIBUTING.md — diag/ отмечен как gitignored, пишется в temp_root
- refactor(tests): все тесты Dell/Cisco переведены с `test_data/` на `get_input_root_dell()` / `get_input_root_cisco()` — единое соглашение с HPE; test_stats_hw_type.py включён
- docs: OPERATIONAL_NOTES, TESTING_GUIDE, NEW_VENDOR_GUIDE, ONE_BUTTON_RUN, TECHNICAL_OVERVIEW, RULES_AUTHORING_GUIDE, USER_GUIDE, README — `test_data/` заменён на `C:\Users\G\Desktop\INPUT\` во всех примерах команд
- fix(.gitignore): `test_data/*.xlsx` расширен до `test_data/` (целиком)
- fix(json_writer): добавлен option_id в unknown_rows.csv (audit_1G P0-1)
- fix(excel_writer): добавлены Group Name, Group ID в cleaned_spec.xlsx (audit_1G P0-2)
- fix(branded_spec): строки до первого BASE сохраняются в preamble-блок вместо silent drop (audit_1G P0-3)
- fix(conftest): skip guard — CI fail при 0 тестах вместо ложного зелёного (audit_1G P0-4)
- fix(branded_spec): добавлена колонка price (option_price) в вывод (audit_1G P1-1)
- fix(rules_engine): _get_field_value поддерживает option_id для матчинга правил (audit_1G P1-2)
- fix(hpe): HPENormalizedRow наследует от NormalizedRow (audit_1G P1-3)
- fix(normalizer): qty default изменён с 0 на 1 для пустых/отсутствующих значений (audit_1G P1-4)

---

## [1.2.2] — 2026-03-01

### Added
- feat: one-button run — scripts/run_full.ps1, run_tests.ps1, clean.ps1; config layering (config.local.yaml); docs/dev/ONE_BUTTON_RUN.md (PROMPT #7).

### Changed
- docs: DATA_CONTRACTS §2 — device_type описан как расширяемый словарь по вендорам (Dell/Cisco примеры); источник истины — `device_type_rules` в `rules/<vendor>_rules.yaml`; новые значения при добавлении вендора — MINOR по разделу 7. Жёсткий список в коде не вводится.
- docs: parser.py и rules_engine.RuleSet — docstrings приведены к vendor-agnostic формулировкам (column-based / sentinel column / vendor YAML); без изменения логики.
- Makefile: добавлены CCW_FILES (ccw_1, ccw_2); generate_golden — второй цикл по CCW_FILES с --vendor cisco; цели test-regression-cisco, test-unknown-cisco, generate_golden_cisco; test объединяет Dell и Cisco регрессию и unknown-threshold.
- annotated_writer.py: комментарии и docstring приведены к vendor-agnostic формулировкам (убраны упоминания «Cisco CCW» для header_row_index=None); без изменения логики.
- config: _load_config() merges config.local.yaml on top of config.yaml (deep merge).
- .gitignore: config.local.yaml, temporary/, diag/, .coverage, htmlcov/, .ruff_cache/, .mypy_cache/.
- README: section «One-button run (Windows)»; DOCS_INDEX: ONE_BUTTON_RUN.md; Makefile title → «Spec Classifier — Makefile».

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
- docs: replace all `C:\Users\G\Desktop\...` with relative paths in README.md, RUN_PATHS_AND_IO_LAYOUT.md, TECHNICAL_OVERVIEW.md, CLI_CONFIG_REFERENCE.md; examples use `input/`, `output/`, `mkdir`; add note on config.local.yaml for absolute paths (LEAK-002, LEAK-003, LEAK-004).
- docs: TECHNICAL_OVERVIEW §1 — «пайплайн для вендорных спецификаций (Dell, Cisco CCW)»; source reference — код в src/, main.py, tests/, config.yaml (remove dell_mvp).
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
- docs: six doc files H1 → «… — spec_classifier» (LEAK-005); core docstrings vendor-agnostic (LEAK-006); hw_type_taxonomy vendors: Dell · Cisco CCW (active) · HPE/Lenovo/xFusion/Huawei (planned) (DOC-010).
- refactor: annotated_writer — replace has_cisco_fields with VENDOR_EXTRA_COLS registry (LEAK-007).
- refactor: test_smoke, test_annotated_writer, test_excel_writer use adapter via _get_adapter (LEAK-008).
- docs: RULES_AUTHORING_GUIDE — секция «Конвенция именования rule_id» (формат, таблица вендоров, NNN, зарезервированные) (DOC-011).
- docs: NEW_VENDOR_GUIDE.md — самодостаточное руководство по добавлению вендора (9 шагов, позитивная сигнатура, VENDOR_EXTRA_COLS, чеклист) (DOC-012).

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
