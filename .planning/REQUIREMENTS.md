# Requirements: Teresa — Milestone v1.1

**Defined:** 2026-05-10
**Milestone:** v1.1 Periphery cleanup (residual)
**Core Value:** The classifier produces correct, deterministic, audited artifacts for every supported vendor. Everything else is plumbing.

## v1.1 Requirements

Requirements for milestone v1.1. Each maps to one phase via the roadmap.

**Methodology:** "Throw out → structure → plan → steps with tests." One milestone, one work — v1.1 is cleanup-only. No code/rules/golden changes (D-22 protected).

**Plan execution order:** Plan 1 → Plan 2 → Plan 3. Plan 2 rewrites `pyproject.toml:5` to wording only true after Plan 1 lands; Plan 3 sweep relies on post-Plan-1+2 state. Sequential dependency; parallel execution unsound.

### Cache Redirect (CACHE) — Plan 1: Wire-up runtime cache redirect

- [ ] **CACHE-01**: `run.ps1` reads `temp_root` from `spec_classifier/config.local.yaml` and sets `$env:PYTHONPYCACHEPREFIX = Join-Path $temp_root "__pycache__"` before any Python invocation.
- [ ] **CACHE-02**: `teresa_gui.py` sets `os.environ["PYTHONPYCACHEPREFIX"]` from the same `temp_root` source in `__main__`, before any `subprocess.Popen`/`subprocess.run` invocation.
- [ ] **CACHE-03**: `run.ps1` invokes `clean.ps1` by default and accepts a `-NoClean` switch to opt out.
- [ ] **CACHE-04**: `docs/dev/ONE_BUTTON_RUN.md` "Workspace cleanup" section reflects clean-by-default + `-NoClean` opt-out.

**Verification (smoke after `.\run.ps1 -Vendor huawei -NoAi -SkipTests`):**

- `Test-Path .\.pytest_cache` = `$false`
- `Test-Path .\spec_classifier\__pycache__` = `$false`
- `Test-Path "$temp_root\__pycache__"` = `$true`

### Orphan Cleanup (ORPH) — Plan 2: Orphan cleanup

- [ ] **ORPH-01**: `spec_classifier/pyproject.toml:5` no longer references the deleted `scripts/run_full.ps1`; replaced with a wording true post-CACHE-01 (e.g., "Set it in your shell profile or use run.ps1 (sets PYTHONPYCACHEPREFIX automatically).").
- [ ] **ORPH-02**: `spec_classifier/config.local.yaml.example:11` no longer references `scripts/run_full.ps1` (rewritten to "Used by scripts/clean.ps1 and run.ps1." or equivalent).
- [ ] **ORPH-03**: Local `.cursor/` directory removed from working tree (gitignored, residual from pre-GSD Cursor era).
- [ ] **ORPH-04**: Local `teresa.zip` sandbox artifact removed from working tree.

**Verification:** `grep -rn "run_full" . --include='*.toml' --include='*.example'` (excluding `CHANGELOG.md`, `LAUNCHER_README.md`, `.planning/`) → 0 matches. `LAUNCHER_README.md:4` retains its historical "replaces three legacy scripts" mention per D-18 / D-19 historical-content convention.

### Doc-vs-Impl Drift Sweep (DRIFT) — Plan 3: Doc-vs-impl sweep + trim class A

- [ ] **DRIFT-01**: All 13 files under `spec_classifier/docs/` plus root `CLAUDE.md`, `CONTRIBUTING.md`, `README.md` undergo a mechanical sweep of every "code does X" claim (grep / `Test-Path` / runtime check). Drifted claims are either fixed or removed; preference is **remove > patch**.
- [ ] **DRIFT-02**: `RUN_PATHS_AND_IO_LAYOUT.md` and `ONE_BUTTON_RUN.md` are trimmed of excessive CLI-flag prose; inline duplication replaced by pointer to `run.ps1 -?`.
- [ ] **DRIFT-03**: `docs/dev/DOC_INVARIANTS.md` is created with ≥5 mechanical drift invariants (e.g., `grep -q "PYTHONPYCACHEPREFIX" run.ps1` exit-code 0).
- [ ] **DRIFT-04**: Re-running the sweep against the corrected tree produces 0 drift claims.

**Justification for `DOC_INVARIANTS.md` creation in a "no-creation" cleanup milestone:** This is tooling/meta-doc materializing the v1.1 retrospective lesson — doc-vs-impl drift is not caught by read-pass audits (v1.0 DOC-03 missed `RUN_PATHS_AND_IO_LAYOUT.md:22` claiming `PYTHONPYCACHEPREFIX` was wired up). Domain content (per-vendor knowledge docs) remains excluded — that's v1.2.

## v2 Requirements (deferred — not in current roadmap)

Per `.planning/MILESTONE-CONTEXT.md` § Forward roadmap (consumed at v1.1 start):

### v1.2 — Per-vendor knowledge base

- **VKB-01**: `docs/vendors/<v>/PART_NUMBERS.md` per vendor
- **VKB-02**: `docs/vendors/<v>/SHEET_LAYOUT.md` per vendor
- **VKB-03**: `docs/vendors/<v>/CATALOG_CONVENTIONS.md` per vendor
- **VKB-04**: `docs/vendors/<v>/RULES_RATIONALE.md` per vendor

### v2.0 — 3-level classification spec (planning, no implementation)

- **TAX-01**: 3-level classification taxonomy specification on paper
- **TAX-02**: Level-boundary selection with rationale
- **TAX-03**: Migration plan (engine + 6 YAML + goldens regen + audit re-wire)
- **TAX-04** *(open question)*: Decide whether `entity_type` (BASE/HW/CONFIG/SOFTWARE/SERVICE/LOGISTIC/NOTE/UNKNOWN) survives as a standalone category or folds into one of the new levels

### v2.1 — 3-level classification implementation

- **IMPL-01**: Engine implementation
- **IMPL-02**: 6 vendor YAML rewrites
- **IMPL-03**: Goldens regen (single milestone where goldens diff is sanctioned with `--update-golden` + diff review)
- **IMPL-04**: Audit re-wire

### v2.2+ — Per-vendor rule fixes & new-vendor onboarding

- **CLAS-01**: Classification rule improvements (carry-forward from v1.0)
- **CLAS-02**: New vendor onboarding under fixed taxonomy (carry-forward from v1.0)

### Backlog (v2.0+)

- **PLAT-01**: Cross-platform launcher (`run.sh`)
- **PLAT-02**: De-Windows GUI dispatch (POSIX)
- **AUTO-01**: CI pipeline (depends on PLAT-01)
- **AUTO-02**: Pre-commit rule-id schema validation

## Out of Scope (v1.1)

Explicitly excluded. Each carries reasoning to prevent re-adding.

| Feature | Reason |
|---|---|
| `load_config_with_local()` regex-parser consolidation | Plan 1 extends an existing 4+-site regex pattern (`run.ps1`, `teresa_gui.py`) to `temp_root`. Helper consolidation deferred to its own milestone (`.planning/codebase/CONCERNS.md` § IMPORTANT). |
| Per-vendor knowledge docs (PART_NUMBERS et al.) | v1.2 scope (creation milestone, not cleanup). |
| Classifier rule changes / new vendors | v2.x scope (3-level taxonomy spec → migration). |
| Cross-platform launcher / POSIX GUI | Windows-first stance retained; backlog v2.0+. |
| CI pipeline / pre-commit hooks | Backlog v2.0+, depends on cross-platform support. |
| `CHANGELOG.md` historical entries | Treated as historical record per D-18 convention; not edited during cleanup. |
| `LAUNCHER_README.md:4` "replaces three legacy scripts" mention | Historical (parallel CHANGELOG); kept per D-18/D-19 historical-content convention. |
| `power_cord` `hw_type=None` "fix" | Intentional per recovery commit `c3c7cb6`; bait for "fix" PRs. Do not touch. |
| `src/core/parser.py` Dell-specificity despite location | Standalone refactor, separate milestone (CONCERNS.md § BLOCKER). |
| `batch_audit.py` reads `*_annotated.xlsx` | Explicit non-fix per `spec_classifier/CLAUDE.md`. |
| YAML rule order (load-bearing, first-match-wins) | Never sort or reorder rule blocks. |
| `HW_TYPE_VOCAB` duplication (`classifier.py` vs `batch_audit.py`) | Tracked in CONCERNS.md but not selected for v1.1. |
| Diffs inside `spec_classifier/{src,rules,golden,tests,batch_audit.py,cluster_audit.py,main.py,conftest.py}` | D-22 protected paths — any diff = phase gate FAIL. |

## Traceability

Phase mapping filled by the roadmapper agent during roadmap creation (2026-05-10).

| Requirement | Phase | Status |
|---|---|---|
| CACHE-01 | Phase 4 | Pending |
| CACHE-02 | Phase 4 | Pending |
| CACHE-03 | Phase 4 | Pending |
| CACHE-04 | Phase 4 | Pending |
| ORPH-01 | Phase 5 | Pending |
| ORPH-02 | Phase 5 | Pending |
| ORPH-03 | Phase 5 | Pending |
| ORPH-04 | Phase 5 | Pending |
| DRIFT-01 | Phase 6 | Pending |
| DRIFT-02 | Phase 6 | Pending |
| DRIFT-03 | Phase 6 | Pending |
| DRIFT-04 | Phase 6 | Pending |

**Coverage:**

- v1.1 requirements: 12 total
- Mapped to phases: 12 / Unmapped: 0 ✓
- Phase 4 (Cache Redirect): 4 reqs (CACHE-01..04)
- Phase 5 (Orphan Cleanup): 4 reqs (ORPH-01..04)
- Phase 6 (Doc-vs-Impl Drift Sweep): 4 reqs (DRIFT-01..04)

---
*Requirements defined: 2026-05-10*
*Last updated: 2026-05-10 — traceability filled after ROADMAP.md creation (Phases 4, 5, 6).*
