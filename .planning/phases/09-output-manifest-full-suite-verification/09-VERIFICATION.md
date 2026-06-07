# Phase 9: Full-Suite Verification

**Date:** 2026-06-07
**Scope:** Plans 09-01, 09-02, 09-03 combined — v1.2 output-manifest + vendor-detector dedup
**Executed by:** 09-03 plan executor (auto-approved checkpoint)

---

## D-09: Full pytest suite results

**Command:** `cd C:\Users\G\Desktop\teresa\spec_classifier && python -m pytest tests/ -q --tb=short`

**Results:**
- **Passed:** 770
- **xfailed:** 1
- **Skipped:** 0
- **Failed:** 0
- **Total:** 771
- **Duration:** 27.10s

**Skip-gate:** 0 / 771 = 0.00% < 50% — PASS
**Passed > 0:** YES — PASS

All 770 tests pass. Suite is fully green within the skip-gate.

---

## Goldens byte-equal

**Command:** `python -m pytest tests/ -q --tb=short -k "golden or regression"`

**Results:** 71 passed, 700 deselected — all golden/regression tests PASS

**No `--update-golden` used** anywhere in v1.2 (Plans 09-01, 09-02, 09-03). All golden
fixtures (`spec_classifier/golden/*_expected.jsonl`) remain byte-equal from before v1.2.

---

## Structural import cleanup verification

```
Import cleanup verified: OK
test_output_structure.py extensions: OK
```

- `test_batch_audit.py`: zero references to `detect_vendor_from_path`
- `test_cluster_audit.py`: zero references to `_detect_vendor_from_path`, `ccw_export`
- `test_output_structure.py`: contains both `test_manifest_readme_exists_after_run` and `test_output_root_top_level_layout`

---

## D-09: Real-data operator run

**Command:** `python main.py --batch-dir C:\Users\G\Desktop\INPUT\dell --vendor dell --output-dir C:\Users\G\Desktop\OUTPUT_TEST_09`

**Input:** C:\Users\G\Desktop\INPUT\dell\ — 5 files (dl1.xlsx, dl2.xlsx, dl3.xlsx, dl4.xlsx, dl5.xlsx)

**Result:** Batch complete — 5 processed, 0 skipped, 0 failed.

### output_root top-level tree

```
OUTPUT_TEST_09/
├── README.md
├── READY/
│   └── dell/
│       ├── dl1/ Коммерческое предложение_dl1.xlsx
│       ├── dl2/ Коммерческое предложение_dl2.xlsx
│       ├── dl3/ Коммерческое предложение_dl3.xlsx
│       ├── dl4/ Коммерческое предложение_dl4.xlsx
│       └── dl5/ Коммерческое предложение_dl5.xlsx
└── SPLIT/
    └── dell/
        ├── dl1/ (classification.jsonl, cleaned_spec.xlsx, dl1_annotated.xlsx, header_rows.csv, rows_normalized.json, rows_raw.json, run.log, run_summary.json, unknown_rows.csv)
        ├── dl2/ (same 9 artifacts)
        ├── dl3/ (same 9 artifacts)
        ├── dl4/ (same 9 artifacts)
        └── dl5/ (same 9 artifacts)
```

**Top-level contains:** `README.md`, `READY/`, `SPLIT/` — no legacy dirs (`run-*`, `*_run`, `*-TOTAL`). AUDIT/ absent (written by batch_audit.py, not tested in this run).

**Verdict:** SC#2 PASS — no legacy layout present. README.md exists at output_root.

### README.md contents (output_root/README.md)

```markdown
# Выходные артефакты классификатора

Папка содержит результаты классификации аппаратных спецификаций.
Артефакты сгруппированы по трём директориям (`READY/`, `SPLIT/`, `AUDIT/`).
Структура вложения: `<bucket>/<vendor>/<spec>/`.

---

## READY — Готовые документы для заказчика

| Файл | Директория | Назначение |
|------|-----------|------------|
| `Коммерческое предложение_<spec>.xlsx` | `READY/<vendor>/<spec>/` | Готовое коммерческое предложение для заказчика |

---

## SPLIT — Технические артефакты классификации

| Файл | Директория | Назначение |
|------|-----------|------------|
| `cleaned_spec.xlsx` | `SPLIT/<vendor>/<spec>/` | Очищенная спецификация (исходные данные без служебных строк) |
| `classification.jsonl` | `SPLIT/<vendor>/<spec>/` | Результаты классификации строк в формате JSONL |
| `<spec>_annotated.xlsx` | `SPLIT/<vendor>/<spec>/` | Аннотированная спецификация с классификацией каждой строки |
| `rows_raw.json` | `SPLIT/<vendor>/<spec>/` | Сырые данные строк до нормализации |
| `rows_normalized.json` | `SPLIT/<vendor>/<spec>/` | Нормализованные данные строк |
| `run_summary.json` | `SPLIT/<vendor>/<spec>/` | Сводка по запуску (статистика, хэши файлов) |
| `unknown_rows.csv` | `SPLIT/<vendor>/<spec>/` | Строки с неопределённым типом сущности |
| `header_rows.csv` | `SPLIT/<vendor>/<spec>/` | Заголовочные строки из спецификации |
| `run.log` | `SPLIT/<vendor>/<spec>/` | Лог выполнения классификатора |

---

## AUDIT — Результаты аудита и кластеризации

| Файл | Директория | Назначение |
|------|-----------|------------|
| `<spec>_annotated_audited.xlsx` | `AUDIT/<vendor>/<spec>/` | Аннотированная спецификация с результатами E-code аудита |
| `audit_report.json` | `AUDIT/` | Сводный отчёт аудита по всем спецификациям |
| `audit_summary.xlsx` | `AUDIT/` | Таблица результатов аудита (все ошибки по всем файлам) |
| `cluster_summary.xlsx` | `AUDIT/` | Сводка кластеризации неизвестных и неклассифицированных строк |
```

Three sections present: READY, SPLIT, AUDIT. Russian (Cyrillic) purpose text confirmed. 14 artifact rows total.

---

## Summary of success criteria

| Criterion | Status |
|-----------|--------|
| test_run_manager.py exists with TestDetectVendorFromPath (8 methods) | PASS |
| test_run_manager.py includes manifest unit tests (3 functions) | PASS |
| test_batch_audit.py: no detect_vendor_from_path references | PASS |
| test_cluster_audit.py: no _detect_vendor_from_path/ccw_export/old aliases | PASS |
| test_output_structure.py: README presence + layout assertions added | PASS |
| Full pytest suite: 770 passed, 0 failed, skip ratio 0% < 50% | PASS |
| Goldens byte-equal, no --update-golden used | PASS |
| README.md exists at output_root after real-data run | PASS |
| No legacy dirs (run-*, *_run, *-TOTAL) in output_root | PASS |

---

*Verification date: 2026-06-07*
*Executor: claude-sonnet-4-6 (09-03 plan)*
