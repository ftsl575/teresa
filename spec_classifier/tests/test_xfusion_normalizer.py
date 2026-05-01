"""Tests for xFusion eDeal normalizer (synthetic dict-rows; no xlsx)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.core.normalizer import RowKind
from src.vendors.xfusion.normalizer import (
    XFusionNormalizedRow,
    normalize_xfusion_rows,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _row(idx, *, position_no="", part_number="", model="", description="",
         unit_qty=None, qty=None, unit_price=None, total_price=None,
         lead_time_days=""):
    """Build a single raw-dict row in the shape produced by parse_excel."""
    return {
        "Position No":         position_no,
        "Part Number":         part_number,
        "Model":               model,
        "Description":         description,
        "Unit Qty.":           unit_qty,
        "Qty.":                qty,
        "Unit Price":          unit_price,
        "Total Price":         total_price,
        "production_lt_days":  lead_time_days,
        "__row_index__":       idx,
    }


def _items(normalized):
    return [r for r in normalized if r.row_kind == RowKind.ITEM]


# ---------------------------------------------------------------------------
# Test 1: level-0 site name with _Site1 suffix is stripped for group_name
# ---------------------------------------------------------------------------

def test_level0_strips_site_suffix():
    raw = [
        _row(10, part_number="Spec_GPU_T4_3_Site1"),
        _row(11, position_no="1", part_number="1288H V7", model="1288H V7"),
        _row(12, position_no="1.1.1", part_number="Memory", model="Memory"),
        _row(13, part_number="0620Y006-006", model="M548R64",
             description="DDR5 RDIMM", qty=24, unit_price=7500.0),
    ]
    items = _items(normalize_xfusion_rows(raw))
    assert len(items) == 1
    assert items[0].group_name == "Spec_GPU_T4_3"


# ---------------------------------------------------------------------------
# Test 2: Spare Parts groups (no _Site1 suffix) survive verbatim
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("site_label", [
    "5288 V7 Spare Parts Overseas",
    "1288H V7 Spare Parts Oversea",
])
def test_spare_parts_group_no_strip(site_label):
    raw = [
        _row(10, part_number=site_label),
        _row(11, part_number="0231Y091", model="MX",
             description="part desc", qty=1, unit_price=100.0),
    ]
    items = _items(normalize_xfusion_rows(raw))
    assert len(items) == 1
    assert items[0].group_name == site_label


# ---------------------------------------------------------------------------
# Test 3: level-1 sets product_name = col4 (Model)
# ---------------------------------------------------------------------------

def test_level1_sets_product_name_from_model():
    raw = [
        _row(10, part_number="1288H V7_Site1"),
        _row(11, position_no="1", part_number="1288H V7", model="1288H V7"),
        _row(12, position_no="1.1.1", part_number="Memory", model="Memory"),
        _row(13, part_number="0620Y006-006", model="M548R64",
             description="DDR5 RDIMM", qty=24, unit_price=7500.0),
    ]
    items = _items(normalize_xfusion_rows(raw))
    assert items[0].product_name == "1288H V7"


# ---------------------------------------------------------------------------
# Test 4: level-3 sets module_name = col3 (Part Number / sub-category label)
# ---------------------------------------------------------------------------

def test_level3_sets_module_name():
    raw = [
        _row(10, part_number="1288H V7_Site1"),
        _row(11, position_no="1", part_number="1288H V7", model="1288H V7"),
        _row(12, position_no="1.1.1", part_number="Memory", model="Memory"),
        _row(13, part_number="0620Y006-006", model="M548R64",
             description="DDR5 RDIMM", qty=24, unit_price=7500.0),
    ]
    items = _items(normalize_xfusion_rows(raw))
    assert items[0].module_name == "Memory"


# ---------------------------------------------------------------------------
# Test 5: ITEM row emission with full field mapping
# ---------------------------------------------------------------------------

def test_item_row_emission_full_mapping():
    raw = [
        _row(10, part_number="1288H V7_Site1"),
        _row(11, position_no="1", part_number="1288H V7", model="1288H V7"),
        _row(12, position_no="1.1.1", part_number="Memory", model="Memory"),
        _row(13,
             part_number="02313MMQ",
             model="DDR4-3200",
             description="32GB RDIMM",
             unit_qty=1, qty=8, unit_price=200.0, total_price=1600.0,
             lead_time_days="30"),
    ]
    items = _items(normalize_xfusion_rows(raw))
    assert len(items) == 1
    r = items[0]
    assert r.source_row_index == 13
    assert r.row_kind == RowKind.ITEM
    assert r.option_id == "02313MMQ"
    assert r.option_name == "32GB RDIMM"
    assert r.qty == 8
    assert r.option_price == 200.0
    assert r.skus == ["02313MMQ"]
    assert r.group_name == "1288H V7"
    assert r.product_name == "1288H V7"
    assert r.module_name == "Memory"


# ---------------------------------------------------------------------------
# Test 6: qty defaults to 1 when raw qty is None or 0
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("qty_raw", [None, 0, ""])
def test_qty_defaults_to_one(qty_raw):
    raw = [
        _row(10, part_number="A_Site1"),
        _row(11, position_no="1", part_number="P", model="P"),
        _row(12, position_no="1.1.1", part_number="Memory", model="Memory"),
        _row(13, part_number="02313MMQ", model="MX", description="desc",
             qty=qty_raw, unit_price=100.0),
    ]
    items = _items(normalize_xfusion_rows(raw))
    assert items[0].qty == 1


# ---------------------------------------------------------------------------
# Test 7: option_price defaults to 0.0 on missing/None Unit Price (no crash)
# ---------------------------------------------------------------------------

def test_option_price_defaults_to_zero_when_missing():
    raw = [
        _row(10, part_number="A_Site1"),
        _row(11, position_no="1", part_number="P", model="P"),
        _row(12, position_no="1.1.1", part_number="Memory", model="Memory"),
        _row(13, part_number="0255Y686", model="", description="SSD,15360GB",
             qty=5, unit_price=None),
    ]
    items = _items(normalize_xfusion_rows(raw))
    assert items[0].option_price == 0.0


# ---------------------------------------------------------------------------
# Test 8: 5 vendor extensions are populated on emitted ITEM rows
# ---------------------------------------------------------------------------

def test_vendor_extensions_populated_on_item():
    raw = [
        _row(10, part_number="A_Site1"),
        _row(11, position_no="1", part_number="P", model="P"),
        _row(12, position_no="1.1.1", part_number="Memory", model="Memory"),
        _row(13,
             part_number="02313MMQ",
             model="DDR4-3200",
             description="desc",
             unit_qty=2, qty=8,
             unit_price=200.0, total_price=1600.0,
             lead_time_days="49"),
    ]
    items = _items(normalize_xfusion_rows(raw))
    r = items[0]
    assert r.position_no == ""
    assert r.model == "DDR4-3200"
    assert r.unit_qty == 2
    assert r.total_price == 1600.0
    assert r.lead_time_days == "49"


# ---------------------------------------------------------------------------
# Test 9: lead_time_days "Uncertain" preserved verbatim (NOT coerced to int)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("lt", ["Uncertain", "-", "30"])
def test_lead_time_days_preserved_as_string(lt):
    raw = [
        _row(10, part_number="A_Site1"),
        _row(11, position_no="1", part_number="P", model="P"),
        _row(12, position_no="1.1.1", part_number="Memory", model="Memory"),
        _row(13, part_number="02313MMQ", model="MX", description="desc",
             qty=1, unit_price=100.0, lead_time_days=lt),
    ]
    items = _items(normalize_xfusion_rows(raw))
    assert items[0].lead_time_days == lt
    assert isinstance(items[0].lead_time_days, str)


# ---------------------------------------------------------------------------
# Test 10: module_name resets when a new level-1 server config begins
# ---------------------------------------------------------------------------

def test_module_name_resets_on_new_product():
    raw = [
        _row(10, part_number="Site1_Site1"),
        _row(11, position_no="1", part_number="Server-A", model="Server-A"),
        _row(12, position_no="1.1.1", part_number="Memory", model="Memory"),
        _row(13, part_number="02313MMQ", model="MX",
             description="32GB", qty=1, unit_price=200.0),
        # New level-1 server config begins; level-3 not yet declared.
        _row(14, position_no="2", part_number="Server-B", model="Server-B"),
        _row(15, part_number="0231Y025", model="PSU",
             description="2000W PSU", qty=2, unit_price=1400.0),
    ]
    items = _items(normalize_xfusion_rows(raw))
    assert len(items) == 2
    assert items[0].module_name == "Memory"
    assert items[0].product_name == "Server-A"
    assert items[1].module_name == ""
    assert items[1].product_name == "Server-B"


# ---------------------------------------------------------------------------
# Test 11: parser drops fully-empty separator rows, so normalizer never sees
# them — but if it did, they would not corrupt rollup. Simulate by passing
# a separator-shaped row (all empty) and assert rollup state survives.
# ---------------------------------------------------------------------------

def test_separator_row_does_not_reset_rollup():
    raw = [
        _row(10, part_number="Site1_Site1"),
        _row(11, position_no="1", part_number="Server-A", model="Server-A"),
        _row(12, position_no="1.1.1", part_number="Memory", model="Memory"),
        # Hypothetical leftover separator (parser actually drops these):
        _row(13),
        _row(14, part_number="02313MMQ", model="MX",
             description="32GB", qty=1, unit_price=200.0),
    ]
    items = _items(normalize_xfusion_rows(raw))
    assert len(items) == 1
    assert items[0].group_name == "Site1"
    assert items[0].module_name == "Memory"


# ---------------------------------------------------------------------------
# Test 12: module_name is GROUP-LOCAL (resets on new level-0 group)
# ---------------------------------------------------------------------------

def test_module_name_resets_on_new_group():
    raw = [
        _row(10, part_number="GroupA_Site1"),
        _row(11, position_no="1", part_number="Server-A", model="Server-A"),
        _row(12, position_no="1.1.1", part_number="Memory", model="Memory"),
        _row(13, part_number="02313MMQ", model="MX",
             description="32GB", qty=1, unit_price=200.0),
        # New level-0 group; module_name must reset to "".
        _row(14, part_number="GroupB Spare Parts Overseas"),
        _row(15, part_number="0231Y091", model="PN",
             description="spare", qty=1, unit_price=100.0),
    ]
    items = _items(normalize_xfusion_rows(raw))
    assert len(items) == 2
    assert items[0].group_name == "GroupA"
    assert items[0].module_name == "Memory"
    assert items[0].product_name == "Server-A"
    assert items[1].group_name == "GroupB Spare Parts Overseas"
    assert items[1].module_name == ""
    assert items[1].product_name is None  # no level-1 in spare parts group


# ---------------------------------------------------------------------------
# Test 13: xf5-style no-SKU-shape sub-module label classified as HEADER, not ITEM
# (covers R3 risk: silent no-price ITEM with option_price=0.0)
# ---------------------------------------------------------------------------

def test_no_sku_shape_label_is_header_not_item():
    label = 'Hard Disk(with 2.5" Front Panel)-NVMe'
    raw = [
        _row(10, part_number="Site_Site1"),
        _row(11, position_no="1", part_number="Server-A", model="Server-A"),
        _row(12, position_no="1.1.1", part_number="Memory", model="Memory"),
        _row(13, part_number=label),       # whitespace + parens → not a SKU
        _row(14, part_number="0255Y686", model="", description="SSD,15360GB",
             qty=5, unit_price=None),
    ]
    out = normalize_xfusion_rows(raw)
    items = [r for r in out if r.row_kind == RowKind.ITEM]
    headers = [r for r in out if r.row_kind == RowKind.HEADER]
    assert len(items) == 1
    assert items[0].option_id == "0255Y686"
    # The labelled row is HEADER (no whitespace-bearing pseudo-SKU leaked):
    label_row = next(r for r in headers if r.source_row_index == 13)
    assert label_row.row_kind == RowKind.HEADER


# ---------------------------------------------------------------------------
# Test 14: empty input returns empty list (no crash, no spurious rows)
# ---------------------------------------------------------------------------

def test_empty_input_returns_empty_list():
    assert normalize_xfusion_rows([]) == []


# ---------------------------------------------------------------------------
# Test 15: get_vendor_stats — CC Q4 three counters (Phase 2)
# ---------------------------------------------------------------------------

def test_vendor_stats():
    """CC Q4: get_vendor_stats returns server_configs_count,
    unique_models_count, spare_parts_groups_count."""
    from src.vendors.xfusion.adapter import XFusionAdapter

    def _item(idx, *, group_name, product_name, option_id):
        return XFusionNormalizedRow(
            source_row_index=idx,
            row_kind=RowKind.ITEM,
            group_name=group_name,
            group_id=None,
            product_name=product_name,
            module_name="",
            option_name="desc",
            option_id=option_id,
            skus=[option_id],
            qty=1,
            option_price=100.0,
        )

    def _header(idx, *, group_name=None, product_name=None):
        return XFusionNormalizedRow(
            source_row_index=idx,
            row_kind=RowKind.HEADER,
            group_name=group_name,
            group_id=None,
            product_name=product_name,
            module_name="",
            option_name="",
            option_id=None,
            skus=[],
            qty=0,
            option_price=0.0,
        )

    rows = [
        # group A: Spec_Server_A_2025, product "1288H V7" — 3 ITEMs
        _header(10, group_name="Spec_Server_A_2025"),
        _item(11, group_name="Spec_Server_A_2025", product_name="1288H V7", option_id="0231Y091"),
        _item(12, group_name="Spec_Server_A_2025", product_name="1288H V7", option_id="0620Y006-006"),
        _item(13, group_name="Spec_Server_A_2025", product_name="1288H V7", option_id="0253Y189"),
        # group B: Spec_Server_B_2025, product "2288H V7" — 2 ITEMs
        _header(14, group_name="Spec_Server_B_2025"),
        _item(15, group_name="Spec_Server_B_2025", product_name="2288H V7", option_id="0231Y025"),
        _item(16, group_name="Spec_Server_B_2025", product_name="2288H V7", option_id="0255Y686"),
        # group C: Spec_Server_C_2025, product "1288H V7" (duplicate model) — 1 ITEM
        _header(17, group_name="Spec_Server_C_2025"),
        _item(18, group_name="Spec_Server_C_2025", product_name="1288H V7", option_id="21243789"),
        # group D: Spare Parts — 2 ITEMs (product "5288 V7" from inherited level-1)
        _header(19, group_name="5288 V7 Spare Parts Overseas"),
        _item(20, group_name="5288 V7 Spare Parts Overseas", product_name="5288 V7", option_id="0231Y091"),
        _item(21, group_name="5288 V7 Spare Parts Overseas", product_name="5288 V7", option_id="0253Y189"),
    ]

    stats = XFusionAdapter().get_vendor_stats(rows)
    assert stats == {
        "server_configs_count":    3,   # A, B, C — spare parts excluded
        "unique_models_count":     3,   # "1288H V7", "2288H V7", "5288 V7"
        "spare_parts_groups_count": 1,  # group D only
    }
