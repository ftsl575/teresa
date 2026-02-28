# Baseline v1.2.0

**Date:** 2026-02-27  
**Status:** Stable / Frozen  
**Предыдущий baseline:** [BASELINE_v1.1.0.md](BASELINE_v1.1.0.md)

Документ фиксирует состояние репозитория после реализации multivendor-расширения (Cisco CCW). Никаких функциональных изменений этот документ не подразумевает; он служит точкой отсчёта перед дальнейшим развитием.

---

## 1. Scope

- **Multivendor pipeline:** VendorAdapter ABC, DellAdapter, CiscoAdapter.
- **Cisco CCW parser:** лист "Price Estimate", line_number иерархия, find_data_end (last-non-empty).
- **CiscoNormalizedRow:** duck-type compatible с NormalizedRow; bundle_id, is_bundle_root, parent_line_number, module_name, service_duration_months и прочие extension-поля.
- **cisco_rules.yaml:** unknown_count = 0 на ccw_1 (26 строк) и ccw_2 (82 строки).
- **Writer fixes:** annotated_writer принимает header_row_index, branded spec пропускается для Cisco.
- **vendor_stats в run_summary:** always present (`{}` для Dell, данные для Cisco).
- **Golden:** ccw_1_expected.jsonl, ccw_2_expected.jsonl добавлены.
- **138+ тестов:** зелёные; добавлены test_cisco_parser, test_cisco_normalizer, test_regression_cisco, test_unknown_threshold_cisco.

---

## 2. Implemented Features

- **VendorAdapter ABC** (`src/vendors/base.py`) — интерфейс `parse()`, `normalize()`, `get_rules_file()`; dispatch через `_get_adapter(vendor, config)` в `main.py`.
- **DellAdapter** (`src/vendors/dell/adapter.py`) — обёртка над существующими `src.core.parser` и `src.core.normalizer`.
- **CiscoAdapter** (`src/vendors/cisco/adapter.py`) — делегирует в cisco parser и cisco normalizer; возвращает `header_row_index` для annotated writer.
- **Cisco CCW parser** (`src/vendors/cisco/parser.py`) — лист `"Price Estimate"` (строго); заголовок по одновременному наличию `"Line Number"` и `"Part Number"`; last-non-empty data-end detection; trailing `=` в Part Number удаляется.
- **CiscoNormalizedRow** (`src/vendors/cisco/normalizer.py`) — duck-type compatible с NormalizedRow; поля: line_number, bundle_id, is_top_level, is_bundle_root, parent_line_number, service_duration_months, smart_account_mandatory, lead_time_days, unit_net_price, disc_pct, extended_net_price.
- **cisco_rules.yaml** (`rules/cisco_rules.yaml`) — Cisco-специфичные правила классификации; first-match semantics; доступные поля: module_name, option_name, sku, is_bundle_root, service_duration_months.
- **--vendor CLI flag** — `--vendor {dell,cisco}` (default: dell); `vendor_rules` секция в config.yaml.
- **vendor_stats в run_summary.json** — always present; `{}` для Dell; `{top_level_bundles_count, rows_with_service_duration, max_hierarchy_depth}` для Cisco.
- **Cisco golden** — `golden/ccw_1_expected.jsonl` (26 строк), `golden/ccw_2_expected.jsonl` (82 строки).

---

## 3. Validation and Acceptance Criteria

- **Все тесты зелёные** — `pytest tests/ -v --tb=short` (138+ тестов) без failures.
- **UNKNOWN = 0** — unknown_count = 0 для dl1–dl5 (Dell) и ccw_1, ccw_2 (Cisco).
- **Dell regression не сломан** — test_regression.py зелёный после введения адаптеров.
- **Cisco golden покрывает 108 строк** — ccw_1 (26) + ccw_2 (82).
- **vendor_stats присутствует** — для всех прогонов в run_summary.json.

---

## 4. Known Limitations (Tech Debt)

- `datetime.utcnow()` deprecation warning (Python 3.12+).
- openpyxl style warning при записи annotated Excel.
- `sku` matching — только skus[0] (MVP; при multi-SKU строках расширить логику).
- Нет formal schema versioning для output JSON.
- Нет формального hw_type taxonomy abstraction (vendor-specific).

---

## 5. Out of Scope / Deferred

Следующее **не является** частью baseline v1.2.0:

- **Formal data contract versioning** — JSON Schema + автоматическая валидация output; запланировано как опциональный следующий шаг.
- **Унификация taxonomy device_type / hw_type** — абстракция hw_type taxonomy между вендорами.
- **Abstract vendor plugin architecture** — автообнаружение вендоров из файловой системы.
- **Расширение на Lenovo / HPE / Huawei** — за рамками текущего scope.

---

## 6. Next Directions (на выбор)

A) Formal data contract (JSON Schema + versioning)  
B) Унификация taxonomy device_type / hw_type  
C) Abstract vendor plugin architecture  
D) CI/CD стандартизация  
E) Масштабирование на Lenovo / HPE / Huawei  

---

## 7. Reference Documents

- [BASELINE_v1.1.0.md](BASELINE_v1.1.0.md) — предыдущий baseline (Dell MVP + hw_type).
- [TECHNICAL_OVERVIEW.md](TECHNICAL_OVERVIEW.md) — актуальный обзор архитектуры (multivendor).
- [../docs/schemas/DATA_CONTRACTS.md](../schemas/DATA_CONTRACTS.md) — схемы всех output-форматов.
- [../README.md](../../README.md) — установка, CLI, артефакты, vendor support.

---

*End of Baseline v1.2.0*

