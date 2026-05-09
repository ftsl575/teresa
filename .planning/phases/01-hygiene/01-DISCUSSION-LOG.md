# Phase 1: Hygiene - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-10
**Phase:** 1-hygiene
**Areas discussed:** Placeholder convention, Scope boundary, Orphan-file definition, Verification gate

---

## Gray Area Selection

User was presented with 4 candidate gray areas; option was to multi-select which warranted discussion (unselected items would default to Claude's recommendation).

| Area | Description | Selected |
|------|-------------|----------|
| Placeholder convention | What literal string replaces `C:\Users\G\`? | ✓ |
| Scope boundary | Does HYG-01 touch `.planning/` and `C:\venv\`? | ✓ |
| Orphan-file definition | Threshold for HYG-03 deletion | ✓ |
| Verification gate | What proves Phase 1 done? | ✓ |

**User's choice:** All four — wanted explicit decisions on every gray area.

---

## Placeholder Convention

| Option | Description | Selected |
|--------|-------------|----------|
| Per-context (Recommended) | PowerShell → `$env:USERPROFILE`; Batch → `%USERPROFILE%`; Python/Makefile → `Path.home()` / forward-slash `$HOME`; Markdown → `<USERNAME>`; YAML example → `<USERNAME>`. Code stays runnable; docs stay readable. | ✓ |
| Uniform `<USERNAME>` | Single placeholder everywhere. Easier visually; breaks runnable examples. | |
| Windows-native everywhere | `%USERPROFILE%` in shells/configs, comment in markdown. Less reader-friendly in pure docs. | |

**User's choice:** Per-context.
**Notes:** User picked correctness over visual uniformity — a runnable example must execute as written. The Python `Path.home()` choice mirrors the existing pattern in `spec_classifier/teresa_gui.py:408`, so this isn't a new convention; it's reinforcing one already present in the codebase.

---

## Scope Boundary

| Option | Description | Selected |
|--------|-------------|----------|
| Skip `.planning/`, keep `C:\venv` (Recommended) | Leave `.planning/` files untouched (descriptive of the discovered problem). Keep `C:\venv\` literal in docs but frame as suggestion. ~22 files in scope. | ✓ |
| Skip `.planning/`, placeholder `C:\venv` too | Also replace `C:\venv\` with `<VENV_DIR>` placeholder. ~25 files in scope. | |
| Aggressive: include `.planning/` | Also rewrite `.planning/` docs that quote `C:\Users\G\` as the discovered problem. Makes the discovery docs lie about what was found. | |

**User's choice:** Skip `.planning/`, keep `C:\venv\`.
**Notes:** `.planning/` files are descriptive artifacts of the cleanup discovery itself; touching them would make the codebase map and CONCERNS doc lie about what was originally found. `C:\venv\` is a documented suggestion (per `spec_classifier/CLAUDE.md` and README), not a hard requirement — keep concrete in docs, don't invent a `<VENV_DIR>` token.

---

## Orphan-File Definition

| Option | Description | Selected |
|--------|-------------|----------|
| Conservative (Recommended) | Delete `commits.txt` (gitignored cruft) and any `*.bak`/`*.zip` in tracked tree. Investigate `verify_teresa_audit_actionables.py` — delete only if zero references found. Old `prompts/` stays (Phase 3 owns). | ✓ |
| Aggressive grep-and-prune | Above + AST-level orphan detection on Python imports across `spec_classifier/src`. Anything unimported with no test coverage gets archived. | |
| Minimal (just `commits.txt`) | Delete `commits.txt` only. Defer everything else — too risky to call orphans without deep grep. | |

**User's choice:** Conservative.
**Notes:** User does not want the planner deleting modules just because a grep can't find imports. Any non-obvious orphan must be investigated (git log + reference grep across `run.ps1`, `Makefile`, `*.md`, `tests/`) before deletion.

---

## Verification Gate

| Option | Description | Selected |
|--------|-------------|----------|
| Full gate (Recommended) | (a) `git grep 'C:\\Users\\G\\'` against tracked files returns 0; (b) exactly one `.gitignore` at root; (c) `pytest tests/` green from `spec_classifier/`; (d) smoke run `.\run.ps1 -Vendor huawei -NoAi -SkipTests` passes. | |
| Pytest-only | Drop the smoke run — unit + regression tests cover behavior. Faster verification. | |
| Full gate + diff review | Same as full gate plus an explicit `git diff --stat` review checkpoint before commit, so user sees exactly what got rewritten. | ✓ |

**User's choice:** Full gate + diff review.
**Notes:** User wants a "no surprises" eyeball pass on `git diff --stat` even under YOLO mode. Process choice — they want to confirm scope didn't drift before commit lands.

---

## Claude's Discretion

- Specific commit grouping inside Phase 1 (one commit per requirement vs. one fat hygiene commit) — left to planner; recommendation is one commit per requirement (HYG-01, HYG-02, HYG-03 each its own commit) for atomic revert-ability.
- Exact regex set used in verification step (1) — verifier's call; the documented variants in CONTEXT.md D-11 are the floor, not the ceiling.
- Handling of unexpected orphan candidates surfaced by the planner's grep — surface in plan, defer deletion, ask before acting.

## Deferred Ideas

- **Cross-platform launcher (`run.sh`, POSIX GUI dispatch)** — `PLAT-01`/`PLAT-02` in REQUIREMENTS.md v2 backlog.
- **CI pipeline** — depends on cross-platform; `AUTO-01` in v2.
- **`<INPUT_ROOT>` / `<OUTPUT_ROOT>` token placeholders in markdown** — rejected for this phase as readability harm; could be revisited in Phase 2 (DOC-01/DOC-02) if README readability suffers.
- **AST-level orphan detection** — Aggressive option declined; future cleanup, not this phase.
- **Renaming `_E8_NO_HW_TYPE_DEVICES` / `DEVICE_TYPE_ALIASES` for clarity** — out of scope per CONCERNS.md "do not fix".
