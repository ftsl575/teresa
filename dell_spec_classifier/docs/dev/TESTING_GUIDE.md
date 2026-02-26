# Руководство по тестированию — Dell Specification Classifier

## 1. Тестовая стратегия

- **Unit (без xlsx):** test_rules_unit, test_state_detector, test_normalizer — не требуют тестовых Excel.
- **Integration (с xlsx):** прогон пайплайна на test_data/dlN.xlsx; проверка артефактов (test_smoke, test_excel_writer, test_annotated_writer, test_cli).
- **Regression (xlsx + golden):** test_regression — построчное сравнение с golden/<stem>_expected.jsonl.
- **Acceptance:** test_unknown_threshold (лимит unknown), test_dec_acceptance и др. по необходимости.

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
```

---

## 3. Тестовые данные

Файлы `test_data/dl1.xlsx` … `dl6.xlsx` не хранятся в git. Размещайте их в `dell_spec_classifier/test_data/`. При отсутствии файла тесты, зависящие от него, пропускаются (skip) с сообщением.

---

## 4. Golden-файлы

- **Генерация:** `python main.py --input test_data/dl1.xlsx --save-golden` → создаётся `golden/dl1_expected.jsonl`.
- **Обновление:** `--update-golden` с интерактивным подтверждением (y/N). В CI — `--save-golden`.
- **Сравниваемые поля:** entity_type, state, matched_rule_id, device_type, hw_type, skus (и другие, заданные в тесте).
- **Политика:** обновлять golden только осознанно после изменения правил/логики; в PR обязательно описание diff и ревью.

---

## 5. Добавление unit-теста

Шаблон в tests/test_rules_unit.py или test_device_type.py: создать нормализованную строку (или использовать фикстуру), вызвать classify_row(row, ruleset), assert result.entity_type / state / matched_rule_id / device_type / hw_type. Для правил — загрузить RuleSet из dell_rules.yaml (через conftest/project_root).

---

## 6. CI gate

Минимальная команда для проверки перед коммитом:

```bash
pytest tests/test_rules_unit.py tests/test_state_detector.py tests/test_normalizer.py \
       tests/test_regression.py tests/test_unknown_threshold.py -v --tb=short
```

При отсутствии test_data или golden часть тестов будет пропущена; unit-тесты и регрессия (если файлы есть) должны быть зелёными.

---

## 7. Unknown threshold gate

Тест test_unknown_threshold ограничивает долю UNKNOWN-строк (например 5%). При превышении лимита — добавлять правила, а не поднимать порог и не обновлять golden без обоснования.

---

## 8. Работа с новым датасетом (dlN)

1. Скопировать xlsx в test_data/dlN.xlsx.
2. Запустить `python main.py --input test_data/dlN.xlsx --save-golden`.
3. Проверить unknown_rows.csv и run_summary.
4. При необходимости добавить правила и повторить.
5. Добавить параметр в parametrize в test_regression.py (и при необходимости в другие тесты).
6. Запустить полный набор тестов.
7. Закоммитить golden/dlN_expected.jsonl и изменения тестов.
