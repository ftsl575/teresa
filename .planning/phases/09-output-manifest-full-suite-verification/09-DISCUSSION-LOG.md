# Phase 9: Output manifest & full-suite verification - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-07
**Phase:** 9-Output manifest & full-suite verification
**Areas discussed:** Generation model, Writer & trigger, Format & language, E2E verification

---

## Generation model (README.md production)

| Option | Description | Selected |
|--------|-------------|----------|
| Static template | Hardcoded table documenting the canonical frozen v1.2 artifact set; deterministic, byte-stable, trivially unit-testable; no runtime tree walk. | ✓ |
| Dynamic scan | Walk the output tree after a run, emit a row per file found; always matches reality incl. conditional files, but varies run-to-run and still needs a static purpose map. | |
| Hybrid | Static lookup table cross-checked against produced files, warn/fail on divergence; strongest accuracy, most code. | |

**User's choice:** Static template
**Notes:** v1.2 freezes the artifact set, so a static table is the simplest path to SC#1; "matches an actual run" is backed by a unit test pinning the table to the known set rather than by runtime introspection.

---

## Writer & trigger (who writes README.md, and when)

| Option | Description | Selected |
|--------|-------------|----------|
| main.py, every run | main.py writes README.md to output_root at end of each invocation (idempotent static bytes); manifest always exists even on classify-only runs. | ✓ |
| cluster_audit.py, last | Final process in the chain writes it, so README implies a complete pipeline ran; but classify-only runs get no manifest. | |
| Standalone in run.ps1 | Dedicated writer invoked as a final launcher step; clean separation but only appears via the launcher. | |

**User's choice:** main.py, every run
**Notes:** Static content makes repeated writes harmless (run.ps1's per-vendor loop overwrites identical bytes). Captured follow-on decisions: write once per main() invocation at output_root (not per-spec inside _run_single), and centralize the writer helper in run_manager.py mirroring create_spec_folder.

---

## Format & language

### Row granularity

| Option | Description | Selected |
|--------|-------------|----------|
| Pattern rows, grouped | One row per artifact type with placeholder names, grouped under READY/SPLIT/AUDIT headings (~14 rows), stable regardless of spec count. | ✓ |
| Flat pattern table | Same pattern rows in one flat table with a Bucket column. | |
| Literal enumerated | One row per actual file per vendor/spec; exhaustive but explodes with spec count and contradicts the static model. | |

**User's choice:** Pattern rows, grouped

### Purpose-column language

| Option | Description | Selected |
|--------|-------------|----------|
| Russian | Operator-facing language; matches READY's human-facing convention. | ✓ |
| English | Matches SPLIT technical convention and repo English-doc baseline. | |
| Bilingual | RU + EN; most accessible, widest table. | |

**User's choice:** Russian
**Notes:** README reads as an operator-facing index of the OUTPUT folder; only the prose "purpose" text is Russian — filenames, bucket names, and path structure stay as-is. Columns fixed as file → bucket → purpose.

---

## E2E verification (TEST-01 / SC#2–SC#4)

| Option | Description | Selected |
|--------|-------------|----------|
| Manifest unit test | Assert the writer emits README.md at output_root with the expected static table; pins template against drift. | ✓ |
| Layout assertion in test_output_structure.py | Extend existing test: run yields README.md + top level only expected buckets, no flat/timestamp/TOTAL leftovers. | ✓ |
| New full E2E pytest test | Drive main.py → batch_audit → cluster_audit in one test asserting exactly {READY, SPLIT, AUDIT, README.md}; strongest but heaviest, overlaps existing coverage. | |
| Real-data manual run in VERIFICATION | Real end-to-end run (6 vendors, --no-ai) recorded in VERIFICATION.md + milestone-wide full pytest green + goldens byte-equal. | ✓ |

**User's choice:** Manifest unit test + Layout assertion in test_output_structure.py + Real-data manual run in VERIFICATION (the heavy 3-process E2E pytest test was deliberately NOT selected)
**Notes:** The three selected checks together prove SC#2 without the overlap/cost of a full 3-process E2E test.

---

## Claude's Discretion

- Exact helper name/signature for the manifest writer in run_manager.py.
- Exact Russian wording of each artifact purpose description.
- Markdown rendering of the grouped table (one table per bucket vs. single table with sub-headers).
- Precise placement of the write_manifest call within main() (must run once per invocation).
- Which specific path/layout assertions to add/realign in test_output_structure.py.

## Addendum — scope addition after initial discussion

User directed adding a separate task to Phase 9: remove the dead
`{vendor}_run` / `hp_run` matchers from `cluster_audit._detect_vendor_from_path`
(WR-01 from the Phase 8 review). `batch_audit` had these removed in Phase 8
(D-07); `cluster_audit` was left untouched, producing a divergence + duplicated
dead code on the same SPLIT/AUDIT tree. Same discipline requested: grep live
callers, confirm vendor detection works for SPLIT/AUDIT paths (`<vendor>` =
folder name), update tests if affected. Captured in 09-CONTEXT.md as D-11..D-13
(domain deliverable #3, classified path-detection-not-audit logic per Phase 8
D-08). No question/option round — direct scope instruction.

## Deferred Ideas

- Artifact content changes (column trimming, translation, new summary docs) — v1.3 (CONTENT-01..03).
- Per-vendor knowledge docs (VKB-01..04) — still deferred.
- spec_classifier/CLAUDE.md OUTPUT-layout block still shows the pre-v1.2 flat/*_run/TOTAL scheme — doc-drift fix for a future docs-update pass, out of this phase's scope.
- Larger batch_audit.py tech-debt (Excel-reading, alias sprawl, god-object) — tracked in CONCERNS.md, not touched.
