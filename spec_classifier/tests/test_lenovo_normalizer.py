"""Tests for Lenovo DCSC normalizer (no external input files)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.core.normalizer import RowKind
from src.vendors.lenovo.normalizer import normalize_lenovo_rows, LenovoNormalizedRow


def _raw(part_number=None, description=None, qty=None, price=None,
         export_control=None, row_index=1):
    return {
        "Part number": part_number,
        "Product Description": description,
        "Qty": qty,
        "Price": price,
        "Export Control": export_control,
        "__row_index__": row_index,
    }


def test_cto_row_is_item_with_config_name():
    rows = normalize_lenovo_rows([
        _raw("7D73CTO1WW", "Server : ThinkSystem SR630 V3-3yr Base Warranty", 1, 5000.0),
    ])
    assert len(rows) == 1
    r = rows[0]
    assert r.row_kind == RowKind.ITEM
    assert r.option_id == "7D73CTO1WW"
    assert r.skus == ["7D73CTO1WW"]
    assert r.option_price == 5000.0
    assert r.module_name == "Server"
    assert r.group_name == "Server"


def test_hw_row_inherits_config_name():
    rows = normalize_lenovo_rows([
        _raw("7D73CTO1WW", "Server : ThinkSystem SR630 V3", 1, 5000.0, row_index=9),
        _raw("BYW4", "Intel Xeon Silver 4510 12C", 2, 100.0, row_index=10),
    ])
    assert rows[1].module_name == "Server"
    assert rows[1].group_name == "Server"
    assert rows[1].option_name == "Intel Xeon Silver 4510 12C"
    assert rows[1].qty == 2


def test_empty_row_is_header():
    rows = normalize_lenovo_rows([
        _raw(None, None, None, None, None, row_index=15),
    ])
    assert len(rows) == 1
    assert rows[0].row_kind == RowKind.HEADER


def test_qty_default_is_1():
    rows = normalize_lenovo_rows([
        _raw("BYW4", "CPU", None, None),
    ])
    assert rows[0].qty == 1


def test_price_default_is_zero():
    rows = normalize_lenovo_rows([
        _raw("BYW4", "CPU", 1, None),
    ])
    assert rows[0].option_price == 0.0


def test_export_control_field():
    rows = normalize_lenovo_rows([
        _raw("C519", "NVIDIA HGX GPU", 1, 100000.0, "Yes"),
    ])
    assert rows[0].export_control == "Yes"


def test_export_control_empty():
    rows = normalize_lenovo_rows([
        _raw("BYW4", "CPU", 1, 100.0, None),
    ])
    assert rows[0].export_control == ""


def test_multi_server_config_names():
    rows = normalize_lenovo_rows([
        _raw("7D73CTO1WW", "1. Storage_cold : ThinkSystem SR650 V3", 1, 5000.0, row_index=9),
        _raw("BYW4", "CPU component", 2, 100.0, row_index=10),
        _raw(None, None, None, None, None, row_index=11),
        _raw("7D9ACTO1WW", "Server 1C DB : ThinkSystem SR665 V3", 1, 8000.0, row_index=12),
        _raw("BWHS", "RAM Module", 8, 50.0, row_index=13),
    ])
    assert rows[0].module_name == "1. Storage_cold"
    assert rows[1].module_name == "1. Storage_cold"
    assert rows[3].module_name == "Server 1C DB"
    assert rows[4].module_name == "Server 1C DB"


def test_isinstance_normalized_row():
    from src.core.normalizer import NormalizedRow
    rows = normalize_lenovo_rows([
        _raw("BYW4", "CPU", 1, 100.0),
    ])
    assert isinstance(rows[0], NormalizedRow)
    assert isinstance(rows[0], LenovoNormalizedRow)


def test_empty_input():
    assert normalize_lenovo_rows([]) == []
