# CLAUDE.md — Контекст проекта Teresa / spec_classifier
> Этот файл читается автоматически в Cowork и Claude Desktop.
> Цель: не грузить репо в каждом окне. Обновляй после каждого значимого цикла.
> Последнее обновление: 2026-03-11
> Последний коммит: 65745e5 fix: update golden + recovery

---

## ПРОЕКТ

**Teresa** — пайплайн классификации оборудования из Excel BOM (Bill of Materials).
Вендоры: **Dell / Cisco / HPE**.
Каждая строка классифицируется по полям:

| Поле | Значения |
|---|---|
| `entity_type` | BASE / HW / CONFIG / SOFTWARE / SERVICE / LOGISTIC / NOTE / UNKNOWN |
| `hw_type` | server / switch / cpu / memory / gpu / storage_drive / … |
| `device_type` | уточнение: ram, nic, raid_controller, cable, chassis, … |
| `state` | PRESENT / ABSENT |
| `row_kind` | HEADER / ITEM ← добавлено в annotated_writer в последнем цикле |

---

## ПУТИ (Windows)

```
Репо:    C:\Users\G\Desktop\teresa\spec_classifier
Input:   C:\Users\G\Desktop\INPUT  (dell/, hpe/, cisco/)
Output:  C:\Users\G\Desktop\OUTPUT
Temp:    C:\Users\G\Desktop\temporary
```

---

## ТЕКУЩЕЕ СОСТОЯНИЕ (v1.3.x, после audit_1G → PASS)

### Тесты
```
181+ (base) + 45 (batch_audit) + 10+ (cluster_audit) = 236+ total — все PASS
```

### Структура INPUT
```
INPUT/
  dell/    dl1.xlsx … dl5.xlsx
  cisco/   ccw_1.xlsx, ccw_2.xlsx
  hpe/     hp1.xlsx … hp8.xlsx
```

### Структура OUTPUT (после полного прогона + аудита)
```
OUTPUT/
  dell_run/  cisco_run/  hpe_run/
    run-YYYY-MM-DD__HH-MM-SS-<stem>/
      classification.jsonl, run_summary.json
      cleaned_spec.xlsx, <stem>_annotated.xlsx
      <stem>_branded.xlsx (Dell only)
      unknown_rows.csv, rows_raw.json, rows_normalized.json
      header_rows.csv, run.log
    run-…-TOTAL/   ← агрегация
  <stem>_audited.xlsx     ← batch_audit.py
  audit_report.json       ← batch_audit.py
  audit_summary.xlsx      ← batch_audit.py
  cluster_summary.xlsx    ← cluster_audit.py
```

### Ключевые файлы репо
```
spec_classifier/
  batch_audit.py          — аудит E-кодов + AI сравнение (E1–E18), 1280 LOC
  cluster_audit.py        — кластеризация UNKNOWN/AI_MISMATCH строк, 492 LOC
  scripts/update_golden_from_tests.py  — НЕ СУЩЕСТВУЕТ как отдельный скрипт
                            ↑ функциональность есть в main.py --update-golden
  rules/  hpe_rules.yaml, dell_rules.yaml, cisco_rules.yaml
  golden/ dl1..dl5, ccw_1..ccw_2, hp1..hp8 _expected.jsonl
  docs/   (нормативные документы)
  src/core/   classifier.py, normalizer.py, parser.py
  src/vendors/  dell/, cisco/, hpe/
  src/outputs/  annotated_writer.py, excel_writer.py, …
  tests/  test_batch_audit.py (45), test_cluster_audit.py (10+), test_hpe_rules_unit.py (25+)
```

---

## CLI КОМАНДЫ

```powershell
# Прогон пайплайна
python main.py --batch-dir <INPUT/vendor> --vendor <vendor>

# Аудит без AI (быстро)
python batch_audit.py --output-dir C:\Users\G\Desktop\OUTPUT --no-ai

# Аудит конкретного вендора с AI
python batch_audit.py --output-dir C:\Users\G\Desktop\OUTPUT --vendor hpe

# Кластеризация
python cluster_audit.py --output-dir C:\Users\G\Desktop\OUTPUT

# Тесты
pytest tests/ -v --tb=short

# Обновление golden
python main.py --update-golden
```

---

## БИЗНЕС-ПРАВИЛА (не нарушать при правках)

- **LOGISTIC** = только упаковка, документы, доставка, freight
- **Power cord, stacking cable, rail, bracket** → HW, не LOGISTIC
- **power_cord**: `hw_type=None` ← таксономия победила (изменено в последнем цикле)
- **BASE** без device_type → норма (E15 = инфо, не баг)
- **BASE с device_type** → валидно (BASE-*-DT-* YAML rules), E6/E10 НЕ должны срабатывать
- **blank_filler + state=ABSENT** → заглушка в слоте, не ошибка (E16 = инфо)
- **Dummy PID for Airflow** → HW/accessory, не CONFIG
- **Factory Integrated** строки (is_factory_integrated=True) → CONFIG, AI не проверяет
- **hw_type applies_to** → `[HW]` (не [HW, BASE]) — код победил, таксономия обновлена

### Алиасы device_type (одно и то же, не мисматч)
```
ram = memory
nic = network_adapter
raid_controller = storage_controller
sfp_cable / fiber_cable = cable
drive_cage / bezel = chassis
storage_nvme / storage_ssd / storage_hdd = storage_drive
```

### Canonical Field Names (batch_audit _ALIASES)
```
config_name       → module_name   (HPE extension!)
description       → option_name
product_description → option_name
part_number       → skus
product_#         → skus          (HPE extension!)
```

---

## E-КОДЫ batch_audit.py

| Код | Описание | Severity |
|---|---|---|
| E2 | UNKNOWN (нет правила) | BLOCKER |
| E6 | entity не в (HW, LOGISTIC, BASE) + device_type | P0 — BASE теперь исключён |
| E10 | BASE + device_type — УБРАН (device_type на BASE валиден) | FIXED |
| E13 | LOGISTIC с физическим кабелем/шнуром питания | P0 |
| E14 | CONFIG похож на blank_filler | P1 |
| E15 | BASE без device_type (норма, инфо) | INFO |
| E16 | blank_filler + ABSENT (заглушка, норма) | INFO |
| E17 | HW без определённого типа | P1 |
| E18 | LOGISTIC с физическим keyword (cord/cable/rail/bracket) | P0 |

### Теги pipeline_check в *_audited.xlsx
- **AI_MISMATCH** — AI не согласен с пайплайном (голубой)
- **AI_SUGGEST** — пайплайн не определил device_type, AI предлагает (зелёный)
- **MANUAL_CHECK** — AI неуверен (оранжевый)
- **E2** — UNKNOWN (красный, BLOCKER)

---

## ИЗВЕСТНЫЙ TECH DEBT (P2, не в scope текущего плана)

> Зафиксировать как `ARCHITECTURE_RISKS.md` перед добавлением 4-го вендора

1. `batch_audit.py` читает Excel вместо `classification.jsonl` — Excel leakage
2. Alias sprawl в `batch_audit.py` — решается одной canonical schema
3. `batch_audit.py` = 1280 LOC, потенциальный god-object
4. TOTAL folders создают confusion при прогонах (удвоение файлов)
5. Vendor-specific hardcodes в `batch_audit.py` (DEVICE_TYPE_MAP, E4, detect_vendor)
6. `VENDOR_EXTRA_COLS` hardcoded в `annotated_writer.py` — требует правки core при новом вендоре
7. `core/parser.py` фактически dell-specific, но живёт в core/

---

## РОЛИ ИНСТРУМЕНТОВ

| Инструмент | Роль |
|---|---|
| **Cursor** (Pro) | пишет/меняет код и документы — исполнитель |
| **Claude** (Pro) | архитектурные выводы, аудит, проектирование изменений |
| **ChatGPT** (Plus) | управляет шагами, PowerShell-команды, итоговый вердикт |
| **Gemini** | опционально — "второе мнение" по финальному отчёту |

---

## ЦИКЛ РАЗРАБОТКИ

```
PRE-CHECK → PLAN (Master Plan) → CURSOR IMPLEMENT → POST-CHECK → AUDIT (1A–1G) → DOC UPDATE
```

| Сценарий | Шаги |
|---|---|
| Маленькая правка YAML | PRE → BATCH AUDIT MASTER PLAN → Cursor → POST |
| Новая фича / рефакторинг | PRE → MASTER PLAN A → Cursor → POST → 1A–1G |
| После FAIL аудита | MASTER PLAN B (fix) → Cursor → POST → 1G |
| Обновление документации | 1A–1G → DOC UPDATE MASTER PLAN → Cursor |

---

## ЖЁСТКИЕ ПРАВИЛА ДЛЯ CLAUDE-ОКОН

- **R1.** Каждый шаг = отдельное новое окно Claude
- **R2.** В каждом окне читать ТОЛЬКО перечисленные файлы
- **R3.** Каждый ответ заканчивается блоком SUMMARY:
  ```
  CLAIMS: …
  EVIDENCE: claim_id → file + место + цитата ≤2 строки
  SEVERITY: P0/P1/P2 на каждый claim
  ACTION: что делать
  ```
- **R4.** Утверждение "tracked в git" требует доказательства, иначе — НЕПОДТВЕРЖДЕНО
- **R5.** В финальное окно (1G) идут ТОЛЬКО SUMMARY-блоки, не весь текст

### Уровни серьёзности
- **P0** — BLOCKER: нельзя продолжать (сломаны тесты, вырос UNKNOWN, нарушен контракт)
- **P1** — IMPORTANT: исправить в ближайшем цикле (отстаёт документация, слепые зоны)
- **P2** — NICE: улучшения качества (рефакторинг, косметика)

---

## РЕКОМЕНДУЕМЫЕ МОДЕЛИ ПО ШАГАМ

| Шаг | Модель | Extended |
|---|---|---|
| PRE-CHECK, POST-CHECK, чеклист (1A, 1C, 1G) | Sonnet 4.6 | OFF |
| Архитектура, стыки, документация, тесты (1B, 1D, 1E, 1F) | Opus 4.6 | ON |
| Master Plan генерация | Opus 4.6 | ON |
| Batch Audit анализ | Opus 4.6 | ON |

---

## ПРОМПТЫ — где лежат

Файл с готовыми промптами для всех шагов:
**`prompts/`** (папка с отдельными .md файлами для каждого шага)
См. `prompts/README.md` для навигации.
