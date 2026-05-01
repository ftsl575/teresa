"""Gate and guardrail tests for Huawei UNKNOWN count."""

import pytest
from pathlib import Path

from conftest import project_root, get_input_root_huawei
from tests.helpers import run_pipeline_in_memory
from src.core.normalizer import RowKind
from src.core.classifier import EntityType

_GOLDEN_FILES = ["hu1.xlsx", "hu2.xlsx", "hu3.xlsx", "hu4.xlsx", "hu5.xlsx"]


@pytest.mark.parametrize("filename", _GOLDEN_FILES)
def test_unknown_count_zero_huawei(filename):
    """
    Gate for current golden dataset: unknown_count must be exactly 0.
    If this fails, there is a gap in huawei_rules.yaml.
    """
    root = project_root()
    input_root = get_input_root_huawei()
    input_path = input_root / filename
    if not input_path.exists():
        pytest.skip(f"Input not found: {input_path} (set paths.input_root in config.local.yaml)")
    rules_path = root / "rules" / "huawei_rules.yaml"
    if not rules_path.exists():
        pytest.skip("rules/huawei_rules.yaml not found")

    normalized, results = run_pipeline_in_memory("huawei", input_path, rules_path)
    unknown_count = sum(
        1 for r in results
        if r.row_kind == RowKind.ITEM and r.entity_type == EntityType.UNKNOWN
    )
    assert unknown_count == 0, (
        f"UNKNOWN rows in {filename}: {unknown_count}. "
        "Gate requires 0 for golden files. Check huawei_rules.yaml."
    )


@pytest.mark.parametrize("filename", _GOLDEN_FILES)
def test_unknown_threshold_huawei(filename):
    """
    Guardrail: UNKNOWN ≤ 5% for future files.
    On current golden files, unknown should be 0.
    """
    root = project_root()
    input_root = get_input_root_huawei()
    input_path = input_root / filename
    if not input_path.exists():
        pytest.skip(f"Input not found: {input_path} (set paths.input_root in config.local.yaml)")
    rules_path = root / "rules" / "huawei_rules.yaml"
    if not rules_path.exists():
        pytest.skip("rules/huawei_rules.yaml not found")

    normalized, results = run_pipeline_in_memory("huawei", input_path, rules_path)
    item_count = sum(1 for r in results if r.row_kind == RowKind.ITEM)
    unknown_count = sum(
        1 for r in results
        if r.row_kind == RowKind.ITEM and r.entity_type == EntityType.UNKNOWN
    )
    ratio = unknown_count / item_count if item_count > 0 else 0
    assert ratio <= 0.05, (
        f"Unknown ratio {ratio:.2%} ({unknown_count}/{item_count}) exceeds 5% threshold"
    )
