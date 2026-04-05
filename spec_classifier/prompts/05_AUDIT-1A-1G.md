# ШАБЛОН 1A–1G — ПОЛНЫЙ АУДИТ
**Когда использовать:**
- добавлен новый вендор/модуль
- были правки в core (classifier/normalizer/writers)
- хочешь "железную уверенность" перед следующей большой фичей
- завершён цикл правок и нужно обновить документацию

**Правило (claude.ai):** каждый шаг = отдельное новое окно. В финал (1G) идут ТОЛЬКО SUMMARY-блоки.
**Правило (Cowork):** все шаги можно выполнять в одной сессии подряд. Скажи: _"запусти шаг 1A"_, затем _"запусти 1B"_ и т.д. В конце передай SUMMARY-блоки в 1G.

---

## 1A — Repo tree + OUTPUT метрики (факты)
**Модель:** Sonnet 4.6 | **Extended:** OFF
**Файлы:** прямой доступ через Cowork _(claude.ai: teresa.zip + OUTPUT.rar)_

```
Ты — аудитор. Никаких исправлений кода, только факты с доказательствами.
_(Cowork: прямой доступ к репо и OUTPUT. claude.ai: прочитай teresa.zip и OUTPUT.rar.)_

A) Выведи дерево файлов репозитория (src/, rules/, docs/, tests/, scripts/).
   Отдельно отметь наличие:
   - batch_audit.py
   - cluster_audit.py
   - scripts/update_golden_from_tests.py (или main.py --update-golden)

B) В OUTPUT.rar для каждого вендора (Dell / Cisco / HPE / Lenovo) посчитай:
   - unknown_count (entity_type == UNKNOWN)
   - hw_type_null_all_items
   - hw_type_null_hw_only (только среди HW строк)
   - item_rows_total, hw_rows_total
   Если есть audit_report.json — добавь:
   - REAL_BUG count, REVIEW_NEEDED count, FALSE_POSITIVE count
   - E2 count, E17 count, E18 count
   Если есть cluster_summary.xlsx — добавь:
   - total_clusters, с heuristic confidence, manual_review count

C) Перечисли все *.yaml/*.yml и *.md файлы (пути).

Формат: 1) RESULTS  2) SUMMARY (CLAIMS/EVIDENCE/SEVERITY/ACTION)
```

**Сохранить:** `audit_1A.txt`

---

## 1B — Архитектура и расширяемость
**Модель:** Opus 4.6 | **Extended:** ON
**Файлы:** прямой доступ через Cowork _(claude.ai: teresa.zip)_

```
Ты — Tech Lead + QA. Никаких правок, только аудит.

Прочитай ТОЛЬКО:
- src/core/classifier.py
- src/core/normalizer.py
- src/core/parser.py
- src/vendors/ (все .py)
- rules/ (все *.yaml/*.yml)
- src/outputs/annotated_writer.py

Ответь:
1) Есть ли vendor-specific знание в classifier/normalizer? (файл+фрагмент)
2) core/parser.py — это действительно общий парсер или фактически dell-specific?
3) VendorAdapter ABC: список абстрактных методов и проверка реализаций в Dell/Cisco/HPE/Lenovo.
4) can_parse: позитивная сигнатура у каждого?
5) get_extra_cols(): реализован ли в каждом адаптере? Возвращает ли
   правильные vendor-extension поля? annotated_writer использует параметр
   extra_cols или всё ещё содержит хардкод VENDOR_EXTRA_COLS?
6) Добавление нового вендора: сколько файлов нужно создать, сколько
   существующих файлов нужно редактировать? Нужны ли правки в batch_audit.py
   или cluster_audit.py? (ожидаемый ответ: нет, они vendor-agnostic)
7) batch_audit.py и cluster_audit.py: подтверди что vendor-agnostic рефакторинг
   работает. Проверь:
   - DEVICE_TYPE_MAP загружается из YAML (не хардкод)?
   - --vendor choices динамические из config.yaml?
   - detect_vendor_from_path() принимает known_vendors?
   - E4 state logic использует E4_STATE_VALIDATORS dict (не if/elif цепочку)?
   - Есть ли KNOWN_FP_CASES для новых вендоров (Lenovo)?

Формат: RESULTS + SUMMARY (CLAIMS/EVIDENCE/SEVERITY/ACTION)
```

**Сохранить:** `audit_1B.txt`

---

## 1C — Проверка фиксов прошлых сессий (чеклист)
**Модель:** Sonnet 4.6 | **Extended:** OFF
**Файлы:** прямой доступ через Cowork _(claude.ai: teresa.zip)_

```
Ты — чеклист-аудитор. Прочитай ТОЛЬКО:
- rules/hpe_rules.yaml, rules/dell_rules.yaml, rules/cisco_rules.yaml
- src/core/classifier.py (только секцию _apply_device_type)
- batch_audit.py (первые 50 строк + функции validate_row и issue_color)
- cluster_audit.py (только KEYWORD_DEVICE_MAP и функцию heuristic_mapping)
- Makefile, .gitignore
- tests/ (только имена файлов и первые 10 строк каждого)

Проверь пункты: ✅/❌/⚠️. Для ❌/⚠️: файл + точное место + фрагмент.

RULES:
[ ] E6 fix: batch_audit.py entity not in ("HW", "LOGISTIC", "BASE")
[ ] E10 fix: device_type на BASE больше не триггерит E10
[ ] config_name → module_name alias в _ALIASES
[ ] product_# в SKU aliases (найти через grep "product_#" batch_audit.py)
[ ] row_kind колонка в annotated_writer.py
[ ] power_cord: hw_type=None во всех трёх YAML (не cable)
[ ] hw_type applies_to: [HW] (не [HW, BASE]) во всех YAML (dell, cisco, hpe, lenovo)
[ ] HPE note_rules: [] присутствует
[ ] BASE-*-DT-001 rules: HPE→server, Dell→server, Cisco→switch, Lenovo→server
[ ] E4_STATE_VALIDATORS содержит записи для ВСЕХ вендоров из config.yaml
[ ] Lenovo rules: lenovo_rules.yaml загружается, rule_id формат корректен
[ ] Windows encoding fix: sys.stdout.reconfigure(encoding="utf-8")
[ ] E18 в validate_row() и issue_color()

ТЕСТЫ:
[ ] tests/test_batch_audit.py существует (подсчитать: grep -c "^def test_" tests/test_batch_audit.py)
[ ] tests/test_cluster_audit.py существует (10+ тестов)
[ ] test_hpe_rules_unit.py: device_type и hw_type assertions присутствуют
[ ] tests/test_lenovo_rules_unit.py существует с device_type/hw_type assertions
[ ] tests/test_lenovo_parser.py существует
[ ] conftest.py: проверка per-vendor subdirs (не только root)

ПУТИ:
[ ] test_data/ не используется как реальный путь
[ ] .gitignore игнорирует test_data/ целиком
[ ] Makefile: INPUT переменная, нет test_data/

Формат: RESULTS + SUMMARY (CLAIMS/EVIDENCE/SEVERITY/ACTION)
```

**Сохранить:** `audit_1C.txt`

---

## 1D — Стыки модулей (anti-hidden bugs)
**Модель:** Opus 4.6 | **Extended:** ON
**Файлы:** прямой доступ через Cowork _(claude.ai: teresa.zip)_

```
Ты — QA по "стыкам". Прочитай ТОЛЬКО:
- src/core/classifier.py
- src/core/normalizer.py
- src/outputs/ (все writer'ы)
- src/vendors/hpe/ (все .py)
- rules/hpe_rules.yaml
- batch_audit.py (функции find_annotated_files, validate_row, _generate_human_report)
- cluster_audit.py (функции load_candidate_rows, write_cluster_summary)

Проведи две цепочки и найди разрывы:

ЦЕПОЧКА 1: Основной пайплайн (HW-item от xlsx до outputs)
1) parser: какие поля читает/пишет для HPE
2) normalizer: какие поля гарантирует (включая vendor extension поля)
3) classifier: какие поля читает и как выбирает applies_to
4) writers: какие поля теряются/где (annotated, cleaned_spec, unknown_rows)

ЦЕПОЧКА 2: Audit-слой (annotated.xlsx → batch_audit → cluster_audit)
1) batch_audit: какие колонки читает из *_annotated.xlsx?
   Что происходит если колонки нет (KeyError vs graceful)?
2) batch_audit → *_audited.xlsx: какие колонки добавляются?
3) cluster_audit: читает ли он *_audited.xlsx или *_annotated.xlsx?
4) cluster_summary.xlsx: есть ли поля для передачи в Cursor как YAML-кандидаты?

Выдай список разрывов P0/P1/P2 с доказательствами.

Формат: RESULTS + SUMMARY (CLAIMS/EVIDENCE/SEVERITY/ACTION)
```

**Сохранить:** `audit_1D.txt`

---

## 1E — Документация как контракт
**Модель:** Opus 4.6 | **Extended:** ON
**Файлы:** прямой доступ через Cowork _(claude.ai: teresa.zip)_

```
Ты — аудитор документации. Никаких правок, только расхождения с доказательствами.
Прочитай ТОЛЬКО:
- docs/DOCS_INDEX.md
- docs/user/USER_GUIDE.md
- docs/user/CLI_CONFIG_REFERENCE.md
- docs/user/RUN_PATHS_AND_IO_LAYOUT.md
- docs/product/TECHNICAL_OVERVIEW.md
- docs/schemas/DATA_CONTRACTS.md
- docs/taxonomy/hw_type_taxonomy.md
- CURRENT_STATE.md
- CHANGELOG.md
- README.md

Проверь:
1) CHANGELOG.md: есть секция [Unreleased]? Запись после [1.3.0]?
2) CURRENT_STATE.md: версия, дата, список вендоров актуальны?
3) INPUT layout: документы описывают плоскую структуру или с подпапками (dell/, cisco/, hpe/)?
4) batch_audit.py и cluster_audit.py в документации:
   - README: упомянут E18? audit-слой описан?
   - RUN_PATHS: описаны audit_report.json, audit_summary.xlsx, cluster_summary.xlsx, *_audited.xlsx?
   - DATA_CONTRACTS: есть схема audit_report.json и cluster_summary.xlsx?
   - DOCS_INDEX: есть ссылка на cluster_audit.py?
5) CLI --vendor enum соответствует факту (dell/cisco/hpe/lenovo)?
6) Устаревшие формулировки без полного списка вендоров.
   Проверить что ВСЕ документы упоминают Lenovo где перечислены вендоры.
7) hw_type_taxonomy.md: power_cord=None, applies_to=[HW] — синхронизировано с кодом?
8) Документация Lenovo: USER_GUIDE описывает Lenovo формат?
   CLI_CONFIG: --vendor lenovo упомянут? hw_type_taxonomy: Lenovo = active?

Формат: RESULTS (таблица: документ → проблема → цитата → риск) + SUMMARY
```

**Сохранить:** `audit_1E.txt`

---

## 1F — Тесты и ловушки разработки
**Модель:** Opus 4.6 | **Extended:** ON
**Файлы:** прямой доступ через Cowork _(claude.ai: teresa.zip)_

```
Ты — QA по тестам и процессу. Никаких правок.
Прочитай ТОЛЬКО:
- tests/ (все test_*.py)
- conftest.py
- scripts/ (все .py и .ps1)
- .gitignore
- config.yaml

Задачи:
1) Покрытие по вендорам: симметрия тестов между Dell/Cisco/HPE/Lenovo.
   Для каждого вендора проверить наличие: rules_unit, normalizer, parser.
   Проверь: есть ли assertions на device_type/hw_type в test_hpe_rules_unit.py?

2) Покрытие audit-слоя:
   - Есть ли тесты для batch_audit.py? (E18, динамический REAL_BUG)
   - Есть ли тесты для cluster_audit.py? (load_candidate_rows, heuristic_mapping)

3) Skip guard: conftest.py проверяет per-vendor subdirs или только root?
   Сколько HPE runtime cases (с учётом parametrize)?

4) Слепые зоны: нет ли schema validation, проверки rule_id формата, обработки битых xlsx.

5) ВАЖНО: отличай "файл есть в репо" от "файл tracked в git".
   Если утверждаешь tracked — дай доказательство (git ls-files) или пометь НЕПОДТВЕРЖДЕНО.

Формат: RESULTS + SUMMARY (CLAIMS/EVIDENCE/SEVERITY/ACTION)
```

**Сохранить:** `audit_1F.txt`

---

## 1G — Финальный вердикт (PASS/FAIL)
**Модель:** Sonnet 4.6 | **Extended:** OFF  
**Файлы:** НИЧЕГО — только SUMMARY-блоки из 1A–1F

```
Ты — релизный гейт-аудитор. На входе только SUMMARY-блоки шагов 1A–1F.

КРИТИЧЕСКОЕ ПРАВИЛО КЛАССИФИКАЦИИ:
НЕ помечай как P0/P1 пункты из категории АРХИТЕКТУРНЫЙ ДОЛГ:
- "parser.py де-факто Dell-specific" — это by design, не баг
- "batch_audit содержит vendor hardcode" — проверь что vendor-agnostic
  рефакторинг сделан; если да — это уже НЕ finding
- "нет тестов для corrupt xlsx" — это P2 (nice-to-have), не P1
- "config.local.yaml не в gitignore" — проверь факт, не повторяй из прошлого аудита

P0 = данные теряются, crash, неправильная классификация.
P1 = секция аудита не проходит (Docs FAIL, Tests FAIL).
P2 = улучшения, arch debt, косметика.

Если ВСЕ секции PASS и P0=0, статус = PASS даже при наличии P2.

Собери финальный отчёт:

AUDIT_STATUS: PASS/FAIL

BLOCKERS (P0):
- …
IMPORTANT (P1):
- …
NICE (P2):
- …

SECTIONS (каждая: PASS/FAIL + 1 строка причины):
- Architecture (включая vendor-agnostic audit layer)
- Outputs/Metrics (включая audit + cluster метрики)
- Rules/Adapters Integrity (все 4 вендора)
- Docs Consistency (CURRENT_STATE, CHANGELOG, vendor docs для всех 4 вендоров)
- Tests & Safety (включая покрытие Lenovo)

ACTION PLAN:
- 5–10 конкретных действий по приоритету (P0 сначала), с указанием файлов.

Ниже summary-блоки:
[ВСТАВЬ СЮДА ТОЛЬКО SUMMARY 1A…1F]
```

**Сохранить:** `результат_шаг1G.txt`
