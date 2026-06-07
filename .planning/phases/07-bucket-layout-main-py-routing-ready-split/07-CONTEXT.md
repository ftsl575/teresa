# Phase 7: Bucket layout & main.py routing (READY + SPLIT) - Context

**Gathered:** 2026-06-07
**Status:** Ready for planning

<domain>
## Phase Boundary

Reroute every `main.py` output from the old
`<output_root>/<vendor>_run/run-<timestamp>-<stem>/` scheme into the new
three-bucket `<bucket>/<vendor>/<spec>/` layout:

- The nine per-spec artifacts (`cleaned_spec.xlsx`, `classification.jsonl`,
  `<stem>_annotated.xlsx`, `rows_raw.json`, `rows_normalized.json`,
  `run_summary.json`, `unknown_rows.csv`, `header_rows.csv`, `run.log`) →
  `SPLIT/<vendor>/<spec>/`.
- The branded workbook → `READY/<vendor>/<spec>/Коммерческое предложение_<spec>.xlsx`
  (filename rename only; bytes byte-identical to the old `<stem>_branded.xlsx`).
- The per-run `run-<timestamp>-<stem>/` folder is gone (overwrite in place).
- The TOTAL copy mechanism (`copy_to_total` + its call site) is removed.

**Routing-only.** No classification / normalization / audit logic changes. No
content changes. Goldens stay byte-equal (no `--update-golden`). The single
content-adjacent change is the branded filename rename.

Covers requirements: LAYOUT-01, LAYOUT-02, LAYOUT-03, ROUTE-01, ROUTE-02,
ROUTE-05 (+ the TEST-01 path/layout realignment needed for these to pass).

**Out of this phase:** AUDIT bucket population (Phase 8 — `batch_audit` /
`cluster_audit`); the `output_root/README.md` manifest (Phase 9).

</domain>

<decisions>
## Implementation Decisions

### Path tokens (forced by spec + existing code — not re-asked)
- **D-01:** `<vendor>` token = the registry key from `VENDOR_REGISTRY`
  (`dell` / `cisco` / `hpe` / `lenovo` / `huawei` / `xfusion`), lowercase.
  Verified compatible with `batch_audit.detect_vendor_from_path` (matches
  `/{vendor}/` and `\{vendor}\` — `batch_audit.py:1360`), so Phase 8 reads it
  without change.
- **D-02:** `<spec>` token = the input file stem (e.g. `dl1` from `dl1.xlsx`).
- **D-03:** Both single-file (`--input`) and batch (`--batch` / `--batch-dir`)
  modes route through the new layout — they share `_run_single`, so the path
  change lands in one place.

### Re-run / stale-file handling (LAYOUT-03)
- **D-04:** **Wipe-first, per-bucket-this-process-writes.** At the start of each
  spec's processing, `rmtree` the spec's directory **only in the buckets this
  process actually writes** — i.e. `READY/<vendor>/<spec>/` and
  `SPLIT/<vendor>/<spec>/` — then recreate and write fresh. This guarantees the
  folder reflects exactly the current run (no orphaned stale artifacts, e.g. a
  leftover `unknown_rows.csv` from a run that had unknowns when the new run does
  not).
- **D-05:** **`main.py` must NOT touch `AUDIT/<vendor>/<spec>/`.** AUDIT belongs
  to Phase 8's `batch_audit` lifecycle and runs as a separate process after
  classification; wiping it from a classify run would clobber audit output.

### AUDIT bucket scope in Phase 7
- **D-06:** `main.py` creates only `READY/` and `SPLIT/` (the buckets it writes).
  An empty `AUDIT/` is **not** created in Phase 7 — it appears when `batch_audit`
  runs in Phase 8. LAYOUT-01 ("three buckets on every run") is satisfied across
  the milestone, not by `main.py` alone.

### Branded workbook (ROUTE-02, byte-equality guard for SC#1)
- **D-07:** Only the **destination path + filename** change. `generate_branded_spec`
  keeps `source_filename=input_path.name` (the *input* name) so the workbook
  bytes are unchanged — the new file at
  `READY/<vendor>/<spec>/Коммерческое предложение_<spec>.xlsx` must be
  byte-identical to the workbook previously emitted as `<stem>_branded.xlsx`.
- **D-08:** The Russian filename contains a space — fine on Windows (the target
  platform). `<spec>` in the filename = the input stem (D-02).

### run_manager.py disposition (ROUTE-05 + cleanup)
- **D-09:** **Delete dead helpers, no dead code left behind.**
  - `copy_to_total` + its `main.py` call site — removed (ROUTE-05).
  - `create_total_folder` + its batch-mode call site — removed (no TOTAL folder).
  - `create_run_folder` and `get_session_stamp` — removed once unused (the
    timestamp-folder scheme is gone). Update the module docstring accordingly.
- **D-10:** **New helper centralizes path construction in `run_manager.py`** —
  e.g. `create_spec_folder(output_root, bucket, vendor, spec)` that returns the
  (wiped + recreated) `<output_root>/<bucket>/<vendor>/<spec>/` path. Keeps path
  logic testable where the old helper lived; `main.py` calls it instead of
  building paths inline.

### Claude's Discretion
- Exact signature/name of the new path helper (`create_spec_folder` is a
  suggestion).
- Batch-mode summary line wording after TOTAL removal (currently prints
  `TOTAL: {total_folder}`) — reword to reference `output_root` / counts; planner/
  executor discretion, no behavioral requirement.
- Which specific path/layout tests need realignment (TEST-01) — research/plan to
  enumerate; content/goldens stay byte-equal regardless.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone scope & requirements
- `.planning/REQUIREMENTS.md` — v1.2 requirements; LAYOUT-01..03, ROUTE-01/02/05,
  TEST-01 definitions and the explicit Out-of-Scope table.
- `.planning/ROADMAP.md` § "Phase 7" + "Milestone-wide invariants" — success
  criteria (5) and the goldens-byte-equal / fix-tests-not-goldens / D-22-lifted /
  skip-gate invariants that gate every phase.

### Load-bearing constraints (do-not-violate)
- `.planning/STATE.md` § Blockers/Concerns — v1.2 phase-gate constraints
  (routing-only edits, no `--update-golden`, skip-ratio < 0.50, no tech-stack
  additions).
- `.planning/codebase/CONCERNS.md` — BLOCKER/IMPORTANT exclusions (Excel-reading
  audit design, YAML rule order, `power_cord` hw_type=None, etc.) — none touched
  by routing.
- `CLAUDE.md` (root) § "Critical business rules" and `spec_classifier/CLAUDE.md` §
  "Business Rules" — must remain intact through routing edits.

### Files this phase edits
- `spec_classifier/main.py` — `_run_single` output paths, branded destination,
  batch-mode TOTAL removal.
- `spec_classifier/src/diagnostics/run_manager.py` — helper deletions + new
  `create_spec_folder` (D-09, D-10).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `run_manager.create_run_folder` (`run_manager.py:19`) — the existing
  "make + uniquify a per-run dir" helper; its role is replaced by the new
  wipe-first `create_spec_folder` (D-10).
- `_run_single` (`main.py:113`) — single chokepoint where all nine artifacts +
  branded are written (`run_folder` is the only path variable). Both single and
  batch modes flow through it, so the routing change is localized.
- `generate_branded_spec` (`main.py:182-189`) — already takes an explicit
  `output_path`; only the path/name args change (D-07).

### Established Patterns
- Output base today = `output_dir / f"{vendor}_run"` then a timestamped run
  folder (`main.py:134-135`, `:316-317`). New base = `output_dir / bucket /
  vendor / spec`. `output_dir` resolution (config `paths.output_root` →
  `--output-dir` → default) is unchanged.
- `batch_audit.detect_vendor_from_path` already matches `/{vendor}/` path
  segments (`batch_audit.py:1360`) — the new `<vendor>/` token is forward-
  compatible with Phase 8 with no detection change.

### Integration Points
- Phase 8 (`batch_audit`) will read `<stem>_annotated.xlsx` from
  `SPLIT/<vendor>/<spec>/` and write into `AUDIT/<vendor>/<spec>/`. Phase 7 must
  leave `AUDIT/` untouched (D-05) so the two lifecycles don't collide.

</code_context>

<specifics>
## Specific Ideas

- Branded filename is exactly `Коммерческое предложение_<spec>.xlsx` (Cyrillic,
  with a space), under `READY/<vendor>/<spec>/`.
- Re-run must overwrite in place — no second timestamped directory accumulates
  (success criterion #3); enforced by the wipe-first helper (D-04).

</specifics>

<deferred>
## Deferred Ideas

- **AUDIT routing** (`batch_audit` / `cluster_audit` read-from-SPLIT,
  write-to-AUDIT; batch aggregates at AUDIT root) — Phase 8 (ROUTE-03, ROUTE-04).
- **`output_root/README.md` manifest** + full-suite end-to-end verification —
  Phase 9 (MANIFEST-01, TEST-01 final).
- Artifact **content** changes (column trimming, translation, new summary docs) —
  v1.3 (CONTENT-01..03), explicitly out of v1.2.

</deferred>

---

*Phase: 7-Bucket layout & main.py routing (READY + SPLIT)*
*Context gathered: 2026-06-07*
