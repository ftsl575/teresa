# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v1.0 — Cleanup & Workflow Setup

**Shipped:** 2026-05-10
**Phases:** 3 | **Plans:** 13 | **Sessions:** 1 (~6.5 hours of focused work)

### What Was Built
- Hygiene baseline — username scrub across 17 tracked files via per-context placeholders, dual `.gitignore` consolidated, 51 MB `commits.txt` orphan removed
- Documentation suite — `spec_classifier/CLAUDE.md` translated Russian → English (303 → 307 lines), root `CLAUDE.md` rewritten as 74-line thin pointer, root `README.md` authored from scratch (129 lines), `spec_classifier/README.md` drift-fixed, 13 `docs/` files audited end-to-end with DOCS_INDEX 1:1, `CHANGELOG.md` unified to English, `CURRENT_STATE.md` archived
- GSD-native workflow — pre-GSD prompts (10 files + COWORK + README, 1345 lines, Russian) `git mv`'d to `.planning/archive/prompts-2026-05-10/` with English mapping README; root `/CONTRIBUTING.md` authored as canonical tool-agnostic contributor doc; "do not fix" tech-debt rules carried verbatim from `PROJECT.md` / `CONCERNS.md`

### What Worked
- **Per-context placeholder convention (D-01 from Phase 1).** Splitting `<USERNAME>` (markdown), `%USERPROFILE%` (batch), `$env:USERPROFILE` (PowerShell), `Path.home()` (Python), `$(HOME)` (Makefile) instead of one uniform token kept every replacement *runnable*. Uniform `<USERNAME>` would have broken example commands.
- **Archive pattern `.planning/archive/<name>-<date>/`.** Established in Phase 2 D-08 (CURRENT_STATE.md), reused verbatim 2× in Phase 3 (prompts + inner CONTRIBUTING.md). `git mv` preserves history; date suffix lets archives stack. Zero data loss; full reversibility.
- **Strict goal-backward verification gates.** D-11 (5-step), D-24 (7-step), D-20 (7-step) — each phase gated by greps + DOCS_INDEX 1:1 + Quick Start runnability + end-to-end read pass + goldens + pytest + diff-review. Catches doc drift before it ships; PASS verdict carries real meaning.
- **One commit per requirement / per task.** Atomic revertability; clean `git log --oneline` reads like a changelog. Phase 1 (HYG-01/02/03) and Phase 2 (DOC-04/05/01/02/03) and Phase 3 (WF-01/02) all followed this. Total 58 commits; zero amends after the fact.
- **Plan-checker arithmetic catch.** Pre-execution plan-checker found two line-count drift bugs (LAUNCHER 73→72; deep CLAUDE.md ~93→63 lines) that would have produced false-positive verify failures. Fixed inline (17 sites across 3 plan files) without re-spawning the planner.
- **Discuss → Plan → Execute → Verify chain via `--chain`.** End-to-end pipeline ran cleanly for Phase 3 (no manual /clear between stages). Each stage's output flowed into the next without context loss.
- **Tool-agnostic /CONTRIBUTING.md voice.** Choosing "use Claude Code or any AI coding agent" over locking to a specific tool ages well. The deep CLAUDE.md's Cursor/Claude/ChatGPT/Gemini split was deliberately NOT carried forward.

### What Was Inefficient
- **PowerShell stdio noise across `bash -c "powershell.exe -Command \"...\""` chains.** Backticks get eaten; multi-line PS commands need `-File`. Pattern documented in `03-01-SUMMARY.md` § patterns-established for future executor reuse — write per-task verify scripts to `.planning/.tmp_verify_*.ps1`, invoke via `-File`, delete after.
- **MILESTONES.md auto-generated accomplishments were noisy.** SDK pulled "One-liner:" labels from per-plan summaries (lines like `"One-liner:"` and `"Line count:"` ended up as bullet points). Hand-edited the entry to use 6 curated milestone-level accomplishments instead. Future: tune `summary-extract` to look for the actual one-liner *value* below the `One-liner:` label, not the label itself.
- **PROJECT.md evolution wasn't done at Phase 1 / Phase 2 close.** All 9 Active items still showed `[ ]` at the start of Phase 3, despite phases 1 and 2 having closed 8 of them. Did the migration in bulk during Phase 3 wrap-up. Workflow has `update_project_md` step but it's per-phase — needs a cleanup pass at milestone close (which this retrospective just did).
- **Phase 2's `02-VERIFICATION.md` placeholder SHA back-fill cycle.** Took two commits (`b3c9e16` + `972d5ed`) because SUMMARY needed the gate-closure SHA, but the gate-closure commit hadn't happened yet. Phase 3 carried the W-3 fix forward (separate back-fill commit, not `git --amend`); standardized as a pattern.

### Patterns Established
- **D-08 archive pattern.** `git mv <name> .planning/archive/<name>-<YYYY-MM-DD>[.md|/]` with optional README rewrite for navigability. Used 3× in milestone.
- **B-1 SUMMARY-before-commit ordering.** Author SUMMARY.md *before* the wrap-up commit so the commit can stage it. Phase 1 had W-4 ordering bug; Phase 2 fixed it as B-1; Phase 3 carried it forward.
- **W-3 separate SHA back-fill commit.** When SUMMARY references the gate-closure SHA, do the back-fill in a *new* commit, not `git --amend`. Preserves immutable git history.
- **W-5 PASS-WITH-CAVEAT for missing INPUT.** Phase 1 D-21 introduced this for Quick Start runnability checks; Phase 2 + Phase 3 reused. Pre-flight INPUT-presence probe; if absent, gate emits PASS-WITH-CAVEAT not FAIL.
- **D-22 protected-files guard.** Every plan asserts `git diff --stat -- <protected paths>` is empty as a gate. Lifts the "do not fix" framing into a checkable invariant.
- **Per-context placeholder scheme (D-01).** `<USERNAME>` (markdown), `%USERPROFILE%` (batch), `$env:USERPROFILE` (PowerShell), `Path.home()` (Python), `$(HOME)` (Makefile) — never uniform tokens that break example runnability.
- **CHANGELOG immutability.** Historical entries stay verbatim (D-18); new entries land under `[Unreleased]` (D-19); release-notes style preserved.

### Key Lessons
1. **Strict gates have real teeth when the conditions are mechanical.** "Read every doc end-to-end and produce per-file findings" sounded heavy at planning time; it caught real drift in Phase 2's DOC-03 audit and zero drift in Phase 3 (because Phase 2's pass had already cleaned everything). The gate's value is calibrated by the prior pass's quality.
2. **Plan-checker pays for itself before the first execution starts.** The 17 line-count drift sites it caught would have produced false-positive failures across the verification gate. Fixing inline took 5 minutes; debugging the false-positives mid-execution would have taken much longer.
3. **The discuss-phase deferred-ideas section is load-bearing.** Capturing the Backlog (PLAT-01, AUTO-01, CLAS-01..02, etc.) inline instead of "remembering to add it later" prevents scope creep — the answer to "should we also add X?" is consistently "deferred to v2.0, see deferred-ideas section" rather than relitigating each time.
4. **Auto-mode (`--auto`/`--chain`) works for low-judgment phases.** Phase 3 was sharply scoped (WF-01 + WF-02, doc-only, no behavior change). The full Discuss → Plan → Execute → Verify chain ran end-to-end with one user input (gray-area selection at the start). For high-judgment work (Phase 1's orphan-deletion conservative-vs-aggressive question, Phase 2's "translate everything or just CLAUDE.md") the user's hand at the discuss step was essential.
5. **Cross-phase reuse beats per-phase re-derivation.** Phase 2's D-24 7-step gate was a clean adaptation of Phase 1's D-11 5-step gate. Phase 3's D-20 was a clean adaptation of D-24. Each phase added the steps unique to its scope (DOCS_INDEX 1:1 came in at Phase 2 because Phase 1 didn't touch docs/) without re-deriving the rest.

### Cost Observations
- Model mix: 100% sonnet for executor + planner + checker + verifier (per `.planning/config.json`); orchestrator was opus
- Sessions: 1 single end-to-end session (~6.5 hours wall clock, including the discuss-phase + plan-phase + execute-phase + complete-milestone chain)
- Notable: the `--chain` pipeline kept context warm across stage boundaries (no `/clear`), so the planner saw the discuss output and the executor saw the planner's PATTERNS implicitly. For Phase 3 (low-judgment scope) this was efficient; for higher-stakes phases the manual `/clear` between stages would still be appropriate.

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v1.0 | 1 | 3 | Initial GSD adoption — established discuss/plan/execute/verify cycle, archive pattern, strict-gate template |

### Cumulative Quality

| Milestone | Tests | Coverage | Zero-Dep Additions |
|-----------|-------|----------|-------------------|
| v1.0 | 774 passed (1 xfailed, 0 skipped, 0 failed) | unchanged from baseline (no test additions; doc-only milestone) | 0 (zero new runtime dependencies; goal was hygiene + workflow, not feature work) |

### Top Lessons (Verified Across Milestones)

1. *(only one milestone shipped — top lessons emerge after v1.1 / v2.0 cross-validates)*

---
*Last updated: 2026-05-10 after v1.0 milestone close*
