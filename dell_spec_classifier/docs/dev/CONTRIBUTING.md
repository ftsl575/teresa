# Участие в разработке — Dell Specification Classifier

## 1. Структура репозитория

```
dell_spec_classifier/
├── main.py                 # Точка входа CLI, оркестрация пайплайна
├── config.yaml             # Конфиг (rules_file, cleaned_spec)
├── requirements.txt
├── rules/
│   └── dell_rules.yaml     # Правила классификации (entity, state, device_type, hw_type)
├── src/
│   ├── core/               # Парсер, нормализатор, классификатор, state_detector
│   ├── rules/              # Загрузка и сопоставление правил (RuleSet)
│   ├── outputs/            # JSON/Excel-запись (json_writer, excel_writer, annotated_writer, branded_spec_writer)
│   └── diagnostics/        # run_manager, stats_collector
├── tests/                  # Unit, integration, regression
├── golden/                 # Ожидаемые JSONL для регрессии (в git)
├── docs/                   # Документация
└── output/                 # Папки прогонов (не в git)
```

---

## 2. Definition of Done для PR

- [ ] `pytest tests/ -v` — все тесты зелёные.
- [ ] При изменении правил: добавлен/обновлён unit-тест, golden обновлён, diff описан в PR.
- [ ] CHANGELOG.md обновлён (Unreleased или версия).
- [ ] Документация актуальна при изменении поведения (README, TECHNICAL_OVERVIEW, user/schemas/rules/dev).

---

## 3. Запреты

- Не коммитить xlsx в git (test_data/*.xlsx в .gitignore).
- Не коммитить output/ в git.
- Не менять rule_id без обновления golden и явного описания в CHANGELOG.

---

## 4. Стиль кода

- PEP 8, отступы 4 пробела.
- Docstrings для публичных функций и модулей.
- Следовать стилю существующего кода в файле/модуле.

---

## 5. Версионирование

- SemVer. При изменении правил обновлять поле **version** в `dell_rules.yaml`. MAJOR — ломающие изменения контрактов вывода/CLI; MINOR — новые поля, новые опции; PATCH — правки правил, тесты, документация.
