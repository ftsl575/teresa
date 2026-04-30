# CLAUDE.md — Контекст проекта Teresa / spec_classifier
> Этот файл читается автоматически в Cowork и Claude Desktop.
> Цель: не грузить репо в каждом окне. Обновляй после каждого значимого цикла.
> Последнее обновление: 2026-04-30
> Последний коммит: f74a3a9 chore: extend .gitignore for archives and OUTPUT folder
> Последний прогон: 2026-04-30 21:17 (4 vendors, 26 files, 4338 rows; см. OUTPUT/audit_report.json)

---

## ПРОЕКТ

**Teresa** — пайплайн классификации оборудования из Excel BOM (Bill of Materials).
Вендоры: **Dell / Cisco / HPE / Lenovo**.
Каждая строка классифицируется по полям:

| Поле | Значения |
|---|---|
| `entity_type` | BASE / HW / CONFIG / SOFTWARE / SERVICE / LOGISTIC / NOTE / UNKNOWN |
| `hw_type` | server / switch / cpu / memory / gpu / storage_drive / … |
| `device_type` | уточнение: ram, nic, raid_controller, cable, chassis, … |
| `state` | PRESENT / ABSENT / DISABLED (DISABLED — для строк типа "Disabled" в Lenovo/Dell, см. E4) |
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
pytest --collect-only: 420 tests collected (244 def-функций по 31 файлам)
  — 71 batch_audit
  — 43 cluster_audit
  — 51 lenovo (parser + normalizer + rules)
  — 30 hpe_rules_unit
  — остальные: dell/cisco/нормализаторы/writer'ы/regression/smoke/state_detector/...
Все PASS на момент 2026-04-30.
```

### Структура INPUT
```
INPUT/
  dell/    dl1.xlsx … dl5.xlsx
  cisco/   ccw_1.xlsx, ccw_2.xlsx
  hpe/     hp1.xlsx … hp8.xlsx
  lenovo/  L1.xlsx … L11.xlsx
```

### Структура OUTPUT (после полного прогона + аудита)
```
OUTPUT/  (вне репо: C:\Users\G\Desktop\OUTPUT, в .gitignore)
  dell_run/  cisco_run/  hpe_run/  lenovo_run/
    run-YYYY-MM-DD__HH-MM-SS-<stem>/
      classification.jsonl, run_summary.json
      cleaned_spec.xlsx, <stem>_annotated.xlsx
      <stem>_branded.xlsx           ← все вендоры (с f2a2300)
      <stem>_annotated_audited.xlsx ← batch_audit.py пишет внутрь run-папки
      unknown_rows.csv, rows_raw.json, rows_normalized.json
      header_rows.csv, run.log
    run-…-TOTAL/   ← агрегация (содержит копии branded.xlsx всех файлов)
  audit_report.json       ← batch_audit.py (на корне OUTPUT/)
  audit_summary.xlsx      ← batch_audit.py (на корне OUTPUT/)
  cluster_summary.xlsx    ← cluster_audit.py (на корне OUTPUT/)
```

### Ключевые файлы репо
```
spec_classifier/
  batch_audit.py          — аудит E-кодов (E1–E18) + AI mismatch, 1489 LOC
  cluster_audit.py        — кластеризация UNKNOWN/AI_MISMATCH строк, 547 LOC
  scripts/update_golden_from_tests.py  — НЕ СУЩЕСТВУЕТ как отдельный скрипт
                            ↑ функциональность есть в main.py --update-golden
  rules/  dell_rules.yaml (93), cisco_rules.yaml (63), hpe_rules.yaml (143),
          lenovo_rules.yaml (112)   ← счёт по rule_id
  golden/ dl1..dl5, ccw_1..ccw_2, hp1..hp8 _expected.jsonl
          (lenovo golden пока отсутствует — golden ещё не сгенерирован)
  docs/   (нормативные документы; см. CURRENT_STATE.md, CHANGELOG.md)
  src/core/   classifier.py, normalizer.py, parser.py (Dell-specific, см. Tech Debt)
  src/vendors/  dell/, cisco/, hpe/, lenovo/
  src/outputs/  annotated_writer.py, excel_writer.py, branded_spec_writer.py, …
  tests/  test_batch_audit.py (def 31 / collected 71)
          test_cluster_audit.py (def 29 / collected 43)
          test_hpe_rules_unit.py (def 6 / collected 30)
          test_lenovo_rules_unit.py + test_lenovo_normalizer.py
            + test_lenovo_parser.py (def 27 / collected 51)
          плюс test_dec_acceptance, test_device_type, test_state_detector,
          test_normalizer, test_rules_traceability, test_schema_validation,
          regression/unknown_threshold per vendor — итого 31 файл, 420 collected
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
- **power_cord**: `hw_type=None` — намеренно не маппится. Источники истины:
  `rules/dell_rules.yaml:278`, `rules/cisco_rules.yaml:196`, `rules/hpe_rules.yaml:360`
  все содержат комментарий `# hw_type: intentionally unmapped — power_cord has no hw_type`.
  power_cord отсутствует в device_type_map всех 4 YAML.
  В `batch_audit.py:449` исключён из E8: `_E8_NO_HW_TYPE_DEVICES = {"power_cord", "enablement_kit"}`.
  Семантический алиас power_cord ≈ cable существует только в `batch_audit.py:DEVICE_TYPE_ALIASES`
  и применяется исключительно для подавления AI_MISMATCH (когда AI говорит "cable"
  — это не считается несогласием с пайплайном). Это не hw_type-маппинг.
  См. git: `c3c7cb6 fix(taxonomy): restore power_cord hw_type=None`.
- **BASE** без device_type → норма (E15 = инфо, не баг)
- **BASE с device_type** → валидно (BASE-*-DT-* YAML rules), E6/E10 НЕ должны срабатывать
- **blank_filler + state=ABSENT** → заглушка в слоте, не ошибка (E16 = инфо)
- **Dummy PID for Airflow** → HW/accessory, не CONFIG
- **Factory Integrated** строки (is_factory_integrated=True) → CONFIG, AI не проверяет
- **hw_type applies_to** → `[HW]` (не [HW, BASE]) — код победил, таксономия обновлена

### Алиасы device_type (одно и то же, не мисматч)

Источник: `batch_audit.py:DEVICE_TYPE_ALIASES`. Применяются ТОЛЬКО для подавления
AI_MISMATCH (равенство "по смыслу"), а не как hw_type-маппинг.

```
ram              = memory
nic              = network_adapter
raid_controller  = storage_controller
hba              = storage_controller
sfp_cable        = cable
fiber_cable      = cable
power_cord       = cable        ← только AI alias; в YAML power_cord БЕЗ hw_type (см. бизнес-правило выше)
drive_cage       = chassis
bezel            = chassis
storage_nvme     = storage_drive
storage_ssd      = storage_drive
storage_hdd      = storage_drive
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

Полный список E-кодов из `batch_audit.py:421–518`. Таблица отсортирована по номеру.

| Код | Описание | Severity |
|---|---|---|
| E1 | invalid_entity (entity не в VALID_ENTITY_TYPES) | P0 |
| E2 | UNKNOWN_no_rule (нет правила) | BLOCKER |
| E3 | invalid_state (state не в VALID_STATES) | P0 |
| E4 | state mismatch by vendor (data-driven, см. E4_STATE_VALIDATORS) | P1 |
| E5 | hw_type на non-HW (entity ∉ {HW, BASE}) | P0 |
| E6 | device_type на wrong entity (entity ∉ {HW, LOGISTIC, BASE}) | P0 — BASE исключён |
| E7 | hw_type не в HW_TYPE_VOCAB | P1 |
| E8 | HW + PRESENT без hw_type (power_cord, enablement_kit исключены) | P1 |
| E9 | device_type → hw_type mapping mismatch / missing | P1 |
| E10 | hw_type на BASE — сужен: device_type на BASE валиден; срабатывает только если у BASE есть hw_type | P0 |
| E11 | hw_type на CONFIG | P0 |
| E12 | hw_type или device_type на NOTE | P0 |
| E13 | LOGISTIC с физическим device_type (power_cord/cable/sfp_cable/fiber_cable) | P0 |
| E14 | CONFIG похож на blank_filler (Dummy/Blank/Filler в name, нет device_type; SKU NXK-AF-PE исключён) | P1 |
| E15 | BASE без device_type (норма, инфо) | INFO |
| E16 | blank_filler + ABSENT (заглушка в слоте; SKU 412-AASK, 470-BCHP исключены) | INFO |
| E17 | HW без device_type и без hw_type (пайплайн не определил тип) | P1 |
| E18 | LOGISTIC с физическим keyword (cord/cable/rail/bracket/mount/kit/rack/pdu/ups), нет device_type | P0 |

### Теги pipeline_check в *_audited.xlsx
- **AI_MISMATCH** — AI не согласен с пайплайном (голубой)
- **AI_SUGGEST** — пайплайн не определил device_type, AI предлагает (зелёный)
- **MANUAL_CHECK** — AI неуверен (оранжевый)
- **E2** — UNKNOWN (красный, BLOCKER)

---

## ИЗВЕСТНЫЙ TECH DEBT (P2, не в scope текущего плана)

> Зафиксировать как `ARCHITECTURE_RISKS.md` перед добавлением 4-го вендора

1. `batch_audit.py` читает Excel (`pd.read_excel`) вместо `classification.jsonl` — Excel leakage сохраняется
2. Alias sprawl в `batch_audit.py` (`DEVICE_TYPE_ALIASES`, `_ALIASES`, `HW_TYPE_TRUST`,
   `DEVICE_TYPE_TRUST`, `ENTITY_TRUST_PIPELINE`) — решается одной canonical schema
3. `batch_audit.py` = 1489 LOC (вырос с 1280), потенциальный god-object
4. TOTAL folders создают confusion при прогонах (удвоение branded/audited файлов)
5. ✅ DONE (audit_1E Step 2, 6147b3a): DEVICE_TYPE_MAP грузится из YAML;
   `detect_vendor_from_path()` принимает known_vendors; `--vendor` choices динамические;
   E4 data-driven через `E4_STATE_VALIDATORS` + `_check_e4()`. См. CURRENT_STATE.md § audit_1E
6. ✅ DONE (audit_1E Step 1, a5e15d3): `VENDOR_EXTRA_COLS` удалён;
   заменён на `VendorAdapter.get_extra_cols()` (default []), переопределён
   в `HPEAdapter` (5 cols) и `CiscoAdapter` (2 cols); `annotated_writer` принимает `extra_cols` параметром
7. `core/parser.py` фактически dell-specific (sentinel "Module Name", см. docstring),
   но живёт в core/ — Cisco/HPE/Lenovo используют свои `parser.py` в `src/vendors/<vendor>/`
8. `lenovo_rules.yaml` пока без полного golden покрытия — `golden/` содержит только dl/ccw/hp;
   `tests/test_lenovo_*.py` опираются на rules-unit + parser/normalizer тесты
9. `run_audit.ps1` запускает только Dell + HPE + Cisco (lenovo не прописан); прогон
   за 2026-04-30 21:17 (см. OUTPUT/audit_report.json) делал lenovo руками или через `main.py --batch-dir`

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
