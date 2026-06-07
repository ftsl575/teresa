# Phase 9: Output manifest & full-suite verification - Context

**Gathered:** 2026-06-07
**Status:** Ready for planning

<domain>
## Phase Boundary

Close out the v1.2 output-reorganization milestone with two deliverables:

1. **MANIFEST-01** — Write a `README.md` manifest at `output_root` describing
   every produced artifact as a table of **file → bucket → purpose**, matching
   what an actual run produces.
2. **TEST-01** — Verify the complete reorganized READY/SPLIT/AUDIT layout
   end-to-end: full pytest suite green within the skip-gate, goldens byte-equal,
   and `output_root` yields exactly `READY/`, `SPLIT/`, `AUDIT/`, and `README.md`
   (nothing in the old flat per-run or TOTAL layout).

**The only new production code is the manifest writer.** Everything else is
verification. Routing-only invariants still apply: no `--update-golden`, goldens
byte-equal, skip-ratio < 0.50, no tech-stack additions, no classification/audit
logic changes.

**Out of this phase:** any artifact *content* change (column trimming,
translation of existing artifacts, new summary documents) — that is v1.3
(CONTENT-01..03). The manifest is a NEW operator-facing index file, which is
explicitly in v1.2 scope (MANIFEST-01); it is not a content edit to an existing
artifact.

</domain>

<decisions>
## Implementation Decisions

### Manifest generation model
- **D-01: Static template, not a dynamic scan.** `README.md` is a hardcoded
  table documenting the canonical v1.2 artifact set (the 9 SPLIT per-spec files,
  the READY branded workbook, the AUDIT per-spec audited workbook, and the 3
  AUDIT-root aggregates). The v1.2 artifact set is frozen, so a static table is
  deterministic, byte-stable across runs, and trivially unit-testable. It does
  NOT walk the output tree at runtime. (Rejected: dynamic scan — would vary
  run-to-run, complicate byte-testing, and still need a static file→purpose map
  anyway. Rejected: hybrid scan+warn — more code than the frozen set justifies.)
- **SC#1 satisfaction:** "matches the files an actual run produces" is guaranteed
  by a unit test pinning the static table against the known artifact set (D-07),
  not by runtime introspection.

### Writer & trigger
- **D-02: `main.py` writes `README.md` to `output_root` on every invocation,
  idempotent.** Because the manifest is static (D-01), the same bytes are written
  every time, so re-runs and `run.ps1`'s per-vendor loop (which invokes `main.py`
  N times) simply overwrite the file with identical content — harmless. The
  manifest therefore always exists even for a classify-only run that never invokes
  `batch_audit`/`cluster_audit`. (Rejected: write from `cluster_audit.py` last —
  a classify-only run would then produce no manifest. Rejected: standalone step in
  `run.ps1` — manifest would only appear via the launcher, not when `main.py` runs
  directly.)
- **D-03: Write once per `main()` invocation, at `output_root` root — not
  per-spec.** The manifest lives at `output_root/README.md` (sibling of the three
  buckets), so it must be written at the `main()` level after the
  single/batch dispatch, NOT inside `_run_single` (which runs per spec). Writing
  it once per invocation keeps batch mode from rewriting it inside the per-file
  loop.
- **D-04: Centralize the writer in `run_manager.py`**, mirroring Phase 7's
  `create_spec_folder` centralization (D-10). A small helper (e.g.
  `write_manifest(output_root)`) keeps the static table and path logic testable
  in one place; `main.py` calls it rather than embedding the table inline.
  (Helper name/signature is planner/executor discretion.)

### Manifest format & language
- **D-05: Pattern rows, grouped by bucket.** One row per artifact *type* using a
  placeholder name (e.g. `<spec>_annotated.xlsx`,
  `Коммерческое предложение_<spec>.xlsx`, `<spec>_annotated_audited.xlsx`,
  `audit_report.json`), grouped under `READY` / `SPLIT` / `AUDIT` headings (~14
  rows total). The table stays stable regardless of how many specs ran —
  consistent with the static model (D-01). Columns are fixed: **file → bucket →
  purpose**. (Rejected: literal enumeration per vendor/spec — explodes with spec
  count and would force a dynamic scan.)
- **D-06: Purpose column in Russian.** The manifest is an operator-facing index
  of the OUTPUT folder; the operator is Russian-speaking and READY artifacts are
  human-facing Russian. Purpose descriptions are written in Russian. (File names,
  bucket names, and the `<vendor>/<spec>/` path structure stay as-is — only the
  prose "purpose" text is Russian.)

### Verification approach (TEST-01 / SC#2–SC#4)
- **D-07: Manifest unit test.** A pytest test asserts the writer emits
  `README.md` at `output_root` with the expected static table (bucket sections,
  pattern rows, Russian purposes). This pins the static template against drift and
  is what concretely backs SC#1.
- **D-08: Extend `tests/test_output_structure.py` with a layout assertion.** A run
  yields `README.md` at `output_root` and the top level contains only the expected
  buckets + manifest — no flat/timestamp/`*_run`/TOTAL leftovers. Reuses the test
  file that already covers Phase 7 structure (SC#2).
- **D-09: Real-data manual run recorded in VERIFICATION.** Document a real
  end-to-end run against the operator's populated INPUT (all 6 vendors, `--no-ai`):
  capture the actual `output_root` tree and the README contents in
  `09-VERIFICATION.md` — mirrors the Phase 6 "REAL DATA" close (STATE.md D-25).
  Plus the milestone-wide full pytest suite green within the skip-gate and goldens
  byte-equal (SC#3, SC#4).
- **D-10: No new full 3-process E2E pytest test.** A test driving
  `main.py → batch_audit → cluster_audit` in one go was considered and rejected as
  the heaviest option with the most overlap against existing coverage; D-07 + D-08
  + D-09 together prove SC#2 sufficiently.

### Claude's Discretion
- Exact helper name/signature for the manifest writer in `run_manager.py`
  (`write_manifest(output_root)` is a suggestion).
- Exact Russian wording of each purpose description (must be accurate to each
  artifact's role; see the E-codes / artifact roles in `spec_classifier/CLAUDE.md`
  and the per-bucket semantics in PROJECT.md).
- Markdown rendering details of the grouped table (one table per bucket section
  vs. a single table with sub-headers) — as long as it reads as file → bucket →
  purpose grouped by READY/SPLIT/AUDIT.
- Precise placement of the `write_manifest` call in `main()` (after batch
  dispatch and before the single-file `return`, vs. a single call covering both
  paths) — must run exactly once per invocation at `output_root`.
- Which specific path/layout assertions to add/realign in
  `test_output_structure.py` — planner/research enumerates; goldens stay
  byte-equal regardless.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone scope & requirements
- `.planning/REQUIREMENTS.md` — v1.2 requirements; MANIFEST-01 and TEST-01
  definitions (§ Output Manifest, § Test Realignment), the Out-of-Scope table,
  and the Traceability matrix (Phase 9 = MANIFEST-01, TEST-01).
- `.planning/ROADMAP.md` § "Phase 9: Output manifest & full-suite verification"
  + "Milestone-wide invariants" — the four success criteria and the
  goldens-byte-equal / fix-tests-not-goldens / D-22-lifted / skip-gate invariants
  that gate every phase.

### Prior-phase decisions this phase depends on (the layout being documented)
- `.planning/phases/07-bucket-layout-main-py-routing-ready-split/07-CONTEXT.md` —
  D-01 (`<vendor>` = lowercase registry key), D-02 (`<spec>` = input stem), the
  nine SPLIT artifacts, the READY branded filename
  `Коммерческое предложение_<spec>.xlsx`, D-10 (`create_spec_folder`
  centralization pattern the manifest writer should mirror).
- `.planning/phases/08-audit-routing-audit/08-CONTEXT.md` — the AUDIT artifacts
  the manifest must list: per-spec `<stem>_annotated_audited.xlsx` under
  `AUDIT/<vendor>/<spec>/`, and the AUDIT-root aggregates `audit_report.json`,
  `audit_summary.xlsx`, `cluster_summary.xlsx`.

### Artifact roles (source of truth for the Russian "purpose" text)
- `spec_classifier/CLAUDE.md` § "Current State / OUTPUT layout" and § "E-codes" —
  what each artifact is and does (annotated/audited workbooks, cluster summary,
  audit report). Note: the OUTPUT-layout block there still shows the OLD
  pre-v1.2 flat/`*_run`/TOTAL scheme — read it for artifact *semantics* only, not
  for paths (paths are the new bucket scheme).
- `.planning/PROJECT.md` § "Current Milestone" — the bucket semantics: READY =
  clean human-facing Russian docs, SPLIT = English technical/debug/DB-feed,
  AUDIT = `annotated_audited` + audit/cluster reports.

### Load-bearing constraints (do-not-violate)
- `.planning/STATE.md` § Blockers/Concerns — v1.2 phase-gate constraints
  (routing-only edits, no `--update-golden`, skip-ratio < 0.50, no tech-stack
  additions).
- `.planning/codebase/CONCERNS.md` — BLOCKER/IMPORTANT exclusions; none touched
  by adding a manifest writer.
- `CLAUDE.md` (root) § "Critical business rules" — must remain intact; the
  manifest writer touches no classification/audit logic.

### Files this phase edits / adds
- `spec_classifier/main.py` — call the manifest writer once per `main()`
  invocation at `output_root` (D-02, D-03).
- `spec_classifier/src/diagnostics/run_manager.py` — add the static-table
  manifest writer helper (D-04).
- `spec_classifier/tests/test_output_structure.py` — top-level layout +
  README presence assertions (D-08); plus a new/colocated manifest unit test
  (D-07).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `run_manager.create_spec_folder(output_root, bucket, vendor, spec)`
  (`run_manager.py:12`) — the Phase 7 centralization precedent; the manifest
  writer should live alongside it in `run_manager.py` and be called from
  `main.py` (D-04).
- `main()` (`main.py:231`) resolves `output_dir` once (`main.py:280-283`) and
  then dispatches to batch (`main.py:286-342`) or single (`main.py:353-363`)
  paths — the single place where `output_root` is known and a once-per-invocation
  manifest write can hook in (D-03).
- `tests/test_output_structure.py` — already asserts the Phase 7 bucket layout;
  the README/top-level assertions extend it (D-08).

### Established Patterns
- `output_dir` resolution (config `paths.output_root` → `--output-dir` → default)
  is unchanged; the manifest writer takes the already-resolved `output_root`.
- Run sequence in `run.ps1`: `main.py` per vendor (loop, `:185`) →
  `batch_audit.py` (`:195/:204`) → `cluster_audit.py` (`:214`). Writing the
  manifest from `main.py` (D-02) means it is present before audit runs and
  rewritten identically on each looped `main.py` call.

### Integration Points
- No new dependency, no launcher edits required: `main.py` already receives
  `output_dir`, so the manifest write is internal to the existing classify run.
- The manifest documents AUDIT artifacts produced by a later process; because the
  table is static (D-01), this cross-process documentation needs no runtime
  coupling.

</code_context>

<specifics>
## Specific Ideas

- `README.md` lives at `output_root/README.md` — a sibling of `READY/`, `SPLIT/`,
  `AUDIT/`, not inside any bucket.
- Table grouped under three headings (READY / SPLIT / AUDIT), one pattern row per
  artifact type, ~14 rows; columns **file → bucket → purpose**, purpose in Russian.
- Pattern/placeholder filenames in the "file" column (e.g.
  `<spec>_annotated.xlsx`, `Коммерческое предложение_<spec>.xlsx`,
  `<spec>_annotated_audited.xlsx`) rather than literal per-spec paths.
- SC#2 target tree: `output_root` contains exactly `READY/`, `SPLIT/`, `AUDIT/`,
  `README.md` — no `run-<timestamp>-<stem>/`, no `*_run/`, no `*-TOTAL/`.

</specifics>

<deferred>
## Deferred Ideas

- Artifact **content** changes — column trimming, translation of existing
  artifacts, new consolidated/summary documents — v1.3 (CONTENT-01..03).
  Explicitly NOT part of the manifest, which only indexes existing artifacts.
- Per-vendor knowledge docs (VKB-01..04) — still deferred.
- `spec_classifier/CLAUDE.md` OUTPUT-layout block still shows the pre-v1.2
  flat/`*_run`/TOTAL scheme — a doc-drift fix, but a documentation sweep is not
  in this phase's routing/verification scope. Note for a future docs-update pass.
- Larger `batch_audit.py` tech-debt (Excel-reading, alias sprawl, god-object) —
  tracked in CONCERNS.md, not touched.

None of the above were folded — discussion stayed within phase scope.

</deferred>

---

*Phase: 9-Output manifest & full-suite verification*
*Context gathered: 2026-06-07*
