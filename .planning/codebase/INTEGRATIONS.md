# External Integrations

**Analysis Date:** 2026-05-04

## Project framing (Teresa)

Внешний контур — файловая система и опционально OpenAI. Нет БД, очередей или хостинга в коде пайплайна.

## File system & I/O layout

**Inputs:**
- Excel `.xlsx` от вендоров. Скрипт `run.ps1` для каждого вендор ожидает подкаталог `{input_root}/{vendor}/` с файлами (например `dell/`, `cisco/`). Корень задаётся в `config.local.yaml` (`input_root`) или по умолчанию `%USERPROFILE%\Desktop\INPUT` при разборе regex в `run.ps1`.
- В репозитории каталогов данных нет (политика «code-only» в комментариях `config.yaml`).

**Outputs:**
- Пишутся под `{output_root}/{vendor}_run/run-<stamp>-<stem>/`: JSONL/JSON/CSV логи нормализации и классификации, `cleaned_spec.xlsx`, аннотированные книги, при поддержке адаптера — `*_branded.xlsx`, `run_summary.json`, и т.д. (см. `spec_classifier/src/diagnostics/run_manager.py`, writers в `spec_classifier/src/outputs/`).
- `batch_audit.py` / `cluster_audit.py` добавляют отчёты на корне output (`audit_report.json`, сводные xlsx) и помечают `*_audited.xlsx` внутри run-папок при соответствующих режимах.

**Gitignore:**
- В корневом `.gitignore` указан `OUTPUT/` (и политика локальных данных); точный список — в файле репо.

## OpenAI (optional)

**Usage:**
- При запуске без `-NoAi` в `run.ps1` после rule-only аудита вызывается `python batch_audit.py --output-dir ... --model gpt-4o-mini` (ключ из `OPENAI_API_KEY`).
- GUI может сохранять ключ через `setx` (`LAUNCHER_README.md`).

**When absent:**
- Пайплайн `main.py` и rule-only аудит работают без сети и без ключа.

## Third-party libraries (runtime)

- **openpyxl** — парсинг и генерация xlsx.
- **pandas** — используется в аудитах и смежной обработке таблиц.

## CI / deployment integrations

- Каталога `.github/workflows/` в репо нет — автоматический CI в репозитории не описан файлами на дату карты.

---

*Integration audit: 2026-05-04*
