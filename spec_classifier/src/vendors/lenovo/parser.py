"""
Lenovo DCSC (Data Center Solution Configurator) Excel parser.
Sheet 'Quote', header row 5 (0-based), data from row 8.
Columns by fixed index: col0=Part number, col2=Product Description,
col4=Qty, col5=Price, col7=Export Control.
Col 6 (Total Part Price) contains Excel formulas — never used.
"""

import openpyxl
from pathlib import Path
from typing import List, Tuple


_HEADER_ROW = 5
_DATA_START_ROW = 8
_STOP_SENTINEL = "terms and conditions"


def parse_excel(filepath: str) -> Tuple[List[dict], int]:
    """
    Parse Lenovo DCSC Quote sheet.

    Returns (rows, header_row_index=5).
    Each row dict: Part number, Product Description, Qty, Price,
    Export Control, __row_index__ (1-based Excel row).
    data_only=False because col 6 has formulas we must ignore.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Excel file not found: {filepath}")

    wb = openpyxl.load_workbook(path, read_only=True, data_only=False)
    try:
        if "Quote" not in wb.sheetnames:
            raise ValueError(
                f"Sheet 'Quote' not found in {filepath}. "
                f"Available sheets: {wb.sheetnames}"
            )
        ws = wb["Quote"]
        all_rows = list(ws.iter_rows(values_only=True))

        rows: List[dict] = []

        for i in range(_DATA_START_ROW, len(all_rows)):
            raw = all_rows[i]
            excel_row_1based = i + 1

            col0 = raw[0] if len(raw) > 0 else None
            col2 = raw[2] if len(raw) > 2 else None
            col4 = raw[4] if len(raw) > 4 else None
            col5 = raw[5] if len(raw) > 5 else None
            col7 = raw[7] if len(raw) > 7 else None

            col0_str = str(col0).strip() if col0 is not None else ""
            if col0_str.lower().startswith(_STOP_SENTINEL):
                break

            row_dict = {
                "Part number": col0 if col0 is not None else None,
                "Product Description": col2 if col2 is not None else None,
                "Qty": col4,
                "Price": col5,
                "Export Control": col7,
                "__row_index__": excel_row_1based,
            }
            rows.append(row_dict)

        return (rows, _HEADER_ROW)
    finally:
        wb.close()
