# Spec Classifier — Technical Overview (Multivendor)

This document describes the **actual** implementation of the project (code in the repository). Sources: code in `src/`, `main.py`, tests in `tests/`, `config.yaml`.

---

## 1. System purpose

The system is a **pipeline** for classifying vendor specifications (Dell, Cisco CCW, HPE, Lenovo, xFusion, Huawei) in Excel format:

- **Input:** one Excel file (`.xlsx`) with a specification table.
- **Output:**
  - a run folder `{vendor}_run/run-YYYY-MM-DD__HH-MM-SS-<stem>/` (e.g. `dell_run/run-2026-02-28__13-24-32-dl1/`) under `output_dir`, with artifacts (JSON, CSV, Excel);
  - cleaned specification `cleaned_spec.xlsx` (only selected types and state);
  - annotated source file `<stem>_annotated.xlsx` (all rows + six columns: Entity Type, State, device_type, hw_type, row_kind, matched_rule_id);
  - branded specification `<stem>_branded.xlsx` (grouped by server and entity type sections).

Classification is **deterministic**, based on rules from YAML (regular expressions on the `module_name` and `option_name` fields). Rows are divided into **HEADER** (separators) and **ITEM** (line items); for ITEM rows, an entity type (BASE, HW, SOFTWARE, SERVICE, LOGISTIC, NOTE, CONFIG, UNKNOWN) and state (PRESENT, ABSENT, DISABLED) are assigned.

Supported vendors: **Dell** (Dell spec export, header "Module Name"), **Cisco CCW** (Cisco Commerce Workspace export, sheet "Price Estimate", header "Line Number" + "Part Number"), **HPE** (QuoteBuilder BOM, sheet "BOM", columns Product #, Product Description), **Lenovo** (DCSC export, sheet "Configuration" or first sheet), **xFusion** (FusionServer eDeal export), **Huawei** (eDeal export for ICT/Server/Storage/WLAN). Vendor is set with the `--vendor {dell,cisco,hpe,lenovo,huawei,xfusion}` flag.

---

## 2. Pipeline architecture (step by step)

Implemented sequence in `main.py`:

1. **Config loading** — `config.yaml` (UTF-8, `yaml.safe_load`). The rules path is taken via `adapter.get_rules_file()`, which returns the value from `config["vendor_rules"][vendor]` (or fallback). Dell: `rules/dell_rules.yaml`; Cisco: `rules/cisco_rules.yaml`; HPE: `rules/hpe_rules.yaml`; Lenovo: `rules/lenovo_rules.yaml`; Huawei: `rules/huawei_rules.yaml`; xFusion: `rules/xfusion_rules.yaml`.
2. **Excel parsing** — `adapter.parse(str(input_path))` (vendor-specific):
   - Dell: finds the header row by the cell `"Module Name"` in the first 20 rows (`src.vendors.dell.adapter` → `src.core.parser`); note: `src/core/parser.py` is Dell-specific despite living in `core/` — a known tech-debt item;
   - Cisco: finds the header row by the simultaneous presence of `"Line Number"` and `"Part Number"` on the sheet `"Price Estimate"` (`src.vendors.cisco.parser`);
   - HPE: reads sheet `"BOM"`, strictly first row is the header (no preamble); detects data end by the sentinel `"total"` (`src.vendors.hpe.parser`);
   - Lenovo/xFusion/Huawei: vendor-specific parsers in `src/vendors/<vendor>/parser.py`.
3. **Normalization** — `adapter.normalize(raw_rows)` (vendor-specific):
   - Dell: `src.core.normalizer.normalize_row` → `NormalizedRow`;
   - Cisco: `src.vendors.cisco.normalizer.normalize_cisco_rows` → `CiscoNormalizedRow` (duck-type compatible with NormalizedRow, contains additional Cisco fields);
   - HPE: `src.vendors.hpe.normalizer.normalize_hpe_rows` → `HPENormalizedRow` (duck-type compatible with NormalizedRow; vendor fields: `product_type`, `extended_price`, `lead_time`, `config_name`, `is_factory_integrated`);
   - Lenovo/xFusion/Huawei: vendor-specific normalizers in `src/vendors/<vendor>/normalizer.py`.
4. **Rules loading** — `src.rules.rules_engine.RuleSet.load(rules_path)` (YAML, UTF-8). Rules are organized by attribute: `base_rules`, `service_rules`, `logistic_rules`, `software_rules`, `note_rules`, `config_rules`, `hw_rules`, plus `get_state_rules()` from `state_rules.absent_keywords`.
5. **Classification** — for each normalized row `src.core.classifier.classify_row(row, ruleset)`:
   - if `row_kind == HEADER` → result with `entity_type=None`, `state=None`, `matched_rule_id="HEADER-SKIP"`;
   - otherwise: first `detect_state(option_name, state_rules)` (PRESENT/ABSENT/DISABLED), then rules checked by priority: BASE → SERVICE → LOGISTIC → SOFTWARE → NOTE → CONFIG → HW; no match → UNKNOWN.
6. **Run folder creation** — `{vendor}_run/run-YYYY-MM-DD__HH-MM-SS-<stem>/` is created under `output_dir` via `create_run_folder(vendor_base, input_filename, stamp)`, where `vendor_base = output_dir / f"{vendor}_run"` (e.g. `dell_run/run-2026-02-28__13-24-32-dl1/`).
7. **Artifact saving:**
   - `src.outputs.json_writer`: `save_rows_raw`, `save_rows_normalized`, `save_classification`, `save_unknown_rows`, `save_header_rows`;
   - `src.diagnostics.stats_collector`: `collect_stats(classification_results)` and `save_run_summary(stats, run_folder)`;
   - `src.outputs.excel_writer.generate_cleaned_spec(...)` → `cleaned_spec.xlsx`;
   - `src.outputs.annotated_writer.generate_annotated_source_excel(...)` → `<stem>_annotated.xlsx`;
   - `src.outputs.branded_spec_writer.generate_branded_spec(...)` → `<stem>_branded.xlsx` (only when `adapter.generates_branded_spec()` returns True).
   **Batch mode:** a TOTAL folder is created via `create_total_folder()` and three presentation files are copied via `copy_to_total()`.
8. **Optional: golden** — with flags `--save-golden` or `--update-golden`, golden rows are built and written to `golden/<stem>_expected.jsonl`; for `--update-golden`, confirmation is requested (y/n) before overwriting.
9. **Logging** — after the run folder is created, a `FileHandler(run_folder / "run.log")` is added to the root logger. A brief summary is printed to stdout (total_rows, header_rows_count, item_rows_count, entity_type_counts, unknown_count, run_folder).

Errors: if the file is missing or YAML is invalid — message to stderr and `exit(1)`; on pipeline exception — `log.exception` and `return 1`.

---

## 3. Input/output formats

**Input**

- **Dell:** first sheet, header row located by cell `"Module Name"` in the first 20 rows. Expected columns: Module Name, Option Name, SKUs, Qty, Option List Price (Group Name, Group ID, Product Name, Option ID optional).
- **Cisco CCW:** sheet `"Price Estimate"`, header row — by simultaneous presence of `"Line Number"` + `"Part Number"` in the first 100 rows.
- **HPE:** sheet `"BOM"`, first row is header (no preamble). Expected columns: Product #, Product Description, Qty, Unit Price (USD), Config Name.
- **Lenovo/xFusion/Huawei:** vendor-specific format; see `docs/user/USER_GUIDE.md` for details.
- **Config:** `config.yaml` — keys `cleaned_spec` (incl. `include_types`, `include_only_present`, `exclude_headers`) and `vendor_rules`.

**Output (in `run_folder`)**

| File | Description |
|------|-------------|
| `rows_raw.json` | Raw rows (list of dict), as after the parser; `json.dump(..., indent=2, ensure_ascii=False)`. |
| `rows_normalized.json` | Normalized rows with `row_kind` and `NormalizedRow` fields. |
| `classification.jsonl` | One row — one JSON: `row_kind`, `entity_type`, `state`, `matched_rule_id`, `warnings`. |
| `unknown_rows.csv` | Only ITEM rows with `entity_type == UNKNOWN`; encoding UTF-8-sig. |
| `header_rows.csv` | Only rows with `row_kind == HEADER`; UTF-8-sig. |
| `run_summary.json` | Aggregates: `total_rows`, `header_rows_count`, `item_rows_count`, `entity_type_counts`, `state_counts`, `unknown_count`, `rules_stats`, `device_type_counts`, `hw_type_counts`, `hw_type_null_count`, `rules_file_hash`, `input_file`, `run_timestamp`. |
| `cleaned_spec.xlsx` | ITEM subset: types from `config["cleaned_spec"]["include_types"]`, with `include_only_present` only state PRESENT. Columns: Group Name, Group ID, Module Name, Option Name, SKUs, Qty, Option ID, Unit Price, Device Type, HW Type, Entity Type, State. |
| `<stem>_annotated.xlsx` | Copy of the source sheet (row-by-row), with six columns added: Entity Type, State, device_type, hw_type, row_kind, matched_rule_id; rows not deleted; written with `header=False`. |
| `<stem>_branded.xlsx` | Branded specification: grouped by BASE (server) and entity type sections; columns SKU, Option Name, Qty, Price. Rows before the first BASE go into a preamble block. Only for vendors where `adapter.generates_branded_spec()` returns True. |
| `run.log` | Text log of pipeline stages. |

Entity types in code: `EntityType` in `src/core/classifier.py` — BASE, HW, CONFIG, SOFTWARE, SERVICE, LOGISTIC, NOTE, UNKNOWN. States: `State` in `src/core/state_detector.py` — PRESENT, ABSENT, DISABLED.

---

## 4. CLI and operation modes

Entry point: `main.py`. Arguments (argparse):

| Argument | Required | Description |
|----------|----------|-------------|
| `--input` | yes (single-file mode) | Path to input Excel. |
| `--batch-dir` | yes (batch mode) | Directory with .xlsx; all files are processed; per-run folders and a TOTAL folder are created. |
| `--config` | no (default `config.yaml`) | Path to YAML config. |
| `--vendor` | no (default: `dell`) | `dell`, `cisco`, `hpe`, `lenovo`, `huawei`, or `xfusion`. Selects the parsing/normalization adapter and rules file. |
| `--output-dir` | no (default: `config paths.output_root`, otherwise `cwd/output`) | Directory for run sub-folders; `{vendor}_run/run-.../` is created inside. |
| `--save-golden` | flag | After pipeline, write result to `golden/<stem>_expected.jsonl` without confirmation. |
| `--update-golden` | flag | Same, but asks "Overwrite golden? [y/N]:"; if not y, write is skipped. |

Run folder naming: under `output_dir` a sub-dir `{vendor}_run` is created (e.g. `dell_run`, `cisco_run`, `hpe_run`, `lenovo_run`, `huawei_run`, `xfusion_run`), inside — **single run** — `run-YYYY-MM-DD__HH-MM-SS-<stem>/`; **batch** — same folders per file plus `run-YYYY-MM-DD__HH-MM-SS-TOTAL/` with aggregated presentation files.

Paths are resolved relative to the current working directory unless absolute paths are given. Examples:

```bash
python main.py --input "C:\Users\<USERNAME>\Desktop\INPUT\dl1.xlsx"
python main.py --input "C:\Users\<USERNAME>\Desktop\INPUT\dl1.xlsx" --save-golden
python main.py --input "C:\Users\<USERNAME>\Desktop\INPUT\dl1.xlsx" --update-golden
```

---

## 5. Golden / Regression

**Golden file format** — JSONL in `golden/<stem>_expected.jsonl` (e.g. `golden/dl1_expected.jsonl`). One row — one JSON object with fields:

- `source_row_index` (int)
- `row_kind` ("ITEM" | "HEADER")
- `entity_type` (string or null)
- `state` (string or null)
- `matched_rule_id` (string)
- `device_type` (string or null)
- `hw_type` (string or null)
- `skus` (list of strings)

Generation: when running with `--save-golden` or after confirmation with `--update-golden`, `main.py` calls `_build_golden_rows(normalized_rows, classification_results)` and `_save_golden(golden_rows, golden_path)`.

**Regression tests** — `tests/test_regression.py`. Parameterized by filename (`dl1.xlsx`, `dl2.xlsx`). For each file:

- if no input file in `paths.input_root` — test is skipped;
- if no `golden/<stem>_expected.jsonl` — test is skipped with a message about `--save-golden`;
- otherwise: the same pipeline (parse → normalize → load RuleSet → classify), build a list of records in golden format and compare row-by-row with the loaded golden on fields `entity_type`, `state`, `matched_rule_id`, `skus`; on mismatch — fail with row number and diff output.

---

## 6. Annotated export

Implementation: `src/outputs/annotated_writer.py`, function `generate_annotated_source_excel(raw_rows, normalized_rows, classification_results, original_excel_path, run_folder, *, header_row_index=None, sheet_name=None)`.

- The source Excel is read via `pandas.read_excel(..., header=None, sheet_name=...)`. The `sheet_name` parameter is passed from `adapter.get_source_sheet_name()` (in `main.py`): `None` → sheet at index 0 (Dell, Cisco); string → named sheet (HPE → `"BOM"`). The header row is passed as `header_row_index` from the adapter (result of `adapter.parse()`). The Dell parser is no longer called inside `annotated_writer`. This ensures correct operation for all vendors.
- Six columns are added to the table: "Entity Type", "State", "device_type", "hw_type", "row_kind", "matched_rule_id". In the header row, these cells contain the corresponding labels.
- For other rows, the classification result is taken by `source_row_index` (1-based row number in Excel). If `row_kind == ITEM` — the new cells are filled with `entity_type.value`, `state.value`, `device_type`, `hw_type`, `matched_rule_id`; otherwise — empty.
- Result saved to `run_folder / "<stem>_annotated.xlsx"` via `to_excel(..., index=False, header=False, engine="openpyxl")`, so the row count matches the source file.

Call is made in `main.py` after `generate_cleaned_spec`.

---

## 7. Project structure

Real structure from the repository:

```
spec_classifier/
├── main.py
├── config.yaml
├── rules/
│   ├── dell_rules.yaml
│   ├── cisco_rules.yaml       # Cisco rules (service_duration_months, bundles, etc.)
│   ├── hpe_rules.yaml         # HPE rules (device_type rules, BASE/HW/SERVICE/CONFIG/SOFTWARE/LOGISTIC)
│   ├── lenovo_rules.yaml
│   ├── huawei_rules.yaml
│   └── xfusion_rules.yaml
├── src/
│   ├── core/                  # parser (Dell-specific, see tech debt), normalizer, classifier, state_detector
│   ├── rules/                 # rules_engine.py
│   ├── outputs/               # json_writer, excel_writer, annotated_writer, branded_spec_writer
│   ├── diagnostics/           # run_manager, stats_collector
│   └── vendors/
│       ├── base.py            # VendorAdapter ABC
│       ├── dell/
│       │   └── adapter.py     # DellAdapter
│       ├── cisco/
│       │   ├── parser.py      # CCW parser
│       │   ├── normalizer.py  # CiscoNormalizedRow
│       │   └── adapter.py     # CiscoAdapter
│       ├── hpe/
│       │   ├── parser.py      # HPE BOM parser (sheet "BOM", no preamble)
│       │   ├── normalizer.py  # HPENormalizedRow
│       │   └── adapter.py     # HPEAdapter
│       ├── lenovo/
│       │   ├── parser.py      # Lenovo DCSC parser
│       │   ├── normalizer.py  # LenovoNormalizedRow
│       │   └── adapter.py     # LenovoAdapter
│       ├── huawei/
│       │   ├── parser.py      # Huawei eDeal parser
│       │   ├── normalizer.py  # HuaweiNormalizedRow
│       │   └── adapter.py     # HuaweiAdapter
│       └── xfusion/
│           ├── parser.py      # xFusion FusionServer parser
│           ├── normalizer.py  # XFusionNormalizedRow
│           └── adapter.py     # XFusionAdapter
├── tests/
│   ├── (Dell tests)
│   ├── test_cisco_parser.py / test_cisco_normalizer.py
│   ├── test_regression_cisco.py / test_unknown_threshold_cisco.py
│   ├── test_hpe_parser.py / test_hpe_normalizer.py / test_hpe_rules_unit.py
│   ├── test_regression_hpe.py / test_unknown_threshold_hpe.py
│   ├── test_lenovo_parser.py / test_lenovo_normalizer.py / test_lenovo_rules_unit.py
│   ├── test_huawei_parser.py / test_huawei_normalizer.py / test_regression_huawei.py
│   └── test_xfusion_parser.py / test_xfusion_normalizer.py
├── golden/
│   ├── dl1_expected.jsonl … dl5_expected.jsonl
│   ├── ccw_1_expected.jsonl, ccw_2_expected.jsonl
│   ├── hp1_expected.jsonl … hp8_expected.jsonl
│   ├── L1_expected.jsonl … L11_expected.jsonl
│   ├── hu1_expected.jsonl … hu5_expected.jsonl
│   └── xf1_expected.jsonl … xf10_expected.jsonl
├── <output_dir>/              # from config paths.output_root or cwd/output
│   ├── dell_run/
│   ├── cisco_run/
│   ├── hpe_run/
│   ├── lenovo_run/
│   ├── huawei_run/
│   └── xfusion_run/
└── docs/
    └── (see docs/DOCS_INDEX.md)
```

There is no separate module for saving `rules_stats.json`; rule statistics are part of `run_summary.json` in the `rules_stats` field.

---

## 8. Testing strategy

- **Smoke** (`tests/test_smoke.py`): one run on `dl1.xlsx` (from `paths.input_root`), check that all listed artifacts are created in the run folder. Skipped if file is missing.
- **Vendor unit tests**: parser, normalizer, rules-unit tests per vendor.
- **Regression tests** (`test_regression*.py`): row-by-row comparison with golden for each vendor.
- **Unknown threshold tests**: `test_unknown_threshold*.py` — gate (`unknown_count == 0`) and guardrail (≤5%) per vendor.
- **Unit tests:**
  - `test_normalizer.py` — `detect_row_kind` (HEADER/ITEM), `normalize_row` (SKUs, qty, option_price, NaN/empty values).
  - `test_state_detector.py` — `detect_state` by rules from YAML (ABSENT, DISABLED, PRESENT by default).
  - `test_rules_unit.py` — classification: HEADER→HEADER-SKIP, BASE, SOFTWARE, HW, SERVICE, LOGISTIC, NOTE, CONFIG, UNKNOWN, state in result.
  - `test_excel_writer.py` — presence of `cleaned_spec.xlsx`, absence of HEADER in it, only types from `include_types`, only PRESENT with `include_only_present`.
  - `test_annotated_writer.py` — presence of `<stem>_annotated.xlsx`, row count matches source, presence of columns Entity Type, State, device_type, hw_type, row_kind, matched_rule_id with filled values for ITEM.
- **CLI** (`test_cli.py`): runs `main.py --input ... --config config.yaml --output-dir output` via subprocess; checks exit code 0, presence in stdout of `total_rows`, presence of `cleaned_spec.xlsx` and `run_summary.json` in `output/run-*`.
- **Regression** (`test_regression.py`): see section 5; on mismatch outputs a diff by rows.

Test dependencies: if the input file (`paths.input_root`) or golden is missing, tests are skipped where implemented. Session gate: `conftest.py` (`MAX_SKIP_RATIO = 0.50`) fails the session if `skipped/total > 0.50` or `passed == 0`.

---

## 9. Limitations and assumptions

- **Six vendors:** Dell, Cisco, HPE, Lenovo, xFusion, Huawei. Each has its own parser and normalizer.
- **Cisco:** reads sheet `"Price Estimate"` (strict, no fallback). Header determined by simultaneous presence of `"Line Number"` and `"Part Number"`. SKU in Cisco: trailing `=` is removed.
- **HPE:** reads sheet `"BOM"` with columns Product #, Product Description. No branded spec.
- **One sheet:** the parser works with one specific sheet (Dell/Cisco — first sheet; HPE — sheet `"BOM"`; Lenovo — sheet "Configuration" or first). Annotated export uses `sheet_name` from `adapter.get_source_sheet_name()` to read the same sheet.
- **Header:** the header row is located by exact match of a cell to the vendor-specific sentinel in the first N rows; if absent — `find_header_row` returns `None`, `parse_excel` raises `ValueError`. For Dell: `"Module Name"` in first 20 rows (limit is hard-coded in `src/core/parser.py:26` — known tech debt).
- **Encodings:** config and YAML rules are read in UTF-8; CSV files are written in UTF-8-sig for correct opening in Excel.
- **Row order:** correspondence between normalized rows and classification results — by index in lists; in annotated export, binding to the sheet row is by `source_row_index` (1-based), assuming the first sheet row in pandas is index 0 (Excel row 1).
- **Rules:** entity type check order is fixed in `classifier.py`; rule order within each group is set by YAML (first match wins). Rule version is stored in YAML (`version`) and available as `RuleSet.version`; not saved separately in run artifacts.
- **Config:** switching types for cleaned spec and the `include_only_present` flag are set only through `config.yaml`; no separate CLI flags.

---

## 10. How to extend rules

Each vendor has its own rules file: `rules/dell_rules.yaml`, `rules/cisco_rules.yaml`, etc. Structure is uniform: `version`, `state_rules`, `base_rules`, `service_rules`, `logistic_rules`, `software_rules`, `note_rules`, `config_rules`, `hw_rules`, `device_type_rules`, `hw_type_rules`. Rules in each group are applied in first-match order (`re.IGNORECASE`).

Adding a rule — see `docs/rules/RULES_AUTHORING_GUIDE.md`.

After adding or changing rules in YAML, run:

```bash
python main.py --batch-dir INPUT/<vendor> --vendor <vendor>
python batch_audit.py --output-dir OUTPUT --vendor <vendor> --no-ai
```

Check `audit_report.json`: the count of E2 (UNKNOWN_no_rule) should decrease.

For the full recommended workflow after rule changes, see `docs/rules/RULES_AUTHORING_GUIDE.md` § "Step-by-step rule addition".

---

## 11. Known Limitations and Risks

- **First-match rule sensitivity:** Entity classification and device_type assignment use first-match semantics within each rule category. Overlapping regex patterns between rules in the same category may cause shadowing: a rule placed earlier in the YAML will match instead of a more specific rule placed later. There is no automated overlap detection. See `.planning/codebase/CONCERNS.md` for details.

- **Golden file coupling:** Golden files (`golden/*_expected.jsonl`) compare exact field values (entity_type, state, matched_rule_id, device_type, skus). Any change to normalization behavior (whitespace handling, SKU parsing order) or serialization will cause regression failures across all datasets. This is intentional — the golden files are the classification contract.

- **No automated rule overlap checker:** There is currently no lint or CI check to detect regex overlap between rules in the same category. At the current rule count, manual review during PR is sufficient.

- **run_summary.json is schema-free:** There is no formal schema or validation for `run_summary.json`. Fields are added by `collect_stats()` and by `main.py`. Tests only assert on `unknown_count` and `item_rows_count`.

- **`core/parser.py` is Dell-specific:** Despite living in `core/`, `src/core/parser.py` is a Dell-only parser (sentinel `"Module Name"`, hard-coded scan limit of 20 rows). All other vendors use their own `parser.py` in `src/vendors/<vendor>/`. See `.planning/codebase/CONCERNS.md` for the fix approach.

- **`batch_audit.py` reads Excel, not JSONL:** The audit step reads from `*_annotated.xlsx` (a presentation artifact) rather than from `classification.jsonl` (the canonical output). This is a known tech-debt item — do not "fix" it as part of unrelated work; it requires a dedicated migration. See `.planning/codebase/CONCERNS.md`.
