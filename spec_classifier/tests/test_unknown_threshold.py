"""
Unknown threshold test: for each dl run pipeline in memory, assert
unknown_count / item_rows_count <= 0.05. Skip if xlsx not found.
"""

import pytest
from pathlib import Path

from src.diagnostics.stats_collector import collect_stats

from conftest import project_root
from tests.helpers import run_pipeline_in_memory

UNKNOWN_RATIO_THRESHOLD = 0.05


@pytest.mark.parametrize("filename", ["dl1.xlsx", "dl2.xlsx", "dl3.xlsx", "dl4.xlsx", "dl5.xlsx"])
def test_unknown_ratio_below_threshold(filename):
    """Run pipeline for filename; assert unknown_count / item_rows_count <= 0.05."""
    root = project_root()
    input_path = root / "test_data" / filename
    if not input_path.exists():
        pytest.skip(f"test_data/{filename} not found at {input_path}")

    rules_path = root / "rules" / "dell_rules.yaml"
    assert rules_path.exists(), f"rules/dell_rules.yaml not found at {rules_path}"

    _, classification_results = run_pipeline_in_memory(input_path, rules_path)
    stats = collect_stats(classification_results)

    unknown_count = stats.get("unknown_count", 0)
    item_rows_count = stats.get("item_rows_count", 0)
    if item_rows_count == 0:
        pytest.skip(f"item_rows_count is 0 for {filename}")

    ratio = unknown_count / item_rows_count
    assert ratio <= UNKNOWN_RATIO_THRESHOLD, (
        f"unknown_count / item_rows_count = {unknown_count}/{item_rows_count} = {ratio:.4f} > {UNKNOWN_RATIO_THRESHOLD}"
    )
