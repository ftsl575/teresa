# CONTRIBUTING.md Audit — Phase 02 / DOC-03

**File:** `spec_classifier/docs/dev/CONTRIBUTING.md`  
**Audited:** 2026-05-10  
**Verdict:** LEGACY

---

## Scope

This file was assessed per decisions D-18, D-19, D-20 from `02-CONTEXT.md`:
- D-18: Assess as legacy, do not rewrite.
- D-19: Add one-line forwarding note after H1.
- D-20: Phase 3 (WF-02) will create the canonical `CONTRIBUTING.md` at repo root.

Assessment scope: do not propose content changes; document findings and defer to Phase 3.

---

## Pre-GSD Content?

Yes. The file was authored before GSD integration. It describes a development cycle (PRE-CHECK → IMPLEMENT → POST-CHECK) that predates the GSD orchestrator and the current audit cycle (audit_1A–1G). The "Definition of Done" and PR checklist reflect the old manual workflow.

---

## References to Retired Prompts or Scripts

- **No references to prompts/** — the file does not link to any prompt files.
- **No references to scripts/run_*.ps1** — the file does not reference the now-retired `run_full.ps1`, `run_tests.ps1`, or `run_audit.ps1`.
- The file references `config.local.yaml` and `config.local.yaml.example` — both still exist and are accurate.

---

## Russian Residue

The entire file is written in Russian (76 lines, 5 sections). No English translation was applied per D-18 (assess, do not rewrite). The forwarding note (D-19) added below the H1 is in English.

---

## Vendor Coverage Drift

The file references only 3 vendors in its directory tree (Dell, Cisco, HPE) and version history section. The project now supports 6 vendors (Dell, Cisco CCW, HPE, Lenovo, xFusion, Huawei). This drift is NOT fixed per D-18 — it will be corrected when Phase 3 writes the canonical CONTRIBUTING.md.

---

## Technical Accuracy (spot check)

| Claim | Status |
|-------|--------|
| `main.py` entry point | ACCURATE |
| `config.yaml` — vendor_rules, cleaned_spec, paths | ACCURATE |
| `rules/dell_rules.yaml`, `cisco_rules.yaml`, `hpe_rules.yaml` | ACCURATE (partial — 3 of 6 vendors) |
| `src/core/` — parser, normalizer, classifier, state_detector | ACCURATE (note: parser.py is Dell-specific per CONCERNS.md) |
| `VendorAdapter ABC` in `src/vendors/base.py` | ACCURATE |
| `golden/` JSONL regression files in git | ACCURATE |
| `output/` not in git | ACCURATE |
| `config.local.yaml.example` required for first run | ACCURATE |
| `pytest tests/ -v` gate | ACCURATE |
| `--save-golden` flag for Cisco/HPE golden update | ACCURATE |
| SemVer version field in YAML rule files | ACCURATE |

---

## Phase 3 Hand-off

Phase 3 (WF-02) will:
1. Create canonical `CONTRIBUTING.md` at repo root (English, all 6 vendors, GSD-native cycle).
2. Optionally remove or archive `spec_classifier/docs/dev/CONTRIBUTING.md`.
3. Update `DOCS_INDEX.md` link if this file is moved or replaced.

---

## Action Taken in Phase 2

A one-line forwarding note was added directly after the H1 heading in `spec_classifier/docs/dev/CONTRIBUTING.md` per D-19. The body of the file was not changed.

Note text (verbatim):
```
> **Note:** This file describes pre-GSD conventions. The current GSD-native development cycle will be documented at `<repo-root>/CONTRIBUTING.md` in Phase 3 (WF-02). For now, refer to `spec_classifier/CLAUDE.md` § Development Cycle for the active workflow.
```
