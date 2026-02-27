"""
Unit tests for classification rules (entity type and rule_id).
"""

import pytest
from pathlib import Path

from src.core.normalizer import NormalizedRow, RowKind
from src.core.classifier import EntityType, ClassificationResult, classify_row
from src.rules.rules_engine import RuleSet


def _ruleset():
    path = Path(__file__).resolve().parent.parent / "rules" / "dell_rules.yaml"
    return RuleSet.load(str(path))


@pytest.fixture
def ruleset():
    return _ruleset()


def _row(
    *,
    row_kind=RowKind.ITEM,
    module_name="",
    option_name="",
    source_row_index=1,
    **kwargs
) -> NormalizedRow:
    defaults = {
        "group_name": None,
        "group_id": None,
        "product_name": None,
        "option_id": None,
        "skus": [],
        "qty": 1,
        "option_price": 0.0,
    }
    defaults.update(kwargs)
    return NormalizedRow(
        source_row_index=source_row_index,
        row_kind=row_kind,
        module_name=module_name,
        option_name=option_name,
        **defaults,
    )


# --- HEADER ---


def test_header_skip(ruleset):
    """HEADER row -> entity_type=None, matched_rule_id=HEADER-SKIP."""
    row = _row(row_kind=RowKind.HEADER, module_name="", option_name="", skus=[])
    result = classify_row(row, ruleset)
    assert result.row_kind == RowKind.HEADER
    assert result.entity_type is None
    assert result.state is None
    assert result.matched_rule_id == "HEADER-SKIP"


# --- BASE ---


def test_base_detection(ruleset):
    """module_name='Base' -> BASE, BASE-001."""
    row = _row(module_name="Base", option_name="PowerEdge R760 Server")
    result = classify_row(row, ruleset)
    assert result.entity_type == EntityType.BASE
    assert result.matched_rule_id == "BASE-001"
    assert result.state.value == "PRESENT"


def test_base_poweredge(ruleset):
    """module_name='PowerEdge R760' -> BASE, BASE-002."""
    row = _row(module_name="PowerEdge R760", option_name="Server")
    result = classify_row(row, ruleset)
    assert result.entity_type == EntityType.BASE
    assert result.matched_rule_id == "BASE-002"


def test_base_poweredge_r6715(ruleset):
    """PowerEdge R6715 -> BASE, BASE-002."""
    row = _row(module_name="PowerEdge R6715", option_name="Server")
    result = classify_row(row, ruleset)
    assert result.entity_type == EntityType.BASE
    assert result.matched_rule_id == "BASE-002"


# --- SOFTWARE (critical) ---


def test_software_embedded_systems(ruleset):
    """Embedded Systems Management -> SOFTWARE, SOFTWARE-001 (critical)."""
    row = _row(
        module_name="Embedded Systems Management",
        option_name="iDRAC9, Enterprise 16G",
    )
    result = classify_row(row, ruleset)
    assert result.entity_type == EntityType.SOFTWARE
    assert result.matched_rule_id == "SOFTWARE-001"


def test_software_dell_secure_onboarding(ruleset):
    """Dell Secure Onboarding -> SOFTWARE, SOFTWARE-002 (critical)."""
    row = _row(
        module_name="Dell Secure Onboarding",
        option_name="Dell Secure Onboarding Client Disabled",
    )
    result = classify_row(row, ruleset)
    assert result.entity_type == EntityType.SOFTWARE
    assert result.matched_rule_id == "SOFTWARE-002"


def test_software_os_media(ruleset):
    """Operating System / OS Media -> SOFTWARE-003."""
    row = _row(module_name="Operating System", option_name="Windows Server")
    result = classify_row(row, ruleset)
    assert result.entity_type == EntityType.SOFTWARE
    assert result.matched_rule_id == "SOFTWARE-003"


def test_software_option_name_license(ruleset):
    """option_name with License -> SOFTWARE-004."""
    row = _row(module_name="Add-on", option_name="Windows License")
    result = classify_row(row, ruleset)
    assert result.entity_type == EntityType.SOFTWARE
    assert result.matched_rule_id == "SOFTWARE-004"


# --- HW (Chassis Configuration = HW, not CONFIG) ---


def test_hw_chassis_config(ruleset):
    """Chassis Configuration -> HW, HW-001 (not CONFIG!)."""
    row = _row(module_name="Chassis Configuration", option_name="4 x 3.5\"")
    result = classify_row(row, ruleset)
    assert result.entity_type == EntityType.HW
    assert result.matched_rule_id == "HW-001"


def test_hw_processor(ruleset):
    """Processor -> HW, HW-002."""
    row = _row(module_name="Processor", option_name="Intel Xeon Silver 4410Y")
    result = classify_row(row, ruleset)
    assert result.entity_type == EntityType.HW
    assert result.matched_rule_id == "HW-002"


def test_hw_tpm(ruleset):
    """Trusted Platform -> HW-003."""
    row = _row(module_name="Trusted Platform Module", option_name="No TPM")
    result = classify_row(row, ruleset)
    assert result.entity_type == EntityType.HW
    assert result.matched_rule_id == "HW-003"


# --- SERVICE ---


def test_service_prosupport(ruleset):
    """ProSupport / Dell Services -> SERVICE."""
    row = _row(
        module_name="Dell Services:Extended Service",
        option_name="ProSupport Plus",
    )
    result = classify_row(row, ruleset)
    assert result.entity_type == EntityType.SERVICE


def test_service_warranty(ruleset):
    """Option name with Warranty -> SERVICE-003."""
    row = _row(module_name="Services", option_name="3Y Warranty")
    result = classify_row(row, ruleset)
    assert result.entity_type == EntityType.SERVICE
    assert result.matched_rule_id == "SERVICE-003"


def test_service_no_warranty_upgrade(ruleset):
    """NO WARRANTY UPGRADE SELECTED -> SERVICE-005."""
    row = _row(module_name="Services", option_name="NO WARRANTY UPGRADE SELECTED")
    result = classify_row(row, ruleset)
    assert result.entity_type == EntityType.SERVICE
    assert result.matched_rule_id == "SERVICE-005"


# --- LOGISTIC ---


def test_logistic_shipping(ruleset):
    """Shipping -> LOGISTIC-001."""
    row = _row(module_name="Shipping", option_name="PowerEdge R660 Shipping")
    result = classify_row(row, ruleset)
    assert result.entity_type == EntityType.LOGISTIC
    assert result.matched_rule_id == "LOGISTIC-001"


# --- NOTE ---


def test_note_supports(ruleset):
    """'supports ONLY' -> NOTE (not SERVICE)."""
    row = _row(
        module_name="Processor",
        option_name="Motherboard supports ONLY CPUs below 250W",
    )
    result = classify_row(row, ruleset)
    assert result.entity_type == EntityType.NOTE
    assert result.matched_rule_id == "NOTE-001"


def test_note_motherboard(ruleset):
    """Option with 'Motherboard' -> NOTE-002."""
    row = _row(module_name="Info", option_name="Motherboard revision 2.0")
    result = classify_row(row, ruleset)
    assert result.entity_type == EntityType.NOTE
    assert result.matched_rule_id == "NOTE-002"


# --- CONFIG ---


def test_config_raid(ruleset):
    """RAID Configuration -> CONFIG-001."""
    row = _row(module_name="RAID Configuration", option_name="RAID 5")
    result = classify_row(row, ruleset)
    assert result.entity_type == EntityType.CONFIG
    assert result.matched_rule_id == "CONFIG-001"


# --- UNKNOWN ---


def test_unknown_no_match(ruleset):
    """No rule matches -> UNKNOWN, UNKNOWN-000, warning."""
    row = _row(module_name="Unknown Module XYZ", option_name="Some option")
    result = classify_row(row, ruleset)
    assert result.entity_type == EntityType.UNKNOWN
    assert result.matched_rule_id == "UNKNOWN-000"
    assert "No matching rule found" in result.warnings


# --- State in classification ---


def test_state_absent_in_classification(ruleset):
    """Option 'No Trusted Platform Module' -> state ABSENT (ITEM still classified as HW)."""
    row = _row(
        module_name="Trusted Platform Module",
        option_name="No Trusted Platform Module",
    )
    result = classify_row(row, ruleset)
    assert result.entity_type == EntityType.HW
    assert result.state is not None
    assert result.state.value == "ABSENT"


def test_state_disabled_in_classification(ruleset):
    """Option with Disabled -> state DISABLED."""
    row = _row(
        module_name="Embedded Systems Management",
        option_name="Dell Connectivity Client - Disabled",
    )
    result = classify_row(row, ruleset)
    assert result.entity_type == EntityType.SOFTWARE
    assert result.state is not None
    assert result.state.value == "DISABLED"


# --- Field dispatch: sku, is_bundle_root, unknown field ---


def test_match_rule_sku_field():
    """Rule with field: sku should match row where skus[0] matches pattern."""
    from src.rules.rules_engine import match_rule
    row = NormalizedRow(
        source_row_index=1,
        row_kind=RowKind.ITEM,
        group_name=None,
        group_id=None,
        product_name=None,
        module_name="",
        option_name="10GBASE-SR SFP Module",
        option_id=None,
        skus=["SFP-10G-SR-S"],
        qty=1,
        option_price=100.0,
    )
    rules = [{"field": "sku", "pattern": "^SFP", "entity_type": "HW", "rule_id": "HW-TEST"}]
    result = match_rule(row, rules)
    assert result is not None
    assert result["rule_id"] == "HW-TEST"


def test_match_rule_unknown_field_guaranteed_skip():
    """Unknown field must NEVER match, even with .* pattern."""
    from src.rules.rules_engine import match_rule
    row = NormalizedRow(
        source_row_index=1,
        row_kind=RowKind.ITEM,
        group_name=None,
        group_id=None,
        product_name=None,
        module_name="Test",
        option_name="Test",
        option_id=None,
        skus=[],
        qty=1,
        option_price=0.0,
    )
    rules = [{"field": "nonexistent_field", "pattern": ".*", "rule_id": "X"}]
    result = match_rule(row, rules)
    assert result is None, "Unknown field with .* pattern must NOT match"


def test_match_rule_is_bundle_root_lowercase():
    """is_bundle_root should be serialized as lowercase 'true'/'false'."""
    from src.rules.rules_engine import _get_field_value

    class FakeRow:
        module_name = ""
        option_name = ""
        skus = []
        is_bundle_root = True

    val = _get_field_value(FakeRow(), "is_bundle_root")
    assert val == "true", f"Expected 'true', got '{val}'"
