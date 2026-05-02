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


def test_xclarity_fod_with_cto_option_id_is_software(lenovo_ruleset):
    """Production case: 7S-prefix CTO option_id must fall through BASE→SOFTWARE via SW-L-001."""
    r = _row("XClarity Controller Platin-FOD", option_id="7S0XCTO5WW")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.SOFTWARE


def test_xclarity_prem_fod_with_cto_option_id_is_software(lenovo_ruleset):
    r = _row("XClarity Controller Prem-FOD", option_id="7S0XCTO8WW")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.SOFTWARE


def test_non_7s_cto_remains_base_server(lenovo_ruleset):
    """Negative-lookahead regression: non-7S CTO option_id still routes to BASE/server."""
    r = _row("ThinkSystem SR650 V3", option_id="7Y0XCTO1WW")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.BASE
    assert result.device_type == "server"


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
    ("ThinkSystem SR650 V3 MB", "motherboard"),
    ("Lenovo ThinkSystem Air Duct", "accessory"),
    ("ThinkSystem HBA 440-8i SAS/SATA PCIe Gen4 12Gb Internal Adapter", "hba"),
])
def test_device_type(lenovo_ruleset, option_name, expected_device_type):
    r = _row(option_name)
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW, f"Expected HW for '{option_name}', got {result.entity_type}"
    assert result.device_type == expected_device_type, f"For '{option_name}': expected {expected_device_type}, got {result.device_type}"


# ── Theme 1: Motherboard / System Board / MB → HW/motherboard/chassis ──────

@pytest.mark.parametrize("option_name", [
    "ThinkSystem SR680a V4 System Board",
    "ThinkSystem SR650 V3 MB",
    "ThinkSystem SR645 V3 MB W/IO,Turin,Oahu,1U",
    "ThinkSystem SR675 V3 System Board v2",
])
def test_motherboard_is_hw_motherboard_chassis(lenovo_ruleset, option_name):
    """System Board / MB / MB W/IO must classify to HW/motherboard/chassis (PR-4a Q1)."""
    r = _row(option_name)
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.device_type == "motherboard"
    assert result.hw_type == "chassis"


@pytest.mark.parametrize("option_name", [
    "8MB cache memory module",
    "100 MB/s throughput cable",
])
def test_mb_inside_word_is_not_motherboard(lenovo_ruleset, option_name):
    """Negative: 'MB' embedded in '8MB' or 'MB/s' must NOT classify as motherboard."""
    r = _row(option_name)
    result = classify_row(r, lenovo_ruleset)
    assert result.device_type != "motherboard"


# ── Theme 3: HDD Type Label / HDD Type Label1/2 → NOTE ───────────────────────

@pytest.mark.parametrize("option_name", [
    'ThinkSystem 2U MS 24x2.5" SATA/SAS HDD Type Label1',
    'ThinkSystem 2U MS 24x2.5" SATA/SAS HDD Type Label2',
    "HDD Type Label",
])
def test_hdd_type_label_is_note(lenovo_ruleset, option_name):
    """Digit-suffix and bare 'HDD Type Label' all route to NOTE (PR-4a regex fix)."""
    r = _row(option_name)
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.NOTE


def test_plain_hdd_remains_storage_drive(lenovo_ruleset):
    """Regression: plain HDD (no Label) still classifies as HW/storage_hdd/storage_drive."""
    r = _row('2.5" 1.2TB 10K SAS HDD')
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.device_type == "storage_hdd"
    assert result.hw_type == "storage_drive"


# ── PR-4b Theme 4: GPU Base → BASE/server ───────────────────────────────────

@pytest.mark.parametrize("option_id, option_name", [
    ("CBAD", "ThinkSystem SR680a V4 B300 GPU Base"),
    ("C9JN", "ThinkSystem SR680a V3 B200 GPU Base"),
    ("BR7G", "ThinkSystem SR675 V3 4DW PCIe GPU Base"),
])
def test_gpu_base_is_base_server(lenovo_ruleset, option_id, option_name):
    """GPU Base SKUs are GPU-chassis foundations, classified as BASE/server (PR-4b Theme 4, Q4)."""
    r = _row(option_name, option_id=option_id)
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.BASE
    assert result.device_type == "server"


def test_legit_gpu_board_remains_gpu(lenovo_ruleset):
    """Regression: legit GPU board (no 'Base' token) still classifies as HW/gpu/gpu."""
    r = _row("ThinkSystem NVIDIA HGX B200 180GB 1000W 8-GPU Board")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.device_type == "gpu"
    assert result.hw_type == "gpu"


# ── PR-4b Theme 5: BlueField DPU → HW/nic/network_adapter ───────────────────

@pytest.mark.parametrize("option_name", [
    "ThinkSystem NVIDIA BlueField-3 B3220 VPI QSFP112 2P 200G PCIe Gen5 x16 with Tin Plating Connector",
    "ThinkSystem BlueField-3 Power Cable",
])
def test_bluefield_is_hw_nic(lenovo_ruleset, option_name):
    """BlueField DPU + Power Cable both route to HW/nic/network_adapter (PR-4b Theme 5)."""
    r = _row(option_name)
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.device_type == "nic"
    assert result.hw_type == "network_adapter"


def test_legit_transceiver_remains_transceiver(lenovo_ruleset):
    """Regression: non-BlueField SFP28 transceiver still classifies as HW/transceiver/transceiver."""
    r = _row("ThinkSystem Finisar Dual Rate 10G/25G SR SFP28 Transceiver")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.device_type == "transceiver"
    assert result.hw_type == "transceiver"


# ── PR-4b Theme 6: Network Card / OSFP → HW/nic/network_adapter ─────────────

def test_osfp_network_card_8gpu_is_nic(lenovo_ruleset):
    """OSFP Network Card description containing '8-GPU complex' must classify as nic, not gpu."""
    r = _row("ThinkSystem SR680a V4 OSFP Network Card for 8-GPU complex")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.device_type == "nic"
    assert result.hw_type == "network_adapter"


def test_legit_8gpu_board_remains_gpu(lenovo_ruleset):
    """Regression: NVIDIA HGX 8-GPU Board (no 'Network Card') still routes to gpu."""
    r = _row("NVIDIA HGX B200 8-GPU Board")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.device_type == "gpu"


# ── PR-4b Theme 7: Fan Boards → HW/fan/fan ──────────────────────────────────

@pytest.mark.parametrize("option_name", [
    "ThinkSystem SR680a V4 GPU Fan Control Board",
    "ThinkSystem SR680a V4 CPU Fan Board for Air-cooled 8U Chassis",
    "ThinkSystem SR680a V3 for B200 Server Fan Control Board",
])
def test_fan_board_is_hw_fan(lenovo_ruleset, option_name):
    """GPU/CPU/Server Fan (Control) Board variants all route to HW/fan/fan (PR-4b Theme 7)."""
    r = _row(option_name)
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.device_type == "fan"
    assert result.hw_type == "fan"


def test_legit_fan_module_remains_fan(lenovo_ruleset):
    """Regression: 'Performance Fan Module' still routes to fan via HW-L-018 (not HW-L-043)."""
    r = _row("ThinkSystem 2U V3 Performance Fan Module")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.device_type == "fan"
    assert result.hw_type == "fan"


# ── PR-4b Theme 8: PCIe Bracket → HW/accessory/accessory ────────────────────

def test_pcie_bracket_qsfp_is_accessory(lenovo_ruleset):
    """Mellanox QSFP56 PCIe Bracket must route to accessory, not transceiver."""
    r = _row("Mellanox Low-Profile Dual-Port QSFP56 PCIe Bracket L1/SBB")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.device_type == "accessory"
    assert result.hw_type == "accessory"


def test_legit_sfp_transceiver_remains_transceiver_post_bracket(lenovo_ruleset):
    """Regression: bare SFP28 transceiver (no 'PCIe Bracket') still routes to transceiver."""
    r = _row("Lenovo 25Gb SFP28 Transceiver Module")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.device_type == "transceiver"
    assert result.hw_type == "transceiver"


# ── PR-4c Theme 9: Bezel "Blowing Rock" → HW/bezel/accessory ────────────────

def test_blowing_rock_bezel(lenovo_ruleset):
    """Lenovo codename 'Blowing Rock' = security bezel → HW/bezel/accessory (PR-4c Q5)."""
    r = _row("L1 Blowing Rock - Red", option_id="BYV7")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.device_type == "bezel"
    assert result.hw_type == "accessory"


# ── PR-4c Theme 10: UNKNOWN-3 SR680a V4 closures ───────────────────────────

def test_ocp_nic_interposer_is_nic(lenovo_ruleset):
    """OCP NIC Interposer Card → HW/nic/network_adapter (PR-4c Theme 10)."""
    r = _row("ThinkSystem SR680a V4 OCP NIC Interposer Card", option_id="CBA1")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.device_type == "nic"
    assert result.hw_type == "network_adapter"


def test_pcie_switch_board_is_accessory(lenovo_ruleset):
    """PCIe Switch Board → HW/accessory/accessory (PR-4c Theme 10)."""
    r = _row("ThinkSystem SR680a V4 PCIe Switch Board with two 144-lanes Switches", option_id="CB9Q")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.device_type == "accessory"
    assert result.hw_type == "accessory"


def test_flexible_printed_circuit_is_cable(lenovo_ruleset):
    """Flexible Printed Circuit (FPC) → HW/cable/cable (PR-4c Theme 10)."""
    r = _row("ThinkSystem SR680a V4 Flexible Printed Circuit", option_id="CB9S")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.device_type == "cable"
    assert result.hw_type == "cable"


# ── Edge cases ───────────────────────────────────────────────────────────────

def test_unknown_row(lenovo_ruleset):
    r = _row("Totally unmatched row text XYZ123")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.UNKNOWN
