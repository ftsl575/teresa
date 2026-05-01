"""Tests for xFusion FusionServer eDeal parser (synthetic in-memory xlsx)."""

import sys
from pathlib import Path

import openpyxl
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.vendors.xfusion.parser import parse_excel, _is_sku_shape


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_xfusion_xlsx(path, data_rows, *, header_overrides=None, sheet_name="AllInOne"):
    """
    Build a synthetic xFusion eDeal xlsx with the standard 9-row preamble:
      R1   = COL_SORTNO.0 tag row (col2 sentinel for can_parse)
      R2..R8 = padding (eDeal tags / blank)
      R9   = display headers (col2..col10)
      R10+ = data rows passed via data_rows
    Each entry of data_rows is a list — written verbatim to the worksheet.
    header_overrides (optional list[(col_idx, value)]) lets a test blank or
    rewrite specific R9 header cells (e.g. xf10-style price-header blanking).
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet_name

    # R1 — eDeal tag row; col2 (0-based) = COL_SORTNO.0
    ws.append([None, None, "COL_SORTNO.0", "COL_SALECODE.0", "COL_MODEL.0",
               "COL_DESCRIPTION.0", "COL_UNIT_QTY.0", "COL_ADD.0",
               "COL_UNIT_PRICE1.0", "COL_TOTAL_PRICE1.0", "COL_LEADTIME.0"])
    # R2..R8 — padding (eDeal expands these in real files)
    for _ in range(7):
        ws.append([None] * 11)
    # R9 — display headers
    headers = [None, None, "No.", "Part Number", "Model", "Description",
               "Unit Qty.", "Qty.", "Unit Price\n(USD)", "Total Price\n(USD)",
               "Production LT\n(Days)"]
    if header_overrides:
        for idx, val in header_overrides:
            headers[idx] = val
    ws.append(headers)
    # R10+ — data
    for r in data_rows:
        ws.append(r)

    wb.save(path)
    wb.close()


# ---------------------------------------------------------------------------
# Test 1: header_row_index == 8 (0-based)
# ---------------------------------------------------------------------------

def test_parser_returns_header_row_index_8(tmp_path):
    p = tmp_path / "xf.xlsx"
    _make_xfusion_xlsx(p, [
        [None, None, "", "0231Y091", "MODEL-X", "Description", 1, 2, 100.0, 200.0, "30"],
    ])
    _rows, header_row = parse_excel(str(p))
    assert header_row == 8


# ---------------------------------------------------------------------------
# Test 2: data starts at Excel row 10 (R0–R7 padding + R8 header are skipped)
# ---------------------------------------------------------------------------

def test_parser_skips_preamble_and_starts_at_row_10(tmp_path):
    p = tmp_path / "xf.xlsx"
    _make_xfusion_xlsx(p, [
        [None, None, "", "0231Y091", "MODEL-X", "Description", 1, 2, 100.0, 200.0, "30"],
    ])
    rows, _ = parse_excel(str(p))
    assert len(rows) == 1
    assert rows[0]["__row_index__"] == 10
    assert rows[0]["Part Number"] == "0231Y091"


# ---------------------------------------------------------------------------
# Test 3: hierarchical Position No values preserved as strings
# ---------------------------------------------------------------------------

def test_parser_preserves_position_no_as_string(tmp_path):
    p = tmp_path / "xf.xlsx"
    _make_xfusion_xlsx(p, [
        [None, None, None,    "1288H V7_Site1", None,             None,         None, None, None,    None,   None],   # level-0
        [None, None, "1",     "1288H V7",       "1288H V7",       None,         None, 2,    117158,  234316, None],   # level-1
        [None, None, "1.1",   "1288H V7",       "1288H V7",       None,         None, None, None,    234316, None],   # level-2
        [None, None, "1.1.1", "Memory",         "Memory",         None,         None, None, None,    180000, None],   # level-3
        [None, None, "",      "0620Y006-006",   "M548R64",        "DDR5 RDIMM", 12,   24,   7500,    180000, "49"],   # ITEM
    ])
    rows, _ = parse_excel(str(p))
    assert [r["Position No"] for r in rows] == [None, "1", "1.1", "1.1.1", None]
    assert rows[0]["__row_index__"] == 10


# ---------------------------------------------------------------------------
# Test 4: _is_sku_shape acceptance / rejection table
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("value,expected", [
    ("02313MMQ",        True),
    ("0231Y025",        True),
    ("04051916-015",    True),
    ("21242932-001",    True),
    ("0620Y006-006",    True),
    ("Memory",          False),     # all alpha, no digits
    ("Hard Disk(NVMe)", False),     # whitespace + parens
    ('Hard Disk(with 2.5" Front Panel)-NVMe', False),  # xf5 R197 case
    ("Spec_GPU_T4_3_Site1", False), # real site name — 19 chars, exceeds 14-char limit
    ("",                False),
    (None,              False),
    ("1288H V7",        False),     # whitespace
    ("Base Configuration", False),  # whitespace + length
])
def test_is_sku_shape_table(value, expected):
    assert _is_sku_shape(value) is expected


# ---------------------------------------------------------------------------
# Test 5: lead_time_days preserved as string ("Uncertain" / "-" / numeric)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("lt_value,expected_str", [
    ("Uncertain", "Uncertain"),
    ("-",         "-"),
    ("30",        "30"),
])
def test_lead_time_days_preserved_as_string(tmp_path, lt_value, expected_str):
    p = tmp_path / "xf.xlsx"
    _make_xfusion_xlsx(p, [
        [None, None, "", "0231Y091", "MX", "Desc", 1, 2, 100.0, 200.0, lt_value],
    ])
    rows, _ = parse_excel(str(p))
    assert len(rows) == 1
    assert str(rows[0]["production_lt_days"]) == expected_str


# ---------------------------------------------------------------------------
# Test 6: xf5-style no-SKU-shape sub-module label is preserved as Part Number
# (parser does NOT null it; normalizer routes it to HEADER via _is_sku_shape)
# ---------------------------------------------------------------------------

def test_parser_keeps_no_sku_shape_label(tmp_path):
    p = tmp_path / "xf.xlsx"
    label = 'Hard Disk(with 2.5" Front Panel)-NVMe'
    _make_xfusion_xlsx(p, [
        [None, None, "", label, None, None, None, None, None, None, None],
        [None, None, "", "0255Y686", "", "SSD,15360GB,NVMe", 5, 5, None, None, None],
    ])
    rows, _ = parse_excel(str(p))
    assert len(rows) == 2
    assert rows[0]["Part Number"] == label
    # Whitespace + parens guarantees it fails the SKU shape test (verified
    # in test_is_sku_shape_table — this row is just the parser side).
    assert _is_sku_shape(rows[0]["Part Number"]) is False


# ---------------------------------------------------------------------------
# Test 7: missing AllInOne sheet -> ValueError
# ---------------------------------------------------------------------------

def test_parser_raises_when_sheet_missing(tmp_path):
    p = tmp_path / "xf.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "OtherSheet"
    ws.append(["something"])
    wb.save(p); wb.close()
    with pytest.raises(ValueError, match=r"Sheet 'AllInOne' not found"):
        parse_excel(str(p))


# ---------------------------------------------------------------------------
# Test 8: missing file -> FileNotFoundError
# ---------------------------------------------------------------------------

def test_parser_raises_when_file_missing(tmp_path):
    missing = tmp_path / "does_not_exist.xlsx"
    with pytest.raises(FileNotFoundError):
        parse_excel(str(missing))


# ---------------------------------------------------------------------------
# Test 9: xf10-style — R8 price headers blanked, parser still extracts data
# (index-driven robustness: header text is irrelevant to parsing)
# ---------------------------------------------------------------------------

def test_parser_handles_blanked_price_headers(tmp_path):
    p = tmp_path / "xf.xlsx"
    _make_xfusion_xlsx(p, [
        [None, None, "", "0231Y091", "MX", "Desc", 1, 2, 100.0, 200.0, "30"],
    ], header_overrides=[(8, None), (9, None)])
    rows, hdr = parse_excel(str(p))
    assert hdr == 8
    assert len(rows) == 1
    assert rows[0]["Unit Price"] == 100.0
    assert rows[0]["Total Price"] == 200.0


# ---------------------------------------------------------------------------
# Test 10: fully-empty separator rows (col2 AND col3 both empty) are dropped
# ---------------------------------------------------------------------------

def test_parser_drops_fully_empty_separator_rows(tmp_path):
    p = tmp_path / "xf.xlsx"
    _make_xfusion_xlsx(p, [
        [None, None, "1.1.1", "Memory", "Memory", None, None, None, None, 180000, None],
        [None, None, None,    None,     None,     None, None, None, None, None,   None],
        [None, None, "",      "0620Y006-006", "M548R64", "DDR5 RDIMM", 12, 24, 7500, 180000, "49"],
    ])
    rows, _ = parse_excel(str(p))
    # 3 written - 1 fully-empty = 2 in result
    assert len(rows) == 2
    assert rows[0]["Part Number"] == "Memory"
    assert rows[1]["Part Number"] == "0620Y006-006"
