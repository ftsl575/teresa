# Testing Patterns

**Analysis Date:** 2026-05-09

## Test Framework

- **Runner:** pytest 7+ (`spec_classifier/requirements.txt:4`). The lockfile-free env runs against pytest 9.0.3 (per `tests/__pycache__/*.cpython-310-pytest-9.0.3.pyc`). Always invoke from `spec_classifier/` as cwd.
- **Config:** `spec_classifier/pyproject.toml` `[tool.pytest.ini_options]` only sets `cache_dir = "../../temporary/.pytest_cache"`. There is no `conftest.py` in `tests/` — the only `conftest.py` is `spec_classifier/conftest.py`, which both tests *and* the session-finish hook live in.
- **Assertion style:** stdlib `assert`. No `unittest`, no Hamcrest. `pytest.raises` for exceptional paths (`spec_classifier/tests/test_rules_traceability.py:22`).

**Run commands** (run from `spec_classifier/`):

```powershell
pytest tests/ -v --tb=short                            # full suite
pytest tests/test_lenovo_rules_unit.py -v              # single file
pytest tests/test_regression.py::test_dl1 -v           # single test (parametrize id)
pytest -k "lenovo and parser" -v                       # by keyword expression
pytest tests/ --collect-only                           # enumerate without execution
```

Wrapped via Make (`spec_classifier/Makefile:67-94`): `make test`, `make test-unit`, `make test-smoke`, `make test-regression`, `make test-regression-cisco`, `make test-regression-hpe`, `make test-unknown`, `make test-unknown-cisco`, `make test-unknown-hpe`. The Makefile groups don't yet include lenovo / huawei / xfusion targets.

Wrapped via PowerShell launcher (`run.ps1`):

```powershell
.\run.ps1                              # full pipeline + audit + cluster + pytest
.\run.ps1 -TestsOnly                   # short-circuit, only pytest tests/ -v --tb=short (run.ps1:71-76)
.\run.ps1 -SkipTests                   # full run without pytest at end (run.ps1:144-152)
.\run.ps1 -Vendor huawei -NoAi -SkipTests   # smoke, single vendor, no OpenAI key, no pytest
```

When `-TestsOnly` or no flag is passed, `run.ps1` ends with `python -m pytest tests/ -v --tb=short` and propagates `$LASTEXITCODE` (`run.ps1:147-151`).

## Test File Organization

**Location:** `spec_classifier/tests/` — all tests in one flat directory. No nested vendor folders.

**Naming patterns observed:**
- `tests/test_<module>.py` — unit tests for one source module: `test_normalizer.py`, `test_state_detector.py`, `test_rules_unit.py`.
- `tests/test_<vendor>_<area>.py` — vendor-specific units: `test_dell` is implicit (the unprefixed file is Dell), `test_cisco_parser.py`, `test_cisco_normalizer.py`, `test_cisco_rules_unit.py`, `test_hpe_parser.py`, `test_hpe_normalizer.py`, `test_hpe_rules_unit.py`, `test_lenovo_parser.py`, `test_lenovo_normalizer.py`, `test_lenovo_rules_unit.py`, `test_huawei_parser.py`, `test_huawei_normalizer.py`, `test_huawei_rules_unit.py`, `test_xfusion_parser.py`, `test_xfusion_normalizer.py`, `test_xfusion_rules_unit.py`.
- `tests/test_regression*.py` — golden-file regression: `test_regression.py` (Dell), `test_regression_cisco.py`, `test_regression_hpe.py`, `test_regression_lenovo.py`, `test_regression_huawei.py`, `test_regression_xfusion.py`.
- `tests/test_unknown_threshold*.py` — UNKNOWN-ratio threshold per vendor: `test_unknown_threshold.py` (Dell), `test_unknown_threshold_cisco.py`, `test_unknown_threshold_hpe.py`, `test_unknown_threshold_huawei.py`, `test_unknown_threshold_xfusion.py`.
- Cross-cutting: `test_smoke.py` (full-pipeline artifact creation), `test_dec_acceptance.py` (DEC P1–P8 acceptance), `test_schema_validation.py` (YAML rule structural checks), `test_rules_traceability.py` (rules-file SHA-256), `test_batch_audit.py`, `test_cluster_audit.py`, `test_annotated_writer.py`, `test_branded_spec_writer.py`, `test_excel_writer.py`, `test_output_structure.py`, `test_cli.py`, `test_stats_hw_type.py`, `test_device_type.py`, `test_can_parse_xfusion_huawei_disjoint.py`.

**Shared helpers:** `spec_classifier/tests/helpers.py` exposes:
- `find_annotated_header_row(filepath, max_rows=60)` and `read_annotated_excel(filepath)` for tests reading produced annotated Excel files.
- `run_pipeline_in_memory(vendor, input_path, rules_path, config=None) -> (normalized_rows, classification_results)` — full pipeline (parse → normalize → classify) in memory, no disk I/O. Imports `_get_adapter` from `main` (`spec_classifier/tests/helpers.py:62`).
- `build_golden_rows(normalized_rows, classification_results)` — builds golden-format dicts matching the JSONL schema `{source_row_index, row_kind, entity_type, state, matched_rule_id, device_type, hw_type, skus}`.

**`spec_classifier/conftest.py` exports:**
- `project_root() -> Path` — returns `spec_classifier/` based on `__file__`, **not cwd**. Fix for tests that run from any cwd.
- `load_config()` — replicates `main._load_config` overlay logic for tests.
- `get_input_root()` and per-vendor variants `get_input_root_dell()`, `get_input_root_cisco()`, `get_input_root_hpe()`, `get_input_root_huawei()`, `get_input_root_lenovo()`, `get_input_root_xfusion()`. Each tries `paths.input_root/<vendor>/`; falls back to flat `paths.input_root/` if subdir doesn't exist.

## Test Structure

**Convention — function-style, no classes:**
```python
@pytest.fixture
def ruleset():
    path = Path(__file__).resolve().parent.parent / "rules" / "dell_rules.yaml"
    return RuleSet.load(str(path))


def _row(*, row_kind=RowKind.ITEM, module_name="", option_name="", **kwargs) -> NormalizedRow:
    """Keyword-only factory; sensible defaults for unset fields."""
    defaults = {"group_name": None, "group_id": None, "product_name": None,
                "option_id": None, "skus": [], "qty": 1, "option_price": 0.0}
    defaults.update(kwargs)
    return NormalizedRow(source_row_index=1, row_kind=row_kind,
                         module_name=module_name, option_name=option_name, **defaults)


def test_base_detection(ruleset):
    """module_name='Base' -> BASE, BASE-001."""
    row = _row(module_name="Base", option_name="PowerEdge R760 Server")
    result = classify_row(row, ruleset)
    assert result.entity_type == EntityType.BASE
    assert result.matched_rule_id == "BASE-001"
    assert result.state.value == "PRESENT"
```
(`spec_classifier/tests/test_rules_unit.py:18-71`)

**Patterns:**
- Module-level `_ruleset()` helper plus a `@pytest.fixture` wrapper (`tests/test_rules_unit.py:13-20`). The bare-helper version is reused as `_ruleset()` so other tests can call without going through the fixture (`tests/test_dec_acceptance.py:16`).
- Module-level `_row(*, ...)` factory with **keyword-only** args. Reused across `test_rules_unit.py`, `test_dec_acceptance.py`, `test_lenovo_rules_unit.py`. Each vendor uses its own `NormalizedRow` subclass (e.g. `LenovoNormalizedRow` in `tests/test_lenovo_rules_unit.py:10`).
- One assertion per logical concept; multi-assert tests check `entity_type`, `matched_rule_id`, and `state.value` together.
- Test docstring is a one-liner specifying the input → expected mapping, often quoting the rule_id (`"""module_name='Base' -> BASE, BASE-001."""`).

**Parametrize style:**
```python
@pytest.mark.parametrize("filename", ["dl1.xlsx", "dl2.xlsx", "dl3.xlsx", "dl4.xlsx", "dl5.xlsx"])
def test_regression(filename):
    ...
```
(`spec_classifier/tests/test_regression.py:36`)

For E-code coverage, `tests/test_batch_audit.py:79-100` uses tuple parametrize with named columns:
```python
@pytest.mark.parametrize("vendor, option_name, state, expect_e4", [
    ("dell", "No Hard Drive", "PRESENT", True),
    ("dell", "No 2 Rear Blanks Included", "PRESENT", False),
    ...
])
```

**Schema parametrization** in `tests/test_schema_validation.py:45-47`:
```python
@pytest.fixture(params=[str(p) for p in _RULES_FILES], ids=[p.stem for p in _RULES_FILES])
def rules_data(request):
    return _load_yaml(request.param), request.param
```
This runs the same structural test against every `rules/*_rules.yaml` with the file stem as the test ID.

## Mocking

- **No `pytest-mock`** dependency. Tests use `unittest.mock.patch` / `MagicMock` directly: `from unittest.mock import patch, MagicMock` (`spec_classifier/tests/test_batch_audit.py:6`).
- **Mock surface:** narrow — mainly used to fake the OpenAI client in `batch_audit` tests so the AI mismatch logic can be tested without an API key.
- **Filesystem mocking:** **avoided**. Tests that need files write real `.xlsx` to `tmp_path` via `openpyxl.Workbook` (`tests/test_lenovo_parser.py:_make_lenovo_xlsx`, `tests/test_cluster_audit.py:_make_xlsx`). This guarantees the parser sees a real workbook structure.
- **What NOT to mock:** the rules engine, the classifier, the parser/normalizer pipeline. Tests run them end-to-end via `run_pipeline_in_memory`.

## Fixtures and Factories

**Test-data fixtures: external, not in repo.**
- Real-vendor XLSX files live under `paths.input_root` (default `C:\Users\G\Desktop\INPUT\<vendor>\`, override via `config.local.yaml`). They are gitignored.
- Tests skip with `pytest.skip(f"Input not found: {input_path} (set paths.input_root in config.local.yaml)")` when files are absent (`spec_classifier/tests/test_regression.py:42-43`).

**Golden fixtures (in repo):** `spec_classifier/golden/*_expected.jsonl` — 41 files committed:
- Dell: `dl1_expected.jsonl` … `dl5_expected.jsonl`
- Cisco: `ccw_1_expected.jsonl`, `ccw_2_expected.jsonl`
- HPE: `hp1_expected.jsonl` … `hp8_expected.jsonl`
- Lenovo: `L1_expected.jsonl` … `L11_expected.jsonl`
- Huawei: `hu1_expected.jsonl` … `hu5_expected.jsonl`
- xFusion: `xf1_expected.jsonl` … `xf10_expected.jsonl`

**Golden file format** (one JSON object per line; `tests/helpers.py:build_golden_rows`):
```json
{"source_row_index": 1, "row_kind": "ITEM", "entity_type": "BASE",
 "state": "PRESENT", "matched_rule_id": "BASE-001",
 "device_type": "server", "hw_type": null, "skus": ["210-BDZY"]}
```

**Generating / updating goldens:**

```powershell
# Single file
python main.py --input <path.xlsx> --vendor <vendor> --save-golden        # overwrite
python main.py --input <path.xlsx> --vendor <vendor> --update-golden      # interactive y/N

# Per-vendor batches via Make (run from spec_classifier/)
make generate_golden_dell     # iterates dl1..dl5
make generate_golden_cisco    # ccw_1..ccw_2
make generate_golden_hpe      # hp1..hp8
make generate_golden          # all three
make generate_golden INPUT=/d/specs/INPUT   # override input root
```
(`spec_classifier/Makefile:30-65`)

The Makefile uses bash heredoc loops (`for d in $(DL_FILES); do …`) so it requires Git Bash / GNU Make on Windows. Lenovo / Huawei / xFusion goldens are not yet wired into Make targets — they are produced via direct `python main.py --save-golden` calls.

**In-test object factories:**
- `_row(*, ...)` for `NormalizedRow` (`tests/test_rules_unit.py:23`, `tests/test_dec_acceptance.py:26`).
- `_row(option_name, *, option_id="TEST1", module_name="")` for `LenovoNormalizedRow` (`tests/test_lenovo_rules_unit.py:19`).
- `_make_xlsx(path, columns, rows)` and `_make_lenovo_xlsx(path, data_rows, ...)` for synthetic Excel fixtures (`tests/test_cluster_audit.py:29`, `tests/test_lenovo_parser.py:26`).

## Test Types

**Unit tests** — no INPUT files needed:
- `tests/test_rules_unit.py` (Dell rules) — fixture-built `NormalizedRow`s tested against the loaded ruleset.
- `tests/test_state_detector.py` — `detect_state` truth table (loads only `rules/dell_rules.yaml` for state rules).
- `tests/test_normalizer.py` — `detect_row_kind`, `normalize_row` against synthetic dicts.
- `tests/test_lenovo_rules_unit.py`, `test_cisco_rules_unit.py`, `test_hpe_rules_unit.py`, `test_huawei_rules_unit.py`, `test_xfusion_rules_unit.py`.
- `tests/test_batch_audit.py` — `validate_row` E-code dispatch over crafted dicts; mocks OpenAI client.
- `tests/test_cluster_audit.py` — clustering helpers via synthetic xlsx in `tmp_path`.
- `tests/test_schema_validation.py` — YAML structural checks over every `rules/*_rules.yaml`.
- `tests/test_rules_traceability.py` — SHA-256 of rules file via `compute_file_hash`.
- `tests/test_dec_acceptance.py` — DEC P1–P8 acceptance cases by `option_id`.
- Vendor parser/normalizer units (`test_<vendor>_parser.py`, `test_<vendor>_normalizer.py`) — synthetic xlsx fixtures.
- `tests/test_can_parse_xfusion_huawei_disjoint.py` — disjointness assertion: an xfusion file should not be `can_parse` by huawei adapter and vice versa.

**Integration / pipeline tests** (need INPUT XLSX present):
- `tests/test_smoke.py` — full pipeline on `dl1..dl5.xlsx`; asserts every artifact (`rows_raw.json`, `rows_normalized.json`, `classification.jsonl`, `unknown_rows.csv`, `header_rows.csv`, `run_summary.json`) is created in a `tmp_path` run folder.
- `tests/test_regression*.py` — pipeline-vs-golden row-by-row comparison.
- `tests/test_unknown_threshold*.py` — runs pipeline; asserts `unknown_count / item_rows_count <= 0.05` (5%).
- `tests/test_output_structure.py` — verifies on-disk run-folder layout.
- `tests/test_cli.py` — end-to-end CLI smoke.
- `tests/test_branded_spec_writer.py`, `test_excel_writer.py`, `test_annotated_writer.py` — output-writer integration.

**No E2E browser / HTTP test layer** — there is no web frontend.

## Common Patterns

**Golden-file regression (the canonical pattern):**

```python
@pytest.mark.parametrize("filename", ["dl1.xlsx", "dl2.xlsx", "dl3.xlsx", "dl4.xlsx", "dl5.xlsx"])
def test_regression(filename):
    root = project_root()
    input_root = get_input_root_dell()
    input_path = input_root / filename
    if not input_path.exists():
        pytest.skip(f"Input not found: {input_path} (set paths.input_root in config.local.yaml)")
    rules_path = root / "rules" / "dell_rules.yaml"
    golden_path = root / "golden" / f"{Path(filename).stem}_expected.jsonl"
    if not golden_path.exists():
        pytest.skip(f"Golden file not found: {golden_path}. Run: python main.py --input <path> --save-golden")

    normalized, results = run_pipeline_in_memory("dell", input_path, rules_path)
    current = build_golden_rows(normalized, results)
    expected_rows = _load_golden(golden_path)

    if len(current) != len(expected_rows):
        pytest.fail(f"Row count mismatch: expected {len(expected_rows)}, got {len(current)}")

    all_diffs = []
    for i, (exp, act) in enumerate(zip(expected_rows, current)):
        diffs = _compare_row(exp, act, f"Row {i}")
        if diffs:
            all_diffs.append(f"Row {i} (source_row_index={act.get('source_row_index')}):")
            all_diffs.extend(diffs)
    if all_diffs:
        pytest.fail("Regression diff:\n" + "\n".join(all_diffs))
```
(`spec_classifier/tests/test_regression.py:36-67`)

Compared keys: `entity_type`, `state`, `matched_rule_id`, `device_type`, `hw_type`, `skus`. `source_row_index` is checked separately as a positional alignment guard.

**UNKNOWN-ratio gate:**
```python
UNKNOWN_RATIO_THRESHOLD = 0.05

@pytest.mark.parametrize("filename", ["dl1.xlsx", ...])
def test_unknown_ratio_below_threshold(filename):
    ...
    _, results = run_pipeline_in_memory("dell", input_path, rules_path)
    stats = collect_stats(results)
    ratio = stats["unknown_count"] / stats["item_rows_count"]
    assert ratio <= UNKNOWN_RATIO_THRESHOLD, (
        f"unknown_count / item_rows_count = {unknown_count}/{item_rows_count} "
        f"= {ratio:.4f} > {UNKNOWN_RATIO_THRESHOLD}"
    )
```
(`spec_classifier/tests/test_unknown_threshold.py:14-40`)

**Skip on missing input** is the universal idiom for tests that need real INPUT files:
```python
if not input_path.exists():
    pytest.skip(f"Input not found: {input_path} (set paths.input_root in config.local.yaml)")
```

**Schema validation idiom:**
```python
def test_all_rule_ids_are_well_formed(rules_data):
    """Every rule_id must be uppercase, dash-separated, contain a 3-digit number."""
    data, filepath = rules_data
    bad = []
    for section, rule in _collect_all_rules(data):
        rid = rule.get("rule_id", "")
        if not rid:
            continue
        if not re.match(r"^[A-Z0-9-]+$", rid):
            bad.append(f"{section}: '{rid}' contains invalid characters")
        if not re.search(r"\d{3}", rid):
            bad.append(f"{section}: '{rid}' missing 3-digit number")
        if "--" in rid:
            bad.append(f"{section}: '{rid}' has empty segment (--)")
    assert not bad, f"Malformed rule_ids in {filepath}:\n" + "\n".join(bad)
```
(`spec_classifier/tests/test_schema_validation.py:50-69`)

**Error-path idiom** (`pytest.raises`):
```python
def test_compute_file_hash_file_not_found():
    with pytest.raises((FileNotFoundError, OSError)):
        compute_file_hash("/nonexistent/path.yaml")
```
(`spec_classifier/tests/test_rules_traceability.py:21-23`)

## conftest Gates — Skip Guard

`spec_classifier/conftest.py:141-217` (`pytest_sessionfinish`) enforces a data-availability gate that hard-fails the session under three conditions:

1. **`MAX_SKIP_RATIO = 0.50`** (`conftest.py:14`). If `skipped / total > 0.50`, the session exits 1 with:
   ```
   ERROR: Skip guard triggered: skipped=N, total=M, passed=P, failed=F, threshold=0.50.
   Too many tests were skipped or no tests passed.
   Please provide input/*.xlsx or set paths.input_root.
   ```
2. **`passed == 0`** while `total > 0` and at least one test ran (i.e. not all deselected by `-k`) — same skip-guard error.
3. **Missing `input_root`** — if the resolved `input_root` does not exist on disk, *and* there were any skips or zero passes, the session fails with:
   ```
   ERROR: Skip guard triggered: input_root is missing: <path>.
   skipped=N, total=M, passed=P, failed=F, threshold=0.50.
   Restore input_root or point paths.input_root to the correct directory (config.local.yaml).
   ```

**Exemptions** (`conftest.py:144-161`):
- `--collect-only` mode never executes tests; `passed == 0` is not an error there.
- `passed + skipped + failed == 0` (e.g. `-k` filter matched nothing — all deselected) — also exempt.

**Silent-skip risk warning** (`conftest.py:165-187`): when `input_root` *does* exist but contains no vendor subdirectories with `*.xlsx` and no flat `*.xlsx`, a yellow `WARNING:` is printed but the session does not fail just for that — only the threshold / passed-zero rules trigger failure.

**Resolution precedence for `input_root`** (`conftest.py:_resolve_input_root_for_skip_guard`): `config.local.yaml` wins over `config.yaml`. Returns `None` only when config is malformed; in that case the gate keeps current behaviour.

**Practical implications:**
- Running pytest without any INPUT files will hard-fail (skipped > 50%).
- Running unit-only without INPUT requires explicit file targeting — either `make test-unit` (`Makefile:72-73`) or `pytest tests/test_rules_unit.py tests/test_state_detector.py tests/test_normalizer.py -v`. Both keep the skip ratio under 0.50 because the targeted set has no XLSX dependency.

## Coverage

- No coverage tool committed (no `coverage.py` config, no `pytest-cov` in `requirements.txt`).
- No coverage threshold enforced.
- "Coverage" is informally tracked in `spec_classifier/CLAUDE.md` § ТЕКУЩЕЕ СОСТОЯНИЕ as "420 tests collected (244 def-функций по 31 файлам)".

## Async Testing

- The codebase is fully synchronous. No `asyncio`, no `pytest-asyncio`. The OpenAI calls in `batch_audit.py` are synchronous SDK calls.

## Run Integration

`run.ps1` orchestration order (`run.ps1:71-152`):

1. `-TestsOnly` short-circuit → run only `python -m pytest tests/ -v --tb=short`, then exit with `$LASTEXITCODE`.
2. Otherwise:
   - For each vendor: `python main.py --batch-dir <INPUT/vendor> --vendor <vendor> --output-dir $OutputRoot`.
   - `python batch_audit.py --output-dir $OutputRoot --no-ai` (rule-only audit).
   - If not `-NoAi`: `python batch_audit.py --output-dir $OutputRoot --model gpt-4o-mini` (AI audit).
   - `python cluster_audit.py --output-dir $OutputRoot`.
   - Unless `-SkipTests`: `python -m pytest tests/ -v --tb=short`.
3. Each stage checks `$LASTEXITCODE`; non-zero aborts the chain.

**Smoke recipes:**

```powershell
.\run.ps1 -Vendor huawei -NoAi -SkipTests
# -> runs pipeline only for huawei (1 vendor, ~5 files), no AI audit, no pytest.

.\run.ps1 -TestsOnly
# -> only pytest tests/ -v --tb=short

.\run.ps1 -Vendor dell
# -> dell pipeline + rule audit + AI audit + cluster + pytest

pytest tests/test_rules_unit.py tests/test_state_detector.py tests/test_normalizer.py -v
# -> unit-only, no INPUT files needed; bypasses skip guard via narrow selection
```

**INPUT missing behaviour:**
- `run.ps1` skips the per-vendor pipeline stage with a yellow `=== Pipeline: $v - SKIP (no input dir at $vDir) ===` (`run.ps1:94-105`).
- `pytest` step still runs at the end. With no INPUT, regression / smoke / unknown-threshold tests skip; the conftest skip guard hard-fails the session if more than 50% of collected tests skipped.
- Therefore: a `run.ps1` invocation without INPUT files will end in pytest failure, even if the pipeline step short-circuited cleanly. This is by design — the skip guard refuses to silently green-light a run that exercised almost nothing.

*Testing analysis: 2026-05-09*
