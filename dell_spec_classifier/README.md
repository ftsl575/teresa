# Dell Specification Classifier

Pipeline for classifying Dell Excel specifications: Excel → parse → normalize → classify → run artifacts + cleaned spec. Classification is deterministic and rule-based (YAML + regex on `module_name` / `option_name`).

For implementation details and architecture, see [docs/TECHNICAL_OVERVIEW.md](docs/TECHNICAL_OVERVIEW.md).

## Design and Planning Documents

The following documents guided development and are kept as reference. They are **completed** and are not the source of truth for current behavior; use [TECHNICAL_OVERVIEW.md](docs/TECHNICAL_OVERVIEW.md) and this README for that.

- **[docs/architecture/dell_mvp_technical_spec.md](docs/architecture/dell_mvp_technical_spec.md)** — Original MVP technical architecture and specification (phases 0–10, row_kind, entity types, rules, tests). Created February 2026; describes the baseline design before implementation.
- **[docs/roadmap/vnext_plan1.md](docs/roadmap/vnext_plan1.md)** — vNext execution plan: test data paths, golden files, full regression (dl1–dl5), UNKNOWN closure, device_type, and documentation. Created 2026-02-23; phases 0–3 and related prompts have been executed.

---

## Installation

- **Requirements:** Python 3.10+, and dependencies from `requirements.txt` (e.g. `pandas`, `openpyxl`, `PyYAML`).
- From the project root (`dell_spec_classifier/`):
  ```bash
  pip install -r requirements.txt
  ```
- No system-wide install; run `main.py` from this directory or pass paths relative to CWD.

---

## Quick Start

```bash
cd dell_spec_classifier
python main.py --input test_data/dl1.xlsx
```

This creates a run folder under `output/run_YYYYMMDD_HHMMSS/` with classification artifacts and `cleaned_spec.xlsx`. Use `--output-dir` to change the output base directory.

---

## CLI Reference

| Option | Description |
|--------|-------------|
| `--input` | **Required.** Path to input Excel file (`.xlsx`). |
| `--config` | Path to config YAML (default: `config.yaml`). |
| `--output-dir` | Base directory for run folders (default: `output`). |
| `--save-golden` | Run pipeline and save `golden/<stem>_expected.jsonl` for the given input (no prompt). |
| `--update-golden` | Run pipeline and overwrite golden after interactive confirmation (`y`/`n`). |

Paths are resolved relative to the current working directory unless absolute.

---

## Run Artifacts

Each run creates a timestamped folder under `output/` (or `--output-dir`) containing:

| File | Description |
|------|-------------|
| `rows_raw.json` | Raw parsed rows from Excel. |
| `rows_normalized.json` | Normalized rows with `row_kind`. |
| `classification.jsonl` | One JSON object per line: `row_kind`, `entity_type`, `state`, `matched_rule_id`, `device_type` (when applicable), `warnings`. |
| `unknown_rows.csv` | ITEM rows classified as UNKNOWN. |
| `header_rows.csv` | HEADER rows. |
| `run_summary.json` | Counts: `total_rows`, `header_rows_count`, `item_rows_count`, `entity_type_counts`, `state_counts`, `unknown_count`, `rules_stats`, `device_type_counts`. |
| `cleaned_spec.xlsx` | Filtered spec per `config.yaml` (e.g. BASE/HW/SOFTWARE/SERVICE, PRESENT only). |
| `annotated_source.xlsx` | Source rows with added Entity Type and State columns. |
| `run.log` | Log for this run. |

---

## entity_type

Eight possible entity types for ITEM rows (HEADER rows have no entity type):

| Value | Description |
|-------|-------------|
| BASE | Base system / chassis (e.g. Base, PowerEdge R660). |
| HW | Hardware (processors, memory, drives, power supply, NICs, etc.). |
| CONFIG | Configuration (e.g. RAID, BIOS). |
| SOFTWARE | Software / OS / licenses. |
| SERVICE | Services (ProSupport, warranty, deployment). |
| LOGISTIC | Logistics (shipping, documentation, power cords, cables). |
| NOTE | Informational notes (e.g. "supports ONLY", "included with"). |
| UNKNOWN | No rule matched. |

---

## row_kind

- **HEADER:** Row where Module Name, Option Name, and SKUs are all empty (section separator). Not classified by entity rules.
- **ITEM:** Any other row; classified by priority (BASE → SERVICE → LOGISTIC → SOFTWARE → NOTE → CONFIG → HW → UNKNOWN).

---

## State

For ITEM rows, state is derived from `option_name` (e.g. "No TPM", "Disabled"):

| Value | Meaning |
|-------|---------|
| PRESENT | Option is present / included. |
| ABSENT | Option is not included (e.g. "No HDD", "Empty"). |
| DISABLED | Option is disabled. |

---

## Rules Change Process

1. **Edit rules** in `rules/dell_rules.yaml` (entity rules and/or `device_type_rules`).
2. **Add or update unit tests** in `tests/test_rules_unit.py` or `tests/test_device_type.py` for the new or changed patterns.
3. **Run the pipeline** on dl1–dl5: `python main.py --input test_data/dlN.xlsx` for N=1..5.
4. **Inspect** `unknown_rows.csv` and `run_summary.json` in the run folder; confirm `unknown_count` and classifications are as intended.
5. **Update golden** if the change is intentional: `python main.py --input test_data/dlN.xlsx --update-golden` (answer `y`), or use `--save-golden` for non-interactive/CI.
6. **Run the full test suite:** `pytest tests/ -v`.
7. **Update CHANGELOG.md** and commit.

---

## How to Run Tests

From `dell_spec_classifier/`:

```bash
# All tests
pytest tests/ -v --tb=short

# Unit tests only (no Excel files needed)
pytest tests/test_rules_unit.py tests/test_state_detector.py tests/test_normalizer.py -v

# Smoke and regression (require test_data/dl1.xlsx … dl5.xlsx)
pytest tests/test_smoke.py tests/test_regression.py -v

# Device-type and unknown-threshold checks
pytest tests/test_device_type.py tests/test_unknown_threshold.py -v
```

Tests that depend on `test_data/*.xlsx` will **skip** with a clear message if the file is missing.

---

## Note on test_data

Test Excel files (`test_data/dl1.xlsx` … `dl5.xlsx`) are **not** in git. Place them locally under `dell_spec_classifier/test_data/` so that:

- Smoke and regression tests can run (otherwise they are skipped).
- Golden generation works: `python main.py --input test_data/dlN.xlsx --save-golden`.

You can regenerate golden for all five files with:

```bash
# PowerShell
.\scripts\generate_golden.ps1
```

---

## Regression

Regression tests compare the current pipeline output to **golden files** row-by-row (`entity_type`, `state`, `matched_rule_id`, `device_type`, `skus`).

- **Generate golden** (first time or after adding a new input file):
  ```bash
  python main.py --input test_data/dl1.xlsx --save-golden
  ```
  This creates `golden/dl1_expected.jsonl`. Repeat for `dl2.xlsx`, etc., or use `scripts/generate_golden.ps1`.

- **Update golden** after intentionally changing rules or logic (prompts for confirmation):
  ```bash
  python main.py --input test_data/dl1.xlsx --update-golden
  ```
  Answer `y` to overwrite `golden/dl1_expected.jsonl`. In non-interactive environments use `--save-golden` instead.

- **Run regression tests**:
  ```bash
  pytest tests/test_regression.py -v
  ```
  Each test runs the pipeline for one input file, loads the corresponding `golden/<stem>_expected.jsonl`, and fails if any row differs.

---

## config.yaml reference

- **`rules_file`:** Path to the rules YAML (default: `rules/dell_rules.yaml`).
- **`cleaned_spec`:** `include_types` (entity types to include in cleaned spec), `include_only_present`, `exclude_headers`. Output columns for the cleaned Excel are fixed in `excel_writer.py`; there is no `output_columns` config parameter.
