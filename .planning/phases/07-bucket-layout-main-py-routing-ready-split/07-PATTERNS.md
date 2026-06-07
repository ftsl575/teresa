# Phase 7: Bucket layout & main.py routing (READY + SPLIT) - Pattern Map

**Mapped:** 2026-06-07
**Files analyzed:** 2 modified files + 3 test files requiring realignment
**Analogs found:** 5 / 5

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `spec_classifier/src/diagnostics/run_manager.py` | utility | file-I/O | self (current `create_run_folder`) | exact (replace-in-place) |
| `spec_classifier/main.py` (`_run_single` + batch block) | controller (pipeline entry) | request-response | self (current `_run_single`) | exact (modify-in-place) |
| `spec_classifier/tests/test_output_structure.py` | test | file-I/O | self (current test) | exact (realign-in-place) |
| `spec_classifier/tests/test_cli.py` | test | request-response | self (current test) | exact (realign-in-place) |

---

## Pattern Assignments

### `spec_classifier/src/diagnostics/run_manager.py` (utility, file-I/O)

**Analog:** self — current `create_run_folder` is the direct predecessor of `create_spec_folder`.

**Current module docstring** (lines 1-7) — update this to drop TOTAL/timestamp references:
```python
"""
Run folder management: create unique output directories per pipeline run and batch session.

Naming conventions:
  Single run:  run-YYYY-MM-DD__HH-MM-SS-<stem>   (e.g. run-2026-02-26__06-09-53-dl1)
  Batch TOTAL: run-YYYY-MM-DD__HH-MM-SS-TOTAL
"""
```

**Current imports** (lines 9-12) — after deletion of `get_session_stamp` and folder helpers that use `datetime`, the `datetime` import can be dropped; `shutil` and `Path` are still needed by `create_spec_folder`:
```python
import shutil
from datetime import datetime
from pathlib import Path
```

**Dead helpers to DELETE entirely (D-09):**

`get_session_stamp` — lines 14-16:
```python
def get_session_stamp() -> str:
    """Return current timestamp in run folder format: YYYY-MM-DD__HH-MM-SS."""
    return datetime.now().strftime("%Y-%m-%d__%H-%M-%S")
```

`create_run_folder` — lines 19-41:
```python
def create_run_folder(base_dir: str, input_filename: str, stamp: str = None) -> Path:
    """
    Create a unique run folder: <base_dir>/run-<stamp>-<stem>/
    If folder already exists (same second), append _1, _2, ... for uniqueness.
    ...
    """
    base_path = Path(base_dir)
    base_path.mkdir(parents=True, exist_ok=True)
    if stamp is None:
        stamp = get_session_stamp()
    stem = Path(input_filename).stem
    name = f"run-{stamp}-{stem}"
    folder = base_path / name
    suffix = 0
    while folder.exists():
        suffix += 1
        folder = base_path / f"{name}_{suffix}"
    folder.mkdir(parents=True)
    return folder
```

`create_total_folder` — lines 44-52:
```python
def create_total_folder(base_dir: str, stamp: str) -> Path:
    """
    Create (or return existing) TOTAL aggregation folder: <base_dir>/run-<stamp>-TOTAL/
    Idempotent: does not fail if already exists.
    """
    base_path = Path(base_dir)
    folder = base_path / f"run-{stamp}-TOTAL"
    folder.mkdir(parents=True, exist_ok=True)
    return folder
```

`copy_to_total` — lines 55-72:
```python
def copy_to_total(run_folder: Path, total_folder: Path, stem: str) -> None:
    """
    Copy the three presentation files from run_folder to total_folder with stem prefix.
    ...
    """
    copies = [
        (run_folder / "cleaned_spec.xlsx",         total_folder / f"{stem}_cleaned_spec.xlsx"),
        (run_folder / f"{stem}_annotated.xlsx",    total_folder / f"{stem}_annotated.xlsx"),
        (run_folder / f"{stem}_branded.xlsx",      total_folder / f"{stem}_branded.xlsx"),
    ]
    for src, dst in copies:
        if src.exists():
            shutil.copy2(src, dst)
```

**New helper to ADD (D-10) — `create_spec_folder`:**

Copy the structural pattern from `create_run_folder` (mkdir-parents, return Path), but replace uniquification with wipe-first semantics. The helper must:
1. Construct `output_root / bucket / vendor / spec` (four-segment path).
2. If the directory exists, `shutil.rmtree` it (wipe-first per D-04).
3. Re-create it with `mkdir(parents=True)`.
4. Return the resulting `Path`.

Pattern skeleton (copy `create_run_folder` structure, replace body):
```python
def create_spec_folder(output_root: Path, bucket: str, vendor: str, spec: str) -> Path:
    """
    Create (or wipe-and-recreate) <output_root>/<bucket>/<vendor>/<spec>/.

    Wipe-first: if the directory already exists it is deleted before recreation,
    ensuring no stale artifacts from a previous run survive.

    Args:
        output_root: top-level output directory (e.g. C:\\...\\OUTPUT)
        bucket:      bucket name ("READY" or "SPLIT")
        vendor:      registry key, lowercase (e.g. "dell", "hpe")
        spec:        input file stem (e.g. "dl1")

    Returns:
        Path to the freshly created directory.
    """
    folder = Path(output_root) / bucket / vendor / spec
    if folder.exists():
        shutil.rmtree(folder)
    folder.mkdir(parents=True)
    return folder
```

Note: `shutil` is already imported (kept from current file). `datetime` import is dropped once `get_session_stamp` is gone.

---

### `spec_classifier/main.py` — `_run_single` (controller, request-response)

**Analog:** self — lines 113-240 are the primary mutation target.

**Current imports from run_manager** (lines 18-23) — all four symbols are removed; replace with single new import:
```python
from src.diagnostics.run_manager import (
    create_run_folder,
    get_session_stamp,
    create_total_folder,
    copy_to_total,
)
```
Replace with:
```python
from src.diagnostics.run_manager import create_spec_folder
```

**`_run_single` signature** (lines 113-125) — remove `session_stamp` and `total_folder` parameters (both are artefacts of the old timestamped scheme):
```python
def _run_single(
    input_path: Path,
    config: dict,
    config_path: Path,
    output_dir: Path,
    vendor: str = "dell",
    session_stamp: str = None,   # DELETE
    total_folder: Path = None,   # DELETE
    save_golden: bool = False,
    update_golden: bool = False,
    cwd: Path = None,
    log=None,
) -> int:
```

**Current path construction in `_run_single`** (lines 134-135) — the two lines that build `vendor_base` and call `create_run_folder` are replaced:
```python
# OLD (lines 134-135):
vendor_base = output_dir / f"{vendor}_run"
run_folder = create_run_folder(str(vendor_base), input_path.name, stamp=session_stamp)
```
Replace with two `create_spec_folder` calls — one for SPLIT, one for READY:
```python
# NEW — two wipe-first bucket folders; AUDIT is not touched (D-05)
split_folder = create_spec_folder(output_dir, "SPLIT", vendor, input_path.stem)
ready_folder = create_spec_folder(output_dir, "READY", vendor, input_path.stem)
```
All subsequent references to `run_folder` that write the nine non-branded artifacts route to `split_folder`. The branded workbook routes to `ready_folder`.

**All nine artifact writes** (lines 159-172) — currently use `run_folder`; change to `split_folder`:
```python
# Lines 159-163 pattern (keep, just swap variable name):
save_rows_raw(raw_rows, run_folder)              # → split_folder
save_rows_normalized(normalized_rows, run_folder) # → split_folder
save_classification(classification_results, normalized_rows, run_folder)  # → split_folder
save_unknown_rows(normalized_rows, classification_results, run_folder)     # → split_folder
save_header_rows(normalized_rows, run_folder)    # → split_folder

# Line 172:
save_run_summary(stats, run_folder)              # → split_folder

# Line 174:
generate_cleaned_spec(normalized_rows, classification_results, config, run_folder)  # → split_folder

# Lines 176-181 (annotated writer):
generate_annotated_source_excel(
    raw_rows, normalized_rows, classification_results, input_path, run_folder,  # → split_folder
    ...
)
```

The `run_log_path` (line 137) also currently lives in `run_folder` — after the change it goes in `split_folder`:
```python
# Line 137 (current):
run_log_path = run_folder / "run.log"
# After change:
run_log_path = split_folder / "run.log"
```

**Branded workbook block** (lines 182-189) — destination path and filename change (D-07, D-08):
```python
# CURRENT (lines 182-189):
if adapter.generates_branded_spec():
    branded_path = run_folder / f"{input_path.stem}_branded.xlsx"
    generate_branded_spec(
        normalized_rows=normalized_rows,
        classification_results=classification_results,
        source_filename=input_path.name,
        output_path=branded_path,
    )
```
Replace `branded_path` only; `source_filename=input_path.name` is unchanged (D-07):
```python
# NEW:
if adapter.generates_branded_spec():
    branded_path = ready_folder / f"Коммерческое предложение_{input_path.stem}.xlsx"
    generate_branded_spec(
        normalized_rows=normalized_rows,
        classification_results=classification_results,
        source_filename=input_path.name,   # unchanged — keeps bytes byte-equal (D-07)
        output_path=branded_path,
    )
```

**TOTAL copy block** (lines 191-194) — delete entirely (D-09):
```python
# DELETE these lines:
if total_folder is not None:
    copy_to_total(run_folder, total_folder, input_path.stem)
    log.info("Copied to TOTAL: %s", total_folder)
```

**Summary print** (line 225) — `run_folder` reference becomes `split_folder`:
```python
# Current:
print(f"  run_folder: {run_folder}")
# After:
print(f"  split_folder: {split_folder}")
```

---

### `spec_classifier/main.py` — batch block in `main()` (controller, request-response)

**Current batch preamble** (lines 315-318) — `session_stamp`, `vendor_base`, and `total_folder` creation are all removed:
```python
# DELETE (lines 315-318):
session_stamp = get_session_stamp()
vendor_base = output_dir / f"{args.vendor}_run"
total_folder = create_total_folder(str(vendor_base), session_stamp)
log.info("Batch mode: %d files, TOTAL folder: %s", len(xlsx_files), total_folder)
```
Replace with a simple count log (no TOTAL folder):
```python
log.info("Batch mode: %d files, output_root: %s", len(xlsx_files), output_dir)
```

**`_run_single` call inside batch loop** (lines 336-348) — remove `session_stamp` and `total_folder` kwargs:
```python
# CURRENT kwargs to remove:
session_stamp=session_stamp,
total_folder=total_folder,
```

**Batch completion print** (line 358) — remove `TOTAL: {total_folder}` suffix (Claude's discretion on rewording):
```python
# CURRENT:
print(f"Batch complete: {len(processed)} processed, {len(skipped)} skipped, {len(failed)} failed. TOTAL: {total_folder}")
# NEW (example):
print(f"Batch complete: {len(processed)} processed, {len(skipped)} skipped, {len(failed)} failed. Output: {output_dir}")
```

---

## Test Files Requiring Realignment (TEST-01)

### `spec_classifier/tests/test_output_structure.py` (test, file-I/O)

**Analog:** self — the entire file tests the old path scheme and must be rewritten to assert the new bucket layout.

**Current layout assertions** (lines 60-78, Dell case) — all references to `dell_run`, `run-*` pattern, and `_branded.xlsx` filename must change:
```python
# CURRENT (lines 61-78) — assertions that must be replaced:
vendor_root = output_root / "dell_run"
assert vendor_root.is_dir(), ...
run_folders = [p for p in vendor_root.iterdir() if p.is_dir() and p.name.startswith("run-")]
assert len(run_folders) >= 1, ...
run_folder = run_folders[0]
assert RUN_FOLDER_PATTERN.match(run_folder.name) ..., ...
assert run_folder.parent == vendor_root, ...
stem = "dl1"
for name in REQUIRED_ARTIFACTS:
    assert (run_folder / name).exists(), ...
assert (run_folder / f"{stem}_annotated.xlsx").exists(), ...
assert (run_folder / f"{stem}_branded.xlsx").exists(), ...  # old filename
```
New assertions must check:
- `output_root / "SPLIT" / "dell" / "dl1" /` for the nine artifacts + `dl1_annotated.xlsx`
- `output_root / "READY" / "dell" / "dl1" / "Коммерческое предложение_dl1.xlsx"` for branded
- No `output_root / "dell_run"` directory exists

**`RUN_FOLDER_PATTERN` constant** (line 21) — delete; no longer used:
```python
RUN_FOLDER_PATTERN = re.compile(r"^run-\d{4}-\d{2}-\d{2}__\d{2}-\d{2}-\d{2}-(.+)$")
```

**`REQUIRED_ARTIFACTS` constant** (lines 24-33) — keep the list; it applies to the `SPLIT` folder exactly as-is.

**`test_output_root_configurable_via_cli`** (lines 123-148) — currently checks `output_root / "dell_run"` and `run-*` glob; update to check `output_root / "SPLIT" / "dell"` instead.

### `spec_classifier/tests/test_cli.py` (test, request-response)

**Analog:** self — artifact location assertions must move from the old timestamped folder to `SPLIT/dell/dl1/`.

**Current path walk** (lines 41-47):
```python
# CURRENT (lines 41-47) — must change:
vendor_root = output_dir / "dell_run"
assert vendor_root.exists(), "output_root/dell_run should exist"
run_folders = list(vendor_root.glob("run-*"))
assert run_folders, "At least one run-* folder under dell_run should exist"
latest = max(run_folders, key=lambda p: p.stat().st_mtime)
assert (latest / "cleaned_spec.xlsx").exists(), ...
assert (latest / "run_summary.json").exists(), ...
```
Replace with direct paths:
```python
# NEW pattern:
split_folder = output_dir / "SPLIT" / "dell" / "dl1"
assert split_folder.is_dir(), f"SPLIT/dell/dl1 folder must exist under {output_dir}"
assert (split_folder / "cleaned_spec.xlsx").exists(), ...
assert (split_folder / "run_summary.json").exists(), ...
```

---

## Shared Patterns

### Wipe-first folder creation
**Source:** `create_run_folder` in `run_manager.py` (lines 19-41) — structural template for `create_spec_folder`.
**Apply to:** `create_spec_folder` in `run_manager.py`.

The key structural pattern to copy (then adapt):
```python
base_path = Path(base_dir)
base_path.mkdir(parents=True, exist_ok=True)   # ← adapt: rmtree + mkdir instead
folder = base_path / name
folder.mkdir(parents=True)
return folder
```

### File handler lifecycle (logging)
**Source:** `main.py` lines 137-141 and 226-228 — FileHandler added before pipeline, removed in `finally`.
**Apply to:** keep this pattern unchanged in `_run_single`; only the path variable feeding `run_log_path` changes (`run_folder` → `split_folder`).
```python
run_log_path = run_folder / "run.log"          # line 137: run_folder → split_folder
fh = logging.FileHandler(run_log_path, encoding="utf-8")
fh.setFormatter(logging.Formatter(...))
root_logger = logging.getLogger()
root_logger.addHandler(fh)
try:
    ...
finally:
    root_logger.removeHandler(fh)
    fh.close()
```

### Error handling in `_run_single`
**Source:** `main.py` lines 230-238 — three `except` blocks at the bottom of `_run_single`.
**Apply to:** keep entirely unchanged; this phase does not touch error handling.
```python
except FileNotFoundError as e:
    print(f"Error: {e}", file=sys.stderr)
    return 1
except yaml.YAMLError as e:
    print(f"Error: Invalid YAML: {e}", file=sys.stderr)
    return 1
except Exception:
    log.exception("Pipeline failed")
    return 1
```

### `generate_branded_spec` call signature
**Source:** `main.py` lines 184-189; `branded_spec_writer.py` lines 151-156.
**Apply to:** branded block in `_run_single` — only `output_path` argument changes; all other args are identical.
```python
generate_branded_spec(
    normalized_rows=normalized_rows,
    classification_results=classification_results,
    source_filename=input_path.name,   # MUST stay input_path.name — D-07 byte-equality guard
    output_path=branded_path,          # this argument changes
)
```

---

## No Analog Found

None. Both files being modified are self-analogous (modify-in-place), and the test files that need realignment are also self-analogous. No net-new files are introduced in Phase 7.

---

## Metadata

**Analog search scope:** `spec_classifier/main.py`, `spec_classifier/src/diagnostics/run_manager.py`, `spec_classifier/tests/test_output_structure.py`, `spec_classifier/tests/test_cli.py`, `spec_classifier/src/outputs/branded_spec_writer.py`
**Files scanned:** 5
**Pattern extraction date:** 2026-06-07
