# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository layout

The repo is two things stacked:

- **Repo root** — a thin Windows launcher (`run.ps1`, `teresa_gui.py`, `teresa.bat`) that orchestrates the pipeline. There is no Python package here.
- **`spec_classifier/`** — the actual codebase: a deterministic, rule-based Excel-spec classifier for six hardware vendors (Dell, Cisco CCW, HPE, Lenovo DCSC, xFusion, Huawei). Pipeline: `Excel → parse → normalize → classify → artifacts`. No ML; all classification is YAML rules + regex.

The deeper, frequently-updated reference for the pipeline (taxonomy, E-codes, business rules, alias tables, current state) lives in `spec_classifier/CLAUDE.md` — read that file when working inside `spec_classifier/`. Do not duplicate it here; update it there.

## Code-only repository policy

- The repo holds **only code**. Test fixtures, INPUT specs, OUTPUT runs, and the venv all live **outside the repo**.
- Default external roots (Windows): `%USERPROFILE%\Desktop\INPUT`, `%USERPROFILE%\Desktop\OUTPUT`, venv at `C:\venv`. Override via `spec_classifier/config.local.yaml` (gitignored; copy from `config.local.yaml.example`).
- `OUTPUT/`, `output/`, `test_data/`, `.venv/`, `commits.txt`, and `*.zip` are gitignored. Do not commit anything from those.
- `config.local.yaml` overlays `config.yaml` at runtime — same logic in both `spec_classifier/main.py:_load_config` and `spec_classifier/conftest.py:load_config`. Local file wins.

## Common commands

Run from the repo root unless noted. PowerShell.

```powershell
# Full pipeline: all vendors → batch_audit (rule + AI) → cluster_audit → pytest
.\run.ps1

# Variants
.\run.ps1 -NoAi                         # rule-based audit only (no OPENAI_API_KEY needed)
.\run.ps1 -Vendor dell                  # one vendor end-to-end
.\run.ps1 -TestsOnly                    # pytest only
.\run.ps1 -SkipTests                    # full run without pytest at the end
.\run.ps1 -Vendor huawei -NoAi -SkipTests   # smoke
```

Direct CLI (run from `spec_classifier/`):

```powershell
# Single file
python main.py --input <path.xlsx> --vendor <dell|cisco|hpe|lenovo|huawei|xfusion>

# Batch a directory
python main.py --batch-dir <path> --vendor <vendor> --output-dir <OUTPUT>

# Save / overwrite golden after a rule change
python main.py --input <path.xlsx> --vendor <vendor> --save-golden
python main.py --input <path.xlsx> --vendor <vendor> --update-golden    # interactive y/N

# Post-run audits
python batch_audit.py   --output-dir <OUTPUT> --no-ai            # rule-based, fast
python batch_audit.py   --output-dir <OUTPUT> --vendor hpe       # AI audit, one vendor
python cluster_audit.py --output-dir <OUTPUT> --dry-run          # discover candidates
```

Tests (run from `spec_classifier/`):

```powershell
pytest tests/ -v --tb=short                            # full suite
pytest tests/test_lenovo_rules_unit.py -v              # single file
pytest tests/test_regression.py::test_dl1 -v           # single test
pytest -k "lenovo and parser" -v                       # by keyword
pytest tests/ --collect-only                            # just enumerate
```

Tests gate on data availability via `conftest.py:pytest_sessionfinish`: the session **fails** if `skipped/total > 0.50` or if `passed == 0` while tests were collected. Missing `paths.input_root` is a hard error. To run unit-only without INPUT files, target specific files (e.g. `test_rules_unit.py`, `test_state_detector.py`, `test_normalizer.py`).

Make targets (`spec_classifier/Makefile`) wrap golden generation per vendor: `make generate_golden_dell`, `make generate_golden_cisco`, `make generate_golden_hpe`. Override INPUT root: `make generate_golden INPUT=/d/specs/INPUT`.

## Architecture

### Pipeline stages (`spec_classifier/main.py:_run_single`)

1. **Adapter dispatch** — `VENDOR_REGISTRY` in `main.py` maps `--vendor` → `VendorAdapter` subclass in `src/vendors/<vendor>/adapter.py`.
2. **Parse** — `adapter.parse(path)` returns `(raw_rows, header_row_index)`. Header location is vendor-specific (Dell sentinel `"Module Name"`; Cisco sheet `"Price Estimate"`; HPE sheet `"BOM"`; Lenovo `"Configuration"`; etc.). Note: `src/core/parser.py` is **dell-specific** despite living in `core/` — every other vendor has its own `src/vendors/<v>/parser.py`. This is known tech debt.
3. **Normalize** — `adapter.normalize(raw_rows)` produces `NormalizedRow` objects with `row_kind ∈ {HEADER, ITEM}` and the canonical fields the rules engine expects (see `src/vendors/base.py:VendorAdapter.normalize` docstring).
4. **Classify** — `RuleSet.load(rules_yaml)` (from `src/rules/rules_engine.py`) + `classify_row` (in `src/core/classifier.py`) yield `ClassificationResult(entity_type, state, device_type, hw_type, matched_rule_id, ...)`. Rules are regex-on-field; **first match wins**, so YAML rule order is load-bearing.
5. **Write artifacts** — `src/outputs/{json_writer,excel_writer,annotated_writer,branded_spec_writer}.py`. Each run produces a timestamped folder under `OUTPUT/<vendor>_run/run-YYYY-MM-DD__HH-MM-SS-<stem>/` with `classification.jsonl`, `run_summary.json`, `cleaned_spec.xlsx`, `<stem>_annotated.xlsx`, `unknown_rows.csv`, `header_rows.csv`, `rows_raw.json`, `rows_normalized.json`, `run.log`. Branded spec is **Dell-only** (gated by `adapter.generates_branded_spec()`).
6. **TOTAL aggregation** — batch mode also creates `run-…-TOTAL/` collecting the presentation files from every per-run folder.

### VendorAdapter contract (`src/vendors/base.py`)

To add a vendor: subclass `VendorAdapter`, implement `parse / normalize / can_parse / get_rules_file / get_vendor_stats / generates_branded_spec`, optionally override `get_source_sheet_name()` and `get_extra_cols()`, register in `VENDOR_REGISTRY` (`main.py`), append to `$ALL_VENDORS` (`run.ps1`), and add the vendor's directory to the GUI's active list (`teresa_gui.py`). The full recipe is in `spec_classifier/prompts/00_VENDOR-RECON.md`.

`get_extra_cols()` returns `[(NormalizedRow attr, Excel column header), …]` — used by `annotated_writer` for vendor-specific extension columns. HPE adds 5 columns, Cisco adds 2, others default to none.

### Post-run audit (`spec_classifier/batch_audit.py`, ~1500 LOC)

Reads `*_annotated.xlsx` from `OUTPUT/` and produces `audit_report.json`, `audit_summary.xlsx`, and `*_audited.xlsx` per file. Two layers:

- **E-codes E1–E18** — rule-based checks over classifier output. Severities range from BLOCKER (E2 = UNKNOWN with no rule) to INFO (E15 = BASE without device_type — by design). The full table with logic is in `spec_classifier/CLAUDE.md`.
- **AI mismatch** (optional, `OPENAI_API_KEY` required) — flags rows where an LLM disagrees with the pipeline. Disagreements are suppressed via `DEVICE_TYPE_ALIASES` and `_ALIASES` in `batch_audit.py`; these tables are **AI-mismatch suppression only**, not `hw_type` mappings (the YAML rule files own that).

Important: `batch_audit.py` reads from Excel (`pd.read_excel`), not from `classification.jsonl` — Excel leakage is known tech debt, do not "fix" it as part of unrelated work.

### Cluster audit (`spec_classifier/cluster_audit.py`)

Mines UNKNOWN / AI_MISMATCH rows from audited outputs and clusters them so a human can author new YAML rules. Output: `cluster_summary.xlsx` plus a `clusters` section appended to `audit_report.json`.

### Recommended workflow

`run pipeline → batch_audit → cluster_audit → review cluster_summary.xlsx → write/edit YAML rules → re-run → verify E2/E17 reduction`. Don't skip the audit step when changing rules: regression tests use frozen golden files, but audit catches new UNKNOWNs and taxonomy drift.

## Critical business rules — do not violate

These are the rules that keep flipping during edits. Source of truth for the long form is `spec_classifier/CLAUDE.md` § "БИЗНЕС-ПРАВИЛА"; the most-bitten:

- **`power_cord` has `hw_type=None` intentionally.** It is absent from `device_type_map` in every vendor YAML, with explicit comments. `batch_audit.py:_E8_NO_HW_TYPE_DEVICES = {"power_cord", "enablement_kit"}` excludes it from E8. Do not "fix" the missing mapping. The `power_cord ≈ cable` alias in `batch_audit.DEVICE_TYPE_ALIASES` is **only** for AI-mismatch suppression.
- **LOGISTIC = packaging, documents, freight only.** Power cords, stacking cables, rails, brackets are HW, not LOGISTIC.
- **BASE without `device_type`** is normal (E15 = INFO). **BASE with `device_type`** is valid; E6/E10 must not fire. Only `hw_type` on BASE triggers E10.
- **`is_factory_integrated=True`** rows are CONFIG; AI does not check them.
- **`hw_type` `applies_to`** is `[HW]` only — not `[HW, BASE]`.
- **YAML rule order matters.** Rules are evaluated top-to-bottom and first match wins. Reordering rule files mid-edit can change classification.

## Alias tables — what they are and aren't

`batch_audit.DEVICE_TYPE_ALIASES` (e.g. `ram=memory`, `nic=network_adapter`, `bezel=chassis`) is the **AI-mismatch suppression table**, not a `hw_type` mapping. Never use it to derive `hw_type` from `device_type`. The authoritative `device_type → hw_type` mapping is `device_type_map` in each `rules/<vendor>_rules.yaml` and may legitimately differ across vendors (e.g. Lenovo maps `bezel→accessory` while HPE keeps `bezel→chassis`).

## Tooling roles (`.cursor/`, GSD)

The repo carries a `.cursor/` tree (`.cursor/agents/`, `.cursor/skills/`, `.cursor/get-shit-done/`) used by the GSD (Get Shit Done) workflow when driving from Cursor. It is **gitignored** and not used by Claude Code directly — treat it as informational. The single source of truth for the development cycle (PRE-CHECK → PLAN → IMPLEMENT → POST-CHECK → AUDIT 1A–1G) is `spec_classifier/CLAUDE.md` and `spec_classifier/prompts/`.

## Where to look first

- Pipeline question, business rule, taxonomy, E-code, alias → `spec_classifier/CLAUDE.md`
- Run a vendor end-to-end on Windows → `run.ps1` / `LAUNCHER_README.md`
- Vendor adapter contract → `spec_classifier/src/vendors/base.py`
- Add a vendor → `spec_classifier/prompts/00_VENDOR-RECON.md`
- Recent state and commit log → `spec_classifier/CHANGELOG.md`, `spec_classifier/CURRENT_STATE.md`
- Rules authoring → `spec_classifier/docs/rules/RULES_AUTHORING_GUIDE.md`, `docs/taxonomy/hw_type_taxonomy.md`
