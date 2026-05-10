# Phase 3: Workflow - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in `03-CONTEXT.md` — this log preserves the alternatives considered.

**Date:** 2026-05-10
**Phase:** 3-Workflow
**Areas discussed:** prompts/ retire mechanism, Inner CONTRIBUTING.md fate, Root CONTRIBUTING.md depth/scope, Deep CLAUDE.md cycle handling

---

## prompts/ retire mechanism

### Q1.1 — Top-level approach for retiring `spec_classifier/prompts/` (10 .md files, 1345 lines)

| Option | Description | Selected |
|--------|-------------|----------|
| `git mv` to `.planning/archive/prompts-2026-05-10/` | Mirrors Phase 2 D-08; history preserved by git mv; cleanest end state | ✓ |
| Replace each file with a 1-2 line deprecation stub | spec_classifier/prompts/ stays; per-file pointer to GSD equivalent; preserves file paths for old external references | |
| Delete the whole folder | spec_classifier/prompts/ removed entirely; history lives in git only; cleanest filesystem | |

**User's choice:** archive via `git mv` (Recommended).
**Notes:** Symmetric with Phase 2 D-08 (CURRENT_STATE.md archive). Date suffix `2026-05-10` lets future archives stack.

### Q1.2 — What does the archived folder's README look like?

| Option | Description | Selected |
|--------|-------------|----------|
| Replace original Russian README with English archive note + per-file mapping table | English archive header + 00→NEW_VENDOR_GUIDE / 01→/gsd-discuss-phase / 02→/gsd-plan-phase / 03→/gsd-execute-phase / 04→/gsd-verify-work / 05→/gsd-audit-fix / 06→batch_audit.py + /gsd-plan-phase / 07→/gsd-docs-update / 08→no GSD equivalent. Original 0X_*.md files preserved verbatim | ✓ |
| Preserve original Russian README + add separate ARCHIVE-NOTE.md | Two README-like files in the archive; cleaner historical preservation but adds a file | |
| Plain `git mv` only — no README rewrite | All explanatory burden pushed into /CONTRIBUTING.md | |

**User's choice:** Replace + per-file mapping (Recommended).
**Notes:** Frees future contributors from needing to read Russian to understand what was there. Original Russian content (in 0X_*.md files) stays as historical record.

### Q1.3 — How should `COWORK_OPUS_FULL_AUDIT.md` be handled?

| Option | Description | Selected |
|--------|-------------|----------|
| Same archive treatment | Moved alongside 00..08; mentioned in mapping as audit-mode equivalent for /gsd-audit-fix or /gsd-code-review | ✓ |
| Archive but flag separately as 'audit-mode' rather than 'cycle-step' | Distinct section in README; slightly more nuance | |
| Delete it | Tightly coupled to a past audit; less reusable historical reference | |

**User's choice:** Same archive treatment (Recommended).
**Notes:** Uniform treatment minimizes per-file decisions in the planner.

### Q1.4 — `LAUNCHER_README.md:52` reference to `prompts/00_VENDOR-RECON.md` — where to repoint?

| Option | Description | Selected |
|--------|-------------|----------|
| Repoint to `spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md` | Natural successor; self-contained; no archive indirection | ✓ |
| Repoint to the archive path | Preserves exact content the line was pointing at; sends contributors into archive | |
| Repoint to `/CONTRIBUTING.md` § 'Adding a vendor' | Slightly more indirection but consistent with 'CONTRIBUTING.md is the entry point' | |

**User's choice:** Repoint to `NEW_VENDOR_GUIDE.md` (Recommended).
**Notes:** User prefers direct, self-contained pointers over indirection chains.

---

## Inner CONTRIBUTING.md fate

### Q2.1 — What happens to `spec_classifier/docs/dev/CONTRIBUTING.md` (77 lines, Russian, with the Phase-2 forwarding note)?

| Option | Description | Selected |
|--------|-------------|----------|
| `git mv` to `.planning/archive/CONTRIBUTING-2026-05-10.md` | Same archive pattern; history preserved; spec_classifier/docs/dev/ freed of LEGACY-flagged file; /CONTRIBUTING.md unambiguously canonical | ✓ |
| Shrink to a 5-line forwarding-only stub | DOCS_INDEX.md keeps the entry but the link target effectively redirects | |
| Delete it | Cleanest filesystem; loses git-mv history continuity | |
| Translate-and-keep as a deeper spec_classifier-specific addendum | More work; introduces a 2-doc structure to maintain | |

**User's choice:** `git mv` to `.planning/archive/` (Recommended).
**Notes:** Same archive-preference signal as D-01.

### Q2.2 — How should `spec_classifier/docs/DOCS_INDEX.md` handle its line 27 entry?

| Option | Description | Selected |
|--------|-------------|----------|
| Drop the line entirely | DOCS_INDEX.md preserves Phase 2 D-16 1:1 invariant automatically; /CONTRIBUTING.md NOT added (DOCS_INDEX scoped to spec_classifier/docs/) | |
| Repoint to `/CONTRIBUTING.md` (with note) | Keeps the row, breaks docs/-scoped invariant slightly | |
| Drop the line AND add a 'See also' breadcrumb under § Conventions | Same as option 1 plus lightweight breadcrumb to canonical doc | ✓ |

**User's choice:** Drop the line + 'See also' breadcrumb.
**Notes:** Wants DOCS_INDEX.md to stay docs/-scoped (Phase 2 D-16 invariant) but not lose the breadcrumb to the new canonical doc.

### Q2.3 — DOCS_INDEX.md line 36 (`prompts/README.md` row) — same treatment?

| Option | Description | Selected |
|--------|-------------|----------|
| Drop the line entirely | Symmetric with how docs/dev/CONTRIBUTING.md is handled; archive is curiosity not entry point | ✓ |
| Repoint to `.planning/archive/prompts-2026-05-10/README.md` | Surfaces the archive in the index; mixes 'live' and 'historical' entries | |
| Drop the line AND extend the 'See also' breadcrumb to mention the prompts archive | Lightweight extra info for archaeology purposes | |

**User's choice:** Drop the line entirely (Recommended).
**Notes:** Consistent with the inner-CONTRIBUTING decision; symmetric treatment.

---

## Root CONTRIBUTING.md depth/scope

### Q3.1 — What overall depth should `/CONTRIBUTING.md` target?

| Option | Description | Selected |
|--------|-------------|----------|
| Minimum (~80–120 lines) | Success-criteria mandates only: GSD cycle + pytest/skip-ratio + NEW_VENDOR_GUIDE pointer + 'do not fix' verbatim + 'where to look first' table | |
| Medium (~150–200 lines) | Above + PR workflow, commit-message style, code-style pointers, 'how to extend the audit' pointer | ✓ |
| Rich (~250+ lines) | Above + tool-roles, vendor-onboarding overview, full PR template with checklist | |

**User's choice:** Medium (~150–200 lines).
**Notes:** Wants enough to teach a fresh contributor the workflow without bloating into rich content that risks duplicating CLAUDE.md / NEW_VENDOR_GUIDE.md.

### Q3.2 — Tone/voice — should `/CONTRIBUTING.md` mention specific AI tools and roles?

| Option | Description | Selected |
|--------|-------------|----------|
| Tool-agnostic — GSD cycle as the workflow, no specific AI tool mentioned | 'use Claude Code or any AI coding agent that runs the GSD commands'; ages well; mirrors root README/root CLAUDE.md style | ✓ |
| Mention Claude Code as primary, others as alternative | Pragmatic given how repo is actually driven; might bias future contributors | |
| Document the historical Cursor/Claude/ChatGPT role split from deep CLAUDE.md | Preserves project history; reinforces a workflow GSD has effectively replaced | |

**User's choice:** Tool-agnostic (Recommended).
**Notes:** Wants /CONTRIBUTING.md to age well; GSD commands, not specific AI tools, are the canonical surface.

### Q3.3 — How verbatim should the 'do not fix' tech-debt rules be transcribed?

| Option | Description | Selected |
|--------|-------------|----------|
| Verbatim copy from PROJECT.md Out of Scope + CONCERNS.md BLOCKER one-liners + pointer | Single source of truth survives; wording fixed; future updates need mirroring once | ✓ |
| Restated in CONTRIBUTING.md voice + CONCERNS.md pointer | More natural-reading but adds drift surface | |
| Pointer-only, no inline list | Lightest-touch but defeats success-criteria intent (visibility) | |

**User's choice:** Verbatim + pointer (Recommended).
**Notes:** Single source of truth + visibility in CONTRIBUTING.md.

### Q3.4 — GSD-cycle section format — how literal?

| Option | Description | Selected |
|--------|-------------|----------|
| Literal command-by-command with one-liner per command | `1. Discuss — /gsd-discuss-phase <N>. ...` + footnote 'see /gsd-help'; reproducible | ✓ |
| Conceptual stages + 'see /gsd-help' pointer | More resilient to renames; less actionable cold | |
| Diagram + literal commands | Visual aid; adds maintenance surface | |

**User's choice:** Literal command-by-command (Recommended).
**Notes:** Same preference for direct, self-contained, reproducible documentation.

---

## Deep CLAUDE.md cycle handling

### Q4.1 — End state for the legacy block in `spec_classifier/CLAUDE.md` (Tool Roles + Development Cycle table + R1–R5 Hard Rules + Recommended Models + Prompts—Location footer)

| Option | Description | Selected |
|--------|-------------|----------|
| Replace whole block with 1-paragraph 'Development Cycle' pointing to /CONTRIBUTING.md | Removes ~50 lines of obsolete narrative; deep CLAUDE.md stays focused on taxonomy/E-codes/business rules | ✓ |
| Keep legacy as 'Historical: pre-GSD cycle' with header note | Preserves R1–R5 + model-selection narrative; risk of contributors mistaking historical for canonical | |
| Minimal: only update the Prompts—Location footer | Smallest delta; risks failing ROADMAP success-criteria 3 | |

**User's choice:** Replace whole legacy block (Recommended).
**Notes:** Cleanest signal yet that legacy narrative is fully retired, not preserved-but-demoted. The 5 critical business rules already deduplicated to root CLAUDE.md per Phase 2 D-01 stay where they are.

### Q4.2 — Root `CLAUDE.md` § Tooling roles (lines 71–74) handling

| Option | Description | Selected |
|--------|-------------|----------|
| Replace with: 'The canonical development cycle (Discuss → Plan → Execute → Verify, GSD-native) is documented in /CONTRIBUTING.md.' | Symmetric with deep CLAUDE.md change; one sentence; preserves .cursor/ informational note | ✓ |
| Drop the sentence entirely | Slightly shorter root CLAUDE.md; one less cross-link | |
| Replace AND remove § Tooling roles section header | Tighter structure; small refactor | |

**User's choice:** Replace (symmetric) (Recommended).
**Notes:** Consistency with deep CLAUDE.md update; same one-sentence shape.

### Q4.3 — Verification gate adaptation

| Option | Description | Selected |
|--------|-------------|----------|
| Adapt the same 7-step pattern, doc-only scope | Greps + DOCS_INDEX 1:1 + Quick Start runnability + end-to-end read pass + goldens + pytest + diff-review; proven shape; same artifacts (03-VERIFICATION.md, 03-READ-REPORT.md, 03-SUMMARY.md) | ✓ |
| Scoped 4-step gate (greps + DOCS_INDEX + pytest + diff-review) | Smaller; faster; risk of regression in /CONTRIBUTING.md prose isn't caught | |
| Defer the gate design to the planner | Maximum flexibility; risk of planner repeating Phase 2 from scratch | |

**User's choice:** Adapt the same 7-step pattern (Recommended).
**Notes:** Same Phase 1/2 preference for proven patterns + concrete checkable conditions.

### Q4.4 — `spec_classifier/CHANGELOG.md` historical lines mentioning `prompts/` (lines 44, 208)

| Option | Description | Selected |
|--------|-------------|----------|
| Leave verbatim — historical record | Honors release-notes immutability convention (Phase 2 D-07); add NEW entry under next version banner instead | ✓ |
| Update inline + add new entry | Slightly more navigability; bends historical-record convention | |
| No CHANGELOG entry at all | Risks losing audit trail in CHANGELOG | |

**User's choice:** Leave verbatim + add new entry (Recommended).
**Notes:** Honors release-notes immutability convention without losing the audit trail.

---

## Claude's Discretion

- **Plan structure** — 3–4 plans expected (one per requirement, plus a final verification-gate plan analogous to `01-04` and `02-06`). Defer to planner.
- **Commit grouping** — one commit per requirement (HYG-01/02/03 and DOC-01..05 pattern). Defer to planner.
- **Order of operations within Phase 3** — recommendation: WF-01 first (archives stabilize the cross-ref target list), then WF-02 + cross-ref cleanup, then verification gate. Planner can decide.
- **Exact wording inside the new CHANGELOG entry (D-19)** — the version banner choice and the exact bullet phrasing are planner/executor decisions.
- **Exact PR-workflow paragraph in /CONTRIBUTING.md (D-10 §5)** — the planner picks how much PR-template content to include vs. just describing the convention. Lean toward 'describe the convention' — the repo doesn't currently have a PR template file.
- **Whether to also add /CONTRIBUTING.md to root README.md § 'Learn more' table** — lean YES for discoverability, but it's a 1-line tweak and not a Phase 3 success criterion. Planner's call.

## Deferred Ideas

- Cross-platform launcher (`run.sh`) — v2 backlog (PLAT-01)
- CI pipeline (GitHub Actions running pytest + audits on push) — v2 backlog (AUTO-01); explicitly NOT in /CONTRIBUTING.md
- Pre-commit hook for rule-id schema validation — v2 backlog (AUTO-02)
- Classification rule improvements — v2 backlog (CLAS-01)
- New vendor onboarding — v2 backlog (CLAS-02); pointer-only in /CONTRIBUTING.md per D-14
- Auto-generated PR template (`.github/PULL_REQUEST_TEMPLATE.md`) — repo has no `.github/` tooling today; defer to AUTO-01 CI work
- Translating archived prompts files to English — preserved as Russian historical record per D-02
- Adding a `.planning/archive/README.md` describing the archive convention — each archived item is self-explanatory by name + date suffix; defer until archive count grows
- Translating remaining `spec_classifier/CHANGELOG.md` historical Russian fragments — Phase 2 D-07 already English-unified the refresh; deeper history preserved verbatim
- Refactoring `spec_classifier/CLAUDE.md` into a smaller core file + sub-files — out of scope; defer to a future docs-restructure milestone
- Renaming the milestone — currently 'Cleanup & Workflow Setup' in REQUIREMENTS.md; could be renamed at milestone-close, not a Phase 3 concern
