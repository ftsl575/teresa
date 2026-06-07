---
phase: 07-bucket-layout-main-py-routing-ready-split
verified: 2026-06-07T17:45:00Z
status: passed
score: 5/5 must-haves verified
overrides_applied: 0
---

# Phase 7: Bucket Layout & main.py Routing (READY + SPLIT) Verification Report

**Phase Goal:** Establish the three-bucket `<bucket>/<vendor>/<spec>/` path scheme, route all `main.py` per-spec outputs into SPLIT and the `branded` workbook into READY (renamed), drop the per-run timestamp folder, and remove the TOTAL copy mechanism.
**Verified:** 2026-06-07T17:45:00Z
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths (ROADMAP § Phase 7 Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `READY/<vendor>/<spec>/Коммерческое предложение_<spec>.xlsx` exists and is byte-identical to old `<stem>_branded.xlsx` (D-07 guard intact) | VERIFIED | `main.py:176` constructs `ready_folder / f"Коммерческое предложение_{input_path.stem}.xlsx"`; `main.py:180` keeps `source_filename=input_path.name` unchanged — bytes are determined by source, not output path. The file is written to `ready_folder` via `create_spec_folder(output_dir, "READY", vendor, input_path.stem)`. |
| 2 | All nine `main.py` artifacts under `SPLIT/<vendor>/<spec>/`; no `run-<timestamp>-<stem>/` folder created | VERIFIED | `main.py:127`: `split_folder = create_spec_folder(output_dir, "SPLIT", vendor, input_path.stem)`. Lines 152–174 route all nine artifacts (rows_raw, rows_normalized, classification, unknown_rows, header_rows, run_summary, cleaned_spec, annotated, run.log) to `split_folder`. Grep confirms zero occurrences of `run_folder`, `vendor_run`, `session_stamp`, `get_session_stamp`, `create_run_folder` in main.py. |
| 3 | Re-running overwrites in place (wipe-first `create_spec_folder`) — no second timestamped dir | VERIFIED | `run_manager.py:29-31`: `if folder.exists(): shutil.rmtree(folder)` then `folder.mkdir(parents=True)` — no `exist_ok`. Wipe-first semantics guarantee no accumulation. |
| 4 | Batch mode produces no TOTAL folder; `run_manager.copy_to_total` and its call site are gone | VERIFIED | `run_manager.py` (32 lines) contains only `create_spec_folder`; `copy_to_total`, `create_total_folder`, `get_session_stamp` are absent (ImportError confirmed). `main.py:303`: batch preamble is a single log line with `output_root`; no `total_folder` variable anywhere in main.py. `main.py:341`: batch completion print says `Output: {output_dir}`. |
| 5 | pytest passes within the skip-gate (skipped/total < 0.50) with goldens byte-equal; READY+SPLIT path/layout tests updated | VERIFIED | Full suite: **774 passed, 1 xfailed, 0 failed, 0 skipped** (19.09s). Skip ratio: 0/774 = 0% — well within < 50% gate. `git diff golden/` shows no changes. `test_output_structure.py` asserts `SPLIT/dell/dl1/`, `READY/dell/dl1/Коммерческое предложение_dl1.xlsx`, and negative assertions for old `dell_run/`, `cisco_run/` paths. `test_cli.py` asserts `SPLIT/dell/dl1/`. |

**Score: 5/5 truths verified**

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `spec_classifier/src/diagnostics/run_manager.py` | Single export `create_spec_folder`; all dead timestamp/TOTAL helpers deleted | VERIFIED | 32 lines (was 72). Contains `def create_spec_folder(`, `shutil.rmtree(folder)`, `folder.mkdir(parents=True)`. No `get_session_stamp`, `create_run_folder`, `create_total_folder`, `copy_to_total`, `datetime` import. |
| `spec_classifier/main.py` | Routes all nine artifacts to `SPLIT/<vendor>/<spec>/` and branded to `READY/<vendor>/<spec>/` | VERIFIED | 367 lines (was 387). `create_spec_folder` imported line 18. `split_folder` + `ready_folder` created at lines 127-128. All nine artifact writes use `split_folder`. Branded path uses `ready_folder`. No dead symbols. |
| `spec_classifier/tests/test_output_structure.py` | Asserts new SPLIT/READY bucket structure; no old timestamp patterns | VERIFIED | No `import re`, no `RUN_FOLDER_PATTERN`, no `dell_run`, no `cisco_run`, no `run-*` glob. Contains `SPLIT`, `READY`, `Коммерческое предложение_`, negative assertions. 3 tests collect cleanly. |
| `spec_classifier/tests/test_cli.py` | Asserts artifacts in `SPLIT/dell/dl1/` | VERIFIED | Contains `split_folder = output_dir / "SPLIT" / "dell" / "dl1"`. No `dell_run`, no `run_folders`, no `run-*` glob. 1 test collected. |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `main.py` | `run_manager.py` | `from src.diagnostics.run_manager import create_spec_folder` | WIRED | Line 18 confirmed; `python -c "from src.diagnostics.run_manager import create_spec_folder; print('OK')"` exits 0. |
| `main.py` | `SPLIT/<vendor>/<spec>/` | `split_folder = create_spec_folder(output_dir, "SPLIT", vendor, input_path.stem)` | WIRED | Line 127 confirmed; all nine artifact writes use `split_folder`. |
| `main.py` | `READY/<vendor>/<spec>/Коммерческое предложение_<spec>.xlsx` | `ready_folder = create_spec_folder(output_dir, "READY", vendor, input_path.stem)` + `if adapter.generates_branded_spec()` gate | WIRED | Lines 128 + 175-182 confirmed. `source_filename=input_path.name` preserved (D-07). |
| `test_output_structure.py` | `SPLIT/dell/dl1/` | `split_folder = output_root / "SPLIT" / "dell" / stem` | WIRED | Line 60 confirmed. |
| `test_output_structure.py` | `READY/dell/dl1/Коммерческое предложение_dl1.xlsx` | `ready_folder = output_root / "READY" / "dell" / stem` | WIRED | Lines 61, 72-73 confirmed. |

---

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|--------------|--------|--------------------|--------|
| `main.py` `_run_single` | `split_folder`, `ready_folder` | `create_spec_folder(output_dir, ...)` at lines 127-128 | Yes — filesystem path, no hardcoded empty value | FLOWING |
| `main.py` branded block | `branded_path` | `ready_folder / f"Коммерческое предложение_{input_path.stem}.xlsx"` | Yes — gated on `adapter.generates_branded_spec()` | FLOWING |

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `create_spec_folder` importable | `python -c "from src.diagnostics.run_manager import create_spec_folder; print('OK')"` | `OK` | PASS |
| Dead symbol `get_session_stamp` raises ImportError | `python -c "from src.diagnostics.run_manager import get_session_stamp"` | `ImportError` | PASS |
| main.py importable | `python -c "import main; print('OK')"` | `OK` (inferred from pytest suite passing 774 tests) | PASS |
| Full pytest suite | `python -m pytest tests/ -q --tb=short` | `774 passed, 1 xfailed, 0 failed, 0 skipped` | PASS |
| No dead symbols in main.py | `grep "get_session_stamp\|create_run_folder\|total_folder\|run_folder\|vendor_run" main.py` | `NO MATCHES` | PASS |

---

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|-------------|---------------|-------------|--------|----------|
| LAYOUT-01 | 07-01, 07-02, 07-03 | Three-bucket `READY/`, `SPLIT/`, `AUDIT/` under `output_root` | SATISFIED (Phase 7 scope) | `create_spec_folder` establishes the bucket path scheme for READY and SPLIT. AUDIT bucket is Phase 8 scope — CONTEXT.md D-05 explicitly scopes AUDIT to Phase 8. LAYOUT-01 is a milestone-level requirement per CONTEXT.md; Phase 7 establishes the scheme. |
| LAYOUT-02 | 07-01, 07-02, 07-03 | Per-spec artifacts nested as `<bucket>/<vendor>/<spec>/` | SATISFIED | `create_spec_folder(output_root, bucket, vendor, spec)` constructs exact path. All artifact writes use `split_folder` or `ready_folder`. |
| LAYOUT-03 | 07-01, 07-02, 07-03 | No timestamp folder; re-run overwrites in place | SATISFIED | `run_manager.py` wipe-first logic. No `get_session_stamp`, no `create_run_folder` anywhere. |
| ROUTE-01 | 07-02, 07-03 | All nine artifacts in `SPLIT/<vendor>/<spec>/` | SATISFIED | `main.py:127` + lines 152-174. Nine artifacts confirmed routed to `split_folder`. |
| ROUTE-02 | 07-02, 07-03 | Branded workbook in `READY/<vendor>/<spec>/Коммерческое предложение_<spec>.xlsx` | SATISFIED | `main.py:176`. `source_filename=input_path.name` preserved (D-07). |
| ROUTE-05 | 07-01, 07-02 | TOTAL copy mechanism removed | SATISFIED | `copy_to_total` and `create_total_folder` deleted from run_manager; call site deleted from main.py; batch completion print updated. |

**Orphaned requirements check:** ROUTE-03, ROUTE-04 → Phase 8 (Pending, correct). MANIFEST-01, TEST-01 → Phase 9 (Pending, correct). No orphaned Phase 7 requirements.

**Traceability note:** REQUIREMENTS.md traceability table marks TEST-01 as Phase 9. Plan 03 does not claim TEST-01 in its `requirements:` field (it claims LAYOUT-01/02/03 and ROUTE-01/02). The test realignment work done in Phase 7 partially fulfills TEST-01 scope early; the full Phase 9 TEST-01 closure will cover full-suite milestone verification. The REQUIREMENTS.md checkbox for TEST-01 remains unchecked — consistent with Phase 9 scope. No gap.

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `main.py` | 240 | `--batch-dir` help text still says "Creates per-run folders + a TOTAL aggregation folder." | INFO | Stale argparse help string; no behavioral effect; noted as IN-01 in code review |
| `main.py` | 3 | Module docstring lists only Dell, Cisco CCW, HPE — missing Lenovo, Huawei, xFusion | INFO | Stale docstring; noted as IN-01 in code review |
| `tests/test_smoke.py` | 50 | `save_classification(classification_results, run_folder)` — two-argument call; three-argument production path untested | WARNING | Code review WR-02: backward-compat branch exercised, not production path. Pre-existing issue; not introduced by Phase 7. |
| `tests/test_smoke.py` | 68 | `st_size >= 0` — vacuously true assertion | INFO | Code review IN-02. Pre-existing weak assertion; not a Phase 7 regression. |
| `tests/test_output_structure.py` | 114-116 | Cisco no-branded assertion uses `or` short-circuit; passes vacuously when dir doesn't exist | WARNING | Code review WR-03. The production behavior (Cisco generates_branded_spec=False) is correct; assertion weakness doesn't hide a real failure, it hides a missing-dir case that is actually the correct outcome. Not a blocker. |
| `src/diagnostics/run_manager.py` | 28-31 | `shutil.rmtree` on path with unsanitized `spec` (= `input_path.stem`) | WARNING (CR-01 in review) | Security class: path traversal possible with crafted filename like `../../target.xlsx`. Not exploitable via the existing launcher or batch mode which uses trusted INPUT directories, but the function lacks a boundary check. Flagged as critical by code reviewer. |

**Stub classification:** No stubs in routing code. Anti-patterns at INFO/WARNING level; none prevent the Phase 7 goal from being achieved. CR-01 (rmtree unsanitized input) is a security concern flagged for a future phase.

---

### Cisco Adapter Deviation Assessment

**Change:** `cisco/adapter.py` `generates_branded_spec()` changed `True` → `False` during Plan 03.

**Verdict: ACCEPTABLE — latent bug fix within phase intent.**

Evidence:
- `base.py:13` docstring explicitly states: `"Whether this adapter produces branded spec output (e.g. Dell yes, Cisco no)."` — Cisco returning `True` was a contract violation against the base class documentation.
- The routing phase's introduction of the `if adapter.generates_branded_spec():` gate in main.py exposed the bug: with the old True value, Cisco would create a `READY/cisco/<stem>/Коммерческое предложение_<stem>.xlsx` file, violating the design intent.
- test_output_structure.py's negative assertion for Cisco READY output was correct per spec; the adapter was wrong. Fixing the adapter is the appropriate corrective action.
- The fix touches classification/normalization/audit logic? No — `generates_branded_spec()` is a routing control method on the adapter, not classification logic.
- Full suite passes (774 passed) after the fix, including the Cisco test assertions.
- The five CLAUDE.md critical business rules (power_cord hw_type=None, LOGISTIC=packaging only, BASE without device_type, is_factory_integrated=CONFIG, hw_type_rules.applies_to=[HW]) are unaffected — none involve branded spec generation.

**Routing-only invariant held:** The five commits in Phase 7 modify only `run_manager.py` (path helper), `main.py` (routing), `test_output_structure.py` (test paths), `test_cli.py` (test paths), `test_smoke.py` (import fix), and `cisco/adapter.py` (routing control boolean). No changes to `src/core/classifier.py`, `src/core/normalizer.py`, `src/rules/`, `batch_audit.py`, `cluster_audit.py`, or any YAML rules file. `git show` confirms this across all five commits.

---

### Human Verification Required

None. All must-have truths verified programmatically.

---

### Gaps Summary

No gaps. All five ROADMAP success criteria verified in the codebase. All six declared requirements (LAYOUT-01/02/03, ROUTE-01/02/05) satisfied. pytest suite is green (774 passed, 1 xfailed, 0 failed, 0 skipped). Goldens byte-equal. Routing-only invariant held.

Open items from code review (CR-01 rmtree path sanitization, WR-01 always-created READY dir, WR-02 smoke test save_classification, WR-03 Cisco assertion weakness, IN-01 stale docstrings, IN-02 vacuous size assertion) are code-quality findings for a future phase — none prevent Phase 7 goal achievement.

---

_Verified: 2026-06-07T17:45:00Z_
_Verifier: Claude (gsd-verifier)_
