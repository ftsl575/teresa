"""
Annotated source Excel: same as input but with two extra columns — Entity Type and State.
All rows preserved; no rows removed.
"""

from pathlib import Path
from typing import List

import pandas as pd

from src.core.parser import find_header_row
from src.core.normalizer import NormalizedRow, RowKind
from src.core.classifier import ClassificationResult


def generate_annotated_source_excel(
    raw_rows: List[dict],
    normalized_rows: List[NormalizedRow],
    classification_results: List[ClassificationResult],
    original_excel_path: Path,
    run_folder: Path,
) -> Path:
    """
    Load original Excel, add columns Entity Type and State, save to run_folder/annotated_source.xlsx.
    Row count unchanged; mapping by source_row_index (Excel 1-based).
    """
    path = Path(original_excel_path)
    if not path.exists():
        raise FileNotFoundError(f"Original Excel not found: {path}")

    df = pd.read_excel(path, header=None, engine="openpyxl")
    header_row_index = find_header_row(str(path))
    if header_row_index is None:
        raise ValueError(f"No header row found in {path}")

    # Map Excel row number (1-based) -> classification result
    row_to_result = {}
    for i in range(len(normalized_rows)):
        excel_row = normalized_rows[i].source_row_index
        row_to_result[excel_row] = classification_results[i]

    # Add two columns (same length as df)
    entity_col = []
    state_col = []
    for r in range(len(df)):
        excel_row_1based = r + 1
        result = row_to_result.get(excel_row_1based)
        if r == header_row_index:
            entity_col.append("Entity Type")
            state_col.append("State")
        elif result and result.row_kind == RowKind.ITEM:
            entity_col.append(result.entity_type.value if result.entity_type else "")
            state_col.append(result.state.value if result.state else "")
        else:
            entity_col.append("")
            state_col.append("")

    df["Entity Type"] = entity_col
    df["State"] = state_col

    out_path = Path(run_folder) / "annotated_source.xlsx"
    df.to_excel(out_path, index=False, header=False, engine="openpyxl")
    return out_path
