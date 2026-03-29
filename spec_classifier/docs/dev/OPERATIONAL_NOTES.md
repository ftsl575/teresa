# Операционные заметки — spec_classifier (teresa)

## 1. Одиночный прогон

```bash
python main.py --input path/to/file.xlsx --output-dir output
python main.py --input "C:\Users\G\Desktop\INPUT\ccw_1.xlsx" --vendor cisco
```

Результат: папка `{vendor}_run/run-YYYY-MM-DD__HH-MM-SS-<stem>/` с полным набором артефактов.

---

## 2. Batch-прогон

```bash
python main.py --batch-dir "C:\Users\G\Desktop\INPUT"
```

Создаётся: для каждого .xlsx в директории — своя папка `run-YYYY-MM-DD__HH-MM-SS-<stem>/`, плюс одна папка `run-YYYY-MM-DD__HH-MM-SS-TOTAL/`.

---

## 3. TOTAL-папка

Содержит агрегированные презентационные файлы по всем обработанным в сессии файлам: `<stem>_annotated.xlsx`, `<stem>_branded.xlsx`, `<stem>_cleaned_spec.xlsx`. Используется для передачи клиенту или консолидации одной сессии. Для Cisco и HPE прогонов `<stem>_branded.xlsx` не копируется (файл не создаётся).

**Важно:** `batch_audit.py` автоматически исключает TOTAL-папки из обработки (`-TOTAL` в имени родительской папки). Это предотвращает двойной счёт строк в `audit_report.json`.

---

## 4. Именование папок прогонов

Единственный канонический формат в коде: **run-YYYY-MM-DD__HH-MM-SS-<stem>** (например run-2026-02-26__06-09-53-dl1). При коллизии (одинаковая секунда) добавляется суффикс _1, _2, … Batch TOTAL: **run-YYYY-MM-DD__HH-MM-SS-TOTAL**.

---

## 5. Политика хранения артефактов

- **output/** — не в git.
- **rows_raw.json**, **rows_normalized.json** — отладочные; можно удалять после проверки.
- **run_summary.json**, **classification.jsonl** — хранить для аудита при необходимости.
- **unknown_rows.csv** — просматривать после каждого прогона; при росте unknown_count — дорабатывать правила.
- **golden/*.jsonl** — в git; обновлять только осознанно после изменения правил/логики.

---

## 6. Работа с новым датасетом

1. Положить xlsx в `C:\Users\G\Desktop\INPUT\` (например dl5.xlsx).
2. Запустить пайплайн: `python main.py --input "C:\Users\G\Desktop\INPUT\dl5.xlsx"`.
3. Проверить unknown_rows.csv и run_summary.json.
4. При необходимости добавить правила в dell_rules.yaml и повторить.
5. Сгенерировать golden: `python main.py --input "C:\Users\G\Desktop\INPUT\dl5.xlsx" --save-golden`.
6. Добавить новый файл (dlN) в parametrize регрессии и другие тесты при необходимости.
7. Запустить pytest tests/ -v и закоммитить изменения.

Новый Cisco датасет (ccwN.xlsx):

1. Положить файл в `C:\Users\G\Desktop\INPUT\ccw_N.xlsx`.
2. Запустить `python main.py --input "C:\Users\G\Desktop\INPUT\ccw_N.xlsx" --vendor cisco`.
3. Проверить `unknown_rows.csv`. Цель — `unknown_count = 0`.
4. При `unknown_count > 0`: добавить правила в `rules/cisco_rules.yaml`, повторить.
5. `python main.py --input "C:\Users\G\Desktop\INPUT\ccw_N.xlsx" --vendor cisco --save-golden`
6. Добавить `ccw_N` в регрессионный тест; `pytest tests/ -v`.

Новый HPE датасет (hpN.xlsx):

1. Положить BOM-файл в `C:\Users\G\Desktop\INPUT\hpe\hpN.xlsx` (лист «BOM», колонки: Product #, Description, Qty, Unit Price).
2. Запустить `python main.py --input "C:\Users\G\Desktop\INPUT\hpe\hpN.xlsx" --vendor hpe`.
3. Проверить `unknown_rows.csv`. Цель — `unknown_count = 0`.
4. При `unknown_count > 0`: добавить правила в `rules/hpe_rules.yaml`; запустить повторно.
5. `python main.py --input "C:\Users\G\Desktop\INPUT\hpe\hpN.xlsx" --vendor hpe --save-golden`
6. Добавить `hpN` в `test_regression_hpe.py` и `test_unknown_threshold_hpe.py`; `pytest tests/test_regression_hpe.py tests/test_unknown_threshold_hpe.py -v`.

---

## 7. Полный прогон (пайплайн + аудит + кластеризация)

Скрипт-запускалка: `run_audit.ps1` в корне репо (`C:\Users\G\Desktop\teresa\run_audit.ps1`).

```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\G\Desktop\teresa\run_audit.ps1
```

Выполняет по порядку:
1. Пайплайн для всех трёх вендоров (dell → hpe → cisco)
2. `batch_audit.py` с AI (`--model gpt-4o-mini`)
3. `cluster_audit.py`

Для быстрой проверки без AI (только E-коды, без токенов) — добавить `--no-ai` в строку `batch_audit.py` внутри скрипта.

> **Примечание:** PowerShell не поддерживает вставку многострочного блока с `&&` — команды выполняются в обратном порядке. Поэтому команды оформлены в `.ps1` скрипт.

---

## Known Tech Debt: batch_audit.py vendor-specific hardcoding

batch_audit.py содержит vendor-specific логику в следующих местах:

1. **DEVICE_TYPE_MAP** (строки 56–79) — device_type→hw_type маппинг per vendor
2. **validate_row() state logic** (строки 346–360) — ветки `if vendor == "dell"` / `"hpe"` / `"cisco"`
3. **LLM_SYSTEM prompt** (строки 90–110) — vendor-aware текст промпта
4. **Known FP cases** (строки 900–971) — vendor-tagged false positive паттерны
5. **fp_patterns / комментарии** — vendor-specific логика в комментариях

Текущее состояние: 3 вендора (dell, cisco, hpe). Работоспособно.

Триггер рефакторинга: до добавления 4-го вендора.

Рекомендуемое решение: вынести vendor-specific конфигурации в YAML-файлы или adapter-registry, чтобы добавление вендора не требовало правок в batch_audit.py.

Источник: audit_1G P1-6.
