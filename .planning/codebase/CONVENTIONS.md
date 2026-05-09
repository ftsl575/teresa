# Coding Conventions

**Analysis Date:** 2026-05-09

## Language & Toolchain

- **Python** — no minimum version pinned in `spec_classifier/pyproject.toml`; tests run on CPython 3.10 (per `spec_classifier/tests/__pycache__/*.cpython-310-pytest-9.0.3.pyc`).
- **Dependencies:** `spec_classifier/requirements.txt` is the only declared dependency list — `openpyxl>=3.1.0`, `pandas>=2.0.0`, `pyyaml>=6.0`, `pytest>=7.0.0`. No `setup.py`, no installable package; code runs directly from `spec_classifier/` as cwd.
- **`spec_classifier/pyproject.toml`** is intentionally minimal — only `cache_dir = "../../temporary/.pytest_cache"`. No `[project]`, `[tool.black]`, `[tool.ruff]`, `[tool.mypy]` sections. No committed formatter / type-checker config.
- The repo root holds **no Python package**. `run.ps1`, `teresa_gui.py`, `teresa.bat` at the root are launchers for `spec_classifier/`.

## Naming Patterns

**Files / modules:**
- All Python modules use `snake_case.py`: `state_detector.py`, `rules_engine.py`, `branded_spec_writer.py`, `run_manager.py`, `stats_collector.py`.
- Vendor adapters: `spec_classifier/src/vendors/<vendor>/{adapter,parser,normalizer,__init__}.py`. Vendor names are **lowercase** in directory names, in `VENDOR_REGISTRY` keys (`spec_classifier/main.py:42`), in the `--vendor` CLI choice, and in the `$ALL_VENDORS` array (`run.ps1:45`).
- Test files mirror the unit under test: `tests/test_<module>.py` (`tests/test_normalizer.py`, `tests/test_state_detector.py`) or `tests/test_<vendor>_<area>.py` (`tests/test_lenovo_parser.py`, `tests/test_hpe_rules_unit.py`, `tests/test_regression_cisco.py`).
- Rule files: `spec_classifier/rules/<vendor>_rules.yaml` (`dell_rules.yaml`, `cisco_rules.yaml`, `hpe_rules.yaml`, `lenovo_rules.yaml`, `huawei_rules.yaml`, `xfusion_rules.yaml`).
- Golden fixtures: `spec_classifier/golden/<stem>_expected.jsonl` where `<stem>` is the input XLSX stem (`dl1`, `ccw_1`, `hp1`, `L1`, `xf1`, `hu1`).

**Functions:**
- `snake_case` everywhere. Module-private helpers prefixed with single underscore: `_get_adapter`, `_load_config`, `_resolve_path`, `_save_golden`, `_run_single`, `_compare_row`, `_load_golden`, `_check_e4`. Leading underscore means "internal — don't import elsewhere".
- Classification helpers: `classify_row`, `match_rule`, `match_device_type_rule`, `match_hw_type_rule`, `detect_state`, `detect_row_kind`, `normalize_row`.

**Variables / constants:**
- Module-level constants are `UPPER_SNAKE_CASE`: `VENDOR_REGISTRY`, `DEFAULT_INPUT_ROOT`, `DEFAULT_OUTPUT_ROOT` (`spec_classifier/main.py`), `MAX_SKIP_RATIO` (`spec_classifier/conftest.py:14`), `HW_TYPE_VOCAB` (`spec_classifier/src/core/classifier.py:28`), `DEVICE_TYPE_ALIASES`, `ENTITY_TRUST_PIPELINE`, `HW_TYPE_TRUST`, `DEVICE_TYPE_TRUST`, `_E8_NO_HW_TYPE_DEVICES`, `_E14_EXCLUDE_SKUS`, `_E16_EXCLUDE_SKUS` (`spec_classifier/batch_audit.py`).
- Locals: `snake_case` (`raw_rows`, `header_row_index`, `normalized_rows`, `classification_results`, `run_folder`).

**Types / classes:**
- `PascalCase` for classes and enums: `RuleSet`, `VendorAdapter`, `DellAdapter`, `CiscoAdapter`, `HPEAdapter`, `LenovoAdapter`, `HuaweiAdapter`, `XFusionAdapter`, `NormalizedRow`, `ClassificationResult`, `EntityType`, `State`, `RowKind`, `LenovoNormalizedRow`.
- Enum class is `PascalCase`, members `UPPER_CASE`: `EntityType.HW`, `RowKind.HEADER`, `State.PRESENT` (`spec_classifier/src/core/classifier.py`, `src/core/normalizer.py`, `src/core/state_detector.py`).

**Run / output stems:**
- Per-file run folder: `OUTPUT/<vendor>_run/run-YYYY-MM-DD__HH-MM-SS-<stem>/` (`spec_classifier/main.py:_run_single`, `src/diagnostics/run_manager.py:create_run_folder`).
- Aggregate folder: `run-YYYY-MM-DD__HH-MM-SS-TOTAL/` (`create_total_folder`).
- `<stem>` = input XLSX filename without extension. Vendor name is **never** capitalised in run folder names.

**Rule IDs:**
- Format: `^[A-Z0-9-]+$`, must contain at least one 3-digit group, no `--`. Enforced by `spec_classifier/tests/test_schema_validation.py:test_all_rule_ids_are_well_formed`.
- Conventions: `<SECTION>-<NNN>` (e.g. `BASE-001`, `HW-005-STORAGE-CUS`, `LOGISTIC-001`, `STATE-OVERRIDE-001`, `HEADER-SKIP`).
- Vendor-specific suffix: Lenovo uses `-L-` (`BASE-L-001`, `SW-L-001`, `SERVICE-L-001`), Dell device-type rules use `-D-` (`BASE-D-DT-001`, `DT-D-029-CABLE`), DEC acceptance rules `DEC-NNN-...` (`DEC-005-PERC-CONTROLLER`, `DEC-010-SFP-DAC-CABLE`).
- Sentinel `HEADER-SKIP` for `RowKind.HEADER` rows (`spec_classifier/src/core/classifier.py:78`); rows with no matching rule get `UNKNOWN-000`.
- `rule_id` namespaces: entity sections (`base_rules`, `service_rules`, …, `hw_rules`) share **one** namespace; `device_type_rules` and `hw_type_rules` are separate. Cross-namespace reuse is intentional. Enforced by `tests/test_schema_validation.py:test_no_duplicate_rule_ids`.

## Code Style

**Formatting:**
- No `.editorconfig`, no `pyproject.toml` formatter config, no `.pre-commit-config.yaml`. Style is convention, not tooling.
- Observed: 4-space indent, double quotes, trailing comma in multi-line literals, line length comfortably under 120.
- Comments are mixed English / Russian — canonical YAML rule files (`spec_classifier/rules/*_rules.yaml`) and `spec_classifier/CLAUDE.md` use Russian for narrative; code-level docstrings are predominantly English.

**Type hints:**
- Pragmatic, not exhaustive. Public dataclasses and engine entry points are typed: `NormalizedRow` (`spec_classifier/src/core/normalizer.py:36`), `ClassificationResult` (`src/core/classifier.py:54`), `RuleSet.load(path: str) -> "RuleSet"`, `match_rule(row: NormalizedRow, rules: List[dict]) -> Optional[dict]`, `classify_row(row: NormalizedRow, ruleset: RuleSet) -> ClassificationResult`.
- Helper / internal functions often omit annotations (`spec_classifier/main.py:_get_adapter`, `_resolve_path`).
- No `mypy`/`pyright` config — type hints are documentation, not gated.
- Mixed `Optional[X]` and `X | None`: `get_source_sheet_name(self) -> str | None` (`spec_classifier/src/vendors/base.py:48`) vs `Optional[dict]` (`src/rules/rules_engine.py:51`). Both styles co-exist; do not rewrite during unrelated edits.

**Dataclasses:**
- `@dataclass` for value-objects (`NormalizedRow`, `ClassificationResult`). `field(default_factory=list)` for mutable defaults (`ClassificationResult.warnings`).

**Enums:**
- `Enum` (not `IntEnum`/`StrEnum`) with explicit string values matching the YAML values: `EntityType.HW = "HW"`, `RowKind.ITEM = "ITEM"`, `State.PRESENT = "PRESENT"`. Serialised via `.value` in `_build_golden_rows` (`spec_classifier/main.py:89`) and `tests/helpers.py:build_golden_rows`.

## Import Organization

Order observed across `spec_classifier/main.py`, `src/core/classifier.py`, `src/rules/rules_engine.py`, `tests/helpers.py`:

1. Standard library (`json`, `logging`, `re`, `sys`, `argparse`, `pathlib`, `dataclasses`, `enum`, `typing`).
2. Third-party (`yaml`, `pandas`, `openpyxl`, `pytest`).
3. Local absolute imports under `src.`: `from src.rules.rules_engine import RuleSet`, `from src.core.classifier import classify_row`.
4. Local imports from the repo root: `from main import _get_adapter`, `from conftest import project_root`, `from batch_audit import validate_row`.

**Path aliases / sys.path:** Tests that import from `batch_audit.py` or `cluster_audit.py` (which live at `spec_classifier/` root, not under `src/`) prepend the parent dir at runtime: `sys.path.insert(0, str(Path(__file__).resolve().parent.parent))` (`tests/test_batch_audit.py:10`, `tests/test_cluster_audit.py:10`, `tests/test_lenovo_parser.py:9`). Do not refactor — codebase is not pip-installable.

## YAML Rules Authoring

**Source of truth:** `spec_classifier/docs/rules/RULES_AUTHORING_GUIDE.md` (referenced from comments in `rules/dell_rules.yaml:279`).

**File structure (per vendor YAML):**

```yaml
version: "X.Y.Z"

state_rules:
  present_override_keywords: [...]
  absent_keywords: [...]

base_rules: [...]            # PRIORITY 1
service_rules: [...]         # PRIORITY 2
logistic_rules: [...]        # PRIORITY 3
software_rules: [...]        # PRIORITY 4
note_rules: [...]            # PRIORITY 5
config_rules: [...]          # PRIORITY 6
hw_rules: [...]              # implicit fallback before UNKNOWN

device_type_rules:
  applies_to: [HW, LOGISTIC, BASE]
  rules: [...]

hw_type_rules:
  applies_to: [HW]           # MUST be [HW] only
  device_type_map: {...}     # device_type → hw_type
  rule_id_map: {...}         # matched_rule_id → hw_type
  rules: [...]               # regex fallback
```

**Rule item shape:**
```yaml
- field: module_name | option_name | option_id | sku | is_bundle_root | service_duration_months
  pattern: '(?i)<regex>'
  entity_type: BASE | HW | CONFIG | SOFTWARE | SERVICE | LOGISTIC | NOTE | UNKNOWN
  rule_id: <UPPERCASE-DASH-3DIGIT>
```

Known fields are enforced in `spec_classifier/src/rules/rules_engine.py:16` (`_KNOWN_FIELDS`); unknown fields log a warning and the rule is skipped.

**Critical authoring rules:**
- **Rule order matters.** Top-to-bottom evaluation, first match wins (`src/rules/rules_engine.py:51-70`, `match_rule`). The canonical priority `BASE → SERVICE → LOGISTIC → SOFTWARE → NOTE → CONFIG → HW → UNKNOWN` is enforced by call order in `classify_row` (`src/core/classifier.py:67-`). Reordering YAML lists mid-edit can flip classification — never sort alphabetically.
- **More-specific patterns first.** Example: `SERVICE-005` (`NO WARRANTY UPGRADE`) is placed *before* generic `SERVICE-003` (`Warranty`) inside `dell_rules.yaml:73-81` with comment `# More specific first`.
- **`applies_to` for `device_type_rules`** is `[HW, LOGISTIC, BASE]` (verified across `dell_rules.yaml:291`, `hpe_rules.yaml:333`).
- **`applies_to` for `hw_type_rules`** is **`[HW]` only** — never `[HW, BASE]`. Validated by `tests/test_schema_validation.py:test_hw_type_applies_to_valid` against `_VALID_ENTITIES`.
- **`device_type_map`** is the authoritative `device_type → hw_type` map for that vendor. Vendors may legitimately differ: HPE maps `bezel → chassis`, Lenovo maps `bezel → accessory`. Source: `rules/<vendor>_rules.yaml:hw_type_rules.device_type_map`.
- **`rule_id_map`** is a second layer — explicit `matched_rule_id → hw_type` (e.g. `HW-001: chassis`, `HW-005-STORAGE-CUS: storage_drive`). Use when a single rule should always produce the same `hw_type` regardless of `device_type`.
- **Schema validation** (`tests/test_schema_validation.py`) gates: rule_id format, valid `entity_type` values, valid `applies_to`, no duplicate `rule_id` within a namespace.
- **Regex flag convention:** `(?i)` inline flag preferred for clarity; `re.IGNORECASE` is also applied by `match_rule` (`src/rules/rules_engine.py:68`) so duplicate flags are harmless. `\b` word boundaries used liberally.

## Critical Business Rules — Do Not Violate

Source of truth: `spec_classifier/CLAUDE.md` § БИЗНЕС-ПРАВИЛА.

1. **`power_cord` has `hw_type=None` intentionally.** Absent from `device_type_map` in every vendor YAML, with explicit comment `# hw_type: intentionally unmapped — power_cord has no hw_type` in `rules/dell_rules.yaml:278`, `rules/cisco_rules.yaml:196`, `rules/hpe_rules.yaml:360`. `batch_audit.py:506` excludes it from E8: `_E8_NO_HW_TYPE_DEVICES = {"power_cord", "enablement_kit"}`. **Do not "fix" the missing mapping.**
2. **LOGISTIC = packaging, documents, freight only.** Power cords, stacking cables, rails, brackets are HW, not LOGISTIC. `batch_audit.py` E13 flags `LOGISTIC + device_type ∈ {power_cord, cable, sfp_cable, fiber_cable}` as P0 (`spec_classifier/batch_audit.py:537-539`).
3. **BASE without `device_type`** is normal (E15 = INFO). **BASE with `device_type`** is valid; E6/E10 must not fire. Only `hw_type` on BASE triggers E10 (`spec_classifier/batch_audit.py:522-527`).
4. **`is_factory_integrated=True`** rows are CONFIG; AI does not check them.
5. **`hw_type_rules.applies_to`** is `[HW]` only — never `[HW, BASE]`.

## Alias Tables — Semantics

`spec_classifier/batch_audit.py:363 DEVICE_TYPE_ALIASES` (e.g. `ram=memory`, `nic=network_adapter`, `power_cord=cable`, `bezel=chassis`, `drive_cage=backplane`) is the **AI-mismatch suppression table**, NOT a `hw_type` mapping. Consumed in exactly one place: `build_ai_mismatch()` (`batch_audit.py:439-440`) where pipeline `device_type` and AI `device_type` are normalised before the equality check; if normalised forms match, no `AI_MISMATCH` is raised.

The authoritative `device_type → hw_type` mapping is `device_type_map` in each `rules/<vendor>_rules.yaml`. **Never** use `DEVICE_TYPE_ALIASES` to derive `hw_type` from `device_type`. Vendors legitimately differ (HPE `bezel → chassis`, Lenovo `bezel → accessory`).

Other auxiliary tables in `batch_audit.py` (`ENTITY_TRUST_PIPELINE`, `HW_TYPE_TRUST`, `DEVICE_TYPE_TRUST`, `spec_classifier/batch_audit.py:387-405`) are also AI-mismatch suppression — they gate which entity / device types are "trusted from pipeline" so AI disagreement is suppressed.

The `_ALIASES` table (canonical-field-name aliasing for HPE Excel quirks) is separate: `config_name → module_name`, `description → option_name`, `part_number → skus`, `product_# → skus` (per `spec_classifier/CLAUDE.md` § "Canonical Field Names").

## Error Handling

**Strategy:** explicit, fail-loud. No silent fallbacks for missing rules / files / config.

**Patterns:**
- **Hard errors (raise / nonzero exit):**
  - Missing rules file: `print(f"Error: Rules file not found: {rules_path}", file=sys.stderr)` then `return 1` from `_run_single` (`spec_classifier/main.py:149-150`).
  - Missing config: `_load_config` raises `FileNotFoundError` (`spec_classifier/main.py:69-71`).
  - Unknown vendor: `_get_adapter` raises `ValueError(f"Unknown vendor: {vendor!r}")` (`spec_classifier/main.py:55`).
  - `VendorAdapter.can_parse` MUST NOT catch exceptions — "unreadable file should propagate as failure, not skip" (`spec_classifier/src/vendors/base.py:18-22`).
- **UNKNOWN as in-band signal (not exception):** A row that no rule matches gets `entity_type=EntityType.UNKNOWN`, `matched_rule_id="UNKNOWN-000"`. This is the *expected* surface for unknown rows — surfaced via `unknown_rows.csv` per run, and via E2 (BLOCKER) in audit (`spec_classifier/batch_audit.py:483-484`).
- **Unknown rule field → log warning, skip rule:** `_get_field_value` returns `None` and `_log.warning("Unknown field in rule: %s — rule will be skipped", field)` (`spec_classifier/src/rules/rules_engine.py:46-48`).
- **Audit E-codes are diagnostics, not exceptions.** `validate_row` returns a `list[str]` of E-code strings; severity interpreted by caller / report (`spec_classifier/batch_audit.py:463-`). Severity ladder: `BLOCKER` (E2) → `P0` (E1, E3, E5, E6, E10–E13, E18) → `P1` (E4, E7–E9, E14, E17) → `INFO` (E15, E16).
- **Pipeline failure return code:** `_run_single` returns `int` (0 success, 1 failure). `run.ps1` checks `$LASTEXITCODE` after each stage and aborts the chain.

## Logging

- Stdlib `logging`. Module loggers: `_log = logging.getLogger(__name__)` (`spec_classifier/src/rules/rules_engine.py:14`). Run-level handler attached per-input-file in `_run_single`: `FileHandler` on `<run_folder>/run.log` with format `"%(asctime)s [%(levelname)s] %(message)s"` and date format `"%Y-%m-%d %H:%M:%S"` (`spec_classifier/main.py:137-139`).
- Levels: `INFO` for stage transitions ("Parsing Excel: ...", "Normalizing rows ..."), `WARNING` for skipped rules / unknown fields.
- No `print` for diagnostics in core code; `print(..., file=sys.stderr)` only for top-level CLI errors (`spec_classifier/main.py:150`). PowerShell launcher `run.ps1` uses `Write-Host` with explicit `-ForegroundColor`.

## Comments

- Block dividers `# ===…===` for top-level YAML/Python sections (`spec_classifier/rules/dell_rules.yaml:3`, `src/core/classifier.py:28`).
- Inline rationale uses Russian for domain decisions, English for code mechanism.
- "Why" comments are mandatory for non-obvious rule placement, business decisions, and known fragile bits — see `# BUGFIX: \bck\b предотвращает ложное срабатывание в "Backplane"` (`rules/dell_rules.yaml:323`), `# More specific first: NO WARRANTY UPGRADE before generic Warranty` (`rules/dell_rules.yaml:72`).
- Cross-references to git commits, doc files, PR identifiers used liberally: `# See git: c3c7cb6 fix(taxonomy): restore power_cord hw_type=None`, `# (PR-4c flip 06d64c1)`, `# See RULES_AUTHORING_GUIDE.md for rationale`.

## Function Design

- Pure-function style preferred for the classification core: `match_rule`, `match_device_type_rule`, `match_hw_type_rule`, `classify_row`, `detect_state`, `detect_row_kind`, `normalize_row` are all referentially transparent given a `RuleSet` + `NormalizedRow`.
- I/O concentrated in `main.py`, `src/outputs/*`, `src/diagnostics/*`. Tests exploit this by calling `helpers.run_pipeline_in_memory` (`spec_classifier/tests/helpers.py:55`) — full pipeline in memory, **no disk I/O** for normalize+classify.
- Functions typically 5–60 lines; the longest are in `batch_audit.py` (`validate_row` ~150 lines).
- Test helpers like `_row(*, row_kind=…, module_name="", …, **kwargs)` use keyword-only after `*` (`spec_classifier/tests/test_rules_unit.py:23`, `tests/test_dec_acceptance.py:26`).

## Module Design

- `src/` is a flat namespace package (`spec_classifier/src/__init__.py` exists empty). No barrel `__init__.py` re-exports — every consumer imports the concrete module: `from src.core.classifier import classify_row`, not `from src.core import classify_row`.
- `src/vendors/<v>/__init__.py` files exist but are typically empty.
- Top-level scripts (`spec_classifier/main.py`, `batch_audit.py`, `cluster_audit.py`) are **not** importable as a package; they are runnable entry points. Tests import their internals via `sys.path` shimming.

## Configuration Layering

- Two-layer YAML overlay: `spec_classifier/config.yaml` (committed defaults, relative paths) overlaid by `spec_classifier/config.local.yaml` (gitignored, absolute paths). Same logic in `main.py:_load_config` and `conftest.py:load_config`. Local file wins per top-level key; nested dicts merged with `data[key].update(value)`.
- CLI flags (`--input`, `--batch-dir`, `--output-dir`, `--vendor`) override config.
- Default fallback paths under repo root violate the code-only policy on purpose for CI portability — `config.yaml` carries `paths.input_root: "input"`, `paths.output_root: "output"`. A note in the file explains this.

## Development Cycle (GSD-style)

Source of truth: `spec_classifier/prompts/` plus `spec_classifier/CLAUDE.md` § ЦИКЛ РАЗРАБОТКИ.

```
PRE-CHECK → PLAN (MASTER PLAN A or B) → CURSOR IMPLEMENT → POST-CHECK → AUDIT (1A–1G) → DOC UPDATE
```

| Scenario | Steps |
|---|---|
| Small YAML edit | `01_PRE-CHECK` → `06_BATCH-AUDIT-MASTER-PLAN` → `03_CURSOR-IMPLEMENT` → `04_POST-CHECK` |
| New feature / refactor | `01_PRE-CHECK` → `02_MASTER-PLAN` (variant A) → `03_CURSOR-IMPLEMENT` → `04_POST-CHECK` → `05_AUDIT-1A-1G` |
| After FAIL audit | `02_MASTER-PLAN` (variant B = fix) → `03` → `04` → `05_1G` |
| Doc update | `05_AUDIT-1A-1G` → `07_DOC-UPDATE-MASTER-PLAN` → `03` |
| New vendor | `00_VENDOR-RECON` → `01` → `02A` → `03` → `04` → `05` → `07` |

**Audit phases (`spec_classifier/prompts/05_AUDIT-1A-1G.md`):** 1A through 1G are six discrete review windows feeding into a final 1G verdict (PASS / FAIL). The final 1G window receives only the SUMMARY blocks from prior windows (rule R5 in `spec_classifier/CLAUDE.md`).

**Severity ladder:** P0 (BLOCKER — broken tests, raised UNKNOWN, contract violation), P1 (IMPORTANT — fix in next cycle), P2 (NICE — refactor / cosmetic). Architectural debt (P2) and documentation drift are **excluded** from a fix-cycle scope by policy (`spec_classifier/prompts/README.md:57-59`).

**Hard rules for Claude windows** (`spec_classifier/CLAUDE.md` § ЖЁСТКИЕ ПРАВИЛА):
- **R1.** Each step = a separate Claude window (Cowork mode exempts this).
- **R2.** Read only files explicitly listed in the prompt for that window.
- **R3.** Every answer ends with a `SUMMARY:` block (CLAIMS / EVIDENCE / SEVERITY / ACTION).
- **R4.** "Tracked in git" claims need an SHA — otherwise unconfirmed.
- **R5.** The final 1G window receives only SUMMARY blocks, never full text.

## Function & Class Quick Reference

| Name | File | Purpose |
|---|---|---|
| `VENDOR_REGISTRY` | `spec_classifier/main.py:42` | Vendor → adapter class map |
| `_get_adapter` | `spec_classifier/main.py:52` | Factory; `ValueError` on unknown vendor |
| `_load_config` | `spec_classifier/main.py:69` | YAML two-layer overlay |
| `_run_single` | `spec_classifier/main.py:113` | Pipeline orchestrator |
| `RuleSet` | `spec_classifier/src/rules/rules_engine.py:110` | Loaded YAML rules wrapper |
| `match_rule` | `spec_classifier/src/rules/rules_engine.py:51` | First-match-wins regex matcher |
| `classify_row` | `spec_classifier/src/core/classifier.py:67` | Row → `ClassificationResult` |
| `EntityType` | `spec_classifier/src/core/classifier.py:15` | Enum: BASE/HW/CONFIG/SOFTWARE/SERVICE/LOGISTIC/NOTE/UNKNOWN |
| `HW_TYPE_VOCAB` | `spec_classifier/src/core/classifier.py:28` | 26 canonical hw_type values |
| `RowKind` / `NormalizedRow` / `detect_row_kind` / `normalize_row` | `spec_classifier/src/core/normalizer.py` | Row kind + value normalisation |
| `State` / `detect_state` | `spec_classifier/src/core/state_detector.py` | PRESENT/ABSENT/DISABLED detection |
| `VendorAdapter` (ABC) | `spec_classifier/src/vendors/base.py:5` | Adapter contract |
| `validate_row` | `spec_classifier/batch_audit.py:463` | E1–E18 dispatch |
| `DEVICE_TYPE_ALIASES` | `spec_classifier/batch_audit.py:363` | AI-mismatch suppression (NOT hw_type map) |
| `MAX_SKIP_RATIO` | `spec_classifier/conftest.py:14` | Pytest skip-guard threshold (0.50) |

*Convention analysis: 2026-05-09*
