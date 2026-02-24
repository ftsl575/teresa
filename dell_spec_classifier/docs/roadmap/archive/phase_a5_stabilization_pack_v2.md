# Phase A.5 Stabilization Implementation Pack

**Project:** Dell Specification Classifier  
**Baseline:** v1.1.0 (frozen)  
**Date:** 2026-02-24  
**Revision:** 2 (incorporated review feedback: helpers location, collect_stats confirmation, Phase B prerequisite)  
**Author:** Senior Technical Architect (automated)  
**Purpose:** Execution-ready plan for pre-Phase B stabilization

---

## 1. Refined Prioritization

| # | Weakness | Severity | Fix When | Type | Rationale |
|---|----------|----------|----------|------|-----------|
| 1 | Tests write to disk (`output/`) | **P0 — CRITICAL** | Phase A.5 PR1 | Structural | `test_unknown_threshold.py` calls `create_run_folder`, `save_rows_raw`, `save_rows_normalized`, `save_classification`, `save_unknown_rows`, `save_header_rows`, `save_run_summary` — 7 disk-writing calls per parametrized run × 5 datasets = 35 filesystem operations per `pytest` invocation. Blocks parallel CI, pollutes `output/`, creates inter-test coupling. Phase B adds fields to `run_summary.json` — every disk-writing test becomes another schema maintenance point. |
| 2 | Pipeline duplication in tests | **P1 — HIGH** | Phase A.5 PR1 (same PR) | Structural | `test_regression.py` and `test_unknown_threshold.py` each independently reconstruct `parse_excel → normalize_row → classify_row`. Phase B adds `resolve_hw_type` step. Without shared harness, the new step must be added in N places. Missing one = silent divergence. |
| 3 | No rules traceability | **P2 — MEDIUM** | Phase A.5 PR2 | Governance | `run_summary.json` has no record of which rules file produced it. Phase B adds `hw_type_map.yaml` — second untraced file. Pattern must exist before Phase B, not after. Fix cost: ~20 lines. |
| 4 | Unsafe `ClassificationResult` copying | **P3 — MEDIUM** | **⚠ MANDATORY Phase B Step 2 prerequisite** | Incidental | `_apply_device_type` manually constructs new `ClassificationResult`. Phase B adds `hw_type` field — if copy logic isn't updated, hw_type silently drops to `None` for all HW/LOGISTIC rows. Fix is trivial (`dataclasses.replace`), but has zero value until Phase B adds the field. **Not in Phase A.5 scope. MUST be the first commit of Phase B Step 2 — before hw_type is wired in.** |
| 5 | Golden file fragility | **P4 — LOW** | Defer (process only) | Structural | Golden files compare exact field values — correct granularity. Risk is in review process, not in code. Add review policy to docs in Phase A.5 PR3. No code change. |
| 6 | Rule ordering / shadowing | **P5 — LOW (immediate)** | Defer | Strategic | First-match semantics are correct for current rule count (~30 rules). Automated linter is high-effort. Add manual checklist to docs in Phase A.5 PR3. No code change. |

**Phase A.5 scope: PR1 + PR2 + PR3. Three PRs. No functional changes.**

---

## 2. PR Plan Overview

| PR | Title | Files Modified | Files Created | Risk | Depends On |
|----|-------|----------------|---------------|------|------------|
| **PR1** | Shared test harness + remove disk side effects | `tests/test_regression.py`, `tests/test_unknown_threshold.py` | `tests/__init__.py`, `tests/helpers.py` | Low (test infra only) | — |
| **PR2** | Rules file traceability in run_summary.json | `src/diagnostics/stats_collector.py`, `main.py` | `tests/test_rules_traceability.py` | Low (additive field) | — (independent of PR1) |
| **PR3** | Documentation: golden review policy + rule ordering warning | `README.md`, `docs/TECHNICAL_OVERVIEW.md` | — | None (docs only) | — (independent) |

All three PRs can be reviewed in parallel. Merge order recommendation: PR1 → PR2 → PR3.

---

## 2.1 Architectural Decision: Why `tests/helpers.py`, Not `conftest.py`

The original plan placed `run_pipeline_in_memory()` and `build_golden_rows()` in the root `conftest.py`. This was reconsidered for the following reasons:

**Problem with conftest.py:**
- pytest loads `conftest.py` at collection time for **every** test session.
- Adding top-level imports of `parse_excel`, `normalize_row`, `RuleSet`, `classify_row` into conftest.py pulls in `pandas`, `openpyxl`, `yaml` at collection.
- If any of these modules is temporarily broken during development, **all** tests fail to collect — including unit tests (`test_rules_unit.py`, `test_normalizer.py`, `test_state_detector.py`) that don't need the pipeline.
- `conftest.py` should contain pytest configuration and lightweight fixtures, not pipeline orchestration logic.

**Solution:**
- Create `tests/helpers.py` with the pipeline functions.
- Create `tests/__init__.py` (empty) to make `tests` a package, enabling `from tests.helpers import ...`.
- `conftest.py` at project root is **untouched** — it keeps only `project_root()`.
- Only test files that explicitly import from `tests.helpers` pull in the heavy dependencies. Unit tests are unaffected.

---

## 3. PR1 — Shared Test Harness + Remove Disk Side Effects

### 3.1 Goal

- Create `tests/helpers.py` with `run_pipeline_in_memory()` and `build_golden_rows()` — the single definition of the test pipeline.
- Eliminate all disk I/O from `test_unknown_threshold.py` (no `create_run_folder`, no `save_*` calls).
- Refactor `test_regression.py` to use the shared harness instead of its private `_run_pipeline_and_build_golden_rows`.
- Leave `conftest.py` completely untouched.

### 3.2 Files to Modify / Create

```
tests/__init__.py                    — CREATE (empty file, makes tests a package)
tests/helpers.py                     — CREATE: run_pipeline_in_memory(), build_golden_rows()
tests/test_regression.py             — MODIFY: remove private pipeline function, import from tests.helpers
tests/test_unknown_threshold.py      — MODIFY: remove all disk I/O, import from tests.helpers
conftest.py                          — NO CHANGE
```

### 3.3 Step-by-Step Implementation Instructions

#### Step A — Create `tests/__init__.py`

Create an empty file `tests/__init__.py`. This makes `tests` a Python package so that `from tests.helpers import ...` works from test files. The file can contain just a blank line or a comment:

```python
# Package marker for tests directory.
```

**If `tests/__init__.py` already exists** (not listed in TECHNICAL_OVERVIEW, but possible), leave it as is.

#### Step B — Create `tests/helpers.py`

Create a new file `tests/helpers.py` with two functions:

1. `run_pipeline_in_memory(input_path: Path, rules_path: Path) -> tuple[list, list]`
   - Imports (at top of file): `from pathlib import Path`, `from src.core.parser import parse_excel`, `from src.core.normalizer import normalize_row`, `from src.rules.rules_engine import RuleSet`, `from src.core.classifier import classify_row`
   - Body: `raw_rows = parse_excel(str(input_path))` → `normalized = [normalize_row(r) for r in raw_rows]` → `ruleset = RuleSet.load(str(rules_path))` → `results = [classify_row(r, ruleset) for r in normalized]` → `return (normalized, results)`
   - Docstring: `"""Run parse → normalize → classify in memory. Returns (normalized_rows, classification_results). No disk I/O."""`

2. `build_golden_rows(normalized_rows: list, classification_results: list) -> list[dict]`
   - No additional imports needed (uses only basic types)
   - Iterates `zip(normalized_rows, classification_results)`, builds list of dicts with keys:
     - `source_row_index`: `row.source_row_index`
     - `row_kind`: `result.row_kind.value`
     - `entity_type`: `result.entity_type.value if result.entity_type else None`
     - `state`: `result.state.value if result.state else None`
     - `matched_rule_id`: `result.matched_rule_id`
     - `device_type`: `getattr(result, "device_type", None)`
     - `skus`: `list(row.skus)`
   - Matches **exactly** the format in current `test_regression.py._run_pipeline_and_build_golden_rows` return value
   - Docstring: `"""Build golden-format dicts from pipeline results. Matches golden JSONL schema."""`

Module docstring: `"""Shared test helpers for pipeline execution. Imported by test_regression.py and test_unknown_threshold.py."""`

#### Step C — Modify `tests/test_regression.py`: use shared harness

**Remove** the private function `_run_pipeline_and_build_golden_rows` entirely (lines containing `def _run_pipeline_and_build_golden_rows` through the end of that function body — the entire function from current file).

**Replace** the import block at the top. Current:

```python
from src.core.parser import parse_excel
from src.core.normalizer import normalize_row
from src.rules.rules_engine import RuleSet

from conftest import project_root
```

New:

```python
from conftest import project_root
from tests.helpers import run_pipeline_in_memory, build_golden_rows
```

**Replace** the call inside `test_regression()`. Current line:

```python
current = _run_pipeline_and_build_golden_rows(input_path, rules_path)
```

New:

```python
normalized, results = run_pipeline_in_memory(input_path, rules_path)
current = build_golden_rows(normalized, results)
```

**Everything else** in the test file stays identical: `_load_golden`, `_compare_row`, parametrize decorator, all assertions, the `json` import, the `pytest` import.

#### Step D — Modify `tests/test_unknown_threshold.py`: remove all disk I/O

**Replace** the entire import block. Current:

```python
import json
import pytest
from pathlib import Path

from src.core.parser import parse_excel
from src.core.normalizer import normalize_row
from src.rules.rules_engine import RuleSet
from src.core.classifier import classify_row
from src.diagnostics.run_manager import create_run_folder
from src.outputs.json_writer import (
    save_rows_raw,
    save_rows_normalized,
    save_classification,
    save_unknown_rows,
    save_header_rows,
)
from src.diagnostics.stats_collector import collect_stats, save_run_summary

from conftest import project_root
```

New:

```python
import pytest
from pathlib import Path

from src.diagnostics.stats_collector import collect_stats

from conftest import project_root
from tests.helpers import run_pipeline_in_memory
```

Removed: `json`, `parse_excel`, `normalize_row`, `RuleSet`, `classify_row`, `create_run_folder`, `save_rows_raw`, `save_rows_normalized`, `save_classification`, `save_unknown_rows`, `save_header_rows`, `save_run_summary`.

**Replace** the entire test body of `test_unknown_ratio_below_threshold`. Current body:

```python
    root = project_root()
    input_path = root / "test_data" / filename
    if not input_path.exists():
        pytest.skip(f"test_data/{filename} not found at {input_path}")

    rules_path = root / "rules" / "dell_rules.yaml"
    assert rules_path.exists(), f"rules/dell_rules.yaml not found at {rules_path}"

    output_base = root / "output"
    rows_raw = parse_excel(str(input_path))
    rows_normalized = [normalize_row(r) for r in rows_raw]
    ruleset = RuleSet.load(str(rules_path))
    classification_results = [classify_row(r, ruleset) for r in rows_normalized]

    run_folder = create_run_folder(str(output_base), input_path.name)
    save_rows_raw(rows_raw, run_folder)
    save_rows_normalized(rows_normalized, run_folder)
    save_classification(classification_results, run_folder)
    save_unknown_rows(rows_normalized, classification_results, run_folder)
    save_header_rows(rows_normalized, run_folder)
    stats = collect_stats(classification_results)
    save_run_summary(stats, run_folder)

    summary_path = run_folder / "run_summary.json"
    assert summary_path.exists(), f"run_summary.json not found at {summary_path}"
    with open(summary_path, encoding="utf-8") as f:
        summary = json.load(f)

    unknown_count = summary.get("unknown_count", 0)
    item_rows_count = summary.get("item_rows_count", 0)
    if item_rows_count == 0:
        pytest.skip(f"item_rows_count is 0 for {filename}")

    ratio = unknown_count / item_rows_count
    assert ratio <= UNKNOWN_RATIO_THRESHOLD, (
        f"unknown_count / item_rows_count = {unknown_count}/{item_rows_count} = {ratio:.4f} > {UNKNOWN_RATIO_THRESHOLD}"
    )
```

New body:

```python
    root = project_root()
    input_path = root / "test_data" / filename
    if not input_path.exists():
        pytest.skip(f"test_data/{filename} not found at {input_path}")

    rules_path = root / "rules" / "dell_rules.yaml"
    assert rules_path.exists(), f"rules/dell_rules.yaml not found at {rules_path}"

    _, classification_results = run_pipeline_in_memory(input_path, rules_path)
    stats = collect_stats(classification_results)

    unknown_count = stats.get("unknown_count", 0)
    item_rows_count = stats.get("item_rows_count", 0)
    if item_rows_count == 0:
        pytest.skip(f"item_rows_count is 0 for {filename}")

    ratio = unknown_count / item_rows_count
    assert ratio <= UNKNOWN_RATIO_THRESHOLD, (
        f"unknown_count / item_rows_count = {unknown_count}/{item_rows_count} = {ratio:.4f} > {UNKNOWN_RATIO_THRESHOLD}"
    )
```

Key changes: no `output_base`, no `run_folder`, no `save_*` calls, no `json.load` from file, no `json` import.

### 3.4 Constraints (what must NOT change)

- **`conftest.py` completely untouched.** `project_root()` is its only content; it stays that way.
- **No golden files touched.** Zero changes to `golden/*.jsonl`.
- **No rule changes.** `rules/dell_rules.yaml` untouched.
- **No classification logic changes.** `classifier.py`, `rules_engine.py`, `normalizer.py`, `state_detector.py`, `parser.py` all untouched.
- **No changes to production pipeline.** `main.py`, `json_writer.py`, `run_manager.py`, `stats_collector.py`, `excel_writer.py`, `annotated_writer.py` all untouched.
- **Assertion logic identical.** Same thresholds, same field comparisons, same parametrization, same skip conditions.

### 3.5 Definition of Done

- [ ] `tests/__init__.py` exists (empty or minimal)
- [ ] `tests/helpers.py` exists with `run_pipeline_in_memory` and `build_golden_rows`
- [ ] `conftest.py` is **unmodified** (verify with `git diff conftest.py` — no changes)
- [ ] `test_regression.py` has no private pipeline function; uses `tests.helpers`
- [ ] `test_unknown_threshold.py` has no imports from `run_manager`, `json_writer`; has no `create_run_folder` or `save_*` calls; does not import `json`
- [ ] `pytest tests/ -v --tb=short` passes with same results as before (same pass/skip/fail counts)
- [ ] Running `pytest tests/test_unknown_threshold.py -v` does NOT create any new folders under `output/`
- [ ] No file outside `tests/` directory is modified

### 3.6 Verification Commands

```bash
cd dell_spec_classifier

# 0. Verify conftest.py is untouched
git diff conftest.py
# Expected: no output (no changes)

# 1. Record current output/ state
dir output /b > before.txt  # Windows
# ls output > before.txt    # Linux/Mac

# 2. Run all tests
pytest tests/ -v --tb=short

# 3. Verify output/ unchanged
dir output /b > after.txt
fc before.txt after.txt
# diff before.txt after.txt  # Linux/Mac
# Expected: no difference

# 4. Run threshold test specifically
pytest tests/test_unknown_threshold.py -v

# 5. Verify no new run folders
dir output /b > after2.txt
fc before.txt after2.txt
# Expected: no difference

# 6. Verify regression test still compares correctly
pytest tests/test_regression.py -v --tb=long

# 7. Verify helpers are importable
python -c "from tests.helpers import run_pipeline_in_memory, build_golden_rows; print('OK')"
```

### 3.7 Cursor Prompt

```
Context: Dell Specification Classifier project at dell_spec_classifier/.
Baseline v1.1.0 — all tests passing. We are doing Phase A.5 stabilization (no functional changes).

Task: PR1 — Shared test harness + remove disk side effects.

Problem:
- test_unknown_threshold.py creates real run folders under output/ and writes JSON/CSV/Excel files to disk on every test run. This is a side effect — the test only needs in-memory stats.
- test_regression.py has a private function _run_pipeline_and_build_golden_rows() that duplicates the pipeline. test_unknown_threshold.py also duplicates it independently.
- Both should share a single pipeline definition.

IMPORTANT: Do NOT put the pipeline functions in conftest.py. conftest.py is loaded globally by pytest — heavy imports (pandas, openpyxl) there would break unit test collection if any src module is temporarily broken. Use tests/helpers.py instead.

Solution — 4 files, in this order:

FILE 1: tests/__init__.py (CREATE — empty file)
Create an empty file tests/__init__.py to make tests a Python package. This enables "from tests.helpers import ..." in test files.
If tests/__init__.py already exists, skip this step.

FILE 2: tests/helpers.py (CREATE — new file)
Module docstring: "Shared test helpers for pipeline execution. Imported by test_regression.py and test_unknown_threshold.py."

Top-level imports:
  from pathlib import Path
  from src.core.parser import parse_excel
  from src.core.normalizer import normalize_row
  from src.rules.rules_engine import RuleSet
  from src.core.classifier import classify_row

Function 1: run_pipeline_in_memory(input_path: Path, rules_path: Path) -> tuple:
  Docstring: "Run parse → normalize → classify in memory. Returns (normalized_rows, classification_results). No disk I/O."
  Body:
    raw_rows = parse_excel(str(input_path))
    normalized = [normalize_row(r) for r in raw_rows]
    ruleset = RuleSet.load(str(rules_path))
    results = [classify_row(r, ruleset) for r in normalized]
    return (normalized, results)

Function 2: build_golden_rows(normalized_rows, classification_results) -> list[dict]:
  Docstring: "Build golden-format dicts from pipeline results. Matches golden JSONL schema."
  Body: iterate zip(normalized_rows, classification_results), for each pair build dict:
    source_row_index = row.source_row_index
    row_kind = result.row_kind.value
    entity_type = result.entity_type.value if result.entity_type else None
    state = result.state.value if result.state else None
    matched_rule_id = result.matched_rule_id
    device_type = getattr(result, "device_type", None)
    skus = list(row.skus)
  Return list of these dicts.

This MUST match EXACTLY the format from the current _run_pipeline_and_build_golden_rows function in test_regression.py.

FILE 3: tests/test_regression.py (MODIFY)
- DELETE the entire _run_pipeline_and_build_golden_rows function
- REPLACE the import block. Current:
    from src.core.parser import parse_excel
    from src.core.normalizer import normalize_row
    from src.rules.rules_engine import RuleSet
    from conftest import project_root
  New:
    from conftest import project_root
    from tests.helpers import run_pipeline_in_memory, build_golden_rows
- In test_regression function body, REPLACE:
    current = _run_pipeline_and_build_golden_rows(input_path, rules_path)
  WITH:
    normalized, results = run_pipeline_in_memory(input_path, rules_path)
    current = build_golden_rows(normalized, results)
- Keep _load_golden, _compare_row, parametrize decorator, and ALL assertions IDENTICAL

FILE 4: tests/test_unknown_threshold.py (MODIFY)
- REPLACE the entire import block. Remove ALL of these:
    import json
    from src.core.parser import parse_excel
    from src.core.normalizer import normalize_row
    from src.rules.rules_engine import RuleSet
    from src.core.classifier import classify_row
    from src.diagnostics.run_manager import create_run_folder
    from src.outputs.json_writer import (save_rows_raw, save_rows_normalized, save_classification, save_unknown_rows, save_header_rows)
    from src.diagnostics.stats_collector import collect_stats, save_run_summary
  New imports:
    import pytest
    from pathlib import Path
    from src.diagnostics.stats_collector import collect_stats
    from conftest import project_root
    from tests.helpers import run_pipeline_in_memory
- REPLACE the test body of test_unknown_ratio_below_threshold. Remove ALL lines related to: output_base, run_folder, create_run_folder, save_rows_raw, save_rows_normalized, save_classification, save_unknown_rows, save_header_rows, save_run_summary, summary_path, json.load.
  New body:
    root = project_root()
    input_path = root / "test_data" / filename
    if not input_path.exists():
        pytest.skip(f"test_data/{filename} not found at {input_path}")
    rules_path = root / "rules" / "dell_rules.yaml"
    assert rules_path.exists(), f"rules/dell_rules.yaml not found at {rules_path}"
    _, classification_results = run_pipeline_in_memory(input_path, rules_path)
    stats = collect_stats(classification_results)
    unknown_count = stats.get("unknown_count", 0)
    item_rows_count = stats.get("item_rows_count", 0)
    if item_rows_count == 0:
        pytest.skip(f"item_rows_count is 0 for {filename}")
    ratio = unknown_count / item_rows_count
    assert ratio <= UNKNOWN_RATIO_THRESHOLD, (
        f"unknown_count / item_rows_count = {unknown_count}/{item_rows_count} = {ratio:.4f} > {UNKNOWN_RATIO_THRESHOLD}"
    )

CONSTRAINTS:
- Do NOT modify conftest.py — it must remain untouched (only project_root)
- Do NOT modify any file outside tests/ directory
- Do NOT change any golden files
- Do NOT change any rules
- Do NOT change classifier.py, main.py, or any src/ file
- Assertion logic must be IDENTICAL — same fields compared, same thresholds
- UNKNOWN_RATIO_THRESHOLD constant stays at 0.05
- After changes, pytest tests/ -v must produce same pass/skip/fail counts
- After changes, running tests must NOT create any new folders under output/

Verify by running: pytest tests/ -v --tb=short
Then verify: git diff conftest.py shows no changes
```

---

## 4. PR2 — Rules File Traceability in run_summary.json

### 4.1 Goal

Add SHA-256 hash of `dell_rules.yaml` to `run_summary.json` so every run artifact is traceable to the exact rules that produced it. Design the utility to accept any file path so Phase B can reuse it for `hw_type_map.yaml`.

### 4.2 Public Interface Confirmation

**`collect_stats()` is NOT modified.** Its signature, logic, and return value are completely unchanged. The hash is computed by a new standalone utility function (`compute_file_hash`) and injected into the stats dict by the caller (`main.py`) at the orchestration layer. `collect_stats()` continues to return only classification-derived statistics. The hash is not a classification statistic — it's a provenance metadata field, and the orchestration layer (`main.py`) is the correct place to add it.

### 4.3 Files to Modify

```
src/diagnostics/stats_collector.py   — ADD: compute_file_hash() standalone function (does NOT change collect_stats or save_run_summary)
main.py                              — ADD: one line to inject hash into stats dict before save_run_summary
tests/test_rules_traceability.py     — CREATE: unit test verifying hash correctness
```

### 4.4 Step-by-Step Implementation Instructions

#### Step A — stats_collector.py: add compute_file_hash

**Add** at the top of the file, after existing imports, before `collect_stats`:

1. New import: `import hashlib`
2. New function: `compute_file_hash(filepath: str, algorithm: str = "sha256") -> str`
   - Opens the file in binary mode (`"rb"`)
   - Reads in 8192-byte chunks (to handle large files efficiently)
   - Returns hex digest string
   - Docstring: `"""Compute hex digest of a file. Default: SHA-256. Reusable for any file (rules, mapping, etc.)."""`

**Do NOT change** `collect_stats` or `save_run_summary`. Their signatures, logic, and return values stay identical. The hash is a provenance metadata field injected by the orchestration layer (main.py), not by the stats collection layer.

#### Step B — main.py: inject hash into stats before saving

**Location:** In `main.py`, after the line that calls `collect_stats(classification_results)` and before `save_run_summary(stats, run_folder)`.

**Add:**

```python
from src.diagnostics.stats_collector import compute_file_hash

# ... (after stats = collect_stats(classification_results))
stats["rules_file_hash"] = compute_file_hash(rules_path)
# ... (then save_run_summary(stats, run_folder))
```

Where `rules_path` is the resolved path to `dell_rules.yaml` that is already used to load the RuleSet.

**Important:** The exact variable name for the rules path in main.py may differ. Use whatever variable holds the resolved rules file path. Based on TECHNICAL_OVERVIEW.md section 2: config is loaded first, `rules_file` key gives the path, which is then resolved and passed to `RuleSet.load()`. Use the same resolved path string.

#### Step C — test: verify hash correctness

**Create** `tests/test_rules_traceability.py`:

1. Import `compute_file_hash` from `src.diagnostics.stats_collector`
2. Import `hashlib`, `Path`
3. Import `project_root` from `conftest`
4. Test function `test_compute_file_hash_matches_manual`:
   - Compute hash using `compute_file_hash(str(rules_path))`
   - Independently compute: `hashlib.sha256(rules_path.read_bytes()).hexdigest()`
   - Assert they are equal
   - Assert result is a 64-character hex string
5. Test function `test_compute_file_hash_file_not_found`:
   - Assert that calling with a nonexistent path raises `FileNotFoundError` (or `OSError`)

**This test does NOT require test_data xlsx files** — it only tests the hashing utility against `rules/dell_rules.yaml` (which is in git).

### 4.5 Constraints (what must NOT change)

- **`collect_stats()` signature, logic, and return value unchanged.** The hash is NOT computed inside `collect_stats` — it's injected by the caller at the orchestration layer.
- **`save_run_summary()` unchanged.** It writes whatever dict it receives.
- **No golden file changes.** Golden files contain classification.jsonl data, not run_summary fields.
- **No rule changes.**
- **No classification logic changes.**
- **Existing tests unaffected.** `test_unknown_threshold.py` reads `unknown_count` and `item_rows_count` from the stats dict — it does not validate the full schema. The new field is additive and invisible to existing tests.

### 4.6 Definition of Done

- [ ] `compute_file_hash` exists in `stats_collector.py` and is importable
- [ ] `collect_stats()` function is byte-for-byte unchanged (verify with `git diff`)
- [ ] `save_run_summary()` function is byte-for-byte unchanged
- [ ] `main.py` injects `rules_file_hash` into stats before calling `save_run_summary`
- [ ] Running `python main.py --input test_data/dl1.xlsx` produces `run_summary.json` containing `"rules_file_hash": "<64-char hex>"`
- [ ] `tests/test_rules_traceability.py` passes
- [ ] `pytest tests/ -v --tb=short` passes with no regressions
- [ ] The hash value is deterministic (same file = same hash on every run)

### 4.7 Verification Commands

```bash
cd dell_spec_classifier

# 1. Verify collect_stats and save_run_summary unchanged
git diff src/diagnostics/stats_collector.py
# Only additions should be: import hashlib, compute_file_hash function. No changes to collect_stats or save_run_summary.

# 2. Run new test
pytest tests/test_rules_traceability.py -v

# 3. Run full suite
pytest tests/ -v --tb=short

# 4. Run pipeline and check summary
python main.py --input test_data/dl1.xlsx
# Find latest run folder:
# dir output /b /od   (Windows)
# ls -t output        (Linux)
# Open run_summary.json, verify "rules_file_hash" key exists with 64-char hex value

# 5. Verify hash matches manual computation
python -c "import hashlib; print(hashlib.sha256(open('rules/dell_rules.yaml','rb').read()).hexdigest())"
# Compare with the value in run_summary.json — must match

# 6. Verify hash is stable
python -c "from src.diagnostics.stats_collector import compute_file_hash; print(compute_file_hash('rules/dell_rules.yaml'))"
python -c "from src.diagnostics.stats_collector import compute_file_hash; print(compute_file_hash('rules/dell_rules.yaml'))"
# Both outputs must be identical
```

### 4.8 Cursor Prompt

```
Context: Dell Specification Classifier project at dell_spec_classifier/.
Baseline v1.1.0 — all tests passing. Phase A.5 stabilization.

Task: PR2 — Add rules file hash (SHA-256) to run_summary.json for traceability.

Problem: run_summary.json does not record which rules file produced the run. Cannot trace artifacts to exact rules version.

CRITICAL: Do NOT modify collect_stats() or save_run_summary() functions. The hash is provenance metadata injected at the orchestration layer (main.py), not a classification statistic. collect_stats() must remain unchanged — same signature, same logic, same return value.

Solution — 3 files:

FILE 1: src/diagnostics/stats_collector.py
Add a new STANDALONE function (do NOT change collect_stats or save_run_summary):
- Add "import hashlib" at top of file alongside existing imports
- Add function compute_file_hash(filepath: str, algorithm: str = "sha256") -> str
  Docstring: "Compute hex digest of a file. Default: SHA-256. Reusable for any file (rules, mapping, etc.)."
  Body: open file in binary mode "rb", read in 8192-byte chunks, update hashlib digest, return hexdigest.
  h = hashlib.new(algorithm)
  with open(filepath, "rb") as f:
      while True:
          chunk = f.read(8192)
          if not chunk:
              break
          h.update(chunk)
  return h.hexdigest()
- This function is generic — accepts any filepath. Phase B will reuse it for hw_type_map.yaml.

FILE 2: main.py
After the line that calls collect_stats(classification_results) to get the stats dict, and BEFORE save_run_summary(stats, run_folder):
- Import compute_file_hash from src.diagnostics.stats_collector (at top of file with other imports)
- Add one line: stats["rules_file_hash"] = compute_file_hash(<the resolved rules file path variable>)
- Use whatever variable in main.py holds the resolved path to dell_rules.yaml (the same path used for RuleSet.load)

FILE 3: tests/test_rules_traceability.py (NEW FILE in tests/)
Create with two test functions:
1. test_compute_file_hash_matches_manual():
   - from src.diagnostics.stats_collector import compute_file_hash
   - from conftest import project_root
   - import hashlib
   - rules_path = project_root() / "rules" / "dell_rules.yaml"
   - computed = compute_file_hash(str(rules_path))
   - manual = hashlib.sha256(rules_path.read_bytes()).hexdigest()
   - assert computed == manual
   - assert len(computed) == 64
   - assert all(c in "0123456789abcdef" for c in computed)

2. test_compute_file_hash_file_not_found():
   - import pytest
   - with pytest.raises((FileNotFoundError, OSError)):
       compute_file_hash("/nonexistent/path.yaml")

CONSTRAINTS:
- Do NOT change collect_stats() — not the signature, not the body, not the return value
- Do NOT change save_run_summary() — not the signature, not the body
- Do NOT change any golden files
- Do NOT change any rules
- Do NOT change classifier.py or any other src/core/ file
- The new field is additive — existing tests must not break

Verify by running:
  git diff src/diagnostics/stats_collector.py  (only additions, no changes to existing functions)
  pytest tests/ -v --tb=short
  python main.py --input test_data/dl1.xlsx  (check run_summary.json for rules_file_hash)
```

---

## 5. PR3 — Documentation: Golden Review Policy + Rule Ordering Warning

### 5.1 Goal

Make implicit knowledge explicit. Add golden diff review policy and rule ordering warning to README.md and TECHNICAL_OVERVIEW.md. No code changes.

### 5.2 Files to Modify

```
README.md                    — UPDATE: Rules Change Process section
docs/TECHNICAL_OVERVIEW.md   — ADD: section 11 "Known Limitations and Risks"; FIX: missing device_type in golden format (section 5)
```

### 5.3 Step-by-Step Implementation Instructions

#### Step A — README.md: enhance Rules Change Process

Current section "Rules Change Process" has 7 steps. **Insert** between current step 5 and step 6 (renumber accordingly):

New step (becomes step 6):

> **Review golden diffs carefully:** When reviewing a PR that updates golden files, verify that: (a) only the intended rows changed; (b) only the intended fields changed; (c) the PR description lists the count of changed rows and the nature of changes. Do not approve golden updates without understanding every diff.

**Add** a new paragraph after the numbered list:

> **⚠ Rule ordering sensitivity:** Rules within each entity category use first-match semantics. When adding a new rule, verify that it does not shadow existing rules by running all 5 datasets (`dl1.xlsx` through `dl5.xlsx`) and confirming that golden diffs are limited to the intended rows. Inserting a rule above an existing rule with an overlapping regex pattern can silently change classification for previously-matched rows.

#### Step B — TECHNICAL_OVERVIEW.md: add Known Limitations section

**Add** at the end of the document, after section 10:

> ## 11. Known Limitations and Risks
>
> - **First-match rule sensitivity:** Entity classification and device_type assignment use first-match semantics within each rule category. Overlapping regex patterns between rules in the same category may cause shadowing: a rule placed earlier in the YAML will match instead of a more specific rule placed later. There is no automated overlap detection. Mitigation: when adding rules, run all 5 test datasets and inspect golden diffs before committing.
>
> - **Golden file coupling:** Golden files (`golden/*_expected.jsonl`) compare exact field values (entity_type, state, matched_rule_id, device_type, skus). Any change to normalization behavior (whitespace handling, SKU parsing order) or serialization will cause regression failures across all datasets. This is intentional — the golden files are the classification contract. However, it means that non-functional refactoring of the normalizer or parser requires golden regeneration and careful diff review.
>
> - **No automated rule overlap checker:** There is currently no lint or CI check to detect regex overlap between rules in the same category. This is deferred; at the current rule count (~30 rules), manual review during PR is sufficient. If the rule set grows significantly, an automated tool should be built.
>
> - **run_summary.json is schema-free:** There is no formal schema or validation for `run_summary.json`. Fields are added by `collect_stats()` and by `main.py`. Tests only assert on `unknown_count` and `item_rows_count`. Other fields could silently change type or disappear without test failure. Consider adding a schema test if the summary grows in scope.

#### Step C — Fix minor doc discrepancy in TECHNICAL_OVERVIEW.md section 5

Current golden format description in section 5 lists fields: `source_row_index`, `row_kind`, `entity_type`, `state`, `matched_rule_id`, `skus`. But the actual golden files (per test_regression.py) also include `device_type`.

**Add** `device_type` to the field list in section 5:

> - `device_type` (строка или null)

Insert after the `matched_rule_id` line and before the `skus` line.

### 5.4 Constraints

- **No code changes.** Only `.md` files.
- **No golden changes.**
- **No rule changes.**

### 5.5 Definition of Done

- [ ] README.md Rules Change Process includes golden diff review step and rule ordering warning
- [ ] TECHNICAL_OVERVIEW.md has section 11 with known limitations
- [ ] TECHNICAL_OVERVIEW.md section 5 golden format includes `device_type`
- [ ] No code files modified

### 5.6 Verification Commands

```bash
# Verify no code changes
git diff --name-only
# Should show only: README.md, docs/TECHNICAL_OVERVIEW.md

# Verify tests still pass (nothing should change)
pytest tests/ -v --tb=short
```

### 5.7 Cursor Prompt

```
Context: Dell Specification Classifier project at dell_spec_classifier/.
Baseline v1.1.0. Phase A.5 stabilization — documentation PR.

Task: PR3 — Add golden review policy, rule ordering warning, and known limitations to docs.

No code changes. Only markdown files.

FILE 1: README.md
In the "Rules Change Process" section, AFTER step 5 ("Update golden if the change is intentional...") and BEFORE step 6 ("Run the full test suite..."):

Add a new step 6 (renumber the rest):
"6. **Review golden diffs carefully:** When reviewing a PR that updates golden files, verify that: (a) only the intended rows changed; (b) only the intended fields changed; (c) the PR description lists the count of changed rows and the nature of changes. Do not approve golden updates without understanding every diff."

Then AFTER the numbered list, add a warning paragraph:
"**⚠ Rule ordering sensitivity:** Rules within each entity category use first-match semantics. When adding a new rule, verify that it does not shadow existing rules by running all 5 datasets (dl1.xlsx through dl5.xlsx) and confirming that golden diffs are limited to the intended rows. Inserting a rule above an existing rule with an overlapping regex pattern can silently change classification for previously-matched rows."

FILE 2: docs/TECHNICAL_OVERVIEW.md
Two changes:

1. In section 5 "Golden / Regression", in the golden format field list, add after matched_rule_id and before skus:
   "- `device_type` (строка или null)"

2. Add new section 11 at the end of the document:
"## 11. Known Limitations and Risks

- **First-match rule sensitivity:** Entity classification and device_type assignment use first-match semantics within each rule category. Overlapping regex patterns between rules in the same category may cause shadowing: a rule placed earlier in the YAML will match instead of a more specific rule placed later. There is no automated overlap detection. Mitigation: when adding rules, run all 5 test datasets and inspect golden diffs before committing.

- **Golden file coupling:** Golden files (golden/*_expected.jsonl) compare exact field values (entity_type, state, matched_rule_id, device_type, skus). Any change to normalization behavior (whitespace handling, SKU parsing order) or serialization will cause regression failures across all datasets. This is intentional — the golden files are the classification contract. However, it means that non-functional refactoring of the normalizer or parser requires golden regeneration and careful diff review.

- **No automated rule overlap checker:** There is currently no lint or CI check to detect regex overlap between rules in the same category. This is deferred; at the current rule count (~30 rules), manual review during PR is sufficient. If the rule set grows significantly, an automated tool should be built.

- **run_summary.json is schema-free:** There is no formal schema or validation for run_summary.json. Fields are added by collect_stats() and by main.py. Tests only assert on unknown_count and item_rows_count. Other fields could silently change type or disappear without test failure. Consider adding a schema test if the summary grows in scope."

CONSTRAINTS:
- Only modify README.md and docs/TECHNICAL_OVERVIEW.md
- No code changes
- No golden changes
- No rule changes
- Keep existing content intact — only add new content
```

---

## 6. Post-Merge Checklist

After all three PRs are merged:

```
[ ] pytest tests/ -v --tb=short — all pass, same counts as before
[ ] Running tests creates NO new folders under output/
[ ] conftest.py is unmodified (git diff conftest.py — no changes)
[ ] python main.py --input test_data/dl1.xlsx produces run_summary.json with rules_file_hash
[ ] README.md has golden review policy and rule ordering warning
[ ] TECHNICAL_OVERVIEW.md has section 11 and device_type in golden format
[ ] git tag v1.1.1 on main (stabilized baseline)
[ ] Begin Phase B Step 1
```

---

## 7. What Is Explicitly NOT In Scope

| Item | Reason | When | Status |
|------|--------|------|--------|
| `dataclasses.replace` for ClassificationResult | No value until Phase B adds hw_type field | **⚠ MANDATORY first commit of Phase B Step 2** | Deferred — MUST be done before hw_type wiring |
| Rule overlap linter | High effort, low immediate risk at ~30 rules | Post-Phase B | Deferred |
| run_summary.json schema validation test | Low urgency; manual inspection sufficient for now | Phase B Step 3 (alongside hw_type_counts) | Deferred |
| Golden tolerance / fuzzy matching | Exact matching is the correct contract | Not planned | Rejected |

---

## 8. Phase B Prerequisite Gate

**Before any Phase B code is written, the following must be true:**

1. **Phase A.5 is fully merged** — all three PRs landed, v1.1.1 tagged.
2. **ClassificationResult copying fix is explicitly in Phase B Step 2 scope** — the first commit of Phase B Step 2 must replace manual field copying in `_apply_device_type` with `dataclasses.replace()` (or equivalent). This is a **blocking prerequisite** — hw_type field addition MUST NOT proceed until this fix is in place.
3. **Rationale:** `_apply_device_type` in `classifier.py` (lines building new `ClassificationResult`) manually copies each field. Phase B adds `hw_type` as a new field. If the copy logic isn't updated first, `hw_type` will silently be set to `None` (the default) for every HW/LOGISTIC row passing through device_type resolution — which is every such row. This bug would pass all existing tests and only be caught (if at all) when golden files are regenerated, at which point the wrong values would be baked into the new golden files.

**The Phase B Step 2 Cursor prompt must begin with:**

> "PREREQUISITE: Before adding hw_type, replace manual ClassificationResult construction in _apply_device_type with dataclasses.replace(result, device_type=match["device_type"]). This prevents silent field loss when new fields are added. Verify with: add a temporary field to ClassificationResult, confirm it survives _apply_device_type."

---

*End of Phase A.5 Stabilization Implementation Pack — Revision 2*
