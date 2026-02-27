"""
Cisco CCW (Commerce Workspace) Excel parser.
Sheet 'Price Estimate', header row by 'Line Number' + 'Part Number'.
"""

import pandas as pd
from pathlib import Path
from typing import List, Tuple


def find_header_row(filepath: str) -> int:
    """
    Читает лист 'Price Estimate' (строго, без fallback).
    Сканирует строки 0..99.
    Возвращает 0-based индекс строки где ОДНОВРЕМЕННО
    присутствуют "Line Number" И "Part Number" среди ячеек строки.
    Raises ValueError если sheet отсутствует (сообщение включает список доступных sheets)
    или header не найден.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Excel file not found: {filepath}")

    xl = pd.ExcelFile(path, engine="openpyxl")
    if "Price Estimate" not in xl.sheet_names:
        raise ValueError(
            f"Sheet 'Price Estimate' not found in {filepath}. "
            f"Available sheets: {xl.sheet_names}"
        )

    df = pd.read_excel(path, sheet_name="Price Estimate", header=None, engine="openpyxl")
    for i in range(min(len(df), 100)):
        row = df.iloc[i]
        cells = [str(v).strip() for v in row if pd.notna(v)]
        if "Line Number" in cells and "Part Number" in cells:
            return int(i)
    raise ValueError(f"Header row (Line Number + Part Number) not found in sheet 'Price Estimate' in {filepath}")


def find_data_end(df: pd.DataFrame) -> int:
    """
    df: DataFrame начиная с header row (первая строка = заголовки).
    Возвращает КОЛИЧЕСТВО строк данных.
    Определяет конец данных как (последний индекс строки где Part Number непустой) + 1.
    Part Number считается непустым если: not NaN, not None, not "".
    """
    if "Part Number" not in df.columns:
        return 0
    col = df["Part Number"]
    last_non_empty = -1
    for i, val in enumerate(col):
        if val is None or pd.isna(val):
            continue
        if str(val).strip() == "":
            continue
        last_non_empty = i
    return last_non_empty + 1


def parse_excel(filepath: str) -> Tuple[List[dict], int]:
    """
    1. Открыть sheet_name='Price Estimate' (строго)
    2. find_header_row() → header_row_index
    3. Прочитать DataFrame с header=header_row_index
    4. find_data_end() → количество строк данных
    5. Для каждой строки данных: dict из row.to_dict() + '__row_index__'
    6. __row_index__ = pandas_idx + header_row_index + 2 (1-based Excel row number)
    7. Вернуть (rows, header_row_index)
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Excel file not found: {filepath}")

    header_row_index = find_header_row(filepath)
    df = pd.read_excel(path, sheet_name="Price Estimate", header=header_row_index, engine="openpyxl")

    n_data = find_data_end(df)
    if n_data <= 0:
        return ([], header_row_index)

    rows: List[dict] = []
    for pandas_idx in range(n_data):
        row = df.iloc[pandas_idx]
        row_dict = row.to_dict()
        row_dict["__row_index__"] = int(pandas_idx) + header_row_index + 2
        rows.append(row_dict)

    return (rows, header_row_index)
