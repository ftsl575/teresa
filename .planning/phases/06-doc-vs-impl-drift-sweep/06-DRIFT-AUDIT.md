# Phase 6 Drift Audit Log

**Created:** 2026-05-11
**Phase:** 06-doc-vs-impl-drift-sweep
**Sibling artifacts:** PLAN.md, CONTEXT.md, VERIFICATION.md, SUMMARY.md (per D-22)
**Sweep order:** D-14 — Group 1 (root) → Group 2 (DOCS_INDEX) → Group 3 (docs/dev) → Group 4 (docs/user) → Group 5 (other docs/) → Area A (.planning/codebase/ surgical patches).

## Purpose

Per-claim ledger for the Phase 6 mechanical drift sweep (DRIFT-01..04). Every "code does X" claim across the 16 in-scope files plus the 3 surgical-patch lines in `.planning/codebase/` is recorded here as one row, including `no_drift` rows so the log is a complete inventory of every claim considered (per Specifics + ROADMAP §SC-5 "every file checked, every claim flagged, and the resolution for each").

`resolution` ∈ `{remove, patch, no_drift}`. Default per D-13 is `remove`; `patch` only when the claim is load-bearing for the reader's mental model AND the patched form is itself stable (symbol/section ref, not a line number).

Categories swept (per D-11):
1. Path/file existence + behavior claims (highest load-bearing — class that broke v1.0).
2. Switch/CLI flag claims.
3. Line-number refs (`file.py:N`) — apply remove > patch aggressively; rewrite to symbol/section refs.

Categories DEFERRED per D-12 (folded into v1.2 `/gsd-map-codebase` refresh; if encountered in-scope, REMOVE):
- Volatile counts: test count, LOC counts, rule_id counts, vendor count.

## Audit Table

| file | line | claim_summary | check_command | resolution |
|------|------|---------------|---------------|------------|
| README.md | 4-5 | "six vendors: Dell, Cisco CCW, HPE, Lenovo (DCSC), xFusion, Huawei" | `grep -E '"(dell\|cisco\|hpe\|lenovo\|huawei\|xfusion)"' run.ps1` (line 71 `$ALL_VENDORS`) | no_drift |
| README.md | 16-17 | "`run.ps1` (PowerShell orchestrator), `teresa.bat`, `teresa_gui.py` (PyQt6 GUI) at repo root" | `test -f run.ps1 && test -f teresa.bat && test -f teresa_gui.py` | no_drift |
| README.md | 19-22 | "`spec_classifier/` contains main.py, batch_audit.py, cluster_audit.py, src/, rules/, tests/, golden/, docs/" | `test -f spec_classifier/main.py && test -f spec_classifier/batch_audit.py && test -f spec_classifier/cluster_audit.py && test -d spec_classifier/src && test -d spec_classifier/rules && test -d spec_classifier/tests && test -d spec_classifier/golden && test -d spec_classifier/docs` | no_drift |
| README.md | 28 | "Python 3.10+" | per PROJECT.md Constraints "CPython 3.10"; spec_classifier/requirements.txt deps pinned compatible | no_drift |
| README.md | 39 | "`pip install -r spec_classifier\requirements.txt`" | `test -f spec_classifier/requirements.txt` | no_drift |
| README.md | 42 | "Copy-Item spec_classifier\config.local.yaml.example spec_classifier\config.local.yaml" | `test -f spec_classifier/config.local.yaml.example` | no_drift |
| README.md | 45-46 | "Defaults: INPUT = %USERPROFILE%\\Desktop\\INPUT\\, OUTPUT = %USERPROFILE%\\Desktop\\OUTPUT\\" | `grep -E 'USERPROFILE.Desktop.(INPUT\|OUTPUT)' run.ps1` (lines 34-35) | no_drift |
| README.md | 52 | "`.\\run.ps1` runs all 6 vendors + audits + pytest" | `grep -E 'ALL_VENDORS\|batch_audit\|cluster_audit\|pytest' run.ps1` (sections 2-5 in run.ps1) | no_drift |
| README.md | 53 | "`.\\run.ps1 -Vendor huawei -NoAi -SkipTests`" | `grep -E '\$Vendor\|\$NoAi\|\$SkipTests' run.ps1` (param block lines 14-20) | no_drift |
| README.md | 56 | "OUTPUT layout `%USERPROFILE%\\Desktop\\OUTPUT\\<vendor>_run\\run-YYYY-MM-DD__HH-MM-SS-<stem>\\`" | matches spec_classifier/CLAUDE.md § OUTPUT layout (lines 64-66) | no_drift |
| README.md | 67 | "`.\\run.ps1` Full pipeline + rule audit + AI audit + cluster + pytest" | `grep -E 'batch_audit\.py.*--no-ai\|batch_audit\.py.*--model\|cluster_audit\.py' run.ps1` | no_drift |
| README.md | 68 | "`.\\run.ps1 -NoAi` skips AI audit" | `grep -A2 'if \(-not \$NoAi\)' run.ps1` (lines 106, 151 guard AI invocation) | no_drift |
| README.md | 69 | "`.\\run.ps1 -Vendor <dell\|cisco\|hpe\|lenovo\|huawei\|xfusion>` one vendor end-to-end" | `grep '"dell", "cisco", "hpe", "lenovo", "huawei", "xfusion"' run.ps1` (line 71) | no_drift |
| README.md | 70 | "`.\\run.ps1 -TestsOnly` pytest only" | `grep -A3 'if \(\$TestsOnly\)' run.ps1` (lines 98-103) | no_drift |
| README.md | 71 | "`.\\run.ps1 -SkipTests` Full run without pytest at the end" | `grep -A1 'if \(-not \$SkipTests\)' run.ps1` (line 171) | no_drift |
| README.md | 72 | "double-click `teresa.bat` Launches the PyQt6 GUI" | `test -f teresa.bat && test -f teresa_gui.py` | no_drift |
| README.md | 75 | "spec_classifier/README.md exists for direct CLI invocation" | `test -f spec_classifier/README.md` | no_drift |
| README.md | 81-82 | "Two-layer YAML overlay: spec_classifier/config.yaml + spec_classifier/config.local.yaml" | `test -f spec_classifier/config.yaml && test -f spec_classifier/config.local.yaml.example` | no_drift |
| README.md | 91-99 | "Vendor support table: Dell sentinel `Module Name`; Cisco sheet `Price Estimate`; HPE sheet `BOM`; Lenovo sheet `Configuration`; xFusion `Configuration Name`/`Component Type`; Huawei `Material Code`/`Description`" | per spec_classifier/CLAUDE.md § Project (vendors) and per-vendor adapter docs; D-22 protected — read-only verification via existing docs/code references | no_drift |
| README.md | 101 | "see spec_classifier/docs/taxonomy/hw_type_taxonomy.md" | `test -f spec_classifier/docs/taxonomy/hw_type_taxonomy.md` | no_drift |
| README.md | 109 | "spec_classifier/README.md — Full CLI reference, golden workflow, troubleshooting" | `test -f spec_classifier/README.md` | no_drift |
| README.md | 110 | "spec_classifier/CLAUDE.md — Pipeline internals, E-codes, business rules, dev cycle" | `test -f spec_classifier/CLAUDE.md` | no_drift |
| README.md | 111 | "LAUNCHER_README.md — Launcher flags, GUI behavior" | `test -f LAUNCHER_README.md` | no_drift |
| README.md | 112 | "spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md — Adding a new vendor" | `test -f spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md` | no_drift |
| README.md | 113 | "spec_classifier/docs/rules/RULES_AUTHORING_GUIDE.md — Rules authoring" | `test -f spec_classifier/docs/rules/RULES_AUTHORING_GUIDE.md` | no_drift |
| README.md | 114 | "spec_classifier/CHANGELOG.md — Recent changes" | `test -f spec_classifier/CHANGELOG.md` | no_drift |
| README.md | 115 | ".planning/STATE.md — Project status / current focus" | `test -f .planning/STATE.md` | no_drift |
| README.md | 121 | "Tests live in `spec_classifier/tests/`. Run from `spec_classifier/`" | `test -d spec_classifier/tests && test -f spec_classifier/conftest.py` | no_drift |
| README.md | 125 | "`pytest tests/ -v --tb=short` full suite" | standard pytest invocation; `test -d spec_classifier/tests` | no_drift |
| README.md | 126 | "`pytest tests/test_rules_unit.py tests/test_state_detector.py tests/test_normalizer.py` unit-only (no INPUT files needed)" | `test -f spec_classifier/tests/test_rules_unit.py && test -f spec_classifier/tests/test_state_detector.py && test -f spec_classifier/tests/test_normalizer.py` | no_drift |
| README.md | 129 | "session fails if `skipped/total > 0.50` or `passed == 0`" | `grep -E 'MAX_SKIP_RATIO\|skipped/total' spec_classifier/conftest.py` (D-22 protected — read-only; matches CONTRIBUTING.md § Skip-ratio gate) | no_drift |

<!-- Rows appended by Plans 01-05 below this line. -->

## Tally (filled by Plan 06)

- Total claims swept: TBD
- Resolutions: TBD remove / TBD patch / TBD no_drift
- Files touched: TBD of 19 (16 in-scope + 3 surgical map lines)
- Drift remaining post-phase: 0 (per ROADMAP §SC-1)
