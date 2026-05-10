---
phase: 04-cache-redirect
plan: 03
subsystem: docs / quick-start operator reference
tags: [docs, markdown, cache-redirect, operator-facing]
requires:
  - "Plan 04-01 (run.ps1 cache redirect + clean.ps1 auto-invocation + -NoClean switch)"
  - "Plan 04-02 (teresa_gui.py cache redirect)"
provides:
  - "spec_classifier/docs/dev/ONE_BUTTON_RUN.md documents clean.ps1 default-on + -NoClean opt-out (CACHE-04 acceptance gate)"
  - "Quick-start numbered list reflects the 8-step run.ps1 contract"
  - "Useful switches block lists -NoClean alongside the other operator flags"
affects:
  - spec_classifier/docs/dev/ONE_BUTTON_RUN.md
tech_stack:
  added: []
  patterns:
    - "Doc edit follows the existing imperative, terse, code-fenced PowerShell tone (no prose explaining why; that lives in RUN_PATHS_AND_IO_LAYOUT.md per D-12)"
key_files:
  created: []
  modified:
    - spec_classifier/docs/dev/ONE_BUTTON_RUN.md
decisions:
  - "Inline `#`-comment column alignment for the new -NoClean switches line: padded to match the existing block (4 spaces between `-NoClean` and `#`-prefixed comment column at byte ~39, identical alignment to surrounding lines). Verified visually — all comment-`#` glyphs sit in the same column."
  - "No deviations from CONTEXT.md decisions (D-11.1, D-11.2, D-11.3, D-12). All 3 edits land at the prescribed locations; no other doc under spec_classifier/docs/ touched."
metrics:
  duration_minutes: 5
  completed_date: 2026-05-10
  task_count: 1
  files_changed: 1
---

# Phase 4 Plan 3: Cache Redirect — ONE_BUTTON_RUN.md doc edits Summary

`spec_classifier/docs/dev/ONE_BUTTON_RUN.md` now reflects Phase 4's clean-by-default + cache-redirect contract via three coordinated edits per CONTEXT.md D-11. Operators reading the quick-start now learn that `run.ps1` cleans first, that `-NoClean` is the opt-out, and that manual `clean.ps1` invocation is the exception (not the default). CACHE-04 acceptance gate (`-NoClean` and `clean.ps1` co-occur in the "Workspace cleanup" section) is satisfied.

## What Changed

Three coordinated edits to `spec_classifier/docs/dev/ONE_BUTTON_RUN.md`:

| Edit | Section                                | Change                                                                                                              | Lines (post-edit) |
| ---- | -------------------------------------- | ------------------------------------------------------------------------------------------------------------------- | ----------------- |
| 1    | "What run.ps1 does" numbered list      | Inserted new step 1 ("Cleans prior `__pycache__` / `.pytest_cache` from `temp_root` and the working tree (skip with `-NoClean`)"); renumbered existing steps 1–7 → 2–8 | 10–19             |
| 2    | "Useful run.ps1 switches" code block   | Inserted `-NoClean` entry between `-SkipTests` and `-Vendor huawei -NoAi -SkipTests`; comment column aligned to existing block | 39–46             |
| 3    | "Workspace cleanup" section            | Replaced manual-only sidebar ("```clean.ps1``` + Removes …") with explicit "auto-invoked at start, opt out with `-NoClean`, manual invocation if needed" wording | 48–54             |

### Pre/post line-range deltas

| Region                                   | Pre-edit       | Post-edit      |
| ---------------------------------------- | -------------- | -------------- |
| "What run.ps1 does" numbered list        | 10–19 (10 lines, 7 steps) | 10–19 (10 lines, 8 steps) |
| "Useful run.ps1 switches" code block     | 36–44 (9 lines)  | 37–46 (10 lines, +1 entry) |
| "Workspace cleanup" section              | 46–53 (8 lines)  | 48–54 (7 lines)  |
| Total file length                        | 53 lines       | 54 lines (+1)   |

### Excerpts (post-edit)

**"What run.ps1 does" (lines 10–19):**

```markdown
## What run.ps1 does

1. Cleans prior `__pycache__` / `.pytest_cache` from `temp_root` and the working tree (skip with `-NoClean`)
2. Finds the repo root
3. Runs the classification pipeline for each active vendor (dell, cisco, hpe, lenovo, huawei, xfusion)
4. Runs `batch_audit.py` (E-code audit; add `-NoAi` to skip the LLM step)
5. Runs `cluster_audit.py`
6. Saves logs to the OUTPUT directory
7. Runs pytest if not `-SkipTests`
8. Prints a summary
```

**"Useful run.ps1 switches" (lines 37–46):**

```markdown
## Useful run.ps1 switches

```powershell
.\run.ps1 -NoAi                        # rule-based audit only (no OPENAI_API_KEY needed)
.\run.ps1 -Vendor dell                 # one vendor end-to-end
.\run.ps1 -TestsOnly                   # pytest only
.\run.ps1 -SkipTests                   # full run without pytest at the end
.\run.ps1 -NoClean                     # skip the start-of-run clean.ps1 sweep
.\run.ps1 -Vendor huawei -NoAi -SkipTests  # smoke run
```
```

**"Workspace cleanup" (lines 48–54):**

```markdown
## Workspace cleanup

`run.ps1` invokes `.\spec_classifier\scripts\clean.ps1` automatically at the start of every run. Pass `-NoClean` to opt out. To clean manually without running the pipeline:

```powershell
.\spec_classifier\scripts\clean.ps1
```
```

## Verification

### Static checks (automated)

All grep predicates from Task 3.1's `<verify><automated>` block exit 0:

| Predicate                                                                                          | Result       |
| -------------------------------------------------------------------------------------------------- | ------------ |
| `grep -F '1. Cleans prior \`__pycache__\` / \`.pytest_cache\`'`                                    | PASS (1)     |
| `grep -F '8. Prints a summary'`                                                                    | PASS (1)     |
| `grep -F '.\run.ps1 -NoClean'`                                                                     | PASS (2 — switches block + workspace-cleanup section sentence) |
| `grep -F 'skip the start-of-run clean.ps1 sweep'`                                                  | PASS (1)     |
| `grep -F '\`run.ps1\` invokes \`.\spec_classifier\scripts\clean.ps1\` automatically'`              | PASS (1)     |
| `grep -F 'Pass \`-NoClean\` to opt out.'`                                                          | PASS (1)     |

### Acceptance criteria

| Criterion                                                                                          | Result       |
| -------------------------------------------------------------------------------------------------- | ------------ |
| `grep -cE '^[0-9]+\. ' ONE_BUTTON_RUN.md` >= 8                                                     | PASS (11 — 8 from "What run.ps1 does" list + 3 from "Configuration" list) |
| `grep -c 'skip with \`-NoClean\`'` >= 1                                                            | PASS (1)     |
| `grep -cF '.\run.ps1 -NoClean '` >= 1 (switches block entry)                                       | PASS (1)     |
| Workspace cleanup section: `-NoClean` count >= 1                                                   | PASS (1)     |
| Workspace cleanup section: `clean.ps1` count >= 1                                                  | PASS (2)     |
| **CACHE-04 acceptance gate**: `-NoClean` AND `clean.ps1` co-occur in "Workspace cleanup" section   | **PASS**     |
| Old "Removes \`__pycache__\`, \`.pytest_cache\`, …" sentence removed (`grep -c == 0`)              | PASS (0)     |

### D-22 protected-paths guard

```
$ git diff --stat HEAD -- spec_classifier/src spec_classifier/rules \
    spec_classifier/golden spec_classifier/tests \
    spec_classifier/batch_audit.py spec_classifier/cluster_audit.py \
    spec_classifier/main.py spec_classifier/conftest.py
(no output)
```

PASS — zero bytes changed inside any D-22 protected path.

### Goldens byte-equal guard

```
$ git diff --stat HEAD -- spec_classifier/golden/
(no output)
```

PASS — all 40 golden fixtures byte-identical.

### Diff-scope guard (D-12: only ONE_BUTTON_RUN.md under spec_classifier/docs/)

```
$ git diff --stat HEAD -- spec_classifier/docs/
 spec_classifier/docs/dev/ONE_BUTTON_RUN.md | 21 +++++++++++----------
 1 file changed, 11 insertions(+), 10 deletions(-)
```

PASS — only `ONE_BUTTON_RUN.md` modified; no other doc in `spec_classifier/docs/` touched (D-12).

### Pytest skip-ratio gate

`C:/venv/Scripts/python.exe -m pytest -q` (run from `spec_classifier/`):

```
774 passed, 1 xfailed, 25 warnings in 20.06s
```

| Counter    | Value |
| ---------- | ----- |
| passed     | 774   |
| skipped    | 0     |
| xfailed    | 1     |
| failed     | 0     |
| total      | 775   |
| skip-ratio | 0/775 = 0% (gate threshold: must be ≤ 50%) |

PASS — `conftest.py::pytest_sessionfinish` skip-guard not tripped. Counts byte-identical to Plans 04-01 and 04-02 (no behavior change confirmed; doc-only edit cannot affect test discovery).

## Deviations from Plan

### Auto-fixed Issues

None.

### Deviations from CONTEXT.md decisions

None. All 3 edits land at the prescribed locations:

- **D-11.1** ("What run.ps1 does" numbered list): inserted new step 1 with cleanup wording mirroring `clean.ps1`'s actual sweep semantics; renumbered subsequent steps. — Applied verbatim.
- **D-11.2** ("Useful run.ps1 switches" code block): added `-NoClean` entry between `-SkipTests` and the smoke-run line; `#`-comment column aligned to surrounding block. — Applied verbatim.
- **D-11.3** ("Workspace cleanup" section): rewritten so `-NoClean` and `clean.ps1` co-occur (CACHE-04 acceptance gate). Old "Removes `__pycache__`, `.pytest_cache`, ..." sentence removed (would invite drift the moment `clean.ps1` is updated, per the plan's `<action>` rationale). — Applied verbatim.
- **D-12** (no other docs touched): only `ONE_BUTTON_RUN.md` under `spec_classifier/docs/` modified. Verified by `git diff --stat HEAD -- spec_classifier/docs/`. — Applied verbatim.

### Out-of-scope discoveries

None. Edit scope is confined to `spec_classifier/docs/dev/ONE_BUTTON_RUN.md` per CONTEXT.md D-11/D-12 and the plan's `<action>` "Out-of-scope reaffirmation" block. The stale `config.local.yaml.example:11` comment ("Used by scripts/clean.ps1 and scripts/run_full.ps1.") was NOT touched — that rewrite belongs to ORPH-02 in Phase 5 per D-14.

## Threat Flags

None — Plan 04-03 is a doc-only edit with no runtime parsing surface, no env-var flow, no subprocess invocation, no untrusted-input handling. The `<threat_model>` register declared `(none)`; that disposition holds unchanged.

## Self-Check: PASSED

- `spec_classifier/docs/dev/ONE_BUTTON_RUN.md` exists and contains all 3 edits — FOUND
- All 6 grep predicates from `<verify><automated>` exit 0 — OK
- All 7 acceptance-criteria checks pass — OK
- CACHE-04 acceptance gate (`-NoClean` + `clean.ps1` co-occur in Workspace cleanup section) — PASS
- D-22 protected-paths guard: zero rows in `git diff --stat HEAD -- spec_classifier/{src,rules,golden,tests,batch_audit.py,cluster_audit.py,main.py,conftest.py}` — OK
- Goldens byte-equal guard: zero rows in `git diff --stat HEAD -- spec_classifier/golden/` — OK
- Diff-scope guard (D-12): only `ONE_BUTTON_RUN.md` under `spec_classifier/docs/` — OK
- Pytest exits clean (774 pass / 1 xfail / 0 skipped / 0 failed; skip-ratio 0% << 50% gate) — OK
- Commit hash for Task 3.1: recorded in commit metadata after Write completes

## Notes for Phase 4 closeout & Phase 6

After Plan 04-03:

- **Phase 4 is functionally complete.** All four CACHE requirements (CACHE-01, CACHE-02, CACHE-03, CACHE-04) are satisfied: `run.ps1` and `teresa_gui.py` both redirect Python bytecode + pytest cache to `temp_root` (CACHE-01/CACHE-02), `run.ps1` auto-invokes `clean.ps1` with `-NoClean` opt-out (CACHE-03), and the operator-facing quick-start doc accurately reflects the new contract (CACHE-04).
- **Doc-vs-impl drift across the rest of the doc tree** (`README.md`, root `CLAUDE.md`, `LAUNCHER_README.md`, `RUN_PATHS_AND_IO_LAYOUT.md`, `spec_classifier/CLAUDE.md`, etc.) is intentionally left for **Phase 6's mechanical drift sweep** per D-12. Any references to `clean.ps1` as "manual" in those files will be reconciled then, not now.
- **Phase 5** (orphan cleanup, ORPH-01..03) is the next sequential phase; it owns the `pyproject.toml:5` rewrite, `config.local.yaml.example:11` comment fix, and `.cursor/` + `teresa.zip` removal. Plan 04-03 deliberately does NOT touch any of those (D-14).
