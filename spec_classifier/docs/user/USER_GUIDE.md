# User Guide — spec_classifier

## 1. Purpose

The system classifies rows from vendor specifications (Dell, Cisco CCW, HPE QuoteBuilder BOM, Lenovo DCSC, xFusion FusionServer eDeal, Huawei eDeal) in Excel format: determines the entity type (BASE, HW, SOFTWARE, etc.), state (PRESENT/ABSENT/DISABLED), device type, and hardware type. The result is deterministic; classification is performed using rules from YAML and regex, with no ML. Output is a run folder with JSON/CSV/Excel artifacts and a cleaned/annotated/branded specification.

---

## 2. Supported input files

Each vendor has its own input file format. The vendor is specified with the `--vendor` flag.

**Dell (`--vendor dell`, default):**

- **Format:** `.xlsx`, first sheet.
- **Header row:** within the first 20 rows there must be a cell with the text `"Module Name"`. This is used to locate the table header.
- **Expected columns:** Module Name, Option Name, SKUs, Qty, Option List Price.
- **Optional:** Group Name, Group ID, Product Name, Option ID.
- **Limitations:** one sheet, one file per run in single-file mode; for multiple files — use `--batch-dir`.

**Cisco CCW (`--vendor cisco`):**

- Format: `.xlsx`, sheet `"Price Estimate"` (strict, no fallback).
- Header row: located by the simultaneous presence of `"Line Number"` and `"Part Number"` in the first 100 rows.
- Expected columns: Line Number, Part Number, Description, Qty, Unit List Price, Unit Net Price, Disc(%), Extended Net Price, Service Duration (Months), Smart Account Mandatory, Estimated Lead Time (Days).
- Details: trailing `=` in Part Number is removed automatically; an empty Part Number within data is allowed (data end is determined by the last non-empty Part Number cell).

**HPE QuoteBuilder BOM (`--vendor hpe`):**

- Format: `.xlsx`, sheet `"BOM"` (strict, no fallback).
- Header row: strictly the first row of the sheet (row 0), no preamble.
- Expected columns: Product #, Product Description, Qty, Unit Price (USD), Config Name. Optional: Product Type, Extended List Price (USD), Estimated Availability Lead Time.
- Details: `Product #` is used as `option_id` in full; the base SKU (up to the first space) goes into `skus[0]`. The `Config Name` column maps to `group_name` and `module_name`. The row `"Factory Integrated"` is classified as `CONFIG` (rule `CONFIG-H-001`). Data end: the first row where the first non-empty cell equals `"total"` (case-insensitive).

**Lenovo DCSC (`--vendor lenovo`):**

- Format: `.xlsx`, sheet "Configuration" or first sheet (DCSC export).
- Header row: located by the presence of cells `"Option Name"` / `"Option ID"` in the first ~20 rows.
- Expected columns: Option ID, Option Name, Quantity, Unit Price; optional Module / Category.
- Details: BASE machine type is encoded as `[A-Z0-9]{4}CTO` (e.g. `7D5GCTO1WW`); XClarity Controller FOD rows (`7S0X…`) are intentionally excluded via negative lookahead `^(?!7S)` and route to SOFTWARE rules. Supported: `device_type=motherboard` (HW-L-040, "System Board"/"MB"; → `hw_type=chassis`), `device_type=bezel` ("Blowing Rock"/Security Bezel; → `hw_type=accessory`, Lenovo-local), GPU Base (`BASE-L-020`; → `entity_type=BASE, device_type=server`).

**xFusion FusionServer eDeal (`--vendor xfusion`):**

- Format: `.xlsx`, sheet with FusionServer configuration.
- Header row: located by the presence of `"Configuration Name"` / `"Component Type"`.
- Expected columns: Part Number / Material Code, Component Type, Description, Quantity, Unit Price.
- Details: BASE machine type uses G-prefix part numbers (`BASE-XF-001` / `DT-XF-021`). Supports `device_type=backplane` (`DT-XF-022-BACKPLANE` → `hw_type=backplane`).

**Huawei eDeal (`--vendor huawei`):**

- Format: `.xlsx`, sheets for ICT/Server/Storage/WLAN catalogs.
- Header row: located by the presence of `"Material Code"` / `"Description"`.
- Details: supports `device_type=storage_enclosure` (Disk Enclosure OceanStor family → `hw_type=storage_enclosure`, new type in HW_TYPE_VOCAB v2.1.0) and `device_type=io_module` (SmartIO modules → `hw_type=io_module`). BASE for AirEngine/AC access points: `entity_type=BASE, device_type=wireless_ap`.

---

## 3. Running and results

Minimal example:

```bash
cd spec_classifier
python main.py --input "C:\Users\<USERNAME>\Desktop\INPUT\dl1.xlsx"
```

Result — folder `output/dell_run/run-YYYY-MM-DD__HH-MM-SS-dl1/` (or with suffix `_1`, `_2` on collision). Inside — all run artifacts. Review results in `run_summary.json` and `unknown_rows.csv`.

---

## 4. Run artifacts

| File | Description |
|------|-------------|
| `classification.jsonl` | One row — one JSON with classification fields for each row (entity_type, state, device_type, hw_type, matched_rule_id, etc.). |
| `run_summary.json` | Summary: total_rows, entity_type_counts, state_counts, unknown_count, device_type_counts, hw_type_counts, rules_file_hash, input_file, run_timestamp. |
| `cleaned_spec.xlsx` | Filtered specification: types from config (BASE, HW, SOFTWARE, SERVICE), PRESENT only (if `include_only_present: true`). |
| `<stem>_annotated.xlsx` | Source file + 6 columns: Entity Type, State, device_type, hw_type, row_kind, matched_rule_id. All rows preserved. |
| `<stem>_branded.xlsx` | Branded specification: grouped by BASE (server) and sections by entity_type; "Not installed" block for ABSENT if needed. |
| `unknown_rows.csv` | Rows with entity_type = UNKNOWN. Columns: source_row_index, option_id, module_name, option_name, skus, qty, option_price, matched_rule_id. Review after every run. |
| `rows_raw.json` | Raw rows after the parser (debug). |
| `rows_normalized.json` | Normalized rows with row_kind (debug). |
| `header_rows.csv` | Section separator rows (HEADER). |
| `run.log` | Pipeline log for this run. |

---

## 5. TOTAL folder (batch mode)

When running with `--batch-dir`, a session summary folder is created: `output/<vendor>_run/run-YYYY-MM-DD__HH-MM-SS-TOTAL/`. It receives copies of three presentation files from each per-run folder:

- `<stem>_cleaned_spec.xlsx`
- `<stem>_annotated.xlsx`
- `<stem>_branded.xlsx`

Use TOTAL for handing off to the client or consolidating a single session's results.

---

## 6. Interpreting classification fields

- **row_kind:** `HEADER` — section separator (empty Module Name, Option Name, SKUs); `ITEM` — specification line item.
- **source_row_index:** 1-based row number in the source Excel (for auditing and cross-referencing with the sheet).
- **entity_type:** one of 8 types. Examples: BASE (Base, PowerEdge R660), SERVICE (ProSupport, Warranty), LOGISTIC (Shipping, packaging, freight), SOFTWARE (Embedded Systems Management), NOTE (supports ONLY), CONFIG (No Cable, RAID Configuration), HW (Processor, Memory, Hard Drives, Power Cord, cables, rails), UNKNOWN (no rule matched).
- **state:** PRESENT — option is present; ABSENT — not installed (e.g. "No TPM", "No HDD", "Empty"); DISABLED — disabled (e.g. "Disabled").
- **device_type:** refinement for HW/LOGISTIC rows. The authoritative source is `device_type_rules` in `rules/<vendor>_rules.yaml`. Common values by category:

  | Category | Values |
  |----------|--------|
  | Compute | `cpu`, `memory`, `gpu` |
  | Storage | `storage_nvme`, `storage_ssd`, `storage_hdd`, `storage_drive`, `storage_controller`, `raid_controller`, `hba`, `drive_cage`, `backplane`, `storage_enclosure`, `io_module` |
  | Network | `network_adapter`, `transceiver`, `cable`, `sfp_cable`, `fiber_cable` |
  | Power | `psu`, `power_cord` |
  | Mechanical | `fan`, `heatsink`, `riser`, `chassis`, `motherboard`, `rail`, `blank_filler`, `bezel`, `battery` |
  | Management | `management`, `tpm`, `accessory` |
  | Infrastructure | `server`, `switch`, `storage_system`, `wireless_ap` |

  May be null if no rule assigned a device_type. The list grows when new vendors are added (MINOR change).
- **hw_type:** hardware type for HW rows. 26 values (v2.6.0 taxonomy): server, switch, storage_system, wireless_ap, cpu, memory, gpu, storage_drive, storage_enclosure, storage_controller, hba, backplane, io_module, network_adapter, transceiver, cable, psu, fan, heatsink, riser, chassis, rail, blank_filler, management, tpm, accessory. For non-HW or unresolved HW — null.
- **matched_rule_id:** identifier of the matched rule (e.g. `HW-002`, `SERVICE-001`). `UNKNOWN-000` — no matches.
- **warnings:** list of warnings (e.g. "hw_type unresolved for HW row"); usually empty.

---

## 7. Recommended workflow

1. Run: `python main.py --input "C:\Users\<USERNAME>\Desktop\INPUT\dl1.xlsx"`.
2. Check `unknown_rows.csv`.
3. If `unknown_count > 0`: add or adjust a rule in `dell_rules.yaml` → re-run → check diff in classification.
4. When accepting changes: `python main.py --input "C:\Users\<USERNAME>\Desktop\INPUT\dl1.xlsx" --save-golden` and `pytest tests/test_regression.py -v`.
5. If `unknown_count = 0` and regression is green — done.

For Cisco CCW: steps are analogous, but with `--vendor cisco` and rules in `rules/cisco_rules.yaml`. Target — `unknown_count = 0` on `ccw_1` and `ccw_2`.

For HPE: steps are analogous, but with `--vendor hpe` and rules in `rules/hpe_rules.yaml`. Input files are recommended to be stored in `INPUT\hpe\`. Target — `unknown_count = 0` on all BOM files (hp1–hp8).

```powershell
python main.py --vendor hpe --input "C:\Users\<USERNAME>\Desktop\INPUT\hpe\hp1.xlsx"
```

For Lenovo / xFusion / Huawei: analogous, with the corresponding `--vendor` and rules `rules/<vendor>_rules.yaml`. Lenovo input → `INPUT\lenovo\` (L1.xlsx … L11.xlsx, regression goldens generated in PR-4c).

```powershell
python main.py --vendor lenovo  --input "C:\Users\<USERNAME>\Desktop\INPUT\lenovo\L1.xlsx"
python main.py --vendor xfusion --input "C:\Users\<USERNAME>\Desktop\INPUT\xfusion\xf1.xlsx"
python main.py --vendor huawei  --input "C:\Users\<USERNAME>\Desktop\INPUT\huawei\hu1.xlsx"
```

---

## 8. cleaned_spec.xlsx

Only ITEM rows with entity_type from `config.cleaned_spec.include_types` (default: BASE, HW, SOFTWARE, SERVICE) are included. With `include_only_present: true` — only rows with state PRESENT. Columns: Group Name, Group ID, Module Name, Option Name, SKUs, Qty, Option ID, Unit Price, Device Type, HW Type, Entity Type, State, Source Row, Rule ID. HEADER rows and other types/states are not included.

For HPE: Group Name / Group ID columns are populated from `Config Name` (server configuration name). This allows identifying which server a row belongs to in a multi-config BOM.

---

## 9. branded_spec.xlsx

Structure: first the BASE row (server), then sections by entity_type. Within sections — grouped items with columns SKU, Option Name, Qty, Price. May include a "Not installed" block for ABSENT rows. If there are ITEM rows before the first BASE, they appear in a "Items without server" preamble block. The file is intended for client presentation.

---

## 10. annotated.xlsx

The source sheet without removing any rows; 6 columns added: Entity Type, State, device_type, hw_type, row_kind, matched_rule_id. Row correspondence is by source_row_index (1-based). All rows are preserved for auditing and manual review.
