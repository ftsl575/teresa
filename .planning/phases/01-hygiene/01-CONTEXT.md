# Phase 1: Hygiene - Context

**Gathered:** 2026-05-10
**Status:** Ready for planning

<domain>
## Phase Boundary

Scrub committed username leakage from tracked files, consolidate the dual `.gitignore` into a single root file, and remove dead/orphan files. No behavior change to the classifier, audits, or rules. All 40 golden regression fixtures must pass byte-for-byte; pytest skip-ratio gate (`skipped/total > 0.50`) must not trip.

Three requirements: HYG-01 (username scrub), HYG-02 (gitignore consolidation), HYG-03 (orphan removal).

</domain>

<decisions>
## Implementation Decisions

### Placeholder Convention (HYG-01)

- **D-01:** Per-context placeholder scheme — each consumer gets the syntax it can actually execute or read cleanly:
  - PowerShell (`run.ps1`, `*.ps1`): `$env:USERPROFILE`
  - Batch (`teresa.bat`, `*.bat`): `%USERPROFILE%`
  - Python (`spec_classifier/batch_audit.py`, runtime defaults): `Path.home() / "Desktop" / "INPUT"` style — match the existing pattern in `spec_classifier/teresa_gui.py:408`
  - Makefile (`spec_classifier/Makefile`): `$(HOME)` with forward slashes (Git Bash / GNU Make context)
  - Markdown docs (READMEs, CLAUDE.md, docs/**/*.md): `<USERNAME>` token — readable to humans
  - YAML example (`spec_classifier/config.local.yaml.example`): `<USERNAME>` token

- **D-02:** Where a path was being given as a *concrete example* (not a runtime default), preserve the example shape — replace only the username segment. E.g. `C:\Users\G\Desktop\INPUT\dell\dl1.xlsx` becomes `C:\Users\<USERNAME>\Desktop\INPUT\dell\dl1.xlsx` in markdown, not `<INPUT_ROOT>/dl1.xlsx`. The user's repo state knows nothing about `<INPUT_ROOT>`-style abstractions outside `config.local.yaml`.

### Scope Boundary (HYG-01)

- **D-03:** `.planning/` files are out of scope for HYG-01. They describe the discovered problem (CONCERNS.md, codebase map docs) and the planning artifacts; rewriting them would make the discovery docs lie about what was found. Roughly 7 `.planning/*.md` files contain `C:\Users\G\` references — left as-is.

- **D-04:** `C:\venv\` references stay literal in docs. The path is a documented suggestion (per `spec_classifier/CLAUDE.md` and `spec_classifier/README.md:21`), not a hard requirement. Where the docs say "Current venv location: `C:\venv`", keep that line but ensure surrounding text frames it as the user's chosen default that can be overridden via `config.local.yaml` — do not invent a new `<VENV_DIR>` placeholder.

- **D-05:** Effective HYG-01 scope is the ~22 files outside `.planning/` from the grep at discussion time. Concrete enumeration:
  - Code: `run.ps1`, `spec_classifier/batch_audit.py`, `spec_classifier/Makefile`
  - Config example: `spec_classifier/config.local.yaml.example`
  - Markdown: root README, `spec_classifier/README.md`, `spec_classifier/CHANGELOG.md`, `spec_classifier/CURRENT_STATE.md`, `spec_classifier/CLAUDE.md`, `spec_classifier/prompts/COWORK_OPUS_FULL_AUDIT.md`, and the `spec_classifier/docs/{dev,user,product,rules,taxonomy}/*.md` files that match the grep
  - The planner should re-run the grep against the working tree at plan time to build the authoritative list, since other phases / commits may shift the count.

### Gitignore Consolidation (HYG-02)

- **D-06:** Consolidate to a single root `.gitignore`. The redundant `spec_classifier/.gitignore` is deleted. Path-relative entries in `spec_classifier/.gitignore` (if any reference paths interpreted relative to that file) are rewritten to be unambiguous from repo root before the move.
- **D-07:** Coverage that must remain intact after consolidation: `.venv/`, `OUTPUT/`, `output/`, `test_data/`, `commits.txt`, `*.zip`, `.cursor/`, `.claude/` (already in root `.gitignore`), plus anything currently only in `spec_classifier/.gitignore` that the planner finds during the merge. The merged `.gitignore` is committed as part of HYG-02.

### Orphan-File Threshold (HYG-03)

- **D-08:** Conservative deletion policy:
  - Definite delete: `commits.txt` (already gitignored, untracked, leftover artifact); any `*.bak`, `*.tmp`, or `*.zip` files that turn out to be tracked.
  - Investigate then decide: `spec_classifier/scripts/verify_teresa_audit_actionables.py` — `git log` it, grep for references in `run.ps1`, `Makefile`, `*.md`, `tests/`. Delete only if zero references found AND no recent commit history suggests it's pending work; otherwise leave with a tracking note.
  - Do not delete: anything under `spec_classifier/prompts/00..08` + `COWORK_OPUS_FULL_AUDIT.md` — Phase 3 (WF-01) owns those.
  - Do not delete: anything in `spec_classifier/golden/`, `spec_classifier/rules/`, `spec_classifier/tests/`, `spec_classifier/src/` — load-bearing.

- **D-09:** The planner runs a one-pass orphan grep at plan time:
  - For each `spec_classifier/src/**/*.py`, check whether its module path appears in any import statement repo-wide.
  - For each top-level script in `spec_classifier/`, check whether it's invoked from `run.ps1`, `Makefile`, `tests/`, or `teresa_gui.py`.
  - Surface candidates in the plan; do not delete unconfirmed orphans without explicit decision.

- **D-10:** The list of removed files is captured in the phase verification output (so the eventual PR description has it).

### Verification Gate (Full + Diff Review)

- **D-11:** Phase 1 is "done" when ALL of these are TRUE — verifier runs them in order:
  1. `git grep -n 'C:\\Users\\G\\'` against tracked files returns zero results. Variants checked: `C:\Users\G\`, `C:/Users/G/`, `C:\\Users\\G\\` (escaped). Negative-control: `git grep -n '<USERNAME>'` against the same tree should return non-zero (at least the placeholders we just wrote).
  2. Exactly one `.gitignore` exists in the working tree at repo root. `git ls-files | grep -c '^\\.gitignore$'` returns 1; `git ls-files | grep -c 'spec_classifier/\\.gitignore'` returns 0.
  3. `pytest tests/ -v --tb=short` from `spec_classifier/` exits 0. The `conftest.py:pytest_sessionfinish` skip-ratio gate must not be tripped — `passed > 0` and `skipped/total <= 0.50`.
  4. Smoke run: `.\run.ps1 -Vendor huawei -NoAi -SkipTests` from repo root completes without error and produces a fresh `OUTPUT/huawei_run/run-...` folder.
  5. Diff review checkpoint: `git diff --stat` is presented to the user before the final commit; user confirms no surprise files were touched.

- **D-12:** Goldens-byte-equality is implicitly asserted by step 3 (regression tests fail fast if any `golden/*_expected.jsonl` mismatches the rerun). No separate manual hash check needed.

### Claude's Discretion

- Specific commit grouping inside Phase 1 (one commit per requirement vs. one fat hygiene commit) is a planning concern — leave to the planner. My recommendation: one commit per requirement (HYG-01, HYG-02, HYG-03 each its own commit) for atomic revert-ability, but defer to whatever GSD config dictates.
- Exact regex used in step (1) of the verification gate is the verifier's call; the listed variants are the floor, not the ceiling.
- If the planner's orphan grep surfaces unexpected candidates beyond `verify_teresa_audit_actionables.py`, surface them in the plan and ask before deleting.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project policy and "do not fix" rules

- `.planning/PROJECT.md` — milestone scope, "Done" definition, Out of Scope list, Key Decisions (especially "Strip `C:\Users\G\` username only; do not de-Windowize launchers")
- `.planning/REQUIREMENTS.md` §Hygiene — HYG-01, HYG-02, HYG-03 in their authoritative phrasing
- `.planning/codebase/CONCERNS.md` §BLOCKER and §IMPORTANT — the load-bearing tech debt that this phase MUST NOT touch (`power_cord` `hw_type=None`, `core/parser.py` Dell-specificity, `batch_audit.py` Excel-reading, YAML rule order, `HW_TYPE_VOCAB` duplication)

### Codebase map (where things live)

- `.planning/codebase/STRUCTURE.md` — full directory layout, name conventions, where to put / not put things
- `.planning/codebase/STACK.md` — language/runtime/dep matrix; informs which file types need which placeholder syntax
- `.planning/codebase/CONVENTIONS.md` — current code style, including the `Path.home() / "Desktop" / "INPUT"` pattern in `teresa_gui.py:408` that HYG-01 follows for Python defaults
- `.planning/codebase/TESTING.md` — pytest invocation, `conftest.py:pytest_sessionfinish` skip-ratio gate (`MAX_SKIP_RATIO = 0.50`), regression-test expectations against `spec_classifier/golden/*_expected.jsonl`

### Project-level conventions

- `spec_classifier/CLAUDE.md` — deep reference; treat as read-only this phase; documents the "do not fix" rules and the `power_cord` taxonomy decision
- `CLAUDE.md` (root) — currently the thin pointer; do not edit content this phase (DOC-04 in Phase 2 owns the dedup)

### Discussion source-of-truth

- `.planning/phases/01-hygiene/01-DISCUSSION-LOG.md` — full Q&A trace for this phase (audit / retrospective; not consumed by downstream agents)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `spec_classifier/teresa_gui.py:408` — already uses `Path.home() / "Desktop" / "INPUT"` for the Python runtime default. HYG-01's Python placeholder choice (`Path.home()` style) mirrors this existing pattern verbatim, so the change is consistent with the codebase, not a new convention.
- `spec_classifier/main.py:_load_config` (lines 69–86) — config overlay logic reads `config.local.yaml.example` users see at first run. Replacing the username in the example file is a doc fix; the loader itself touches nothing in this phase.
- `run.ps1` already uses `$env:USERPROFILE` for default INPUT/OUTPUT roots in some places — HYG-01 normalizes the rest to that convention.

### Established Patterns

- **Code-only repo policy** (root + `spec_classifier/CLAUDE.md`): INPUT, OUTPUT, fixtures, `.venv/` live outside the repo. HYG-01 + HYG-03 reinforce this by removing committed leakage.
- **Config layering** (`config.yaml` overlaid by `config.local.yaml`, gitignored): `config.local.yaml.example` is the only template the user touches. Username in the example file is purely illustrative; replacing with `<USERNAME>` does not affect the loader.
- **Single-process, single-threaded pipeline**: no concurrency/atomicity concerns for cleanup. Simple sequential edits are safe.

### Integration Points

- After HYG-02 (single root `.gitignore`), DOC-03 (Phase 2, `docs/` audit) and DOC-04 (CLAUDE.md dedup) inherit a cleaner baseline — easier to audit drift when there's only one ignore file.
- After HYG-03 cleanup, the planner for Phase 3 (WF-01) has a clearer view of what's actually in `spec_classifier/prompts/` since orphan noise has been cleared.
- Smoke-run dependency: huawei vendor needs `INPUT/huawei/` files locally. The user has them; document this gating in the verification step so a fresh contributor isn't blocked. (Note: cross-platform / fresh-clone runnability is explicitly OUT of scope this milestone — PLAT-01 in v2.)

</code_context>

<specifics>
## Specific Ideas

- The user explicitly chose `Per-context` over `Uniform <USERNAME>` because uniform breaks runnable examples. This is a *correctness* choice, not aesthetic.
- The user explicitly added the `Diff review` to the verification gate — they want to see `git diff --stat` before the final commit lands. This is a process choice: the user wants a "no surprises" eyeball pass even under YOLO mode.
- Conservative orphan policy is preferred — the user does NOT want the planner deleting modules just because the grep can't find imports. Investigation required for any non-obvious orphan.

</specifics>

<deferred>
## Deferred Ideas

- **Cross-platform launcher (`run.sh`, POSIX GUI dispatch)** — explicitly out of scope per PROJECT.md; tracked as `PLAT-01` and `PLAT-02` in REQUIREMENTS.md v2 backlog.
- **CI pipeline** — depends on cross-platform support; tracked as `AUTO-01` in v2.
- **`<INPUT_ROOT>` / `<OUTPUT_ROOT>` token placeholders in markdown** — considered during placeholder discussion, rejected for this phase. Could be revisited in DOC-01/DOC-02 (Phase 2) if README readability suffers, but not part of HYG-01.
- **AST-level orphan detection** — the user picked Conservative over Aggressive. Aggressive grep-and-prune (full import graph analysis) is a future cleanup, not this phase.
- **Renaming `_E8_NO_HW_TYPE_DEVICES` / `DEVICE_TYPE_ALIASES` for clarity** (mentioned in CONCERNS.md) — explicitly out of scope; needs dedicated migration with golden re-verification.

</deferred>

---

*Phase: 1-Hygiene*
*Context gathered: 2026-05-10*
