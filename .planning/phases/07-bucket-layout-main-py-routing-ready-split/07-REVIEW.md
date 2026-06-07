---
phase: 07-bucket-layout-main-py-routing-ready-split
reviewed: 2026-06-07T00:00:00Z
depth: standard
files_reviewed: 6
files_reviewed_list:
  - spec_classifier/main.py
  - spec_classifier/src/diagnostics/run_manager.py
  - spec_classifier/src/vendors/cisco/adapter.py
  - spec_classifier/tests/test_cli.py
  - spec_classifier/tests/test_output_structure.py
  - spec_classifier/tests/test_smoke.py
findings:
  critical: 1
  warning: 3
  info: 2
  total: 6
status: issues_found
---

# Phase 07: Code Review Report

**Reviewed:** 2026-06-07
**Depth:** standard
**Files Reviewed:** 6
**Status:** issues_found

## Summary

This phase reroutes pipeline output from a timestamp-folder scheme to a three-bucket
`<bucket>/<vendor>/<spec>/` layout. The routing logic in `main.py` and `run_manager.py` is
correct at the happy-path level: SPLIT artifacts land under `SPLIT/<vendor>/<spec>/`, branded
output lands under `READY/<vendor>/<spec>/`, and the AUDIT bucket is untouched (D-05 satisfied).
The `source_filename=input_path.name` call in `generate_branded_spec` is intact (D-07 satisfied).
`CiscoAdapter.generates_branded_spec()` returning `False` is correct per the base-class contract.

One security-class finding is present: `shutil.rmtree` is called on a path whose `spec`
component is derived from an untrusted input filename stem, with no boundary check. Three
warnings cover an always-created-but-sometimes-empty READY directory, a test that does not
exercise the production call path for `save_classification`, and a logically-weak assertion
in the Cisco no-branded test. Two info items cover a stale docstring and a vacuously-true
size assertion.

---

## Critical Issues

### CR-01: `shutil.rmtree` on a path derived from unsanitized user input (`input_path.stem`)

**File:** `spec_classifier/src/diagnostics/run_manager.py:28-31`

**Issue:** `create_spec_folder` constructs its target as `Path(output_root) / bucket / vendor /
spec`. The `bucket` and `vendor` arguments come from hard-coded literals (`"SPLIT"`, `"READY"`)
and `VENDOR_REGISTRY` keys (controlled), but `spec` is `input_path.stem` — the filename stem of
the user-supplied Excel file. `pathlib.Path` performs no sanitisation: a file named
`../../critical_folder.xlsx` would produce a stem of `../../critical_folder`, and the resulting
path after `Path` division escapes the intended output tree. `shutil.rmtree` is then called on
that escaped path, silently destroying data outside `output_root`.

The risk is real on Windows too: `Path("C:/OUTPUT/SPLIT/dell") / "../../important"` resolves
to `C:/OUTPUT/important` — outside the bucket.

**Fix:**
```python
import re

_SAFE_STEM = re.compile(r'^[\w\- ]+$')   # allow word chars, hyphens, spaces

def create_spec_folder(output_root: Path, bucket: str, vendor: str, spec: str) -> Path:
    if not _SAFE_STEM.match(spec):
        raise ValueError(
            f"Unsafe spec stem {spec!r}: must contain only word characters, hyphens, and spaces."
        )
    folder = Path(output_root) / bucket / vendor / spec
    # Additional belt-and-suspenders: verify folder is still inside output_root
    try:
        folder.resolve().relative_to(Path(output_root).resolve())
    except ValueError:
        raise ValueError(f"Resolved spec folder {folder} escapes output_root {output_root}")
    if folder.exists():
        shutil.rmtree(folder)
    folder.mkdir(parents=True)
    return folder
```

---

## Warnings

### WR-01: `READY/<vendor>/<spec>/` directory always created, even for vendors that produce no branded output

**File:** `spec_classifier/main.py:127-128`

**Issue:** `create_spec_folder` is called unconditionally for both `"SPLIT"` and `"READY"` at
the top of `_run_single`, before `adapter.generates_branded_spec()` is consulted (line 175).
For Cisco (and any future vendor where `generates_branded_spec()` returns `False`), the READY
directory is created, wiped if pre-existing, and then left empty. This means:

1. Every Cisco run silently wipes and re-creates an empty `READY/cisco/<stem>/` directory.
2. Consumers that glob `READY/` to find delivered workbooks will encounter empty vendor
   subdirectories, which is misleading.
3. If a previous run placed a valid branded workbook in that READY path (e.g., from a Dell
   run that shared the same stem), it is destroyed.

**Fix:** Gate the `ready_folder` creation on `adapter.generates_branded_spec()`:
```python
split_folder = create_spec_folder(output_dir, "SPLIT", vendor, input_path.stem)
ready_folder = (
    create_spec_folder(output_dir, "READY", vendor, input_path.stem)
    if adapter.generates_branded_spec()
    else None
)
```
And guard the `branded_path` block accordingly (it already has the `if adapter.generates_branded_spec()` guard at line 175, so only the early creation needs to move).

---

### WR-02: `test_smoke.py` exercises the old two-argument `save_classification` path; the three-argument production path is untested

**File:** `spec_classifier/tests/test_smoke.py:52`

**Issue:** The smoke test calls:
```python
save_classification(classification_results, run_folder)
```
This triggers the backward-compatibility branch in `json_writer.save_classification` that sets
`source_row_index = None` for every row. The three-argument call used by `main.py` —
`save_classification(results, normalized_rows, run_folder)` — is not exercised by any test in
the reviewed set. A regression that breaks the three-argument path (e.g., a length mismatch
between `results` and `normalized_rows`) would not be caught here.

The smoke test also does not assert on the content of `classification.jsonl`, so even the
backward-compat branch is only tested for file existence.

**Fix:** Update the smoke test to use the three-argument call:
```python
save_classification(classification_results, rows_normalized, run_folder)
```
And add a content assertion, for example:
```python
with open(run_folder / "classification.jsonl") as f:
    lines = f.readlines()
assert len(lines) == len(rows_normalized), "One JSONL line per normalized row"
import json
first = json.loads(lines[0])
assert "source_row_index" in first and first["source_row_index"] is not None
```

---

### WR-03: Cisco "no branded file" assertion in `test_output_structure.py` passes vacuously when the READY directory does not exist

**File:** `spec_classifier/tests/test_output_structure.py:114-116`

**Issue:**
```python
assert not (output_root / "READY" / "cisco" / stem).is_dir() or \
    not any((output_root / "READY" / "cisco" / stem).iterdir()), \
    "Cisco must not produce a branded file in READY"
```
The `or` operator short-circuits: when `(... / stem).is_dir()` is `False` (directory does not
exist), the entire expression is `True` and the assertion passes without ever calling
`.iterdir()`. If the production code were changed to stop creating the READY directory for
Cisco, this test would continue to pass — providing no assurance that a branded file is absent.

Additionally, even if the READY directory is created and empty (current production behaviour),
the test also passes. The test only catches the case where the directory exists *and* contains
at least one file — which is the correct intent, but the assertion structure makes it hard to
reason about.

**Fix:** Make the two conditions explicit and independent:
```python
ready_dir = output_root / "READY" / "cisco" / stem
if ready_dir.is_dir():
    branded_files = [
        f for f in ready_dir.iterdir()
        if f.suffix == ".xlsx" and "предложение" in f.name
    ]
    assert not branded_files, \
        f"Cisco must not produce a branded file in READY; found: {branded_files}"
```

---

## Info

### IN-01: Module docstring in `main.py` lists only three of six registered vendors

**File:** `spec_classifier/main.py:3`

**Issue:** `"""Spec Classifier — multivendor CLI entry point (Dell, Cisco CCW, HPE)."""`
Lenovo, Huawei, and xFusion adapters are imported and registered in `VENDOR_REGISTRY` (lines
33-44) but are absent from the module docstring. The `argparse` description at line 234 has
the same stale list. A developer reading the module header will not know the full vendor set.

**Fix:**
```python
"""
Spec Classifier — multivendor CLI entry point
(Dell, Cisco CCW, HPE, Lenovo DCSC, Huawei, xFusion).
Pipeline: Excel → parse → normalize → classify → artifacts + cleaned spec.
"""
```
Update the `argparse` description at line 234 to match.

---

### IN-02: `test_smoke.py` size assertion is vacuously true — `st_size >= 0` is always satisfied

**File:** `spec_classifier/tests/test_smoke.py:68`

**Issue:**
```python
assert path.stat().st_size >= 0, f"File {name} should be readable"
```
`st_size` is always non-negative; this assertion can never fail. An empty artifact file
(zero bytes) passes silently. The intent was almost certainly `> 0`.

**Fix:**
```python
assert path.stat().st_size > 0, f"File {name} is empty — expected non-empty artifact"
```

---

_Reviewed: 2026-06-07_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
