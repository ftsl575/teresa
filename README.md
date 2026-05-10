# Teresa — Excel Spec Classifier

Deterministic, rule-based pipeline that turns vendor hardware Bills of Materials (Excel `.xlsx`)
into structured, audited classification output for **Dell, Cisco CCW, HPE, Lenovo (DCSC),
xFusion (FusionServer eDeal), and Huawei (eDeal)**.

> Excel in → parse → normalize → classify → Excel/JSON/CSV out.
> No ML; everything is YAML rules + regex. Fully reproducible.

---

## Repository layout

The repo is two things stacked:

- **Repo root** — a thin Windows launcher: `run.ps1` (PowerShell orchestrator),
  `teresa.bat` (double-click → GUI), `teresa_gui.py` (PyQt6 GUI).
  No Python package lives here.
- **`spec_classifier/`** — the actual codebase: CLI entry (`main.py`),
  audits (`batch_audit.py`, `cluster_audit.py`), source tree (`src/`),
  per-vendor YAML rules (`rules/`), pytest suite (`tests/`), golden fixtures,
  and long-form docs (`docs/`). INPUT specs, OUTPUT runs, and the venv live **outside** the repo.

---

## Quick Start (Windows)

Prerequisites: Windows 10+, **Python 3.10+**, PowerShell.

```powershell
# 1. Clone
git clone <repo-url> teresa
cd teresa

# 2. Create or activate a venv.
#    Default suggestion: C:\venv  (override freely — any venv location works)
python -m venv C:\venv
C:\venv\Scripts\Activate.ps1
pip install -r spec_classifier\requirements.txt

# 3. Optional: customise paths (skip to use defaults)
Copy-Item spec_classifier\config.local.yaml.example spec_classifier\config.local.yaml
# Edit spec_classifier\config.local.yaml  →  set paths.input_root / paths.output_root
# Defaults if you skip this step:
#   INPUT  = %USERPROFILE%\Desktop\INPUT\
#   OUTPUT = %USERPROFILE%\Desktop\OUTPUT\

# 4. Place vendor .xlsx files into INPUT\<vendor>\, e.g.
#    %USERPROFILE%\Desktop\INPUT\huawei\hu1.xlsx

# 5. Run the pipeline
.\run.ps1                                   # all 6 vendors + audits + pytest
.\run.ps1 -Vendor huawei -NoAi -SkipTests  # single-vendor smoke (no OpenAI key needed)
```

Output lands in `%USERPROFILE%\Desktop\OUTPUT\<vendor>_run\run-YYYY-MM-DD__HH-MM-SS-<stem>\`.

---

## Common commands

Run from the repo root in PowerShell.

| Command | What it does |
|---|---|
| `.\run.ps1` | Full pipeline + rule audit + AI audit + cluster + pytest |
| `.\run.ps1 -NoAi` | Same, without AI audit (no `OPENAI_API_KEY` needed) |
| `.\run.ps1 -Vendor <dell\|cisco\|hpe\|lenovo\|huawei\|xfusion>` | One vendor end-to-end |
| `.\run.ps1 -TestsOnly` | pytest only |
| `.\run.ps1 -SkipTests` | Full run without pytest at the end |
| `.\run.ps1 -Vendor huawei -NoAi -SkipTests` | Quick smoke run |
| double-click `teresa.bat` | Launches the PyQt6 GUI |

For direct CLI invocation (single-file classification, golden workflow, batch flags),
see `spec_classifier/README.md`.

---

## Configuration

Two-layer YAML overlay: `spec_classifier/config.yaml` (committed defaults) +
`spec_classifier/config.local.yaml` (gitignored; copy from `config.local.yaml.example`, local file wins).
Set `paths.input_root` / `paths.output_root` there if the defaults do not match your layout.

`C:\venv` is the **suggested** venv location, not a hard requirement — any venv works.

---

## Vendor support

| Vendor | Sheet / parser hint |
|---|---|
| Dell | Sentinel column `Module Name` in first 20 rows |
| Cisco CCW | Sheet `Price Estimate` |
| HPE | Sheet `BOM`, columns `Product #` + `Product Description` |
| Lenovo | Sheet `Configuration` (or first sheet); markers `Option Name` / `Option ID` |
| xFusion (FusionServer eDeal) | Markers `Configuration Name` / `Component Type`; G-prefix part numbers |
| Huawei (eDeal) | ICT/Server/Storage/WLAN catalog sheets; markers `Material Code` / `Description` |

Per-row classification taxonomy (`device_type`, `hw_type`, vendor coverage matrix, divergences)
is in `spec_classifier/docs/taxonomy/hw_type_taxonomy.md`.

---

## Learn more

| What you want | Where to look |
|---|---|
| Full CLI reference, golden workflow, troubleshooting | [`spec_classifier/README.md`](spec_classifier/README.md) |
| Pipeline internals, E-codes, business rules, dev cycle | [`spec_classifier/CLAUDE.md`](spec_classifier/CLAUDE.md) |
| Launcher flags, GUI behavior | [`LAUNCHER_README.md`](LAUNCHER_README.md) |
| Adding a new vendor | [`spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md`](spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md) |
| Rules authoring | [`spec_classifier/docs/rules/RULES_AUTHORING_GUIDE.md`](spec_classifier/docs/rules/RULES_AUTHORING_GUIDE.md) |
| Recent changes | [`spec_classifier/CHANGELOG.md`](spec_classifier/CHANGELOG.md) |
| Project status / current focus | [`.planning/STATE.md`](.planning/STATE.md) |

---

## Tests

Tests live in `spec_classifier/tests/`. Run from `spec_classifier/`:

```powershell
cd spec_classifier
pytest tests/ -v --tb=short                                     # full suite
pytest tests/test_rules_unit.py tests/test_state_detector.py tests/test_normalizer.py -v  # unit-only (no INPUT files needed)
```

The session fails if `skipped/total > 0.50` or `passed == 0`. See `spec_classifier/README.md` for full test guidance.
