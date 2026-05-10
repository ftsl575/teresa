# Roadmap: Teresa

## Milestones

- ✅ **v1.0 Cleanup & Workflow Setup** — Phases 1-3 (shipped 2026-05-10)
- 🚧 **v1.1 Periphery cleanup (residual)** — Phases 4-6 (in progress)

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3, 4, 5, 6): Planned milestone work
- Decimal phases (e.g., 4.1): Urgent insertions (marked with INSERTED)
- v1.1 continues numbering from v1.0 (started Phase 4); never restart at 1

<details>
<summary>✅ v1.0 Cleanup & Workflow Setup (Phases 1-3) — SHIPPED 2026-05-10</summary>

- [x] Phase 1: Hygiene (4/4 plans) — completed 2026-05-10
- [x] Phase 2: Docs (6/6 plans) — completed 2026-05-10
- [x] Phase 3: Workflow (3/3 plans) — completed 2026-05-10

Full details: [`.planning/milestones/v1.0-ROADMAP.md`](milestones/v1.0-ROADMAP.md)

</details>

### 🚧 v1.1 Periphery cleanup (residual) (In Progress)

**Milestone Goal:** Throw out residual periphery v1.0 missed — close the runtime-cache architectural gap (`PYTHONPYCACHEPREFIX`), kill orphan references and on-disk junk, and add a doc-vs-impl drift sweep with a mechanical-invariants doc. No code/rules/golden changes.

**Sequential dependency:** Phases run 4 → 5 → 6 strictly. Plan 2 rewrites `pyproject.toml:5` to wording only true after Plan 1 lands; Plan 3 sweep relies on post-Plan-1+2 state. Do not parallelize.

- [ ] **Phase 4: Cache Redirect** — Wire `PYTHONPYCACHEPREFIX` from `temp_root` through `run.ps1` and `teresa_gui.py`; default-on `clean.ps1` with `-NoClean` opt-out; doc reflection in `ONE_BUTTON_RUN.md`.
- [ ] **Phase 5: Orphan Cleanup** — Kill stale `scripts/run_full.ps1` references in `pyproject.toml` and `config.local.yaml.example`; remove residual `.cursor/` and `teresa.zip`.
- [ ] **Phase 6: Doc-vs-Impl Drift Sweep** — Mechanical claim sweep across 13 `docs/` + 3 root markdown files; trim CLI prose in 2 named docs; create `DOC_INVARIANTS.md` with ≥5 mechanical checks; re-sweep returns 0.

## Phase Details

### Phase 4: Cache Redirect
**Goal**: Runtime `__pycache__` and `.pytest_cache` artifacts land in `$temp_root\__pycache__` (outside the repo working tree) for every entry point — `run.ps1`, `teresa.bat`, and `teresa_gui.py`. `run.ps1` cleans by default with a `-NoClean` opt-out, and `ONE_BUTTON_RUN.md` reflects the new contract.
**Depends on**: Phase 3 (v1.0 close — clean baseline; `config.local.yaml` regex parser exists; `clean.ps1` exists; `temp_root` key already on disk per CONCERNS.md § IMPORTANT)
**Requirements**: CACHE-01, CACHE-02, CACHE-03, CACHE-04
**Success Criteria** (what must be TRUE):
  1. After `.\run.ps1 -Vendor huawei -NoAi -SkipTests`, `Test-Path .\.pytest_cache` returns `$false` and `Test-Path .\spec_classifier\__pycache__` returns `$false` (no cache pollution inside the repo).
  2. After the same run, `Test-Path "$temp_root\__pycache__"` returns `$true` (cache redirected to the configured external root).
  3. `run.ps1 -NoClean` runs end-to-end without invoking `clean.ps1`, and a plain `run.ps1` invokes `clean.ps1` exactly once at the start of the run.
  4. `docs/dev/ONE_BUTTON_RUN.md` "Workspace cleanup" section names `clean.ps1` as default-on with `-NoClean` opt-out (grep verifies the strings `-NoClean` and `clean.ps1` co-occur in that section).
  5. Launching `teresa_gui.py` and triggering one classification run from the GUI produces no `__pycache__` directory under the repo (same external-root invariant as criterion 1, via the GUI dispatch path).
**D-22 guard step**: `git diff --stat HEAD~ -- spec_classifier/src spec_classifier/rules spec_classifier/golden spec_classifier/tests spec_classifier/batch_audit.py spec_classifier/cluster_audit.py spec_classifier/main.py spec_classifier/conftest.py` MUST be empty. Any nonzero diff inside D-22 protected paths = phase gate FAIL.
**Pytest skip-ratio gate**: Run `pytest -q` from `spec_classifier/`; session must finish without tripping `conftest.py::pytest_sessionfinish` `skipped/total > 0.50` guard. Record `passed/skipped/failed/xfailed` counts in the phase SUMMARY.
**Goldens byte-equal gate**: `git diff --stat -- spec_classifier/golden/` MUST be empty across the phase window (40 `*_expected.jsonl` fixtures unchanged byte-for-byte). No `--update-golden` runs sanctioned in v1.1.
**Plans:** 3 plans (Wave 1, all parallel — disjoint files)

Plans:
- [x] 04-01-PLAN.md — run.ps1: -NoClean switch, temp_root parse, PYTHONPYCACHEPREFIX/PYTEST_ADDOPTS env vars, default-on clean.ps1 invocation (CACHE-01, CACHE-03)
- [x] 04-02-PLAN.md — teresa_gui.py: _discover_temp_path() + cache-redirect env vars set in main() before QApplication (CACHE-02)
- [x] 04-03-PLAN.md — ONE_BUTTON_RUN.md: 3 coordinated edits (numbered list, switches block, Workspace cleanup section) (CACHE-04)

### Phase 5: Orphan Cleanup
**Goal**: All references to the deleted `scripts/run_full.ps1` are gone from canonical config files, replaced with wording that's true post-Phase-4 (i.e., `run.ps1` sets `PYTHONPYCACHEPREFIX` automatically). The local `.cursor/` directory and `teresa.zip` sandbox artifact are removed from the working tree. `CHANGELOG.md` and `LAUNCHER_README.md:4` retain their historical mentions per D-18 / D-19 historical-content convention.
**Depends on**: Phase 4 (ORPH-01's `pyproject.toml:5` rewrite presumes Phase 4's wiring is real; replacement wording references `run.ps1`'s new `PYTHONPYCACHEPREFIX` behavior).
**Requirements**: ORPH-01, ORPH-02, ORPH-03, ORPH-04
**Success Criteria** (what must be TRUE):
  1. `grep -rn "run_full" .` (excluding `CHANGELOG.md`, `LAUNCHER_README.md`, `.planning/`) returns zero matches across the entire repo.
  2. `spec_classifier/pyproject.toml:5` references `run.ps1` (not `scripts/run_full.ps1`); the wording is consistent with Phase 4's `PYTHONPYCACHEPREFIX` wiring.
  3. `spec_classifier/config.local.yaml.example:11` references `scripts/clean.ps1` and `run.ps1` (not `scripts/run_full.ps1`).
  4. `Test-Path .\.cursor` returns `$false` and `Test-Path .\teresa.zip` returns `$false` in the working tree (both confirmed gitignored, removed without modifying `.gitignore`).
  5. `LAUNCHER_README.md:4` still contains its "replaces three legacy scripts" mention (historical, untouched per D-18); same for any `CHANGELOG.md` historical entries.
**D-22 guard step**: `git diff --stat` for the phase window MUST show zero bytes changed inside `spec_classifier/{src,rules,golden,tests,batch_audit.py,cluster_audit.py,main.py,conftest.py}`. Any nonzero diff = phase gate FAIL.
**Pytest skip-ratio gate**: Run `pytest -q` from `spec_classifier/`; session must finish without tripping the 0.50 skip-ratio guard. Phase 5 cannot lower the active-test ratio below threshold.
**Goldens byte-equal gate**: `git diff --stat -- spec_classifier/golden/` MUST be empty across the phase window. No `--update-golden`.
**Plans**: TBD

### Phase 6: Doc-vs-Impl Drift Sweep
**Goal**: Every "code does X" claim across the 13 `spec_classifier/docs/` files and the 3 root markdown files (`README.md`, `CLAUDE.md`, `CONTRIBUTING.md`) is mechanically verified post-Phase-4-and-5; drifted claims are removed (preferred) or fixed; `RUN_PATHS_AND_IO_LAYOUT.md` and `ONE_BUTTON_RUN.md` are trimmed of duplicated CLI-flag prose; `docs/dev/DOC_INVARIANTS.md` is created with ≥5 mechanical drift invariants; a fresh re-sweep returns 0 drift claims.
**Depends on**: Phase 5 (sweep runs against the post-Phase-4-and-5 tree; `pyproject.toml`, `config.local.yaml.example`, `ONE_BUTTON_RUN.md`, and the cache-redirect wiring all need to be settled before claims are checked).
**Requirements**: DRIFT-01, DRIFT-02, DRIFT-03, DRIFT-04
**Success Criteria** (what must be TRUE):
  1. Re-running the mechanical sweep (grep / `Test-Path` / runtime check) against the 16 in-scope files (13 `spec_classifier/docs/` + root `README.md` + root `CLAUDE.md` + root `CONTRIBUTING.md`) yields 0 drift claims.
  2. `docs/dev/DOC_INVARIANTS.md` exists and contains at least 5 mechanical invariants, each with a one-line shell or Python check (e.g., `grep -q "PYTHONPYCACHEPREFIX" run.ps1` exit-code 0).
  3. `docs/dev/RUN_PATHS_AND_IO_LAYOUT.md` and `docs/dev/ONE_BUTTON_RUN.md` are reduced in size (line count strictly less than pre-phase baseline) and the trimmed CLI-flag prose is replaced with a pointer to `run.ps1 -?`.
  4. Each of the 5 (or more) `DOC_INVARIANTS.md` checks executes successfully (exit 0) against the post-phase tree, demonstrating the invariants are accurate, not aspirational.
  5. The sweep audit log (recorded in the phase SUMMARY) lists every file checked, every claim flagged, and the resolution (remove vs. patch) for each — preference is "remove > patch".
**D-22 guard step**: `git diff --stat` for the phase window MUST show zero bytes changed inside `spec_classifier/{src,rules,golden,tests,batch_audit.py,cluster_audit.py,main.py,conftest.py}`. Doc-only edits permitted; any code/rules/golden/test diff = phase gate FAIL.
**Pytest skip-ratio gate**: Run `pytest -q` from `spec_classifier/`; session must finish without tripping the 0.50 skip-ratio guard. Doc edits cannot affect test discovery.
**Goldens byte-equal gate**: `git diff --stat -- spec_classifier/golden/` MUST be empty across the phase window. No `--update-golden`.
**No new tech-stack constraint**: `DOC_INVARIANTS.md` checks may invoke only Python 3.10, `openpyxl`, `pandas`, `pyyaml`, `pytest`, plus standard shell utilities (`grep`, `Test-Path`). No new runtime dependencies introduced.
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order; v1.1 is strictly sequential: 4 → 5 → 6. No parallel execution.

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Hygiene | v1.0 | 4/4 | Complete | 2026-05-10 |
| 2. Docs | v1.0 | 6/6 | Complete | 2026-05-10 |
| 3. Workflow | v1.0 | 3/3 | Complete | 2026-05-10 |
| 4. Cache Redirect | v1.1 | 0/3 | Planning complete | - |
| 5. Orphan Cleanup | v1.1 | 0/TBD | Not started | - |
| 6. Doc-vs-Impl Drift Sweep | v1.1 | 0/TBD | Not started | - |

## Coverage

v1.1 requirements mapped: 12 / 12 ✓
- Phase 4: CACHE-01, CACHE-02, CACHE-03, CACHE-04 (4 reqs)
- Phase 5: ORPH-01, ORPH-02, ORPH-03, ORPH-04 (4 reqs)
- Phase 6: DRIFT-01, DRIFT-02, DRIFT-03, DRIFT-04 (4 reqs)

No orphans. No duplicates. Each requirement maps to exactly one phase.

## Cross-Phase Invariants (v1.1)

These constraints apply to **every phase** in v1.1; phase-level gate steps reaffirm them:

1. **D-22 protected paths.** Any diff inside `spec_classifier/{src,rules,golden,tests,batch_audit.py,cluster_audit.py,main.py,conftest.py}` = phase gate FAIL. Doc-only and launcher-only edits sanctioned.
2. **Pytest skip-guard.** `conftest.py::pytest_sessionfinish` fails if `skipped/total > 0.50` or `passed == 0`. Cleanup must not trip this.
3. **Goldens byte-equal.** All 40 `spec_classifier/golden/*_expected.jsonl` fixtures remain byte-equal end-to-end. No `--update-golden` runs in v1.1.
4. **No tech-stack additions.** Python 3.10, `openpyxl`, `pandas`, `pyyaml`, `pytest` only. No new runtime dependencies.
5. **YAML rule order untouched.** First-match-wins is load-bearing; cleanup never sorts or reorders rule blocks. (Out of scope for v1.1 anyway via D-22, but stated explicitly.)
6. **"Do not fix" tech-debt items honored.** `power_cord` `hw_type=None`, `core/parser.py` Dell-specificity, `batch_audit.py` reading from Excel, `HW_TYPE_VOCAB` duplication remain untouched per `.planning/codebase/CONCERNS.md` BLOCKER + IMPORTANT sections.

---
*v1.0 milestone closed 2026-05-10. Per-phase details preserved in `.planning/milestones/v1.0-ROADMAP.md`. v1.1 roadmap created 2026-05-10; 12/12 requirements mapped across phases 4-6.*
