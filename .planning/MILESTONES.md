# Milestones

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
