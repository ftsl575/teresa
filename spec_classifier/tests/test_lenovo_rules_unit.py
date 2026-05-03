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
    ("Lenovo ThinkSystem Air Duct", "air_duct"),  # PR-10 Q10e: new device_type
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


def test_pcie_switch_board_is_interconnect_board(lenovo_ruleset):
    """PCIe Switch Board → HW/interconnect_board/chassis (PR-9b Q8).
    Was HW/accessory/accessory in PR-4c (rule HW-L-047-PCIE-SWITCH-BOARD);
    promoted to its own taxonomy bucket in PR-9b under HW-L-049-INTERCONNECT-BOARD."""
    r = _row("ThinkSystem SR680a V4 PCIe Switch Board with two 144-lanes Switches", option_id="CB9Q")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.matched_rule_id == "HW-L-049-INTERCONNECT-BOARD"
    assert result.device_type == "interconnect_board"
    assert result.hw_type == "chassis"


def test_flexible_printed_circuit_is_cable(lenovo_ruleset):
    """Flexible Printed Circuit (FPC) → HW/cable/cable (PR-4c Theme 10)."""
    r = _row("ThinkSystem SR680a V4 Flexible Printed Circuit", option_id="CB9S")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.device_type == "cable"
    assert result.hw_type == "cable"


# ── PR-9a Q7a: Front Operator Panel → HW/front_panel/management ────────────

@pytest.mark.parametrize("option_id, option_name", [
    ("BAVU", "Front Operator Panel with Quad Line LCD Display"),
    ("BFTH", "ThinkSystem SR670 V2/ SR675 V3 Front Operator Panel ASM"),
    ("BV1V", "ThinkSystem SR950 V3 Front Operator Panel"),
])
def test_front_operator_panel_is_hw_front_panel_management(lenovo_ruleset, option_id, option_name):
    """PR-9a Q7a: Lenovo Front Operator Panel SKUs route to HW/front_panel/management.
    Lenovo Docs document Front Operator Panel as server controls/LEDs/status display."""
    r = _row(option_name, option_id=option_id)
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.matched_rule_id == "HW-L-046-FRONT-PANEL"
    assert result.device_type == "front_panel"
    assert result.hw_type == "management"


def test_external_operator_panel_port_remains_accessory(lenovo_ruleset):
    """NEGATIVE PR-9a Q7a: BV2C 'Serial Port and Port for External Operator Panel'
    is a rear-panel I/O accessory (port FOR an external panel), NOT a front operator
    panel itself. Must remain HW/accessory/accessory via HW-L-027-ACCESSORY."""
    r = _row("ThinkSystem SR950 V3 Serial Port and Port for External Operator Panel",
             option_id="BV2C")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.matched_rule_id == "HW-L-027-ACCESSORY"
    assert result.device_type == "accessory"
    assert result.hw_type == "accessory"


def test_bare_lcd_display_does_not_match_front_panel(lenovo_ruleset):
    """NEGATIVE PR-9a Q7a guard: bare 'LCD Display' (no Front Operator Panel context)
    must NOT match HW-L-046-FRONT-PANEL — regex is anchored on
    'Front Operator Panel' or 'LCD system information display'."""
    r = _row("Generic 19-inch LCD Display Monitor")
    result = classify_row(r, lenovo_ruleset)
    assert result.matched_rule_id != "HW-L-046-FRONT-PANEL"
    assert result.device_type != "front_panel"


# ── PR-9a Q7b: Root of Trust Module → HW/tpm/tpm ────────────────────────────

@pytest.mark.parametrize("option_id, option_name", [
    ("BR7U", "ThinkSystem SR675 V3 Root of Trust Module"),
    ("BV2H", "ThinkSystem SR950 V3 Root of Trust Module"),
    ("C257", "ThinkSystem SR6445 V3/SR665 V3 Absolut-RoW RoT Module for Turin MLK"),
    ("BTTS", "ThinkSystem SR850 V3 Root of Trust Module"),
])
def test_rot_module_is_hw_tpm(lenovo_ruleset, option_id, option_name):
    """PR-9a Q7b: Lenovo RoT Module SKUs route to HW/tpm/tpm. Lenovo documents
    RoT as 'Firmware and Root of Trust/TPM 2.0 Security Module' — same security
    bucket as TPM."""
    r = _row(option_name, option_id=option_id)
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.matched_rule_id == "HW-L-047-ROT-MODULE"
    assert result.device_type == "tpm"
    assert result.hw_type == "tpm"


def test_tpm_2_remains_tpm_via_existing_rule(lenovo_ruleset):
    """NEGATIVE PR-9a Q7b guard: bare 'TPM 2.0' must keep firing via the existing
    HW-L-024-TPM rule (NOT via the new RoT rule) — regex separation preserved."""
    r = _row("TPM 2.0 v3 Module")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.matched_rule_id == "HW-L-024-TPM"
    assert result.device_type == "tpm"
    assert result.hw_type == "tpm"


def test_random_module_does_not_match_rot(lenovo_ruleset):
    """NEGATIVE PR-9a Q7b guard: a random 'Module' description must NOT match
    HW-L-047-ROT-MODULE — regex requires 'Root of Trust' / 'RoT' / 'Firmware
    and Root of Trust' phrase."""
    r = _row("ThinkSystem SR650 V3 Memory Module")
    result = classify_row(r, lenovo_ruleset)
    assert result.matched_rule_id != "HW-L-047-ROT-MODULE"
    assert result.device_type != "tpm"


def test_firmware_rot_security_module_remains_software(lenovo_ruleset):
    """REGRESSION PR-9a Q7b: 'Firmware and Root of Trust Security Module' must
    still route to SOFTWARE via SW-L-010 (SOFTWARE rules fire BEFORE HW rules
    in the classifier pipeline). BYQL/BM8S unaffected by the new HW-L-047 rule."""
    r = _row("ThinkSystem SR650 V3 Firmware and Root of Trust Security Module v2",
             option_id="BYQL")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.SOFTWARE
    assert result.matched_rule_id == "SW-L-010"


def test_enablement_kit_remains_accessory_after_rot_extraction(lenovo_ruleset):
    """REGRESSION PR-9a Q7b + PR-9b Q8: HW-L-034 still catches bare 'Retimer' /
    'Enablement Kit' (RoT moved out in PR-9a; PCIe *Retimer Card* moved to
    HW-L-049-INTERCONNECT-BOARD in PR-9b). 'Enablement Kit' has no Card/Board
    suffix so it falls through to HW-L-034 → accessory."""
    r = _row("ThinkSystem 4U PCIe Gen5 Enablement Kit")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.matched_rule_id == "HW-L-034"
    assert result.device_type == "accessory"
    assert result.hw_type == "accessory"


# ── PR-9b Q8: Power Distribution Board → HW/power_distribution_board/chassis ──

@pytest.mark.parametrize("option_id, option_name", [
    ("CB9J", "ThinkSystem 8GPU Server CFFV5 Power Interface Board"),
    ("CBWP", "ThinkSystem 8GPU Server CFFV5 Power Interface Board"),
    ("CBA4", "ThinkSystem SR680a V4 P12V PSU Power Distribution Board"),
    ("C9N7", "ThinkSystem 8GPU Server Power Distribution Board 3"),
    ("BV23", "ThinkSystem SR950 V3 Power Interconnect Board"),
])
def test_pdb_is_hw_power_distribution_board_chassis(lenovo_ruleset, option_id, option_name):
    """PR-9b Q8: Lenovo internal PDB / Power Interface / Power Interconnect Board
    SKUs route to HW/power_distribution_board/chassis. Distinct from PSU (which
    converts AC→DC) and from power_cord."""
    r = _row(option_name, option_id=option_id)
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.matched_rule_id == "HW-L-053-PDB"
    assert result.device_type == "power_distribution_board"
    assert result.hw_type == "chassis"


# ── PR-9b Q8: Interconnect Board → HW/interconnect_board/chassis ──────────────

@pytest.mark.parametrize("option_id, option_name", [
    ("BV26", "ThinkSystem SR950 V3 I/O Board"),
    ("CBA3", "ThinkSystem SR680a V4 PCIe Retimer Card"),
    ("CB9Q", "ThinkSystem SR680a V4 PCIe Switch Board with two 144-lanes Switches"),
])
def test_interconnect_board_is_hw_interconnect_board_chassis(lenovo_ruleset, option_id, option_name):
    """PR-9b Q8: Lenovo internal interconnect board (PCIe Switch Board / PCIe
    Retimer Card / I/O Board) routes to HW/interconnect_board/chassis. Distinct
    from motherboard (Q1 main system board) and from external io_module
    (Huawei storage pluggable)."""
    r = _row(option_name, option_id=option_id)
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.matched_rule_id == "HW-L-049-INTERCONNECT-BOARD"
    assert result.device_type == "interconnect_board"
    assert result.hw_type == "chassis"


# ── PR-9b Q8 negative guards ──────────────────────────────────────────────────

def test_power_cord_does_not_match_pdb(lenovo_ruleset):
    """NEGATIVE PR-9b Q8 guard: 'Power Cord' must NOT match HW-L-053-PDB —
    the PDB regex requires a literal 'Board' suffix. Power cords route to
    HW-L-017-POWERCORD → power_cord."""
    r = _row("ThinkSystem 2.8m, 10A/100-250V, C13 to C14 Jumper Power Cord")
    result = classify_row(r, lenovo_ruleset)
    assert result.matched_rule_id != "HW-L-053-PDB"
    assert result.device_type != "power_distribution_board"
    assert result.matched_rule_id == "HW-L-017-POWERCORD"
    assert result.device_type == "power_cord"


def test_power_supply_does_not_match_pdb(lenovo_ruleset):
    """NEGATIVE PR-9b Q8 guard: 'Power Supply' must NOT match HW-L-053-PDB —
    PSU is AC→DC conversion, distinct from internal PDB. Routes to HW-L-016-PSU."""
    r = _row("ThinkSystem 1100W Titanium Power Supply v2")
    result = classify_row(r, lenovo_ruleset)
    assert result.matched_rule_id != "HW-L-053-PDB"
    assert result.device_type != "power_distribution_board"
    assert result.matched_rule_id == "HW-L-016-PSU"
    assert result.device_type == "psu"


def test_motherboard_remains_motherboard_not_interconnect_board(lenovo_ruleset):
    """REGRESSION PR-9b Q8: BLL0 'ThinkSystem SR650 V3 MB' (Q1 motherboard)
    must keep routing to HW-L-040-MOTHERBOARD → motherboard/chassis. The new
    INTERCONNECT-BOARD rule must NOT swallow the main system board."""
    r = _row("ThinkSystem SR650 V3 MB", option_id="BLL0")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.matched_rule_id == "HW-L-040-MOTHERBOARD"
    assert result.device_type == "motherboard"
    assert result.hw_type == "chassis"


def test_external_io_adapter_does_not_match_interconnect_board(lenovo_ruleset):
    """NEGATIVE PR-9b Q8 guard: 'OCP I/O Adapter' (no Board/Card suffix) must
    NOT match HW-L-049-INTERCONNECT-BOARD. The interconnect regex requires the
    literal 'Board' or 'Card' suffix, so generic I/O adapters fall through."""
    r = _row("Generic OCP I/O Adapter v3")
    result = classify_row(r, lenovo_ruleset)
    assert result.matched_rule_id != "HW-L-049-INTERCONNECT-BOARD"
    assert result.device_type != "interconnect_board"


def test_huawei_io_module_unaffected_by_lenovo_interconnect_rule():
    """REGRESSION PR-9b Q8: Lenovo INTERCONNECT-BOARD rule applies only to
    Lenovo files. Huawei 'I/O module' (HW-HU-001) must keep routing to
    HW/io_module — verify by classifying the Huawei row against the Huawei
    ruleset directly."""
    from src.vendors.huawei.normalizer import HuaweiNormalizedRow
    rules_path = Path(__file__).resolve().parent.parent / "rules" / "huawei_rules.yaml"
    huawei_ruleset = RuleSet.load(str(rules_path))
    row = HuaweiNormalizedRow(
        source_row_index=1,
        row_kind=RowKind.ITEM,
        group_name=None,
        group_id=None,
        product_name=None,
        module_name="",
        option_name="OceanStor I/O module Smart NVMe SmartIO 4-port",
        option_id="HU-IO-1",
        skus=["HU-IO-1"],
        qty=1,
        option_price=100.0,
    )
    result = classify_row(row, huawei_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.matched_rule_id == "HW-HU-001-IO-MODULE"
    assert result.device_type == "io_module"


# ── PR-9c Q9: HDD Cage → HW/drive_cage/backplane ──────────────────────────────

@pytest.mark.parametrize("option_id, option_name", [
    ("B97T", "ThinkSystem 2U MidBay 4X3.5\" HDD Cage"),
    ("BWKY", "ThinkSystem Rear 4x2.5\" NVMe HDD Cage"),
    ("BV2K", "ThinkSystem SR950 V3 2.5\" HD Cage"),
])
def test_hdd_cage_is_hw_drive_cage_backplane(lenovo_ruleset, option_id, option_name):
    """PR-9c Q9: Lenovo HDD/HD/NVMe Cage SKUs route to HW/drive_cage/backplane,
    matching HPE drive_cage semantics established in PR-3 (drive_cage→backplane).
    Was HW/chassis/chassis under HW-L-023-CHASSIS catch-all."""
    r = _row(option_name, option_id=option_id)
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.matched_rule_id == "HW-L-061-DRIVE-CAGE"
    assert result.device_type == "drive_cage"
    assert result.hw_type == "backplane"


# ── PR-9c Q9: Media Bay → HW/media_bay/chassis ────────────────────────────────

@pytest.mark.parametrize("option_id, option_name", [
    ("BQ2M", "ThinkSystem 1U V3 10x2.5\" Media Bay without External Diagnostics Port"),
    ("C1YP", "ThinkSystem 1U V4 Standard Media Bay"),
])
def test_media_bay_is_hw_media_bay_chassis(lenovo_ruleset, option_id, option_name):
    """PR-9c Q9: Lenovo Media Bay SKUs route to HW/media_bay/chassis. New
    device_type — Media Bay is a removable physical bay that may host front
    I/O panel, optical drive, or front-mounted devices; not always drive cage,
    so hw_type stays chassis (not backplane)."""
    r = _row(option_name, option_id=option_id)
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.matched_rule_id == "HW-L-062-MEDIA-BAY"
    assert result.device_type == "media_bay"
    assert result.hw_type == "chassis"


# ── PR-9c Q9 negative guards ──────────────────────────────────────────────────

def test_generic_chassis_remains_chassis(lenovo_ruleset):
    """REGRESSION PR-9c Q9: bare 'Chassis' SKU must keep routing to
    HW-L-023-CHASSIS → chassis/chassis. The catch-all was trimmed to
    (Chassis|Bezel) only — drive_cage and media_bay extracted into their own
    rules — but generic chassis SKUs are unaffected."""
    r = _row("ThinkSystem SR650 V3 2U Chassis Assembly")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.matched_rule_id == "HW-L-023-CHASSIS"
    assert result.device_type == "chassis"
    assert result.hw_type == "chassis"


def test_storage_media_does_not_match_media_bay(lenovo_ruleset):
    """NEGATIVE PR-9c Q9 guard: 'Storage media' (no 'Bay' suffix) must NOT
    match HW-L-062-MEDIA-BAY. The regex requires literal 'Media Bay' as
    contiguous tokens."""
    r = _row("ThinkSystem Storage media handling utility")
    result = classify_row(r, lenovo_ruleset)
    assert result.matched_rule_id != "HW-L-062-MEDIA-BAY"
    assert result.device_type != "media_bay"


def test_hdd_filler_does_not_match_drive_cage(lenovo_ruleset):
    """NEGATIVE PR-9c Q9 guard: 'HDD Filler' must NOT match HW-L-061-DRIVE-CAGE.
    The regex requires literal 'Cage' suffix; HDD/SSD fillers route to
    blank_filler via DT-L-005-BLANK."""
    r = _row("ThinkSystem 2.5\" HDD Filler 8-pack")
    result = classify_row(r, lenovo_ruleset)
    assert result.matched_rule_id != "HW-L-061-DRIVE-CAGE"
    assert result.device_type != "drive_cage"


def test_hpe_drive_cage_unaffected_by_lenovo_pr9c():
    """REGRESSION PR-9c Q9: HPE drive_cage (P75741-B21 etc., PR-3) must keep
    routing to HW/drive_cage/backplane via HPE rules. Verify by classifying
    the HPE row against the HPE ruleset directly."""
    from src.vendors.hpe.normalizer import HPENormalizedRow
    rules_path = Path(__file__).resolve().parent.parent / "rules" / "hpe_rules.yaml"
    hpe_ruleset = RuleSet.load(str(rules_path))
    row = HPENormalizedRow(
        source_row_index=1,
        row_kind=RowKind.ITEM,
        group_name=None,
        group_id=None,
        product_name=None,
        module_name="",
        option_name="HPE ProLiant Compute DL3XX Gen12 8SFF x4 U.3 Tri-Mode Drive Cage Kit",
        option_id="P75741-B21",
        skus=["P75741-B21"],
        qty=1,
        option_price=100.0,
    )
    result = classify_row(row, hpe_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.device_type == "drive_cage"
    assert result.hw_type == "backplane"


# ── PR-10 Q10b: M.2 Bay Adapter sanity (no change — already raid_controller) ─

def test_pr10_bm8x_m2_bay_adapter_remains_raid_controller(lenovo_ruleset):
    """PR-10 Q10b sanity: BM8X 'ThinkSystem M.2 SATA/x4 NVMe 2-Bay Adapter' was
    already routed via HW-L-037-M2-BAY-ADAPTER → raid_controller/storage_controller
    in PR-7. PR-10 confirms no change. Test guards against accidental regression
    from neighbouring rule edits (Cable Riser / Air Duct insertion above)."""
    r = _row("ThinkSystem M.2 SATA/x4 NVMe 2-Bay Adapter", option_id="BM8X")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.matched_rule_id == "HW-L-037-M2-BAY-ADAPTER"
    assert result.device_type == "raid_controller"
    assert result.hw_type == "storage_controller"


def test_pr10_m2_tray_remains_accessory(lenovo_ruleset):
    """NEGATIVE PR-10 Q10b guard: 'M.2 Tray' must NOT match HW-L-037-M2-BAY-ADAPTER.
    HW-L-036-M2-ACCESSORY catches Tray/Interposer/Cage and routes to accessory."""
    r = _row("ThinkSystem M.2 Tray Kit")
    result = classify_row(r, lenovo_ruleset)
    assert result.matched_rule_id != "HW-L-037-M2-BAY-ADAPTER"
    assert result.device_type != "raid_controller"


# ── PR-10 Q10c: RAID Enablement Kit sanity (no change — already raid_controller)

def test_pr10_bt7p_raid_enablement_remains_raid_controller(lenovo_ruleset):
    """PR-10 Q10c sanity: BT7P 'ThinkSystem Raid 540-8i for M.2/7MM NVMe boot
    Enablement' was already routed via HW-L-008-RAID → raid_controller/
    storage_controller. Test guards against accidental regression."""
    r = _row("ThinkSystem Raid 540-8i for M.2/7MM NVMe boot Enablement", option_id="BT7P")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.matched_rule_id == "HW-L-008-RAID"
    assert result.device_type == "raid_controller"
    assert result.hw_type == "storage_controller"


# ── PR-10 Q10d: Cable Riser → HW/riser/riser ──────────────────────────────────

@pytest.mark.parametrize("option_id, option_name", [
    ("C1YH", "ThinkSystem SR630 V4 x16/x16 PCIe Gen5 Cable Riser 1"),
    ("C1YHX", "ThinkSystem SR650 V4 PCIe Gen5 Cable Riser 2"),
])
def test_pr10_cable_riser_is_riser(lenovo_ruleset, option_id, option_name):
    """PR-10 Q10d: 'Cable Riser' SKUs route to HW/riser/riser via the new
    HW-L-063-CABLE-RISER rule. Was cable/cable under HW-L-050-CABLE-THROUGH —
    the literal 'Cable' token was hijacking these. New rule fires BEFORE
    cable-through to give precedence to the riser semantics."""
    r = _row(option_name, option_id=option_id)
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.matched_rule_id == "HW-L-063-CABLE-RISER"
    assert result.device_type == "riser"
    assert result.hw_type == "riser"


def test_pr10_pcie_power_cable_remains_cable(lenovo_ruleset):
    """NEGATIVE PR-10 Q10d guard: 'PCIe Power Cable' / 'GPU Power Cable' must
    NOT match HW-L-063-CABLE-RISER. The regex requires the literal 'Cable Riser'
    bigram (no Riser keyword in plain power cables)."""
    r = _row("ThinkSystem PCIe Power Cable Kit")
    result = classify_row(r, lenovo_ruleset)
    assert result.matched_rule_id != "HW-L-063-CABLE-RISER"
    assert result.device_type != "riser"
    assert result.device_type == "cable"


def test_pr10_plain_riser_remains_riser_via_riser_rule(lenovo_ruleset):
    """REGRESSION PR-10 Q10d: a plain Riser SKU (no 'Cable' prefix) still
    routes via HW-L-020-RISER (existing rule). Guards against the new
    HW-L-063-CABLE-RISER stealing legit risers."""
    r = _row("ThinkSystem SR650 V3 x16/x8/x8 PCIe Gen5 Riser1 or 2 v2")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.matched_rule_id == "HW-L-020-RISER"
    assert result.device_type == "riser"
    assert result.hw_type == "riser"


# ── PR-10 Q10e: Air Duct → HW/air_duct/accessory ──────────────────────────────

@pytest.mark.parametrize("option_id, option_name", [
    ("C3RP", "ThinkSystem 2U GPU air duct"),       # PR-10 fix: was hijacked by HW-L-007-GPU
    ("BP46", "ThinkSystem 2U Main Air Duct"),
    ("BV2A", "ThinkSystem SR950 V3 Air Duct"),
    ("B8NM", "ThinkSystem 1U MS Air Duct"),
    ("BQ2Z", "ThinkSystem 2U MS main Airduct"),    # spaceless variant
])
def test_pr10_air_duct_is_air_duct(lenovo_ruleset, option_id, option_name):
    """PR-10 Q10e: Lenovo Air Duct / Airduct SKUs route to HW/air_duct/accessory
    via the new HW-L-064-AIR-DUCT rule. Was accessory/accessory (or gpu/gpu for
    C3RP because of the 'GPU' keyword). New device_type 'air_duct' represents an
    airflow guide; mapped to hw_type=accessory (no 'cooling' bucket exists in
    the canonical 26-value HW_TYPE_VOCAB)."""
    r = _row(option_name, option_id=option_id)
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.matched_rule_id == "HW-L-064-AIR-DUCT"
    assert result.device_type == "air_duct"
    assert result.hw_type == "accessory"


def test_pr10_air_baffle_remains_accessory(lenovo_ruleset):
    """NEGATIVE PR-10 Q10e guard: 'Air Baffle' (BT6C/BT6E) must keep routing
    to HW-L-027-ACCESSORY (accessory/accessory). The new HW-L-064-AIR-DUCT
    pattern is intentionally narrowed to Air Duct / Airduct only — Baffle
    stays in the accessory catch-all per PR-10 spec."""
    r = _row("ThinkSystem SR850 V3 Front CPUs 1U Air Baffle 1", option_id="BT6C")
    result = classify_row(r, lenovo_ruleset)
    assert result.matched_rule_id == "HW-L-027-ACCESSORY"
    assert result.device_type == "accessory"
    assert result.hw_type == "accessory"


def test_pr10_air_duct_filler_remains_blank_filler(lenovo_ruleset):
    """REGRESSION PR-10 Q10e: 'Air Duct Filler' (B8MP) must keep routing to
    HW-L-005-BLANK-RISER → blank_filler. The Filler keyword is caught earlier;
    the new air_duct rule does NOT preempt blank_filler classification."""
    r = _row("ThinkSystem 2U MS Air Duct Filler(For 2U Gap)", option_id="B8MP")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.device_type == "blank_filler"
    assert result.hw_type == "blank_filler"


def test_pr10_heatsink_remains_heatsink(lenovo_ruleset):
    """NEGATIVE PR-10 Q10e guard: Heatsink stays heatsink/heatsink (no
    accidental promotion to air_duct via the new rule)."""
    r = _row("ThinkSystem SR650 V3 Performance Heatsink")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.device_type == "heatsink"
    assert result.hw_type == "heatsink"


def test_pr10_fan_module_remains_fan(lenovo_ruleset):
    """NEGATIVE PR-10 Q10e guard: Fan module stays fan/fan."""
    r = _row("ThinkSystem 2U V3 Performance Fan Module")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.device_type == "fan"
    assert result.hw_type == "fan"


# ── PR-10 Q10a sanity: Fan Control Board (no change) ─────────────────────────

def test_pr10_c9jt_fan_control_board_remains_fan(lenovo_ruleset):
    """PR-10 Q10a sanity: C9JT 'ThinkSystem SR680a V3 for B200 Server Fan
    Control Board' was already routed via HW-L-043-FAN-BOARD → fan/fan
    in PR-4b. Guards against regression from PR-10 rule additions."""
    r = _row("ThinkSystem SR680a V3 for B200 Server Fan Control Board", option_id="C9JT")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.HW
    assert result.matched_rule_id == "HW-L-043-FAN-BOARD"
    assert result.device_type == "fan"
    assert result.hw_type == "fan"


# ── Edge cases ───────────────────────────────────────────────────────────────

def test_unknown_row(lenovo_ruleset):
    r = _row("Totally unmatched row text XYZ123")
    result = classify_row(r, lenovo_ruleset)
    assert result.entity_type == EntityType.UNKNOWN
