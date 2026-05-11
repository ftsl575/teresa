# Testing Guide — Spec Classifier

## 1. Testing strategy

- **Unit (no xlsx):** `test_rules_unit`, `test_state_detector`, `test_normalizer` — do not require test Excel files.
- **Integration (with xlsx):** pipeline run on `dlN.xlsx` from `C:\Users\<USERNAME>\Desktop\INPUT\`; artifact verification (`test_smoke`, `test_excel_writer`, `test_annotated_writer`, `test_cli`).
- **Regression (xlsx + golden):** `test_regression` — row-by-row comparison with `golden/<stem>_expected.jsonl`.
- **Acceptance:** `test_unknown_threshold` (unknown limit), `test_dec_acceptance`, etc. as needed.
- **Cisco Unit:** `test_cisco_parser` — `parse_excel` on `ccw_1`/`ccw_2`; `test_cisco_normalizer` — `bundle_id`, `parent_line_number`, `is_bundle_root`, `module_name`, `standalone`.
- **Cisco Regression:** `test_regression_cisco` — row-by-row comparison with `golden/ccw_1_expected.jsonl` and `golden/ccw_2_expected.jsonl`.
- **Cisco Threshold:** `test_unknown_threshold_cisco` — `unknown_count = 0` for `ccw_1` and `ccw_2`.
- **HPE Unit:** `test_hpe_parser` — parse on `hp1–hp8` (sheet BOM, col_map); `test_hpe_normalizer` — `HPENormalizedRow` vendor extensions; `test_hpe_rules_unit` — parametrized `device_type`/`hw_type` cases for all HPE device types.
- **HPE Regression:** `test_regression_hpe` — row-by-row comparison with `golden/hp1–hp8_expected.jsonl`.
- **HPE Threshold:** `test_unknown_threshold_hpe` — `unknown_count = 0` for `hp1–hp8`.
- **Lenovo:** `test_lenovo_parser`, `test_lenovo_normalizer`, `test_lenovo_rules_unit`, `test_regression_lenovo`.
- **Huawei / xFusion:** `test_huawei_parser`, `test_huawei_normalizer`, `test_regression_huawei`, `test_xfusion_parser`, `test_xfusion_normalizer`, `test_unknown_threshold_huawei`, `test_unknown_threshold_xfusion`.

---

## 2. Quick start

```bash
# Unit without xlsx
pytest tests/test_rules_unit.py tests/test_state_detector.py tests/test_normalizer.py -v

# With xlsx (smoke + CLI)
pytest tests/test_smoke.py tests/test_cli.py -v

# Regression (requires INPUT files and golden/)
pytest tests/test_regression.py -v

# Full suite
pytest tests/ -v --tb=short

# Cisco tests
pytest tests/test_cisco_parser.py tests/test_cisco_normalizer.py \
       tests/test_regression_cisco.py tests/test_unknown_threshold_cisco.py -v

# HPE tests
pytest tests/test_hpe_parser.py tests/test_hpe_normalizer.py \
       tests/test_hpe_rules_unit.py \
       tests/test_regression_hpe.py tests/test_unknown_threshold_hpe.py -v

# Lenovo tests
pytest tests/test_lenovo_parser.py tests/test_lenovo_normalizer.py \
       tests/test_lenovo_rules_unit.py -v

# Huawei / xFusion tests
pytest tests/test_huawei_parser.py tests/test_huawei_normalizer.py \
       tests/test_regression_huawei.py tests/test_xfusion_parser.py \
       tests/test_xfusion_normalizer.py -v
```

---

## 3. Test data

Input xlsx files are not stored in git. Place them in `C:\Users\<USERNAME>\Desktop\INPUT\` (or specify your path in `config.local.yaml → paths.input_root`). If the file is missing, tests are skipped with a message.

---

## 4. Golden files

- **Generation:** `python main.py --input "C:\Users\<USERNAME>\Desktop\INPUT\dl1.xlsx" --save-golden` → creates `golden/dl1_expected.jsonl`.
- **Update:** `--update-golden` with interactive confirmation (y/N). In CI — `--save-golden`.
- **Compared fields:** `entity_type`, `state`, `matched_rule_id`, `device_type`, `hw_type`, `skus` (and others, as defined in the test).
- **Policy:** update golden only deliberately after rule/logic changes; always include a diff description and review in the PR.
- **Cisco golden:** `golden/ccw_1_expected.jsonl`, `golden/ccw_2_expected.jsonl`. Generation: `python main.py --input "C:\Users\<USERNAME>\Desktop\INPUT\ccw_1.xlsx" --vendor cisco --save-golden` (same for `ccw_2`). After changing `cisco_rules.yaml` — update both Cisco golden files.

---

## 5. Adding a unit test

Template in `tests/test_rules_unit.py` or `test_device_type.py`: create a normalized row (or use a fixture), call `classify_row(row, ruleset)`, assert `result.entity_type` / `state` / `matched_rule_id` / `device_type` / `hw_type`. For rules — load `RuleSet` from `dell_rules.yaml` (via `conftest`/`project_root`).

---

## 6. CI gate

Minimum command to verify before a commit:

```bash
pytest tests/test_rules_unit.py tests/test_state_detector.py tests/test_normalizer.py \
       tests/test_regression.py tests/test_unknown_threshold.py \
       tests/test_regression_cisco.py tests/test_unknown_threshold_cisco.py \
       tests/test_hpe_parser.py tests/test_hpe_normalizer.py tests/test_hpe_rules_unit.py \
       tests/test_regression_hpe.py tests/test_unknown_threshold_hpe.py \
       tests/test_lenovo_rules_unit.py tests/test_lenovo_normalizer.py \
       tests/test_regression_huawei.py tests/test_xfusion_parser.py \
       -v --tb=short
```

When INPUT files or golden files are missing, some tests will be skipped; unit tests and regression tests (when files are present) must be green.

**Session gate:** `conftest.py` (`MAX_SKIP_RATIO = 0.50`) fails the session if `skipped/total > 0.50` or if `passed == 0` while tests were collected. Missing `paths.input_root` is a hard error.

---

## 7. Unknown threshold gate

The `test_unknown_threshold` test limits the UNKNOWN row fraction (e.g. 5%). If the limit is exceeded — add rules rather than raising the threshold or updating golden without justification.

---

## 8. Working with a new dataset

1. Place xlsx in `C:\Users\<USERNAME>\Desktop\INPUT\dlN.xlsx`.
2. Run `python main.py --input "C:\Users\<USERNAME>\Desktop\INPUT\dlN.xlsx" --save-golden`.
3. Check `unknown_rows.csv` and `run_summary`.
4. Add rules if needed and re-run.
5. Add the parameter to the `parametrize` list in `test_regression.py` (and other tests as needed).
6. Run the full test suite.
7. Commit `golden/dlN_expected.jsonl` and test changes.

### New Cisco dataset (ccwN.xlsx)

1. Place in `C:\Users\<USERNAME>\Desktop\INPUT\ccw_N.xlsx`.
2. Run `python main.py --input "C:\Users\<USERNAME>\Desktop\INPUT\ccw_N.xlsx" --vendor cisco`.
3. Check `unknown_rows.csv` and `run_summary.json` (target: `unknown_count = 0`).
4. If `unknown > 0`: add rules to `rules/cisco_rules.yaml`, repeat step 2.
5. Run `python main.py --input "C:\Users\<USERNAME>\Desktop\INPUT\ccw_N.xlsx" --vendor cisco --save-golden`.
6. Add `ccw_N` to `@pytest.mark.parametrize` in `test_regression_cisco.py`.
7. Run `pytest tests/ -v` and commit `golden/ccw_N_expected.jsonl`.

### New HPE dataset (hpN.xlsx)

1. Place in the directory specified in `config.local.yaml → paths.input_root`.
2. Run `python main.py --input ".../hpN.xlsx" --vendor hpe`.
3. Check `unknown_rows.csv` and `run_summary.json` (target: `unknown_count = 0`).
4. If `unknown > 0`: add rules to `rules/hpe_rules.yaml`, repeat step 2.
   **Note:** when changing `hpe_rules.yaml`, always update the HPE golden files (hp1–hp8).
5. Run `python main.py --input ".../hpN.xlsx" --vendor hpe --save-golden`.
6. Add `hpN` to `@pytest.mark.parametrize` in `test_regression_hpe.py`.
7. Run `pytest tests/ -v` and commit `golden/hpN_expected.jsonl`.
