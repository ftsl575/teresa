"""Unit tests for Lenovo classification rules (no external input files)."""

from pathlib import Path

import pytest

from src.core.classifier import classify_row, EntityType
from src.core.normalizer import RowKind
from src.rules.rules_engine import RuleSet
from src.vendors.lenovo.normalizer import LenovoNormalizedRow


@pytest.fixture
def lenovo_ruleset():
    rules_path = Path(__file__).resolve().parent.parent / "rules" / "lenovo_rules.yaml"
    return RuleSet.load(str(rules_path))


def _row(option_name: str, *, option_id: str = "TEST1", module_name: str = "") -> LenovoNormalizedRow:
    return LenovoNormalizedRow(
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


# ── BASE ─────────────────────────────────────────────────────────────────────

def test_cto_is_base(lenovo_ruleset):
    r = _row("Server : ThinkSystem SR630 V3-3yr Base Warranty", option_id="7D73CTO1WW")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.BASE


# ── SOFTWARE ─────────────────────────────────────────────────────────────────

def test_xclarity_fod_is_software(lenovo_ruleset):
    r = _row("XClarity Controller Platin-FOD", option_id="7S0X1234WW")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.SOFTWARE


def test_firmware_security_module_is_software(lenovo_ruleset):
    r = _row("ThinkSystem SR650 V3 Firmware and Root of Trust Security Module v2")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.SOFTWARE


# ── CONFIG ───────────────────────────────────────────────────────────────────

def test_config_instruction(lenovo_ruleset):
    r = _row("Configuration Instruction", option_id="5374CM1")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.CONFIG


def test_operating_mode_is_config(lenovo_ruleset):
    r = _row('Operating mode selection for: "Efficiency - Favoring Performance Mode"')
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.CONFIG


def test_nplus_n_redundancy_is_config(lenovo_ruleset):
    r = _row("N+N Redundancy With Over-Subscription")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.CONFIG


# ── NOTE ─────────────────────────────────────────────────────────────────────

def test_label_is_note(lenovo_ruleset):
    r = _row("XCC Label")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.NOTE


def test_package_is_note(lenovo_ruleset):
    r = _row("Package")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.NOTE


# ── HW + device_type parametrized ───────────────────────────────────────────

@pytest.mark.parametrize("option_name, expected_device_type", [
    ("Intel Xeon Silver 4510 12C 150W 2.4GHz Processor", "cpu"),
    ("ThinkSystem 64GB TruDDR5 5600MHz (2Rx4) RDIMM", "ram"),
    ("ThinkSystem NVIDIA HGX B200 180GB 1000W 8-GPU Board", "gpu"),
    ("ThinkSystem Memory Dummy", "blank_filler"),
    ("ThinkSystem 1x1 3.5\" HDD Filler", "blank_filler"),
    ("ThinkSystem RAID 940-16i 4GB Flash PCIe Gen4 12Gb Adapter", "raid_controller"),
    ("ThinkSystem M.2 with RAID Adapter", "raid_controller"),
    ("ThinkSystem Mellanox ConnectX-6 Lx 10/25GbE SFP28 2-port PCIe Ethernet Adapter", "nic"),
    ("ThinkSystem Finisar Dual Rate 10G/25G SR SFP28 Transceiver", "transceiver"),
    ("ThinkSystem 2.5\" U.2 VA 6.4TB Mixed Use NVMe PCIe 5.0 x4 HS SSD", "storage_ssd"),
    ("ThinkSystem 3.5\" 22TB 7.2K SAS 12Gb Hot Swap 512e HDD", "storage_hdd"),
    ("ThinkSystem 1800W 230V Platinum Hot-Swap Gen2 Power Supply v2", "psu"),
    ("2.8m, 13A/100-250V, C13 to C14 Jumper Cord", "power_cord"),
    ("ThinkSystem 2U V3 Performance Fan Module", "fan"),
    ("ThinkSystem SR650 V3 Performance Heatsink", "heatsink"),
    ("ThinkSystem SR650 V3 x16/x8/x8 PCIe Gen5 Riser1 or 2 v2", "riser"),
    ("ThinkSystem Toolless Slide Rail Kit v2 with 2U CMA", "rail"),
    ("ThinkSystem 2U 12x3.5\" SAS/SATA Backplane", "backplane"),
    ("ThinkSystem V3 2U 12x3.5\" Chassis", "chassis"),
    ("TPM 2.0", "tpm"),
    ("M.2 Cable", "cable"),
    ("ThinkSystem RAID 930/940 SuperCap", "battery"),
    ("ThinkSystem SR650 V3 MB", "accessory"),
    ("Lenovo ThinkSystem Air Duct", "accessory"),
    ("ThinkSystem HBA 440-8i SAS/SATA PCIe Gen4 12Gb Internal Adapter", "hba"),
])
def test_device_type(lenovo_ruleset, option_name, expected_device_type):
    r = _row(option_name)
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW, f"Expected HW for '{option_name}', got {result.entity_type}"
    assert result.device_type == expected_device_type, f"For '{option_name}': expected {expected_device_type}, got {result.device_type}"


# ── Edge cases ───────────────────────────────────────────────────────────────

def test_unknown_row(lenovo_ruleset):
    r = _row("Totally unmatched row text XYZ123")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.UNKNOWN
