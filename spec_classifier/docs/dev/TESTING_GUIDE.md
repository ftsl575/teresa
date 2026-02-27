# Руководство по тестированию — Spec Classifier (Dell + Cisco CCW)

## 1. Тестовая стратегия

- **Unit (без xlsx):** test_rules_unit, test_state_detector, test_normalizer — не требуют тестовых Excel.
- **Integration (с xlsx):** прогон пайплайна на test_data/dlN.xlsx; проверка артефактов (test_smoke, test_excel_writer, test_annotated_writer, test_cli).
- **Regression (xlsx + golden):** test_regression — построчное сравнение с golden/<stem>_expected.jsonl.
- **Acceptance:** test_unknown_threshold (лимит unknown), test_dec_acceptance и др. по необходимости.
- **Cisco Unit:** test_cisco_parser — parse_excel на ccw_1/ccw_2 (26 и 82 строки); test_cisco_normalizer — bundle_id, parent_line_number, is_bundle_root, module_name, standalone.
- **Cisco Regression:** test_regression_cisco — построчное сравнение с golden/ccw_1_expected.jsonl и ccw_2_expected.jsonl.
- **Cisco Threshold:** test_unknown_threshold_cisco — unknown_count = 0 для ccw_1 и ccw_2.

---

## 2. Быстрый запуск

```bash
# Unit без xlsx
pytest tests/test_rules_unit.py tests/test_state_detector.py tests/test_normalizer.py -v

# С xlsx (smoke + CLI)
pytest tests/test_smoke.py tests/test_cli.py -v

# Регрессия (нужны test_data и golden)
pytest tests/test_regression.py -v

# Вся батарея
pytest tests/ -v --tb=short

# Cisco тесты
pytest tests/test_cisco_parser.py tests/test_cisco_normalizer.py \
       tests/test_regression_cisco.py tests/test_unknown_threshold_cisco.py -v
```

---

## 3. Тестовые данные

Файлы `test_data/dl1.xlsx` … `dl5.xlsx`, `ccw_1.xlsx`, `ccw_2.xlsx` не хранятся в git. Размещайте их в `spec_classifier/test_data/`. При отсутствии файла тесты, зависящие от него, пропускаются (skip) с сообщением.

---

## 4. Golden-файлы

- **Генерация:** `python main.py --input test_data/dl1.xlsx --save-golden` → создаётся `golden/dl1_expected.jsonl`.
- **Обновление:** `--update-golden` с интерактивным подтверждением (y/N). В CI — `--save-golden`.
- **Сравниваемые поля:** entity_type, state, matched_rule_id, device_type, hw_type, skus (и другие, заданные в тесте).
- **Политика:** обновлять golden только осознанно после изменения правил/логики; в PR обязательно описание diff и ревью.
- **Cisco golden:** `golden/ccw_1_expected.jsonl`, `golden/ccw_2_expected.jsonl`. Генерация: `python main.py --input test_data/ccw_1.xlsx --vendor cisco --save-golden` (аналогично для ccw_2). После изменения `cisco_rules.yaml` — обновить оба Cisco golden.

---

## 5. Добавление unit-теста

Шаблон в tests/test_rules_unit.py или test_device_type.py: создать нормализованную строку (или использовать фикстуру), вызвать classify_row(row, ruleset), assert result.entity_type / state / matched_rule_id / device_type / hw_type. Для правил — загрузить RuleSet из dell_rules.yaml (через conftest/project_root).

---

## 6. CI gate

Минимальная команда для проверки перед коммитом:

```bash
pytest tests/test_rules_unit.py tests/test_state_detector.py tests/test_normalizer.py \
       tests/test_regression.py tests/test_unknown_threshold.py \
       tests/test_regression_cisco.py tests/test_unknown_threshold_cisco.py -v --tb=short
```

При отсутствии test_data или golden часть тестов будет пропущена; unit-тесты и регрессия (если файлы есть) должны быть зелёными.

---

## 7. Unknown threshold gate

Тест test_unknown_threshold ограничивает долю UNKNOWN-строк (например 5%). При превышении лимита — добавлять правила, а не поднимать порог и не обновлять golden без обоснования.

---

## 8. Работа с новым датасетом

1. Скопировать xlsx в test_data/dlN.xlsx.
2. Запустить `python main.py --input test_data/dlN.xlsx --save-golden`.
3. Проверить unknown_rows.csv и run_summary.
4. При необходимости добавить правила и повторить.
5. Добавить параметр в parametrize в test_regression.py (и при необходимости в другие тесты).
6. Запустить полный набор тестов.
7. Закоммитить golden/dlN_expected.jsonl и изменения тестов.

### Новый Cisco датасет (ccwN.xlsx)

1. Скопировать в `test_data/ccw_N.xlsx`.
2. Запустить `python main.py --input test_data/ccw_N.xlsx --vendor cisco`.
3. Проверить `unknown_rows.csv` и `run_summary.json` (цель: `unknown_count = 0`).
4. При `unknown > 0`: добавить правила в `rules/cisco_rules.yaml`, повторить шаг 2.
5. Запустить `python main.py --input test_data/ccw_N.xlsx --vendor cisco --save-golden`.
6. Добавить `ccw_N` в `@pytest.mark.parametrize` в `test_regression_cisco.py`.
7. Запустить `pytest tests/ -v` и закоммитить `golden/ccw_N_expected.jsonl`.
