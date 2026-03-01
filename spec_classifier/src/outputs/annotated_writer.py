"""
Annotated source Excel: same as input but with extra columns — Entity Type, State, device_type, hw_type.
All rows preserved; no rows removed.
"""

from pathlib import Path
from typing import List, Optional

import pandas as pd

from src.core.normalizer import NormalizedRow, RowKind
from src.core.classifier import ClassificationResult


def generate_annotated_source_excel(
    raw_rows: List[dict],
    normalized_rows: List,
    classification_results: List[ClassificationResult],
    original_excel_path: Path,
    run_folder: Path,
    header_row_index: Optional[int] = None,
) -> Path:
    """
    Load original Excel, add columns Entity Type, State, device_type, hw_type,
    and save to run_folder/<stem>_annotated.xlsx.
    Row count unchanged; mapping by source_row_index (Excel 1-based).
    header_row_index from adapter: 0-based row for header labels; None is valid (e.g. formats with no fixed header row) — no header row highlight/freeze.
    """
    path = Path(original_excel_path)
    if not path.exists():
        raise FileNotFoundError(f"Original Excel not found: {path}")

    df = pd.read_excel(path, header=None, engine="openpyxl")
    # header_row_index=None is valid (format has no header row): use row 0 for labels, no highlight/freeze
    label_row = header_row_index if header_row_index is not None else 0

    # Map Excel row number (1-based) -> classification result
    row_to_result = {}
    for i in range(len(normalized_rows)):
        excel_row = normalized_rows[i].source_row_index
        row_to_result[excel_row] = classification_results[i]

    # Add four columns (same length as df)
    entity_col = []
    state_col = []
    device_type_col = []
    hw_type_col = []
    for r in range(len(df)):
        excel_row_1based = r + 1
        result = row_to_result.get(excel_row_1based)
        if r == label_row:
            entity_col.append("Entity Type")
            state_col.append("State")
            device_type_col.append("device_type")
            hw_type_col.append("hw_type")
        elif result and result.row_kind == RowKind.ITEM:
            entity_col.append(result.entity_type.value if result.entity_type else "")
            state_col.append(result.state.value if result.state else "")
            device_type_col.append(result.device_type or "")
            hw_type_col.append(result.hw_type or "")
        else:
            entity_col.append("")
            state_col.append("")
            device_type_col.append("")
            hw_type_col.append("")

    df["Entity Type"] = entity_col
    df["State"] = state_col
    df["device_type"] = device_type_col
    df["hw_type"] = hw_type_col

    # --- Vendor extension columns (extensible) ---
    # Each tuple: (attribute_name_on_NormalizedRow, column_header_in_excel)
    # When adding a new vendor with extra fields, add tuples here.
    VENDOR_EXTRA_COLS = [
        ("line_number", "line_number"),
        ("service_duration_months", "service_duration_months"),
    ]

    row_to_norm = {r.source_row_index: r for r in normalized_rows}
    for attr, col_name in VENDOR_EXTRA_COLS:
        if not any(getattr(r, attr, None) is not None for r in normalized_rows[:10]):
            continue
        col_data = []
        for r in range(len(df)):
            if r == label_row:
                col_data.append(col_name)
            else:
                excel_row_1based = r + 1
                norm = row_to_norm.get(excel_row_1based)
                val = getattr(norm, attr, None) if norm else None
                col_data.append(str(val) if val is not None else "")
        df[col_name] = col_data

    run_folder = Path(run_folder)
    stem = path.stem
    out_path = run_folder / f"{stem}_annotated.xlsx"
    df.to_excel(out_path, index=False, header=False, engine="openpyxl")
    return out_path
