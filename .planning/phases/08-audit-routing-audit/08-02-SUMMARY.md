---
phase: 08-audit-routing-audit
plan: 02
subsystem: cluster-audit-routing
tags: [routing, cluster_audit, SPLIT, AUDIT, dual-bucket]
requires:
  - "Phase 8 Plan 01: batch_audit writes audit_report.json + audited workbooks to output_root/AUDIT/"
  - "Phase 7 bucket layout: SPLIT/<vendor>/<spec>/<stem>_annotated.xlsx (main.py routing)"
provides:
  - "cluster_audit reads *_annotated_audited.xlsx from output_root/AUDIT/ and *_annotated.xlsx from output_root/SPLIT/ (explicit dual-bucket, is_dir-guarded)"
  - "cluster_summary.xlsx written to output_root/AUDIT/ root"
  - "audit_report.json cluster-merge update targets output_root/AUDIT/audit_report.json (matches batch_audit's location)"
affects:
  - "tests/test_cluster_audit.py (Plan 08-03 path/layout realignment; full pytest gate)"
tech-stack:
  added: []
  patterns:
    - "SP-1 bucket-root derivation: AUDIT/SPLIT roots = output_dir / bucket"
    - "SP-3 one-segment / 'AUDIT' insertion for aggregate destinations"
    - "dual-bucket read = SP-1 applied to two read bases preserving prefer-audited dedup"
key-files:
  created: []
  modified:
    - spec_classifier/cluster_audit.py
decisions:
  - "D-01: --output-dir stays output_root; AUDIT/SPLIT roots derived inline in _collect_xlsx_files"
  - "D-02: strict is_dir()-guarded bucket reads -> empty on missing bucket (no whole-tree fallback)"
  - "D-05: cluster_summary.xlsx + audit_report.json cluster-merge update target AUDIT/ root"
  - "D-06: explicit dual-bucket read (AUDIT audited + SPLIT annotated) with prefer-audited dedup preserved"
metrics:
  duration: ~4min
  completed: 2026-06-07
---

# Phase 8 Plan 02: Audit routing (cluster_audit) Summary

Re-pointed `cluster_audit.py` at the Phase-7/Phase-8 bucket layout: `_collect_xlsx_files`
now reads audited workbooks from `output_root/AUDIT/` and annotated fallbacks from
`output_root/SPLIT/` (explicit dual-bucket, each `is_dir()`-guarded), and
`write_cluster_summary` writes `cluster_summary.xlsx` plus the `audit_report.json`
cluster-merge update to the `output_root/AUDIT/` root — matching where Plan 08-01's
batch_audit now writes `audit_report.json`. Routing-only; clustering logic, prefer-audited
dedup, and `_detect_vendor_from_path` untouched; goldens byte-equal.

## What Was Built

### Task 1 - Dual-bucket read in _collect_xlsx_files (commit 68483f6)
- Derived `audit_root = output_dir / "AUDIT"` and `split_root = output_dir / "SPLIT"`
  inline at the top of `_collect_xlsx_files` (D-01).
- audited dict now rglobs `audit_root` for `*_annotated_audited.xlsx`, guarded by
  `if audit_root.is_dir() else []` (D-02 strict; missing bucket -> empty dict).
- annotated dict now rglobs `split_root` for `*_annotated.xlsx`, guarded by
  `if split_root.is_dir() else []`, keeping the `not p.stem.endswith("_annotated_audited")`
  filter (D-06 dual-bucket read).
- The prefer-audited stem dedup `audited.get(stem) or annotated[stem]` is preserved
  byte-for-byte (load-bearing behavior, unchanged).
- No whole-tree `output_dir.rglob` remains in the function; `load_candidate_rows` and
  `_detect_vendor_from_path` untouched (out of scope).

### Task 2 - Aggregates to AUDIT root (commit d45fe70)
- `cluster_summary.xlsx` write (was `output_dir / "cluster_summary.xlsx"`) is now
  `output_dir / "AUDIT" / "cluster_summary.xlsx"`, preceded by a defensive
  `(output_dir / "AUDIT").mkdir(parents=True, exist_ok=True)` in case cluster_audit runs
  before batch_audit created AUDIT (D-05, SC#3).
- `audit_report.json` cluster-merge read/update (was `output_dir / "audit_report.json"`)
  is now `output_dir / "AUDIT" / "audit_report.json"` (D-05). This is the critical merge
  target: the `json_path.exists()` check at :459 must find the file Plan 08-01's batch_audit
  writes at `AUDIT/audit_report.json`, otherwise the cluster section silently never merges.
  The read/merge logic (try/except JSONDecodeError, `report["clusters"]` assignment, write-back)
  is unchanged - only the path moved.

## Verification

- `python -c "import ast; ast.parse(...)"` exits 0 (final state).
- Dual-bucket bases + aggregate dests present (grep `output_dir / "(AUDIT|SPLIT)"`):
  lines 153 (AUDIT base), 154 (SPLIT base), 452-453 (cluster_summary.xlsx AUDIT dest +
  defensive mkdir), 458 (audit_report.json AUDIT dest).
- Prefer-audited dedup `audited.get(stem) or annotated[stem]` returns exactly 1 match (line 168).
- `is_dir()` guards present on both read bases (lines 157, 161).
- No whole-tree `output_dir.rglob("*_annotated...` remains in `_collect_xlsx_files` (grep empty).
- No bare-root aggregate writes remain: `output_dir / "cluster_summary.xlsx"` and
  `output_dir / "audit_report.json"` (without AUDIT) both grep empty.
- `_detect_vendor_from_path` not in the 2-commit diff (confirmed untouched per constraint).
- Full pytest gate deferred to Plan 08-03 (Wave 2), after test realignment - not run here
  per the plan's verification note.

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

None.

## Self-Check: PASSED

- spec_classifier/cluster_audit.py - FOUND
- .planning/phases/08-audit-routing-audit/08-02-SUMMARY.md - FOUND
- Commit 68483f6 - FOUND
- Commit d45fe70 - FOUND
