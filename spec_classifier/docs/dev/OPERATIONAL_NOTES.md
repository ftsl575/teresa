# Операционные заметки — Dell Specification Classifier

## 1. Одиночный прогон

```bash
python main.py --input path/to/file.xlsx --output-dir output
python main.py --input test_data/ccw_1.xlsx --vendor cisco --output-dir output
```

Результат: папка `output/run-YYYY-MM-DD__HH-MM-SS-<stem>/` с полным набором артефактов.

---

## 2. Batch-прогон

```bash
python main.py --batch-dir test_data --output-dir output
```

Создаётся: для каждого .xlsx в директории — своя папка `run-YYYY-MM-DD__HH-MM-SS-<stem>/`, плюс одна папка `run-YYYY-MM-DD__HH-MM-SS-TOTAL/`.

---

## 3. TOTAL-папка

Содержит агрегированные презентационные файлы по всем обработанным в сессии файлам: `<stem>_annotated.xlsx`, `<stem>_branded.xlsx`, `<stem>_cleaned_spec.xlsx`. Используется для передачи клиенту или консолидации одной сессии. Для Cisco прогонов `<stem>_branded.xlsx` не копируется (файл не создаётся).

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

1. Скопировать xlsx в test_data/ (например dl5.xlsx).
2. Запустить пайплайн: `python main.py --input test_data/dl5.xlsx`.
3. Проверить unknown_rows.csv и run_summary.json.
4. При необходимости добавить правила в dell_rules.yaml и повторить.
5. Сгенерировать golden: `python main.py --input test_data/dl5.xlsx --save-golden`.
6. Добавить новый файл (dlN) в parametrize регрессии и другие тесты при необходимости.
7. Запустить pytest tests/ -v и закоммитить изменения.

Новый Cisco датасет (ccwN.xlsx):

1. Скопировать файл в `test_data/ccw_N.xlsx`.
2. Запустить `python main.py --input test_data/ccw_N.xlsx --vendor cisco`.
3. Проверить `unknown_rows.csv`. Цель — `unknown_count = 0`.
4. При `unknown_count > 0`: добавить правила в `rules/cisco_rules.yaml`, повторить.
5. `python main.py --input test_data/ccw_N.xlsx --vendor cisco --save-golden`
6. Добавить `ccw_N` в регрессионный тест; `pytest tests/ -v`.
