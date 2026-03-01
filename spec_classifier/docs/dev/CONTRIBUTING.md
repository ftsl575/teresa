# Участие в разработке — spec_classifier (teresa)

## 1. Структура репозитория

```
spec_classifier/
├── main.py                 # Точка входа CLI, оркестрация пайплайна
├── config.yaml             # Конфиг (rules_file, vendor_rules, cleaned_spec)
├── requirements.txt
├── rules/
│   ├── dell_rules.yaml     # Правила для Dell (entity, state, device_type, hw_type)
│   └── cisco_rules.yaml    # Правила для Cisco CCW
├── src/
│   ├── core/               # Парсер (Dell), нормализатор (Dell), классификатор, state_detector
│   ├── rules/              # Загрузка и сопоставление правил (RuleSet)
│   ├── vendors/            # Vendor adapters (Dell, Cisco)
│   │   ├── base.py         # VendorAdapter ABC
│   │   ├── dell/
│   │   │   └── adapter.py  # DellAdapter (wraps core parser/normalizer)
│   │   └── cisco/
│   │       ├── parser.py   # Cisco CCW parser (sheet "Price Estimate")
│   │       ├── normalizer.py # CiscoNormalizedRow + normalize_cisco_rows
│   │       └── adapter.py  # CiscoAdapter
│   ├── outputs/            # JSON/Excel-запись (json_writer, excel_writer, annotated_writer, branded_spec_writer)
│   └── diagnostics/        # run_manager, stats_collector
├── tests/                  # Unit, integration, regression (Dell + Cisco)
├── golden/                 # Ожидаемые JSONL для регрессии (в git)
├── docs/                   # Документация
└── output/                 # Папки прогонов (не в git)
```

**Примечание:** `diag/` — в .gitignore; логи прогонов пишутся в `temp_root/diag/` (см. config.local.yaml).

---

## 2. Definition of Done для PR

- [ ] `pytest tests/ -v` — все тесты зелёные.
- [ ] При изменении правил: добавлен/обновлён unit-тест, golden обновлён, diff описан в PR.
- [ ] При изменении `cisco_rules.yaml`: Cisco golden обновлён (`--vendor cisco --save-golden`), добавлен/обновлён unit-тест, diff описан в PR.
- [ ] CHANGELOG.md обновлён (Unreleased или версия).
- [ ] Документация актуальна при изменении поведения (README, TECHNICAL_OVERVIEW, user/schemas/rules/dev).

---

## 3. Запреты

- Не коммитить xlsx в git (test_data/*.xlsx в .gitignore).
- Не коммитить output/ в git.
- Не менять rule_id без обновления golden и явного описания в CHANGELOG.
- Не менять `cisco_rules.yaml` без обновления Cisco golden (`ccw_1_expected.jsonl`, `ccw_2_expected.jsonl`).

---

## 4. Стиль кода

- PEP 8, отступы 4 пробела.
- Docstrings для публичных функций и модулей.
- Следовать стилю существующего кода в файле/модуле.

---

## 5. Версионирование

- SemVer. При изменении правил обновлять поле **version** в соответствующем файле: `dell_rules.yaml` (для Dell) или `cisco_rules.yaml` (для Cisco). MAJOR — ломающие изменения контрактов вывода/CLI; MINOR — новые поля, новые опции; PATCH — правки правил, тесты, документация.
