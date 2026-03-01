"""
Excel parser for column-based specification files (used by DellAdapter).
Finds header row by a sentinel column value ('Module Name'), then parses data rows
with __row_index__ = 1-based Excel row number.
"""

from pathlib import Path
from typing import List, Optional, Tuple

import pandas as pd


def find_header_row(filepath: str) -> Optional[int]:
    """
    Find the 0-based row index where the header (containing 'Module Name') is located.

    Reads the first sheet and scans rows until a cell contains exactly 'Module Name'.
    Returns None if not found.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Excel file not found: {filepath}")

    # Read without header to scan raw rows
    df = pd.read_excel(path, header=None, engine="openpyxl")
    for i in range(min(len(df), 20)):  # Limit scan to first 20 rows
        row = df.iloc[i]
        for val in row:
            if pd.notna(val) and str(val).strip() == "Module Name":
                return int(i)
    return None


def parse_excel(filepath: str) -> Tuple[List[dict], int]:
    """
    Parse Excel file into a list of row dicts and the header row index.

    - Uses find_header_row() once to detect header row.
    - Removes column 'Unnamed: 0' if present.
    - Does NOT drop empty rows (they may be HEADER rows for later processing).
    - Adds __row_index__ = Excel sheet row number (1-based): pandas_idx + header_row_index + 2.
    - Returns (list of row dicts, header_row_index) so callers avoid re-reading the file.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Excel file not found: {filepath}")

    header_row_index = find_header_row(filepath)
    if header_row_index is None:
        raise ValueError(f"No header row containing 'Module Name' found in {filepath}")

    df = pd.read_excel(path, header=header_row_index, engine="openpyxl")

    # Remove index column if present (often exported as 'Unnamed: 0')
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    # Do not drop empty rows — they can be HEADER rows
    result: List[dict] = []
    for pandas_idx, row in df.iterrows():
        row_dict = row.to_dict()
        # Excel row number: first data row = header_row_index + 2 (e.g. header at 3 → data at 4)
        row_dict["__row_index__"] = int(pandas_idx) + header_row_index + 2
        result.append(row_dict)

    return (result, header_row_index)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m src.core.parser <filepath>")
        sys.exit(1)
    rows, _ = parse_excel(sys.argv[1])
    print(f"Rows: {len(rows)}")
