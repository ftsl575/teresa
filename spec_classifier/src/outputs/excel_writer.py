"""
Generate cleaned spec Excel: only ITEM rows of included types and (optionally) PRESENT state.
"""

from pathlib import Path
from typing import List

import pandas as pd

from src.core.normalizer import NormalizedRow, RowKind
from src.core.classifier import ClassificationResult, EntityType
from src.core.state_detector import State
from src.vendors.hpe.normalizer import HPENormalizedRow


COLUMNS = [
    "Group Name",
    "Group ID",
    "Module Name",
    "Option Name",
    "SKUs",
    "Qty",
    "Option ID",
    "Unit Price",
    "Device Type",
    "HW Type",
    "Entity Type",
    "State",
    "Source Row",
    "Rule ID",
]

# Extra columns emitted only when the input is an HPE BOM.
# Mirrors the vendor extension fields on HPENormalizedRow / annotated_writer.
HPE_EXTRA_COLUMNS = [
    "Config Name",
    "Lead Time",
    "Extended Price",
    "Product Type",
    "Factory Integrated",
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
    For HPE inputs, vendor extension columns are appended after the core columns.
    """
    run_folder = Path(run_folder)
    cleaned = config.get("cleaned_spec") or {}
    include_types = set(cleaned.get("include_types") or ["BASE", "HW", "SOFTWARE", "SERVICE"])
    include_only_present = cleaned.get("include_only_present", True)

    # P0-2 verified: isinstance checks Python type (not row data); bool() guards empty list
    is_hpe = bool(normalized_rows) and isinstance(normalized_rows[0], HPENormalizedRow)

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
        record = {
            "Group Name": row.group_name or "",
            "Group ID": row.group_id or "",
            "Module Name": row.module_name,
            "Option Name": row.option_name,
            "SKUs": ", ".join(row.skus) if row.skus else "",
            "Qty": row.qty,
            "Option ID": getattr(row, "option_id", None) or "",
            "Unit Price": row.option_price,
            "Device Type": result.device_type or "",
            "HW Type": getattr(result, "hw_type", None) or "",
            "Entity Type": result.entity_type.value,
            "State": result.state.value if result.state else "",
            "Source Row": row.source_row_index,
            "Rule ID": result.matched_rule_id if result.matched_rule_id else "",
        }
        if is_hpe:
            record["Config Name"] = getattr(row, "config_name", "") or ""
            record["Lead Time"] = getattr(row, "lead_time", "") or ""
            record["Extended Price"] = getattr(row, "extended_price", 0.0)
            record["Product Type"] = getattr(row, "product_type", "") or ""
            record["Factory Integrated"] = getattr(row, "is_factory_integrated", False)
        rows.append(record)

    final_columns = COLUMNS + (HPE_EXTRA_COLUMNS if is_hpe else [])
    df = pd.DataFrame(rows, columns=final_columns)
    out_path = run_folder / "cleaned_spec.xlsx"
    df.to_excel(out_path, index=False, engine="openpyxl")
    return out_path
