# Teresa batch_audit.py — MASTER PLAN

**Автор:** Senior Staff Engineer / Tech Lead / QA analysis
**Дата:** 2026-03-05
**Версия:** 1.0
**Scope:** batch_audit.py (P0 bugfixes) + cluster_audit.py (новый модуль)
**Ограничение:** src/ НЕ трогаем. Только batch_audit.py и новый cluster_audit.py.

---

## ЧАСТЬ 0. ОЦЕНКА ИДЕЙ-ДОКУМЕНТОВ

### 0.1 teresa_run_analysis_modules_ideas.txt — Оценка

Документ предлагает 2- или 3-модульную архитектуру анализа.

**Что применимо сейчас:**

Модуль 1 (Deterministic Audit) — это и есть текущий batch_audit.py (E1–E17 checks). Уже реализован на ~80%. Не хватает: динамической классификации REAL_BUG, корректного промпта, покрытия state-валидации. Все три пробела закрываются ЭТАПОМ 1 данного плана.

Модуль 2 (Pattern Mining / Clustering) — полностью применим. В текущем batch_audit.py его нет. Именно этот модуль реализуем как cluster_audit.py в ЭТАПЕ 2.

Модуль 3 (AI Review Layer) — преждевременен. Текущий AI-слой batch_audit.py уже генерирует 26% false positives. Добавлять ещё один AI-слой до исправления промпта и уменьшения шума — контрпродуктивно. Рекомендация: вернуться к модулю 3 после того, как false positive rate batch_audit.py упадёт ниже 10%.

**Идея "Signals, not rows"** — ключевая. cluster_audit.py должен выдавать 20–50 сигналов, а не тысячи строк.

**Идея "Separation of concerns"** — подтверждена архитектурой: Teresa (ядро) → batch_audit.py (проверка) → cluster_audit.py (discovery). Три слоя, три файла, нулевая связность.

### 0.2 teresa_cluster_rule_discovery.txt — Оценка

**Полностью реалистичный документ.** Каждый шаг (select → normalize → vectorize → cluster → analyze → heuristic → report) проверяем и реализуем без внешних зависимостей (кроме scikit-learn).

**Что принимаем как есть:**

- Фильтры: E2 (UNKNOWN) + E17 (HW без device_type) + entity_type=HW & device_type пусто. Это правильные входные данные для кластеризации.
- TF-IDF char n-grams (3–5) — хороший выбор для BOM-данных с токенами вроде "sfp+", "qsfp28", "c13", "dl380".
- HDBSCAN как primary, MiniBatchKMeans как fallback. Нормальный подход.
- Heuristic device mapping (keyword → device_type) без LLM — именно то, что нужно для детерминированного discovery.

**Что корректируем:**

- Документ предлагает "интегрировать в batch_audit.py" (секция Integration). Отвергаем — делаем отдельный cluster_audit.py. Причина: batch_audit.py уже 1262 строки, добавлять кластеризацию в него = нарушить единственную ответственность и усложнить тестирование.
- "Optional AI Layer" — откладываем. Не нужен на первом этапе.
- Валидация "run with --no-ai" — подтверждаем. После генерации правил из кластеров, прогон Teresa + batch_audit.py --no-ai должен показать снижение E2/E17.

---

## ЧАСТЬ 1. АНАЛИЗ ТЕКУЩЕГО СОСТОЯНИЯ

### 1.1 Данные последнего прогона (audit_report.json)

| Метрика | Значение |
|---------|----------|
| Файлов | 30 (Dell: 10, HPE: 16, Cisco: 4) |
| Строк | 3296 |
| OK | 2635 (79.9%) |
| Issues | 661 (20.1%) |
| AI_MISMATCH | 450 + 61 medium = 511 |
| E6 (device_type on wrong entity) | 132 |
| E10 (hw/device on BASE) | 132 |
| E16 (blank_filler info) | 22 |
| AI_SUGGEST | 6 |
| Модель | gpt-4o-mini |
| Стоимость прогона | $0.04 |

### 1.2 Профиль ошибок

Топ-5 "bugs" из audit_report.json (по count):

1. `entity_mismatch:HW→LOGISTIC` — **102 строки** (FALSE_POSITIVE — AI ошибается из-за промпта)
2. `entity_mismatch:HW→NOTE` — **93 строки** (FALSE_POSITIVE — AI не знает HW+ABSENT)
3. `device_mismatch:server→cable` — **47 строк** (REVIEW_NEEDED, HPE)
4. `entity_mismatch:HW→CONFIG` — **44 строки** (FALSE_POSITIVE — AI путает Dell chassis)
5. `device_mismatch:server→fan` / `server→heatsink` — по **36 строк** (REVIEW_NEEDED, HPE)

Подавляющее большинство — HPE device_mismatch формата `server→X`. Это паттерн: HPE rows с device_type=server, но AI видит конкретный компонент (cable/fan/heatsink). Причина — HPE pipeline ставит device_type=server на строки-компоненты внутри серверных модулей. Это **не баг AI** — это известная особенность HPE-правил.

### 1.3 Три P0-бага (подтверждены)

**P0-1: LLM_SYSTEM промпт (строка 98–101)**

Код строки 101: `"For LOGISTIC: power cords and cables shipped with the unit are typically LOGISTIC with device_type=power_cord or cable."`

Факт: По бизнес-правилам Teresa, power cord = HW. Строка 98 также содержит `"rack rail kit"` в списке LOGISTIC — рельсы тоже HW.

Влияние: AI не генерирует AI_MISMATCH для ошибочных LOGISTIC-строк. 102 false positives типа HW→LOGISTIC — прямое следствие. AI *согласен* с ошибкой Teresa, потому что промпт учит его тому же.

**P0-2: Hardcoded real_bug_patterns (строки 920–924)**

```python
real_bug_patterns = {
    "cable→battery", "gpu→backplane", "storage_nvme→backplane",
    "gpu→accessory", "cable→accessory", "sfp_cable→cable",
    "storage_nvme→cable"
}
```

Факт: Это статический набор из 7 паттернов. Новые реальные баги классифицируются как REVIEW_NEEDED. В текущем прогоне единственный REAL_BUG: `storage_nvme→backplane` (count=2). Остальные 28+ REVIEW_NEEDED паттернов не проходят через hardcoded фильтр.

Влияние: audit_report.json не различает приоритеты корректно. claude_prompt секция содержит "Нет явных багов" если ни один паттерн не попал в hardcoded set.

**P0-3: AI не знает паттерн HW+ABSENT (строка 82–108)**

Факт: 93 строки AI_MISMATCH entity[HW→NOTE] из-за "No Hard Drive", "No TPM", "No Quick Sync". AI считает это NOTE. Teresa правильно ставит HW + state=ABSENT.

Влияние: 93 ложных AI_MISMATCH в отчёте. Это 14% всех issues — чистый шум.

---

## ЧАСТЬ 2. MASTER PLAN

### ЭТАП 1 — Исправление P0-багов в batch_audit.py

**Принцип:** Минимальные точечные правки. Никакого рефакторинга. Каждая правка — один pull request с тестируемым результатом.

---

#### ЗАДАЧА 1.1: Исправить LLM_SYSTEM промпт

**Файл:** `batch_audit.py`, строки 82–108 (константа `LLM_SYSTEM`)

**Что менять:**

A) Строка 98 — убрать `"rack rail kit"` и `"power cord for delivery"` из определения LOGISTIC:
```
БЫЛО:  "LOGISTIC = shipping, delivery, freight, documentation, rack rail kit, power cord for delivery"
СТАЛО: "LOGISTIC = shipping labels, delivery/freight charges, packing materials, documentation only"
```

B) Строка 101 — убрать или инвертировать правило про power cords:
```
БЫЛО:  "For LOGISTIC: power cords and cables shipped with the unit are typically LOGISTIC..."
СТАЛО: "Power cords, rack rails, mounting hardware, and cables are ALWAYS HW (entity_type=HW), never LOGISTIC.
        LOGISTIC is ONLY for non-physical items: shipping charges, freight, labels, packing slips."
```

C) Добавить правило HW+ABSENT (после строки 103):
```
ДОБАВИТЬ: "For rows starting with 'No ...' (e.g., 'No Hard Drive', 'No TPM', 'No Quick Sync', 'No Rear Storage'):
           entity_type=HW, state=ABSENT. These represent absent hardware slots, NOT informational notes."
```

D) Добавить подсказку про BASE (после строки 93):
```
ДОБАВИТЬ: "BASE is determined by row position and module context (bundle root, first product row).
           If pipeline says BASE, trust it — do not reclassify based on option_name alone."
```

E) Добавить подсказку про Dell module_name:
```
ДОБАВИТЬ: "For Dell BOM rows, Module Name is the PRIMARY signal for entity_type.
           'Chassis Configuration' module contains HW rows, not CONFIG."
```

**Acceptance Criteria:**
1. Прогон `batch_audit.py --no-ai` — без изменений (промпт не влияет на rule-based checks)
2. Прогон с AI — AI_MISMATCH entity[HW→LOGISTIC] уменьшается с 102 до <20
3. Прогон с AI — AI_MISMATCH entity[HW→NOTE] уменьшается с 93 до <10
4. Прогон с AI — AI_MISMATCH entity[HW→CONFIG] уменьшается с 44 до <15
5. Прогон с AI — AI_MISMATCH entity[BASE→CONFIG] исчезает (0)
6. Общий false positive rate падает с 26% до <10%

**Как проверить:** Сравнить audit_report.json до и после. Секция `bugs` → count по каждому паттерну.

---

#### ЗАДАЧА 1.2: Заменить hardcoded real_bug_patterns на эвристику

**Файл:** `batch_audit.py`, строки 918–938

**Что менять:**

Удалить hardcoded set `real_bug_patterns` и заменить на динамическую классификацию:

```python
# Логика классификации bug_type:
# 1. device_mismatch + count >= 3 + confidence=high в >50% примеров → REAL_BUG
# 2. device_mismatch + count >= 2 + примеры из >=2 разных файлов → REAL_BUG
# 3. entity_mismatch из fp_patterns → FALSE_POSITIVE (оставить как есть)
# 4. Всё остальное → REVIEW_NEEDED (оставить как есть)
```

Конкретная реализация:

```python
# Вместо hardcoded set:
bug_type = "UNKNOWN"
if kind == "entity_mismatch" and f"{from_val}→{to_val}" in fp_patterns:
    bug_type = "FALSE_POSITIVE"
elif kind == "device_mismatch":
    unique_files = len(set(i["file"] for i in items))
    # Эвристика: повторяющийся паттерн из разных файлов = реальный баг
    if len(items) >= 3 or (len(items) >= 2 and unique_files >= 2):
        bug_type = "REAL_BUG"
    else:
        bug_type = "REVIEW_NEEDED"
elif kind == "entity_mismatch":
    bug_type = "REVIEW_NEEDED"
```

**Acceptance Criteria:**
1. Старые REAL_BUG паттерны (cable→battery и т.д.) всё ещё определяются как REAL_BUG при count>=3
2. Новые device_mismatch с count>=3 автоматически получают REAL_BUG
3. device_mismatch с count=1 из одного файла → REVIEW_NEEDED
4. fp_patterns по-прежнему дают FALSE_POSITIVE
5. audit_report.json → bugs секция содержит новые REAL_BUG (если они есть в данных)

**Как проверить:** Прогон на текущих данных. В audit_report.json `bugs` должны появиться REAL_BUG для паттернов `server→cable` (47), `server→fan` (36), `server→heatsink` (36) — все count>=3.

---

#### ЗАДАЧА 1.3: Расширить fp_patterns для HPE device_mismatch `server→*`

**Файл:** `batch_audit.py`, строки 925–928

**Что менять:**

Добавить в `fp_patterns` паттерны, которые являются известными особенностями HPE-pipeline (device_type=server на строках-компонентах внутри серверного модуля):

```python
fp_patterns = {
    # entity mismatches (AI ошибается)
    "HW→LOGISTIC", "HW→NOTE", "HW→CONFIG", "SOFTWARE→NOTE",
    "LOGISTIC→NOTE", "SERVICE→NOTE", "CONFIG→NOTE", "BASE→CONFIG",
    # HPE device mismatches (pipeline ставит server на компоненты серверного модуля)
    # TODO: убрать после исправления HPE rules
}
```

**ВАЖНО:** НЕ добавлять HPE `server→*` в fp_patterns на данном этапе. Причина: эти 47+36+36 строк могут быть реальными багами HPE-правил. Вместо этого добавить комментарий в код и оставить как REVIEW_NEEDED / REAL_BUG (задача 1.2 обработает их).

**Acceptance Criteria:**
1. HPE `server→cable/fan/heatsink` паттерны остаются видимыми в отчёте
2. Они получают bug_type=REAL_BUG (count>3, >2 файлов)
3. Комментарий в коде объясняет, почему они не в fp_patterns

---

#### ЗАДАЧА 1.4: Добавить E18 — LOGISTIC строка с физическим компонентом по keyword (расширение E13)

**Файл:** `batch_audit.py`, функция `validate_row()` (после строки 414)

**Что добавить:**

```python
# E18 — LOGISTIC строка, содержащая keyword физического компонента
# Расширение E13: ловит случаи, когда device_type не проставлен, но option_name физический
if entity == "LOGISTIC" and not device_type:
    physical_keywords = r'\b(cord|cable|rail|rails|bracket|mount|kit|rack|pdu|ups)\b'
    if re.search(physical_keywords, option_name, re.IGNORECASE):
        issues.append(f"E18:logistic_physical_keyword[suggest_HW]")
```

**Acceptance Criteria:**
1. Прогон --no-ai: E18 ловит LOGISTIC строки с "power cord", "rail kit" etc. без device_type
2. Не дублирует E13 (E13 работает когда device_type заполнен, E18 — когда пуст)
3. Прогон показывает ≥5 новых E18 (ожидаемо: Cisco stacking cables, HPE rail kits)

---

### ЭТАП 2 — Кластеризация как отдельный модуль cluster_audit.py

**Принцип:** Новый файл рядом с batch_audit.py. Читает те же *_annotated.xlsx. Выдаёт cluster_summary.xlsx + обновляет audit_report.json.

---

#### ЗАДАЧА 2.1: Создать скелет cluster_audit.py

**Файл:** `spec_classifier/cluster_audit.py` (новый)

**Структура:**

```
cluster_audit.py
├── CLI: --output-dir, --vendor, --min-cluster-size, --max-clusters
├── Step 1: load_candidate_rows(output_dir, vendor)
│           → читает *_annotated.xlsx
│           → фильтрует: E2 (UNKNOWN), E17 (HW без device_type),
│             entity=HW & device_type пусто, entity=LOGISTIC & E13/E18
│           → возвращает list[dict] с option_name, vendor, file, entity, device, hw
├── Step 2: normalize_text(rows)
│           → lowercase, remove prices, normalize units (gb/tb/gbe),
│             collapse variants (10gb→10gbe, sfp plus→sfp+)
│           → optional: strip part numbers
├── Step 3: vectorize(normalized_texts)
│           → TF-IDF, char n-grams (3,5), max_features=5000
├── Step 4: cluster(vectors)
│           → HDBSCAN (primary) + MiniBatchKMeans (fallback)
│           → return cluster_labels
├── Step 5: analyze_clusters(rows, labels)
│           → per cluster: count, top terms, examples (3–5), heuristic device_type
├── Step 6: heuristic_mapping(cluster_keywords)
│           → keyword→device_type dict (таблица из teresa_cluster_rule_discovery.txt)
│           → return proposed_device_type, proposed_hw_type
├── Step 7: write_cluster_summary(clusters, output_dir)
│           → cluster_summary.xlsx
│           → cluster section в audit_report.json (если существует)
└── main()
```

**Зависимости (добавить в requirements.txt):**
```
scikit-learn>=1.3.0
hdbscan>=0.8.33
```

**Acceptance Criteria:**
1. `python cluster_audit.py --output-dir OUTPUT --dry-run` — показывает кол-во candidate rows
2. Без HDBSCAN (fallback) — работает с MiniBatchKMeans
3. Не импортирует ничего из batch_audit.py или src/

---

#### ЗАДАЧА 2.2: Реализовать Step 1 — загрузка кандидатов

**Логика:**

```python
def load_candidate_rows(output_dir, vendor_filter=None):
    """
    Читает *_annotated.xlsx (или *_audited.xlsx если есть pipeline_check).
    Фильтрует строки по критериям:
    - entity_type == "UNKNOWN" (E2)
    - entity_type == "HW" and device_type пусто and hw_type пусто (E17)
    - entity_type == "LOGISTIC" and device_type in (power_cord, cable, ...)  (E13)
    - pipeline_check содержит E18 (если доступен)
    """
```

Приоритет чтения: если есть `*_audited.xlsx` — читать из него (там уже есть pipeline_check). Если нет — читать из `*_annotated.xlsx` и применять validate_row() локально.

**Acceptance Criteria:**
1. На текущих OUTPUT-данных (3296 строк) — загрузка ≥50 candidate rows
2. Каждый candidate row содержит: option_name, vendor, source_file, entity_type, device_type, hw_type
3. Дубликаты (одинаковый option_name из разных BOM) сохраняются (важно для count)

---

#### ЗАДАЧА 2.3: Реализовать Steps 2–4 — нормализация, векторизация, кластеризация

**Нормализация (Step 2):**

```python
UNIT_NORMALIZATIONS = {
    r'\b(\d+)\s*gb\b': r'\1gb',
    r'\b(\d+)\s*tb\b': r'\1tb',
    r'\b(\d+)\s*gbit\b': r'\1gbe',
    r'\b(\d+)\s*gbps\b': r'\1gbe',
    r'\bsfp\s*plus\b': 'sfp+',
    r'\bsfp\s*\+\b': 'sfp+',
}

def normalize_text(text):
    t = text.lower()
    t = re.sub(r'\$[\d,.]+', '', t)           # remove prices
    t = re.sub(r'\b[A-Z0-9]{6,}-[A-Z0-9]+\b', '', t, flags=re.I)  # remove part numbers (heuristic)
    for pattern, repl in UNIT_NORMALIZATIONS.items():
        t = re.sub(pattern, repl, t, flags=re.I)
    t = re.sub(r'\s+', ' ', t).strip()
    return t
```

**Векторизация (Step 3):** TF-IDF, char n-grams (3,5), max_features=5000.

**Кластеризация (Step 4):** HDBSCAN primary (min_cluster_size=3), MiniBatchKMeans fallback (n_clusters = min(50, len(rows)//5)).

**Acceptance Criteria:**
1. На >100 candidate rows: HDBSCAN выдаёт 10–80 кластеров + noise bucket
2. На <20 candidate rows: fallback на KMeans
3. Кластеры deterministic (random_state=42 для KMeans, HDBSCAN стабилен по дефолту)
4. Unit test: 10 строк с "sfp+ 10gbe transceiver" → один кластер

---

#### ЗАДАЧА 2.4: Реализовать Steps 5–6 — анализ кластеров и heuristic mapping

**Анализ кластеров:**
Для каждого cluster_id:
- count (кол-во строк)
- top_terms (5 самых частых токенов из нормализованных текстов)
- examples (до 5 representative rows — ближайшие к центроиду)
- vendors (уникальные вендоры в кластере)
- source_files (уникальные файлы)

**Heuristic mapping:**

```python
KEYWORD_DEVICE_MAP = {
    # keyword_regex → (device_type, hw_type)
    r'\b(power\s*cord|c13|c14|c15|c19|c20|jumper\s*cord)\b': ('power_cord', 'cable'),
    r'\b(rail|rails|cma|cable\s*management\s*arm)\b': ('rail', 'rail'),
    r'\b(sfp\+?|qsfp|transceiver|optic)\b': ('transceiver', 'transceiver'),
    r'\b(nvme|ssd|hdd|solid.state|hard.drive)\b': ('storage_drive', 'storage'),
    r'\b(fan|blower)\b': ('fan', 'cooling'),
    r'\b(heatsink|heat.sink)\b': ('heatsink', 'cooling'),
    r'\b(psu|power.supply)\b': ('psu', 'psu'),
    r'\b(riser)\b': ('riser', 'riser'),
    r'\b(bezel|blank|filler)\b': ('blank_filler', 'blank_filler'),
    r'\b(gpu|nvidia|tesla|a100|h100|l40)\b': ('gpu', 'gpu'),
    r'\b(tpm)\b': ('tpm', 'tpm'),
    r'\b(backplane)\b': ('backplane', 'backplane'),
    r'\b(battery|capacitor|bbwc)\b': ('battery', 'accessory'),
}
```

Для каждого кластера: применить KEYWORD_DEVICE_MAP к top_terms. Если ≥1 match → proposed_device_type + proposed_hw_type. Иначе → "MANUAL_REVIEW".

**Acceptance Criteria:**
1. Кластер с top_terms ["rail", "rack", "slide", "kit"] → proposed_device_type="rail"
2. Кластер с top_terms ["sfp+", "10gbe", "transceiver"] → proposed_device_type="transceiver"
3. Кластер без match → proposed_device_type="MANUAL_REVIEW"
4. Noise bucket (unclustered) → отдельная секция в отчёте

---

#### ЗАДАЧА 2.5: Реализовать Step 7 — отчёт

**cluster_summary.xlsx:**

| Колонка | Описание |
|---------|----------|
| cluster_id | Номер кластера (или "noise") |
| count | Кол-во строк |
| vendors | Уникальные вендоры |
| top_terms | Топ-5 ключевых слов |
| proposed_device_type | Предложенный device_type |
| proposed_hw_type | Предложенный hw_type |
| confidence | "heuristic" или "manual_review" |
| example_1 | Первая строка-пример (option_name) |
| example_2 | Вторая строка-пример |
| example_3 | Третья строка-пример |
| suggested_yaml_rule | Шаблон regex для YAML (если confidence=heuristic) |

**audit_report.json update:**

Если файл существует — добавить секцию `"clusters"` в JSON:

```json
{
  "clusters": {
    "total_candidates": 200,
    "total_clusters": 35,
    "noise_rows": 12,
    "clusters": [
      {
        "cluster_id": 7,
        "count": 18,
        "keywords": ["rail", "rack", "slide", "kit"],
        "proposed_device_type": "rail",
        "proposed_hw_type": "rail",
        "confidence": "heuristic",
        "examples": ["Rack Rail Kit for DL380 Gen11", "Sliding Rails Kit", "Rail Kit 2U Server"],
        "vendors": ["hpe", "dell"]
      }
    ]
  }
}
```

**Acceptance Criteria:**
1. cluster_summary.xlsx создаётся в OUTPUT dir
2. audit_report.json обновляется (если существует) без потери существующих секций
3. Каждый кластер имеет ≥3 строки (min_cluster_size)
4. suggested_yaml_rule — валидный regex (проверяемый re.compile)

---

#### ЗАДАЧА 2.6: CLI и интеграция

**Команды:**

```bash
# Полный прогон
python cluster_audit.py --output-dir OUTPUT

# Только определённый вендор
python cluster_audit.py --output-dir OUTPUT --vendor hpe

# С настройкой параметров
python cluster_audit.py --output-dir OUTPUT --min-cluster-size 5 --max-clusters 50

# Dry-run (показать кандидатов, не кластеризовать)
python cluster_audit.py --output-dir OUTPUT --dry-run
```

**Рекомендуемый workflow (в README или Makefile):**

```bash
# 1. Запуск Teresa
python main.py --vendor dell --input quotes/

# 2. Rule-based audit
python batch_audit.py --output-dir OUTPUT --no-ai

# 3. Кластеризация проблемных строк
python cluster_audit.py --output-dir OUTPUT

# 4. Review cluster_summary.xlsx → написать YAML-правила

# 5. Повторный прогон Teresa + audit → проверить снижение E2/E17
```

**Acceptance Criteria:**
1. `python cluster_audit.py --help` — показывает все опции
2. Exit code 0 при успехе, 1 при ошибке
3. Работает без batch_audit.py (читает *_annotated.xlsx напрямую)
4. Работает с *_audited.xlsx (если есть pipeline_check — использует его для фильтрации)

---

## ЧАСТЬ 3. ПОРЯДОК ВЫПОЛНЕНИЯ ДЛЯ CURSOR

### Этап 1 — batch_audit.py P0 fixes

```
Шаг 1.1: Правка LLM_SYSTEM (строки 82–108)
  → Файл: batch_audit.py
  → Строки: 98, 101, добавить после 103
  → Тест: прогон с AI, сравнить counts

Шаг 1.2: Замена hardcoded real_bug_patterns (строки 918–938)
  → Файл: batch_audit.py
  → Удалить real_bug_patterns set
  → Добавить dynamic classification logic
  → Тест: прогон, проверить bugs секцию

Шаг 1.3: Оставить HPE server→* как REVIEW_NEEDED/REAL_BUG
  → Файл: batch_audit.py
  → Добавить комментарий в fp_patterns
  → Тест: HPE паттерны видны в отчёте

Шаг 1.4: Добавить E18 check
  → Файл: batch_audit.py, функция validate_row()
  → Тест: прогон --no-ai, проверить новые E18 в отчёте
```

### Этап 2 — cluster_audit.py

```
Шаг 2.1: Скелет + CLI + dry-run
  → Новый файл: cluster_audit.py
  → Тест: --dry-run показывает кандидатов

Шаг 2.2: Загрузка кандидатов из annotated/audited xlsx
  → Тест: ≥50 кандидатов из текущих данных

Шаг 2.3: Нормализация + TF-IDF + кластеризация
  → requirements.txt: scikit-learn, hdbscan
  → Тест: 10–80 кластеров, deterministic

Шаг 2.4: Анализ кластеров + heuristic mapping
  → Тест: кластер с "rail" → proposed_device_type=rail

Шаг 2.5: cluster_summary.xlsx + audit_report.json update
  → Тест: файлы создаются, JSON не ломается

Шаг 2.6: README update + Makefile target
  → Тест: make cluster-audit работает
```

---

## SUMMARY

### CLAIMS

| # | Claim | Evidence | Confidence |
|---|-------|----------|------------|
| C1 | LLM_SYSTEM промпт содержит правило, противоречащее бизнес-логике Teresa (power cord = LOGISTIC) | batch_audit.py строка 101; batch_audit_review.txt п.1.2; audit_report.json: 102 HW→LOGISTIC false positives | Подтверждено, HIGH |
| C2 | Hardcoded real_bug_patterns не детектируют новые баги | batch_audit.py строки 920–924: 7 статических паттернов; audit_report.json: 28 REVIEW_NEEDED паттернов не проходят фильтр | Подтверждено, HIGH |
| C3 | AI не знает HW+ABSENT → 93 ложных AI_MISMATCH | audit_report.json: entity_mismatch HW→NOTE = 93; batch_audit_review.txt п.1.3 | Подтверждено, HIGH |
| C4 | Кластеризация из teresa_cluster_rule_discovery.txt реализуема и полезна | OUTPUT данные: 3296 строк, E2/E17 кандидаты в annotated.xlsx; алгоритм TF-IDF + HDBSCAN стандартный | Подтверждено, MEDIUM (зависит от кол-ва кандидатов) |
| C5 | Модуль 3 (AI Review Layer) преждевременен | audit_report.json: 26% false positive rate; batch_audit_review.txt п.3.1 | Подтверждено, HIGH |
| C6 | HPE device_mismatch server→* (47+36+36 строк) — известная особенность, не баг AI | audit_report.json: все server→* только от HPE; HPE rules ставят device_type=server на компоненты | Подтверждено, MEDIUM (требует проверки HPE rules) |

### SEVERITY

| Severity | Issue | Impact | Fix |
|----------|-------|--------|-----|
| **P0-CRITICAL** | LLM_SYSTEM противоречит бизнес-правилам | 102 false positives + AI не ловит реальные LOGISTIC-ошибки | Задача 1.1 |
| **P0-HIGH** | Hardcoded real_bug_patterns | Новые баги классифицируются как REVIEW_NEEDED | Задача 1.2 |
| **P0-HIGH** | AI не знает HW+ABSENT | 93 ложных AI_MISMATCH | Задача 1.1 (часть C) |
| **P1-MEDIUM** | Нет кластеризации → ручной просмотр 1000+ строк | Медленное создание правил | Этап 2 |
| **P2-LOW** | HPE server→* видимость | Шум в отчёте, но не ложный сигнал | Задача 1.3 (комментарий) |

### ACTION

| Приоритет | Действие | Estimated LOC | Estimated Time |
|-----------|----------|---------------|----------------|
| 1 | Задача 1.1: Fix LLM_SYSTEM prompt | ~30 строк изменений | 15 мин |
| 2 | Задача 1.2: Dynamic REAL_BUG classification | ~20 строк изменений | 15 мин |
| 3 | Задача 1.4: Add E18 check | ~10 строк | 10 мин |
| 4 | Задача 1.3: HPE comment | ~5 строк | 5 мин |
| 5 | **ПРОГОН batch_audit.py → валидация Этапа 1** | 0 | 10 мин |
| 6 | Задача 2.1–2.2: cluster_audit.py skeleton + load | ~150 строк | 45 мин |
| 7 | Задача 2.3: Normalize + vectorize + cluster | ~120 строк | 30 мин |
| 8 | Задача 2.4: Analysis + heuristic mapping | ~100 строк | 30 мин |
| 9 | Задача 2.5: Reports (xlsx + json) | ~120 строк | 30 мин |
| 10 | Задача 2.6: CLI + integration + README | ~50 строк | 15 мин |
| 11 | **ПРОГОН cluster_audit.py → валидация Этапа 2** | 0 | 10 мин |

**Итого estimated:** ~600 новых строк кода, ~3.5 часа работы.

**Ожидаемый результат после обоих этапов:**
- False positive rate: 26% → <10%
- Manual review: 1000+ строк → 20–50 кластеров
- Новые баги: автоматическая детекция (dynamic REAL_BUG)
- Rule discovery: cluster_summary.xlsx → прямая генерация YAML-правил
