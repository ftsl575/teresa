---
status: partial
phase: 09-output-manifest-full-suite-verification
source: [09-VERIFICATION.md, 09-REVIEW.md]
started: 2026-06-07T00:00:00Z
updated: 2026-06-07T00:00:00Z
---

## Current Test

[awaiting human testing]

## Tests

### 1. Full 6-vendor real-data run against the new READY/SPLIT/AUDIT layout (D-09)
expected: Running the full pipeline (`main.py` → `batch_audit.py` → `cluster_audit.py`,
`--no-ai`) against the operator's populated INPUT for ALL six vendors (Dell, Cisco CCW,
HPE, Lenovo DCSC, xFusion, Huawei) yields, at `output_root`, exactly `READY/`, `SPLIT/`,
`AUDIT/`, and `README.md` — with no legacy flat per-run / `*_run` / `*-TOTAL` directories,
and the `README.md` manifest matching the artifacts actually produced. The automated
verifier confirmed all codepaths; the executor's recorded real-data run covered **Dell only**
(5 files, classify-only). The remaining 5 vendors + the full 3-process pipeline are unrun
because they require the operator's INPUT (integration tests skip when INPUT is absent).
result: [pending]

### 2. CR-01 decision — vendor-detection substring match on pathological paths
expected: Decide whether to accept or harden `detect_vendor_from_path`. Code review (CR-01,
BLOCKER) flagged that the unified function's full-path substring match (`/<vendor>/`) can
misattribute a vendor when a non-vendor path segment equals a vendor key (e.g. a Windows
username `C:\Users\dell\...`). This is the divergence **explicitly locked in CONTEXT.md
D-13(2)** (batch substring matching chosen deliberately, pathological-path divergence
accepted). It does NOT trigger for this operator (`C:\Users\G\`), and the canonical
`<bucket>/<vendor>/<spec>/` layout always makes `/<vendor>/` a real segment in production.
Options: (a) accept as the locked D-13 tradeoff [recommended], or (b) harden to
per-component exact matching (`vendor.lower() in [p.lower() for p in Path(path).parts]`)
as a follow-up — passes all existing tests, but overrides locked decision D-13(2).
result: resolved — user chose to harden. `detect_vendor_from_path` now uses right-to-left
per-component exact matching (commit `4894ba9`), so the real `<vendor>` segment near the file
wins over any vendor-named prefix segment. Regression test added (closes review IN-02). Full
suite 771 passed, goldens byte-equal. Consciously overrides locked decision D-13(2) per user
approval.

## Summary

total: 2
passed: 1
issues: 0
pending: 1
skipped: 0
blocked: 0

## Gaps
