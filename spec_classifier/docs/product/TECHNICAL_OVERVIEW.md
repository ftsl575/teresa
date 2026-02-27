# Dell Specification Classifier — Technical Overview

Документ описывает **фактическую** реализацию проекта (код в репозитории). Источники: спецификация `dell_mvp_technical_spec.md`, код в `src/`, `main.py`, тесты в `tests/`, `config.yaml`, `README.md`.

---

## 1. Назначение системы

Система — **MVP-пайплайн** для классификации Dell-спецификаций в формате Excel:

- **Вход:** один Excel-файл (`.xlsx`) с таблицей спецификации (столбцы в том числе: Module Name, Option Name, SKUs, Qty, Option List Price).
- **Выход:**
  - папка прогона `output/run-YYYY-MM-DD__HH-MM-SS-<stem>/` с артефактами (JSON, CSV, Excel);
  - очищенная спецификация `cleaned_spec.xlsx` (только выбранные типы и состояние);
  - аннотированный исходный файл `<stem>_annotated.xlsx` (все строки + колонки Entity Type, State, device_type, hw_type);
  - брендированная спецификация `<stem>_branded.xlsx` (группировка по серверу и типам сущностей).

Классификация **детерминированная**, на основе правил из YAML (регулярные выражения по полям `module_name` и `option_name`). Строки делятся на **HEADER** (разделители) и **ITEM** (позиции); для ITEM задаются тип сущности (BASE, HW, SOFTWARE, SERVICE, LOGISTIC, NOTE, CONFIG, UNKNOWN) и состояние (PRESENT, ABSENT, DISABLED).

---

## 2. Архитектура пайплайна (по шагам)

Реализованная последовательность в `main.py`:

1. **Загрузка конфига** — `config.yaml` (UTF-8, `yaml.safe_load`). Путь к правилам берётся из `config["rules_file"]` (по умолчанию `rules/dell_rules.yaml`).
2. **Парсинг Excel** — `src.core.parser.parse_excel(filepath)`:
   - поиск строки заголовка по ячейке `"Module Name"` (`find_header_row`);
   - чтение листа с этим заголовком, удаление колонки `"Unnamed: 0"` при наличии;
   - каждая строка — dict с полями листа и `__row_index__` = номер строки в Excel (1-based): `pandas_idx + header_row_index + 2`.
3. **Нормализация** — для каждой сырой строки вызывается `src.core.normalizer.normalize_row(raw_row)`:
   - определение `row_kind`: HEADER, если пусты Module Name, Option Name и SKUs; иначе ITEM;
   - приведение типов (SKUs → список строк, Qty → int, Option List Price → float), пробелы и пустоты обрабатываются.
4. **Загрузка правил** — `src.rules.rules_engine.RuleSet.load(rules_path)` (YAML, UTF-8). Правила разложены по атрибутам: `base_rules`, `service_rules`, `logistic_rules`, `software_rules`, `note_rules`, `config_rules`, `hw_rules`, плюс `get_state_rules()` из `state_rules.absent_keywords`.
5. **Классификация** — для каждой нормализованной строки `src.core.classifier.classify_row(row, ruleset)`:
   - если `row_kind == HEADER` → результат с `entity_type=None`, `state=None`, `matched_rule_id="HEADER-SKIP"`;
   - иначе: сначала `detect_state(option_name, state_rules)` (PRESENT/ABSENT/DISABLED), затем проверка правил по приоритету: BASE → SERVICE → LOGISTIC → SOFTWARE → NOTE → CONFIG → HW; при отсутствии совпадений → UNKNOWN.
6. **Создание папки прогона** — создаётся `output/run-YYYY-MM-DD__HH-MM-SS-<stem>/` через `create_run_folder(output_dir, input_filename, stamp)`.
7. **Сохранение артефактов:**
   - `src.outputs.json_writer`: `save_rows_raw`, `save_rows_normalized`, `save_classification`, `save_unknown_rows`, `save_header_rows`;
   - `src.diagnostics.stats_collector`: `collect_stats(classification_results)` и `save_run_summary(stats, run_folder)`;
   - `src.outputs.excel_writer.generate_cleaned_spec(normalized_rows, classification_results, config, run_folder)` → `cleaned_spec.xlsx`;
   - `src.outputs.annotated_writer.generate_annotated_source_excel(...)` → `<stem>_annotated.xlsx`;
   - `src.outputs.branded_spec_writer.generate_branded_spec(...)` → `<stem>_branded.xlsx`.
   **Режим batch:** создаётся папка TOTAL через `create_total_folder()` и копирование трёх презентационных файлов через `copy_to_total()`.
8. **Опционально: golden** — при флагах `--save-golden` или `--update-golden` формируются строки в формате golden и запись в `golden/<stem>_expected.jsonl`; для `--update-golden` перед перезаписью запрашивается подтверждение (y/n).
9. **Логирование** — после создания папки прогона в корневой логгер добавляется `FileHandler(run_folder / "run.log")`. В stdout выводится краткий summary (total_rows, header_rows_count, item_rows_count, entity_type_counts, unknown_count, run_folder).

Ошибки: при отсутствии файла или невалидном YAML — сообщение в stderr и `exit(1)`; при исключении в пайплайне — `log.exception` и `return 1`.

---

## 3. Форматы входа/выхода

**Вход**

- **Excel:** первый лист, строка заголовка определяется по ячейке с текстом `"Module Name"`. Ожидаемые столбцы (после парсера): Module Name, Option Name, SKUs, Qty, Option List Price и др. (наличие Group Name, Group ID, Product Name, Option ID опционально). Колонка `Unnamed: 0` при чтении удаляется.
- **Конфиг:** `config.yaml` — ключи `cleaned_spec` (в т.ч. `include_types`, `include_only_present`, `exclude_headers`) и `rules_file`.

**Выход (в `run_folder`)**

| Файл | Описание |
|------|----------|
| `rows_raw.json` | Сырые строки (list of dict), как после парсера; `json.dump(..., indent=2, ensure_ascii=False)`. |
| `rows_normalized.json` | Нормализованные строки с `row_kind` и полями `NormalizedRow`. |
| `classification.jsonl` | Одна строка — один JSON: `row_kind`, `entity_type`, `state`, `matched_rule_id`, `warnings`. |
| `unknown_rows.csv` | Только ITEM-строки с `entity_type == UNKNOWN`; кодировка UTF-8-sig. |
| `header_rows.csv` | Только строки с `row_kind == HEADER`; UTF-8-sig. |
| `run_summary.json` | Агрегаты: `total_rows`, `header_rows_count`, `item_rows_count`, `entity_type_counts`, `state_counts`, `unknown_count`, `rules_stats`, `device_type_counts`, `hw_type_counts`, `hw_type_null_count`, `rules_file_hash`, `input_file`, `run_timestamp`. |
| `cleaned_spec.xlsx` | Подмножество ITEM: типы из `config["cleaned_spec"]["include_types"]`, при `include_only_present` только state PRESENT. Колонки: Module Name, Option Name, SKUs, Qty, Option List Price, Entity Type, State. |
| `<stem>_annotated.xlsx` | Копия исходного листа (построчно), добавлены четыре колонки: Entity Type, State, device_type, hw_type; строки не удаляются; запись с `header=False`. |
| `<stem>_branded.xlsx` | Брендированная спецификация: группировка по BASE (сервер) и секциям по типу сущности; из `src.outputs.branded_spec_writer.py`. |
| `run.log` | Текстовый лог этапов пайплайна. |

Типы сущностей в коде: `EntityType` в `src/core/classifier.py` — BASE, HW, CONFIG, SOFTWARE, SERVICE, LOGISTIC, NOTE, UNKNOWN. Состояния: `State` в `src/core/state_detector.py` — PRESENT, ABSENT, DISABLED.

---

## 4. CLI и режимы работы

Точка входа: `main.py`. Аргументы (argparse):

| Аргумент | Обязательность | Описание |
|----------|----------------|----------|
| `--input` | обязателен в single-file режиме | Путь к входному Excel. |
| `--batch-dir` | обязателен в batch режиме | Директория с .xlsx; обрабатываются все файлы; создаются per-run папки и папка TOTAL. |
| `--config` | нет (по умолчанию `config.yaml`) | Путь к YAML-конфигу. |
| `--output-dir` | нет (по умолчанию `output`) | Каталог для подпапок прогонов. |
| `--save-golden` | флаг | После пайплайна записать результат в `golden/<stem>_expected.jsonl` без подтверждения. |
| `--update-golden` | флаг | То же, но с запросом «Overwrite golden? [y/N]:»; при не-y запись не выполняется. |

Именование папок прогонов: **одиночный запуск** — `run-YYYY-MM-DD__HH-MM-SS-<stem>/`; **batch** — те же папки по файлам плюс `run-YYYY-MM-DD__HH-MM-SS-TOTAL/` с агрегированными презентационными файлами.

Пути к файлам разрешаются относительно текущей рабочей директории, если не заданы абсолютные. Примеры:

```bash
python main.py --input test_data/dl1.xlsx
python main.py --input test_data/dl1.xlsx --save-golden
python main.py --input test_data/dl1.xlsx --update-golden
```

---

## 5. Golden / Regression

**Формат golden-файла** — JSONL в `golden/<stem>_expected.jsonl` (например, `golden/dl1_expected.jsonl`). Одна строка — один JSON-объект с полями:

- `source_row_index` (int)
- `row_kind` ("ITEM" | "HEADER")
- `entity_type` (строка или null)
- `state` (строка или null)
- `matched_rule_id` (строка)
- `device_type` (строка или null)
- `skus` (список строк)

Генерация: при запуске с `--save-golden` или после подтверждения при `--update-golden` в `main.py` вызываются `_build_golden_rows(normalized_rows, classification_results)` и `_save_golden(golden_rows, golden_path)`.

**Регрессионные тесты** — `tests/test_regression.py`. Параметризация по имени файла (`dl1.xlsx`, `dl2.xlsx`). Для каждого файла:

- если нет `test_data/<filename>` — тест пропускается;
- если нет `golden/<stem>_expected.jsonl` — тест пропускается с сообщением про `--save-golden`;
- иначе: в тесте выполняется тот же пайплайн (parse → normalize → load RuleSet → classify), строится список записей в формате golden и построчно сравнивается с загруженным golden по полям `entity_type`, `state`, `matched_rule_id`, `skus`; при расхождении — падение с выводом номера строки и отличий.

---

## 6. Annotated export

Реализация: `src/outputs/annotated_writer.py`, функция `generate_annotated_source_excel(raw_rows, normalized_rows, classification_results, original_excel_path, run_folder)`.

- Исходный Excel читается через `pandas.read_excel(..., header=None)`. Строка заголовка находится через `find_header_row(original_excel_path)`.
- К таблице добавляются четыре колонки: "Entity Type", "State", "device_type", "hw_type". В строке заголовка в этих ячейках пишутся соответствующие подписи.
- Для остальных строк результат классификации берётся по `source_row_index` (1-based номер строки в Excel). Если `row_kind == ITEM` — в новые ячейки пишутся `entity_type.value`, `state.value`, `device_type`, `hw_type`; иначе — пусто.
- Результат сохраняется в `run_folder / "<stem>_annotated.xlsx"` через `to_excel(..., index=False, header=False, engine="openpyxl")`, чтобы число строк совпадало с исходным файлом.

Вызов выполняется в `main.py` после `generate_cleaned_spec`.

---

## 7. Структура проекта

Реальная структура по репозиторию:

```
spec_classifier/
├── main.py                    # CLI и оркестрация пайплайна
├── config.yaml                # cleaned_spec, rules_file
├── requirements.txt
├── README.md
├── CHANGELOG.md
├── rules/
│   └── dell_rules.yaml        # version, state_rules.absent_keywords, base_rules, service_rules, logistic_rules, software_rules, note_rules, config_rules, hw_rules
├── src/
│   ├── core/
│   │   ├── parser.py          # find_header_row, parse_excel
│   │   ├── normalizer.py      # RowKind, NormalizedRow, detect_row_kind, normalize_row
│   │   ├── classifier.py      # EntityType, ClassificationResult, classify_row
│   │   └── state_detector.py   # State, detect_state
│   ├── rules/
│   │   └── rules_engine.py    # match_rule, RuleSet.load
│   ├── outputs/
│   │   ├── json_writer.py     # save_rows_raw, save_rows_normalized, save_classification, save_unknown_rows, save_header_rows
│   │   ├── excel_writer.py    # generate_cleaned_spec
│   │   └── annotated_writer.py # generate_annotated_source_excel
│   └── diagnostics/
│       ├── run_manager.py     # create_run_folder
│       └── stats_collector.py # collect_stats, save_run_summary
├── tests/
│   ├── test_smoke.py          # полный прогон на dl1.xlsx, проверка наличия артефактов
│   ├── test_normalizer.py     # unit-тесты нормализатора и row_kind
│   ├── test_state_detector.py # unit-тесты detect_state
│   ├── test_rules_unit.py     # unit-тесты классификации (в т.ч. HEADER, BASE, SOFTWARE-001/002, HW-001)
│   ├── test_excel_writer.py   # прогон и проверка cleaned_spec.xlsx
│   ├── test_annotated_writer.py # прогон и проверка annotated_source.xlsx
│   ├── test_cli.py            # запуск main.py через subprocess, проверка exit code и артефактов
│   └── test_regression.py     # построчное сравнение с golden
├── golden/
│   └── <stem>_expected.jsonl  # при наличии
├── output/
│   └── run-YYYY-MM-DD__HH-MM-SS-<stem>/   # артефакты прогонов
└── docs/
    └── TECHNICAL_OVERVIEW.md  # этот документ
```

Отдельного модуля для сохранения `rules_stats.json` в коде нет; статистика по правилам входит в `run_summary.json` в поле `rules_stats`.

---

## 8. Тестовая стратегия

- **Smoke** (`tests/test_smoke.py`): один прогон на `test_data/dl1.xlsx`, проверка создания всех перечисленных артефактов в папке прогона (в т.ч. `rows_raw.json`, `rows_normalized.json`, `classification.jsonl`, `unknown_rows.csv`, `header_rows.csv`, `run_summary.json`). При отсутствии файла — skip.
- **Unit-тесты:**
  - `test_normalizer.py` — `detect_row_kind` (HEADER/ITEM), `normalize_row` (SKUs, qty, option_price, NaN/пустоты).
  - `test_state_detector.py` — `detect_state` по правилам из YAML (ABSENT, DISABLED, PRESENT по умолчанию).
  - `test_rules_unit.py` — классификация: HEADER→HEADER-SKIP, BASE, SOFTWARE (в т.ч. Embedded Systems Management, Dell Secure Onboarding), HW (Chassis Configuration), SERVICE, LOGISTIC, NOTE, CONFIG, UNKNOWN, state в результате.
  - `test_excel_writer.py` — наличие `cleaned_spec.xlsx`, отсутствие HEADER в нём, только типы из `include_types`, только PRESENT при `include_only_present`.
  - `test_annotated_writer.py` — наличие `<stem>_annotated.xlsx`, совпадение числа строк с исходным, наличие колонок Entity Type, State, device_type, hw_type и заполненных значений для ITEM.
- **CLI** (`test_cli.py`): запуск `main.py --input ... --config config.yaml --output-dir output` через subprocess; проверка exit code 0, наличия в stdout подстроки `total_rows`, наличия в `output/run-*` файлов `cleaned_spec.xlsx` и `run_summary.json`.
- **Regression** (`test_regression.py`): см. раздел 5; при отличии выводится diff по строкам.

Зависимости тестов: при отсутствии `test_data/dl1.xlsx` или соответствующих golden файлов тесты помечаются как skip, где это реализовано.

---

## 9. Ограничения и допущения

- **Один бренд:** правила заточены под Dell; единый файл правил `rules/dell_rules.yaml`. Плагинной модели по брендам в коде нет.
- **Один лист:** парсер и аннотированный экспорт работают с первым листом Excel.
- **Заголовок:** строка заголовка ищется по точному совпадению ячейки с `"Module Name"` в первых 20 строках; при отсутствии — `find_header_row` возвращает `None`, `parse_excel` бросает `ValueError`.
- **Кодировки:** конфиг и YAML правил читаются в UTF-8; CSV пишутся в UTF-8-sig для корректного открытия в Excel.
- **Порядок строк:** соответствие нормализованных строк и результатов классификации — по индексу в списках; в аннотированном экспорте привязка к строке листа по `source_row_index` (1-based), считая, что первая строка листа в pandas — индекс 0 (Excel row 1).
- **Правила:** порядок проверки типов сущностей фиксирован в `classifier.py`; порядок правил внутри каждой группы задаётся YAML (первое совпадение выигрывает). Версия правил хранится в YAML (`version`) и доступна как `RuleSet.version`; в артефактах прогона отдельно не сохраняется.
- **Конфиг:** переключение типов для cleaned spec и флаг `include_only_present` задаются только через `config.yaml`; в CLI нет отдельных флагов для них.

---

## 10. Как расширять правила

- **Файл правил:** `rules/dell_rules.yaml`. Структура: `version`, `state_rules.absent_keywords`, затем группы `base_rules`, `service_rules`, `logistic_rules`, `software_rules`, `note_rules`, `config_rules`, `hw_rules`. Каждое правило — объект с полями `field` (`module_name` или `option_name`), `pattern` (regex), `entity_type`, `rule_id`. Для state — `pattern`, `state` (ABSENT/DISABLED), `rule_id`.
- **Добавление правил:** добавить в нужную группу новый элемент с уникальным `rule_id`. Порядок в группе важен: срабатывает первое совпадение. Регулярные выражения применяются без учёта регистра (`re.IGNORECASE` в `match_rule` и `detect_state`).
- **Новый тип сущности:** потребует изменений в коде: enum `EntityType` в `classifier.py`, ветка в `classify_row`, при необходимости — секция в YAML и её чтение в `RuleSet`. В текущей реализации новых типов без правок кода добавить нельзя.
- **Регрессия:** после изменения правил или логики классификации нужно обновить golden (`--update-golden` с подтверждением) и перезапустить `pytest tests/test_regression.py`, при необходимости обновить `CHANGELOG.md` по принятой в проекте практике.

---

## 11. Known Limitations and Risks

- **First-match rule sensitivity:** Entity classification and device_type assignment use first-match semantics within each rule category. Overlapping regex patterns between rules in the same category may cause shadowing: a rule placed earlier in the YAML will match instead of a more specific rule placed later. There is no automated overlap detection. Mitigation: when adding rules, run all 5 test datasets and inspect golden diffs before committing.

- **Golden file coupling:** Golden files (golden/*_expected.jsonl) compare exact field values (entity_type, state, matched_rule_id, device_type, skus). Any change to normalization behavior (whitespace handling, SKU parsing order) or serialization will cause regression failures across all datasets. This is intentional — the golden files are the classification contract. However, it means that non-functional refactoring of the normalizer or parser requires golden regeneration and careful diff review.

- **No automated rule overlap checker:** There is currently no lint or CI check to detect regex overlap between rules in the same category. This is deferred; at the current rule count (~30 rules), manual review during PR is sufficient. If the rule set grows significantly, an automated tool should be built.

- **run_summary.json is schema-free:** There is no formal schema or validation for run_summary.json. Fields are added by collect_stats() and by main.py. Tests only assert on unknown_count and item_rows_count. Other fields could silently change type or disappear without test failure. Consider adding a schema test if the summary grows in scope.
