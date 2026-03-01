# Руководство по добавлению нового вендора — spec_classifier

Самодостаточный документ: новый вендор можно добавить, следуя только этому файлу (плюс образцы Dell/Cisco в коде).

---

## 1. Обзор: какие файлы создать и изменить

**Создать:**
- `src/vendors/<vendor>/__init__.py` (пустой)
- `src/vendors/<vendor>/adapter.py` — класс адаптера
- `rules/<vendor>_rules.yaml` — правила классификации
- `tests/test_regression_<vendor>.py` (по образцу test_regression_cisco.py)
- `tests/test_unknown_threshold_<vendor>.py` (по образцу test_unknown_threshold_cisco.py)
- Тестовые данные в `test_data/` (например `<vendor>_1.xlsx`)
- Golden: `golden/<stem>_expected.jsonl` (генерируются через `--save-golden`)

**Изменить:**
- `main.py` — одна строка в VENDOR_REGISTRY
- `config.yaml` — одна строка в `vendor_rules`
- При необходимости: `src/outputs/annotated_writer.py` — добавить tuple в VENDOR_EXTRA_COLS, если у нормализованных строк есть дополнительные поля для колонок в annotated Excel
- `CHANGELOG.md`, `CURRENT_STATE.md` — после добавления вендора

---

## 2. Пошаговая инструкция

### Шаг 1: src/vendors/<vendor>/__init__.py

Создать пустой файл (или с минимальным экспортом адаптера, если принято в проекте).

### Шаг 2: src/vendors/<vendor>/adapter.py — реализация VendorAdapter

Реализовать все 6 обязательных методов ABC:

- **can_parse(path)**  
  **ОБЯЗАТЕЛЬНО: позитивная сигнатура** — уникальный маркер файла этого вендора.  
  Пример Dell: ячейка `"Module Name"` в первых 20 строках первого листа.  
  Пример Cisco: наличие листа `"Price Estimate"` в книге.  
  **ЗАПРЕЩЕНО:** «negative identity» (return True if not другой_вендор).  
  Не ловить исключения — нечитаемый файл должен приводить к падению, а не к пропуску.

- **parse(path)**  
  Возвращает `(list[dict], int)`: список строк (каждый dict с полями + `__row_index__` 1-based) и 0-based индекс строки заголовка.

- **normalize(raw_rows)**  
  Возвращает `list` объектов, совместимых с NormalizedRow.  
  **Обязательные поля:** source_row_index, row_kind, group_name, group_id, product_name, module_name, option_name, option_id, skus, qty, option_price.  
  Остальные по контракту (см. DATA_CONTRACTS.md и src/core/normalizer.NormalizedRow).

- **get_rules_file()**  
  Путь к YAML правил (например `rules/<vendor>_rules.yaml`), можно брать из `config["vendor_rules"][vendor]` с fallback.

- **get_vendor_stats(normalized_rows)**  
  Словарь для run_summary.json (см. п. 3).

- **generates_branded_spec()**  
  True только если для вендора реализован branded spec; иначе False.

### Шаг 3: rules/<vendor>_rules.yaml

Структура: version, state_rules, base_rules, service_rules, … hw_rules, device_type_rules (по образцу dell_rules.yaml или cisco_rules.yaml).  
**rule_id:** формат `<CATEGORY>-<VENDOR_CODE>-NNN` — см. docs/rules/RULES_AUTHORING_GUIDE.md, раздел «Конвенция именования rule_id». Для нового вендора выбрать свой код (например H для HPE).

### Шаг 4: Добавить в VENDOR_REGISTRY в main.py

Одна строка: импорт адаптера и запись `"<vendor>": <Vendor>Adapter` в словарь VENDOR_REGISTRY.

### Шаг 5: Добавить в vendor_rules в config.yaml

В секции `vendor_rules` добавить: `<vendor>: "rules/<vendor>_rules.yaml"`.

### Шаг 6: Тесты

- **test_regression_<vendor>.py** — по образцу test_regression_cisco.py: прогон через `_get_adapter("<vendor>", config)`, сравнение с golden.
- **test_unknown_threshold_<vendor>.py** — по образцу test_unknown_threshold_cisco.py: проверка unknown_count = 0 на тестовых файлах вендора.

### Шаг 7: Golden файлы

Для каждого тестового файла:

```bash
python main.py --save-golden --input test_data/<file>.xlsx --vendor <vendor>
```

Положить/проверить golden в `golden/<stem>_expected.jsonl`.

### Шаг 8: Обновить CHANGELOG.md и CURRENT_STATE.md

В CHANGELOG [Unreleased]: добавление вендора, новые тесты, новые правила.  
В CURRENT_STATE: перечень активных вендоров и тестовых датасетов.

### Шаг 9: Дополнительные колонки в annotated Excel

Если адаптер добавляет поля к нормализованной строке (как Cisco: line_number, service_duration_months), добавить соответствующие tuple в **VENDOR_EXTRA_COLS** в `src/outputs/annotated_writer.py`. Колонка появится в annotated xlsx только если хотя бы у одной из первых 10 строк атрибут задан.

---

## 3. vendor_stats

- **Dell:** `get_vendor_stats()` возвращает `{}` — в run_summary.json секция vendor_stats пустая.
- **Cisco:** возвращает словарь с метриками (например top_level_bundles_count, max_hierarchy_depth) — они попадают в run_summary.json.

Для нового вендора: либо `{}`, либо свой набор метрик по необходимости.

---

## 4. Чеклист перед PR

- [ ] **can_parse:** позитивная сигнатура (уникальный маркер формата), без «negative identity».
- [ ] **unknown_count = 0** на всех тестовых файлах вендора.
- [ ] **hw_type_null_count = 0** (если применимо).
- [ ] Все тесты зелёные: `python -m pytest tests/ -v`.
- [ ] Golden файлы сгенерированы и регрессия проходит.
- [ ] CHANGELOG.md обновлён (новая запись в [Unreleased] или в версии релиза).

---

## См. также

- `docs/rules/RULES_AUTHORING_GUIDE.md` — конвенция rule_id, структура YAML.
- `docs/schemas/DATA_CONTRACTS.md` — контракт NormalizedRow и артефактов.
- `src/vendors/dell/adapter.py`, `src/vendors/cisco/adapter.py` и `src/vendors/cisco/parser.py`, `normalizer.py` — образцы реализации.
