# External Integrations

**Analysis Date:** 2026-05-09

This is a desktop Excel-spec classifier with a deliberately small integration surface. There are **no databases**, **no web auth**, **no HTTP server**, **no message queues**, **no webhooks**, **no cloud storage**. The only real external integration is an optional LLM API call during audit; everything else is local filesystem I/O against an Excel-based INPUT/OUTPUT layout.

## APIs & External Services

**LLM providers (optional, audit-only):**

- **OpenAI** — default. Used in `spec_classifier/batch_audit.py` for the AI-mismatch layer of the post-pipeline audit.
  - SDK/Client: `openai` (lazy-imported at `batch_audit.py:1416`). Constructed via `openai.OpenAI(api_key=api_key)` at `batch_audit.py:1423`.
  - Auth: `OPENAI_API_KEY` environment variable, read at `batch_audit.py:1417`.
  - Default model: `gpt-4o-mini` (also `gpt-4o` priced in `PRICING` table at `batch_audit.py:235-240`).
  - Call site: `client.chat.completions.create(model=..., max_tokens=4096, messages=[{role: system, ...}, {role: user, content: <JSON batch>}])` at `batch_audit.py:258-265`.
  - Batch size: 40 rows per request (configurable via `--batch-size`).
  - Filtered to row_kind ITEM, entity_type ∈ {HW, BASE, UNKNOWN, ""}, with non-empty `option_name`, excluding factory-integrated rows (`batch_audit.py:307-315`).
  - Disabled when `--no-ai` flag passed (`run.ps1:118`).

- **Anthropic** — alternative provider. Selected via `--provider anthropic`.
  - SDK/Client: `anthropic` (lazy-imported at `batch_audit.py:1426`). Constructed via `anthropic.Anthropic(api_key=api_key)` at `batch_audit.py:1433`.
  - Auth: `ANTHROPIC_API_KEY` environment variable, read at `batch_audit.py:1427`.
  - Models priced: `claude-opus-4-5`, `claude-sonnet-4-5` (`batch_audit.py:238-239`).
  - Call site: `client.messages.create(model=..., max_tokens=4096, system=LLM_SYSTEM, messages=[{role: user, content: <JSON batch>}])` at `batch_audit.py:270-275`.

**Behavior on missing key / SDK:**
- Missing env var → log "⚠ OPENAI_API_KEY не найден → запуск без AI-проверки" and set `use_ai = False` (`batch_audit.py:1418-1421`). Pipeline continues with rule-based audit only.
- Missing library → `ImportError` is caught at `batch_audit.py:1435-1438`; logged and `use_ai = False`.
- Per-batch network/parse error → caught at `batch_audit.py:291-293`, logged as `⚠ LLM batch error: {e}`, batch returns `([], 0, 0)` (zero predictions, zero tokens).

**No other API integrations.** No `requests`, no `httpx`, no `urllib3`, no Stripe / Supabase / AWS / GCP / Sentry SDK imports anywhere in the codebase.

## Data Storage

**Databases:**
- None. No SQLAlchemy, no `sqlite3`, no `psycopg`, no MongoDB driver, no ORM. All persistence is the local filesystem.

**File Storage:**
- **Local filesystem only.** No S3, no Azure Blob, no GCS. No file-upload endpoints.
- Read paths: vendor `.xlsx` files under `paths.input_root` (default `%USERPROFILE%\Desktop\INPUT`).
- Write paths: per-run timestamped folders under `paths.output_root` (default `%USERPROFILE%\Desktop\OUTPUT`).

**Caching:**
- None. No Redis, no Memcached, no `functools.lru_cache` on hot paths. The pipeline is fully recomputed each run.

## File-System Integrations

The repo is **code-only by policy** (`CLAUDE.md` § "Code-only repository policy"). All large/dynamic data lives outside the repo.

**External roots (Windows defaults):**
| Role | Default path | Override |
|------|--------------|----------|
| INPUT (vendor `.xlsx` files) | `%USERPROFILE%\Desktop\INPUT` | `paths.input_root` in `spec_classifier/config.local.yaml` |
| OUTPUT (run artifacts, audit reports) | `%USERPROFILE%\Desktop\OUTPUT` | `paths.output_root` in `spec_classifier/config.local.yaml` |
| TEMP (`.pytest_cache/`, `__pycache__/`) | `C:\Users\<USERNAME>\Desktop\temporary` | `temp_root` in `config.local.yaml` |
| Virtual environment | `C:\venv` | external; not configured by code, by convention only |

**Override mechanism (`config.local.yaml` overlay):**
- Layer 1: `spec_classifier/config.yaml` — committed defaults (`input_root: "input"`, `output_root: "output"` — fallback CI paths inside the repo).
- Layer 2: `spec_classifier/config.local.yaml` — gitignored, copied from `config.local.yaml.example`. Wins over layer 1.
- Layer 3: CLI flags — `--input`, `--batch-dir`, `--output-dir` override both YAML layers (`main.py:289-304`).
- Loaded by `main.py:_load_config` (lines 69-86) with full nested-dict merge. `batch_audit.py:_load_config` and `cluster_audit.py:_load_config` use a flat `cfg.update(local_cfg)` (only paths matter there). `conftest.py:load_config` mirrors `main.py` exactly.
- The PowerShell launcher (`run.ps1:36-40`) parses `config.local.yaml` with a regex to extract `input_root` / `output_root` because PowerShell has no built-in YAML parser. The teresa_gui mirrors this regex parse at `teresa_gui.py:397-421` (`_discover_input_path`, `_discover_output_path`).

**INPUT directory layout:**
```
INPUT/
  dell/      dl1.xlsx … dl5.xlsx
  cisco/     ccw_1.xlsx, ccw_2.xlsx
  hpe/       hp1.xlsx … hp8.xlsx
  lenovo/    L1.xlsx … L11.xlsx
  huawei/    hu1.xlsx, hu2.xlsx, …
  xfusion/   …xlsx
```
Each vendor subfolder is independent; `run.ps1:94-105` skips any vendor whose subfolder is missing or contains no `.xlsx`. `conftest.py:get_input_root_<vendor>()` resolves either `<input_root>/<vendor>/` (preferred) or `<input_root>/` flat (fallback).

**OUTPUT directory layout:**
```
OUTPUT/
  dell_run/
    run-2026-05-09__14-23-01-dl1/
      classification.jsonl          ← src/outputs/json_writer.py:save_classification
      run_summary.json              ← src/diagnostics/stats_collector.py:save_run_summary
      cleaned_spec.xlsx             ← src/outputs/excel_writer.py
      dl1_annotated.xlsx            ← src/outputs/annotated_writer.py
      dl1_branded.xlsx              ← src/outputs/branded_spec_writer.py (Dell only — adapter.generates_branded_spec())
      dl1_annotated_audited.xlsx    ← batch_audit.py (after audit step)
      unknown_rows.csv              ← json_writer.save_unknown_rows
      header_rows.csv               ← json_writer.save_header_rows
      rows_raw.json                 ← json_writer.save_rows_raw
      rows_normalized.json          ← json_writer.save_rows_normalized
      run.log                       ← per-run logger handler attached in main._run_single
    run-2026-05-09__14-23-01-TOTAL/  ← batch aggregation, copies branded.xlsx / audited.xlsx from each run
  cisco_run/   …
  hpe_run/     …
  lenovo_run/  …
  huawei_run/  …
  xfusion_run/ …
  audit_report.json                  ← batch_audit.py at OUTPUT root
  audit_summary.xlsx                 ← batch_audit.py at OUTPUT root
  cluster_summary.xlsx               ← cluster_audit.py at OUTPUT root
```
Run folders are named via `src/diagnostics/run_manager.py:create_run_folder` (`run-<YYYY-MM-DD__HH-MM-SS>-<stem>`). Collisions append `_1`, `_2`, … (`run_manager.py:36-40`).

**Excel as integration surface:**
- Read: `pd.read_excel(path, header=None, engine="openpyxl", sheet_name=...)` (`annotated_writer.py:40`, `batch_audit.py:1458`). Adapters override sheet name via `VendorAdapter.get_source_sheet_name()` — Dell/Cisco use sheet 0, HPE uses `"BOM"`.
- Write: `pd.to_excel(...)` for cleaned spec, raw `openpyxl.Workbook` for branded spec (cell-level brand styling at `branded_spec_writer.py:11-35`).
- **Excel-leakage tech debt:** `batch_audit.py` reads from `*_annotated.xlsx` (Excel) instead of `classification.jsonl` (the canonical JSONL). Documented as known tech debt in `spec_classifier/CLAUDE.md` § "ИЗВЕСТНЫЙ TECH DEBT" item 1.

**Golden fixtures (regression test integration):**
- Location: `spec_classifier/golden/<stem>_expected.jsonl` (in-repo, committed). 30+ files at last freeze: `dl1..dl5`, `ccw_1..ccw_2`, `hp1..hp8`, `L1..L11`, `hu1..hu4`, etc.
- Generated by: `python main.py --save-golden --input <xlsx>` or `--update-golden` (interactive). Logic at `main.py:_save_golden` (lines 106-110) and `_build_golden_rows` (lines 89-103).
- Schema (per-row JSON): `source_row_index`, `row_kind`, `entity_type`, `state`, `matched_rule_id`, `device_type`, `hw_type`, `skus[]` (`main.py:92-102`).
- Consumed by `tests/test_regression.py`, `test_regression_cisco.py`, `test_regression_hpe.py`, etc.
- Make targets `generate_golden_dell|cisco|hpe` (`Makefile:30-65`). Lenovo/Huawei/xFusion goldens are generated via the CLI directly.

**Run-summary integration:**
- `src/diagnostics/stats_collector.py:save_run_summary` writes `run_summary.json` containing `total_rows`, `header_rows_count`, `item_rows_count`, `entity_type_counts`, `state_counts`, `unknown_count`, `rules_stats`, plus a SHA-256 hash of the rules YAML (`compute_file_hash` at `stats_collector.py:14-23`) so reruns can be tracked against rule changes.
- Consumed by humans and by `cluster_audit.py` for trend analysis.

## Authentication & Identity

**Auth Provider:**
- None. The pipeline has no users, no sessions, no tokens (other than the LLM API keys above). Filesystem ACLs are the only access control.

## Monitoring & Observability

**Error Tracking:**
- None. No Sentry, no Rollbar, no Bugsnag.

**Logs:**
- Python `logging` module, configured at `main.py:270-274` with `level=INFO` and format `"%(asctime)s [%(levelname)s] %(message)s"`.
- Per-run file handler attached to the root logger inside `main._run_single` (lines 137-140), writing to `<run_folder>/run.log`. Detached in `finally` (line 227) to avoid handler accumulation across batch runs.
- Audit and cluster scripts print directly to stdout with emoji-coded status (`🤖`, `⚠`, `❌`, `✓`).

## CI/CD & Deployment

**Hosting:**
- None. Desktop tool only.

**CI Pipeline:**
- No GitHub Actions, GitLab CI, or Jenkins config in the repo (`.github/`, `.gitlab-ci.yml`, `Jenkinsfile` all absent).
- "CI-like" guard exists locally: `conftest.py:pytest_sessionfinish` (lines 141-217) fails the pytest session if the data-availability heuristic is breached (skipped > 50%, or `paths.input_root` missing). This is the closest thing to a quality gate.

## Environment Configuration

**Required env vars:**
- `OPENAI_API_KEY` — only when running `batch_audit.py` without `--no-ai`. Persisted via `setx` from the GUI (`teresa_gui.py:198-208`); prompted via `Read-Host -AsSecureString` from `run.ps1:80-86` if missing.
- `ANTHROPIC_API_KEY` — only when `--provider anthropic`.
- `PYTHONPYCACHEPREFIX` and `PYTEST_ADDOPTS` — set by `run.ps1` and `teresa_gui.py` from `config.local.yaml::temp_root`. Together they redirect `__pycache__/` and `.pytest_cache/` to `$temp_root` so cache artifacts never land inside the repo working tree (Phase 4 CACHE-01/CACHE-02; defense-in-depth — both entry points set both vars independently).

**Secrets location:**
- Windows User-scope environment (registry, via `setx`). The repo never stores keys.
- `.env` files: not used. Not gitignored explicitly, but no code path reads them.

**No env files.** No `python-dotenv`, no `.env` loading anywhere in `spec_classifier/`. `os.environ.get("OPENAI_API_KEY")` is the only read path.

## Webhooks & Callbacks

**Incoming:**
- None. No HTTP server.

**Outgoing:**
- None. No `requests.post`, no webhook URLs, no callbacks. The only outbound traffic is the OpenAI / Anthropic API calls described above.

## Notable Absences

- No database, no ORM, no migrations.
- No web framework (FastAPI / Flask / Django absent).
- No async runtime (no `asyncio` use; the LLM calls are synchronous loops at `batch_audit.py:331-356`).
- No message broker, no scheduler, no cron config.
- No package distribution (`setup.py`, `setup.cfg`, build/dist artifacts all absent).
- No Docker, no docker-compose, no Kubernetes manifests.

---

*Integration audit: 2026-05-09*
