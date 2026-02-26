# Руководство пользователя — Dell Specification Classifier

## 1. Назначение

Система классифицирует строки Dell-спецификаций в формате Excel: определяет тип сущности (BASE, HW, SOFTWARE и др.), состояние (PRESENT/ABSENT/DISABLED), тип устройства и тип железа. Результат — детерминированный; классификация выполняется по правилам из YAML и regex, без ML. На выходе — папка прогона с JSON/CSV/Excel артефактами и очищенной/аннотированной/брендированной спецификацией.

---

## 2. Поддерживаемые входные файлы

- **Формат:** `.xlsx`, первый лист.
- **Строка заголовка:** в первых 20 строках должна быть ячейка с текстом `"Module Name"` (обязательно). По ней определяется заголовок таблицы.
- **Ожидаемые столбцы:** Module Name, Option Name, SKUs, Qty, Option List Price.
- **Опциональные:** Group Name, Group ID, Product Name, Option ID.
- **Ограничения:** один лист, один файл за запуск в single-file режиме; для нескольких файлов — режим `--batch-dir`.

---

## 3. Запуск и результаты

Минимальный пример:

```bash
cd dell_spec_classifier
python main.py --input test_data/dl1.xlsx
```

Результат — папка `output/run-YYYY-MM-DD__HH-MM-SS-dl1/` (или с суффиксом `_1`, `_2` при коллизии). В ней — все артефакты прогона. Итоги смотрите в `run_summary.json` и `unknown_rows.csv`.

---

## 4. Артефакты прогона

| Файл | Описание |
|------|----------|
| `classification.jsonl` | Одна строка — один JSON с полями классификации по каждой строке (entity_type, state, device_type, hw_type, matched_rule_id и др.). |
| `run_summary.json` | Сводка: total_rows, entity_type_counts, state_counts, unknown_count, device_type_counts, hw_type_counts, rules_file_hash, input_file, run_timestamp. |
| `cleaned_spec.xlsx` | Отфильтрованная спецификация: типы из конфига (BASE, HW, SOFTWARE, SERVICE), только PRESENT (если `include_only_present: true`). |
| `<stem>_annotated.xlsx` | Исходный файл + 4 колонки: Entity Type, State, device_type, hw_type. Все строки сохранены. |
| `<stem>_branded.xlsx` | Брендированная спецификация: группировка по BASE (сервер) и секциям по entity_type; блок «Не установлено» для ABSENT при необходимости. |
| `unknown_rows.csv` | Строки, для которых не сработало ни одно правило (entity_type = UNKNOWN). Ревизия после каждого прогона. |
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
- **hw_type:** тип железа для HW-строк. 20 значений: cpu, ram, ssd, hdd, nvme, storage_controller, psu, fan, cpu_heatsink, network_adapter, riser, gpu, tpm, chassis, cable, management, motherboard, mounting_kit, backplane, blank. Для не-HW или неразрешённых HW — null.
- **matched_rule_id:** идентификатор сработавшего правила (например HW-002, SERVICE-001). UNKNOWN-000 — совпадений нет.
- **warnings:** список предупреждений (например «hw_type unresolved for HW row»); обычно пуст.

---

## 7. Рекомендованный рабочий процесс

1. Запустить прогон: `python main.py --input test_data/dl1.xlsx`.
2. Проверить `unknown_rows.csv`.
3. Если `unknown_count > 0`: добавить или скорректировать правило в `dell_rules.yaml` → запустить снова → проверить diff в классификации.
4. При принятии изменений: `python main.py --input test_data/dl1.xlsx --save-golden` и `pytest tests/test_regression.py -v`.
5. Если `unknown_count = 0` и регрессия зелёная — готово.

---

## 8. cleaned_spec.xlsx

Включаются только ITEM-строки с entity_type из `config.cleaned_spec.include_types` (по умолчанию BASE, HW, SOFTWARE, SERVICE). При `include_only_present: true` — только строки с state PRESENT. Колонки: Module Name, Option Name, SKUs, Qty, Option List Price, Entity Type, State. HEADER и остальные типы/состояния в файл не попадают.

---

## 9. branded_spec.xlsx

Структура: сначала BASE-строка (сервер), затем секции по entity_type. Внутри секций — сгруппированные позиции. Может быть блок «Не установлено» для ABSENT-строк, если это предусмотрено выводом. Файл предназначен для презентации клиенту.

---

## 10. annotated.xlsx

Исходный лист без удаления строк; добавлены 4 колонки: Entity Type, State, device_type, hw_type. Соответствие строке листа — по source_row_index (1-based). Все строки сохранены для аудита и ручной проверки.
