---
phase: 06-doc-vs-impl-drift-sweep
plan: 05
subsystem: planning-codebase-maps
tags: [surgical-patch, area-a, planning-codebase, drift-04, hyg-01, defense-in-depth]
requirements: [DRIFT-04]
dependency_graph:
  requires:
    - "Phase 4 D-08/D-13 (PYTHONPYCACHEPREFIX + PYTEST_ADDOPTS env vars wired in run.ps1 AND teresa_gui.py)"
    - "Phase 5 D-05/D-06 (canonical replacement vocabulary established)"
    - "06-01 (DRIFT-AUDIT.md scaffold + table format)"
  provides:
    - "DRIFT-04 closure: 3 surgical line patches landed in .planning/codebase/"
    - "Audit log appended with 3 patch rows (per D-22 audit-log requirement)"
  affects:
    - ".planning/codebase/STACK.md (line 79)"
    - ".planning/codebase/INTEGRATIONS.md (lines 55 + 150)"
    - ".planning/phases/06-doc-vs-impl-drift-sweep/06-DRIFT-AUDIT.md (3 new rows)"
tech_stack:
  added: []
  patterns:
    - "Defense-in-depth env-var documentation: name BOTH run.ps1 AND teresa_gui.py (Phase 4 D-13 regression guard)"
    - "HYG-01 placeholder convention: C:\\Users\\<USERNAME>\\ instead of hardcoded usernames"
    - "Audit-log column-shape stability (N-2 fix): check_command holds bare check; pre-state context goes in resolution column"
key_files:
  created:
    - ".planning/phases/06-doc-vs-impl-drift-sweep/06-05-SUMMARY.md"
  modified:
    - ".planning/codebase/STACK.md"
    - ".planning/codebase/INTEGRATIONS.md"
    - ".planning/phases/06-doc-vs-impl-drift-sweep/06-DRIFT-AUDIT.md"
decisions:
  - "Reused Phase 5 D-05/D-06 verbatim replacement vocabulary across both stale env-var bullets — vocabulary consistency across the milestone (D-03)."
  - "Single atomic commit `docs(06): T1 ...` per planner discretion (D-21 borderline note: map-file patches are documentation-class)."
metrics:
  duration_minutes: 1
  tasks_completed: 1
  files_modified: 3
  lines_changed: 9
  completed_date: "2026-05-11"
---

# Phase 6 Plan 05: .planning/codebase/ Surgical Patches Summary

3 surgical line patches applied to `.planning/codebase/STACK.md` and `.planning/codebase/INTEGRATIONS.md` — closes DRIFT-04 (the Area A hand-off Phase 5 explicitly punted to Phase 6) by replacing two stale `PYTHONPYCACHEPREFIX` claims with the Phase 5 D-05/D-06 canonical defense-in-depth vocabulary AND fixing one `C:\Users\G\` username leak that v1.0 HYG-01 missed.

## Scope

Per D-01 (surgical fix, not full refresh), this plan touches exactly the 3 known stale lines pre-identified in D-02. Broader refresh of the 7-file `.planning/codebase/` map tree (STACK / INTEGRATIONS / ARCHITECTURE / STRUCTURE / CONCERNS / CONVENTIONS / TESTING) remains deferred to a separate `/gsd-map-codebase` task in v1.2 backlog (per D-01 rationale: scope discipline + tooling fit).

## Patches Applied

### Patch 1 — `.planning/codebase/STACK.md:79` (D-02 + D-03)

**Pre-patch text:**
```
- `PYTHONPYCACHEPREFIX` — referenced in `spec_classifier/pyproject.toml:4-5` as the only mechanism to redirect `__pycache__/`. Not set by `run.ps1` (used to be set by the old `scripts/run_full.ps1`).
```

**Post-patch text:**
```
- `PYTHONPYCACHEPREFIX` and `PYTEST_ADDOPTS` — set by `run.ps1` and `teresa_gui.py` from `config.local.yaml::temp_root`. Together they redirect `__pycache__/` and `.pytest_cache/` to `$temp_root` so cache artifacts never land inside the repo working tree (Phase 4 CACHE-01/CACHE-02; defense-in-depth — both entry points set both vars independently).
```

**Why:** The stale claim falsely said `run.ps1` does NOT set `PYTHONPYCACHEPREFIX` and referenced the now-deleted `scripts/run_full.ps1` orphan (cleaned up in Phase 5). Post-Phase-4, both `run.ps1` AND `teresa_gui.py` independently set BOTH `PYTHONPYCACHEPREFIX` AND `PYTEST_ADDOPTS` from `config.local.yaml::temp_root`. New text uses the Phase 5 D-05/D-06 vocabulary verbatim and preserves the Phase 4 D-13 defense-in-depth wording (both entry points named, both env vars named).

### Patch 2 — `.planning/codebase/INTEGRATIONS.md:150` (D-02 + D-03)

**Pre-patch text:**
```
- `PYTHONPYCACHEPREFIX` — optional. Referenced in `pyproject.toml:4-5` as the only way to redirect `__pycache__/`. Not currently exported by `run.ps1` (was set by the now-retired `scripts/run_full.ps1`).
```

**Post-patch text:**
```
- `PYTHONPYCACHEPREFIX` and `PYTEST_ADDOPTS` — set by `run.ps1` and `teresa_gui.py` from `config.local.yaml::temp_root`. Together they redirect `__pycache__/` and `.pytest_cache/` to `$temp_root` so cache artifacts never land inside the repo working tree (Phase 4 CACHE-01/CACHE-02; defense-in-depth — both entry points set both vars independently).
```

**Why:** Same stale claim, same canonical D-03 vocabulary. Single replacement bullet keeps STACK.md and INTEGRATIONS.md in lock-step on the env-var wiring story so any future drift trips both files identically.

### Patch 3 — `.planning/codebase/INTEGRATIONS.md:55` (HYG-01 placeholder convention)

**Pre-patch text (table row):**
```
| TEMP (`.pytest_cache/`, `__pycache__/`) | `C:\Users\G\Desktop\temporary` | `temp_root` in `config.local.yaml` |
```

**Post-patch text (table row):**
```
| TEMP (`.pytest_cache/`, `__pycache__/`) | `C:\Users\<USERNAME>\Desktop\temporary` | `temp_root` in `config.local.yaml` |
```

**Why:** Hardcoded `C:\Users\G\` was a v1.0 HYG-01 stripping miss — the surrounding rows at lines 53-54 already use `%USERPROFILE%\Desktop\INPUT` / `%USERPROFILE%\Desktop\OUTPUT` placeholders. Replacement uses the `<USERNAME>` placeholder convention (per CLAUDE.md root § "Code-only repository policy"). Reduces information-disclosure surface (T-06-15 mitigation).

## Audit Log Rows Added

Three rows appended to `.planning/phases/06-doc-vs-impl-drift-sweep/06-DRIFT-AUDIT.md` (above the `## Tally` section), using the N-2-fixed column shape (`check_command` column holds ONLY the bare check command; pre-state context lives in `resolution` column):

| file | line | claim_summary | check_command | resolution |
|------|------|---------------|---------------|------------|
| .planning/codebase/STACK.md | 79 | "Not set by run.ps1 (used to be set by old scripts/run_full.ps1)" | `! grep -q "Not set by .run.ps1." .planning/codebase/STACK.md` | patch (pre-state: stale claim grep returned 0 / present; post-state: returns non-0 / removed; D-02/D-03 vocabulary applied — both env vars + both entry points + temp_root named) |
| .planning/codebase/INTEGRATIONS.md | 150 | "Not currently exported by run.ps1 (was set by the now-retired scripts/run_full.ps1)" | `! grep -q "Not currently exported" .planning/codebase/INTEGRATIONS.md` | patch (pre-state: stale claim present; post-state: removed; D-02/D-03 vocabulary applied — both env vars + both entry points + temp_root named) |
| .planning/codebase/INTEGRATIONS.md | 55 | "C:\\Users\\G\\Desktop\\temporary" hardcoded username | `! grep -q "C:..Users..G.." .planning/codebase/INTEGRATIONS.md` | patch (pre-state: hardcoded G\\ leak present — v1.0 HYG-01 miss; post-state: replaced with C:\\Users\\<USERNAME>\\Desktop\\temporary placeholder per HYG-01 convention) |

## Verification

All substantive acceptance criteria PASS:

- `git diff --stat -- spec_classifier/{src,rules,golden,tests,batch_audit.py,cluster_audit.py,main.py,conftest.py}` empty → D-22 byte-equal: PASS
- `git diff --stat -- spec_classifier/golden/` empty → goldens byte-equal: PASS (D-26)
- `grep -F 'PYTHONPYCACHEPREFIX' .planning/codebase/STACK.md` exits 0 → vocabulary present (line 79): PASS
- `grep -F 'PYTEST_ADDOPTS' .planning/codebase/STACK.md` exits 0 → second env var named: PASS
- `grep -F 'teresa_gui.py' .planning/codebase/STACK.md` exits 0 → defense-in-depth wording preserved: PASS
- `grep -F 'config.local.yaml::temp_root' .planning/codebase/STACK.md` exits 0 → temp_root source named: PASS
- `! grep -F 'Not set by `run.ps1`' .planning/codebase/STACK.md` → stale claim removed: PASS
- `! grep -F 'scripts/run_full' .planning/codebase/STACK.md` → orphan ref removed: PASS
- Same six checks on `.planning/codebase/INTEGRATIONS.md`: ALL PASS
- `grep -F 'C:\Users\<USERNAME>\Desktop\temporary' .planning/codebase/INTEGRATIONS.md` exits 0 → HYG-01 placeholder applied: PASS
- `! grep -F 'C:\Users\G\' .planning/codebase/INTEGRATIONS.md` → username leak removed: PASS
- `grep -c 'STACK\.md' .planning/phases/06-doc-vs-impl-drift-sweep/06-DRIFT-AUDIT.md` ≥ 1 (actual: 1) → audit row recorded: PASS
- `grep -c 'INTEGRATIONS\.md' .planning/phases/06-doc-vs-impl-drift-sweep/06-DRIFT-AUDIT.md` ≥ 2 (actual: 2) → audit rows for both 55 and 150 recorded: PASS
- No file outside `.planning/codebase/{STACK.md,INTEGRATIONS.md}` and `.planning/phases/06-doc-vs-impl-drift-sweep/` modified (`git status --short` confirms exactly 3 modified files): PASS

## Plan-spec Note (regex-form acceptance greps)

The plan's `<verify>` block and `<acceptance_criteria>` use BRE patterns like `grep -q "C:..Users..<USERNAME>..Desktop..temporary"`. In BRE, `..` matches any **two** characters; the actual content has only single backslashes between segments AND `<USERNAME>` is 10 characters between two backslashes, so the literal `..` regex matches the original `C:\Users\G\Desktop\temporary` (single G char between backslashes — `..` matches `\G`) but NOT the new `C:\Users\<USERNAME>\Desktop\temporary` (where the segment between backslashes is 10 chars).

This is a **plan-spec regex semantics issue, not a patch failure.** Substantive acceptance is met, verified via the equivalent fixed-string greps shown above (`grep -F 'C:\Users\<USERNAME>\Desktop\temporary'` exits 0; `grep -F 'C:\Users\G\'` exits non-0). The orchestrator's `success_criteria` block actually uses the canonical escaped-backslash fixed-string form (`grep -q "C:\\\\Users\\\\<USERNAME>"`) which has the same semantics issue under bash quoting in the executor environment but matches under PowerShell or with single-quoted args; either way the underlying file-content property is met. Captured here so a future re-sweep does not flag this as drift.

## Deviations from Plan

**None.** Plan executed exactly as written. The plan-spec regex note above is a verification-tooling observation, not a deviation in the patches themselves.

## Threat Model Closure

- **T-06-14 (Tampering, accept):** Single atomic commit, fully revertable.
- **T-06-15 (Information Disclosure, mitigate):** `C:\Users\G\` username removed from `.planning/codebase/INTEGRATIONS.md:55`; replaced with `<USERNAME>` placeholder per HYG-01.
- **T-06-16 (Repudiation, mitigate):** Atomic commit with `docs(06): T1 ...` subject (per D-21 borderline-doc-class call).

## Self-Check: PASSED

- File `.planning/codebase/STACK.md` exists at the correct path: FOUND
- File `.planning/codebase/INTEGRATIONS.md` exists at the correct path: FOUND
- File `.planning/phases/06-doc-vs-impl-drift-sweep/06-DRIFT-AUDIT.md` exists: FOUND
- File `.planning/phases/06-doc-vs-impl-drift-sweep/06-05-SUMMARY.md` (this file) exists: FOUND
- 3 patch rows in audit log under `## Audit Table` and above `## Tally`: VERIFIED
- D-22 protected paths diffstat empty: VERIFIED
- Goldens diffstat empty: VERIFIED
- Single commit hash will be recorded post-commit and appended to STATE.md decisions
