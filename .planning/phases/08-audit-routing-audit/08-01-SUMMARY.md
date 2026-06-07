---
phase: 08-audit-routing-audit
plan: 01
subsystem: batch-audit-routing
tags: [routing, batch_audit, SPLIT, AUDIT, dead-code-removal]
requires:
  - "Phase 7 bucket layout: SPLIT/<vendor>/<spec>/<stem>_annotated.xlsx (main.py routing)"
provides:
  - "batch_audit.py reads annotated input only from output_root/SPLIT/<vendor>/<spec>/"
  - "batch_audit.py writes <stem>_annotated_audited.xlsx to output_root/AUDIT/<vendor>/<spec>/ (SPLIT-mirror)"
  - "audit_report.json + audit_summary.xlsx written to output_root/AUDIT/ root"
affects:
  - "cluster_audit.py (Plan 08-02 dual-bucket read must find AUDIT/audit_report.json)"
  - "tests/test_batch_audit.py (Plan 08-02 path/layout + vendor-detection realignment)"
tech-stack:
  added: []
  patterns:
    - "SP-1 bucket-root derivation: SPLIT_root/AUDIT_root = output_dir / bucket"
    - "SP-2 relative_to(SPLIT_root) mirror remap for AUDIT write path"
    - "SP-3 one-segment / 'AUDIT' insertion for aggregate destinations"
key-files:
  created: []
  modified:
    - spec_classifier/batch_audit.py
decisions:
  - "D-01: --output-dir stays output_root; SPLIT/AUDIT roots derived inline in main() (no helper, no launcher edits)"
  - "D-02: strict SPLIT-only read with is_dir() guard -> [] on missing SPLIT (no whole-tree fallback)"
  - "D-03: AUDIT path = AUDIT_root / f.relative_to(SPLIT_root).parent / <stem>_audited.xlsx"
  - "D-04: overwrite-in-place via mkdir(parents=True, exist_ok=True); no rmtree / no create_spec_folder"
  - "D-05: audit_report.json + audit_summary.xlsx written to AUDIT/ root"
  - "D-07: dead {vendor}_run / hp_run / -TOTAL matchers removed; /{vendor}/ and \\{vendor}\\ retained"
metrics:
  duration: ~6min
  completed: 2026-06-07
---

# Phase 8 Plan 01: Audit routing (batch_audit) Summary

Re-pointed `batch_audit.py` at the Phase-7 three-bucket layout — reads annotated input
from `output_root/SPLIT/<vendor>/<spec>/`, writes the per-spec audited workbook to the
parallel `output_root/AUDIT/<vendor>/<spec>/` mirror, and emits `audit_report.json` +
`audit_summary.xlsx` to the `AUDIT/` root — and stripped the dead pre-Phase-7
`{vendor}_run` / `hp_run` / `-TOTAL` path matchers. Routing-only; no audit/E-code/
AI-mismatch/alias logic touched; goldens byte-equal.

## What Was Built

### Task 1 — Rebase read root to SPLIT + strip dead matchers (commit 74c7dda)
- `find_annotated_files` renamed its param to `split_root`, added a `if not
  split_root.is_dir(): return []` guard (D-02 strict, no whole-tree fallback), and
  rglobs `split_root` instead of the whole `output_dir`.
- Deleted the `-TOTAL` parent-folder exclusion line (D-07 — no TOTAL folders after
  Phase 7 ROUTE-05). Kept the defensive `"_audited" not in f.name` filter.
- `detect_vendor_from_path`: dropped the `f"{vendor}_run"` clause and the entire
  `hp_run -> hpe` alias block (D-07). Kept `/{vendor}/` and `\{vendor}\` (forward-
  compatible with the new SPLIT layout, Phase 7 D-01).
- `main()` now derives `SPLIT_root = output_dir / "SPLIT"` and `AUDIT_root =
  output_dir / "AUDIT"` inline (D-01; Claude's-discretion: chose inline over a helper,
  did NOT reuse `create_spec_folder` which rmtrees). The discovery call passes
  `SPLIT_root`; the file-list print uses `f.relative_to(SPLIT_root)` (cosmetic).

### Task 2 — Remap per-file out_path + aggregates to AUDIT root (commit 83f2eb7)
- Per-file write (was `f.parent / f"{f.stem}{args.suffix}.xlsx"`) now
  `AUDIT_root / f.relative_to(SPLIT_root).parent / f"{f.stem}{args.suffix}.xlsx"`
  followed by `out_path.parent.mkdir(parents=True, exist_ok=True)` (D-03 mirror, D-04
  overwrite-in-place, no rmtree). With `--suffix` default `_audited` and stem
  `<stem>_annotated`, the filename stays `<stem>_annotated_audited.xlsx` (SC#1).
- `audit_summary.xlsx` (writer line ~1027): `Path(output_dir) / "AUDIT" /
  "audit_summary.xlsx"` + defensive mkdir-parents (D-05).
- `audit_report.json` (`_generate_report`, line ~1290): `Path(output_dir) / "AUDIT" /
  "audit_report.json"` + defensive mkdir-parents (D-05).
- `_generate_human_report` (line 924, `Path(output_dir).rglob(f"{stem}_audited.xlsx")`)
  left byte-for-byte unchanged — deliberate non-change; still resolves because audited
  files remain under `output_dir` (now nested in AUDIT/).

## Verification

- `python -c "import ast; ast.parse(...)"` exits 0 (both tasks, final state).
- Dead matchers: `grep -nE 'f"{vendor}_run"|hp_run|-TOTAL'` returns NONE.
- `/{vendor}/` matcher retained (line 1361); `SPLIT` root derivation + rebased glob
  present (lines 1394, 1397, 1404).
- Per-file remap, `"AUDIT" / "audit_summary.xlsx"`, `"AUDIT" / "audit_report.json"` all
  present (Task 2 assertion block printed `OK`).
- No functional `rmtree` introduced — the only two "rmtree" substrings in the file are
  in my own explanatory comments (lines 1397, 1452); there is no `shutil.rmtree` call.
- `_generate_human_report` :924 rglob confirmed still present and unchanged.
- Full pytest gate is Plan 08-02 (Wave 2), after test realignment — not run here per
  the plan's verification note.

## Deviations from Plan

None - plan executed exactly as written. (Task 1 cosmetic discretion: chose inline
`SPLIT_root`/`AUDIT_root` derivation over a `_bucket_roots` helper, and switched the
file-list print to `relative_to(SPLIT_root)` — both explicitly Claude's-discretion per
CONTEXT lines 101/108.)

## Known Stubs

None.

## Self-Check: PASSED

- spec_classifier/batch_audit.py — FOUND
- .planning/phases/08-audit-routing-audit/08-01-SUMMARY.md — FOUND
- Commit 74c7dda — FOUND
- Commit 83f2eb7 — FOUND
