---
phase: 05-orphan-cleanup
plan: 01
subsystem: cleanup
tags: [cleanup, config, powershell, orphan-removal, gitignore]

# Dependency graph
requires:
  - phase: 04-cache-redirect
    provides: "run.ps1 + teresa_gui.py both set PYTHONPYCACHEPREFIX + PYTEST_ADDOPTS from config.local.yaml::temp_root (the wording the Phase 5 replacement text mirrors verbatim)"
provides:
  - "ROADMAP.md §SC-1 grep gate scoped to *.toml + *.example files (matches REQUIREMENTS.md verbatim)"
  - "spec_classifier/pyproject.toml:4-6 names BOTH env vars and BOTH entry points (post-Phase-4 wording)"
  - "spec_classifier/config.local.yaml.example:11 names all three temp_root consumers"
  - "Working tree free of .cursor/ and teresa.zip (both still gitignored)"
affects: [06-doc-vs-impl-drift-sweep]

# Tech tracking
tech-stack:
  added: []
  patterns: ["Test-Path-guarded Remove-Item for fail-fast filesystem cleanup (no try/catch wrapper, no git clean -fdx)"]

key-files:
  created: []
  modified:
    - .planning/ROADMAP.md
    - spec_classifier/pyproject.toml
    - spec_classifier/config.local.yaml.example
  removed:
    - .cursor/ (gitignored — filesystem-only deletion)
    - teresa.zip (gitignored — filesystem-only deletion, --allow-empty audit-trail commit)

key-decisions:
  - "T2 + T3 replacement wording locked to Phase-4-aware vocabulary (PYTHONPYCACHEPREFIX + PYTEST_ADDOPTS, run.ps1 AND teresa_gui.py) per phase4_handoff — not regressed to looser REQUIREMENTS.md phrasing"
  - "T4/T5 used --allow-empty commits because both targets were gitignored; commits serve as the audit-trail anchors per D-18"
  - "Check 5 dispositioned as substantive PASS / literal FAIL: plan-author authoring slip (case-sensitive grep vs file's literal capital R); D-19 invariant satisfied — file byte-equal to phase-start (HEAD~5 diff empty)"

patterns-established:
  - "Phase-window D-22 protected-paths guard: per-task `git diff --stat HEAD~1 -- <D-22 paths>` plus phase-final `git diff --stat HEAD~5 -- <D-22 paths>` — two-layer mechanical guard against tampering with src/rules/golden/tests/audit modules"
  - "Atomic 1-line config edits with literal pre/post text in <action> + exact-string greps in <verify> = mechanically detectable wording regression"

requirements-completed: [ORPH-01, ORPH-02, ORPH-03, ORPH-04]

# Metrics
duration: ~4 min
completed: 2026-05-10
---

# Phase 5 Plan 05-01: Orphan Cleanup Summary

**Stale `scripts/run_full.ps1` references purged from pyproject.toml + config.local.yaml.example with Phase-4-aware replacement wording; ROADMAP §SC-1 grep gate tightened to `*.toml`/`*.example` scope; .cursor/ and teresa.zip removed from working tree; ROADMAP wording, gitignores, D-22 protected paths, and goldens all byte-equal to phase-start.**

## Performance

- **Duration:** ~4 min
- **Started:** 2026-05-10T17:26:48Z
- **Completed:** 2026-05-10T17:30:25Z
- **Tasks:** 5
- **Files modified:** 3 (`.planning/ROADMAP.md`, `spec_classifier/pyproject.toml`, `spec_classifier/config.local.yaml.example`)
- **Files removed:** 2 (`.cursor/`, `teresa.zip`) — see Removed-Artifact Pre-State Notes below

## Accomplishments

- ROADMAP.md §SC-1 grep gate now scopes to `*.toml`/`*.example` files (matches REQUIREMENTS.md verbatim) — eliminates `run.ps1:3` (RU comment) and `teresa_gui.py::_run_full` method-name false positives.
- `spec_classifier/pyproject.toml:4-6` rewritten with the 3-line block naming BOTH env vars (`PYTHONPYCACHEPREFIX + PYTEST_ADDOPTS`) AND BOTH entry points (`run.ps1 and teresa_gui.py`).
- `spec_classifier/config.local.yaml.example:11` rewritten to name all three consumers (`scripts/clean.ps1, run.ps1, and teresa_gui.py`).
- `.cursor/` directory removed from the working tree; `.gitignore:48` rule preserved so re-introduction is still ignored.
- `teresa.zip` audit-trail commit recorded; `.gitignore:45` (`*.zip`) and `.gitignore:56` (`teresa.zip`) both preserved.
- Pytest passes 774 / 1 xfailed in 17.85s with 0 skips → D-20 skip-ratio guard PASS (0.00 ≪ 0.50).

## Task Commits

Each task was committed atomically (oldest → most recent):

1. **T1: Tighten ROADMAP §SC-1 grep scope** — `ae11f48` (chore)
2. **T2: ORPH-01 rewrite pyproject.toml lines 4-6** — `8bfc73f` (chore)
3. **T3: ORPH-02 rewrite config.local.yaml.example:11** — `3b08b36` (chore)
4. **T4: ORPH-03 remove .cursor/ directory** — `bd2984b` (chore, --allow-empty since gitignored)
5. **T5: ORPH-04 remove teresa.zip artifact** — `4a29f6f` (chore, --allow-empty since gitignored)

**Plan metadata:** `<sha-pending>` (this SUMMARY.md + STATE/ROADMAP/REQUIREMENTS bundled metadata commit — `docs(05): plan 05-01 summary`)

## Files Created/Modified

- `.planning/ROADMAP.md` — §SC-1 grep wording: added `--include='*.toml' --include='*.example'` flags + retargeted the trailing prose. Single line change.
- `spec_classifier/pyproject.toml` — lines 4-6 (the 3-comment block) replaced with the D-05 vocabulary; lines 1-3 + 7 byte-equal to pre-edit; file shape preserved (7 lines).
- `spec_classifier/config.local.yaml.example` — line 11 rewritten with the D-06 three-consumer comment; lines 1-10 + 12 byte-equal to pre-edit; file shape preserved (12 lines).
- `.cursor/` — directory removed from working tree (gitignored at line 48, never tracked).
- `teresa.zip` — removed from working tree (gitignored at lines 45 + 56, never tracked); commit `4a29f6f` (--allow-empty) recorded as ORPH-04 audit marker per D-18.

## Decisions Made

- **Replacement-text vocabulary lock honored:** T2 used the Phase-4-aware wording (BOTH env vars + BOTH entry points) instead of regressing to REQUIREMENTS.md's looser phrasing. T3 likewise named all three temp_root consumers, not just two.
- **T4/T5 commits recorded as `--allow-empty`:** both targets were gitignored, so the deletions produced no staged changes; commits serve as the D-18 audit-trail anchors that ORPH-03 / ORPH-04 were executed in this phase window.
- **Check 5 dispositioned as substantive PASS:** see verification log entry for Check 5 below — the plan's verification grep used a case-sensitive form that did not match the file's literal capital `R`. The substantive D-19 invariant (historical content preserved, file untouched) is upheld by the empty `git diff --stat HEAD~5 -- LAUNCHER_README.md`.

## Deviations from Plan

None. All five tasks executed exactly as written — literal `<action>` text applied with no paraphrase, no auto-fix, no ask. The plan was fully specified and self-contained.

## Verification Log (Plan-Level Final Verification — 11 checks)

### Check 1 — ROADMAP.md §SC-1 contains the new include-flag-scoped grep wording
- **Command:** `grep -c -- "--include='\*\.toml' --include='\*\.example'" .planning/ROADMAP.md`
- **Output:** `1`
- **Result:** PASS

### Check 2 — spec_classifier/pyproject.toml lines 4-6 are the exact D-05 block
- **Command (a):** `grep -c "PYTHONPYCACHEPREFIX + PYTEST_ADDOPTS" spec_classifier/pyproject.toml`
- **Output (a):** `1` → PASS
- **Command (b):** `grep -c "run.ps1 and teresa_gui.py set both" spec_classifier/pyproject.toml`
- **Output (b):** `1` → PASS
- **Command (c):** `grep -c "pyproject.toml cannot redirect" spec_classifier/pyproject.toml`
- **Output (c):** `1` → PASS
- **Result:** PASS (3 of 3 sub-checks)

### Check 3 — spec_classifier/config.local.yaml.example:11 is the exact D-06 line
- **Command:** `grep -c "Used by scripts/clean.ps1, run.ps1, and teresa_gui.py." spec_classifier/config.local.yaml.example`
- **Output:** `1`
- **Result:** PASS

### Check 4 — Working-tree absence of `.cursor/` AND `teresa.zip`
- **Command:** `powershell -NoProfile -Command "Test-Path .\.cursor; Test-Path .\teresa.zip"`
- **Output:** `False` / `False`
- **Result:** PASS

### Check 5 — LAUNCHER_README.md historical content preserved (negative check)

**Check 5: PASS (substantive); FAIL (literal grep, plan-author casing slip).** Plan command `grep -c "replaces three legacy scripts" LAUNCHER_README.md` returned `0` because the file's actual content is `"Replaces three legacy scripts"` (capital R) at line 3. Case-insensitive form `grep -ic "replaces three legacy scripts" LAUNCHER_README.md` returns `1`. The plan's `<interfaces>` block (lines 132-138) records the file with capital `R`, confirming the verification grep was an authoring slip rather than a substantive expectation. The D-19 invariant tested by Check 5 — "historical mention preserved, file untouched" — is upheld: `git diff --stat HEAD~5 -- LAUNCHER_README.md` is empty (byte-equal to phase-start). Substantive PASS accepted by orchestrator. Recommend follow-up tracking item: future Phase 5–style plans should use case-insensitive grep (or quote the exact-case phrase) when checking historical content.

Supporting commands and outputs:
- **Command (a — case-sensitive, as authored in plan):** `grep -c "replaces three legacy scripts" LAUNCHER_README.md`
- **Output (a):** `0` (literal grep FAIL — plan-author casing slip per disposition above)
- **Command (b — case-insensitive, substantive invariant):** `grep -ic "replaces three legacy scripts" LAUNCHER_README.md`
- **Output (b):** `1` (line 3: `One launcher to rule them all. Replaces three legacy scripts (\`run_audit.ps1\`,`)
- **Command (c — historical scripts/run_full.ps1 reference still in LAUNCHER_README.md):** `grep -c "scripts/run_full.ps1" LAUNCHER_README.md`
- **Output (c):** `1` (untouched historical reference exempted by D-02 / D-19) → PASS
- **Command (d — D-19 byte-equal invariant):** `git diff --stat HEAD~5 -- LAUNCHER_README.md`
- **Output (d):** (empty — file untouched across phase window) → PASS

### Check 6 — D-22 guard: zero bytes changed inside protected paths over the phase window
- **Command:** `git diff --stat HEAD~5 -- spec_classifier/src spec_classifier/rules spec_classifier/golden spec_classifier/tests spec_classifier/batch_audit.py spec_classifier/cluster_audit.py spec_classifier/main.py spec_classifier/conftest.py`
- **Output:** (empty — zero files listed, zero bytes changed)
- **Result:** PASS — D-22 invariant holds across all 5 phase-window commits.

### Check 7 — Pytest skip-ratio gate (D-20)
- **Command:** `cd spec_classifier && pytest -q`
- **Output (last line):** `774 passed, 1 xfailed, 25 warnings in 17.85s`
- **Counts:** passed=774, skipped=0, failed=0, xfailed=1
- **Skip ratio:** 0/775 = 0.00 (well under 0.50 threshold)
- **Result:** PASS — D-20 skip-ratio guard not tripped.

### Check 8 — Goldens byte-equal gate (D-21)
- **Command:** `git diff --stat HEAD~5 -- spec_classifier/golden/`
- **Output:** (empty)
- **Result:** PASS — all 40 `*_expected.jsonl` fixtures byte-equal across the phase window.

### Check 9 — Post-T1 gate grep (cumulative — all `*.toml` + `*.example` files clean)
- **Command:** `grep -rn "run_full" . --include='*.toml' --include='*.example' --exclude-dir=.planning`
- **Output:** (empty — zero matches)
- **Result:** PASS — Phase 5 success criterion #1 (post-T1 ROADMAP §SC-1 wording) satisfied.

### Check 10 — .gitignore lines 48 + 56 untouched (D-13)
- **Command (a):** `sed -n '48p' .gitignore` → `.cursor/` → PASS
- **Command (b):** `sed -n '56p' .gitignore` → `teresa.zip` → PASS
- **Command (c):** `git diff --stat HEAD~5 -- .gitignore` → (empty) → PASS
- **Result:** PASS — `.gitignore` not in the phase-window diff; both rules preserved verbatim.

### Check 11 — Five atomic commits exist with the expected subject pattern
- **Command:** `git log -5 --pretty=%s`
- **Output:**
  ```
  chore(05): T5 remove teresa.zip from working tree
  chore(05): T4 remove .cursor directory from working tree
  chore(05): T3 rewrite config.local.yaml.example temp_root note
  chore(05): T2 rewrite pyproject.toml run_full reference
  chore(05): T1 align ROADMAP §SC-1 grep scope with REQUIREMENTS
  ```
- **Result:** PASS — 5 of 5 lines match `^chore\(05\): T[1-5] `; all subjects ≤72 chars.

## D-22 Guard Log (full diff over phase window)

```
$ git diff --stat HEAD~5 -- spec_classifier/src spec_classifier/rules spec_classifier/golden spec_classifier/tests spec_classifier/batch_audit.py spec_classifier/cluster_audit.py spec_classifier/main.py spec_classifier/conftest.py
(empty — zero files listed, zero bytes changed)
```

PASS — D-22 invariant holds end-to-end.

## Goldens Diff Log (full diff over phase window)

```
$ git diff --stat HEAD~5 -- spec_classifier/golden/
(empty)
```

PASS — all 40 `*_expected.jsonl` fixtures byte-equal.

## Pytest Run Summary (D-20 record)

```
774 passed, 1 xfailed, 25 warnings in 17.85s
```

- passed: 774
- skipped: 0
- failed: 0
- xfailed: 1
- xpassed: 0
- skip ratio: 0.00 (D-20 threshold: > 0.50 fails — well under)

## Removed-Artifact Pre-State Notes

- `.cursor/` — size not recorded — gitignored, not in any commit, removed before measurement.
- `teresa.zip` — size not recorded — gitignored, not in any commit, removed before measurement.

## Issues Encountered

- **Verification Check 5 — case-sensitive grep authoring slip in plan.** Dispositioned as substantive PASS by orchestrator (see Check 5 entry above). No file modification attempted because correcting `LAUNCHER_README.md` would violate D-19; no plan modification attempted because the plan is closed. Recommended follow-up tracking item: future Phase 5–style plans should use case-insensitive grep (or quote the exact-case phrase) when checking historical content.

## Self-Check

- `.planning/phases/05-orphan-cleanup/05-01-SUMMARY.md` — FOUND
- `.planning/phases/05-orphan-cleanup/05-01-PLAN.md` — FOUND
- `.planning/ROADMAP.md` — FOUND
- `spec_classifier/pyproject.toml` — FOUND
- `spec_classifier/config.local.yaml.example` — FOUND
- Commit `ae11f48` (T1) — FOUND
- Commit `8bfc73f` (T2) — FOUND
- Commit `3b08b36` (T3) — FOUND
- Commit `bd2984b` (T4) — FOUND
- Commit `4a29f6f` (T5) — FOUND

## Self-Check: PASSED

## Next Phase Readiness

- **Phase 6 (Doc-vs-Impl Drift Sweep) prerequisites met:**
  - Phase 5's edits to `pyproject.toml`, `config.local.yaml.example`, and ROADMAP.md are in place; the post-Phase-4-and-5 tree the Phase 6 sweep operates against is now realized.
  - D-22 protected paths byte-equal to phase start; goldens byte-equal; pytest passes; .gitignore unchanged.
  - No deferred items, no blockers, no broken state.

---
*Phase: 05-orphan-cleanup*
*Completed: 2026-05-10*
