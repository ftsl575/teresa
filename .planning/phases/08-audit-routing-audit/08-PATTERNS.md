# Phase 8: Audit routing (AUDIT) - Pattern Map

**Mapped:** 2026-06-07
**Files analyzed:** 2 source files / 8 change sites
**Analogs found:** 8 / 8 (all routing-internal; strongest analog = Phase 7 `main.py` + `run_manager.create_spec_folder`)

> Routing-only phase. Every change site below mirrors an already-shipped Phase 7
> pattern (output_root → bucket derivation, `relative_to(...)` remap, dead-branch
> deletion). No new files are created. No audit / E-code / clustering logic is
> touched. Goldens stay byte-equal. PATTERNS.md is the only file written.

---

## File Classification

| Change site | File | Role | Data Flow | Closest Analog | Match Quality |
|-------------|------|------|-----------|----------------|---------------|
| `find_annotated_files` rglob base | `batch_audit.py:1339-1351` | read-routing | file-I/O (discovery) | `main.py:127` `create_spec_folder(..., "SPLIT", ...)` + Phase 7 `output_dir/bucket` derivation | exact (mirrors SPLIT bucket) |
| `find_annotated_files` `-TOTAL` guard removal | `batch_audit.py:1345` | dead-code-removal | — | Phase 7 D-09 `copy_to_total`/`create_total_folder` deletions (`run_manager.py`) | exact (echo of Phase 7 D-09) |
| per-file `out_path` remap | `batch_audit.py:1448` | write-routing | file-I/O (per-spec write) | `main.py:127-128` bucket folder + `input.relative_to(SPLIT_root)` (new) | role-match (D-03 remap) |
| `audit_summary.xlsx` dest | `batch_audit.py:1027` | aggregate-destination | file-I/O (aggregate write) | Phase 7 `output_dir / bucket / ...` one-segment insertion | exact |
| `audit_report.json` dest | `batch_audit.py:1290` | aggregate-destination | file-I/O (aggregate write) | same as above | exact |
| `detect_vendor_from_path` dead branches | `batch_audit.py:1354-1366` | dead-code-removal | transform (path → vendor) | Phase 7 D-09 dead-helper deletion; Phase 7 D-01 verified `/{vendor}/` kept | exact (echo of Phase 7 D-09) |
| `_collect_xlsx_files` dual rglob bases | `cluster_audit.py:148-167` | read-routing | file-I/O (discovery) | `batch_audit.find_annotated_files` SPLIT/AUDIT read (this phase) + Phase 7 bucket derivation | exact (dual-bucket of same pattern) |
| `cluster_summary.xlsx` + `audit_report.json` dest | `cluster_audit.py:450,455` | aggregate-destination | file-I/O (aggregate write/update) | `batch_audit.py:1027,1290` aggregate-dest change (this phase) | exact |

---

## Shared Patterns

These three cross-cutting patterns apply to multiple change sites. Copy them
verbatim; do not re-invent.

### SP-1: Bucket-root derivation from `output_root` (Phase 7 canonical)

**Source:** `spec_classifier/main.py:127-128` (and `run_manager.create_spec_folder`)
**Apply to:** every read/write site in both audit files (D-01).

Phase 7 keeps the single `--output-dir` = `output_root` flag and derives buckets
internally. `main.py` passes the bucket name as a string and the helper joins it:

```python
# main.py:127-128 — output_dir is output_root; "SPLIT"/"READY" are bucket segments
split_folder = create_spec_folder(output_dir, "SPLIT", vendor, input_path.stem)
ready_folder = create_spec_folder(output_dir, "READY", vendor, input_path.stem)
```

```python
# run_manager.py:28-29 — the join itself: output_root / bucket / vendor / spec
output_root = Path(output_root)
folder = output_root / bucket / vendor / spec
```

**Phase 8 application:** in `batch_audit.main` (`batch_audit.py:1390`,
`output_dir = Path(args.output_dir)`) and `cluster_audit.main`
(`cluster_audit.py:497`, identical line), derive:
- `SPLIT_root = output_dir / "SPLIT"` (read base)
- `AUDIT_root = output_dir / "AUDIT"` (write base; `mkdir(parents=True, exist_ok=True)` — D-02)

Claude's Discretion (CONTEXT line 101): a small `_bucket_roots(output_dir)` helper
vs inline `output_dir / "SPLIT"`. Mirror `create_spec_folder`'s centralization
spirit if it reads cleanly. NOTE: the audit write does NOT wipe (D-04), so do NOT
reuse `create_spec_folder` (it `rmtree`s); use plain `mkdir(parents=True,
exist_ok=True)`.

### SP-2: `relative_to(...)` mirror remap (D-03)

**Source:** the SPLIT-subtree-is-source-of-truth idea (Phase 7 D-01/D-02; the
`input_path.stem` token at `main.py:127`).
**Apply to:** `batch_audit.py:1448` per-file `out_path` only.

The AUDIT tree mirrors the SPLIT tree's `<vendor>/<spec>/` subpath by remapping,
NOT by re-detecting vendor/spec — so the mirror cannot drift:

```python
# REPLACES batch_audit.py:1448  out_path = f.parent / f"{f.stem}{args.suffix}.xlsx"
out_path = AUDIT_root / f.relative_to(SPLIT_root).parent / f"{f.stem}{args.suffix}.xlsx"
out_path.parent.mkdir(parents=True, exist_ok=True)   # D-04: mkdir-parents, overwrite in place, no rmtree
```

With `--suffix` default `_audited` and input stem `<stem>_annotated`, the filename
stays `<stem>_annotated_audited.xlsx` (SC#1) — unchanged from today.

### SP-3: Aggregate-destination one-segment insertion (ROUTE-04 / D-05)

**Source:** existing aggregate writes are `Path(output_dir) / "<name>"`.
**Apply to:** `batch_audit.py:1027,1290` and `cluster_audit.py:450,455`.

The change is a single `/ "AUDIT"` segment inserted before the filename. Pattern
to copy at every aggregate site:

```python
# batch_audit.py:1027  out_path = Path(output_dir) / "audit_summary.xlsx"
# batch_audit.py:1290  out_path = Path(output_dir) / "audit_report.json"
# cluster_audit.py:450 xlsx_path = output_dir / "cluster_summary.xlsx"
# cluster_audit.py:455 json_path = output_dir / "audit_report.json"
#   →  insert AUDIT segment (use the SP-1 AUDIT_root if derived in main and threaded through):
out_path = Path(output_dir) / "AUDIT" / "audit_summary.xlsx"
```

NOTE: aggregate writers receive `output_dir` as a **str** (`batch_audit.py:1540-1542`
pass `args.output_dir`; the funcs at `:855,:1127,:426` take `output_dir: str`).
Either thread `AUDIT_root` in, or insert `"AUDIT"` inside each function. The AUDIT
root must already exist (created by SP-1 before per-file writes); if a path can be
reached without any per-file write, guard with `mkdir(parents=True, exist_ok=True)`.

---

## Pattern Assignments

### `batch_audit.py:1339-1351` — `find_annotated_files` (read-routing + dead-code-removal)

**Analog:** Phase 7 SPLIT bucket derivation (SP-1). Read base moves from whole
`output_dir` to `output_dir/SPLIT`.

**Current code:**
```python
def find_annotated_files(output_dir: Path, vendor_filter: str | None,
                          since: str | None) -> list[Path]:
    files = sorted(output_dir.rglob("*_annotated.xlsx"))
    # Exclude already-audited files
    files = [f for f in files if "_audited" not in f.name]
    # Exclude TOTAL aggregation folders (contain duplicates of per-run files)
    files = [f for f in files if "-TOTAL" not in f.parent.name]   # ← DELETE (D-07; no TOTAL after Phase 7 ROUTE-05)
    ...
```

**Changes:**
1. Rebase the rglob: `sorted((output_dir / "SPLIT").rglob("*_annotated.xlsx"))`.
   Strict — no whole-tree fallback (D-02). If `SPLIT/` is absent, return `[]`
   (today's empty-result path, already handled by caller at `:1396-1398`
   "Файлы *_annotated.xlsx не найдены" → `sys.exit(0)`). Guard with
   `if not SPLIT_root.is_dir(): return []` to avoid `rglob` on a missing dir.
2. Delete the `-TOTAL` parent-folder exclusion line (`:1345`) — dead after ROUTE-05.
3. Keep the `_audited` name exclusion (`:1343`) — still correct (audited files now
   live under AUDIT/, but a defensive name filter is harmless and routing-only).

**Caller cosmetic (Claude's Discretion, CONTEXT line 108):** `:1402`
`f.relative_to(output_dir)` still resolves (SPLIT is under output_dir) but
`f.relative_to(SPLIT_root)` reads cleaner now that the base is SPLIT.

---

### `batch_audit.py:1448` — per-file `out_path` (write-routing)

**Analog:** SP-2 (`relative_to` remap) + SP-1 (AUDIT_root).

**Current code:**
```python
for f in files:
    vendor = args.vendor or detect_vendor_from_path(f, known_vendors)
    out_path = f.parent / f"{f.stem}{args.suffix}.xlsx"   # ← REMAP to AUDIT mirror (D-03)
```

**Change:** apply SP-2. `f` now comes from `SPLIT_root.rglob(...)`, so
`f.relative_to(SPLIT_root).parent` == `<vendor>/<spec>`. Write into the AUDIT mirror.
No `rmtree` — single deterministic file, overwrite in place (D-04). `vendor` is still
needed for the report/AI path, so `detect_vendor_from_path` stays in the loop; only
its dead branches are stripped (see next).

---

### `batch_audit.py:1354-1366` — `detect_vendor_from_path` (dead-code-removal)

**Analog:** Phase 7 D-09 dead-helper deletion; Phase 7 D-01 verified `/{vendor}/`
and `\{vendor}\` already match the new `SPLIT/<vendor>/<spec>/` layout.

**Current code:**
```python
def detect_vendor_from_path(path: Path, known_vendors: list[str] | None = None) -> str:
    ...
    for vendor in known_vendors:
        if f"{vendor}_run" in s or f"/{vendor}/" in s or f"\\{vendor}\\" in s:   # ← drop "{vendor}_run"
            return vendor
    # HPE alias: "hp_run" → "hpe"
    if "hp_run" in s:        # ← DELETE these two lines (D-07)
        return "hpe"
    print(f"  [WARN] Cannot detect vendor from path: {path}", file=sys.stderr)
    return "unknown"
```

**Change (D-07):** strip the `{vendor}_run` clause and the `hp_run` → `hpe` alias
block (dead pre-Phase-7 path matchers). KEEP the `/{vendor}/` and `\{vendor}\`
clauses — they handle the new layout. Resulting check:
```python
        if f"/{vendor}/" in s or f"\\{vendor}\\" in s:
            return vendor
```
This is path-detection logic, not audit logic — in scope per D-08. TEST-01 / SC#4
realigns the vendor-detection-from-path tests in `tests/test_batch_audit.py`
(fix tests, not goldens).

---

### `batch_audit.py:1027` — `audit_summary.xlsx` destination (aggregate-destination)

**Analog:** SP-3. `out_path = Path(output_dir) / "audit_summary.xlsx"` →
`Path(output_dir) / "AUDIT" / "audit_summary.xlsx"`. Inside `_write_summary`-style
function taking `output_dir: str` — see SP-3 note on threading vs inline insertion.

---

### `batch_audit.py:1290` — `audit_report.json` destination (aggregate-destination)

**Analog:** SP-3. `out_path = Path(output_dir) / "audit_report.json"` →
`Path(output_dir) / "AUDIT" / "audit_report.json"`. Inside `_generate_report`
(`:1127`, `output_dir: str`).

**NON-CHANGE to verify (do not break):** `_generate_human_report` at
`batch_audit.py:924` does `Path(output_dir).rglob(f"{stem}_audited.xlsx")`. This
still resolves because audited files remain under `output_dir` (now nested in
AUDIT/). Leave it as a whole-`output_dir` rglob — re-scoping it is out of phase and
the existing rglob is forward-compatible. Flag only; no edit required.

---

### `cluster_audit.py:148-167` — `_collect_xlsx_files` (read-routing, dual-bucket)

**Analog:** `batch_audit.find_annotated_files` SPLIT rebase (this phase) +
`batch_audit` AUDIT mirror. CONTEXT D-06 = explicit dual-bucket read.

**Current code:**
```python
def _collect_xlsx_files(output_dir: Path) -> list[Path]:
    audited = {
        p.stem.replace("_annotated_audited", ""): p
        for p in output_dir.rglob("*_annotated_audited.xlsx")   # ← rebase to AUDIT_root
    }
    annotated = {
        p.stem.replace("_annotated", ""): p
        for p in output_dir.rglob("*_annotated.xlsx")           # ← rebase to SPLIT_root
        if not p.stem.endswith("_annotated_audited")
    }
    selected: list[Path] = []
    all_stems = set(audited) | set(annotated)
    for stem in sorted(all_stems):
        selected.append(audited.get(stem) or annotated[stem])   # ← prefer-audited dedup PRESERVED
    return selected
```

**Change (D-06):** change ONLY the two rglob bases:
- audited dict: `(output_dir / "AUDIT").rglob("*_annotated_audited.xlsx")`
- annotated dict: `(output_dir / "SPLIT").rglob("*_annotated.xlsx")`

Guard each with `if (output_dir / bucket).is_dir()` (a missing bucket → empty dict),
consistent with strict D-02. Keep the stem-dedup / prefer-audited-over-annotated
logic exactly (`audited.get(stem) or annotated[stem]`). Do NOT whole-tree rglob and
do NOT read AUDIT-only (would drop the annotated fallback — behavior change).
`load_candidate_rows` (`:170`, `:186`) calls this unchanged.

> CONTEXT cites lines 148-166; the actual rglob block is `_collect_xlsx_files`
> at `:148-167` (called by `load_candidate_rows`). Both globs live here, not in
> `load_candidate_rows` body.

---

### `cluster_audit.py:450,455` — `cluster_summary.xlsx` + `audit_report.json` dest (aggregate-destination)

**Analog:** SP-3.

**Current code (`write_cluster_summary`, `output_dir: Path` at `:426`):**
```python
xlsx_path = output_dir / "cluster_summary.xlsx"      # :450 → output_dir / "AUDIT" / "cluster_summary.xlsx"
...
json_path = output_dir / "audit_report.json"         # :455 → output_dir / "AUDIT" / "audit_report.json"
if json_path.exists():
    ...
```

**Change (D-05, both verified):** insert `/ "AUDIT"` at both. CONTEXT D-05 flagged
the docstring claim (`cluster_audit.py:5`, "updates audit_report.json") for
verification — **confirmed**: line 455-456 reads/updates `audit_report.json`. This
update MUST also target `AUDIT/` root so it finds the file `batch_audit` now writes
at `AUDIT/audit_report.json` (`:1290`). If it stays at `output_dir` root, the
`json_path.exists()` check fails silently and the cluster section is never merged.

This is a Path arg (not str), so `output_dir / "AUDIT" / ...` is direct; ensure
`(output_dir / "AUDIT")` exists (it will, since batch_audit ran first; defensively
`mkdir(parents=True, exist_ok=True)` before the xlsx write).

---

## No Analog Found

None. Every change site is a routing variant of a Phase 7 pattern already shipped,
or an internal echo (`batch_audit` SPLIT/AUDIT pattern reused by `cluster_audit`).
RESEARCH.md fallback is not required for any site.

---

## Metadata

**Analog search scope:** `spec_classifier/main.py`,
`spec_classifier/src/diagnostics/run_manager.py`, `spec_classifier/batch_audit.py`,
`spec_classifier/cluster_audit.py`.
**Files scanned:** 4.
**Strongest analog:** `main.py:127-128` + `run_manager.create_spec_folder`
(`run_manager.py:12-40`) — Phase 7's shipped bucket-routing.
**Pattern extraction date:** 2026-06-07.
**Constraint reminder for planner:** routing-only; no `--update-golden`; AUDIT
writes use `mkdir(exist_ok=True)` NOT `create_spec_folder` (no wipe — D-04);
goldens byte-equal; fix tests not goldens (TEST-01).
