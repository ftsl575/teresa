"""
Shared test helpers for pipeline execution. Imported by test_regression.py and test_unknown_threshold.py.
"""

from pathlib import Path
from typing import Optional, Union

import pandas as pd

from src.core.parser import parse_excel
from src.core.normalizer import normalize_row
from src.rules.rules_engine import RuleSet
from src.core.classifier import classify_row


# Required column labels to identify the data table header in annotated Excel (may have preamble).
ANNOTATED_HEADER_REQUIRED = ("Option ID", "Entity Type")


def find_annotated_header_row(
    filepath: Union[Path, str], max_rows: int = 60
) -> Optional[int]:
    """
    Find the 0-based row index of the table header in an annotated (or similar) Excel file
    that may have a preamble (e.g. Solution Info). Scans the first max_rows rows for a row
    that contains the required column labels (Option ID and Entity Type).
    Returns None if not found.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Excel file not found: {filepath}")
    df = pd.read_excel(path, header=None, engine="openpyxl")
    for i in range(min(len(df), max_rows)):
        row = df.iloc[i]
        values = {str(v).strip() for v in row if pd.notna(v) and str(v).strip()}
        if all(required in values for required in ANNOTATED_HEADER_REQUIRED):
            return int(i)
    return None


def read_annotated_excel(filepath: Union[Path, str]) -> tuple[int, pd.DataFrame]:
    """
    Read an annotated Excel file using robust header detection. Returns (header_row_index, df)
    where df has column names from the detected header row. Raises ValueError if no header
    row is found.
    """
    header_row_index = find_annotated_header_row(filepath)
    if header_row_index is None:
        raise ValueError(
            f"No header row containing {ANNOTATED_HEADER_REQUIRED!r} found in {filepath}"
        )
    path = Path(filepath)
    df = pd.read_excel(path, header=header_row_index, engine="openpyxl")
    return (header_row_index, df)


def run_pipeline_in_memory(input_path: Path, rules_path: Path) -> tuple[list, list]:
    """Run parse → normalize → classify in memory. Returns (normalized_rows, classification_results). No disk I/O."""
    raw_rows = parse_excel(str(input_path))
    normalized = [normalize_row(r) for r in raw_rows]
    ruleset = RuleSet.load(str(rules_path))
    results = [classify_row(r, ruleset) for r in normalized]
    return (normalized, results)


def build_golden_rows(normalized_rows: list, classification_results: list) -> list[dict]:
    """Build golden-format dicts from pipeline results. Matches golden JSONL schema."""
    out = []
    for row, result in zip(normalized_rows, classification_results):
        out.append({
            "source_row_index": row.source_row_index,
            "row_kind": result.row_kind.value,
            "entity_type": result.entity_type.value if result.entity_type else None,
            "state": result.state.value if result.state else None,
            "matched_rule_id": result.matched_rule_id,
            "device_type": getattr(result, "device_type", None),
            "hw_type": getattr(result, "hw_type", None),
            "skus": list(row.skus),
        })
    return out
