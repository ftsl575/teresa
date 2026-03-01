"""Gate and guardrail tests for HPE UNKNOWN count. XLSX from config paths.input_root/hpe/, not test_data."""

import pytest
from pathlib import Path

from conftest import project_root, get_input_root, load_config
from tests.helpers import run_pipeline_in_memory
from src.core.normalizer import RowKind
from src.core.classifier import EntityType

HP_FILES = ["hp1.xlsx", "hp2.xlsx", "hp3.xlsx", "hp4.xlsx", "hp5.xlsx", "hp6.xlsx", "hp7.xlsx", "hp8.xlsx"]


@pytest.mark.parametrize("filename", HP_FILES)
def test_unknown_count_zero_hpe(filename):
    """Gate: unknown_count must be 0 for golden HPE files. If file missing at input_root/hpe/ → skip."""
    root = project_root()
    input_root = get_input_root()
    input_path = input_root / filename
    if not input_path.exists():
        pytest.skip(f"Input not found: {input_path} (set paths.input_root in config.local.yaml)")
    rules_path = root / "rules" / "hpe_rules.yaml"
    if not rules_path.exists():
        pytest.skip("rules/hpe_rules.yaml not found")

    config = load_config()
    normalized, results = run_pipeline_in_memory("hpe", input_path, rules_path, config)
    unknown_count = sum(
        1 for r in results
        if r.row_kind == RowKind.ITEM and r.entity_type == EntityType.UNKNOWN
    )
    assert unknown_count == 0, (
        f"UNKNOWN rows in {filename}: {unknown_count}. "
        "Gate requires 0 for golden files. Check hpe_rules.yaml."
    )


@pytest.mark.parametrize("filename", HP_FILES)
def test_unknown_threshold_hpe(filename):
    """Guardrail: UNKNOWN ≤ 5% for HPE files. If file missing at input_root/hpe/ → skip."""
    root = project_root()
    input_root = get_input_root()
    input_path = input_root / filename
    if not input_path.exists():
        pytest.skip(f"Input not found: {input_path} (set paths.input_root in config.local.yaml)")
    rules_path = root / "rules" / "hpe_rules.yaml"
    if not rules_path.exists():
        pytest.skip("rules/hpe_rules.yaml not found")

    config = load_config()
    normalized, results = run_pipeline_in_memory("hpe", input_path, rules_path, config)
    item_count = sum(1 for r in results if r.row_kind == RowKind.ITEM)
    unknown_count = sum(
        1 for r in results
        if r.row_kind == RowKind.ITEM and r.entity_type == EntityType.UNKNOWN
    )
    ratio = unknown_count / item_count if item_count > 0 else 0
    assert ratio <= 0.05, (
        f"Unknown ratio {ratio:.2%} ({unknown_count}/{item_count}) exceeds 5% threshold"
    )
