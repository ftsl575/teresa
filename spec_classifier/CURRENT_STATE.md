# Current State — spec_classifier (teresa)

## Версия
1.4.0

## Дата последнего аудита
2026-03-06 (audit_2G PASS — 281 tests collected; unit/rules/writer tests 0 fail); 2026-03-07 (audit_1G FAIL — 7 P0); 2026-03-11 (recovery: golden sync, stray revert); 2026-03-15 (batch audit review — FAIL, 3 P0 / 10 P1); 2026-04-04 (audit_1E — Steps 0-2 delivered: Dell raid_controller fix, get_extra_cols() per-adapter, vendor-agnostic audit scripts)

## Активные вендоры
- Dell (spec export)
- Cisco (CCW — Commerce Workspace)
- HPE (QuoteBuilder BOM) — адаптер, правила (hpe_rules.yaml), регистрация в VENDOR_REGISTRY, config.yaml, annotated_writer (6 колонок, включая matched_rule_id), Makefile (HP_FILES, golden/тесты)

## Статус классификации
- unknown_count = 0 на всех датасетах (dl1–dl5, ccw_1, ccw_2, hp1–hp8)
- hw_type_null_count = 0 на всех датасетах (кроме power_cord: hw_type=None — intentional, per business rules)

## Документация — device_type (DATA_CONTRACTS)
- **device_type** описан как расширяемый словарь по вендорам; источник истины — `device_type_rules` в `rules/<vendor>_rules.yaml`. Новые значения при добавлении вендора — MINOR по разделу 7. Жёсткий список в коде не вводится.

## Известные проблемы
- Смотри CHANGELOG.md [Unreleased] для актуального списка изменений.
- 2026-03-11 recovery: golden files synced after power_cord hw_type=None change. Stray Cowork runtime schema validation in rules_engine.py reverted. prompts/ and CLAUDE.md added to repo.
- audit_2G (2026-03-06) — PASS: E6/E10 false positives устранены, HPE aliases в batch_audit, row_kind колонка в annotated output, E18 check, taxonomy P1-7 (power_cord hw_type=None, applies_to=[HW]), conftest skip guard исправлен, cleaned_spec HPE extensions, test coverage расширена (batch_audit, cluster_audit, hpe_rules_unit).
- audit_1G (2026-03-03) — PASS: option_id в unknown_rows.csv, Group Name/Group ID в cleaned_spec.xlsx, preamble-блок в branded_spec, qty default 0→1, skip guard в CI, HPE unit tests добавлены.

## HPE (Step 1–2)
- **src/vendors/hpe/:** созданы parser.py (BOM, col_map по имени, Total/EOF), normalizer.py (HPENormalizedRow + vendor extensions), adapter.py (HPEAdapter). can_parse: лист BOM + заголовки "Product #", "Product Description".
- **rules/hpe_rules.yaml:** создан (version 1.0.0) — base_rules, service_rules, logistic_rules, config_rules, software_rules, device_type_rules (82 правила), hw_type_rules.device_type_map.
- **Интеграция (Step 3):** main.py — VENDOR_REGISTRY["hpe"] = HPEAdapter; config.yaml — hpe: rules/hpe_rules.yaml; annotated_writer — 5 HPE колонок (теперь через HPEAdapter.get_extra_cols()), skip по первым 10 строкам убран; Makefile — HP_FILES, generate_golden_hpe, test-regression-hpe, test-unknown-hpe. Тесты test_regression_hpe и test_unknown_threshold_hpe — отдельный шаг (файлы тестов и golden).

## Adapter can_parse (P0)
- DellAdapter: положительная сигнатура — ячейка "Module Name" в первых 20 строках первого листа.
- CiscoAdapter: положительная сигнатура — лист "Price Estimate" в wb.sheetnames.
- HPEAdapter: положительная сигнатура — лист "BOM" в wb.sheetnames и в строке 1 наличие "Product #" и "Product Description".
- В смешанном batch каждый адаптер отклоняет чужие файлы по своей сигнатуре.

## I/O и парсинг (P1)
- `parse_excel()` (core) возвращает `(rows, header_row_index)` — один проход по файлу; DellAdapter.parse() делегирует ему, без повторного find_header_row() (BUG-002).
- config.yaml: пути по умолчанию `input` / `output`; ключ `rules_file` удалён; правила вендоров только в `vendor_rules` (LEAK-001, LEAK-009).
- Нормализация qty: при пустом или отсутствующем значении используется default = 1 (ранее 0).

## Документация — пути (P1, LEAK-002–004)
- README.md, RUN_PATHS_AND_IO_LAYOUT.md, TECHNICAL_OVERVIEW.md, CLI_CONFIG_REFERENCE: все примеры используют относительные пути `input/`, `output/`. Пути задаются через config.local.yaml. TECHNICAL_OVERVIEW: формулировка «пайплайн для вендорных спецификаций (Dell, Cisco CCW, HPE)»; источник — код и config, без dell_mvp.

## Документация — заголовки и ядро (P1, LEAK-005, LEAK-006, DOC-010)
- Шесть doc-файлов: H1 заменён на «… — spec_classifier» (LEAK-005). Docstrings core: normalizer, rules_engine, parser, state_detector — без «Dell specification», «load Dell rules» (LEAK-006). parser.py: «column-based specification files», «sentinel column value», «1-based Excel row number»; rules_engine.RuleSet: «Loaded classification rules from a vendor YAML file». Taxonomy: «Vendors covered: Dell · Cisco CCW (active) · HPE · Lenovo · xFusion · Huawei (planned)» (DOC-010).

## Annotated writer и тесты (P1, LEAK-007, LEAK-008)
- annotated_writer: проверка `has_cisco_fields` заменена на расширяемый паттерн (LEAK-007); в рамках audit_1E рефакторинг завершён: VENDOR_EXTRA_COLS удалён, вместо него — `VendorAdapter.get_extra_cols()` (default []), переопределён в HPEAdapter (5 колонок) и CiscoAdapter (2 колонки). Комментарии и docstring — без упоминания «Cisco CCW» (header_row_index=None описан как «formats with no fixed header row» / «format has no header row»). test_smoke, test_annotated_writer, test_excel_writer: используют _get_adapter("dell", {}), adapter.parse(), adapter.normalize() вместо прямых вызовов parse_excel/normalize_row (LEAK-008).

## P2 — документация (DOC-011, DOC-012)
- RULES_AUTHORING_GUIDE: добавлена секция «Конвенция rule_id» — формат PREFIX-NUMBER[-SUFFIX], мультивендор (-C- для Cisco), уникальность, связь с golden (DOC-011).
- NEW_VENDOR_GUIDE.md (docs/dev/): пошаговое руководство по добавлению нового вендора (адаптер, регистрация, config, правила, тесты, VENDOR_EXTRA_COLS) (DOC-012).

## Структура docs/
- docs/user/       — инструкции для пользователей
- docs/dev/        — инструкции для разработчиков (в т.ч. NEW_VENDOR_GUIDE.md)
- docs/schemas/    — контракты данных (DATA_CONTRACTS.md)
- docs/taxonomy/   — справочники типов
- docs/rules/      — документация правил классификации
- docs/product/    — TECHNICAL_OVERVIEW.md (единственный актуальный обзор)
- docs/archive/    — замёрзшие материалы (не актуальны)

## audit_1E (2026-04-04) — Steps 0-2

- **Step 0 — bugfix:**
  - BUG-1: `rules/dell_rules.yaml` DT-D-027-RAID расширен на BOSS + Storage Controller; raid_controller теперь не падает в accessory.
  - BUG-2: `spec_classifier/.gitignore` — добавлен `config.local.yaml`.
  - BUG-3: `.gitignore` (outer) перезаписан в UTF-8 LF (был смешанный UTF-16LE).
- **Step 1 — VendorAdapter.get_extra_cols():**
  - `VendorAdapter.get_extra_cols()` добавлен как конкретный метод (default `[]`).
  - HPEAdapter.get_extra_cols() возвращает 5 HPE-специфичных колонок.
  - CiscoAdapter.get_extra_cols() возвращает 2 Cisco-специфичных колонки.
  - DellAdapter — без изменений (наследует default).
  - `annotated_writer.generate_annotated_source_excel()` принимает `extra_cols` как параметр; VENDOR_EXTRA_COLS удалён.
  - `main.py` передаёт `adapter.get_extra_cols()`.
- **Step 2 — vendor-agnostic audit:**
  - `batch_audit.py`: DEVICE_TYPE_MAP загружается из YAML (R1); `detect_vendor_from_path()` принимает `known_vendors` (R2); `--vendor choices` динамические из `config.yaml` (R3); E4 state logic data-driven dict `E4_STATE_VALIDATORS` + `_check_e4()` (R4); LLM_SYSTEM промпт шаблонизирован через `_build_llm_system()` (R5).
  - `cluster_audit.py`: `_load_config()` / `_get_known_vendors()` добавлены; `_detect_vendor_from_path()` generic; choices динамические (R6).
  - Тесты: 114 tests green (8 новых для R2/R6).

## Workflow
Claude анализирует репо → пишет промпты → Cursor выполняет →
Claude проводит аудит после каждого набора изменений.

## One-button workflow (PROMPT #7)
- **Config layering:** main.py загружает config.yaml, затем поверх — config.local.yaml (если есть); глубокое слияние по ключам.
- **config.local.yaml.example** в корне; config.local.yaml в .gitignore.
- **.gitignore:** добавлены config.local.yaml, temporary/, diag/, .coverage, htmlcov/, .ruff_cache/, .mypy_cache/.
- **temp_root/diag:** Логи run_full и все временные артефакты (diag/runs/\<timestamp\>/, .ruff_cache, .mypy_cache, __pycache__, .pytest_cache) пишутся в temp_root из config.local.yaml; репо не засоряется. clean.ps1 удаляет их из temp_root и при необходимости из рабочего дерева (старый diag/ в репо удалён).
- **Скрипты (scripts/):** run_full.ps1 (pytest + batch по вендорам), run_tests.ps1 (только pytest), clean.ps1 (очистка __pycache__, .pytest_cache, .ruff_cache, .mypy_cache, diag/). Логи run_full → temp_root/diag/runs/\<timestamp\>/.
- **Документация:** docs/dev/ONE_BUTTON_RUN.md; README — секция «One-button run (Windows)»; DOCS_INDEX — ссылка на ONE_BUTTON_RUN.
- **Makefile:** заголовок изменён на «Spec Classifier — Makefile». Переменные DL_FILES (dl1–dl5), CCW_FILES (ccw_1, ccw_2). Цель `test` включает test-regression-cisco и test-unknown-cisco. `generate_golden` генерирует golden и для Dell, и для Cisco (второй цикл по CCW_FILES с --vendor cisco). Отдельная цель `generate_golden_cisco` — только Cisco.
- Makefile: INPUT ?= C:/Users/G/Desktop/INPUT — единый корень для Dell/Cisco/HPE; generate_golden_dell отдельная цель
