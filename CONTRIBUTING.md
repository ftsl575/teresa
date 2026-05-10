# Contributing to teresa

teresa is a deterministic, rule-based Excel-spec classifier for six hardware
vendors (Dell, Cisco CCW, HPE, Lenovo DCSC, xFusion, Huawei). The repo is two
things stacked: a thin Windows launcher at the root (`run.ps1`, `teresa_gui.py`,
`teresa.bat`) and the actual codebase under `spec_classifier/`. See the
[root README](README.md) for installation and a runnable Quick Start.

This document covers the development cycle, how to run tests, how to add a
vendor, the PR workflow, code style, and the project's "do not fix" tech-debt
rules. It is tool-agnostic — use Claude Code or any AI coding agent that runs
the GSD (Get Shit Done) commands documented below. Windows-only this milestone;
cross-platform support is on the v2 backlog.

## Development cycle

The project uses the GSD-native cycle. Each phase moves through four commands
in order:

1. **Discuss** — `/gsd-discuss-phase <N>`. Clarifies HOW to implement what's in
   `.planning/ROADMAP.md` for phase N. Produces `NN-CONTEXT.md`.
2. **Plan** — `/gsd-plan-phase <N>`. Produces `NN-PP-PLAN.md` task lists with
   verification gates derived from the phase's success criteria.
3. **Execute** — `/gsd-execute-phase <N>`. Runs the plans in dependency order,
   producing atomic commits (one per task) and `NN-PP-SUMMARY.md` per plan.
4. **Verify** — `/gsd-verify-work <N>`. Confirms goal achievement against
   ROADMAP success criteria; produces `NN-VERIFICATION.md` and the gate verdict.

Run `/gsd-help` for the full command list (audit, code review, doc updates,
progress checks).

Phase artifacts live under `.planning/phases/NN-<name>/`. Planning artifacts
that survive across phases (`PROJECT.md`, `REQUIREMENTS.md`, `ROADMAP.md`,
`STATE.md`, `codebase/*.md`) live at `.planning/`.

The cycle is intentionally linear and one-way per phase: Discuss outputs feed
Plan, Plan outputs feed Execute, Execute outputs feed Verify. If a verify gate
trips, the recovery is a follow-up plan in a new phase, not an in-place rewrite
of the failed plan — that keeps the planning history honest and the per-phase
artifacts immutable. Skip a step only if the phase has no work to do for it
(e.g., a pure-docs phase may not need separate Discuss output).

## Tests

Run pytest from `spec_classifier/` (the test config and the session-finish hook
both live in `spec_classifier/conftest.py`):

```powershell
cd spec_classifier
pytest tests/ -v --tb=short                            # full suite
pytest tests/test_lenovo_rules_unit.py -v              # single file
pytest -k "lenovo and parser" -v                       # by keyword expression
```

The launcher wraps pytest:

```powershell
.\run.ps1 -TestsOnly                   # short-circuit, only pytest
.\run.ps1 -SkipTests                   # full pipeline run, skip pytest at end
```

**Skip-ratio gate.** `spec_classifier/conftest.py:pytest_sessionfinish` forces
session FAIL if `skipped/total > 0.50` or if `passed == 0` or if `input_root`
is missing entirely (`MAX_SKIP_RATIO = 0.50`). A clean clone with no INPUT data
will trip this — populate `%USERPROFILE%\Desktop\INPUT\<vendor>\` with at least
one `.xlsx` per vendor before running the suite, or expect the gate to flag a
"skip guard triggered" message even though all active tests pass.

**Goldens.** `spec_classifier/golden/*_expected.jsonl` is the regression
contract — any rule edit MUST update the affected golden via
`python main.py --vendor <v> --update-golden` before the regression test will
pass. See [`spec_classifier/docs/dev/TESTING_GUIDE.md`](spec_classifier/docs/dev/TESTING_GUIDE.md)
for the golden workflow.

## Adding a vendor

See [`spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md`](spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md)
for the full adapter contract, parser/normalizer scaffold, golden workflow, and
per-vendor sheet conventions. This file does not duplicate that content —
NEW_VENDOR_GUIDE.md is the canonical doc; updates land there.

What to expect: a new vendor adds a `src/vendors/<v>/{adapter.py, parser.py,
normalizer.py}` triplet, a `rules/<v>_rules.yaml` rule file, registers
`"<v>"` in `$ALL_VENDORS` in `run.ps1`, moves `"<v>"` from `VENDORS_DISABLED`
to `VENDORS_ACTIVE` in `teresa_gui.py`, and ships at least one golden
(`golden/<v>1_expected.jsonl`) before merge.

## PR workflow

**Commit messages.** Follow the existing `<type>(<phase>-<plan>): <subject>`
pattern from `git log`:

```
docs(02-01): translate spec_classifier/CLAUDE.md to English + dedup root CLAUDE.md
chore(03-01): retire spec_classifier/prompts/ to archive + repoint LAUNCHER_README
fix(02-04): tighten paragraph X (DOC-02)
```

Common types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`. Reference the
requirement ID (`HYG-01`, `DOC-04`, `WF-02`) in the subject when relevant.

**One commit per task.** Each `<task>` block in a PLAN.md should produce one
commit (or one rename + one commit if a `git mv` precedes content changes). A
failed task is recovered by a NEW follow-up commit, not `git commit --amend`.

**One requirement per phase-closing commit.** Phase wrap-up commits group
artifacts by requirement (one commit per `HYG-NN` / `DOC-NN` / `WF-NN`) so any
individual requirement is atomically revertable.

There is no PR template file in the repo today; the convention is described
here, not auto-injected. The PR description should reference the phase SUMMARY
(`.planning/phases/NN-<name>/NN-SUMMARY.md`) for context.

**Atomic revertability.** Because each task and each requirement lands as its
own commit, `git revert <hash>` cleanly undoes any single change without
unwinding unrelated work in the same phase. This is the same property the
phase verification gates rely on — a failed gate can pinpoint and revert the
specific commit that caused regression.

## Code style

PEP 8, 4-space indent, docstrings for public functions and modules. Match the
style of the surrounding file when in doubt. Do not introduce new conventions
in a hygiene or docs phase. Project-specific rule-authoring style lives in
[`spec_classifier/docs/rules/RULES_AUTHORING_GUIDE.md`](spec_classifier/docs/rules/RULES_AUTHORING_GUIDE.md);
follow it for any YAML rule edit.

## Do not fix

The five items below are load-bearing on purpose. Each has a recovery commit
or an explicit Project decision behind it; "fixing" any of them as part of an
unrelated PR has caused real regressions. Treat them as constraints, not
technical debt to be paid down.

1. **`power_cord` has `hw_type=None` intentionally.** Recovery commit `c3c7cb6 fix(taxonomy): restore power_cord hw_type=None` exists. Do NOT add it to `device_type_map` or remove it from `_E8_NO_HW_TYPE_DEVICES`.
2. **`spec_classifier/src/core/parser.py` is Dell-specific despite living in `core/`.** Sentinel `"Module Name"` is hard-coded; other vendors use their own `parser.py` under `src/vendors/<v>/`. Standalone refactor only — out of scope of any unrelated PR.
3. **`spec_classifier/batch_audit.py` reads from `*_annotated.xlsx` instead of `classification.jsonl`.** Excel leakage; Project CLAUDE.md explicitly says do not "fix" as part of unrelated work — needs dedicated migration.
4. **YAML rule order is load-bearing (first-match-wins).** Never `sort` rule blocks alphabetically. Cosmetic reorders silently flip classification.
5. **`HW_TYPE_VOCAB` is duplicated between `classifier.py` and `batch_audit.py`.** Tracked in CONCERNS.md but not selected for cleanup milestones.

> Full rationale and context: [.planning/codebase/CONCERNS.md](.planning/codebase/CONCERNS.md) § BLOCKER + IMPORTANT.

## Where to look first

| Question | Authoritative file |
|---|---|
| Pipeline stages, E-codes, alias-table semantics | [`spec_classifier/CLAUDE.md`](spec_classifier/CLAUDE.md) (deep reference) |
| The 5 critical business rules at a glance | [`CLAUDE.md`](CLAUDE.md) (root pointer) |
| Run a vendor end-to-end on Windows | [`run.ps1`](run.ps1), [`LAUNCHER_README.md`](LAUNCHER_README.md) |
| Vendor adapter contract | [`spec_classifier/src/vendors/base.py`](spec_classifier/src/vendors/base.py) |
| Add a new vendor | [`spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md`](spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md) |
| Rules authoring | [`spec_classifier/docs/rules/RULES_AUTHORING_GUIDE.md`](spec_classifier/docs/rules/RULES_AUTHORING_GUIDE.md), [`spec_classifier/docs/taxonomy/hw_type_taxonomy.md`](spec_classifier/docs/taxonomy/hw_type_taxonomy.md) |
| Recent changes | [`spec_classifier/CHANGELOG.md`](spec_classifier/CHANGELOG.md) |
| Project status / current focus | [`.planning/STATE.md`](.planning/STATE.md) |
| Tech-debt items NOT to fix | [`.planning/codebase/CONCERNS.md`](.planning/codebase/CONCERNS.md) (BLOCKER + IMPORTANT sections) |
