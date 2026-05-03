"""Unit tests for HPE classification rules (no external input files)."""

from pathlib import Path

import pytest

from src.core.classifier import classify_row, EntityType
from src.core.normalizer import RowKind
from src.rules.rules_engine import RuleSet
from src.vendors.hpe.normalizer import HPENormalizedRow


@pytest.fixture
def hpe_ruleset():
    rules_path = Path(__file__).resolve().parent.parent / "rules" / "hpe_rules.yaml"
    return RuleSet.load(str(rules_path))


def _hpe_row(option_name: str, *, option_id: str = "SKU-1", module_name: str = "") -> HPENormalizedRow:
    return HPENormalizedRow(
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


def test_hpe_classify_hw_row(hpe_ruleset):
    row = _hpe_row("Intel Xeon Gold 5416S")
    result = classify_row(row, hpe_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.matched_rule_id == "HW-H-GLOBAL-002"


def test_hpe_classify_service_row(hpe_ruleset):
    row = _hpe_row("3Y ProCare warranty service")
    result = classify_row(row, hpe_ruleset)
    assert result.entity_type == EntityType.SERVICE
    assert result.matched_rule_id == "SERVICE-H-001"


def test_hpe_classify_logistic_row(hpe_ruleset):
    row = _hpe_row("Shipping and delivery service")
    result = classify_row(row, hpe_ruleset)
    assert result.entity_type == EntityType.LOGISTIC
    assert result.matched_rule_id == "LOGISTIC-H-001"


def test_hpe_classify_unknown_row(hpe_ruleset):
    row = _hpe_row("Totally unmatched row text")
    result = classify_row(row, hpe_ruleset)
    assert result.entity_type == EntityType.UNKNOWN
    assert result.matched_rule_id == "UNKNOWN-000"
    assert "No matching rule found" in result.warnings


def test_hpe_factory_integrated_matches_config_rule(hpe_ruleset):
    row = _hpe_row("Factory Integrated")
    result = classify_row(row, hpe_ruleset)
    assert result.entity_type == EntityType.CONFIG
    assert result.matched_rule_id == "CONFIG-H-001"


# ---------------------------------------------------------------------------
# device_type / hw_type coverage — all 25 unique HPE device_types
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("option_name, exp_device_type, exp_hw_type", [
    # 1  server  (BASE entity → hw_type not applied)
    ("HPE ProLiant DL380 Gen11 Configure-to-order Server", "server", None),
    # 2  cpu
    ("Intel Xeon Gold 5416S", "cpu", "cpu"),
    # 3  ram
    ("HPE 64GB DDR5-5600 Registered Smart Memory Kit", "ram", "memory"),
    # 4  blank_filler
    ("HPE DDR5 DIMM Blank Kit", "blank_filler", "blank_filler"),
    # 5  storage_nvme
    ("HPE 1.6TB NVMe SSD", "storage_nvme", "storage_drive"),
    # 6  storage_ssd
    ("HPE 480GB SATA 6G Read Intensive SFF SSD", "storage_ssd", "storage_drive"),
    # 7  storage_hdd
    ("HPE 2.4TB SAS 12G Mission Critical HDD", "storage_hdd", "storage_drive"),
    # 8  psu
    ("HPE 800W Flex Slot Platinum Power Supply", "psu", "psu"),
    # 9  power_cord (hw_type=None per taxonomy — power_cord is device_type only)
    ("Power Cord C13 to C14 2.5m", "power_cord", None),
    # 10 raid_controller
    ("HPE MR416i-p Gen11 Storage Controller", "raid_controller", "storage_controller"),
    # 11 hba
    ("HPE SN1610Q 32Gb Fibre Channel Host Bus Adapter", "hba", "hba"),
    # 12 nic
    ("HPE Ethernet 10Gb 2-port 562SFP+ Adapter", "nic", "network_adapter"),
    # 13 transceiver
    ("HPE 25GbE SFP28 Transceiver", "transceiver", "transceiver"),
    # 14 gpu
    ("NVIDIA A100 PCIe Accelerator for HPE", "gpu", "gpu"),
    # 15 fiber_cable
    ("HPE Premier Flex LC/LC OM4 2m Cable", "fiber_cable", "cable"),
    # 16 cable
    ("HPE GPU Power Cable Kit", "cable", "cable"),
    # 17 fan
    ("HPE Standard Fan Kit", "fan", "fan"),
    # 18 heatsink
    ("HPE Standard Heat Sink Kit", "heatsink", "heatsink"),
    # 19 riser
    ("HPE DL380 Gen11 Primary Riser Kit", "riser", "riser"),
    # 20 rail
    ("HPE Easy Install Rail Kit", "rail", "rail"),
    # 21 drive_cage
    ("HPE DL380 8SFF Drive Cage Kit", "drive_cage", "backplane"),
    # 22 backplane
    ("HPE 8SFF U.3 Backplane Kit", "backplane", "backplane"),
    # 23 bezel
    ("HPE DL380 Gen11 Bezel Kit", "bezel", "chassis"),
    # 24 battery
    ("HPE Smart Storage Lithium-ion Battery", "battery", "accessory"),
    # 25 accessory (generic — Optical Drive moved to optical_drive in PR-10 Q10f)
    ("HPE 9.5mm SATA DVD-RW Optical Drive", "optical_drive", "storage_drive"),
])
def test_hpe_device_type_and_hw_type(hpe_ruleset, option_name, exp_device_type, exp_hw_type):
    row = _hpe_row(option_name)
    result = classify_row(row, hpe_ruleset)
    assert result.device_type == exp_device_type
    assert result.hw_type == exp_hw_type


def test_drive_cage_p75741_b21_fires_as_backplane(hpe_ruleset):
    """PR-3: real P75741-B21 drive cage SKU — after drive_cage→backplane map flip,
    device_type stays drive_cage, but hw_type is now backplane (was chassis)."""
    row = _hpe_row(
        "HPE ProLiant Compute DL3XX Gen12 8SFF x4 U.3 Tri-Mode Drive Cage Kit"
    )
    result = classify_row(row, hpe_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.device_type == "drive_cage"
    assert result.hw_type == "backplane"
    assert result.matched_rule_id == "HW-H-GLOBAL-028"


# ── PR-9b Q8: HPE Power Distribution Board → HW/power_distribution_board/chassis ─

def test_hpe_pdb_p57888_b21_is_power_distribution_board(hpe_ruleset):
    """PR-9b Q8: real P57888-B21 'HPE ProLiant DL385 Gen11 Power Distribution
    Board Kit' must promote from accessory/accessory to power_distribution_board
    /chassis. Entity rule HW-H-GLOBAL-034 unchanged; device-type rule
    HW-H-080-PDB now outputs power_distribution_board, mapped to chassis via
    device_type_map (PR-9b)."""
    row = _hpe_row(
        "HPE ProLiant DL385 Gen11 Power Distribution Board Kit",
        option_id="P57888-B21",
    )
    result = classify_row(row, hpe_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.matched_rule_id == "HW-H-GLOBAL-034"
    assert result.device_type == "power_distribution_board"
    assert result.hw_type == "chassis"


def test_hpe_power_cord_does_not_match_pdb(hpe_ruleset):
    """NEGATIVE PR-9b Q8 guard: HPE 'Power Cord' must NOT pick up power_distribution_board.
    HW-H-GLOBAL-034 / HW-H-080-PDB regex requires 'power distribution board' literal."""
    row = _hpe_row("HPE Power Cord C13 to C14 2.5m AC Jumper")
    result = classify_row(row, hpe_ruleset)
    assert result.matched_rule_id != "HW-H-GLOBAL-034"
    assert result.device_type != "power_distribution_board"
    assert result.device_type == "power_cord"


# ── PR-10 Q10f: HPE Optical Drive → HW/optical_drive/storage_drive ───────────

def test_pr10_hpe_dvd_rw_726537_b21_is_optical_drive(hpe_ruleset):
    """PR-10 Q10f: real 726537-B21 'HPE 9.5mm SATA DVD-RW Optical Drive'
    promotes from accessory/accessory to optical_drive/storage_drive. Entity
    rule HW-H-GLOBAL-038 unchanged; device-type rules HW-H-081-OPTICAL-DRIVE
    and HW-H-082-DVD now output optical_drive, mapped to storage_drive via
    device_type_map (PR-10)."""
    row = _hpe_row(
        "HPE 9.5mm SATA DVD-RW Optical Drive",
        option_id="726537-B21",
    )
    result = classify_row(row, hpe_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.matched_rule_id == "HW-H-GLOBAL-038"
    assert result.device_type == "optical_drive"
    assert result.hw_type == "storage_drive"


def test_pr10_hpe_drive_cage_is_not_optical_drive(hpe_ruleset):
    """NEGATIVE PR-10 Q10f guard: HPE 'Drive Cage' must NOT match
    HW-H-GLOBAL-038 (optical drive entity rule); it stays drive_cage/backplane
    via HW-H-GLOBAL-028. The optical-drive regex requires 'dvd|optical drive|
    cd-rom|blu-ray', none of which appear in 'Drive Cage Kit'."""
    row = _hpe_row(
        "HPE ProLiant Compute DL3XX Gen12 8SFF x4 U.3 Tri-Mode Drive Cage Kit",
        option_id="P75741-B21",
    )
    result = classify_row(row, hpe_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.matched_rule_id != "HW-H-GLOBAL-038"
    assert result.device_type == "drive_cage"
    assert result.hw_type == "backplane"


def test_pr10_hpe_generic_storage_drive_is_not_optical(hpe_ruleset):
    """NEGATIVE PR-10 Q10f guard: a generic SAS/SATA HDD must keep its
    storage_hdd device_type — must NOT be misrouted to optical_drive."""
    row = _hpe_row("HPE 2.4TB SAS 12G Mission Critical HDD")
    result = classify_row(row, hpe_ruleset)
    assert result.matched_rule_id != "HW-H-GLOBAL-038"
    assert result.device_type == "storage_hdd"
    assert result.hw_type == "storage_drive"
