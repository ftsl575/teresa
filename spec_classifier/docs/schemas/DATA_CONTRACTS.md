# Контракты данных — spec_classifier

## 1. Введение

Data contracts задают точные форматы выходных артефактов пайплайна. Они нужны для детерминизма, регрессионных тестов (golden) и аудита. Изменение контракта без обновления документации и тестов недопустимо.

---

## 2. classification.jsonl

- **Формат:** JSONL, UTF-8; одна строка — один JSON-объект.
- **Поля:**

| Поле | Тип | Обязательность | Семантика |
|------|-----|----------------|-----------|
| source_row_index | int \| null | да | 1-based номер строки в Excel; null только при legacy-пути. |
| row_kind | string | да | "ITEM" \| "HEADER". |
| entity_type | string \| null | да | BASE, HW, CONFIG, SOFTWARE, SERVICE, LOGISTIC, NOTE, UNKNOWN; null для HEADER. |
| state | string \| null | да | PRESENT, ABSENT, DISABLED; null для HEADER. |
| matched_rule_id | string | да | Идентификатор правила или HEADER-SKIP, UNKNOWN-000. |
| device_type | string \| null | да | Заполняется только для ITEM с matched_rule_id != UNKNOWN-000 и entity_type HW/LOGISTIC. Иначе null. |
| hw_type | string \| null | да | Заполняется для ITEM с entity_type HW при разрешении; иначе null. |
| warnings | array of string | да | Обычно []; при неразрешённом hw_type для HW — например ["hw_type unresolved for HW row"]. |

**device_type** (расширяемый словарь; значения определяются правилами вендора):
- Dell: power_cord, sfp_cable, storage_nvme, storage_ssd, psu, nic, raid_controller, hba, cpu
- Cisco: fan, transceiver, cable, psu, power_cord
- HPE: cpu, ram, blank_filler, storage_nvme, storage_ssd, storage_hdd, hba, raid_controller, nic, transceiver, fiber_cable, cable, gpu, riser, rail, drive_cage, backplane, fan, heatsink, bezel, battery, accessory, psu, power_cord

Источник истины — секция `device_type_rules` в `rules/<vendor>_rules.yaml`. Новые значения при добавлении вендора — MINOR-изменение по правилам стабильности (раздел 7).

**applies_to scope** (определяется в `rules/<vendor>_rules.yaml`):
- `device_type_rules.applies_to: [HW, LOGISTIC, BASE]` — `device_type` назначается только для строк с этими `entity_type`.
- `hw_type_rules.applies_to: [HW]` — `hw_type` назначается только для строк с `entity_type = HW`.

**hw_type** (25 значений): server, switch, storage_system, wireless_ap, cpu, memory, gpu, storage_drive, storage_controller, hba, backplane, io_module, network_adapter, transceiver, cable, psu, fan, heatsink, riser, chassis, rail, blank_filler, management, tpm, accessory.

**unknown_rows.csv** — производный артефакт: только строки с entity_type = UNKNOWN. Колонки: source_row_index, option_id, module_name, option_name, skus, qty, option_price, matched_rule_id. Кодировка UTF-8-sig. option_id заполняется из NormalizedRow.option_id (для HPE — полный Product #; для Dell/Cisco — пустая строка если отсутствует).

**cleaned_spec.xlsx** — фильтрованная спецификация: только ITEM-строки с entity_type из config cleaned_spec.include_types и (опционально) state PRESENT. Колонки: Group Name, Group ID, Module Name, Option Name, SKUs, Qty, Option ID, Unit Price, Device Type, HW Type, Entity Type, State.

---

## 3. rows_raw.json

- **Формат:** один JSON-массив объектов (list of dict).
- Поля каждого объекта соответствуют столбцам исходного листа плюс `__row_index__` (int, 1-based). Значения не нормализованы (как после парсера). NaN заменяются на null.

---

## 4. rows_normalized.json

- **Формат:** list of NormalizedRow-объектов (сериализованы в dict).
- **Поля:** source_row_index (int), row_kind (str), group_name (str | null), group_id (str | null), product_name (str | null), module_name (str), option_name (str), option_id (str | null), skus (list[str]), qty (int, default 1 при пустом/отсутствующем значении), option_price (float).

Vendor Extension (Cisco-only, additive):

Для Cisco прогонов к объекту добавляются поля, если значение семантически присутствует (не null и не пустая строка). Значения `false`, `0`, `0.0` считаются валидными и записываются. Поля: `line_number` (str), `bundle_id` (str), `is_top_level` (bool), `is_bundle_root` (bool), `parent_line_number` (str | null), `service_duration_months` (int | null), `smart_account_mandatory` (bool), `lead_time_days` (int | null), `unit_net_price` (float), `disc_pct` (float), `extended_net_price` (float).

Vendor Extension (HPE-only, additive):

Для HPE прогонов к объекту добавляются поля, если значение семантически присутствует. Поля: `product_type` (str — значение из колонки `Product Type`, например `"HW"`), `extended_price` (float — из `Extended List Price (USD)`), `lead_time` (str — из `Estimated Availability Lead Time`), `config_name` (str — из `Config Name`), `is_factory_integrated` (bool — `true` когда `option_name == "Factory Integrated"`). Поля с пустыми строками или `0.0` не сериализуются (аналогично Cisco-правилу).

---

## 5. run_summary.json

- **Поля:** total_rows (int), header_rows_count (int), item_rows_count (int), entity_type_counts (dict), state_counts (dict), unknown_count (int), rules_stats (dict), device_type_counts (dict), hw_type_counts (dict), hw_type_null_count (int), rules_file_hash (str, hex), input_file (str), run_timestamp (str, ISO), vendor_stats (dict). Все поля присутствуют после прогона.

`vendor_stats` — всегда присутствует. Для Dell: `{}`. Для Cisco: `{"top_level_bundles_count": int, "rows_with_service_duration": int, "max_hierarchy_depth": int}`. Для HPE: `{"factory_integrated_count": int}` (или `{}` если пусто).

---

## 6. golden/<stem>_expected.jsonl

- Тот же набор полей, что сравнивается в регрессии: `source_row_index`, `row_kind`, `entity_type`, `state`, `matched_rule_id`, `device_type`, `hw_type`, `skus`. Регрессионный тест сравнивает построчно; при изменении правил golden обновляется через `--save-golden` или `--update-golden` с явным ревью diff.

---

## 7. audit_report.json

Генерируется `batch_audit.py --output-dir <dir>`. Файл создаётся рядом с `<dir>`.

- **Формат:** один JSON-объект.
- **Поля верхнего уровня:**

| Поле | Тип | Описание |
|------|-----|----------|
| `meta` | object | Метаданные прогона: `run_date`, `model`, `total_tokens`, `tokens_in`, `tokens_out`, `cost_usd`. |
| `stats` | object | Агрегированная статистика: `total_files`, `total_rows`, `ok`, `issues`, `by_tag`, `by_vendor`, `by_file`. |
| `bugs` | array | Паттерны AI_MISMATCH, сортированные по типу: `REAL_BUG` (device_mismatch ≥3 или ≥2 из разных файлов) → `FALSE_POSITIVE` (entity_mismatch в fp_patterns) → `REVIEW_NEEDED`. Каждый элемент: `type`, `pattern`, `count`, `vendors`, `examples`, `fix_target`. |
| `yaml_candidates` | array | AI_SUGGEST паттерны: `device_type`, `count`, `vendors`, `note`. |
| `rule_issues` | array | E-code breakdown: `code`, `count`, `vendors`, `examples`. |
| `claude_prompt` | string | Готовый промпт для Claude с описанием найденных проблем. |
| `clusters` | object | Присутствует только после запуска `cluster_audit.py`. Поля: `total_candidates`, `total_clusters`, `clusters` (массив кластеров из `cluster_summary.xlsx`). |

---

## 8. cluster_summary.xlsx

Генерируется `cluster_audit.py --output-dir <dir>`.

- **Формат:** xlsx, одна строка — один кластер.
- **Колонки:**

| Колонка | Тип | Описание |
|---------|-----|----------|
| `cluster_id` | int | Идентификатор кластера (из HDBSCAN/KMeans). |
| `count` | int | Число строк в кластере. |
| `vendors` | str | Список вендоров через запятую. |
| `top_terms` | str | Топ-5 слов через запятую. |
| `proposed_device_type` | str | Эвристически предложенный device_type (или пусто). |
| `confidence` | str | `"heuristic"` или `"manual_review"`. |
| `example_1` / `example_2` / `example_3` | str | Первые 3 примера option_name из кластера. |
| `suggested_yaml_rule` | str | Предложенный regex-паттерн для нового правила. |

---

## 9. *_annotated_audited.xlsx

Генерируется `batch_audit.py` из `*_annotated.xlsx`.

- **Формат:** xlsx; исходная структура `*_annotated.xlsx` сохранена полностью + одна колонка `pipeline_check` справа.
- **Колонка `pipeline_check`:**
  - `"OK"` — строка прошла все E-проверки и (если включён AI) AI согласен.
  - Строка кодов через `;` — при наличии проблем, например: `"E8:hw_type_missing_on_hw; AI_MISMATCH:entity[pipeline:HW→ai:CONFIG]"`.
  - E-коды E1–E18: rule-based проверки (entity type, state logic, hw_type vocab, mapping consistency, etc.).
  - `AI_MISMATCH`: предсказание LLM расходится с пайплайном.
  - `AI_SUGGEST`: LLM предлагает device_type для строки без device_type.

---

## 10. Canonical Field Names

Таблица канонических имён полей, используемых в пайплайне, и их алиасов в различных вендорских форматах.

| Каноническое имя | Алиасы (источник) | Описание |
|---|---|---|
| `sku` | `skus`, `sku`, `part_number`, `product_#` | Номер части / артикул (SKU). Для HPE — `Product #` (до первого пробела). Для Dell/Cisco — `Part Number` или `skus`. |
| `module_name` | `module_name`, `module name`, `config_name` | Имя модуля / конфигурационной группы. Для HPE — из колонки `Config Name`. |
| `option_name` | `option_name`, `description`, `product_description`, `Option Name` | Описание строки (наименование опции/компонента). |
| `entity_type` | `entity_type`, `Entity Type` | Классифицированный тип строки: BASE, HW, CONFIG, SOFTWARE, SERVICE, LOGISTIC, NOTE, UNKNOWN. |
| `device_type` | `device_type` | Детальный тип устройства (cpu, ram, psu, power_cord, …). Только для ITEM-строк с entity_type в applies_to. |
| `hw_type` | `hw_type` | Нормализованный аппаратный тип из HW_TYPE_VOCAB (25 значений). Только для HW-строк. |
| `row_kind` | `row_kind` | Тип строки: `"ITEM"` (данные) или `"HEADER"` (заголовок / разделитель). |

### Canonical Field Names

Следующие имена полей считаются каноническими и используются
во всех выходных артефактах Teresa:

- vendor
- option_name
- entity_type
- device_type
- hw_type
- pipeline_check
- rule_id
- state
- confidence

Требования:
- имена должны совпадать во всех Excel / JSON / audit outputs
- любые vendor-specific поля должны добавляться отдельно
  и не менять канонические имена

Примечание:
canonical fields используются в:
- annotated_source.xlsx
- classification.jsonl
- audit_report.json
- cluster_summary.xlsx

---

## 11. Правила стабильности

- **MAJOR:** удаление поля из classification.jsonl, изменение типа поля, изменение семантики entity_type/state (новые значения enum без обратной совместимости).
- **MINOR:** добавление нового поля, новое значение enum, новые поля в run_summary.
- **PATCH:** изменение matched_rule_id без изменения entity_type/state (например уточнение rule_id при той же классификации).
