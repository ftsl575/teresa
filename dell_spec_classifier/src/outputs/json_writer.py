"""
Save pipeline artifacts: raw rows, normalized rows, classification (JSON/JSONL), unknown/header rows (CSV).
"""

import csv
import json
from pathlib import Path
from typing import List

from src.core.normalizer import NormalizedRow, RowKind
from src.core.classifier import ClassificationResult, EntityType


def _normalized_row_to_dict(row: NormalizedRow) -> dict:
    return {
        "source_row_index": row.source_row_index,
        "row_kind": row.row_kind.value,
        "group_name": row.group_name,
        "group_id": row.group_id,
        "product_name": row.product_name,
        "module_name": row.module_name,
        "option_name": row.option_name,
        "option_id": row.option_id,
        "skus": row.skus,
        "qty": row.qty,
        "option_price": row.option_price,
    }


def _classification_result_to_dict(result: ClassificationResult) -> dict:
    return {
        "row_kind": result.row_kind.value,
        "entity_type": result.entity_type.value if result.entity_type else None,
        "state": result.state.value if result.state else None,
        "matched_rule_id": result.matched_rule_id,
        "warnings": result.warnings,
    }


def save_rows_raw(rows: List[dict], run_folder: Path) -> None:
    """Write raw parsed rows to rows_raw.json (indent=2, ensure_ascii=False)."""
    path = Path(run_folder) / "rows_raw.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)


def save_rows_normalized(rows: List[NormalizedRow], run_folder: Path) -> None:
    """Write normalized rows to rows_normalized.json (including row_kind)."""
    path = Path(run_folder) / "rows_normalized.json"
    data = [_normalized_row_to_dict(r) for r in rows]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_classification(results: List[ClassificationResult], run_folder: Path) -> None:
    """Write one JSON object per line to classification.jsonl."""
    path = Path(run_folder) / "classification.jsonl"
    with open(path, "w", encoding="utf-8") as f:
        for result in results:
            line = json.dumps(_classification_result_to_dict(result), ensure_ascii=False) + "\n"
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
