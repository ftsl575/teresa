"""Unit tests for Huawei classification rules (no external input files)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.classifier import classify_row, EntityType
from src.core.normalizer import RowKind
from src.rules.rules_engine import RuleSet
from src.vendors.huawei.normalizer import HuaweiNormalizedRow


@pytest.fixture
def huawei_ruleset():
    rules_path = Path(__file__).resolve().parent.parent / "rules" / "huawei_rules.yaml"
    return RuleSet.load(str(rules_path))


def _row(option_name: str, *, option_id: str = "HU000001",
         module_name: str = "") -> HuaweiNormalizedRow:
    return HuaweiNormalizedRow(
        source_row_index=1,
        row_kind=RowKind.ITEM,
        group_name=None,
        group_id=None,
        product_name=None,
        module_name=module_name,
        option_name=option_name,
        option_id=option_id,
        skus=[option_id],
        qty=1,
        option_price=100.0,
    )


# ── BASE ──────────────────────────────────────────────────────────────────

def test_BASE_HU_001_oceanstor_dual_ctrl_cache(huawei_ruleset):
    r = _row("OceanStor Dorado 5000 V6(2U,Dual Ctrl,NVMe,128GB Cache,16*GE)")
    result = classify_row(r, huawei_ruleset)
    assert result.entity_type == EntityType.BASE
    assert result.matched_rule_id == "BASE-HU-001-OCEANSTOR"


def test_BASE_HU_002_s_series_switch(huawei_ruleset):
    r = _row("S5735-S48P4XE-V2 (48*10/100/1000BASE-T ports, 4*10GE SFP+ ports)")
    result = classify_row(r, huawei_ruleset)
    assert result.entity_type == EntityType.BASE
    assert result.matched_rule_id == "BASE-HU-002-SWITCH"


def test_BASE_HU_003_airengine_wireless(huawei_ruleset):
    r = _row("AirEngine 9700-M1")
    result = classify_row(r, huawei_ruleset)
    assert result.entity_type == EntityType.BASE
    assert result.matched_rule_id == "BASE-HU-003-WIRELESS"


# ── SOFTWARE ──────────────────────────────────────────────────────────────

def test_SW_HU_001_software_bundle(huawei_ruleset):
    r = _row("Software Bundle for OceanStor")
    result = classify_row(r, huawei_ruleset)
    assert result.entity_type == EntityType.SOFTWARE
    assert result.matched_rule_id == "SW-HU-001-BUNDLE"


def test_SW_HU_002_sw_license(huawei_ruleset):
    # Must match SW-HU-002 before generic SW-HU-003
    r = _row("S5735 SW License Premium")
    result = classify_row(r, huawei_ruleset)
    assert result.entity_type == EntityType.SOFTWARE
    assert result.matched_rule_id == "SW-HU-002-SW-LICENSE"


def test_SW_HU_003_license_generic(huawei_ruleset):
    r = _row("License for Advanced Feature X")
    result = classify_row(r, huawei_ruleset)
    assert result.entity_type == EntityType.SOFTWARE
    assert result.matched_rule_id == "SW-HU-003-LICENSE-GENERIC"


# ── HW ────────────────────────────────────────────────────────────────────

def test_HW_HU_001_io_module(huawei_ruleset):
    r = _row("I/O module Smart NVMe SmartIO 4-port")
    result = classify_row(r, huawei_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.matched_rule_id == "HW-HU-001-IO-MODULE"


def test_HW_HU_002_nvme_disk_unit(huawei_ruleset):
    # Critical: NVMe matches BEFORE SSD/HDD
    r = _row("10x 7.68TB SSD NVMe Palm Disk Unit")
    result = classify_row(r, huawei_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.matched_rule_id == "HW-HU-002-NVME"


def test_HW_HU_003_ssd_sas_disk_unit(huawei_ruleset):
    r = _row("1.92TB SSD SAS Disk Unit")
    result = classify_row(r, huawei_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.matched_rule_id == "HW-HU-003-SSD-SAS"


def test_HW_HU_004_hdd_disk_unit(huawei_ruleset):
    r = _row("8TB NL-SAS Disk Unit")
    result = classify_row(r, huawei_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.matched_rule_id == "HW-HU-004-HDD"


def test_HW_HU_005_power_module(huawei_ruleset):
    r = _row("Power Module 800W AC")
    result = classify_row(r, huawei_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.matched_rule_id == "HW-HU-005-PSU"


def test_HW_HU_006_optical_transceiver(huawei_ruleset):
    r = _row("Optical Transceiver,eSFP,GE,1310nm,LC")
    result = classify_row(r, huawei_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.matched_rule_id == "HW-HU-006-TRANSCEIVER"


def test_HW_HU_007_patch_cord(huawei_ruleset):
    r = _row("Patch Cord,DLC/PC,Multi-mode,3m")
    result = classify_row(r, huawei_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.matched_rule_id == "HW-HU-007-CABLE"


def test_HW_HU_008_disk_enclosure(huawei_ruleset):
    # Matches only when no "Disk Unit" in the same string
    r = _row("SAS Disk Enclosure,4U,Without Disk Units")
    result = classify_row(r, huawei_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.matched_rule_id == "HW-HU-008-DISK-ENCLOSURE"


# ── device_type ───────────────────────────────────────────────────────────

def test_DT_HU_001_io_module_device_type(huawei_ruleset):
    r = _row("I/O module SmartIO 4-port")
    result = classify_row(r, huawei_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.device_type == "io_module"


def test_DT_HU_002_storage_nvme_device_type(huawei_ruleset):
    r = _row("10x 7.68TB SSD NVMe Palm Disk Unit")
    result = classify_row(r, huawei_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.device_type == "storage_nvme"


def test_BASE_HU_DT_001_storage_system_device_type(huawei_ruleset):
    r = _row("OceanStor Dorado 5000 V6(2U,Dual Ctrl,NVMe,128GB Cache,16*GE)")
    result = classify_row(r, huawei_ruleset)
    assert result.entity_type == EntityType.BASE
    assert result.device_type == "storage_system"


# ── NEGATIVE (cross-vendor) ───────────────────────────────────────────────

def test_lenovo_cto_does_not_match_huawei_base(huawei_ruleset):
    r = _row("ThinkSystem SR650 V3 - 2U Multi-socket Base", option_id="7DDQCTO1WW")
    result = classify_row(r, huawei_ruleset)
    # Lenovo CTO rows must NOT fall into any huawei BASE-HU-* or DT-HU-* rule
    assert not (result.matched_rule_id or "").startswith("BASE-HU-"), (
        f"Lenovo CTO matched Huawei BASE rule: {result.matched_rule_id}"
    )
    assert result.device_type is None, (
        f"Lenovo CTO got Huawei device_type: {result.device_type}"
    )


def test_dell_module_name_does_not_match_huawei(huawei_ruleset):
    r = _row("Dell PowerEdge R650xs Server")
    result = classify_row(r, huawei_ruleset)
    # Must not match ANY huawei rule
    rid = result.matched_rule_id or ""
    assert "-HU-" not in rid, f"Dell row matched Huawei rule: {rid}"
    assert result.entity_type == EntityType.UNKNOWN, (
        f"Expected UNKNOWN, got {result.entity_type}"
    )


# ── ORDER validation ──────────────────────────────────────────────────────

def test_first_match_wins_nvme_before_hdd(huawei_ruleset):
    """
    "SSD NVMe Disk Unit" must match NVMe rules (HW-HU-002, DT-HU-002)
    and NOT HDD rules (HW-HU-004, DT-HU-004).
    This validates first-match-wins ordering.
    """
    r = _row("10x 7.68TB SSD NVMe Palm Disk Unit")
    result = classify_row(r, huawei_ruleset)
    assert result.matched_rule_id == "HW-HU-002-NVME", (
        f"Expected HW-HU-002-NVME (NVMe rule should match first), "
        f"got {result.matched_rule_id}"
    )
    assert result.device_type == "storage_nvme", (
        f"Expected device_type=storage_nvme, got {result.device_type}"
    )
