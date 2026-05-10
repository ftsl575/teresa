---
phase: "02-docs"
plan: "02-05"
subsystem: "docs"
tags: ["docs-audit", "translation", "drift-fix", "taxonomy", "legacy-assessment"]
dependency_graph:
  requires: ["02-04"]
  provides: ["clean-docs-tree", "english-docs", "legacy-assessed"]
  affects: ["developer-onboarding", "rules-authoring", "vendor-coverage-accuracy"]
tech_stack:
  added: []
  patterns: ["docs-audit", "drift-fix", "russian-to-english-translation"]
key_files:
  created:
    - ".planning/phases/02-docs/02-DOC-AUDIT.md"
    - ".planning/phases/02-docs/02-CONTRIBUTING-AUDIT.md"
  modified:
    - "spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md"
    - "spec_classifier/docs/dev/ONE_BUTTON_RUN.md"
    - "spec_classifier/docs/dev/OPERATIONAL_NOTES.md"
    - "spec_classifier/docs/dev/TESTING_GUIDE.md"
    - "spec_classifier/docs/user/CLI_CONFIG_REFERENCE.md"
    - "spec_classifier/docs/user/RUN_PATHS_AND_IO_LAYOUT.md"
    - "spec_classifier/docs/user/USER_GUIDE.md"
    - "spec_classifier/docs/product/TECHNICAL_OVERVIEW.md"
    - "spec_classifier/docs/rules/RULES_AUTHORING_GUIDE.md"
    - "spec_classifier/docs/schemas/DATA_CONTRACTS.md"
    - "spec_classifier/docs/taxonomy/hw_type_taxonomy.md"
    - "spec_classifier/docs/DOCS_INDEX.md"
    - "spec_classifier/docs/dev/CONTRIBUTING.md"
decisions:
  - "All 13 docs translated to English; Russian residue only in audit_summary.xlsx column names (intentional — those are the actual Excel headers)"
  - "CONTRIBUTING.md assessed as LEGACY per D-18; one-line forwarding note added per D-19; no content rewrite"
  - "DOCS_INDEX.md now 1:1 with docs/ tree (14 files including self; 13 listed entries)"
  - "All 6 D-21/D-22 protected tech-debt references verified accurate in live code — no fixes proposed"
  - "Broken script references (run_full.ps1, run_tests.ps1, run_audit.ps1) corrected to run.ps1 across all affected docs"
  - "cycle2_summary.md added to DOCS_INDEX.md — was missing despite file existing in taxonomy/"
metrics:
  duration_minutes: 180
  completed_date: "2026-05-10"
  tasks_completed: 3
  files_changed: 15
---

# Phase 02 Plan 05: Docs/ Tree Audit and Drift Fixes Summary

**One-liner:** Full English translation and drift correction of all 13 docs/ files; CONTRIBUTING.md assessed as legacy; DOCS_INDEX.md reconciled 1:1 with tree.

---

## Tasks Completed

| Task | Name | Commit | Key Output |
|------|------|--------|-----------|
| 5.1 | Audit all 13 docs end-to-end | `9c10a07` (included) | `02-DOC-AUDIT.md` — 13 per-doc verdicts |
| 5.2 | Apply drift fixes — batch 1/3 (dev/) | `27ceb55` | NEW_VENDOR_GUIDE, ONE_BUTTON_RUN, OPERATIONAL_NOTES, TESTING_GUIDE |
| 5.2 | Apply drift fixes — batch 2/3 (user/ + product/) | `7ce2f26` | CLI_CONFIG_REFERENCE, RUN_PATHS_AND_IO_LAYOUT, USER_GUIDE, TECHNICAL_OVERVIEW |
| 5.2 | Apply drift fixes — batch 3/3 (rules/ + schemas/ + taxonomy/ + DOCS_INDEX) | `9c10a07` | RULES_AUTHORING_GUIDE, DATA_CONTRACTS, hw_type_taxonomy, DOCS_INDEX, 02-DOC-AUDIT.md |
| 5.3 | Assess CONTRIBUTING.md as legacy | `8a6e9c0` | `02-CONTRIBUTING-AUDIT.md`, forwarding note in CONTRIBUTING.md |

---

## Summary of Changes

### Task 5.1: Audit Findings

All 13 docs were read end-to-end. Verdicts assigned:

| Doc | Verdict | Primary Issues |
|-----|---------|---------------|
| `cycle2_summary.md` | CLEAN | No drift |
| `CONTRIBUTING.md` | LEGACY | Pre-GSD, Russian, 3-vendor |
| `NEW_VENDOR_GUIDE.md` | DRIFT | Russian, 3-vendor, broken CURRENT_STATE refs |
| `ONE_BUTTON_RUN.md` | DRIFT | Russian, references non-existent `scripts/run_full.ps1` |
| `OPERATIONAL_NOTES.md` | DRIFT | Russian, references non-existent `run_audit.ps1`, 3-vendor |
| `TESTING_GUIDE.md` | DRIFT | Russian, title "(Dell + Cisco CCW + HPE)", 3-vendor |
| `CLI_CONFIG_REFERENCE.md` | DRIFT | Russian, 3-vendor |
| `RUN_PATHS_AND_IO_LAYOUT.md` | DRIFT | Russian, broken script refs, 3-vendor |
| `USER_GUIDE.md` | DRIFT | Russian narrative, `ram`/`nic` canonical names, version v2.1.0→v2.6.0 |
| `TECHNICAL_OVERVIEW.md` | DRIFT | Russian, 3-vendor, missing lenovo/xfusion/huawei |
| `RULES_AUTHORING_GUIDE.md` | DRIFT | Russian, 3-vendor rule_id table |
| `DATA_CONTRACTS.md` | DRIFT | Russian, duplicate section, missing tech-debt notes |
| `hw_type_taxonomy.md` | DRIFT | Russian section headers, group labels, table captions |
| `DOCS_INDEX.md` | DRIFT | Stale title, missing cycle2_summary.md, orphan pipe |

Tech-debt verification: all 6 D-21/D-22 protected items verified accurate in live code.

### Task 5.2: Drift Fixes Applied

**Batch 1 — dev/ (4 files):**

- `NEW_VENDOR_GUIDE.md`: translated Russian to English; removed 2 `CURRENT_STATE.md` references (archived); added Lenovo/Huawei/xFusion rule_id codes; added Step 6 "Wire the launcher and GUI"
- `ONE_BUTTON_RUN.md`: translated; replaced `.\scripts\run_full.ps1` (does not exist) with `.\run.ps1` (repo root); updated cleanup script path
- `OPERATIONAL_NOTES.md`: translated; replaced `run_audit.ps1` (does not exist) with `run.ps1`; updated "all three vendors" → "all active vendors (dell, cisco, hpe, lenovo, huawei, xfusion)"
- `TESTING_GUIDE.md`: translated; removed "(Dell + Cisco CCW + HPE)" from title; added Lenovo/Huawei/xFusion test strategy and modules; added session gate note (`MAX_SKIP_RATIO = 0.50`)

**Batch 2 — user/ + product/ (4 files):**

- `CLI_CONFIG_REFERENCE.md`: translated; updated `--vendor` to all 6; expanded output structure to all 6 vendor run dirs; added all-vendor CLI examples
- `RUN_PATHS_AND_IO_LAYOUT.md`: translated; fixed `run_full.ps1`/`run_tests.ps1` → `run.ps1`; expanded INPUT subfolder table and run commands to all 6 vendors
- `USER_GUIDE.md`: translated Russian narrative sections; fixed `ram` → `memory`, `nic` → `network_adapter` in device_type table; updated hw_type version to v2.6.0
- `TECHNICAL_OVERVIEW.md`: translated entire 313-line Russian file; added lenovo/xfusion/huawei to vendor list; updated `--vendor` choices; expanded project tree; added CONCERNS.md tech-debt pointers

**Batch 3 — rules/ + schemas/ + taxonomy/ + DOCS_INDEX (5 files):**

- `RULES_AUTHORING_GUIDE.md`: translated; updated to 6 rule files and vendors; added Lenovo/Huawei/xFusion to rule_id naming table; enhanced power_cord section with `_E8_NO_HW_TYPE_DEVICES` reference
- `DATA_CONTRACTS.md`: translated; removed duplicate "Canonical Field Names" subsection; added `HW_TYPE_VOCAB` duplication note; added `batch_audit.py` Excel reading note with CONCERNS.md pointers
- `hw_type_taxonomy.md`: translated all Russian section headers ("Зафиксированные решения" → "Recorded decisions", "Словарь" → "Vocabulary", group labels, migration table labels, filter table); preserved all technical content and code blocks
- `DOCS_INDEX.md`: removed "(Dell + Cisco CCW + HPE)" from title; added `cycle2_summary.md` row; merged orphan pipe-only row into Key Documents table; index now 1:1 with docs/ tree
- `02-DOC-AUDIT.md`: committed with batch 3 (Task 5.1 artifact created earlier)

### Task 5.3: CONTRIBUTING.md Legacy Assessment

- `CONTRIBUTING.md` assessed as LEGACY: pre-GSD content, entirely in Russian, references only 3 vendors, describes retired manual workflow
- One-line forwarding note added after H1 per D-19 — body unchanged per D-18
- `02-CONTRIBUTING-AUDIT.md` created: scope, pre-GSD content assessment, technical accuracy spot-check, Phase 3 hand-off plan

---

## Deviations from Plan

None — plan executed exactly as written.

- Broken script references (run_full.ps1, run_tests.ps1, run_audit.ps1) confirmed via `Test-Path` and replaced with `run.ps1`
- Russian residue check at end: 12 of 13 translated docs are fully clean; DATA_CONTRACTS.md has 3 lines of Russian that are the literal Excel column names in the generated `audit_summary.xlsx` — intentional and documented inline
- CONTRIBUTING.md Russian not translated per D-18 (assess only)

---

## Tech-Debt Verification (D-21/D-22 Protected Items)

All 6 items verified accurate in live code — no fixes proposed:

| Item | Code Location | Status |
|------|--------------|--------|
| `power_cord hw_type=None` | `dell_rules.yaml:278` comment | VERIFIED ACCURATE |
| `_E8_NO_HW_TYPE_DEVICES` | `batch_audit.py:506` | VERIFIED ACCURATE |
| `core/parser.py` Dell-specific | `parser.py:29` "Module Name" sentinel | VERIFIED ACCURATE |
| `batch_audit.py` Excel reading | `batch_audit.py:611` `pd.read_excel` | VERIFIED ACCURATE |
| `HW_TYPE_VOCAB` duplication | `classifier.py:28` + `batch_audit.py:44` | VERIFIED ACCURATE |
| YAML rule order | `dell_rules.yaml:573,617` "ORDER MATTERS" comments | VERIFIED ACCURATE |

---

## Known Stubs

None — all docs are now factually accurate and reference correct paths/tools. No placeholder content present.

---

## Threat Flags

None — docs/ directory changes only; no network endpoints, auth paths, file access patterns, or schema changes introduced.

---

## Self-Check: PASSED

- `02-DOC-AUDIT.md` exists: YES (`9c10a07`)
- `02-CONTRIBUTING-AUDIT.md` exists: YES (`8a6e9c0`)
- All 13 docs modified: YES (12 DRIFT + 1 LEGACY with forwarding note)
- Batch commits present: YES (`27ceb55`, `7ce2f26`, `9c10a07`)
- DOCS_INDEX.md 1:1 with tree: YES (13 listed entries + self = 14 files total)
- Russian residue in translated docs: NONE (except intentional Excel column names in DATA_CONTRACTS.md)
