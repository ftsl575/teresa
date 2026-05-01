"""Tests for Huawei eDeal normalizer."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.normalizer import NormalizedRow, RowKind
from src.vendors.huawei.normalizer import normalize_huawei_rows, HuaweiNormalizedRow


# ---------------------------------------------------------------------------
# Helper: synthetic raw row matching parser dict keys
# ---------------------------------------------------------------------------

def _raw(position_no="", part_number="", model="", description="",
         unit_qty=None, qty=None, total_price=None, extended_price=None,
         production_lt_days="", eom="", eos="", row_index=1):
    return {
        "Position No":         position_no,
        "Part Number":         part_number,
        "_col4_aux":           model,
        "Product Description": description,
        "Unit Quantity":       unit_qty,
        "Qty":                 qty,
        "Total Price":         total_price,
        "Extended Price":      extended_price,
        "production_lt_days":  production_lt_days,
        "eom":                 eom,
        "eos":                 eos,
        "_col0_metadata":      None,
        "_col1_sort_no":       None,
        "__row_index__":       row_index,
    }


# ---------------------------------------------------------------------------
# (1) Instances are HuaweiNormalizedRow
# ---------------------------------------------------------------------------

def test_normalizer_returns_huawei_normalized_row_instances():
    rows = normalize_huawei_rows([
        _raw(part_number="PN001", description="CPU"),
    ])
    assert len(rows) == 1
    assert isinstance(rows[0], HuaweiNormalizedRow)
    assert isinstance(rows[0], NormalizedRow)


# ---------------------------------------------------------------------------
# (2) Extension fields present with correct defaults
# ---------------------------------------------------------------------------

def test_extension_fields_present_with_defaults():
    fields = set(HuaweiNormalizedRow.__dataclass_fields__)
    base_fields = set(NormalizedRow.__dataclass_fields__)
    ext = fields - base_fields
    assert ext == {"position_no", "unit_qty", "total_price", "lead_time_days", "eom", "eos"}

    # Verify default values via a default-constructed instance
    base_defaults = {
        f: v.default
        for f, v in NormalizedRow.__dataclass_fields__.items()
        if v.default is not v.default_factory  # has a scalar default
    }
    # Just check the extension defaults directly from field metadata
    hw_fields = HuaweiNormalizedRow.__dataclass_fields__
    assert hw_fields["position_no"].default == ""
    assert hw_fields["unit_qty"].default == 0
    assert hw_fields["total_price"].default == 0.0
    assert hw_fields["lead_time_days"].default == ""
    assert hw_fields["eom"].default == ""
    assert hw_fields["eos"].default == ""


# ---------------------------------------------------------------------------
# (3) group_name propagation from top-level rollup
# ---------------------------------------------------------------------------

def test_group_name_propagation_top_level():
    rows = normalize_huawei_rows([
        _raw(position_no="1", description="Server Product A"),
        _raw(position_no="1.1.1", part_number="PN001", description="CPU"),
    ])
    assert len(rows) == 2
    assert rows[1].group_name == "Server Product A"


# ---------------------------------------------------------------------------
# (4) module_name propagation from mid-level rollup
# ---------------------------------------------------------------------------

def test_module_name_propagation_mid_level():
    rows = normalize_huawei_rows([
        _raw(position_no="1", description="Server"),
        _raw(position_no="1.1", description="Module CPU"),
        _raw(position_no="1.1.1", part_number="PN001"),
    ])
    assert len(rows) == 3
    assert rows[2].module_name == "Module CPU"


# ---------------------------------------------------------------------------
# (5) module_name resets on top-level switch  ← R10 critical
# ---------------------------------------------------------------------------

def test_module_name_resets_on_top_level_switch():
    rows = normalize_huawei_rows([
        _raw(position_no="1", description="Product A"),
        _raw(position_no="1.1", description="Module X"),
        _raw(position_no="1.1.1", part_number="PN001"),
        _raw(position_no="2", description="Product B"),
        _raw(position_no="2.1.1", part_number="PN002"),
    ])
    leaf_b = [r for r in rows if r.option_id == "PN002"]
    assert len(leaf_b) == 1, "Expected exactly one row with option_id='PN002'"
    assert leaf_b[0].module_name == "", (
        f"Expected module_name='' after top-level switch, got {leaf_b[0].module_name!r}"
    )
    assert leaf_b[0].group_name == "Product B", (
        f"Expected group_name='Product B', got {leaf_b[0].group_name!r}"
    )


# ---------------------------------------------------------------------------
# (6) row_kind ITEM when Part Number present
# ---------------------------------------------------------------------------

def test_row_kind_item_when_part_number_present():
    rows = normalize_huawei_rows([_raw(part_number="PN001")])
    r = rows[0]
    assert r.row_kind == RowKind.ITEM
    assert r.option_id == "PN001"
    assert r.skus == ["PN001"]


# ---------------------------------------------------------------------------
# (7) row_kind HEADER when Part Number absent
# ---------------------------------------------------------------------------

def test_row_kind_header_when_part_number_absent():
    rows = normalize_huawei_rows([_raw(part_number="")])
    r = rows[0]
    assert r.row_kind == RowKind.HEADER
    assert r.option_id is None
    assert r.skus == []


# ---------------------------------------------------------------------------
# (8) qty default = 1 when empty or zero
# ---------------------------------------------------------------------------

def test_qty_default_one_when_empty():
    r_none = normalize_huawei_rows([_raw(part_number="PN", qty=None)])[0]
    r_zero = normalize_huawei_rows([_raw(part_number="PN", qty=0)])[0]
    r_five = normalize_huawei_rows([_raw(part_number="PN", qty=5)])[0]
    assert r_none.qty == 1
    assert r_zero.qty == 1
    assert r_five.qty == 5


# ---------------------------------------------------------------------------
# (9) unit_qty extension extracted
# ---------------------------------------------------------------------------

def test_unit_qty_extension_extracted():
    r_set  = normalize_huawei_rows([_raw(part_number="PN", unit_qty=10)])[0]
    r_none = normalize_huawei_rows([_raw(part_number="PN", unit_qty=None)])[0]
    assert r_set.unit_qty == 10
    assert r_none.unit_qty == 0


# ---------------------------------------------------------------------------
# (10) total_price extension extracted from Extended Price
# ---------------------------------------------------------------------------

def test_total_price_extension_extracted():
    r_set  = normalize_huawei_rows([_raw(part_number="PN", extended_price=1234.56)])[0]
    r_none = normalize_huawei_rows([_raw(part_number="PN", extended_price=None)])[0]
    assert r_set.total_price == 1234.56
    assert r_none.total_price == 0.0


# ---------------------------------------------------------------------------
# (11) lead_time_days is str type in all cases
# ---------------------------------------------------------------------------

def test_lead_time_days_str_type():
    r_num  = normalize_huawei_rows([_raw(part_number="PN", production_lt_days="14")])[0]
    r_tbd  = normalize_huawei_rows([_raw(part_number="PN", production_lt_days="TBD")])[0]
    r_none = normalize_huawei_rows([_raw(part_number="PN", production_lt_days=None)])[0]
    assert r_num.lead_time_days == "14"
    assert r_tbd.lead_time_days == "TBD"
    assert r_none.lead_time_days == ""


# ---------------------------------------------------------------------------
# (12) product_name from _col4_aux (Model field)
# ---------------------------------------------------------------------------

def test_product_name_from_col4_model():
    r_set   = normalize_huawei_rows([_raw(part_number="PN", model="DL380 Gen11")])[0]
    r_empty = normalize_huawei_rows([_raw(part_number="PN", model="")])[0]
    r_none  = normalize_huawei_rows([_raw(part_number="PN", model=None)])[0]
    assert r_set.product_name == "DL380 Gen11"
    assert r_empty.product_name is None
    assert r_none.product_name is None


# ---------------------------------------------------------------------------
# (13) E2E smoke: parse + normalize real hu1.xlsx
# ---------------------------------------------------------------------------

def test_e2e_smoke_normalize_real_file_hu1():
    import conftest
    path = conftest.get_input_root() / "huawei" / "hu1.xlsx"
    if not path.exists():
        pytest.skip(f"Input file not found: {path}")

    from src.vendors.huawei.parser import parse_excel
    raw_rows, _hdr = parse_excel(str(path))
    result = normalize_huawei_rows(raw_rows)

    assert len(result) > 0, "E2E: normalize returned 0 rows"
    assert any(r.row_kind == RowKind.ITEM for r in result), \
        "E2E: no ITEM rows found"
    assert any(r.option_id is not None for r in result), \
        "E2E: no row has option_id"
    assert all(r.option_price >= 0.0 for r in result), \
        "E2E: some row has negative option_price"
    assert all(r.qty >= 1 for r in result), \
        "E2E: some row has qty < 1"
