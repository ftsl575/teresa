# Phase 5: Orphan Cleanup - Context

**Gathered:** 2026-05-10
**Status:** Ready for planning

<domain>
## Phase Boundary

Kill the two stale `scripts/run_full.ps1` references in canonical config files
(`spec_classifier/pyproject.toml:5`, `spec_classifier/config.local.yaml.example:11`)
and replace them with wording that's true post-Phase-4 (i.e., `run.ps1` and
`teresa_gui.py` set `PYTHONPYCACHEPREFIX` + `PYTEST_ADDOPTS` from
`config.local.yaml::temp_root`). Remove the residual `.cursor/` directory and
`teresa.zip` sandbox artifact from the working tree (both gitignored, neither
git-tracked). Tighten `ROADMAP.md` Phase 5 §SC-1 to scope its `run_full` grep
gate to `--include='*.toml' --include='*.example'`, matching `REQUIREMENTS.md`
verification verbatim — closes a real gate-spec disagreement before the
verification step runs.

`CHANGELOG.md`, `LAUNCHER_README.md:4`, and `run.ps1:3` (Russian historical
"Заменяет: …" comment) retain their `run_full` mentions per D-18 / D-19
historical-content convention. The `_run_full` method in `teresa_gui.py:294,489`
is the GUI's "run all vendors" button handler — unrelated to the deleted script,
left untouched.

**Strictly out of scope:**
- Any diff inside D-22 protected paths
  (`spec_classifier/{src,rules,golden,tests,batch_audit.py,cluster_audit.py,main.py,conftest.py}`).
  Phase gate fails on a non-empty diff there.
- Stale post-Phase-4 references in `.planning/codebase/STACK.md:79` and
  `.planning/codebase/INTEGRATIONS.md:150` ("`run.ps1` does not export
  `PYTHONPYCACHEPREFIX`") — both inside the gate's `.planning/` exclusion
  scope; deferred to Phase 6's drift sweep or a post-v1.1 `/gsd-map-codebase`
  refresh.
- Translation of `run.ps1:3` Russian comment to English — exempt under the
  tightened gate; not a Phase 5 deliverable.
- Renaming the `_run_full` method in `teresa_gui.py` — exempt under the
  tightened gate; substring match is a false-positive grep concern, not a real
  reference to the deleted script.
- `clean.ps1` augmentation to sweep `.cursor/` or `teresa.zip` on every run —
  one-shot residual artifacts, not recurring runtime caches.
- Any new file under `scripts/` (e.g., a dedicated orphan-sweep script) —
  inline plan-step removal preferred.
- `.gitignore` edits — `.cursor/` and `teresa.zip` already gitignored
  (lines 48, 56); leave entries in place so the artifacts stay ignored if they
  ever reaccumulate.

</domain>

<decisions>
## Implementation Decisions

### Area A — `run_full` grep gate scope (gate-realignment)

- **D-01 (gate scope tightened):** ROADMAP.md Phase 5 §SC-1 is rewritten so
  the gate's grep is scoped to `--include='*.toml' --include='*.example'`,
  matching `REQUIREMENTS.md` § "Orphan Cleanup (ORPH) — Plan 2" verbatim. The
  current ROADMAP wording ("`grep -rn "run_full" .` … returns zero matches
  across the entire repo") is a real spec disagreement: applied as written, it
  would FAIL on `run.ps1:3` (RU historical comment, exempt by D-18 spirit) and
  on `teresa_gui.py:294,489` (unrelated `_run_full` method name). Tightening
  resolves the disagreement without touching launcher code.
- **D-02 (RU comment disposition):** `run.ps1:3` Russian comment ("Заменяет:
  run_audit.ps1, scripts/run_full.ps1, scripts/run_tests.ps1") is left
  unchanged. Same status as `LAUNCHER_README.md:4` — historical mention,
  exempted under the tightened gate. Translation is a separate hygiene concern
  not in Phase 5's scope.
- **D-03 (`_run_full` method left as-is):** `teresa_gui.py:294`
  (`self.full_btn.clicked.connect(self._run_full)`) and `teresa_gui.py:489`
  (`def _run_full`) are method-name false positives in the substring grep. The
  method handles the GUI's "run all vendors" button — not a reference to the
  deleted script. Left untouched; tightened gate excludes them.
- **D-04 (gate-realignment is a Phase 5 deliverable):** The ROADMAP.md edit
  ships as the 5th task under Phase 5's single plan, alongside ORPH-01..04. Not
  added as a new requirement (no ORPH-05) — captured here in CONTEXT.md as a
  documented adjustment that the planner consumes. Task ordering puts the
  ROADMAP edit first (T1) so subsequent verification within the plan uses the
  correct gate spec.

### Area B — Replacement wording (ORPH-01 / ORPH-02)

- **D-05 (ORPH-01 — `pyproject.toml:4-6` rewrite):** Replace lines 4-6 with a
  3-line block that names both env vars (PYTHONPYCACHEPREFIX + PYTEST_ADDOPTS)
  and both entry points (run.ps1 + teresa_gui.py), reflecting Phase 4's full
  D-08 + D-13 wiring:
  ```
  # __pycache__ + .pytest_cache redirection requires PYTHONPYCACHEPREFIX + PYTEST_ADDOPTS env vars.
  # run.ps1 and teresa_gui.py set both from config.local.yaml::temp_root automatically.
  # pyproject.toml cannot redirect __pycache__ (only env var can).
  ```
  Tighter than `REQUIREMENTS.md` ORPH-01's suggested wording ("Set it in your
  shell profile or use run.ps1 (sets PYTHONPYCACHEPREFIX automatically)."),
  which omits PYTEST_ADDOPTS and `teresa_gui.py`. Lines 1-3 (the `[tool.pytest.ini_options]`
  block) and line 7+ (the `[tool.python]` block) are untouched.
- **D-06 (ORPH-02 — `config.local.yaml.example:11` rewrite):** Replace line 11
  with `# Used by scripts/clean.ps1, run.ps1, and teresa_gui.py.` Names all
  three consumers of `temp_root`. Tighter than REQUIREMENTS.md ORPH-02's
  suggested wording ("Used by scripts/clean.ps1 and run.ps1.") which omits
  `teresa_gui.py`. Line 10 (the section heading comment) and line 12 (the
  `temp_root:` assignment) are untouched.
- **D-07 (no other doc edits in Phase 5):** Phase 5 does not touch
  `RUN_PATHS_AND_IO_LAYOUT.md`, `README.md`, `LAUNCHER_README.md`, or any
  doc under `spec_classifier/docs/`. Phase 6's mechanical drift sweep handles
  cross-doc reconciliation against the post-Phase-5 tree.

### Area C — Removal mechanism for `.cursor/` and `teresa.zip` (ORPH-03 / ORPH-04)

- **D-08 (one-shot inline removal):** Plan executes the removals via two
  Test-Path-guarded `Remove-Item` lines inline in the plan's action block:
  ```powershell
  if (Test-Path .\.cursor)    { Remove-Item .\.cursor    -Recurse -Force }
  if (Test-Path .\teresa.zip) { Remove-Item .\teresa.zip -Force }
  ```
  Idempotent (Test-Path guards survive replay), atomic, no new files. Both
  artifacts are gitignored — no `git rm` needed. Replay-safe so a re-execution
  after partial completion is a no-op on the already-removed item.
- **D-09 (no `clean.ps1` augmentation):** `.cursor/` and `teresa.zip` are NOT
  added to `clean.ps1`'s sweep list. They are one-off residual artifacts, not
  recurring runtime caches; conflating them dilutes `clean.ps1`'s purpose.
  `.cursor/` would also legitimately reappear if the user opens the repo in
  Cursor — automated re-sweep would block legitimate use.
- **D-10 (no new sweep script):** Phase 5 does not add `scripts/orphan_sweep.ps1`
  or any other one-off cleanup script. Inline plan steps suffice; a one-shot
  script in the repo for a single milestone's cleanup is awkward to retire.
- **D-11 (no `git clean -fdx`):** Removal does not use `git clean -fdx --
  .cursor teresa.zip`. While semantically clean for "gitignored junk", it
  couples removal to git state and would silently no-op if git is unavailable
  or the worktree is dirty in unrelated ways. Plain `Remove-Item` is more
  predictable.
- **D-12 (fail-fast on lock):** Wrap the two `Remove-Item` calls in the plan's
  default `$ErrorActionPreference = "Stop"` discipline (no try/catch wrapper).
  If a file is locked (e.g., by an open IDE), the phase halts and surfaces
  the error immediately. The verification gate (`Test-Path returns $false`)
  would not pass on partial removal anyway — fail at the action, not at the
  gate. No retry-with-backoff (complexity not justified for a once-per-milestone
  operation).
- **D-13 (`.gitignore` untouched):** Lines 48 (`.cursor/`) and 56 (`teresa.zip`)
  remain in `.gitignore` after removal. If either artifact reappears later,
  the existing ignore rule keeps them out of git. Removing the ignore rules
  would require also removing the artifacts every time they reappear — net
  worse.

### Area D — Plan structure for Phase 5

- **D-14 (single plan, 5 sequential tasks):** Phase 5 ships as a single
  `05-01-PLAN.md` with 5 tasks (T1..T5). Disjoint files; small surface area;
  one plan keeps the context atomic. Phase 4's 3-plan precedent reflected
  larger per-file scope (run.ps1 had 5 distinct edits) — Phase 5's per-deliverable
  edits are 1-3 lines each.
- **D-15 (task ordering — ROADMAP first):**
  - **T1:** ROADMAP.md §SC-1 grep-scope tightening (gate-realignment).
  - **T2:** ORPH-01 — pyproject.toml:4-6 rewrite (D-05).
  - **T3:** ORPH-02 — config.local.yaml.example:11 rewrite (D-06).
  - **T4:** ORPH-03 — `.cursor/` removal (D-08).
  - **T5:** ORPH-04 — `teresa.zip` removal (D-08).

  Rationale: T1 must precede T2..T5 verification because the gate's grep
  semantics affect what counts as "zero matches". T2..T5 have no inter-dependencies
  (disjoint files). One commit per task = 5 atomic commits per plan.
- **D-16 (verification per task):** Each task's verification command runs
  immediately after the task's action and uses the post-T1 grep spec (`--include='*.toml'
  --include='*.example'` excluding `CHANGELOG.md`, `LAUNCHER_README.md`, `.planning/`).
  Plan-level final verification re-runs the success-criteria checks #1-5 from
  ROADMAP §SC-1..5.
- **D-17 (no parallel waves):** Although T2..T5 are technically parallel-safe
  (disjoint files), they execute sequentially within the single plan. The
  parallelism gain is negligible (5 small edits), and sequential execution
  keeps per-task verification clean.

### Cross-cutting

- **D-18 (commit granularity):** Each of the 5 tasks produces one atomic commit
  with subject `chore(05): T<N> <description>`. Aligns with v1.0/v1.1 commit
  conventions (e.g., `chore(04): T1 …`).
- **D-19 (D-22 protection unchanged):** Phase 5 touches `.planning/ROADMAP.md`,
  `spec_classifier/pyproject.toml`, `spec_classifier/config.local.yaml.example`,
  `.cursor/`, and `teresa.zip`. None of these paths are inside D-22's
  protected set (`spec_classifier/{src,rules,golden,tests,batch_audit.py,
  cluster_audit.py,main.py,conftest.py}`). `git diff --stat` for the
  D-22 protected paths over the phase window MUST be empty.
- **D-20 (pytest skip-ratio gate):** `pytest -q` from `spec_classifier/` runs
  unchanged in Phase 5 verification. Phase 5 does not add or remove tests, so
  the skip ratio is structurally unchanged. Passing the gate is a sanity check,
  not a deliverable.
- **D-21 (goldens byte-equal):** `git diff --stat -- spec_classifier/golden/`
  for the phase window MUST be empty. Phase 5 doesn't touch golden fixtures.

### Claude's Discretion

- Exact wording of the ROADMAP.md §SC-1 edit (D-04). The substantive change
  is adding `--include='*.toml' --include='*.example'` to the grep
  invocation; surrounding prose may be paraphrased to match ROADMAP.md's
  existing voice (e.g., "across the entire repo" → "across `*.toml` /
  `*.example` files").
- Exact phrasing of commit subject lines (D-18) — `chore(05): T1 align ROADMAP
  §SC-1 grep scope` and analogous for T2..T5. Adjust to match v1.1 commit
  precedent if it differs.
- Whether each `Remove-Item` (D-08) emits a confirmation `Write-Host` line.
  Cosmetic; leaning yellow-warning if ran with `-Verbose` style, otherwise
  silent.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Scope, requirements, gates
- `.planning/ROADMAP.md` § "Phase 5: Orphan Cleanup" — goal, success criteria
  1-5, D-22 / pytest-skip / goldens-byte-equal gates verbatim. **Note:**
  Phase 5 T1 rewrites §SC-1 to scope its grep to `--include='*.toml'
  --include='*.example'`; downstream agents should read both the pre-edit and
  post-edit forms (planner reads pre-edit to know what to change; executor
  applies the edit).
- `.planning/REQUIREMENTS.md` § "Orphan Cleanup (ORPH) — Plan 2" — ORPH-01..04
  verbatim, plus the verification grep spec that ROADMAP §SC-1 is realigning to.
- `.planning/PROJECT.md` § "Current Milestone: v1.1" + § "Constraints" —
  milestone goals, no-tech-stack-additions, sequential-phase dependency
  (Phase 4 → 5 → 6).
- `.planning/STATE.md` § "Decisions" — `[v1.1 Init]` lines locking
  helper-consolidation exclusion and sequential phase dependency.

### Cross-phase coordination
- `.planning/phases/04-cache-redirect/04-CONTEXT.md` § D-14 — explicit
  hand-off note: "Phase 4 leaves [`config.local.yaml.example:11`] alone —
  Phase 5 owns the rewrite. Coordination is intentional per the v1.1
  sequential-execution decision." Phase 5's ORPH-02 closes that hand-off.
- `.planning/phases/04-cache-redirect/04-CONTEXT.md` § D-08, D-13 — Phase 4's
  full env-var wiring (PYTHONPYCACHEPREFIX + PYTEST_ADDOPTS in both `run.ps1`
  and `teresa_gui.py`). The replacement wording in D-05 + D-06 above mirrors
  this wiring.

### Architectural guards (do NOT touch)
- `.planning/codebase/CONCERNS.md` § BLOCKER — "do-not-fix" items
  (`power_cord` taxonomy, Dell-specific parser, audit-reads-Excel,
  YAML-rule-order, `HW_TYPE_VOCAB` duplication). All load-bearing during
  Phase 5; phase touches none of them.
- `CLAUDE.md` (root) § "Critical business rules" + § "Code-only repository
  policy" — D-22 protected paths verbatim.
- `spec_classifier/CLAUDE.md` § "Business Rules" + § "Known Tech Debt" —
  deep reference for the same exclusions.

### Files Phase 5 will edit
- `.planning/ROADMAP.md` — §SC-1 of Phase 5 (line ~63 in current state).
  T1 edit per D-01 + D-04.
- `spec_classifier/pyproject.toml` — current state at lines 4-6 (3-line
  comment block above `[tool.python]`). T2 edit per D-05.
- `spec_classifier/config.local.yaml.example` — current state at line 11
  (single comment line above `temp_root:`). T3 edit per D-06.

### Files Phase 5 will remove
- `.cursor/` (root) — directory containing `agents/`, `get-shit-done/`,
  `gsd-file-manifest.json`, `skills/`. Gitignored at `.gitignore:48`. T4
  removal per D-08.
- `teresa.zip` (root) — sandbox artifact. Gitignored at `.gitignore:56`.
  T5 removal per D-08.

### Files Phase 5 reads but does NOT edit
- `run.ps1` — line 3 RU historical comment is exempt under the tightened
  gate (D-02). Method names elsewhere unrelated.
- `teresa_gui.py` — `_run_full` method on lines 294 + 489 is unrelated to
  the deleted script (D-03).
- `LAUNCHER_README.md` — line 4 historical "replaces three legacy scripts"
  mention preserved per D-18 / D-19 historical-content convention.
- `spec_classifier/CHANGELOG.md` — historical entries on lines 33, 125, 148
  preserved per D-18.
- `.planning/codebase/STACK.md:79` and `.planning/codebase/INTEGRATIONS.md:150`
  — stale post-Phase-4 references inside `.planning/` exclusion; deferred to
  Phase 6 / future `/gsd-map-codebase` refresh.
- `.gitignore` — lines 48 (`.cursor/`) and 56 (`teresa.zip`) untouched per
  D-13.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **Phase 4's wiring vocabulary** — `04-CONTEXT.md` D-08 / D-13 introduces
  the canonical phrase "PYTHONPYCACHEPREFIX + PYTEST_ADDOPTS env vars … set
  from `config.local.yaml::temp_root`". Phase 5's ORPH-01 / ORPH-02
  replacement wording (D-05 / D-06) reuses this phrase verbatim for
  consistency.
- **`Test-Path` + `Remove-Item -Recurse -Force` pattern** — used throughout
  `spec_classifier/scripts/clean.ps1` and the Phase 4 verification step
  (`Test-Path .\.pytest_cache` / `Test-Path .\spec_classifier\__pycache__`).
  Phase 5's D-08 inline removal mirrors this idempotent, gitignored-safe
  pattern.
- **Atomic per-task commit convention** — established in v1.0 (Phase 1 / 2 / 3)
  and extended through Phase 4. Phase 5's D-18 follows the same `chore(NN):
  TM <description>` subject style.

### Established Patterns
- **D-22 protected paths** — load-bearing for every v1.1 phase. Phase 5
  touches zero D-22 paths; the gate is a passive guard, not a hurdle.
- **First-match-wins YAML rule order** — irrelevant to Phase 5 (no rules
  edits) but reaffirmed by D-22 protection.
- **Defense-in-depth env-var setting** (Phase 4 D-13) — the wording in D-05
  / D-06 must reflect that BOTH `run.ps1` AND `teresa_gui.py` set the env
  vars. Single-source language ("`run.ps1` sets …") would be a regression
  from Phase 4's defense-in-depth story.

### Integration Points
- **Phase 5 → Phase 6 hand-off:** Phase 6's mechanical drift sweep operates
  on the post-Phase-5 tree. The two `.planning/codebase/` stale references
  (STACK.md:79, INTEGRATIONS.md:150) are explicitly deferred to Phase 6's
  scope decision; if Phase 6 chooses not to include `.planning/codebase/`,
  flag this as remaining drift in the Phase 6 SUMMARY.
- **No runtime-pipeline integration** — Phase 5 is purely cleanup; no
  classifier, parser, audit, or test code runs differently after the phase.
  Pytest skip-ratio gate runs as a sanity check (D-20).

</code_context>

<specifics>
## Specific Ideas

- **Mirror REQUIREMENTS.md verification semantics in ROADMAP.md** — the
  phrase to thread into §SC-1's edit is `--include='*.toml' --include='*.example'`
  (with the surrounding `(excluding CHANGELOG.md, LAUNCHER_README.md, .planning/)`
  qualifier preserved). Mechanical consistency with REQUIREMENTS.md ORPH
  verification is what makes the gate audit-trail-clean.
- **Three-line-block edit for `pyproject.toml`** (D-05) — preserve the
  existing structure: line 4 ("`# … requires`"), line 5 ("`# run.ps1 and
  teresa_gui.py set both …`"), line 6 ("`# pyproject.toml cannot redirect
  …`"). Don't collapse into one long comment; downstream readers parse the
  3-line shape.
- **Idempotent Test-Path guards** in D-08 — wrap each `Remove-Item` so a
  partial-completion replay is a no-op. Worth the 6-extra-tokens
  insurance against re-execution.
- **Commit message verbosity** — keep T1..T5 commit subjects short
  (≤72 chars). Detail belongs in the body. Pattern: `chore(05): T<N>
  <verb> <object>` (e.g., `chore(05): T2 rewrite pyproject.toml run_full
  reference`).

</specifics>

<deferred>
## Deferred Ideas

- **`.planning/codebase/STACK.md:79` + `.planning/codebase/INTEGRATIONS.md:150`
  stale references** — both files describe `run.ps1` as "not exporting
  PYTHONPYCACHEPREFIX" / "not currently exported by run.ps1" — stale post-Phase-4
  reality. Inside `.planning/` so excluded by Phase 5's grep gate. Two
  pathways: (a) fold into Phase 6's drift sweep scope by extending the in-scope
  file list to include `.planning/codebase/`, or (b) defer to a post-v1.1
  `/gsd-map-codebase` refresh. Reopen at Phase 6 planning.
- **Translation of `run.ps1:3` Russian historical comment to English** —
  exempt under the tightened gate; same status as `LAUNCHER_README.md:4`.
  If a future hygiene milestone converts all in-tree comments to English, this
  is one of them. Captured here so it's not forgotten.
- **Renaming `_run_full` method in `teresa_gui.py`** — false-positive grep
  match, not a real reference to the deleted script. Renaming would be a
  small refactor (`_run_full` → `_run_all_vendors` or similar) inside
  launcher code, out of cleanup scope. Not blocking; only relevant if a
  future contributor proposes it.
- **`clean.ps1` extension to sweep `.cursor/` / `teresa.zip`** — explicitly
  rejected (D-09). `.cursor/` would legitimately reappear if the user opens
  the repo in Cursor; automated re-sweep would conflict.
- **`scripts/orphan_sweep.ps1` as a reusable cleanup script** — explicitly
  rejected (D-10). One-off milestone cleanup doesn't justify a permanent
  script.
- **`git clean -fdx -- .cursor teresa.zip` removal mechanism** — explicitly
  rejected (D-11). Couples removal to git state in an unhelpful way.
- **Removing `.gitignore` lines 48 / 56 after the artifacts are deleted** —
  explicitly rejected (D-13). Keeps the ignore rules as a passive guard
  against reaccumulation.
- **Adding ORPH-05 (or similar) for the ROADMAP §SC-1 edit** — explicitly
  rejected (D-04). The realignment is a documented adjustment captured in
  CONTEXT.md; not a new requirement that needs traceability matrix updates.

### Reviewed Todos (not folded)
None — `gsd-sdk query todo.match-phase 5` returned 0 matches, so no todos
were reviewed during discussion.

</deferred>

---

*Phase: 5-orphan-cleanup*
*Context gathered: 2026-05-10*
