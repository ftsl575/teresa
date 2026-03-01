# Руководство по правилам — spec_classifier

## 1. Обзор

Правила хранятся в `rules/dell_rules.yaml` (Dell) и `rules/cisco_rules.yaml` (Cisco). Файл выбирается через `--vendor {dell,cisco}` и секцию `vendor_rules` в `config.yaml`. Классификация детерминирована; для каждой ITEM-строки применяется первое совпадение (first-match) в заданном порядке категорий и внутри каждой категории; семантика одинакова для обоих вендоров.

---

## 2. Структура YAML

- **version** — версия набора правил (например 1.1.0).
- **state_rules** — определение state (absent_keywords, present_override_keywords).
- **base_rules, service_rules, logistic_rules, software_rules, note_rules, config_rules, hw_rules** — правила типа сущности (entity_type).
- **device_type_rules** — второй проход: назначение device_type для HW/LOGISTIC.
- **hw_type_rules** — третий проход: назначение hw_type для HW (device_type_map, rule_id_map, rules).

---

## 3. Порядок классификации entity_type

| Приоритет | Категория | Описание |
|-----------|-----------|----------|
| 1 | BASE | Базовая система (Base, PowerEdge R6xx). |
| 2 | SERVICE | Услуги (ProSupport, Warranty). |
| 3 | LOGISTIC | Логистика (Shipping, Power Cord, Cables). |
| 4 | SOFTWARE | ПО (Embedded Systems Management, OS). |
| 5 | NOTE | Информационные заметки. |
| 6 | CONFIG | Конфигурация (No Cable, RAID). |
| 7 | HW | Железо (Processor, Memory, Drives). |
| 8 | UNKNOWN | Нет совпадений. |

---

## 4. Формат entity-правила

```yaml
- field: module_name   # или option_name
  pattern: 'regex'     # всегда re.IGNORECASE
  entity_type: HW      # информационно
  rule_id: HW-002      # уникальный, не переиспользуется
```

---

## 5. State-правила

- **absent_keywords:** pattern + state: ABSENT (или DISABLED) + rule_id. Проверка по option_name.
- **present_override_keywords:** переопределение на PRESENT (например «N Rear Blanks»).

---

## 6. device_type-правила

В секции `device_type_rules.rules` у правила указывается поле **device_type** (вместо entity_type). Применяются только к ITEM с entity_type из `applies_to` (HW, LOGISTIC) и при matched_rule_id != UNKNOWN-000.

---

## 7. hw_type_rules — три слоя

1. **device_type_map:** маппинг device_type → hw_type (например nic → network_adapter).
2. **rule_id_map:** маппинг matched_rule_id → hw_type (например HW-001 → chassis).
3. **rules:** список правил с полем **hw_type** и pattern по module_name/option_name; первое совпадение выигрывает. Порядок правил важен.

---

## 8. Конвенция именования rule_id

Формат: `<CATEGORY>-[<VENDOR_CODE>-]<NNN>`

| Вендор | Код | Пример |
|--------|-----|--------|
| Dell | (без кода) | BASE-001, HW-002, STATE-001 |
| Cisco | C | BASE-C-001, HW-C-001, STATE-C-001 |
| Новый вендор (HPE) | H | BASE-H-001, HW-H-001 |

- **NNN** — трёхзначный номер в рамках категории и вендора.
- **rule_id** глобально уникален (не только в рамках одного YAML-файла).
- **Зарезервированные:** HEADER-SKIP, UNKNOWN-000 — не переиспользовать.

Изменение или переименование rule_id требует обновления golden (`--save-golden` / `--update-golden`) и записи в CHANGELOG.

---

## 9. Пошаговое добавление правила

1. Сформулировать критерий (regex по module_name или option_name).
2. Проверить regex на тестовых строках (в т.ч. на всех датасетах dl1–dl5 (для Dell) или ccw_1, ccw_2 (для Cisco)).
3. Выбрать категорию и место в YAML (после более специфичных правил).
4. Добавить правило с уникальным rule_id.
5. Запустить пайплайн на всех тестовых файлах вендора:
   - Dell: `python main.py --input "C:\Users\G\Desktop\INPUT\dl1.xlsx"` (и dl2..dl5)
   - Cisco: `python main.py --input "C:\Users\G\Desktop\INPUT\ccw_1.xlsx" --vendor cisco` (и ccw_2)
6. Проверить unknown_rows.csv и run_summary.json.
7. При необходимости добавить unit-тест в test_rules_unit.py или test_device_type.py.
8. Обновить golden (`--save-golden`) и прогнать test_regression.py.
9. Обновить CHANGELOG.md и при необходимости документацию.

---

## 10. Анти-паттерны

- **Слишком широкий pattern:** например голый `\bOCP\b` перехватывает «OCP 3.0 Accessories»; сужать контекст.
- **Negative lookahead без проверки на всех датасетах:** может сломать другие строки.
- **Shadowed rule:** правило, стоящее после более общего и никогда не срабатывающее — проверять порядок.
- **Дублирование rule_id:** один rule_id не должен встречаться в разных целях (entity vs device_type vs hw_type — допустимо одно и то же значение в разных секциях только если это один и тот же логический rule).
- **Изменение rule_id без обновления golden:** регрессия упадёт; обновлять golden и описывать в CHANGELOG.

---

## 11. Типовые паттерны

- **Точное совпадение:** `'^Base$'`, `'^Chassis\s+Configuration$'`.
- **Префикс/вхождение:** `'\b(Processor|Memory\s+Capacity)\b'`.
- **Negative lookahead:** `'(?i)\b((?<!GPU\s)Blanks?|Filler)\b'` — исключить «GPU Blanks».
- **Два условия (AND):** `'(?i)(?=.*No\s+BOSS)(?=.*Rear\s+Blank).*'`.

---

## 12. Версионирование правил

При изменении правил обновлять поле **version** в `dell_rules.yaml`. То же применяется к `cisco_rules.yaml` — поле **version** обновлять при любом изменении Cisco-правил. SHA-256 файла правил записывается в run_summary.json (rules_file_hash) для воспроизводимости.

---

## 13. Cisco-правила

- **Файл:** `rules/cisco_rules.yaml`.
- **Доступные поля для `field`:** `module_name`, `option_name`, `sku`, `is_bundle_root` (значения `"true"`/`"false"` в нижнем регистре), `service_duration_months`.
- **Примечание:** `sku` матчится только по `skus[0]` (MVP limitation). При наличии multi-SKU строк рекомендуется расширить логику.
- **После изменений:**

```bash
python main.py --input "C:\Users\G\Desktop\INPUT\ccw_1.xlsx" --vendor cisco --save-golden
python main.py --input "C:\Users\G\Desktop\INPUT\ccw_2.xlsx" --vendor cisco --save-golden
pytest tests/test_regression_cisco.py tests/test_unknown_threshold_cisco.py -v
```
