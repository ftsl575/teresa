# Phase 9: Output manifest & full-suite verification - Pattern Map

**Mapped:** 2026-06-07
**Files analyzed:** 7 new/modified files
**Analogs found:** 7 / 7

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `spec_classifier/src/diagnostics/run_manager.py` (add `write_manifest` + `detect_vendor_from_path`) | utility | file-I/O + transform | `run_manager.py` itself (`create_spec_folder`, lines 12-40) | exact (same module, same helper style) |
| `spec_classifier/main.py` (add `write_manifest` call) | controller | request-response | `main.py` lines 277-342 (`output_dir` resolution + dispatch) | exact (same function, same call site pattern) |
| `spec_classifier/batch_audit.py` (delete local `detect_vendor_from_path`, import shared) | utility | transform | `batch_audit.py` lines 1357-1366 (the function being deleted) | exact (import swap pattern from `main.py:18`) |
| `spec_classifier/cluster_audit.py` (delete `_detect_vendor_from_path`, import shared, update caller) | utility | transform | `cluster_audit.py` lines 97-117 (the function being deleted); caller at line 195 | exact (same import swap + caller update) |
| `spec_classifier/tests/test_output_structure.py` (extend with layout + manifest assertions) | test | request-response | `test_output_structure.py` lines 33-74 (`test_output_tree_shape_dell_run` pattern) | exact (same subprocess + assert pattern) |
| `spec_classifier/tests/test_batch_audit.py` (remove `TestDetectVendorFromPath`, redirect import) | test | transform | `test_batch_audit.py` lines 438-468 (class being removed/replaced) | exact (same pytest class pattern, inverted — deletion) |
| `spec_classifier/tests/test_run_manager.py` (new — consolidated detect-vendor suite) | test | transform | `test_batch_audit.py` `TestDetectVendorFromPath` (lines 438-468) | role-match (same test class and assertion style, re-targeted to `run_manager`) |

---

## Pattern Assignments

### `run_manager.py` — add `write_manifest(output_root)` helper

**Analog:** `run_manager.py` lines 1-40 (existing `create_spec_folder`)

**Module header and imports pattern** (lines 1-9 — extend, do not replace):
```python
"""
Run folder management: create and prepare per-spec output directories.

Naming convention:
  Spec folder: <output_root>/<bucket>/<vendor>/<spec>/  (e.g. SPLIT/dell/dl1/)
"""

import shutil
from pathlib import Path
```
Add `import sys` to the import block (required for the WARN print in `detect_vendor_from_path`).

**Core helper pattern** (lines 12-40 — `create_spec_folder` as structural model):
```python
def create_spec_folder(output_root: Path, bucket: str, vendor: str, spec: str) -> Path:
    """
    Create (or wipe-and-recreate) <output_root>/<bucket>/<vendor>/<spec>/.
    ...
    """
    output_root = Path(output_root)
    folder = output_root / bucket / vendor / spec
    ...
    folder.mkdir(parents=True)
    return folder
```
`write_manifest` follows the same shape: accept `output_root: Path`, coerce with `Path(output_root)`, write `output_root / "README.md"` with the static table bytes, return nothing (or the written path). No config access. No dynamic scan.

**New function to add — `detect_vendor_from_path`** (extracted from `batch_audit.py:1357-1366`, signature made strict per D-11):
```python
def detect_vendor_from_path(path: Path, known_vendors: list[str]) -> str:
    """Detect vendor from path components using known vendor list."""
    s = str(path).lower()
    for vendor in known_vendors:
        if f"/{vendor}/" in s or f"\\{vendor}\\" in s:
            return vendor
    print(f"  [WARN] Cannot detect vendor from path: {path}", file=sys.stderr)
    return "unknown"
```
Key delta from `batch_audit` original: `known_vendors` is **required** (no `| None = None` default, no `_get_known_vendors` call inside). `sys` is used for `file=sys.stderr`.

---

### `main.py` — add `write_manifest` call once per invocation

**Analog:** `main.py` lines 277-342 (the `output_dir` resolution + batch/single dispatch section)

**Import addition** (line 18, existing import block — add alongside `create_spec_folder`):
```python
from src.diagnostics.run_manager import create_spec_folder
```
Becomes:
```python
from src.diagnostics.run_manager import create_spec_folder, write_manifest
```
(Proven import path: `main.py:18` already uses this exact module path from `spec_classifier/` cwd.)

**`output_dir` resolution pattern** (lines 277-283 — `output_dir` is resolved once here, before dispatch):
```python
paths_cfg = config.get("paths") or {}
output_dir_raw = (
    args.output_dir
    or paths_cfg.get("output_root")
    or str(DEFAULT_OUTPUT_ROOT)
)
output_dir = Path(output_dir_raw) if Path(output_dir_raw).is_absolute() else _resolve_path(output_dir_raw, cwd)
```

**Call site placement** (D-03: once per invocation, after batch dispatch, before single-file return):
- After line 342 (batch path `return`) but the call must cover the single path too.
- Correct pattern: call `write_manifest(output_dir)` **before** the `if batch_dir is not None:` early return at line 342, OR place one call just before the `if batch_dir is not None:` block begins (line 294) and one before the `return _run_single(...)` at line 353. Per D-03, one call covering both paths means calling it after `output_dir` is resolved (line 283) and before the dispatch branches — i.e., at line ~284, immediately after resolution.

---

### `batch_audit.py` — delete local function, import shared

**Analog:** `main.py:18` (the proven import pattern for `run_manager`):
```python
from src.diagnostics.run_manager import create_spec_folder
```

**What to delete** (lines 1357-1366 — the entire local function):
```python
def detect_vendor_from_path(path: Path, known_vendors: list[str] | None = None) -> str:
    """Detect vendor from path components using known vendor list."""
    if known_vendors is None:
        known_vendors = _get_known_vendors(_load_config())
    s = str(path).lower()
    for vendor in known_vendors:
        if f"/{vendor}/" in s or f"\\{vendor}\\" in s:
            return vendor
    print(f"  [WARN] Cannot detect vendor from path: {path}", file=sys.stderr)
    return "unknown"
```

**Import to add** (at top of file, alongside existing imports):
```python
from src.diagnostics.run_manager import detect_vendor_from_path
```

**Live caller** (line 1451 — no signature change needed; `known_vendors` is already in scope at the call site):
```python
vendor = args.vendor or detect_vendor_from_path(f, known_vendors)
```
This call already passes `known_vendors` explicitly, so it is compatible with the new required-parameter signature.

---

### `cluster_audit.py` — delete local function, import shared, update caller

**Analog:** `main.py:18` (same import pattern).

**What to delete** (lines 97-117 — the entire local function including dead aliases):
```python
def _detect_vendor_from_path(path: Path, known_vendors: list[str] | None = None) -> str:
    """Infer vendor from file name, parent, or grandparent directory name."""
    if known_vendors is None:
        known_vendors = _get_known_vendors(_load_config())
    stem = path.stem.lower()
    parent = path.parent.name.lower()
    grandparent = path.parent.parent.name.lower()

    for text in (stem, parent, grandparent):
        for vendor in known_vendors:
            if f"{vendor}_run" in text or text == vendor:
                return vendor
    # HPE alias: "hp_run" or stem starting with "hp"
    for text in (stem, parent, grandparent):
        if "hp_run" in text or (text.startswith("hp") and "hp" not in known_vendors):
            return "hpe"
    # Cisco alias: "ccw" in path
    if any("ccw" in t for t in (stem, parent, grandparent)):
        if "cisco" in known_vendors:
            return "cisco"
    return "unknown"
```

**Import to add** (alongside existing imports at top):
```python
from src.diagnostics.run_manager import detect_vendor_from_path
```

**Live caller update** (line 195 — currently passes no arguments, relying on the removed `None` default):
```python
# Before (line 195):
vendor = _detect_vendor_from_path(path)

# After:
config = _load_config()
known_vendors = _get_known_vendors(config)
vendor = detect_vendor_from_path(path, known_vendors)
```
Note: `_load_config` and `_get_known_vendors` already exist in `cluster_audit.py` (lines 24-41). The config load is already done at the module's `build_parser` path (line 55); the executor should check whether `load_candidate_rows` has access to the config or if a local call is needed. The pattern at `cluster_audit.py:100` (inside `build_parser`) already calls `_get_known_vendors(_load_config())` as a one-liner — that same pattern applies here.

---

### `tests/test_output_structure.py` — extend with README + top-level layout assertions

**Analog:** `test_output_structure.py` lines 33-74 (`test_output_tree_shape_dell_run`)

**subprocess invocation pattern** (lines 44-56 — copy verbatim for new tests):
```python
result = subprocess.run(
    [
        sys.executable, "main.py",
        "--input", str(input_xlsx),
        "--config", str(root / "config.yaml"),
        "--output-dir", str(output_root),
    ],
    cwd=str(root),
    capture_output=True,
    text=True,
    timeout=60,
)
assert result.returncode == 0, f"CLI failed: {result.stderr!r}"
```

**Negative assertion pattern** (line 64):
```python
assert not (output_root / "dell_run").exists(), "Old dell_run/ folder must NOT exist"
```
Apply the same negative pattern to assert no `run-<timestamp>-*/`, no `*-TOTAL/` at `output_root`.

**New assertions to add** (D-07 manifest unit test + D-08 layout assertion):
```python
# README.md presence at output_root
assert (output_root / "README.md").exists(), "README.md manifest must exist at output_root"

# Top-level contains ONLY the three buckets + README.md
top_level = {p.name for p in output_root.iterdir()}
assert top_level == {"READY", "SPLIT", "AUDIT", "README.md"}, \
    f"output_root must contain exactly READY/, SPLIT/, AUDIT/, README.md — got {top_level}"
```
The manifest unit test (D-07) can either live in this file as a standalone function (no subprocess needed — call `write_manifest(tmp_path)` directly and inspect the written file) or in the new `test_run_manager.py`. Either location uses `tmp_path` and direct function call, not a subprocess.

---

### `tests/test_batch_audit.py` — remove `TestDetectVendorFromPath`

**What to remove:** the entire class `TestDetectVendorFromPath` (lines 438-468).

**Import to update** (line 12-14 — remove `detect_vendor_from_path` from the `from batch_audit import` line):
```python
# Before:
from batch_audit import (
    validate_row, _generate_report, detect_vendor_from_path,
    issue_color, _is_known_fp, KNOWN_FP_CASES,
)

# After:
from batch_audit import (
    validate_row, _generate_report,
    issue_color, _is_known_fp, KNOWN_FP_CASES,
)
```

---

### `tests/test_run_manager.py` (new) — consolidated detect-vendor test suite

**Analog:** `test_batch_audit.py` `TestDetectVendorFromPath` class (lines 438-468) — same assertions, re-targeted to the shared function.

**Module header and import pattern** (mirrors `test_batch_audit.py` lines 1-14):
```python
"""Tests for run_manager.py — create_spec_folder + detect_vendor_from_path."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.diagnostics.run_manager import detect_vendor_from_path
```

**Test class pattern** (mirrors `TestDetectVendorFromPath` in `test_batch_audit.py`):
```python
class TestDetectVendorFromPath:
    KNOWN = ["cisco", "dell", "hpe"]

    def test_dell_split_layout(self):
        assert detect_vendor_from_path(Path("OUTPUT/SPLIT/dell/dl1/dl1_annotated.xlsx"), self.KNOWN) == "dell"

    def test_hpe_split_layout(self):
        assert detect_vendor_from_path(Path("OUTPUT/SPLIT/hpe/hp1/hp1_annotated.xlsx"), self.KNOWN) == "hpe"

    def test_cisco_split_layout(self):
        assert detect_vendor_from_path(Path("OUTPUT/SPLIT/cisco/ccw_1/ccw_1_annotated.xlsx"), self.KNOWN) == "cisco"

    def test_hp_run_alias_removed_returns_unknown(self):
        assert detect_vendor_from_path(Path("OUTPUT/hp_run/file.xlsx"), self.KNOWN) == "unknown"

    def test_lenovo_run_returns_unknown(self):
        assert detect_vendor_from_path(Path("OUTPUT/lenovo_run/file.xlsx"), self.KNOWN) == "unknown"

    def test_no_vendor_keyword_returns_unknown(self):
        assert detect_vendor_from_path(Path("/some/random/path/file.xlsx"), self.KNOWN) == "unknown"

    def test_new_vendor_in_known_vendors(self):
        extended = self.KNOWN + ["lenovo"]
        assert detect_vendor_from_path(Path("OUTPUT/SPLIT/lenovo/L1/L1_annotated.xlsx"), extended) == "lenovo"

    def test_vendor_in_directory_path(self):
        assert detect_vendor_from_path(Path("OUTPUT/dell/subdir/file.xlsx"), self.KNOWN) == "dell"
```

**Assertions from `test_cluster_audit.py` to DROP** (these encode behavior the unified function deliberately does not have — D-14):
- `("OUTPUT/hpe_run/hp8_annotated_audited.xlsx", "hpe")` — `_run` alias gone
- `("OUTPUT/dell_run/dl5_annotated_audited.xlsx", "dell")` — `_run` alias gone
- `("OUTPUT/cisco_run/ccw_2_annotated_audited.xlsx", "cisco")` — `_run` alias gone
- `test_detect_vendor_ccw_alias_returns_cisco` — `ccw` alias gone (D-13)
- `test_detect_vendor_new_vendor_in_known` with `lenovo_run` path — `_run` alias gone

**Also add: manifest unit test** (D-07 — if placed here rather than `test_output_structure.py`):
```python
from src.diagnostics.run_manager import write_manifest

def test_write_manifest_creates_readme(tmp_path):
    write_manifest(tmp_path)
    readme = tmp_path / "README.md"
    assert readme.exists(), "write_manifest must create README.md at output_root"
    content = readme.read_text(encoding="utf-8")
    # Bucket headings present
    assert "READY" in content
    assert "SPLIT" in content
    assert "AUDIT" in content
    # At least one Russian-language purpose description present
    assert any(ord(c) > 127 for c in content), "Purpose text must contain Russian characters"
    # Idempotent: second call overwrites with identical bytes
    write_manifest(tmp_path)
    assert readme.read_text(encoding="utf-8") == content
```

---

## Shared Patterns

### Import path for `run_manager`
**Source:** `main.py:18`
**Apply to:** `batch_audit.py` and `cluster_audit.py` import additions
```python
from src.diagnostics.run_manager import create_spec_folder
```
Both audit scripts run from the `spec_classifier/` cwd (same as `main.py`), so `from src.diagnostics.run_manager import ...` resolves identically — no packaging changes needed.

### `sys.path.insert` in test files
**Source:** `test_batch_audit.py:10`, `test_cluster_audit.py:10`
**Apply to:** `test_run_manager.py`
```python
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
```
This makes the `spec_classifier/` package root importable from the `tests/` subdirectory.

### `tmp_path` + `subprocess.run` test pattern
**Source:** `test_output_structure.py` lines 33-56
**Apply to:** new manifest integration assertion in `test_output_structure.py`
The pattern is: create `output_root = tmp_path / "output"`, run `main.py` via subprocess with `--output-dir`, assert presence/absence of paths. For the manifest unit test (`D-07`), skip subprocess and call `write_manifest(tmp_path)` directly.

### `pytest.skip` for missing input files
**Source:** `test_output_structure.py:39`
**Apply to:** any new integration test that needs real INPUT files
```python
if not input_xlsx.exists():
    pytest.skip(f"Input not found: {input_xlsx} ...")
```

---

## No Analog Found

All files have close analogs. No entries.

---

## Metadata

**Analog search scope:** `spec_classifier/` (main.py, batch_audit.py, cluster_audit.py, src/diagnostics/run_manager.py, tests/)
**Files read:** run_manager.py, main.py (lines 1-60, 225-368), batch_audit.py (lines 1-30, 1350-1455), cluster_audit.py (lines 1-130, 185-205), test_output_structure.py, test_batch_audit.py (lines 1-30, 430-468), test_cluster_audit.py (lines 1-75)
**Pattern extraction date:** 2026-06-07
