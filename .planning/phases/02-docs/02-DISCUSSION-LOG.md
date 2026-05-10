# Phase 2: Docs - Discussion Log

> **Audit trail only.** Not consumed by downstream agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-10
**Phase:** 02-docs
**Areas discussed:** CLAUDE.md split rule, CHANGELOG/CURRENT_STATE fate, Language convention, Verification gate, Root README scope, CONTRIBUTING split

---

## Round 1: Core gray areas

### CLAUDE.md split rule

| Option | Description | Selected |
|--------|-------------|----------|
| Root = pointer only | ~30 lines: layout note + pointer; ALL business rules move to deep file. | |
| Root = pointer + critical rules | Root keeps the 5 critical rules so any GSD command run at root sees them; deep owns everything else. | ✓ |
| Root = full English mirror | Root stays comprehensive English; deep stays Russian. Heavy split-by-audience. | |

**User's choice:** Root = pointer + critical rules.
**Notes:** Concern was that a contributor or future-Claude running a GSD command at repo root might miss the load-bearing business rules. Keeping the 5 critical rules at root is a safety net.

### CHANGELOG.md and CURRENT_STATE.md fate

| Option | Description | Selected |
|--------|-------------|----------|
| Archive both | Both move to `.planning/archive/` with forwarding pointers. | |
| Refresh both against current state | Rewrite both to match reality. | |
| Refresh CHANGELOG, archive CURRENT_STATE | CHANGELOG keeps as release-notes; CURRENT_STATE replaced by GSD STATE.md. | ✓ |

**User's choice:** Refresh CHANGELOG, archive CURRENT_STATE.
**Notes:** Signal that CHANGELOG has ongoing value (humans read release notes), but `.planning/STATE.md` makes CURRENT_STATE.md redundant.

### Language convention for deep CLAUDE.md

| Option | Description | Selected |
|--------|-------------|----------|
| Keep Russian | Deep file stays Russian. Audience split. | |
| Translate to English | Full RU→EN translation of `spec_classifier/CLAUDE.md`. | ✓ |
| Bilingual key sections | Translate just business rules / do-not-fix list. | |

**User's choice:** Translate to English.
**Notes:** Wants accessibility for future contributors and AI agents. ~303 lines of dense technical content. Single executor pass with technical-accuracy review.

### Phase 2 verification gate

| Option | Description | Selected |
|--------|-------------|----------|
| Cross-ref + index + spot-read | DOCS_INDEX 1:1 + cross-refs valid + Quick Start runnable + spot-read 3 random. | |
| Strict: read every doc | Same as Recommended PLUS read every doc end-to-end line-by-line. Highest confidence. | ✓ |
| Light: cross-ref + spot-check | Just (a) and (b) plus single spot-read. Fastest gate. | |

**User's choice:** Strict.
**Notes:** Same pattern as Phase 1 — preferred concrete checkable conditions over trust. Acceptable verifier-agent token cost given Phase 2 is the natural moment to lock doc accuracy before Phase 3.

---

## Round 2: Discovered scope clarifications

### Root README scope

| Option | Description | Selected |
|--------|-------------|----------|
| Minimal repo intro | ~30–50 lines: intro + repo layout + pointer to deep README. | |
| Full top-level intro | ~80–120 lines: pitch + Quick Start + key commands. Self-contained for GitHub-arrivers. | ✓ |
| One-liner + pointer only | ~5 lines: just point at spec_classifier/. | |

**User's choice:** Full top-level intro.
**Notes:** Discovered that root README.md is currently EMPTY (0 lines). DOC-01 is "create" not "refresh". User wants someone landing at GitHub root to be able to install and run without descending into `spec_classifier/`. Acceptable overlap with deep README.

### CONTRIBUTING.md handling (Phase 2 vs Phase 3 coordination)

| Option | Description | Selected |
|--------|-------------|----------|
| Audit existing in Phase 2, new root in Phase 3 | Two files transiently; clear scopes (inner: spec_classifier, root: GSD cycle). | ✓ |
| Delete inner now, only root in Phase 3 | Treat existing inner as Phase 3's predecessor; archive in Phase 2. | |
| Merge into root in Phase 3 | Phase 2 leaves inner alone; Phase 3 absorbs it. | |

**User's choice:** Audit existing in Phase 2, new root in Phase 3.
**Notes:** Discovered `spec_classifier/docs/dev/CONTRIBUTING.md` already exists (75 lines). User wants Phase 2 to do its job without inheriting Phase 3 decisions. Phase 2 audit will flag whether inner is pre-GSD; Phase 3 WF-02 then decides archive vs merge.

---

## Claude's Discretion

- Plan structuring (4–5 plans recommended; planner decides exact split)
- Commit grouping (one commit per requirement; planner decides)
- Translation tone (technical, no flourish; match root CLAUDE.md style)
- Whether to audit `prompts/COWORK_OPUS_FULL_AUDIT.md` for stale content (default NO — Phase 3 owns prompts/)
- Order of operations (recommended: DOC-04 first to establish deep reference, then others)

## Deferred Ideas

- Translate YAML rule-file comments — out of scope (load-bearing, risk without benefit)
- Translate `prompts/COWORK_OPUS_FULL_AUDIT.md` — Phase 3 retires prompts/
- Audit `.planning/codebase/` docs — GSD intel, not project documentation
- Migrate CHANGELOG to GSD-managed format — future polish milestone
- Add glossary doc — `hw_type_taxonomy.md` already serves
- Auto-generate API/CLI ref from argparse — manual reference is source of truth
