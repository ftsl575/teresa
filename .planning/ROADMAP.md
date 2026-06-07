# Roadmap: Teresa

## Milestones

- ✅ **v1.0 Cleanup & Workflow Setup** — Phases 1-3 (shipped 2026-05-10)
- ✅ **v1.1 Periphery cleanup (residual)** — Phases 4-6 (shipped 2026-05-11)
- 🔨 **v1.2 Output structure reorganization** — Phases 7-9 (in progress, started 2026-06-07)

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3, 4, 5, 6, 7…): Planned milestone work
- Decimal phases (e.g., 4.1): Urgent insertions (marked with INSERTED)
- Phase numbering is monotonic across milestones — never restart at 1

<details>
<summary>✅ v1.0 Cleanup & Workflow Setup (Phases 1-3) — SHIPPED 2026-05-10</summary>

- [x] Phase 1: Hygiene (4/4 plans) — completed 2026-05-10
- [x] Phase 2: Docs (6/6 plans) — completed 2026-05-10
- [x] Phase 3: Workflow (3/3 plans) — completed 2026-05-10

Full details: [`.planning/milestones/v1.0-ROADMAP.md`](milestones/v1.0-ROADMAP.md)

</details>

<details>
<summary>✅ v1.1 Periphery cleanup (residual) (Phases 4-6) — SHIPPED 2026-05-11</summary>

- [x] Phase 4: Cache Redirect (3/3 plans) — completed 2026-05-10
- [x] Phase 5: Orphan Cleanup (1/1 plans) — completed 2026-05-10
- [x] Phase 6: Doc-vs-Impl Drift Sweep (6/6 plans) — completed 2026-05-11

Full details: [`.planning/milestones/v1.1-ROADMAP.md`](milestones/v1.1-ROADMAP.md)

</details>

### 🔨 v1.2 Output structure reorganization (Phases 7-9)

**Milestone goal:** Route every output artifact into three purpose-named buckets under `output_root` (READY / SPLIT / AUDIT), keyed by `<vendor>/<spec>/`, with zero content changes.

**Milestone-wide invariants (apply to every phase gate):**
- **Goldens byte-equal:** all `spec_classifier/golden/*_expected.jsonl` fixtures stay byte-equal. No `--update-golden` anywhere in v1.2. Files move; content is not rewritten.
- **Fix tests, not goldens:** path/layout assertions that break are updated to the new structure; classification content is unchanged.
- **D-22 lifted for this milestone:** routing edits to `main.py`, `run_manager.py`, `batch_audit.py`, `cluster_audit.py` are in scope (the v1.1 D-22 protected-path freeze does not apply to v1.2).
- **No content changes:** no column trimming, translation, or new documents. The single content-adjacent change is the `branded` → `Коммерческое предложение_<spec>.xlsx` filename rename.
- **Skip-gate:** pytest session must keep `skipped/total < 0.50` and `passed > 0`.

---

#### Phase 7: Bucket layout & main.py routing (READY + SPLIT)

**Goal:** Establish the three-bucket `<bucket>/<vendor>/<spec>/` path scheme, route all `main.py` per-spec outputs into SPLIT and the `branded` workbook into READY (renamed), drop the per-run timestamp folder, and remove the TOTAL copy mechanism.

**Requirements:** LAYOUT-01, LAYOUT-02, LAYOUT-03, ROUTE-01, ROUTE-02, ROUTE-05

**Success criteria:**
1. After a run, `output_root/READY/<vendor>/<spec>/Коммерческое предложение_<spec>.xlsx` exists and is byte-identical to the workbook previously emitted as `<stem>_branded.xlsx`.
2. After a run, all nine `main.py` artifacts (`cleaned_spec.xlsx`, `classification.jsonl`, `<stem>_annotated.xlsx`, `rows_raw.json`, `rows_normalized.json`, `run_summary.json`, `unknown_rows.csv`, `header_rows.csv`, `run.log`) exist under `output_root/SPLIT/<vendor>/<spec>/`, and no `run-<timestamp>-<stem>/` folder is created.
3. Re-running the same spec overwrites its files in place under READY/SPLIT — no second timestamped directory accumulates.
4. Batch mode produces no TOTAL folder; `run_manager.copy_to_total` and its call site are gone.
5. pytest passes within the skip-gate with goldens byte-equal; READY+SPLIT path/layout tests are updated to the new structure.

#### Phase 8: Audit routing (AUDIT)

**Goal:** Re-point `batch_audit.py` and `cluster_audit.py` to read annotated input from SPLIT and write `annotated_audited` per-spec into AUDIT, with batch-level aggregates at the AUDIT root.

**Requirements:** ROUTE-03, ROUTE-04

**Success criteria:**
1. `batch_audit.py` discovers `<stem>_annotated.xlsx` under `SPLIT/<vendor>/<spec>/` and writes `<stem>_annotated_audited.xlsx` to `AUDIT/<vendor>/<spec>/`.
2. `audit_report.json` and `audit_summary.xlsx` are written to the `AUDIT/` root (no vendor/spec nesting).
3. `cluster_summary.xlsx` is written to the `AUDIT/` root.
4. pytest passes within the skip-gate with goldens byte-equal; `batch_audit`/`cluster_audit` path tests (including vendor-detection-from-path) are updated to the new structure.

#### Phase 9: Output manifest & full-suite verification

**Goal:** Write the `README.md` manifest at `output_root` and verify the complete reorganized layout end-to-end with the full test suite green and goldens byte-equal.

**Requirements:** MANIFEST-01, TEST-01

**Success criteria:**
1. `output_root/README.md` lists every produced artifact as a table of file → bucket → purpose, and matches the files an actual run produces.
2. A single end-to-end run yields exactly `READY/`, `SPLIT/`, `AUDIT/`, and `README.md` under `output_root` — nothing in the old flat per-run or TOTAL layout.
3. Full pytest suite is green within the skip-gate across the whole milestone window.
4. Goldens are byte-equal end-to-end (no `--update-golden` used anywhere in v1.2).

## Progress

| Phase                        | Milestone | Plans Complete | Status   | Completed  |
| ---------------------------- | --------- | -------------- | -------- | ---------- |
| 1. Hygiene                   | v1.0      | 4/4            | Complete | 2026-05-10 |
| 2. Docs                      | v1.0      | 6/6            | Complete | 2026-05-10 |
| 3. Workflow                  | v1.0      | 3/3            | Complete | 2026-05-10 |
| 4. Cache Redirect            | v1.1      | 3/3            | Complete | 2026-05-10 |
| 5. Orphan Cleanup            | v1.1      | 1/1            | Complete | 2026-05-10 |
| 6. Doc-vs-Impl Drift Sweep   | v1.1      | 6/6            | Complete | 2026-05-11 |
| 7. Bucket layout & main.py routing | v1.2 | 0/—          | Planned  | —          |
| 8. Audit routing             | v1.2      | 0/—            | Planned  | —          |
| 9. Manifest & verification   | v1.2      | 0/—            | Planned  | —          |

---
*v1.0 milestone closed 2026-05-10. v1.1 milestone closed 2026-05-11. v1.2 started 2026-06-07. Per-milestone details preserved in `.planning/milestones/`.*
