# Phase 5: Orphan Cleanup - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-10
**Phase:** 5-orphan-cleanup
**Areas discussed:** run_full grep gate scope, Replacement wording (ORPH-01/02), Removal mechanism for .cursor/ + teresa.zip, Plan structure for Phase 5

---

## run_full grep gate scope

### Q1 — Reconciling ROADMAP §SC-1 vs REQUIREMENTS verification mismatch

| Option | Description | Selected |
|--------|-------------|----------|
| Tighten ROADMAP to match REQUIREMENTS | Update ROADMAP §SC-1 to scope grep to `--include='*.toml' --include='*.example'`, matching REQUIREMENTS.md verification verbatim. Honors D-18 historical-content convention for code-file comments and method names. No code/comment changes; the gate just stops false-positive-tripping. Make this an explicit Phase 5 deliverable. | ✓ |
| Honor ROADMAP verbatim — clean false positives | Translate run.ps1:3 Russian comment to English (or remove), and rename teresa_gui.py:_run_full method to _run_all_vendors. Both files are launcher-tier (not D-22 protected). Costs a real refactor of teresa_gui.py that arguably exceeds 'cleanup-only' intent. | |
| Add run.ps1 + teresa_gui.py to exclusion list | Extend the gate's exclusion list (currently CHANGELOG.md, LAUNCHER_README.md, .planning/) to also cover run.ps1 and teresa_gui.py. Preserves both files untouched but bloats the exemption list and weakens the gate. | |

**User's choice:** Tighten ROADMAP to match REQUIREMENTS (Recommended)
**Notes:** Becomes a 5th Phase 5 deliverable (T1 in the single plan), captured as a documented adjustment in CONTEXT.md rather than a new requirement (no ORPH-05 added).

### Q2 — Disposition of run.ps1:3 Russian historical comment

| Option | Description | Selected |
|--------|-------------|----------|
| Leave as-is, exempted by tightened gate | Same status as LAUNCHER_README.md:4: historical mention preserved, exempted under the new *.toml/*.example-only gate. No code edit. Avoids scope-creep into launcher code. | ✓ |
| Translate to English in Phase 5 | Change the comment to English (same content) since Phase 1 scrubbed user-visible Russian incompletely. Adds an additional 'comment translation' deliverable to Phase 5 that wasn't in the milestone plan. | |
| Defer to a later phase | Capture as a deferred idea for Phase 6 (drift sweep) or a future hygiene pass. Phase 5 stays purely on ORPH-01..04. | |

**User's choice:** Leave as-is, exempted by tightened gate (Recommended)
**Notes:** Translation captured as a Deferred Idea in CONTEXT.md for a future hygiene milestone if one materializes.

### Q3 — Tracking the ROADMAP §SC-1 realignment in Phase 5

| Option | Description | Selected |
|--------|-------------|----------|
| 5th deliverable in Phase 5 | Add an explicit task under Phase 5: edit ROADMAP.md to scope SC-1's grep to `--include='*.toml' --include='*.example'`, matching REQUIREMENTS.md verbatim. Document as part of the phase verification gate cleanup. Tracked in CONTEXT.md as a documented adjustment, not a new requirement (no ORPH-05). | ✓ |
| Fold into ORPH-01 acceptance check | Treat the ROADMAP edit as part of ORPH-01 implementation — the rewriter touches both pyproject.toml:5 and ROADMAP.md §SC-1 in the same plan. Single commit covering both. | |
| Capture only in CONTEXT.md as a discussion outcome | Don't edit ROADMAP.md — instead document the reconciliation in CONTEXT.md, and have the planner reference REQUIREMENTS.md verification as the canonical gate. Slight documentation drift between ROADMAP and REQUIREMENTS persists. | |

**User's choice:** 5th deliverable in Phase 5 (Recommended)
**Notes:** Lands as T1 in the plan (executes before T2..T5 so subsequent verification uses the corrected gate spec).

### Q4 — Stale .planning/codebase/ references (STACK.md:79, INTEGRATIONS.md:150)

| Option | Description | Selected |
|--------|-------------|----------|
| Defer to Phase 6 drift sweep | Capture as a deferred idea — Phase 6's mechanical sweep covers 13 spec_classifier/docs/ + 3 root markdown files. Codebase intel files (STACK, INTEGRATIONS) are also doc-vs-impl drift. Either fold them into Phase 6's scope, or refresh via /gsd-map-codebase post-v1.1. | ✓ |
| Patch in Phase 5 — same theme | While Phase 5 is touching ORPH-01/02 wording, also fix STACK.md:79 and INTEGRATIONS.md:150 to reflect post-Phase-4 reality. Keeps the cleanup logically complete. But .planning/codebase/ wasn't enumerated in Phase 5's REQUIREMENTS or ROADMAP. | |
| Leave alone — not in scope | Don't touch them in any phase; codebase intel will be refreshed by a future /gsd-map-codebase run. Phase 5 stays narrow to its 4 ORPH requirements + ROADMAP §SC-1 alignment. | |

**User's choice:** Defer to Phase 6 drift sweep (Recommended)
**Notes:** Captured in CONTEXT.md § Deferred Ideas. Phase 6 planner should reopen this.

---

## Replacement wording (ORPH-01/02)

### Q1 — pyproject.toml:5 replacement wording

| Option | Description | Selected |
|--------|-------------|----------|
| REQUIREMENTS.md verbatim | Replace line 5 with: '# Set it in your shell profile or use run.ps1 (sets PYTHONPYCACHEPREFIX automatically).' Matches REQUIREMENTS.md ORPH-01 verbatim. Mentions run.ps1 (per Phase 4) and the auto-set behavior. Single-line edit, no other lines touched. | |
| Tighter — also mention teresa_gui.py + PYTEST_ADDOPTS | Replace lines 4-6 with a more complete summary that names both entry points and both env vars: '# __pycache__ + .pytest_cache redirection requires PYTHONPYCACHEPREFIX + PYTEST_ADDOPTS env vars. # run.ps1 and teresa_gui.py set both from config.local.yaml::temp_root automatically. # pyproject.toml cannot redirect __pycache__ (only env var can).' More accurate to Phase 4's full wiring (D-08, D-13). | ✓ |
| Minimal — just kill the run_full reference | Replace 'scripts/run_full.ps1' with 'run.ps1' in line 5; keep the rest of the line unchanged. Lowest-touch fix, but keeps the now-misleading 'shell profile' framing as the primary recommendation. | |

**User's choice:** Tighter — also mention teresa_gui.py + PYTEST_ADDOPTS
**Notes:** Final 3-line block captured verbatim in CONTEXT.md D-05.

### Q2 — config.local.yaml.example:11 replacement wording

| Option | Description | Selected |
|--------|-------------|----------|
| REQUIREMENTS.md verbatim | Replace line 11 with: '# Used by scripts/clean.ps1 and run.ps1.' Matches REQUIREMENTS.md ORPH-02 verbatim. Names both consumers. Symmetric with ORPH-01's run.ps1 mention. | |
| Also mention teresa_gui.py | Replace line 11 with: '# Used by scripts/clean.ps1, run.ps1, and teresa_gui.py.' Names all three consumers. Slightly more accurate to Phase 4's wiring (teresa_gui.py also reads temp_root). | ✓ |
| Minimal — just swap run_full for run | Replace 'scripts/run_full.ps1' with 'run.ps1' on line 11; keep 'scripts/clean.ps1' formatting. Lowest-touch fix, asymmetric path notation (one with scripts/ prefix, one without). | |

**User's choice:** Also mention teresa_gui.py
**Notes:** Captured verbatim in CONTEXT.md D-06. Departs slightly from REQUIREMENTS.md ORPH-02 suggested wording — gain is post-Phase-4 accuracy.

---

## Removal mechanism for .cursor/ + teresa.zip

### Q1 — How to perform the removal

| Option | Description | Selected |
|--------|-------------|----------|
| One-shot Remove-Item during phase execution | Plan executes 'Remove-Item .\.cursor -Recurse -Force' and 'Remove-Item .\teresa.zip -Force' once. Both are gitignored — no 'git rm' needed. Clean, atomic, single commit. Doesn't touch clean.ps1 or .gitignore. | ✓ |
| Augment clean.ps1 to sweep them on every run | Add .cursor/ and teresa.zip to clean.ps1's sweep list, then run clean.ps1 once. Would prevent reaccumulation but conflates one-off artifact removal with recurring runtime-cache cleanup. Also: .cursor/ legitimately reappears if the user opens the repo in Cursor again. | |
| Remove + add a CI guard | Remove once, then add a phase-gate or pre-commit check that fails if .cursor/ or teresa.zip reappear. Heavy-handed for a single residual cleanup; would block legitimate Cursor use. | |

**User's choice:** One-shot Remove-Item during phase execution (Recommended)
**Notes:** Captured in CONTEXT.md D-08. clean.ps1 explicitly NOT augmented (D-09).

### Q2 — Failure handling when Remove-Item hits a lock

| Option | Description | Selected |
|--------|-------------|----------|
| Fail the phase — require clean removal | Wrap in try/catch, surface error, halt. Forces user to free the lock and re-run; phase gate (Test-Path returns $false) wouldn't pass on partial removal anyway. No silent best-effort. | ✓ |
| Best-effort — log and continue | Mirror Phase 4 D-06's clean.ps1 try/catch pattern: log warning in yellow, continue. Survives transient locks. But the phase verification (Test-Path = $false) would then surface the failure downstream as a gate failure rather than at the action. | |
| Retry with backoff before failing | Retry 3 times with 500ms backoff to handle transient Windows file locks (common with .cursor/skills loaded in IDE), then fail. Complexity for a once-per-milestone operation. | |

**User's choice:** Fail the phase — require clean removal (Recommended)
**Notes:** Captured in CONTEXT.md D-12. Uses default `$ErrorActionPreference = "Stop"` discipline; no try/catch wrapper.

### Q3 — Where in the plan should removals run

| Option | Description | Selected |
|--------|-------------|----------|
| Inline PowerShell step in the plan | Two-line action block: 'if (Test-Path .\.cursor) { Remove-Item .\.cursor -Recurse -Force }; if (Test-Path .\teresa.zip) { Remove-Item .\teresa.zip -Force }'. Idempotent, no new files created, no clean.ps1 changes. Survives a re-run if .cursor/ has already been removed. | ✓ |
| Add to scripts/ as orphan_sweep.ps1 | Create a one-off 'scripts/orphan_sweep.ps1' or similar; run it during phase execution. Costs a new file in the repo whose only purpose is a single milestone's cleanup. Delete-after-use is awkward. | |
| Use 'git clean -fdx -- .cursor teresa.zip' | Let git remove ignored files explicitly. Cleaner semantics for 'gitignored junk', but couples removal to git — won't run if user has worktree dirty in unrelated ways or git not available. | |

**User's choice:** Inline PowerShell step in the plan (Recommended)
**Notes:** Captured in CONTEXT.md D-08, D-10, D-11. Test-Path guards make it idempotent for replay.

---

## Plan structure for Phase 5

### Q1 — Plan-file count

| Option | Description | Selected |
|--------|-------------|----------|
| Single plan with 5 tasks | One 05-01-PLAN.md covers all five deliverables as discrete tasks: T1 ORPH-01, T2 ORPH-02, T3 ORPH-03, T4 ORPH-04, T5 ROADMAP §SC-1. Each task = one commit. Cleanest for a small mechanical phase. Executor can run all 5 sequentially in one wave. | ✓ |
| Two plans — text rewrites vs working-tree rm | 05-01-PLAN.md = ORPH-01 + ORPH-02 + ROADMAP §SC-1 (text edits to 3 config/doc files); 05-02-PLAN.md = ORPH-03 + ORPH-04 (working-tree removals). Different verbs (edit vs delete) in different plans. Both can run in parallel (disjoint files). | |
| Mirror Phase 4 — one plan per file | 5 plans (05-01..05-05): one each for pyproject.toml, config.local.yaml.example, .cursor/, teresa.zip, ROADMAP.md. Maximally granular commits but plan-overhead-per-task ratio is high for trivial edits. | |

**User's choice:** Single plan with 5 tasks (Recommended)
**Notes:** Captured in CONTEXT.md D-14. ROADMAP §SC-1 realignment occupies T1, ORPH-01..04 occupy T2..T5 (note: T1 is ROADMAP-edit, NOT ORPH-01 — see Q2 below for ordering).

### Q2 — Task ordering

| Option | Description | Selected |
|--------|-------------|----------|
| T1 ROADMAP → T2 pyproject.toml → T3 config.local.yaml.example → T4 .cursor/ → T5 teresa.zip | Align gate scope first (T1) so the verification grep behaves as intended throughout; then text edits (T2, T3); then working-tree removals (T4, T5). Verification can run after each task without false positives. | ✓ |
| ORPH-01..04 first, ROADMAP last | Match REQUIREMENTS ordering. Risk: if T1 verification (grep -rn run_full . | wc -l == 0) runs before ROADMAP is realigned, the gate uses ROADMAP's 'across entire repo' rule and false-positives on run.ps1:3 / teresa_gui.py. | |
| Parallelize all 5 — no inherent ordering | All 5 tasks have disjoint files, so wave-1 parallel. Faster but verification only runs at end-of-plan, not between tasks. | |

**User's choice:** T1 ROADMAP → T2 pyproject.toml → T3 config.local.yaml.example → T4 .cursor/ → T5 teresa.zip (Recommended)
**Notes:** Captured in CONTEXT.md D-15, D-17. Sequential within plan; no parallel waves.

---

## Claude's Discretion

- Exact wording of the ROADMAP.md §SC-1 edit (substantive change is the
  `--include='*.toml' --include='*.example'` flag addition; surrounding prose
  may be paraphrased to match ROADMAP's existing voice).
- Exact phrasing of commit subject lines (`chore(05): T<N> <verb> <object>`
  pattern; specific verbs/objects per task).
- Whether each `Remove-Item` emits a confirmation `Write-Host` line (cosmetic).

## Deferred Ideas

- **`.planning/codebase/STACK.md:79` + `INTEGRATIONS.md:150` stale post-Phase-4
  references** — fold into Phase 6 drift sweep scope OR refresh via post-v1.1
  `/gsd-map-codebase`. Reopen at Phase 6 planning.
- **Translation of `run.ps1:3` Russian historical comment to English** — exempt
  under the tightened gate; future hygiene-milestone candidate.
- **Renaming `_run_full` method in `teresa_gui.py`** — substring grep false
  positive; only relevant if a future contributor proposes the rename.
- **`clean.ps1` extension to sweep `.cursor/` / `teresa.zip`** — explicitly
  rejected; one-off artifacts vs recurring runtime caches.
- **`scripts/orphan_sweep.ps1` reusable cleanup script** — explicitly rejected;
  retire-after-use awkward.
- **`git clean -fdx -- .cursor teresa.zip` removal mechanism** — explicitly
  rejected; couples removal to git state in an unhelpful way.
- **Removing `.gitignore` lines 48/56 after artifacts deleted** — explicitly
  rejected; passive guard against reaccumulation worth keeping.
- **Adding ORPH-05 for ROADMAP §SC-1 edit** — explicitly rejected; documented
  adjustment, not a new requirement.
