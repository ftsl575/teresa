"""Gate and guardrail tests for Cisco UNKNOWN count."""

import pytest
from pathlib import Path

from conftest import project_root
from tests.helpers import run_cisco_pipeline_in_memory
from src.core.normalizer import RowKind
from src.core.classifier import EntityType

_GOLDEN_FILES = ["ccw_1.xlsx", "ccw_2.xlsx"]


@pytest.mark.parametrize("filename", _GOLDEN_FILES)
def test_unknown_count_zero_cisco(filename):
    """
    Gate for current golden dataset: unknown_count must be exactly 0.
    If this fails, there is a gap in cisco_rules.yaml.
    """
    root = project_root()
    input_path = root / "test_data" / filename
    if not input_path.exists():
        pytest.skip(f"test_data/{filename} not found")
    rules_path = root / "rules" / "cisco_rules.yaml"
    if not rules_path.exists():
        pytest.skip("rules/cisco_rules.yaml not found")

    normalized, results = run_cisco_pipeline_in_memory(input_path, rules_path)
    unknown_count = sum(
        1 for r in results
        if r.row_kind == RowKind.ITEM and r.entity_type == EntityType.UNKNOWN
    )
    assert unknown_count == 0, (
        f"UNKNOWN rows in {filename}: {unknown_count}. "
        "Gate requires 0 for golden files. Check cisco_rules.yaml."
    )


@pytest.mark.parametrize("filename", _GOLDEN_FILES)
def test_unknown_threshold_cisco(filename):
    """
    Guardrail: UNKNOWN ≤ 5% for future files.
    On current golden files, unknown should be 0.
    """
    root = project_root()
    input_path = root / "test_data" / filename
    if not input_path.exists():
        pytest.skip(f"test_data/{filename} not found")
    rules_path = root / "rules" / "cisco_rules.yaml"
    if not rules_path.exists():
        pytest.skip("rules/cisco_rules.yaml not found")

    normalized, results = run_cisco_pipeline_in_memory(input_path, rules_path)
    item_count = sum(1 for r in results if r.row_kind == RowKind.ITEM)
    unknown_count = sum(
        1 for r in results
        if r.row_kind == RowKind.ITEM and r.entity_type == EntityType.UNKNOWN
    )
    ratio = unknown_count / item_count if item_count > 0 else 0
    assert ratio <= 0.05, (
        f"Unknown ratio {ratio:.2%} ({unknown_count}/{item_count}) exceeds 5% threshold"
    )
