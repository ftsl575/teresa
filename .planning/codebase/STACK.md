# Technology Stack

**Analysis Date:** 2026-05-09

The repo is two stacked layers:
1. **Repo root (Windows launcher)** — PowerShell + a thin PyQt6 GUI that orchestrates the pipeline (`run.ps1`, `teresa_gui.py`, `teresa.bat`).
2. **`spec_classifier/`** — Python application: a deterministic, rule-based Excel-spec classifier for six hardware vendors. No ML in the core pipeline; classification is YAML rules + regex via `src/rules/rules_engine.py`.

## Languages

**Primary:**
- Python 3.10+ — the entire `spec_classifier/` codebase, plus the GUI (`teresa_gui.py`). Lower bound `3.10` is asserted by `teresa.bat` ("Install Python 3.10+ and try again").
- PowerShell 5+ — `run.ps1` (single launcher; depends on `[System.Text.Encoding]::UTF8`, `Read-Host -AsSecureString`, `Get-ChildItem`, `Test-Path`).

**Secondary:**
- Windows batch — `teresa.bat` only. Auto-installs `PyQt6` if missing, then spawns the GUI via `pythonw`.
- GNU Make — `spec_classifier/Makefile`, used from Git Bash to regenerate golden fixtures (`generate_golden_dell`, `generate_golden_cisco`, `generate_golden_hpe`).
- YAML — declarative classification rules (`spec_classifier/rules/*_rules.yaml`) and runtime config (`config.yaml`, `config.local.yaml`).

## Runtime

**Environment:**
- CPython 3.10+ on Windows 10 / 11. The codebase is Windows-first but uses `pathlib.Path` everywhere — no hard `\` separators in pipeline code (one minor exception: PowerShell-side path concatenation in `run.ps1`).
- Stdout/stderr are explicitly reconfigured to UTF-8 in `spec_classifier/batch_audit.py:35-40` and `spec_classifier/cluster_audit.py:43-48` because emoji status output otherwise crashes on legacy `cp1251` consoles.
- The launcher pipeline is single-process, single-threaded: `run.ps1` runs each vendor, then audits, then tests, sequentially.
- The GUI launches `run.ps1` in a **new** PowerShell console via `subprocess.Popen(..., creationflags=subprocess.CREATE_NEW_CONSOLE)` (`teresa_gui.py:225-229`) so the user sees raw progress.

**Package Manager:**
- pip (only manager used). Three separate manifests:
  - `spec_classifier/requirements.txt` — core runtime deps (4 packages).
  - `requirements-gui.txt` — GUI-only dep (`PyQt6>=6.5`).
  - Optional, not pinned anywhere: `openai`, `anthropic`, `scikit-learn`, `hdbscan`, `numpy` — imported lazily, see "Key Dependencies".
- Lockfile: **missing** — no `requirements.lock`, no `Pipfile.lock`, no `poetry.lock`, no `uv.lock`. Versions are specified as lower-bound (`>=`) only.
- Virtual environment is **external** to the repo at `C:\venv` (per `spec_classifier/README.md:21` and `spec_classifier/docs/user/RUN_PATHS_AND_IO_LAYOUT.md:32`). The repo enforces a "code-only" policy and gitignores `.venv/`, `venv/`, `env/` (`spec_classifier/.gitignore:5-7`).

## Frameworks

**Core (runtime):**
- `pandas>=2.0.0` — DataFrame operations for Excel I/O. Used by every adapter parser and by all writers (`spec_classifier/src/outputs/{annotated_writer.py,excel_writer.py}`, `batch_audit.py`).
- `openpyxl>=3.1.0` — low-level XLSX read/write (sheet detection, styling). Used directly in `spec_classifier/src/vendors/*/adapter.py` for `can_parse()` sheet probes (e.g. `DellAdapter:13` opens `read_only=True` to look for `"Module Name"`; HPEAdapter looks for sheet `"BOM"`). Also used in `spec_classifier/src/outputs/branded_spec_writer.py` for cell-level styling (`PatternFill`, `Font`, `Alignment`, `Border`).
- `pyyaml>=6.0` — loads vendor rule YAML and config (`spec_classifier/src/rules/rules_engine.py:10`, `main.py:14`, `conftest.py:10`, `batch_audit.py:29`, `cluster_audit.py:19`).

**GUI:**
- `PyQt6>=6.5` — `teresa_gui.py` only. Imports `QApplication`, `QMainWindow`, `QPushButton`, `QLineEdit`, `QCheckBox`, `QTableWidget`, `QGroupBox`, `QMessageBox` (`teresa_gui.py:26-33`). Catppuccin-Mocha-style stylesheet inline at `teresa_gui.py:47-179`.

**Testing:**
- `pytest>=7.0.0` — only test framework. 31 test files under `spec_classifier/tests/`, ~420 collected tests at last freeze (per `spec_classifier/CLAUDE.md` § ТЕКУЩЕЕ СОСТОЯНИЕ).
- `spec_classifier/conftest.py` provides `project_root()`, `load_config()`, vendor-specific input-root resolvers (`get_input_root_dell()` … `get_input_root_xfusion()`), and a `pytest_sessionfinish` hook (lines 141-217) that **fails the session** when `skipped/total > 0.50`, when `passed == 0`, or when `paths.input_root` doesn't exist on disk.
- Test config: `spec_classifier/pyproject.toml` redirects pytest cache to `../../temporary/.pytest_cache` (keeps repo clean).

**Build/Dev:**
- GNU Make — `spec_classifier/Makefile` orchestrates golden generation per vendor. Default `INPUT=C:/Users/G/Desktop/INPUT` overridable via `make generate_golden INPUT=/d/specs/INPUT`.
- No bundler, no transpiler, no linter config committed (`.eslintrc`, `.ruff.toml`, `.flake8`, `pyproject.toml`'s `[tool.ruff]` are all absent). `spec_classifier/.gitignore:15-16` reserves `.ruff_cache/` and `.mypy_cache/` slots, but neither tool is configured.

## Key Dependencies

**Critical (always loaded):**
- `pandas>=2.0.0` — DataFrames, `pd.read_excel(... engine="openpyxl")` is the standard parse path.
- `openpyxl>=3.1.0` — workbook detection (`load_workbook(read_only=True)` in adapters), styling.
- `pyyaml>=6.0` — `yaml.safe_load()` everywhere; rule files, config files.
- `pytest>=7.0.0` — runtime dep because `conftest.py` is loaded even by `--collect-only`.

**Optional (lazy-imported in `batch_audit.py`):**
- `openai` — `import openai; openai.OpenAI(api_key=...)` at `spec_classifier/batch_audit.py:1416,1423`. Only loaded when AI audit is enabled (`--no-ai` skips). Default model: `gpt-4o-mini`.
- `anthropic` — `import anthropic; anthropic.Anthropic(api_key=...)` at `spec_classifier/batch_audit.py:1426,1433`. Selected via `--provider anthropic`. Pricing table for both providers at `batch_audit.py:235-240` (`gpt-4o-mini`, `gpt-4o`, `claude-opus-4-5`, `claude-sonnet-4-5`).
- Failure mode: missing library logs `pip install openai or pip install anthropic` and continues with `use_ai = False`.

**Optional (lazy-imported in `cluster_audit.py`):**
- `scikit-learn` — `TfidfVectorizer` (`cluster_audit.py:284`) and fallback `MiniBatchKMeans` (`cluster_audit.py:296`).
- `hdbscan` — preferred clustering algorithm (`cluster_audit.py:293`). Falls back to KMeans if not installed.
- `numpy` — `cluster_audit.py:416`.
- None of `scikit-learn`, `hdbscan`, `numpy` appear in any `requirements*.txt`; the user must `pip install scikit-learn hdbscan` separately to use cluster mining.

## Configuration

**Environment variables:**
- `OPENAI_API_KEY` — required when AI audit is enabled. Read at `spec_classifier/batch_audit.py:1417`. The GUI persists it via `setx OPENAI_API_KEY ...` at User scope (`teresa_gui.py:198-208`); `run.ps1:80-86` prompts via `Read-Host -AsSecureString` if not set.
- `ANTHROPIC_API_KEY` — required when `--provider anthropic`. Read at `batch_audit.py:1427`.
- `PYTHONPYCACHEPREFIX` and `PYTEST_ADDOPTS` — set by `run.ps1` and `teresa_gui.py` from `config.local.yaml::temp_root`. Together they redirect `__pycache__/` and `.pytest_cache/` to `$temp_root` so cache artifacts never land inside the repo working tree (Phase 4 CACHE-01/CACHE-02; defense-in-depth — both entry points set both vars independently).

**Config layering (`config.yaml` + `config.local.yaml`):**
- `spec_classifier/config.yaml` — committed defaults: `paths.input_root="input"`, `paths.output_root="output"`, `cleaned_spec.include_types=[BASE,HW,SOFTWARE,SERVICE]`, and the `vendor_rules` dict mapping each vendor key to a YAML rule path.
- `spec_classifier/config.local.yaml` — gitignored personal overlay (template at `config.local.yaml.example`). Currently sets `paths.input_root: C:/Users/G/Desktop/INPUT`, `paths.output_root: C:/Users/G/Desktop/OUTPUT`, `temp_root: C:/Users/G/Desktop/temporary`.
- Overlay logic is duplicated in three places — they all do `data.update(local_data)` (or per-key dict-merge for nested dicts):
  - `spec_classifier/main.py:_load_config` (lines 69-86) — full nested merge.
  - `spec_classifier/conftest.py:load_config` (lines 22-39) — same nested merge.
  - `spec_classifier/batch_audit.py:_load_config` (lines 60-70) and `spec_classifier/cluster_audit.py:_load_config` (lines 24-36) — flat `cfg.update(local_cfg)` (subtle inconsistency).
- `run.ps1:36-40` reads `config.local.yaml` with a regex (no YAML parser available in vanilla PowerShell) to pull `input_root` / `output_root` for the launcher's own bookkeeping.
- CLI flags (`--input`, `--batch-dir`, `--output-dir`) override everything (`main.py:289-304`).

**Vendor rule files (declarative classification logic):**
- `spec_classifier/rules/dell_rules.yaml`
- `spec_classifier/rules/cisco_rules.yaml`
- `spec_classifier/rules/hpe_rules.yaml`
- `spec_classifier/rules/lenovo_rules.yaml`
- `spec_classifier/rules/huawei_rules.yaml`
- `spec_classifier/rules/xfusion_rules.yaml`

Each contains `state_rules`, `base_rules`, `entity_type` rule lists with `pattern` (regex) + `rule_id`, plus an `hw_type_rules.device_type_map` that the audit also consumes via `batch_audit._load_device_type_maps()` (`batch_audit.py:78-94`).

**Build:**
- No build step — pure-Python source executed directly via `python main.py …`. No `setup.py`, no `setup.cfg`, no buildable distribution.
- `spec_classifier/pyproject.toml` is minimal (8 lines): only `[tool.pytest.ini_options].cache_dir`, no `[project]`, no `[build-system]`.

## Platform Requirements

**Development:**
- Windows 10 / 11 (PowerShell launcher, `setx`-based env persistence, `pythonw.exe` for windowless GUI launch, `os.startfile()` to open OUTPUT folders at `teresa_gui.py:518`).
- Python 3.10+ in `PATH` (probed by `teresa.bat:11`).
- External venv at `C:\venv` (or wherever the user creates it). Activate via `C:\venv\Scripts\Activate.ps1` per `spec_classifier/README.md:25`.
- INPUT folder at `%USERPROFILE%\Desktop\INPUT` with vendor subfolders (`dell/`, `cisco/`, `hpe/`, `lenovo/`, `huawei/`, `xfusion/`).
- OUTPUT folder at `%USERPROFILE%\Desktop\OUTPUT` (created on first run).

**Production:**
- No deployment target. This is a desktop pipeline tool. Artifacts (`audit_report.json`, `audit_summary.xlsx`, `cluster_summary.xlsx`, per-run `*_audited.xlsx`) are consumed by humans, not servers.
- No web server, no daemon, no scheduler.

## Vendor Adapter Registry

The codebase pluggable surface is `spec_classifier/src/vendors/base.py:VendorAdapter` (ABC). Six concrete adapters:
- `spec_classifier/src/vendors/dell/adapter.py:DellAdapter` (uses shared `src/core/parser.py` — Dell-specific despite living in core; tech debt).
- `spec_classifier/src/vendors/cisco/adapter.py:CiscoAdapter`.
- `spec_classifier/src/vendors/hpe/adapter.py:HPEAdapter` (sheet `"BOM"`, 5 extra cols).
- `spec_classifier/src/vendors/lenovo/adapter.py:LenovoAdapter`.
- `spec_classifier/src/vendors/huawei/adapter.py:HuaweiAdapter`.
- `spec_classifier/src/vendors/xfusion/adapter.py:XFusionAdapter`.

Registered in `spec_classifier/main.py:VENDOR_REGISTRY` (lines 42-49). Adding a vendor requires touching: adapter class, `VENDOR_REGISTRY`, `run.ps1:$ALL_VENDORS` (line 45), and `teresa_gui.py:VENDORS_ACTIVE` (line 38).

---

*Stack analysis: 2026-05-09*
