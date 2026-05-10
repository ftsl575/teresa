# Phase 3: Workflow - Context

**Gathered:** 2026-05-10
**Status:** Ready for planning

<domain>
## Phase Boundary

Make GSD the single canonical development cycle for this repo. Three deliverables, no code or behavior change:

1. **WF-01 — Retire `spec_classifier/prompts/`** (10 .md files, 1345 lines, Russian) by `git mv` to `.planning/archive/prompts-2026-05-10/`. Includes `00..08`, `COWORK_OPUS_FULL_AUDIT.md`, and `README.md`.
2. **WF-02 — Author root `/CONTRIBUTING.md`** (~150–200 lines, English, tool-agnostic) documenting the GSD-native cycle (Discuss → Plan → Execute → Verify), pytest invocation + skip-ratio gate, link to `spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md` for vendor onboarding, and the project's "do not fix" tech-debt rules verbatim from `.planning/PROJECT.md` Out of Scope + `.planning/codebase/CONCERNS.md` BLOCKER.
3. **Cross-reference cleanup** so no doc points at a retired file: `spec_classifier/docs/dev/CONTRIBUTING.md` → archived; `spec_classifier/CLAUDE.md` legacy block → replaced with 1-paragraph pointer; root `CLAUDE.md` line 73–74 → symmetric replacement; `LAUNCHER_README.md:52` → repointed to `NEW_VENDOR_GUIDE.md`; `spec_classifier/docs/DOCS_INDEX.md` lines 27 + 36 → dropped + breadcrumb; `spec_classifier/CHANGELOG.md` historical lines → left verbatim, new entry added.

Strict non-goals: no behavior change, no goldens move, no YAML rule edits, no "do not fix" tech debt fixes. All 40 golden regression fixtures continue to pass byte-for-byte; pytest skip-ratio gate (`skipped/total > 0.50`) must not trip. Verification via the proven 7-step D-24 gate adapted to doc-only scope.

</domain>

<decisions>
## Implementation Decisions

### prompts/ Retirement (WF-01)

- **D-01:** Top-level approach — `git mv spec_classifier/prompts/ .planning/archive/prompts-2026-05-10/`. Mirrors Phase 2 D-08 (CURRENT_STATE.md archive). `spec_classifier/prompts/` ceases to exist in the working tree; git history preserved by `git mv`. Date suffix `2026-05-10` lets future archives stack.
- **D-02:** Inside the archive, the original Russian `prompts/README.md` is **rewritten in English** with three sections: (a) one-paragraph "this folder is the retired pre-GSD prompt library, archived 2026-05-10" note, (b) per-file mapping table, (c) link back to `/CONTRIBUTING.md` as the canonical doc. The 10 `0X_*.md` files (and `COWORK_OPUS_FULL_AUDIT.md`) are preserved verbatim (Russian) inside the archive as historical record.
- **D-03:** Per-file mapping table content (lock the wording so the planner doesn't re-derive):
  - `00_VENDOR-RECON.md` → `spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md`
  - `01_PRE-CHECK.md` → `/gsd-discuss-phase` (or `/gsd-progress` for status)
  - `02_MASTER-PLAN.md` → `/gsd-plan-phase`
  - `03_CURSOR-IMPLEMENT.md` → `/gsd-execute-phase`
  - `04_POST-CHECK.md` → `/gsd-verify-work`
  - `05_AUDIT-1A-1G.md` → `/gsd-audit-fix` (and `/gsd-code-review` for the focused review pieces)
  - `06_BATCH-AUDIT-MASTER-PLAN.md` → run `python batch_audit.py` then `/gsd-plan-phase` against the findings
  - `07_DOC-UPDATE-MASTER-PLAN.md` → `/gsd-docs-update`
  - `08_CHATGPT-SYSTEM-PROMPTS.md` → no GSD equivalent (these were ChatGPT-specific system prompts)
  - `COWORK_OPUS_FULL_AUDIT.md` → `/gsd-audit-fix` or `/gsd-code-review` for the audit cycle (audit-mode, not a per-step prompt)
- **D-04:** `COWORK_OPUS_FULL_AUDIT.md` uses the **same** archive treatment as `00..08` — moved alongside, listed in the mapping table flagged as "audit-mode" rather than "cycle-step" so a reader doesn't expect a step-by-step.
- **D-05:** `LAUNCHER_README.md:52` ("Implement adapter (see `prompts/00_VENDOR-RECON.md`).") is **repointed to `spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md`**. The natural successor; self-contained; doesn't send contributors into the archive for content that's already covered by a live guide.

### Inner CONTRIBUTING.md Fate (WF-02 enabling)

- **D-06:** `spec_classifier/docs/dev/CONTRIBUTING.md` (77 lines, Russian, with the Phase-2 forwarding note already inside) — `git mv` to `.planning/archive/CONTRIBUTING-2026-05-10.md`. Same archive pattern as D-08 (Phase 2) and D-01 here. History preserved; `spec_classifier/docs/dev/` is freed of the LEGACY-flagged file; `/CONTRIBUTING.md` is unambiguously canonical. Zero risk of two CONTRIBUTING.mds drifting.
- **D-07:** `spec_classifier/docs/DOCS_INDEX.md` line 27 (the `docs/dev/CONTRIBUTING.md` row) — **drop the row**. The 1:1 invariant Phase 2 D-16 established (every entry points at an existing file) is preserved automatically.
- **D-08:** `spec_classifier/docs/DOCS_INDEX.md` line 36 (the `prompts/README.md` row) — **drop the row** (consistent with D-07 and the prompts/ archive). Symmetric treatment.
- **D-09:** Add a single "See also" breadcrumb under `spec_classifier/docs/DOCS_INDEX.md` § Conventions: `> **Repo-root contributor doc:** see [/CONTRIBUTING.md](../../CONTRIBUTING.md) for the GSD-native development cycle and contribution rules.` Lightweight pointer that survives the docs/-scoped index.

### Root /CONTRIBUTING.md Scope (WF-02)

- **D-10:** Target depth — **medium, ~150–200 lines**. Sections (in order):
  1. One-sentence "what this repo is" + pointer to root README for install/run.
  2. **Development cycle** — literal command-by-command (per D-13 below).
  3. **Tests** — how to run pytest from `spec_classifier/`, the `skipped/total > 0.50` skip-ratio gate (`spec_classifier/conftest.py:pytest_sessionfinish`), and a one-liner on goldens (`golden/*_expected.jsonl` is the regression contract — see `spec_classifier/docs/dev/TESTING_GUIDE.md`).
  4. **Adding a vendor** — pointer-only to `spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md` (no duplication per ROADMAP success-criteria 2c).
  5. **PR workflow** — commit-message convention (`docs(NN-PP): ...`, mirrors the existing pattern from Phase 1/2 commits), one-commit-per-task pattern, atomic revertability.
  6. **Code style** — PEP 8, 4-space indent, docstrings for public functions, follow surrounding-file style (one paragraph; not a duplicate of NEW_VENDOR_GUIDE / RULES_AUTHORING_GUIDE).
  7. **Do not fix** — verbatim list per D-15.
  8. **Where to look first** — table mirroring root `CLAUDE.md` § "Where to look first", with one extra row pointing back at `spec_classifier/CLAUDE.md` for the deep reference.
- **D-11:** Tone — **tool-agnostic**. The doc says "use Claude Code or any AI coding agent that runs the GSD commands" rather than locking the project to a specific tool. Mirrors how root `README.md` and root `CLAUDE.md` are written. Does **not** carry forward the deep CLAUDE.md "Tool Roles" table (Cursor/Claude/ChatGPT/Gemini split) — that's GSD-superseded narrative.
- **D-12:** Platform stance — `/CONTRIBUTING.md` says **"Windows-only this milestone"** in passing (one sentence in the Tests / Development cycle context, mirroring root `README.md`'s framing). Does NOT re-litigate the cross-platform decision (PLAT-01/PLAT-02 are deferred per `.planning/REQUIREMENTS.md` v2 backlog).
- **D-13:** GSD-cycle section format — **literal command-by-command with one-liner per command**:
  ```
  1. Discuss — `/gsd-discuss-phase <N>`. Clarifies HOW to implement what's in ROADMAP.md for phase N.
  2. Plan    — `/gsd-plan-phase <N>`. Produces NN-PP-PLAN.md task lists with verification gates.
  3. Execute — `/gsd-execute-phase <N>`. Runs the plans in dependency order with atomic commits.
  4. Verify  — `/gsd-verify-work <N>`. Confirms goal achievement against ROADMAP success criteria.

  Run `/gsd-help` for the full command list.
  ```
  Reproducible: a contributor sees exactly which commands run in which order. Stays accurate as long as the four commands keep their names; if GSD renames any, this section gets a one-line edit.
- **D-14:** "Adding a vendor" section is a **pointer**, not duplicated content: `> See [`spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md`](spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md) for the adapter contract, parser/normalizer scaffold, golden workflow, and per-vendor sheet conventions.` (Plus a one-paragraph "what to expect" framing.) Honors ROADMAP success-criteria 2c (link only, no duplication).
- **D-15:** "Do not fix" section content — **verbatim copy from `.planning/PROJECT.md` § Out of Scope and `.planning/codebase/CONCERNS.md` § BLOCKER one-liners**, ending with `> Full rationale and context: [.planning/codebase/CONCERNS.md](.planning/codebase/CONCERNS.md) § BLOCKER + IMPORTANT.` Items to lift verbatim:
  - `power_cord` has `hw_type=None` intentionally (recovery commit `c3c7cb6`)
  - `spec_classifier/src/core/parser.py` is Dell-specific despite living in `core/`
  - `spec_classifier/batch_audit.py` reads from `*_annotated.xlsx` instead of `classification.jsonl`
  - YAML rule order is load-bearing (first-match-wins; never sort or reorder)
  - `HW_TYPE_VOCAB` is duplicated between `classifier.py` and `batch_audit.py` (tracked, not selected for cleanup milestones)

  Single source of truth survives — wording stays fixed; future updates to PROJECT.md / CONCERNS.md need to be mirrored once into CONTRIBUTING.md.

### Deep & Root CLAUDE.md Updates (cross-reference cleanup)

- **D-16:** `spec_classifier/CLAUDE.md` legacy block — **replace** §§ "Tool Roles", "Development Cycle" (table with PRE-CHECK → MASTER PLAN → CURSOR IMPLEMENT → POST-CHECK → AUDIT 1A–1G), "Hard Rules for Claude Windows" (R1–R5), "Recommended Models per Step", and "Prompts — Location" with a single ~3-line section:
  ```
  ## Development Cycle

  This project uses the GSD-native cycle (Discuss → Plan → Execute → Verify).
  See [/CONTRIBUTING.md](../CONTRIBUTING.md) for the canonical workflow,
  pytest invocation, PR conventions, and the project's "do not fix" rules.
  ```
  Removes ~50 lines of obsolete narrative; deep CLAUDE.md stays focused on its core (taxonomy, E-codes, business rules, current state, paths). The 5 critical business rules already deduplicated to root CLAUDE.md per Phase 2 D-01 stay where they are; this change does NOT touch the business-rules sections.
- **D-17:** Root `CLAUDE.md` § Tooling roles (lines 71–74) — **replace** the legacy step-list sentence with: `The canonical development cycle (Discuss → Plan → Execute → Verify, GSD-native) is documented in [`/CONTRIBUTING.md`](CONTRIBUTING.md).` Symmetric with D-16; stays at one sentence; preserves the `.cursor/` informational note above it. Section header `## Tooling roles` stays (the `.cursor/` line is still relevant).

### CHANGELOG.md Handling

- **D-18:** `spec_classifier/CHANGELOG.md` historical lines mentioning `prompts/` (e.g., line 44 "docs: prompts/ — prompt library", line 208 "docs/prompts/") — **leave verbatim**. CHANGELOG entries describe what landed at the time; rewriting historical entries falsifies history (Phase 2 D-07 explicitly chose release-notes style).
- **D-19:** Add a NEW CHANGELOG entry under the next version banner (planner picks the version; suggested `v1.4.x` or matching the Phase 3 milestone version) noting:
  ```
  ### Changed
  - Retired `spec_classifier/prompts/` to `.planning/archive/prompts-2026-05-10/`;
    the GSD-native cycle is now documented at `/CONTRIBUTING.md` (new file).
  - Archived `spec_classifier/docs/dev/CONTRIBUTING.md` to
    `.planning/archive/CONTRIBUTING-2026-05-10.md`; superseded by `/CONTRIBUTING.md`.
  - Replaced legacy "Development Cycle" block in `spec_classifier/CLAUDE.md` with a
    pointer to `/CONTRIBUTING.md`.
  ```
  Standard "changed" note; gives readers an audit trail without bending historical entries.

### Verification Gate (Adapt D-24 to Doc-Only Scope)

- **D-20:** Reuse the proven 7-step pattern from Phase 2 D-24, scoped to Phase 3 deliverables:
  1. **Cross-reference integrity (greps).** Negative-control: outside `.planning/archive/`, `git grep -nE 'PRE-CHECK|MASTER-PLAN|CURSOR-IMPLEMENT|POST-CHECK|AUDIT-1A|VENDOR-RECON|BATCH-AUDIT-MASTER|DOC-UPDATE-MASTER|CHATGPT-SYSTEM' -- ':!.planning/archive/'` returns 0 hits. Positive-control: `git grep -n 'CONTRIBUTING.md'` against tracked files returns the root `/CONTRIBUTING.md` plus the new pointers (deep CLAUDE.md, root CLAUDE.md, DOCS_INDEX.md breadcrumb, etc.). Negative-control: no tracked file references `spec_classifier/prompts/` or `spec_classifier/docs/dev/CONTRIBUTING.md` outside `.planning/`.
  2. **DOCS_INDEX 1:1.** Every `spec_classifier/docs/**/*.md` file is listed in `DOCS_INDEX.md`; every entry in `DOCS_INDEX.md` exists. Both rows dropped (lines 27, 36) and the `See also` breadcrumb present. Set-diff via `comm -3 <(...) <(...)` returns empty in both directions.
  3. **Quick Start runnability.** `.\run.ps1 -Vendor huawei -NoAi -SkipTests` from repo root after following root README's Quick Start verbatim — exits 0, produces fresh `OUTPUT/huawei_run/run-...` folder. (Phase 2 verified this; re-run as a regression check, **with the W-5 PASS-WITH-CAVEAT pattern from Phase 1 D-21 if INPUT files are absent on the runner**.)
  4. **End-to-end read pass.** Verifier reads each modified/new doc end-to-end: `/CONTRIBUTING.md` (new), `spec_classifier/CLAUDE.md` (updated), root `CLAUDE.md` (updated), `spec_classifier/docs/DOCS_INDEX.md` (updated), `LAUNCHER_README.md` (updated), `.planning/archive/prompts-2026-05-10/README.md` (new), `spec_classifier/CHANGELOG.md` (new entry added). Emits `03-READ-REPORT.md` with per-file findings. Any HIGH-severity drift blocks the gate.
  5. **Goldens unchanged.** `git diff --stat <pre-Phase-3..HEAD> -- spec_classifier/golden/` empty.
  6. **Pytest still green.** `pytest tests/ -v --tb=short` from `spec_classifier/` exits 0; skip-ratio gate not tripped (Phase 1 W-5 INPUT-precondition probe pattern carries forward).
  7. **Diff-review checkpoint.** `git diff --stat HEAD~N..HEAD` reviewed before final commits land (mirrors Phase 1 D-11 step 5 and Phase 2 D-24 step 7). User confirms scope is clean.
- **D-21:** Phase 3 verification artifacts: `03-VERIFICATION.md` (per-step gate evidence), `03-READ-REPORT.md` (per-file end-to-end findings), `03-SUMMARY.md` (phase-level wrap-up). Same shape as Phase 2 (`02-VERIFICATION.md`, `02-READ-REPORT.md`, `02-SUMMARY.md`).

### Honor "Do Not Fix" Framing

- **D-22:** Throughout Phase 3, the load-bearing tech-debt items in `.planning/codebase/CONCERNS.md` § BLOCKER + IMPORTANT are **referenced verbatim in `/CONTRIBUTING.md`** (per D-15) but **not touched in code**. `power_cord=None`, `core/parser.py` Dell-specificity, `batch_audit.py` Excel-reader, YAML rule order, `HW_TYPE_VOCAB` duplication all stay exactly as they are.
- **D-23:** No documentation-of-intent-to-fix language allowed in `/CONTRIBUTING.md` — the section is "do not fix" only, not "do not fix YET" or "planned for later." Frame each item as "intentional behavior; see CONCERNS.md for the full rationale."

### Claude's Discretion

- **Plan structure:** I expect 3–4 plans (one per requirement is the established Phase 1/2 pattern — `WF-01 prompts archive`, `WF-02 root CONTRIBUTING.md + cross-ref cleanup`, plus a final verification-gate plan analogous to `01-04` and `02-06`). Defer to planner.
- **Commit grouping:** one commit per requirement (HYG-01/02/03 and DOC-01..05 pattern). Defer to planner.
- **Order of operations within Phase 3:** my recommendation is WF-01 first (archives stabilize the cross-ref target list before WF-02 writes to those targets), then WF-02 + cross-ref cleanup, then verification gate. Planner can decide.
- **Exact wording inside the new CHANGELOG entry (D-19):** the version banner choice and the exact bullet phrasing are planner/executor decisions, as long as the three changes (prompts/ archive, inner CONTRIBUTING archive, deep CLAUDE.md update) are mentioned.
- **Exact PR-workflow paragraph in /CONTRIBUTING.md (D-10 §5):** the planner picks how much PR-template content to include vs. just describing the convention. Lean toward "describe the convention" — the repo doesn't currently have a PR template file.
- **Whether to also add `/CONTRIBUTING.md` to root `README.md` § "Learn more" table:** I lean YES for discoverability, but it's a 1-line tweak and not a Phase 3 success criterion. Planner's call.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project policy and "do not fix" rules

- `.planning/PROJECT.md` — milestone scope, "Done" definition, Out of Scope (especially "Strip `C:\Users\G\` username only; do not de-Windowize launchers"; "Honor 'do not fix' tech debt"; the full Out of Scope table is the verbatim source for D-15)
- `.planning/REQUIREMENTS.md` § Workflow — WF-01 and WF-02 in their authoritative phrasing
- `.planning/codebase/CONCERNS.md` § BLOCKER and § IMPORTANT — verbatim source for the "do not fix" list in `/CONTRIBUTING.md` per D-15

### Phase 1 + 2 carry-forward decisions

- `.planning/phases/01-hygiene/01-CONTEXT.md` D-01 + D-04 — placeholder convention (`<USERNAME>`, `%USERPROFILE%`, etc.); applies to any new doc content
- `.planning/phases/01-hygiene/01-CONTEXT.md` D-11 — verification gate pattern (5-step → adapted in D-20 to 7-step doc-only)
- `.planning/phases/01-hygiene/01-CONTEXT.md` D-21 — PASS-WITH-CAVEAT for missing INPUT (applies to D-20 step 3 Quick Start runnability)
- `.planning/phases/02-docs/02-CONTEXT.md` D-08 — archive pattern (CURRENT_STATE-2026-05-10.md); template for D-01 and D-06 here
- `.planning/phases/02-docs/02-CONTEXT.md` D-16 — DOCS_INDEX 1:1 invariant; D-07/D-08 here preserve it
- `.planning/phases/02-docs/02-CONTEXT.md` D-18/D-19/D-20 — pre-set the inner-CONTRIBUTING.md handover to Phase 3; D-06 here closes those items
- `.planning/phases/02-docs/02-CONTEXT.md` D-21/D-22 — "do not fix" framing; D-22/D-23 here carry it forward
- `.planning/phases/02-docs/02-CONTEXT.md` D-24 — 7-step verification gate; D-20 here adapts it to doc-only scope
- `.planning/phases/02-docs/02-CONTRIBUTING-AUDIT.md` — the Phase 2 LEGACY assessment of `spec_classifier/docs/dev/CONTRIBUTING.md`; explicit Phase 3 hand-off in § "Phase 3 Hand-off"
- `.planning/phases/02-docs/02-SUMMARY.md` — what landed in Phase 2; especially the `Out-of-Scope Confirmations` table flagging "CURRENT_STATE.md references in prompts/" and "CONTRIBUTING.md full rewrite" as Phase 3-owned

### Codebase map

- `.planning/codebase/STRUCTURE.md` — full directory layout; informs where `/CONTRIBUTING.md` sits and what cross-refs to write
- `.planning/codebase/CONVENTIONS.md` — code style + business rules; informs the brief code-style paragraph in `/CONTRIBUTING.md` D-10 §6
- `.planning/codebase/TESTING.md` — pytest invocation, `skipped/total > 0.50` skip-ratio gate, golden regression contract; verbatim source for `/CONTRIBUTING.md` D-10 §3

### Files in scope (subjects of edits / moves / new content)

- `spec_classifier/prompts/` (10 files, 1345 lines) — `git mv` to `.planning/archive/prompts-2026-05-10/` per D-01; archive README rewritten per D-02/D-03; COWORK file treated per D-04
- `spec_classifier/docs/dev/CONTRIBUTING.md` (77 lines, Russian, Phase-2 forwarding note inside) — `git mv` to `.planning/archive/CONTRIBUTING-2026-05-10.md` per D-06
- `/CONTRIBUTING.md` (does not exist; new file) — authored per D-10..D-15
- `spec_classifier/CLAUDE.md` lines 215–307 (~93 lines) — legacy block replaced per D-16; the 5 critical business rules and earlier sections (Project, Paths, Current State, Tests, INPUT/OUTPUT layout, Key repo files, CLI Commands, Business Rules, E-codes, Known Tech Debt) stay untouched
- `CLAUDE.md` (root, 74 lines) lines 71–74 — § Tooling roles sentence replaced per D-17
- `spec_classifier/docs/DOCS_INDEX.md` lines 27 + 36 — rows dropped per D-07/D-08; "See also" breadcrumb added under § Conventions per D-09
- `LAUNCHER_README.md` line 52 — repointed per D-05
- `spec_classifier/CHANGELOG.md` — historical lines untouched per D-18; new entry added per D-19

### Discussion source-of-truth

- `.planning/phases/03-workflow/03-DISCUSSION-LOG.md` — full Q&A trace for this phase (audit / retrospective; not consumed by downstream agents)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **D-08 archive pattern from Phase 2.** `git mv spec_classifier/CURRENT_STATE.md .planning/archive/CURRENT_STATE-2026-05-10.md` is the proven template; D-01 (prompts/) and D-06 (inner CONTRIBUTING.md) reuse it verbatim, just with the file/folder substituted. Date suffix lets future archives stack.
- **7-step verification gate (Phase 2 D-24).** Reused in D-20 with adapted greps (legacy step-name patterns instead of `C:\Users\G\` patterns) and adapted read scope (Phase 3-touched docs instead of all 13 docs/ files). The PowerShell `Invoke-GitGrepExclPlanning` helper from Phase 1 Plan 04 is reusable for the negative-control grep in D-20 step 1.
- **W-5 PASS-WITH-CAVEAT pattern (Phase 1 D-21).** INPUT-presence precondition probe before running the smoke test; absent INPUT yields PASS-WITH-CAVEAT not FAIL. Carries into D-20 step 3.
- **Per-context placeholder scheme (Phase 1 D-01).** Any literal Windows path examples in `/CONTRIBUTING.md` use `%USERPROFILE%` (batch/PowerShell context) or `<USERNAME>` (markdown context); `C:\venv` stays literal as a documented suggestion (Phase 1 D-04).
- **Existing root README.md § "Learn more" table.** Pattern for the `/CONTRIBUTING.md` § "Where to look first" table in D-10 §8 — same row format, same link discipline.
- **`spec_classifier/conftest.py:pytest_sessionfinish` skip-ratio gate.** Already documented in `.planning/codebase/TESTING.md`; D-10 §3 quotes the rule (`skipped/total > 0.50` triggers session FAIL) verbatim.

### Established Patterns

- **Code-only repo policy.** Phase 1 enforced; Phase 3 reinforces it implicitly (no code touched, no INPUT/OUTPUT/venv references added to `/CONTRIBUTING.md`).
- **One-commit-per-task / one-commit-per-requirement.** Phase 1 (HYG-01/02/03 each its own commit) and Phase 2 (DOC-04, DOC-05, DOC-01, DOC-02, DOC-03 each its own commit) established the convention. Phase 3 plans should follow it: WF-01 commit (prompts archive), WF-02 commit (root CONTRIBUTING.md + cross-ref cleanup), gate-closure commit. PR-workflow paragraph in `/CONTRIBUTING.md` D-10 §5 documents this convention so future contributors keep it.
- **Forwarding-pointer convention.** Phase 2 D-08 added a forward-pointer in `spec_classifier/CLAUDE.md` § Current State → archive. D-16 here keeps the same shape — `spec_classifier/CLAUDE.md` § Development Cycle becomes a forward-pointer to `/CONTRIBUTING.md`.
- **Russian-content quarantine.** Phase 2 chose to translate `spec_classifier/CLAUDE.md` to English (D-04) and refresh CHANGELOG to English (D-07), but explicitly left YAML rule-file Russian comments untouched (D-06). D-02 here is consistent: archive README rewritten in English, but the archived `0X_*.md` files keep their original Russian (historical record; not user-facing).

### Integration Points

- **Phase 3 → milestone close.** This is the last phase of the v1.0 cleanup-and-workflow milestone (per `.planning/STATE.md`: "total_phases: 3, completed_phases: 2"). After Phase 3 verification gate PASSes, the milestone can be closed via `/gsd-complete-milestone`. The milestone-close step will likely audit Phase 3's deliverables — `/CONTRIBUTING.md` existing and being accurate is a natural close criterion.
- **`/CONTRIBUTING.md` and `/gsd-complete-milestone`.** The new `/CONTRIBUTING.md` becomes the entry point for any contributor opening the next milestone (v2.0 — likely classification rule improvements per `.planning/REQUIREMENTS.md` v2). It needs to teach the GSD cycle without assuming prior project history.
- **Archive folder `.planning/archive/` becomes a multi-resident directory** after Phase 3 (CURRENT_STATE-2026-05-10.md from Phase 2 + prompts-2026-05-10/ + CONTRIBUTING-2026-05-10.md from Phase 3). No README needed at `.planning/archive/` itself — each archived item is self-explanatory by name + date suffix.
- **DOCS_INDEX.md set-diff invariant.** D-16 from Phase 2 locks DOCS_INDEX.md to the docs/ tree; D-07/D-08 here drop rows whose targets are leaving docs/. The verification step 2 in D-20 re-runs the set-diff to catch any miss. No risk of orphaned rows surviving.
- **No CI dependency.** PLAT-01/AUTO-01 (cross-platform launcher + CI pipeline) are explicit v2 deferrals per `.planning/REQUIREMENTS.md`. Phase 3 should NOT add a `.github/workflows/` directory or any CI references to `/CONTRIBUTING.md` — that would be scope creep.

</code_context>

<specifics>
## Specific Ideas

- The user explicitly chose **archive (`git mv` to `.planning/archive/prompts-2026-05-10/`)** over deprecation-stub or full delete — consistent with their Phase 2 D-08 preference for archives over deletions, and with their general "preserve history, leave a forward-pointer" pattern.
- The user explicitly chose **English archive README + per-file mapping table** over preserving the original Russian or doing a plain `git mv`. Signal: they want the archive to be navigable for future contributors (English-readable), not just a historical dump. Also frees them from needing to know Russian to understand what was there.
- The user explicitly chose to give **COWORK_OPUS_FULL_AUDIT.md the same archive treatment** as `00..08` rather than separating it or deleting. Uniform treatment minimizes per-file decisions in the planner and keeps the archive cohesive.
- The user explicitly chose **`LAUNCHER_README.md:52` → `NEW_VENDOR_GUIDE.md`** over the archive path or the new `/CONTRIBUTING.md`. Signal: they prefer direct, self-contained pointers over indirection chains.
- The user explicitly chose **`git mv` of inner CONTRIBUTING.md to archive** over delete, forwarding-stub, or translate-and-keep. Same archive-preference signal as D-01.
- The user explicitly chose **drop both DOCS_INDEX.md rows + add a single 'See also' breadcrumb under § Conventions**. Signal: they want DOCS_INDEX.md to stay docs/-scoped (Phase 2 D-16 invariant) but not lose the breadcrumb to the new canonical doc.
- The user explicitly chose **medium depth (~150–200 lines)** for `/CONTRIBUTING.md` over minimum or rich. Wants enough to teach a fresh contributor the workflow without bloating into rich content that risks duplicating CLAUDE.md / NEW_VENDOR_GUIDE.md.
- The user explicitly chose **tool-agnostic voice** over mentioning Claude Code or carrying forward the Cursor/Claude/ChatGPT/Gemini split. Signal: they want `/CONTRIBUTING.md` to age well; GSD commands, not specific AI tools, are the canonical surface.
- The user explicitly chose **verbatim "do not fix" rules + pointer to CONCERNS.md** over restated voice or pointer-only. Same single-source-of-truth + visibility-in-CONTRIBUTING preference; mirrors D-15.
- The user explicitly chose **literal command-by-command** GSD-cycle format over conceptual or diagrammed. Same preference for direct, self-contained, reproducible documentation.
- The user explicitly chose **replace the whole legacy block in deep CLAUDE.md with a 1-paragraph pointer** over keep-as-historical or minimal-footer-only. Cleanest signal yet that legacy narrative is fully retired, not preserved-but-demoted.
- The user explicitly chose **symmetric replacement in root CLAUDE.md line 73–74**. Consistency with deep CLAUDE.md update; same one-sentence shape.
- The user explicitly chose **adapt the same 7-step gate, doc-only scope** over scoped-down 4-step or planner-discretion. Same Phase 1/2 preference for proven patterns + concrete checkable conditions.
- The user explicitly chose **leave CHANGELOG historical lines verbatim, add new entry**. Honors release-notes immutability convention (Phase 2 D-07) without losing the audit trail.

</specifics>

<deferred>
## Deferred Ideas

- **Cross-platform launcher (`run.sh`)** — explicit v2 backlog (`.planning/REQUIREMENTS.md` PLAT-01); not Phase 3.
- **CI pipeline (GitHub Actions running pytest + audits on push)** — explicit v2 backlog (AUTO-01); depends on cross-platform support; explicitly NOT in `/CONTRIBUTING.md`.
- **Pre-commit hook for rule-id schema validation** — explicit v2 backlog (AUTO-02); not Phase 3.
- **Classification rule improvements** — explicit v2 backlog (CLAS-01); the next milestone after v1.0 cleanup-and-workflow closes.
- **New vendor onboarding** — explicit v2 backlog (CLAS-02); pointer-only in `/CONTRIBUTING.md` per D-14.
- **Auto-generated PR template (`.github/PULL_REQUEST_TEMPLATE.md`)** — considered during D-10 §5 discussion, deferred. Repo has no `.github/` tooling today; adding one is its own decision (likely ties to AUTO-01 CI work).
- **Translating archived prompts files to English** — explicitly NOT done per D-02; preserved as Russian historical record. A future polish milestone could revisit.
- **Adding a `.planning/archive/README.md` describing the archive convention** — considered during D-09 discussion, deferred. Each archived item is self-explanatory by name + date suffix; no need for an archive-folder README yet. Could be added later if archive count grows.
- **Translating `spec_classifier/CHANGELOG.md` historical Russian entries** — Phase 2 D-07 chose English-unified for the refresh; any remaining Russian fragments in deep history are preserved verbatim. Out of scope for Phase 3.
- **Refactoring `spec_classifier/CLAUDE.md` into a smaller core file + sub-files** — considered during D-16 discussion, deferred. Phase 3 only edits the legacy block; the deeper file structure remains. A future docs-restructure milestone could split it.
- **Renaming the milestone** — currently labeled "Cleanup & Workflow Setup" in `REQUIREMENTS.md`; could be renamed at milestone-close. Not a Phase 3 concern.

### Reviewed Todos (not folded)

None — `gsd-sdk query todo.match-phase 3` returned 0 matches; no pending todos surfaced for this phase.

</deferred>

---

*Phase: 3-Workflow*
*Context gathered: 2026-05-10*
