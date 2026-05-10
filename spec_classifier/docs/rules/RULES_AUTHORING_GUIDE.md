# Rules Authoring Guide — spec_classifier

## 1. Overview

Rules are stored in `rules/dell_rules.yaml` (Dell), `rules/cisco_rules.yaml` (Cisco), `rules/hpe_rules.yaml` (HPE), `rules/lenovo_rules.yaml` (Lenovo), `rules/huawei_rules.yaml` (Huawei), and `rules/xfusion_rules.yaml` (xFusion). The file is selected via `--vendor {dell,cisco,hpe,lenovo,huawei,xfusion}` and the `vendor_rules` section in `config.yaml`. Classification is deterministic; for each ITEM row, the first match (first-match) is applied in the given category order and within each category; semantics are the same for all vendors.

---

## 2. YAML structure

- **version** — rule set version (e.g. 1.1.0).
- **state_rules** — state definition (absent_keywords, present_override_keywords).
- **base_rules, service_rules, logistic_rules, software_rules, note_rules, config_rules, hw_rules** — entity_type rules.
- **device_type_rules** — second pass: device_type assignment for HW/LOGISTIC.
- **hw_type_rules** — third pass: hw_type assignment for HW (device_type_map, rule_id_map, rules).

---

## 3. entity_type classification order

| Priority | Category | Description |
|----------|----------|-------------|
| 1 | BASE | Base system (Base, PowerEdge R6xx). |
| 2 | SERVICE | Services (ProSupport, Warranty). |
| 3 | LOGISTIC | Logistics (Shipping, packaging, documents, delivery). |
| 4 | SOFTWARE | Software (Embedded Systems Management, OS). |
| 5 | NOTE | Informational notes. |
| 6 | CONFIG | Configuration (No Cable, RAID). |
| 7 | HW | Hardware (Processor, Memory, Drives, Power Cord, cables). |
| 8 | UNKNOWN | No matches. |

---

## 4. Entity rule format

```yaml
- field: module_name   # or option_name
  pattern: 'regex'     # always re.IGNORECASE
  entity_type: HW      # informational
  rule_id: HW-002      # unique, not reused
```

---

## 5. State rules

- **absent_keywords:** pattern + state: ABSENT (or DISABLED) + rule_id. Checked against option_name.
- **present_override_keywords:** override to PRESENT (e.g. "N Rear Blanks").

---

## 6. device_type rules

In the `device_type_rules.rules` section, a rule specifies the **device_type** field (instead of entity_type). Applied only to ITEM rows with entity_type from `applies_to` (HW, LOGISTIC) and when `matched_rule_id != UNKNOWN-000`.

---

## 7. hw_type_rules — three layers

1. **device_type_map:** mapping device_type → hw_type (e.g. nic → network_adapter).
2. **rule_id_map:** mapping matched_rule_id → hw_type (e.g. HW-001 → chassis).
3. **rules:** list of rules with **hw_type** field and pattern on module_name/option_name; first match wins. Rule order matters.

---

## 8. rule_id naming convention

Format: `<CATEGORY>-[<VENDOR_CODE>-]<NNN>`

| Vendor | Code | Example |
|--------|------|---------|
| Dell | (no code) | BASE-001, HW-002, STATE-001 |
| Cisco | C | BASE-C-001, HW-C-001, STATE-C-001 |
| HPE | H | BASE-H-001, HW-H-001 |
| Lenovo | L | BASE-L-001, HW-L-001, DT-L-001 |
| Huawei | HU | BASE-HU-001, HW-HU-001, DT-HU-001 |
| xFusion | XF | BASE-XF-001, HW-XF-001, DT-XF-001 |

- **NNN** — three-digit number within the category and vendor.
- **rule_id** is globally unique (not just within one YAML file).
- **Reserved:** HEADER-SKIP, UNKNOWN-000 — do not reuse.

Changing or renaming a rule_id requires updating golden (`--save-golden` / `--update-golden`) and recording the change in CHANGELOG.

---

## 9. Step-by-step rule addition

1. Formulate the criterion (regex on module_name or option_name).
2. Test the regex on test rows (including all datasets for the vendor).
3. Choose the category and position in YAML (after more specific rules).
4. Add the rule with a unique rule_id.
5. Run the pipeline on all test files for the vendor:
   - Dell: `python main.py --input "C:\Users\<USERNAME>\Desktop\INPUT\dl1.xlsx"` (and dl2..dl5)
   - Cisco: `python main.py --input "C:\Users\<USERNAME>\Desktop\INPUT\ccw_1.xlsx" --vendor cisco` (and ccw_2)
   - HPE/Lenovo/Huawei/xFusion: analogous with the corresponding `--vendor` flag
6. Check `unknown_rows.csv` and `run_summary.json`.
7. Add a unit test to `test_rules_unit.py` or `test_<vendor>_rules_unit.py` if needed.
8. Update golden (`--save-golden`) and run `test_regression*.py`.
9. Update `CHANGELOG.md` and documentation if needed.

---

## 10. Anti-patterns

- **Too broad a pattern:** e.g. bare `\bOCP\b` catches "OCP 3.0 Accessories"; narrow the context.
- **Negative lookahead without testing on all datasets:** can break other rows.
- **Shadowed rule:** a rule placed after a more general one that never fires — check order.
- **Duplicate rule_id:** one rule_id must not appear for different purposes (entity vs device_type vs hw_type — the same value in different sections is allowed only if it is the same logical rule).
- **Changing rule_id without updating golden:** regression will fail; update golden and describe in CHANGELOG.

---

## 11. Typical patterns

- **Exact match:** `'^Base$'`, `'^Chassis\s+Configuration$'`.
- **Prefix/substring:** `'\b(Processor|Memory\s+Capacity)\b'`.
- **Negative lookahead:** `'(?i)\b((?<!GPU\s)Blanks?|Filler)\b'` — exclude "GPU Blanks".
- **Two conditions (AND):** `'(?i)(?=.*No\s+BOSS)(?=.*Rear\s+Blank).*'`.

---

## 12. Rule versioning

When changing rules, update the **version** field in `dell_rules.yaml`, `cisco_rules.yaml`, or the corresponding vendor file. The SHA-256 of the rules file is written to `run_summary.json` (`rules_file_hash`) for reproducibility.

---

## 13. Cisco rules

- **File:** `rules/cisco_rules.yaml`.
- **Available fields for `field`:** `module_name`, `option_name`, `sku`, `is_bundle_root` (values `"true"`/`"false"` in lowercase), `service_duration_months`.
- **Note:** `sku` is matched only against `skus[0]` (MVP limitation). With multi-SKU rows, consider extending the logic.
- **After changes:**

```bash
python main.py --input "C:\Users\<USERNAME>\Desktop\INPUT\ccw_1.xlsx" --vendor cisco --save-golden
python main.py --input "C:\Users\<USERNAME>\Desktop\INPUT\ccw_2.xlsx" --vendor cisco --save-golden
pytest tests/test_regression_cisco.py tests/test_unknown_threshold_cisco.py -v
```

---

## power_cord: hw_type is intentionally absent

`power_cord` is the only `device_type` that is intentionally not mapped to `hw_type` via `hw_type_rules.device_type_map`. The `hw_type` value remains `None` by default.

This is a deliberate decision, not an oversight. Reason: a power cord is not a hardware component with a classifiable hardware type.

**Important for rule authors:** do not add `hw_type: null` as a field in `device_type_rules.rules` — this field is inert for the engine (`match_device_type_rule()` reads only `field` and `pattern`). `hw_type` assignment happens in a separate pass through `hw_type_rules`. Writing `hw_type: null` in `device_type_rules` does not change behavior and is misleading.

The `_E8_NO_HW_TYPE_DEVICES = {"power_cord", "enablement_kit"}` set in `batch_audit.py` excludes these device types from the E8 audit check ("HW + PRESENT without hw_type"). This is intentional — do not remove these exceptions.

See `.planning/codebase/CONCERNS.md` for the full "do not fix" context.

---

## HPE: hw_type depends only on device_type_map (Layer 1)

HPE `hw_type_rules` use only Layer 1 (`device_type_map`). Layers 2–3 (`rule_id_map`, `rules`) are empty.

**Warning:** when adding a new `device_type` for HPE, you MUST simultaneously add the mapping to `hw_type_rules.device_type_map`. If the mapping is not added → `hw_type` will remain `None`, the row will be flagged as "hw_type unresolved for HW row" in diagnostics, but there is no dedicated E-code for this case. This is a silent defect.
