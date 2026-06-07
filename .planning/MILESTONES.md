# Milestones

## v1.2 Output structure reorganization (Shipped: 2026-06-07)

**Phases completed:** 3 phases (7-9), 9 plans, 19 tasks
**Timeline:** 2026-05-11 → 2026-06-07
**Git range:** `feat(07-01)` → `feat(09-03)` (~60 commits in milestone window)
**Tests:** 771 passed + 1 xfailed + 0 skipped; goldens byte-equal end-to-end (no `--update-golden` anywhere in v1.2); routing-only invariant held under git-diff/grep across the milestone window

**Delivered:** Every output artifact routed into three purpose-named buckets under `output_root` (READY / SPLIT / AUDIT), keyed by `<vendor>/<spec>/`, with zero content changes (single content-adjacent exception: the `branded` workbook renamed to its Russian filename on move into READY).

**Key accomplishments:**

1. **Three-bucket layout & main.py routing (Phase 7: LAYOUT-01..03, ROUTE-01/02/05)** — Replaced four timestamp/TOTAL helpers in `run_manager.py` with a single wipe-first `create_spec_folder` (72 → 32 lines). All nine per-spec `main.py` artifacts route to `SPLIT/<vendor>/<spec>/`; the branded workbook routes to `READY/<vendor>/<spec>/Коммерческое предложение_<spec>.xlsx` (filename rename only, bytes byte-equal). Per-run timestamp folder dropped (overwrite-in-place semantics); the TOTAL copy mechanism (`copy_to_total` + call site) removed entirely; all TOTAL/timestamp dead code stripped from `main.py` (387 → 367 lines).

2. **Audit routing → AUDIT (Phase 8: ROUTE-03/04)** — `batch_audit.py` reads `<stem>_annotated.xlsx` from `SPLIT/<vendor>/<spec>/` (rglob) and writes `<stem>_annotated_audited.xlsx` to `AUDIT/<vendor>/<spec>/` via a `relative_to` mirror; batch-level aggregates (`audit_report.json`, `audit_summary.xlsx`, `cluster_summary.xlsx`) written to the AUDIT root; `cluster_audit.py` dual-bucket SPLIT/AUDIT read. Dead path matchers stripped; goldens byte-equal.

3. **Output manifest (Phase 9: MANIFEST-01)** — `output_root/README.md` written once per `main()` via static, byte-stable `run_manager.write_manifest(output_root)`: a file → bucket → purpose table (Russian purpose column) grouped by READY/SPLIT/AUDIT (~14 pattern rows). A single end-to-end run yields exactly `{READY/, SPLIT/, AUDIT/, README.md}` — no legacy `run-*` / `*_run` / `*-TOTAL` layout.

4. **Vendor-detector deduplication (Phase 9: WR-01)** — Single shared `detect_vendor_from_path` extracted into `run_manager.py`; both local copies (in `batch_audit.py` + `cluster_audit.py`) deleted; cluster caller updated to pass `known_vendors` explicitly; hardened to right-to-left per-component matching.

5. **Full-suite verification & test realignment (Phase 9: TEST-01)** — Path/layout tests across `test_output_structure.py`, `test_cli.py`, `test_smoke.py`, `batch_audit`/`cluster_audit` path tests, and a consolidated `test_run_manager.py` (detect-vendor + manifest units) realigned to the `<bucket>/<vendor>/<spec>/` structure; full suite green (771 passed, 1 xfailed, 0 skipped) within the skip-gate. Fixed a latent Cisco branded-spec routing bug surfaced during Phase 7.

**Verification gates:**

| Phase | Gate | Verdict |
|-------|------|---------|
| Phase 7 | READY/SPLIT layout + no run-folder/TOTAL; goldens byte-equal | PASS (5/5 truths) |
| Phase 8 | AUDIT routing; routing-only invariant under git-diff/grep; goldens byte-equal | PASS (4/4 truths) |
| Phase 9 | Manifest + WR-01 dedup + full-suite green; CR-01 (vendor-detector) resolved `4894ba9`; UAT closed | PASS (11/11 truths) |
| Milestone | Audit: 10/10 REQs · 3/3 phases · 4/4 integration seams · 1/1 E2E flow | ✅ PASSED |

**Tech debt deferred to v1.3** (documentation/help-text drift only — routing/classification correct):

- `main.py:240` `--batch-dir` help text still mentions the removed TOTAL aggregation folder (IN-01).
- `main.py:3` module docstring lists only 3 of 6 vendors (IN-01).
- `docs/product/TECHNICAL_OVERVIEW.md:43,50` and `spec_classifier/CLAUDE.md` "OUTPUT layout" section still describe the pre-v1.2 run-folder/TOTAL layout (doc drift).

**Known deferred items at close:** 0 (open-artifact audit clear).

---

## v1.1 Periphery cleanup (residual) (Shipped: 2026-05-11)

**Phases completed:** 3 phases (4-6), 10 plans, 18 tasks
**Timeline:** 2026-05-10 → 2026-05-11 (2 days; final 6-plan Phase 6 ran in a single auto-mode session)
**Git range:** `866dd33` → `9dfe793` (~60 commits in milestone window)
**Tests:** 774 passed + 1 xfailed + 0 skipped (real-data, not structural-skips); zero D-22 violations; goldens byte-equal end-to-end

**Key accomplishments:**

1. **Runtime cache redirect wired (Phase 4: CACHE-01..04)** — `run.ps1` and `teresa_gui.py` both set `PYTHONPYCACHEPREFIX` + `PYTEST_ADDOPTS` from `config.local.yaml::temp_root` before any Python invocation. `clean.ps1` runs by default with `-NoClean` opt-out. Defense-in-depth (both launcher AND GUI) protects against single-source regressions. Closes the runtime-cache architectural gap that v1.0's read-pass DOC-03 audit didn't catch.

2. **Orphan references purged (Phase 5: ORPH-01..04)** — All references to the deleted `scripts/run_full.ps1` removed from `pyproject.toml:5` and `config.local.yaml.example:11`; rewritten with wording true post-Phase-4. Local `.cursor/` directory and `teresa.zip` sandbox artifact removed. `CHANGELOG.md` and `LAUNCHER_README.md:4` historical mentions deliberately preserved per D-18 historical-content convention.

3. **Doc-vs-impl drift sweep (Phase 6: DRIFT-01)** — 369 claims mechanically audited across 18 files (13 `spec_classifier/docs/` + 3 root markdown + 2 `.planning/codebase/` map files). Resolution: 356 `no_drift` + 10 patches + 3 removes. `remove > patch` heuristic applied throughout. Notable patches included: Power Cord LOGISTIC mis-classification in USER_GUIDE.md (load-bearing business rule), HPE no-branded-spec claim in TECHNICAL_OVERVIEW.md, schema column-list omissions, line-number → symbol-ref rewrites.

4. **DRIFT-02 deliverables (Phase 6: DRIFT-02)** — `run.ps1` ships English `<# .SYNOPSIS / .DESCRIPTION / 5×.PARAMETER / 6×.EXAMPLE #>` comment-based help block (RU header at lines 1-13 byte-equal, SHA-frozen at `2c7dd607...`). `ONE_BUTTON_RUN.md` 54→50 lines and `RUN_PATHS_AND_IO_LAYOUT.md` 281→264 lines, both with pointer to `run.ps1 -?` and trimmed CLI-flag duplication.

5. **DOC_INVARIANTS.md mechanical floor (Phase 6: DRIFT-03)** — `spec_classifier/docs/dev/DOC_INVARIANTS.md` created with 8 Bash one-liner invariants (exceeded ≥5 floor): PYTHONPYCACHEPREFIX in `run.ps1` + `teresa_gui.py`, PYTEST_ADDOPTS in `run.ps1`, `clean.ps1` invoked from `run.ps1`, no `run_full` orphans in `*.toml`/`*.example`, `power_cord` "intentionally unmapped" comment present, six-vendor list registered, Phase 6 help block survives. Each cites a real drift incident; all 8 exit 0 against post-phase tree (SC #4 PASS).

6. **Surgical map patches (Phase 6: DRIFT-04)** — 3 surgical line patches to `.planning/codebase/{STACK.md:79, INTEGRATIONS.md:55, INTEGRATIONS.md:150}`. Stale PYTHONPYCACHEPREFIX claims replaced with Phase 5 D-05/D-06 canonical defense-in-depth vocabulary. INTEGRATIONS.md:55 hardcoded `C:\Users\G\` username leak replaced with `C:\Users\<USERNAME>\` per HYG-01 placeholder convention (retroactive v1.0 HYG-01 catch).

7. **Code review caught critical regression in own deliverable** — Phase 6 code review found CR-01: every `.EXAMPLE` line in the new `run.ps1` help block contained `.un.ps1` instead of `.\run.ps1` because `.\r` was consumed as a CR escape during string handling. Auto-fixed via byte-precise replacement (`2e 0d 75 6e` → `2e 5c 72 75 6e`); RU header SHA preserved. Invariant #8 grep tightened to `grep -qF '.\run.ps1'` so future identical regressions trip the gate. 4 additional WR findings (5 stale Cisco/HPE branded.xlsx claims, test_unknown_threshold misattribution to Lenovo) all auto-fixed in the same session.

**Verification gates:**

| Phase | Gate | Verdict |
|-------|------|---------|
| Phase 4 | Cache redirect smoke (`Test-Path .\.pytest_cache` = `$false`) | PASS |
| Phase 5 | `pyproject.toml`/`config.local.yaml.example` no `run_full` refs | PASS |
| Phase 6 | DOC_INVARIANTS 8/8 exit 0; SC #1 re-sweep returns 0 drift | PASS |
| All phases | D-22 protected paths byte-equal across milestone window | PASS |
| All phases | Goldens byte-equal across milestone window | PASS |
| All phases | Pytest skip-ratio gate (`skipped/total < 0.50`, `passed > 0`) | PASS (774/0/1xf in 21s) |

**Issues deferred to v1.2:**

- Broader `/gsd-map-codebase` refresh of all 7 `.planning/codebase/` maps (folds in volatile-counts deferral from Phase 6)
- `spec_classifier/CLAUDE.md` + `spec_classifier/README.md` drift sweep (deepest accumulation of drift-prone claims; out of v1.1's 16-file ROADMAP scope)
- `load_config_with_local()` regex-parser consolidation (CONCERNS.md § IMPORTANT)
- Pre-commit hook + CI integration of DOC_INVARIANTS.md (depends on v2.0 PLAT-01 cross-platform)
- `run.ps1:1-13` Russian header → English translation (D-18 historical-content exemption preserved)

---

## v1.0 Cleanup & Workflow Setup (Shipped: 2026-05-10)

**Phases completed:** 3 phases, 13 plans, 22 tasks
**Timeline:** 2026-05-10 01:31 → 08:11 (~6.5 hours of focused work)
**Git range:** `7976ce1` … `557ed0c` (58 commits in milestone window)
**Files modified:** 84 (mostly docs additions; archive moves; new CONTRIBUTING/README)
**Lines:** +13,285 / -1,667

**Key accomplishments:**

1. **Hygiene baseline established** — `C:\Users\G\` username scrubbed from 17 tracked files via per-context placeholders (PowerShell `$env:USERPROFILE`, batch `%USERPROFILE%`, Python `Path.home()`, Makefile `$(HOME)`, Markdown `<USERNAME>`); dual `.gitignore` consolidated into a single root file; `commits.txt` (51 MB orphan) removed; D-11 5-step verification gate PASS.
2. **Documentation suite translated and refreshed** — `spec_classifier/CLAUDE.md` translated Russian → English (303 → 307 lines, technical identifiers preserved verbatim); root `CLAUDE.md` rewritten as 74-line thin pointer + 5 critical business rules + "where to look" table; root `README.md` authored from scratch (129 lines); `spec_classifier/README.md` drift-fixed (289 lines); 13 `spec_classifier/docs/` files audited end-to-end with `DOCS_INDEX.md` 1:1; `CHANGELOG.md` unified to English release-notes format; `CURRENT_STATE.md` archived to `.planning/archive/`; D-24 7-step verification gate PASS.
3. **GSD-native workflow adopted** — pre-GSD prompt library (10 step prompts + COWORK_OPUS_FULL_AUDIT + README, 1345 lines, Russian) `git mv`'d to `.planning/archive/prompts-2026-05-10/` with English mapping README that maps each retired prompt to its GSD-native equivalent (00→NEW_VENDOR_GUIDE, 01→/gsd-discuss-phase, 02→/gsd-plan-phase, 03→/gsd-execute-phase, 04→/gsd-verify-work, 05→/gsd-audit-fix, 06→batch_audit.py + /gsd-plan-phase, 07→/gsd-docs-update, 08→no GSD equivalent); `LAUNCHER_README.md:52` repointed to `NEW_VENDOR_GUIDE.md`; root `/CONTRIBUTING.md` authored (155 lines, English, tool-agnostic) as the canonical contributor entry-point; D-20 7-step verification gate PASS.
4. **"Do not fix" tech-debt rules carried verbatim** into `/CONTRIBUTING.md` so future contributors don't relapse on the 5 load-bearing items: `power_cord` `hw_type=None` (recovery commit `c3c7cb6`), `core/parser.py` Dell-specificity, `batch_audit.py` reading from `*_annotated.xlsx`, YAML rule order load-bearing first-match-wins, `HW_TYPE_VOCAB` duplication between `classifier.py` and `batch_audit.py`. Source-of-truth pointer back to `.planning/codebase/CONCERNS.md` § BLOCKER + IMPORTANT.
5. **Code-only repository policy enforced** — INPUT, OUTPUT, fixtures, venv all live outside the repo; `OUTPUT/`, `output/`, `test_data/`, `.venv/`, `commits.txt`, `*.zip` gitignored. Archive pattern `.planning/archive/<name>-<date>/` established and reused 3× (CURRENT_STATE-2026-05-10.md, prompts-2026-05-10/, CONTRIBUTING-2026-05-10.md).
6. **Zero regressions across the milestone** — 774 pytest passed throughout all 3 phases (1 xfailed, 0 skipped, 0 failed); 40 golden regression fixtures byte-equal end-to-end (`git diff --stat <pre-Phase-1..post-Phase-3> -- spec_classifier/golden/` empty); D-22 protected files untouched (`spec_classifier/{rules,src,tests,batch_audit.py,cluster_audit.py,main.py,conftest.py}`, `run.ps1`, `teresa.bat`, `teresa_gui.py` all unchanged).

**Verification gates:**

| Phase | Gate | Steps | Verdict |
|-------|------|-------|---------|
| 1. Hygiene | D-11 | 5 (greps + gitignore count + pytest + smoke + diff-review) | PASS |
| 2. Docs | D-24 | 7 (cross-refs + DOCS_INDEX 1:1 + Quick Start + read-pass 19 docs + goldens + pytest + diff-review) | PASS |
| 3. Workflow | D-20 | 7 (cross-refs + DOCS_INDEX 1:1 + Quick Start + read-pass 7 docs + goldens + pytest + diff-review) | PASS |

**Known deferred items at close:** 0 (open-artifact audit clear).

**Out of scope (deferred to v2.0+):**

- Classification rule improvements (CLAS-01) and new vendor onboarding (CLAS-02) — v2.0 backlog
- Cross-platform launcher `run.sh` (PLAT-01) and de-Windows GUI (PLAT-02) — v2.0+ backlog
- CI pipeline (AUTO-01) and pre-commit rule-id validation (AUTO-02) — v2.0+ backlog (depends on PLAT-01)

**Tag:** `v1.0` (created at milestone close)

---
