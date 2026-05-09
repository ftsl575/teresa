# Requirements: Teresa — Cleanup & Workflow Setup Milestone

**Defined:** 2026-05-10
**Core Value:** The classifier produces correct, deterministic, audited artifacts for every supported vendor. Everything else is plumbing.

## v1 Requirements

Requirements for this milestone (cleanup + GSD-native workflow setup). Each maps to roadmap phases.

### Hygiene

File cleanup — no behavior changes.

- [ ] **HYG-01**: Hardcoded `C:\Users\G\` username is removed from every committed file (examples, docs, Makefile, configs); replaced with `<USERNAME>` placeholder or `$HOME`/`%USERPROFILE%` style references where appropriate.
- [ ] **HYG-02**: Dual `.gitignore` files (`/.gitignore` and `spec_classifier/.gitignore`) are consolidated into a single root `.gitignore` covering both layers; the redundant one is deleted.
- [ ] **HYG-03**: Dead and orphan files are removed (orphans include unimported modules, `commits.txt`, `.bak`, `.zip`, abandoned scratch files); list of removed files documented in the PR.

### Docs

Documentation refresh — drift fixed, accuracy verified against the codebase.

- [ ] **DOC-01**: Root `README.md` is refreshed — elevator pitch is current, repo layout note matches reality, Quick Start instructions are runnable as written.
- [ ] **DOC-02**: `spec_classifier/README.md` is refreshed — CLI usage, config layering, output paths, and golden workflow all match the current code; no broken cross-references.
- [ ] **DOC-03**: `spec_classifier/docs/` tree is audited — `DOCS_INDEX.md` lists every present doc, every listed doc still exists, stale content is removed or rewritten, broken cross-references are fixed.
- [ ] **DOC-04**: Root `CLAUDE.md` and `spec_classifier/CLAUDE.md` overlap is removed — root keeps a thin pointer + repo-layout note, the deep reference stays in `spec_classifier/CLAUDE.md`, no business rule or pipeline detail is duplicated across both.
- [ ] **DOC-05**: `spec_classifier/CHANGELOG.md` and `spec_classifier/CURRENT_STATE.md` are refreshed against current state OR archived (`.planning/archive/` or removed) with a note on the replacement source-of-truth (git log, GSD artifacts).

### Workflow

GSD-native development cycle — adopt and document.

- [ ] **WF-01**: Pre-GSD prompt templates (`spec_classifier/prompts/00_VENDOR-RECON.md` through `08_CHATGPT-SYSTEM-PROMPTS.md` plus `COWORK_OPUS_FULL_AUDIT.md`) are retired — deleted, archived under `.planning/archive/`, or clearly marked as deprecated with a pointer to the GSD-native equivalent. `prompts/README.md` updated accordingly.
- [ ] **WF-02**: `CONTRIBUTING.md` exists at the repo root documenting the GSD development cycle (`/gsd-discuss-phase` → `/gsd-plan-phase` → `/gsd-execute-phase` → `/gsd-verify-work`), how to run tests, how to add a vendor (pointer to `spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md`), and the project's "do not fix" tech-debt rules.

## v2 Requirements

Acknowledged but deferred to a later milestone.

### Classification

- **CLAS-01**: Improve classification rules (next-milestone scope; specifics TBD by audit findings)
- **CLAS-02**: New vendor onboarding (next-milestone scope; specific vendor TBD)

### Cross-Platform

- **PLAT-01**: POSIX launcher equivalent (`run.sh`) — enables Linux/macOS contributors and CI
- **PLAT-02**: De-Windows the GUI (`teresa_gui.py` `os.startfile`, `setx`-based key storage)

### Automation

- **AUTO-01**: CI pipeline (GitHub Actions or equivalent) running pytest + audits on push
- **AUTO-02**: Pre-commit hook for rule-id schema validation

## Out of Scope

Explicitly excluded for this milestone.

| Feature | Reason |
|---------|--------|
| Classification rule changes | Hygiene first; rule edits land in a follow-up milestone |
| Cross-platform launchers (`run.sh`) | User chose Windows-only; deferred to PLAT-01 |
| Merging the two `CLAUDE.md` files into one | User chose to keep both; root thin pointer + deep reference under `spec_classifier/` |
| Auto-regenerating `CLAUDE.md` from a GSD baseline | User chose to preserve hand-written content |
| Separate onboarding guide doc | Folded into README refresh + `CONTRIBUTING.md` |
| Fixing `power_cord` `hw_type=None` | Intentional per `spec_classifier/CLAUDE.md`; load-bearing; recovery commit `c3c7cb6` exists |
| Fixing `batch_audit.py` reading from `*_annotated.xlsx` | Project CLAUDE.md says "do not fix as part of unrelated work"; needs dedicated migration |
| Moving `spec_classifier/src/core/parser.py` (Dell-specific) | Standalone refactor; out of scope here |
| Deduplicating `HW_TYPE_VOCAB` between `classifier.py` and `batch_audit.py` | Tracked in CONCERNS but not selected for this milestone |
| Touching YAML rule order | Load-bearing first-match-wins; cleanup must not reorder |
| Test reorganization that affects skip-ratio | Pytest gates at `skipped/total > 0.50`; cleanup must not trip it |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| HYG-01 | TBD | Pending |
| HYG-02 | TBD | Pending |
| HYG-03 | TBD | Pending |
| DOC-01 | TBD | Pending |
| DOC-02 | TBD | Pending |
| DOC-03 | TBD | Pending |
| DOC-04 | TBD | Pending |
| DOC-05 | TBD | Pending |
| WF-01 | TBD | Pending |
| WF-02 | TBD | Pending |

**Coverage:**
- v1 requirements: 10 total
- Mapped to phases: 0 (filled during roadmap creation)
- Unmapped: 10 (will be 0 after roadmap)

---
*Requirements defined: 2026-05-10*
*Last updated: 2026-05-10 after initial definition*
