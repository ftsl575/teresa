"""Tests for Huawei eDeal parser and HuaweiAdapter.can_parse()."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.vendors.huawei.parser import parse_excel
from src.vendors.huawei.adapter import HuaweiAdapter

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _huawei_input_dir() -> Path:
    """Resolve input/huawei directory via conftest helpers (avoids modifying conftest)."""
    # Import here to avoid circular issues at module level
    import conftest
    base = conftest.get_input_root()
    return base / "huawei"


def _huawei_files():
    d = _huawei_input_dir()
    if not d.exists():
        return []
    return sorted(d.glob("hu*.xlsx"))


def _skip_if_missing(path: Path):
    if not path.exists():
        pytest.skip(f"Input file not found: {path}")


# ---------------------------------------------------------------------------
# Test 1: parser returns header_row == 8 for all 5 files
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("filename", ["hu1.xlsx", "hu2.xlsx", "hu3.xlsx", "hu4.xlsx", "hu5.xlsx"])
def test_huawei_parse_returns_header_row_8(filename):
    path = _huawei_input_dir() / filename
    _skip_if_missing(path)
    _rows, header_row = parse_excel(str(path))
    assert header_row == 8, f"{filename}: expected header_row=8, got {header_row}"


# ---------------------------------------------------------------------------
# Test 2: first row in result has __row_index__ >= 10 (data_start_row=9, 0-based → row 10)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("filename", ["hu1.xlsx", "hu2.xlsx", "hu3.xlsx", "hu4.xlsx", "hu5.xlsx"])
def test_huawei_parse_returns_data_from_row_9(filename):
    path = _huawei_input_dir() / filename
    _skip_if_missing(path)
    rows, _hdr = parse_excel(str(path))
    assert len(rows) > 0, f"{filename}: parser returned 0 rows"
    first_idx = rows[0]["__row_index__"]
    assert first_idx >= 10, (
        f"{filename}: first row __row_index__={first_idx}, expected >= 10 "
        f"(0-based data_start_row=9 → 1-based row 10)"
    )


# ---------------------------------------------------------------------------
# Test 3: stop sentinel — EOM row and anything after it absent in result
# ---------------------------------------------------------------------------

def test_huawei_parse_stops_at_eom_sentinel_hu1():
    path = _huawei_input_dir() / "hu1.xlsx"
    _skip_if_missing(path)

    rows, _hdr = parse_excel(str(path))

    # No row in result should have Part Number == "EOM"
    eom_rows = [r for r in rows if str(r.get("Part Number", "") or "").strip() == "EOM"]
    assert eom_rows == [], (
        f"hu1.xlsx: sentinel row 'EOM' should not appear in result, "
        f"but got {len(eom_rows)} rows with Part Number='EOM'"
    )

    # Verify the sentinel actually exists in the raw file (parser stopped, not filtered)
    import openpyxl
    wb = openpyxl.load_workbook(str(path), read_only=True, data_only=False)
    try:
        ws = wb["AllInOne"]
        all_raw = list(ws.iter_rows(values_only=True))
    finally:
        wb.close()

    sentinel_row_idx = None
    for i, raw in enumerate(all_raw):
        col3 = raw[3] if len(raw) > 3 else None
        if col3 is not None and str(col3).strip() == "EOM":
            sentinel_row_idx = i
            break

    assert sentinel_row_idx is not None, (
        "hu1.xlsx: no EOM sentinel row found in raw file — "
        "recheck file or spec (col3 expected)"
    )

    # Verify parser actually stopped (not just filtered): no result row has
    # __row_index__ >= 1-based index of the sentinel row or later.
    sentinel_excel_row = sentinel_row_idx + 1  # convert 0-based to 1-based
    post_sentinel_result_rows = [
        r for r in rows if r["__row_index__"] >= sentinel_excel_row
    ]
    assert post_sentinel_result_rows == [], (
        f"hu1.xlsx: parser included {len(post_sentinel_result_rows)} row(s) "
        f"at or after EOM sentinel (1-based row {sentinel_excel_row}): "
        f"__row_index__ values = {[r['__row_index__'] for r in post_sentinel_result_rows]}"
    )


# ---------------------------------------------------------------------------
# Test 4: hu2.xlsx has empty col0 — parser must not crash and _col0_metadata is None/""
# ---------------------------------------------------------------------------

def test_huawei_parse_handles_empty_col0_hu2():
    path = _huawei_input_dir() / "hu2.xlsx"
    _skip_if_missing(path)

    rows, _hdr = parse_excel(str(path))
    assert len(rows) > 0, "hu2.xlsx: parser returned 0 rows"

    for row in rows:
        val = row.get("_col0_metadata")
        assert val is None or str(val).strip() == "", (
            f"hu2.xlsx: expected _col0_metadata to be None or empty, "
            f"got {val!r} at row {row.get('__row_index__')}"
        )


# ---------------------------------------------------------------------------
# Test 5: can_parse positive — all 5 hu*.xlsx must return True
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("filename", ["hu1.xlsx", "hu2.xlsx", "hu3.xlsx", "hu4.xlsx", "hu5.xlsx"])
def test_huawei_can_parse_positive_signature(filename):
    path = _huawei_input_dir() / filename
    _skip_if_missing(path)
    adapter = HuaweiAdapter()
    result = adapter.can_parse(str(path))
    assert result is True, f"{filename}: HuaweiAdapter.can_parse() returned {result}, expected True"


# ---------------------------------------------------------------------------
# Test 6: can_parse negative — other vendors must return False
# ---------------------------------------------------------------------------

def test_huawei_can_parse_negative_other_vendors():
    import conftest
    base = conftest.get_input_root()

    candidate_dirs = ["dell", "cisco", "hpe", "lenovo"]
    candidates = []
    for d in candidate_dirs:
        sub = base / d
        if sub.exists():
            candidates.extend(sorted(sub.glob("*.xlsx"))[:2])

    if not candidates:
        pytest.skip(
            "No other-vendor xlsx files found in input/{dell,cisco,hpe,lenovo}/ — "
            "cannot run negative can_parse test"
        )

    adapter = HuaweiAdapter()
    for path in candidates:
        result = adapter.can_parse(str(path))
        assert result is False, (
            f"HuaweiAdapter.can_parse() returned True for non-Huawei file: {path.name}"
        )


# ---------------------------------------------------------------------------
# Test 7: subcategory rollup rows must NOT survive parser cleansing
# ---------------------------------------------------------------------------

def test_huawei_parser_rejects_subcategory_rollup_rows_hu1():
    """
    hu1.xlsx contains subcategory rollup-rows where col 3 contains
    descriptive text (e.g. "Mainframe", "Software", "Power") instead of
    a real SKU. Parser must treat these as HEADER rows by setting
    Part Number to None / empty string.

    Real SKUs are ≤ 12-character alphanumeric without whitespace.
    """
    path = _huawei_input_dir() / "hu1.xlsx"
    _skip_if_missing(path)
    rows, _ = parse_excel(str(path))

    subcategory_phrases = {
        "CloudEngine",
        "Mainframe",
        "Software",
        "Power",
        "Optical Transceiver",
        "GE-SFP Optical Transceiver",
        "S5700 Series",
        "S5735-S Series",
    }

    for row in rows:
        pn = row.get("Part Number")
        if pn is None:
            continue
        pn_str = str(pn).strip()
        if not pn_str:
            continue
        assert " " not in pn_str, (
            f"Row {row.get('__row_index__')} has whitespace in Part Number "
            f"('{pn_str}') — subcategory rollup leaked through parser"
        )
        assert len(pn_str) <= 12, (
            f"Row {row.get('__row_index__')} has Part Number too long "
            f"('{pn_str}') — descriptive text leaked through parser"
        )
        for phrase in subcategory_phrases:
            assert phrase != pn_str, (
                f"Row {row.get('__row_index__')} has subcategory phrase "
                f"'{pn_str}' as Part Number — should be filtered to None"
            )
