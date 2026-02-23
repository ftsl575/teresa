"""
Unit tests for device_type assignment (Phase 2 rules: LOGISTIC-004-CORD, HW-005–009, LOGISTIC-005-SFP-CABLE).
Covers MUST-FIX SKUs from vnext_plan1.md and edge cases (UNKNOWN → device_type None; non-HW/LOGISTIC → None).
"""

import pytest
from pathlib import Path

from src.core.normalizer import NormalizedRow, RowKind
from src.core.classifier import EntityType, classify_row
from src.rules.rules_engine import RuleSet

from conftest import project_root


def _ruleset() -> RuleSet:
    path = project_root() / "rules" / "dell_rules.yaml"
    return RuleSet.load(str(path))


@pytest.fixture
def ruleset():
    return _ruleset()


def _row(
    *,
    row_kind=RowKind.ITEM,
    module_name="",
    option_name="",
    source_row_index=1,
    skus=None,
    **kwargs,
) -> NormalizedRow:
    defaults = {
        "group_name": None,
        "group_id": None,
        "product_name": None,
        "option_id": None,
        "skus": skus or [],
        "qty": 1,
        "option_price": 0.0,
    }
    defaults.update(kwargs)
    return NormalizedRow(
        source_row_index=source_row_index,
        row_kind=row_kind,
        module_name=module_name,
        option_name=option_name,
        **defaults,
    )


# --- Power Cords (LOGISTIC-004-CORD) ---
def test_power_cord_rack_c13_c14(ruleset):
    row = _row(option_name="Rack Power Cord 2M (C13/C14 10A)", skus=["450-AADY"])
    r = classify_row(row, ruleset)
    assert r.entity_type == EntityType.LOGISTIC
    assert r.matched_rule_id == "LOGISTIC-004-CORD"
    assert r.device_type == "power_cord"


def test_power_cord_c19_c20(ruleset):
    row = _row(option_name="C19 to C20, 250V, 0.6m Power Cord", skus=["450-AAXT"])
    r = classify_row(row, ruleset)
    assert r.entity_type == EntityType.LOGISTIC
    assert r.matched_rule_id == "LOGISTIC-004-CORD"
    assert r.device_type == "power_cord"


def test_power_cord_jumper(ruleset):
    row = _row(option_name="Jumper Cord - C13/C14, 0,6M, 250V, 10A (US,EUR)", skus=["450-AADX"])
    r = classify_row(row, ruleset)
    assert r.entity_type == EntityType.LOGISTIC
    assert r.matched_rule_id == "LOGISTIC-004-CORD"
    assert r.device_type == "power_cord"


# --- Storage SSD/NVMe (HW-005-STORAGE-CUS) ---
def test_storage_ssd_cus_kit(ruleset):
    row = _row(
        option_name="480GB SSD SATA Mixed Use 6Gbps 512e 2.5in Hot-Plug, CUS Kit",
        skus=["345-BDPH"],
    )
    r = classify_row(row, ruleset)
    assert r.entity_type == EntityType.HW
    assert r.matched_rule_id == "HW-005-STORAGE-CUS"
    assert r.device_type == "storage_ssd"


def test_storage_nvme_customer_kit(ruleset):
    row = _row(
        option_name="800G Data Center NVMe Mixed Use AG Drive U2 with carrier, Customer Kit",
        skus=["345-BKBV"],
    )
    r = classify_row(row, ruleset)
    assert r.entity_type == EntityType.HW
    assert r.matched_rule_id == "HW-005-STORAGE-CUS"
    assert r.device_type == "storage_nvme"


# --- PSU (HW-006-PSU-CUS) ---
def test_psu_800w_customer_kit(ruleset):
    row = _row(
        option_name="Single, Hot-Plug MHS Power Supply, 800W, Customer Kit",
        skus=["384-BDQX"],
    )
    r = classify_row(row, ruleset)
    assert r.entity_type == EntityType.HW
    assert r.matched_rule_id == "HW-006-PSU-CUS"
    assert r.device_type == "psu"


def test_psu_1500w_titanium_ck(ruleset):
    row = _row(
        option_name="Single, Hot-Plug MHS Power Supply, 1500W, Titanium, Customer Kit",
        skus=["384-BDRL"],
    )
    r = classify_row(row, ruleset)
    assert r.entity_type == EntityType.HW
    assert r.matched_rule_id == "HW-006-PSU-CUS"
    assert r.device_type == "psu"


# --- NIC (HW-007-NIC-CUS) ---
def test_nic_intel_e810_customer_kit(ruleset):
    row = _row(
        option_name="Intel E810-XXV 25GbE SFP28 Dual Port PCIe Low Profile Customer Kit",
        skus=["540-BCXX"],
    )
    r = classify_row(row, ruleset)
    assert r.entity_type == EntityType.HW
    assert r.matched_rule_id == "HW-007-NIC-CUS"
    assert r.device_type == "nic"


def test_nic_broadcom_ocp_customer_install(ruleset):
    row = _row(
        option_name="Broadcom 57504 Quad Port 10/25GbE, SFP28, OCP NIC 3.0 Customer Install",
        skus=["540-BCRY"],
    )
    r = classify_row(row, ruleset)
    assert r.entity_type == EntityType.HW
    assert r.matched_rule_id == "HW-007-NIC-CUS"
    assert r.device_type == "nic"


# --- SFP Cable (LOGISTIC-005-SFP-CABLE) ---
def test_sfp_cable_twinax_3m(ruleset):
    row = _row(
        option_name="Dell Networking, Cable, SFP28 to SFP28, 25GbE, Passive Copper Twinax Direct Attach Cable, 3 Meter",
        skus=["470-ACEV"],
    )
    r = classify_row(row, ruleset)
    assert r.entity_type == EntityType.LOGISTIC
    assert r.matched_rule_id == "LOGISTIC-005-SFP-CABLE"
    assert r.device_type == "sfp_cable"


def test_sfp_cable_cus_kit(ruleset):
    row = _row(
        option_name="SC Cable, SFP28 to SFP28, 25GbE, Passive Copper Twinax Direct Attach Cable, 3 Meter, Cus Kit",
        skus=["470-ADDO"],
    )
    r = classify_row(row, ruleset)
    assert r.entity_type == EntityType.LOGISTIC
    assert r.matched_rule_id == "LOGISTIC-005-SFP-CABLE"
    assert r.device_type == "sfp_cable"


# --- HBA / PERC (HW-008-HBA-PERC-CUS) ---
def test_hba_full_height_dib(ruleset):
    row = _row(option_name="HBA465e Adapter Full Height DIB", skus=["405-BBDC"])
    r = classify_row(row, ruleset)
    assert r.entity_type == EntityType.HW
    assert r.matched_rule_id == "HW-008-HBA-PERC-CUS"
    assert r.device_type == "hba"


def test_hba_full_height_low_profile_ck(ruleset):
    row = _row(option_name="HBA465e Adapter Full Height/Low Profile, CK", skus=["405-BBDD"])
    r = classify_row(row, ruleset)
    assert r.entity_type == EntityType.HW
    assert r.matched_rule_id == "HW-008-HBA-PERC-CUS"
    assert r.device_type == "hba"


def test_perc_controller_ck(ruleset):
    row = _row(option_name="PERC H965i Controller, Front, DCMHS, CK", skus=["403-BDMW"])
    r = classify_row(row, ruleset)
    assert r.entity_type == EntityType.HW
    assert r.matched_rule_id == "HW-008-HBA-PERC-CUS"
    assert r.device_type == "raid_controller"


def test_fibre_channel_hba(ruleset):
    row = _row(
        option_name="QLogic 2772 Dual Port 32Gb Fibre Channel HBA, PCIe Full Height, V2",
        skus=["540-BDHC"],
    )
    r = classify_row(row, ruleset)
    assert r.entity_type == EntityType.HW
    assert r.matched_rule_id == "HW-008-HBA-PERC-CUS"
    assert r.device_type == "hba"


# --- CPU (HW-009-CPU-CUS) ---
def test_cpu_xeon_customer_install(ruleset):
    row = _row(
        option_name="Intel Xeon 6 Performance 6737P 2.9G, 32C/64T, 24GT/s, 144M Cache, Turbo, (270W) DDR5-6400, Customer Install",
        skus=["338-CSZN"],
    )
    r = classify_row(row, ruleset)
    assert r.entity_type == EntityType.HW
    assert r.matched_rule_id == "HW-009-CPU-CUS"
    assert r.device_type == "cpu"


def test_cpu_xeon_6511p_ck(ruleset):
    row = _row(
        option_name="Intel Xeon 6 Performance 6511P 2.5G, 16C/32T, 72M Cache, Turbo, (150W) DDR5-6400, Customer Install",
        skus=["338-CSZP"],
    )
    r = classify_row(row, ruleset)
    assert r.entity_type == EntityType.HW
    assert r.matched_rule_id == "HW-009-CPU-CUS"
    assert r.device_type == "cpu"


# --- Edge: UNKNOWN row → device_type is None ---
def test_unknown_row_has_no_device_type(ruleset):
    row = _row(option_name="Some random option with no matching rule", skus=["999-XXXX"])
    r = classify_row(row, ruleset)
    assert r.entity_type == EntityType.UNKNOWN
    assert r.matched_rule_id == "UNKNOWN-000"
    assert r.device_type is None


# --- Edge: HEADER row → device_type not set ---
def test_header_row_no_device_type(ruleset):
    row = _row(row_kind=RowKind.HEADER, module_name="", option_name="", skus=[])
    r = classify_row(row, ruleset)
    assert r.row_kind == RowKind.HEADER
    assert r.entity_type is None
    assert r.matched_rule_id == "HEADER-SKIP"
    assert r.device_type is None


# --- Edge: BASE/SERVICE (non-HW/LOGISTIC) → device_type None ---
def test_base_row_no_device_type(ruleset):
    row = _row(module_name="Base", option_name="", skus=[])
    r = classify_row(row, ruleset)
    assert r.entity_type == EntityType.BASE
    assert r.matched_rule_id == "BASE-001"
    assert r.device_type is None
