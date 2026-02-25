# hw_type System v4 — Full Implementation Plan

**Project:** teresa / dell_spec_classifier  
**Date:** 2026-02-24  
**Baseline:** v1.1.2 (Phase B Step 2)  
**Approach:** Option B — полное обновление enum + тесты + golden + docs  
**Changes from v3:** Pack 5/7 test consistency fix, OCP regex narrowed, no predicted counts, Group Manager → CONFIG-004, Fan risk noted

---

## Status

**Status:** Completed / reference-only (plan executed).  
**Last updated:** 2026-02-26  

## Execution log (what was actually merged)

- DEC-007: optics rule narrowing + tests (prompt_p7a_optics_rule_narrow_and_tests_dec007.txt).
- DEC-005: device_type coverage for PERC controller rows (PROMPT_8_PERC_device_type_DEC-005.txt).
- Golden + CHANGELOG + release tag alignment for v1.1.0 (PROMPT_9_Golden_Tests_Changelog_Version_1.1.0.txt; baseline text reference PROMPT_9_ORIGINAL_1to1.txt).
- Rules/fixes for SFP Modules + DAC cables, plus storage hw_type fixes (PROMPT_10_SFP_Modules_and_Storage_hw_type_fix.txt).
- Tests-only: robust header-row detection for annotated.xlsx exports with a preamble (CURSOR_PROMPT_fix_annotated_header_row.txt).

### Git anchors

- Release tag **v1.1.0** points to commit **5af576d**.
- Annotated.xlsx header detection fix was merged via PR #2 and is on **main** at merge commit **a0499e8** (post-tag).

---

## Table of Contents

1. [UNDERSTANDING](#1-understanding)
2. [ASSUMPTIONS](#2-assumptions)
3. [TAXONOMY v4 (финальная)](#3-taxonomy-v4)
4. [ENTITY_TYPE BUGFIXES (Pack 4.5)](#4-entity-type-bugfixes)
5. [ANNOTATED SOURCE CHANGES](#5-annotated-source-changes)
6. [MASTER PLAN (Packs 4.5–10)](#6-master-plan)
7. [VALIDATION](#7-validation)
8. [PROMPT PACK FOR CURSOR](#8-prompt-pack-for-cursor)

---

## 1. UNDERSTANDING

**Задача:** Реализовать детерминистическое вычисление `hw_type` для HW-строк + исправить entity_type баги + обновить annotated_source.xlsx.

**Три потока работ:**
1. **Entity-type bugfixes** — Performance Profile → CONFIG, Password → CONFIG, Group Manager → CONFIG, iDRAC License → SOFTWARE.
2. **hw_type taxonomy v4** — 20 значений snake_case, трёхслойная резолюция.
3. **Annotated source** — колонка hw_type + переименование по источнику.

---

## 2. ASSUMPTIONS

**CLI note:** `main.py` requires `--input`. All run/validation commands must call:
`python .\main.py --input <file.xlsx> [--config config.yaml] [--output-dir output]`


1. **Option B:** enum меняется сразу, тесты и golden обновляются в том же цикле.
2. hw_type назначается ТОЛЬКО строкам с `entity_type=HW`. Для остальных — `null`.
3. Единый файл правил `dell_rules.yaml` (без второго файла).
4. Для ABSENT/DISABLED HW-строк hw_type вычисляется (тип железа не зависит от состояния).
5. annotated_source.xlsx — существующий output; добавляем колонку и меняем naming.
6. Фиксы entity_type (Pack 4.5) делаются ДО hw_type.
7. **Строки с module_name "Thermal Configuration" без явного Heatsink/Fan в option_name — получают `null` + warning.**
8. **Строки с module_name "Hard Drives" без явного SSD/HDD/NVMe в option_name — получают `null` + warning.**
9. **hw_type_counts НЕ предсказываются заранее.** Точные значения фиксируются ТОЛЬКО после реального прогона в Pack 9.
10. **Между Pack 5 и Pack 9 тест проверяет `isinstance(hw_type_counts, dict)`, а НЕ конкретные значения.** Конкретные counts — только в Pack 9.

---

## 3. TAXONOMY v4 (финальная)

### 3.1 hw_type enum — 20 значений, ALL snake_case

| hw_type | Описание | Примеры |
|---------|----------|---------|
| `cpu` | Процессоры | Processor, Additional Processor, Xeon CK |
| `ram` | Модули памяти | Memory Capacity, RDIMM, LRDIMM |
| `ssd` | SATA/SAS SSD | "480GB SSD SATA Read Intensive…" |
| `hdd` | Жёсткие диски | "1TB 7.2K RPM SATA…" |
| `nvme` | NVMe накопители | "800G Data Center NVMe…" |
| `storage_controller` | RAID/HBA + BBU | PERC, HBA, RAID Controller, RAID Battery |
| `psu` | Блоки питания | Power Supply, PSU Customer Kit |
| `fan` | Вентиляторы | "High Performance Gold Fan" |
| `cpu_heatsink` | Радиаторы CPU | "Heatsink for 2 CPU…" |
| `network_adapter` | Сетевые адаптеры | OCP 3.0 Network Adapters, NIC CK |
| `riser` | PCIe райзеры | PCIe Riser, "Riser Config…" |
| `gpu` | GPU / FPGA / акселераторы | GPU, FPGA (без "Cables") |
| `tpm` | Модули безопасности | TPM, Trusted Platform Module |
| `chassis` | Шасси, безели | Chassis Configuration, Bezel |
| `cable` | Кабели, "No cable" строки | Cables, "No Cable Required" |
| `management` | KVM, BMC, Quick Sync | KVM, BMC |
| `motherboard` | Материнская плата | Motherboard |
| `mounting_kit` | Рейки, CMA, крепёж | Rack Rails, ReadyRails, CMA |
| `backplane` | Бэкплейны / drive cage | "Rear Backplane…", "NVMe Backplane Assembly" |
| `blank` | Заглушки / филлеры | Drive Blanks, DIMM Filler |

**Стиль:** lowercase snake_case, без исключений.

### 3.2 Layer 1: device_type → hw_type

```yaml
device_type_map:
  cpu: cpu
  psu: psu
  nic: network_adapter
  storage_nvme: nvme
  storage_ssd: ssd
  raid_controller: storage_controller
  hba: storage_controller
```

### 3.3 Layer 2: rule_id → hw_type

```yaml
rule_id_map:
  HW-001: chassis
  HW-004: nvme
  HW-005-STORAGE-CUS: nvme
  HW-006-PSU-CUS: psu
  HW-007-NIC-CUS: network_adapter
  HW-008-HBA-PERC-CUS: storage_controller
  HW-009-CPU-CUS: cpu
```

### 3.4 Layer 3: regex rules — порядок КРИТИЧЕН

**Принципы:**
- «Перехватчики» первыми: blank → backplane → cable → mounting_kit.
- Специфичные option_name (NVMe, SSD, HDD, Heatsink, Fan) до generic module_name.
- **НЕТ generic storage fallback.** Hard Drives без сигнала → null + warning.
- **НЕТ Thermal → heatsink.** Только явный Heatsink/Fan в option_name.
- **OCP сужен:** `OCP\s+3\.0\s+Network` вместо голого `OCP` — не перехватывает Accessories.

```
Порядок regex rules (first match wins):
 1. blank       (module/option: Blank|Filler|Dummy)
 2. backplane   (module/option: Backplane|Drive Cage|Bay Assembly)
 3. cable       (module: Cables; option: No Cable/No Cables Required/No DPU)
 4. mounting_kit (module: Rack Rails|Cable Management; option: ReadyRails|CMA)
 5. cpu         (module: Processor|Additional Processor)
 6. ram         (module: Memory Capacity)
 7. nvme        (option: NVMe; module: Boot Optimized|BOSS)
 8. ssd         (option: SSD|SATA, negative lookahead NVMe)
 9. hdd         (option: HDD|RPM patterns)
10. storage_controller (module: RAID|Storage Controller; option: PERC|HBA|BBU)
11. psu         (module: Power Supply)
12. cpu_heatsink (option: Heatsink — ONLY explicit)
13. fan         (option: Fan; module: Fans — RISK: verify on dl2 no false positives)
14. network_adapter (module: Network Adapter|OCP 3.0 Network|NIC|Multi Selection Network)
15. gpu         (module: ^GPU|^FPGA, без Cables)
16. riser       (module: PCIe|Riser)
17. chassis     (module: Chassis|Bezel|Server Accessories)
18. management  (module: KVM|BMC|Quick Sync)
19. tpm         (module: TPM|Trusted Platform)
20. motherboard (module: Motherboard)
```

**Осознанные null + warning:**
- `module_name: "Thermal Configuration"` без Heatsink/Fan в option → null.
- `module_name: "Hard Drives"` без SSD/HDD/NVMe в option → null.
- Новые module_name из dl2–dl5 → null → Pack 10.

**Известный риск (Fan):**
- `module_name: "Fans"` и `option_name: "Fan"` — проверить на dl2 что нет false positives в non-cooling контекстах.

---

## 4. ENTITY_TYPE BUGFIXES (Pack 4.5)

### Bug 1: Performance/Thermal/Power Profile → CONFIG

**Фикс:** Добавить в `config_rules`:
```yaml
- field: module_name
  pattern: '(?i)\b(Performance|Thermal|Power)\s+Profile\b'
  entity_type: CONFIG
  rule_id: CONFIG-002
```

### Bug 2: Password → CONFIG

**Фикс (2 шага):**
1. Добавить в `config_rules`:
```yaml
- field: module_name
  pattern: '(?i)^Password$'
  entity_type: CONFIG
  rule_id: CONFIG-003
```
2. Убрать `Password` из HW-003 pattern:
```
было:  \b(BOSS|TPM|Trusted\s+Platform|GPU|FPGA|Acceleration|Quick\s+Sync|Password|BMC|KVM|Rack\s+Rails|Server\s+Accessories)\b
стало: \b(BOSS|TPM|Trusted\s+Platform|GPU|FPGA|Acceleration|Quick\s+Sync|BMC|KVM|Rack\s+Rails|Server\s+Accessories)\b
```

### Bug 3: Group Manager → CONFIG

**Проблема:** module_name "Group Manager" с option "iDRAC Group Manager, Disabled" — конфигурация iDRAC, не железо.

**Фикс:** Добавить в `config_rules`:
```yaml
- field: module_name
  pattern: '(?i)^Group\s+Manager$'
  entity_type: CONFIG
  rule_id: CONFIG-004
```

### Bug 4: iDRAC License → SOFTWARE (узкое правило)

**Фикс:**
```yaml
- field: option_name
  pattern: '(?i)\b(iDRAC|OpenManage|BMC)\b.*\bLicense\b'
  entity_type: SOFTWARE
  rule_id: SOFTWARE-005
```

### Обязательная проверка Pack 4.5

Прогнать **dl1–dl5**, сравнить entity_type_counts diff. Допустимые изменения:
- Profile строки: HW→CONFIG.
- Password строки: HW→CONFIG.
- Group Manager строки: может быть из UNKNOWN или HW → CONFIG.
- iDRAC License строки: HW→SOFTWARE.
- Всё остальное — без изменений.

---

## 5. ANNOTATED SOURCE CHANGES

### 5.1 Колонка hw_type

Добавить `hw_type` после `device_type` в annotated_source.xlsx. Значение из `ClassificationResult.hw_type`. Для non-HW — пустая ячейка.

### 5.2 Переименование

`{source_basename}_annotated.xlsx`: dl1.xlsx → dl1_annotated.xlsx.

---

## 6. MASTER PLAN (Packs 4.5–10)

### Pack 4.5 — Entity-type bugfixes

| | |
|---|---|
| **Цель** | Исправить 4 бага entity_type до hw_type |
| **Задачи** | CONFIG-002 (Profile), CONFIG-003 (Password), CONFIG-004 (Group Manager), SOFTWARE-005 (iDRAC License), HW-003 pattern fix |
| **Проверка** | dl1–dl5 прогон, entity_type_counts diff |
| **Acceptance** | pytest green, все 4 бага исправлены |
| **Effort** | S |
| **Priority** | P0 |

### Pack 5 — hw_type enum + contract

| | |
|---|---|
| **Цель** | Зафиксировать 20 snake_case значений, добавить поле в dataclass |
| **Задачи** | HW_TYPE_VOCAB frozenset (20), hw_type field в ClassificationResult, тест vocabulary |
| **Тест** | `assert isinstance(hw_type_counts, dict)` — НЕ проверяет содержимое. Точные counts → Pack 9 |
| **Acceptance** | pytest green, hw_type=null везде, len(HW_TYPE_VOCAB)==20 |
| **Effort** | S |
| **Priority** | P0 |

### Pack 6 — hw_type_rules config + RuleSet

| | |
|---|---|
| **Цель** | Секция hw_type_rules в YAML + загрузка в RuleSet |
| **Задачи** | YAML секция (device_type_map, rule_id_map, rules), RuleSet attrs |
| **Acceptance** | YAML парсится, attrs доступны, len(rules)>=28 |
| **Effort** | S |
| **Priority** | P0 |

### Pack 7 — _apply_hw_type() activation

| | |
|---|---|
| **Цель** | Третий pass, активация логики |
| **Задачи** | match_hw_type_rule(), _apply_hw_type(), подключение в classify_row() |
| **Acceptance** | hw_type_counts не пустой, non-HW=null, pytest GREEN (тест проверяет только isinstance) |
| **Effort** | M |
| **Priority** | P0 |

### Pack 8 — Annotated source

| | |
|---|---|
| **Цель** | hw_type колонка + {source}_annotated.xlsx naming |
| **Задачи** | excel_writer update, main.py filename propagation |
| **Acceptance** | dl1_annotated.xlsx с hw_type колонкой |
| **Effort** | S |
| **Priority** | P0 |

### Pack 9 — Golden + regression lock

| | |
|---|---|
| **Цель** | Обновить golden, зафиксировать ТОЧНЫЕ hw_type_counts в тестах |
| **Задачи** | Перегенерация golden, обновление тестов: `isinstance(…, dict)` → конкретные expected counts |
| **Acceptance** | pytest green, golden содержит hw_type |
| **Effort** | S |
| **Priority** | P0 |

### Pack 10 — dl2–dl5 expansion + monitoring

| | |
|---|---|
| **Цель** | Покрытие новых module_name, warning + hw_type_null_count |
| **Задачи** | Warning "hw_type unresolved", hw_type_null_count в stats, новые regex, Fan verification на dl2 |
| **Acceptance** | hw_type_null_count минимален для dl1–dl5, pytest green |
| **Effort** | M–L |
| **Priority** | P1 |

---

## 7. VALIDATION

### Test Cases

| # | Input | Expected | Layer |
|---|-------|----------|-------|
| 1 | device_type=cpu | cpu | L1 |
| 2 | device_type=psu | psu | L1 |
| 3 | device_type=nic | network_adapter | L1 |
| 4 | device_type=storage_nvme | nvme | L1 |
| 5 | device_type=hba | storage_controller | L1 |
| 6 | rule_id=HW-001 | chassis | L2 |
| 7 | rule_id=HW-004 | nvme | L2 |
| 8 | HW-002, module="Processor" | cpu | L3 |
| 9 | HW-002, module="Memory Capacity" | ram | L3 |
| 10 | HW-002, module="Fans", opt="…Fan" | fan | L3 |
| 11 | HW-002, module="Thermal Config", opt="Heatsink…" | cpu_heatsink | L3 |
| 12 | HW-003, module="KVM" | management | L3 |
| 13 | HW-003, module="Rack Rails" | mounting_kit | L3 |
| 14 | HW-002, module="Acceleration Cards Cables" | cable | L3 |
| 15 | HW-002, module="Hard Drives", opt="No Hard Drive" | null | — |
| 16 | HW-002, module="Hard Drives", opt="480GB SSD SATA…" | ssd | L3 |
| 17 | HW-002, module="Hard Drives (PCIe…)", opt="800G NVMe…" | nvme | L3 |

### Edge Cases

| # | Scenario | Expected |
|---|----------|----------|
| E1 | entity_type=LOGISTIC, device_type=power_cord | null (не HW) |
| E2 | entity_type=HW, state=ABSENT, opt="No Hard Drive" | null (нет типа) |
| E3 | entity_type=HW, rule_id=UNKNOWN-000 | null |
| E4 | module="GPU/FPGA/Acceleration Cables" | cable (не gpu) |
| E5 | module="Drive Blanks" | blank |
| E6 | option="Rear Backplane with 2x2.5in SAS/SATA" | backplane |
| E7 | module="Performance Profile" (после fix) | entity_type=CONFIG → null |
| E8 | option="iDRAC9 Enterprise License" (после fix) | entity_type=SOFTWARE → null |
| E9 | device_type=cpu + module="Fans" (conflict) | cpu (L1 > L3) |
| E10 | module="Thermal Configuration", opt="Thermal Blanking Cover" | blank (Blank в option) |
| E11 | module="OCP 3.0 Accessories", opt="2 OCP - No Cable" | cable (cable rule перехватывает до network) |
| E12 | module="Hard Drives", opt="1TB 7.2K RPM SATA 6Gbps…" | hdd |
| E13 | module="Group Manager" (после fix) | entity_type=CONFIG → null |
| E14 | module="OCP 3.0 Network Adapters", opt="Broadcom…" | network_adapter |

### Manual QA Checklist

**IMPORTANT (output paths):** pipeline writes artifacts into `output/run_YYYYMMDD_HHMMSS[_N]/`.  
For any validation commands below that read `run_summary.json` / `classification.jsonl`, always use the *latest* run folder:

```powershell
$run = Get-ChildItem .\output -Directory -Filter "run_*" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$run
```

Then read artifacts from:
- `$run\run_summary.json`
- `$run\classification.jsonl`
- `$run\rows_normalized.json` (if produced)


- [ ] `python main.py test_data/dl1.xlsx` — без ошибок.
- [ ] Output: `dl1_annotated.xlsx` (не `annotated_source.xlsx`).
- [ ] `dl1_annotated.xlsx` содержит колонку `hw_type` после `device_type`.
- [ ] Non-HW строки: hw_type пусто.
- [ ] `run_summary.json` → `hw_type_counts` не пустой.
- [ ] `pytest tests/ -v` — 0 failures.
- [ ] rules_file_hash обновился.
- [ ] dl2: проверить что "Fan"/"Fans" не перехватывает non-cooling строки.

---

## 8. PROMPT PACK FOR CURSOR

---

### Prompt 1 — Pack 4.5: Entity-type bugfixes

```
ПРОЕКТ: teresa / dell_spec_classifier
ФАЙЛ: rules/dell_rules.yaml
BASELINE: v1.1.2

КОНТЕКСТ:
4 бага entity_type классификации:
1. "Performance Profile"/"Thermal Profile"/"Power Profile" → пробивается в HW (должно быть CONFIG).
2. "Password" как module_name → HW-003 (должно быть CONFIG: "iDRAC,Legacy Password").
3. "Group Manager" как module_name → может пробиться в HW/UNKNOWN (должно быть CONFIG: "iDRAC Group Manager, Disabled").
4. "iDRAC9 Enterprise License" → может пробиться в HW (должно быть SOFTWARE).

ЗАДАЧА (5 изменений в dell_rules.yaml):

A) В секцию config_rules (ПОСЛЕ CONFIG-001) добавить 3 правила:

  - field: module_name
    pattern: '(?i)\b(Performance|Thermal|Power)\s+Profile\b'
    entity_type: CONFIG
    rule_id: CONFIG-002

  - field: module_name
    pattern: '(?i)^Password$'
    entity_type: CONFIG
    rule_id: CONFIG-003

  - field: module_name
    pattern: '(?i)^Group\s+Manager$'
    entity_type: CONFIG
    rule_id: CONFIG-004

B) В секцию software_rules (В КОНЕЦ) добавить:

  - field: option_name
    pattern: '(?i)\b(iDRAC|OpenManage|BMC)\b.*\bLicense\b'
    entity_type: SOFTWARE
    rule_id: SOFTWARE-005

   ВАЖНО: правило УЗКОЕ — ловит License ТОЛЬКО в контексте iDRAC/OpenManage/BMC.
   НЕ используй generic "\bLicense\b".

C) В hw_rules, правило HW-003 — УБРАТЬ "Password|" из pattern:

   Было:
   pattern: '\b(BOSS|TPM|Trusted\s+Platform|GPU|FPGA|Acceleration|Quick\s+Sync|Password|BMC|KVM|Rack\s+Rails|Server\s+Accessories)\b'

   Стало:
   pattern: '\b(BOSS|TPM|Trusted\s+Platform|GPU|FPGA|Acceleration|Quick\s+Sync|BMC|KVM|Rack\s+Rails|Server\s+Accessories)\b'

ОГРАНИЧЕНИЯ:
- НЕ менять существующие правила кроме HW-003 pattern.
- НЕ менять порядок секций.
- НЕ добавлять hw_type_rules (следующий Pack).
- YAML валидный.

ACCEPTANCE:
- python -c "import yaml; yaml.safe_load(open('rules/dell_rules.yaml'))" — OK.
- config_rules содержит CONFIG-001, CONFIG-002, CONFIG-003, CONFIG-004.
- software_rules содержит SOFTWARE-005.
- HW-003 pattern НЕ содержит "Password".

ПРОВЕРКА:
  python -c "
import yaml
d = yaml.safe_load(open('rules/dell_rules.yaml'))
cr = [r['rule_id'] for r in d['config_rules']]
sr = [r['rule_id'] for r in d['software_rules']]
hw3 = [r for r in d['hw_rules'] if r['rule_id']=='HW-003'][0]['pattern']
print('config:', cr)
print('software:', sr)
print('HW-003 has Password:', 'Password' in hw3)
"
  # Ожидается:
  # config: ['CONFIG-001', 'CONFIG-002', 'CONFIG-003', 'CONFIG-004']
  # software: [..., 'SOFTWARE-005']
  # HW-003 has Password: False

  # ОБЯЗАТЕЛЬНО: прогнать dl1-dl5 и проверить entity_type_counts diff
  for f in test_data/dl*.xlsx; do
  # PowerShell alternative (Windows):
  Get-ChildItem .\test_data -Filter "dl*.xlsx" | ForEach-Object {
    Write-Host "=== $($_.FullName) ==="
    python .\main.py --input $_.FullName --config .\config.yaml --output-dir .\output
    $run = Get-ChildItem .\output -Directory -Filter "run_*" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    python -c "import json; from pathlib import Path; p=Path(r'$($run.FullName)')/'run_summary.json'; print(json.dumps(json.load(open(p, encoding='utf-8'))['entity_type_counts'], indent=2))"
  }

    echo "=== $f ==="
    python main.py "$f"
    python -c "from pathlib import Path\
out = Path('output')\
_latest_run = max(out.glob('run_*'), key=lambda p: p.stat().st_mtime)\
import json; print(json.dumps(json.load(open(_latest_run/'run_summary.json', encoding='utf-8'))['entity_type_counts'], indent=2))"
  done
  # Допустимые изменения: Profile/Password/GroupManager → +CONFIG, -HW/UNKNOWN.
  # iDRAC License → +SOFTWARE, -HW.
  # Всё остальное без изменений.

  pytest tests/ -v
```

---

### Prompt 2 — Pack 5: hw_type enum + ClassificationResult field

```
ПРОЕКТ: teresa / dell_spec_classifier
ФАЙЛЫ: src/core/classifier.py, tests/test_stats_hw_type.py

КОНТЕКСТ:
hw_type сейчас читается через getattr(r, "hw_type", None), но поле
НЕ объявлено в dataclass. Нужно формализовать: поле + vocab (20 snake_case значений).

ЗАДАЧА:

A) В src/core/classifier.py:

   1. Добавить константу ПЕРЕД ClassificationResult:

      HW_TYPE_VOCAB = frozenset({
          "cpu", "ram", "ssd", "hdd", "nvme",
          "storage_controller", "psu", "fan", "cpu_heatsink",
          "network_adapter", "riser", "gpu",
          "tpm", "chassis", "cable", "management",
          "motherboard", "mounting_kit", "backplane", "blank",
      })

   2. Добавить поле в ClassificationResult dataclass:
      hw_type: Optional[str] = None
      Позиция: ПОСЛЕ device_type, ПЕРЕД warnings.

B) В tests/test_stats_hw_type.py:

   1. Добавить тест vocab:
      - from src.core.classifier import HW_TYPE_VOCAB
      - assert len(HW_TYPE_VOCAB) == 20
      - assert all(isinstance(v, str) and v for v in HW_TYPE_VOCAB)
      - assert all(v == v.lower() for v in HW_TYPE_VOCAB)  # all snake_case

   2. ИЗМЕНИТЬ существующий тест hw_type_counts:
      Вместо assert hw_type_counts == {}
      Сделать:
        assert isinstance(hw_type_counts, dict)
        # Точные значения будут зафиксированы в Pack 9 после реального прогона.

      ЭТО КРИТИЧНО: между Pack 5 и Pack 9 тест НЕ проверяет содержимое counts,
      только тип. Это позволяет Pack 7 (активация hw_type) не ломать тесты.

ОГРАНИЧЕНИЯ:
- ВСЕ значения строго lowercase snake_case.
- НЕ добавлять логику вычисления hw_type.
- НЕ менять json_writer/stats_collector.
- НЕ менять порядок существующих полей.

ACCEPTANCE:
- pytest проходит.
- hw_type = null во всех output.
- from src.core.classifier import HW_TYPE_VOCAB; len(HW_TYPE_VOCAB) == 20
- all(v == v.lower() for v in HW_TYPE_VOCAB) == True
- Тест hw_type_counts проверяет isinstance(dict), НЕ конкретные значения.

ПРОВЕРКА:
  python -c "
from src.core.classifier import HW_TYPE_VOCAB
print(f'Count: {len(HW_TYPE_VOCAB)}')
print(f'All lowercase: {all(v == v.lower() for v in HW_TYPE_VOCAB)}')
print(sorted(HW_TYPE_VOCAB))
"
  pytest tests/test_stats_hw_type.py -v
  python main.py test_data/dl1.xlsx
  python -c "from pathlib import Path\
out = Path('output')\
_latest_run = max(out.glob('run_*'), key=lambda p: p.stat().st_mtime)\
import json; print(json.load(open(_latest_run/'run_summary.json', encoding='utf-8'))['hw_type_counts'])"
  # Должно быть: {}
```

---

### Prompt 3 — Pack 6 part 1: hw_type_rules секция в YAML

```
ПРОЕКТ: teresa / dell_spec_classifier
ФАЙЛ: rules/dell_rules.yaml

КОНТЕКСТ:
Taxonomy v4: 20 hw_type значений (все snake_case).
Три слоя: device_type_map → rule_id_map → regex rules.
Порядок regex КРИТИЧЕН. Перехватчики первые. НЕТ generic storage fallback.
НЕТ Thermal→heatsink. OCP сужен до "OCP 3.0 Network".

ЗАДАЧА: Добавить секцию hw_type_rules В КОНЕЦ dell_rules.yaml (после device_type_rules).

СОДЕРЖИМОЕ (вставить дословно):

# ============================================================
# HW TYPE (third pass: only for ITEM rows with entity_type HW)
# Priority: device_type_map > rule_id_map > regex rules > null
# First match wins in regex rules. ORDER MATTERS.
# ============================================================
hw_type_rules:
  applies_to: [HW]

  # Layer 1: device_type → hw_type (all snake_case)
  device_type_map:
    cpu: cpu
    psu: psu
    nic: network_adapter
    storage_nvme: nvme
    storage_ssd: ssd
    raid_controller: storage_controller
    hba: storage_controller

  # Layer 2: matched_rule_id → hw_type
  rule_id_map:
    HW-001: chassis
    HW-004: nvme
    HW-005-STORAGE-CUS: nvme
    HW-006-PSU-CUS: psu
    HW-007-NIC-CUS: network_adapter
    HW-008-HBA-PERC-CUS: storage_controller
    HW-009-CPU-CUS: cpu

  # Layer 3: regex rules (first match wins, ORDER MATTERS)
  rules:
    # --- blank (перехват до всего) ---
    - field: module_name
      pattern: '(?i)\b(Blank|Filler|Dummy)\b'
      hw_type: blank

    - field: option_name
      pattern: '(?i)\b(Blank|Filler|Dummy|Slot\s+Filler)\b'
      hw_type: blank

    # --- backplane (до storage) ---
    - field: module_name
      pattern: '(?i)\b(Backplane|Drive\s+Cage|Bay\s+Assembly)\b'
      hw_type: backplane

    - field: option_name
      pattern: '(?i)\b(Backplane|Drive\s+Cage|Bay\s+Assembly)\b'
      hw_type: backplane

    # --- cable (до GPU/network — перехват "No Cable" и Cables модулей) ---
    - field: module_name
      pattern: '(?i)\bCables?\b'
      hw_type: cable

    - field: option_name
      pattern: '(?i)(No\s+(Cable|Cables)\s+Required|No\s+Cable|No\s+DPU)'
      hw_type: cable

    # --- mounting_kit (до chassis) ---
    - field: module_name
      pattern: '(?i)\b(Rack\s+Rails|Cable\s+Management)\b'
      hw_type: mounting_kit

    - field: option_name
      pattern: '(?i)\b(ReadyRails|Cable\s+Management\s+Arm|CMA)\b'
      hw_type: mounting_kit

    # --- cpu ---
    - field: module_name
      pattern: '(?i)\b(Processor|Additional\s+Processor)\b'
      hw_type: cpu

    # --- ram ---
    - field: module_name
      pattern: '(?i)\bMemory\s+Capacity\b'
      hw_type: ram

    # --- nvme (option_name, до generic storage) ---
    - field: option_name
      pattern: '(?i)\bNVMe\b'
      hw_type: nvme

    - field: module_name
      pattern: '(?i)\b(Boot\s+Optimized|BOSS)\b'
      hw_type: nvme

    # --- ssd (option_name, negative lookahead for NVMe) ---
    - field: option_name
      pattern: '(?i)\b(SSD|SATA)\b(?!.*NVMe)'
      hw_type: ssd

    # --- hdd ---
    - field: option_name
      pattern: '(?i)\b(HDD|\d+(\.\d+)?K\s*RPM|7200\s*RPM|10K\s*RPM|15K\s*RPM)\b'
      hw_type: hdd

    # --- storage_controller ---
    - field: module_name
      pattern: '(?i)\b(RAID|Storage\s+Controller|External\s+Controller)\b'
      hw_type: storage_controller

    - field: option_name
      pattern: '(?i)\b(PERC|HBA|Fibre\s+Channel|BBU|Battery\s+Backup)\b'
      hw_type: storage_controller

    # --- psu ---
    - field: module_name
      pattern: '(?i)\bPower\s+Supply\b'
      hw_type: psu

    # --- cpu_heatsink (ONLY explicit Heatsink in option_name) ---
    - field: option_name
      pattern: '(?i)\bHeatsink\b'
      hw_type: cpu_heatsink

    # --- fan (explicit Fan in option or Fans in module) ---
    # RISK: verify on dl2 that "Fan"/"Fans" does not appear in non-cooling contexts
    - field: option_name
      pattern: '(?i)\bFan\b'
      hw_type: fan

    - field: module_name
      pattern: '(?i)\bFans?\b'
      hw_type: fan

    # --- network_adapter (NARROWED: explicit adapter context, not bare "OCP") ---
    - field: module_name
      pattern: '(?i)\b(Network\s+Adapter|OCP\s+3\.0\s+Network|NIC|Multi\s+Selection\s+Network)\b'
      hw_type: network_adapter

    # --- gpu (module starts with GPU/FPGA, NOT containing Cables) ---
    - field: module_name
      pattern: '(?i)^(GPU|FPGA)\b(?!.*Cables)'
      hw_type: gpu

    # --- riser ---
    - field: module_name
      pattern: '(?i)\b(PCIe|Riser)\b'
      hw_type: riser

    # --- chassis ---
    - field: module_name
      pattern: '(?i)\b(Chassis|Bezel|Server\s+Accessories)\b'
      hw_type: chassis

    # --- management ---
    - field: module_name
      pattern: '(?i)\b(KVM|BMC|Quick\s+Sync)\b'
      hw_type: management

    # --- tpm ---
    - field: module_name
      pattern: '(?i)\b(TPM|Trusted\s+Platform)\b'
      hw_type: tpm

    # --- motherboard ---
    - field: module_name
      pattern: '(?i)\bMotherboard\b'
      hw_type: motherboard

    # NOTE: Thermal Configuration without Heatsink/Fan in option → no match → null + warning.
    # NOTE: Hard Drives without SSD/HDD/NVMe signal in option → no match → null + warning.
    # NOTE: "OCP 3.0 Accessories" with "No Cable" → caught by cable rule above.
    # These gaps are resolved in Pack 10 (dl2-dl5 expansion).

ОГРАНИЧЕНИЯ:
- НЕ менять существующие секции.
- ВСЕ hw_type значения — lowercase snake_case.
- Порядок regex rules строго как выше.
- YAML валидный.

ACCEPTANCE:
- python -c "import yaml; d=yaml.safe_load(open('rules/dell_rules.yaml')); h=d['hw_type_rules']; print(len(h['rules']), len(h['device_type_map']), len(h['rule_id_map']))"
  Ожидается: >= 28 rules, 7 device_type_map, 7 rule_id_map
- Все значения lowercase.

ПРОВЕРКА:
  python -c "
import yaml
d = yaml.safe_load(open('rules/dell_rules.yaml'))
h = d['hw_type_rules']
all_vals = list(h['device_type_map'].values()) + list(h['rule_id_map'].values()) + [r['hw_type'] for r in h['rules']]
print(f'Rules: {len(h[\"rules\"])}')
print(f'All lowercase: {all(v == v.lower() for v in all_vals)}')
print(f'Unique hw_types: {sorted(set(all_vals))}')
"
```

---

### Prompt 4 — Pack 6 part 2: RuleSet загрузка hw_type_rules

```
ПРОЕКТ: teresa / dell_spec_classifier
ФАЙЛ: src/rules/rules_engine.py

КОНТЕКСТ:
hw_type_rules добавлена в YAML. Загрузить в RuleSet аналогично device_type_rules.

ЗАДАЧА:
В RuleSet.__init__(), ПОСЛЕ блока device_type_rules, добавить:

    htr = self._data.get("hw_type_rules") or {}
    self.hw_type_rules: List[dict] = htr.get("rules") or []
    self.hw_type_device_type_map: dict = htr.get("device_type_map") or {}
    self.hw_type_rule_id_map: dict = htr.get("rule_id_map") or {}
    ht_applies = htr.get("applies_to") or []
    self.hw_type_applies_to = set(ht_applies) if isinstance(ht_applies, list) else set()

ОГРАНИЧЕНИЯ:
- НЕ менять существующий код.
- НЕ добавлять функций.
- Паттерн ИДЕНТИЧЕН device_type_rules.

ACCEPTANCE:
- RuleSet.load("rules/dell_rules.yaml") — OK.
- ruleset.hw_type_device_type_map["cpu"] == "cpu"
- ruleset.hw_type_rule_id_map["HW-001"] == "chassis"
- len(ruleset.hw_type_rules) >= 28
- "HW" in ruleset.hw_type_applies_to

ПРОВЕРКА:
  python -c "
from src.rules.rules_engine import RuleSet
rs = RuleSet.load('rules/dell_rules.yaml')
print('rules:', len(rs.hw_type_rules))
print('dt_map:', rs.hw_type_device_type_map)
print('rid_map:', rs.hw_type_rule_id_map)
print('applies:', rs.hw_type_applies_to)
assert rs.hw_type_device_type_map['cpu'] == 'cpu'
assert rs.hw_type_rule_id_map['HW-001'] == 'chassis'
print('OK')
"
  pytest tests/ -v
```

---

### Prompt 5 — Pack 7: _apply_hw_type() реализация и подключение

```
ПРОЕКТ: teresa / dell_spec_classifier
ФАЙЛЫ: src/rules/rules_engine.py, src/core/classifier.py

КОНТЕКСТ:
RuleSet загружает hw_type_rules. Нужен третий pass _apply_hw_type().
Три слоя: device_type_map → rule_id_map → regex rules → null.
hw_type только для entity_type HW. Все значения lowercase snake_case.

ЗАДАЧА (2 файла):

=== src/rules/rules_engine.py ===

Добавить match_hw_type_rule() ПОСЛЕ match_device_type_rule():

def match_hw_type_rule(row: NormalizedRow, rules: List[dict]) -> Optional[dict]:
    """Match row against hw_type regex rules. First match wins."""
    if not rules:
        return None
    for rule in rules:
        field = rule.get("field")
        pattern = rule.get("pattern")
        if not field or not pattern:
            continue
        if field == "module_name":
            value = row.module_name or ""
        elif field == "option_name":
            value = row.option_name or ""
        else:
            continue
        if re.search(pattern, str(value), re.IGNORECASE):
            return rule
    return None

=== src/core/classifier.py ===

1. Обновить import:
   from src.rules.rules_engine import RuleSet, match_rule, match_device_type_rule, match_hw_type_rule

2. Добавить _apply_hw_type() ПОСЛЕ _apply_device_type():

def _apply_hw_type(
    row: NormalizedRow,
    result: ClassificationResult,
    ruleset: RuleSet,
) -> ClassificationResult:
    """
    Third pass: compute hw_type for HW rows.
    Priority: device_type_map > rule_id_map > regex rules > null.
    Only applies to entity_types in hw_type_rules.applies_to.
    """
    if result.entity_type is None or result.matched_rule_id == "UNKNOWN-000":
        return result
    if result.entity_type.value not in ruleset.hw_type_applies_to:
        return result

    # Layer 1: device_type → hw_type
    if result.device_type and result.device_type in ruleset.hw_type_device_type_map:
        return replace(result, hw_type=ruleset.hw_type_device_type_map[result.device_type])

    # Layer 2: rule_id → hw_type
    if result.matched_rule_id in ruleset.hw_type_rule_id_map:
        return replace(result, hw_type=ruleset.hw_type_rule_id_map[result.matched_rule_id])

    # Layer 3: regex rules (first match wins)
    match = match_hw_type_rule(row, ruleset.hw_type_rules)
    if match and match.get("hw_type"):
        return replace(result, hw_type=match["hw_type"])

    return result

3. В classify_row() — КАЖДОЕ:
     return _apply_device_type(row, result, ruleset)
   ЗАМЕНИТЬ на:
     result = _apply_device_type(row, result, ruleset)
     return _apply_hw_type(row, result, ruleset)

   Мест: 8 (BASE, SERVICE, LOGISTIC, SOFTWARE, NOTE, CONFIG, HW, UNKNOWN).
   Для UNKNOWN (финальный return):
     result = ClassificationResult(row_kind=..., ..., warnings=[...])
     return _apply_hw_type(row, result, ruleset)
   (UNKNOWN не пройдёт из-за matched_rule_id == "UNKNOWN-000".)

ОГРАНИЧЕНИЯ:
- НЕ менять логику entity_type/device_type/state.
- replace() для immutable update.
- Вызывать для ВСЕХ типов (проверка applies_to внутри).

ACCEPTANCE:
- python main.py test_data/dl1.xlsx: hw_type_counts НЕ пустой.
- Non-HW: hw_type = null.
- pytest GREEN (тест проверяет isinstance(dict), не содержимое).

ПРОВЕРКА:
  python main.py test_data/dl1.xlsx

  python -c "
import json
d = json.load(open(_latest_run/'run_summary.json', encoding='utf-8'))
print('hw_type_counts:', json.dumps(d['hw_type_counts'], indent=2))
print('total hw_type:', sum(d['hw_type_counts'].values()))
"

  python -c "
import json
with open('($run.FullName + '\classification.jsonl')') as f:
    lines = [json.loads(l) for l in f if l.strip()]
hw_null = [(i, l.get('matched_rule_id')) for i,l in enumerate(lines)
           if l.get('entity_type')=='HW' and not l.get('hw_type')]
print(f'HW rows without hw_type: {len(hw_null)}')
for idx, rid in hw_null:
    print(f'  row {idx}: {rid}')
nonhw = [i for i,l in enumerate(lines) if l.get('entity_type')!='HW' and l.get('hw_type')]
print(f'Non-HW with hw_type: {len(nonhw)} (must be 0)')
"

  pytest tests/ -v
```

---

### Prompt 6 — Pack 8: Annotated source — hw_type + naming

```
ПРОЕКТ: teresa / dell_spec_classifier
ФАЙЛЫ: src/outputs/excel_writer.py (или файл генерирующий annotated_source.xlsx), main.py

КОНТЕКСТ:
annotated_source.xlsx — отладочный Excel. Два изменения:
(1) колонка hw_type, (2) naming по источнику.

ЗАДАЧА:

A) Колонка hw_type:
   1. Найти код: grep -r "annotated_source" src/
   2. Добавить "hw_type" ПОСЛЕ "device_type" в список колонок.
   3. Значение: ClassificationResult.hw_type (или getattr(result, "hw_type", None)).
   4. HW: строковое значение. Non-HW: пустая ячейка.

B) Naming:
   1. filename = f"{Path(input_file).stem}_annotated.xlsx"
   2. Пробросить input_file из main.py.
   3. dl1.xlsx → dl1_annotated.xlsx

ОГРАНИЧЕНИЯ:
- НЕ менять логику классификации.
- НЕ менять другие output файлы.
- Если сигнатура меняется — обновить callers.

ACCEPTANCE:
- python main.py test_data/dl1.xlsx → output/dl1_annotated.xlsx.
- Колонка "hw_type" после "device_type".
- Файл "annotated_source.xlsx" НЕ создаётся.

ПРОВЕРКА:
  python main.py test_data/dl1.xlsx
  ls output/*_annotated.xlsx

  python -c "
import openpyxl
wb = openpyxl.load_workbook('output/dl1_annotated.xlsx')
ws = wb.active
headers = [cell.value for cell in ws[1]]
print('Headers:', headers)
assert 'hw_type' in headers, 'FAIL: hw_type column missing'
dt_idx = headers.index('device_type')
ht_idx = headers.index('hw_type')
assert ht_idx == dt_idx + 1, f'FAIL: hw_type at {ht_idx}, expected {dt_idx+1}'
print('OK')
"
```

---

### Prompt 7 — Pack 9: Golden + regression lock (ТОЧНЫЕ counts)

```
ПРОЕКТ: teresa / dell_spec_classifier
ФАЙЛЫ: golden/dl1_expected.jsonl..dl5_expected.jsonl, tests/test_stats_hw_type.py, tests/test_regression.py

КОНТЕКСТ:
hw_type активирован (Pack 7). Golden устарели. Тест проверяет isinstance(dict).
ТЕПЕРЬ фиксируем точные counts на основе РЕАЛЬНОГО прогона.
В test_regression.py ранее был временный ignore hw_type (TEMP) — теперь его нужно убрать,
чтобы regression снова сравнивал hw_type строго.

ЗАДАЧА:

A) Перегенерировать golden (dl1–dl5):
   Для каждого файла dlN.xlsx:
   python .\main.py --input .\test_data\dlN.xlsx --config .\config.yaml --output-dir .\output
   $run = Get-ChildItem .\output -Directory -Filter "run_*" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
   Copy-Item ($run.FullName + "\classification.jsonl") -Destination (".\golden\dlN_expected.jsonl") -Force

B) Обновить tests/test_stats_hw_type.py:
   1. Заменить assert isinstance(hw_type_counts, dict) на ТОЧНЫЕ expected counts
      из output/run_summary.json → hw_type_counts (после прогона dl1.xlsx).
   2. Добавить: все значения в hw_type_counts ∈ HW_TYPE_VOCAB.
   3. Добавить: sum(hw_type_counts.values()) == expected total.

C) Убрать временный ignore hw_type в tests/test_regression.py:
   1. Найти блок с комментарием:
      # TEMP: ignore hw_type until Pack 9 (golden regeneration)
   2. Удалить pop("hw_type", None) и сравнивать полные dict как раньше.

D) Убедиться все тесты проходят.

ОГРАНИЧЕНИЯ:
- Значения берутся ТОЛЬКО из реального прогона, НЕ из таблицы в плане.
- НЕ менять classifier.py / rules.

ACCEPTANCE:
- pytest tests/ -v — 0 failures.
- golden (dl1–dl5) содержит hw_type.
- Тест проверяет точные counts (по dl1).
- Все hw_type значения ∈ HW_TYPE_VOCAB.
- Regression снова сравнивает hw_type (ignore удалён).

ПРОВЕРКА:
  # Прогон + golden update (пример для dl1)
  python .\main.py --input .\test_data\dl1.xlsx --config .\config.yaml --output-dir .\output
  $run = Get-ChildItem .\output -Directory -Filter "run_*" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
  Copy-Item ($run.FullName + "\classification.jsonl") -Destination .\golden\dl1_expected.jsonl -Force

  pytest tests/ -v

  python -c "
import json
from src.core.classifier import HW_TYPE_VOCAB
with open('golden/dl1_expected.jsonl') as f:
    lines = [json.loads(l) for l in f if l.strip()]
used = set(l['hw_type'] for l in lines if l.get('hw_type'))
bad = used - HW_TYPE_VOCAB
print(f'hw_types in golden: {sorted(used)}')
assert not bad, f'NOT in vocab: {bad}'
print('OK')
"
```

---
### Prompt 8 — Pack 10 part 1: Warning + monitoring

```
ПРОЕКТ: teresa / dell_spec_classifier
ФАЙЛЫ: src/core/classifier.py, src/diagnostics/stats_collector.py

КОНТЕКСТ:
_apply_hw_type() может оставить hw_type=null для HW-строки. Нужен warning и метрика.

ЗАДАЧА:

A) src/core/classifier.py — _apply_hw_type():
   В конце, ПЕРЕД финальным `return result`, добавить:

   if result.entity_type and result.entity_type.value in ruleset.hw_type_applies_to:
       return replace(result, warnings=result.warnings + ["hw_type unresolved for HW row"])
   return result

B) src/diagnostics/stats_collector.py — collect_stats():
   ПОСЛЕ hw_type_counts добавить:

   hw_type_null_count = sum(
       1 for r in classification_results
       if r.row_kind == RowKind.ITEM
       and r.entity_type == EntityType.HW
       and not getattr(r, "hw_type", None)
   )

   Добавить в return dict: "hw_type_null_count": hw_type_null_count

ОГРАНИЧЕНИЯ:
- Warning через replace().
- НЕ менять слои резолюции.

ACCEPTANCE:
- dl1: hw_type_null_count — число (ожидаем ≤ 2).
- Warning "hw_type unresolved" появляется для null строк.
- pytest green.

ПРОВЕРКА:
  python main.py test_data/dl1.xlsx
  python -c "
import json
d = json.load(open(_latest_run/'run_summary.json', encoding='utf-8'))
print('hw_type_null_count:', d.get('hw_type_null_count', 'MISSING'))
"
  python -c "
import json
with open('($run.FullName + '\classification.jsonl')') as f:
    lines = [json.loads(l) for l in f if l.strip()]
warned = [(i, l) for i,l in enumerate(lines)
          if 'hw_type unresolved' in str(l.get('warnings',''))]
print(f'Warned rows: {len(warned)}')
for idx, l in warned:
    print(f'  row {idx}: rule={l[\"matched_rule_id\"]}')
"
```

---

### Prompt 9 — Pack 10 part 2: dl2–dl5 expansion + Fan verification

```
ПРОЕКТ: teresa / dell_spec_classifier
ФАЙЛЫ: rules/dell_rules.yaml, golden/*_expected.jsonl

КОНТЕКСТ:
hw_type работает для dl1. Расширяем для dl2–dl5.
ВАЖНО: на dl2 проверить что "Fan"/"Fans" regex не даёт false positives
в non-cooling контекстах.

ЗАДАЧА:

1. Прогнать каждый файл:

   for f in test_data/dl2.xlsx test_data/dl3.xlsx test_data/dl4.xlsx test_data/dl5.xlsx; do
     echo "=== $f ==="
     python main.py "$f"
     python -c "
import json
d = json.load(open(_latest_run/'run_summary.json', encoding='utf-8'))
print('null:', d.get('hw_type_null_count', 0))
print('counts:', json.dumps(d.get('hw_type_counts', {}), indent=2))
"
   done

2. ОБЯЗАТЕЛЬНО на dl2: проверить Fan строки:

   python -c "
import json
with open('($run.FullName + '\classification.jsonl')') as f:
    cls = [json.loads(l) for l in f if l.strip()]
with open('output/rows_normalized.json') as f:
    norm = json.load(f)
for i,(n,c) in enumerate(zip(norm,cls)):
    if c.get('hw_type') == 'fan':
        print(f'row={i} mod=\"{n[\"module_name\"]}\" opt=\"{n[\"option_name\"][:80]}\"')
"
   Если есть false positive — сузить regex.

3. Для null hw_type строк:

   python -c "
import json
with open('($run.FullName + '\classification.jsonl')') as f:
    cls = [json.loads(l) for l in f if l.strip()]
with open('output/rows_normalized.json') as f:
    norm = json.load(f)
for i,(n,c) in enumerate(zip(norm,cls)):
    if c.get('entity_type')=='HW' and not c.get('hw_type'):
        print(f'row={i} rule={c[\"matched_rule_id\"]} mod=\"{n[\"module_name\"]}\" opt=\"{n[\"option_name\"][:80]}\"')
"

4. Для каждой непокрытой строки:
   - Определить hw_type.
   - Добавить regex в hw_type_rules.rules (в правильном месте по приоритету).
   - ПРОВЕРИТЬ dl1 regression: python main.py test_data/dl1.xlsx && pytest tests/ -v

5. Перегенерировать golden для dl2–dl5.

ОГРАНИЧЕНИЯ:
- Каждый hw_type ДОЛЖЕН быть в HW_TYPE_VOCAB.
- Если нужен новый — СНАЧАЛА обновить vocab + тесты.
- НЕ менять существующие regex (только добавлять).
- НЕ менять entity_type правила.

ACCEPTANCE:
- hw_type_null_count минимален для dl1–dl5.
- Нет Fan false positives.
- pytest green.
- Все golden обновлены.

ПРОВЕРКА:
  for f in test_data/dl*.xlsx; do
    python main.py "$f"
    echo "$f: null=$(python -c \"import json; print(json.load(open(_latest_run/'run_summary.json', encoding='utf-8')).get('hw_type_null_count',0))\")"
  done
  pytest tests/ -v
```

---

## Порядок выполнения

```
Pack 4.5 → Prompt 1  (entity_type bugfixes: 4 бага)   ← ПЕРВЫМ
Pack 5   → Prompt 2  (enum + field + test isinstance)  ← contract only, no behavior
Pack 6   → Prompt 3  (YAML rules)                      ← config only
Pack 6   → Prompt 4  (RuleSet loading)                  ← config only
Pack 7   → Prompt 5  (_apply_hw_type)                   ← hw_type ВКЛЮЧАЕТСЯ, test green
Pack 8   → Prompt 6  (annotated source)
Pack 9   → Prompt 7  (golden + ТОЧНЫЕ counts)           ← test locks exact values
Pack 10  → Prompt 8  (warning/monitoring)
Pack 10  → Prompt 9  (dl2–dl5 + Fan verify)
```

Каждый prompt = один атомарный PR.
pytest green после КАЖДОГО prompt (без исключений — это было противоречие в v3, исправлено).
