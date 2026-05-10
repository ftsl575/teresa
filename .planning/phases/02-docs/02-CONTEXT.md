# Phase 2: Docs - Context

**Gathered:** 2026-05-10
**Status:** Ready for planning

<domain>
## Phase Boundary

Refresh every committed documentation file (root + `spec_classifier/`) to accurately describe the post-Phase-1 codebase. Deduplicate the two `CLAUDE.md` files per the user-locked split rule. Translate `spec_classifier/CLAUDE.md` from Russian to English. Refresh `CHANGELOG.md` against git history; archive `CURRENT_STATE.md`. Audit the `spec_classifier/docs/` tree end-to-end for drift, broken cross-references, and stale content.

No code changes. No behavior changes. All 40 golden regression fixtures continue to pass byte-for-byte; pytest skip-ratio gate must not trip.

Five requirements: DOC-01 (root README), DOC-02 (spec_classifier README), DOC-03 (docs/ tree audit), DOC-04 (CLAUDE.md dedup + translation), DOC-05 (CHANGELOG refresh / CURRENT_STATE archive).

</domain>

<decisions>
## Implementation Decisions

### CLAUDE.md Split Rule (DOC-04)

- **D-01:** Root `CLAUDE.md` = pointer + critical rules. Final size ~80–100 lines. Contents:
  - Project name + one-paragraph "what this is"
  - Repo-layout note (root launcher + `spec_classifier/`; code-only repo policy)
  - The 5 critical business rules verbatim (so any GSD command launched at root sees them):
    1. `power_cord` has `hw_type=None` intentionally
    2. LOGISTIC = packaging/docs/freight only (NOT power cords, cables, rails, brackets)
    3. BASE without `device_type` is normal (E15 = INFO); BASE with `hw_type` triggers E10
    4. `is_factory_integrated=True` rows are CONFIG; AI does not check them
    5. `hw_type_rules.applies_to` is `[HW]` only — never `[HW, BASE]`
  - "Where to look first" table (Pipeline question / vendor adapter / add a vendor / rules authoring → all point at `spec_classifier/CLAUDE.md` or `spec_classifier/docs/`)
  - Pointer to `spec_classifier/CLAUDE.md` for everything else
- **D-02:** Deep `spec_classifier/CLAUDE.md` owns everything else: full pipeline-stages section, audit E1–E18 table, alias-table semantics (`DEVICE_TYPE_ALIASES`, `_ALIASES`, `device_type_map` distinctions), dev cycle (PRE-CHECK → AUDIT 1A–1G), hard rules R1–R5, taxonomy notes, "do not fix" tech-debt notes verbatim. No content from these areas is duplicated in root.
- **D-03:** Overlap detection at execute time: planner runs `diff <(extract-bullets root) <(extract-bullets spec_classifier)` (or equivalent grep) and any business-rule sentence appearing in both is removed from root. Critical-rules section is the only sanctioned overlap (5 rules above).

### Language Convention (DOC-04)

- **D-04:** Translate `spec_classifier/CLAUDE.md` from Russian to English. ~303 lines, medium effort, single executor pass with technical-accuracy review.
  - Preserve technical terms unchanged: `device_type`, `hw_type`, `RowKind`, `EntityType`, `BASE/HW/CONFIG/SOFTWARE/SERVICE/LOGISTIC/NOTE/UNKNOWN`, `power_cord`, `_E8_NO_HW_TYPE_DEVICES`, etc.
  - Preserve all section headers but translate them (e.g., "ЦИКЛ РАЗРАБОТКИ" → "Development Cycle"; "ЖЁСТКИЕ ПРАВИЛА" → "Hard Rules"; "БИЗНЕС-ПРАВИЛА" → "Business Rules"; "ТЕКУЩЕЕ СОСТОЯНИЕ" → "Current State"; "ПУТИ" → "Paths").
  - Preserve all code blocks, file references, line numbers, and command examples verbatim.
  - Preserve all comments inside YAML/Python examples in their original language IF those examples were copied verbatim from rule files (the rule-file comments are themselves Russian; translating them would diverge from the YAML source).
  - Translation MUST keep the same semantic meaning; if a Russian phrase has multiple English readings, prefer the one that matches actual code behavior (cross-check at translation time).
- **D-05:** Root `CLAUDE.md` stays English (already is).
- **D-06:** Russian narrative in YAML rule files (`spec_classifier/rules/*.yaml`) is OUT OF SCOPE — those rule files are load-bearing and not in any DOC-* requirement. Comments stay Russian.

### CHANGELOG.md and CURRENT_STATE.md (DOC-05)

- **D-07:** `spec_classifier/CHANGELOG.md` — refresh against current state.
  - Source of truth: `git log --oneline --reverse` from project inception, grouped by milestone/phase boundary.
  - Format: keep release-notes style; one entry per logical change (not per commit). Group by month or version banner.
  - Length target: similar to current 258 lines (don't bloat). Drop entries that have been superseded.
  - Do NOT translate (English is fine; the existing CHANGELOG is already in mixed English/Russian — unify to English during refresh).
- **D-08:** `spec_classifier/CURRENT_STATE.md` — archive.
  - Move to `.planning/archive/CURRENT_STATE-2026-05-10.md` (with date suffix so future archives can stack).
  - Create `.planning/archive/` directory if not present.
  - Add a one-line note in `spec_classifier/CLAUDE.md` "Current State" section pointing to the archive AND to `.planning/STATE.md` as the live source-of-truth going forward.
  - The archive copy is committed verbatim — historical record.
- **D-09:** No content from `CURRENT_STATE.md` is migrated into `PROJECT.md` or `STATE.md` — those have their own evolution rules and are not historical archives.

### Root README.md Scope (DOC-01)

- **D-10:** Write root `README.md` from scratch (currently empty). Target ~80–120 lines, full top-level intro:
  - Project name + tagline
  - One-paragraph "what this is" (mirrors PROJECT.md "What This Is")
  - "Repo layout" note: root launcher (`run.ps1`, `teresa.bat`, `teresa_gui.py`) vs `spec_classifier/` (the actual codebase)
  - Quick Start (must be runnable verbatim — see D-15 below):
    - Install Python 3.10+, pip install requirements (or note venv at `C:\venv`)
    - Place INPUT under `%USERPROFILE%\Desktop\INPUT\<vendor>\`
    - Run `.\run.ps1` or double-click `teresa.bat`
  - Key commands table: `.\run.ps1 -Vendor <v>`, `-NoAi`, `-TestsOnly`, etc.
  - "Learn more" pointer to `spec_classifier/README.md` (deep CLI/config reference) and `spec_classifier/CLAUDE.md` (developer reference)
- **D-11:** Some overlap with `spec_classifier/README.md` is acceptable — root targets repo-arrivers, deep targets users-already-running-it. Don't aggressively dedupe between READMEs.

### spec_classifier/README.md Refresh (DOC-02)

- **D-12:** Refresh `spec_classifier/README.md` (286 lines, currently). Audit all sections against current code:
  - CLI usage examples: cross-check against `spec_classifier/main.py` argparse spec
  - Config layering (`config.yaml` ← `config.local.yaml`): cross-check against `_load_config()` in `main.py:69-86`
  - Output paths: cross-check against `spec_classifier/src/diagnostics/run_manager.py`
  - Golden file workflow: cross-check against `Makefile` and `--save-golden` / `--update-golden` flags
  - Cross-references to `docs/`: every file referenced must exist
  - Remove any references to `CURRENT_STATE.md` (archived in this phase)
  - `C:\venv\` references stay literal (D-04 from Phase 1 carries forward)
- **D-13:** No structural rewrite — drift fixes only. If a section is fundamentally wrong, FIX the prose; if the structure is workable, keep the structure and update content.

### docs/ Tree Audit (DOC-03)

- **D-14:** Audit each file in `spec_classifier/docs/` end-to-end. Files in scope (~2,200 lines total across 13 files):
  - `docs/DOCS_INDEX.md` (29 lines)
  - `docs/dev/CONTRIBUTING.md` (75 lines), `NEW_VENDOR_GUIDE.md` (123), `ONE_BUTTON_RUN.md` (40), `OPERATIONAL_NOTES.md` (113), `TESTING_GUIDE.md` (118)
  - `docs/product/TECHNICAL_OVERVIEW.md` (312)
  - `docs/rules/RULES_AUTHORING_GUIDE.md` (154)
  - `docs/schemas/DATA_CONTRACTS.md` (232)
  - `docs/taxonomy/cycle2_summary.md` (103), `hw_type_taxonomy.md` (462)
  - `docs/user/CLI_CONFIG_REFERENCE.md` (105), `RUN_PATHS_AND_IO_LAYOUT.md` (281), `USER_GUIDE.md` (166)
- **D-15:** For each file:
  - Verify every cross-reference (file paths, line numbers, links) points at something that exists post-Phase-1
  - Verify factual claims about commands / flags / file paths against the live code
  - Flag stale content for rewrite OR removal — choose based on the rule below
  - Stale-content rule: if a section describes something no longer true AND the section's purpose is still relevant, REWRITE; if the section's purpose is itself obsolete, DELETE.
- **D-16:** `docs/DOCS_INDEX.md` must end Phase 2 in 1:1 correspondence with the `docs/` tree:
  - Every file in `docs/**/*.md` is listed in `DOCS_INDEX.md`
  - Every entry in `DOCS_INDEX.md` points at an existing file
  - The reference to `docs/dev/CONTRIBUTING.md` STAYS during Phase 2 (the file still exists; Phase 3 owns its fate per D-19)
  - The reference to `CHANGELOG.md` (root-relative, `spec_classifier/CHANGELOG.md`) is preserved
  - Add an entry pointing at the `.planning/archive/CURRENT_STATE-*.md` archive (or remove the `CURRENT_STATE.md` reference if the index lists it)
- **D-17:** Quick Start runnability for both READMEs:
  - Plan 02-?? executes the documented Quick Start commands verbatim and confirms they produce a working pipeline run
  - PASS-WITH-CAVEAT path for missing INPUT files (mirrors Phase 1 D-11 W-5 pattern)
  - Smoke test: at minimum `.\run.ps1 -Vendor huawei -NoAi -SkipTests` after each README refresh

### CONTRIBUTING.md Handling (cross-phase coordination)

- **D-18:** During Phase 2 DOC-03 audit, the existing `spec_classifier/docs/dev/CONTRIBUTING.md` (75 lines) is treated as legacy:
  - Read and assess: is it pre-GSD? does it reference retired prompts (`prompts/00..08`)?
  - If pre-GSD content: mark in `02-CONTRIBUTING-AUDIT.md` (a small artifact in `.planning/phases/02-docs/`) noting Phase 3 should handle archival
  - During Phase 2 itself, do NOT delete or rewrite this file — leave it tracked, just flag it
  - DOCS_INDEX.md continues to list it through Phase 2
- **D-19:** Phase 3 WF-02 lands a NEW `CONTRIBUTING.md` at the *repo root* documenting the GSD development cycle. The existing `spec_classifier/docs/dev/CONTRIBUTING.md` is then either archived or rewritten with a forwarding pointer — that decision belongs to Phase 3.
- **D-20:** Naming-collision risk: with both files present transiently between Phase 2 and Phase 3, contributors might wonder which is canonical. Add a one-line note in `spec_classifier/docs/dev/CONTRIBUTING.md` during Phase 2 audit: "Note: this file describes pre-GSD conventions. The current GSD-native development cycle will be documented at `<repo-root>/CONTRIBUTING.md` in Phase 3 (WF-02)." (Adjust wording to match what's actually true after audit.)

### Honor "Do Not Fix" Framing

- **D-21:** Throughout DOC-03 audit, when a doc references load-bearing tech-debt items (per `.planning/codebase/CONCERNS.md` BLOCKER and IMPORTANT sections), the audit:
  - Does NOT propose to fix the underlying tech debt
  - Does NOT remove the doc references to those items
  - DOES verify the references are still accurate (e.g. `power_cord` STILL has `hw_type=None`, `_E8_NO_HW_TYPE_DEVICES` STILL exists at the cited line)
  - May add a "see `.planning/codebase/CONCERNS.md`" pointer where relevant
- **D-22:** Specifically protected items (touch only to verify references stay accurate):
  - `power_cord` `hw_type=None` (per Phase 1 + PROJECT.md)
  - `_E8_NO_HW_TYPE_DEVICES` whitelist
  - `spec_classifier/src/core/parser.py` Dell-specificity
  - `spec_classifier/batch_audit.py` reading from `*_annotated.xlsx`
  - `HW_TYPE_VOCAB` duplication between `classifier.py` and `batch_audit.py`
  - YAML rule order load-bearing first-match-wins

### Phase 2 Verification Gate (Strict)

- **D-23:** Verifier reads EVERY doc end-to-end. Phase 2 verifier-agent prompt explicitly instructs reading each file in DOC-01..05 scope line-by-line and flagging any contradiction with the live code. ~3,356 lines total, fits comfortably in an Opus context window.
- **D-24:** Verification gate steps (analog of Phase 1 D-11):
  1. **Cross-reference integrity:** every file path / line number reference in every doc points at something that exists. `git grep` for known-bad patterns (e.g., references to `commits.txt`, `CURRENT_STATE.md` outside the archive) returns 0 matches.
  2. **DOCS_INDEX 1:1:** Every `docs/**/*.md` is in `DOCS_INDEX.md`; every entry in `DOCS_INDEX.md` exists. Negative-control: `comm -3 <(ls docs-tree-files) <(grep -o pattern DOCS_INDEX.md)` returns empty.
  3. **Quick Start runnability:** `.\run.ps1 -Vendor huawei -NoAi -SkipTests` from repo root after following root README's Quick Start verbatim — exits 0, produces fresh `OUTPUT/huawei_run/run-...`. Same for `spec_classifier/README.md`'s documented commands.
  4. **End-to-end read pass:** Verifier reads each of the 13+ doc files end-to-end; emits `READ_REPORT.md` with per-file findings (drift / accurate / unclear). Any HIGH-severity drift blocks the gate.
  5. **Goldens unchanged:** `git diff <pre-Phase-2..HEAD> -- spec_classifier/golden/` empty. (Phase 2 is doc-only; goldens MUST not move.)
  6. **Pytest still green:** `pytest tests/ -v --tb=short` from `spec_classifier/` exits 0; skip-ratio gate not tripped (W-5 INPUT precondition probe pattern from Phase 1 carries forward).
  7. **Diff-review checkpoint:** `git diff --stat HEAD~N..HEAD` review before final commits land (mirrors Phase 1 D-11 step 5).
- **D-25:** "Read every doc" approach is the user's explicit choice for highest confidence. The verifier-agent token cost is acceptable; Phase 2 is the natural moment to lock in doc accuracy before Phase 3 lands `CONTRIBUTING.md` referencing these docs.

### No New Docs

- **D-26:** Per PROJECT.md Out of Scope, no separate onboarding guide is created in Phase 2. Onboarding content lives in: root README (Quick Start), `spec_classifier/README.md` (full CLI), and Phase 3's `CONTRIBUTING.md` (GSD cycle).
- **D-27:** No "MIGRATION.md", "ROADMAP.md" (different from `.planning/ROADMAP.md`), or other invented docs. The only NEW file Phase 2 creates is the root `README.md` (because it's currently empty) and the `.planning/archive/CURRENT_STATE-2026-05-10.md` (the archived copy).

### Claude's Discretion

- Plan structuring: I expect 4–5 plans (one per requirement is natural here, with a final verification-gate plan analogous to Phase 1's 01-04). Defer to planner.
- Commit grouping: one commit per requirement (HYG-01/02/03 pattern from Phase 1). Defer to planner.
- Translation tone: keep technical, no flourish. Match the existing root CLAUDE.md's English style.
- Whether to also check `prompts/COWORK_OPUS_FULL_AUDIT.md` (which Phase 1 only username-scrubbed) for stale content — DEFAULT NO. Phase 3 owns prompts/.
- Order of operations within Phase 2: my recommendation is DOC-04 first (CLAUDE.md split + translation establishes the "deep reference" before READMEs link to it), then DOC-01/02/03/05 in any order. Planner can decide.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project policy and "do not fix" rules

- `.planning/PROJECT.md` — milestone scope, "Done" definition, Out of Scope (especially "Keep both CLAUDE.md files; root = thin pointer"; "Translate to English not selected at PROJECT level — locked here in 02-CONTEXT.md instead")
- `.planning/REQUIREMENTS.md` §Docs — DOC-01 through DOC-05 in their authoritative phrasing
- `.planning/codebase/CONCERNS.md` §BLOCKER and §IMPORTANT — the load-bearing tech debt the audit MUST acknowledge but NOT fix

### Phase 1 carry-forward decisions

- `.planning/phases/01-hygiene/01-CONTEXT.md` D-01 (placeholder convention — already applied; affects how docs reference paths post-scrub)
- `.planning/phases/01-hygiene/01-CONTEXT.md` D-04 (`C:\venv\` stays literal in docs — applies to DOC-01/02 too)
- `.planning/phases/01-hygiene/01-CONTEXT.md` D-11 (verification gate pattern — Phase 2 D-23/D-24 adapts it for docs)
- `.planning/phases/01-hygiene/01-CONTEXT.md` D-21 (PASS-WITH-CAVEAT for missing INPUT — applies to Phase 2 Quick Start runnability checks)
- `.planning/phases/01-hygiene/01-SUMMARY.md` — what landed; informs DOC-02 and DOC-04 about post-Phase-1 reality

### Codebase map (where things live)

- `.planning/codebase/STRUCTURE.md` — full directory layout; needed for DOC-01 repo-layout note
- `.planning/codebase/STACK.md` — language/runtime/dep matrix; informs README install instructions
- `.planning/codebase/ARCHITECTURE.md` — pipeline pattern; informs `TECHNICAL_OVERVIEW.md` audit
- `.planning/codebase/CONVENTIONS.md` — code style + business rules + alias semantics; cross-check source for DOC-04 deep CLAUDE.md
- `.planning/codebase/TESTING.md` — pytest invocation, skip-ratio gate; informs `TESTING_GUIDE.md` audit
- `.planning/codebase/INTEGRATIONS.md` — OpenAI integration details; informs CLI ref and operational notes audits

### Existing docs (subjects of the audit)

- `CLAUDE.md` (root, 130 lines, English) — current; will be rewritten per D-01/D-02
- `spec_classifier/CLAUDE.md` (303 lines, Russian) — current; will be translated + content split per D-01/D-02/D-04
- `README.md` (root, 0 lines) — empty; will be written from scratch per D-10
- `spec_classifier/README.md` (286 lines) — will be refreshed per D-12/D-13
- `spec_classifier/CHANGELOG.md` (258 lines) — will be refreshed per D-07
- `spec_classifier/CURRENT_STATE.md` (95 lines) — will be archived per D-08
- `spec_classifier/docs/DOCS_INDEX.md` (29 lines) — must be 1:1 with docs/ tree per D-16
- 13 files under `spec_classifier/docs/` — audited per D-14/D-15

### Discussion source-of-truth

- `.planning/phases/02-docs/02-DISCUSSION-LOG.md` — full Q&A trace for this phase

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- **Verification gate pattern from Phase 1.** D-11's 5-step gate is reused here as 7 steps in D-24. The `Invoke-GitGrepExclPlanning` PowerShell helper from Phase 1 Plan 04 (W-1 fix) is reusable for DOCS_INDEX cross-reference checks. The INPUT-presence precondition probe (W-5 fix) is reusable for Quick Start runnability checks.
- **The `.planning/codebase/` map.** All 7 codebase docs are accurate as of 2026-05-09/10. They ARE NOT subject to Phase 2 audit (out of scope; not in `docs/` tree). They ARE used as reference material — when the audit needs to know "what does the code actually do today", the codebase map answers without re-reading source.
- **`spec_classifier/CLAUDE.md` business-rule sections** are already accurate (Phase 1 didn't touch prose, only username strings). Translation preserves accuracy.

### Established Patterns

- **Code-only repo policy** (carried forward): docs do not embed credentials, INPUT files, or paths with the user's username (Phase 1 enforced).
- **Russian-language convention for project narrative** (existing): the deep CLAUDE.md and rule-file comments use Russian. D-04 changes this for the deep CLAUDE.md only; YAML rule comments stay Russian.
- **Cross-link discipline**: every doc that points at another doc uses relative paths from repo root or from its own location consistently. Audit must preserve this.

### Integration Points

- **Phase 3 WF-01 (retire prompts/)** depends on Phase 2 DOC-03 having flagged any docs that reference the retired prompts. The audit should produce a list of cross-references to `prompts/00..08` so Phase 3 knows what to update.
- **Phase 3 WF-02 (root CONTRIBUTING.md)** depends on Phase 2 DOC-04 having translated/finalized `spec_classifier/CLAUDE.md` (so CONTRIBUTING.md can link at it as the canonical deep reference).
- **Phase 3 WF-02 also depends on D-18/D-19/D-20** above — Phase 2's audit of the existing inner CONTRIBUTING.md feeds Phase 3's decision on how to land the root one.

</code_context>

<specifics>
## Specific Ideas

- The user explicitly chose `Strict: read every doc end-to-end` over the lighter options for verification. Highest-confidence pass; matches their pattern from Phase 1 of preferring concrete checkable conditions over trust.
- The user explicitly chose `Translate to English` over keeping Russian or partial bilingual. They want the deep CLAUDE.md to be accessible to future contributors and AI agents.
- The user explicitly chose `Refresh CHANGELOG, archive CURRENT_STATE` (the compromise option, not the cheapest archive-both). Signal: CHANGELOG has ongoing value as release notes; CURRENT_STATE doesn't (GSD's `.planning/STATE.md` replaces it).
- The user explicitly chose `Root = pointer + critical rules` (the middle option) — wants the 5 critical rules accessible even at root level, not just deep. This protects against a contributor running a GSD command at root and missing the load-bearing rules.
- The user explicitly chose `Full top-level intro` for root README — wants someone landing at GitHub root to be able to install and run without descending into `spec_classifier/`. Some overlap with deep README is OK.
- The user explicitly chose `Audit existing in Phase 2, new root in Phase 3` for the CONTRIBUTING.md split — wants Phase 2 to do its job (audit) without inheriting Phase 3 decisions.

</specifics>

<deferred>
## Deferred Ideas

- **Translate YAML rule-file comments (`spec_classifier/rules/*.yaml`)** — explicitly out of scope for Phase 2 (D-06). Rule files are load-bearing; comment translation is risk without benefit. Could be revisited in a future polish milestone.
- **Translate `prompts/COWORK_OPUS_FULL_AUDIT.md`** — that file's prompts are themselves Russian-written. Phase 3 WF-01 retires prompts; translation would be wasted effort. Out of scope for Phase 2.
- **Audit `.planning/codebase/` docs** — out of scope (those are GSD intel artifacts, not project documentation).
- **Migrate CHANGELOG to GSD-managed format** — the format choice is "keep release-notes style, refresh content". A future milestone could move to a `.planning/CHANGELOG.md` GSD-native format. Not this phase.
- **Add a glossary doc** — considered during scout, rejected. The hw_type_taxonomy.md already serves this purpose for taxonomy terms.
- **Auto-generate API/CLI ref from argparse** — out of scope; manual `CLI_CONFIG_REFERENCE.md` is the source of truth.

### Reviewed Todos (not folded)

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 2-Docs*
*Context gathered: 2026-05-10*
