"""Unit tests for Cisco CCW parser."""

import pytest
import pandas as pd

from src.vendors.cisco.parser import find_header_row, find_data_end, parse_excel


def test_find_header_row_standard(tmp_path):
    """Header at row 17: Line Number and Part Number present."""
    import openpyxl
    path = tmp_path / "ccw.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Price Estimate"
    for i in range(17):
        ws.append(["x", "y"])
    ws.append(["Line Number", "Part Number", "Description"])
    wb.save(path)
    idx = find_header_row(str(path))
    assert idx == 17


def test_find_header_row_not_found(tmp_path):
    """No 'Line Number' in sheet -> ValueError."""
    import openpyxl
    path = tmp_path / "ccw.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Price Estimate"
    ws.append(["A", "B"])
    ws.append(["C", "D"])
    wb.save(path)
    with pytest.raises(ValueError, match="Header row"):
        find_header_row(str(path))


def test_find_data_end():
    """Five data rows (Part Number filled), then two empty -> count 5."""
    df = pd.DataFrame({
        "Part Number": ["P1", "P2", "P3", "P4", "P5", pd.NA, pd.NA],
        "Description": ["D"] * 7,
    })
    assert find_data_end(df) == 5


def test_find_data_end_empty():
    """No Part Number -> 0."""
    df = pd.DataFrame({"Part Number": [pd.NA, pd.NA], "Description": ["D", "D"]})
    assert find_data_end(df) == 0


def test_row_index_1based():
    """First data row __row_index__ = header_row_index + 2."""
    from conftest import project_root, get_input_root_cisco
    root = project_root()
    path = get_input_root_cisco() / "ccw_1.xlsx"
    if not path.exists():
        pytest.skip(f"Input not found: {path} (set paths.input_root in config.local.yaml)")
    rows, hdr = parse_excel(str(path))
    assert len(rows) >= 1
    assert rows[0]["__row_index__"] == hdr + 2


def test_parse_returns_tuple():
    """parse_excel returns (list, int)."""
    from conftest import project_root, get_input_root_cisco
    root = project_root()
    path = get_input_root_cisco() / "ccw_1.xlsx"
    if not path.exists():
        pytest.skip(f"Input not found: {path} (set paths.input_root in config.local.yaml)")
    result = parse_excel(str(path))
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert isinstance(result[0], list)
    assert isinstance(result[1], int)


@pytest.mark.parametrize("filename,expected_rows,expected_header", [("ccw_1.xlsx", 26, 17), ("ccw_2.xlsx", 82, 17)])
def test_parse_ccw_real(filename, expected_rows, expected_header):
    """Real files: ccw_1 26 rows header 17, ccw_2 82 rows header 17."""
    from conftest import project_root, get_input_root_cisco
    root = project_root()
    path = get_input_root_cisco() / filename
    if not path.exists():
        pytest.skip(f"Input not found: {path} (set paths.input_root in config.local.yaml)")
    rows, hdr = parse_excel(str(path))
    assert hdr == expected_header, f"header expected {expected_header}, got {hdr}"
    assert len(rows) == expected_rows, f"rows expected {expected_rows}, got {len(rows)}"
    assert "Line Number" in rows[0] and "Part Number" in rows[0] and "__row_index__" in rows[0]
