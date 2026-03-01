"""Regression tests for HPE pipeline vs golden JSONL. XLSX from config paths.input_root/hpe/, not test_data."""

import json
import pytest
from pathlib import Path

from conftest import project_root, get_input_root, load_config
from tests.helpers import run_pipeline_in_memory, build_golden_rows

HP_FILES = ["hp1.xlsx", "hp2.xlsx", "hp3.xlsx", "hp4.xlsx", "hp5.xlsx", "hp6.xlsx", "hp7.xlsx", "hp8.xlsx"]


def _load_golden(golden_path: Path):
    rows = []
    with open(golden_path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def _compare_row(expected: dict, actual: dict) -> list:
    diffs = []
    for key in ("entity_type", "state", "matched_rule_id", "device_type", "hw_type", "skus"):
        exp, act = expected.get(key), actual.get(key)
        if exp != act:
            diffs.append(f"  {key}: expected {exp!r}, got {act!r}")
    return diffs


@pytest.mark.parametrize("filename", HP_FILES)
def test_regression_hpe(filename):
    """Run HPE pipeline; compare to golden. Input from config paths.input_root/hpe/, golden from golden/."""
    root = project_root()
    input_root = get_input_root()
    input_path = input_root / filename
    if not input_path.exists():
        pytest.skip(f"Input not found: {input_path} (set paths.input_root in config.local.yaml)")
    rules_path = root / "rules" / "hpe_rules.yaml"
    if not rules_path.exists():
        pytest.skip("rules/hpe_rules.yaml not found")
    golden_path = root / "golden" / f"{Path(filename).stem}_expected.jsonl"
    if not golden_path.exists():
        pytest.skip(f"Golden not found: {golden_path}")

    config = load_config()
    normalized, results = run_pipeline_in_memory("hpe", input_path, rules_path, config)
    current = build_golden_rows(normalized, results)
    expected_rows = _load_golden(golden_path)

    if len(current) != len(expected_rows):
        pytest.fail(f"Row count mismatch: expected {len(expected_rows)}, got {len(current)}")

    all_diffs = []
    for i, (exp, act) in enumerate(zip(expected_rows, current)):
        if exp.get("source_row_index") != act.get("source_row_index"):
            all_diffs.append(f"Row {i}: source_row_index mismatch")
        diffs = _compare_row(exp, act)
        if diffs:
            all_diffs.append(f"Row {i} (src={act.get('source_row_index')}):")
            all_diffs.extend(diffs)
    if all_diffs:
        pytest.fail("Regression diff:\n" + "\n".join(all_diffs))
