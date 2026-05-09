# Architecture

**Analysis Date:** 2026-05-04

## Project framing (Teresa)

Пайплайн: **Excel → парсинг (адаптер вендора) → нормализация → классификация по YAML-правилам → артефакты** (очищенная спецификация, аннотированный источник, брендированная книга где поддержано). Опционально: **batch_audit** (правила E1–E18 ± LLM) и **cluster_audit**. Выбор вендора на уровне CLI; автодетект «чей файл» для смешанных каталогов опирается на `VendorAdapter.can_parse()` (дешёвая проверка книги).

**Исключение из рантайма:** `spec_classifier/prompts/` — материалы для AI-ассистента при разработке, не импортируются пайплайном.

## Pattern overview

**Overall:** модульный офлайн-процессор с **Strategy по вендору** (адаптеры) и общим ядром классификации.

**Characteristics:**
- Однопроходный CLI-запуск на файл или пакет (`main.py`).
- Правила данных и таксономии — в YAML per vendor; код — `RuleSet` + `classify_row`.
- Состояние строки (PRESENT / ABSENT / DISABLED) определяется в классификации через `detect_state` из `src/core/state_detector.py`, используемый из `src/core/classifier.py`.

## Layers

**CLI / orchestration:**
- `spec_classifier/main.py` — загрузка конфига (мердж с `config.local.yaml`), маршрутизация по `VENDOR_REGISTRY`, цикл `_run_single`: parse → normalize → load rules → classify → write artifacts.
- Корневые `run.ps1`, `teresa_gui.py` — внешний запуск без изменения модели данных.

**Vendor adapters** (`spec_classifier/src/vendors/<vendor>/`):
- Реализуют контракт `VendorAdapter` в `spec_classifier/src/vendors/base.py`: `can_parse`, `parse`, `normalize`, `get_rules_file`, `get_vendor_stats`, `generates_branded_spec`, опционально `get_extra_cols`, `get_source_sheet_name`.
- Регистрация имён вендоров: словарь `VENDOR_REGISTRY` в `main.py` (dell, cisco, hpe, lenovo, huawei, xfusion).

**Core** (`spec_classifier/src/core/`):
- `normalizer.py` — общая модель нормализованной строки и логика уровня ядра.
- `parser.py` — общие/legacy-помощники; фактические форматы вендоров разбираются в `vendors/*/parser.py` (см. drift в документации про Dell-sentinel).
- `classifier.py` — приоритетное сопоставление правил, второй проход для `device_type` / `hw_type` где применимо.
- `state_detector.py` — извлечение `State`.

**Rules** (`spec_classifier/src/rules/rules_engine.py`):
- Загрузка YAML, матчинг базовых правил и карт `device_type` / `hw_type`.

**Outputs** (`spec_classifier/src/outputs/`):
- Запись cleaned / annotated / branded Excel, JSONL классификации, вспомогательные дампы.

**Diagnostics** (`spec_classifier/src/diagnostics/`):
- Папки прогона, статистика, `run_summary.json`.

**Post-process audits (отдельные процессы):**
- `spec_classifier/batch_audit.py` — валидация и разметка проблем в Excel-выходах; опционально вызов модели OpenAI.
- `spec_classifier/cluster_audit.py` — кластеризация проблемных строк для обзора.

## Data flow

**Typical CLI run (`_run_single` in `main.py`):**

1. Выбор адаптера по аргументу `--vendor`.
2. `adapter.parse(path)` → сырые строки + индекс строки заголовка.
3. `adapter.normalize` → список объектов, совместимых с `NormalizedRow`.
4. `RuleSet.load` из пути `adapter.get_rules_file()`.
5. Для каждой строки: `classify_row(row, ruleset)` (внутри — `detect_state`, матчинг правил).
6. Сохранение артефактов в run-folder; при batch — копирование в TOTAL через `run_manager`.

**State:** состояние процесса небольшое; основной «state» домена — поля в классификации и файлы на диске.

## Key abstractions

- **`VendorAdapter`** — граница вендор ↔ общее ядро (`spec_classifier/src/vendors/base.py`).
- **`NormalizedRow` / `RowKind`** — единый вход классификатора (`normalizer.py`).
- **`ClassificationResult`** — сущность + состояние + идентификатор правила + типы (`classifier.py`).
- **`RuleSet`** — скомпилированные YAML-правила (`rules_engine.py`).

## Entry points

- **`spec_classifier/main.py`** — основной CLI пайплайна.
- **`run.ps1`** — полный цикл: пайплайн по вендорам, аудиты, pytest.
- **`batch_audit.py`**, **`cluster_audit.py`** — автономные CLI аудита.
- **`teresa.bat` / `teresa_gui.py`** — GUI-лаунчер поверх `run.ps1`.

## Error handling

- Исключения в `_run_single` логируются и приводят к ненулевому exit code; YAML-ошибки отдельно перехватываются.
- Аудиты имеют собственный `main` и коды выхода (см. концы файлов).

---

*Architecture analysis: 2026-05-04*
