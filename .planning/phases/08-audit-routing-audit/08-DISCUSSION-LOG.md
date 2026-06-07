# Phase 8: Audit routing (AUDIT) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-07
**Phase:** 8-Audit routing (AUDIT)
**Areas discussed:** CLI contract / bucket roots, AUDIT path mapping & re-run wipe, cluster_audit read scope, Legacy detection cruft

---

## CLI contract / bucket roots

| Option | Description | Selected |
|--------|-------------|----------|
| Keep --output-dir=output_root, derive internally | Scripts keep --output-dir = OUTPUT root; derive SPLIT (read) + AUDIT (write) internally. run.ps1/GUI unchanged. Matches Phase 7. | ✓ |
| Point --output-dir at SPLIT + add --audit-dir | --output-dir = read root (SPLIT); separate --audit-dir for write root. Requires editing run.ps1 (3 sites). | |
| Add --split-dir / --audit-dir, deprecate --output-dir | Two new explicit flags; --output-dir fallback. Most surface area + test churn. | |

**User's choice:** Keep --output-dir=output_root, derive internally
**Notes:** Keeps launcher contract intact — no edits to run.ps1:195/204/214 or GUI.

### Follow-up: SPLIT-read derivation strictness

| Option | Description | Selected |
|--------|-------------|----------|
| Strict: read SPLIT, create AUDIT, no fallback | Read only output_root/SPLIT/; create output_root/AUDIT/; no legacy whole-tree scan. | ✓ |
| Fallback: rglob output_root if SPLIT/ missing | Prefer SPLIT/, else scan whole output_root (old behavior). Keeps dead-path logic alive. | |

**User's choice:** Strict — read SPLIT, create AUDIT, no fallback

---

## AUDIT path mapping & re-run wipe

### Per-spec destination derivation

| Option | Description | Selected |
|--------|-------------|----------|
| Relative remap from SPLIT root | out = AUDIT_root / input.relative_to(SPLIT_root).parent / f"{stem}_audited.xlsx". SPLIT subtree is source of truth for subpath; no re-detection. | ✓ |
| Re-detect vendor + spec, rebuild path | detect_vendor_from_path + stem → rebuild AUDIT/<vendor>/<spec>/. Duplicates logic, risks drift. | |

**User's choice:** Relative remap from SPLIT root

### Re-run / stale handling

| Option | Description | Selected |
|--------|-------------|----------|
| Overwrite file in place (mkdir parents) | One deterministic file per spec; mkdir -p + overwrite. No wipe. | ✓ |
| Wipe-first the spec dir (mirror Phase 7 D-04) | rmtree AUDIT/<vendor>/<spec>/ then recreate. Audit emits one file — nothing stale to clear; risks clobber. | |

**User's choice:** Overwrite file in place (mkdir parents)

---

## cluster_audit read scope

| Option | Description | Selected |
|--------|-------------|----------|
| Explicit: audited from AUDIT, annotated from SPLIT | rglob AUDIT/ for *_annotated_audited.xlsx + SPLIT/ for *_annotated.xlsx; keep prefer-audited dedup. Consistent with strict Area 1. | ✓ |
| Whole-tree rglob from output_root | Scan entire output_root; finds both naturally. Smallest diff but inconsistent with strict no-whole-tree rule. | |
| AUDIT only (audited files) | Scan only AUDIT/; drops annotated fallback for un-audited specs. Behavior change; violates routing-only. | |

**User's choice:** Explicit: audited from AUDIT, annotated from SPLIT

---

## Legacy detection cruft

| Option | Description | Selected |
|--------|-------------|----------|
| Remove dead branches, update tests | Strip {vendor}_run/hp_run matching and -TOTAL exclusion (dead after Phase 7). Echoes Phase 7 D-09. Routing logic, in scope. | ✓ |
| Keep as harmless no-ops | Leave dead matchers; never fire under new layout. Smallest diff but contradicts delete-dead-code stance. | |
| Remove _run/hp_run, keep -TOTAL guard | Drop vendor aliases, keep -TOTAL. Inconsistent — both equally dead. | |

**User's choice:** Remove dead branches, update tests

---

## Claude's Discretion

- Internal helper shape for deriving SPLIT/AUDIT roots from output_dir (helper vs inline).
- Keep `--suffix` arg as-is vs hard-derive filename (output must be `<stem>_annotated_audited.xlsx`).
- Wording of file-list / progress print lines after read root moves to SPLIT (cosmetic).
- Which specific path/layout + vendor-detection tests need realignment (TEST-01) — planner enumerates.

## Deferred Ideas

- `output_root/README.md` manifest + full-suite end-to-end verification — Phase 9 (MANIFEST-01, TEST-01 final).
- Artifact content changes (column trimming, translation, new summary docs) — v1.3 (CONTENT-01..03).
- batch_audit.py tech-debt (Excel-reading-vs-jsonl, alias sprawl, HW_TYPE_VOCAB duplication, ~1489 LOC) — tracked in CONCERNS.md, not touched by routing.
