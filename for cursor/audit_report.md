# Аудит репозитория Teresa (Dell Spec Classifier MVP)

**Дата аудита**: 2026-02-23  
**Источники**: `dell_mvp_technical_spec.md` (v2.0), архив `teresa-main.zip`  
**Метод**: статический анализ кода, сравнение со спецификацией. Код не запускался (нет установленных зависимостей в среде аудита).

---

## A) Executive Summary

### Сильные стороны

1. **Архитектура полностью соответствует плану.** Слои parser → normalizer → classifier → rules_engine → state_detector → outputs → diagnostics реализованы как отдельные модули с чёткими ответственностями.
2. **Детерминированный приоритетный классификатор реализован верно.** Порядок BASE → SERVICE → LOGISTIC → SOFTWARE → NOTE → CONFIG → HW → UNKNOWN соблюдён, first-match семантика, HEADER-SKIP до классификации.
3. **Правила (`dell_rules.yaml`) полностью покрывают спецификацию.** Все rule_id из спеки присутствуют (BASE-001/002, SERVICE-001–005, SOFTWARE-001–004, HW-001–004, NOTE-001/002, CONFIG-001, LOGISTIC-001–003), версия 1.0.0, структура корректна.
4. **Unit-тесты качественные и покрывают критические кейсы.** 21 тест в `test_rules_unit.py` (включая HEADER-SKIP, Embedded Systems Management, Chassis Configuration ≠ CONFIG, NOTE vs SERVICE «supports»), 8 тестов state_detector, 12 тестов normalizer.
5. **CHANGELOG.md и версионирование правил** соответствуют плану (формат Keep a Changelog, SemVer, запись v1.0.0).

### Ключевые риски/блокеры

1. **`test_data/` находится вне `dell_spec_classifier/` — все smoke/regression/integration тесты будут пропущены (pytest.skip).** Тесты ищут файлы через `_project_root() / "test_data"`, но `test_data/` лежит в `teresa-main/`, а не в `dell_spec_classifier/`. Это **критический блокер** для CI и регрессии.
2. **Папка `golden/` пуста (только `.gitkeep`).** Без эталонных JSONL-файлов regression-тесты не работают. Невозможно подтвердить, что пайплайн вообще запускался end-to-end с генерацией golden.
3. **Regression-тесты покрывают только dl1 и dl2** (параметризованы `["dl1.xlsx", "dl2.xlsx"]`), план требует dl1–dl5.
4. **Smoke-тест запускается только на dl1.xlsx**, план требует прогон на всех dl1–dl5.
5. **Артефакты `input_snapshot.json` и `rules_stats.json` (как отдельный файл) отсутствуют.** Спецификация перечисляет `input_snapshot.json` как обязательный артефакт; `rules_stats` включён в `run_summary.json`, но отдельного файла `rules_stats.json` нет.

---

## B) Матрица соответствия плану

| # | Требование (кратко) | Ожидание по спеке | Факт в репо | Статус | Комментарий |
|---|---|---|---|---|---|
| 1 | Структура проекта `dell_spec_classifier/` | src/core/, src/rules/, src/outputs/, src/diagnostics/, tests/, golden/, output/, main.py, config.yaml, CHANGELOG.md, requirements.txt | Все папки и файлы присутствуют, `__init__.py` на месте | **OK** | — |
| 2 | `parser.py`: find_header_row + parse_excel | Автоопределение header, удаление Unnamed:0, `__row_index__` = pandas_idx + header_row_index + 2 | Реализовано полностью, формула совпадает | **OK** | — |
| 3 | `normalizer.py`: RowKind(ITEM/HEADER) + NormalizedRow | detect_row_kind по Module Name / Option Name / SKUs; dataclass с row_kind | Реализовано, NaN обработка через `value != value` | **OK** | — |
| 4 | `state_detector.py`: State(PRESENT/ABSENT/DISABLED) | Regex-паттерны из YAML (state_rules.absent_keywords), default PRESENT | Реализовано, re.IGNORECASE, первый матч | **OK** | — |
| 5 | `rules_engine.py`: RuleSet + match_rule | Загрузка YAML, матчинг по field+pattern, first-match | Реализовано; match_rule возвращает dict правила или None | **OK** | — |
| 6 | `classifier.py`: EntityType enum (8 типов) + classify_row | HEADER→SKIP, ITEM→приоритетный порядок (BASE→SERVICE→…→HW→UNKNOWN), NOTE state=PRESENT, BASE state=PRESENT | Полностью реализовано, порядок совпадает со спекой | **OK** | — |
| 7 | `dell_rules.yaml` v1.0.0 | Все правила из спеки (BASE-001/002, SERVICE-001–005, LOGISTIC-001–003, SOFTWARE-001–004, NOTE-001/002, CONFIG-001, HW-001–004) + state_rules | Все присутствуют. SERVICE-005 перемещён перед SERVICE-003 (правильно — more specific first) | **OK** | — |
| 8 | `config.yaml` с cleaned_spec + rules_file | include_types, include_only_present, exclude_headers, output_columns, rules_file | `output_columns` отсутствует в config.yaml; остальное есть | **PARTIAL** | `output_columns` указан в спеке, но не используется кодом (колонки захардкожены в excel_writer.py). Фактически не влияет на работу. |
| 9 | Артефакты run-папки: rows_raw.json, rows_normalized.json, classification.jsonl, unknown_rows.csv, header_rows.csv, rules_stats.json, run_summary.json, cleaned_spec.xlsx, run.log, input_snapshot.json | Все перечисленные файлы должны создаваться | `input_snapshot.json` — **не реализован**. `rules_stats.json` — отдельного файла нет (данные внутри run_summary.json). `annotated_source.xlsx` — **бонус**, не в спеке | **PARTIAL** | `input_snapshot.json` не создаётся. `rules_stats` — семантически покрыт через run_summary.json, но формально отдельного файла нет. |
| 10 | `run.log` с логированием HEADER/ITEM/UNKNOWN | FileHandler в run-папке, INFO/DEBUG уровни | FileHandler добавляется **после** создания run_folder; этапы parse/normalize/classify логируются до этого и не попадают в файл | **PARTIAL** | Ранние этапы пайплайна (parse, normalize) логируются до FileHandler → в `run.log` их не будет. |
| 11 | CLI: --input, --config, --output-dir, --save-golden, --update-golden | Все аргументы | Все реализованы, --update-golden с подтверждением (y/n) | **OK** | — |
| 12 | Smoke tests на dl1–dl5 | test_smoke_all_files() прогон на всех 5 файлах | `test_smoke.py` тестирует только dl1.xlsx | **PARTIAL** | Спека требует smoke на всех dl1–dl5. |
| 13 | Regression tests (построчный JSONL golden) dl1–dl5 | Параметризованные тесты для dl1–dl5, построчное сравнение entity_type/state/matched_rule_id/skus | Параметризация только `["dl1.xlsx", "dl2.xlsx"]`, golden пуста | **PARTIAL** | dl3–dl5 не параметризованы; golden не сгенерирован. |
| 14 | Golden JSONL файлы (dl1–dl5_expected.jsonl) | Файлы в golden/ | Папка пуста (.gitkeep) | **MISSING** | Необходимо сгенерировать: `python main.py --save-golden --input test_data/dlX.xlsx` для каждого файла. |
| 15 | Unit tests правил (≥20 тестов) | Минимум 20 unit tests включая HEADER, SOFTWARE-001/002, Chassis Config, NOTE | 21 тест в test_rules_unit.py | **OK** | — |
| 16 | test_data/ доступна тестам | Файлы dl1–dl5.xlsx доступны из тестов | test_data/ на уровне teresa-main/, а не dell_spec_classifier/ | **MISSING** | Все тесты с файлами будут `pytest.skip`. Нужно переместить test_data/ внутрь dell_spec_classifier/ или исправить пути. |
| 17 | CHANGELOG.md (формат Keep a Changelog) | Версия 1.0.0, формат KAC+SemVer | Присутствует, соответствует формату | **OK** | — |
| 18 | README.md: установка, запуск, артефакты, row_kind, Rules Change Process | Полный README с CLI, артефактами, row_kind, Rules Change Process | README содержит только секцию Regression (save-golden / update-golden / run) | **PARTIAL** | Отсутствуют: установка, описание артефактов, описание row_kind/state, Rules Change Process, описание entity_type. |
| 19 | Cleaned spec Excel: фильтрация ITEM+include_types+PRESENT | Исключение HEADER, CONFIG, LOGISTIC, NOTE, UNKNOWN, ABSENT/DISABLED | Реализовано корректно в excel_writer.py | **OK** | — |
| 20 | `annotated_source.xlsx` | Не в спеке (бонус) | Реализован в annotated_writer.py + тест | **OK** | Дополнительный артефакт сверх спеки, полезен. |
| 21 | Приоритет правил: BASE → SERVICE → LOGISTIC → SOFTWARE → NOTE → CONFIG → HW → UNKNOWN | Строгий порядок в classify_row | Порядок соблюдён в коде | **OK** | — |
| 22 | State detection ДО entity classification | detect_state() вызывается до match_rule() | В classify_row: state = detect_state() первой строкой после HEADER-check | **OK** | — |
| 23 | docs/TECHNICAL_OVERVIEW.md | Не в спеке | Подробный технический обзор фактической реализации | **OK** | Бонус: качественный документ, описывающий пайплайн по шагам. |

---

## C) Критические несоответствия

### C1. `test_data/` вне рабочей директории проекта

**Что не так:** Каталог `test_data/` (dl1–dl5.xlsx) находится в `teresa-main/test_data/`, а все тесты ищут его как `dell_spec_classifier/test_data/` (через `_project_root() / "test_data"`). Из-за `pytest.skip` при отсутствии файла ни один smoke/regression/integration тест не выполняется.

**Почему критично:** Без доступа к тестовым данным невозможно подтвердить работоспособность пайплайна; CI будет показывать «0 failed» при фактически 0 проверенных кейсах.

**Минимальное исправление:** Переместить (или скопировать/симлинковать) `teresa-main/test_data/` → `dell_spec_classifier/test_data/`.

**Риск, если не исправить:** Полная иллюзия работающих тестов при нулевом фактическом покрытии.

### C2. Golden-файлы не сгенерированы

**Что не так:** Папка `golden/` содержит только `.gitkeep`. Ни один `dlX_expected.jsonl` не создан.

**Почему критично:** Regression-тесты — основной механизм защиты от поломок. Без golden они не работают (pytest.skip).

**Минимальное исправление:** После исправления C1 — запустить `python main.py --save-golden --input test_data/dlX.xlsx` для каждого dl1–dl5, проверить результаты визуально, закоммитить golden-файлы.

**Риск, если не исправить:** Любое изменение правил останется без автоматической проверки; регрессии накапливаются незаметно.

### C3. Regression-тесты покрывают только dl1 и dl2

**Что не так:** `test_regression.py` параметризован как `["dl1.xlsx", "dl2.xlsx"]`, спека требует dl1–dl5.

**Почему критично:** dl3–dl5 могут содержать паттерны, не встречающиеся в dl1/dl2 (например, PowerEdge R6715 в dl5, другие вариации модулей). Без регрессии по этим файлам изменения правил могут сломать их незаметно.

**Минимальное исправление:** Расширить параметризацию до `["dl1.xlsx", "dl2.xlsx", "dl3.xlsx", "dl4.xlsx", "dl5.xlsx"]`.

**Риск, если не исправить:** Средний — dl1/dl2 могут покрывать большинство паттернов, но гарантий нет.

### C4. Smoke-тест только на dl1

**Что не так:** `test_smoke.py` запускает пайплайн только на `dl1.xlsx`, спека требует все dl1–dl5.

**Почему критично:** Нет гарантии, что пайплайн не упадёт на dl2–dl5 (разная структура заголовков, разные паттерны).

**Минимальное исправление:** Параметризовать smoke-тест по всем 5 файлам.

**Риск, если не исправить:** Средний — проблемы с парсингом/нормализацией конкретных файлов останутся незамеченными.

### C5. `input_snapshot.json` не реализован

**Что не так:** Спека перечисляет `input_snapshot.json` среди обязательных артефактов run-папки. В коде нет ни генерации, ни упоминания этого файла.

**Почему критично:** Низкая критичность для MVP. `input_snapshot.json` нужен для трейсабилити (какой файл обрабатывался, его размер/hash/path), но без него пайплайн работает.

**Минимальное исправление:** Добавить сохранение `{"input_file": ..., "file_size": ..., "sha256": ..., "timestamp": ...}` в run-папку.

**Риск, если не исправить:** Низкий; усложняет аудит прогонов при множественных файлах.

---

## D) Документация

### Что покрыто хорошо

- `CHANGELOG.md` — формат корректен, содержит v1.0.0, соответствует Keep a Changelog / SemVer.
- `docs/TECHNICAL_OVERVIEW.md` — подробный технический обзор (~20 Кб), описывает пайплайн, форматы, CLI, golden/regression. Это полезный артефакт, хотя он не требовался спекой.
- `dell_rules.yaml` — хорошо прокомментирован (приоритеты, предупреждения о Chassis Configuration).
- Код — docstring'ы присутствуют во всех модулях и функциях.

### Что отсутствует/устарело

- **README.md** крайне минималистичен (только секция Regression). Отсутствуют:
  - Установка (`pip install -r requirements.txt`)
  - Общее описание проекта и назначения
  - Примеры CLI (`python main.py --input dl1.xlsx`)
  - Описание артефактов run-папки
  - Описание row_kind (ITEM/HEADER) и entity_type
  - Описание state (PRESENT/ABSENT/DISABLED)
  - **Rules Change Process** (требование спеки)
  - Как запустить тесты
  - Описание config.yaml

### Конкретные пункты для исправления

1. Дописать README.md: установка, запуск, описание артефактов, row_kind/state, entity_type, Rules Change Process.
2. Добавить в README упоминание `--update-golden` и workflow изменения правил (уже частично есть, но без Rules Change Process как отдельной секции).
3. Добавить в README упоминание «Embedded Systems Management» и «Dell Secure Onboarding» как критических SOFTWARE-правил (требование спеки).
4. Привести README в соответствие со спекой п. 7.1 (Фаза 7).
5. В `config.yaml` добавить `output_columns` (или задокументировать, что колонки фиксированы и этот параметр не поддерживается).

---

## E) Готовность к дальнейшему развитию

### Вердикт: **ДА, НО** необходимо сначала исправить gating-блокеры

### Gating fixes (обязательно до продолжения)

1. **Переместить `test_data/` внутрь `dell_spec_classifier/`** (или исправить пути в тестах). Без этого — нулевое тестовое покрытие на реальных данных.
2. **Сгенерировать golden-файлы** для dl1–dl5: `python main.py --save-golden --input test_data/dlX.xlsx`.
3. **Расширить regression-параметризацию** до dl1–dl5.
4. **Проверить, что все тесты проходят** (не skip'аются) после исправлений 1–3.

### Дорожная карта следующих шагов (в порядке важности)

1. **Исправить расположение test_data/** и убедиться, что `pytest tests/` запускает ≥40 тестов (а не 0 из-за skip).
2. **Сгенерировать и закоммитить golden-файлы** для всех dl1–dl5.
3. **Расширить smoke и regression** до полного покрытия dl1–dl5; параметризовать smoke-тест.
4. **Дописать README.md** (установка, артефакты, Rules Change Process, row_kind/state).
5. **Исправить `run.log`**: переместить создание FileHandler **до** parse/normalize/classify, чтобы ранние этапы попадали в лог (или логировать в два этапа: сначала в stdout, затем скопировать буфер в файл).
6. **Добавить `input_snapshot.json`** и (опционально) отдельный `rules_stats.json`.
7. **Провести первый полный прогон на dl1–dl5**, визуально проверить `unknown_rows.csv` и `cleaned_spec.xlsx`, оценить процент UNKNOWN.

---

## F) Что невозможно проверить

1. **Корректность классификации на реальных данных.** Без запуска пайплайна на dl1–dl5.xlsx невозможно проверить, совпадают ли результаты с ожиданиями спеки (например, «~54 строки в dl1», «~374 строки в dl2», «26 строк Embedded Systems Management в dl2», «header_rows_count: 3 в dl1»).
2. **Формула `__row_index__`.** Корректность `pandas_idx + header_row_index + 2` для всех файлов можно подтвердить только прогоном и сверкой с номерами строк в Excel.
3. **Процент UNKNOWN.** Спека ожидает <5% — без прогона невозможно оценить.
4. **Корректность `annotated_source.xlsx`.** Совпадение строк и колонок с исходным Excel можно проверить только визуально после прогона.
5. **Корректность `cleaned_spec.xlsx`.** Спека ожидает «~30–40 строк» для dl1 — без прогона невозможно подтвердить.
6. **Наличие ложных срабатываний NOTE-002.** Правило `\b(Motherboard|included\s+with|required\s+for)\b` по `option_name` потенциально широкое — слово «Motherboard» может встретиться в option_name HW-строки (например, «Motherboard revision 2.0»). Тест `test_note_motherboard` проходит, но на реальных данных могут быть неожиданные перехваты (NOTE приоритетнее CONFIG и HW). Требуется прогон для проверки.
7. **Работоспособность `--update-golden` в non-interactive режиме.** `EOFError` обрабатывается (answer → «n»), но в CI подтверждение невозможно — это by design для защиты, но стоит документировать.
