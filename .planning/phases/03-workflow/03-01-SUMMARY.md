---
phase: 03-workflow
plan: 01
subsystem: docs
tags: [workflow, archive, prompts, git-mv, launcher-repoint, gsd-cycle]

# Dependency graph
requires:
  - phase: 02-docs
    provides: ".planning/archive/ directory + Phase 2 D-08 archive pattern (CURRENT_STATE-2026-05-10.md precedent)"
provides:
  - "Archived pre-GSD prompt library at .planning/archive/prompts-2026-05-10/ (10 verbatim Russian originals + 1 English README with 11-row mapping table)"
  - "Stable cross-reference target list for Plan 03-02 (WF-02 root /CONTRIBUTING.md author) — every retired prompt now has a known-good GSD-native pointer"
  - "LAUNCHER_README.md repointed away from prompts/ (line 52 → spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md)"
affects: [03-02, 03-03, milestone-close]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Folder-scoped git mv archive (Phase 2 D-08 precedent extended from single-file to whole-directory)"
    - "English archive README + per-file mapping table over plain git mv (per D-02; navigability for non-Russian-readers)"
    - "Markdown-link form for doc cross-references (`[`text`](path)`) over plain backtick (per D-05 LAUNCHER_README.md edit)"

key-files:
  created:
    - ".planning/archive/prompts-2026-05-10/README.md (English, 34 lines, 11-row mapping table)"
  modified:
    - "LAUNCHER_README.md (line 52 only; 1 + / 1 - net zero; total 72 lines preserved)"
  moved:
    - "spec_classifier/prompts/00_VENDOR-RECON.md → .planning/archive/prompts-2026-05-10/00_VENDOR-RECON.md"
    - "spec_classifier/prompts/01_PRE-CHECK.md → .planning/archive/prompts-2026-05-10/01_PRE-CHECK.md"
    - "spec_classifier/prompts/02_MASTER-PLAN.md → .planning/archive/prompts-2026-05-10/02_MASTER-PLAN.md"
    - "spec_classifier/prompts/03_CURSOR-IMPLEMENT.md → .planning/archive/prompts-2026-05-10/03_CURSOR-IMPLEMENT.md"
    - "spec_classifier/prompts/04_POST-CHECK.md → .planning/archive/prompts-2026-05-10/04_POST-CHECK.md"
    - "spec_classifier/prompts/05_AUDIT-1A-1G.md → .planning/archive/prompts-2026-05-10/05_AUDIT-1A-1G.md"
    - "spec_classifier/prompts/06_BATCH-AUDIT-MASTER-PLAN.md → .planning/archive/prompts-2026-05-10/06_BATCH-AUDIT-MASTER-PLAN.md"
    - "spec_classifier/prompts/07_DOC-UPDATE-MASTER-PLAN.md → .planning/archive/prompts-2026-05-10/07_DOC-UPDATE-MASTER-PLAN.md"
    - "spec_classifier/prompts/08_CHATGPT-SYSTEM-PROMPTS.md → .planning/archive/prompts-2026-05-10/08_CHATGPT-SYSTEM-PROMPTS.md"
    - "spec_classifier/prompts/COWORK_OPUS_FULL_AUDIT.md → .planning/archive/prompts-2026-05-10/COWORK_OPUS_FULL_AUDIT.md"
    - "spec_classifier/prompts/README.md → .planning/archive/prompts-2026-05-10/README.md (then rewritten in English in task 1.2)"

key-decisions:
  - "Followed plan exactly — no auto-fixes triggered; no architectural deviations needed"
  - "Committed each task individually per orchestrator success criteria (overrode plan's <verification> step 7 single-commit suggestion); resulting 3 atomic commits stay aligned with Phase 1/2 atomic-commit convention and ROADMAP success-criteria 7"
  - "Used PowerShell verification scripts via -File invocation (not -Command inline) to dodge bash↔PowerShell backtick-escaping conflicts when checking markdown table rows; plan's inline -Command verification snippet had a backtick-quoting artifact and would have spuriously failed"

patterns-established:
  - "Folder-scoped git mv to .planning/archive/{name}-YYYY-MM-DD/ — extends Phase 2 D-08 single-file pattern; future archives (CONTRIBUTING-2026-05-10.md in Plan 03-02) reuse the same shape"
  - "Archived README rewritten in English with per-file mapping table to GSD-native equivalents — pattern reusable for any future deprecation of a multi-file legacy library"
  - "PowerShell verification harness: write a .ps1 to .planning/.tmp_verify_*.ps1, invoke with `powershell.exe -NoProfile -ExecutionPolicy Bypass -File`, delete after — sidesteps cross-shell quoting issues when verifications include markdown backticks"

requirements-completed: [WF-01]

# Metrics
duration: 5min
completed: 2026-05-10
---

# Phase 3 Plan 01: Retire spec_classifier/prompts/ to Archive Summary

**Pre-GSD prompt library (11 files, 1345 lines, Russian) folder-scoped git mv'd to `.planning/archive/prompts-2026-05-10/`, archive README rewritten in English with verbatim 11-row mapping table to GSD-native equivalents, LAUNCHER_README.md line 52 repointed to NEW_VENDOR_GUIDE.md.**

## Performance

- **Duration:** 5 min
- **Started:** 2026-05-10T04:26:00Z
- **Completed:** 2026-05-10T04:31:03Z
- **Tasks:** 3 / 3
- **Files modified:** 13 (11 renamed + 1 rewritten + 1 line-edited)

## Accomplishments

- `spec_classifier/prompts/` removed from working tree; all 11 files relocated to `.planning/archive/prompts-2026-05-10/` via single folder-scoped `git mv` (rename detection at 100% similarity for every file — `git log --follow` works on each one).
- `.planning/archive/prompts-2026-05-10/README.md` rewritten as a 34-line English archive README with three sections per D-02: (a) one-paragraph archive note + date stamp, (b) verbatim 11-row per-file mapping table per D-03/D-04 (each retired prompt → its GSD-native equivalent, with `COWORK_OPUS_FULL_AUDIT.md` flagged as "audit-mode" per D-04), (c) back-pointer paragraph to `/CONTRIBUTING.md` as canonical doc.
- `LAUNCHER_README.md` line 52 repointed from `prompts/00_VENDOR-RECON.md` to a markdown-link-form pointer to `spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md` per D-05; surrounding 3-step "Adding a new vendor" list intact, file line count preserved at 72.
- All 10 archived original `.md` files (`00_VENDOR-RECON.md` … `08_CHATGPT-SYSTEM-PROMPTS.md` + `COWORK_OPUS_FULL_AUDIT.md`) remain byte-identical to their pre-move state per D-02 historical-record requirement (Russian preserved).
- Zero edits to D-22 protected files: `spec_classifier/golden/`, `spec_classifier/rules/`, `spec_classifier/src/`, `spec_classifier/tests/`, `spec_classifier/main.py`, `spec_classifier/batch_audit.py`, `spec_classifier/cluster_audit.py`, `spec_classifier/conftest.py`, `run.ps1`, `teresa.bat`, `teresa_gui.py` (verified via `git diff --stat HEAD~3..HEAD -- {paths}` returning empty).

## Task Commits

Each task was committed atomically (per executor success criteria; overrode plan `<verification>` step 7 single-commit suggestion):

1. **Task 1.1: git mv spec_classifier/prompts/ to .planning/archive/prompts-2026-05-10/** — `c8a0977` (chore)
   - 11 files renamed (100% similarity each); zero content changes; git status showed 11 R-entries.
2. **Task 1.2: Rewrite archive README.md in English with per-file mapping table** — `85f9d22` (docs)
   - 1 file changed (29 + / 54 -); replaced 59-line Russian original with 34-line English D-02-conformant rewrite.
3. **Task 1.3: Repoint LAUNCHER_README.md line 52 to NEW_VENDOR_GUIDE.md** — `ea4f050` (docs)
   - 1 file changed (1 + / 1 -); pure in-place line replacement; total file line count unchanged at 72.

**Plan metadata commit:** to be added with this SUMMARY.md + STATE.md + ROADMAP.md updates (separate from per-task commits).

## Files Created/Modified

- `.planning/archive/prompts-2026-05-10/README.md` — NEW (rewritten from Russian original): English archive note + 11-row per-file mapping table + back-pointer paragraph to `/CONTRIBUTING.md`. 34 lines.
- `LAUNCHER_README.md` — MODIFIED (1 line): line 52 markdown-link to `spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md` replaces the legacy `prompts/00_VENDOR-RECON.md` pointer.
- `.planning/archive/prompts-2026-05-10/{00_VENDOR-RECON,01_PRE-CHECK,02_MASTER-PLAN,03_CURSOR-IMPLEMENT,04_POST-CHECK,05_AUDIT-1A-1G,06_BATCH-AUDIT-MASTER-PLAN,07_DOC-UPDATE-MASTER-PLAN,08_CHATGPT-SYSTEM-PROMPTS,COWORK_OPUS_FULL_AUDIT}.md` — RENAMED from `spec_classifier/prompts/{...}.md`. Content byte-identical to pre-move state (verified via `git diff HEAD~2..HEAD` returning empty for each).

## Decisions Made

- **Followed plan exactly** — no auto-fixes triggered. Plan was unusually detailed and self-consistent; D-22 protected-files boundary was honored without effort because the plan's task scope is purely doc-only.
- **Per-task commits over single requirement-grouped commit.** Plan `<verification>` step 7 suggested one combined `chore(03-01): ... (WF-01)` commit wrapping all three tasks; orchestrator success criteria explicitly required "Each task committed individually". Resolved in favor of orchestrator (binding instruction). Result: three atomic commits (`c8a0977`, `85f9d22`, `ea4f050`), each cleanly revertable, which is also the Phase 1/2 atomic-commit convention. Single requirement (WF-01) is still tracked in STATE.md / REQUIREMENTS.md by requirement ID, not by commit count.
- **PowerShell verification via `-File` over `-Command`.** The plan's inline verification used `powershell.exe -NoProfile -Command "..."` with embedded backticks for markdown-table-row checks; bash's interpolation through `Bash(command)` ate the backticks, causing spurious "missing token" reports. Worked around by writing each verification to `.planning/.tmp_verify_task_*.ps1`, invoking with `-File`, and deleting after. Pattern is documented in patterns-established for future executor reuse.

## Deviations from Plan

None - plan executed exactly as written.

(Caveat for the record: the plan's success criteria mentioned "Single commit per WF-01 requirement" but the executor's binding orchestrator instructions said "Each task committed individually". This is a per-orchestrator-prompt resolution, not a content deviation — the work landed exactly as the plan's `<tasks>` blocks specified.)

## Issues Encountered

- **PowerShell `-Command` backtick-eating via bash invocation.** When the plan's inline `<automated>` verification snippets were run as `powershell.exe -NoProfile -Command "..."` through the Bash tool, the backticks inside test strings (e.g., `` | `00_VENDOR-RECON.md` `` for markdown-table-row matching) were stripped by an intermediate shell layer, producing spurious "missing token" reports. Resolved by writing each verification block to a `.ps1` file and invoking via `powershell.exe -NoProfile -ExecutionPolicy Bypass -File <script>`. All three tasks then verified `OK`. No content change to the plan or to the produced artifacts; verification harness only.

## User Setup Required

None — no external service configuration required. All work is doc-only.

## Next Phase Readiness

- **Plan 03-02 (WF-02) unblocked.** The prompts/ archive is stable; Plan 03-02 can author root `/CONTRIBUTING.md` and the deep-CLAUDE.md / root-CLAUDE.md / DOCS_INDEX.md cross-reference cleanup with confidence that all retired-prompt cross-references resolve to a known-good GSD-native pointer (the 11-row mapping table in this archive's README is the single source of truth).
- **Plan 03-03 (verification gate, D-20 7-step) prerequisites partially met.** This plan's V1–V6 internal verification covers steps 1 (cross-reference negative-control for prompts/), 5 (goldens unchanged — N/A here, no goldens touched), and parts of 6 (no code touched). Plan 03-03 will re-run the full 7-step gate at phase boundary.
- **Zero blockers introduced.** No `STATE.md` blockers added; no deferred items added; no new threat surface introduced (threat model: documentation-only phase, no trust boundaries crossed per `<threat_model>` block).

## Self-Check: PASSED

Created files exist:
- FOUND: .planning/archive/prompts-2026-05-10/README.md (34 lines, English, mapping table present)
- FOUND: .planning/archive/prompts-2026-05-10/00_VENDOR-RECON.md (and 9 other archived originals)

Modified files reflect the edit:
- FOUND: LAUNCHER_README.md line 52 = `1. Implement adapter (see [`spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md`](spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md)).`

Source removed:
- ABSENT: spec_classifier/prompts/ (Test-Path returns False)

Commits exist on `main`:
- FOUND: c8a0977 (Task 1.1)
- FOUND: 85f9d22 (Task 1.2)
- FOUND: ea4f050 (Task 1.3)

D-22 protected-files diff stat (`HEAD~3..HEAD -- spec_classifier/{golden,rules,src,tests,main.py,batch_audit.py,cluster_audit.py,conftest.py} run.ps1 teresa.bat teresa_gui.py`):
- EMPTY (no protected files touched)

---

*Phase: 03-workflow*
*Completed: 2026-05-10*
