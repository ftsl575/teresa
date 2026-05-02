# Spec Classifier (Dell · Cisco · HPE · Lenovo · xFusion · Huawei)

Deterministic rule-based pipeline for classifying Dell, Cisco CCW, HPE, Lenovo (DCSC), xFusion (FusionServer eDeal), and Huawei (eDeal) Excel specification files.

**Excel in → parse → normalize → classify → Excel/JSON/CSV out.**
Classification uses YAML rules + regex. No ML. Fully reproducible.

---

## Requirements

- Python 3.10+
- `pip install -r requirements.txt`

---

## Virtual Environment

The project uses an **external** virtual environment. The repository must remain code-only; no `.venv` directory is allowed inside the project.

**Current venv location:** `C:\venv`

**Activation (PowerShell):**
```powershell
C:\venv\Scripts\Activate.ps1
```

**Or run without activation:**
```powershell
C:\venv\Scripts\python.exe main.py --input input/dl1.xlsx
```

Install dependencies into the external venv: `pip install -r requirements.txt` (with the venv activated) or `C:\venv\Scripts\pip.exe install -r requirements.txt`.

---

## Quick Start

По умолчанию вход и выход — каталоги `input` и `output` относительно текущей директории (или из config). Репозиторий остаётся только с кодом.

```bash
cd spec_classifier
pip install -r requirements.txt

# Создать папки (один раз)
mkdir input
mkdir output

# Положить .xlsx в input/, затем:

# Одиночный Dell
python main.py --input input/dl1.xlsx

# Одиночный Cisco CCW
python main.py --input input/ccw_1.xlsx --vendor cisco

# Batch: все .xlsx из input
python main.py --batch-dir input
```

**Где искать результат:** `output/dell_run/run-YYYY-MM-DD__HH-MM-SS-<stem>/` (Dell), `output/cisco_run/run-.../` (Cisco) или `output/hpe_run/run-.../` (HPE). Подробно: [docs/user/RUN_PATHS_AND_IO_LAYOUT.md](docs/user/RUN_PATHS_AND_IO_LAYOUT.md), [docs/user/CLI_CONFIG_REFERENCE.md](docs/user/CLI_CONFIG_REFERENCE.md).

---

## One-button run (Windows)

```powershell
.\scripts\run_full.ps1
```

Запускает тесты + batch-прогон всех вендоров. Логи в `temp_root/diag/runs/<timestamp>/` (temp_root из config.local.yaml).

- Только тесты: `.\scripts\run_tests.ps1`
- Чистка мусора: `.\scripts\clean.ps1`

Настройка путей: скопировать `config.local.yaml.example` → `config.local.yaml`, задать свои пути. Подробнее: [docs/dev/ONE_BUTTON_RUN.md](docs/dev/ONE_BUTTON_RUN.md).

---

## Output

Each run creates a timestamped folder under **output_root** (default `output` relative to cwd). Inside it, vendor subfolders are created:

**Single run:** `output_root/dell_run/run-YYYY-MM-DD__HH-MM-SS-<stem>/`, `output_root/cisco_run/run-.../` or `output_root/hpe_run/run-.../`
**Batch:** per-file run folders + `output_root/<vendor>_run/run-YYYY-MM-DD__HH-MM-SS-TOTAL/`

### Per-run artifacts

| File | Description |
|---|---|
| `classification.jsonl` | Classification result per row (entity_type, state, device_type, hw_type) |
| `run_summary.json` | Aggregate counts: entity types, states, hw_types, unknown count |
| `cleaned_spec.xlsx` | Filtered spec (types from config: BASE, HW, SOFTWARE, SERVICE; PRESENT only) |
| `<stem>_annotated.xlsx` | Original file + 6 added columns: Entity Type, State, device_type, hw_type, row_kind, matched_rule_id |
| `<stem>_branded.xlsx` | Branded spec (Dell only; not created for Cisco or HPE) |
| `unknown_rows.csv` | Rows that matched no rule — review these after each run |
| `rows_raw.json` | Raw parsed rows (debug) |
| `rows_normalized.json` | Normalized rows with row_kind (debug) |
| `header_rows.csv` | Section separator rows |
| `run.log` | Pipeline log for this run |

### TOTAL folder (batch mode)

`run-YYYY-MM-DD__HH-MM-SS-TOTAL/` aggregates the three presentation files from every
per-run folder: `<stem>_annotated.xlsx`, `<stem>_branded.xlsx`, `<stem>_cleaned_spec.xlsx`.

---

## CLI Reference

| Option | Default | Description |
|---|---|---|
| `--vendor {dell,cisco,hpe,lenovo,xfusion,huawei}` | `dell` | Vendor adapter: Dell spec, Cisco CCW, HPE BOM, Lenovo DCSC, xFusion FusionServer eDeal, Huawei eDeal |
| `--input PATH` | — | **Required** (single-file mode). Path to input .xlsx |
| `--batch-dir PATH` | — | Batch mode: process all .xlsx in this directory |
| `--config PATH` | `config.yaml` | Config YAML |
| `--output-dir PATH` | from config `paths.output_root` or `cwd/output` | Top-level output root; inside it `dell_run/`, `cisco_run/`, `hpe_run/` and run folders are created |
| `--save-golden` | — | Save golden/<stem>_expected.jsonl without confirmation |
| `--update-golden` | — | Overwrite golden with interactive confirmation |

Either `--input`, `--batch-dir`, or `--batch` is required. Full reference: [docs/user/CLI_CONFIG_REFERENCE.md](docs/user/CLI_CONFIG_REFERENCE.md). Paths and I/O layout: [docs/user/RUN_PATHS_AND_IO_LAYOUT.md](docs/user/RUN_PATHS_AND_IO_LAYOUT.md).

---

## Vendor Support

- **Dell (default):** Parses Dell export (header row by "Module Name"). All artifacts including branded spec. Use `--vendor dell` or omit.
- **Cisco CCW:** Parses Cisco Commerce Workspace export (sheet **"Price Estimate"**). Same pipeline; annotated Excel gets extra columns (line_number, service_duration_months). Branded spec is not generated for Cisco. `run_summary.json` includes `vendor_stats` (e.g. top_level_bundles_count, max_hierarchy_depth).
- **HPE:** Parses HPE QuoteBuilder BOM (sheet **"BOM"**, columns Product #, Product Description). Same pipeline; annotated Excel gets HPE vendor columns. Branded spec is not generated for HPE. `run_summary.json` includes `vendor_stats` (e.g. factory_integrated_count).
- **Lenovo:** Parses Lenovo DCSC export (sheet **"Configuration"** or first sheet; header row located by "Option Name" / "Option ID"). Annotated Excel gets Lenovo vendor columns; branded spec is not generated for Lenovo. Test files: `L1.xlsx ... L11.xlsx`.
- **xFusion:** Parses xFusion FusionServer eDeal export (header row located by "Configuration Name" / "Component Type"; G-prefix part numbers normalized via `BASE-XF-001` / `DT-XF-021`). Branded spec is not generated for xFusion.
- **Huawei:** Parses Huawei eDeal export (sheets for ICT/Server/Storage/WLAN catalogs; header row located by "Material Code" / "Description"). Supports `device_type=storage_enclosure` (Disk Enclosure family) and `device_type=io_module` (OceanStor SmartIO modules). Branded spec is not generated for Huawei.

For the full per-row classification taxonomy (`device_type`, `hw_type`, vendor coverage matrix, cross-vendor divergences) see [`docs/taxonomy/hw_type_taxonomy.md`](docs/taxonomy/hw_type_taxonomy.md).

**Config:** Rules per vendor in `config.yaml`:

```yaml
vendor_rules:
  dell: "rules/dell_rules.yaml"
  cisco: "rules/cisco_rules.yaml"
  hpe: "rules/hpe_rules.yaml"
  lenovo: "rules/lenovo_rules.yaml"
  xfusion: "rules/xfusion_rules.yaml"
  huawei: "rules/huawei_rules.yaml"
```

**Cisco parser limitations:**
- Sheet name must be exactly `"Price Estimate"` (no fallback).
- Empty Part Number within data is allowed; parser uses last non-empty Part Number row to determine data end.
- Trailing `=` on Part Number (e.g. `SFP-10G-SR-S=`) is stripped automatically.

---

## Test Data

Test files (dl1–dl5.xlsx for Dell, ccw_1.xlsx/ccw_2.xlsx for Cisco, hp1–hp8.xlsx for HPE)
are **not stored in git**. Place them in `C:\Users\G\Desktop\INPUT\`
(or configure `paths.input_root` in `config.local.yaml`).
Smoke, regression, and threshold tests skip automatically if files are absent.

---

## Running Tests

```bash
# Unit tests only (no xlsx needed)
pytest tests/test_rules_unit.py tests/test_state_detector.py tests/test_normalizer.py -v

# Full suite (requires INPUT\ files + golden/)
pytest tests/ -v --tb=short

# Regression only
pytest tests/test_regression.py -v

# Cisco тесты
pytest tests/test_cisco_parser.py tests/test_cisco_normalizer.py \
       tests/test_regression_cisco.py tests/test_unknown_threshold_cisco.py -v
```

---

## Updating Golden (after rule changes)

```bash
python main.py --input "C:\Users\G\Desktop\INPUT\dl1.xlsx" --save-golden
# Repeat for dl2..dl5 as needed
# Cisco: python main.py --input "C:\Users\G\Desktop\INPUT\ccw_1.xlsx" --vendor cisco --save-golden (and ccw_2)
pytest tests/test_regression.py -v
```

---

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `Input file not found` | Wrong `--input` path | Use absolute path or run from `spec_classifier/` |
| `Config file not found` | Wrong `--config` path | Default is `config.yaml` in CWD |
| `No header row found` | Excel missing `"Module Name"` cell | Verify first sheet has `Module Name` header in first 20 rows |
| `Rules file not found` | `vendor_rules` in config invalid | Check `config.yaml` → `vendor_rules` path |
| Regression test fails | Rules changed without golden update | Run `--save-golden`, review diff carefully |
| `unknown_rows.csv` not empty | Input has rows matching no rule | Review patterns; add rules per `docs/rules/RULES_AUTHORING_GUIDE.md` |
| `Sheet 'Price Estimate' not found` | Cisco файл содержит другой лист | Убедитесь что загружен именно CCW export; список листов будет в сообщении об ошибке |
| `--vendor cisco` — нет `_branded.xlsx` | Ожидаемо | Cisco branded spec не создаётся |

---

## Audit & Cluster Analysis

Two scripts extend Teresa with post-run quality checks and pattern discovery.

### batch_audit.py — Rule & AI Audit

Checks all `*_annotated.xlsx` outputs for classification errors (E-codes)
and AI mismatches. Key checks include:
- **E2:** UNKNOWN entity (no rule matched)
- **E17:** HW row with no device_type or hw_type determined
- **E18:** LOGISTIC rows with physical keywords (cord, cable, rail, bracket, kit, rack, pdu, ups) but no device_type
```bash
# Rule-based only (fast, no API key needed)
python batch_audit.py --output-dir C:\Users\G\Desktop\OUTPUT --no-ai

# Full audit with AI validation
$env:OPENAI_API_KEY="sk-..."
python batch_audit.py --output-dir C:\Users\G\Desktop\OUTPUT
```

Outputs: `audit_report.json`, `audit_summary.xlsx`, `*_audited.xlsx` per file.

---

### cluster_audit.py — Pattern Mining

Clusters unclassified rows to discover new YAML rules. 
Reads `*_audited.xlsx` (or `*_annotated.xlsx`) from output dir.
```bash
# Preview candidates without clustering
python cluster_audit.py --output-dir C:\Users\G\Desktop\OUTPUT --dry-run

# Full clustering run
python cluster_audit.py --output-dir C:\Users\G\Desktop\OUTPUT

# Filter by vendor
python cluster_audit.py --output-dir C:\Users\G\Desktop\OUTPUT --vendor hpe

# Custom cluster parameters
python cluster_audit.py --output-dir C:\Users\G\Desktop\OUTPUT --min-cluster-size 5 --max-clusters 30
```

| Argument | Default | Description |
|---|---|---|
| `--output-dir` | required | Path to folder with *_audited.xlsx or *_annotated.xlsx |
| `--vendor` | all | Filter by vendor: dell / hpe / cisco |
| `--min-cluster-size` | 3 | Minimum rows to form a cluster |
| `--max-clusters` | 50 | Maximum number of clusters |
| `--dry-run` | off | Show candidate counts and exit |

Outputs: `cluster_summary.xlsx` + updates `audit_report.json` with `clusters` section.

---

### Recommended Workflow
```bash
# 1. Run Teresa
python main.py --batch-dir C:\Users\G\Desktop\INPUT

# 2. Rule-based audit
python batch_audit.py --output-dir C:\Users\G\Desktop\OUTPUT --no-ai

# 3. Cluster unclassified rows
python cluster_audit.py --output-dir C:\Users\G\Desktop\OUTPUT

# 4. Review cluster_summary.xlsx → write YAML rules

# 5. Re-run Teresa + audit → verify E2/E17 reduction
python batch_audit.py --output-dir C:\Users\G\Desktop\OUTPUT --no-ai
```

---

## Documentation

Full documentation: [`docs/DOCS_INDEX.md`](docs/DOCS_INDEX.md)

Changelog: [`CHANGELOG.md`](CHANGELOG.md)
