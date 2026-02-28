"""
Regression tests: compare pipeline output to golden/*_expected.jsonl row-by-row.
"""

import json
import pytest
from pathlib import Path

from conftest import project_root
from tests.helpers import run_pipeline_in_memory, build_golden_rows


def _load_golden(golden_path: Path):
    """Load golden JSONL into list of dicts."""
    rows = []
    with open(golden_path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def _compare_row(expected: dict, actual: dict, row_label: str) -> list[str]:
    """Return list of diff messages for this row."""
    diffs = []
    for key in ("entity_type", "state", "matched_rule_id", "device_type", "hw_type", "skus"):
        exp = expected.get(key)
        act = actual.get(key)
        if exp != act:
            diffs.append(f"  {key}: expected {exp!r}, got {act!r}")
    return diffs


@pytest.mark.parametrize("filename", ["dl1.xlsx", "dl2.xlsx", "dl3.xlsx", "dl4.xlsx", "dl5.xlsx"])
def test_regression(filename):
    """Run pipeline for filename, load golden, compare row-by-row (entity_type, state, matched_rule_id, skus)."""
    root = project_root()
    input_path = root / "test_data" / filename
    if not input_path.exists():
        pytest.skip(f"test_data/{filename} not found")
    rules_path = root / "rules" / "dell_rules.yaml"
    golden_path = root / "golden" / f"{Path(filename).stem}_expected.jsonl"
    if not golden_path.exists():
        pytest.skip(f"Golden file not found: {golden_path}. Run: python main.py --input test_data/{filename} --save-golden")

    normalized, results = run_pipeline_in_memory("dell", input_path, rules_path)
    current = build_golden_rows(normalized, results)
    expected_rows = _load_golden(golden_path)

    if len(current) != len(expected_rows):
        pytest.fail(
            f"Row count mismatch: expected {len(expected_rows)}, got {len(current)}"
        )

    all_diffs = []
    for i, (exp, act) in enumerate(zip(expected_rows, current)):
        if exp.get("source_row_index") != act.get("source_row_index"):
            all_diffs.append(f"Row {i}: source_row_index mismatch (expected {exp.get('source_row_index')}, got {act.get('source_row_index')})")
        diffs = _compare_row(exp, act, f"Row {i}")
        if diffs:
            all_diffs.append(f"Row {i} (source_row_index={act.get('source_row_index')}):")
            all_diffs.extend(diffs)
    if all_diffs:
        pytest.fail("Regression diff:\n" + "\n".join(all_diffs))
