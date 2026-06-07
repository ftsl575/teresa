---
phase: 08-audit-routing-audit
reviewed: 2026-06-07T17:02:09Z
depth: standard
files_reviewed: 4
files_reviewed_list:
  - spec_classifier/batch_audit.py
  - spec_classifier/cluster_audit.py
  - spec_classifier/tests/test_batch_audit.py
  - spec_classifier/tests/test_cluster_audit.py
findings:
  critical: 0
  blocker: 0
  warning: 4
  info: 3
  total: 7
status: issues_found
---

# Phase 8: Code Review Report

**Reviewed:** 2026-06-07T17:02:09Z
**Depth:** standard
**Files Reviewed:** 4
**Status:** issues_found

## Summary

This was a routing-only phase: `batch_audit.py` and `cluster_audit.py` were re-pointed
to read `*_annotated.xlsx` from `output_root/SPLIT` and write per-spec audited workbooks
plus aggregates (`audit_report.json`, `audit_summary.xlsx`, `cluster_summary.xlsx`) under
`output_root/AUDIT`. Dead pre-Phase-7 path matchers (`{vendor}_run`, `hp_run`, `-TOTAL`)
were removed from `batch_audit.detect_vendor_from_path` / `find_annotated_files`, and the
corresponding tests were realigned to the dual-bucket layout.

I traced the diff against the scoping concerns (relative_to edge cases, missing mkdir,
silent audit_report.json no-op, weakened skip-gates, accidental audit-logic changes).
**Classification, E-code, AI-mismatch, and clustering logic are unchanged** — the diff is
confined to path derivation, two function signatures, and string constants. All 115 tests
in the two files pass.

No BLOCKER/Critical issues found. The routing is internally consistent (every write target
now lands under `AUDIT/`, every read source under `SPLIT/`, mkdir guards are present, and
`relative_to(SPLIT_root)` is safe because `find_annotated_files` only yields files under
`SPLIT_root`). The findings below are quality/robustness gaps and an incomplete realignment
between the two modules, not correctness defects in the happy path.

## Warnings

### WR-01: cluster_audit vendor detector not realigned — diverges from batch_audit, retains dead `_run`/`hp_run` matchers

**File:** `spec_classifier/cluster_audit.py:97-117`
**Issue:** The phase removed the `{vendor}_run`, `hp_run`, and `-TOTAL` matchers from
`batch_audit.detect_vendor_from_path` (diff at `batch_audit.py:1357-1365`) and from
`find_annotated_files`. The functionally-equivalent `cluster_audit._detect_vendor_from_path`
was **not** realigned: it still contains `f"{vendor}_run" in text`, the `"hp_run"` HPE alias,
and the `"ccw"` Cisco alias. The two modules now apply different vendor-detection rules to the
same AUDIT/SPLIT tree. Worse, `test_cluster_audit.py:47-72` *locks in* the old behavior
(`hpe_run`→hpe, `dell_run`→dell, `ccw_export`→cisco) — directly contradicting
`test_batch_audit.py:450-457` which now asserts `hp_run`/`lenovo_run`→`unknown`. A reader
cannot tell from the tests whether `_run` support is intended or vestigial.
**Fix:** Decide one contract. If Phase-7+ output never contains `_run` dirs, mirror the
batch_audit change in cluster_audit (drop the `_run`/`hp_run` branches) and update
`test_cluster_audit.py` to the SPLIT/AUDIT layout, e.g.:
```python
def _detect_vendor_from_path(path, known_vendors=None):
    ...
    for text in (stem, parent, grandparent):
        for vendor in known_vendors:
            if text == vendor:
                return vendor
    if any("ccw" in t for t in (stem, parent, grandparent)) and "cisco" in known_vendors:
        return "cisco"
    return "unknown"
```
If `_run` support must be retained for back-compat, add a comment in *both* files explaining
why the detectors intentionally differ.

### WR-02: D-04 "overwrite in place, no rmtree" leaves stale audited files that cluster_audit silently consumes

**File:** `spec_classifier/batch_audit.py:1452-1454`, `spec_classifier/cluster_audit.py:153-169`
**Issue:** `main()` writes each audited workbook into `AUDIT/<vendor>/<spec>/...` and never
prunes `AUDIT/`. If a SPLIT source is renamed or removed between runs, its previously-written
`AUDIT/.../X_annotated_audited.xlsx` persists. `cluster_audit._collect_xlsx_files` reads
**every** `AUDIT/**/*_annotated_audited.xlsx` unconditionally, so clustering will ingest stale
audited rows that no longer correspond to any current SPLIT input — producing candidate rows
and clusters for specs that are no longer part of the run. This is a behavioral risk introduced
by the routing design (the old layout co-located audited files with the per-run folder, so a
removed run took its audited file with it).
**Fix:** Either clear per-spec stale output (e.g. remove `AUDIT/<vendor>/<spec>` before
writing, scoped — not a blanket `rmtree AUDIT`), or have `cluster_audit` reconcile AUDIT
against the current SPLIT set and skip audited stems with no live SPLIT source. At minimum,
document the stale-file behavior where D-04 is asserted.

### WR-03: `write_cluster_summary` silently no-ops the audit_report.json merge when the report is absent

**File:** `spec_classifier/cluster_audit.py:457-476`
**Issue:** After re-pointing to `AUDIT/audit_report.json`, the merge is still guarded by
`if json_path.exists():`. When `cluster_audit.py` runs standalone (no prior `batch_audit.py`
run, or AUDIT not yet created), the `clusters` section is silently dropped: `cluster_summary.xlsx`
is written but the JSON is neither created nor updated, with no warning. A user running only the
clustering step gets a report with no `clusters` key and no indication why. The routing change
makes this more likely to surprise users because the JSON now lives in a separate `AUDIT/`
bucket that may not exist independently of a batch run.
**Fix:** Emit an explicit notice on the no-op path, or write a minimal report when absent:
```python
if json_path.exists():
    ... # existing merge
else:
    print(f"[INFO] {json_path} not found — writing clusters-only report.", file=sys.stderr)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump({"clusters": {...}}, fh, ensure_ascii=False, indent=2, cls=_NumpyEncoder)
```

### WR-04: New `find_annotated_files` SPLIT-only behavior is untested

**File:** `spec_classifier/batch_audit.py:1341-1356`
**Issue:** `find_annotated_files` gained the load-bearing D-02 contract — signature renamed to
`split_root`, a `if not split_root.is_dir(): return []` early-return (no whole-tree fallback),
and removal of the `-TOTAL` exclusion. None of this is covered by a test. There is no test
asserting that a missing `SPLIT/` yields `[]` (rather than scanning the whole `output_root`),
nor that `_audited` files are still excluded, nor that `vendor_filter`/`since` still apply
against the SPLIT subtree. A future edit could reintroduce a whole-tree fallback (which would
re-scan `AUDIT/` and double-process) with no failing test.
**Fix:** Add focused tests, e.g. missing-SPLIT returns `[]`; a SPLIT tree with one
`*_annotated.xlsx` and one `*_annotated_audited.xlsx` returns only the former; a file outside
SPLIT is never returned.

## Info

### IN-01: `files.index(f)` for progress numbering is fragile and O(n²)

**File:** `spec_classifier/batch_audit.py:1455`
**Issue:** `file_num = files.index(f) + 1` re-scans the list each iteration and returns the
*first* index equal to `f`. It is correct only while paths are unique (they are, from rglob),
but it is needlessly brittle for what is just a loop counter.
**Fix:** Use `enumerate`: `for file_num, f in enumerate(files, 1):`.

### IN-02: `_generate_human_report` rglob is unscoped and picks `[0]` on stem collision

**File:** `spec_classifier/batch_audit.py:924-927`
**Issue:** `Path(output_dir).rglob(f"{stem}_audited.xlsx")` searches the entire `output_root`
(not the `AUDIT/` bucket) and takes `audited_files[0]`. With the new per-vendor mirror layout,
two vendors could in principle share a spec stem, making the chosen file arbitrary. This code
was not touched by the diff, but the routing change is the reason audited files are now spread
across `AUDIT/<vendor>/<spec>/` rather than co-located with their run, increasing collision
surface.
**Fix:** Scope the search to `AUDIT/` and disambiguate by vendor, e.g.
`(Path(output_dir) / "AUDIT").rglob(...)` filtered on `fdata["vendor"]` in the path.

### IN-03: Stale "Сохранены рядом с исходными" message contradicts new routing

**File:** `spec_classifier/batch_audit.py:1542`
**Issue:** `print(f"Сохранены рядом с исходными как *{args.suffix}.xlsx")` ("saved next to the
sources") is now false — audited files are written to `AUDIT/`, not next to the SPLIT sources.
The CLAUDE.md OUTPUT-layout section is likewise stale, though docs are out of review scope.
**Fix:** Update the message to point at `AUDIT/`, e.g. `f"Сохранены в {AUDIT_root} как *{args.suffix}.xlsx"`.

---

_Reviewed: 2026-06-07T17:02:09Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
