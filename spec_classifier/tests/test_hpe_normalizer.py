"""Unit tests for HPE normalizer with in-memory raw dict fixtures."""

from src.core.normalizer import RowKind
from src.vendors.hpe.normalizer import normalize_hpe_rows


def test_normalize_hpe_empty_input():
    assert normalize_hpe_rows([]) == []


def test_normalize_hpe_basic_mapping_and_group_fields():
    raw_rows = [
        {
            "__row_index__": 7,
            "Product #": "P123 ABC",
            "Product Description": "Intel Xeon Gold 5416S",
            "Qty": "2",
            "Unit Price (USD)": "1999.5",
            "Config Name": "Config A",
            "Product Type": "HW",
            "Extended List Price (USD)": "3999.0",
            "Estimated Availability Lead Time": "7 days",
        }
    ]
    out = normalize_hpe_rows(raw_rows)
    row = out[0]
    assert row.source_row_index == 7
    assert row.row_kind == RowKind.ITEM
    assert row.option_id == "P123 ABC"
    assert row.skus == ["P123"]
    assert row.group_id == "P123"
    assert row.group_name == "Config A"
    assert row.module_name == "Config A"
    assert row.qty == 2
    assert row.option_price == 1999.5
    assert row.product_type == "HW"
    assert row.extended_price == 3999.0
    assert row.lead_time == "7 days"


def test_normalize_hpe_header_detection_on_empty_product_and_description():
    raw_rows = [
        {
            "__row_index__": 10,
            "Product #": None,
            "Product Description": "   ",
            "Qty": None,
            "Unit Price (USD)": None,
            "Config Name": None,
        }
    ]
    out = normalize_hpe_rows(raw_rows)
    row = out[0]
    assert row.row_kind == RowKind.HEADER
    assert row.option_id is None
    assert row.option_name == ""
    assert row.skus == []
    assert row.qty == 1
    assert row.option_price == 0.0
    assert row.group_name is None


def test_normalize_hpe_factory_integrated_flag_true():
    raw_rows = [
        {
            "__row_index__": 3,
            "Product #": "FI-001",
            "Product Description": "Factory Integrated",
            "Qty": 1,
            "Unit Price (USD)": 0,
            "Config Name": "Cfg",
        }
    ]
    out = normalize_hpe_rows(raw_rows)
    row = out[0]
    assert row.row_kind == RowKind.ITEM
    assert row.is_factory_integrated is True


def test_normalize_hpe_invalid_qty_and_price_fallback_to_defaults():
    raw_rows = [
        {
            "__row_index__": 11,
            "Product #": "SKU-1",
            "Product Description": "Some item",
            "Qty": "not-a-number",
            "Unit Price (USD)": "bad-price",
            "Config Name": "",
        }
    ]
    out = normalize_hpe_rows(raw_rows)
    row = out[0]
    assert row.qty == 1
    assert row.option_price == 0.0
    assert row.group_name is None
    assert row.module_name == ""


def test_normalize_hpe_option_id_and_sku_split_behavior():
    raw_rows = [
        {
            "__row_index__": 5,
            "Product #": "Q2R41A B21",
            "Product Description": "HPE drive",
            "Qty": 1,
            "Unit Price (USD)": 100.0,
        }
    ]
    out = normalize_hpe_rows(raw_rows)
    row = out[0]
    assert row.option_id == "Q2R41A B21"
    assert row.skus == ["Q2R41A"]
    assert row.group_id == "Q2R41A"
