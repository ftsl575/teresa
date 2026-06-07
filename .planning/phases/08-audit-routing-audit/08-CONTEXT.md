# Phase 8: Audit routing (AUDIT) - Context

**Gathered:** 2026-06-07
**Status:** Ready for planning

<domain>
## Phase Boundary

Re-point `batch_audit.py` and `cluster_audit.py` at the three-bucket layout
established in Phase 7:

- **Read** annotated input (`<stem>_annotated.xlsx`) from
  `SPLIT/<vendor>/<spec>/`.
- **Write** the per-spec audited workbook `<stem>_annotated_audited.xlsx` into
  `AUDIT/<vendor>/<spec>/`.
- **Write** the batch-level aggregates to the `AUDIT/` **root** (no vendor/spec
  nesting): `audit_report.json` + `audit_summary.xlsx` (`batch_audit.py`) and
  `cluster_summary.xlsx` (`cluster_audit.py`).

**Routing-only.** No audit / E-code / clustering logic changes. No content
changes. Goldens stay byte-equal (no `--update-golden`). The only logic touched
beyond destination paths is removal of dead pre-Phase-7 path-detection branches
(routing logic, not audit logic — see D-08).

Covers requirements: ROUTE-03, ROUTE-04 (+ the TEST-01 path/layout +
vendor-detection-from-path realignment needed for these to pass).

**Out of this phase:** the `output_root/README.md` manifest and full-suite
end-to-end verification (Phase 9 — MANIFEST-01, TEST-01 final). Artifact
*content* changes (column trimming, translation, new summary docs) — v1.3
(CONTENT-01..03).

</domain>

<decisions>
## Implementation Decisions

### CLI contract / bucket roots
- **D-01:** **Keep `--output-dir` = `output_root`; derive buckets internally.**
  Both `batch_audit.py` and `cluster_audit.py` keep their existing
  `--output-dir` flag pointing at the OUTPUT root and internally compute
  `SPLIT = output_root/SPLIT` (read) and `AUDIT = output_root/AUDIT` (write).
  **No launcher edits** — `run.ps1:195,204,214` (and the GUI equivalents) stay
  unchanged. Consistent with Phase 7, where `output_root` is the single root and
  buckets are derived from it.
- **D-02:** **Strict derivation — no whole-tree fallback.** Read only from
  `output_root/SPLIT/`; create `output_root/AUDIT/` if missing. If `SPLIT/` is
  absent, behave as "no annotated files found" (today's empty-result path). Do
  NOT fall back to the old whole-`output_root` rglob — the flat/timestamp/TOTAL
  layout is gone after Phase 7, so a fallback would only resurrect dead paths.

### AUDIT per-spec path mapping & re-run handling
- **D-03:** **Relative remap from the SPLIT root.** For each annotated input
  found under SPLIT:
  `out_path = AUDIT_root / input.relative_to(SPLIT_root).parent / f"{input.stem}_audited.xlsx"`.
  The SPLIT subtree *is* the source of truth for the `<vendor>/<spec>/` subpath —
  no vendor/spec re-detection for the write path, so the AUDIT mirror cannot
  drift from SPLIT.
  - Note: with the existing `--suffix` default `_audited` and input stem
    `<stem>_annotated`, the produced filename is `<stem>_annotated_audited.xlsx`,
    matching SC#1.
- **D-04:** **Overwrite the single file in place; no wipe.** `batch_audit`
  emits exactly one file per spec into `AUDIT/<vendor>/<spec>/`, so just
  `mkdir`-parents and overwrite that deterministic filename. No `rmtree` of the
  spec dir (unlike Phase 7's SPLIT/READY wipe-first D-04, which guarded against
  9 artifacts of which some are conditional). Nothing stale can accumulate here.

### Aggregate destinations (ROUTE-04 — locked by requirements)
- **D-05:** `audit_report.json` and `audit_summary.xlsx` (`batch_audit.py`),
  and `cluster_summary.xlsx` (`cluster_audit.py`), are written to the `AUDIT/`
  **root** — currently they go to the `output_dir` root
  (`batch_audit.py:1027,1290`, `cluster_audit.py:450`), so the change is
  `output_dir` → `output_dir/AUDIT`.
  - **Verify during planning:** `cluster_audit`'s docstring (`cluster_audit.py:5`)
    says it also *updates* `audit_report.json`. If it does write/update that file,
    that write must ALSO target the `AUDIT/` root, not `output_dir` root.

### cluster_audit read scope
- **D-06:** **Explicit dual-bucket read.** `cluster_audit.load_candidate_rows`
  (`cluster_audit.py:148-166`) rglobs AUDIT/ for `*_annotated_audited.xlsx` and
  SPLIT/ for `*_annotated.xlsx`, preserving the existing prefer-audited-over-
  annotated dedup-by-stem. Do NOT whole-tree rglob `output_root` (rejected for
  consistency with the strict D-02 contract) and do NOT read AUDIT-only (that
  would drop the annotated fallback for un-audited specs — a behavior change that
  violates routing-only).

### Legacy detection cleanup (delete dead code — echoes Phase 7 D-09)
- **D-07:** **Remove dead pre-Phase-7 path matchers** in `batch_audit.py`:
  - `detect_vendor_from_path` (`batch_audit.py:1360`) — strip the `{vendor}_run`
    and `hp_run` branches. Keep `/{vendor}/` and `\{vendor}\` matching (these
    handle the new `SPLIT/<vendor>/<spec>/` layout — verified forward-compatible
    in Phase 7 D-01).
  - `find_annotated_files` (`batch_audit.py:1345`) — remove the `-TOTAL`
    parent-folder exclusion (no TOTAL folders exist after Phase 7 ROUTE-05).
- **D-08:** This removal is **routing/path-detection logic, not audit logic** —
  in scope for v1.2 (D-22 lifted for these four files). It is NOT a change to
  E-code computation, AI-mismatch, or clustering behavior. Vendor-detection-from-
  path tests will be realigned accordingly (SC#4 / TEST-01).

### Claude's Discretion
- Exact internal helper shape for deriving SPLIT/AUDIT roots from `output_dir`
  (e.g., a small `_bucket_roots(output_dir)` helper vs inline `output_dir /
  "SPLIT"`). Mirror Phase 7's `create_spec_folder` centralization spirit if it
  reads cleanly; planner/executor discretion.
- Whether to keep the `--suffix` arg as-is (default `_audited`) or hard-derive
  the audited filename — no behavioral requirement either way as long as the
  output is `<stem>_annotated_audited.xlsx` (SC#1).
- Exact wording of the file-list / progress print lines (e.g.
  `f.relative_to(output_dir)` at `batch_audit.py:1402`) after the read root moves
  to SPLIT — cosmetic.
- Which specific path/layout + vendor-detection tests need realignment (TEST-01)
  — research/plan enumerates; content/goldens stay byte-equal regardless.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone scope & requirements
- `.planning/REQUIREMENTS.md` — v1.2 requirements; ROUTE-03, ROUTE-04
  definitions, the Out-of-Scope table, and the Traceability matrix (Phase 8 =
  ROUTE-03, ROUTE-04).
- `.planning/ROADMAP.md` § "Phase 8: Audit routing (AUDIT)" + "Milestone-wide
  invariants" — the four success criteria and the goldens-byte-equal /
  fix-tests-not-goldens / D-22-lifted / skip-gate invariants that gate every
  phase.

### Prior-phase decisions this phase depends on
- `.planning/phases/07-bucket-layout-main-py-routing-ready-split/07-CONTEXT.md` —
  D-01 (`<vendor>` = registry key, lowercase), D-02 (`<spec>` = input stem),
  D-05 (`main.py` must NOT touch AUDIT — AUDIT is THIS phase's lifecycle), and
  the verified note that `detect_vendor_from_path` already matches `/{vendor}/`.

### Load-bearing constraints (do-not-violate)
- `.planning/STATE.md` § Blockers/Concerns — v1.2 phase-gate constraints
  (routing-only edits, no `--update-golden`, skip-ratio < 0.50, no tech-stack
  additions) and the explicit "`batch_audit.py` reads Excel — change only WHERE
  it reads/writes, not THAT it reads Excel" exclusion.
- `.planning/codebase/CONCERNS.md` — BLOCKER/IMPORTANT exclusions
  (Excel-reading audit design, `HW_TYPE_VOCAB` duplication across
  `classifier.py`/`batch_audit.py`, YAML rule order, `power_cord` hw_type=None) —
  none touched by routing.
- `CLAUDE.md` (root) § "Critical business rules" and `spec_classifier/CLAUDE.md`
  § "Business Rules" / "E-codes" — must remain intact through routing edits.

### Files this phase edits
- `spec_classifier/batch_audit.py` — `find_annotated_files` (read root → SPLIT,
  drop `-TOTAL` guard), per-file `out_path` (→ AUDIT relative remap, line 1448),
  `detect_vendor_from_path` (drop dead `_run`/`hp_run`), `audit_summary.xlsx`
  destination (line 1027), `audit_report.json` destination (line 1290).
- `spec_classifier/cluster_audit.py` — `load_candidate_rows` (dual-bucket read,
  lines 148-166), `cluster_summary.xlsx` destination (line 450), and any
  `audit_report.json` update destination (verify per D-05) → AUDIT root.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `find_annotated_files(output_dir, vendor_filter, since)`
  (`batch_audit.py:1339`) — single discovery chokepoint; pointing its `rglob`
  base at `output_dir/SPLIT` localizes the read-side routing change.
- Per-file write site `out_path = f.parent / f"{f.stem}{args.suffix}.xlsx"`
  (`batch_audit.py:1448`) — single line where the audited destination is
  computed; D-03 relative-remap lands here.
- `cluster_audit.load_candidate_rows` (`cluster_audit.py:148-166`) — two `rglob`
  calls (audited-priority + annotated-fallback) with stem dedup; the dual-bucket
  read (D-06) changes only the two glob bases.
- `detect_vendor_from_path` (`batch_audit.py:1354`) — already matches
  `/{vendor}/` and `\{vendor}\` (Phase 7 D-01 verified), so the new
  `SPLIT/<vendor>/<spec>/` layout is read with no detection change beyond
  dead-branch removal.

### Established Patterns
- Both audit scripts already take `--output-dir` and resolve everything relative
  to it (`batch_audit.py:1390`, `cluster_audit.py:497`). Keeping that flag and
  deriving `SPLIT`/`AUDIT` underneath (D-01) mirrors Phase 7's
  output_root-rooted bucket derivation.
- Aggregates are already written as `Path(output_dir) / "<name>"`
  (`batch_audit.py:1027,1290`, `cluster_audit.py:450`) — the ROUTE-04 change is a
  one-segment `/ "AUDIT"` insertion at each site.

### Integration Points
- Upstream: Phase 7's `main.py` writes `<stem>_annotated.xlsx` into
  `SPLIT/<vendor>/<spec>/` and deliberately leaves `AUDIT/` untouched (Phase 7
  D-05), so this phase owns AUDIT creation/population without collision.
- The `<vendor>` SPLIT token = `VENDOR_REGISTRY` key, lowercase
  (`dell`/`cisco`/`hpe`/`lenovo`/`huawei`/`xfusion`) — already detection-
  compatible.

</code_context>

<specifics>
## Specific Ideas

- Per-spec audited filename is exactly `<stem>_annotated_audited.xlsx` under
  `AUDIT/<vendor>/<spec>/` (SC#1).
- Aggregates (`audit_report.json`, `audit_summary.xlsx`, `cluster_summary.xlsx`)
  sit flat at the `AUDIT/` root — no vendor/spec nesting (SC#2, SC#3).
- The AUDIT mirror of the SPLIT subpath is derived by `relative_to(SPLIT_root)`,
  not by re-detecting vendor/spec — guarantees the two trees stay parallel.

</specifics>

<deferred>
## Deferred Ideas

- **`output_root/README.md` manifest** + full-suite end-to-end verification —
  Phase 9 (MANIFEST-01, TEST-01 final).
- Artifact **content** changes (column trimming, translation, new summary docs) —
  v1.3 (CONTENT-01..03), explicitly out of v1.2.
- Larger `batch_audit.py` tech-debt (Excel-reading-instead-of-jsonl, alias
  sprawl, `HW_TYPE_VOCAB` duplication, ~1489 LOC god-object) — tracked in
  CONCERNS.md, explicitly NOT touched by routing.

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 8-Audit routing (AUDIT)*
*Context gathered: 2026-06-07*
