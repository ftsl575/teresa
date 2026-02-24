# Phase B Step 2 Preparation Pack — Safe ClassificationResult Copying

**Project:** Dell Specification Classifier  
**Baseline:** v1.1.1 (Phase A.5 complete, stabilized)  
**Date:** 2026-02-24  
**Revision:** 1  
**Author:** Senior Technical Architect (automated)  
**Purpose:** Execution-ready plan for Phase B Step 2 prerequisite — replace manual ClassificationResult construction with `dataclasses.replace`

---

## 1. Overview / Motivation

### 1.1 Problem

In `src/core/classifier.py`, the function `_apply_device_type` constructs a new `ClassificationResult` by manually copying every field:

```python
return ClassificationResult(
    row_kind=result.row_kind,
    entity_type=result.entity_type,
    state=result.state,
    matched_rule_id=result.matched_rule_id,
    device_type=match["device_type"],
    warnings=result.warnings,
)
```

This is a **field-enumeration pattern** — it explicitly lists every field of the dataclass. When a new field is added (e.g. `hw_type` in Phase B Step 2), this constructor does not include it, so the new field silently falls back to its default value (`None`). The result: every row that passes through device_type resolution loses `hw_type`, and this loss is invisible to existing tests.

### 1.2 Why Now

Phase B Step 2 adds `hw_type` as a new field on `ClassificationResult`. If `_apply_device_type` is not fixed **before** `hw_type` is wired in, the following failure mode occurs:

1. `classify_row` sets `hw_type` correctly on each result.
2. `_apply_device_type` rebuilds `ClassificationResult` without `hw_type`.
3. `hw_type` silently resets to `None` for every HW/LOGISTIC row with a device_type match.
4. All existing tests pass (they don't check `hw_type`).
5. Golden files are regenerated with the wrong `None` values baked in.
6. The bug is invisible until production data review.

This fix is the **mandatory first commit** of Phase B Step 2 — it must land before `hw_type` is added to the dataclass.

### 1.3 Solution

Replace the manual field-enumeration constructor with `dataclasses.replace`:

```python
return replace(result, device_type=match["device_type"])
```

`dataclasses.replace` shallow-copies all fields of the source instance and overrides only the fields specified as keyword arguments. Any field added in the future (e.g. `hw_type`) is automatically preserved.

### 1.4 Risk Assessment

**Risk: None.** `dataclasses.replace` is a stdlib function (Python 3.7+). `ClassificationResult` is already a `@dataclass`. The replacement is a 1:1 behavioral equivalent for the current field set. No new fields, no new behavior, no output changes.

---

## 2. Scope

| Item | In Scope | Rationale |
|------|----------|-----------|
| Replace manual `ClassificationResult(...)` in `_apply_device_type` | ✅ | Core fix |
| Add `from dataclasses import replace` import | ✅ | Required by fix |
| Everything else | ❌ | Out of scope |

**This is a single-function, single-file change.**

---

## 3. Files to Modify

```
src/core/classifier.py   — MODIFY: add import, replace manual constructor in _apply_device_type
```

No files created. No files deleted. No other files modified.

### 3.1 What Must NOT Change

- **No other functions in classifier.py.** Only `_apply_device_type` is touched.
- **No new fields added.** `ClassificationResult` definition is untouched.
- **No golden files.** Zero changes to `golden/*.jsonl`.
- **No rule changes.** `rules/dell_rules.yaml` untouched.
- **No test changes.** All test files untouched.
- **No main.py changes.**
- **No other src/ files.** `normalizer.py`, `parser.py`, `state_detector.py`, `rules_engine.py`, `stats_collector.py`, `json_writer.py`, `run_manager.py`, `excel_writer.py`, `annotated_writer.py` all untouched.
- **No conftest.py changes.**
- **No tests/helpers.py changes.**

---

## 4. Step-by-Step Implementation Instructions

### Step A — Add `replace` import to `src/core/classifier.py`

At the top of the file, locate the existing `dataclasses` import. There should already be a `from dataclasses import dataclass` or `from dataclasses import dataclass, field` line (since `ClassificationResult` is a `@dataclass`).

**Modify** the existing dataclasses import to include `replace`:

If current is:
```python
from dataclasses import dataclass
```

Change to:
```python
from dataclasses import dataclass, replace
```

If current is:
```python
from dataclasses import dataclass, field
```

Change to:
```python
from dataclasses import dataclass, field, replace
```

If `dataclasses` is imported differently (e.g. `import dataclasses`), add `replace` as a separate import:
```python
from dataclasses import replace
```

**Do NOT** add a new `import dataclasses` line if `dataclass` is already imported via `from dataclasses import ...`.

### Step B — Replace manual constructor in `_apply_device_type`

**Locate** the `_apply_device_type` function. Find the `return ClassificationResult(...)` block that manually copies all fields.

**Current code** (the return statement inside the match branch):

```python
return ClassificationResult(
    row_kind=result.row_kind,
    entity_type=result.entity_type,
    state=result.state,
    matched_rule_id=result.matched_rule_id,
    device_type=match["device_type"],
    warnings=result.warnings,
)
```

**Replace with:**

```python
return replace(result, device_type=match["device_type"])
```

**Keep everything else in `_apply_device_type` identical:**
- All guard clauses (early returns, None checks) unchanged.
- The match lookup logic unchanged.
- The fallback `return result` (if no match) unchanged.
- Function signature unchanged.
- Docstring unchanged.

---

## 5. Constraints

| Constraint | Rationale |
|------------|-----------|
| No new fields added to `ClassificationResult` | This PR is purely mechanical — field additions come in the next commit |
| No behavioral changes | `dataclasses.replace` is a drop-in equivalent for the current field set |
| No golden regeneration | Output is bit-identical; no golden diffs expected |
| No refactoring outside `_apply_device_type` | Scope is one function only |
| One atomic PR | Single commit, single review, fast merge |
| All existing tests must pass with zero changes | No test modifications allowed — tests validate behavioral equivalence |

---

## 6. Definition of Done

- [ ] `src/core/classifier.py` imports `replace` from `dataclasses`
- [ ] `_apply_device_type` uses `replace(result, device_type=match["device_type"])` instead of manual `ClassificationResult(...)` constructor
- [ ] No other functions in `classifier.py` are modified
- [ ] No other files are modified (verify with `git diff --name-only` — must show only `src/core/classifier.py`)
- [ ] `pytest tests/ -v --tb=short` passes with identical results (same pass/skip/fail counts as v1.1.1)
- [ ] `pytest tests/test_regression.py -v --tb=long` passes — golden comparison unchanged
- [ ] `python main.py --input test_data/dl1.xlsx` produces identical output to v1.1.1 baseline

---

## 7. Verification

### 7.1 Verification Commands

```bash
cd dell_spec_classifier

# 1. Verify only classifier.py changed
git diff --name-only
# Expected output: src/core/classifier.py (and nothing else)

# 2. Verify the diff is minimal
git diff src/core/classifier.py
# Expected: one import line changed, one return block replaced (~8 lines removed, ~1 line added)

# 3. Run full test suite
pytest tests/ -v --tb=short
# Expected: identical pass/skip/fail counts as v1.1.1

# 4. Run regression tests specifically (golden comparison)
pytest tests/test_regression.py -v --tb=long
# Expected: all pass, no golden diffs

# 5. Run threshold tests specifically
pytest tests/test_unknown_threshold.py -v
# Expected: all pass, identical ratios

# 6. Run production pipeline and compare output
python main.py --input test_data/dl1.xlsx
# Expected: run_summary.json contents identical to v1.1.1 baseline run
```

### 7.2 Manual Smoke Test (Optional — Recommended)

To confirm `replace` correctly preserves all fields, temporarily add a verification in a Python shell:

```python
from dataclasses import replace
from src.core.classifier import ClassificationResult

# Create a result with all fields populated
# (use actual enum values from the codebase)
# Call replace with only device_type changed
# Assert all other fields are preserved
```

This is an optional confidence check — the existing test suite already validates behavioral equivalence.

---

## 8. Cursor Prompt

```
Context: Dell Specification Classifier project at dell_spec_classifier/.
Baseline v1.1.1 — Phase A.5 complete, all tests passing.
This is the mandatory first commit of Phase B Step 2.

Task: Replace manual ClassificationResult construction in _apply_device_type
with dataclasses.replace. Behavior must remain identical. No new fields added yet.

PREREQUISITE: Before adding hw_type (which comes in the NEXT commit),
replace manual ClassificationResult construction in _apply_device_type with
dataclasses.replace(result, device_type=match["device_type"]).
This prevents silent field loss when new fields are added.

FILE: src/core/classifier.py (MODIFY — the ONLY file to change)

CHANGE 1 — Import:
Find the existing "from dataclasses import ..." line at the top of the file.
Add "replace" to the import list.
For example, if it currently says:
  from dataclasses import dataclass
Change it to:
  from dataclasses import dataclass, replace
If it says "from dataclasses import dataclass, field", change to:
  from dataclasses import dataclass, field, replace
Do NOT add a duplicate dataclasses import line.

CHANGE 2 — Function _apply_device_type:
Find the return statement that manually constructs a new ClassificationResult
by copying every field from result. It looks like this:

  return ClassificationResult(
      row_kind=result.row_kind,
      entity_type=result.entity_type,
      state=result.state,
      matched_rule_id=result.matched_rule_id,
      device_type=match["device_type"],
      warnings=result.warnings,
  )

Replace that entire return statement with:

  return replace(result, device_type=match["device_type"])

Do NOT change anything else in the function:
- All guard clauses and early returns stay identical
- The match lookup logic stays identical
- The fallback "return result" (when no match found) stays identical
- The function signature stays identical
- The docstring stays identical

CONSTRAINTS:
- ONLY modify src/core/classifier.py — no other files
- Do NOT modify any other function in classifier.py
- Do NOT add any new fields to ClassificationResult
- Do NOT modify any test files
- Do NOT modify any golden files
- Do NOT modify main.py, conftest.py, or any other src/ file
- Do NOT regenerate golden files
- The change must be purely mechanical — identical behavior

VERIFY:
1. git diff --name-only → must show ONLY src/core/classifier.py
2. pytest tests/ -v --tb=short → all tests pass, same counts as before
3. pytest tests/test_regression.py -v --tb=long → golden comparison unchanged
```

---

## 9. What Comes Next

After this PR is merged, Phase B Step 2 proceeds with:

1. Add `hw_type: Optional[str] = None` field to `ClassificationResult`
2. Wire `hw_type` resolution logic
3. Regenerate golden files with `hw_type` values

Because `_apply_device_type` now uses `dataclasses.replace`, the new `hw_type` field will be automatically preserved through device_type resolution — no further changes needed in this function.

---

*End of Phase B Step 2 Preparation Pack — Revision 1*
