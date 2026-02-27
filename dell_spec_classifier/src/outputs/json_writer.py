"""
Save pipeline artifacts: raw rows, normalized rows, classification (JSON/JSONL), unknown/header rows (CSV).
"""

import csv
import json
from pathlib import Path
from typing import List, Optional, Union

from src.core.normalizer import NormalizedRow, RowKind
from src.core.classifier import ClassificationResult, EntityType


def _normalized_row_to_dict(row) -> dict:
    """Serialize NormalizedRow or compatible duck-type to dict.
    Core fields always present. Vendor-specific fields added if semantically present."""
    d = {
        "source_row_index": row.source_row_index,
        "row_kind": row.row_kind.value if hasattr(row.row_kind, "value") else str(row.row_kind),
        "group_name": row.group_name,
        "group_id": row.group_id,
        "product_name": row.product_name,
        "module_name": row.module_name,
        "option_name": row.option_name,
        "option_id": getattr(row, "option_id", None),
        "skus": row.skus,
        "qty": row.qty,
        "option_price": row.option_price,
    }
    _VENDOR_FIELDS = [
        "line_number", "bundle_id", "is_top_level", "is_bundle_root",
        "parent_line_number", "service_duration_months",
        "smart_account_mandatory", "lead_time_days",
        "unit_net_price", "disc_pct", "extended_net_price",
    ]
    for f in _VENDOR_FIELDS:
        val = getattr(row, f, None)
        if val is None:
            continue
        if isinstance(val, str) and val == "":
            continue
        d[f] = val
    return d


def _classification_result_to_dict(
    result: ClassificationResult,
    source_row_index: Optional[int] = None,
) -> dict:
    """Build dict for classification.jsonl.
    source_row_index is int when normalized_rows provided, null otherwise.
    Field is always present in output schema.
    """
    out = {
        "source_row_index": source_row_index,  # null when old call path, int when new
        "row_kind": result.row_kind.value,
        "entity_type": result.entity_type.value if result.entity_type else None,
        "state": result.state.value if result.state else None,
        "matched_rule_id": result.matched_rule_id,
        "warnings": result.warnings,
    }
    is_classified = (
        result.row_kind.value == "ITEM"
        and result.matched_rule_id != "UNKNOWN-000"
        and result.entity_type is not None
    )
    out["device_type"] = result.device_type if is_classified else None
    out["hw_type"] = getattr(result, "hw_type", None) if is_classified else None
    return out


def save_rows_raw(rows: List[dict], run_folder: Path) -> None:
    """Write raw parsed rows to rows_raw.json. float NaN replaced with null."""
    path = Path(run_folder) / "rows_raw.json"

    def _sanitize_nan(obj):
        """Replace float NaN with None only. str/int/bool/None unchanged."""
        if isinstance(obj, float) and obj != obj:
            return None
        if isinstance(obj, dict):
            return {k: _sanitize_nan(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_sanitize_nan(v) for v in obj]
        return obj

    with open(path, "w", encoding="utf-8") as f:
        json.dump(_sanitize_nan(rows), f, indent=2, ensure_ascii=False)


def save_rows_normalized(rows: List[NormalizedRow], run_folder: Path) -> None:
    """Write normalized rows to rows_normalized.json (including row_kind)."""
    path = Path(run_folder) / "rows_normalized.json"
    data = [_normalized_row_to_dict(r) for r in rows]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_classification(
    results: List[ClassificationResult],
    normalized_rows_or_run_folder: Union[List[NormalizedRow], Path],
    run_folder: Optional[Path] = None,
) -> None:
    """Write one JSON object per line to classification.jsonl.

    Backward-compatible signature:
      Old (smoke tests): save_classification(results, run_folder)
        → source_row_index: null in every row
      New (main.py):     save_classification(results, normalized_rows, run_folder)
        → source_row_index: int from normalized_rows[i].source_row_index
    """
    if isinstance(normalized_rows_or_run_folder, Path):
        # Old call path: second arg is run_folder
        actual_run_folder = normalized_rows_or_run_folder
        normalized_rows = None
    else:
        # New call path: second arg is normalized_rows
        normalized_rows = normalized_rows_or_run_folder
        actual_run_folder = run_folder
        assert len(results) == len(normalized_rows), \
            "Results and normalized_rows length mismatch"

    path = Path(actual_run_folder) / "classification.jsonl"
    with open(path, "w", encoding="utf-8") as f:
        for i, result in enumerate(results):
            source_row_index = (
                normalized_rows[i].source_row_index
                if normalized_rows is not None
                else None
            )
            line = json.dumps(
                _classification_result_to_dict(result, source_row_index),
                ensure_ascii=False,
            ) + "\n"
            f.write(line)


def save_unknown_rows(
    normalized_rows: List[NormalizedRow],
    classification_results: List[ClassificationResult],
    run_folder: Path,
) -> None:
    """Write only ITEM rows classified as UNKNOWN to unknown_rows.csv (utf-8-sig for Excel)."""
    path = Path(run_folder) / "unknown_rows.csv"
    fieldnames = [
        "source_row_index", "module_name", "option_name", "skus", "qty", "option_price", "matched_rule_id"
    ]
    rows_to_write = []
    for row, result in zip(normalized_rows, classification_results):
        if result.row_kind != RowKind.ITEM or result.entity_type != EntityType.UNKNOWN:
            continue
        rows_to_write.append({
            "source_row_index": row.source_row_index,
            "module_name": row.module_name,
            "option_name": row.option_name,
            "skus": ",".join(row.skus) if row.skus else "",
            "qty": row.qty,
            "option_price": row.option_price,
            "matched_rule_id": result.matched_rule_id,
        })
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows_to_write)


def save_header_rows(normalized_rows: List[NormalizedRow], run_folder: Path) -> None:
    """Write only HEADER rows to header_rows.csv (utf-8-sig for Excel)."""
    path = Path(run_folder) / "header_rows.csv"
    header_rows = [r for r in normalized_rows if r.row_kind == RowKind.HEADER]
    fieldnames = [
        "source_row_index", "group_name", "group_id", "product_name",
        "module_name", "option_name", "option_id", "skus", "qty", "option_price",
    ]
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for row in header_rows:
            w.writerow({
                "source_row_index": row.source_row_index,
                "group_name": row.group_name,
                "group_id": row.group_id,
                "product_name": row.product_name,
                "module_name": row.module_name,
                "option_name": row.option_name,
                "option_id": row.option_id,
                "skus": ",".join(row.skus) if row.skus else "",
                "qty": row.qty,
                "option_price": row.option_price,
            })
