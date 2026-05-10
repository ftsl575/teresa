# CLI and Config Reference — spec_classifier

Detailed description of input/output paths, priorities, and directory structure: **[RUN_PATHS_AND_IO_LAYOUT.md](RUN_PATHS_AND_IO_LAYOUT.md)**.

## 1. CLI parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `--input PATH` | Yes (single-file) | — | Path to the input `.xlsx` file. |
| `--batch-dir PATH` | Yes (batch) | — | Directory with `.xlsx` files; all files are processed alphabetically. |
| `--vendor VENDOR` | No | `dell` | Vendor: `dell`, `cisco`, `hpe`, `lenovo`, `huawei`, `xfusion`. Selects the parsing adapter and rules file. |
| `--config PATH` | No | `config.yaml` | Path to the YAML config. |
| `--output-dir PATH` | No | from config `paths.output_root` or `cwd/output` | Output root. Vendor sub-dirs are created inside: `dell_run/`, `cisco_run/`, `hpe_run/`, `lenovo_run/`, `huawei_run/`, `xfusion_run/`, each containing run folders `run-YYYY-MM-DD__HH-MM-SS-<stem>/`. |
| `--batch` | No | — | Batch: all `.xlsx` from `input_root` (config or default). |
| `--save-golden` | No | — | Save golden without confirmation. |
| `--update-golden` | No | — | Overwrite golden with confirmation (y/N). |

Note: exactly one of `--input`, `--batch-dir`, or `--batch` is required.

---

## 2. Output structure

**output_root** is the top-level output root (default: `cwd/output` or `config paths.output_root`). Vendor sub-dirs are automatically created inside:

- `output_root/dell_run/run-YYYY-MM-DD__HH-MM-SS-<stem>/` — Dell (includes `<stem>_branded.xlsx`, `run.log`)
- `output_root/cisco_run/run-YYYY-MM-DD__HH-MM-SS-<stem>/` — Cisco (no branded, has `run.log`)
- `output_root/hpe_run/run-YYYY-MM-DD__HH-MM-SS-<stem>/` — HPE (no branded, has `run.log`)
- `output_root/lenovo_run/run-YYYY-MM-DD__HH-MM-SS-<stem>/` — Lenovo
- `output_root/huawei_run/run-YYYY-MM-DD__HH-MM-SS-<stem>/` — Huawei
- `output_root/xfusion_run/run-YYYY-MM-DD__HH-MM-SS-<stem>/` — xFusion

Without `--output-dir`, uses `paths.output_root` from config or `cwd/output`; no artifacts are created inside the repository. Full description: [RUN_PATHS_AND_IO_LAYOUT.md](RUN_PATHS_AND_IO_LAYOUT.md).

---

## 3. Examples

All examples use the default external paths (`Desktop\INPUT`, `Desktop\OUTPUT`). See [RUN_PATHS_AND_IO_LAYOUT.md](RUN_PATHS_AND_IO_LAYOUT.md) for folder creation and checklist.

```powershell
# Single Dell file (result: C:\Users\<USERNAME>\Desktop\OUTPUT\dell_run\run-...-<stem>\)
python main.py --input "C:\Users\<USERNAME>\Desktop\INPUT\dl1.xlsx"

# Explicit output-root (result: D:\results\dell_run\run-...\)
python main.py --input "C:\Users\<USERNAME>\Desktop\INPUT\dl1.xlsx" --output-dir "D:\results"

# Batch: all .xlsx from INPUT
python main.py --batch-dir "C:\Users\<USERNAME>\Desktop\INPUT"
python main.py --batch

# Cisco CCW (result: OUTPUT\cisco_run\run-...-<stem>\)
python main.py --input "C:\Users\<USERNAME>\Desktop\INPUT\ccw_1.xlsx" --vendor cisco

# Cisco batch
python main.py --batch-dir "C:\Users\<USERNAME>\Desktop\INPUT" --vendor cisco

# HPE single run (result: OUTPUT\hpe_run\run-...-<stem>\)
python main.py --input "C:\Users\<USERNAME>\Desktop\INPUT\hpe\hp1.xlsx" --vendor hpe

# HPE batch
python main.py --batch-dir "C:\Users\<USERNAME>\Desktop\INPUT\hpe" --vendor hpe

# Lenovo
python main.py --input "C:\Users\<USERNAME>\Desktop\INPUT\lenovo\L1.xlsx" --vendor lenovo

# xFusion
python main.py --input "C:\Users\<USERNAME>\Desktop\INPUT\xfusion\xf1.xlsx" --vendor xfusion

# Huawei
python main.py --input "C:\Users\<USERNAME>\Desktop\INPUT\huawei\hu1.xlsx" --vendor huawei

# Save golden (in repo: golden/<stem>_expected.jsonl)
python main.py --input "C:\Users\<USERNAME>\Desktop\INPUT\dl1.xlsx" --save-golden

# Update golden interactively
python main.py --input "C:\Users\<USERNAME>\Desktop\INPUT\dl1.xlsx" --update-golden
```

---

## 4. config.yaml schema

```yaml
# Input/output roots (optional). CLI --output-dir / --batch-dir override.
paths:
  input_root: "input"
  output_root: "output"

# Rule file paths per vendor (used with --vendor)
vendor_rules:
  dell:    "rules/dell_rules.yaml"
  cisco:   "rules/cisco_rules.yaml"
  hpe:     "rules/hpe_rules.yaml"
  lenovo:  "rules/lenovo_rules.yaml"
  huawei:  "rules/huawei_rules.yaml"
  xfusion: "rules/xfusion_rules.yaml"

cleaned_spec:
  # Entity types for cleaned_spec.xlsx
  # Allowed: BASE, HW, CONFIG, SOFTWARE, SERVICE, LOGISTIC, NOTE, UNKNOWN
  include_types:
    - BASE
    - HW
    - SOFTWARE
    - SERVICE

  # true = include only rows with state=PRESENT
  include_only_present: true
```

---

## 5. Compatibility guarantees

- Keys `cleaned_spec.include_types`, `include_only_present` have been stable since v1.0.0.
- `vendor_rules` — mapping of `vendor` → path to YAML rules; determines the rules file for each vendor.
- Unknown keys in `config.yaml` are ignored (forward-compatible).
- Paths are resolved relative to the current working directory (CWD), not relative to the config file location.
- Changes breaking the config contract are reflected in a MAJOR version and in `CHANGELOG.md`.
