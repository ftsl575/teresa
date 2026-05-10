# Data Contracts — spec_classifier

## 1. Introduction

Data contracts define the exact formats of the pipeline's output artifacts. They are needed for determinism, regression tests (golden), and auditing. Changing a contract without updating documentation and tests is not allowed.

---

## 2. classification.jsonl

- **Format:** JSONL, UTF-8; one row — one JSON object.
- **Fields:**

| Field | Type | Required | Semantics |
|-------|------|----------|-----------|
| source_row_index | int \| null | yes | 1-based row number in Excel; null only in legacy path. |
| row_kind | string | yes | "ITEM" \| "HEADER". |
| entity_type | string \| null | yes | BASE, HW, CONFIG, SOFTWARE, SERVICE, LOGISTIC, NOTE, UNKNOWN; null for HEADER. |
| state | string \| null | yes | PRESENT, ABSENT, DISABLED; null for HEADER. |
| matched_rule_id | string | yes | Rule identifier or HEADER-SKIP, UNKNOWN-000. |
| device_type | string \| null | yes | Filled only for ITEM with matched_rule_id != UNKNOWN-000 and entity_type HW/LOGISTIC. Otherwise null. |
| hw_type | string \| null | yes | Filled for ITEM with entity_type HW when resolved; otherwise null. |
| warnings | array of string | yes | Usually []; when hw_type is unresolved for HW — e.g. ["hw_type unresolved for HW row"]. |

**device_type** (extensible vocabulary; values are defined by vendor rules):
- Dell: power_cord, sfp_cable, storage_nvme, storage_ssd, psu, nic, raid_controller, hba, cpu
- Cisco: fan, transceiver, cable, psu, power_cord
- HPE: cpu, ram, blank_filler, storage_nvme, storage_ssd, storage_hdd, hba, raid_controller, nic, transceiver, fiber_cable, cable, gpu, riser, rail, drive_cage, backplane, fan, heatsink, bezel, battery, accessory, psu, power_cord, power_distribution_board, interconnect_board, optical_drive
- Lenovo: server, cpu, ram, gpu, storage_ssd, storage_hdd, storage_nvme, raid_controller, hba, nic, network_adapter, transceiver, sfp_cable, psu, power_cord, fan, heatsink, riser, chassis, motherboard, backplane, drive_cage, media_bay, rail, blank_filler, management, tpm, bezel, accessory, battery, front_panel, power_distribution_board, interconnect_board, air_duct
- xFusion: server, cpu, memory, storage_ssd, storage_hdd, storage_nvme, raid_controller, hba, nic, transceiver, sfp_cable, psu, power_cord, fan, riser, backplane, rail, enablement_kit, battery, air_duct, accessory
- Huawei: storage_system, wireless_ap, switch, storage_drive, storage_enclosure, io_module, transceiver, cable, psu, accessory

Source of truth — the `device_type_rules` section in `rules/<vendor>_rules.yaml`. New values when adding a vendor — MINOR change per stability rules (section 7).

**Examples of `device_type` from taxonomy cycles (do not replace YAML):** cycle 1 — `motherboard`, `storage_enclosure`, `backplane`, `bezel` (different vendors); cycle 2 — no new `hw_type` literals; added/refined `device_type` labels: `front_panel`, `power_distribution_board`, `interconnect_board`, `media_bay`, `air_duct`, `optical_drive`, plus unification of Lenovo `drive_cage`/`battery` where they appeared in rules. See `docs/taxonomy/hw_type_taxonomy.md` (PR-11 master map).

**applies_to scope** (defined in `rules/<vendor>_rules.yaml`):
- `device_type_rules.applies_to: [HW, LOGISTIC, BASE]` — `device_type` is assigned only to rows with these `entity_type` values.
- `hw_type_rules.applies_to: [HW]` — `hw_type` is assigned only to rows with `entity_type = HW`.

**hw_type** (26 values): server, switch, storage_system, wireless_ap, cpu, memory, gpu, storage_drive, storage_enclosure, storage_controller, hba, backplane, io_module, network_adapter, transceiver, cable, psu, fan, heatsink, riser, chassis, rail, blank_filler, management, tpm, accessory.

**Note on `HW_TYPE_VOCAB`:** the 26-value vocabulary is defined in two places — `src/core/classifier.py` and `batch_audit.py` — and must be kept in sync. See `.planning/codebase/CONCERNS.md` for the known duplication.

**unknown_rows.csv** — derived artifact: only rows with entity_type = UNKNOWN. Columns: source_row_index, option_id, module_name, option_name, skus, qty, option_price, matched_rule_id. Encoding UTF-8-sig. option_id is populated from NormalizedRow.option_id (for HPE — full Product #; for Dell/Cisco — empty string if absent).

**cleaned_spec.xlsx** — filtered specification: only ITEM rows with entity_type from config `cleaned_spec.include_types` and (optionally) state PRESENT. Columns: Group Name, Group ID, Module Name, Option Name, SKUs, Qty, Option ID, Unit Price, Device Type, HW Type, Entity Type, State, Source Row, Rule ID.

| Column | Type | Description |
|--------|------|-------------|
| Group Name … State | (see above) | Existing columns — order unchanged. |
| `Source Row` | int | `source_row_index` from NormalizedRow: 1-based row number in source Excel. |
| `Rule ID` | str | `matched_rule_id` from ClassificationResult: matched rule identifier (empty string if None). |

---

## 3. rows_raw.json

- **Format:** one JSON array of objects (list of dict).
- Fields of each object correspond to the source sheet columns plus `__row_index__` (int, 1-based). Values are not normalized (as after the parser). NaN is replaced with null.

---

## 4. rows_normalized.json

- **Format:** list of NormalizedRow objects (serialized as dict).
- **Fields:** source_row_index (int), row_kind (str), group_name (str | null), group_id (str | null), product_name (str | null), module_name (str), option_name (str), option_id (str | null), skus (list[str]), qty (int, default 1 when empty/missing), option_price (float).

Vendor Extension (Cisco-only, additive):

For Cisco runs, fields are added to the object if the value is semantically present (not null and not empty string). Values `false`, `0`, `0.0` are valid and are written. Fields: `line_number` (str), `bundle_id` (str), `is_top_level` (bool), `is_bundle_root` (bool), `parent_line_number` (str | null), `service_duration_months` (int | null), `smart_account_mandatory` (bool), `lead_time_days` (int | null), `unit_net_price` (float), `disc_pct` (float), `extended_net_price` (float).

Vendor Extension (HPE-only, additive):

For HPE runs, fields are added to the object if the value is semantically present. Fields: `product_type` (str — value from `Product Type` column, e.g. `"HW"`), `extended_price` (float — from `Extended List Price (USD)`), `lead_time` (str — from `Estimated Availability Lead Time`), `config_name` (str — from `Config Name`), `is_factory_integrated` (bool — `true` when `option_name == "Factory Integrated"`). Fields with empty strings or `0.0` are not serialized (same rule as Cisco).

---

## 5. run_summary.json

- **Fields:** total_rows (int), header_rows_count (int), item_rows_count (int), entity_type_counts (dict), state_counts (dict), unknown_count (int), rules_stats (dict), device_type_counts (dict), hw_type_counts (dict), hw_type_null_count (int), rules_file_hash (str, hex), input_file (str), run_timestamp (str, ISO), vendor_stats (dict). All fields are present after a run.

`vendor_stats` — always present. For Dell: `{}`. For Cisco: `{"top_level_bundles_count": int, "rows_with_service_duration": int, "max_hierarchy_depth": int}`. For HPE: `{"factory_integrated_count": int}` (or `{}` if empty).

---

## 6. golden/<stem>_expected.jsonl

- Same set of fields compared in regression: `source_row_index`, `row_kind`, `entity_type`, `state`, `matched_rule_id`, `device_type`, `hw_type`, `skus`. The regression test compares row-by-row; when rules change, golden is updated via `--save-golden` or `--update-golden` with explicit diff review.

---

## 7. audit_report.json

Generated by `batch_audit.py --output-dir <dir>`. File is created next to `<dir>`.

- **Format:** one JSON object.
- **Top-level fields:**

| Field | Type | Description |
|-------|------|-------------|
| `meta` | object | Run metadata: `run_date`, `model`, `total_tokens`, `tokens_in`, `tokens_out`, `cost_usd`. |
| `stats` | object | Aggregated statistics: `total_files`, `total_rows`, `ok`, `issues`, `by_tag`, `by_vendor`, `by_file`. |
| `bugs` | array | AI_MISMATCH patterns, sorted by type: `REAL_BUG` (device_mismatch ≥3 or ≥2 from different files) → `FALSE_POSITIVE` (entity_mismatch in fp_patterns) → `REVIEW_NEEDED`. Each element: `type`, `pattern`, `count`, `vendors`, `examples`, `fix_target`. |
| `yaml_candidates` | array | AI_SUGGEST patterns: `device_type`, `count`, `vendors`, `note`. |
| `rule_issues` | array | E-code breakdown: `code`, `count`, `vendors`, `examples`. |
| `claude_prompt` | string | Ready-made prompt for Claude describing found issues. |
| `clusters` | object | Present only after running `cluster_audit.py`. Fields: `total_candidates`, `total_clusters`, `clusters` (array of clusters from `cluster_summary.xlsx`). |

**Note:** `batch_audit.py` reads from `*_annotated.xlsx` (Excel presentation artifact), not from `classification.jsonl`. This is a known tech-debt item — do not "fix" it as part of unrelated work. See `.planning/codebase/CONCERNS.md`.

---

## 8. cluster_summary.xlsx

Generated by `cluster_audit.py --output-dir <dir>`.

- **Format:** xlsx, one row — one cluster.
- **Columns:**

| Column | Type | Description |
|--------|------|-------------|
| `cluster_id` | int | Cluster identifier (from HDBSCAN/KMeans). |
| `count` | int | Number of rows in the cluster. |
| `vendors` | str | List of vendors, comma-separated. |
| `top_terms` | str | Top 5 words, comma-separated. |
| `proposed_device_type` | str | Heuristically proposed device_type (or empty). |
| `confidence` | str | `"heuristic"` or `"manual_review"`. |
| `example_1` / `example_2` / `example_3` | str | First 3 examples of option_name from the cluster. |
| `sku_examples` | str | SKU (part number / Product #) from the first 3 cluster candidates, delimiter ` | `. |
| `module_examples` | str | module_name / config_name from the first 3 cluster candidates, delimiter ` | `. |
| `suggested_yaml_rule` | str | Proposed regex pattern for a new rule. |

---

## 9. *_annotated_audited.xlsx

Generated by `batch_audit.py` from `*_annotated.xlsx`.

- **Format:** xlsx; source `*_annotated.xlsx` structure fully preserved + one `pipeline_check` column on the right.
- **`pipeline_check` column:**
  - `"OK"` — row passed all E-checks and (if AI enabled) AI agrees.
  - String of codes separated by `;` — when issues are present, e.g.: `"E8:hw_type_missing_on_hw; AI_MISMATCH:entity[pipeline:HW→ai:CONFIG]"`.
  - E-codes E1–E18: rule-based checks (entity type, state logic, hw_type vocab, mapping consistency, etc.).
  - `AI_MISMATCH`: LLM prediction differs from the pipeline.
  - `AI_SUGGEST`: LLM proposes a device_type for a row without one.

---

## 10. audit_summary.xlsx

Generated by `batch_audit.py --output-dir <dir>`. File is created in the root of `<dir>`.

- **Format:** xlsx, sheet "Сводный отчёт" (the sheet name is in Russian in the generated Excel file); one row — one problematic row from the audited file.
- **Purpose:** aggregated report across all vendors / files for manual review. Rows with `pipeline_check = "OK"` are not included.

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| `Документ` | str | yes | Name of the source file (`*_annotated.xlsx`). |
| `Вендор` | str | yes | Vendor: `dell`, `cisco`, `hpe`, `lenovo`, `huawei`, `xfusion`, or `unknown`. |
| `Артикул / SKU` | str | no | SKU / Part Number. Empty string if absent. |
| `Описание` | str | yes | `option_name` of the row. |
| `Module Name` | str | no | `module_name` / `config_name`. Empty string if absent. |
| `Entity Type` | str | no | Classified type: BASE, HW, CONFIG, … |
| `HW Type` | str | no | `hw_type` of the row. Empty string if null. |
| `Device Type` | str | no | `device_type` of the row. Empty string if null. |
| `State` | str | no | PRESENT / ABSENT / DISABLED. |
| `Пометка скрипта` | str | yes | `pipeline_check` value: E-code(s) separated by `;`, `AI_MISMATCH:…`, `AI_SUGGEST:…`. |
| `Комментарий` | str | no | Always empty string at generation time (field for manual annotations). |

Note: the Excel column headers above are the actual column names in the generated file (Russian, as generated by `batch_audit.py`).

**Row color coding** (cell fill):

| Tag | Color |
|-----|-------|
| `AI_MISMATCH` | light blue (`DDEEFF`) |
| `MANUAL_CHECK` | light orange (`FFE0B2`) |
| `AI_SUGGEST` | light green (`E8F5E9`) |
| `E2` | light red (`FFCCCC`) |
| `E13` / `E14` / `E9` | peach (`FFE0CC`) |
| `E15` / `E17` | gray (`F5F5F5` / `FAFAFA`) |
| others | white (`FFFFFF`) |

**Note:** rows are sorted by file (traversal order of output_dir); within a file — order from `*_annotated_audited.xlsx`. Rows without issues (`pipeline_check = "OK"`) are not included.

---

## 11. Canonical field names

Table of canonical field names used in the pipeline and their aliases in various vendor formats.

| Canonical name | Aliases (source) | Description |
|---|---|---|
| `sku` | `skus`, `sku`, `part_number`, `product_#` | Part number / SKU. For HPE — `Product #` (up to first space). For Dell/Cisco — `Part Number` or `skus`. |
| `module_name` | `module_name`, `module name`, `config_name` | Module name / configuration group name. For HPE — from `Config Name` column. |
| `option_name` | `option_name`, `description`, `product_description`, `Option Name` | Row description (option/component name). |
| `entity_type` | `entity_type`, `Entity Type` | Classified row type: BASE, HW, CONFIG, SOFTWARE, SERVICE, LOGISTIC, NOTE, UNKNOWN. |
| `device_type` | `device_type` | Detailed device type (cpu, memory, psu, power_cord, …). Only for ITEM rows with entity_type in applies_to. |
| `hw_type` | `hw_type` | Normalized hardware type from HW_TYPE_VOCAB (26 values). Only for HW rows. |
| `row_kind` | `row_kind` | Row type: `"ITEM"` (data) or `"HEADER"` (header / separator). |
| `source_row_index` | `Source Row` | 1-based row number in source Excel. Column `"Source Row"` in cleaned_spec.xlsx. |
| `matched_rule_id` | `Rule ID`, `rule_id` | Matched rule identifier; empty string in cleaned_spec.xlsx if None. |

The following field names are canonical and must match across all output artifacts (Excel / JSON / audit outputs):

- vendor
- option_name
- entity_type
- device_type
- hw_type
- pipeline_check
- rule_id
- state
- confidence

Any vendor-specific fields must be added separately without changing the canonical names.

---

## 12. Stability rules

- **MAJOR:** removing a field from classification.jsonl, changing a field type, changing the semantics of entity_type/state (new enum values without backward compatibility).
- **MINOR:** adding a new field, new enum value, new fields in run_summary.
- **PATCH:** changing matched_rule_id without changing entity_type/state (e.g. refining rule_id with the same classification).
