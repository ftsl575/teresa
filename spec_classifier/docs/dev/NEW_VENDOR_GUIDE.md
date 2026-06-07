# New Vendor Guide — spec_classifier

Self-contained document: a new vendor can be added by following only this file (plus the Dell/Cisco examples in the code).

---

## 1. Overview: files to create and modify

**Create:**
- `src/vendors/<vendor>/__init__.py` (empty)
- `src/vendors/<vendor>/adapter.py` — adapter class
- `rules/<vendor>_rules.yaml` — classification rules
- `tests/test_regression_<vendor>.py` (based on test_regression_cisco.py)
- `tests/test_unknown_threshold_<vendor>.py` (based on test_unknown_threshold_cisco.py)
- Test data in `C:\Users\<USERNAME>\Desktop\INPUT\` (e.g. `<vendor>_1.xlsx`); not stored in the repo
- Golden files: `golden/<stem>_expected.jsonl` (generated via `--save-golden`)

**Modify:**
- `main.py` — one line in `VENDOR_REGISTRY`
- `config.yaml` — one line in `vendor_rules`
- `run.ps1` (repo root) — append `"<vendor>"` to `$ALL_VENDORS`
- `teresa_gui.py` — append `"<vendor>"` to `VENDORS_ACTIVE` and add a label in `_build_left_column`
- If needed: `src/vendors/<vendor>/adapter.py` — override `get_extra_cols()` (see `VendorAdapter` in `src/vendors/base.py`) if the normalized rows have additional fields for annotated Excel columns. Examples: `HPEAdapter.get_extra_cols()` (5 columns), `LenovoAdapter.get_extra_cols()` (1 column), `CiscoAdapter.get_extra_cols()` (2 columns). `annotated_writer.py` accepts them as the `extra_cols` parameter and does not need to be modified.
- `CHANGELOG.md` — after adding the vendor

---

## 2. Step-by-step instructions

### Step 1: src/vendors/<vendor>/__init__.py

Create an empty file (or with minimal adapter export if that is the project convention).

### Step 2: src/vendors/<vendor>/adapter.py — VendorAdapter implementation

Implement all 6 required abstract methods:

- **can_parse(path)**
  **Required: positive signature** — a unique marker for this vendor's files.
  Dell example: the cell `"Module Name"` in the first 20 rows of the first sheet.
  Cisco example: the presence of a sheet named `"Price Estimate"`.
  **Forbidden:** "negative identity" (`return True if not another_vendor`).
  Do not catch exceptions — an unreadable file must raise, not be silently skipped.

- **parse(path)**
  Returns `(list[dict], int)`: list of rows (each dict has columns + `__row_index__` 1-based) and the 0-based header row index.

- **normalize(raw_rows)**
  Returns a `list` of objects compatible with `NormalizedRow`.
  **Required fields:** `source_row_index`, `row_kind`, `group_name`, `group_id`, `product_name`, `module_name`, `option_name`, `option_id`, `skus`, `qty`, `option_price`.
  Other fields per contract (see `DATA_CONTRACTS.md` and `src/core/normalizer.NormalizedRow`).

- **get_rules_file()**
  Path to the rules YAML (e.g. `rules/<vendor>_rules.yaml`); can read from `config["vendor_rules"][vendor]` with fallback.

- **get_vendor_stats(normalized_rows)**
  Dict for `run_summary.json` (see Step 3 below).

- **generates_branded_spec()**
  Do NOT override. All vendors brand uniformly; the value is defined once in
  `VendorAdapter` (base) as `return True` and is the single source of truth.
  A new vendor inherits branding automatically — no per-vendor method needed.

### Step 3: rules/<vendor>_rules.yaml

Structure: `version`, `state_rules`, `base_rules`, `service_rules`, … `hw_rules`, `device_type_rules` (based on `dell_rules.yaml` or `cisco_rules.yaml`).
**rule_id:** format `<CATEGORY>-<VENDOR_CODE>-NNN` — see `docs/rules/RULES_AUTHORING_GUIDE.md`, section "rule_id naming convention". Choose a unique code for the new vendor (e.g., `L` for Lenovo, `HU` for Huawei, `XF` for xFusion).

### Step 4: Add to VENDOR_REGISTRY in main.py

One line: import the adapter and add `"<vendor>": <Vendor>Adapter` to the `VENDOR_REGISTRY` dict.

### Step 5: Add to vendor_rules in config.yaml

In the `vendor_rules` section add: `<vendor>: "rules/<vendor>_rules.yaml"`.

### Step 6: Wire the launcher and GUI

- Append `"<vendor>"` to `$ALL_VENDORS` in `run.ps1` (repo root).
- Append `"<vendor>"` to `VENDORS_ACTIVE` in `teresa_gui.py` and add a label entry in `_build_left_column`.

### Step 7: Tests

- **test_regression_<vendor>.py** — based on `test_regression_cisco.py`: run via `_get_adapter("<vendor>", config)`, compare with golden.
- **test_unknown_threshold_<vendor>.py** — based on `test_unknown_threshold_cisco.py`: verify `unknown_count = 0` on all vendor test files.

### Step 8: Golden files

For each test file:

```bash
python main.py --save-golden --input "C:\Users\<USERNAME>\Desktop\INPUT\<file>.xlsx" --vendor <vendor>
```

Place/verify the golden at `golden/<stem>_expected.jsonl`.

### Step 9: Update CHANGELOG.md

In `CHANGELOG.md` under `[Unreleased]`: document the new vendor addition, new tests, new rules.

> Note: `CURRENT_STATE.md` has been archived to `.planning/archive/CURRENT_STATE-2026-05-10.md`. The live project status is tracked in `.planning/STATE.md`.

### Step 10: Additional columns in annotated Excel

If the adapter adds fields to the normalized row (like Cisco: `line_number`, `service_duration_months`; HPE: `product_type`, `extended_price`, `lead_time`, `config_name`, `is_factory_integrated`; Lenovo: `export_control`), override `get_extra_cols()` in the adapter. The method returns `list[tuple[str, str]]`, where each tuple is `(attribute_name_on_NormalizedRow, column_header_in_excel)`. The base implementation in `src/vendors/base.py:VendorAdapter.get_extra_cols()` returns `[]` (default). `main.py` passes the result to `generate_annotated_source_excel(..., extra_cols=adapter.get_extra_cols())` — no changes to `src/outputs/annotated_writer.py` are needed. Vendor extension columns always appear in the annotated output.

---

## 3. vendor_stats

- **Dell:** `get_vendor_stats()` returns `{}` — the `vendor_stats` section in `run_summary.json` is empty.
- **Cisco:** returns a dict with metrics (e.g. `top_level_bundles_count`, `max_hierarchy_depth`) — these appear in `run_summary.json`.

For a new vendor: either `{}`, or a custom metric set as needed.

---

## 4. Pre-PR checklist

- [ ] **can_parse:** positive signature (unique format marker), no "negative identity".
- [ ] **unknown_count = 0** on all vendor test files.
- [ ] **hw_type_null_count = 0** (if applicable).
- [ ] All tests green: `python -m pytest tests/ -v`.
- [ ] Golden files generated and regression passes.
- [ ] `CHANGELOG.md` updated (new entry in `[Unreleased]` or release version).

---

## See also

- `docs/rules/RULES_AUTHORING_GUIDE.md` — rule_id convention, YAML structure.
- `docs/schemas/DATA_CONTRACTS.md` — NormalizedRow contract and output artifacts.
- `src/vendors/dell/adapter.py`, `src/vendors/cisco/adapter.py` and `src/vendors/cisco/parser.py`, `normalizer.py` — implementation examples.
