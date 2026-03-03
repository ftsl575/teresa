"""Unit tests for HPE classification rules (no external input files)."""

from pathlib import Path

import pytest

from src.core.classifier import classify_row, EntityType
from src.core.normalizer import RowKind
from src.rules.rules_engine import RuleSet
from src.vendors.hpe.normalizer import HPENormalizedRow


@pytest.fixture
def hpe_ruleset():
    rules_path = Path(__file__).resolve().parent.parent / "rules" / "hpe_rules.yaml"
    return RuleSet.load(str(rules_path))


def _hpe_row(option_name: str, *, option_id: str = "SKU-1", module_name: str = "") -> HPENormalizedRow:
    return HPENormalizedRow(
        source_row_index=1,
        row_kind=RowKind.ITEM,
        group_name=None,
        group_id=None,
        product_name=None,
        module_name=module_name,
        option_name=option_name,
        option_id=option_id,
        skus=[option_id],
        qty=1,
        option_price=100.0,
    )


def test_hpe_classify_hw_row(hpe_ruleset):
    row = _hpe_row("Intel Xeon Gold 5416S")
    result = classify_row(row, hpe_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.matched_rule_id == "HW-H-GLOBAL-002"


def test_hpe_classify_service_row(hpe_ruleset):
    row = _hpe_row("3Y ProCare warranty service")
    result = classify_row(row, hpe_ruleset)
    assert result.entity_type == EntityType.SERVICE
    assert result.matched_rule_id == "SERVICE-H-001"


def test_hpe_classify_logistic_row(hpe_ruleset):
    row = _hpe_row("Shipping and delivery service")
    result = classify_row(row, hpe_ruleset)
    assert result.entity_type == EntityType.LOGISTIC
    assert result.matched_rule_id == "LOGISTIC-H-001"


def test_hpe_classify_unknown_row(hpe_ruleset):
    row = _hpe_row("Totally unmatched row text")
    result = classify_row(row, hpe_ruleset)
    assert result.entity_type == EntityType.UNKNOWN
    assert result.matched_rule_id == "UNKNOWN-000"
    assert "No matching rule found" in result.warnings


def test_hpe_factory_integrated_matches_config_rule(hpe_ruleset):
    row = _hpe_row("Factory Integrated")
    result = classify_row(row, hpe_ruleset)
    assert result.entity_type == EntityType.CONFIG
    assert result.matched_rule_id == "CONFIG-H-001"
