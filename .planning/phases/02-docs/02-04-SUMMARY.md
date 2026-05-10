---
phase: 02-docs
plan: 04
subsystem: docs
tags: [readme, drift-fix, spec-classifier, translation]

# Dependency graph
requires:
  - phase: 02-docs
    provides: "02-02 archived CURRENT_STATE.md; 02-03 wrote root README.md"
provides:
  - "spec_classifier/README.md refreshed: English-only, CLI/config accurate, cross-references intact"
affects: [02-06-verification]

# Tech tracking
tech-stack:
  added: []
  patterns: []

key-files:
  created: []
  modified:
    - spec_classifier/README.md

key-decisions:
  - "One-button run section rewritten to point at repo-root ..\run.ps1 (scripts/run_full.ps1 and run_tests.ps1 do not exist post-launcher-unification)"
  - "Russian Quick Start comments translated to English in-place without structural rewrite"
  - "Troubleshooting Cisco rows translated to English (2 rows)"
  - "clean.ps1 mention preserved (script still exists at spec_classifier/scripts/clean.ps1)"
  - "C:\\venv kept literal per D-04"

patterns-established: []

requirements-completed: [DOC-02]

# Metrics
duration: 15min
completed: 2026-05-10
---

# Phase 02 Plan 04: spec_classifier/README.md Drift Refresh Summary

**spec_classifier/README.md refreshed: Russian fragments translated to English, defunct scripts/run_full.ps1 replaced with repo-root run.ps1, Troubleshooting Cisco rows translated, zero Cyrillic residue**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-05-10T00:00:00Z
- **Completed:** 2026-05-10T00:15:00Z
- **Tasks:** 2 (Task 4.1 audit + Task 4.2 fixes, combined into 1 commit)
- **Files modified:** 1

## Accomplishments

- Translated all Russian-language fragments to English (Quick Start prose + inline comments, One-button run section, Troubleshooting table rows)
- Rewrote One-button run section to reference repo-root `run.ps1` instead of defunct `scripts/run_full.ps1` and `scripts/run_tests.ps1`
- Verified all 5 `docs/` cross-references exist on disk (PASS)
- Confirmed `CURRENT_STATE.md` not referenced (none found — clean)
- Confirmed `C:\venv` preserved as literal suggestion; framing is "default suggestion"

## Task Commits

1. **Tasks 4.1 + 4.2: Audit + apply drift fixes** - `3699b30` (docs)

**Plan metadata:** (to be added by final commit)

## Lines Before / After

- **Before:** 286 lines
- **After:** 289 lines (within 250-290 target; net +3 due to One-button run section rewrite adding one explanatory sentence)

## Per-edit Drift Fix Table

| Line(s) before | Fix type | Before (snippet) | After (snippet) |
|---|---|---|---|
| 39 | translate | "По умолчанию вход и выход — каталоги..." | "By default, INPUT and OUTPUT are the directories..." |
| 45 | translate | "# Создать папки (один раз)" | "# Create folders (one-time)" |
| 49 | translate | "# Положить .xlsx в input/, затем:" | "# Drop .xlsx files into input/, then:" |
| 51 | translate | "# Одиночный Dell" | "# Single Dell file" |
| 54 | translate | "# Одиночный Cisco CCW" | "# Single Cisco CCW file" |
| 57 | translate | "# Batch: все .xlsx из input" | "# Batch: every .xlsx in input" |
| 61 | translate | "**Где искать результат:**..." | "**Where to find results:**..." |
| 65-76 | rewrite section | `.\scripts\run_full.ps1` + Russian prose | `..\run.ps1` variants + English prose |
| 71 | translate (within rewrite) | "Запускает тесты + batch-прогон..." | (absorbed into rewritten section) |
| 73-74 | translate + fix | Russian bullets + defunct run_tests.ps1 | clean.ps1 mention only (run_tests.ps1 removed) |
| 76 | translate (within rewrite) | "Настройка путей: скопировать..." | "Configure paths: copy..." |
| 176 | translate | "# Cisco тесты" | "# Cisco-specific tests" |
| 204 | translate | "Cisco файл содержит другой лист \| Убедитесь..." | "Cisco file contains a different sheet \| Ensure..." |
| 205 | translate | "`--vendor cisco` — нет `_branded.xlsx` \| Ожидаемо \| Cisco branded spec не создаётся" | "`--vendor cisco` — no `_branded.xlsx` \| Expected \| Cisco branded spec is not generated" |

## Cross-reference Verification Table

| Link | Status | Notes |
|---|---|---|
| `docs/dev/ONE_BUTTON_RUN.md` | PASS | File exists |
| `docs/rules/RULES_AUTHORING_GUIDE.md` | PASS | File exists |
| `docs/taxonomy/hw_type_taxonomy.md` | PASS | File exists |
| `docs/user/CLI_CONFIG_REFERENCE.md` | PASS | File exists |
| `docs/user/RUN_PATHS_AND_IO_LAYOUT.md` | PASS | File exists |
| `docs/DOCS_INDEX.md` | PASS | File exists |
| `CHANGELOG.md` | PASS | File exists |
| `scripts/run_full.ps1` | REMOVED | Did not exist; reference removed |
| `scripts/run_tests.ps1` | REMOVED | Did not exist; reference removed |
| `scripts/clean.ps1` | KEPT | File exists |

## C:\venv and placeholder verification

- `C:\venv` present as literal suggestion in Virtual Environment section: CONFIRMED
- `<USERNAME>` placeholder usage on lines 158, 186, 188, 222, 226, 239, 242, 266, 269, 272, 277: INTACT (no real username introduced)
- `git grep -c 'C:\Users\G\'` in README: 0 matches

## Deviations from Plan

None - plan executed exactly as written. All 14 known drift items from plan's `<interfaces>` section addressed. The One-button run section rewrite was fully anticipated by plan step 2 (scripts/run_full.ps1 = False confirmed, rewrite applied per instructions).

## Issues Encountered

- PowerShell regex for Cyrillic detection produced false positives due to terminal encoding mismatch during `[А-Яа-я]` pattern matching. Verified with explicit UTF-8 decoding (`[System.IO.File]::ReadAllText`) and Python - zero actual Cyrillic characters remain.
- PowerShell regex `-match 'C:\\\\venv'` failed because `\v` is a regex escape for vertical tab. Used `.Contains('C:\venv')` literal check instead - confirmed present.

## Self-Check

- `spec_classifier/README.md` exists: CONFIRMED (289 lines)
- Commit `3699b30` exists: CONFIRMED
- Zero Cyrillic characters (Python + PowerShell UTF-8 verified)
- All docs/ links resolve on disk
- Goldens unchanged: `git diff --stat HEAD -- spec_classifier/golden/` empty

## Self-Check: PASSED

---
*Phase: 02-docs*
*Completed: 2026-05-10*
