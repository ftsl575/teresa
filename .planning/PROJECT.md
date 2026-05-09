# Teresa

## What This Is

Teresa is a deterministic, rule-based Excel-spec classifier for hardware vendor BOMs. It ingests `.xlsx` quotes from six vendors (Dell, Cisco CCW, HPE, Lenovo DCSC, xFusion, Huawei), normalizes each row, classifies it via vendor-specific YAML rules (first-match-wins regex, no ML), and emits structured artifacts plus a post-run audit (E1–E18 + optional LLM mismatch check). The user is a Windows-based operator running it via a PowerShell launcher (`run.ps1`) or a PyQt6 GUI (`teresa_gui.py`).

## Core Value

The classifier produces correct, deterministic, audited artifacts for every supported vendor. Everything else is plumbing.

## Requirements

### Validated

<!-- Inferred from existing codebase per .planning/codebase/ARCHITECTURE.md and STACK.md -->

- ✓ Six vendor adapters (Dell, Cisco, HPE, Lenovo, Huawei, xFusion) under a `VendorAdapter` ABC contract — existing
- ✓ Five-stage pipeline: parse → normalize → classify → write artifacts → optional batch aggregation — existing (`spec_classifier/main.py:_run_single`)
- ✓ Rule engine with first-match-wins YAML rules per vendor — existing (`spec_classifier/src/rules/rules_engine.py`)
- ✓ Post-run audit (E1–E18) with optional OpenAI mismatch checking — existing (`spec_classifier/batch_audit.py`)
- ✓ Cluster audit mining UNKNOWN / mismatch rows for new rule discovery — existing (`spec_classifier/cluster_audit.py`)
- ✓ Pytest suite (~420 tests) with golden-file regression across 40 fixtures — existing
- ✓ Windows launcher: PowerShell orchestrator + double-click .bat + PyQt6 GUI — existing
- ✓ Output artifacts: `classification.jsonl`, `cleaned_spec.xlsx`, `<stem>_annotated.xlsx`, branded spec (Dell-only), TOTAL aggregation — existing

### Active

<!-- Cleanup & workflow milestone -->

- [ ] Old pre-GSD prompts (`spec_classifier/prompts/00–08` + `COWORK_OPUS_FULL_AUDIT.md`) retired or repurposed
- [ ] Stale tracking docs (`CHANGELOG.md`, `CURRENT_STATE.md`) refreshed or archived
- [ ] Duplicate content between root `CLAUDE.md` and `spec_classifier/CLAUDE.md` removed (both files kept; root = thin pointer, deep one stays under `spec_classifier/`)
- [ ] Hardcoded `C:\Users\G\` username scrubbed from committed examples and docs (replaced with `<USERNAME>` placeholder)
- [ ] Dual `.gitignore` consolidated (root + `spec_classifier/.gitignore`)
- [ ] Dead / orphan files identified and removed (unimported modules, `commits.txt`, `.bak`, etc.)
- [ ] Both READMEs (root `README.md` + `spec_classifier/README.md`) refreshed — drift fixed, Quick Start verified working
- [ ] `spec_classifier/docs/` tree audited (`DOCS_INDEX.md` accurate, stale content removed, drift corrected)
- [ ] `CONTRIBUTING.md` authored documenting the GSD development cycle for future contributors

### Out of Scope

- Classification rule improvements or new vendors — explicitly deferred to a later milestone
- Cross-platform launcher (`run.sh`, POSIX GUI dispatch) — Windows-first is the chosen position; just strip username from examples
- CI pipeline (GitHub Actions, etc.) — depends on cross-platform support; deferred
- Merging the two `CLAUDE.md` files into one — chose to keep both and just deduplicate
- Regenerating `CLAUDE.md` from a GSD baseline — chose to preserve hand-written content
- A separate onboarding guide doc — folded into README refresh + `CONTRIBUTING.md`
- "Do not fix" tech debt items — `power_cord` `hw_type=None`, `batch_audit.py` reading from Excel, `src/core/parser.py` being Dell-specific, `HW_TYPE_VOCAB` duplication. These are load-bearing per `spec_classifier/CLAUDE.md`; explicit non-goals for this milestone (see `.planning/codebase/CONCERNS.md`).

## Context

- Brownfield init: existing codebase mapped in `.planning/codebase/` (STACK, ARCHITECTURE, STRUCTURE, CONVENTIONS, TESTING, INTEGRATIONS, CONCERNS) on 2026-05-09/10.
- The repo is two layers stacked: a thin Windows launcher at the root (`run.ps1`, `teresa.bat`, `teresa_gui.py`) and the actual codebase under `spec_classifier/`. There is no Python package; code runs from `spec_classifier/` as cwd.
- Code-only repo policy: INPUT specs, OUTPUT runs, fixtures, and the venv all live outside the repo (default `%USERPROFILE%\Desktop\INPUT|OUTPUT`, venv at `C:\venv`). `config.local.yaml` overlays `config.yaml` at runtime to point at absolute paths.
- A pre-GSD development cycle exists in `spec_classifier/prompts/01_PRE-CHECK.md` … `08_CHATGPT-SYSTEM-PROMPTS.md` plus `COWORK_OPUS_FULL_AUDIT.md`. Several of these duplicate functionality now provided natively by `/gsd-*` commands.
- Pytest gates the session via `conftest.py:pytest_sessionfinish` — fails if `skipped/total > 0.50` or `passed == 0`. Cleanup must not trip this gate.
- Tracked recovery commits (e.g. `c3c7cb6` for `power_cord` taxonomy) document past "fix attempts" that reverted intentional behavior; cleanup must not regress these.

## Constraints

- **Tech stack**: Python (CPython 3.10), `openpyxl>=3.1.0`, `pandas>=2.0.0`, `pyyaml>=6.0`, `pytest>=7.0.0`. Do not introduce new runtime dependencies.
- **Platform**: Windows-first by user decision. Launchers (`run.ps1`, `teresa.bat`, `teresa_gui.py`) remain Windows-only this milestone.
- **Compatibility**: All 40 golden regression fixtures (`spec_classifier/golden/*_expected.jsonl`) must continue to pass byte-for-byte. No classification behavior changes.
- **YAML rule order is load-bearing**: First-match-wins. Cleanup must not reorder rule blocks within `spec_classifier/rules/*_rules.yaml`.
- **Pytest skip-guard**: Session fails if `skipped/total > 0.50`. Reorganizing fixtures or test files must keep the active test ratio above the threshold.
- **No behavior change**: This milestone is hygiene only. Any classifier or audit logic edits land in a follow-up milestone.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Cleanup before classification improvements | User wants a hygienic base before iterating on rules; reduces "fix" PRs that revert intentional behavior | — Pending |
| Keep both `CLAUDE.md` files; deduplicate overlap | Root stays a thin pointer; deep reference stays with the code in `spec_classifier/` | — Pending |
| "Done" = clean diff + green tests + GSD-native workflow | Compound criterion: cosmetic cleanup alone is insufficient | — Pending |
| Strip `C:\Users\G\` username only; do not de-Windowize launchers | Cross-platform is a separate, larger effort; user is Windows-only operator today | — Pending |
| Retire (or clearly deprecate) `spec_classifier/prompts/00–08` | GSD-native commands now cover PRE-CHECK / PLAN / IMPLEMENT / POST-CHECK / AUDIT cycle | — Pending |
| Honor "do not fix" tech debt notes | `power_cord=None`, Excel-reading audit, `core/parser.py` Dell-specificity are intentional per project CLAUDE.md; bait for "fix" PRs | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-05-10 after initialization*
