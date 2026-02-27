"""
Unit tests for row normalizer and row_kind detection.
"""

import math
import pytest
from src.core.normalizer import (
    RowKind,
    NormalizedRow,
    detect_row_kind,
    normalize_row,
)


# --- detect_row_kind: HEADER cases (2-3 tests) ---


def test_detect_row_kind_header_all_empty_strings():
    """HEADER when Module Name, Option Name, SKUs are all empty strings."""
    raw = {"Module Name": "", "Option Name": "", "SKUs": ""}
    assert detect_row_kind(raw) == RowKind.HEADER


def test_detect_row_kind_header_all_none():
    """HEADER when all three key fields are None."""
    raw = {"Module Name": None, "Option Name": None, "SKUs": None}
    assert detect_row_kind(raw) == RowKind.HEADER


def test_detect_row_kind_header_whitespace_only():
    """HEADER when fields are only whitespace."""
    raw = {"Module Name": "  ", "Option Name": "\t", "SKUs": " "}
    assert detect_row_kind(raw) == RowKind.HEADER


# --- detect_row_kind: ITEM cases ---


def test_detect_row_kind_item_module_name_set():
    """ITEM when Module Name is set, others empty."""
    raw = {"Module Name": "Base", "Option Name": "", "SKUs": ""}
    assert detect_row_kind(raw) == RowKind.ITEM


def test_detect_row_kind_item_option_name_set():
    """ITEM when Option Name is set."""
    raw = {"Module Name": "", "Option Name": "PowerEdge R760", "SKUs": ""}
    assert detect_row_kind(raw) == RowKind.ITEM


def test_detect_row_kind_item_skus_set():
    """ITEM when SKUs is set."""
    raw = {"Module Name": "", "Option Name": "", "SKUs": "210-BDZY"}
    assert detect_row_kind(raw) == RowKind.ITEM


def test_detect_row_kind_item_all_set():
    """ITEM when all key fields are set."""
    raw = {
        "Module Name": "Base",
        "Option Name": "PowerEdge R760 Server",
        "SKUs": "210-BDZY",
    }
    assert detect_row_kind(raw) == RowKind.ITEM


# --- normalize_row: field parsing ---


def test_normalize_row_header_row():
    """Normalized HEADER row has row_kind=HEADER, empty skus, zero qty/price."""
    raw = {
        "__row_index__": 1,
        "Module Name": "",
        "Option Name": "",
        "SKUs": "",
        "Qty": 0,
        "Option List Price": 0,
    }
    row = normalize_row(raw)
    assert row.row_kind == RowKind.HEADER
    assert row.module_name == ""
    assert row.option_name == ""
    assert row.skus == []
    assert row.qty == 0
    assert row.option_price == 0.0
    assert row.source_row_index == 1


def test_normalize_row_item_single_sku():
    """ITEM row with single SKU parses correctly."""
    raw = {
        "__row_index__": 4,
        "Module Name": "Base",
        "Option Name": "PowerEdge R760 Server",
        "SKUs": "210-BDZY",
        "Qty": 1,
        "Option List Price": 4709.0,
    }
    row = normalize_row(raw)
    assert row.row_kind == RowKind.ITEM
    assert row.module_name == "Base"
    assert row.option_name == "PowerEdge R760 Server"
    assert row.skus == ["210-BDZY"]
    assert row.qty == 1
    assert row.option_price == 4709.0
    assert row.source_row_index == 4


def test_normalize_row_multiple_skus():
    """Multiple SKUs split by comma and stripped."""
    raw = {
        "__row_index__": 5,
        "Module Name": "Memory",
        "Option Name": "64GB",
        "SKUs": "338-CHSG, 379-BDCO",
        "Qty": 2,
        "Option List Price": 1200.5,
    }
    row = normalize_row(raw)
    assert row.row_kind == RowKind.ITEM
    assert row.skus == ["338-CHSG", "379-BDCO"]
    assert row.qty == 2
    assert row.option_price == 1200.5


def test_normalize_row_nan_handling():
    """HEADER when key fields are NaN (pandas-style)."""
    raw = {
        "__row_index__": 2,
        "Module Name": math.nan,
        "Option Name": math.nan,
        "SKUs": math.nan,
        "Qty": 1,
        "Option List Price": 24060.93,
    }
    row = normalize_row(raw)
    assert row.row_kind == RowKind.HEADER
    assert row.skus == []
    assert row.source_row_index == 2
