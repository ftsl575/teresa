# Current State — spec_classifier (teresa)

## Версия
1.2.0

## Дата последнего аудита
2026-03-01

## Активные вендоры
- Dell (spec export)
- Cisco (CCW — Commerce Workspace)

## Статус классификации
- unknown_count = 0 на всех датасетах (dl1–dl5, ccw_1, ccw_2)
- hw_type_null_count = 0

## Известные проблемы
- Смотри CHANGELOG.md [Unreleased]

## Adapter can_parse (P0)
- DellAdapter: положительная сигнатура — ячейка "Module Name" в первых 20 строках первого листа.
- CiscoAdapter: положительная сигнатура — лист "Price Estimate" в wb.sheetnames.
- В смешанном batch (Dell + Cisco) каждый адаптер отклоняет чужие файлы по своей сигнатуре.

## I/O и парсинг (P1)
- `parse_excel()` (core) возвращает `(rows, header_row_index)` — один проход по файлу; DellAdapter.parse() делегирует ему, без повторного find_header_row() (BUG-002).
- config.yaml: пути по умолчанию `input` / `output`; ключ `rules_file` удалён; правила вендоров только в `vendor_rules` (LEAK-001, LEAK-009).

## Документация — пути (P1, LEAK-002–004)
- README.md, RUN_PATHS_AND_IO_LAYOUT.md, TECHNICAL_OVERVIEW.md, CLI_CONFIG_REFERENCE: все примеры используют относительные пути `input/`, `output/`; личные пути `C:\Users\G\...` удалены. TECHNICAL_OVERVIEW: формулировка «пайплайн для вендорных спецификаций (Dell, Cisco CCW)»; источник — код и config, без dell_mvp.

## Документация — заголовки и ядро (P1, LEAK-005, LEAK-006, DOC-010)
- Шесть doc-файлов: H1 заменён на «… — spec_classifier» (LEAK-005). Docstrings core: normalizer, rules_engine, parser, state_detector — без «Dell specification», «load Dell rules» (LEAK-006). Taxonomy: «Vendors covered: Dell · Cisco CCW (active) · HPE · Lenovo · xFusion · Huawei (planned)» (DOC-010).

## Annotated writer и тесты (P1, LEAK-007, LEAK-008)
- annotated_writer: проверка `has_cisco_fields` заменена на расширяемый реестр VENDOR_EXTRA_COLS (LEAK-007). test_smoke, test_annotated_writer, test_excel_writer: используют _get_adapter("dell", {}), adapter.parse(), adapter.normalize() вместо прямых вызовов parse_excel/normalize_row (LEAK-008).

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

## Workflow
Claude анализирует репо → пишет промпты → Cursor выполняет →
Claude проводит аудит после каждого набора изменений.

## One-button workflow (PROMPT #7)
- **Config layering:** main.py загружает config.yaml, затем поверх — config.local.yaml (если есть); глубокое слияние по ключам.
- **config.local.yaml.example** в корне; config.local.yaml в .gitignore.
- **.gitignore:** добавлены config.local.yaml, temporary/, diag/, .coverage, htmlcov/, .ruff_cache/, .mypy_cache/.
- **Скрипты (scripts/):** run_full.ps1 (pytest + batch по вендорам), run_tests.ps1 (только pytest), clean.ps1 (очистка __pycache__ и .pytest_cache). Логи run_full → diag/runs/\<timestamp\>/.
- **Документация:** docs/dev/ONE_BUTTON_RUN.md; README — секция «One-button run (Windows)»; DOCS_INDEX — ссылка на ONE_BUTTON_RUN.
- **Makefile:** заголовок изменён на «Spec Classifier — Makefile».
