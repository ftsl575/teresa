"""Regression tests for Lenovo pipeline vs golden JSONL."""

import json
import pytest
from pathlib import Path

from conftest import project_root, get_input_root_lenovo
from tests.helpers import run_pipeline_in_memory, build_golden_rows
from src.core.classifier import classify_row, EntityType
from src.core.normalizer import RowKind
from src.rules.rules_engine import RuleSet
from src.vendors.lenovo.normalizer import LenovoNormalizedRow


LENOVO_FILES = [f"L{i}.xlsx" for i in range(1, 12)]


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


@pytest.mark.parametrize("filename", LENOVO_FILES)
def test_regression_lenovo(filename):
    root = project_root()
    input_root = get_input_root_lenovo()
    input_path = input_root / filename
    if not input_path.exists():
        pytest.skip(f"Input not found: {input_path} (set paths.input_root in config.local.yaml)")
    rules_path = root / "rules" / "lenovo_rules.yaml"
    if not rules_path.exists():
        pytest.skip("rules/lenovo_rules.yaml not found")
    golden_path = root / "golden" / f"{Path(filename).stem}_expected.jsonl"
    if not golden_path.exists():
        pytest.skip(f"Golden not found: {golden_path}")

    normalized, results = run_pipeline_in_memory("lenovo", input_path, rules_path)
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


# ── Cycle 2 (PR-8–PR-10) signature SKUs — explicit lock beyond row-order golden ──
# Full thematic matrix (incl. negatives) remains in tests/test_lenovo_rules_unit.py.


@pytest.fixture(scope="module")
def lenovo_rules_for_cycle2():
    p = project_root() / "rules" / "lenovo_rules.yaml"
    return RuleSet.load(str(p))


def _lrow(name: str, oid: str = "REG2") -> LenovoNormalizedRow:
    return LenovoNormalizedRow(
        source_row_index=1,
        row_kind=RowKind.ITEM,
        group_name=None,
        group_id=None,
        product_name=None,
        module_name="",
        option_name=name,
        option_id=oid,
        skus=[oid],
        qty=1,
        option_price=1.0,
    )


@pytest.mark.parametrize(
    "oid, name, erule, edt, ehw",
    [
        ("BV2K", "ThinkSystem SR950 V3 2.5\" HD Cage", "HW-L-061-DRIVE-CAGE", "drive_cage", "backplane"),  # PR-9c
        ("BQ2M", "ThinkSystem 1U V3 10x2.5\" Media Bay without External Diagnostics Port", "HW-L-062-MEDIA-BAY", "media_bay", "chassis"),  # PR-9c
        ("CB9Q", "ThinkSystem SR680a V4 PCIe Switch Board with two 144-lanes Switches", "HW-L-049-INTERCONNECT-BOARD", "interconnect_board", "chassis"),  # PR-9b
        ("CB9J", "ThinkSystem 8GPU Server CFFV5 Power Interface Board", "HW-L-053-PDB", "power_distribution_board", "chassis"),  # PR-9b
        ("BV1V", "ThinkSystem SR950 V3 Front Operator Panel", "HW-L-046-FRONT-PANEL", "front_panel", "management"),  # PR-9a
        ("BV2H", "ThinkSystem SR950 V3 Root of Trust Module", "HW-L-047-ROT-MODULE", "tpm", "tpm"),  # PR-9a
        ("C3RP", "ThinkSystem 2U GPU air duct", "HW-L-064-AIR-DUCT", "air_duct", "accessory"),  # PR-10 Q10e
        ("C1YH", "ThinkSystem SR630 V4 x16/x16 PCIe Gen5 Cable Riser 1", "HW-L-063-CABLE-RISER", "riser", "riser"),  # PR-10 Q10d
        ("BM8X", "ThinkSystem M.2 SATA/x4 NVMe 2-Bay Adapter", "HW-L-037-M2-BAY-ADAPTER", "raid_controller", "storage_controller"),  # sanity PR-10b
        ("726537-OFF", "ThinkSystem PCIe Power Cable Kit", "HW-L-050-CABLE-THROUGH", "cable", "cable"),  # PR-10d negative cue
    ],
)
def test_regression_cycle2_lenovo_signature_skus(lenovo_rules_for_cycle2, oid, name, erule, edt, ehw):
    r = _lrow(name, oid)
    res = classify_row(r, lenovo_rules_for_cycle2)
    assert res.entity_type == EntityType.HW
    assert res.matched_rule_id == erule
    assert res.device_type == edt
    assert res.hw_type == ehw


def test_regression_cycle2_lenovo_fan_control_board_unchanged(lenovo_rules_for_cycle2):
    r = _lrow(
        "ThinkSystem SR680a V3 for B200 Server Fan Control Board",
        "C9JT",
    )
    res = classify_row(r, lenovo_rules_for_cycle2)
    assert res.matched_rule_id == "HW-L-043-FAN-BOARD"
    assert res.device_type == "fan"
    assert res.hw_type == "fan"
