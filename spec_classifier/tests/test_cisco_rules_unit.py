"""Unit tests for Cisco classification rules — device_type / hw_type matrix."""

from pathlib import Path

import pytest

from src.core.classifier import classify_row, EntityType
from src.core.normalizer import RowKind
from src.rules.rules_engine import RuleSet
from src.vendors.cisco.normalizer import CiscoNormalizedRow


@pytest.fixture
def cisco_ruleset():
    rules_path = Path(__file__).resolve().parent.parent / "rules" / "cisco_rules.yaml"
    return RuleSet.load(str(rules_path))


def _cisco_row(option_name: str, *, sku: str = "", is_bundle_root: bool = False) -> CiscoNormalizedRow:
    return CiscoNormalizedRow(
        source_row_index=1,
        row_kind=RowKind.ITEM,
        group_name=None,
        group_id=None,
        product_name=None,
        module_name="",
        option_name=option_name,
        option_id=None,
        skus=[sku] if sku else [],
        qty=1,
        option_price=0.0,
        is_bundle_root=is_bundle_root,
        service_duration_months=None,
    )


# ---------------------------------------------------------------------------
# Cisco device_type / hw_type matrix
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("option_name, sku, exp_device_type, exp_hw_type, exp_entity_type", [
    ("Cisco Fan Module", "FAN-T4-F", "fan", "fan", "HW"),
    ("AC Power Supply 1100W", "PWR-C1-1100WAC", "psu", "psu", "HW"),
    ("10GBASE-SR SFP Module", "SFP-10G-SR", "transceiver", "transceiver", "HW"),
    ("Stacking Cable 3M", "STACK-T4-3M", "cable", "cable", "HW"),
    ("32GB DRAM Memory", "MEM-32G-DDR4", "ram", "memory", "HW"),
    ("Slot Blank Filler", "", "blank_filler", "blank_filler", "HW"),
    ("Power Cord C13 C14", "", "power_cord", None, "HW"),
])
def test_cisco_device_type_and_hw_type(cisco_ruleset, option_name, sku, exp_device_type, exp_hw_type, exp_entity_type):
    row = _cisco_row(option_name, sku=sku)
    result = classify_row(row, cisco_ruleset)
    assert result.device_type == exp_device_type
    assert result.hw_type == exp_hw_type
    assert result.entity_type.value == exp_entity_type


# ---------------------------------------------------------------------------
# Cisco entity_type — one case per entity type
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("option_name, sku, is_bundle_root, exp_entity_type", [
    # BASE-C-001: is_bundle_root=True → BASE
    ("Cisco Catalyst 9300L-48P Switch", "C9300L-48P-4G-E", True, "BASE"),
    # HW-C-002: option_name matches \bfan\b → HW
    ("Cisco Fan Module", "FAN-T4-F", False, "HW"),
    # service_rules is empty in cisco_rules.yaml — SERVICE is unreachable for Cisco
    pytest.param(
        "Cisco SMARTnet 1 Year Service", "CON-SNT-C9300X48", False, "SERVICE",
        marks=pytest.mark.xfail(strict=False, reason="service_rules: [] in cisco_rules.yaml — SERVICE entity type not reachable"),
    ),
    # SOFTWARE-C-002: option_name matches \bDNA\b → SOFTWARE
    ("Cisco DNA Essentials License", "", False, "SOFTWARE"),
    # LOGISTIC-C-001: sku ^CAB-(?!9K|C13|C15|TA-|2Q|GUIDE) → LOGISTIC
    ("Console Cable 6ft with RJ45", "CAB-CONSOLE-RJ45", False, "LOGISTIC"),
])
def test_cisco_entity_type(cisco_ruleset, option_name, sku, is_bundle_root, exp_entity_type):
    row = _cisco_row(option_name, sku=sku, is_bundle_root=is_bundle_root)
    result = classify_row(row, cisco_ruleset)
    assert result.entity_type.value == exp_entity_type
