"""
Tests for hw_type_counts in collect_stats and run_summary.json.
"""

import pytest

from conftest import project_root, get_input_root_dell
from tests.helpers import run_pipeline_in_memory
from src.diagnostics.stats_collector import collect_stats
from src.core.classifier import HW_TYPE_VOCAB

# Exact expected hw_type_counts from real run on dl1.xlsx (taxonomy v2: memory, storage_drive, rail, blank_filler)
EXPECTED_DL1_HW_TYPE_COUNTS = {
    "tpm": 1,
    "chassis": 2,
    "cpu": 4,
    "memory": 1,
    "storage_controller": 2,
    "storage_drive": 3,
    "fan": 1,
    "psu": 2,
    "riser": 1,
    "network_adapter": 3,
    "cable": 1,
    "management": 1,
    "rail": 1,
}
EXPECTED_DL1_HW_TYPE_TOTAL = sum(EXPECTED_DL1_HW_TYPE_COUNTS.values())  # 23


def test_hw_type_vocab():
    assert len(HW_TYPE_VOCAB) == 25
    assert all(isinstance(v, str) and v for v in HW_TYPE_VOCAB)
    assert all(v == v.lower() for v in HW_TYPE_VOCAB)


@pytest.fixture
def dl1_stats():
    """Run pipeline on dl1.xlsx, call collect_stats, return stats dict."""
    root = project_root()
    input_root = get_input_root_dell()
    input_path = input_root / "dl1.xlsx"
    if not input_path.exists():
        pytest.skip(f"Input not found: {input_path} (set paths.input_root in config.local.yaml)")
    rules_path = root / "rules" / "dell_rules.yaml"
    _, classification_results = run_pipeline_in_memory("dell", input_path, rules_path)
    return collect_stats(classification_results)


def test_hw_type_counts_key_exists(dl1_stats):
    assert "hw_type_counts" in dl1_stats
    assert isinstance(dl1_stats["hw_type_counts"], dict)


def test_hw_type_counts_exact_values(dl1_stats):
    """Exact counts from dl1.xlsx run; all keys in HW_TYPE_VOCAB."""
    hw_type_counts = dl1_stats["hw_type_counts"]
    assert hw_type_counts == EXPECTED_DL1_HW_TYPE_COUNTS
    for key in hw_type_counts:
        assert key in HW_TYPE_VOCAB, f"hw_type_counts key {key!r} not in HW_TYPE_VOCAB"
    assert sum(hw_type_counts.values()) == EXPECTED_DL1_HW_TYPE_TOTAL


def test_hw_type_counts_sum_le_hw_entity_count(dl1_stats):
    hw_type_counts = dl1_stats["hw_type_counts"]
    entity_type_counts = dl1_stats["entity_type_counts"]
    hw_count = entity_type_counts.get("HW", 0)
    total_hw_type = sum(hw_type_counts.values())
    assert total_hw_type <= hw_count, (
        f"sum(hw_type_counts)={total_hw_type} should be <= entity_type_counts['HW']={hw_count}"
    )
