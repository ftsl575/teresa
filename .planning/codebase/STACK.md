# Technology Stack

**Analysis Date:** 2026-05-04

## Project framing (Teresa)

**Teresa** — локальный классификатор строк BOM из Excel-спецификаций шести вендоров (Dell, Cisco, HPE, Lenovo, Huawei, xFusion): на вход `.xlsx` из конфигураторов, на выход нормализованные артефакты и размеченные книги. Репозиторий держит код и правила; типичные данные и результаты — вне репо (`INPUT` / `OUTPUT`, см. `INTEGRATIONS.md`). Каталог `spec_classifier/prompts/` — **рабочие промпты для разработки через AI**, не зависимости рантайма.

## Languages

**Primary:**
- Python 3 — всё приложение: CLI (`spec_classifier/main.py`), аудиты (`batch_audit.py`, `cluster_audit.py`), GUI-обёртка (`teresa_gui.py`).

**Secondary:**
- PowerShell — оркестрация полного прогона (`run.ps1`).
- YAML — правила классификации (`spec_classifier/rules/<vendor>_rules.yaml`), конфиг (`spec_classifier/config.yaml`, необязательный `config.local.yaml`).
- Markdown — документация (`spec_classifier/docs/`), промпты разработки (`spec_classifier/prompts/`), корневые README.

## Runtime

**Environment:**
- CPython (версия не зафиксирована в репо через `pyproject`; ориентир — локальная установка разработчика).
- Windows — основной сценарий (`run.ps1`, `teresa.bat`, пути в документации).

**Dependencies** (`spec_classifier/requirements.txt`):
- `openpyxl>=3.1.0` — чтение/запись Excel.
- `pandas>=2.0.0` — табличная обработка (в т.ч. аудиты).
- `pyyaml>=6.0` — загрузка правил и конфига.
- `pytest>=7.0.0` — тесты.

**GUI (опционально):**
- `requirements-gui.txt` — PyQt6 для `teresa_gui.py`; CLI и пайплайн PyQt не требуют.

## Frameworks

**Core:**
- Нет веб-фреймворка: офлайн CLI и скрипты.

**Testing:**
- `pytest` — единый раннер; по состоянию на дату анализа: **775** тестов собирается (`python -m pytest tests/ --collect-only` из `spec_classifier/`).

## Configuration

**Файлы:**
- `spec_classifier/config.yaml` — пути по умолчанию (`paths.input_root`, `paths.output_root`), `cleaned_spec`, карта `vendor_rules` → YAML.
- `spec_classifier/config.local.yaml` — локальные абсолютные пути и переопределения; в `.gitignore` (не коммитится).
- `run.ps1` дополнительно подставляет `%USERPROFILE%\Desktop\INPUT` и `\OUTPUT`, если ключи прочитаны из `config.local.yaml`.

## Platform requirements

**Development / production:**
- Машина пользователя с Python и Excel-совместимыми входами; сеть нужна только если включён AI-режим `batch_audit` (OpenAI API).

---

*Stack analysis: 2026-05-04*
