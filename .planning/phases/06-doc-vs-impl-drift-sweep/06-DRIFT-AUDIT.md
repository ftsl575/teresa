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
| CLAUDE.md | 9 | "Repo root is a thin Windows launcher (`run.ps1`, `teresa_gui.py`, `teresa.bat`)" | `test -f run.ps1 && test -f teresa_gui.py && test -f teresa.bat` | no_drift |
| CLAUDE.md | 11-13 | "`spec_classifier/` is the actual codebase: deterministic, rule-based Excel-spec classifier for six hardware vendors (Dell, Cisco CCW, HPE, Lenovo DCSC, xFusion, Huawei)" | `grep '"dell", "cisco", "hpe", "lenovo", "huawei", "xfusion"' run.ps1` (line 71) | no_drift |
| CLAUDE.md | 17 | "deeper reference … lives in `spec_classifier/CLAUDE.md`" | `test -f spec_classifier/CLAUDE.md` | no_drift |
| CLAUDE.md | 25-26 | "Default external roots (Windows): `%USERPROFILE%\\Desktop\\INPUT`, `%USERPROFILE%\\Desktop\\OUTPUT`, venv at `C:\\venv`" | `grep -E 'USERPROFILE.Desktop.(INPUT\|OUTPUT)' run.ps1` (lines 34-35); venv `C:\\venv` is suggestion per README:85 | no_drift |
| CLAUDE.md | 27 | "override via `spec_classifier/config.local.yaml`, gitignored; copy from `config.local.yaml.example`" | `test -f spec_classifier/config.local.yaml.example && grep -q 'spec_classifier/config.local.yaml' .gitignore` | no_drift |
| CLAUDE.md | 28-29 | "`OUTPUT/`, `output/`, `test_data/`, `.venv/`, `commits.txt`, and `*.zip` are gitignored" | `grep -E '^(OUTPUT/\|output/\|test_data/\|\.venv/\|commits\.txt\|\*\.zip)$' .gitignore` returns 6 matches | no_drift |
| CLAUDE.md | 36-40 | "`power_cord` has `hw_type=None` intentionally. Absent from `device_type_map` in every vendor YAML, with explicit comments. `batch_audit.py:_E8_NO_HW_TYPE_DEVICES = {\"power_cord\", \"enablement_kit\"}` excludes it from E8" | `grep -n '_E8_NO_HW_TYPE_DEVICES = {\"power_cord\", \"enablement_kit\"}' spec_classifier/batch_audit.py` (line 506); `grep -n 'intentionally unmapped' spec_classifier/rules/dell_rules.yaml` (line 278); D-22 read-only | no_drift |
| CLAUDE.md | 38 | "`batch_audit.py:_E8_NO_HW_TYPE_DEVICES`" — symbol ref (D-11 cat #3 line-ref) | symbol-ref form (no line number); stable per D-13 patched-form rule | no_drift |
| CLAUDE.md | 40 | "`power_cord ≈ cable` alias in `batch_audit.DEVICE_TYPE_ALIASES` is only for AI-mismatch suppression" | `grep -n 'DEVICE_TYPE_ALIASES' spec_classifier/batch_audit.py` (line 363); matches spec_classifier/CLAUDE.md § device_type Aliases | no_drift |
| CLAUDE.md | 42-43 | "LOGISTIC = packaging, documents, freight only. Power cords, stacking cables, rails, brackets are HW, not LOGISTIC" | matches spec_classifier/CLAUDE.md § Business Rules (lines 131-132); rule-policy claim, validated by source-of-truth doc | no_drift |
| CLAUDE.md | 45-47 | "BASE without `device_type` is normal (E15 = INFO). BASE with `device_type` is valid; E6/E10 must not fire. Only `hw_type` on BASE triggers E10" | matches spec_classifier/CLAUDE.md § Business Rules (lines 142-144) and E-codes table E6/E10/E15 | no_drift |
| CLAUDE.md | 49 | "`is_factory_integrated=True` rows are CONFIG; AI does not check them" | matches spec_classifier/CLAUDE.md § Business Rules (line 146) | no_drift |
| CLAUDE.md | 51 | "`hw_type_rules.applies_to` is `[HW]` only — never `[HW, BASE]`" | matches spec_classifier/CLAUDE.md § Business Rules (line 148) | no_drift |
| CLAUDE.md | 53-54 | "YAML rule order is also load-bearing — first-match-wins. Reordering rule blocks during cosmetic edits can silently flip classification" | matches PROJECT.md § Constraints + CONCERNS.md BLOCKER | no_drift |
| CLAUDE.md | 60 | "table row: Pipeline stages, E-codes, alias-table semantics, dev cycle → `spec_classifier/CLAUDE.md`" | `test -f spec_classifier/CLAUDE.md` | no_drift |
| CLAUDE.md | 61 | "Run a vendor end-to-end on Windows → `run.ps1`, `LAUNCHER_README.md`" | `test -f run.ps1 && test -f LAUNCHER_README.md` | no_drift |
| CLAUDE.md | 62 | "Vendor adapter contract → `spec_classifier/src/vendors/base.py`" | `test -f spec_classifier/src/vendors/base.py && grep -q 'class VendorAdapter' spec_classifier/src/vendors/base.py` (line 5) | no_drift |
| CLAUDE.md | 63 | "Add a new vendor → `spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md`" | `test -f spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md` | no_drift |
| CLAUDE.md | 64 | "Rules authoring → `spec_classifier/docs/rules/RULES_AUTHORING_GUIDE.md`, `spec_classifier/docs/taxonomy/hw_type_taxonomy.md`" | `test -f spec_classifier/docs/rules/RULES_AUTHORING_GUIDE.md && test -f spec_classifier/docs/taxonomy/hw_type_taxonomy.md` | no_drift |
| CLAUDE.md | 65 | "Recent changes → `spec_classifier/CHANGELOG.md`" | `test -f spec_classifier/CHANGELOG.md` | no_drift |
| CLAUDE.md | 66 | "Project status / current focus → `.planning/STATE.md`" | `test -f .planning/STATE.md` | no_drift |
| CLAUDE.md | 67 | "Tech-debt items NOT to fix → `.planning/codebase/CONCERNS.md` (BLOCKER + IMPORTANT sections)" | `test -f .planning/codebase/CONCERNS.md` | no_drift |
| CLAUDE.md | 71-72 | "The repo carries a `.cursor/` tree (gitignored) used by the GSD workflow when driving from Cursor" | `grep -q '^\.cursor/' .gitignore` (line 48); .cursor/ removed in Phase 5 ORPH-04 from working tree but rule entry remains valid for any local re-creation | no_drift |
| CLAUDE.md | 73-74 | "canonical development cycle (Discuss → Plan → Execute → Verify, GSD-native) is documented in `/CONTRIBUTING.md`" | `test -f CONTRIBUTING.md && grep -E 'Discuss\|Plan\|Execute\|Verify' CONTRIBUTING.md` (lines 17-27) | no_drift |
| CONTRIBUTING.md | 4-5 | "six hardware vendors (Dell, Cisco CCW, HPE, Lenovo DCSC, xFusion, Huawei). Repo is two things stacked: thin Windows launcher (`run.ps1`, `teresa_gui.py`, `teresa.bat`) and `spec_classifier/`" | `grep '"dell", "cisco", "hpe", "lenovo", "huawei", "xfusion"' run.ps1` (line 71); `test -f run.ps1 && test -f teresa_gui.py && test -f teresa.bat` | no_drift |
| CONTRIBUTING.md | 17-27 | "GSD-native cycle: 1. Discuss `/gsd-discuss-phase`, 2. Plan `/gsd-plan-phase`, 3. Execute `/gsd-execute-phase`, 4. Verify `/gsd-verify-work`. Produces NN-CONTEXT/NN-PP-PLAN/NN-PP-SUMMARY/NN-VERIFICATION.md" | matches PROJECT.md cycle convention; commands are GSD framework deliverables (not in-tree code) | no_drift |
| CONTRIBUTING.md | 29-30 | "`/gsd-help` for the full command list" | GSD framework command (not in-tree code); matches CONTRIBUTING.md cycle docs | no_drift |
| CONTRIBUTING.md | 32-34 | "Phase artifacts under `.planning/phases/NN-<name>/`. Cross-phase artifacts (`PROJECT.md`, `REQUIREMENTS.md`, `ROADMAP.md`, `STATE.md`, `codebase/*.md`) live at `.planning/`" | `test -d .planning/phases && test -f .planning/PROJECT.md && test -f .planning/REQUIREMENTS.md && test -f .planning/ROADMAP.md && test -f .planning/STATE.md && test -d .planning/codebase` | no_drift |
| CONTRIBUTING.md | 45-46 | "Run pytest from `spec_classifier/` (test config and session-finish hook in `spec_classifier/conftest.py`)" | `test -f spec_classifier/conftest.py && grep -q 'pytest_sessionfinish' spec_classifier/conftest.py` | no_drift |
| CONTRIBUTING.md | 49-51 | "`pytest tests/ -v --tb=short`, `pytest tests/test_lenovo_rules_unit.py -v`, `pytest -k \"lenovo and parser\" -v`" | `test -f spec_classifier/tests/test_lenovo_rules_unit.py` | no_drift |
| CONTRIBUTING.md | 57-58 | "`.\\run.ps1 -TestsOnly` short-circuit, only pytest; `.\\run.ps1 -SkipTests` full pipeline, skip pytest at end" | `grep -E '\$TestsOnly\|\$SkipTests' run.ps1` (params lines 17-18; sections lines 98, 171) | no_drift |
| CONTRIBUTING.md | 62-67 | "`spec_classifier/conftest.py:pytest_sessionfinish` forces session FAIL if `skipped/total > 0.50` or if `passed == 0` or if `input_root` is missing entirely (`MAX_SKIP_RATIO = 0.50`)" | `grep -n 'MAX_SKIP_RATIO = 0.50' spec_classifier/conftest.py` (line 14); D-22 read-only | no_drift |
| CONTRIBUTING.md | 69-73 | "`spec_classifier/golden/*_expected.jsonl` is regression contract — any rule edit MUST update affected golden via `python main.py --vendor <v> --update-golden`. See `spec_classifier/docs/dev/TESTING_GUIDE.md`" | `test -d spec_classifier/golden && grep -q 'update-golden' spec_classifier/main.py` (line 267); `test -f spec_classifier/docs/dev/TESTING_GUIDE.md` | no_drift |
| CONTRIBUTING.md | 77 | "See `spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md` for full adapter contract, parser/normalizer scaffold, golden workflow" | `test -f spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md` | no_drift |
| CONTRIBUTING.md | 83-86 | "new vendor adds `src/vendors/<v>/{adapter.py, parser.py, normalizer.py}` triplet, `rules/<v>_rules.yaml`, registers `\"<v>\"` in `\$ALL_VENDORS` in `run.ps1`, moves `\"<v>\"` from `VENDORS_DISABLED` to `VENDORS_ACTIVE` in `teresa_gui.py`, ships `golden/<v>1_expected.jsonl`" | `grep -n '\$ALL_VENDORS' run.ps1` (line 71); `grep -n 'VENDORS_ACTIVE\|VENDORS_DISABLED' teresa_gui.py` (lines 38-39) | no_drift |
| CONTRIBUTING.md | 90-99 | "Commit messages follow `<type>(<phase>-<plan>): <subject>` pattern; common types feat/fix/docs/chore/refactor/test; reference requirement IDs (HYG-01, DOC-04, WF-02)" | matches actual git log convention through Phase 5 (e.g., `chore(05): T5 remove teresa.zip from working tree`); D-21 reaffirms for Phase 6 | no_drift |
| CONTRIBUTING.md | 94 | "docs(02-01): translate spec_classifier/CLAUDE.md to English + dedup root CLAUDE.md" | historical commit example per D-18 historical-content convention; preserved as illustrative pattern, not a current-state claim | no_drift |
| CONTRIBUTING.md | 95 | "chore(03-01): retire spec_classifier/prompts/ to archive + repoint LAUNCHER_README" | historical commit example per D-18; preserved | no_drift |
| CONTRIBUTING.md | 96 | "fix(02-04): tighten paragraph X (DOC-02)" | historical commit example per D-18; preserved | no_drift |
| CONTRIBUTING.md | 102-104 | "One commit per task. Failed task is recovered by NEW follow-up commit, not `git commit --amend`" | matches v1.0/Phase-3/Phase-5 atomic-commit convention; D-21 reaffirms | no_drift |
| CONTRIBUTING.md | 106-108 | "One requirement per phase-closing commit. Phase wrap-up commits group artifacts by requirement (one commit per `HYG-NN`/`DOC-NN`/`WF-NN`) so any individual requirement is atomically revertable" | convention claim; matches Phase 3/5 closure pattern | no_drift |
| CONTRIBUTING.md | 112 | "PR description should reference the phase SUMMARY (`.planning/phases/NN-<name>/NN-SUMMARY.md`)" | path pattern; per-phase SUMMARY artifact present in 01..05 phase dirs | no_drift |
| CONTRIBUTING.md | 121-126 | "PEP 8, 4-space indent. Project-specific rule-authoring style lives in `spec_classifier/docs/rules/RULES_AUTHORING_GUIDE.md`" | `test -f spec_classifier/docs/rules/RULES_AUTHORING_GUIDE.md` | no_drift |
| CONTRIBUTING.md | 135 | "`power_cord` has `hw_type=None` intentionally. Recovery commit `c3c7cb6 fix(taxonomy): restore power_cord hw_type=None` exists. Do NOT add it to `device_type_map` or remove it from `_E8_NO_HW_TYPE_DEVICES`" | `git log --oneline --all \| grep c3c7cb6`; `grep -n '_E8_NO_HW_TYPE_DEVICES' spec_classifier/batch_audit.py` (line 506) | no_drift |
| CONTRIBUTING.md | 136 | "`spec_classifier/src/core/parser.py` is Dell-specific despite living in `core/`. Sentinel `\"Module Name\"` is hard-coded; other vendors use their own `parser.py` under `src/vendors/<v>/`" | matches spec_classifier/CLAUDE.md § Known Tech Debt #7 (line 234-235); matches CONCERNS.md BLOCKER section | no_drift |
| CONTRIBUTING.md | 137 | "`spec_classifier/batch_audit.py` reads from `*_annotated.xlsx` instead of `classification.jsonl`. Excel leakage; needs dedicated migration" | matches spec_classifier/CLAUDE.md § Known Tech Debt #1 (line 223); CONCERNS.md BLOCKER | no_drift |
| CONTRIBUTING.md | 138 | "YAML rule order is load-bearing (first-match-wins). Never `sort` rule blocks alphabetically. Cosmetic reorders silently flip classification" | matches PROJECT.md § Constraints + CONCERNS.md BLOCKER + CLAUDE.md root | no_drift |
| CONTRIBUTING.md | 139 | "`HW_TYPE_VOCAB` is duplicated between `classifier.py` and `batch_audit.py`. Tracked in CONCERNS.md but not selected for cleanup milestones" | matches spec_classifier/CLAUDE.md § Known Tech Debt and CONCERNS.md IMPORTANT | no_drift |
| CONTRIBUTING.md | 141 | "Full rationale and context: `.planning/codebase/CONCERNS.md` § BLOCKER + IMPORTANT" | `test -f .planning/codebase/CONCERNS.md && grep -E '^## (BLOCKER\|IMPORTANT)' .planning/codebase/CONCERNS.md` | no_drift |
| CONTRIBUTING.md | 147 | "table: Pipeline stages, E-codes, alias-table semantics → `spec_classifier/CLAUDE.md`" | `test -f spec_classifier/CLAUDE.md` | no_drift |
| CONTRIBUTING.md | 148 | "5 critical business rules at a glance → `CLAUDE.md`" | `test -f CLAUDE.md && grep -q 'Critical business rules' CLAUDE.md` (line 31) | no_drift |
| CONTRIBUTING.md | 149 | "Run a vendor end-to-end on Windows → `run.ps1`, `LAUNCHER_README.md`" | `test -f run.ps1 && test -f LAUNCHER_README.md` | no_drift |
| CONTRIBUTING.md | 150 | "Vendor adapter contract → `spec_classifier/src/vendors/base.py`" | `test -f spec_classifier/src/vendors/base.py && grep -q 'class VendorAdapter' spec_classifier/src/vendors/base.py` (line 5) | no_drift |
| CONTRIBUTING.md | 151 | "Add a new vendor → `spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md`" | `test -f spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md` | no_drift |
| CONTRIBUTING.md | 152 | "Rules authoring → `spec_classifier/docs/rules/RULES_AUTHORING_GUIDE.md`, `spec_classifier/docs/taxonomy/hw_type_taxonomy.md`" | `test -f spec_classifier/docs/rules/RULES_AUTHORING_GUIDE.md && test -f spec_classifier/docs/taxonomy/hw_type_taxonomy.md` | no_drift |
| CONTRIBUTING.md | 153 | "Recent changes → `spec_classifier/CHANGELOG.md`" | `test -f spec_classifier/CHANGELOG.md` | no_drift |
| CONTRIBUTING.md | 154 | "Project status / current focus → `.planning/STATE.md`" | `test -f .planning/STATE.md` | no_drift |
| CONTRIBUTING.md | 155 | "Tech-debt items NOT to fix → `.planning/codebase/CONCERNS.md` (BLOCKER + IMPORTANT sections)" | `test -f .planning/codebase/CONCERNS.md` | no_drift |
| spec_classifier/docs/DOCS_INDEX.md | 8 | "`docs/product/` Normative. Architecture, baseline, data pipeline" | `test -d spec_classifier/docs/product` | no_drift |
| spec_classifier/docs/DOCS_INDEX.md | 9 | "`docs/user/` Normative. User guide, CLI reference. How to operate the tool" | `test -d spec_classifier/docs/user` | no_drift |
| spec_classifier/docs/DOCS_INDEX.md | 10 | "`docs/schemas/` Normative. Data contracts: field specs for all output formats" | `test -d spec_classifier/docs/schemas` | no_drift |
| spec_classifier/docs/DOCS_INDEX.md | 11 | "`docs/rules/` Normative. Rules authoring guide" | `test -d spec_classifier/docs/rules` | no_drift |
| spec_classifier/docs/DOCS_INDEX.md | 12 | "`docs/dev/` Normative. Contributing, testing, operational notes" | `test -d spec_classifier/docs/dev` | no_drift |
| spec_classifier/docs/DOCS_INDEX.md | 13 | "`docs/taxonomy/` Normative. Source of truth for controlled vocabularies (e.g., hw_type)" | `test -d spec_classifier/docs/taxonomy` | no_drift |
| spec_classifier/docs/DOCS_INDEX.md | 18 | "`README.md` — How do I install and run this?" | `test -f README.md` (root README) | no_drift |
| spec_classifier/docs/DOCS_INDEX.md | 19 | "`docs/user/USER_GUIDE.md` — How do I interpret the output?" | `test -f spec_classifier/docs/user/USER_GUIDE.md` | no_drift |
| spec_classifier/docs/DOCS_INDEX.md | 20 | "`docs/user/CLI_CONFIG_REFERENCE.md` — What are all CLI options and config keys?" | `test -f spec_classifier/docs/user/CLI_CONFIG_REFERENCE.md` | no_drift |
| spec_classifier/docs/DOCS_INDEX.md | 21 | "`docs/user/RUN_PATHS_AND_IO_LAYOUT.md` — Where do inputs/outputs go? Default paths (Desktop INPUT/OUTPUT), vendor run layout, no TEMP" | `test -f spec_classifier/docs/user/RUN_PATHS_AND_IO_LAYOUT.md` (Plan 02 will sweep contents per D-14 Group 4) | no_drift |
| spec_classifier/docs/DOCS_INDEX.md | 22 | "`docs/schemas/DATA_CONTRACTS.md` — What are the exact output schemas?" | `test -f spec_classifier/docs/schemas/DATA_CONTRACTS.md` | no_drift |
| spec_classifier/docs/DOCS_INDEX.md | 23 | "`docs/rules/RULES_AUTHORING_GUIDE.md` — How do I add or change a rule safely?" | `test -f spec_classifier/docs/rules/RULES_AUTHORING_GUIDE.md` | no_drift |
| spec_classifier/docs/DOCS_INDEX.md | 24 | "`docs/dev/NEW_VENDOR_GUIDE.md` — How do I add a new vendor (adapter, rules, tests)?" | `test -f spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md` | no_drift |
| spec_classifier/docs/DOCS_INDEX.md | 25 | "`docs/dev/ONE_BUTTON_RUN.md` — How do I run tests and batch with one script (Windows)?" | `test -f spec_classifier/docs/dev/ONE_BUTTON_RUN.md` | no_drift |
| spec_classifier/docs/DOCS_INDEX.md | 26 | "`docs/dev/TESTING_GUIDE.md` — How do I run tests and update golden?" | `test -f spec_classifier/docs/dev/TESTING_GUIDE.md` | no_drift |
| spec_classifier/docs/DOCS_INDEX.md | 27 | "`docs/dev/OPERATIONAL_NOTES.md` — How do I run batch jobs and manage artifacts?" | `test -f spec_classifier/docs/dev/OPERATIONAL_NOTES.md` | no_drift |
| spec_classifier/docs/DOCS_INDEX.md | 28 | "`docs/product/TECHNICAL_OVERVIEW.md` — How does the pipeline work internally?" | `test -f spec_classifier/docs/product/TECHNICAL_OVERVIEW.md` | no_drift |
| spec_classifier/docs/DOCS_INDEX.md | 29 | "`CHANGELOG.md` — What changed in each version?" | `test -f spec_classifier/CHANGELOG.md` (DOCS_INDEX cwd-relative; refers to spec_classifier/CHANGELOG.md) | no_drift |
| spec_classifier/docs/DOCS_INDEX.md | 30 | "`docs/taxonomy/hw_type_taxonomy.md` — What are the allowed hw_type values and the exact meaning/boundaries?" | `test -f spec_classifier/docs/taxonomy/hw_type_taxonomy.md` | no_drift |
| spec_classifier/docs/DOCS_INDEX.md | 31 | "`docs/taxonomy/cycle2_summary.md` — What device_type changes were made in cycle 2 (PR-8–PR-11)?" | `test -f spec_classifier/docs/taxonomy/cycle2_summary.md` | no_drift |
| spec_classifier/docs/DOCS_INDEX.md | 32 | "`batch_audit.py` — How do I run post-pipeline rule checks (E1–E18) and LLM verification across all vendor outputs?" | `test -f spec_classifier/batch_audit.py` | no_drift |
| spec_classifier/docs/DOCS_INDEX.md | 33 | "`cluster_audit.py` — How do I cluster unclassified/UNKNOWN rows to discover new rules?" | `test -f spec_classifier/cluster_audit.py` | no_drift |
| spec_classifier/docs/DOCS_INDEX.md | 34 | "`CLAUDE.md` — Project context for Cowork / Claude Desktop sessions" | `test -f spec_classifier/CLAUDE.md` (DOCS_INDEX cwd-relative; refers to spec_classifier/CLAUDE.md, not root) | no_drift |
| spec_classifier/docs/DOCS_INDEX.md | 38-39 | "Normative docs (product/, user/, schemas/, rules/, dev/, taxonomy/) must stay in sync with code. Update docs in the same commit as any behavior change" | convention claim; matches CONTRIBUTING.md PR workflow | no_drift |
| spec_classifier/docs/DOCS_INDEX.md | 41 | "Repo-root contributor doc: see `/CONTRIBUTING.md` for the GSD-native development cycle and contribution rules" | `test -f CONTRIBUTING.md` | no_drift |

<!-- Rows appended by Plans 01-05 below this line. -->
| spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md | 10-12 | "Create: src/vendors/<vendor>/__init__.py, adapter.py, rules/<vendor>_rules.yaml" | `test -d spec_classifier/src/vendors && test -d spec_classifier/rules` | no_drift |
| spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md | 13-14 | "tests/test_regression_<vendor>.py and tests/test_unknown_threshold_<vendor>.py based on cisco templates" | `test -f spec_classifier/tests/test_regression_cisco.py && test -f spec_classifier/tests/test_unknown_threshold_cisco.py` | no_drift |
| spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md | 15 | "Test data in C:\\Users\\<USERNAME>\\Desktop\\INPUT\\ (e.g. <vendor>_1.xlsx); not stored in the repo" | matches Phase 5 HYG-01 USERNAME convention; INPUT root configurable via config.local.yaml | no_drift |
| spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md | 16 | "Golden files: golden/<stem>_expected.jsonl (generated via --save-golden)" | `test -d spec_classifier/golden && grep -q 'save-golden' spec_classifier/main.py` (line 266) | no_drift |
| spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md | 19 | "main.py — one line in VENDOR_REGISTRY" | `grep -q 'VENDOR_REGISTRY' spec_classifier/main.py` (D-22 read-only) | no_drift |
| spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md | 20 | "config.yaml — one line in vendor_rules" | `grep -q 'vendor_rules' spec_classifier/config.yaml` | no_drift |
| spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md | 21 | "run.ps1 (repo root) — append \"<vendor>\" to $ALL_VENDORS" | `grep -n '\$ALL_VENDORS' run.ps1` (line 71) | no_drift |
| spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md | 22 | "teresa_gui.py — append \"<vendor>\" to VENDORS_ACTIVE and add a label in _build_left_column" | `grep -n 'VENDORS_ACTIVE\|_build_left_column' teresa_gui.py` (VENDORS_ACTIVE at line 38) | no_drift |
| spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md | 23 | "src/vendors/<vendor>/adapter.py — override get_extra_cols() (see VendorAdapter in src/vendors/base.py); HPEAdapter (5), LenovoAdapter (1), CiscoAdapter (2); annotated_writer.py accepts them as extra_cols and does not need to be modified" | `grep -n 'get_extra_cols' spec_classifier/src/vendors/base.py spec_classifier/src/vendors/hpe/adapter.py spec_classifier/src/vendors/lenovo/adapter.py spec_classifier/src/vendors/cisco/adapter.py` (HPE 5 cols line 55-62, Lenovo 1 col line 61-62, Cisco 2 cols line 42-46) | no_drift |
| spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md | 36 | "Implement all 6 required abstract methods" | `grep -c '@abstractmethod' spec_classifier/src/vendors/base.py` returns 6 | no_drift |
| spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md | 38-43 | "can_parse: positive signature; Dell example sentinel \"Module Name\"; Cisco sheet \"Price Estimate\"; do not catch exceptions" | matches src/vendors/base.py:VendorAdapter.can_parse docstring (lines 16-22 in base.py) | no_drift |
| spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md | 45-46 | "parse(path) returns (list[dict], int): list of rows (each dict has columns + __row_index__ 1-based) and the 0-based header row index" | matches src/vendors/base.py:VendorAdapter.parse docstring (lines 25-31 in base.py) | no_drift |
| spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md | 48-51 | "normalize(raw_rows): required fields source_row_index, row_kind, group_name, group_id, product_name, module_name, option_name, option_id, skus, qty, option_price" | matches src/vendors/base.py:VendorAdapter.normalize docstring (lines 33-41 in base.py) | no_drift |
| spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md | 53-54 | "get_rules_file(): path to YAML rules; can read from config[\"vendor_rules\"][vendor] with fallback" | matches src/vendors/base.py:VendorAdapter.get_rules_file (line 44 in base.py) | no_drift |
| spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md | 56 | "get_vendor_stats(normalized_rows): dict for run_summary.json" | matches src/vendors/base.py:VendorAdapter.get_vendor_stats docstring (line 7-8 in base.py) | no_drift |
| spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md | 59 | "generates_branded_spec(): True only if a branded spec is implemented for the vendor" | matches src/vendors/base.py:VendorAdapter.generates_branded_spec docstring (line 12-13 in base.py) | no_drift |
| spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md | 65 | "rule_id: format <CATEGORY>-<VENDOR_CODE>-NNN — see docs/rules/RULES_AUTHORING_GUIDE.md" | `test -f spec_classifier/docs/rules/RULES_AUTHORING_GUIDE.md` | no_drift |
| spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md | 67-69 | "Step 4: Add to VENDOR_REGISTRY in main.py — one line: import the adapter and add to dict" | `grep -q 'VENDOR_REGISTRY' spec_classifier/main.py` (D-22 read-only) | no_drift |
| spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md | 71-73 | "Step 5: Add to vendor_rules in config.yaml" | `grep -q 'vendor_rules' spec_classifier/config.yaml` | no_drift |
| spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md | 77 | "Append \"<vendor>\" to $ALL_VENDORS in run.ps1 (repo root)" | `grep -n '\$ALL_VENDORS' run.ps1` (line 71) | no_drift |
| spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md | 78 | "Append \"<vendor>\" to VENDORS_ACTIVE in teresa_gui.py and add a label entry in _build_left_column" — line-number ref `teresa_gui.py:38` REMOVED per D-11 cat #3 + D-13 (symbol-ref form retained) | `grep -n 'VENDORS_ACTIVE\|_build_left_column' teresa_gui.py` (VENDORS_ACTIVE at line 38) | patch |
| spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md | 82 | "test_regression_<vendor>.py based on test_regression_cisco.py: run via _get_adapter(\"<vendor>\", config), compare with golden" | `test -f spec_classifier/tests/test_regression_cisco.py && grep -q '_get_adapter' spec_classifier/tests/test_regression_cisco.py` (D-22 read-only) | no_drift |
| spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md | 83 | "test_unknown_threshold_<vendor>.py based on test_unknown_threshold_cisco.py: verify unknown_count = 0" | `test -f spec_classifier/tests/test_unknown_threshold_cisco.py` | no_drift |
| spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md | 89-91 | "python main.py --save-golden --input \"...\" --vendor <vendor>" | `grep -n 'save-golden' spec_classifier/main.py` (line 266) | no_drift |
| spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md | 99 | "Note: CURRENT_STATE.md has been archived to .planning/archive/CURRENT_STATE-2026-05-10.md. Live project status is tracked in .planning/STATE.md" | `test -f .planning/archive/CURRENT_STATE-2026-05-10.md && test -f .planning/STATE.md` | no_drift |
| spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md | 103 | "base implementation in src/vendors/base.py:VendorAdapter.get_extra_cols() returns [] (default); main.py passes the result to generate_annotated_source_excel(..., extra_cols=adapter.get_extra_cols())" | `grep -n 'get_extra_cols' spec_classifier/src/vendors/base.py` (line 56-62 returns []) | no_drift |
| spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md | 109-110 | "Dell: get_vendor_stats() returns {}; Cisco: returns dict with metrics (e.g. top_level_bundles_count, max_hierarchy_depth)" | per src/vendors/dell/adapter.py and src/vendors/cisco/adapter.py implementations (D-22 read-only); cisco get_vendor_stats appears at adapter.py:42 area | no_drift |
| spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md | 121 | "All tests green: python -m pytest tests/ -v" | standard pytest invocation; `test -d spec_classifier/tests` | no_drift |
| spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md | 129-131 | "See also: docs/rules/RULES_AUTHORING_GUIDE.md, docs/schemas/DATA_CONTRACTS.md, src/vendors/dell/adapter.py, src/vendors/cisco/adapter.py and src/vendors/cisco/parser.py, normalizer.py" | `test -f spec_classifier/docs/rules/RULES_AUTHORING_GUIDE.md && test -f spec_classifier/docs/schemas/DATA_CONTRACTS.md && test -f spec_classifier/src/vendors/dell/adapter.py && test -f spec_classifier/src/vendors/cisco/adapter.py && test -f spec_classifier/src/vendors/cisco/parser.py` | no_drift |

## Tally (filled by Plan 06)

- Total claims swept: TBD
- Resolutions: TBD remove / TBD patch / TBD no_drift
- Files touched: TBD of 19 (16 in-scope + 3 surgical map lines)
- Drift remaining post-phase: 0 (per ROADMAP §SC-1)
