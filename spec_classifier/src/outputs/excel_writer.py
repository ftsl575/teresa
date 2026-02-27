"""
Generate cleaned spec Excel: only ITEM rows of included types and (optionally) PRESENT state.
"""

from pathlib import Path
from typing import List

import pandas as pd

from src.core.normalizer import NormalizedRow, RowKind
from src.core.classifier import ClassificationResult, EntityType
from src.core.state_detector import State


COLUMNS = [
    "Module Name",
    "Option Name",
    "SKUs",
    "Qty",
    "Option List Price",
    "Entity Type",
    "State",
]


def generate_cleaned_spec(
    normalized_rows: List[NormalizedRow],
    classification_results: List[ClassificationResult],
    config: dict,
    run_folder: Path,
) -> Path:
    """
    Build filtered DataFrame and save as run_folder/cleaned_spec.xlsx.

    INCLUDE: row_kind == ITEM, entity_type in include_types,
             and if include_only_present then state == PRESENT.
    EXCLUDE: HEADER always; optional exclude_types from config.
    """
    run_folder = Path(run_folder)
    cleaned = config.get("cleaned_spec") or {}
    include_types = set(cleaned.get("include_types") or ["BASE", "HW", "SOFTWARE", "SERVICE"])
    include_only_present = cleaned.get("include_only_present", True)

    rows = []
    for row, result in zip(normalized_rows, classification_results):
        if result.row_kind != RowKind.ITEM:
            continue
        if result.entity_type is None:
            continue
        if result.entity_type.value not in include_types:
            continue
        if include_only_present and (result.state is None or result.state != State.PRESENT):
            continue
        rows.append({
            "Module Name": row.module_name,
            "Option Name": row.option_name,
            "SKUs": ", ".join(row.skus) if row.skus else "",
            "Qty": row.qty,
            "Option List Price": row.option_price,
            "Entity Type": result.entity_type.value,
            "State": result.state.value if result.state else "",
        })

    df = pd.DataFrame(rows, columns=COLUMNS)
    out_path = run_folder / "cleaned_spec.xlsx"
    df.to_excel(out_path, index=False, engine="openpyxl")
    return out_path
