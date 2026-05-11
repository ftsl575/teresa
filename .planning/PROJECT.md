# Teresa

## What This Is

Teresa is a deterministic, rule-based Excel-spec classifier for hardware vendor BOMs. It ingests `.xlsx` quotes from six vendors (Dell, Cisco CCW, HPE, Lenovo DCSC, xFusion, Huawei), normalizes each row, classifies it via vendor-specific YAML rules (first-match-wins regex, no ML), and emits structured artifacts plus a post-run audit (E1–E18 + optional LLM mismatch check). The user is a Windows-based operator running it via a PowerShell launcher (`run.ps1`) or a PyQt6 GUI (`teresa_gui.py`).

## Core Value

The classifier produces correct, deterministic, audited artifacts for every supported vendor. Everything else is plumbing.

## Current State

**Last shipped:** v1.1 Periphery cleanup (residual) — 2026-05-11
**Next milestone:** TBD — run `/gsd-new-milestone` to scope.

**v1.1 delivered:**
- Runtime cache redirect (`PYTHONPYCACHEPREFIX` + `PYTEST_ADDOPTS`) wired through `run.ps1` and `teresa_gui.py` from `config.local.yaml::temp_root`; `clean.ps1` runs by default with `-NoClean` opt-out (Phase 4: CACHE-01..04).
- Orphan cleanup: stale `scripts/run_full.ps1` refs gone from `pyproject.toml` + `config.local.yaml.example`; `.cursor/` + `teresa.zip` removed (Phase 5: ORPH-01..04).
- Doc-vs-impl drift sweep: 369 claims swept across 18 files; 10 patches + 3 removes; `spec_classifier/docs/dev/DOC_INVARIANTS.md` created with 8 mechanical Bash one-liner invariants; `run.ps1` ships English `<#.SYNOPSIS#>` help block alongside the preserved RU header; `ONE_BUTTON_RUN.md` 54→50 and `RUN_PATHS_AND_IO_LAYOUT.md` 281→264 (Phase 6: DRIFT-01..04).

**v1.2 candidates** (surfaced during v1.1):
- Per-vendor knowledge documentation (the original v1.2 scope per `[v1.1 Init]`).
- Broader `/gsd-map-codebase` refresh of all 7 `.planning/codebase/` maps + `spec_classifier/CLAUDE.md` + `spec_classifier/README.md` drift sweep (deferred from Phase 6's 16-file scope).
- Pre-commit hook integration of `DOC_INVARIANTS.md` checks (deferred per AUTO-02 — depends on v2.0 cross-platform work).

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

<!-- v1.1 Phase 4 — Cache Redirect closed 2026-05-10 -->

- ✓ `run.ps1` sets `PYTHONPYCACHEPREFIX` and `PYTEST_ADDOPTS` from `config.local.yaml::temp_root` before any Python invocation; `clean.ps1` runs by default with `-NoClean` opt-out — Validated in Phase 4: Cache Redirect (CACHE-01, CACHE-03)
- ✓ `teresa_gui.py` `main()` sets the same env vars before `QApplication` so subprocess-spawned PowerShell children inherit the redirect — Validated in Phase 4: Cache Redirect (CACHE-02)
- ✓ `spec_classifier/docs/dev/ONE_BUTTON_RUN.md` reflects the new clean-by-default + cache-redirect contract; `-NoClean` and `clean.ps1` co-occur in the "Workspace cleanup" section — Validated in Phase 4: Cache Redirect (CACHE-04)

<!-- v1.1 Phase 5 — Orphan Cleanup closed 2026-05-10 -->

- ✓ `spec_classifier/pyproject.toml:5` no longer references the deleted `scripts/run_full.ps1`; rewritten to point at the post-Phase-4 `run.ps1` PYTHONPYCACHEPREFIX wiring — Validated in Phase 5: Orphan Cleanup (ORPH-01)
- ✓ `spec_classifier/config.local.yaml.example:11` no longer references `scripts/run_full.ps1`; rewritten to mention `clean.ps1` and `run.ps1` — Validated in Phase 5: Orphan Cleanup (ORPH-02)
- ✓ Local `.cursor/` directory and `teresa.zip` sandbox artifact removed from working tree — Validated in Phase 5: Orphan Cleanup (ORPH-03, ORPH-04)
- ✓ `CHANGELOG.md` and `LAUNCHER_README.md:4` historical mentions preserved per D-18 historical-content convention — confirmed in Phase 5

<!-- v1.1 Phase 6 — Doc-vs-Impl Drift Sweep closed 2026-05-11 -->

- ✓ Mechanical claim sweep across 13 `spec_classifier/docs/` files + 3 root markdown files (`README.md`, `CLAUDE.md`, `CONTRIBUTING.md`) + 2 `.planning/codebase/` map files: 369 claims audited, 10 patches + 3 removes + 356 `no_drift`; remove > patch heuristic applied — Validated in Phase 6: Doc-vs-Impl Drift Sweep (DRIFT-01)
- ✓ `spec_classifier/docs/user/RUN_PATHS_AND_IO_LAYOUT.md` (281→264) and `spec_classifier/docs/dev/ONE_BUTTON_RUN.md` (54→50) trimmed of duplicated CLI-flag prose; pointer to `run.ps1 -?` added; `run.ps1` ships English `<# .SYNOPSIS / .DESCRIPTION / 5×.PARAMETER / 6×.EXAMPLE #>` help block (RU header at lines 1-13 byte-equal, SHA-frozen) — Validated in Phase 6: Doc-vs-Impl Drift Sweep (DRIFT-02)
- ✓ `spec_classifier/docs/dev/DOC_INVARIANTS.md` created with 8 mechanical Bash one-liner invariants (SC #2 ≥5 floor exceeded); each exits 0 against the post-phase tree (SC #4); audit log at `.planning/phases/06-doc-vs-impl-drift-sweep/06-DRIFT-AUDIT.md` records every (file, line, claim, check, resolution) — Validated in Phase 6: Doc-vs-Impl Drift Sweep (DRIFT-03)
- ✓ Re-sweep against the corrected tree returns 0 drift claims (SC #1); 3 surgical patches to `.planning/codebase/{STACK.md:79, INTEGRATIONS.md:55, INTEGRATIONS.md:150}` close the Phase 5 hand-off (PYTHONPYCACHEPREFIX defense-in-depth vocabulary + HYG-01 username placeholder) — Validated in Phase 6: Doc-vs-Impl Drift Sweep (DRIFT-04)

### Active

(none — v1.1 milestone complete; run `/gsd-new-milestone` to scope v1.2)

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
| One milestone — one work | "Throw out → structure → plan → steps with tests" methodology; v1.1 is cleanup-only; per-vendor knowledge docs are v1.2; classifier rule changes are v2.x | ✓ Good — v1.1 closed clean (10 plans, 18 tasks, zero D-22 violations, zero golden regressions) |
| Sequential plan execution for v1.1 (1 → 2 → 3) | Plan 2 rewrites `pyproject.toml:5` to a wording only true after Plan 1 lands; Plan 3 sweep relies on post-Plan-1+2 state. Parallel execution is unsound | ✓ Good — Phase 4 → 5 → 6 ordering held; Phase 5 D-05/D-06 vocabulary was reused verbatim by Phase 6 D-03 patches as designed |
| `DOC_INVARIANTS.md` is in scope despite "no creation" framing | Tooling/meta-doc materializing the v1.0 retrospective lesson (doc-vs-impl drift not caught by read-pass); domain content (per-vendor docs) stays excluded — that's v1.2 | ✓ Good — shipped 8 invariants (exceeded ≥5 floor); all 8 exit 0 against post-phase tree; 1 invariant tightened during code review (CR-01 caught by `grep -F '.\run.ps1'` addition) |
| Acknowledged debt extension: `config.local.yaml` regex parser | Plan 1 extends an existing 4+-site regex pattern to `temp_root`. Consolidation into `load_config_with_local()` helper deferred to its own milestone (CONCERNS.md § IMPORTANT) — explicit non-goal here | ✓ Good — extension landed without consolidation; helper consolidation remains v1.2/v2.x candidate |
| Cleanup before classification improvements | User wants a hygienic base before iterating on rules; reduces "fix" PRs that revert intentional behavior | ✓ Good — v1.1 close gives a clean, drift-checked base for v1.2 per-vendor work |
| Keep both `CLAUDE.md` files; deduplicate overlap | Root stays a thin pointer; deep reference stays with the code in `spec_classifier/` | ✓ Good — root CLAUDE.md confirmed as 13-line load-bearing summary; spec_classifier/CLAUDE.md untouched in v1.1 (deferred sweep to v1.2) |
| "Done" = clean diff + green tests + GSD-native workflow | Compound criterion: cosmetic cleanup alone is insufficient | ✓ Good — Phase 6 post-execution: pytest 774 passed + 1 xfailed; D-22 byte-equal; goldens byte-equal across full milestone window |
| Strip `C:\Users\G\` username only; do not de-Windowize launchers | Cross-platform is a separate, larger effort; user is Windows-only operator today | ✓ Good — INTEGRATIONS.md:55 retroactive HYG-01 catch landed in Phase 6; cross-platform deferred to v2.0 PLAT-01 |
| Retire (or clearly deprecate) `spec_classifier/prompts/00–08` | GSD-native commands now cover PRE-CHECK / PLAN / IMPLEMENT / POST-CHECK / AUDIT cycle | ✓ Good — archived in v1.0 Phase 3 (WF-01); GSD-native cycle proven through v1.1 |
| Honor "do not fix" tech debt notes | `power_cord=None`, Excel-reading audit, `core/parser.py` Dell-specificity are intentional per project CLAUDE.md; bait for "fix" PRs | ✓ Good — Phase 6 sweep caught 1 USER_GUIDE.md violation (Power Cord LOGISTIC mis-classification) and patched it; invariant #6 protects `power_cord` "intentionally unmapped" comment as a mechanical floor |
| Default to atomic-fix-on-find for code-review findings during auto-mode | Auto-mode mandates fixing clear-cut bugs in the same session rather than punting; CR-01 (`.un.ps1` from `.\r` escape consumption) was a critical bug in Phase 6's own deliverable that would have failed verification | ✓ Good — Phase 6 close: 5 code-review findings auto-fixed (`fix(06)` commits); verifier re-pass confirmed zero residuals; 1 verifier-found 6th sister location patched inline |
| `06-DRIFT-AUDIT.md` records `no_drift` rows alongside drifts | SC #5 wording requires "every claim flagged"; `no_drift` rows make the audit log a complete inventory rather than just a delta — supports re-sweep verification and gives next contributor a meaningful baseline | ✓ Good — 369 rows total (356 no_drift + 10 patch + 3 remove); composite SC #1 re-sweep returned 0 drift |

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
*Last updated: 2026-05-11 after v1.1 milestone (Periphery cleanup) shipped — CACHE-01..04 + ORPH-01..04 + DRIFT-01..04 validated; 12/12 milestone requirements complete.*
