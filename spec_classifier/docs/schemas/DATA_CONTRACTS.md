# Контракты данных — Dell Specification Classifier

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

**device_type** (полный список): power_cord, sfp_cable, storage_nvme, storage_ssd, psu, nic, raid_controller, hba, cpu.

**hw_type** (20 значений): cpu, ram, ssd, hdd, nvme, storage_controller, psu, fan, cpu_heatsink, network_adapter, riser, gpu, tpm, chassis, cable, management, motherboard, mounting_kit, backplane, blank.

---

## 3. rows_raw.json

- **Формат:** один JSON-массив объектов (list of dict).
- Поля каждого объекта соответствуют столбцам исходного листа плюс `__row_index__` (int, 1-based). Значения не нормализованы (как после парсера). NaN заменяются на null.

---

## 4. rows_normalized.json

- **Формат:** list of NormalizedRow-объектов (сериализованы в dict).
- **Поля:** source_row_index (int), row_kind (str), group_name (str | null), group_id (str | null), product_name (str | null), module_name (str), option_name (str), option_id (str | null), skus (list[str]), qty (int), option_price (float).

---

## 5. run_summary.json

- **Поля:** total_rows (int), header_rows_count (int), item_rows_count (int), entity_type_counts (dict), state_counts (dict), unknown_count (int), rules_stats (dict), device_type_counts (dict), hw_type_counts (dict), hw_type_null_count (int), rules_file_hash (str, hex), input_file (str), run_timestamp (str, ISO). Все поля присутствуют после прогона.

---

## 6. golden/<stem>_expected.jsonl

- Тот же набор полей, что сравнивается в регрессии: source_row_index, row_kind, entity_type, state, matched_rule_id, device_type, hw_type, skus. Регрессионный тест сравнивает построчно; при изменении правил golden обновляется через `--save-golden` или `--update-golden` с явным ревью diff.

---

## 7. Правила стабильности

- **MAJOR:** удаление поля из classification.jsonl, изменение типа поля, изменение семантики entity_type/state (новые значения enum без обратной совместимости).
- **MINOR:** добавление нового поля, новое значение enum, новые поля в run_summary.
- **PATCH:** изменение matched_rule_id без изменения entity_type/state (например уточнение rule_id при той же классификации).
