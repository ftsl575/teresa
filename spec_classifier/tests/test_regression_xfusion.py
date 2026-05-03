"""Regression tests for XFusion eDeal pipeline vs golden JSONL."""

import json
import pytest
from pathlib import Path

from conftest import project_root, get_input_root_xfusion
from tests.helpers import run_pipeline_in_memory, build_golden_rows
from src.core.classifier import classify_row, EntityType
from src.core.normalizer import RowKind
from src.rules.rules_engine import RuleSet
from src.vendors.xfusion.normalizer import XFusionNormalizedRow


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


@pytest.mark.parametrize("filename", [f"xf{i}.xlsx" for i in range(1, 11)])
def test_xfusion_regression(filename):
    root = project_root()
    input_root = get_input_root_xfusion()
    input_path = input_root / filename
    if not input_path.exists():
        pytest.skip(f"Input not found: {input_path}")
    rules_path = root / "rules" / "xfusion_rules.yaml"
    if not rules_path.exists():
        pytest.skip("rules/xfusion_rules.yaml not found")
    golden_path = root / "golden" / f"{Path(filename).stem}_expected.jsonl"
    if not golden_path.exists():
        pytest.skip(f"Golden not found: {golden_path}")

    normalized, results = run_pipeline_in_memory("xfusion", input_path, rules_path)
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


# ── Cycle 2 — PR-8 SuperCap bucket / PR-10 air_duct ───────────────────────────────


@pytest.fixture(scope="module")
def xfusion_rules_cycle2():
    return RuleSet.load(str(project_root() / "rules" / "xfusion_rules.yaml"))


def _xrow(option_name: str, option_id: str = "2120CHK") -> XFusionNormalizedRow:
    return XFusionNormalizedRow(
        source_row_index=1,
        row_kind=RowKind.ITEM,
        group_name=None,
        group_id=None,
        product_name=None,
        module_name="",
        option_name=option_name,
        option_id=option_id,
        skus=[option_id],
        qty=1,
        option_price=1.0,
    )


@pytest.mark.parametrize(
    "desc, rid, dt, hw",
    [
        ("Air duct(2U radiator)", "HW-XF-018-AIR-DUCT-ACCESSORY", "air_duct", "accessory"),
        ("Fan bracket", "HW-XF-018-AIR-DUCT-ACCESSORY", "accessory", "accessory"),
        ("35xx/39xx RAID Card SuperCap", "HW-XF-008-SUPERCAP", "battery", "accessory"),
    ],
)
def test_regression_cycle2_xfusion_air_duct_and_supercap(xfusion_rules_cycle2, desc, rid, dt, hw):
    res = classify_row(_xrow(desc), xfusion_rules_cycle2)
    assert res.entity_type == EntityType.HW
    assert res.matched_rule_id == rid
    assert res.device_type == dt
    assert res.hw_type == hw
