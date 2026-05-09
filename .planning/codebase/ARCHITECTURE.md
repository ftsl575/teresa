# Architecture

**Analysis Date:** 2026-05-10
**Scope:** Full repo (`C:\Users\G\Desktop\teresa`) — both root launcher layer and `spec_classifier/`.

## System Overview

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                  ENTRY LAYER (Windows launcher / CLI / GUI)                  │
├────────────────────────┬─────────────────────────┬───────────────────────────┤
│      run.ps1           │   spec_classifier/      │     teresa_gui.py         │
│   (orchestrator)       │     main.py (CLI)       │   (PyQt6 front-end)       │
│   `run.ps1`            │   `spec_classifier/     │   `teresa_gui.py`         │
│                        │      main.py`           │                           │
└──────────┬─────────────┴────────────┬────────────┴───────────┬───────────────┘
           │                          │                         │
           │ shells out to ──────────►│◄──── shells out via PowerShell ────────│
           ▼                          ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                       PIPELINE LAYER (per file, per vendor)                  │
│   _run_single() in `spec_classifier/main.py`                                 │
│   ① Adapter dispatch  ──►  VENDOR_REGISTRY                                   │
│   ② Parse             ──►  adapter.parse(path) -> (raw_rows, header_idx)     │
│   ③ Normalize         ──►  adapter.normalize(raw_rows) -> [NormalizedRow]    │
│   ④ Classify          ──►  classify_row(row, ruleset) -> ClassificationResult│
│   ⑤ Write artifacts   ──►  json/excel/annotated/branded writers              │
│   ⑥ TOTAL aggregation ──►  copy_to_total() (batch mode only)                 │
└──────────┬─────────────────────────┬──────────────────────┬──────────────────┘
           ▼                         ▼                       ▼
┌──────────────────────┐  ┌──────────────────────┐  ┌─────────────────────────┐
│  VENDOR ADAPTERS     │  │   RULES ENGINE       │  │      OUTPUTS            │
│  src/vendors/<v>/    │  │   src/rules/         │  │   src/outputs/          │
│  base.py (ABC)       │  │   rules_engine.py    │  │   json_writer.py        │
│  dell/adapter.py     │  │   loads YAML rules   │  │   excel_writer.py       │
│  cisco/adapter.py    │  │   from rules/<v>.yml │  │   annotated_writer.py   │
│  hpe/adapter.py      │  │   first-match-wins   │  │   branded_spec_writer.py│
│  lenovo/adapter.py   │  │                      │  │                         │
│  huawei/adapter.py   │  │   classifier.py      │  │   diagnostics/          │
│  xfusion/adapter.py  │  │   in src/core/       │  │   run_manager.py        │
└──────────┬───────────┘  └──────────┬───────────┘  └────────────┬────────────┘
           └────────────┬────────────┴────────────┬───────────────┘
                        ▼                         ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  ARTIFACT STORE (external — outside repo, code-only policy)                  │
│  OUTPUT/<vendor>_run/run-YYYY-MM-DD__HH-MM-SS-<stem>/                        │
│    classification.jsonl, run_summary.json, cleaned_spec.xlsx,                │
│    <stem>_annotated.xlsx, <stem>_branded.xlsx,                               │
│    rows_raw.json, rows_normalized.json, unknown_rows.csv,                    │
│    header_rows.csv, run.log                                                  │
│  OUTPUT/<vendor>_run/run-…-TOTAL/   (batch aggregation)                      │
└──────────────────────────────────────────────────────────────────────────────┘
                        ▲                         ▲
                        │ reads *_annotated.xlsx  │ reads *_audited.xlsx
┌──────────────────────────────────┐  ┌────────────────────────────────────────┐
│  POST-RUN AUDIT                  │  │  PATTERN MINING                        │
│  `spec_classifier/batch_audit.py`│  │  `spec_classifier/cluster_audit.py`    │
│  E1–E18 + optional gpt-4o-mini   │  │  TF-IDF + HDBSCAN/KMeans               │
│  Writes audit_report.json,       │  │  Writes cluster_summary.xlsx,          │
│  audit_summary.xlsx, *_audited   │  │  appends `clusters` to audit_report    │
└──────────────────────────────────┘  └────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| `run.ps1` orchestrator | Loop vendors → run pipeline → audits → pytest | `run.ps1` |
| `teresa_gui.py` | PyQt6 front-end; spawns `run.ps1` in a new console | `teresa_gui.py` |
| `teresa.bat` | Double-click launcher; checks Python+PyQt6, starts GUI | `teresa.bat` |
| CLI / pipeline driver | Argparse + `_run_single()`; batch + golden modes | `spec_classifier/main.py` |
| `VENDOR_REGISTRY` | Map `--vendor` → adapter class | `spec_classifier/main.py` lines 42–49 |
| Vendor adapter contract | ABC: `parse / normalize / can_parse / get_rules_file / get_vendor_stats / generates_branded_spec / get_source_sheet_name / get_extra_cols` | `spec_classifier/src/vendors/base.py` |
| Vendor adapters | Per-vendor dispatch | `spec_classifier/src/vendors/{dell,cisco,hpe,lenovo,huawei,xfusion}/adapter.py` |
| Vendor parsers | Locate header row + read XLSX into raw row dicts | `spec_classifier/src/vendors/<v>/parser.py` (Dell uses `src/core/parser.py` — tech debt) |
| Vendor normalizers | Raw cells → `NormalizedRow` with `row_kind` + extra fields | `spec_classifier/src/vendors/<v>/normalizer.py` (Dell uses `src/core/normalizer.py`) |
| Rules loader | Load YAML into `RuleSet` | `spec_classifier/src/rules/rules_engine.py` |
| Classifier | First-match-wins over `RuleSet` | `spec_classifier/src/core/classifier.py` |
| State detector | `PRESENT / ABSENT / DISABLED` | `spec_classifier/src/core/state_detector.py` |
| JSON / CSV writer | `classification.jsonl`, `rows_raw.json`, `rows_normalized.json`, `unknown_rows.csv`, `header_rows.csv` | `spec_classifier/src/outputs/json_writer.py` |
| Cleaned-spec writer | Filtered Excel (BASE/HW/SOFTWARE/SERVICE, PRESENT only) | `spec_classifier/src/outputs/excel_writer.py` |
| Annotated writer | Original sheet + classification columns | `spec_classifier/src/outputs/annotated_writer.py` |
| Branded-spec writer | Customer-facing branded XLSX (per-vendor opt-in) | `spec_classifier/src/outputs/branded_spec_writer.py` |
| Run / TOTAL folder mgmt | Timestamped run dirs + batch aggregation copies | `spec_classifier/src/diagnostics/run_manager.py` |
| Run-summary stats | Aggregated counts + file hash for `run_summary.json` | `spec_classifier/src/diagnostics/stats_collector.py` |
| Post-run audit | E1–E18 + optional AI mismatch | `spec_classifier/batch_audit.py` |
| Cluster audit | Mine UNKNOWN / mismatch rows for new rules | `spec_classifier/cluster_audit.py` |
| Config loader | `config.yaml` overlaid by `config.local.yaml` | `spec_classifier/main.py:_load_config`, `spec_classifier/conftest.py:load_config` |
| Test fixtures / gates | Skip-ratio gating, INPUT root resolution | `spec_classifier/conftest.py` |

## Pattern Overview

**Overall:** Pluggable per-vendor adapter pipeline driven by a strict 5-stage contract — **parse → normalize → classify → write artifacts → optional aggregate**. Classification is a deterministic regex-on-field rules engine (no ML). Per-vendor knowledge lives entirely in `rules/<vendor>_rules.yaml` + `src/vendors/<v>/`.

**Key Characteristics:**
- **Adapter / Strategy** for vendor differences (`VendorAdapter` ABC + `VENDOR_REGISTRY` dict).
- **Pipeline / Pipes-and-Filters** with stable in-memory contracts (`NormalizedRow`, `ClassificationResult`).
- **Data-driven classification:** code is generic; rules + taxonomy maps live in YAML.
- **First-match-wins** rule evaluation — YAML order is business logic.
- **Code-only repo:** INPUT/OUTPUT live outside the repo (`%USERPROFILE%\Desktop\INPUT|OUTPUT`); `config.local.yaml` injects absolute paths.
- **Audits are out-of-band** — `batch_audit.py` reads `*_annotated.xlsx`, not `classification.jsonl` (known tech debt).

## Layers

**Entry layer:**
- Purpose: Take user input (CLI / GUI / batch defaults) and drive the pipeline once per `(vendor, file)`.
- Location: `run.ps1`, `teresa_gui.py`, `teresa.bat`, `spec_classifier/main.py`.
- Contains: argparse, vendor registry, config loading, run-folder creation.
- Depends on: vendor adapter layer, rules engine, outputs, diagnostics.
- Used by: end users; CI; `run.ps1`.

**Vendor adapter layer:**
- Purpose: Encapsulate vendor-specifics (sheet name, header sentinel, raw → `NormalizedRow`, extra columns, vendor stats).
- Location: `spec_classifier/src/vendors/`.
- Contains: `base.py` (ABC) + one subdir per vendor with `adapter.py`, `parser.py`, `normalizer.py`.
- Depends on: `openpyxl`, `pandas`, `src/core/normalizer.py`.
- Used by: `spec_classifier/main.py:_get_adapter`.

**Core layer:**
- Purpose: Vendor-agnostic primitives.
- Location: `spec_classifier/src/core/`.
- Contains: `normalizer.py` (`NormalizedRow`, `RowKind`, `detect_row_kind`, `normalize_row`), `classifier.py` (`EntityType`, `ClassificationResult`, `classify_row`, `_apply_device_type`, `_apply_hw_type`, `HW_TYPE_VOCAB`), `state_detector.py` (`State`, `detect_state`), `parser.py` (Dell-only — see Anti-Patterns).
- Depends on: `src/rules/rules_engine.py`.

**Rules layer:**
- Purpose: Load YAML; provide regex match primitives.
- Location: `spec_classifier/src/rules/rules_engine.py` + `spec_classifier/rules/<vendor>_rules.yaml`.
- Contains: `RuleSet`, `match_rule`, `match_device_type_rule`, `match_hw_type_rule`, `_get_field_value`.
- Depends on: `pyyaml`, `re`, `NormalizedRow`.

**Outputs layer:**
- Purpose: Serialize results to JSONL, CSV, multiple XLSX flavors.
- Location: `spec_classifier/src/outputs/`.
- Contains: `json_writer.py`, `excel_writer.py`, `annotated_writer.py`, `branded_spec_writer.py`.

**Diagnostics layer:**
- Purpose: Run-folder lifecycle + stats aggregation.
- Location: `spec_classifier/src/diagnostics/`.
- Contains: `run_manager.py` (folder + TOTAL copies), `stats_collector.py` (`run_summary.json`, file hash).

**Audit layer (out-of-band):**
- Purpose: Post-hoc validation; pattern mining for new rules.
- Location: `spec_classifier/batch_audit.py`, `spec_classifier/cluster_audit.py`.
- Contains: E1–E18 rule checks, optional OpenAI client, TF-IDF clustering.
- Depends on: `pd.read_excel(*_annotated.xlsx)` (Excel-leakage tech debt), `openai` (optional).

## Data Flow

### Primary Pipeline Path (single file)

1. **Entry:** `.\run.ps1` or `python spec_classifier/main.py --input <xlsx> --vendor <v>` (`run.ps1` lines 92–113; `spec_classifier/main.py:main` line 243).
2. **Config load:** `_load_config` reads `config.yaml` then overlays `config.local.yaml` (`spec_classifier/main.py` lines 69–86).
3. **Adapter dispatch:** `_get_adapter(vendor, config)` → `VENDOR_REGISTRY[vendor](config)` (`spec_classifier/main.py` lines 42–56).
4. **Run folder:** `create_run_folder(...)` makes `OUTPUT/<vendor>_run/run-YYYY-MM-DD__HH-MM-SS-<stem>/`; attaches a `run.log` `FileHandler` to the root logger (`spec_classifier/main.py` lines 134–140; `src/diagnostics/run_manager.py:19`).
5. **Parse:** `adapter.parse(path)` returns `(raw_rows: list[dict], header_row_index: int)` (`spec_classifier/main.py:143`). Each raw dict carries `__row_index__` (1-based Excel row).
6. **Normalize:** `adapter.normalize(raw_rows)` returns `[NormalizedRow]` with `row_kind ∈ {HEADER, ITEM}` (`spec_classifier/main.py:145`).
7. **Rules load:** `RuleSet.load(rules_path)` reads `rules/<vendor>_rules.yaml`, indexes `base_rules / service_rules / logistic_rules / software_rules / note_rules / config_rules / hw_rules / device_type_rules / hw_type_rules / state_rules` (`spec_classifier/src/rules/rules_engine.py:152`).
8. **Classify:** `classify_row(r, ruleset)` per row in priority order BASE → SERVICE → LOGISTIC → SOFTWARE → NOTE → CONFIG → HW → UNKNOWN; for matched ITEM rows, second pass sets `device_type`, third pass resolves `hw_type` via (a) `device_type_map`, (b) `rule_id_map`, (c) regex rules (`spec_classifier/src/core/classifier.py:67`, `_apply_device_type:170`, `_apply_hw_type:194`).
9. **Write artifacts:** `save_rows_raw`, `save_rows_normalized`, `save_classification`, `save_unknown_rows`, `save_header_rows`, `collect_stats` + `save_run_summary`, `generate_cleaned_spec`, `generate_annotated_source_excel`, then `generate_branded_spec` if `adapter.generates_branded_spec()` (`spec_classifier/main.py:159–189`).
10. **Batch TOTAL:** if `--batch-dir`, `copy_to_total(run_folder, total_folder, stem)` copies `cleaned_spec.xlsx`, `<stem>_annotated.xlsx`, `<stem>_branded.xlsx` into `OUTPUT/<vendor>_run/run-<stamp>-TOTAL/` (`spec_classifier/main.py:192–194`; `src/diagnostics/run_manager.py:55`).
11. **Post-run audit:** `batch_audit.py` walks `OUTPUT/`, reads each `*_annotated.xlsx` with `pd.read_excel`, runs E1–E18 + optional AI mismatch, writes `audit_report.json`, `audit_summary.xlsx`, `*_audited.xlsx`.
12. **Cluster audit:** `cluster_audit.py` reads `*_audited.xlsx`, TF-IDF + HDBSCAN/KMeans on UNKNOWN / HW-without-device_type rows; writes `cluster_summary.xlsx` and appends `clusters` to `audit_report.json`.
13. **Tests:** `run.ps1` finishes by invoking `python -m pytest tests/ -v --tb=short` from `spec_classifier/`.

### Batch Flow

`spec_classifier/main.py:main` lines 297–359: enumerate `*.xlsx` in `--batch-dir`, create one shared `session_stamp` and one `TOTAL` folder, then call `_run_single` per file, gating each with `adapter.can_parse(path)` (skip if False, fail if it raises). Aggregate `processed / skipped / failed` counts; non-zero exit only if any file failed.

### Rules Engine Internals

```python
# spec_classifier/src/core/classifier.py:67
def classify_row(row, ruleset):
    if row.row_kind == RowKind.HEADER:
        return ClassificationResult(row_kind=HEADER, ..., matched_rule_id="HEADER-SKIP")
    state = detect_state(row.option_name, ruleset.get_state_rules())
    # Priority order — first match wins:
    for entity, rules in [
        (BASE,     ruleset.base_rules),
        (SERVICE,  ruleset.service_rules),
        (LOGISTIC, ruleset.logistic_rules),
        (SOFTWARE, ruleset.software_rules),
        (NOTE,     ruleset.note_rules),
        (CONFIG,   ruleset.config_rules),
        (HW,       ruleset.hw_rules),
    ]:
        match = match_rule(row, rules)        # regex on field, IGNORECASE
        if match:
            result = ClassificationResult(entity, state, match["rule_id"])
            result = _apply_device_type(row, result, ruleset)  # 2nd pass
            return _apply_hw_type(row, result, ruleset)        # 3rd pass
    # Fallthrough → UNKNOWN-000 (warning emitted; flagged as E2 in batch_audit)
```

`hw_type` resolution priority (`_apply_hw_type` lines 194–225):
1. `ruleset.hw_type_device_type_map[result.device_type]` — per-vendor `device_type_map` in YAML.
2. `ruleset.hw_type_rule_id_map[result.matched_rule_id]` — per-vendor `rule_id_map`.
3. `match_hw_type_rule(row, ruleset.hw_type_rules)` — regex fallback.
4. Else → unresolved warning.

**State Management:** No long-lived state. Pipeline is per-file, top-down: `_run_single` constructs everything fresh and returns 0/1. `OPENAI_API_KEY` is process-env. Logging is configured globally; per-run `FileHandler` attached/detached via `try/finally` so each `run.log` captures only its own run.

## Key Abstractions

**`VendorAdapter`** (ABC):
- Purpose: Single contract every vendor must satisfy.
- Examples: `spec_classifier/src/vendors/dell/adapter.py:DellAdapter`, `…/cisco/adapter.py:CiscoAdapter`, `…/hpe/adapter.py:HPEAdapter`, `…/lenovo/adapter.py:LenovoAdapter`, `…/huawei/adapter.py:HuaweiAdapter`, `…/xfusion/adapter.py:XFusionAdapter`.
- Pattern: Strategy + Template Method (default `get_source_sheet_name() -> None`, `get_extra_cols() -> []`; rest abstract).
- Signature (`spec_classifier/src/vendors/base.py`):

```python
class VendorAdapter(ABC):
    @abstractmethod
    def can_parse(self, path: str) -> bool: ...
    @abstractmethod
    def parse(self, filepath: str) -> Tuple[List[dict], int]: ...
    @abstractmethod
    def normalize(self, raw_rows: List[dict]) -> list: ...
    @abstractmethod
    def get_rules_file(self) -> str: ...
    @abstractmethod
    def get_vendor_stats(self, normalized_rows: list) -> dict: ...
    @abstractmethod
    def generates_branded_spec(self) -> bool: ...
    def get_source_sheet_name(self) -> str | None:  return None
    def get_extra_cols(self) -> list[tuple[str, str]]:  return []
```

**`VENDOR_REGISTRY`** (dict, single source of truth):

```python
# spec_classifier/main.py lines 42–49
VENDOR_REGISTRY: dict[str, type] = {
    "dell":    DellAdapter,
    "cisco":   CiscoAdapter,
    "hpe":     HPEAdapter,
    "lenovo":  LenovoAdapter,
    "huawei":  HuaweiAdapter,
    "xfusion": XFusionAdapter,
}
```

**`NormalizedRow`** (dataclass, `spec_classifier/src/core/normalizer.py:36`):
- Required fields: `source_row_index, row_kind, group_name, group_id, product_name, module_name, option_name, option_id, skus (list[str]), qty, option_price`.
- Vendor extensions added by per-vendor normalizers; surfaced to Excel via `adapter.get_extra_cols()`:
  - HPE: `is_factory_integrated, config_name, product_type, extended_price, lead_time` (5 cols).
  - Cisco: `line_number, service_duration_months` + internal `is_bundle_root` (2 cols).
  - Lenovo: `export_control` (1 col).
  - Huawei: `position_no, unit_qty, total_price, lead_time_days, eom, eos` (6 cols).
  - xFusion: `position_no, model, unit_qty, total_price, lead_time_days` (5 cols).
  - Dell: none (default `[]`).

**`RowKind`** (enum, `src/core/normalizer.py:29`): `ITEM | HEADER`. HEADER rows short-circuit to `matched_rule_id="HEADER-SKIP"`.

**`RuleSet`** (`spec_classifier/src/rules/rules_engine.py:110`): exposes `base_rules, service_rules, logistic_rules, software_rules, note_rules, config_rules, hw_rules` (each `list[dict]` of `{field, pattern, rule_id, entity_type, ...}`), `device_type_rules`, `device_type_applies_to`, `hw_type_rules`, `hw_type_device_type_map`, `hw_type_rule_id_map`, `hw_type_applies_to`, plus state rules (absent + override).

**`ClassificationResult`** (dataclass, `src/core/classifier.py:54`): `row_kind, entity_type, state, matched_rule_id, device_type, hw_type, warnings`.

**`EntityType`** (enum, `src/core/classifier.py:15`): `BASE | HW | CONFIG | SOFTWARE | SERVICE | LOGISTIC | NOTE | UNKNOWN`.

**`State`** (enum, `src/core/state_detector.py:11`): `PRESENT | ABSENT | DISABLED`.

**`HW_TYPE_VOCAB`** (frozenset, 26 buckets): defined twice — `src/core/classifier.py:28` and `batch_audit.py:44` — must stay in sync; documented in `spec_classifier/docs/taxonomy/hw_type_taxonomy.md`.

## Entry Points

**`run.ps1`**: User in PowerShell at repo root. Resolves INPUT/OUTPUT from `config.local.yaml`; loops `$ALL_VENDORS = @("dell","cisco","hpe","lenovo","huawei","xfusion")`; runs `python main.py --batch-dir … --vendor …`, then `batch_audit.py` (rule-based then optional AI), then `cluster_audit.py`, then `pytest`.

**`teresa.bat`**: Double-click in Explorer. Verifies Python on PATH, ensures PyQt6, launches GUI via `pythonw teresa_gui.py`.

**`teresa_gui.py`**: PyQt6 window with per-vendor buttons + Full Pipeline button + AI/tests toggles + OpenAI key field. On click, `subprocess.Popen` with `CREATE_NEW_CONSOLE` spawns a new PowerShell running `run.ps1` with chosen flags. Discovers INPUT/OUTPUT from `spec_classifier/config.local.yaml`.

**`spec_classifier/main.py`**: `python main.py --input … --vendor …` or `--batch-dir … --vendor …` or `--batch`. Argparse, config loading, adapter dispatch, per-file `_run_single`, optional `--save-golden` / `--update-golden`.

**`spec_classifier/batch_audit.py`**: `python batch_audit.py --output-dir <OUTPUT> [--no-ai] [--vendor <v>] [--since YYYY-MM-DD] [--dry-run]`. Walks run folders, reads `*_annotated.xlsx`, runs E1–E18 + optional OpenAI calls, writes `audit_report.json`, `audit_summary.xlsx`, `*_audited.xlsx`.

**`spec_classifier/cluster_audit.py`**: `python cluster_audit.py --output-dir <OUTPUT> [--vendor <v>] [--dry-run] [--min-cluster-size N] [--max-clusters N]`. TF-IDF + HDBSCAN/KMeans on UNKNOWN / HW-without-device_type rows; emits `cluster_summary.xlsx`; appends `clusters` to `audit_report.json`.

**`spec_classifier/conftest.py`**: pytest entry. Resolves `paths.input_root` (hard error if missing); `pytest_sessionfinish` fails the session if `skipped/total > 0.50` or `passed == 0` while tests collected.

## Architectural Constraints

- **Threading:** Single-threaded, synchronous. No `asyncio`, no thread pool. Per-file processing is serial in `_run_single`. The GUI uses `subprocess.Popen` with `CREATE_NEW_CONSOLE` to run pipelines in a separate PowerShell process.
- **Global state:** Module-level dicts in `spec_classifier/main.py` (`VENDOR_REGISTRY`) and `batch_audit.py` (`HW_TYPE_VOCAB`, `VALID_ENTITY_TYPES`, `VALID_STATES`, `DEVICE_TYPE_ALIASES`, `_ALIASES`, `_E8_NO_HW_TYPE_DEVICES`, `E4_STATE_VALIDATORS`). Logging is configured globally via `logging.basicConfig`; per-run `FileHandler` attached/detached around `_run_single`.
- **Circular imports:** None known. Direction: `entry → vendors / outputs → core → rules`.
- **YAML rule order is load-bearing:** Rules evaluated top-to-bottom, first match wins. Reordering a YAML file mid-edit can change classifications without code change.
- **Code-only repo:** INPUT, OUTPUT, fixtures, golden runs, `.venv/` live outside the repo. `config.local.yaml` (gitignored) overlays `config.yaml`. Both `main.py:_load_config` and `conftest.py` implement the same overlay logic — keep them in sync.
- **`hw_type` `applies_to` is `[HW]` only** (never `[HW, BASE]`). Code-confirmed contract.
- **`HW_TYPE_VOCAB` duplication:** canonical 26-bucket set duplicated verbatim between `src/core/classifier.py:28` and `batch_audit.py:44`.
- **Branded spec is per-vendor opt-in** via `adapter.generates_branded_spec()`. All current adapters return `True`, but the plumbing is gated.
- **Adding a vendor requires four touch points:** subclass `VendorAdapter`, register in `VENDOR_REGISTRY` (`spec_classifier/main.py`), append to `$ALL_VENDORS` (`run.ps1`), append to `VENDORS_ACTIVE` (`teresa_gui.py`). Recipe in `spec_classifier/prompts/00_VENDOR-RECON.md` and `spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md`.

## Anti-Patterns

### Dell-specific code in the `core/` directory
**What happens:** `spec_classifier/src/core/parser.py` searches the sentinel `"Module Name"` (Dell-only) and is imported only by `DellAdapter`. Every other vendor has its own `src/vendors/<v>/parser.py`.
**Why it's wrong:** Files in `core/` should be vendor-agnostic. A reader assuming `core/parser.py` is shared will be misled, and "fixing it for HPE" will break Dell.
**Do this instead:** Move it to `spec_classifier/src/vendors/dell/parser.py` and update `DellAdapter` import. Tracked as tech debt item #7 in `spec_classifier/CLAUDE.md`.

### Audit reads from Excel instead of `classification.jsonl`
**What happens:** `spec_classifier/batch_audit.py` opens `*_annotated.xlsx` via `pd.read_excel` and re-derives entity_type / device_type / hw_type from human-readable columns.
**Why it's wrong:** Round-tripping through Excel introduces string-coercion bugs (NaN, blank vs `""`, header offset). The pipeline already produces structured `classification.jsonl`.
**Do this instead:** Audit should consume `classification.jsonl` + `rows_normalized.json`. Tracked as tech debt item #1. **Do not "fix" as part of unrelated work.**

### Alias-table sprawl in `batch_audit.py`
**What happens:** Multiple parallel mapping tables (`DEVICE_TYPE_ALIASES`, `_ALIASES`, `HW_TYPE_TRUST`, `DEVICE_TYPE_TRUST`, `ENTITY_TRUST_PIPELINE`) used for AI-mismatch suppression.
**Why it's wrong:** Easy to mistake `DEVICE_TYPE_ALIASES` for an `hw_type` mapping (it isn't — `power_cord ≈ cable` is suppression-only). Authoritative `device_type → hw_type` is `device_type_map` in each `rules/<vendor>_rules.yaml`.
**Do this instead:** Consolidate behind a single canonical schema. Tech debt item #2.

### `HW_TYPE_VOCAB` duplicated between modules
**What happens:** 26-bucket taxonomy hard-coded in both `src/core/classifier.py:28` and `batch_audit.py:44`.
**Why it's wrong:** Adding/removing a bucket in one place silently desyncs validators.
**Do this instead:** Extract to `src/core/taxonomy.py`; import from both.

### `batch_audit.py` god-object (~1500 LOC)
**What happens:** One file holds E-code logic, AI suppression tables, vendor detection, Excel I/O, audit-report assembly.
**Why it's wrong:** Hard to test in isolation; changes risk regressions in unrelated audit paths.
**Do this instead:** Split by concern. Tech debt item #3.

## Error Handling

**Strategy:** Fail-fast at entry; `_run_single` returns non-zero on any pipeline exception; batch mode collects per-file failures and returns 1 if any failed.

**Patterns:**
- `_run_single` (`spec_classifier/main.py:113`) wraps the pipeline in top-level `try/except`:
  - `FileNotFoundError` → stderr message, return 1.
  - `yaml.YAMLError` → stderr message, return 1.
  - bare `Exception` → `log.exception("Pipeline failed")`, return 1.
  - Inner `try/finally` ensures the `run.log` `FileHandler` is removed and closed even on failure.
- `adapter.can_parse(path)` is the cheap gate in batch mode; documented to **let read errors propagate** (`src/vendors/base.py:18–22`: *"Do not catch exceptions — unreadable file should propagate as failure, not skip."*).
- Rules engine warns (does not raise) on unknown rule fields: `_get_field_value` returns `None` and logs (`src/rules/rules_engine.py:46`).
- `_apply_hw_type` adds `"hw_type unresolved for HW row"` to `result.warnings` instead of raising (`src/core/classifier.py:223`).
- `run.ps1` exits with the failed step's exit code (`exit $LASTEXITCODE`) at every stage.

## Cross-Cutting Concerns

**Logging:**
- `logging.basicConfig(level=INFO, format="%(asctime)s [%(levelname)s] %(message)s")` set in `spec_classifier/main.py:270`.
- Per-run `FileHandler` writes to `<run_folder>/run.log` (UTF-8); attached/detached via `try/finally` in `_run_single` (lines 137–227).

**Validation:**
- Schema validation via `tests/test_schema_validation.py` and `tests/test_rules_traceability.py`.
- `_validate_hw_type_vocab` (`src/core/classifier.py:186`) tags any `hw_type` outside `HW_TYPE_VOCAB` with a warning rather than raising.
- E1–E18 in `batch_audit.py` are the post-hoc validation layer.

**Authentication:** Only `OPENAI_API_KEY` (env var). Read by `run.ps1` (lines 78–90) and `teresa_gui.py:get_env_key`. GUI persists via `setx` at User scope. No databases, no remote services, no secrets in repo.

**Configuration:**
- `spec_classifier/config.yaml` (committed): `paths` (relative fallbacks — explicitly flagged as policy-violating in the file's own header), `cleaned_spec.include_types`, `cleaned_spec.include_only_present`, `vendor_rules` mapping vendor → YAML path.
- `spec_classifier/config.local.yaml` (gitignored): absolute `input_root` / `output_root`, optional `vendor_rules` overrides. Loaded by both `main.py:_load_config` and `conftest.py:load_config` — keep both in sync.

**Encoding:** All file I/O uses `encoding="utf-8"` (or `utf-8-sig` for `_load_config` in `batch_audit.py`). Both audit scripts force `sys.stdout` / `sys.stderr` to UTF-8 via `reconfigure(encoding="utf-8", errors="replace")` for Cyrillic-safe Windows output.

*Architecture map: 2026-05-10*
