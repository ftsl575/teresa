"""
Collect and persist run statistics (counts by entity_type, state, rules).
"""

import hashlib
import json
from pathlib import Path
from typing import List

from src.core.normalizer import RowKind
from src.core.classifier import ClassificationResult, EntityType


def compute_file_hash(filepath: str, algorithm: str = "sha256") -> str:
    """Compute hex digest of a file. Default: SHA-256. Reusable for any file (rules, mapping, etc.)."""
    h = hashlib.new(algorithm)
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def collect_stats(classification_results: List[ClassificationResult]) -> dict:
    """
    Build stats dict: total_rows, header_rows_count, item_rows_count,
    entity_type_counts (ITEM only), state_counts (ITEM only), unknown_count, rules_stats.
    """
    total_rows = len(classification_results)
    header_rows_count = sum(1 for r in classification_results if r.row_kind == RowKind.HEADER)
    item_rows_count = sum(1 for r in classification_results if r.row_kind == RowKind.ITEM)

    entity_type_counts = {}
    state_counts = {}
    for r in classification_results:
        if r.row_kind != RowKind.ITEM:
            continue
        if r.entity_type is not None:
            key = r.entity_type.value
            entity_type_counts[key] = entity_type_counts.get(key, 0) + 1
        if r.state is not None:
            key = r.state.value
            state_counts[key] = state_counts.get(key, 0) + 1

    unknown_count = sum(
        1 for r in classification_results
        if r.row_kind == RowKind.ITEM and r.entity_type == EntityType.UNKNOWN
    )

    rules_stats = {}
    for r in classification_results:
        rid = r.matched_rule_id
        rules_stats[rid] = rules_stats.get(rid, 0) + 1

    device_type_counts = {}
    for r in classification_results:
        if r.row_kind != RowKind.ITEM or not getattr(r, "device_type", None):
            continue
        dt = r.device_type
        if dt:
            device_type_counts[dt] = device_type_counts.get(dt, 0) + 1

    hw_type_counts = {}
    for r in classification_results:
        if r.row_kind != RowKind.ITEM or not getattr(r, "hw_type", None):
            continue
        ht = r.hw_type
        if ht:
            hw_type_counts[ht] = hw_type_counts.get(ht, 0) + 1

    hw_type_null_count = sum(
        1 for r in classification_results
        if r.row_kind == RowKind.ITEM
        and r.entity_type == EntityType.HW
        and not getattr(r, "hw_type", None)
    )

    return {
        "total_rows": total_rows,
        "header_rows_count": header_rows_count,
        "item_rows_count": item_rows_count,
        "entity_type_counts": entity_type_counts,
        "state_counts": state_counts,
        "unknown_count": unknown_count,
        "rules_stats": rules_stats,
        "device_type_counts": device_type_counts,
        "hw_type_counts": hw_type_counts,
        "hw_type_null_count": hw_type_null_count,
    }


def save_run_summary(stats: dict, run_folder: Path) -> None:
    """Write run_summary.json (indent=2, ensure_ascii=False)."""
    path = Path(run_folder) / "run_summary.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
