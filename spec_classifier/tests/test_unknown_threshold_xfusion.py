"""Gate and guardrail tests for XFusion UNKNOWN count."""

import pytest
from pathlib import Path

from conftest import project_root, get_input_root_xfusion
from tests.helpers import run_pipeline_in_memory
from src.core.normalizer import RowKind
from src.core.classifier import EntityType

_GOLDEN_FILES = [f"xf{i}.xlsx" for i in range(1, 11)]


@pytest.mark.parametrize("filename", _GOLDEN_FILES)
def test_xfusion_unknown_count_zero_on_golden(filename):
    """Phase 4 gate: every golden fixture must classify with 0 UNKNOWN ITEMs."""
    root = project_root()
    input_root = get_input_root_xfusion()
    input_path = input_root / filename
    if not input_path.exists():
        pytest.skip(f"Input not found: {input_path}")
    rules_path = root / "rules" / "xfusion_rules.yaml"
    if not rules_path.exists():
        pytest.skip("rules/xfusion_rules.yaml not found")

    normalized, results = run_pipeline_in_memory("xfusion", input_path, rules_path)
    unknown_count = sum(
        1 for r in results
        if r.row_kind == RowKind.ITEM and r.entity_type == EntityType.UNKNOWN
    )
    assert unknown_count == 0, (
        f"UNKNOWN rows in {filename}: {unknown_count}. "
        "Gate requires 0 for golden files. Check xfusion_rules.yaml."
    )


def test_xfusion_unknown_threshold_below_5_percent():
    """Aggregate guardrail: across all xfX fixtures, UNKNOWN ITEMs <= 5%."""
    root = project_root()
    src_root = get_input_root_xfusion()
    rules_path = root / "rules" / "xfusion_rules.yaml"
    total_items = 0
    total_unknown = 0
    for i in range(1, 11):
        src = src_root / f"xf{i}.xlsx"
        if not src.exists():
            continue
        normalized, results = run_pipeline_in_memory("xfusion", src, rules_path)
        item_count = sum(1 for r in results if r.row_kind == RowKind.ITEM)
        unknown_count = sum(
            1 for r in results
            if r.row_kind == RowKind.ITEM and r.entity_type == EntityType.UNKNOWN
        )
        total_items += item_count
        total_unknown += unknown_count
    if total_items == 0:
        pytest.skip("no fixtures present")
    ratio = total_unknown / total_items
    assert ratio <= 0.05, (
        f"Unknown ratio {ratio:.2%} ({total_unknown}/{total_items}) exceeds 5% threshold"
    )
