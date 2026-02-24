"""
Tests for hw_type_counts in collect_stats and run_summary.json.
"""

import pytest

from conftest import project_root
from tests.helpers import run_pipeline_in_memory
from src.diagnostics.stats_collector import collect_stats

VALID_HW_TYPES = {
    "processor",
    "memory",
    "storage",
    "power_supply",
    "network",
    "storage_controller",
    "gpu",
    "cooling",
    "expansion",
    "security",
    "chassis",
    "cable",
    "motherboard",
    "management",
}


@pytest.fixture
def dl1_stats():
    """Run pipeline on dl1.xlsx, call collect_stats, return stats dict."""
    root = project_root()
    input_path = root / "test_data" / "dl1.xlsx"
    if not input_path.exists():
        pytest.skip("test_data/dl1.xlsx not found")
    rules_path = root / "rules" / "dell_rules.yaml"
    _, classification_results = run_pipeline_in_memory(input_path, rules_path)
    return collect_stats(classification_results)


def test_hw_type_counts_key_exists(dl1_stats):
    assert "hw_type_counts" in dl1_stats
    assert isinstance(dl1_stats["hw_type_counts"], dict)


def test_hw_type_counts_values_are_positive(dl1_stats):
    for key, value in dl1_stats["hw_type_counts"].items():
        assert isinstance(value, int), f"hw_type_counts[{key!r}] should be int"
        assert value > 0, f"hw_type_counts[{key!r}] should be > 0, got {value}"


def test_hw_type_counts_sum_le_hw_entity_count(dl1_stats):
    hw_type_counts = dl1_stats["hw_type_counts"]
    entity_type_counts = dl1_stats["entity_type_counts"]
    hw_count = entity_type_counts.get("HW", 0)
    total_hw_type = sum(hw_type_counts.values())
    assert total_hw_type <= hw_count, (
        f"sum(hw_type_counts)={total_hw_type} should be <= entity_type_counts['HW']={hw_count}"
    )


def test_hw_type_counts_keys_are_valid(dl1_stats):
    for key in dl1_stats["hw_type_counts"]:
        assert key in VALID_HW_TYPES, f"hw_type_counts key {key!r} not in known hw_type set"
