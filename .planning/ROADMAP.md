# Roadmap: Teresa â€” Cleanup & Workflow Setup Milestone

## Overview

This milestone is hygiene-first. Three phases take the brownfield repo from drift to a defensible baseline: scrub committed username leakage and dead files (Phase 1), reconcile every doc against post-hygiene reality (Phase 2), and lock in a GSD-native development cycle so future contributors don't relapse (Phase 3). Strict non-goals: no classification rule edits, no `power_cord` taxonomy changes, no `batch_audit.py` Excel-reader rewrite, no `core/parser.py` move, no `HW_TYPE_VOCAB` dedup, no YAML rule reorders. All 40 golden regression files must continue to pass byte-for-byte.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Hygiene** - Scrub hardcoded `C:\Users\G\` paths, consolidate dual `.gitignore`, remove dead/orphan files
- [ ] **Phase 2: Docs** - Refresh both READMEs, audit `docs/` tree, deduplicate root vs `spec_classifier/CLAUDE.md`, reconcile or archive `CHANGELOG.md` / `CURRENT_STATE.md`
- [ ] **Phase 3: Workflow** - Retire pre-GSD `prompts/` templates and author repo-root `CONTRIBUTING.md` documenting the GSD cycle

## Phase Details

### Phase 1: Hygiene
**Goal**: Repo contains no committed username leakage, no duplicate ignore rules, and no orphan/scratch files; pytest still green and all 40 goldens still pass.
**Depends on**: Nothing (first phase)
**Requirements**: HYG-01, HYG-02, HYG-03
**Success Criteria** (what must be TRUE):
  1. `git grep -n 'C:\\Users\\G\\'` against tracked files returns zero results; remaining absolute Windows paths use `<USERNAME>`, `%USERPROFILE%`, `$HOME`, or `<INPUT_ROOT>` placeholders.
  2. Exactly one `.gitignore` exists in the working tree (root); the previous `spec_classifier/.gitignore` is deleted and root coverage continues to ignore `.venv/`, `OUTPUT/`, `output/`, `test_data/`, `commits.txt`, `*.zip`, `.cursor/`, `.claude/`, `config.local.yaml`.
  3. Tracked dead files (`commits.txt`, any `*.bak`, abandoned scratch modules, stray `*.zip`) are no longer present, and the removal list is captured in the phase SUMMARY for the eventual PR description.
  4. `pytest tests/ -v --tb=short` (run from `spec_classifier/`) still passes with the same skip ratio behavior â€” the cleanup must not trip `conftest.py:pytest_sessionfinish` (`skipped/total > 0.50` or `passed == 0`).
**Constraints honored** (per PROJECT.md Out of Scope and `.planning/codebase/CONCERNS.md`):
- No edits to `spec_classifier/rules/*.yaml` rule order or content (first-match-wins is load-bearing).
- No `power_cord` `hw_type` change; `_E8_NO_HW_TYPE_DEVICES` whitelist stays as-is.
- No move of `spec_classifier/src/core/parser.py`; no `HW_TYPE_VOCAB` dedup; no `batch_audit.py` switch from Excel to JSONL.
- Launchers stay Windows-only by design â€” only the username string is scrubbed; `run.ps1`, `teresa.bat`, `teresa_gui.py` remain PowerShell/Windows.
**Plans**: 4 plans
- [x] 01-01-PLAN.md — HYG-01 username scrub across 17 tracked files (per-context placeholders per D-01)
- [x] 01-02-PLAN.md — HYG-02 consolidate dual .gitignore into single root file
- [x] 01-03-PLAN.md — HYG-03 remove dead/orphan files (commits.txt; investigated keep list)
- [x] 01-04-PLAN.md — D-11 verification gate (greps + pytest + smoke + diff review) and phase commits

### Phase 2: Docs
**Goal**: Every present documentation file (root + `spec_classifier/`) accurately describes the post-Phase-1 codebase, with no duplicated business-rule content between root `CLAUDE.md` and `spec_classifier/CLAUDE.md`, and tracking docs (`CHANGELOG.md`, `CURRENT_STATE.md`) either current or archived with a forwarding pointer.
**Depends on**: Phase 1 (docs reflect post-hygiene paths and file layout)
**Requirements**: DOC-01, DOC-02, DOC-03, DOC-04, DOC-05
**Success Criteria** (what must be TRUE):
  1. Root `README.md` and `spec_classifier/README.md` Quick Start instructions, when followed verbatim by a fresh user, produce a working classifier run; `C:\venv` is documented as a default suggestion (override via `config.local.yaml`), not a hard requirement.
  2. `spec_classifier/docs/DOCS_INDEX.md` lists every doc currently present under `spec_classifier/docs/` and only docs that exist (no broken cross-references in either direction); stale content has been rewritten or removed.
  3. Root `CLAUDE.md` is a thin pointer/repo-layout note â€” no business rule, E-code table, alias-table, or pipeline-stage detail is duplicated from `spec_classifier/CLAUDE.md`; the deep reference remains in `spec_classifier/CLAUDE.md`.
  4. `spec_classifier/CHANGELOG.md` and `spec_classifier/CURRENT_STATE.md` are either refreshed against current state or moved to `.planning/archive/` (or deleted) with a one-line note in the surviving doc pointing to the replacement source-of-truth (git log + GSD `.planning/` artifacts).
**Constraints honored**:
- No business-rule re-derivation â€” copy/preserve the existing wording in `spec_classifier/CLAUDE.md` (`power_cord=None`, LOGISTIC scope, BASE rules, alias-table semantics, "do not fix" markers all stay verbatim where they live today).
- No documentation of intent to fix the load-bearing tech debt items in `.planning/codebase/CONCERNS.md` BLOCKER section; if mentioned, frame as "intentional, see CONCERNS.md".
- No new doc files invented beyond what the requirements call for (the separate onboarding guide is explicitly Out of Scope per PROJECT.md).
**Plans**: 6 plans
- [x] 02-01-PLAN.md — DOC-04: translate spec_classifier/CLAUDE.md to English + dedup root CLAUDE.md
- [x] 02-02-PLAN.md — DOC-05: refresh CHANGELOG to English-unified release notes + archive CURRENT_STATE.md
- [x] 02-03-PLAN.md — DOC-01: author root README.md from scratch (~80–120 lines)
- [x] 02-04-PLAN.md — DOC-02: refresh spec_classifier/README.md drift fixes
- [ ] 02-05-PLAN.md — DOC-03: audit spec_classifier/docs/ tree end-to-end + DOCS_INDEX 1:1
- [ ] 02-06-PLAN.md — D-23/D-24 verification gate + final commits per requirement

### Phase 3: Workflow
**Goal**: Future contributors and future-Claude have one obvious development cycle to follow (the GSD cycle), the legacy `prompts/00..08` + `COWORK_OPUS_FULL_AUDIT.md` cannot accidentally be reused as the canonical process, and the "do not fix" tech-debt rules are explicitly carried into `CONTRIBUTING.md` so they survive the next refactor PR.
**Depends on**: Phase 2 (CONTRIBUTING.md cross-references the refreshed README, DOCS_INDEX, and `NEW_VENDOR_GUIDE`)
**Requirements**: WF-01, WF-02
**Success Criteria** (what must be TRUE):
  1. `spec_classifier/prompts/` either no longer exists, OR contains only a deprecation notice (`prompts/README.md` updated) plus pointers from each retired template to its GSD-native equivalent (`/gsd-discuss-phase`, `/gsd-plan-phase`, `/gsd-execute-phase`, `/gsd-verify-work`); `00_VENDOR-RECON.md` is replaced or pointed at `spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md`.
  2. `CONTRIBUTING.md` exists at the repo root and documents (a) the GSD cycle by command, (b) how to run pytest from `spec_classifier/` including the skip-ratio gate, (c) how to add a vendor (link only â€” points at `spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md`, no duplication), and (d) the project's "do not fix" tech-debt rules verbatim from PROJECT.md and `.planning/codebase/CONCERNS.md` BLOCKER section (`power_cord=None`, `core/parser.py` Dell-specific, `batch_audit.py` reads Excel, YAML rule order load-bearing, `HW_TYPE_VOCAB` duplication).
  3. Any reference in retained docs (READMEs, `CLAUDE.md` files, `DOCS_INDEX.md`) to the legacy PRE-CHECK / MASTER-PLAN / IMPLEMENT / POST-CHECK prompt sequence either points to the GSD-native equivalent or links to the deprecation notice; no cross-reference points at a file that no longer exists.
**Constraints honored**:
- `CONTRIBUTING.md` documents the existing GSD cycle and the project's existing "do not fix" rules â€” it does not re-author rules or invent new policy.
- The retire decision per template (delete vs archive vs deprecation-stub) is documented in the phase SUMMARY so the rationale survives.
- No edits to `spec_classifier/CLAUDE.md` business-rule sections, even if it currently references the retired prompts (update the cross-reference only).
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 â†’ 2 â†’ 3

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Hygiene | 4/4 | Complete | 2026-05-10 |
| 2. Docs | 4/6 | In Progress|  |
| 3. Workflow | 0/TBD | Not started | - |

---
*Roadmap created: 2026-05-10*
