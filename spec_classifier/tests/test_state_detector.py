"""
Unit tests for state detection (PRESENT / ABSENT / DISABLED).
"""

import pytest
import yaml
from pathlib import Path

from conftest import project_root
from src.core.state_detector import State, detect_state


def _load_state_rules():
    """Load state rules list from dell_rules.yaml (absent_keywords)."""
    path = Path(__file__).resolve().parent.parent / "rules" / "dell_rules.yaml"
    with open(path, encoding="utf-8") as f:
        rules = yaml.safe_load(f)
    return rules["state_rules"]["absent_keywords"]


@pytest.fixture
def state_rules():
    return _load_state_rules()


def test_no_trusted_platform_module_absent(state_rules):
    """'No Trusted Platform Module' -> ABSENT (matches leading 'No ')."""
    assert detect_state("No Trusted Platform Module", state_rules) == State.ABSENT


def test_dell_connectivity_client_disabled(state_rules):
    """'Dell Connectivity Client - Disabled' -> DISABLED."""
    assert detect_state("Dell Connectivity Client - Disabled", state_rules) == State.DISABLED


def test_intel_xeon_present(state_rules):
    """'Intel Xeon Silver' -> PRESENT (no match, default)."""
    assert detect_state("Intel Xeon Silver", state_rules) == State.PRESENT


def test_no_hdd_absent(state_rules):
    """'No HDD' -> ABSENT."""
    assert detect_state("No HDD", state_rules) == State.ABSENT


def test_none_keyword_absent(state_rules):
    """Option containing 'None' -> ABSENT."""
    assert detect_state("None", state_rules) == State.ABSENT


def test_empty_option_present(state_rules):
    """Empty option_name -> PRESENT (no pattern applied)."""
    assert detect_state("", state_rules) == State.PRESENT


def test_disabled_only(state_rules):
    """'Disabled' alone -> DISABLED."""
    assert detect_state("Disabled", state_rules) == State.DISABLED


def test_not_included_absent(state_rules):
    """'Not Included' -> ABSENT."""
    assert detect_state("Not Included", state_rules) == State.ABSENT


def test_blank_override_present():
    """DEC-003: 'No OCP - 2 Rear Blanks' -> PRESENT (override)."""
    from src.rules.rules_engine import RuleSet
    rs = RuleSet.load(str(project_root() / "rules" / "dell_rules.yaml"))
    assert detect_state("No OCP - 2 Rear Blanks", rs.get_state_rules()).value == "PRESENT"


def test_no_cable_absent():
    """DEC-001: '2 OCP - No Cable' -> ABSENT."""
    from src.rules.rules_engine import RuleSet
    rs = RuleSet.load(str(project_root() / "rules" / "dell_rules.yaml"))
    assert detect_state("2 OCP - No Cable", rs.get_state_rules()).value == "ABSENT"


def test_boss_blank_present():
    """Override: '1 Rear Blank' in 'No BOSS card, 1 Rear Blank' -> PRESENT (quantity + Rear Blanks)."""
    from src.rules.rules_engine import RuleSet
    rs = RuleSet.load(str(project_root() / "rules" / "dell_rules.yaml"))
    assert detect_state("No BOSS card, 1 Rear Blank", rs.get_state_rules()).value == "PRESENT"
