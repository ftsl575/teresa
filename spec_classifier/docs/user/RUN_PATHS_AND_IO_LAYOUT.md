# Run Paths & I/O Layout — Input/Output roots

For run.ps1 switches, see `run.ps1 -?` or [docs/dev/ONE_BUTTON_RUN.md](../dev/ONE_BUTTON_RUN.md). For path discovery internals, see below.

## Goal: code-only repository

The `teresa/` folder (`spec_classifier/`) contains ONLY source code, rules, documentation, and tests. Input data, run results, caches, and temporary files are ALWAYS stored OUTSIDE.

## Data Isolation Policy

Four directories are ALWAYS separate:

| Role      | Path                                    | Contents                              |
|-----------|-----------------------------------------|---------------------------------------|
| CODE      | `C:\Users\<USERNAME>\Desktop\teresa`    | Only `.py`, `.yaml`, `.md`, `.ps1`, tests |
| INPUT     | `C:\Users\<USERNAME>\Desktop\INPUT`     | Source `.xlsx` files from configurator |
| OUTPUT    | `C:\Users\<USERNAME>\Desktop\OUTPUT`    | Run results (run folders)             |
| TEMPORARY | `C:\Users\<USERNAME>\Desktop\temporary` | `__pycache__`, `.pytest_cache`, `diag/` |

How this is enforced:

1. `config.local.yaml` sets absolute paths (not committed to git).
2. `pyproject.toml` redirects `.pytest_cache` to `../../temporary/` (from `spec_classifier` → `Desktop\temporary\.pytest_cache`).
3. `PYTHONPYCACHEPREFIX` and `PYTEST_ADDOPTS` env vars are exported by both `run.ps1` and `teresa_gui.py` from `config.local.yaml::temp_root` (Phase 4 defense-in-depth) so `__pycache__` and `.pytest_cache` land under the temp root regardless of entry point.
4. `.gitignore` blocks `input/`, `output/`, `temporary/`, `__pycache__/`, `.pytest_cache/`.
5. `clean.ps1` removes any leaked cache files from the repo (also invoked by `run.ps1` at the start of every run unless `-NoClean`).

---

### Virtual Environment Policy

The virtual environment is **external** to the repository. Current path: `C:\venv`. The repository must not store virtual environments; this keeps the repo lightweight and clean. Dependency installation is done via `requirements.txt` (install into the external venv after creating it with `python -m venv C:\venv`).

---

## Default folders

| Purpose   | Default path |
|-----------|-------------|
| **INPUT** | `input/` (relative to cwd) — directory with input `.xlsx` files (single file is specified by file path; for batch — directory of files). |
| **OUTPUT** | `output/` (relative to cwd) — output root; `dell_run/`, `cisco_run/`, `hpe_run/`, `lenovo_run/`, `huawei_run/`, `xfusion_run/` are created inside, then run folders. |
| **TEMP** | **Not used.** The pipeline works in memory (parse → normalize → classify) and writes only to the final run folder. A separate temp directory is not required. |

---

## Recommended INPUT folder structure

When working with multiple vendors, keep files in separate sub-folders:

```
input/
  dell/      <- dl*.xlsx
  cisco/     <- ccw*.xlsx
  hpe/       <- hp*.xlsx
  lenovo/    <- L*.xlsx
  huawei/    <- hu*.xlsx
  xfusion/   <- xf*.xlsx
```

Sub-folders `dell/`, `cisco/`, `hpe/` etc. are used by the system as standard paths when calling `get_input_root_dell()` / `get_input_root_cisco()` / `get_input_root_hpe()` etc. (see `conftest.py`). If the sub-folder is missing, the `input_root` is used.

Run:

```bash
python main.py --batch-dir input/dell    --vendor dell
python main.py --batch-dir input/cisco   --vendor cisco
python main.py --batch-dir input/hpe     --vendor hpe
python main.py --batch-dir input/lenovo  --vendor lenovo
python main.py --batch-dir input/huawei  --vendor huawei
python main.py --batch-dir input/xfusion --vendor xfusion
```

This prevents files from one vendor being processed by another vendor's adapter.

---

## Configuration path priority

1. **CLI** — explicit arguments take highest priority:
   `--output-dir`, `--batch-dir` (or directory specified in `--input` for a single file).
2. **config.yaml** — `paths` section:
   `paths.input_root`, `paths.output_root` (used when the corresponding CLI argument is not passed).
3. **Defaults** — if `paths` or the key is missing from config:
   `input`, `output` (relative to current directory).

---

## Exact output tree

Top level — **output_root** (default `output/`). Vendor sub-dirs and run folders are created below.

### Dell

```
output/
  dell_run/
    run-YYYY-MM-DD__HH-MM-SS-<stem>/
      rows_raw.json
      rows_normalized.json
      classification.jsonl
      cleaned_spec.xlsx
      header_rows.csv
      unknown_rows.csv
      run_summary.json
      run.log
      <stem>_annotated.xlsx
      <stem>_branded.xlsx
```

- Every Dell run folder contains all listed artifacts, including **run.log** and **\<stem\>_branded.xlsx**.

### Cisco

```
output/
  cisco_run/
    run-YYYY-MM-DD__HH-MM-SS-<stem>/
      rows_raw.json
      rows_normalized.json
      classification.jsonl
      cleaned_spec.xlsx
      header_rows.csv
      unknown_rows.csv
      run_summary.json
      run.log
      <stem>_annotated.xlsx
```

- **run.log** is present in every run.

### HPE

```
output/
  hpe_run/
    run-YYYY-MM-DD__HH-MM-SS-<stem>/
      rows_raw.json
      rows_normalized.json
      classification.jsonl
      cleaned_spec.xlsx
      header_rows.csv
      unknown_rows.csv
      run_summary.json
      run.log
      <stem>_annotated.xlsx
```

- **run.log** is present in every run.

### Batch (TOTAL)

In batch mode, an aggregation folder is additionally created:
`output_root\<vendor>_run\run-YYYY-MM-DD__HH-MM-SS-TOTAL\` with copies of the presentation files from each run (with stem prefix).

---

## Example commands

### Create INPUT and OUTPUT folders

```bash
mkdir input
mkdir output
```

### Single Dell run

```bash
cd spec_classifier
# Place dl1.xlsx in input/, then:
python main.py --input input/dl1.xlsx
# Result: output/dell_run/run-YYYY-MM-DD__HH-MM-SS-dl1/
```

### Single Cisco run

```bash
cd spec_classifier
python main.py --input input/ccw_1.xlsx --vendor cisco
# Result: output/cisco_run/run-YYYY-MM-DD__HH-MM-SS-ccw_1/
```

### Single HPE run

```bash
cd spec_classifier
python main.py --input input/hpe/hp1.xlsx --vendor hpe
# Result: output/hpe_run/run-YYYY-MM-DD__HH-MM-SS-hp1/
```

### Batch (all .xlsx from input)

```bash
cd spec_classifier
python main.py --batch-dir input
# Result: output/dell_run/run-...-<stem>/ for each file + run-...-TOTAL/
```

---

## Common mistakes

- **Do not specify `--output-dir output` when running from the repository** — artifacts will appear in `spec_classifier/output/` and pollute the repo.
- **Do not commit** `.venv/`, `__pycache__/`, `.pytest_cache/`, or any `out/`, `output/` with run results.
- **Do not run the pipeline without `config.local.yaml`** — relative defaults will create `input/` and `output/` inside the repo.

---

## Audit & Cluster Output Paths

`batch_audit.py` and `cluster_audit.py` create artifacts next to the vendor run folders or in the explicitly specified directory.

### batch_audit.py

```
output/
  audit_report.json              <- full JSON report (bugs, yaml_candidates, rule_issues, stats)
  audit_summary.xlsx             <- summary Excel with E-codes across all files
  <vendor>_run/
    <run-folder>/
      <stem>_annotated_audited.xlsx  <- annotated copy + pipeline_check column
```

Run:

```bash
python batch_audit.py --output-dir "C:\Users\<USERNAME>\Desktop\OUTPUT" --no-ai
python batch_audit.py --output-dir "C:\Users\<USERNAME>\Desktop\OUTPUT" --vendor hpe
```

Key artifacts:

| File | Contents |
|------|---------|
| `audit_report.json` | Full report: bugs, yaml_candidates, rule_issues, claude_prompt. |
| `audit_summary.xlsx` | One row per issue: vendor, file, issue count, E-codes, SKU, Module. |
| `*_annotated_audited.xlsx` | Source annotated + `pipeline_check` column (OK or E-codes). |

### cluster_audit.py

```
output/
  cluster_summary.xlsx            <- UNKNOWN row clusters with proposed_device_type
```

Run:

```bash
python cluster_audit.py --output-dir "C:\Users\<USERNAME>\Desktop\OUTPUT"
python cluster_audit.py --output-dir "C:\Users\<USERNAME>\Desktop\OUTPUT" --dry-run
```

Key artifacts:

| File | Contents |
|------|---------|
| `cluster_summary.xlsx` | Clusters: `cluster_id`, `count`, `vendors`, `top_terms`, `proposed_device_type`, examples, `suggested_yaml_rule`. |

---

## See also

- [CLI_CONFIG_REFERENCE.md](CLI_CONFIG_REFERENCE.md) — all CLI parameters and config.
- [DOCS_INDEX.md](../DOCS_INDEX.md) — documentation index.
