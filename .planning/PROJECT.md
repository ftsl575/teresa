# Teresa

## What This Is

Teresa is a deterministic, rule-based Excel-spec classifier for hardware vendor BOMs. It ingests `.xlsx` quotes from six vendors (Dell, Cisco CCW, HPE, Lenovo DCSC, xFusion, Huawei), normalizes each row, classifies it via vendor-specific YAML rules (first-match-wins regex, no ML), and emits structured artifacts plus a post-run audit (E1–E18 + optional LLM mismatch check). The user is a Windows-based operator running it via a PowerShell launcher (`run.ps1`) or a PyQt6 GUI (`teresa_gui.py`).

## Core Value

The classifier produces correct, deterministic, audited artifacts for every supported vendor. Everything else is plumbing.

## Current Milestone: v1.1 Periphery cleanup (residual)

**Goal:** Throw out residual periphery v1.0 missed — close the runtime-cache architectural gap (`PYTHONPYCACHEPREFIX`), kill orphan references and on-disk junk, and add a doc-vs-impl drift sweep with a mechanical-invariants doc. No code/rules/golden changes.

**Target features:**
- Wire-up runtime cache redirect: `run.ps1` + `teresa_gui.py` set `PYTHONPYCACHEPREFIX` from `config.local.yaml::temp_root` before any Python invocation; `run.ps1` calls `clean.ps1` by default with `-NoClean` opt-out.
- Orphan cleanup: fix two stale `scripts/run_full.ps1` references; remove local `.cursor/` and `teresa.zip`. Leave `CHANGELOG.md` and `LAUNCHER_README.md:4` historical (D-18).
- Doc-vs-impl sweep + trim class A: mechanically check every "code does X" claim across the doc tree, prefer removing drifted claims over editing, trim excess CLI prose, and create `docs/dev/DOC_INVARIANTS.md` with ≥5 mechanical drift checks.

**Sequential dependency:** Plans must run 1 → 2 → 3 (Plan 2 rewrites `pyproject.toml:5` to a wording only true after Plan 1 lands; Plan 3 sweep relies on post-Plan-1+2 state).

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

<!-- v1.0 Cleanup & Workflow Setup milestone — closed 2026-05-10 -->

- ✓ Hardcoded `C:\Users\G\` username scrubbed from committed examples and docs (replaced with per-context placeholders) — Validated in Phase 1: Hygiene (HYG-01)
- ✓ Dual `.gitignore` consolidated into single root file — Validated in Phase 1: Hygiene (HYG-02)
- ✓ Dead / orphan files removed (`commits.txt` + investigated keep list) — Validated in Phase 1: Hygiene (HYG-03)
- ✓ Both READMEs refreshed — root README authored from scratch (129 lines), `spec_classifier/README.md` drift fixed (289 lines); Quick Start runnable verbatim — Validated in Phase 2: Docs (DOC-01, DOC-02)
- ✓ `spec_classifier/docs/` tree audited — DOCS_INDEX 1:1, all 13 files drift-corrected — Validated in Phase 2: Docs (DOC-03)
- ✓ Duplicate content between root `CLAUDE.md` and `spec_classifier/CLAUDE.md` removed — root = thin pointer (74 lines) + 5 critical rules; deep reference translated RU→EN (307 lines) — Validated in Phase 2: Docs (DOC-04)
- ✓ Stale tracking docs refreshed or archived — `CHANGELOG.md` unified to English release-notes; `CURRENT_STATE.md` archived to `.planning/archive/` — Validated in Phase 2: Docs (DOC-05)
- ✓ Old pre-GSD prompts (`spec_classifier/prompts/00–08` + `COWORK_OPUS_FULL_AUDIT.md`) retired — `git mv` to `.planning/archive/prompts-2026-05-10/` with English mapping README — Validated in Phase 3: Workflow (WF-01)
- ✓ Root `CONTRIBUTING.md` authored (155 lines, English, tool-agnostic) — GSD-cycle commands literal, pytest + skip-ratio gate, NEW_VENDOR_GUIDE pointer, "do not fix" rules verbatim — Validated in Phase 3: Workflow (WF-02)

### Active

<!-- v1.1 Periphery cleanup (residual). Requirements derived from MILESTONE-CONTEXT.md → 3 sequential plans. Mapped to phases during roadmap creation. -->

(populated by REQUIREMENTS.md / roadmap step — see `## Current Milestone: v1.1` block above)

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
| One milestone — one work | "Throw out → structure → plan → steps with tests" methodology; v1.1 is cleanup-only; per-vendor knowledge docs are v1.2; classifier rule changes are v2.x | — Pending |
| Sequential plan execution for v1.1 (1 → 2 → 3) | Plan 2 rewrites `pyproject.toml:5` to a wording only true after Plan 1 lands; Plan 3 sweep relies on post-Plan-1+2 state. Parallel execution is unsound | — Pending |
| `DOC_INVARIANTS.md` is in scope despite "no creation" framing | Tooling/meta-doc materializing the v1.0 retrospective lesson (doc-vs-impl drift not caught by read-pass); domain content (per-vendor docs) stays excluded — that's v1.2 | — Pending |
| Acknowledged debt extension: `config.local.yaml` regex parser | Plan 1 extends an existing 4+-site regex pattern to `temp_root`. Consolidation into `load_config_with_local()` helper deferred to its own milestone (CONCERNS.md § IMPORTANT) — explicit non-goal here | — Pending |
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
*Last updated: 2026-05-10 after starting milestone v1.1 (Periphery cleanup, residual).*
