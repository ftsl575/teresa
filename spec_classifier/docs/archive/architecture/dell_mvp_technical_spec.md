---
**Document:** Original MVP technical architecture and specification for the Dell Specification Classifier pipeline.  
**Created:** February 2026.  
**Stage:** Pre-implementation / MVP design (Phases 0–10).  
**Status:** Reference only — implementation is complete; this document is preserved for context and future contributors. For current behavior and usage, see [TECHNICAL_OVERVIEW.md](../TECHNICAL_OVERVIEW.md) and [README.md](../../README.md).
---

# Dell Specification Classifier MVP - Полная техническая спецификация

**Версия документа**: 2.0 (финальная)  
**Дата**: 23 февраля 2026  
**Цель**: MVP-пайплайн для классификации Dell спецификаций (Excel → JSON + cleaned spec + диагностика)

---

# [UNDERSTANDING]

## Задача
Создать **детерминированный MVP-пайплайн** для классификации Dell спецификаций (Excel → JSON + cleaned spec + диагностика), с возможностью расширения на другие бренды.

## Входные данные
- 5 реальных файлов Dell: dl1.xlsx-dl5.xlsx
- Структура: header в строке 3 (dl1) или 7 (dl2-dl5)
- Ключевые столбцы: Module Name, Option Name, SKUs, Qty, Option List Price
- **ВАЖНО**: Есть строки-разделители (пустые Module Name + Option Name) — это HEADER, не сущности

## Выходные данные MVP
1. **JSON**: нормализованные строки с трейсабилити + row_kind (ITEM/HEADER)
2. **Excel**: cleaned spec (только ITEM строки нужных типов)
3. **Диагностические артефакты** (для каждого прогона в отдельной папке)
4. **Тесты**: smoke + **усиленная snapshot regression (по строкам)** + unit tests для правил

---

# [КРИТИЧЕСКИЕ НАХОДКИ ИЗ АНАЛИЗА ДАННЫХ]

## 1. Проблема с "Slot" моделью
**ВЫВОД**: В реальных Excel НЕТ явных slot-идентификаторов (bay1/bay2).  
**РЕШЕНИЕ**: Для MVP отказываемся от Slot, используем упрощённую модель:
- **HW** (Hardware) — физические компоненты
- **CONFIG** — конфигурационные параметры  
- Слоты можно вернуть позже, когда будет необходимость и данные.

## 2. **НОВОЕ**: Критическая проблема со строками-разделителями (HEADER rows)
**НАХОДКА**: В Excel есть строки, где:
- `Module Name == None AND Option Name == None AND SKUs == None`
- Это разделители/заголовки продуктов, НЕ покупаемые позиции

**ПРОБЛЕМА**: Если классифицировать их как сущности → много ложных UNKNOWN.

**РЕШЕНИЕ**: Добавить `row_kind`:
```python
class RowKind(Enum):
    ITEM = "ITEM"       # Реальная позиция (есть SKU или Option Name + Qty)
    HEADER = "HEADER"   # Разделитель/заголовок (пустые поля)
```

**Логика определения**:
```python
def detect_row_kind(row: dict) -> RowKind:
    """
    HEADER если:
    - (Module Name пустой OR None) AND
    - (Option Name пустой OR None) AND
    - (SKUs пустой OR None)
    
    Иначе: ITEM
    """
    module_empty = not (row.get("Module Name") or "").strip()
    option_empty = not (row.get("Option Name") or "").strip()
    skus_empty = not (row.get("SKUs") or "").strip()
    
    if module_empty and option_empty and skus_empty:
        return RowKind.HEADER
    return RowKind.ITEM
```

**Обработка**:
- HEADER строки **НЕ классифицируются** по entity_type
- Сохраняются в `rows_raw.json` с `row_kind=HEADER`
- **Исключаются** из cleaned spec
- Считаются в `run_summary.json` отдельно (`header_rows_count`)

## 3. **НОВОЕ**: Пробел в SOFTWARE — "Embedded Systems Management" не покрыт
**НАХОДКА**: В данных есть модуль `"Embedded Systems Management"` (26 строк!):
- "iDRAC9, Enterprise 16G"
- "Dell Connectivity Client - Disabled"
- "Dell Secure Onboarding Client Disabled"

**ПРОБЛЕМА**: Текущие SOFTWARE правила не покрывают этот модуль → уйдёт в UNKNOWN или неверный тип.

**РЕШЕНИЕ**: Расширить SOFTWARE правила:
```yaml
software_rules:
  # Embedded Systems Management — это SOFTWARE
  - field: module_name
    pattern: '^Embedded\s+Systems\s+Management$'
    entity_type: SOFTWARE
    rule_id: SOFTWARE-001
  
  # Dell Secure Onboarding
  - field: module_name
    pattern: '^Dell\s+Secure\s+Onboarding$'
    entity_type: SOFTWARE
    rule_id: SOFTWARE-002
  
  # Operating System, OS Media, iDRAC, OpenManage
  - field: module_name
    pattern: '\b(Operating\s+System|OS\s+Media|iDRAC|OpenManage)\b'
    entity_type: SOFTWARE
    rule_id: SOFTWARE-003
  
  # Option Name паттерны
  - field: option_name
    pattern: '\b(Connectivity\s+Client|Secure\s+Onboarding\s+Client|iDRAC|Windows|Linux|VMware|License)\b'
    entity_type: SOFTWARE
    rule_id: SOFTWARE-004
```

## 4. Проблема "PowerEdge" как BASE
В файлах встречается:
- `Module Name == "Base"` → явно BASE
- `Module Name == "PowerEdge R6715"` (dl5) → тоже BASE
- `Module Name == "Shipping"` + `Option Name contains "PowerEdge R660"` → это LOGISTIC, НЕ BASE

**РЕШЕНИЕ**: Правило BASE должно быть СТРОГИМ (только по `module_name`):
```yaml
base_rules:
  - field: module_name
    pattern: '^Base$'
    entity_type: BASE
    rule_id: BASE-001
    
  - field: module_name
    pattern: '^PowerEdge\s+R\d{3,4}(xs)?$'  # R660, R6715, R760xs, etc.
    entity_type: BASE
    rule_id: BASE-002
```

**НЕ матчить** BASE по `option_name` (защита от ложных срабатываний).

## 5. Опасность слова "Support"
- `"ProSupport"` → SERVICE ✅
- `"supports ONLY CPUs"` → NOTE (информация), НЕ SERVICE ❌

**РЕШЕНИЕ**: Паттерн для SERVICE должен быть **узким и брендовым**:
```regex
\b(ProSupport|Hardware\s+Support|Extended\s+Service|Warranty|Next\s+Business\s+Day|Onsite\s+Service|Deployment\s+Svcs)\b
```
**НЕ** просто `\bSupport\b`!

## 6. Chassis Configuration — это HW, а НЕ CONFIG
`"Chassis Configuration"` — описывает физический chassis (количество слотов, PERC).  
**РЕШЕНИЕ**: Это HW, несмотря на слово "Configuration" в имени (добавить явное исключение).

## 7. Обязательность NOTE типа
Найдены строки вроде:
```
"Motherboard supports ONLY CPUs below 250W..."
```
Это **НЕ сервис**, **НЕ компонент** — это ограничение/примечание.  
**РЕШЕНИЕ**: Добавить тип **NOTE** и исключать из cleaned spec (но сохранять в JSON).

---

# [РЕШЕНИЯ И АРХИТЕКТУРА]

## A) Архитектура MVP

```
spec_classifier/
├── src/
│   ├── core/
│   │   ├── parser.py          # Парсинг Excel → raw rows
│   │   ├── normalizer.py      # Нормализация полей + row_kind detection
│   │   ├── classifier.py      # Классификация по правилам (только ITEM rows)
│   │   └── state_detector.py  # Определение state (PRESENT/ABSENT/DISABLED)
│   ├── rules/
│   │   ├── rules_engine.py    # Универсальный движок правил
│   │   └── dell_rules.yaml    # Правила Dell (версионируемые)
│   ├── outputs/
│   │   ├── json_writer.py     # Генерация JSON артефактов
│   │   └── excel_writer.py    # Генерация cleaned spec
│   └── diagnostics/
│       ├── run_manager.py     # Создание папки прогона
│       └── stats_collector.py # Сбор статистики
├── tests/
│   ├── test_smoke.py          # Smoke test на dl1-dl5
│   ├── test_regression.py     # Усиленная snapshot regression (по строкам!)
│   └── test_rules_unit.py     # Unit tests для правил
├── golden/                     # Эталонные результаты для регрессии
│   ├── dl1_expected.jsonl     # ПО КАЖДОЙ СТРОКЕ (не только counts!)
│   ├── dl2_expected.jsonl
│   └── ...
├── output/                     # Результаты прогонов
│   └── run_YYYYMMDD_HHMMSS/
│       ├── input_snapshot.json
│       ├── rows_raw.json
│       ├── rows_normalized.json
│       ├── classification.jsonl
│       ├── unknown_rows.csv
│       ├── header_rows.csv     # НОВОЕ: HEADER строки отдельно
│       ├── rules_stats.json
│       ├── cleaned_spec.xlsx
│       ├── run_summary.json
│       └── run.log
├── main.py                     # CLI entry point
├── config.yaml                 # Конфигурация
├── CHANGELOG.md                # История изменений правил (ОБЯЗАТЕЛЬНО!)
└── requirements.txt
```

### Плагинная модель для других брендов (будущее)
```python
# Интерфейс
class BrandClassifier(ABC):
    @abstractmethod
    def load_rules(self) -> RuleSet: pass
    
    @abstractmethod
    def classify_row(self, row: NormalizedRow) -> ClassificationResult: pass

# Dell реализация
class DellClassifier(BrandClassifier):
    def load_rules(self):
        return load_yaml("rules/dell_rules.yaml")
```

---

## **КРИТИЧЕСКИ ВАЖНО: Процесс изменения правил**

### Обязательный workflow при изменении `dell_rules.yaml`:

1. **Изменить правила** в `rules/dell_rules.yaml`
   - Увеличить версию: `version: "1.0.0"` → `version: "1.0.1"` (patch) или `"1.1.0"` (minor)

2. **Запустить regression тесты** (они упадут):
   ```bash
   pytest tests/test_regression.py -v
   ```
   - Проверить diff — убедиться, что изменения ожидаемые

3. **Обновить golden эталоны**:
   ```bash
   python main.py --update-golden --input dl1.xlsx
   python main.py --update-golden --input dl2.xlsx
   python main.py --update-golden --input dl3.xlsx
   python main.py --update-golden --input dl4.xlsx
   python main.py --update-golden --input dl5.xlsx
   ```

4. **ОБЯЗАТЕЛЬНО: Обновить CHANGELOG.md**:
   ```markdown
   ## [1.0.1] - 2026-02-24
   
   ### Added
   - SOFTWARE-005: Добавлено правило для "VMware vSphere" (issue #123)
   
   ### Changed
   - HW-002: Расширен паттерн для Network Adapters (теперь включает Fibre Channel)
   
   ### Impact
   - dl2.xlsx: 3 строки изменились с UNKNOWN на SOFTWARE (rows 45, 67, 89)
   - dl5.xlsx: 1 строка изменилась с HW на SOFTWARE (row 23)
   ```

5. **Запустить все тесты**:
   ```bash
   pytest tests/ -v
   ```

6. **Commit изменений** (вместе!):
   ```bash
   git add rules/dell_rules.yaml golden/*.jsonl CHANGELOG.md
   git commit -m "rules: add SOFTWARE-005 for VMware vSphere (v1.0.1)"
   ```

### Формат CHANGELOG.md:

```markdown
# Changelog

All notable changes to Dell classification rules will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.1] - 2026-02-24

### Added
- SOFTWARE-005: Rule for "VMware vSphere" classification (issue #123)
- HW-006: Rule for "Fibre Channel Adapters"

### Changed
- HW-002: Extended pattern to include Fibre Channel in Network Adapters

### Fixed
- SERVICE-003: Fixed false positive matching "Support" in product descriptions

### Impact
- dl2.xlsx: 3 rows changed from UNKNOWN to SOFTWARE (rows 45, 67, 89)
- dl5.xlsx: 1 row changed from HW to SOFTWARE (row 23)
- Total UNKNOWN reduced from 5% to 2%

## [1.0.0] - 2026-02-23

### Added
- Initial release with 8 entity types (BASE, HW, CONFIG, SOFTWARE, SERVICE, LOGISTIC, NOTE, UNKNOWN)
- row_kind detection (ITEM/HEADER)
- SOFTWARE-001: Embedded Systems Management
- SOFTWARE-002: Dell Secure Onboarding
- Full test coverage with regression tests

### Known Issues
- Some GPU/FPGA rows may classify as UNKNOWN (to be addressed in v1.1.0)
```

### Версионирование правил (Semantic Versioning):

- **MAJOR** (1.0.0 → 2.0.0): Несовместимые изменения (изменение структуры YAML, удаление entity types)
- **MINOR** (1.0.0 → 1.1.0): Новые правила, расширение паттернов (обратно совместимые)
- **PATCH** (1.0.0 → 1.0.1): Исправления ошибок в правилах, уточнение паттернов

### Почему это критично:

1. **Трейсабилити**: Каждое изменение классификации документировано
2. **Регрессия**: Golden эталоны всегда актуальны
3. **Аудит**: Можно понять, почему строка изменила тип между версиями
4. **Откат**: Можно вернуться к старой версии правил + golden
5. **Коммуникация**: Команда понимает, что изменилось и почему

---

## B) Детерминированный алгоритм классификации Dell

### Минимальный набор типов строк (ФИНАЛЬНЫЙ)
```python
class RowKind(Enum):
    ITEM = "ITEM"       # Реальная позиция
    HEADER = "HEADER"   # Разделитель/заголовок продукта

class EntityType(Enum):
    BASE = "BASE"           # Платформа сервера
    HW = "HW"               # Физические компоненты и аксессуары
    CONFIG = "CONFIG"       # Режимы/профили/параметры конфигурации
    SOFTWARE = "SOFTWARE"   # ПО/лицензии/management
    SERVICE = "SERVICE"     # Гарантии/поддержка
    LOGISTIC = "LOGISTIC"   # Shipping/packaging/docs/regulatory
    NOTE = "NOTE"           # Информационные/ограничительные строки
    UNKNOWN = "UNKNOWN"     # Не классифицировано

class State(Enum):
    PRESENT = "PRESENT"     # Установлено/активно/включено
    ABSENT = "ABSENT"       # Отсутствует/не выбрано
    DISABLED = "DISABLED"   # Выключено/отключено
```

### Алгоритм (приоритетный single-pass)

```python
def process_row(raw_row: dict) -> ProcessedRow:
    """
    ШАГ 1: Определение row_kind
    ШАГ 2: Классификация (только для ITEM)
    """
    
    # ШАГ 1: ROW KIND
    row_kind = detect_row_kind(raw_row)
    
    if row_kind == RowKind.HEADER:
        # HEADER строки НЕ классифицируются
        return ProcessedRow(
            row_kind=RowKind.HEADER,
            entity_type=None,
            state=None,
            matched_rule_id="HEADER-SKIP"
        )
    
    # ШАГ 2: Нормализация (только для ITEM)
    normalized_row = normalize_row(raw_row)
    
    # ШАГ 3: Определение STATE (global priority)
    state = detect_state(normalized_row.option_name)
    
    # ШАГ 4: КЛАССИФИКАЦИЯ ТИПА (приоритетный порядок)
    """
    ПРИОРИТЕТ (первое совпадение побеждает):
    1. BASE
    2. SERVICE
    3. LOGISTIC
    4. SOFTWARE
    5. NOTE
    6. CONFIG
    7. HW
    8. UNKNOWN (fallback)
    """
    
    # BASE (highest priority)
    if is_base(normalized_row):
        return ClassificationResult(
            row_kind=RowKind.ITEM,
            entity_type=EntityType.BASE,
            state=State.PRESENT,  # BASE всегда PRESENT
            matched_rule_id="BASE-001"
        )
    
    # SERVICE
    if is_service(normalized_row):
        return ClassificationResult(
            row_kind=RowKind.ITEM,
            entity_type=EntityType.SERVICE,
            state=state,
            matched_rule_id="SERVICE-xxx"
        )
    
    # LOGISTIC
    if is_logistic(normalized_row):
        return ClassificationResult(
            row_kind=RowKind.ITEM,
            entity_type=EntityType.LOGISTIC,
            state=state,
            matched_rule_id="LOGISTIC-xxx"
        )
    
    # SOFTWARE
    if is_software(normalized_row):
        return ClassificationResult(
            row_kind=RowKind.ITEM,
            entity_type=EntityType.SOFTWARE,
            state=state,
            matched_rule_id="SOFTWARE-xxx"
        )
    
    # NOTE (informational)
    if is_note(normalized_row):
        return ClassificationResult(
            row_kind=RowKind.ITEM,
            entity_type=EntityType.NOTE,
            state=State.PRESENT,  # NOTE не бывает ABSENT
            matched_rule_id="NOTE-xxx"
        )
    
    # CONFIG
    if is_config(normalized_row):
        return ClassificationResult(
            row_kind=RowKind.ITEM,
            entity_type=EntityType.CONFIG,
            state=state,
            matched_rule_id="CONFIG-xxx"
        )
    
    # HW (default для физических компонентов)
    if is_hw(normalized_row):
        return ClassificationResult(
            row_kind=RowKind.ITEM,
            entity_type=EntityType.HW,
            state=state,
            matched_rule_id="HW-xxx"
        )
    
    # UNKNOWN (fallback)
    return ClassificationResult(
        row_kind=RowKind.ITEM,
        entity_type=EntityType.UNKNOWN,
        state=state,
        matched_rule_id="UNKNOWN-000",
        warnings=["No matching rule found"]
    )
```

### Детальные правила (YAML-файл) — **ОБНОВЛЁННАЯ ВЕРСИЯ**

```yaml
version: "1.0.0"

# ============================================================
# ROW KIND DETECTION (выполняется ПЕРВЫМ, до классификации)
# ============================================================
# Реализуется в коде (detect_row_kind), не в YAML
# HEADER: Module Name пустой AND Option Name пустой AND SKUs пустой
# ITEM: всё остальное

# ============================================================
# STATE DETECTION (global, применяется до классификации типа)
# ============================================================
state_rules:
  absent_keywords:
    - pattern: '^\s*No\s+'  # "No TPM", "No HDD"
      state: ABSENT
      rule_id: STATE-001
    
    - pattern: '\bNone\b'
      state: ABSENT
      rule_id: STATE-002
    
    - pattern: '\b(Empty|Not\s+Included|Without)\b'
      state: ABSENT
      rule_id: STATE-003
    
    - pattern: '\bDisabled\b'
      state: DISABLED
      rule_id: STATE-004

# ============================================================
# ENTITY TYPE CLASSIFICATION (только для ITEM rows)
# ============================================================

# BASE (PRIORITY 1)
base_rules:
  - field: module_name
    pattern: '^Base$'
    entity_type: BASE
    rule_id: BASE-001
    
  - field: module_name
    pattern: '^PowerEdge\s+R\d{3,4}(xs)?$'  # R660, R6715, R7625, R760xs, etc.
    entity_type: BASE
    rule_id: BASE-002

# SERVICE (PRIORITY 2)
service_rules:
  # ВАЖНО: Только узкие, брендовые паттерны (НЕ просто "Support"!)
  - field: module_name
    pattern: '\b(ProSupport|Hardware\s+(Support|Service)|Extended\s+Service|Deployment\s+Svcs)\b'
    entity_type: SERVICE
    rule_id: SERVICE-001
    
  - field: module_name
    pattern: '^Dell\s+Services'
    entity_type: SERVICE
    rule_id: SERVICE-002
    
  - field: option_name
    pattern: '\b(Warranty|ProSupport|Next\s+Business\s+Day|Onsite\s+Service)\b'
    entity_type: SERVICE
    rule_id: SERVICE-003
    
  # "Asset Tag - ProSupport" — это SERVICE
  - field: option_name
    pattern: '\bAsset\s+Tag.*ProSupport\b'
    entity_type: SERVICE
    rule_id: SERVICE-004
  
  # "NO WARRANTY UPGRADE SELECTED" — тоже SERVICE (но ABSENT)
  - field: option_name
    pattern: '\bNO\s+WARRANTY\s+UPGRADE\b'
    entity_type: SERVICE
    rule_id: SERVICE-005

# LOGISTIC (PRIORITY 3)
logistic_rules:
  - field: module_name
    pattern: '\b(Shipping|Regulatory|ECCN|Documentation|Box\s+Labels)\b'
    entity_type: LOGISTIC
    rule_id: LOGISTIC-001
    
  - field: module_name
    pattern: '^System\s+Documentation$'
    entity_type: LOGISTIC
    rule_id: LOGISTIC-002
  
  - field: module_name
    pattern: '^Shipping\s+Material$'
    entity_type: LOGISTIC
    rule_id: LOGISTIC-003

# SOFTWARE (PRIORITY 4) — **РАСШИРЕНО**
software_rules:
  # Embedded Systems Management — критически важно!
  - field: module_name
    pattern: '^Embedded\s+Systems\s+Management$'
    entity_type: SOFTWARE
    rule_id: SOFTWARE-001
  
  # Dell Secure Onboarding
  - field: module_name
    pattern: '^Dell\s+Secure\s+Onboarding$'
    entity_type: SOFTWARE
    rule_id: SOFTWARE-002
  
  # Operating System, OS Media, iDRAC, OpenManage
  - field: module_name
    pattern: '\b(Operating\s+System|OS\s+Media|iDRAC|OpenManage)\b'
    entity_type: SOFTWARE
    rule_id: SOFTWARE-003
  
  # Option Name паттерны
  - field: option_name
    pattern: '\b(Connectivity\s+Client|Secure\s+Onboarding\s+Client|iDRAC|Windows|Linux|VMware|License)\b'
    entity_type: SOFTWARE
    rule_id: SOFTWARE-004

# NOTE (PRIORITY 5)
note_rules:
  # "supports" (НЕ "Support"!)
  - field: option_name
    pattern: '\bsupports\s+(ONLY|ALL|up\s+to)\b'
    entity_type: NOTE
    rule_id: NOTE-001
    
  - field: option_name
    pattern: '\b(Motherboard|included\s+with|required\s+for)\b'
    entity_type: NOTE
    rule_id: NOTE-002

# CONFIG (PRIORITY 6)
config_rules:
  - field: module_name
    pattern: '\b(RAID\s+Configuration|BIOS.*Settings?|Memory.*Type|Advanced\s+System\s+Configurations)\b'
    entity_type: CONFIG
    rule_id: CONFIG-001
    
  # ВАЖНО: "Chassis Configuration" — это HW, не CONFIG! (исключение ниже в HW)

# HW (PRIORITY 7, default для физических компонентов)
hw_rules:
  # Chassis Configuration — явное исключение (HW, несмотря на "Configuration")
  - field: module_name
    pattern: '^Chassis\s+Configuration$'
    entity_type: HW
    rule_id: HW-001
  
  # Основные HW модули
  - field: module_name
    pattern: '\b(Processor|Additional\s+Processor|Memory\s+Capacity|Hard\s+Drives|Power\s+Supply|Fans|Bezel|Motherboard|PCIe|OCP|RAID.*Controllers?|Cables|Thermal|Riser|Network\s+(Cards?|Adapters?))\b'
    entity_type: HW
    rule_id: HW-002
  
  # Более специфичные HW компоненты
  - field: module_name
    pattern: '\b(BOSS|TPM|Trusted\s+Platform|GPU|FPGA|Acceleration|Quick\s+Sync|Password|BMC|KVM|Rack\s+Rails|Server\s+Accessories)\b'
    entity_type: HW
    rule_id: HW-003
  
  # Storage-related
  - field: module_name
    pattern: '\b(BACKPLANE|FRONT\s+STORAGE|REAR\s+STORAGE|Boot\s+Optimized\s+Storage)\b'
    entity_type: HW
    rule_id: HW-004
```

### Нормализация полей + ROW KIND

```python
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class RowKind(Enum):
    ITEM = "ITEM"
    HEADER = "HEADER"

@dataclass
class NormalizedRow:
    source_row_index: int
    row_kind: RowKind  # НОВОЕ!
    
    # Данные из Excel
    group_name: Optional[str]
    group_id: Optional[str]
    product_name: Optional[str]  # НОВОЕ: для HEADER rows
    
    module_name: str
    option_name: str
    option_id: Optional[str]
    skus: List[str]
    qty: int
    option_price: float

def detect_row_kind(raw_row: dict) -> RowKind:
    """
    Определяет тип строки: ITEM или HEADER
    
    HEADER если:
    - Module Name пустой AND
    - Option Name пустой AND
    - SKUs пустой
    
    Иначе: ITEM
    """
    module_name = (raw_row.get("Module Name") or "").strip()
    option_name = (raw_row.get("Option Name") or "").strip()
    skus = (raw_row.get("SKUs") or "").strip()
    
    # Все три поля пустые → HEADER
    if not module_name and not option_name and not skus:
        return RowKind.HEADER
    
    return RowKind.ITEM

def normalize_row(raw_row: dict) -> NormalizedRow:
    """
    Нормализует строку из Excel:
    - очистка пробелов
    - парсинг SKUs (может быть несколько через запятую)
    - преобразование Qty в int
    - преобразование цен в float
    - определение row_kind
    """
    
    # Определяем row_kind
    row_kind = detect_row_kind(raw_row)
    
    module_name = (raw_row.get("Module Name") or "").strip()
    option_name = (raw_row.get("Option Name") or "").strip()
    
    # SKUs могут быть "338-CHSG, 379-BDCO"
    skus_raw = (raw_row.get("SKUs") or "").strip()
    skus = [s.strip() for s in skus_raw.split(",") if s.strip()]
    
    qty = int(raw_row.get("Qty") or 0)
    option_price = float(raw_row.get("Option List Price") or 0.0)
    
    return NormalizedRow(
        source_row_index=raw_row["__row_index__"],
        row_kind=row_kind,
        
        group_name=raw_row.get("Group Name"),
        group_id=raw_row.get("Group ID"),
        product_name=raw_row.get("Product Name"),  # Для HEADER
        
        module_name=module_name,
        option_name=option_name,
        option_id=raw_row.get("Option ID"),
        skus=skus,
        qty=qty,
        option_price=option_price
    )
```

---

## C) Минимальная структура JSON на строку — **ОБНОВЛЁННАЯ**

```json
{
  "source_file": "dl1.xlsx",
  "source_row_index": 4,
  
  "row_kind": "ITEM",
  
  "group_id": "6489181.1.1",
  "group_name": "Group 1",
  "product_name": "PowerEdge R760 - Full Configuration - [EMEA_R760]",
  
  "module_name": "Base",
  "option_name": "PowerEdge R760 Server",
  "option_id": "GYF30OW",
  "skus": ["210-BDZY"],
  "qty": 1,
  "option_price": 4709.00,
  
  "entity_type": "BASE",
  "state": "PRESENT",
  
  "matched_rule_id": "BASE-001",
  "warnings": [],
  
  "classification_version": "1.0.0",
  "classified_at": "2026-02-23T10:15:30Z"
}
```

**Для HEADER строк**:
```json
{
  "source_file": "dl1.xlsx",
  "source_row_index": 1,
  
  "row_kind": "HEADER",
  
  "group_id": "6489181.1.1",
  "group_name": "Group 1",
  "product_name": "PowerEdge R760 - Full Configuration - [EMEA_R760]",
  
  "module_name": "",
  "option_name": "",
  "option_id": null,
  "skus": [],
  "qty": 1,
  "option_price": 24060.93,
  
  "entity_type": null,
  "state": null,
  
  "matched_rule_id": "HEADER-SKIP",
  "warnings": [],
  
  "classification_version": "1.0.0",
  "classified_at": "2026-02-23T10:15:30Z"
}
```

---

## D) Cleaned Spec Excel

### Включать в cleaned spec:
```python
INCLUDE_IN_CLEANED_SPEC = [
    EntityType.BASE,     # Всегда включаем
    EntityType.HW,       # Физические компоненты
    EntityType.SOFTWARE, # Лицензии/ПО
    EntityType.SERVICE,  # Гарантии/поддержка
]

EXCLUDE_FROM_CLEANED_SPEC = [
    RowKind.HEADER,      # НОВОЕ: Исключаем разделители
    EntityType.CONFIG,   # Конфигурационные параметры (опционально)
    EntityType.LOGISTIC, # Shipping/docs (не нужны для закупки)
    EntityType.NOTE,     # Информационные строки
    EntityType.UNKNOWN,  # Не классифицированные
]

# Дополнительно: только PRESENT (по умолчанию)
INCLUDE_ONLY_PRESENT = True  # Исключаем ABSENT/DISABLED
```

### Переключатели (config.yaml):
```yaml
cleaned_spec:
  include_types:
    - BASE
    - HW
    - SOFTWARE
    - SERVICE
  
  # Опционально добавить:
  # - CONFIG
  # - LOGISTIC
  
  include_only_present: true
  exclude_headers: true  # НОВОЕ: всегда исключать HEADER rows
  
  output_columns:
    - Module Name
    - Option Name
    - SKUs
    - Qty
    - Option List Price
    - Entity Type
    - State

rules_file: "rules/dell_rules.yaml"
```

---

## E) Разбивка на задачи для Cursor

### Фаза 0: Setup & Infrastructure (P0)
**Цель**: Подготовить структуру проекта и зависимости

**Задача 0.1**: Создать структуру проекта
- Создать папки: `src/`, `tests/`, `golden/`, `output/`
- Создать `requirements.txt`:
  ```
  openpyxl>=3.1.0
  pandas>=2.0.0
  pyyaml>=6.0
  pytest>=7.0.0
  ```
- Создать `README.md` с кратким описанием
- **DoD**: Структура создана, `pip install -r requirements.txt` работает
- **Тест**: `ls -R` показывает правильные папки
- **Effort**: S
- **Priority**: P0

---

### Фаза 1: Parsing & Normalization (P0)
**Цель**: Научиться парсить Excel → normalized rows + row_kind

**Задача 1.1**: Реализовать `parser.py`
- Функция `find_header_row(filepath) -> int`
  - Ищет строку с "Module Name"
  - Возвращает индекс или None
- Функция `parse_excel(filepath) -> List[dict]`
  - Читает Excel с правильным header
  - **ВАЖНО**: Удаляет колонку "Unnamed: 0" (это индекс, не данные)
  - **КРИТИЧНО**: Добавляет `__row_index__` = **номер строки в Excel (sheet row number), начиная с 1**, а НЕ pandas index
    - Формула: `__row_index__ = pandas_idx + header_row_index + 2`
  - Возвращает список raw rows (dict)
- **DoD**: 
  - Парсит dl1.xlsx (строка 3) и dl2.xlsx (строка 7) корректно
  - Возвращает правильное количество строк (включая HEADER)
  - `__row_index__` соответствует номеру строки в Excel (например, первая data строка = 4 для dl1.xlsx)
- **Тест**: `python -m src.core.parser /path/to/dl1.xlsx` выводит количество строк
- **Effort**: M
- **Priority**: P0

**Задача 1.2**: Реализовать `normalizer.py` — **ОБНОВЛЕНО**
- Enum `RowKind` (ITEM/HEADER)
- Функция `detect_row_kind(raw_row: dict) -> RowKind`:
  - HEADER если: Module Name пустой AND Option Name пустой AND SKUs пустой
  - Иначе: ITEM
- Класс `NormalizedRow` (dataclass) — с полем `row_kind`
- Функция `normalize_row(raw_row: dict) -> NormalizedRow`:
  - Определяет row_kind
  - Очистка пробелов в module_name, option_name
  - Парсинг SKUs (split by comma)
  - Преобразование Qty → int, Option List Price → float
- **DoD**: 
  - HEADER строки корректно определяются (row_kind=HEADER)
  - ITEM строки нормализуются правильно
  - SKUs "338-CHSG, 379-BDCO" → ["338-CHSG", "379-BDCO"]
- **Тест**: Unit test на 10 примеров (включая 2-3 HEADER)
- **Effort**: M
- **Priority**: P0

---

### Фаза 2: Rules Engine & State Detection (P0)
**Цель**: Детерминированные правила классификации

**Задача 2.1**: Реализовать `state_detector.py`
- Enum `State` (PRESENT/ABSENT/DISABLED)
- Функция `detect_state(option_name: str, state_rules: List[dict]) -> State`:
  - Проверяет паттерны из YAML (`state_rules`)
  - Возвращает PRESENT/ABSENT/DISABLED
  - По умолчанию: PRESENT
- **DoD**: 
  - "No TPM" → ABSENT
  - "Disabled" → DISABLED
  - "Intel Xeon" → PRESENT (default)
- **Тест**: Unit test на 10 примеров
- **Effort**: S
- **Priority**: P0

**Задача 2.2**: Создать `rules/dell_rules.yaml` — **ОБНОВЛЕНО**
- Скопировать **ОБНОВЛЁННУЮ** структуру YAML из раздела B выше
- Версия 1.0.0
- **ВАЖНО**: Включить расширенные SOFTWARE правила (Embedded Systems Management, Dell Secure Onboarding)
- **DoD**: YAML корректный (можно загрузить через `yaml.safe_load`)
- **Тест**: `yamllint rules/dell_rules.yaml` (или просто `yaml.safe_load`)
- **Effort**: S
- **Priority**: P0

**Задача 2.3**: Реализовать `rules_engine.py`
- Класс `RuleSet` (загрузка из YAML)
- Функция `match_rule(row: NormalizedRow, rules: List[Rule]) -> Optional[Rule]`:
  - Проверяет regex-паттерны по приоритету
  - Возвращает первое совпадение (или None)
- **DoD**: 
  - Загружает `dell_rules.yaml`
  - Корректно матчит паттерны
- **Тест**: Unit test на 5 правил
- **Effort**: M
- **Priority**: P0

**Задача 2.4**: Реализовать `classifier.py` — **ОБНОВЛЕНО**
- Enum `EntityType` (BASE, HW, CONFIG, SOFTWARE, SERVICE, LOGISTIC, NOTE, UNKNOWN)
- Dataclass `ClassificationResult` (с полем `row_kind`)
- Функция `classify_row(row: NormalizedRow, ruleset: RuleSet) -> ClassificationResult`:
  - **ВАЖНО**: Сначала проверяет `row.row_kind`
  - Если HEADER → возвращает `entity_type=None, state=None, matched_rule_id="HEADER-SKIP"`
  - Если ITEM → реализует приоритетный алгоритм из раздела B
  - Возвращает `entity_type`, `state`, `matched_rule_id`, `warnings`
- **DoD**: 
  - HEADER строки НЕ классифицируются (entity_type=None)
  - ITEM строки классифицируются корректно (BASE, SERVICE, SOFTWARE с Embedded Systems Management, HW)
  - Обрабатывает UNKNOWN (fallback)
- **Тест**: Unit test на 20 реальных строк из dl1 (включая HEADER)
- **Effort**: M
- **Priority**: P0

---

### Фаза 3: Diagnostic Artifacts (P0)
**Цель**: Сохранять артефакты для каждого прогона

**Задача 3.1**: Реализовать `diagnostics/run_manager.py`
- Функция `create_run_folder(base_dir: str, input_filename: str) -> Path`:
  - Создаёт `output/run_YYYYMMDD_HHMMSS/`
  - Возвращает путь к папке прогона
- **DoD**: Создаёт уникальную папку с timestamp
- **Тест**: Вызвать 2 раза подряд → 2 разные папки
- **Effort**: S
- **Priority**: P0

**Задача 3.2**: Реализовать сохранение JSON артефактов — **ОБНОВЛЕНО**
- `save_rows_raw(rows, run_folder)` → `rows_raw.json`
- `save_rows_normalized(rows, run_folder)` → `rows_normalized.json` (включая row_kind)
- `save_classification(results, run_folder)` → `classification.jsonl` (JSON Lines)
- `save_unknown_rows(rows, run_folder)` → `unknown_rows.csv`
- **НОВОЕ**: `save_header_rows(rows, run_folder)` → `header_rows.csv` (отдельно HEADER строки)
- **DoD**: 
  - Все файлы сохраняются корректно
  - JSON валидный, CSV читается в Excel
  - HEADER строки в отдельном файле
- **Тест**: Прогон на dl1.xlsx → проверить все файлы созданы
- **Effort**: M
- **Priority**: P0

**Задача 3.3**: Реализовать `stats_collector.py` — **ОБНОВЛЕНО**
- Функция `collect_stats(classification_results) -> dict`:
  - Считает: total_rows, **header_rows_count**, **item_rows_count**
  - Считает: counts по entity_type (только ITEM), counts по state
  - Считает: unknown_count, rules_stats (rule_id → count)
- Функция `save_run_summary(stats, run_folder)`:
  - Сохраняет `run_summary.json`
- **DoD**: 
  - `run_summary.json` содержит всю статистику (включая header_rows_count)
  - Легко читается человеком
- **Тест**: Прогон на dl2.xlsx → проверить корректность counts
- **Effort**: M
- **Priority**: P0

**Задача 3.4**: Реализовать `save_rules_stats()`
- Функция `save_rules_stats(classification_results, run_folder)`:
  - Группирует по `matched_rule_id`
  - **Исключает** "HEADER-SKIP" из статистики (или считает отдельно)
  - Сохраняет `rules_stats.json`: `{"BASE-001": 8, "HW-002": 45, ...}`
- **DoD**: JSON корректный, все правила учтены
- **Тест**: Прогон на dl3.xlsx → проверить совпадение с ручным подсчётом
- **Effort**: S
- **Priority**: P0

---

### Фаза 4: Cleaned Spec Generation (P0)
**Цель**: Генерировать Excel cleaned spec

**Задача 4.1**: Реализовать `outputs/excel_writer.py` — **ОБНОВЛЕНО**
- Функция `generate_cleaned_spec(classification_results, config, run_folder)`:
  - **Фильтрует**: 
    - `row_kind == ITEM` (исключаем HEADER)
    - `entity_type` in `include_types`
    - `include_only_present=true` → только PRESENT
  - Создаёт DataFrame с колонками: Module Name, Option Name, SKUs (join через ", "), Qty, Option List Price, Entity Type, State
  - Сохраняет в `cleaned_spec.xlsx`
- **DoD**: 
  - Excel открывается корректно
  - Только ITEM строки нужных типов (BASE, HW, SOFTWARE, SERVICE, PRESENT)
  - HEADER строки полностью исключены
- **Тест**: Прогон на dl1.xlsx → открыть Excel, проверить содержимое (должно быть ~30-40 строк, не ~54)
- **Effort**: M
- **Priority**: P0

---

### Фаза 5: Main Pipeline & CLI (P0)
**Цель**: Объединить всё в CLI

**Задача 5.1**: Реализовать `main.py`
- Аргументы CLI: `--input dl1.xlsx`, `--config config.yaml`, `--output-dir output/`
- Pipeline:
  1. Parse Excel
  2. Normalize rows (с определением row_kind)
  3. Classify rows (HEADER → skip, ITEM → classify)
  4. Create run folder
  5. Save all artifacts (JSON, CSV, Excel, stats) включая header_rows.csv
  6. Print summary (включая header_rows_count)
- **DoD**: 
  - `python main.py --input dl1.xlsx` работает end-to-end
  - Все артефакты созданы в `output/run_*/`
  - Summary показывает: total_rows, header_rows, item_rows, entity_type_counts, unknown_count
- **Тест**: Прогон на всех dl1-dl5.xlsx
- **Effort**: M
- **Priority**: P0

**Задача 5.2**: Добавить логирование
- Настроить `logging` в `main.py`
- Сохранять `run.log` в папку прогона
- Уровни: INFO для основных шагов, DEBUG для деталей
- **Логировать**: 
  - Количество HEADER rows (skipped)
  - Количество ITEM rows (classified)
  - По каждой UNKNOWN строке — почему не сматчилось
- **DoD**: 
  - `run.log` содержит понятный trace
  - Можно отследить, почему строка получила определённый тип
- **Тест**: Прогон на dl1.xlsx → проверить `run.log`
- **Effort**: S
- **Priority**: P0

---

### Фаза 6: Tests (P0) — **УСИЛЕННАЯ РЕГРЕССИЯ**
**Цель**: Автоматизированные тесты для регрессии

**Задача 6.1**: Реализовать `tests/test_smoke.py`
- Тест `test_smoke_all_files()`:
  - Прогон на dl1-dl5.xlsx
  - Проверяет, что все артефакты созданы (JSON, CSV, Excel, stats, **header_rows.csv**)
  - Проверяет, что нет exception
- **DoD**: `pytest tests/test_smoke.py` проходит
- **Тест**: Просто запустить pytest
- **Effort**: S
- **Priority**: P0

**Задача 6.2**: Генерация эталонов для регрессии — **УСИЛЕННАЯ ВЕРСИЯ**
- Команда: `python main.py --input dl1.xlsx --save-golden`
  - Прогон на dl1-dl5.xlsx
  - Сохраняет в `golden/dl1_expected.jsonl`, `golden/dl2_expected.jsonl`, ...
  - **ВАЖНО**: Формат эталона — **JSON Lines (по каждой строке)**:
    ```jsonl
    {"source_row_index": 1, "row_kind": "HEADER", "entity_type": null, "state": null, "matched_rule_id": "HEADER-SKIP", "skus": []}
    {"source_row_index": 4, "row_kind": "ITEM", "entity_type": "BASE", "state": "PRESENT", "matched_rule_id": "BASE-001", "skus": ["210-BDZY"]}
    {"source_row_index": 5, "row_kind": "ITEM", "entity_type": "HW", "state": "ABSENT", "matched_rule_id": "HW-003", "skus": ["461-AADZ"]}
    ...
    ```
  - Каждая строка содержит: `source_row_index`, `row_kind`, `entity_type`, `state`, `matched_rule_id`, `skus` (для идентификации)
- **DoD**: Эталоны созданы в `golden/` (по одному .jsonl на файл)
- **Тест**: Проверить вручную `golden/dl1_expected.jsonl`
- **Effort**: M
- **Priority**: P0

**Задача 6.3**: Реализовать `tests/test_regression.py` — **УСИЛЕННАЯ ВЕРСИЯ**
- Тест `test_regression_dl1()`, `test_regression_dl2()`, ... (для каждого файла)
  - Прогон на dlX.xlsx
  - Загрузка `golden/dlX_expected.jsonl`
  - **ПОСТРОЧНОЕ СРАВНЕНИЕ**:
    - Для каждой строки сравниваем: `entity_type`, `state`, `matched_rule_id`
    - Если хотя бы одна строка отличается → FAIL
    - Вывод diff (какие строки изменились, старое vs новое значение)
  - **Дополнительно**: Сравнение агрегатов (entity_type_counts, unknown_count) как санити-чек
- **DoD**: 
  - `pytest tests/test_regression.py` проходит на эталонных данных
  - При изменении правил (даже если counts совпадают) — тест падает
  - Diff показывает конкретные строки, которые изменились
- **Пример ошибки**:
  ```
  FAILED: Row 15 changed
    Expected: entity_type=SOFTWARE, matched_rule_id=SOFTWARE-001
    Got:      entity_type=UNKNOWN, matched_rule_id=UNKNOWN-000
  ```
- **Тест**: 
  1. Запустить на эталонных данных → OK
  2. Изменить правило (например, удалить SOFTWARE-001) → тест должен упасть
  3. Проверить, что diff показывает конкретные строки
- **Effort**: L (сложнее, чем простое сравнение counts)
- **Priority**: P0

**Задача 6.4**: Добавить команду обновления эталонов
- `python main.py --update-golden`
  - Перезаписывает `golden/*.jsonl` новыми результатами
  - Требует подтверждения (y/n)
- **DoD**: Можно обновить эталоны после сознательного изменения правил
- **Effort**: S
- **Priority**: P1 (не критично для MVP, но очень полезно)

**Задача 6.5**: Реализовать `tests/test_rules_unit.py` — **ОБНОВЛЕНО**
- Unit tests для отдельных правил:
  ```python
  def test_base_detection():
      row = NormalizedRow(row_kind=RowKind.ITEM, module_name="Base", ...)
      result = classify_row(row, ruleset)
      assert result.entity_type == EntityType.BASE
      assert result.matched_rule_id == "BASE-001"
  
  def test_header_skip():
      row = NormalizedRow(row_kind=RowKind.HEADER, module_name="", option_name="", skus=[], ...)
      result = classify_row(row, ruleset)
      assert result.entity_type is None
      assert result.matched_rule_id == "HEADER-SKIP"
  
  def test_software_embedded_systems():
      row = NormalizedRow(row_kind=RowKind.ITEM, module_name="Embedded Systems Management", ...)
      result = classify_row(row, ruleset)
      assert result.entity_type == EntityType.SOFTWARE
      assert result.matched_rule_id == "SOFTWARE-001"
  
  def test_software_dell_secure_onboarding():
      row = NormalizedRow(row_kind=RowKind.ITEM, module_name="Dell Secure Onboarding", ...)
      result = classify_row(row, ruleset)
      assert result.entity_type == EntityType.SOFTWARE
      assert result.matched_rule_id == "SOFTWARE-002"
  
  def test_service_prosupport():
      row = NormalizedRow(row_kind=RowKind.ITEM, module_name="Dell Services:Extended Service", ...)
      result = classify_row(row, ruleset)
      assert result.entity_type == EntityType.SERVICE
  
  def test_note_supports():
      row = NormalizedRow(row_kind=RowKind.ITEM, option_name="Motherboard supports ONLY CPUs below 250W", ...)
      result = classify_row(row, ruleset)
      assert result.entity_type == EntityType.NOTE
  
  def test_hw_chassis_config():
      row = NormalizedRow(row_kind=RowKind.ITEM, module_name="Chassis Configuration", ...)
      result = classify_row(row, ruleset)
      assert result.entity_type == EntityType.HW  # НЕ CONFIG!
      assert result.matched_rule_id == "HW-001"
  ```
- **DoD**: 
  - Минимум 20 unit tests (включая HEADER, новые SOFTWARE правила, Chassis Configuration)
  - Все проходят
- **Тест**: `pytest tests/test_rules_unit.py`
- **Effort**: M
- **Priority**: P0

---

### Фаза 7: Documentation & Refinement (P1)
**Цель**: Документация и полировка

**Задача 7.1**: Написать `README.md`
- Как установить
- Как запустить
- Примеры использования
- Описание артефактов (включая header_rows.csv)
- Описание row_kind (ITEM vs HEADER)
- **DoD**: README полный и понятный
- **Effort**: S
- **Priority**: P1

**Задача 7.2**: Добавить `config.yaml` — **ОБНОВЛЕНО**
- Переключатели для cleaned spec (include_types, include_only_present, **exclude_headers**)
- Путь к rules файлу
- **DoD**: Можно переключать настройки без изменения кода
- **Effort**: S
- **Priority**: P1

---

## РИСКИ — **ОБНОВЛЕНО**

| Риск | Вероятность | Влияние | Митигация |
|------|-------------|---------|-----------|
| Правила не покрывают все случаи | Высокая | Средняя | UNKNOWN + warnings → итеративное расширение правил |
| HEADER строки ошибочно классифицируются | **Низкая** | **Низкая** | row_kind detection (до классификации) |
| "Embedded Systems Management" не классифицируется | **Устранена** | Высокая | Явное правило SOFTWARE-001 |
| Разная структура заголовков в новых файлах | Средняя | Низкая | `find_header_row()` автоопределение |
| Паттерны конфликтуют (например, "Support" vs "supports") | Средняя | Высокая | Приоритетный порядок + узкие SERVICE правила + unit tests |
| Пользователь хочет изменить правила | Высокая | Низкая | YAML + версионирование правил |
| Excel файлы повреждены/нестандартные | Низкая | Средняя | Try-catch + понятное сообщение об ошибке |
| Regression тест не ловит поломки | **Устранена** | Высокая | Построчное сравнение (не только counts) |

---

## OUT OF SCOPE (не делаем в MVP)

- ❌ База данных (только файлы)
- ❌ Другие бренды кроме Dell (но архитектура готова для расширения)
- ❌ **Slot-модель** (явно OUT OF SCOPE, упрощено до HW/CONFIG)
- ❌ Web-интерфейс
- ❌ Автоматическое обновление правил через ML
- ❌ Интеграция с ERP/CRM

---

# [PROMPT_PACK_FOR_OTHER_CODER] — **ОБНОВЛЁННЫЕ ПРОМПТЫ**

## Prompt 1 — Setup Project Structure

**Context**: Создаём MVP-пайплайн для классификации Dell спецификаций (Excel → JSON + cleaned spec + диагностика).

**Task**: 
1. Создай структуру проекта:
   ```
   spec_classifier/
   ├── src/
   │   ├── core/
   │   ├── rules/
   │   ├── outputs/
   │   └── diagnostics/
   ├── tests/
   ├── golden/
   ├── output/
   ├── main.py
   ├── config.yaml
   ├── CHANGELOG.md
   ├── requirements.txt
   └── README.md
   ```
2. Создай `requirements.txt` с зависимостями:
   - openpyxl>=3.1.0
   - pandas>=2.0.0
   - pyyaml>=6.0
   - pytest>=7.0.0

3. **ВАЖНО**: Создай начальный `CHANGELOG.md`:
   ```markdown
   # Changelog
   
   All notable changes to Dell classification rules will be documented in this file.
   
   The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
   and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
   
   ## [Unreleased]
   
   ## [1.0.0] - 2026-02-23
   
   ### Added
   - Initial release with 8 entity types (BASE, HW, CONFIG, SOFTWARE, SERVICE, LOGISTIC, NOTE, UNKNOWN)
   - row_kind detection (ITEM/HEADER)
   - SOFTWARE-001: Embedded Systems Management
   - SOFTWARE-002: Dell Secure Onboarding
   - Full test coverage with regression tests
   ```

**Constraints**:
- НЕ добавляй никаких других зависимостей
- Все `__init__.py` файлы пустые
- README пока просто placeholder (1-2 строки)
- **CHANGELOG.md должен быть создан с начальной записью версии 1.0.0**

**Acceptance Criteria**:
- Структура папок создана
- `pip install -r requirements.txt` работает без ошибок
- `ls -R` показывает правильную структуру
- **CHANGELOG.md существует и содержит версию 1.0.0**

**Commands to verify**:
```bash
ls -R spec_classifier/
pip install -r spec_classifier/requirements.txt
cat spec_classifier/CHANGELOG.md  # Должен показать версию 1.0.0
```

---

## Prompt 2 — Implement Excel Parser

**Context**: Нужно парсить Dell Excel файлы. Заголовки могут быть в строке 3 или 7 (автоопределение).

**Task**: Реализуй `src/core/parser.py`:
1. Функция `find_header_row(filepath: str) -> Optional[int]`:
   - Ищет строку с "Module Name"
   - Возвращает индекс строки (pandas index, начиная с 0) или None
2. Функция `parse_excel(filepath: str) -> List[dict]`:
   - Читает Excel с header=найденный_индекс
   - **ВАЖНО**: Удаляет колонку "Unnamed: 0" (это индекс, не данные)
   - **НЕ** убирает пустые строки (они могут быть HEADER)
   - **КРИТИЧНО**: Добавляет `__row_index__` = **номер строки в Excel (sheet row number), начиная с 1**, а НЕ pandas index
     - Формула: `__row_index__ = pandas_idx + header_row_index + 2`
   - Возвращает список dict

**Constraints**:
- Используй `pandas.read_excel()` и `openpyxl`
- НЕ меняй названия столбцов
- Обрабатывай ошибки (FileNotFoundError, InvalidFileException)
- **`__row_index__` должен соответствовать номеру строки в Excel** (для стабильности golden/regression)

**Acceptance Criteria**:
- Парсит `/path/to/dl1.xlsx` → ~54 rows (включая HEADER строки)
- Парсит `/path/to/dl2.xlsx` → ~374 rows
- Каждая строка имеет `__row_index__` = номер строки в Excel (например, первая data строка после header = 4 для dl1.xlsx)
- Колонка "Unnamed: 0" удалена

**Commands to verify**:
```bash
python -c "from src.core.parser import parse_excel; rows = parse_excel('dl1.xlsx'); print(f'Rows: {len(rows)}'); print(f'First row __row_index__: {rows[0][\"__row_index__\"]}'); print('Columns:', list(rows[0].keys()))"
# Expected output: First row __row_index__: 4 (for dl1.xlsx)
```

---

## Prompt 3 — Implement Row Normalizer + Row Kind Detection

**Context**: Нужно нормализовать сырые строки из Excel + определять row_kind (ITEM/HEADER).

**Task**: Реализуй `src/core/normalizer.py`:

1. **Enum `RowKind`**:
   ```python
   class RowKind(Enum):
       ITEM = "ITEM"       # Реальная позиция
       HEADER = "HEADER"   # Разделитель/заголовок
   ```

2. **Функция `detect_row_kind(raw_row: dict) -> RowKind`**:
   - HEADER если: `Module Name` пустой AND `Option Name` пустой AND `SKUs` пустой
   - Иначе: ITEM
   - Пустой = `None` или `""` (после `.strip()`)

3. **Dataclass `NormalizedRow`**:
   ```python
   @dataclass
   class NormalizedRow:
       source_row_index: int
       row_kind: RowKind          # НОВОЕ!
       
       group_name: Optional[str]
       group_id: Optional[str]
       product_name: Optional[str] # Для HEADER rows
       
       module_name: str
       option_name: str
       option_id: Optional[str]
       skus: List[str]
       qty: int
       option_price: float
   ```

4. **Функция `normalize_row(raw_row: dict) -> NormalizedRow`**:
   - Сначала вызывает `detect_row_kind()`
   - Очистка `.strip()` для строк
   - Парсинг SKUs: `split(',')` → strip каждого → список
   - `Qty` → int (default 0)
   - `Option List Price` → float (default 0.0)

**Constraints**:
- НЕ добавляй новые поля в NormalizedRow (кроме row_kind)
- Обрабатывай None/NaN корректно (default значения)

**Acceptance Criteria**:
- HEADER строка: `module_name=""`, `option_name=""`, `skus=[]` → `row_kind=HEADER`
- ITEM строка: `module_name="Base"`, `option_name="PowerEdge R760"`, `skus=["210-BDZY"]` → `row_kind=ITEM`
- SKUs "338-CHSG, 379-BDCO" → ["338-CHSG", "379-BDCO"]
- Qty "1" → 1 (int)

**Commands to verify**:
```bash
pytest tests/test_normalizer.py -v
```

---

## Prompt 4 — Implement State Detector & YAML Rules

**Context**: Нужно определять state строки (PRESENT/ABSENT/DISABLED) по Option Name.

**Task 1**: Создай `rules/dell_rules.yaml`:
- Скопируй **ОБНОВЛЁННУЮ** структуру YAML из раздела [РЕШЕНИЯ] выше
- Версия 1.0.0
- **КРИТИЧЕСКИ ВАЖНО**: Включить расширенные SOFTWARE правила:
  - SOFTWARE-001: `Embedded Systems Management`
  - SOFTWARE-002: `Dell Secure Onboarding`
  - SOFTWARE-004: паттерн с `Connectivity Client`

**Task 2**: Реализуй `src/core/state_detector.py`:
1. Enum `State(Enum)`: PRESENT, ABSENT, DISABLED
2. Функция `detect_state(option_name: str, state_rules: List[dict]) -> State`:
   - Проверяет regex-паттерны из `state_rules`
   - Возвращает первое совпадение (ABSENT/DISABLED)
   - Default: PRESENT

**Constraints**:
- Используй `re.search(pattern, option_name, re.IGNORECASE)`
- НЕ хардкоди паттерны в коде (только из YAML)

**Acceptance Criteria**:
- "No Trusted Platform Module" → ABSENT
- "Dell Connectivity Client - Disabled" → DISABLED
- "Intel Xeon Silver 4410Y" → PRESENT (default)
- YAML содержит SOFTWARE-001 и SOFTWARE-002

**Commands to verify**:
```bash
pytest tests/test_state_detector.py -v
python -c "import yaml; rules = yaml.safe_load(open('rules/dell_rules.yaml')); print('SOFTWARE rules:', len(rules['software_rules']))"
```

---

## Prompt 5 — Implement Rules Engine & Classifier

**Context**: Нужен движок правил для классификации строк по типам (BASE/HW/SERVICE/...).

**Task 1**: Реализуй `src/rules/rules_engine.py`:
1. Класс `RuleSet`:
   - Загрузка из YAML (`yaml.safe_load`)
   - Хранит правила по категориям (base_rules, service_rules, software_rules, ...)
2. Функция `match_rule(row: NormalizedRow, rules: List[dict]) -> Optional[dict]`:
   - Проверяет `field` (module_name или option_name)
   - Матчит `pattern` (regex)
   - Возвращает первое совпадение или None

**Task 2**: Реализуй `src/core/classifier.py`:
1. Enum `EntityType`: BASE, HW, CONFIG, SOFTWARE, SERVICE, LOGISTIC, NOTE, UNKNOWN
2. Dataclass `ClassificationResult`:
   ```python
   @dataclass
   class ClassificationResult:
       row_kind: RowKind
       entity_type: Optional[EntityType]  # None для HEADER
       state: Optional[State]             # None для HEADER
       matched_rule_id: str
       warnings: List[str] = field(default_factory=list)
   ```
3. Функция `classify_row(row: NormalizedRow, ruleset: RuleSet) -> ClassificationResult`:
   - **ШАГ 1**: Проверяет `row.row_kind`
   - Если `HEADER` → возвращает `entity_type=None, state=None, matched_rule_id="HEADER-SKIP"`
   - Если `ITEM` → реализует приоритетный алгоритм (BASE → SERVICE → LOGISTIC → SOFTWARE → NOTE → CONFIG → HW → UNKNOWN)

**Constraints**:
- НЕ меняй порядок приоритетов
- UNKNOWN — это fallback (всегда есть)
- Первое совпадение побеждает (no overwriting)
- HEADER строки обрабатываются **ДО** всех остальных правил

**Acceptance Criteria**:
- `row_kind=HEADER` → `entity_type=None, matched_rule_id="HEADER-SKIP"`
- `row_kind=ITEM, module_name="Base"` → `entity_type=BASE`
- `row_kind=ITEM, module_name="Embedded Systems Management"` → `entity_type=SOFTWARE, matched_rule_id=SOFTWARE-001`
- `row_kind=ITEM, module_name="Dell Secure Onboarding"` → `entity_type=SOFTWARE, matched_rule_id=SOFTWARE-002`
- `row_kind=ITEM, module_name="Processor"` → `entity_type=HW`
- Нет совпадений → `entity_type=UNKNOWN`

**Commands to verify**:
```bash
pytest tests/test_rules_unit.py -v
```

---

## Prompt 6 — Implement Diagnostic Artifacts

**Context**: Каждый прогон должен создавать папку с артефактами (JSON, CSV, stats).

**Task 1**: Реализуй `src/diagnostics/run_manager.py`:
- Функция `create_run_folder(base_dir: str, input_filename: str) -> Path`:
  - Создаёт `output/run_YYYYMMDD_HHMMSS/`
  - Возвращает Path объект

**Task 2**: Реализуй сохранение артефактов в `src/outputs/json_writer.py`:
- `save_rows_raw(rows: List[dict], run_folder: Path)` → `rows_raw.json`
- `save_rows_normalized(rows: List[NormalizedRow], run_folder: Path)` → `rows_normalized.json` (с row_kind!)
- `save_classification(results: List[ClassificationResult], run_folder: Path)` → `classification.jsonl` (JSON Lines)
- `save_unknown_rows(rows: List[...], run_folder: Path)` → `unknown_rows.csv` (только ITEM + UNKNOWN)
- **НОВОЕ**: `save_header_rows(rows: List[NormalizedRow], run_folder: Path)` → `header_rows.csv` (только HEADER строки)

**Task 3**: Реализуй `src/diagnostics/stats_collector.py`:
- Функция `collect_stats(classification_results: List[ClassificationResult]) -> dict`:
  ```python
  {
    "total_rows": 54,
    "header_rows_count": 3,      # НОВОЕ!
    "item_rows_count": 51,        # НОВОЕ!
    "entity_type_counts": {"BASE": 1, "HW": 30, ...},  # только ITEM
    "state_counts": {"PRESENT": 40, "ABSENT": 11},     # только ITEM
    "unknown_count": 2,
    "rules_stats": {"BASE-001": 1, "HW-002": 15, "HEADER-SKIP": 3, ...}
  }
  ```
- Функция `save_run_summary(stats: dict, run_folder: Path)` → `run_summary.json`

**Constraints**:
- Используй `json.dump()` с `indent=2`
- JSON Lines: одна строка = один JSON объект
- CSV должен открываться в Excel
- HEADER строки считаются отдельно (header_rows_count)

**Acceptance Criteria**:
- Прогон на dl1.xlsx создаёт папку `output/run_YYYYMMDD_HHMMSS/`
- Все файлы созданы: `rows_raw.json`, `rows_normalized.json`, `classification.jsonl`, `unknown_rows.csv`, **`header_rows.csv`**, `run_summary.json`
- JSON валидный (`json.load()` без ошибок)
- `run_summary.json` содержит `header_rows_count` и `item_rows_count`

**Commands to verify**:
```bash
python main.py --input dl1.xlsx
ls output/run_*/
cat output/run_*/run_summary.json | jq '.header_rows_count'
```

---

## Prompt 7 — Implement Cleaned Spec Excel Generator

**Context**: Нужно создавать cleaned spec Excel: только ITEM строки нужных типов (BASE, HW, SOFTWARE, SERVICE) + только PRESENT.

**Task**: Реализуй `src/outputs/excel_writer.py`:
1. Функция `generate_cleaned_spec(classification_results, original_rows, config, run_folder)`:
   - **Фильтрует**: 
     - `row_kind == ITEM` (исключаем HEADER)
     - `entity_type` in `include_types` (из config.yaml)
     - `include_only_present=true` → только PRESENT
   - Создаёт DataFrame с колонками:
     - Module Name
     - Option Name
     - SKUs (join через ", ")
     - Qty
     - Option List Price
     - Entity Type
     - State
   - Сохраняет в `cleaned_spec.xlsx` через `pandas.to_excel()`

**Constraints**:
- По умолчанию include_types = [BASE, HW, SOFTWARE, SERVICE]
- Исключаем: HEADER (row_kind), CONFIG, LOGISTIC, NOTE, UNKNOWN
- Только PRESENT (ABSENT/DISABLED исключаем)

**Acceptance Criteria**:
- Excel открывается корректно
- Только ITEM строки нужных типов (BASE, HW, SOFTWARE, SERVICE, PRESENT)
- HEADER строки полностью исключены
- Колонка "Entity Type" заполнена корректно
- Для dl1.xlsx: должно быть ~30-40 строк (не ~54, потому что исключены HEADER, LOGISTIC, NOTE, ABSENT)

**Commands to verify**:
```bash
python main.py --input dl1.xlsx
python -c "import pandas as pd; df = pd.read_excel('output/run_*/cleaned_spec.xlsx'); print(f'Rows: {len(df)}'); print(df['Entity Type'].value_counts())"
```

---

## Prompt 8 — Implement Main Pipeline & CLI

**Context**: Нужен CLI для запуска всего пайплайна end-to-end.

**Task**: Реализуй `main.py`:
1. CLI аргументы (используй `argparse`):
   - `--input <filepath>` — путь к Excel файлу
   - `--config <filepath>` — путь к config.yaml (default: `config.yaml`)
   - `--output-dir <path>` — базовая папка для output (default: `output/`)
   - `--save-golden` — флаг для сохранения эталонов (для regression)
2. Pipeline:
   ```python
   # 1. Parse Excel
   rows_raw = parse_excel(args.input)
   
   # 2. Normalize (с определением row_kind)
   rows_normalized = [normalize_row(r) for r in rows_raw]
   
   # 3. Load rules
   ruleset = RuleSet.load("rules/dell_rules.yaml")
   
   # 4. Classify (HEADER → skip, ITEM → classify)
   classification_results = [classify_row(r, ruleset) for r in rows_normalized]
   
   # 5. Create run folder
   run_folder = create_run_folder(args.output_dir, args.input)
   
   # 6. Save artifacts
   save_rows_raw(rows_raw, run_folder)
   save_rows_normalized(rows_normalized, run_folder)
   save_classification(classification_results, run_folder)
   save_unknown_rows([...], run_folder)
   save_header_rows([...], run_folder)  # НОВОЕ!
   save_run_summary(stats, run_folder)
   generate_cleaned_spec(classification_results, rows_normalized, config, run_folder)
   
   # 7. Print summary
   print(f"✓ Processed {len(rows_raw)} rows")
   print(f"  - HEADER: {stats['header_rows_count']}")
   print(f"  - ITEM: {stats['item_rows_count']}")
   print(f"  - UNKNOWN: {stats['unknown_count']}")
   print(f"✓ Artifacts saved to {run_folder}")
   
   # 8. (Optional) Save golden for regression
   if args.save_golden:
       save_golden_for_regression(classification_results, args.input)
   ```
3. Добавь логирование:
   - Настрой `logging` (INFO level)
   - Сохраняй в `run_folder/run.log`
   - Логируй: количество HEADER, ITEM, UNKNOWN строк

**Constraints**:
- НЕ добавляй никаких других опций CLI
- Обрабатывай ошибки (FileNotFoundError, YAMLError) с понятными сообщениями

**Acceptance Criteria**:
- `python main.py --input dl1.xlsx` работает без ошибок
- Все артефакты созданы (включая header_rows.csv)
- `run.log` содержит понятный trace
- Summary показывает header_rows_count, item_rows_count

**Commands to verify**:
```bash
python main.py --input dl1.xlsx
python main.py --input dl2.xlsx
ls output/run_*/
cat output/run_*/run.log | grep "HEADER"
```

---

## Prompt 9 — Implement Tests (Smoke + УСИЛЕННАЯ Regression + Unit)

**Context**: Нужны автоматические тесты для регрессии и валидации.

**Task 1**: Реализуй `tests/test_smoke.py`:
```python
def test_smoke_all_files():
    """Прогон на всех dl1-dl5.xlsx, проверка, что все артефакты созданы"""
    files = ["dl1.xlsx", "dl2.xlsx", "dl3.xlsx", "dl4.xlsx", "dl5.xlsx"]
    for f in files:
        # Запуск main.py
        # Проверка, что папка run_* создана
        # Проверка, что все файлы созданы (rows_raw.json, header_rows.csv, ..., cleaned_spec.xlsx)
```

**Task 2**: Реализуй генерацию эталонов (в `main.py`) — **УСИЛЕННАЯ ВЕРСИЯ**:
- Опция CLI: `--save-golden`
- Сохраняет `golden/dl1_expected.jsonl`, `golden/dl2_expected.jsonl`, ...
- **ФОРМАТ**: JSON Lines (по каждой строке):
  ```jsonl
  {"source_row_index": 1, "row_kind": "HEADER", "entity_type": null, "state": null, "matched_rule_id": "HEADER-SKIP", "skus": []}
  {"source_row_index": 4, "row_kind": "ITEM", "entity_type": "BASE", "state": "PRESENT", "matched_rule_id": "BASE-001", "skus": ["210-BDZY"]}
  {"source_row_index": 5, "row_kind": "ITEM", "entity_type": "HW", "state": "ABSENT", "matched_rule_id": "HW-003", "skus": ["461-AADZ"]}
  ```
- Каждая строка: `source_row_index`, `row_kind`, `entity_type`, `state`, `matched_rule_id`, `skus`

**Task 3**: Реализуй `tests/test_regression.py` — **УСИЛЕННАЯ ВЕРСИЯ**:
```python
@pytest.mark.parametrize("filename", ["dl1.xlsx", "dl2.xlsx", "dl3.xlsx", "dl4.xlsx", "dl5.xlsx"])
def test_regression(filename):
    """ПОСТРОЧНОЕ сравнение с эталонными results"""
    # 1. Прогон на filename
    results = run_classification(filename)
    
    # 2. Загрузка golden/{filename}_expected.jsonl
    golden_file = f"golden/{Path(filename).stem}_expected.jsonl"
    with open(golden_file) as f:
        golden_rows = [json.loads(line) for line in f]
    
    # 3. ПОСТРОЧНОЕ СРАВНЕНИЕ
    for i, (result, golden) in enumerate(zip(results, golden_rows)):
        assert result['source_row_index'] == golden['source_row_index'], f"Row {i}: index mismatch"
        assert result['row_kind'] == golden['row_kind'], f"Row {i}: row_kind changed"
        assert result['entity_type'] == golden['entity_type'], f"Row {i}: entity_type changed from {golden['entity_type']} to {result['entity_type']}"
        assert result['state'] == golden['state'], f"Row {i}: state changed"
        assert result['matched_rule_id'] == golden['matched_rule_id'], f"Row {i}: matched_rule_id changed from {golden['matched_rule_id']} to {result['matched_rule_id']}"
    
    # 4. (Optional) Санити-чек агрегатов
    assert len(results) == len(golden_rows), "Total rows count changed"
```

**Constraints**:
- Используй `pytest`
- Тесты должны быть детерминированные (без random)
- Regression тест должен падать при изменении ЛЮБОЙ строки (не только при изменении counts)

**Acceptance Criteria**:
- `pytest tests/test_smoke.py` — OK
- `python main.py --save-golden --input dl1.xlsx` создаёт `golden/dl1_expected.jsonl`
- `pytest tests/test_regression.py` — OK (при эталонных правилах)
- При изменении правил (например, удалить SOFTWARE-001) — тест падает с конкретной ошибкой:
  ```
  Row 15: entity_type changed from SOFTWARE to UNKNOWN
  ```

**Commands to verify**:
```bash
# Генерация эталонов
python main.py --save-golden --input dl1.xlsx
python main.py --save-golden --input dl2.xlsx
# ... для всех файлов

# Проверка эталонов
cat golden/dl1_expected.jsonl | head -5

# Запуск regression
pytest tests/test_regression.py -v

# Тест падения при изменении правил (удалить SOFTWARE-001 из YAML)
# sed -i '/SOFTWARE-001/d' rules/dell_rules.yaml
# pytest tests/test_regression.py -v  # должно упасть с детальным diff
```

**Task 4**: Реализуй `tests/test_rules_unit.py` — **ОБНОВЛЕНО**:
- Unit tests для отдельных правил (минимум 20):
  - `test_header_skip()` — HEADER строка
  - `test_base_detection()` — BASE
  - `test_software_embedded_systems()` — SOFTWARE-001 (**критично!**)
  - `test_software_dell_secure_onboarding()` — SOFTWARE-002 (**критично!**)
  - `test_service_prosupport()` — SERVICE
  - `test_note_supports()` — NOTE
  - `test_hw_chassis_config()` — HW-001 (Chassis Configuration = HW, не CONFIG)
  - И т.д.

**Commands to verify**:
```bash
pytest tests/test_rules_unit.py -v
```

---

## Prompt 10 — Create Config & Documentation

**Context**: Нужен config.yaml для переключателей и README для пользователя.

**Task 1**: Создай `config.yaml`:
```yaml
cleaned_spec:
  include_types:
    - BASE
    - HW
    - SOFTWARE
    - SERVICE
  
  include_only_present: true
  exclude_headers: true  # НОВОЕ: всегда исключать HEADER rows
  
  output_columns:
    - Module Name
    - Option Name
    - SKUs
    - Qty
    - Option List Price
    - Entity Type
    - State

rules_file: "rules/dell_rules.yaml"
```

**Task 2**: Напиши `README.md`:
- Описание проекта
- Установка (`pip install -r requirements.txt`)
- Использование (`python main.py --input dl1.xlsx`)
- **Описание row_kind** (ITEM vs HEADER)
- Описание артефактов (что в каждом файле, включая header_rows.csv)
- Как запустить тесты (`pytest tests/`)
- Как обновить эталоны (`python main.py --save-golden --input dl1.xlsx`)
- **КРИТИЧНО**: Упомянуть, что "Embedded Systems Management" и "Dell Secure Onboarding" классифицируются как SOFTWARE
- **НОВОЕ**: Добавить раздел "Rules Change Process":
  ```markdown
  ## Rules Change Process
  
  When modifying `rules/dell_rules.yaml`:
  
  1. Update rule version in YAML (e.g., `1.0.0` → `1.0.1`)
  2. Run regression tests to see what changed: `pytest tests/test_regression.py -v`
  3. Update golden files: `python main.py --update-golden --input dl*.xlsx`
  4. **MANDATORY**: Update `CHANGELOG.md` with:
     - What rules were added/changed/fixed
     - Impact on classification (which files/rows changed)
     - New version number
  5. Commit all together: `git add rules/ golden/ CHANGELOG.md`
  
  See `CHANGELOG.md` for version history.
  ```

**Task 3**: Убедись, что `CHANGELOG.md` уже создан (из Prompt 1):
- Должен содержать версию 1.0.0
- Формат: Keep a Changelog
- Semantic Versioning

**Constraints**:
- Markdown форматирование
- Примеры команд
- Понятно для не-программиста
- **Rules Change Process обязателен в README**

**Acceptance Criteria**:
- README содержит всю необходимую информацию
- config.yaml корректный (yaml.safe_load работает)
- Упоминание row_kind (ITEM/HEADER) в README
- **Rules Change Process описан в README**
- **CHANGELOG.md существует и корректен**

**Commands to verify**:
```bash
cat README.md | grep "Rules Change Process"
cat CHANGELOG.md | grep "1.0.0"
yamllint config.yaml
```

---

# [VALIDATION]

## Test Cases (Happy Path)

1. **TC-001**: Парсинг dl1.xlsx
   - Input: dl1.xlsx (~54 rows)
   - Expected: ~54 normalized rows (включая HEADER), заголовки корректные, "Unnamed: 0" удалён, `__row_index__` = номер строки Excel

2. **TC-002**: Определение row_kind (HEADER)
   - Input: `module_name=""`, `option_name=""`, `skus=""`
   - Expected: `row_kind=HEADER`

3. **TC-003**: Определение row_kind (ITEM)
   - Input: `module_name="Base"`, `option_name="PowerEdge R760"`, `skus="210-BDZY"`
   - Expected: `row_kind=ITEM`

4. **TC-004**: Классификация HEADER
   - Input: `row_kind=HEADER`
   - Expected: `entity_type=None, state=None, matched_rule_id="HEADER-SKIP"`

5. **TC-005**: Классификация BASE
   - Input: `row_kind=ITEM, module_name="Base", option_name="PowerEdge R760 Server"`
   - Expected: `entity_type=BASE, state=PRESENT, matched_rule_id=BASE-001`

6. **TC-006**: Классификация SOFTWARE (Embedded Systems Management)
   - Input: `row_kind=ITEM, module_name="Embedded Systems Management", option_name="iDRAC9, Enterprise 16G"`
   - Expected: `entity_type=SOFTWARE, matched_rule_id=SOFTWARE-001`

7. **TC-007**: Классификация SOFTWARE (Dell Secure Onboarding)
   - Input: `row_kind=ITEM, module_name="Dell Secure Onboarding", option_name="Dell Secure Onboarding Client Disabled"`
   - Expected: `entity_type=SOFTWARE, state=DISABLED, matched_rule_id=SOFTWARE-002`

8. **TC-008**: Классификация SERVICE
   - Input: `row_kind=ITEM, module_name="Dell Services:Extended Service", option_name="ProSupport..."`
   - Expected: `entity_type=SERVICE, matched_rule_id=SERVICE-001`

9. **TC-009**: Классификация LOGISTIC
   - Input: `row_kind=ITEM, module_name="Shipping", option_name="PowerEdge R660 Shipping..."`
   - Expected: `entity_type=LOGISTIC, matched_rule_id=LOGISTIC-001`

10. **TC-010**: State ABSENT
    - Input: `option_name="No Trusted Platform Module"`
    - Expected: `state=ABSENT`

11. **TC-011**: State DISABLED
    - Input: `option_name="Dell Connectivity Client - Disabled"`
    - Expected: `state=DISABLED`

12. **TC-012**: Cleaned spec generation
    - Input: 54 rows (HEADER=3, ITEM=51, где BASE=1, HW=30, SERVICE=3, LOGISTIC=6, SOFTWARE=2, ABSENT=14)
    - Expected: Cleaned spec содержит только ITEM строки типа BASE+HW+SERVICE+SOFTWARE+PRESENT (~25-30 rows)

13. **TC-013**: Все артефакты созданы
    - Input: Прогон на dl1.xlsx
    - Expected: В `output/run_*/` есть все файлы (rows_raw.json, header_rows.csv, cleaned_spec.xlsx, ...)

14. **TC-014**: run_summary.json содержит header_rows_count
    - Input: Прогон на dl1.xlsx
    - Expected: `run_summary.json` содержит `"header_rows_count": 3`

## Edge Cases

1. **EC-001**: Файл с другой структурой заголовков
   - Input: Excel с header в строке 10
   - Expected: `find_header_row()` находит корректно или возвращает None

2. **EC-002**: Строка с множественными SKUs
   - Input: `skus="338-CHSG, 379-BDCO, 461-AADZ"`
   - Expected: `skus=["338-CHSG", "379-BDCO", "461-AADZ"]`

3. **EC-003**: ITEM строка без Module Name
   - Input: `module_name=None, option_name="Some option", skus=["123-ABC"]`
   - Expected: `row_kind=ITEM` (не HEADER, т.к. есть SKU)

4. **EC-004**: Конфликтующие паттерны ("Chassis Configuration")
   - Input: `module_name="Chassis Configuration"`
   - Expected: `entity_type=HW, matched_rule_id=HW-001` (НЕ CONFIG!)

5. **EC-005**: "supports" vs "Support"
   - Input: `option_name="Motherboard supports ONLY CPUs below 250W"`
   - Expected: `entity_type=NOTE` (НЕ SERVICE)

6. **EC-006**: Пустой файл Excel
   - Input: Excel без строк данных
   - Expected: `rows_raw=[]`, артефакты созданы, `run_summary.json` показывает 0 rows

7. **EC-007**: Неправильный формат файла
   - Input: `input.txt` вместо `.xlsx`
   - Expected: Понятное сообщение об ошибке

8. **EC-008**: Несуществующий файл
   - Input: `--input nonexistent.xlsx`
   - Expected: FileNotFoundError с понятным сообщением

9. **EC-009**: HEADER строка с частично заполненными полями
   - Input: `module_name="", option_name="", skus="", product_name="PowerEdge R760 - Full Configuration"`
   - Expected: `row_kind=HEADER`

10. **EC-010**: Regression тест при изменении одной строки
    - Input: Изменить SOFTWARE-001 правило → одна строка изменится с SOFTWARE на UNKNOWN
    - Expected: Regression тест падает с детальным diff (указывает конкретную строку)

## Manual QA Checklist

- [ ] Прогон на всех dl1-dl5.xlsx без ошибок
- [ ] Opened cleaned_spec.xlsx в Excel — форматирование корректное, HEADER строки исключены
- [ ] `header_rows.csv` содержит только HEADER строки (пустые Module Name/Option Name/SKUs)
- [ ] `run.log` читается и понятен, показывает количество HEADER/ITEM строк
- [ ] `unknown_rows.csv` содержит только реально неклассифицированные ITEM строки (не HEADER)
- [ ] `rules_stats.json` показывает распределение правил:
  - [ ] SOFTWARE-001 (Embedded Systems Management) присутствует (~26 раз в dl2)
  - [ ] SOFTWARE-002 (Dell Secure Onboarding) присутствует (~12 раз)
  - [ ] HEADER-SKIP присутствует (количество HEADER строк)
  - [ ] Нет перекоса на UNKNOWN
- [ ] Regression тесты падают при изменении правил (даже если counts совпадают)
- [ ] Regression diff показывает конкретные строки, которые изменились
- [ ] Обновление эталонов через `--update-golden` работает
- [ ] **CHANGELOG.md обновлён при изменении правил**
- [ ] **Версия в dell_rules.yaml соответствует версии в CHANGELOG.md**

## Monitoring Checklist (post-deployment)

- [ ] Количество UNKNOWN строк < 5% от item_rows_count
- [ ] header_rows_count стабильно для одного и того же файла
- [ ] SOFTWARE-001 матчится на "Embedded Systems Management" (~26 раз в dl2)
- [ ] Нет warnings в classification results (или они понятны)
- [ ] rules_stats показывает, что все правила используются (нет мёртвых правил)
- [ ] Cleaned spec содержит ожидаемое количество строк (не 0, не 100% от total)
- [ ] Regression тесты ловят все изменения в классификации

---

# ФИНАЛЬНАЯ СВОДКА

## Что получаем в MVP (ОБНОВЛЕНО):
✅ Детерминированный пайплайн классификации Dell спецификаций  
✅ **row_kind detection** (ITEM vs HEADER) — исключает ложные UNKNOWN  
✅ 8 типов строк (BASE, HW, CONFIG, SOFTWARE, SERVICE, LOGISTIC, NOTE, UNKNOWN)  
✅ **Расширенные SOFTWARE правила** (Embedded Systems Management, Dell Secure Onboarding)  
✅ 3 состояния (PRESENT, ABSENT, DISABLED)  
✅ Полные диагностические артефакты для каждого прогона (включая **header_rows.csv**)  
✅ Cleaned spec Excel (только ITEM строки нужных типов, HEADER исключены)  
✅ **Усиленные автоматические тесты** (smoke + **построчная regression** + unit)  
✅ Версионируемые правила (YAML)  
✅ **CHANGELOG.md для трейсабилити изменений правил**  
✅ Расширяемая архитектура (плагины для других брендов)  
✅ **`__row_index__` = номер строки в Excel** (стабильность golden/regression)  

## Ключевые улучшения по сравнению с первой версией:
1. **row_kind (ITEM/HEADER)** — устраняет ложные UNKNOWN от разделителей
2. **Расширенные SOFTWARE правила** — покрывает "Embedded Systems Management" (26 строк в dl2!)
3. **Усиленная regression** — построчное сравнение (не только counts) → ловит больше поломок
4. **`__row_index__` = Excel row number** — стабильность эталонов при изменении парсинга
5. **CHANGELOG.md** — обязательная документация всех изменений правил

## Обязательный процесс изменения правил:
1. Изменить `dell_rules.yaml` (увеличить версию)
2. Запустить regression тесты (проверить diff)
3. Обновить golden эталоны (`--update-golden`)
4. **ОБЯЗАТЕЛЬНО**: Обновить `CHANGELOG.md` (что изменилось, impact)
5. Commit всё вместе (rules + golden + CHANGELOG)

## Что НЕ делаем:
❌ База данных (только файлы)  
❌ Другие бренды в MVP (но архитектура готова)  
❌ **Slot-модель** (явно OUT OF SCOPE)  
❌ Web-интерфейс  
❌ ML/эвристики  

## Оценка времени (для Cursor):
- **Фаза 0-2** (Setup + Parsing + Rules): 2-3 дня
- **Фаза 3-4** (Artifacts + Excel): 1-2 дня
- **Фаза 5-6** (CLI + **Усиленные Tests**): 3-4 дня (больше из-за построчной regression)
- **Фаза 7** (Docs): 0.5 дня
- **TOTAL**: ~7-10 дней

## Следующие шаги после MVP:
1. Прогон на реальных данных → расширение правил на основе UNKNOWN строк
2. Добавление Slot-модели (если нужно)
3. Добавление других брендов (HP, Lenovo, ...)
4. Интеграция с ERP/CRM

---

**Конец документа**
