# Phase 6: Doc-vs-Impl Drift Sweep - Context

**Gathered:** 2026-05-11
**Status:** Ready for planning

<domain>
## Phase Boundary

Mechanically re-verify every "code does X" claim across the 13 files under
`spec_classifier/docs/` plus the 3 root markdown files (`README.md`, `CLAUDE.md`,
`CONTRIBUTING.md`) against the post-Phase-4-and-5 tree. Drifted claims are
removed (preferred per ROADMAP §SC-5 "remove > patch") or fixed. Trim
duplicated CLI-flag prose in `spec_classifier/docs/user/RUN_PATHS_AND_IO_LAYOUT.md`
and `spec_classifier/docs/dev/ONE_BUTTON_RUN.md` (line counts strictly less than
pre-phase baseline). Create `spec_classifier/docs/dev/DOC_INVARIANTS.md` with
≥5 mechanical drift invariants, each a one-line check that exits 0 against the
post-phase tree. A re-sweep against the corrected tree returns 0 drift claims.

Phase 6 also extends the sweep with **3 surgical patches** to `.planning/codebase/`
that Phase 5 explicitly punted ("Phase 6's drift sweep OR a post-v1.1
`/gsd-map-codebase` refresh"). The 3 lines are the known stale ones — broader
refresh of the 7-file `.planning/codebase/` map tree stays a separate
`/gsd-map-codebase` task in v1.2 backlog.

Phase 6 also extends `run.ps1` with a comment-based help block (`<#.SYNOPSIS#>`)
in English so the ROADMAP DRIFT-02 phrase "pointer to `run.ps1 -?`" becomes
literally true. The existing Russian comment header at `run.ps1:1-13` is left
untouched per Phase 5 D-02 + the D-18 historical-content convention.

**Strictly out of scope:**
- Any diff inside D-22 protected paths
  (`spec_classifier/{src,rules,golden,tests,batch_audit.py,cluster_audit.py,main.py,conftest.py}`).
  Phase gate fails on a non-empty diff there. Note: `run.ps1` and `teresa_gui.py`
  are NOT D-22 paths — Phase 6's only launcher edit (the help block on `run.ps1`)
  is comments-only and behavior-neutral.
- `spec_classifier/CLAUDE.md`, `spec_classifier/README.md`,
  `spec_classifier/CHANGELOG.md` — explicitly NOT in the ROADMAP-enumerated
  16-file scope. `CHANGELOG.md` exempt under D-18; the other two carry rich
  drift surface (LOC counts, rule_id counts, line numbers) but their refresh
  is folded into the deferred broader `/gsd-map-codebase` task.
- Volatile-count claims (test count, LOC, rule_id counts, vendor count) in
  IN-scope files. Patching chases moving targets; most live in the carved-out
  `spec_classifier/CLAUDE.md` anyway. Captured as deferred for the same
  `/gsd-map-codebase` refresh.
- Full 7-file refresh of `.planning/codebase/` maps. Only the 3 known stale
  lines (STACK.md:79, INTEGRATIONS.md:150, INTEGRATIONS.md:55) get surgically
  patched in Phase 6.
- Translation of `run.ps1:1-13` Russian header to English. Phase 5 D-02 already
  exempted it; Phase 6 inherits that exemption (B-3 coexist decision).
- Pre-commit hook / CI integration of `DOC_INVARIANTS.md` checks. v1.1 is
  no-tooling-additions per REQUIREMENTS.md AUTO-02 backlog deferral.
- Any new file under `scripts/` or runner script for the invariants —
  DOC_INVARIANTS.md is doc-of-record only (D-2 D-23 below).

</domain>

<decisions>
## Implementation Decisions

### Area A — `.planning/codebase/` stale references (Phase 5 hand-off)

- **D-01 (surgical fix, not full refresh):** Phase 6 patches the 3 known stale
  lines in `.planning/codebase/` inline as part of the sweep. It does NOT
  enumerate or fix broader drift in the 7-file map tree (STACK / INTEGRATIONS /
  ARCHITECTURE / STRUCTURE / CONCERNS / CONVENTIONS / TESTING). Broader refresh
  is deferred to a separate `/gsd-map-codebase` task in v1.2 backlog. Rationale:
  scope discipline (Phase 6's existing 16-file load is large; expanding to 7 more
  files of map prose pushes the audit log past tractability) plus tooling fit
  (`/gsd-map-codebase` is the right tool for full-file refresh; surgical line
  patches are the right tool for known stale claims).
- **D-02 (the 3 surgical lines):** Exact patch set:
  - `.planning/codebase/STACK.md:79` — currently `PYTHONPYCACHEPREFIX … Not
    set by run.ps1 (used to be set by the old scripts/run_full.ps1)`. Stale
    post-Phase-4. Replacement: prose mirroring Phase 5 D-05/D-06 vocabulary
    (PYTHONPYCACHEPREFIX + PYTEST_ADDOPTS env vars, `run.ps1` and
    `teresa_gui.py`, set from `config.local.yaml::temp_root`).
  - `.planning/codebase/INTEGRATIONS.md:150` — same stale claim
    (`PYTHONPYCACHEPREFIX … Not currently exported by run.ps1 (was set by
    the now-retired scripts/run_full.ps1)`). Same replacement vocabulary.
  - `.planning/codebase/INTEGRATIONS.md:55` — `| TEMP (.pytest_cache/,
    __pycache__/) | C:\Users\G\Desktop\temporary | temp_root in
    config.local.yaml |` — hardcoded `C:\Users\G\` username leak that v1.0
    HYG-01 was supposed to strip. Replacement: `C:\Users\<USERNAME>\Desktop\temporary`
    per HYG-01 convention.
- **D-03 (preferred replacement vocabulary):** Phase 5 D-05/D-06 already
  established the canonical phrase: "PYTHONPYCACHEPREFIX + PYTEST_ADDOPTS env
  vars set by `run.ps1` and `teresa_gui.py` from `config.local.yaml::temp_root`".
  Reuse verbatim in D-02's first two patches for vocabulary consistency
  across the milestone. Defense-in-depth (both launcher AND GUI) must be
  preserved — single-source language is a Phase 4 D-13 regression.

### Area B — `run.ps1 -?` pointer reality (DRIFT-02 trim)

- **D-04 (both: help block + canonical-doc pointer):** Phase 6 (a) adds a
  comment-based help block (`<#.SYNOPSIS / .DESCRIPTION / .PARAMETER / .EXAMPLE#>`)
  to `run.ps1` so `Get-Help .\run.ps1` and `.\run.ps1 -?` actually return
  useful help, AND (b) keeps `spec_classifier/docs/dev/ONE_BUTTON_RUN.md` as
  the canonical human-readable switch table; `RUN_PATHS_AND_IO_LAYOUT.md`
  CLI prose gets trimmed to a one-line pointer to ONE_BUTTON_RUN.md (and to
  `run.ps1 -?`). Both reader paths work after Phase 6.
- **D-05 (help block content):** Six examples mirror the existing RU header at
  `run.ps1:1-13`:
  ```
  .EXAMPLE  .\run.ps1                              # full pipeline + AI audit + cluster + tests
  .EXAMPLE  .\run.ps1 -NoAi                        # full pipeline + rule-only audit (no OpenAI)
  .EXAMPLE  .\run.ps1 -Vendor dell                 # only dell, otherwise as usual
  .EXAMPLE  .\run.ps1 -TestsOnly                   # pytest only
  .EXAMPLE  .\run.ps1 -SkipTests                   # full pipeline without pytest at end
  .EXAMPLE  .\run.ps1 -Vendor huawei -NoAi -SkipTests  # minimal smoke run
  ```
  Plus one `.PARAMETER` block for each of the 5 switches: `Vendor`, `NoAi`,
  `TestsOnly`, `SkipTests`, `NoClean`. Plus a one-line `.SYNOPSIS` and a
  short `.DESCRIPTION` paragraph (3-5 lines) summarizing the pipeline.
- **D-06 (RU header coexists, untouched):** The Russian comment header at
  `run.ps1:1-13` stays exactly as-is. New `<#...#>` block is added adjacent
  (planner picks above-vs-below; below the RU header reads more naturally,
  but either satisfies the deliverable). Phase 5 D-02 + D-18 historical-content
  convention preserved.
- **D-07 (DRIFT-02 wording realignment):** The ROADMAP DRIFT-02 phrase
  "trimmed CLI-flag prose is replaced with a pointer to `run.ps1 -?`" was
  literally false at phase start (`run.ps1` had no help block; `-?` returned
  nothing useful). It becomes literally true after the D-05 task lands. This
  is a documented adjustment captured here in CONTEXT.md (mirrors the Phase 5
  D-04 ROADMAP-realignment pattern) — NOT a new requirement, NOT an edit to
  ROADMAP DRIFT-02 itself.
- **D-08 (D-22 verification for run.ps1 edit):** `run.ps1` is NOT inside
  D-22's protected set (`spec_classifier/{src,rules,golden,tests,batch_audit.py,cluster_audit.py,main.py,conftest.py}`).
  The help block is comments-only — no behavior change. `git diff --stat
  -- run.ps1` over the phase window will show insertions in the comments
  block; no token in `param()`, the `if`/`foreach` blocks, or any executable
  line should change.
- **D-09 (trim mechanism for the two named docs):**
  - `ONE_BUTTON_RUN.md` (54 lines pre-phase) — the "Useful run.ps1 switches"
    section already lists all 6 switches. Add a one-line pointer above the
    section: "These switches are also documented in `run.ps1`'s comment-based
    help (run `.\run.ps1 -?`)." Line count must STRICTLY DECREASE per SC #3 —
    achieved by collapsing or removing the "Quick start" / "Workspace cleanup"
    sections that duplicate the switches block.
  - `RUN_PATHS_AND_IO_LAYOUT.md` (281 lines pre-phase) — the bulk of CLI prose
    lives in §"Configuration path priority" + §"Default folders" + the
    end-of-file IDE notes. Trim the "Do not run python -m pytest directly
    without run.ps1" / "Run `clean.ps1`" prose into a single pointer paragraph
    at top: "For run.ps1 switches, see `run.ps1 -?` or
    [docs/dev/ONE_BUTTON_RUN.md](../dev/ONE_BUTTON_RUN.md). For path
    discovery internals, see below." Then keep the path/I/O tables as-is —
    those are the doc's load-bearing content, not the CLI prose.

### Area C — Sweep mechanism + claim definition

- **D-10 (sweep mechanism = hybrid manual + scripted-subset):** Phase 6's
  sweep is human-driven: the executor reads each in-scope file, mentally
  checks every "code does X" claim against the current code (using `grep`,
  `Test-Path`, line-number lookup, or runtime check as appropriate), and
  decides remove vs. patch per claim. Each (file, line, claim, check,
  resolution) tuple is recorded in `06-DRIFT-AUDIT.md` (D-22 below). The
  5+ MOST drift-prone of those checks are then materialized in
  `DOC_INVARIANTS.md` (Area D) as Bash one-liners. SC #1 re-sweep =
  re-run `DOC_INVARIANTS.md` checks + spot-check newly-added claims by
  re-reading the diffed lines.
- **D-11 (claim categories IN scope):** Three categories are swept:
  1. **Path/file existence + behavior claims.** Examples: "`run.ps1` exists",
     "`scripts/clean.ps1` exists", "`run.ps1` sets `PYTHONPYCACHEPREFIX`",
     "audit reads `*_annotated.xlsx`", "first-match-wins". Checked by
     `Test-Path` / `grep` / runtime. Highest load-bearing — the class of
     claim that broke v1.0 (PYTHONPYCACHEPREFIX wiring drift not caught by
     read-pass DOC-03 audit).
  2. **Switch/CLI flag claims.** Examples: "`.\run.ps1 -NoClean`", "`python
     main.py --update-golden`", "`pytest -k expression`", "`--vendor dell`".
     Checked by `grep` in `run.ps1`/`main.py`/`teresa_gui.py`. Medium
     load-bearing — wrong CLI examples break copy-paste. Common in
     `ONE_BUTTON_RUN.md`, `CLI_CONFIG_REFERENCE.md`, `USER_GUIDE.md`, root
     `README.md`, root `CONTRIBUTING.md`.
  3. **Line-number refs (`file.py:N`).** Examples: "see `run.ps1:36-40`",
     "`teresa_gui.py:225,489`", "`pyproject.toml:4-5`". Line-shifted refs
     are stale every time the underlying file changes. Apply remove > patch
     aggressively: rewrite as **symbol or section refs** ("see `run.ps1`'s
     `param()` block", "see `_discover_input_path` in `teresa_gui.py`")
     instead of chasing line numbers. Removing the line-number entirely (no
     replacement) is also acceptable when the surrounding prose suffices.
- **D-12 (claim categories DEFERRED, not swept in Phase 6):** Volatile counts
  — test count ("420 tests"), LOC counts ("`batch_audit.py` 1489 LOC"),
  rule_id counts ("`dell_rules.yaml` 93 rules"), vendor count, doc count.
  Patching chases moving targets; most live in the OUT-of-scope
  `spec_classifier/CLAUDE.md` anyway. Deferred to the broader
  `/gsd-map-codebase` refresh task (v1.2 backlog) along with the
  Area-A-deferred 7-file map tree.
- **D-13 (remove > patch heuristic):** ROADMAP §SC-5 says "preference is
  remove > patch". Concrete heuristic: **default removal**. Patch only when
  BOTH (a) the claim is load-bearing for the reader's mental model (i.e.,
  removing degrades comprehension) AND (b) the patched form is itself stable
  (e.g., a symbol-name reference, not a line number). When in doubt, remove
  and let the reader `grep` the code directly — that's the durable
  knowledge path.
- **D-14 (sweep order):** Files are swept top-to-bottom in this order so
  that downstream files can reference upstream patched wording without
  re-drift:
  1. Root: `README.md`, `CLAUDE.md`, `CONTRIBUTING.md` (root docs lead;
     they constrain the docs/ tree's vocabulary).
  2. `spec_classifier/docs/DOCS_INDEX.md` (1:1 contract; touch it last in
     this group only if a doc is renamed — none planned).
  3. `spec_classifier/docs/dev/` (NEW_VENDOR_GUIDE, ONE_BUTTON_RUN,
     OPERATIONAL_NOTES, TESTING_GUIDE) — heavy CLI density.
  4. `spec_classifier/docs/user/` (CLI_CONFIG_REFERENCE,
     RUN_PATHS_AND_IO_LAYOUT, USER_GUIDE) — heavy path/CLI density; also
     the 2 trim targets for DRIFT-02.
  5. `spec_classifier/docs/product/` (TECHNICAL_OVERVIEW),
     `spec_classifier/docs/schemas/` (DATA_CONTRACTS),
     `spec_classifier/docs/rules/` (RULES_AUTHORING_GUIDE),
     `spec_classifier/docs/taxonomy/` (hw_type_taxonomy, cycle2_summary).
  6. `.planning/codebase/STACK.md` and `.planning/codebase/INTEGRATIONS.md`
     (Area A surgical patches — done last so the executor has full sweep
     context).

### Area D — `DOC_INVARIANTS.md` design

- **D-15 (location):** `spec_classifier/docs/dev/DOC_INVARIANTS.md`
  (roadmap-locked).
- **D-16 (check language = Bash one-liners):** Every invariant is a Bash
  one-liner using `grep` / `test` / standard shell utilities. Matches the
  ROADMAP §SC-2 example verbatim (`grep -q "PYTHONPYCACHEPREFIX" run.ps1`
  exit 0). Runs in Git Bash on Windows (already a GSD workflow dep) and on
  POSIX. Most portable; reproducible across contributors regardless of
  shell. PowerShell-only patterns (`Test-Path .cursor`) get re-expressed
  as `[ ! -e .cursor ]` or `test -e .cursor`.
- **D-17 (execution model = doc-of-record + manual run):**
  `DOC_INVARIANTS.md` is a human-runnable reference. Each invariant is a
  copy-pasteable Bash line; a "How to run them all" footer shows a single
  composite invocation (e.g., a `for` loop reading the lines and counting
  exit codes). NO CI integration. NO pre-commit hook. NO Python wrapper
  script. NO `/scripts/` artifact. Re-sweep / future drift detection is
  "open the doc, paste the lines into Git Bash." Matches v1.1's no-new-tech-stack
  stance and the no-new-files bias — the doc IS the tool. (Pre-commit
  integration is deferred per REQUIREMENTS.md AUTO-02 backlog; CI
  integration depends on v2.0 PLAT-01 cross-platform support.)
- **D-18 (the 8 invariants):** Ship all 8 (exceeds the ≥5 floor; gives the
  next contributor a meaningful baseline rather than a token gesture):

  | # | Invariant | Bash one-liner | Validates |
  |---|---|---|---|
  | 1 | `PYTHONPYCACHEPREFIX` wired in `run.ps1` (Phase 4 CACHE-01) | `grep -q "PYTHONPYCACHEPREFIX" run.ps1` | The exact ROADMAP §SC-2 example. Catches the original v1.0 drift. |
  | 2 | `PYTHONPYCACHEPREFIX` wired in `teresa_gui.py` (Phase 4 D-13 defense-in-depth) | `grep -q "PYTHONPYCACHEPREFIX" teresa_gui.py` | Catches partial reverts that leave only the launcher side wired. |
  | 3 | `PYTEST_ADDOPTS` wired in `run.ps1` (Phase 4 D-08 cache_dir partner) | `grep -q "PYTEST_ADDOPTS" run.ps1` | Closes the latent `.pytest_cache` gap that PYTHONPYCACHEPREFIX alone doesn't cover. |
  | 4 | `clean.ps1` invoked by `run.ps1` (Phase 4 CACHE-03) | `grep -q "clean.ps1" run.ps1` | Catches `-NoClean` becoming default-on or the call being dropped. |
  | 5 | No `scripts/run_full.ps1` orphan refs in `*.toml` / `*.example` (Phase 5 ORPH-01/02) | `! grep -rqI "run_full" --include='*.toml' --include='*.example' --exclude-dir=.planning --exclude=CHANGELOG.md --exclude=LAUNCHER_README.md .` | Catches orphan references creeping back. Mirrors Phase 5 §SC-1 grep verbatim. |
  | 6 | `power_cord` intentionally unmapped in `dell_rules.yaml` (recovery commit `c3c7cb6`) | `grep -q "intentionally unmapped" spec_classifier/rules/dell_rules.yaml` | Catches the "fix" PRs that revert `c3c7cb6` and re-add `power_cord` to `device_type_map`. The single most repeatedly-broken business rule. |
  | 7 | Six vendors registered in `run.ps1` `$ALL_VENDORS` | `for v in dell cisco hpe lenovo huawei xfusion; do grep -q "\"$v\"" run.ps1 \|\| exit 1; done` | Catches vendor-list drift between `run.ps1`, `teresa_gui.py:VENDORS_ACTIVE`, and `main.py:VENDOR_REGISTRY`. |
  | 8 | Phase 6's own help block survives in `run.ps1` (Area B-2 self-protect) | `grep -q "\.SYNOPSIS" run.ps1` | Catches accidental removal of the D-05 deliverable, which would re-stale DRIFT-02 wording. |

- **D-19 (pre-validation status):** As of 2026-05-11 against the current
  tree, invariants #1–#7 already exit 0 (verified by the discuss-phase
  scout). Invariant #8 currently FAILs because the help block is itself a
  Phase 6 deliverable (D-05). The planner MUST order Phase 6's tasks so
  that the D-05 help-block task lands BEFORE the SC #4 verification gate
  runs (which requires every invariant to exit 0 against the post-phase
  tree).
- **D-20 (DOC_INVARIANTS.md format):** Standard Markdown. Recommended
  structure: H1 title; H2 §Purpose (one paragraph linking back to the v1.0
  retrospective); H2 §How to run; H2 §Invariants — one numbered subsection
  per invariant with a one-paragraph explanation, the one-liner in a
  fenced `bash` block, and a "Why this matters" line citing the recovery
  commit / requirement / phase that surfaced it. H2 §Adding new invariants
  with a 3-line "must exit 0; must be one-liner; must cite a real drift
  incident, not a hypothetical" rubric so contributors don't bloat the
  list.

### Cross-cutting

- **D-21 (commit granularity):** Each task in Phase 6's plan(s) produces
  one atomic commit subject `<type>(06): T<N> <description>` matching v1.1
  precedent. Doc-only edits use `docs(06)`; `run.ps1` help-block edit uses
  `chore(06)` since it's launcher comments not pipeline behavior.
  `DOC_INVARIANTS.md` creation uses `docs(06)`.
- **D-22 (audit log location):** Per-claim audit log lives at
  `.planning/phases/06-doc-vs-impl-drift-sweep/06-DRIFT-AUDIT.md` with the
  full `(file, line, claim_summary, check_command, resolution)` table.
  `06-SUMMARY.md` stays terse and references the audit log + tally
  ("N claims swept across 19 files (16 in-scope + 3 surgical map lines);
  M removed, P patched, 0 remaining drift"). Audit log becomes the 5th
  per-phase artifact sibling to PLAN / CONTEXT / VERIFICATION / SUMMARY.
- **D-23 (no new file under `scripts/` or `tools/`):** Phase 6 creates
  exactly two new files: `spec_classifier/docs/dev/DOC_INVARIANTS.md` and
  `.planning/phases/06-doc-vs-impl-drift-sweep/06-DRIFT-AUDIT.md`. No
  runner script, no sweep script, no helper library. The doc IS the tool
  (D-17). Mirrors Phase 5 D-10 stance ("no new sweep script").
- **D-24 (D-22 protection unchanged):** Phase 6 touches:
  - 13 `spec_classifier/docs/*.md` (sweep + 2 trims + 1 creation)
  - 3 root `*.md` (`README.md`, `CLAUDE.md`, `CONTRIBUTING.md`)
  - 2 `.planning/codebase/*.md` (3 surgical lines per D-02)
  - `run.ps1` (comments-only help block per D-05)
  - `.planning/phases/06-doc-vs-impl-drift-sweep/*` (planning artifacts)

  ZERO of these paths are inside D-22's protected set. `git diff --stat`
  for `spec_classifier/{src,rules,golden,tests,batch_audit.py,cluster_audit.py,main.py,conftest.py}`
  over the phase window MUST be empty.
- **D-25 (pytest skip-ratio gate):** `pytest -q` from `spec_classifier/`
  runs unchanged in Phase 6 verification. Phase 6 adds zero tests, removes
  zero tests, and changes no test-discoverable code. Skip ratio is
  structurally unchanged; gate is a sanity check, not a deliverable.
- **D-26 (goldens byte-equal):** `git diff --stat -- spec_classifier/golden/`
  over the phase window MUST be empty. Phase 6 doesn't touch golden fixtures.
- **D-27 (no new tech stack):** All invariants and sweep checks invoke only
  `grep`, `test`, standard shell utilities, plus (where needed) Python 3.10
  with the existing dep set (`openpyxl`, `pandas`, `pyyaml`, `pytest`).
  No new runtime dependencies. Matches ROADMAP §"No new tech-stack constraint".

### Claude's Discretion

- Exact placement of the new `<#...#>` help block in `run.ps1` (above-vs-below
  the existing RU header at lines 1-13). Both satisfy D-04 + D-06; below
  reads more naturally because the RU header already serves as a "what this
  script does" preamble.
- Exact wording of the trim pointers in `RUN_PATHS_AND_IO_LAYOUT.md` and
  `ONE_BUTTON_RUN.md` (D-09). Substantive constraint: line count strictly
  decreases per SC #3; surrounding prose may be paraphrased to match each
  file's existing voice.
- Exact phrasing of the 3 surgical-patch replacement sentences (D-02 / D-03).
  Substantive constraint: name both env vars, both entry points, and the
  `temp_root` source (Phase 5 D-05/D-06 vocabulary). Sentence shape may vary.
- Whether `DOC_INVARIANTS.md` invariants are listed in numbered subsections
  (D-20 recommendation) or in a single Markdown table. Both satisfy SC #2
  ("at least 5 mechanical invariants"). Subsections give more room for the
  "Why this matters" rationale; table is more compact.
- Commit subject prefix per task — `docs(06)` vs `chore(06)`. D-21 sets the
  default but borderline cases (e.g., the surgical map patches: docs?
  chore? infra?) are at planner discretion.
- Whether the "How to run them all" footer in `DOC_INVARIANTS.md` ships a
  copy-pasteable composite invocation (a `for` loop) or just instructs
  "run each line in sequence". Footer is a usability nicety, not a
  deliverable; both are acceptable.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Scope, requirements, gates
- `.planning/ROADMAP.md` § "Phase 6: Doc-vs-Impl Drift Sweep" — goal, success
  criteria 1-5, D-22 / pytest-skip / goldens-byte-equal gates verbatim;
  also the "No new tech-stack constraint" line that bounds D-16/D-27.
- `.planning/REQUIREMENTS.md` § "Doc-vs-Impl Drift Sweep (DRIFT) — Plan 3" —
  DRIFT-01..04 verbatim plus the DRIFT-03 justification paragraph
  ("tooling/meta-doc materializing the v1.1 retrospective lesson").
- `.planning/PROJECT.md` § "Current Milestone: v1.1" + § "Constraints" —
  milestone goal, no-tech-stack-additions, sequential phase dependency
  (Phase 4 → 5 → 6).
- `.planning/STATE.md` § "Decisions" — `[v1.1 Init]` lines locking
  helper-consolidation exclusion, sequential phase dependency, and the
  `DOC_INVARIANTS.md`-in-scope decision; `[Phase 5]` line for closing state.

### Cross-phase coordination
- `.planning/phases/04-cache-redirect/04-CONTEXT.md` § D-08, D-13 — Phase 4's
  full env-var wiring (PYTHONPYCACHEPREFIX + PYTEST_ADDOPTS in both `run.ps1`
  and `teresa_gui.py`). Source vocabulary for D-03 replacement wording AND
  for invariants #1-3.
- `.planning/phases/05-orphan-cleanup/05-CONTEXT.md` § D-02 — RU comment
  preservation precedent (informs D-06 coexist decision); § D-04 — ROADMAP
  realignment-as-documented-adjustment pattern (informs D-07); § D-22 — the
  unchanged-D-22 boilerplate Phase 6 inherits.
- `.planning/phases/05-orphan-cleanup/05-CONTEXT.md` <deferred> — explicit
  "STACK.md:79 + INTEGRATIONS.md:150 stale references … Reopen at Phase 6
  planning" hand-off note. Closed by Area A surgical-fix decision.

### Architectural guards (do NOT touch)
- `.planning/codebase/CONCERNS.md` § BLOCKER — `power_cord` taxonomy,
  Dell-specific parser, audit-reads-Excel, YAML rule order,
  `HW_TYPE_VOCAB` duplication. All load-bearing during Phase 6; phase
  touches none of them. Invariant #6 is built specifically to defend the
  `power_cord` rule.
- `.planning/codebase/CONCERNS.md` § IMPORTANT — `config.local.yaml` overlay
  duplication; informs the deferred `/gsd-map-codebase` refresh planning
  but not Phase 6 work itself.
- `CLAUDE.md` (root) § "Critical business rules" + § "Code-only repository
  policy" — D-22 protected paths verbatim.
- `spec_classifier/CLAUDE.md` § "Business Rules" + § "Known Tech Debt" — deep
  reference for the same exclusions. NOTE: `spec_classifier/CLAUDE.md`
  itself is OUT of scope for the Phase 6 sweep (per ROADMAP enumeration);
  it is read as a reference, not edited.

### In-scope files Phase 6 will sweep (16)
**Root (3):**
- `README.md`
- `CLAUDE.md`
- `CONTRIBUTING.md`

**`spec_classifier/docs/` (13):**
- `spec_classifier/docs/DOCS_INDEX.md`
- `spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md`
- `spec_classifier/docs/dev/ONE_BUTTON_RUN.md` (also DRIFT-02 trim target)
- `spec_classifier/docs/dev/OPERATIONAL_NOTES.md`
- `spec_classifier/docs/dev/TESTING_GUIDE.md`
- `spec_classifier/docs/product/TECHNICAL_OVERVIEW.md`
- `spec_classifier/docs/rules/RULES_AUTHORING_GUIDE.md`
- `spec_classifier/docs/schemas/DATA_CONTRACTS.md`
- `spec_classifier/docs/taxonomy/cycle2_summary.md`
- `spec_classifier/docs/taxonomy/hw_type_taxonomy.md`
- `spec_classifier/docs/user/CLI_CONFIG_REFERENCE.md`
- `spec_classifier/docs/user/RUN_PATHS_AND_IO_LAYOUT.md` (also DRIFT-02 trim target)
- `spec_classifier/docs/user/USER_GUIDE.md`

### In-scope surgical-patch files (Area A)
- `.planning/codebase/STACK.md` — line 79 only (D-02).
- `.planning/codebase/INTEGRATIONS.md` — lines 55 + 150 only (D-02).

### In-scope launcher edit (Area B)
- `run.ps1` — add `<#.SYNOPSIS#>` block per D-05; RU header at lines 1-13
  untouched per D-06.

### File Phase 6 will create
- `spec_classifier/docs/dev/DOC_INVARIANTS.md` — per D-15..D-20 (8 invariants).
- `.planning/phases/06-doc-vs-impl-drift-sweep/06-DRIFT-AUDIT.md` — per D-22.

### Files Phase 6 reads but does NOT edit
- `spec_classifier/CLAUDE.md` — out of scope per ROADMAP enumeration.
  Read as reference for `power_cord` invariant (#6) and Business Rules
  context. Drift in this file is deferred to `/gsd-map-codebase` refresh.
- `spec_classifier/README.md` — same status.
- `spec_classifier/CHANGELOG.md` — exempt under D-18 historical-content
  convention.
- `LAUNCHER_README.md` — line 4 historical "replaces three legacy scripts"
  preserved per Phase 5 D-18; out of in-scope sweep file list.
- `run.ps1:1-13` (RU header) — exempt under Phase 5 D-02; D-06 reaffirms.
- `run.ps1:33-94` (param parsing, env-var setting, header banner) — read
  to confirm Phase 4 wiring for invariants #1-4; not edited.
- `teresa_gui.py:_main_` env-var block (Phase 4 D-13) — read to confirm
  for invariant #2; not edited.
- `spec_classifier/scripts/clean.ps1` — read to confirm Phase 4 CACHE-03
  call site; not edited.
- `spec_classifier/rules/dell_rules.yaml:278` — read to confirm `intentionally
  unmapped` comment for invariant #6; not edited (D-22 protected anyway).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **Phase 5 D-05/D-06 replacement vocabulary** — "PYTHONPYCACHEPREFIX +
  PYTEST_ADDOPTS env vars … set by `run.ps1` and `teresa_gui.py` from
  `config.local.yaml::temp_root`". Reused verbatim in D-03 surgical patches
  for vocabulary consistency across the milestone.
- **`run.ps1:1-13` existing RU comment header** — lists the 6 canonical CLI
  invocations. Mined as the source content for the D-05 English help-block
  examples (translation + restructure into `.EXAMPLE` blocks; no semantic
  change).
- **ROADMAP §SC-2 example** — `grep -q "PYTHONPYCACHEPREFIX" run.ps1` exit 0.
  Used verbatim as DOC_INVARIANTS.md invariant #1; sets the Bash-one-liner
  pattern (D-16) for the rest.
- **Phase 5 §SC-1 grep spec** — `grep -rn "run_full" . --include='*.toml'
  --include='*.example' --exclude-dir=.planning --exclude=CHANGELOG.md
  --exclude=LAUNCHER_README.md`. Reused verbatim (with `-q`) as invariant
  #5; exact pattern reuse means a future drift in #5 trips the same
  contract Phase 5 SC-1 enforced.
- **Atomic per-task commit convention** — `chore(NN): T<M> <description>` /
  `docs(NN): T<M> <description>`. Established v1.0–Phase 5; D-21 follows.
- **Per-phase artifact tree** — PLAN, CONTEXT, VERIFICATION, SUMMARY,
  DISCUSSION-LOG (and now DRIFT-AUDIT). Adding the audit log as a sibling
  matches the existing convention; no new artifact-tree shape introduced.

### Established Patterns
- **D-22 protected paths** — load-bearing for every v1.1 phase. Phase 6
  touches zero D-22 paths; the gate is a passive guard, not a hurdle.
- **First-match-wins YAML rule order** — irrelevant to Phase 6 (no rules
  edits) but reaffirmed by D-22 protection.
- **Defense-in-depth env-var setting** (Phase 4 D-13) — the wording in D-03
  must reflect that BOTH `run.ps1` AND `teresa_gui.py` set the env vars.
  Single-source language ("`run.ps1` sets …") is a regression. Invariants
  #1 and #2 explicitly enforce both sides.
- **Documented-adjustment pattern** (Phase 5 D-04) — when ROADMAP wording
  is found false at phase start, the realignment is captured as a
  CONTEXT.md decision (Phase 5: D-04 for §SC-1; Phase 6: D-07 for DRIFT-02).
  ROADMAP itself is NOT edited unless the wording is broken in a way that
  affects the verification gate's pass/fail. DRIFT-02 wording is borderline
  — the help block makes it true post-phase, so no ROADMAP edit needed.
- **Historical-content convention (D-18)** — RU comment in `run.ps1:1-13`,
  `LAUNCHER_README.md:4` "replaces three legacy scripts", `CHANGELOG.md`
  entries. All preserved. D-06 reaffirms for the RU header specifically.

### Integration Points
- **Phase 6 → no downstream phase** — v1.1 closes after Phase 6. The
  deferred broader `/gsd-map-codebase` refresh and the
  `spec_classifier/CLAUDE.md`/`README.md` drift cleanup roll into v1.2
  scope (per the deferred items list).
- **DOC_INVARIANTS.md → future contributors** — the invariants doc is the
  Phase 6 deliverable that has the longest half-life. Its content is the
  v1.1 retrospective lesson made executable. Treat each invariant as a
  contract a future PR has to consciously break to drift the codebase.
- **Help block on `run.ps1` → `Get-Help` / `-?` reader path** — once the
  D-05 task lands, two reader paths exist for "what does run.ps1 do":
  (a) ONE_BUTTON_RUN.md (canonical doc), (b) `.\run.ps1 -?` (in-shell).
  Both must stay in sync; ONE_BUTTON_RUN.md is the source of truth and
  the help block paraphrases it. If they ever diverge, prefer
  ONE_BUTTON_RUN.md.

</code_context>

<specifics>
## Specific Ideas

- **Mirror ROADMAP §SC-2 example as invariant #1 verbatim** — the phrase
  `grep -q "PYTHONPYCACHEPREFIX" run.ps1` is the literal example given in
  the success-criterion. Using it as #1 means the SC #4 self-check ("each
  check executes successfully against the post-phase tree") trivially
  passes for the canonical example.
- **Mirror Phase 5 §SC-1 grep as invariant #5** — same pattern that gates
  Phase 5 should gate Phase 6+. Re-use prevents grep-spec drift between
  the two phases' verification semantics.
- **Audit log table columns:** `(file, line, claim_summary,
  check_command, resolution)`. `resolution` ∈ `{remove, patch, no_drift}`.
  `no_drift` rows are still recorded so the audit log is a complete
  inventory of every claim considered, not just the changed ones — supports
  the SC #5 "every claim flagged" wording.
- **Help block placement** — recommend BELOW the existing RU header (i.e.,
  at lines 14-30 ish, before the `param()` block). The RU header is a
  human-readable preamble; the `<#...#>` block is parser-readable.
  Convention is `<#...#>` immediately before `param()`.
- **DOC_INVARIANTS.md "Adding new invariants" rubric** (D-20):
  ```
  - Must exit 0 against the current tree (run it first)
  - Must be a Bash one-liner (no scripts, no helpers)
  - Must cite a real drift incident: which commit / phase / requirement
    surfaced the underlying claim. Hypotheticals don't earn an entry.
  ```
  Last bullet specifically blocks the "let's add 30 nice-to-have invariants"
  bloat path.
- **Trim baselines for SC #3 verification:**
  - `RUN_PATHS_AND_IO_LAYOUT.md` pre-phase = **281 lines**
  - `ONE_BUTTON_RUN.md` pre-phase = **54 lines**
  Both must STRICTLY decrease (`wc -l` post-phase < pre-phase). Recorded
  here so the planner can build the SC #3 verification step against fixed
  numbers, not against re-discovery.

</specifics>

<deferred>
## Deferred Ideas

- **Broader `/gsd-map-codebase` refresh of all 7 `.planning/codebase/` maps**
  — Area A defers everything beyond the 3 surgical lines. Folds in the
  Area C deferred volatile-counts work (test counts, LOC counts, rule_id
  counts). Right tool: `/gsd-map-codebase` re-scan. Right milestone: v1.2
  (per-vendor knowledge base) since v1.2 is already a doc-creation milestone
  where map refresh fits naturally. If v1.2 doesn't pick it up, falls
  through to a standalone `/gsd-map-codebase` invocation.
- **`spec_classifier/CLAUDE.md` drift sweep** — the file has the deepest
  accumulation of drift-prone claims in the repo (LOC counts, rule_id
  counts, line numbers, "Last commit" header, "Last run" header) but is
  explicitly NOT in the ROADMAP-enumerated 16-file scope. Defer to v1.2 +
  `/gsd-map-codebase` refresh.
- **`spec_classifier/README.md` drift sweep** — same status. Phase 2
  (v1.0 DOC-02) was the last touch; not re-audited in Phase 6 by ROADMAP
  scope decision.
- **Translation of `run.ps1:1-13` Russian header to English** — Phase 5
  D-02 + Phase 6 D-06 both exempt it under D-18 historical-content
  convention. If a future hygiene milestone converts all in-tree comments
  to English, this is one. Coexists with the new EN help block per D-06.
- **Pre-commit hook integration of DOC_INVARIANTS.md checks** — D-17
  rules out for v1.1 (no-tooling-additions stance; AUTO-02 backlog
  defers pre-commit). Reopen at v2.0 alongside AUTO-02.
- **CI integration of DOC_INVARIANTS.md checks** — D-17 rules out;
  depends on v2.0 PLAT-01 cross-platform support.
- **Sweep runner script (`sweep-invariants.sh` / `.ps1`) under
  `spec_classifier/scripts/`** — D-23 rules out; explicitly rejected
  in favor of doc-of-record + manual run (D-17). The doc IS the tool.
  Reopen only if v2.0 CI demands a programmatic entry point.
- **pytest test wrapping the invariants
  (`tests/test_doc_invariants.py`)** — D-22 protects `tests/`; would
  require a D-22 carve-out. v1.1 doesn't grant one. Reopen at v2.x
  alongside the broader test-infrastructure work.
- **DOCS_INDEX.md auto-generation from filesystem** — interesting drift
  surface (DOCS_INDEX claims a 1:1 map with `docs/`; out-of-sync would
  be invisible without an explicit check). Captured as a candidate for
  invariant #9 in a future iteration; not in the Phase 6 8-slate
  because adding/removing docs is rare and DOCS_INDEX is short enough
  to eyeball. If `/gsd-map-codebase` v1.2 refresh wants it, fold there.
- **Renaming `_run_full` method in `teresa_gui.py:294,489`** — Phase 5
  D-03 false-positive; Phase 6 inherits. Out of cleanup scope.
- **Adding DRIFT-05 (or similar) for the surgical map patches /
  help block / audit log split** — explicitly NOT done. The Area A
  surgical patches, Area B help block, and Area C audit-log split are
  documented adjustments captured here in CONTEXT.md (mirrors Phase 5
  D-04 stance: not new requirements, not a traceability matrix update).
- **Volatile-count claims in IN-scope files** — D-12 defers all of these.
  If any IN-scope file (e.g., `TESTING_GUIDE.md`) has a "420 tests"
  claim, it's removed during the sweep (remove > patch heuristic), NOT
  patched to a current count. The rationale belongs in the audit log's
  `resolution` column.

### Reviewed Todos (not folded)
None — no `gsd-sdk query todo.match-phase 6` matches expected
(milestone is doc-only cleanup; no feature todos). Confirmed by the
discuss-phase scout.

</deferred>

---

*Phase: 6-doc-vs-impl-drift-sweep*
*Context gathered: 2026-05-11*
