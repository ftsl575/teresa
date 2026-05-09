# Testing Patterns

**Analysis Date:** 2026-05-04

## Test framework

**Runner:**
- `pytest` (версия из `requirements.txt`: `>=7.0.0`).

**Collection (fact):**
- Из каталога `spec_classifier/`: `775 tests collected` (`python -m pytest tests/ --collect-only -q`, 2026-05-04).

**Typical commands:**
```powershell
Set-Location spec_classifier
python -m pytest tests/ -v --tb=short
```

**Makefile shortcuts** (в `spec_classifier/Makefile`): узкий быстрый набор unit-тестов без полного дерева — см. цели вроде короткого `pytest` набора для rules/state/normalizer.

## Test file organization

**Location:**
- Все тесты под `spec_classifier/tests/`, префикс `test_*.py`.

**Themes (по именам файлов):**
- Регрессия по вендорам: `test_regression_*.py`, golden-сравнение.
- Пороги UNKNOWN: `test_unknown_threshold*.py`.
- Парсеры/нормализаторы: `test_*_parser.py`, `test_*_normalizer.py`.
- Правила: `test_*_rules_unit.py`.
- Писатели выходов и схема: `test_output_structure.py`, `test_excel_writer.py`, `test_annotated_writer.py`, `test_branded_spec_writer.py`.
- Аудиты: `test_batch_audit.py`, `test_cluster_audit.py`.
- Ядро: `test_state_detector.py`, `test_device_type.py`, `test_cli.py`, и др.

## Fixtures

- `spec_classifier/conftest.py` — общие фикстуры/настройки (в т.ч. guard’ы для окружения — см. файл).
- Эталонные данные: `spec_classifier/golden/*.jsonl`; входные xlsx для тестов — по путям внутри тестов (часто вне репозитория или minimal fixtures — уточнять в конкретном тесте).

## Coverage / CI

- В репозитории на дату карты нет `.github/workflows/` — автоматический CI не зафиксирован YAML-файлами.
- Требования по покрытию в этом документе не нормируются — ориентир: зелёный полный `pytest tests/`.

---

*Testing analysis: 2026-05-04*
