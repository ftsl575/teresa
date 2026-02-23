"""
Unknown threshold test: for each dl run pipeline, read run_summary.json,
assert unknown_count / item_rows_count <= 0.05. Skip if xlsx not found.
"""

import json
import pytest
from pathlib import Path

from src.core.parser import parse_excel
from src.core.normalizer import normalize_row
from src.rules.rules_engine import RuleSet
from src.core.classifier import classify_row
from src.diagnostics.run_manager import create_run_folder
from src.outputs.json_writer import (
    save_rows_raw,
    save_rows_normalized,
    save_classification,
    save_unknown_rows,
    save_header_rows,
)
from src.diagnostics.stats_collector import collect_stats, save_run_summary

from conftest import project_root

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

    output_base = root / "output"
    rows_raw = parse_excel(str(input_path))
    rows_normalized = [normalize_row(r) for r in rows_raw]
    ruleset = RuleSet.load(str(rules_path))
    classification_results = [classify_row(r, ruleset) for r in rows_normalized]

    run_folder = create_run_folder(str(output_base), input_path.name)
    save_rows_raw(rows_raw, run_folder)
    save_rows_normalized(rows_normalized, run_folder)
    save_classification(classification_results, run_folder)
    save_unknown_rows(rows_normalized, classification_results, run_folder)
    save_header_rows(rows_normalized, run_folder)
    stats = collect_stats(classification_results)
    save_run_summary(stats, run_folder)

    summary_path = run_folder / "run_summary.json"
    assert summary_path.exists(), f"run_summary.json not found at {summary_path}"
    with open(summary_path, encoding="utf-8") as f:
        summary = json.load(f)

    unknown_count = summary.get("unknown_count", 0)
    item_rows_count = summary.get("item_rows_count", 0)
    if item_rows_count == 0:
        pytest.skip(f"item_rows_count is 0 for {filename}")

    ratio = unknown_count / item_rows_count
    assert ratio <= UNKNOWN_RATIO_THRESHOLD, (
        f"unknown_count / item_rows_count = {unknown_count}/{item_rows_count} = {ratio:.4f} > {UNKNOWN_RATIO_THRESHOLD}"
    )
