# Coding Conventions

**Analysis Date:** 2026-05-04

## Naming patterns

**Python:**
- Модули и функции: `snake_case`.
- Классы: `PascalCase` (`VendorAdapter`, `DellAdapter`, `ClassificationResult`, `RuleSet`).
- Перечисления: `Enum` в `classifier.py` (`EntityType`), `state_detector.py` (`State`), `normalizer.py` (`RowKind`).
- Константы таксономии: множества вроде `HW_TYPE_VOCAB` в `classifier.py` (дублируются/согласуются с аудитом — см. комментарии в коде).

**YAML rules:**
- Идентификаторы правил в формате, описанном в документации автора правил (`docs/` — RULES_AUTHORING и др.).

## Code style

- Явная типизация встречается в современных участках (`base.py` использует `list`, `Tuple`, union-типы для Python 3.10+).
- Docstrings преимущественно на английском в ядре; в адаптерах возможны русские пояснения в контракте `VendorAdapter`.
- Отдельного закреплённого в репо конфига Ruff/Black в представленном срезе зависимостей нет — форматирование по фактической практике файлов.

## Import organization

- Импорты от корня пакета под `spec_classifier/`: `from src.core...`, `from src.vendors...` (как в `main.py` и тестах).

## Error handling

- Граница CLI: перехват `FileNotFoundError`, `yaml.YAMLError`, общий `Exception` с `log.exception` в `_run_single` (`main.py`).
- Адаптеры по контракту `can_parse` не должны глотать ошибки чтения файла — некорректный файл должен всплыть.

## Logging

- Стандартный `logging`; для прогона добавляется `FileHandler` на `run.log` в папке run (`main.py`).

## Comments

- Бизнес-инварианты и связь с E-кодами аудита нередко отражены комментариями в `classifier.py` и `batch_audit.py`.
- Промпты и долгие методологии живут в `prompts/` и `docs/`, не дублируются как обязательные комментарии в каждой функции.

---

*Convention analysis: 2026-05-04*
