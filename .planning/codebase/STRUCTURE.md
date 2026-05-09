# Structure

**Analysis Date:** 2026-05-10

## Directory Layout

```
teresa/                                # repo root — Windows launcher only
├── run.ps1                           # PowerShell orchestrator (entry)
├── teresa.bat                        # double-click launcher → GUI
├── teresa_gui.py                     # PyQt6 front-end
├── README.md                         # short repo intro
├── LAUNCHER_README.md                # launcher usage notes
├── LICENSE
├── CLAUDE.md                         # repo-root project instructions
├── .gitattributes
├── .gitignore                        # ignores .venv/, OUTPUT/, output/, test_data/, .cursor/, etc.
└── spec_classifier/                  # the actual codebase
    ├── main.py                       # CLI entry — argparse + _run_single
    ├── batch_audit.py                # post-run E1–E18 + AI mismatch
    ├── cluster_audit.py              # UNKNOWN/MISMATCH clustering
    ├── conftest.py                   # pytest fixtures + skip-ratio gate
    ├── config.yaml                   # committed config (relative fallbacks)
    ├── config.local.yaml             # gitignored — absolute INPUT/OUTPUT paths
    ├── config.local.yaml.example     # template
    ├── pyproject.toml
    ├── requirements.txt
    ├── Makefile                      # generate_golden_<vendor> + test targets
    ├── README.md
    ├── CLAUDE.md                     # detailed pipeline / business-rule reference
    ├── CHANGELOG.md
    ├── CURRENT_STATE.md
    │
    ├── src/                          # actual library code
    │   ├── __init__.py
    │   ├── core/                     # vendor-agnostic primitives
    │   │   ├── __init__.py
    │   │   ├── classifier.py         # classify_row, EntityType, HW_TYPE_VOCAB
    │   │   ├── normalizer.py         # NormalizedRow, RowKind, normalize_row
    │   │   ├── state_detector.py     # State enum, detect_state
    │   │   └── parser.py             # Dell-specific (tech debt: lives in core/)
    │   ├── rules/
    │   │   ├── __init__.py
    │   │   └── rules_engine.py       # RuleSet + match_* functions
    │   ├── vendors/                  # one subdir per vendor
    │   │   ├── __init__.py
    │   │   ├── base.py               # VendorAdapter ABC
    │   │   ├── dell/                 # adapter only (uses core/parser+normalizer)
    │   │   │   ├── __init__.py
    │   │   │   └── adapter.py
    │   │   ├── cisco/                # adapter + parser + normalizer
    │   │   │   ├── __init__.py
    │   │   │   ├── adapter.py
    │   │   │   ├── parser.py
    │   │   │   └── normalizer.py
    │   │   ├── hpe/
    │   │   │   ├── __init__.py
    │   │   │   ├── adapter.py
    │   │   │   ├── parser.py
    │   │   │   └── normalizer.py
    │   │   ├── lenovo/
    │   │   │   ├── __init__.py
    │   │   │   ├── adapter.py
    │   │   │   ├── parser.py
    │   │   │   └── normalizer.py
    │   │   ├── huawei/
    │   │   │   ├── __init__.py
    │   │   │   ├── adapter.py
    │   │   │   ├── parser.py
    │   │   │   └── normalizer.py
    │   │   └── xfusion/
    │   │       ├── __init__.py
    │   │       ├── adapter.py
    │   │       ├── parser.py
    │   │       └── normalizer.py
    │   ├── outputs/                  # serializers
    │   │   ├── __init__.py
    │   │   ├── json_writer.py        # JSONL + CSV (classification, raw, normalized, unknown, header)
    │   │   ├── excel_writer.py       # cleaned_spec.xlsx
    │   │   ├── annotated_writer.py   # <stem>_annotated.xlsx
    │   │   └── branded_spec_writer.py # <stem>_branded.xlsx (per-vendor opt-in)
    │   └── diagnostics/
    │       ├── __init__.py
    │       ├── run_manager.py        # create_run_folder / TOTAL / copy_to_total
    │       └── stats_collector.py    # run_summary.json + file hash
    │
    ├── rules/                        # per-vendor YAML — single source of truth for taxonomy
    │   ├── dell_rules.yaml
    │   ├── cisco_rules.yaml
    │   ├── hpe_rules.yaml
    │   ├── lenovo_rules.yaml
    │   ├── huawei_rules.yaml
    │   └── xfusion_rules.yaml
    │
    ├── golden/                       # frozen expected outputs (regression baselines)
    │   ├── dl1_expected.jsonl … dl5_expected.jsonl
    │   ├── ccw_1_expected.jsonl, ccw_2_expected.jsonl
    │   ├── hp1_expected.jsonl … hp8_expected.jsonl
    │   ├── L1_expected.jsonl … L11_expected.jsonl
    │   ├── hu1_expected.jsonl … hu5_expected.jsonl
    │   └── xf1_expected.jsonl … xf10_expected.jsonl
    │
    ├── tests/                        # pytest suite
    │   ├── __init__.py
    │   ├── helpers.py
    │   ├── conftest.py
    │   ├── test_smoke.py
    │   ├── test_normalizer.py
    │   ├── test_state_detector.py
    │   ├── test_rules_unit.py
    │   ├── test_rules_traceability.py
    │   ├── test_schema_validation.py
    │   ├── test_cli.py
    │   ├── test_excel_writer.py
    │   ├── test_annotated_writer.py
    │   ├── test_branded_spec_writer.py
    │   ├── test_output_structure.py
    │   ├── test_dec_acceptance.py
    │   ├── test_can_parse_xfusion_huawei_disjoint.py
    │   ├── test_cluster_audit.py
    │   ├── test_unknown_threshold.py
    │   ├── test_unknown_threshold_cisco.py
    │   ├── test_unknown_threshold_hpe.py
    │   ├── test_unknown_threshold_huawei.py
    │   ├── test_unknown_threshold_xfusion.py
    │   ├── test_regression.py        # Dell
    │   ├── test_regression_cisco.py
    │   ├── test_regression_huawei.py
    │   ├── test_cisco_parser.py / test_cisco_rules_unit.py
    │   ├── test_hpe_parser.py / test_hpe_normalizer.py
    │   ├── test_lenovo_normalizer.py
    │   ├── test_huawei_parser.py / test_huawei_normalizer.py
    │   └── test_xfusion_parser.py / test_xfusion_normalizer.py
    │
    ├── docs/                         # documentation
    │   ├── DOCS_INDEX.md
    │   ├── dev/
    │   │   ├── CONTRIBUTING.md
    │   │   ├── TESTING_GUIDE.md
    │   │   ├── ONE_BUTTON_RUN.md
    │   │   ├── OPERATIONAL_NOTES.md
    │   │   └── NEW_VENDOR_GUIDE.md
    │   ├── user/
    │   │   ├── USER_GUIDE.md
    │   │   ├── CLI_CONFIG_REFERENCE.md
    │   │   └── RUN_PATHS_AND_IO_LAYOUT.md
    │   ├── product/
    │   │   └── TECHNICAL_OVERVIEW.md
    │   ├── rules/
    │   │   └── RULES_AUTHORING_GUIDE.md
    │   ├── taxonomy/
    │   │   ├── hw_type_taxonomy.md
    │   │   └── cycle2_summary.md
    │   └── schemas/
    │       └── DATA_CONTRACTS.md
    │
    ├── prompts/                      # GSD / Claude / Cursor workflow prompts
    │   ├── README.md
    │   ├── 00_VENDOR-RECON.md
    │   ├── 01_PRE-CHECK.md
    │   ├── 02_MASTER-PLAN.md
    │   ├── 03_CURSOR-IMPLEMENT.md
    │   ├── 04_POST-CHECK.md
    │   ├── 05_AUDIT-1A-1G.md
    │   ├── 06_BATCH-AUDIT-MASTER-PLAN.md
    │   ├── 07_DOC-UPDATE-MASTER-PLAN.md
    │   ├── 08_CHATGPT-SYSTEM-PROMPTS.md
    │   └── COWORK_OPUS_FULL_AUDIT.md
    │
    └── scripts/
        └── clean.ps1                 # workspace cleanup helper
```

**External (gitignored, lives outside repo):**

```
%USERPROFILE%\Desktop\
├── INPUT\                            # source XLSX files
│   ├── dell\    dl1.xlsx … dl5.xlsx
│   ├── cisco\   ccw_1.xlsx, ccw_2.xlsx
│   ├── hpe\     hp1.xlsx … hp8.xlsx
│   ├── lenovo\  L1.xlsx … L11.xlsx
│   ├── huawei\  hu1.xlsx … hu5.xlsx
│   └── xfusion\ xf1.xlsx … xf10.xlsx
└── OUTPUT\                           # all run artifacts (timestamped)
    ├── audit_report.json             # batch_audit (root-level, all vendors)
    ├── audit_summary.xlsx            # batch_audit per-vendor summary
    ├── cluster_summary.xlsx          # cluster_audit
    ├── dell_run\
    │   ├── run-2026-05-09__18-22-31-dl1\
    │   │   ├── classification.jsonl
    │   │   ├── run_summary.json
    │   │   ├── cleaned_spec.xlsx
    │   │   ├── dl1_annotated.xlsx
    │   │   ├── dl1_branded.xlsx
    │   │   ├── dl1_annotated_audited.xlsx   # batch_audit writes here
    │   │   ├── unknown_rows.csv
    │   │   ├── header_rows.csv
    │   │   ├── rows_raw.json
    │   │   ├── rows_normalized.json
    │   │   └── run.log
    │   ├── run-2026-05-09__18-22-31-dl2\ …
    │   └── run-2026-05-09__18-22-31-TOTAL\  # batch aggregation copies
    ├── cisco_run\ …
    ├── hpe_run\ …
    ├── lenovo_run\ …
    ├── huawei_run\ …
    └── xfusion_run\ …

C:\venv\                              # virtualenv (default; override in config.local.yaml)
```

## Directory Purposes

**`teresa/` (repo root):**
- Purpose: Windows launcher layer. No Python package here.
- Contains: `run.ps1`, `teresa.bat`, `teresa_gui.py`, `README.md`, `LAUNCHER_README.md`, `LICENSE`, `CLAUDE.md`, `.gitattributes`, `.gitignore`.
- Key files: `run.ps1` (orchestrator), `teresa_gui.py` (GUI), `teresa.bat` (double-click).

**`spec_classifier/`:**
- Purpose: The actual deterministic, rule-based Excel-spec classifier. Treat as a flat Python project (no installable package — runs from cwd via `python main.py …`).
- Contains: CLI (`main.py`), audits (`batch_audit.py`, `cluster_audit.py`), config (`config.yaml`, `config.local.yaml`), source tree (`src/`), rules (`rules/`), test suite (`tests/`), goldens (`golden/`), docs (`docs/`), workflow prompts (`prompts/`), helpers (`scripts/`), `Makefile`, `pyproject.toml`, `requirements.txt`, `conftest.py`, `CLAUDE.md`, `CHANGELOG.md`, `CURRENT_STATE.md`.

**`spec_classifier/src/core/`:**
- Purpose: Vendor-agnostic primitives.
- Contains: `classifier.py`, `normalizer.py`, `state_detector.py`, `parser.py` (Dell-specific despite location — tech debt).
- Key files: `spec_classifier/src/core/classifier.py` (`classify_row`, `EntityType`, `HW_TYPE_VOCAB`), `spec_classifier/src/core/normalizer.py` (`NormalizedRow`, `RowKind`).

**`spec_classifier/src/rules/`:**
- Purpose: YAML rule loading + regex match primitives.
- Key file: `spec_classifier/src/rules/rules_engine.py` (`RuleSet`, `match_rule`, `match_device_type_rule`, `match_hw_type_rule`).

**`spec_classifier/src/vendors/`:**
- Purpose: One subdir per supported vendor. Each subdir has at least `adapter.py`, plus `parser.py` and `normalizer.py` for everyone except Dell.
- Key file: `spec_classifier/src/vendors/base.py` (`VendorAdapter` ABC — *required reading before adding a vendor*).

**`spec_classifier/src/outputs/`:**
- Purpose: Serializers. Every artifact written under `OUTPUT/.../run-…/` originates here.
- Key files: `json_writer.py`, `excel_writer.py`, `annotated_writer.py`, `branded_spec_writer.py`.

**`spec_classifier/src/diagnostics/`:**
- Purpose: Run lifecycle and stats.
- Key files: `run_manager.py` (folder creation + TOTAL copies), `stats_collector.py` (`run_summary.json`, file hash).

**`spec_classifier/rules/`:**
- Purpose: Per-vendor YAML — single source of truth for taxonomy. Includes `state_rules`, `base_rules`, `service_rules`, `logistic_rules`, `software_rules`, `note_rules`, `config_rules`, `hw_rules`, `device_type_rules` (with `applies_to`), `hw_type_rules` (with `device_type_map`, `rule_id_map`, `applies_to`).
- One file per vendor: `dell_rules.yaml`, `cisco_rules.yaml`, `hpe_rules.yaml`, `lenovo_rules.yaml`, `huawei_rules.yaml`, `xfusion_rules.yaml`.

**`spec_classifier/golden/`:**
- Purpose: Frozen expected output JSONL files used by `tests/test_regression*.py`. Generated via `python main.py --save-golden --input <xlsx> --vendor <v>` or `--update-golden`. One file per fixture stem: `<stem>_expected.jsonl`.
- Stems present (40 total): `dl1..dl5`, `ccw_1..ccw_2`, `hp1..hp8`, `L1..L11`, `hu1..hu5`, `xf1..xf10`.

**`spec_classifier/tests/`:**
- Purpose: pytest suite (~420+ tests collected). Contains unit tests, parser/normalizer tests per vendor, regression tests (golden-based), unknown-threshold tests, schema/traceability checks, smoke, CLI test, output-structure test, cluster-audit test, factory-discriminator test (`test_can_parse_xfusion_huawei_disjoint.py`).
- Helpers: `helpers.py`, local `conftest.py`.

**`spec_classifier/docs/`:**
- Purpose: All long-form documentation. Subdirs by audience: `dev/` (contributing, testing, ops, vendor onboarding), `user/` (CLI/config, run paths, user guide), `product/` (technical overview), `rules/` (rule authoring guide), `taxonomy/` (hw_type taxonomy + cycle 2 summary), `schemas/` (data contracts).
- Index: `spec_classifier/docs/DOCS_INDEX.md`.

**`spec_classifier/prompts/`:**
- Purpose: GSD / Cursor / Claude workflow prompt templates. Numbered by step in the development cycle (PRE-CHECK → PLAN → IMPLEMENT → POST-CHECK → AUDIT 1A–1G → DOC UPDATE).
- Index: `spec_classifier/prompts/README.md`.
- Critical: `prompts/00_VENDOR-RECON.md` is the recipe for adding a new vendor.

**`spec_classifier/scripts/`:**
- Purpose: Operational helpers. Currently only `clean.ps1`.

## Key File Locations

**Entry Points:**
- `run.ps1` — PowerShell orchestrator (single-button entry).
- `teresa.bat` — Windows double-click launcher.
- `teresa_gui.py` — PyQt6 GUI front-end.
- `spec_classifier/main.py` — Python CLI entry; argparse + `_run_single` per file.
- `spec_classifier/batch_audit.py` — post-run audit CLI.
- `spec_classifier/cluster_audit.py` — pattern-mining CLI.

**Configuration:**
- `spec_classifier/config.yaml` — committed defaults.
- `spec_classifier/config.local.yaml` — gitignored, absolute paths (copy from `.example`).
- `spec_classifier/config.local.yaml.example` — template.
- `spec_classifier/pyproject.toml` — Python project metadata.
- `spec_classifier/requirements.txt` — Python dependencies.
- `spec_classifier/Makefile` — golden-generation + test targets.
- `spec_classifier/conftest.py` — pytest skip-ratio gate.
- `.gitignore` (root) — excludes `.venv/`, `OUTPUT/`, `output/`, `test_data/`, `commits.txt`, `*.zip`, `.cursor/`.

**Core Logic:**
- `spec_classifier/src/vendors/base.py` — `VendorAdapter` ABC.
- `spec_classifier/src/core/classifier.py` — `classify_row`, `EntityType`, `HW_TYPE_VOCAB`.
- `spec_classifier/src/core/normalizer.py` — `NormalizedRow`, `RowKind`.
- `spec_classifier/src/core/state_detector.py` — `State`, `detect_state`.
- `spec_classifier/src/rules/rules_engine.py` — `RuleSet`, `match_*` functions.
- `spec_classifier/main.py` (lines 42–49) — `VENDOR_REGISTRY`.

**Outputs:**
- `spec_classifier/src/outputs/json_writer.py`
- `spec_classifier/src/outputs/excel_writer.py`
- `spec_classifier/src/outputs/annotated_writer.py`
- `spec_classifier/src/outputs/branded_spec_writer.py`
- `spec_classifier/src/diagnostics/run_manager.py`
- `spec_classifier/src/diagnostics/stats_collector.py`

**Rules (data):**
- `spec_classifier/rules/dell_rules.yaml`
- `spec_classifier/rules/cisco_rules.yaml`
- `spec_classifier/rules/hpe_rules.yaml`
- `spec_classifier/rules/lenovo_rules.yaml`
- `spec_classifier/rules/huawei_rules.yaml`
- `spec_classifier/rules/xfusion_rules.yaml`

**Testing:**
- `spec_classifier/tests/` — full pytest suite.
- `spec_classifier/golden/` — frozen regression expectations.
- `spec_classifier/conftest.py` — fixtures + skip-ratio gate (`pytest_sessionfinish` fails session if `skipped/total > 0.50` or `passed == 0`).

## Naming Conventions

**Files:**
- Python source: `snake_case.py` (e.g. `rules_engine.py`, `state_detector.py`, `branded_spec_writer.py`).
- Tests: `test_<unit>.py` or `test_<vendor>_<unit>.py` (e.g. `test_normalizer.py`, `test_hpe_parser.py`, `test_unknown_threshold_xfusion.py`).
- Vendor adapters: every vendor has `adapter.py` inside `src/vendors/<vendor>/`. Class name is `<Vendor>Adapter` PascalCase (`DellAdapter`, `CiscoAdapter`, `HPEAdapter`, `LenovoAdapter`, `HuaweiAdapter`, `XFusionAdapter`).
- Rule files: `<vendor>_rules.yaml` (lowercase vendor key, matches `VENDOR_REGISTRY` keys exactly).
- Golden files: `<input_stem>_expected.jsonl` (one per fixture).

**Directories:**
- Vendor subdirs: lowercase, single word (`dell`, `cisco`, `hpe`, `lenovo`, `huawei`, `xfusion`). The vendor key is the same string used by `--vendor` CLI flag, the YAML rule filename prefix, and `VENDOR_REGISTRY` dict keys.
- Documentation subdirs: lowercase, audience-based (`dev/`, `user/`, `product/`, `rules/`, `taxonomy/`, `schemas/`).

**Output run folders (`run_manager.py` lines 19–41):**
- Per-run: `run-YYYY-MM-DD__HH-MM-SS-<input_stem>` (note: **double underscore** between date and time).
- Batch TOTAL: `run-YYYY-MM-DD__HH-MM-SS-TOTAL` (`run_manager.py:44`).
- Collision suffix: if folder already exists in same second, append `_1`, `_2`, …
- Vendor base dir: `<OUTPUT>/<vendor>_run/` (e.g. `OUTPUT/dell_run/`).

**Artifact filenames inside a run folder:**
- Always present: `classification.jsonl`, `run_summary.json`, `cleaned_spec.xlsx`, `<stem>_annotated.xlsx`, `unknown_rows.csv`, `header_rows.csv`, `rows_raw.json`, `rows_normalized.json`, `run.log`.
- Vendor-gated: `<stem>_branded.xlsx` (only when `adapter.generates_branded_spec()`).
- Audit-injected: `<stem>_annotated_audited.xlsx` (`batch_audit.py` writes this *into the run folder*, not at OUTPUT root).

**OUTPUT-root artifacts (one per OUTPUT/, not per run):**
- `audit_report.json` — `batch_audit.py`.
- `audit_summary.xlsx` — `batch_audit.py`.
- `cluster_summary.xlsx` — `cluster_audit.py`.

**Rule IDs (in YAML):**
- Pattern: `<ENTITY>-<NUM>` or `<ENTITY>-<TAG>-<NUM>` (e.g. `BASE-001`, `BASE-002`, `HW-010-POWER-CORD`, `LOGISTIC-005-SFP-CABLE`, `STATE-001`, `BASE-D-DT-001` for device-type variants).
- `UNKNOWN-000` — reserved sentinel for unmatched rows.
- `HEADER-SKIP` — reserved sentinel for HEADER `RowKind` rows.

## Where to Add New Code

**New vendor (full recipe in `spec_classifier/prompts/00_VENDOR-RECON.md` and `spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md`):**
1. Create directory: `spec_classifier/src/vendors/<vendor>/`.
2. Add `adapter.py` (subclass `VendorAdapter` from `spec_classifier/src/vendors/base.py`), `parser.py`, `normalizer.py`, `__init__.py`.
3. Implement abstract methods: `can_parse`, `parse`, `normalize`, `get_rules_file`, `get_vendor_stats`, `generates_branded_spec`. Override `get_source_sheet_name` and `get_extra_cols` if needed.
4. Add YAML: `spec_classifier/rules/<vendor>_rules.yaml`.
5. Register: append `"<vendor>": <Vendor>Adapter` to `VENDOR_REGISTRY` in `spec_classifier/main.py` (lines 42–49) and add the import.
6. Wire launcher: append `"<vendor>"` to `$ALL_VENDORS` in `run.ps1` line 45.
7. Wire GUI: append `"<vendor>"` to `VENDORS_ACTIVE` in `teresa_gui.py:38` and add a label entry in `_build_left_column` (line 272).
8. Add config entry: append `<vendor>: "rules/<vendor>_rules.yaml"` under `vendor_rules:` in `spec_classifier/config.yaml`.
9. Add tests: `spec_classifier/tests/test_<vendor>_parser.py`, `test_<vendor>_normalizer.py`, regression + unknown-threshold tests.
10. Generate golden: `python main.py --save-golden --input <xlsx> --vendor <vendor>`.

**New rule (existing vendor):**
- Edit `spec_classifier/rules/<vendor>_rules.yaml` directly. Order matters — first match wins. Document the change in `spec_classifier/CHANGELOG.md`.
- After editing, re-run pipeline + audits and verify E2 / E17 reduction; do not skip `batch_audit.py`.

**New entity / device type:**
- Add rule entry under correct list in YAML.
- If introducing a new `hw_type` bucket: update `HW_TYPE_VOCAB` in **both** `spec_classifier/src/core/classifier.py:28` **and** `spec_classifier/batch_audit.py:44` (must stay in sync). Also update `spec_classifier/docs/taxonomy/hw_type_taxonomy.md`.
- If introducing a new `device_type`: ensure mapping exists in the vendor's `device_type_map` inside `hw_type_rules:` of the YAML (or document why it intentionally has no `hw_type`, like `power_cord`).

**New output artifact:**
- Add module to `spec_classifier/src/outputs/`.
- Wire into `_run_single()` in `spec_classifier/main.py` after `save_classification` (lines 159–189).
- If vendor-gated, follow `generates_branded_spec()` pattern: add an abstract or default method to `VendorAdapter` (`spec_classifier/src/vendors/base.py`) and gate the call in `_run_single`.
- If it should aggregate to TOTAL in batch mode, extend `copy_to_total` (`spec_classifier/src/diagnostics/run_manager.py:55`).

**New audit check (E-code):**
- Edit `spec_classifier/batch_audit.py`. The E-code table (E1–E18) is documented in `spec_classifier/CLAUDE.md` § "E-КОДЫ batch_audit.py" — keep that table in sync.

**New test:**
- Add file to `spec_classifier/tests/` matching pattern `test_<unit>.py` or `test_<vendor>_<unit>.py`.
- Use existing helpers in `spec_classifier/tests/helpers.py` and fixtures in `spec_classifier/conftest.py`.
- For regression tests, add a golden file to `spec_classifier/golden/<stem>_expected.jsonl` (generated via `--save-golden`).

**New CLI flag:**
- For pipeline: `spec_classifier/main.py:main` (argparse around line 244).
- For audits: `spec_classifier/batch_audit.py` or `spec_classifier/cluster_audit.py`.
- For launcher orchestration: add `[switch]$NewFlag` to `run.ps1` `param()` block (lines 14–19).

**New config key:**
- Edit both `spec_classifier/config.yaml` (committed defaults) and document the override path in `spec_classifier/config.local.yaml.example`.
- Read it via `paths_cfg = config.get("paths") or {}` pattern in `spec_classifier/main.py` (line 289).

**Helpers / utilities:**
- Vendor-agnostic: `spec_classifier/src/core/`.
- Vendor-specific: `spec_classifier/src/vendors/<vendor>/` (do NOT add to `core/`).

## Special Directories

**`spec_classifier/golden/`:**
- Purpose: Regression baselines.
- Generated: Yes — by `python main.py --save-golden --input <xlsx> --vendor <v>` or via `make generate_golden_<vendor>`.
- Committed: Yes (these are the test ground truth).
- Update path: `--update-golden` (interactive y/N prompt) or rerun `make generate_golden_<vendor>`.

**`spec_classifier/rules/`:**
- Purpose: Vendor classification rules.
- Generated: No — hand-authored.
- Committed: Yes (single source of truth for taxonomy mapping).
- Authoring guide: `spec_classifier/docs/rules/RULES_AUTHORING_GUIDE.md`.

**`spec_classifier/.venv/` (if present):**
- Purpose: Local Python venv. Not used — repo uses `C:\venv\` by default (override in `config.local.yaml`).
- Generated: Yes (by user).
- Committed: No (gitignored).

**`OUTPUT\` (external, `%USERPROFILE%\Desktop\OUTPUT`):**
- Purpose: All run artifacts. Lives outside the repo per code-only policy.
- Generated: Yes (by `main.py`, `batch_audit.py`, `cluster_audit.py`).
- Committed: No (gitignored at every name: `OUTPUT/`, `output/`).

**`INPUT\` (external, `%USERPROFILE%\Desktop\INPUT`):**
- Purpose: Vendor source XLSX files. Subdirs per vendor (e.g. `INPUT\dell\dl1.xlsx`).
- Generated: No (curated by user).
- Committed: No (lives outside the repo).

**`temp\` (external, `%USERPROFILE%\Desktop\temporary`):**
- Purpose: Diagnostics, logs, scratch. Documented in `spec_classifier/CLAUDE.md` § "ПУТИ".
- Committed: No.

**`.cursor/` / `.claude/` / `.agents/` (root):**
- Purpose: Tool-specific workflow assets (Cursor GSD, Claude Code skills). Do not assume presence; check before reading.
- Committed: No (gitignored at root `.gitignore` line for `.cursor/`).

**`spec_classifier/prompts/`:**
- Purpose: Numbered workflow prompts (`00_VENDOR-RECON.md` through `08_CHATGPT-SYSTEM-PROMPTS.md` plus `COWORK_OPUS_FULL_AUDIT.md`).
- Committed: Yes.
- Used by: humans and tools running the GSD development cycle (PRE-CHECK → PLAN → IMPLEMENT → POST-CHECK → AUDIT).

*Structure map: 2026-05-10*
