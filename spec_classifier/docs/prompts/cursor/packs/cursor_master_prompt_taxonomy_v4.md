# CURSOR MASTER PROMPT — Cisco Cable Fix + hw_type Taxonomy v2.0
## teresa / spec_classifier · Feature branch: `feature/hw-type-taxonomy-v2`

---

## ПЛАН (порядок обязателен)

| Фаза | Что делаем | Файлы | Golden меняется? |
|------|-----------|-------|-----------------|
| **A** | **Cisco cable fix**: убрать кабели из LOGISTIC → HW | cisco_rules.yaml, ccw golden | ДА (entity_type!) |
| 0 | Разместить taxonomy doc в репо | docs/taxonomy/ | нет |
| 1 | Расширить HW_TYPE_VOCAB (27+legacy), applies_to BASE | classifier.py, yaml | нет |
| 2 | Переименовать hw_type в Dell правилах | dell_rules.yaml, dl golden | ДА (только hw_type) |
| 3 | Переименовать hw_type в Cisco правилах | cisco_rules.yaml, ccw golden | ДА (только hw_type) |
| 4 | Удалить legacy из vocab | classifier.py | нет |

Фазу A делать на **чистой ветке до старта taxonomy migration**. Фазы 0–4 — после мержа A.

---

## ОБЯЗАТЕЛЬНО ПРОЧИТАТЬ ПЕРЕД СТАРТОМ

Программа работает стабильно (v1.2.0, unknown_count=0 на всех 7 датасетах).  
**Главный принцип: не сломать ничего из того, что работает. Каждая фаза верифицируется тестами до перехода к следующей.**

Прочитай перед работой:
- `docs/taxonomy/hw_type_taxonomy.md` — source of truth по новому словарю (27 значений)
- `docs/roadmap/hw_type_plan_v4.md` — архитектура hw_type (3 слоя: device_type_map → rule_id_map → regex)
- `src/core/classifier.py` — `HW_TYPE_VOCAB`, `_apply_hw_type()`, `hw_type_applies_to`
- `rules/dell_rules.yaml` — текущие `hw_type_rules`
- `rules/cisco_rules.yaml` — текущие `hw_type_rules`
- `tests/test_regression.py`, `tests/test_regression_cisco.py` — как работают regression тесты
- `tests/test_dec_acceptance.py`, `tests/test_device_type.py` — unit-тесты с явными hw_type assert

---

## АРХИТЕКТУРНЫЕ ОГРАНИЧЕНИЯ (действуют во всех фазах)

```
ЗАПРЕЩЕНО ТРОГАТЬ БЕЗ ЯВНОГО РАЗРЕШЕНИЯ В КОНКРЕТНОЙ ФАЗЕ:
- src/core/normalizer.py
- src/core/state_detector.py
- src/rules/rules_engine.py
- src/vendors/
- src/outputs/
- src/diagnostics/
- main.py
- tests/conftest.py
- golden/*_expected.jsonl      (обновлять ТОЛЬКО командой --update-golden, не вручную)

РАЗРЕШЕНО ВЕЗДЕ (чтение):
- Любые файлы для понимания контекста (read-only)
```

---

## GIT-СТРАТЕГИЯ

```powershell
# Убедиться что рабочее дерево чисто
git diff --name-only        # должен быть пустой вывод

# Создать ветку
git checkout main
git tag baseline-before-taxonomy-v2
git checkout -b feature/hw-type-taxonomy-v2
```

Коммит после каждой успешно пройденной фазы — только явно перечисленными файлами. **`git add .` запрещено.**

---

## ФАЗА A — CISCO CABLE FIX (делается ДО taxonomy migration)

### Контекст: что сломано

Все кабели в Cisco CCW сейчас уходят в `entity_type: LOGISTIC` через два слишком широких правила:
- `LOGISTIC-C-001`: `^CAB-` — ловит ВСЕ SKU с префиксом CAB- включая сигнальные кабели и органайзеры
- `LOGISTIC-C-002`: `^STACK-T` — ловит стекинг кабель

Кабели — физические компоненты с ценой и артикулом. Они должны быть `entity_type: HW`.

### Полная картина затронутых строк (ccw_1 + ccw_2)

| SKU | option_name | Сейчас | Должно быть |
|-----|------------|--------|------------|
| CAB-9K10A-EU | Power Cord, 250VAC 10A CEE 7/7 Plug, EU | LOGISTIC / power_cord / None | HW / power_cord / None |
| CAB-C13-CBN | Cabinet Jumper Power Cord, 250 VAC 10A, C14-C13 | LOGISTIC / power_cord / None | HW / power_cord / None |
| CAB-C15-CBN | Cabinet Jumper Power Cord, 250 VAC 13A, C14-C15 | LOGISTIC / power_cord / None | HW / power_cord / None |
| CAB-GUIDE-1RU | 1RU Cable Management Guides 9200 and 9300 | LOGISTIC / power_cord / None | HW / None / mounting_kit |
| STACK-T3A-1M | C9300L & C9300LM 1M Type 3A Stacking Cable | LOGISTIC / power_cord / None | HW / None / cable |

> **Примечание по CAB-GUIDE-1RU:** Это не кабель и не кабель питания — это металлический кронштейн-органайзер. Текущий `device_type=power_cord` — двойная ошибка. Правильно: `hw_type=mounting_kit` (в taxonomy Phase 3 станет `rail`).
>
> **Примечание по `hw_type=None` для power_cord:** По контракту taxonomy (решение №6) — `power_cord` не входит в `HW_TYPE_VOCAB`, `hw_type` остаётся `None` намеренно.

### Git для Фазы A

```powershell
git checkout main
git pull
git tag baseline-before-cable-fix
git checkout -b feature/cisco-cable-fix
```

### Разрешённые файлы в Фазе A

- `rules/cisco_rules.yaml` — секции `logistic_rules`, `hw_rules`, `device_type_rules`, `hw_type_rules`
- `golden/ccw_1_expected.jsonl`, `golden/ccw_2_expected.jsonl` — только через `--update-golden`

### Изменение 1 — `logistic_rules`: удалить кабельные правила

```yaml
# БЫЛО (5 правил):
logistic_rules:
  - field: sku
    pattern: '^CAB-'
    entity_type: LOGISTIC
    rule_id: LOGISTIC-C-001          # ← УДАЛИТЬ
  - field: sku
    pattern: '^STACK-T'
    entity_type: LOGISTIC
    rule_id: LOGISTIC-C-002          # ← УДАЛИТЬ
  - field: option_name
    pattern: '(?i)power cord|jumper power cord'
    entity_type: LOGISTIC
    rule_id: LOGISTIC-C-003          # ← УДАЛИТЬ
  - field: option_name
    pattern: '(?i)stacking cable'
    entity_type: LOGISTIC
    rule_id: LOGISTIC-C-004          # ← УДАЛИТЬ
  - field: option_name
    pattern: '(?i)cable management guide'
    entity_type: LOGISTIC
    rule_id: LOGISTIC-C-005          # ← УДАЛИТЬ

# СТАЛО (пустой список — для Cisco нет реально логистических строк):
logistic_rules: []
```

### Изменение 2 — `hw_rules`: добавить правила для кабелей

Добавить в конец секции `hw_rules` (после последнего существующего правила):

```yaml
  # --- Power cords (кабели питания) ---
  - field: option_name
    pattern: '(?i)(power\s+cord|jumper\s+power\s+cord)'
    entity_type: HW
    rule_id: HW-C-015-PWRCORD

  # --- Stacking cable ---
  - field: sku
    pattern: '^STACK-T'
    entity_type: HW
    rule_id: HW-C-016-STACKCBL

  - field: option_name
    pattern: '(?i)stacking\s+cable'
    entity_type: HW
    rule_id: HW-C-017-STACKCBL-OPT

  # --- Cable management / organizer ---
  - field: option_name
    pattern: '(?i)cable\s+management\s+guide'
    entity_type: HW
    rule_id: HW-C-018-CBLGUIDE
```

### Изменение 3 — `device_type_rules`: разделить DT-C-003

```yaml
# БЫЛО (один паттерн для всех CAB- и STACK-T → power_cord):
- field: sku
  pattern: '^(CAB-|STACK-T)'
  device_type: power_cord
  rule_id: DT-C-003

# СТАЛО (два точечных правила):
# Кабели питания по описанию (точнее чем по SKU-префиксу)
- field: option_name
  pattern: '(?i)(power\s+cord|jumper\s+power\s+cord)'
  device_type: power_cord
  rule_id: DT-C-003-PWRCORD

# Стекинг кабель — device_type не нужен (hw_type=cable достаточно)
# CAB-GUIDE-1RU — device_type не нужен (hw_type=mounting_kit)
# Оба получат device_type=None автоматически
```

### Изменение 4 — `hw_type_rules`: добавить маппинги для новых HW строк

В секцию `hw_type_rules.rules` добавить (в начало, до существующих правил):

```yaml
  # --- Stacking cable → cable ---
  - field: sku
    pattern: '^STACK-T'
    hw_type: cable
    rule_id: HWT-C-008-STACKCBL

  - field: option_name
    pattern: '(?i)stacking\s+cable'
    hw_type: cable
    rule_id: HWT-C-009-STACKCBL-OPT

  # --- Cable management organizer → mounting_kit ---
  # (В Фазе 3 taxonomy migration будет переименовано в rail)
  - field: option_name
    pattern: '(?i)cable\s+management\s+guide'
    hw_type: mounting_kit
    rule_id: HWT-C-010-CBLGUIDE

  # --- Power cords → hw_type: None (намеренно, power_cord не в HW_TYPE_VOCAB) ---
  # Правило не нужно — отсутствие совпадения = hw_type: None для HW строк
  # ВАЖНО: строки power_cord теперь HW → получат warning "hw_type unresolved"
  # Это ожидаемо и принято как компромисс (power_cord вне vocab по контракту)
  # Чтобы подавить warning, добавить в device_type_map:
```

В секцию `hw_type_rules.device_type_map` добавить:

```yaml
device_type_map:
  # ... существующие ...
  power_cord: power_cord   # ← ДОБАВИТЬ: подавляет hw_type warning для power_cord строк
                           # Но power_cord не в HW_TYPE_VOCAB → будет валидационная ошибка!
```

> **⚠️ СТОП — проблема с power_cord и HW_TYPE_VOCAB:**  
> Если `device_type_map: power_cord: power_cord`, то `hw_type=power_cord` не пройдёт валидацию HW_TYPE_VOCAB (power_cord там нет).  
> **Решение:** НЕ добавлять power_cord в device_type_map. Строки с `device_type=power_cord` и `entity_type=HW` получат `hw_type=None` + warning "hw_type unresolved".  
> Это warning в stats/logs, но **не тест-фейл** — тесты проверяют только known_count=0 для HW строк без hw_type при entity_type=HW.  
> После Фазы A проверить: does `test_unknown_threshold` fail? Если да — нужно добавить power_cord в HW_TYPE_VOCAB уже в Фазе A (не ждать Фазы 1).

### Обновление golden

```powershell
python main.py --input test_data/ccw_1.xlsx --vendor cisco --update-golden
python main.py --input test_data/ccw_2.xlsx --vendor cisco --update-golden
```

### Проверка golden diff (ОБЯЗАТЕЛЬНО)

```powershell
git diff golden/ccw_1_expected.jsonl golden/ccw_2_expected.jsonl
```

**Допустимые изменения** (в отличие от всех других фаз — здесь меняется `entity_type`):

| SKU | Поле | До | После |
|-----|------|----|-------|
| CAB-9K10A-EU | `entity_type` | `LOGISTIC` | `HW` |
| CAB-9K10A-EU | `matched_rule_id` | `LOGISTIC-C-001` | `HW-C-015-PWRCORD` |
| CAB-9K10A-EU | `device_type` | `power_cord` | `power_cord` |
| CAB-9K10A-EU | `hw_type` | `null` | `null` |
| CAB-C13-CBN, CAB-C15-CBN | (аналогично CAB-9K10A-EU) | — | — |
| CAB-GUIDE-1RU | `entity_type` | `LOGISTIC` | `HW` |
| CAB-GUIDE-1RU | `matched_rule_id` | `LOGISTIC-C-001` | `HW-C-018-CBLGUIDE` |
| CAB-GUIDE-1RU | `device_type` | `power_cord` | `null` |
| CAB-GUIDE-1RU | `hw_type` | `null` | `mounting_kit` |
| STACK-T3A-1M | `entity_type` | `LOGISTIC` | `HW` |
| STACK-T3A-1M | `matched_rule_id` | `LOGISTIC-C-002` | `HW-C-016-STACKCBL` |
| STACK-T3A-1M | `device_type` | `power_cord` | `null` |
| STACK-T3A-1M | `hw_type` | `null` | `cable` |

**СТОП если в diff есть:** изменения в строках, не перечисленных выше, или изменения полей `state`, `skus`.

### Верификация

```powershell
pytest tests/ -v --tb=short
# ВСЕ тесты PASS

pytest tests/test_unknown_threshold.py -v
# Если FAIL на ccw_1 или ccw_2 — power_cord строки дают hw_type warning
# Решение: добавить в HW_TYPE_VOCAB "power_cord" уже в этой фазе,
# и в hw_type_rules.device_type_map: power_cord: power_cord
```

### TODO после Фазы A (в отдельный PR)

Dell тоже классифицирует кабели питания как LOGISTIC (LOGISTIC-004-CORD). По тому же принципу они должны стать HW. Не делать в этом PR — отдельный коммит после стабилизации.

### Коммит

```powershell
git add rules/cisco_rules.yaml \
        golden/ccw_1_expected.jsonl golden/ccw_2_expected.jsonl
git commit -m "fix(cisco): move cables from LOGISTIC to HW — power_cord, stacking cable, cable guide"

# Merge в main перед стартом taxonomy migration
git checkout main
git merge feature/cisco-cable-fix
git tag baseline-before-taxonomy-v2
```

---

## ФАЗА 0 — ПОДГОТОВКА (без изменений кода)

**Задача:** разместить taxonomy в репозитории.

**Разрешённые файлы:** `docs/taxonomy/hw_type_taxonomy.md` (создать папку и скопировать файл).

```powershell
# Верификация
Test-Path docs/taxonomy/hw_type_taxonomy.md   # True

git add docs/taxonomy/hw_type_taxonomy.md
git commit -m "docs: add hw_type_taxonomy v1.1 as source of truth"
```

---

## ФАЗА 1 — РАСШИРИТЬ HW_TYPE_VOCAB

**Задача:** только расширить vocab и обновить `applies_to`. Никаких изменений в правилах, никаких изменений в golden.

**Разрешённые файлы:**
- `src/core/classifier.py` — только блок `HW_TYPE_VOCAB`
- `rules/dell_rules.yaml` — только строка `applies_to` в `hw_type_rules`
- `rules/cisco_rules.yaml` — только строка `applies_to` в `hw_type_rules`

### Изменение 1 — `src/core/classifier.py`

```python
# БЫЛО (20 значений):
HW_TYPE_VOCAB = frozenset({
    "cpu", "ram", "ssd", "hdd", "nvme",
    "storage_controller", "psu", "fan", "cpu_heatsink",
    "network_adapter", "riser", "gpu",
    "tpm", "chassis", "cable", "management",
    "motherboard", "mounting_kit", "backplane", "blank",
})

# СТАЛО (27 новых + 8 legacy для обратной совместимости = 35 на время миграции):
HW_TYPE_VOCAB = frozenset({
    # Основное изделие (BASE rows)
    "server", "switch", "storage_system", "wireless_ap",
    # Вычислительные компоненты
    "cpu", "memory", "gpu",
    # Подсистема хранения
    "storage_drive", "storage_controller", "hba", "backplane", "io_module",
    # Сеть
    "network_adapter", "transceiver", "cable",
    # Питание
    "psu",
    # Охлаждение
    "fan", "heatsink",
    # Расширение и механика
    "riser", "chassis", "rail", "blank_filler",
    # Управление
    "management", "tpm",
    # Аксессуары
    "accessory",
    # --- LEGACY (временно, удалить после Фазы 3) ---
    "ram", "ssd", "hdd", "nvme", "cpu_heatsink",
    "motherboard", "mounting_kit", "blank",
})
```

> Legacy значения (`ram`, `ssd`, `hdd`, `nvme`, `cpu_heatsink`, `motherboard`, `mounting_kit`, `blank`) сохранены намеренно — golden dl1–dl5 и ccw* ещё содержат эти значения. Тесты не упадут.  
> **Счёт:** 27 — финальный контракт (source of truth в taxonomy.md); 35 — временный размер vocab на период миграции. Legacy 8 значений удаляются в Фазе 4 после обновления всех golden. Не "чинить" это несоответствие раньше Фазы 4.

### Изменение 2 — `rules/dell_rules.yaml`

```yaml
# Найти секцию hw_type_rules и изменить только applies_to:
hw_type_rules:
  applies_to: [HW, BASE]    # было: [HW]
```

### Изменение 3 — `rules/cisco_rules.yaml`

```yaml
hw_type_rules:
  applies_to: [HW, BASE]    # было: [HW]
```

### Верификация

```powershell
pytest tests/ -v --tb=short
# Ожидаемый результат: ВСЕ тесты PASS
# Если есть FAIL — остановиться, не двигаться дальше
```

```powershell
git add src/core/classifier.py rules/dell_rules.yaml rules/cisco_rules.yaml
git commit -m "feat(taxonomy): expand HW_TYPE_VOCAB to v2 (27+legacy), add BASE to applies_to"
```

---

## ФАЗА 2 — ОБНОВИТЬ dell_rules.yaml + dl1–dl5 golden

**Задача:** исправить маппинги в Dell правилах, обновить golden, исправить unit-тесты.

**Разрешённые файлы:**
- `rules/dell_rules.yaml` — секции `device_type_map`, `rule_id_map`, `rules` внутри `hw_type_rules`
- `golden/dl1_expected.jsonl` — `golden/dl5_expected.jsonl` — только через `--update-golden`
- `tests/test_dec_acceptance.py`
- `tests/test_device_type.py`

### ⚠️ Скрытый риск: SAS HBA без суффикса попадёт в storage_controller

В текущем `dell_rules.yaml` `device_type=hba` ставится **только** если option_name содержит суффикс `(dib|ck|full\s+height|low\s+profile)`:
```
pattern: '(?i)(hba|fibre\s+channel|fc\s+hba).*(dib|ck|full\s+height|low\s+profile)'
device_type: hba
```

SAS/FC HBA без этих суффиксов `device_type` не получит. Тогда Layer 1 (`device_type_map`) не сработает, и строка попадёт в Layer 3, где:
```
pattern: '(?i)\b(PERC|HBA|Fibre\s+Channel|BBU|Battery\s+Backup)\b'
hw_type: storage_controller   ← неверно для HBA без суффикса
```

**Что сделать в Фазе 2:** после обновления golden запустить:
```powershell
# Найти строки где hw_type=storage_controller, но option_name содержит "HBA" без "PERC"
python -c "
import json
for i in range(1,6):
    with open(f'golden/dl{i}_expected.jsonl', encoding='utf-8-sig') as f:
        for line in f:
            r = json.loads(line)
            name = r.get('option_name', '') or ''
            if r.get('hw_type') == 'storage_controller' and 'HBA' in name and 'PERC' not in name:
                print(f'dl{i}: {name[:80]} | skus={r.get(\"skus\")}')
"
```
Если вывод непустой — в `dell_rules.yaml` нужно расширить паттерн для `device_type=hba` чтобы покрыть эти строки, либо добавить явное regex-правило в `hw_type_rules.rules` (pattern `\bHBA\b` без `PERC` → `hw_type: hba`). Это **не блокирует** переход к Фазе 3, но должно быть зафиксировано как issue для отдельного коммита.

### Изменение 1 — `device_type_map` в `hw_type_rules`

```yaml
# БЫЛО:
device_type_map:
  cpu: cpu
  psu: psu
  nic: network_adapter
  storage_nvme: nvme
  storage_ssd: ssd
  raid_controller: storage_controller
  hba: storage_controller      # ← ОШИБКА: HBA попадал в RAID

# СТАЛО:
device_type_map:
  cpu: cpu
  psu: psu
  nic: network_adapter
  storage_nvme: storage_drive   # nvme → storage_drive
  storage_ssd: storage_drive    # ssd → storage_drive
  raid_controller: storage_controller
  hba: hba                      # ← ИСПРАВЛЕНО: FC/SAS HBA → отдельный тип
```

### Изменение 2 — `rule_id_map`

```yaml
# БЫЛО:
rule_id_map:
  HW-001: chassis
  HW-OPTICS-001: network_adapter
  HW-BOSS-001: storage_controller
  HW-NOBOSS-BLANK-001: blank
  HW-005-STORAGE-CUS: nvme
  HW-006-PSU-CUS: psu
  HW-007-NIC-CUS: network_adapter
  HW-008-HBA-PERC-CUS: storage_controller
  HW-009-CPU-CUS: cpu

# СТАЛО:
rule_id_map:
  HW-001: chassis
  HW-OPTICS-001: network_adapter
  HW-BOSS-001: storage_controller
  HW-NOBOSS-BLANK-001: blank_filler    # blank → blank_filler
  HW-005-STORAGE-CUS: storage_drive    # nvme → storage_drive
  HW-006-PSU-CUS: psu
  HW-007-NIC-CUS: network_adapter
  HW-008-HBA-PERC-CUS: storage_controller  # PERC остаётся storage_controller
  HW-009-CPU-CUS: cpu
```

> **Почему HW-008-HBA-PERC-CUS остаётся `storage_controller`:**  
> `device_type_map` (Layer 1) имеет приоритет над `rule_id_map` (Layer 2) в `_apply_hw_type()`.  
> Строки с `device_type=hba` → Layer 1 → `hw_type=hba` ✓ (не доходят до rule_id_map).  
> Строки с `device_type=raid_controller` → Layer 1 → `hw_type=storage_controller` ✓  
> Строки без device_type → Layer 2 → `hw_type=storage_controller` (для PERC без device_type) ✓

### Изменение 3 — переименование в секции `rules`

В секции `hw_type_rules.rules` найти и заменить **все** вхождения:

| Найти | Заменить |
|-------|----------|
| `hw_type: ram` | `hw_type: memory` |
| `hw_type: nvme` | `hw_type: storage_drive` |
| `hw_type: ssd` | `hw_type: storage_drive` |
| `hw_type: hdd` | `hw_type: storage_drive` |
| `hw_type: cpu_heatsink` | `hw_type: heatsink` |
| `hw_type: mounting_kit` | `hw_type: rail` |
| `hw_type: blank` | `hw_type: blank_filler` |
| `hw_type: motherboard` | `hw_type: chassis` |

> **НЕ ТРОГАТЬ** `hw_type: storage_controller` — все PERC/BOSS/RAID правила корректны.

### Обновление golden

```powershell
python main.py --input test_data/dl1.xlsx --vendor dell --update-golden
python main.py --input test_data/dl2.xlsx --vendor dell --update-golden
python main.py --input test_data/dl3.xlsx --vendor dell --update-golden
python main.py --input test_data/dl4.xlsx --vendor dell --update-golden
python main.py --input test_data/dl5.xlsx --vendor dell --update-golden
```

### Проверка golden diff (ОБЯЗАТЕЛЬНО)

```powershell
git diff golden/
```

Допустимые изменения (только в поле `"hw_type"`):

| До | После |
|----|-------|
| `"hw_type": "ram"` | `"hw_type": "memory"` |
| `"hw_type": "nvme"` | `"hw_type": "storage_drive"` |
| `"hw_type": "ssd"` | `"hw_type": "storage_drive"` |
| `"hw_type": "hdd"` | `"hw_type": "storage_drive"` |
| `"hw_type": "cpu_heatsink"` | `"hw_type": "heatsink"` |
| `"hw_type": "mounting_kit"` | `"hw_type": "rail"` |
| `"hw_type": "blank"` | `"hw_type": "blank_filler"` |
| `"hw_type": "storage_controller"` (для device_type=hba строк) | `"hw_type": "hba"` |

**СТОП если в diff есть:** изменения `entity_type`, `state`, `matched_rule_id`, `skus`, или изменения в строках где `hw_type` не должен меняться.

### Обновление unit-тестов

В файлах `tests/test_dec_acceptance.py` и `tests/test_device_type.py` найти и исправить `assert r.hw_type == "..."`:

```python
# Переименования (менять везде):
assert r.hw_type == "ram"          # → assert r.hw_type == "memory"
assert r.hw_type == "cpu_heatsink" # → assert r.hw_type == "heatsink"
assert r.hw_type == "mounting_kit" # → assert r.hw_type == "rail"
assert r.hw_type == "blank"        # → assert r.hw_type == "blank_filler"
assert r.hw_type == "motherboard"  # → assert r.hw_type == "chassis"
assert r.hw_type == "nvme"         # → assert r.hw_type == "storage_drive"
assert r.hw_type == "ssd"          # → assert r.hw_type == "storage_drive"
assert r.hw_type == "hdd"          # → assert r.hw_type == "storage_drive"

# HBA строки (менять ТОЛЬКО если в том же тесте device_type == "hba"
# или option_name явно содержит "HBA" / "Host Bus Adapter"):
assert r.hw_type == "storage_controller"  # → assert r.hw_type == "hba"
```

> **ОСТОРОЖНО:** `assert r.hw_type == "storage_controller"` для PERC/BOSS/RAID строк — **не трогать**.

### Верификация

```powershell
pytest tests/ -v --tb=short
# ВСЕ тесты PASS
```

```powershell
git add rules/dell_rules.yaml \
        golden/dl1_expected.jsonl golden/dl2_expected.jsonl \
        golden/dl3_expected.jsonl golden/dl4_expected.jsonl \
        golden/dl5_expected.jsonl \
        tests/test_dec_acceptance.py tests/test_device_type.py
git commit -m "feat(taxonomy): update dell hw_type — fix hba split, rename ssd/hdd/nvme→storage_drive, ram→memory, etc; update dl1-dl5 golden"
```

---

## ФАЗА 3 — ОБНОВИТЬ cisco_rules.yaml + ccw golden

**Задача:** разделить `sfp_cable` на `transceiver`/`cable`, переименовать `mounting_kit`→`rail` и `blank`→`blank_filler`, исправить `accessory`.

**Разрешённые файлы:**
- `rules/cisco_rules.yaml` — секции `device_type_rules`, `hw_type_rules`
- `golden/ccw_1_expected.jsonl`, `golden/ccw_2_expected.jsonl` — только через `--update-golden`

### Контекст: текущие Cisco SKU в golden

Текущее состояние (все `sfp_cable` → `hw_type: network_adapter` — неверно):

| SKU | Что это | Должно стать |
|-----|---------|-------------|
| SFP-10G-SR-S, SFP-25G-SR-S, GLC-SX-MMD, GLC-LH-SMD, GLC-TE | Оптический трансивер | `hw_type: transceiver` |
| QSFP-100G-LR-S, QSFP-100G-SR4-S, SFP-10/25G-CSR-S | Оптический трансивер | `hw_type: transceiver` |
| QSFP-100G-CU1M | Пассивный DAC-кабель | `hw_type: cable` |
| NXK-ACC-KIT-1RU, C8500L-RM-19-1R, C9K-ACC-RBFT, C9K-ACC-SCR-4 | Rail / крепёж | `hw_type: rail` (было `mounting_kit`) |
| C9300L-STACK-BLANK | Заглушка | `hw_type: blank_filler` (было `blank`) |
| C9300L-STACK-A | Stacking module | `hw_type: accessory` (было `network_adapter`) |

### Изменение 1 — разделить sfp_cable в `device_type_rules`

Добавить новые правила **перед** существующим `DT-C-001` (порядок важен — более специфичный паттерн первым):

```yaml
device_type_rules:
  applies_to: [HW, LOGISTIC]
  rules:
    # [НОВОЕ] Пассивный медный DAC/twinax кабель — по SKU (первый, самый специфичный)
    - field: sku
      pattern: '(?i)-CU\d'            # QSFP-100G-CU1M=, SFP-xxG-CUxM=
      device_type: cable
      rule_id: DT-C-001-DAC-SKU

    # [НОВОЕ] Пассивный медный DAC/twinax или активный AOC кабель — по описанию (fallback, до оптики)
    # Покрывает случаи где SKU не содержит -CU суффикс
    - field: option_name
      pattern: '(?i)(passive\s+copper|twinax|direct.attach\s+cable|\bDAC\b|\bAOC\b)'
      device_type: cable
      rule_id: DT-C-001-DAC-OPT

    # [ИЗМЕНЕНО] Оптические трансиверы (остальные GLC/SFP/QSFP/QDD)
    - field: sku
      pattern: '^(GLC|SFP|QSFP|QDD)'
      device_type: transceiver         # было: sfp_cable
      rule_id: DT-C-001-OPT

    # Остальные правила без изменений...
    - field: sku
      pattern: '(?i)^(PWR-|NXA-PAC|C\dK?-PWR)'
      device_type: psu
      rule_id: DT-C-002
    # ...
```

### Изменение 2 — `hw_type_rules.device_type_map`

```yaml
# БЫЛО:
device_type_map:
  sfp_cable: network_adapter    # ← неверно
  psu: psu
  fan: fan

# СТАЛО:
device_type_map:
  transceiver: transceiver      # новый device_type → hw_type
  cable: cable                  # DAC cables
  sfp_cable: cable              # fallback: если sfp_cable остался где-то → cable
  psu: psu
  fan: fan
```

### Изменение 3 — `hw_type_rules.rules` (переименования)

```yaml
# HWT-C-004: mounting → rail
- field: option_name
  pattern: '(?i)rack mount|mounting|accessory kit|rubber feet|screws'
  hw_type: rail                 # было: mounting_kit
  rule_id: HWT-C-004

# HWT-C-003: blank → blank_filler
- field: option_name
  pattern: '(?i)\bblank\b|filler'
  hw_type: blank_filler         # было: blank
  rule_id: HWT-C-003

# HWT-C-006: stacking module → accessory (было network_adapter)
- field: option_name
  pattern: '(?i)stacking?\s+module'
  hw_type: accessory            # было: network_adapter
  rule_id: HWT-C-006-MOD

- field: option_name
  pattern: '(?i)stacking?\s+kit'
  hw_type: accessory            # было: network_adapter (если было)
  rule_id: HWT-C-006-KIT
```

### Обновление golden

```powershell
python main.py --input test_data/ccw_1.xlsx --vendor cisco --update-golden
python main.py --input test_data/ccw_2.xlsx --vendor cisco --update-golden
```

### Проверка golden diff (ОБЯЗАТЕЛЬНО)

```powershell
git diff golden/ccw_1_expected.jsonl golden/ccw_2_expected.jsonl
```

Допустимые изменения:

| До | После |
|----|-------|
| `"hw_type": "network_adapter"` (SFP/QSFP модули) | `"hw_type": "transceiver"` |
| `"hw_type": "network_adapter"` (QSFP-100G-CU1M DAC) | `"hw_type": "cable"` |
| `"hw_type": "mounting_kit"` | `"hw_type": "rail"` |
| `"hw_type": "blank"` | `"hw_type": "blank_filler"` |
| `"hw_type": "network_adapter"` (C9300L-STACK-A) | `"hw_type": "accessory"` |
| `"device_type": "sfp_cable"` (SFP/QSFP модули) | `"device_type": "transceiver"` |
| `"device_type": "sfp_cable"` (QSFP-100G-CU1M) | `"device_type": "cable"` |

**СТОП если:** изменился `entity_type`, `state`, `matched_rule_id`, `skus`, или что-то кроме `hw_type`/`device_type`.

### Верификация

```powershell
pytest tests/ -v --tb=short
# ВСЕ тесты PASS
```

```powershell
git add rules/cisco_rules.yaml \
        golden/ccw_1_expected.jsonl golden/ccw_2_expected.jsonl
git commit -m "feat(taxonomy): update cisco hw_type — split sfp_cable→transceiver/cable, mounting_kit→rail, blank→blank_filler, stacking→accessory; update ccw golden"
```

---

## ФАЗА 4 — ФИНАЛЬНАЯ ОЧИСТКА

**Задача:** удалить legacy значения из vocab после обновления всех golden.

**Разрешённые файлы:** `src/core/classifier.py` — только блок `HW_TYPE_VOCAB`.

```python
# Удалить секцию LEGACY — итоговый vocab (27 значений):
HW_TYPE_VOCAB = frozenset({
    # Основное изделие (BASE rows)
    "server", "switch", "storage_system", "wireless_ap",
    # Вычислительные компоненты
    "cpu", "memory", "gpu",
    # Подсистема хранения
    "storage_drive", "storage_controller", "hba", "backplane", "io_module",
    # Сеть
    "network_adapter", "transceiver", "cable",
    # Питание
    "psu",
    # Охлаждение
    "fan", "heatsink",
    # Расширение и механика
    "riser", "chassis", "rail", "blank_filler",
    # Управление
    "management", "tpm",
    # Аксессуары
    "accessory",
})
```

### Верификация

```powershell
pytest tests/ -v --tb=short
# ВСЕ тесты PASS

# Полный батч-прогон
python main.py --batch-dir test_data --vendor dell
python main.py --batch-dir test_data --vendor cisco

# Проверить run_summary.json последнего прогона:
# hw_type_counts должен содержать только новые значения
# ("memory", "storage_drive", "hba", "heatsink", "rail", "blank_filler" и т.д.)
# НЕ должно быть "ram", "ssd", "hdd", "nvme", "cpu_heatsink", "mounting_kit", "blank"
```

```powershell
git add src/core/classifier.py
git commit -m "feat(taxonomy): remove legacy hw_type values — HW_TYPE_VOCAB v2.0.0 final (27 values)"
```

---

## ФИНАЛЬНЫЙ ЧЕКЛИСТ

```powershell
# 1. Все тесты
pytest tests/ -v --tb=short
# Expected: 138+ passed, 0 failed

# 2. unknown_count = 0
pytest tests/test_unknown_threshold.py -v
# Expected: 7 passed (dl1–dl5, ccw_1, ccw_2)

# 3. Regression
pytest tests/test_regression.py tests/test_regression_cisco.py -v
# Expected: 7 passed

# 4. run_summary hw_type_counts не содержит legacy значений
python main.py --input test_data/dl1.xlsx
# В output/run-*/run_summary.json:
#   hw_type_counts должен иметь "memory", "storage_drive", "hba" и т.д.
#   НЕ должно быть "ram", "ssd", "hdd", "nvme"

# 5. Git история
git log --oneline feature/hw-type-taxonomy-v2
# 6 коммитов: Фаза 0–4 + финальная очистка
```

---

## СПРАВОЧНАЯ ТАБЛИЦА ИЗМЕНЕНИЙ

| Старый `hw_type` / поведение | Новый `hw_type` / поведение | Файлы |
|---|---|---|
| `ram` | `memory` | dell_rules.yaml, golden dl* |
| `ssd` + `hdd` + `nvme` | `storage_drive` | dell_rules.yaml, golden dl* |
| `cpu_heatsink` | `heatsink` | dell_rules.yaml, golden dl* |
| `mounting_kit` | `rail` | dell_rules.yaml + cisco_rules.yaml, golden * |
| `blank` | `blank_filler` | dell_rules.yaml + cisco_rules.yaml, golden * |
| `motherboard` | `chassis` | dell_rules.yaml |
| `hba` device_type → `storage_controller` | `hba` device_type → `hba` | dell_rules.yaml, golden dl* |
| `sfp_cable` → `network_adapter` (SFP/QSFP модули) | `transceiver` device_type → `transceiver` | cisco_rules.yaml, golden ccw* |
| `sfp_cable` → `network_adapter` (DAC кабели) | `cable` device_type → `cable` | cisco_rules.yaml, golden ccw* |
| stacking module → `network_adapter` | stacking module → `accessory` | cisco_rules.yaml, golden ccw* |
| `power_cord` device_type, `hw_type=None` | без изменений — `hw_type=None` намеренно | — |
| `enablement_kit` device_type (новый), `hw_type=None` | только device_type, `hw_type=None` намеренно | hpe_rules.yaml (будущее) |
| `applies_to: [HW]` | `applies_to: [HW, BASE]` | dell_rules.yaml, cisco_rules.yaml |

---

## ИЗВЕСТНЫЕ РИСКИ И ЗАЩИТЫ

| Риск | Защита |
|------|--------|
| Сломать PERC/BOSS → storage_controller | device_type_map Layer 1 имеет приоритет; rule_id_map для HW-008-HBA-PERC-CUS остаётся `storage_controller` |
| SAS HBA попасть в storage_controller | device_type=hba → device_type_map → `hw_type=hba` (Layer 1 отрабатывает раньше rule_id_map) |
| DAC-кабели (CU) попасть в transceiver | паттерн `-(CU\|DAC)\d` идёт первым в device_type_rules (до общего GLC/SFP/QSFP) |
| Потерять unknown_count=0 | `pytest tests/test_unknown_threshold.py` после каждой фазы |
| Случайно изменить entity_type / state / skus в golden | `git diff golden/` перед коммитом; любое изменение кроме hw_type/device_type — СТОП |
| Лишние файлы в git add | только явное перечисление файлов; `git add .` запрещено |
| **TODO после Фазы 4:** Dell optics остаются `network_adapter` | `HW-OPTICS-001: network_adapter` в rule_id_map намеренно не меняется в этом PR. Dell HPE SFP28 SR трансиверы формально должны быть `transceiver`, но это отдельный коммит: изменить `HW-OPTICS-001: network_adapter` → `HW-OPTICS-001: transceiver` + обновить golden. Не смешивать с текущим PR. |
