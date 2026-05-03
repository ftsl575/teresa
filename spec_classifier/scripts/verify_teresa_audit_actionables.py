#!/usr/bin/env python3
"""
Verify actionable rows from teresa_full_audit_fix_report_194.csv against the latest
classification.jsonl outputs (PR-11 acceptance: 70 taxonomy/actionable SKUs).

Typical CSV columns (case-insensitive headers; extra columns ignored):
  - status: CONFIRMED_BUG | LIKELY_BUG | TAXONOMY_DECISION
  - sku / skus / product_# / part_number: primary SKU token
  - expected_device_type / expected_hw_type: optional explicit expectations
  - expected_direction: fallback free text, e.g.
        "device_type=optical_drive hw_type=storage_drive"
        "optical_drive/storage_drive"
        "optical_drive → storage_drive"

Usage:
  python scripts/verify_teresa_audit_actionables.py ^
    --csv C:\\path\\teresa_full_audit_fix_report_194.csv ^
    --output-dir C:\\Users\\YOU\\Desktop\\OUTPUT

If --jsonl is omitted, the script picks the newest classification.jsonl under each
*_<run>*/** path (by filesystem mtime) and merges SKU -> row (first hit wins per file
in deterministic path order; latest files override older ones).
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any


ACTIONABLE = {"CONFIRMED_BUG", "LIKELY_BUG", "TAXONOMY_DECISION"}

SKU_HEADER_CANDIDATES = (
    "sku",
    "skus",
    "product_#",
    "product#",
    "part_number",
    "part number",
    "product number",
)

DT_HEADER = ("expected_device_type", "expected_dt", "target_device_type")
HW_HEADER = ("expected_hw_type", "expected_hw", "target_hw_type")


def _norm_header(h: str) -> str:
    return h.strip().lower().replace(" ", "_")


def _norm_sku(s: str) -> str:
    return s.strip().upper()


def _parse_direction(text: str) -> tuple[str | None, str | None]:
    if not text or not str(text).strip():
        return None, None
    t = str(text).strip()
    md = re.search(r"device[_\s]?type\s*[=:]\s*(\S+)", t, re.I)
    mh = re.search(r"hw[_\s]?type\s*[=:]\s*(\S+)", t, re.I)
    if md and mh:
        return md.group(1).strip(), mh.group(1).strip()
    if "/" in t and "://" not in t:
        parts = re.split(r"[/→]", t)
        if len(parts) == 2:
            return parts[0].strip(), parts[1].strip()
    return None, None


def _resolve_headers(fieldnames: list[str] | None) -> dict[str, str]:
    if not fieldnames:
        raise SystemExit("CSV has no header row.")
    raw = list(fieldnames)
    norm_map = {_norm_header(h): h for h in raw}

    def pick(*cands: str) -> str | None:
        for c in cands:
            k = _norm_header(c)
            if k in norm_map:
                return norm_map[k]
        return None

    sku_col = pick(*SKU_HEADER_CANDIDATES)
    if not sku_col:
        raise SystemExit(f"CSV missing SKU column; tried {SKU_HEADER_CANDIDATES!r}")

    st_col = pick("status")
    if not st_col:
        raise SystemExit("CSV missing status column.")

    dt_col = pick(*DT_HEADER)
    hw_col = pick(*HW_HEADER)
    dir_col = pick("expected_direction", "direction", "expected")

    return {
        "sku": sku_col,
        "status": st_col,
        "dt": dt_col or "",
        "hw": hw_col or "",
        "dir": dir_col or "",
    }


def _collect_classification_paths(output_dir: Path) -> list[Path]:
    hits = sorted(
        output_dir.rglob("classification.jsonl"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return hits


def _load_jsonl_index(paths: list[Path]) -> dict[str, dict[str, Any]]:
    """Later files first (caller should pass newest-first); first SKU win per file skipped if already set."""
    index: dict[str, dict[str, Any]] = {}
    for jp in reversed(paths):  # oldest -> newest so newest overrides
        try:
            lines = jp.read_text(encoding="utf-8").splitlines()
        except OSError as e:
            print(f"[warn] skip {jp}: {e}", file=sys.stderr)
            continue
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            skus = row.get("skus") or []
            if isinstance(skus, str):
                skus = [skus]
            for sku in skus:
                key = _norm_sku(str(sku))
                if key:
                    index[key] = row
    return index


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify audit CSV SKUs vs classification.jsonl.")
    ap.add_argument("--csv", required=True, type=Path, help="teresa_full_audit_fix_report_194.csv path")
    ap.add_argument("--output-dir", type=Path, help="OUTPUT root containing vendor runs")
    ap.add_argument(
        "--jsonl",
        type=Path,
        help="Explicit classification.jsonl (overrides --output-dir crawl)",
    )
    ap.add_argument(
        "--status-values",
        default=",".join(sorted(ACTIONABLE)),
        help="Comma-separated statuses to include",
    )
    args = ap.parse_args()

    active_status = {s.strip().upper() for s in args.status_values.split(",") if s.strip()}

    if args.jsonl:
        index = _load_jsonl_index([args.jsonl])
    else:
        if not args.output_dir:
            ap.error("--output-dir or --jsonl is required")
        od = args.output_dir.expanduser()
        if not od.is_dir():
            ap.error(f"output dir not found: {od}")
        paths = _collect_classification_paths(od)
        if not paths:
            ap.error(f"no classification.jsonl under {od}")
        print(f"[info] merging {len(paths)} classification.jsonl files (newest last wins SKU)")
        index = _load_jsonl_index(paths)

    text = args.csv.read_text(encoding="utf-8-sig", newline="")
    # csv.Sniffer unreliable on mixed delimiters — try comma first
    reader = csv.DictReader(text.splitlines())
    cols = _resolve_headers(reader.fieldnames)

    failures: list[str] = []
    checked = 0
    skipped = 0

    for row in reader:
        status_raw = (row.get(cols["status"]) or "").strip().upper()
        if status_raw not in active_status:
            skipped += 1
            continue
        sku_raw = (row.get(cols["sku"]) or "").strip()
        if not sku_raw:
            failures.append(f"status={status_raw} empty SKU")
            continue
        key = _norm_sku(sku_raw)

        exp_dt = (row.get(cols["dt"]) or "").strip() if cols["dt"] else ""
        exp_hw = (row.get(cols["hw"]) or "").strip() if cols["hw"] else ""
        if cols["dir"] and (not exp_dt or not exp_hw):
            d1, h1 = _parse_direction(row.get(cols["dir"]) or "")
            exp_dt = exp_dt or (d1 or "")
            exp_hw = exp_hw or (h1 or "")

        if not exp_dt and not exp_hw:
            failures.append(f"{sku_raw}: neither expected columns nor parsed expected_direction")
            continue

        hit = index.get(key)
        if not hit:
            failures.append(f"{sku_raw}: SKU not found in classification index")
            continue

        dt_ok = hw_ok = True
        if exp_dt:
            dt_ok = (hit.get("device_type") or "") == exp_dt
        if exp_hw:
            hw_ok = (hit.get("hw_type") or "") == exp_hw

        if not (dt_ok and hw_ok):
            failures.append(
                f"{sku_raw}: got device_type={hit.get('device_type')!r} hw_type={hit.get('hw_type')!r} "
                f"expected device_type={exp_dt!r} hw_type={exp_hw!r}"
            )
        checked += 1

    print(f"[ok] checked {checked} actionable rows ({skipped} rows skipped by status filter). Index size ~{len(index)} SKU keys.")
    if failures:
        print(f"[FAIL] {len(failures)} issue(s):\n", file=sys.stderr)
        for fline in failures:
            print(f"  - {fline}", file=sys.stderr)
        return 2

    print("[PASS] All checked rows match.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
