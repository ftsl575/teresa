# Operational Notes — spec_classifier (teresa)

## 1. Single-file run

```bash
python main.py --input path/to/file.xlsx --output-dir output
python main.py --input "C:\Users\<USERNAME>\Desktop\INPUT\ccw_1.xlsx" --vendor cisco
```

Result: folder `{vendor}_run/run-YYYY-MM-DD__HH-MM-SS-<stem>/` with the full artifact set.

---

## 2. Batch run

```bash
python main.py --batch-dir "C:\Users\<USERNAME>\Desktop\INPUT"
```

Creates: for each `.xlsx` in the directory — its own `run-YYYY-MM-DD__HH-MM-SS-<stem>/` folder, plus one `run-YYYY-MM-DD__HH-MM-SS-TOTAL/` folder.

---

## 3. TOTAL folder

Contains aggregated presentation files for all files processed in the session: `<stem>_annotated.xlsx`, `<stem>_branded.xlsx`, `<stem>_cleaned_spec.xlsx`. Used for handing off to the client or consolidating a single session. For Cisco and HPE runs `<stem>_branded.xlsx` is not copied (the file is not created).

**Important:** `batch_audit.py` automatically excludes TOTAL folders from processing (`-TOTAL` in the parent folder name). This prevents double-counting rows in `audit_report.json`.

---

## 4. Run folder naming

The only canonical format in code: **run-YYYY-MM-DD__HH-MM-SS-\<stem\>** (e.g. `run-2026-02-26__06-09-53-dl1`). On collision (same second), a suffix `_1`, `_2`, … is appended. Batch TOTAL: **run-YYYY-MM-DD__HH-MM-SS-TOTAL**.

---

## 5. Artifact storage policy

- **output/** — not in git.
- **rows_raw.json**, **rows_normalized.json** — debug artifacts; can be deleted after verification.
- **run_summary.json**, **classification.jsonl** — keep for audit if needed.
- **unknown_rows.csv** — review after each run; if `unknown_count` rises, update rules.
- **golden/*.jsonl** — in git; update only deliberately after rule/logic changes.

---

## 6. Working with a new dataset

1. Place the xlsx in `C:\Users\<USERNAME>\Desktop\INPUT\<vendor>\` (e.g. `dl5.xlsx`).
2. Run the pipeline: `python main.py --input "C:\Users\<USERNAME>\Desktop\INPUT\dl5.xlsx"`.
3. Check `unknown_rows.csv` and `run_summary.json`.
4. If needed, add rules to `dell_rules.yaml` and re-run.
5. Generate golden: `python main.py --input "C:\Users\<USERNAME>\Desktop\INPUT\dl5.xlsx" --save-golden`.
6. Add the new file (dlN) to the parametrize list in regression tests as needed.
7. Run `pytest tests/ -v` and commit changes.

New Cisco dataset (ccwN.xlsx):

1. Place file at `C:\Users\<USERNAME>\Desktop\INPUT\ccw_N.xlsx`.
2. Run `python main.py --input "C:\Users\<USERNAME>\Desktop\INPUT\ccw_N.xlsx" --vendor cisco`.
3. Check `unknown_rows.csv`. Target: `unknown_count = 0`.
4. If `unknown_count > 0`: add rules to `rules/cisco_rules.yaml`, re-run.
5. `python main.py --input "C:\Users\<USERNAME>\Desktop\INPUT\ccw_N.xlsx" --vendor cisco --save-golden`
6. Add `ccw_N` to the regression test; `pytest tests/ -v`.

New HPE dataset (hpN.xlsx):

1. Place the BOM file at `C:\Users\<USERNAME>\Desktop\INPUT\hpe\hpN.xlsx` (sheet "BOM", columns: Product #, Description, Qty, Unit Price).
2. Run `python main.py --input "C:\Users\<USERNAME>\Desktop\INPUT\hpe\hpN.xlsx" --vendor hpe`.
3. Check `unknown_rows.csv`. Target: `unknown_count = 0`.
4. If `unknown_count > 0`: add rules to `rules/hpe_rules.yaml`; re-run.
5. `python main.py --input "C:\Users\<USERNAME>\Desktop\INPUT\hpe\hpN.xlsx" --vendor hpe --save-golden`
6. Add `hpN` to `test_regression_hpe.py` and `test_unknown_threshold_hpe.py`; `pytest tests/test_regression_hpe.py tests/test_unknown_threshold_hpe.py -v`.

---

## 7. Full run (pipeline + audit + clustering)

Use `run.ps1` from the repo root:

```powershell
# From teresa/ repo root:
.\run.ps1

# Rule-based audit only (no AI, no OPENAI_API_KEY required):
.\run.ps1 -NoAi

# Single vendor:
.\run.ps1 -Vendor dell

# Smoke (no AI, skip tests):
.\run.ps1 -Vendor huawei -NoAi -SkipTests
```

`run.ps1` executes in order:
1. Pipeline for all active vendors (dell, cisco, hpe, lenovo, huawei, xfusion)
2. `batch_audit.py` (with AI by default; add `-NoAi` to skip)
3. `cluster_audit.py`

---

## Known Tech Debt: batch_audit.py vendor-specific hardcoding

`batch_audit.py` contains vendor-specific logic in the following places:

1. **DEVICE_TYPE_MAP** — `device_type→hw_type` mapping per vendor (loaded from YAML since audit_1E)
2. **validate_row() state logic** — per-vendor branches for state validation (now data-driven via `E4_STATE_VALIDATORS`)
3. **LLM_SYSTEM prompt** — vendor-aware prompt text
4. **Known FP cases** — vendor-tagged false-positive patterns
5. **fp_patterns / comments** — vendor-specific logic in comments

Current state: vendors covered are dell, cisco, hpe, lenovo, huawei, xfusion. Functional.

Refactor trigger: before adding a 7th vendor. See `.planning/codebase/CONCERNS.md` for details.

Recommended solution: move vendor-specific configurations to YAML files or adapter-registry so adding a vendor does not require edits to `batch_audit.py`.

Source: audit_1G P1-6.
