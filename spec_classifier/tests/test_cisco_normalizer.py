"""Unit tests for Cisco CCW normalizer."""

from src.vendors.cisco.normalizer import CiscoNormalizedRow, normalize_cisco_rows


def _make_raw(line_numbers, descriptions, part_numbers=None, svc_durations=None, prices=None):
    """Helper to build raw_row dicts."""
    rows = []
    for i, (ln, desc) in enumerate(zip(line_numbers, descriptions)):
        row = {
            "Line Number": ln,
            "Part Number": part_numbers[i] if part_numbers else f"TEST-{ln.replace('.', '-')}",
            "Description": desc,
            "Qty": 1,
            "Unit List Price": prices[i] if prices else (100.0 if ln.endswith(".0") else 0.0),
            "Service Duration (Months)": svc_durations[i] if svc_durations else "---",
            "Smart Account Mandatory": "-",
            "Estimated Lead Time (Days)": 14,
            "Unit Net Price": 0.0,
            "Disc(%)": 0,
            "Extended Net Price": 0.0,
            "Pricing Term": None,
            "__row_index__": i + 19,
        }
        rows.append(row)
    return rows


def test_is_bundle_root_true():
    rows = _make_raw(["1.0", "1.1", "1.2"], ["Switch", "Opt A", "Opt B"])
    norm = normalize_cisco_rows(rows)
    assert norm[0].is_bundle_root is True


def test_is_bundle_root_false_standalone():
    rows = _make_raw(["3.0"], ["SFP Module"])
    norm = normalize_cisco_rows(rows)
    assert norm[0].is_bundle_root is False


def test_is_bundle_root_false_for_children():
    rows = _make_raw(["1.0", "1.1"], ["Switch", "Opt"])
    norm = normalize_cisco_rows(rows)
    assert norm[1].is_bundle_root is False


def test_bundle_id_extraction():
    all_rows = _make_raw(
        ["2.0", "2.1", "2.1.1"],
        ["Router", "DNA", "License"],
        svc_durations=["---", "---", "36"],
    )
    norm = normalize_cisco_rows(all_rows)
    assert norm[2].bundle_id == "2"


def test_parent_line_number_two_level():
    rows = _make_raw(["1.0", "1.1", "1.2"], ["Switch", "Fan", "PSU"])
    norm = normalize_cisco_rows(rows)
    assert norm[1].parent_line_number == "1.0"
    assert norm[2].parent_line_number == "1.0"
    assert norm[0].parent_line_number is None


def test_parent_line_number_three_level():
    rows = _make_raw(["2.0", "2.1", "2.1.1"], ["R", "DNA", "Lic"])
    norm = normalize_cisco_rows(rows)
    assert norm[2].parent_line_number == "2.1"
    assert norm[1].parent_line_number == "2.0"


def test_sku_trailing_equals():
    rows = _make_raw(["3.0"], ["SFP"], part_numbers=["SFP-10G-SR-S="])
    norm = normalize_cisco_rows(rows)
    assert norm[0].skus == ["SFP-10G-SR-S"]


def test_service_duration_int():
    rows = _make_raw(["1.0"], ["Lic"], svc_durations=[36])
    norm = normalize_cisco_rows(rows)
    assert norm[0].service_duration_months == 36


def test_service_duration_none():
    rows = _make_raw(["1.0"], ["HW"], svc_durations=["---"])
    norm = normalize_cisco_rows(rows)
    assert norm[0].service_duration_months is None


def test_module_name_from_bundle():
    rows = _make_raw(["1.0", "1.1"], ["Nexus 9300 Switch", "Fan Module"])
    norm = normalize_cisco_rows(rows)
    assert "Nexus 9300" in norm[1].module_name


def test_module_name_standalone_not_empty():
    """Standalone 3.0 must have module_name = its own Description, NOT empty."""
    rows = _make_raw(["3.0"], ["10GBASE-SR SFP Module"])
    norm = normalize_cisco_rows(rows)
    assert norm[0].module_name == "10GBASE-SR SFP Module"
    assert norm[0].module_name != ""


def test_row_kind_always_item():
    rows = _make_raw(["1.0", "1.1"], ["Switch", "Fan"])
    norm = normalize_cisco_rows(rows)
    for r in norm:
        assert r.row_kind.value == "ITEM"


def test_option_price_field_name():
    rows = _make_raw(["1.0"], ["Test"], prices=[99.5])
    norm = normalize_cisco_rows(rows)
    assert hasattr(norm[0], "option_price")
    assert norm[0].option_price == 99.5
