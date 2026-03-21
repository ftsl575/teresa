# Руководство пользователя — spec_classifier

## 1. Назначение

Система классифицирует строки спецификаций (Dell, Cisco CCW и HPE QuoteBuilder BOM) в формате Excel: определяет тип сущности (BASE, HW, SOFTWARE и др.), состояние (PRESENT/ABSENT/DISABLED), тип устройства и тип железа. Результат — детерминированный; классификация выполняется по правилам из YAML и regex, без ML. На выходе — папка прогона с JSON/CSV/Excel артефактами и очищенной/аннотированной/брендированной спецификацией.

---

## 2. Поддерживаемые входные файлы

- **Формат:** `.xlsx`, первый лист.
- **Строка заголовка:** в первых 20 строках должна быть ячейка с текстом `"Module Name"` (обязательно). По ней определяется заголовок таблицы.
- **Ожидаемые столбцы:** Module Name, Option Name, SKUs, Qty, Option List Price.
- **Опциональные:** Group Name, Group ID, Product Name, Option ID.
- **Ограничения:** один лист, один файл за запуск в single-file режиме; для нескольких файлов — режим `--batch-dir`.

**Cisco CCW (`--vendor cisco`):**

- Формат: `.xlsx`, лист `"Price Estimate"` (строго, без fallback).
- Строка заголовка: ищется по одновременному наличию `"Line Number"` и `"Part Number"` в первых 100 строках.
- Ожидаемые столбцы: Line Number, Part Number, Description, Qty, Unit List Price, Unit Net Price, Disc(%), Extended Net Price, Service Duration (Months), Smart Account Mandatory, Estimated Lead Time (Days).
- Особенности: trailing `=` в Part Number удаляется автоматически; пустой Part Number внутри данных допустим (конец данных определяется по последней непустой ячейке Part Number).

**HPE QuoteBuilder BOM (`--vendor hpe`):**

- Формат: `.xlsx`, лист `"BOM"` (строго, без fallback).
- Строка заголовка: строго первая строка листа (row 0), no preamble.
- Ожидаемые столбцы: Product #, Product Description, Qty, Unit Price (USD), Config Name. Опционально: Product Type, Extended List Price (USD), Estimated Availability Lead Time.
- Особенности: `Product #` используется полностью как `option_id`; базовый SKU (до первого пробела) записывается в `skus[0]`. Колонка `Config Name` отображается в `group_name` и `module_name`. Строка `"Factory Integrated"` классифицируется как `CONFIG` (правило `CONFIG-H-001`). Конец данных: первая строка, у которой первая непустая ячейка = `"total"` (без учёта регистра).

---

## 3. Запуск и результаты

Минимальный пример:

```bash
cd spec_classifier
python main.py --input "C:\Users\G\Desktop\INPUT\dl1.xlsx"
```

Результат — папка `output/run-YYYY-MM-DD__HH-MM-SS-dl1/` (или с суффиксом `_1`, `_2` при коллизии). В ней — все артефакты прогона. Итоги смотрите в `run_summary.json` и `unknown_rows.csv`.

---

## 4. Артефакты прогона

| Файл | Описание |
|------|----------|
| `classification.jsonl` | Одна строка — один JSON с полями классификации по каждой строке (entity_type, state, device_type, hw_type, matched_rule_id и др.). |
| `run_summary.json` | Сводка: total_rows, entity_type_counts, state_counts, unknown_count, device_type_counts, hw_type_counts, rules_file_hash, input_file, run_timestamp. |
| `cleaned_spec.xlsx` | Отфильтрованная спецификация: типы из конфига (BASE, HW, SOFTWARE, SERVICE), только PRESENT (если `include_only_present: true`). |
| `<stem>_annotated.xlsx` | Исходный файл + 5 колонок: Entity Type, State, device_type, hw_type, row_kind. Все строки сохранены. |
| `<stem>_branded.xlsx` | Брендированная спецификация: группировка по BASE (сервер) и секциям по entity_type; блок «Не установлено» для ABSENT при необходимости. ⚠️ Не создаётся для Cisco CCW прогонов. |
| `unknown_rows.csv` | Строки с entity_type = UNKNOWN. Колонки: source_row_index, option_id, module_name, option_name, skus, qty, option_price, matched_rule_id. Ревизия после каждого прогона. |
| `rows_raw.json` | Сырые строки после парсера (отладка). |
| `rows_normalized.json` | Нормализованные строки с row_kind (отладка). |
| `header_rows.csv` | Строки-разделители секций (HEADER). |
| `run.log` | Лог пайплайна для этого прогона. |

---

## 5. TOTAL-папка (batch mode)

При запуске с `--batch-dir` создаётся общая папка сессии: `output/run-YYYY-MM-DD__HH-MM-SS-TOTAL/`. В неё копируются три презентационных файла из каждого per-run каталога:

- `<stem>_cleaned_spec.xlsx`
- `<stem>_annotated.xlsx`
- `<stem>_branded.xlsx`

Используйте TOTAL для передачи клиенту или консолидации результатов одной сессии.

---

## 6. Интерпретация полей классификации

- **row_kind:** HEADER — разделитель секции (пустые Module Name, Option Name, SKUs); ITEM — позиция спецификации.
- **source_row_index:** 1-based номер строки в исходном Excel (для аудита и сопоставления с листом).
- **entity_type:** один из 8 типов. Примеры: BASE (Base, PowerEdge R660), SERVICE (ProSupport, Warranty), LOGISTIC (Shipping, Power Cord), SOFTWARE (Embedded Systems Management), NOTE (supports ONLY), CONFIG (No Cable, RAID Configuration), HW (Processor, Memory, Hard Drives), UNKNOWN (ни одно правило не сработало).
- **state:** PRESENT — опция присутствует; ABSENT — не установлена (например «No TPM», «No HDD», «Empty»); DISABLED — отключена (например «Disabled»).
- **device_type:** уточнение для HW/LOGISTIC. Значения: power_cord, sfp_cable, storage_nvme, storage_ssd, psu, nic, raid_controller, hba, cpu. Может быть null, если правило не назначило device_type.
- **hw_type:** тип железа для HW-строк. 25 значений (v2.0.0): server, switch, storage_system, wireless_ap, cpu, memory, gpu, storage_drive, storage_controller, hba, backplane, io_module, network_adapter, transceiver, cable, psu, fan, heatsink, riser, chassis, rail, blank_filler, management, tpm, accessory. Для не-HW или неразрешённых HW — null.
- **matched_rule_id:** идентификатор сработавшего правила (например HW-002, SERVICE-001). UNKNOWN-000 — совпадений нет.
- **warnings:** список предупреждений (например «hw_type unresolved for HW row»); обычно пуст.

---

## 7. Рекомендованный рабочий процесс

1. Запустить прогон: `python main.py --input "C:\Users\G\Desktop\INPUT\dl1.xlsx"`.
2. Проверить `unknown_rows.csv`.
3. Если `unknown_count > 0`: добавить или скорректировать правило в `dell_rules.yaml` → запустить снова → проверить diff в классификации.
4. При принятии изменений: `python main.py --input "C:\Users\G\Desktop\INPUT\dl1.xlsx" --save-golden` и `pytest tests/test_regression.py -v`.
5. Если `unknown_count = 0` и регрессия зелёная — готово.

Для Cisco CCW: шаги аналогичны, но с `--vendor cisco` и правилами в `rules/cisco_rules.yaml`. Цель — `unknown_count = 0` на `ccw_1` и `ccw_2`.

Для HPE: шаги аналогичны, но с `--vendor hpe` и правилами в `rules/hpe_rules.yaml`. Входные файлы рекомендуется хранить в `INPUT\hpe\`. Цель — `unknown_count = 0` на всех BOM-файлах (hp1–hp8).

```powershell
python main.py --vendor hpe --input "C:\Users\G\Desktop\INPUT\hpe\hp1.xlsx"
```

---

## 8. cleaned_spec.xlsx

Включаются только ITEM-строки с entity_type из `config.cleaned_spec.include_types` (по умолчанию BASE, HW, SOFTWARE, SERVICE). При `include_only_present: true` — только строки с state PRESENT. Колонки: Group Name, Group ID, Module Name, Option Name, SKUs, Qty, Option ID, Unit Price, Device Type, HW Type, Entity Type, State. HEADER и остальные типы/состояния в файл не попадают.

Для HPE: колонки Group Name / Group ID заполняются из `Config Name` (название конфигурации сервера). Это позволяет идентифицировать принадлежность строки к конкретному серверу в multi-config BOM.

---

## 9. branded_spec.xlsx

Структура: сначала BASE-строка (сервер), затем секции по entity_type. Внутри секций — сгруппированные позиции с колонками SKU, Option Name, Qty, Price. Может быть блок «Не установлено» для ABSENT-строк. Если в спецификации есть ITEM-строки до первого BASE, они выводятся в блоке «Позиции без привязки к серверу» (preamble). Файл предназначен для презентации клиенту. ⚠️ Не создаётся для Cisco CCW и HPE прогонов.

---

## 10. annotated.xlsx

Исходный лист без удаления строк; добавлены 5 колонок: Entity Type, State, device_type, hw_type, row_kind. Соответствие строке листа — по source_row_index (1-based). Все строки сохранены для аудита и ручной проверки.
