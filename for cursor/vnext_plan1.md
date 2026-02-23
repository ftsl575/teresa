# Dell Spec Classifier — vNext Plan

**Версия документа**: 1.1 (vNext, точечные правки)
**Дата**: 2026-02-23
**Цель**: Закрыть gap'ы из audit_report.md и run_results.md (dl1–dl5). Не меняем архитектуру, не добавляем фичи без обоснования данными.

---

## Changelog документа (v1.0 → v1.1)

- **[Fix 1 — Power cord rule]** Паттерн `LOGISTIC-004-CORD` переведён на `option_name` как primary (содержит "Cord", "C13/C14", "C19/C20" во всех 3 UNKNOWN-SKU из run_results.md); `module_name` помечен как TBD-сигнал до верификации в xlsx. Добавлен явный DoD по покрытию 450-AADX/AADY/AAXT. Обновлены: Phase 2B Группа 1, MUST-FIX summary, матрица, тест-кейс #14.
- **[Fix 2 — Regex-нотация]** В summary-таблице добавлен явный notice: `\|` в ячейках таблицы — Markdown-экранирование, в YAML-паттернах пишется `|`. Добавлено требование: все паттерны должны быть валидированы `re.search()` в unit-тестах на примерах из run_results.md до коммита.
- **[Fix 3 — Anti-regression DoD Phase 2]** В DoD Phase 2 добавлено требование: diff `classification.jsonl` до/после должен затрагивать **только** строки с baseline `matched_rule_id = UNKNOWN-000`. Добавлен конкретный PowerShell-скрипт верификации diff. Требование продублировано в Prompt 2 DoD.
- **[Fix 4 — device_type контракт]** В Phase 2A добавлены 2 предложения: device_type назначается исключительно правилами; для HEADER, UNKNOWN (UNKNOWN-000), BASE, CONFIG, SOFTWARE, SERVICE, NOTE — поле отсутствует/null. DoD Phase 2A, Manual QA checklist, Prompt 2 DoD обновлены под этот контракт.

---

# [UNDERSTANDING]

## Что нужно улучшить и почему

**Блокер тестирования (audit C1/C2/C3/C4):** `test_data/` лежит вне `dell_spec_classifier/`, поэтому все smoke/regression/integration тесты молча пропускаются (`pytest.skip`). Golden-файлы не существуют (папка `golden/` содержит только `.gitkeep`). Regression параметризована на dl1–dl2 вместо dl1–dl5. Smoke — только dl1. Итог: **нулевое фактическое тестовое покрытие на реальных данных**, хотя unit-тесты (21+8+12 = 41) проходят без xlsx-файлов.

**UNKNOWN выше 5% на dl3 (audit F3, run_results):** dl3 — 12/89 = 13.5%; dl1 — 4/49 = 8.2%; dl2 — 8/365 = 2.2%; dl4 — 2/50 = 4%; dl5 — 1/38 = 2.6%. Конкретные паттерны из unknown_rows.csv четко идентифицированы и поддаются детерминированным правилам.

**device_type отсутствует:** Spec требует новое поле для HW и LOGISTIC в classification.jsonl и run_summary.json. Это требование по Acceptance Criteria C, данные для обоснования есть.

**Документация (audit D):** README.md содержит только секцию Regression; отсутствуют установка, CLI, артефакты, row_kind/state, entity_type, Rules Change Process.

## Точные gap'ы

- `test_data/` не в `dell_spec_classifier/` → все тесты с файлами skip (audit C1, блокер)
- `golden/` пустая → regression не работает (audit C2, блокер)
- Regression параметризована `["dl1.xlsx", "dl2.xlsx"]` → dl3–dl5 не покрыты (audit C3)
- Smoke только на dl1 → dl2–dl5 не проверяются (audit C4)
- `input_snapshot.json` не генерируется (audit C5, низкий приоритет)
- `run.log`: FileHandler создаётся после parse/normalize → ранние этапы не логируются (audit B10)
- UNKNOWN dl1: 4 строки (450-AADX, 345-BDPH, 384-BDQX, 540-BCXX)
- UNKNOWN dl2: 8 строк — все один SKU 450-AADY (Power Cord) повторяется 8 раз
- UNKNOWN dl3: 12 строк — 450-AADY×2, 405-BBDC, 470-ACEV, 540-BCRY, 384-BDRL, 345-BKBV, 403-BDMW, 338-CSZN, 338-CSZP, 405-BBDD, 470-ADDO
- UNKNOWN dl4: 2 строки — 450-AAXT, 540-BDHC
- UNKNOWN dl5: 1 строка — 450-AADY
- `device_type` поле не существует в коде, классификаторе, правилах, артефактах
- README отсутствуют: установка, CLI примеры, артефакты, row_kind, entity_type, state, Rules Change Process

---

# [QUESTIONS]

No questions; sufficient facts provided.

---

# [MASTER_PLAN]

---

## Phase 0 — Gating: Test Data Paths & Ignore

**Goal:** Сделать так, чтобы unit-тесты всегда проходили, а smoke/regression запускались при наличии xlsx-файлов по документированному пути.

**Tasks:**
- Задокументировать ожидаемый путь: `dell_spec_classifier/test_data/dl{1..5}.xlsx` (не коммитим xlsx в git, добавляем в `.gitignore`).
- Убедиться, что `_project_root() / "test_data"` разрешается корректно из `dell_spec_classifier/` (не из `teresa-main/`).
- Добавить `test_data/*.xlsx` в `.gitignore`.
- Unit-тесты (`test_rules_unit.py`, `test_state_detector.py`, `test_normalizer.py`) должны проходить без xlsx-файлов — проверить отсутствие неявных зависимостей.
- Добавить в `conftest.py` фикстуру `skip_if_no_test_data` (уже может быть; если нет — добавить явно), чтобы пропуски были видимы как `SKIPPED` с конкретным сообщением, а не тихим skip.

**DoD / Acceptance:**
- `cd dell_spec_classifier && pytest tests/test_rules_unit.py tests/test_state_detector.py tests/test_normalizer.py -v` → 41+ passed, 0 failed, 0 errors (без xlsx).
- `pytest tests/ -v` без xlsx → все smoke/regression/integration → SKIPPED (с сообщением), не ERROR.
- `pytest tests/ -v` при наличии `test_data/dl1.xlsx` → smoke dl1 проходит без skip.
- `test_data/*.xlsx` присутствует в `.gitignore`.

**Verification commands:**
```powershell
# Без xlsx-файлов:
cd dell_spec_classifier
pytest tests/test_rules_unit.py tests/test_state_detector.py tests/test_normalizer.py -v --tb=short
# Ожидание: 41+ passed

# Проверка .gitignore:
Select-String "test_data" .gitignore
```

**Risks:** Если `_project_root()` зависит от CWD, а не от `__file__` — потребуется правка функции.
**Effort:** S | **Priority:** P0

---

## Phase 1 — Golden + Full Regression + UNKNOWN Coverage Check

**Goal:** Сгенерировать golden для dl1–dl5, расширить тесты до dl1–dl5, ввести автоматическую проверку UNKNOWN ≤ 5%.

**Tasks:**
- Сгенерировать golden-файлы для dl1–dl5:
  ```
  python main.py --input test_data/dl1.xlsx --save-golden
  python main.py --input test_data/dl2.xlsx --save-golden
  python main.py --input test_data/dl3.xlsx --save-golden
  python main.py --input test_data/dl4.xlsx --save-golden
  python main.py --input test_data/dl5.xlsx --save-golden
  ```
  Визуально проверить `unknown_rows.csv` (до правок Phase 2 — это baseline).
- Расширить `test_regression.py`: параметризация `["dl1.xlsx", "dl2.xlsx", "dl3.xlsx", "dl4.xlsx", "dl5.xlsx"]`.
- Расширить `test_smoke.py`: параметризовать по всем 5 файлам.
- Добавить coverage-тест `test_unknown_threshold.py` (или параметр в regression): для каждого dl проверить `unknown_count / item_rows_count <= 0.05`. Baseline UNKNOWN-метрики из run_results.md:
  | dl | item_rows | unknown_now | threshold_5% |
  |----|-----------|-------------|--------------|
  | dl1| 49        | 4 (8.2%)    | ≤ 2          |
  | dl2| 365       | 8 (2.2%)    | ≤ 18         |
  | dl3| 89        | 12 (13.5%)  | ≤ 4          |
  | dl4| 50        | 2 (4.0%)    | ≤ 2          |
  | dl5| 38        | 1 (2.6%)    | ≤ 1          |
  - dl1 и dl3 failing threshold → Phase 2 должна снизить до ≤5% до финального golden.
- Golden коммитятся **только после** Phase 2 (с уже закрытыми UNKNOWN).
  - До Phase 2: golden — interim baseline, регрессия по нему не запускается как gating.
  - После Phase 2: регенерировать golden, закоммитить финальную версию.

**DoD / Acceptance:**
- `pytest tests/test_smoke.py -v` при наличии dl1–dl5.xlsx → 5 passed.
- `pytest tests/test_regression.py -v` → параметры включают dl1–dl5 (файлы существуют → runs).
- `pytest tests/test_unknown_threshold.py -v` → dl2, dl4, dl5 passed; dl1 и dl3 — TBD (после Phase 2 → all pass).
- `golden/` содержит `dl1_expected.jsonl` … `dl5_expected.jsonl` (финальные, после Phase 2).

**Verification commands:**
```powershell
cd dell_spec_classifier
# Генерация golden (после Phase 2):
foreach ($i in 1..5) { python main.py --input test_data/dl$i.xlsx --save-golden }

# Прогон тестов:
pytest tests/test_smoke.py tests/test_regression.py tests/test_unknown_threshold.py -v --tb=short
```

**Risks:** golden должны быть вручную проверены перед коммитом; не коммитить с непроверенным UNKNOWN-содержимым.
**Effort:** M | **Priority:** P0

---

## Phase 2 — device_type Model + Rules for UNKNOWN Closure

**Goal:** Добавить поле `device_type` в модель данных и правила; закрыть все UNKNOWN из unknown_rows.csv (dl1–dl5) или явно пометить out-of-scope.

### 2A — device_type модель

**Tasks:**
- Добавить `device_type: str | None` в dataclass `ClassifiedRow` (или аналогичный output-объект).
- В `classifier.py`: после определения `entity_type` выполнить отдельный second-pass матч по `device_type_rules` (тот же first-match YAML, только для HW и LOGISTIC).
- В `dell_rules.yaml`: добавить секцию `device_type_rules` с полями `rule_id`, `applies_to` (список EntityType), `field`, `pattern`, `device_type`.
- **Источник истины:** `device_type` назначается **исключительно правилами** (`rule_id → {entity_type, device_type}`); никакой эвристики, умолчаний по имени модуля или иного вывода без явного правила.
- **Контракт поля в артефактах:** в `classification.jsonl` поле `device_type` присутствует **только** у строк с `row_kind = ITEM` и `matched_rule_id != UNKNOWN-000`. Для строк с `row_kind = HEADER`, `entity_type = UNKNOWN` (т.е. `matched_rule_id = UNKNOWN-000`), а также для типов, не входящих в `applies_to` (BASE, CONFIG, SOFTWARE, SERVICE, NOTE), поле `device_type` отсутствует или равно `null`.
- В `classification.jsonl`: добавить поле `device_type` согласно контракту выше.
- В `run_summary.json`: добавить `device_type_counts` (агрегация ненулевых значений по строкам с непустым `device_type`).

**DoD (Phase 2A):** `classification.jsonl` содержит поле `device_type`; поле присутствует и непусто только для строк `ITEM` с `matched_rule_id != UNKNOWN-000`; для HEADER и UNKNOWN строк — отсутствует/null; `run_summary.json` содержит `device_type_counts`; unit-тест `test_device_type.py` включает кейс "UNKNOWN строка → device_type is null".

### 2B — MUST-FIX список UNKNOWN → правила

Все 27 уникальных UNKNOWN-случаев (по данным dl1–dl5) разобраны ниже:

#### Группа 1: Power Cords (module_name = "Power Cords")

| SKU | option_name | Встречается в | Предлагаемое действие |
|-----|------------|---------------|-----------------------|
| 450-AADX | Jumper Cord - C13/C14, 0.6M, 250V, 10A | dl1 | LOGISTIC, device_type=power_cord |
| 450-AADY | Rack Power Cord 2M (C13/C14 10A) | dl2×8, dl3×2, dl5×1 | LOGISTIC, device_type=power_cord |
| 450-AAXT | C19 to C20, 250V, 0.6m Power Cord | dl4 | LOGISTIC, device_type=power_cord |

**Rule placeholder:** `LOGISTIC-004-CORD` (LOGISTIC-002/003 — проверить yaml на предмет занятости).

**Pattern (базовый — по option_name):** `option_name` matches `(?i)(power\s+cord|jumper\s+cord|rack\s+cord|C13|C14|C19|C20)`.
Все три UNKNOWN-SKU содержат в option_name явные маркеры ("Cord", "C13/C14", "C19 to C20") — это устойчивый детерминированный сигнал, не зависящий от заполнения module_name.

**module_name как дополнительный сигнал:** В unknown_rows.csv (run_results.md) все три строки имеют `module_name = "Power Cords"`. Если это подтверждается в xlsx (фактическое значение ячейки), можно добавить второй вариант правила по `module_name` → `(?i)^power\s+cords?$`. **До верификации в xlsx — использовать только option_name паттерн как primary; module_name вариант помечается TBD.**

> ⚠️ Факт: в dl2 LOGISTIC=48, и одновременно 8 power cord UNKNOWN. Значит LOGISTIC-001 срабатывает на что-то другое, а Power Cords — отдельный паттерн. Это подтверждает необходимость нового правила, но основа — option_name, не module_name.

**DoD для этой группы:** После добавления LOGISTIC-004-CORD прогон dl1–dl5 должен показать `unknown_count = 0` для всех SKU 450-AADX, 450-AADY, 450-AAXT. Проверять явно: `Get-Content output/vnext_check/dl*/*/unknown_rows.csv | Select-String "450-AAD|450-AAXT"` → пустой вывод.

#### Группа 2: SSD/NVMe (Storage)

| SKU | option_name | dl | Действие |
|-----|------------|-----|----------|
| 345-BDPH | 480GB SSD SATA Mixed Use 6Gbps 512e 2.5in Hot-Plug, CUS Kit | dl1 | HW, device_type=storage_ssd |
| 345-BKBV | 800G Data Center NVMe Mixed Use AG Drive U2 with carrier, Customer Kit | dl3 | HW, device_type=storage_nvme |

**Rule placeholder:** `HW-005-STORAGE-CUS` — `option_name` matches `(?i)(ssd|nvme|sata|hot-plug).*(cus(tomer)?\s+kit|ck)`.

#### Группа 3: Power Supply (PSU)

| SKU | option_name | dl | Действие |
|-----|------------|-----|----------|
| 384-BDQX | Single, Hot-Plug MHS Power Supply, 800W, Customer Kit | dl1 | HW, device_type=psu |
| 384-BDRL | Single, Hot-Plug MHS Power Supply, 1500W, Titanium, Customer Kit | dl3 | HW, device_type=psu |

**Rule placeholder:** `HW-006-PSU-CUS` — `option_name` matches `(?i)power\s+supply.*(cus(tomer)?\s+kit|ck)`.

#### Группа 4: NIC / SFP (Network)

| SKU | option_name | dl | Действие |
|-----|------------|-----|----------|
| 540-BCXX | Intel E810-XXV 25GbE SFP28 Dual Port PCIe Low Profile Customer Kit | dl1 | HW, device_type=nic |
| 540-BCRY | Broadcom 57504 Quad Port 10/25GbE, SFP28, OCP NIC 3.0 Customer Install | dl3 | HW, device_type=nic |
| 470-ACEV | Dell Networking, Cable, SFP28 to SFP28, 25GbE, Passive Copper Twinax, 3M | dl3 | LOGISTIC, device_type=sfp_cable |
| 470-ADDO | SC Cable, SFP28 to SFP28, 25GbE, Passive Copper Twinax, 3M, Cus Kit | dl3 | LOGISTIC, device_type=sfp_cable |

**Rule placeholder NIC:** `HW-007-NIC-CUS` — `option_name` matches `(?i)(gbe|sfp28|sfp\+|nic|ocp).*(cus(tomer)?\s+(kit|install)|ck)`.
**Rule placeholder SFP Cable:** `LOGISTIC-005-SFP-CABLE` — `option_name` matches `(?i)(sfp|twinax|dac).*(cable|direct\s+attach)` OR `module_name` matches `(?i)sfp\s+module`.

#### Группа 5: HBA / PERC / FC Adapters (Storage Controllers)

| SKU | option_name | dl | Действие |
|-----|------------|-----|----------|
| 405-BBDC | HBA465e Adapter Full Height DIB | dl3 | HW, device_type=hba |
| 405-BBDD | HBA465e Adapter Full Height/Low Profile, CK | dl3 | HW, device_type=hba |
| 403-BDMW | PERC H965i Controller, Front, DCMHS, CK | dl3 | HW, device_type=raid_controller |
| 540-BDHC | QLogic 2772 Dual Port 32Gb Fibre Channel HBA, PCIe Full Height, V2 | dl4 | HW, device_type=hba |

**Rule placeholder:** `HW-008-HBA-PERC-CUS` — `option_name` matches `(?i)(hba|perc|fibre\s+channel|fc\s+hba|raid\s+controller).*(dib|ck|full\s+height|low\s+profile)`.

> ⚠️ Проверить, почему `405-BBDC` (no "CK" suffix) не покрывается HW-003 или HW-004. Паттерн DIB может быть edge case.

#### Группа 6: CPU (Processor)

| SKU | option_name | dl | Действие |
|-----|------------|-----|----------|
| 338-CSZN | Intel Xeon 6 Performance 6737P 2.9G, 32C/64T … Customer Install | dl3 | HW, device_type=cpu |
| 338-CSZP | Intel Xeon 6 Performance 6511P 2.5G, 16C/32T … Customer Install | dl3 | HW, device_type=cpu |

**Rule placeholder:** `HW-009-CPU-CUS` — `option_name` matches `(?i)(xeon|intel\s+xeon).*(customer\s+install|cus(tomer)?\s+kit|ck)`.

> ⚠️ Проверить, почему HW-001 или HW-002 не покрывают эти строки — "Intel Xeon 6" vs "Intel Xeon" в существующем паттерне. Возможно, HW-002 матчит только `Module Name = Processor` и здесь module_name пустой.

#### Итоговый MUST-FIX summary

> ⚠️ **Regex-нотация:** паттерны ниже — это Python-совместимые regex (для `re` / PyYAML). Символ `|` — alternation оператор Python regex; он **не экранируется** в YAML-значении как `\|`. Все паттерны должны быть проверены unit-тестом (`test_rules_unit.py` или `test_device_type.py`) на примерах из run_results.md до коммита в `dell_rules.yaml`.

| rule_id placeholder | Паттерн (field → Python regex) | Покрывает SKU | entity_type | device_type |
|--------------------|-------------------------------|---------------|-------------|-------------|
| LOGISTIC-004-CORD  | option_name → `(?i)(power cord\|jumper cord\|rack cord\|C13\|C14\|C19\|C20)` | 450-AADX, 450-AADY, 450-AAXT | LOGISTIC | power_cord |
| HW-005-STORAGE-CUS | option_name → `(?i)(ssd\|nvme\|sata).*(cus(tomer)? kit\|ck)` | 345-BDPH, 345-BKBV | HW | storage_ssd / storage_nvme |
| HW-006-PSU-CUS | option_name → `(?i)power supply.*(cus(tomer)? kit\|ck)` | 384-BDQX, 384-BDRL | HW | psu |
| HW-007-NIC-CUS | option_name → `(?i)(gbe\|sfp28\|ocp nic).*(cus(tomer)? (kit\|install)\|ck)` | 540-BCXX, 540-BCRY | HW | nic |
| LOGISTIC-005-SFP-CABLE | option_name → `(?i)(sfp\|twinax).*(cable\|direct attach)` | 470-ACEV, 470-ADDO | LOGISTIC | sfp_cable |
| HW-008-HBA-PERC-CUS | option_name → `(?i)(hba\|perc\|fibre channel).*(dib\|ck\|full height)` | 405-BBDC/DD, 403-BDMW, 540-BDHC | HW | hba / raid_controller |
| HW-009-CPU-CUS | option_name → `(?i)(xeon).*(customer install\|ck)` | 338-CSZN, 338-CSZP | HW | cpu |

> 📌 **Nota bene (Markdown vs YAML):** в таблице выше `\|` — это Markdown-экранирование символа `|` в ячейке таблицы. В YAML-файле (`dell_rules.yaml`) пишите `|` без обратного слеша. В unit-тестах проверяйте паттерн через `re.search(pattern, option_name, re.IGNORECASE)` с фактическими строками из unknown_rows.csv.

**Out-of-scope:** Нет ни одного UNKNOWN, который следует пометить out-of-scope — все имеют однозначную интерпретацию по имеющимся данным.

**Tasks Phase 2:**
- Добавить 6 новых правил в `dell_rules.yaml` (см. таблицу выше) с конкретными rule_id.
- Добавить `device_type_rules` секцию в `dell_rules.yaml`.
- Обновить `classifier.py` для second-pass device_type матча.
- Обновить `ClassifiedRow` / output dataclass.
- Обновить `excel_writer.py` / `outputs.py` для записи `device_type` в `classification.jsonl`.
- Обновить `run_summary.json` генератор для `device_type_counts`.
- Добавить unit-тесты `test_device_type.py` (минимум 7 тест-кейсов по таблице выше + 2 edge case).
- После добавления правил — прогнать dl1–dl5, убедиться, что UNKNOWN ≤ 5% на всех.
- Регенерировать golden (финальные).

**DoD / Acceptance:**
- `run_summary.json` содержит `device_type_counts`.
- `classification.jsonl` — каждая строка HW/LOGISTIC с `matched_rule_id != UNKNOWN-000` содержит непустой `device_type`.
- `pytest tests/test_device_type.py -v` → all passed.
- `pytest tests/test_unknown_threshold.py -v` → all 5 dl passed (UNKNOWN ≤ 5%).
- dl1: ≤2 UNKNOWN (было 4), dl3: ≤4 UNKNOWN (было 12), dl2/dl4/dl5 уже в норме.
- **Anti-regression:** прогон dl1–dl5 до/после Phase 2; diff `classification.jsonl` должен затрагивать **только** строки, у которых `matched_rule_id` изменился с `UNKNOWN-000` на новый rule_id. Строки с любым другим `matched_rule_id` (HW-001–004, LOGISTIC-001–003, и т.д.) не должны измениться.

**Anti-regression verification:**
```powershell
# Сохранить baseline (до правок):
foreach ($i in 1..5) {
  Copy-Item output/vnext_check/dl$i/*/classification.jsonl `
    output/vnext_check/dl$i/classification_baseline.jsonl
}
# После добавления правил — прогнать заново:
foreach ($i in 1..5) {
  python main.py --input test_data/dl$i.xlsx --output-dir output/vnext_check/dl$i
}
# Diff: все различия должны быть только в строках с UNKNOWN-000 в baseline:
foreach ($i in 1..5) {
  $before = Get-Content output/vnext_check/dl$i/classification_baseline.jsonl | ConvertFrom-Json
  $after  = Get-Content output/vnext_check/dl$i/*/classification.jsonl | ConvertFrom-Json
  $changed = for ($j=0; $j -lt $before.Count; $j++) {
    if ($before[$j].matched_rule_id -ne $after[$j].matched_rule_id) { $before[$j] }
  }
  $illegal = $changed | Where-Object { $_.matched_rule_id -ne "UNKNOWN-000" }
  if ($illegal) { Write-Error "dl$i: non-UNKNOWN rows changed — REGRESSION" }
  else { Write-Host "dl$i anti-regression OK ($($changed.Count) rows reclassified from UNKNOWN-000)" }
}
```

**Verification commands:**
```powershell
cd dell_spec_classifier
# Прогон после правок:
foreach ($i in 1..5) {
  python main.py --input test_data/dl$i.xlsx --output-dir output/vnext_check/dl$i
}
# Проверить UNKNOWN:
foreach ($i in 1..5) {
  $s = Get-Content output/vnext_check/dl$i/*/run_summary.json | ConvertFrom-Json
  Write-Host "dl$i unknown=$($s.unknown_count) item_rows=$($s.item_rows_count)"
}
# Тесты:
pytest tests/test_device_type.py tests/test_unknown_threshold.py -v --tb=short
```

**Risks:** Паттерн `HW-008` для `405-BBDC` (без явного CK) требует проверки на ложные срабатывания с другими HBA-строками, которые уже покрыты HW-003/HW-004.
**Effort:** M | **Priority:** P1

---

## Phase 3 — Документация

**Goal:** README и CHANGELOG соответствуют реальному поведению; Rules Change Process задокументирован; команды запуска проверены.

**Tasks:**
- Дописать `README.md` (секции: Installation, Quick Start, CLI Reference, Artifacts, entity_type / row_kind / state, Rules Change Process, How to update golden, How to run tests, config.yaml reference).
- В секции Rules Change Process: шаги — (1) edit `dell_rules.yaml`, (2) add unit test in `test_rules_unit.py`, (3) run pipeline on dl1–dl5, (4) verify unknown_rows.csv, (5) `--update-golden` + manual review, (6) update CHANGELOG.md, (7) commit.
- Задокументировать, что `test_data/*.xlsx` не в git; инструкция по размещению файлов локально.
- Задокументировать: `--update-golden` не работает в non-interactive (EOFError → 'n'), CI должен использовать `--save-golden` на новых файлах.
- Добавить `output_columns` в `config.yaml` (или комментарий, что колонки фиксированы в `excel_writer.py`).
- Добавить в CHANGELOG.md запись `vNext` (версия TBD — определить по SemVer: 1.1.0 если minor, 2.0.0 если breaking из-за device_type).
- Исправить `run.log`: переместить создание FileHandler **до** вызова parse/normalize (или добавить MemoryHandler с flush в file после создания папки).

**DoD / Acceptance:**
- `README.md` содержит все секции из audit D.
- `README.md` содержит секцию "Rules Change Process" с ≥5 шагами.
- `README.md` содержит команду установки и примеры CLI.
- `CHANGELOG.md` содержит запись для vNext с device_type и новыми правилами.
- `run.log` после прогона содержит строки parse и normalize этапов.

**Verification commands:**
```powershell
# Проверить секции README:
Select-String "Rules Change Process|Installation|Quick Start|Artifacts|entity_type" README.md

# Проверить run.log содержит ранние этапы:
python main.py --input test_data/dl1.xlsx
Select-String "parse|normaliz" output/*/run.log | Select-Object -First 5
```

**Risks:** Низкий. Чисто документация + мелкие правки.
**Effort:** S | **Priority:** P2

---

## Phase 4 (optional) — Мелкие артефакты

**Goal:** Добавить `input_snapshot.json` и опционально отдельный `rules_stats.json`.

**Tasks:**
- Добавить генерацию `input_snapshot.json`: `{"input_file": path, "file_size_bytes": N, "sha256": hash, "processed_at": ts}`.
- Опционально: добавить отдельный `rules_stats.json` (данные уже есть в `run_summary.json`).

**DoD:** `input_snapshot.json` присутствует в run-папке после каждого прогона.
**Effort:** S | **Priority:** P2

---

# [ISSUE_FIX_VERIFICATION_MATRIX]

| Issue (источник) | Fix | How to verify |
|-----------------|-----|---------------|
| `test_data/` не в `dell_spec_classifier/` (audit C1) | Поместить dl1–dl5.xlsx в `dell_spec_classifier/test_data/`; добавить в `.gitignore` | `pytest tests/ -v` → smoke/regression not SKIPPED; `Select-String "test_data" .gitignore` |
| golden/ пустая (audit C2) | `python main.py --save-golden --input test_data/dlX.xlsx` для dl1–dl5 | `ls golden/*.jsonl` → 5 файлов |
| Regression только dl1–dl2 (audit C3) | Расширить параметризацию `test_regression.py` до dl1–dl5 | `grep -A3 "parametrize" tests/test_regression.py` содержит dl3–dl5 |
| Smoke только dl1 (audit C4) | Параметризовать `test_smoke.py` по dl1–dl5 | `pytest tests/test_smoke.py -v` → 5 passed |
| UNKNOWN >5% dl1 (8.2%) (run_results dl1) | Добавить правила LOGISTIC-004-CORD, HW-005-STORAGE-CUS, HW-006-PSU-CUS, HW-007-NIC-CUS | `run_summary.json` dl1 `unknown_count ≤ 2` |
| UNKNOWN >5% dl3 (13.5%) (run_results dl3) | Добавить правила фаз 2 (все 6 групп) | `run_summary.json` dl3 `unknown_count ≤ 4` |
| 450-AADY×8 в dl2 (run_results dl2) | LOGISTIC-004-CORD по `option_name` (primary); `module_name` как доп. сигнал — TBD до верификации xlsx | dl2 `unknown_count = 0` |
| `device_type` отсутствует (AC-C) | Секция `device_type_rules` в yaml; second-pass в classifier; поле в jsonl/summary | `classification.jsonl` — HW строки содержат `device_type`; `run_summary.json` содержит `device_type_counts` |
| `input_snapshot.json` не создаётся (audit C5) | Добавить генерацию в `main.py`/`outputs.py` | `ls output/*/input_snapshot.json` → присутствует |
| `run.log` не содержит ранние этапы (audit B10) | FileHandler до parse/normalize | `Select-String "parse\|normaliz" output/*/run.log` → есть строки |
| README неполный (audit D) | Дописать все секции | `Select-String "Rules Change Process\|Installation" README.md` → находит обе |

---

# [VALIDATION]

## Тест-кейсы (15 штук)

| # | Тип | input (field → value) | Ожидаемый entity_type | Ожидаемый device_type | rule_id |
|---|-----|----------------------|----------------------|----------------------|---------|
| 1 | happy | option_name="Rack Power Cord 2M (C13/C14 10A)", skus="450-AADY" (module_name — любой, не влияет на матч) | LOGISTIC | power_cord | LOGISTIC-004-CORD |
| 2 | happy | option_name="C19 to C20, 250V, 0.6m Power Cord", skus="450-AAXT" (module_name — любой, не влияет на матч) | LOGISTIC | power_cord | LOGISTIC-004-CORD |
| 3 | happy | option_name="480GB SSD SATA Mixed Use … CUS Kit", skus="345-BDPH" | HW | storage_ssd | HW-005-STORAGE-CUS |
| 4 | happy | option_name="800G Data Center NVMe … Customer Kit", skus="345-BKBV" | HW | storage_nvme | HW-005-STORAGE-CUS |
| 5 | happy | option_name="Single, Hot-Plug MHS Power Supply, 800W, Customer Kit", skus="384-BDQX" | HW | psu | HW-006-PSU-CUS |
| 6 | happy | option_name="Intel E810-XXV 25GbE SFP28 Dual Port PCIe … Customer Kit", skus="540-BCXX" | HW | nic | HW-007-NIC-CUS |
| 7 | happy | option_name="Dell Networking, Cable, SFP28 to SFP28, 25GbE, Passive Copper Twinax, 3M", skus="470-ACEV" | LOGISTIC | sfp_cable | LOGISTIC-005-SFP-CABLE |
| 8 | happy | option_name="HBA465e Adapter Full Height DIB", skus="405-BBDC" | HW | hba | HW-008-HBA-PERC-CUS |
| 9 | happy | option_name="PERC H965i Controller, Front, DCMHS, CK", skus="403-BDMW" | HW | raid_controller | HW-008-HBA-PERC-CUS |
| 10 | happy | option_name="QLogic 2772 Dual Port 32Gb Fibre Channel HBA, PCIe Full Height, V2", skus="540-BDHC" | HW | hba | HW-008-HBA-PERC-CUS |
| 11 | happy | option_name="Intel Xeon 6 Performance 6737P 2.9G, 32C/64T … Customer Install", skus="338-CSZN" | HW | cpu | HW-009-CPU-CUS |
| 12 | edge | module_name=None, option_name=None, skus=None | HEADER (skip) | N/A | HEADER-SKIP |
| 13 | edge | option_name="Single, Hot-Plug MHS Power Supply, 800W" (без "Customer Kit") | HW (или UNKNOWN) | TBD | Проверить: не должен попасть в HW-006-PSU-CUS; если уже покрыт HW-002 — HW |
| 14 | edge | option_name="Rack Power Cord 2M (C13/C14 10A)" (module_name пустой, не "Power Cords") | LOGISTIC | power_cord | Должен совпасть по option_name (паттерн `(?i)cord\|C13\|C14`); подтверждает, что primary — option_name, не module_name |
| 15 | edge | option_name="SFP28 Transceiver, 25GbE" (не cable) | HW (оптика) | TBD — не sfp_cable | Не должен попасть в LOGISTIC-005; проверить паттерн |

## Manual QA checklist (после каждого прогона dl1–dl5)

- [ ] `unknown_count / item_rows_count ≤ 0.05` для каждого dl
- [ ] `unknown_rows.csv` пустой или содержит только задокументированные out-of-scope
- [ ] `classification.jsonl` — все ITEM-строки HW/LOGISTIC с `matched_rule_id != UNKNOWN-000` имеют непустой `device_type`; строки с UNKNOWN-000 и HEADER — `device_type` отсутствует/null
- [ ] `run_summary.json` содержит `device_type_counts`
- [ ] `cleaned_spec.xlsx` не содержит HEADER/CONFIG/LOGISTIC/NOTE/UNKNOWN/ABSENT/DISABLED строк
- [ ] `run.log` содержит записи для всех этапов (parse, normalize, classify)
- [ ] `input_snapshot.json` присутствует и содержит корректный sha256

---

# [PROMPT_PACK_FOR_OTHER_CODER]

---

## Prompt 1: Tests / Golden / Coverage

**Context:**
Репозиторий `dell_spec_classifier/` — детерминированный пайплайн классификации Excel-спецификаций Dell. Тесты существуют, но не работают из-за:
1. `test_data/dl1–dl5.xlsx` находятся в `teresa-main/test_data/`, а тесты ищут `dell_spec_classifier/test_data/` через `_project_root()`.
2. `golden/` пуста — нет `dl1_expected.jsonl … dl5_expected.jsonl`.
3. `test_regression.py` параметризован только на dl1–dl2.
4. `test_smoke.py` запускается только на dl1.

**Task:**
1. Убедиться, что `_project_root()` возвращает `dell_spec_classifier/` (на основе `__file__`, не CWD). Если нет — исправить.
2. Добавить `test_data/*.xlsx` в `.gitignore`.
3. Расширить `test_regression.py` параметры: `["dl1.xlsx", "dl2.xlsx", "dl3.xlsx", "dl4.xlsx", "dl5.xlsx"]`.
4. Расширить `test_smoke.py` — параметризовать по dl1–dl5.
5. Создать `tests/test_unknown_threshold.py`: для каждого dl запустить pipeline, прочитать `run_summary.json`, assert `unknown_count / item_rows_count <= 0.05`. Пропускать тест (`pytest.skip`) если xlsx не найден.
6. Добавить скрипт или Makefile-команду `generate_golden` которая запускает `python main.py --save-golden --input test_data/dlX.xlsx` для dl1–dl5 последовательно.

**Files to touch:**
- `tests/test_regression.py`
- `tests/test_smoke.py`
- `tests/conftest.py` (или `tests/utils.py` с `_project_root()`)
- `tests/test_unknown_threshold.py` (новый)
- `.gitignore`
- `Makefile` или `scripts/generate_golden.ps1` (новый)

**DoD:**
- `pytest tests/test_rules_unit.py tests/test_state_detector.py tests/test_normalizer.py -v` → 41+ passed без xlsx.
- `pytest tests/test_smoke.py -v` при наличии dl1–dl5.xlsx → 5 passed.
- `pytest tests/test_regression.py -v` параметрически включает dl1–dl5.
- `pytest tests/test_unknown_threshold.py -v` dl2/dl4/dl5 → passed; dl1/dl3 → failing (до Phase 2 правок).

**Commands:**
```powershell
cd dell_spec_classifier
pytest tests/ -v --tb=short 2>&1 | Tee-Object test_output.txt
Select-String "SKIPPED|PASSED|FAILED|ERROR" test_output.txt | Group-Object { $_.Line.Split()[0] }
```

---

## Prompt 2: device_type + Rules for UNKNOWN

**Context:**
Пайплайн: parser → normalizer → state_detector → rules_engine → classifier → outputs. Правила в `dell_rules.yaml` (v1.0.0). Текущие UNKNOWN из прогонов dl1–dl5 (все 27 случаев) задокументированы в vNext plan, раздел Phase 2B MUST-FIX. Нельзя менять архитектуру; device_type — детерминированный first-match, не ML.

**Task:**
1. Добавить в `dell_rules.yaml` секцию `device_type_rules` (first-match, применяется только к HW и LOGISTIC).
2. Добавить 6 новых entity_type правил (LOGISTIC-004-CORD, HW-005-STORAGE-CUS, HW-006-PSU-CUS, HW-007-NIC-CUS, LOGISTIC-005-SFP-CABLE, HW-008-HBA-PERC-CUS, HW-009-CPU-CUS) с паттернами из таблицы vNext plan §Phase 2B.
3. Добавить поле `device_type: Optional[str]` в output dataclass (в `src/core/` или где хранится `ClassifiedRow`).
4. В `classifier.py` — после определения `entity_type` для HW/LOGISTIC строк выполнить матч `device_type_rules` и записать результат.
5. В `outputs.py` / `excel_writer.py` — включить `device_type` в `classification.jsonl` и в `run_summary.json` как `device_type_counts`.
6. Создать `tests/test_device_type.py` с 9+ тест-кейсами (по 1 на каждый SKU из MUST-FIX таблицы + 2 edge case: no match → None, non-HW → None).

**Files to touch:**
- `src/rules/dell_rules.yaml`
- `src/core/classifier.py`
- `src/core/rules_engine.py` (если нужно загружать device_type_rules отдельно)
- `src/outputs/outputs.py` или соответствующий файл (TBD из кода)
- `tests/test_device_type.py` (новый)
- `CHANGELOG.md` (добавить vNext запись)

**DoD:**
- `python main.py --input test_data/dl1.xlsx` → `classification.jsonl` содержит `device_type` для ITEM-строк HW/LOGISTIC с `matched_rule_id != UNKNOWN-000`; строки UNKNOWN-000 и HEADER — `device_type` null/отсутствует.
- `run_summary.json` содержит `device_type_counts`.
- `pytest tests/test_device_type.py -v` → 9+ passed (включая кейс: UNKNOWN строка → device_type is null).
- `pytest tests/test_unknown_threshold.py -v` → все 5 dl passed (UNKNOWN ≤ 5%).
- UNKNOWN dl1 ≤ 2, dl3 ≤ 4.
- Anti-regression: diff `classification.jsonl` до/после затрагивает только строки, где baseline `matched_rule_id = UNKNOWN-000`.

**Commands:**
```powershell
cd dell_spec_classifier
python main.py --input test_data/dl1.xlsx --output-dir output/vnext_v1/dl1
python main.py --input test_data/dl3.xlsx --output-dir output/vnext_v1/dl3
# Проверить UNKNOWN:
Get-Content output/vnext_v1/dl1/*/run_summary.json | ConvertFrom-Json | Select unknown_count, item_rows_count, device_type_counts
Get-Content output/vnext_v1/dl3/*/run_summary.json | ConvertFrom-Json | Select unknown_count, item_rows_count, device_type_counts
pytest tests/test_device_type.py tests/test_unknown_threshold.py -v --tb=short
```

---

## Prompt 3: README / Docs

**Context:**
`README.md` содержит только секцию Regression. Аудит (audit_report.md раздел D) требует добавить: Installation, Quick Start, CLI Reference, артефакты run-папки, entity_type/row_kind/state, Rules Change Process, how-to-run tests, config.yaml reference. `docs/TECHNICAL_OVERVIEW.md` уже существует и подробен — README должен ссылаться на него, а не дублировать.

**Task:**
1. Дописать `README.md` со следующими секциями: Installation, Quick Start, CLI Reference (`--input`, `--config`, `--output-dir`, `--save-golden`, `--update-golden`), Run Artifacts (перечень файлов run-папки), entity_type enum (8 типов), row_kind (ITEM/HEADER), State (PRESENT/ABSENT/DISABLED), Rules Change Process (≥5 шагов), How to Run Tests, Note on test_data (не в git, локальный путь).
2. Добавить в `config.yaml` комментарий об `output_columns` (фиксированы в `excel_writer.py` — параметр не используется).
3. Обновить `CHANGELOG.md`: добавить запись `[1.1.0] - vNext` с описанием device_type и новых правил.

**Files to touch:**
- `README.md`
- `config.yaml`
- `CHANGELOG.md`

**DoD:**
- `Select-String "Rules Change Process|Installation|Quick Start|Artifacts|entity_type|row_kind" README.md` находит все 6 строк.
- `CHANGELOG.md` содержит запись `1.1.0` или `vNext`.
- `config.yaml` содержит комментарий об `output_columns`.

**Commands:**
```powershell
Select-String "Rules Change Process|Installation|Quick Start|Artifacts|entity_type|row_kind" README.md
Select-String "1.1.0|vNext" CHANGELOG.md
Select-String "output_columns" config.yaml
```
