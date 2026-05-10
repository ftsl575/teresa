---
phase: 03-workflow
plan: 02
subsystem: docs
tags: [workflow, contributing, claude-md, docs-index, changelog, cross-ref-cleanup, gsd-cycle]

# Dependency graph
requires:
  - phase: 03-workflow
    plan: 01
    provides: "Stable cross-reference target list (11-row prompts/ archive mapping table); LAUNCHER_README.md already repointed; .planning/archive/ directory with 2026-05-10 date suffix convention established"
provides:
  - "Root /CONTRIBUTING.md (155 lines, English, tool-agnostic, GSD-cycle command-by-command, do-not-fix verbatim) as the canonical contributor entry point"
  - "Inner CONTRIBUTING.md retired to .planning/archive/CONTRIBUTING-2026-05-10.md (history preserved via git mv, 100% similarity rename)"
  - "Deep spec_classifier/CLAUDE.md normalized: legacy ~63-line block (Tool Roles + legacy dev cycle table + Hard Rules R1-R5 + Recommended Models + Prompts—Location footer) replaced with 5-line pointer to /CONTRIBUTING.md"
  - "Root CLAUDE.md § Tooling roles repointed symmetrically (1-sentence cycle reference now points at /CONTRIBUTING.md instead of spec_classifier/CLAUDE.md)"
  - "DOCS_INDEX.md cleaned: 2 retired-doc rows dropped (CONTRIBUTING.md + prompts/README.md); See-also breadcrumb added under § Conventions; Phase 2 D-16 1:1 invariant preserved"
  - "CHANGELOG.md [Unreleased] § Changed extended with Phase 3 Workflow sub-section (3 bullets); historical version banners untouched per D-18"
affects: [03-03, milestone-close]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Cross-doc symmetric pointer pattern: deep CLAUDE.md and root CLAUDE.md both updated to point at the same canonical contributor doc; future doc consolidations can reuse the shape"
    - "Forward-pointer with relative path discipline: deep CLAUDE.md uses ../CONTRIBUTING.md (one level up), DOCS_INDEX.md breadcrumb uses ../../CONTRIBUTING.md (two levels up); paths verified at edit time via the pre-flight scripts"
    - "Atomic per-task commits with single requirement-grouped narrative (overrode plan's <verification> step 8 single-commit suggestion in favor of orchestrator success-criteria 'Each task committed individually' — same call as Plan 03-01)"
    - "PowerShell verifier I/O encoding fix: explicit [System.IO.File]::ReadAllText(path, [System.Text.Encoding]::UTF8) instead of Get-Content -Raw (which uses system codepage on PS 5.1) — sidesteps em-dash/§ mojibake when checking markdown files containing UTF-8 multibyte chars"

key-files:
  created:
    - "CONTRIBUTING.md (155 lines, repo root)"
  modified:
    - "spec_classifier/CLAUDE.md (307 → 249 lines; net -58)"
    - "CLAUDE.md (74 → 74 lines; line-for-line replacement of cycle sentence)"
    - "spec_classifier/docs/DOCS_INDEX.md (41 → 41 lines; -2 rows + 2 lines breadcrumb)"
    - "spec_classifier/CHANGELOG.md (245 → 250 lines; +5 lines for Phase 3 sub-section)"
  moved:
    - "spec_classifier/docs/dev/CONTRIBUTING.md → .planning/archive/CONTRIBUTING-2026-05-10.md (100% similarity rename, 77 lines preserved)"

key-decisions:
  - "Followed plan exactly — no auto-fixes triggered; no architectural deviations; D-22 protected-files boundary honored without effort because plan scope is purely doc-only"
  - "Per-task atomic commits over single requirement-grouped commit (consistent with Plan 03-01's executor-side resolution of the same plan/orchestrator conflict). Six commits land cleanly revertable; WF-02 still atomically tracked by requirement ID in REQUIREMENTS.md"
  - "PowerShell verification harness via .ps1 files (not -Command inline) — same harness pattern Plan 03-01 established. Added [System.Text.Encoding]::UTF8 explicit-read after Task 2.2 verifier flagged em-dash mojibake as 'Russian residue detected' (false positive from PS 5.1 default codepage decoding)"
  - "CONTRIBUTING.md initial draft came in at 142 lines (under 150 target); expanded prose paragraphs in § Development cycle (cycle-linearity note) and § PR workflow (atomic-revertability note) to land at 155 lines per plan instructions ('expand prose, do not pad do-not-fix list')"

patterns-established:
  - "Symmetric pointer cleanup: when retiring a duplicated narrative (legacy dev cycle was in deep CLAUDE.md AND root CLAUDE.md), update both files in the same plan with parallel one-line/three-line pointers — keeps the cross-doc story consistent"
  - "Phase-scoped CHANGELOG sub-sections under [Unreleased]: '### Changed (Phase N — <Name>, YYYY-MM-DD)' format. Mirrors Plan 02-04's existing Phase 1/2 entries; Phase 3 entry slots in chronologically; existing ### Added section stays preserved between Phase 3's ### Changed and the unrelated v1.0+ historical entries"
  - "PowerShell verifier UTF-8 read pattern (extends Plan 03-01's .ps1-file-not-Command pattern): use [System.IO.File]::ReadAllText(absolutePath, [System.Text.Encoding]::UTF8) instead of Get-Content -Raw when verifying markdown files that contain em-dashes (—), § symbols, or other non-ASCII UTF-8; Get-Content -Raw on PS 5.1 silently converts them through the system codepage, producing false-positive 'Russian residue' warnings from Cyrillic-range regexes"

requirements-completed: [WF-02]

# Metrics
duration: 9min
completed: 2026-05-10
---

# Phase 3 Plan 02: Author Root /CONTRIBUTING.md + Cross-Reference Cleanup Summary

**Root `/CONTRIBUTING.md` (155 lines, 8 sections in D-10 order, GSD-cycle command-by-command per D-13, do-not-fix verbatim per D-15) authored as the canonical contributor doc; legacy inner CONTRIBUTING.md archived; deep + root CLAUDE.md updated to symmetric forward-pointers; DOCS_INDEX.md retired-doc rows dropped + See-also breadcrumb added; CHANGELOG.md Phase 3 entry added under [Unreleased] without disturbing historical lines.**

## Performance

- **Duration:** ~9 min
- **Started:** 2026-05-10T04:37:22Z
- **Completed:** 2026-05-10T04:46:14Z
- **Tasks:** 6 / 6
- **Files touched:** 6 (1 new + 1 moved + 4 modified)

## Accomplishments

- `/CONTRIBUTING.md` authored at repo root: 155 lines, English, tool-agnostic per D-11, Windows-only-this-milestone passing mention per D-12, all 8 D-10 sections in order (`# Contributing to teresa`, `## Development cycle`, `## Tests`, `## Adding a vendor`, `## PR workflow`, `## Code style`, `## Do not fix`, `## Where to look first`).
- § Development cycle uses literal command-by-command per D-13: numbered list 1–4 (Discuss / Plan / Execute / Verify) plus `/gsd-help` footnote; cycle-linearity paragraph added during line-count expansion.
- § Tests cites `spec_classifier/conftest.py:pytest_sessionfinish`, `MAX_SKIP_RATIO = 0.50`, the `skipped/total > 0.50` failure mode, and the goldens regression contract per D-10 §3.
- § Adding a vendor is pointer-only to `spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md` per D-14; one-paragraph "what to expect" framing added so the section isn't empty.
- § Do not fix lists all 5 protected items verbatim per D-15 (`power_cord` `hw_type=None`, `core/parser.py` Dell-specificity, `batch_audit.py` Excel-leakage, YAML rule-order load-bearing, `HW_TYPE_VOCAB` duplication) plus the back-pointer blockquote to `.planning/codebase/CONCERNS.md` § BLOCKER + IMPORTANT. D-23 honored: zero "do not fix YET" / "planned for v2" framing — items framed as intentional constraints.
- § Where to look first table mirrors root CLAUDE.md table per D-10 §8 (9 rows, including the new pointer-back to `spec_classifier/CLAUDE.md` for deep reference).
- Inner `spec_classifier/docs/dev/CONTRIBUTING.md` archived to `.planning/archive/CONTRIBUTING-2026-05-10.md` per D-06: single `git mv` at 100% similarity; 77-line Russian original preserved verbatim including the Phase-2 forwarding note inside.
- Deep `spec_classifier/CLAUDE.md` legacy block replaced per D-16: `## Tool Roles` (Cursor/Claude/ChatGPT/Gemini table), `## Development Cycle` (PRE-CHECK→...→AUDIT 1A-1G + 4-scenario sub-table), `## Hard Rules for Claude Windows` (R1–R5 + ### Severity Levels), `## Recommended Models per Step` (Sonnet/Opus assignments), `## Prompts — Location` footer all gone (~63 lines deleted); replaced with 3-line pointer to `../CONTRIBUTING.md`. Net delta: 307 → 249 lines (-58 net, matching D-16 expectation).
- Earlier sections of deep `spec_classifier/CLAUDE.md` untouched per D-22: `## Project`, `## Paths (Windows)`, `## Current State` (with Phase-2 archive forward-pointer preserved), `## CLI Commands`, `## Business Rules` (5 critical rules + alias tables), `## E-codes` (E1–E18 table), `## Known Tech Debt`. Critical-rule tokens still present: `power_cord`, `_E8_NO_HW_TYPE_DEVICES`, `HW_TYPE_VOCAB`, `BASE without device_type`.
- Root `CLAUDE.md` § Tooling roles updated per D-17: section header preserved, `.cursor/` informational sentence preserved (still relevant), cycle-pointer sentence updated from "PRE-CHECK → PLAN → IMPLEMENT → POST-CHECK → AUDIT 1A–1G is documented in `spec_classifier/CLAUDE.md`" to "Discuss → Plan → Execute → Verify, GSD-native is documented in [`/CONTRIBUTING.md`](CONTRIBUTING.md)". Line count stays at 74 (line-for-line replacement). 5 critical business rules and "Where to look first" table untouched.
- `spec_classifier/docs/DOCS_INDEX.md` cleaned per D-07/D-08/D-09: `docs/dev/CONTRIBUTING.md` row dropped, `prompts/README.md` row dropped, See-also breadcrumb added under § Conventions pointing at `../../CONTRIBUTING.md`. Net 0 line change. Phase 2 D-16 1:1 invariant preserved (every remaining row points at an existing file).
- `spec_classifier/CHANGELOG.md` extended per D-18/D-19: new `### Changed (Phase 3 — Workflow, 2026-05-10)` sub-section under `[Unreleased]` with 3 bullets covering the three Phase-3 changes; placement after Phase 2 sub-section, before existing `### Added`. Historical version banners (v1.3.x, v1.2.x, etc.) and their existing `prompts/` mentions untouched per D-18 release-notes immutability.
- Zero edits to D-22 protected files: `spec_classifier/golden/`, `spec_classifier/rules/`, `spec_classifier/src/`, `spec_classifier/tests/`, `spec_classifier/main.py`, `spec_classifier/batch_audit.py`, `spec_classifier/cluster_audit.py`, `spec_classifier/conftest.py`, `run.ps1`, `teresa.bat`, `teresa_gui.py` (verified via `git diff --stat HEAD~6..HEAD -- {paths}` returning empty).

## Task Commits

Each task committed atomically (orchestrator success-criteria 'Each task committed individually'; same resolution as Plan 03-01 of the plan-vs-orchestrator one-vs-many commit conflict):

1. **Task 2.1: git mv inner CONTRIBUTING.md to .planning/archive/CONTRIBUTING-2026-05-10.md (D-06)** — `2e2edfb` (chore)
   - 1 file renamed at 100% similarity; 77 lines preserved; Phase-2 forwarding note inside intact.
2. **Task 2.2: Author root /CONTRIBUTING.md (WF-02 D-10..D-15)** — `cb2b3ee` (docs)
   - 1 file created (155 lines); 8 D-10 sections; D-13 GSD commands literal; D-15 do-not-fix verbatim; D-23 framing honored.
3. **Task 2.3: Replace spec_classifier/CLAUDE.md legacy block with GSD pointer (D-16)** — `94bc2af` (docs)
   - 1 file changed (3 + / 61 -); 307 → 249 lines; 5 forbidden legacy section headers gone; 5 critical business rules preserved.
4. **Task 2.4: Repoint root CLAUDE.md § Tooling roles to /CONTRIBUTING.md (D-17)** — `98a8109` (docs)
   - 1 file changed (3 + / 3 -); line-for-line sentence replacement; section header + .cursor/ note preserved.
5. **Task 2.5: Drop DOCS_INDEX.md retired-doc rows + add See-also breadcrumb (D-07/D-08/D-09)** — `936b0b0` (docs)
   - 1 file changed (2 + / 2 -); net 0 line change; 1:1 invariant preserved.
6. **Task 2.6: Add Phase 3 Workflow CHANGELOG entry under [Unreleased] (D-19)** — `f16cc85` (docs)
   - 1 file changed (5 + / 0 -); historical lines untouched per D-18.

**Plan metadata commit:** to be added with this SUMMARY.md + STATE.md + ROADMAP.md updates (separate from per-task commits).

## Files Created/Modified

- `CONTRIBUTING.md` — NEW (repo root): 155-line English contributor doc with 8 D-10 sections, GSD-cycle command-by-command per D-13, pytest+skip-ratio gate citations per D-10 §3, vendor pointer-only per D-14, 5-item do-not-fix verbatim per D-15, 9-row where-to-look table per D-10 §8.
- `.planning/archive/CONTRIBUTING-2026-05-10.md` — RENAMED from `spec_classifier/docs/dev/CONTRIBUTING.md` (100% similarity; 77 lines preserved verbatim including Russian content + Phase-2 forwarding note).
- `spec_classifier/CLAUDE.md` — MODIFIED (-58 net): legacy ~63-line block (Tool Roles + Development Cycle table + Hard Rules R1-R5 + Severity Levels + Recommended Models + Prompts—Location) replaced with 5-line `## Development Cycle` pointer to `../CONTRIBUTING.md`. Line count 307 → 249.
- `CLAUDE.md` (root) — MODIFIED (line-for-line): § Tooling roles cycle sentence repointed from `spec_classifier/CLAUDE.md` to `/CONTRIBUTING.md`; cycle string updated from legacy `PRE-CHECK → PLAN → IMPLEMENT → POST-CHECK → AUDIT 1A–1G` to `Discuss → Plan → Execute → Verify, GSD-native`. Section header + .cursor/ note preserved. Line count stays at 74.
- `spec_classifier/docs/DOCS_INDEX.md` — MODIFIED (net 0): dropped `| docs/dev/CONTRIBUTING.md |` row (D-07), dropped `| prompts/README.md |` row (D-08), added See-also breadcrumb under § Conventions pointing at `../../CONTRIBUTING.md` (D-09).
- `spec_classifier/CHANGELOG.md` — MODIFIED (+5 lines): new `### Changed (Phase 3 — Workflow, 2026-05-10)` sub-section under `[Unreleased]` with 3 bullets; placement between existing Phase 2 sub-section and existing `### Added` section.

## Decisions Made

- **Followed plan exactly** — no auto-fixes triggered. Plan was unusually self-consistent (the `<interfaces>` block locked verbatim content for D-13, D-15, D-16, D-17, D-19); only judgment call was line-count expansion in CONTRIBUTING.md (under 150 → 155 via prose, not pad-the-list, per plan instructions).
- **Per-task atomic commits** over single requirement-grouped commit. Plan `<verification>` step 8 suggested one combined `docs(03-02): author root /CONTRIBUTING.md + cross-ref cleanup (WF-02)` commit; orchestrator success-criteria explicitly required "Each task committed individually". Resolved in favor of orchestrator (binding instruction). Result: six atomic commits, each cleanly revertable. WF-02 requirement still atomically tracked in STATE.md / REQUIREMENTS.md by requirement ID. Same resolution as Plan 03-01.
- **PowerShell verifier UTF-8 read fix.** Task 2.2's first verifier run via `Get-Content -Raw` flagged "Russian residue detected" because PS 5.1's default codepage decoding turned em-dashes (UTF-8 `\xE2\x80\x94`) into Cyrillic `Ћ` (U+0402), which then matched the Cyrillic-block regex `[Ѐ-ӿ]`. Switched to `[System.IO.File]::ReadAllText(absolutePath, [System.Text.Encoding]::UTF8)` for all subsequent verifiers; Tasks 2.2–2.6 all returned `OK`. Pattern documented in patterns-established for future executor reuse — extends Plan 03-01's `.ps1-file-not-Command` pattern with the encoding fix.

## Deviations from Plan

None — plan executed exactly as written.

(Caveats for the record:
- The plan's success criteria mentioned "Single commit per WF-02 requirement" but the executor's binding orchestrator instructions said "Each task committed individually". Same per-orchestrator-prompt resolution as Plan 03-01; not a content deviation — the work landed exactly as the plan's `<tasks>` blocks specified.
- Plan task 2.2 instructed expanding prose if line count came in under 150. Initial draft was 142; expanded § Development cycle (cycle-linearity note) and § PR workflow (atomic-revertability note) to land at 155 lines. This was anticipated by the plan, not a deviation.)

## Issues Encountered

- **PowerShell em-dash → Cyrillic mojibake.** Task 2.2's first verification flagged `Russian residue detected` because `Get-Content -Raw` on PS 5.1 reads files through the system codepage (Windows-1251 on this box). UTF-8 em-dashes (`—`, bytes `E2 80 94`) decoded as `Ћ` (U+0402), which then matched the Cyrillic-block regex `[Ѐ-ӿ]` in the verifier. The actual file content was clean UTF-8 (verified via `file CONTRIBUTING.md` showing `Unicode text, UTF-8 text` and via Bash `grep` for Cyrillic returning no matches). Fix applied to Tasks 2.3–2.6 verifiers: explicit `[System.IO.File]::ReadAllText(path, [System.Text.Encoding]::UTF8)` instead of `Get-Content -Raw`. Task 2.6's verifier still false-positived on em-dash and `§` characters embedded in the .ps1 script itself (PS 5.1 reading the .ps1 file via system codepage during script-load); resolved by inspecting file content directly via `Grep` tool which confirmed all required strings present byte-correctly. No content change to plan or artifacts; verification harness only.

## User Setup Required

None — no external service configuration required. All work is doc-only.

## Next Phase Readiness

- **Plan 03-03 (verification gate, D-20 7-step) prerequisites fully met.** WF-01 (Plan 03-01) and WF-02 (this plan) artifacts are in place; the cross-reference target list is now stable for the negative-control greps in D-20 step 1 (legacy step-name patterns: `PRE-CHECK|MASTER-PLAN|CURSOR-IMPLEMENT|POST-CHECK|AUDIT-1A|VENDOR-RECON|BATCH-AUDIT-MASTER|DOC-UPDATE-MASTER|CHATGPT-SYSTEM` outside `.planning/archive/` should return 0 hits) and step 2 (DOCS_INDEX 1:1 set-diff). The `End-to-end read pass` (D-20 step 4) will read /CONTRIBUTING.md (this plan), spec_classifier/CLAUDE.md (this plan), root CLAUDE.md (this plan), DOCS_INDEX.md (this plan), CHANGELOG.md (this plan), LAUNCHER_README.md (Plan 03-01), .planning/archive/prompts-2026-05-10/README.md (Plan 03-01).
- **Zero blockers introduced.** No `STATE.md` blockers added; no deferred items added; no new threat surface introduced (threat model: documentation-only phase, no trust boundaries crossed per `<threat_model>` block).
- **Milestone-close readiness.** This is the last content plan of the Phase 3 wave; only the verification gate (Plan 03-03) remains before the v1.0 cleanup-and-workflow milestone can be closed via `/gsd-complete-milestone`. The new `/CONTRIBUTING.md` becomes the entry point for any contributor opening the next milestone (v2.0 — likely classification rule improvements per `.planning/REQUIREMENTS.md` v2 backlog).

## Self-Check: PASSED

Created files exist:
- FOUND: CONTRIBUTING.md (repo root, 155 lines)
- FOUND: .planning/archive/CONTRIBUTING-2026-05-10.md (77 lines, Russian content + Phase-2 forwarding note preserved)

Modified files reflect the edits:
- FOUND: spec_classifier/CLAUDE.md (249 lines; legacy block gone; `## Development Cycle` pointer to `../CONTRIBUTING.md` present; `## Project`, `## Paths (Windows)`, `## Current State`, `## CLI Commands`, `## Business Rules`, `## E-codes`, `## Known Tech Debt` all present)
- FOUND: CLAUDE.md (74 lines; `[`/CONTRIBUTING.md`](CONTRIBUTING.md)` pointer present in § Tooling roles; `PRE-CHECK → PLAN → IMPLEMENT` legacy string absent)
- FOUND: spec_classifier/docs/DOCS_INDEX.md (41 lines; `| docs/dev/CONTRIBUTING.md |` row absent; `| prompts/README.md |` row absent; `Repo-root contributor doc:` breadcrumb present)
- FOUND: spec_classifier/CHANGELOG.md (250 lines; `### Changed (Phase 3 — Workflow, 2026-05-10)` sub-section present at line 27; existing Phase 1 + Phase 2 sub-sections preserved; `### Added` section preserved)

Source removed:
- ABSENT: spec_classifier/docs/dev/CONTRIBUTING.md (Test-Path returns False)

Commits exist on `main`:
- FOUND: 2e2edfb (Task 2.1 — chore: archive inner CONTRIBUTING.md)
- FOUND: cb2b3ee (Task 2.2 — docs: author root /CONTRIBUTING.md)
- FOUND: 94bc2af (Task 2.3 — docs: replace deep CLAUDE.md legacy block)
- FOUND: 98a8109 (Task 2.4 — docs: repoint root CLAUDE.md § Tooling roles)
- FOUND: 936b0b0 (Task 2.5 — docs: clean DOCS_INDEX.md)
- FOUND: f16cc85 (Task 2.6 — docs: extend CHANGELOG.md)

D-22 protected-files diff stat (`git diff --stat HEAD~6..HEAD -- spec_classifier/{golden,rules,src,tests,main.py,batch_audit.py,cluster_audit.py,conftest.py} run.ps1 teresa.bat teresa_gui.py`):
- EMPTY (no protected files touched)

---

*Phase: 03-workflow*
*Completed: 2026-05-10*
