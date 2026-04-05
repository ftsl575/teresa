"""Tests for Lenovo DCSC parser (no external input files)."""

import sys
from pathlib import Path

import openpyxl
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.vendors.lenovo.parser import parse_excel


def _make_lenovo_xlsx(path, data_rows, *, include_terms=True):
    """Create a minimal Lenovo DCSC Quote xlsx for testing."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Quote"

    # Row 0 (1-based: row 1)
    ws.append([None, None, "Data Center Solution Configurator Quote", None, None])
    # Row 1
    ws.append([None, None, "Prepared for:", "Prepared by:"])
    # Row 2
    ws.append([None, None, None, "Price Date:", "26-Feb-26"])
    # Row 3 (empty)
    ws.append([])
    # Row 4
    ws.append([None, None, "Your final configuration..."])
    # Row 5 = header
    ws.append(["Part number", None, "Product Description", None, "Qty", "Price",
               "Total Part Price", "Export Control"])
    # Row 6 = sub-header (skipped by parser)
    ws.append([None, None, None, None, None, "(per unit)\nUS Dollar"])
    # Row 7 (empty)
    ws.append([])

    # Row 8+ = data rows
    for row in data_rows:
        ws.append(row)

    if include_terms:
        ws.append([])
        ws.append(["TERMS AND CONDITIONS:", None, "Some legal text..."])

    wb.save(path)
    wb.close()


def test_header_row_index(tmp_path):
    p = tmp_path / "test.xlsx"
    _make_lenovo_xlsx(p, [
        ["BYW4", None, "Intel Xeon Silver 4510", None, 2, 100.0, None, None],
    ])
    rows, hdr = parse_excel(str(p))
    assert hdr == 5


def test_data_start_at_row_8(tmp_path):
    p = tmp_path / "test.xlsx"
    _make_lenovo_xlsx(p, [
        ["BYW4", None, "Intel Xeon Silver 4510", None, 2, 100.0, None, None],
    ], include_terms=False)
    rows, _ = parse_excel(str(p))
    assert len(rows) == 1
    assert rows[0]["Part number"] == "BYW4"
    assert rows[0]["Product Description"] == "Intel Xeon Silver 4510"
    assert rows[0]["Qty"] == 2
    assert rows[0]["Price"] == 100.0
    assert rows[0]["__row_index__"] == 9  # 0-based row 8 → 1-based row 9


def test_terms_and_conditions_stops_parsing(tmp_path):
    """Empty row before T&C is included; T&C itself is excluded."""
    p = tmp_path / "test.xlsx"
    _make_lenovo_xlsx(p, [
        ["BYW4", None, "CPU", None, 2, 100.0, None, None],
        ["BWHS", None, "RAM", None, 8, 50.0, None, None],
    ], include_terms=True)
    rows, _ = parse_excel(str(p))
    # 2 data rows + 1 empty separator before T&C
    assert len(rows) == 3
    assert rows[0]["Part number"] == "BYW4"
    assert rows[1]["Part number"] == "BWHS"
    assert rows[2]["Part number"] is None  # empty separator


def test_multi_server_cto_rows(tmp_path):
    p = tmp_path / "test.xlsx"
    _make_lenovo_xlsx(p, [
        ["7D73CTO1WW", None, "Server : ThinkSystem SR630 V3", None, 1, 5000.0, None, None],
        ["BYW4", None, "Intel Xeon Silver 4510", None, 2, 100.0, None, None],
        [None, None, None, None, None, None, None, None],  # separator
        ["7D9ACTO1WW", None, "Server 1C DB : ThinkSystem SR665 V3", None, 1, 8000.0, None, None],
        ["BWHS", None, "RAM Module", None, 8, 50.0, None, None],
    ], include_terms=False)
    rows, _ = parse_excel(str(p))
    assert len(rows) == 5
    assert rows[0]["Part number"] == "7D73CTO1WW"
    assert rows[3]["Part number"] == "7D9ACTO1WW"


def test_missing_sheet_raises(tmp_path):
    p = tmp_path / "test.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "SomeOther"
    ws.append(["data"])
    wb.save(p)
    wb.close()
    with pytest.raises(ValueError, match="Sheet 'Quote' not found"):
        parse_excel(str(p))


def test_empty_rows_included_as_separators(tmp_path):
    p = tmp_path / "test.xlsx"
    _make_lenovo_xlsx(p, [
        ["BYW4", None, "CPU", None, 2, 100.0, None, None],
        [None, None, None, None, None, None, None, None],
        ["BWHS", None, "RAM", None, 8, 50.0, None, None],
    ], include_terms=False)
    rows, _ = parse_excel(str(p))
    assert len(rows) == 3
    assert rows[1]["Part number"] is None
    assert rows[1]["Product Description"] is None


def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        parse_excel("/nonexistent/path/file.xlsx")
