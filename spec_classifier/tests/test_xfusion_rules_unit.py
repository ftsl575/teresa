"""Unit tests for xFusion classification rules (no external input files).

Strings are taken verbatim from real fixtures (xf2 / xf3 / xf4 / xf6 / xf9 /
xf10). Test names ending in '_fires_before_*' or 'fires_as_*_not_*' are
ORDER-CRITICAL CI gates against rule-ordering regressions.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.classifier import classify_row, EntityType
from src.core.normalizer import RowKind
from src.rules.rules_engine import RuleSet, match_device_type_rule
from src.vendors.xfusion.normalizer import XFusionNormalizedRow


@pytest.fixture
def xfusion_ruleset():
    rules_path = Path(__file__).resolve().parent.parent / "rules" / "xfusion_rules.yaml"
    return RuleSet.load(str(rules_path))


def _row(option_name: str, *, option_id: str = "0231Y000",
         module_name: str = "") -> XFusionNormalizedRow:
    return XFusionNormalizedRow(
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


# ─── ORDER-CRITICAL TESTS (CI gates against ordering regression) ────────────

def test_hba_fires_before_transceiver(xfusion_ruleset):
    """FC HBA descriptions contain '(with 2x Multi-mode Optical Transceiver)'.
    HBA rule (#11) MUST fire before transceiver rule (#14)."""
    desc = ('Emulex,FC HBA,-32Gb/s(LPe32002),2-Port,'
            'SFP+(with 2x Multi-mode Optical Transceiver),'
            'PCIE 3.0 x8-Vendor ID 10DF-Device ID E300-2')
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.entity_type == EntityType.HW
    assert r.matched_rule_id == "HW-XF-011-HBA"
    assert r.device_type == "hba"
    assert r.hw_type == "hba"


def test_hba_card_lpe35002_fires_as_hba(xfusion_ruleset):
    """Variant: 'Emulex,HBA Card LPE35002-AP,FC Double Ports--32Gb/s,SFP28+(...)'."""
    desc = ('Emulex,HBA Card LPE35002-AP,FC Double Ports--32Gb/s,'
            'SFP28+(with 2x Multi-mode Optical Transceiver),'
            'PCIE 4.0 x8-Vendor ID 10DF-Device ID F600')
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-011-HBA"
    assert r.hw_type == "hba"


def test_nic_ethernet_adapter_fires_before_transceiver(xfusion_ruleset):
    """Ethernet Adapter with SFP+ in description must NOT fall to transceiver."""
    desc = ('XC333 OCP3.0 Ethernet Adapter-10GE(BCM57412)-Dual Port-'
            'SFP+(without Optical Module)-PCIE 3.0 X8-Vendor ID 14E4-Device ID 16D7')
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-012-NIC"
    assert r.device_type == "nic"
    assert r.hw_type == "network_adapter"


def test_nic_ethernet_card_fires_as_nic(xfusion_ruleset):
    """'Ethernet Card' (not 'Adapter') variant from xf6."""
    desc = ('XC310 BC53ETHF- GE350-T2 OCP3.0 Ethernet Card-2*GE(I350)-'
            'Dual Port-RJ45, PCIE 2.1 x4-Vendor ID 8086-Device ID 1521')
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-012-NIC"
    assert r.hw_type == "network_adapter"


def test_nic_network_card_with_sfp28_fires_as_nic(xfusion_ruleset):
    """'Network Card' with SFP28 — must NOT be transceiver, must NOT be cable."""
    desc = ('Network Card,25Gb Optical Interface(BCM957414A4142CC),'
            '2-Port,SFP28(without Optical Transceiver),PCIE 3.0 x8-Vendor ID 14E4')
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-012-NIC"
    assert r.hw_type == "network_adapter"


def test_transceiver_lowercase_t_matches(xfusion_ruleset):
    """xfusion uses lowercase 't' in 'Optical transceiver' (not 'Transceiver')."""
    desc = 'Optical transceiver,SFP+,850nm,10Gb/s,-7.3~-1dBm,-9.9dBm,LC, MM,0.3km'
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-014-TRANSCEIVER"
    assert r.device_type == "transceiver"
    assert r.hw_type == "transceiver"


def test_a800_auxiliary_fires_as_accessory_not_gpu(xfusion_ruleset):
    """Per Q2: A800 auxiliary is accessory NOT gpu — GPU-ACCESSORY rule (#10)
    MUST fire before GPU rule (#13)."""
    desc = 'A800 auxiliary material package'
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-010-GPU-ACCESSORY"
    assert r.device_type == "accessory"
    assert r.hw_type == "accessory"


def test_m2_raid_pcie_card_fires_as_storage_controller(xfusion_ruleset):
    """Per Q3: M.2 RAID PCIE card is storage_controller, NOT storage_drive.
    Cannot be caught by HW-XF-005-STORAGE-M2 (which requires \\bM\\.2\\s+SSD\\b)."""
    desc = ('XP270-M2-(SAS3808-BootCard)-M.2 RAID PCIE card-'
            'RAID0,1,JBOD-No CacheSupport Sideband Management')
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-009-RAID-CONTROLLER"
    assert r.device_type == "raid_controller"
    assert r.hw_type == "storage_controller"


def test_io1_2_module_fires_as_riser_not_backplane(xfusion_ruleset):
    """Per Q5: 'IO1&2 module' MUST be riser, NOT accessory.
    Backplane regex (#21) is strict \\bBackplane\\b — must NOT catch generic 'Module'."""
    desc = '1*16X SLOT(PCIE5.0)+2*8X SLOT(PCIE4.0)-IO1&2 module'
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-019-RISER"
    assert r.device_type == "riser"
    assert r.hw_type == "riser"


# ─── BASE / CHASSIS ─────────────────────────────────────────────────────────

def test_base_chassis_intel_xeon_1288h_v6(xfusion_ruleset):
    desc = '1288H V6 (8*2.5 inch HDD Chassis) H12H-06(For oversea)'
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.entity_type == EntityType.BASE
    assert r.matched_rule_id == "BASE-XF-001-CHASSIS"
    assert r.device_type == "server"


def test_base_chassis_amd_genoa(xfusion_ruleset):
    desc = 'AMD Genoa (12*3.5inch HDD Through Chassis)A22H-07(For oversea)'
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.entity_type == EntityType.BASE
    assert r.matched_rule_id == "BASE-XF-001-CHASSIS"


def test_base_chassis_5288_raid(xfusion_ruleset):
    desc = '5288 V7(40*3.5 inch HDD single RAID Chassis B)(For oversea)'
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.entity_type == EntityType.BASE
    assert r.matched_rule_id == "BASE-XF-001-CHASSIS"


def test_base_chassis_5885h_with_extras(xfusion_ruleset):
    """Chassis line mentions 'EXP backplane' but BASE rule must fire first
    (priority order: BASE before HW per classifier pipeline)."""
    desc = ('5885H V7(25*2.5-inch HDD Chassis,EXP backplane,'
            'supporting GPU,8080 fans)(For oversea)')
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.entity_type == EntityType.BASE
    assert r.matched_rule_id == "BASE-XF-001-CHASSIS"


# ─── CPU (Q1) ───────────────────────────────────────────────────────────────

def test_cpu_intel_xeon_processor(xfusion_ruleset):
    """Intel Xeon ... Processor (no 'CPU' keyword)."""
    desc = ('Intel Xeon Gold 6348(2.6GHz/28-Core/42MB/235W)'
            'Ice lake Processor (with 1U heatsink)')
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-002-CPU"
    assert r.device_type == "cpu"
    assert r.hw_type == "cpu"


def test_cpu_intel_xeon_cpu(xfusion_ruleset):
    desc = ('Intel Xeon Gold 6430(2.1GHz/32-core/60MB/270W) '
            'Sapphire Rapids XCC CPU (with 1U special heatsink)')
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-002-CPU"
    assert r.hw_type == "cpu"


def test_cpu_amd_genoa(xfusion_ruleset):
    desc = ('AMD Genoa 9554(3.1GHz/64-Core/256MB/360W)CPU '
            '(with 2U body 2U special heatsink)')
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-002-CPU"
    assert r.hw_type == "cpu"


# ─── GPU vs A800 auxiliary (Q2) ─────────────────────────────────────────────

def test_gpu_tesla_t4_fires_as_gpu(xfusion_ruleset):
    desc = ('NVIDIA,Tesla T4,16GB Memory/ 320GB/s Bandwidth/ '
            'PCIE 3.0 X16-10DE-1EB8-1,70W/ Single Slot/PassiveCoolling')
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-013-GPU"
    assert r.device_type == "gpu"
    assert r.hw_type == "gpu"


def test_gpu_video_card_a40_fires_as_gpu(xfusion_ruleset):
    desc = ('Video Card,GPU-Data Center A40 PCIe,'
            'PN:900-2G133-0000-100/48GB Memory/696GB/s Bandwidth/'
            'PCIE 4.0 x16-10DE-2235-1,300W/dualSlot/PassiveCooling,'
            'English doc,1PCS Cable')
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-013-GPU"
    assert r.hw_type == "gpu"


def test_dual_slot_gpu_accessories_fires_as_accessory(xfusion_ruleset):
    desc = 'Accessories for dual slot GPU card'
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-010-GPU-ACCESSORY"
    assert r.hw_type == "accessory"


# ─── M.2 SSD vs M.2 RAID Card (Q3) ──────────────────────────────────────────

def test_m2_ssd_fires_as_storage_drive(xfusion_ruleset):
    """ORDER-CRITICAL: M.2 SSD rule (#5) must fire BEFORE STORAGE-SSD (#6),
    else 'M.2 SSD,SATA' would be caught by \\bSSD\\b.*?\\bSATA\\b first."""
    desc = 'M.2 SSD,SATA 6Gb/s-480GB,hot-swappable'
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-005-STORAGE-M2"
    assert r.device_type == "storage_ssd"
    assert r.hw_type == "storage_drive"


# ─── CABLE family (Q4) — all → hw_type=cable ────────────────────────────────

def test_high_speed_cable_sfp28_fires_as_cable(xfusion_ruleset):
    desc = ('High Speed Cable,25G SFP28 Passive High Speed Cable,3m,'
            'SFP28,CC2P0.254B(S),SFP28')
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-015-CABLE"
    assert r.device_type == "cable"
    assert r.hw_type == "cable"


def test_mini_sas_hd_cable_fires_as_cable(xfusion_ruleset):
    desc = ('High Speed Cable,Internal Mini SAS HD Cable,0.9m,'
            'Internal Mini SAS HD R/A,...')
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-015-CABLE"
    assert r.hw_type == "cable"


def test_power_cable_fires_as_cable(xfusion_ruleset):
    desc = 'Power Cable'
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-015-CABLE"
    assert r.hw_type == "cable"


def test_btb_connector_fires_as_cable(xfusion_ruleset):
    desc = ('BTB Connector module,74,UBC 8X curved,800mm,0.16mm,10mm,'
            '22500MB/s,1.57mm,Wire mounting,Y')
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-015-CABLE"
    assert r.hw_type == "cable"


# ─── POWER CORD (separate from cable; hw_type=None) ─────────────────────────

def test_power_cords_cable_fires_as_power_cord(xfusion_ruleset):
    """device_type=power_cord. NOT in device_type_map → hw_type=None."""
    desc = ('Power Cords Cable,Europe AC 250V10A,1.8m,C14SM,'
            'H05VV-F- 3*1.00^2,C13SF,PDU Cable')
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-016-POWER-CORD"
    assert r.device_type == "power_cord"
    assert r.hw_type is None


# ─── BACKPLANE (Q5) ─────────────────────────────────────────────────────────

def test_backplane_fires_as_backplane(xfusion_ruleset):
    desc = 'Rear 4*2.5" Hard Disk Backplane Module for NVME'
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-021-BACKPLANE"
    assert r.device_type == "backplane"
    assert r.hw_type == "backplane"


def test_backplane_module_dt_rule_fires(xfusion_ruleset):
    """PR-3: explicit DT-level check — DT-XF-022-BACKPLANE must win on xf9:33
    descriptor. Pipeline matched_rule_id reflects the HW-level rule
    (HW-XF-021-BACKPLANE), but device_type=backplane can only be emitted by
    DT-XF-022-BACKPLANE, not by DT-XF-018-ACCESSORY (which no longer matches
    \\bBackplane\\b after Spec 2.A)."""
    desc = 'Rear 4*2.5" Hard Disk Backplane Module for NVME'
    dt_match = match_device_type_rule(_row(desc), xfusion_ruleset.device_type_rules)
    assert dt_match is not None
    assert dt_match["rule_id"] == "DT-XF-022-BACKPLANE"
    assert dt_match["device_type"] == "backplane"


# ─── SOFTWARE ───────────────────────────────────────────────────────────────

def test_sw_88_prefix_fires_as_software(xfusion_ruleset):
    """SKU prefix-based rule (matches by option_id, not description)."""
    r = classify_row(_row("Anything goes here", option_id="8803Y126"), xfusion_ruleset)
    assert r.entity_type == EntityType.SOFTWARE
    assert r.matched_rule_id == "SW-XF-001-SKU-PREFIX"


def test_sw_fusiondirector_description_fires_as_software(xfusion_ruleset):
    """option_id without 88 prefix; option_name carries 'FusionDirector'."""
    r = classify_row(_row("FusionDirector V100R001 base license", option_id="0231Y999"),
                     xfusion_ruleset)
    assert r.entity_type == EntityType.SOFTWARE
    assert r.matched_rule_id == "SW-XF-002-LICENSE-DESC"


# ─── PSU / MEMORY / STORAGE / FAN / RAIL / RISER / SUPERCAP / RAID ──────────

def test_psu_titanium_fires_as_psu(xfusion_ruleset):
    desc = 'Server Titanium 2000W AC power supply'
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-001-PSU"
    assert r.hw_type == "psu"


def test_psu_power_module_fires_as_psu(xfusion_ruleset):
    desc = '900W Titanium AC Power Module'
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-001-PSU"
    assert r.hw_type == "psu"


def test_memory_ddr4_rdimm_comma(xfusion_ruleset):
    desc = 'DDR4,RDIMM,64GB,288pin,0.625ns,3200000KHz,1.2V,ECC,2Rank(4G*4bit)'
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-003-MEMORY"
    assert r.hw_type == "memory"


def test_memory_ddr5_rdimm_space(xfusion_ruleset):
    desc = ('DDR5 RDIMM DRAM,64GB,288pin,0.42ns,4800MT/s,1.1V,'
            'ECC,2Rank(4G*4bit)')
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-003-MEMORY"
    assert r.hw_type == "memory"


def test_storage_nvme(xfusion_ruleset):
    desc = ('SSD,3840GB,NVMe PCIe,Read Intensive,PM9A3 Series,'
            '2.5inch(2.5inch Drive Bay)')
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-004-STORAGE-NVME"
    assert r.device_type == "storage_nvme"
    assert r.hw_type == "storage_drive"


def test_storage_ssd_sas(xfusion_ruleset):
    desc = ('SSD,6400GB,SAS 12Gb/s,Mixed Use,UH631a-Y Series,'
            '2.5inch(2.5inch Drive Bay)')
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-006-STORAGE-SSD"
    assert r.device_type == "storage_ssd"
    assert r.hw_type == "storage_drive"


def test_storage_hdd_nl_sas(xfusion_ruleset):
    desc = ('HDD,20000GB,NL SAS 12Gb/s,7200rpm,256MB,'
            '3.5inch(3.5inch Drive Bay)')
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-007-STORAGE-HDD"
    assert r.device_type == "storage_hdd"
    assert r.hw_type == "storage_drive"


def test_fan_module_fires_as_fan(xfusion_ruleset):
    desc = '4056+ Fan module'
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-017-FAN"
    assert r.hw_type == "fan"


def test_air_duct_fires_as_air_duct(xfusion_ruleset):
    """PR-10 Q10e: xfusion 'Air duct' SKUs route to HW/air_duct/accessory.
    Was accessory/accessory pre-PR-10 — DT-XF-018-ACCESSORY was split into
    DT-XF-018A-AIR-DUCT (Air duct → air_duct) and DT-XF-018-ACCESSORY
    (Fan bracket / Extended radiator → accessory). Entity rule
    HW-XF-018-AIR-DUCT-ACCESSORY itself unchanged."""
    desc = 'Air duct(2U radiator)'
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-018-AIR-DUCT-ACCESSORY"
    assert r.device_type == "air_duct"
    assert r.hw_type == "accessory"


def test_xfusion_fan_bracket_remains_accessory(xfusion_ruleset):
    """NEGATIVE PR-10 Q10e guard: xfusion 'Fan bracket' (e.g. SKU 21203766)
    must NOT be promoted to air_duct — stays accessory/accessory via the
    trimmed DT-XF-018-ACCESSORY pattern (Fan bracket / Extended radiator only)."""
    r = classify_row(_row("Fan bracket"), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-018-AIR-DUCT-ACCESSORY"
    assert r.device_type == "accessory"
    assert r.hw_type == "accessory"


def test_xfusion_extended_radiator_remains_accessory(xfusion_ruleset):
    """NEGATIVE PR-10 Q10e guard: xfusion 'Extended radiator bracket assembly'
    (e.g. SKU 0231YAFU '5288 V7 2U Extended radiator bracket assembly') must
    stay accessory/accessory — distinct from Air duct semantics."""
    r = classify_row(_row("5288 V7 2U Extended radiator bracket assembly"), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-018-AIR-DUCT-ACCESSORY"
    assert r.device_type == "accessory"
    assert r.hw_type == "accessory"


def test_rail_kit_fires_as_rail(xfusion_ruleset):
    desc = 'Ball Bearing Rail Kit(Direct delivery material)'
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-020-RAIL"
    assert r.hw_type == "rail"


def test_riser_pcie4_fires_as_riser(xfusion_ruleset):
    desc = '2*16X SLOT(PCIE4.0) RISER1 Module'
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-019-RISER"
    assert r.hw_type == "riser"


def test_riser_with_riser_digit_suffix(xfusion_ruleset):
    """xf3 row 61: 'SLOT,RISER1&RISER2 module' — must match \\bRISER\\d*\\b
    (not bare \\bRISER\\b which fails on 'RISER1' because '1' is a word char)."""
    desc = '3*16X SLOT,RISER1&RISER2 module'
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-019-RISER"
    assert r.hw_type == "riser"


def test_supercap_standalone_fires_as_battery_accessory(xfusion_ruleset):
    """PR-8 / Q6: Super capacitor module → device_type=battery, hw_type=accessory.
    Unified with lenovo SuperCap (HW-L-026-BATTERY) and HPE Hybrid Capacitor /
    Smart Storage Battery (HW-H-GLOBAL-030)."""
    desc = ('Super capacitor module,64mm*51mm*13.1mm,Wire mounting,'
            'split from 08170002,NA,7600uF,5h')
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-008-SUPERCAP"
    assert r.device_type == "battery"
    assert r.hw_type == "accessory"


def test_supercap_raid_card_fires_as_battery_accessory(xfusion_ruleset):
    """ORDER-CRITICAL: SUPERCAP (#8) must fire BEFORE RAID-CONTROLLER (#9),
    else 'RAID Card SuperCap' would be caught by \\bRAID\\s+Card\\b first.
    PR-8 / Q6: device_type=battery (unified with lenovo/hpe)."""
    desc = '35xx/39xx RAID Card SuperCap'
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-008-SUPERCAP"
    assert r.device_type == "battery"
    assert r.hw_type == "accessory"


def test_raid_card_supercap_with_used_for_fires_as_battery_accessory(xfusion_ruleset):
    """PR-8 / Q6: device_type=battery (unified with lenovo/hpe)."""
    desc = 'RAID Card SuperCap,used for 35XX/39XX'
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-008-SUPERCAP"
    assert r.device_type == "battery"
    assert r.hw_type == "accessory"


# ─── PR-8 / Q6: SuperCap unification — real-fixture SKU descriptions ────────

def test_supercap_sku_0231yaal_fires_as_battery(xfusion_ruleset):
    """xf2/xf3 fixture SKU 0231YAAL — verbatim option_name from real eDeal."""
    desc = 'RAID Card SuperCap,used for 35XX/39XX'
    r = classify_row(_row(desc, option_id='0231YAAL'), xfusion_ruleset)
    assert r.entity_type == EntityType.HW
    assert r.matched_rule_id == "HW-XF-008-SUPERCAP"
    assert r.device_type == "battery"
    assert r.hw_type == "accessory"


def test_supercap_sku_0231y384_fires_as_battery(xfusion_ruleset):
    """xf3 fixture SKU 0231Y384 — verbatim option_name from real eDeal."""
    desc = '35xx/39xx RAID Card SuperCap'
    r = classify_row(_row(desc, option_id='0231Y384'), xfusion_ruleset)
    assert r.entity_type == EntityType.HW
    assert r.matched_rule_id == "HW-XF-008-SUPERCAP"
    assert r.device_type == "battery"
    assert r.hw_type == "accessory"


def test_supercap_sku_0231y676_fires_as_battery(xfusion_ruleset):
    """xf5/xf7/xf8/xf9 fixture SKU 0231Y676 — verbatim option_name from real eDeal."""
    desc = 'RAID Card SuperCap, used for 35xx/39xx'
    r = classify_row(_row(desc, option_id='0231Y676'), xfusion_ruleset)
    assert r.entity_type == EntityType.HW
    assert r.matched_rule_id == "HW-XF-008-SUPERCAP"
    assert r.device_type == "battery"
    assert r.hw_type == "accessory"


def test_negative_raid_card_cable_does_not_match_supercap(xfusion_ruleset):
    """NEGATIVE PR-8 guard: 'RAID Card Cable' must NOT match SUPERCAP rule.
    SUPERCAP regex is anchored on '\\bRAID\\s+Card\\s+SuperCap\\b' — a bare
    'RAID Card Cable' must fall through to RAID-CONTROLLER (whose pattern
    explicitly admits 'RAID (?:Cable )?Card') and never become a battery."""
    desc = 'RAID Card Cable,Mini-SAS HD,0.8m'
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id != "HW-XF-008-SUPERCAP"
    assert r.device_type != "battery"


def test_negative_power_cable_does_not_match_supercap(xfusion_ruleset):
    """NEGATIVE PR-8 guard: generic 'Power Cable' must NOT match SUPERCAP rule.
    Must fall to HW-XF-015-CABLE (device_type=cable, hw_type=cable)."""
    desc = 'Power Cable,1.5m,12AWG,for PSU'
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id != "HW-XF-008-SUPERCAP"
    assert r.device_type != "battery"
    assert r.matched_rule_id == "HW-XF-015-CABLE"
    assert r.device_type == "cable"
    assert r.hw_type == "cable"


def test_raid_controller_9560_fires_as_storage_controller(xfusion_ruleset):
    desc = '9560-8i,PCIe RAID Controller,4GB Cache,PCIe 4.0 X8-HH/HL'
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-009-RAID-CONTROLLER"
    assert r.device_type == "raid_controller"
    assert r.hw_type == "storage_controller"


def test_sas_sata_raid_card_mr_fires_as_storage_controller(xfusion_ruleset):
    desc = ('SAS/SATA RAID Card MR,RAID0,1,5,6,10,50,60,4GB Cache,'
            'Support SuperCap and Sideband Management-3508 BCM')
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.matched_rule_id == "HW-XF-009-RAID-CONTROLLER"
    assert r.hw_type == "storage_controller"


# ─── NEGATIVE cross-vendor: foreign descriptions don't match xfusion rules ─

def test_huawei_disk_unit_does_not_match_xfusion(xfusion_ruleset):
    """Huawei NVMe Disk Unit description must NOT fall to any HW-XF-* rule."""
    r = classify_row(_row("10x 7.68TB SSD NVMe Palm Disk Unit"), xfusion_ruleset)
    rid = r.matched_rule_id or ""
    # Must not match any XF rule (unrelated description)
    assert "-XF-" not in rid, f"Huawei disk unit matched xfusion rule: {rid}"
    assert r.entity_type == EntityType.UNKNOWN


# ── Phase 4 calibration tests ───────────────────────────────────────────────

def test_amd_turin_chassis_fires_as_base(xfusion_ruleset):
    """xf1 row 39 — AMD Turin chassis must be BASE (per Phase 4 calibration)."""
    desc = "AMD Turin (8*3.5inch SAS/SATA HDD Through Chassis)(For oversea)"
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.entity_type == EntityType.BASE, f"entity_type={r.entity_type}, rule={r.matched_rule_id}"
    assert r.device_type == "server", f"device_type={r.device_type}"


def test_sas_raid_9540_fires_as_storage_controller(xfusion_ruleset):
    """xf5/xf10 rows — '12G SAS RAID-9540-8i' must be storage_controller.
    Description starts with PCIE 4.0 X8-Vendor ID prefix; RAID appears mid-string."""
    desc = (
        "PCIE 4.0 X8-Vendor ID 1000-Device ID 10E6-1-Subvendor ID 1000-"
        "Subdevice ID 40D5-12G SAS RAID-9540-8i"
    )
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.entity_type == EntityType.HW, f"entity_type={r.entity_type}, rule={r.matched_rule_id}"
    assert r.hw_type == "storage_controller", f"hw_type={r.hw_type}"
    assert r.device_type == "raid_controller", f"device_type={r.device_type}"


def test_io_extended_module_fires_as_riser(xfusion_ruleset):
    """xf5 row 124 — 'IO Extended Module' under module='Riser Card' must be riser."""
    desc = "1*16X SLOT,CPU straight out IO Extended Module"
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.entity_type == EntityType.HW, f"entity_type={r.entity_type}, rule={r.matched_rule_id}"
    assert r.hw_type == "riser", f"hw_type={r.hw_type}"
    assert r.device_type == "riser", f"device_type={r.device_type}"


def test_gpu_card_power_line_fires_as_accessory_not_cable(xfusion_ruleset):
    """xf5 row 135 — GPU power line must be accessory (stakeholder decision Phase 4).
    GPU-ACCESSORY rule (#10) must fire before CABLE rule (#15) — order-critical guard."""
    desc = (
        "GPU Card Power Line Spare Pack(H100&L40&RTX4090 Card "
        "Power Line,PCIE 16Pin to PCIE 16Pin)"
    )
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.entity_type == EntityType.HW, f"entity_type={r.entity_type}, rule={r.matched_rule_id}"
    assert r.hw_type == "accessory", f"hw_type={r.hw_type} (expected accessory, not cable)"
    assert r.device_type == "accessory", f"device_type={r.device_type}"
    assert "GPU-ACCESSORY" in (r.matched_rule_id or ""), (
        f"Must match GPU-ACCESSORY rule, got: {r.matched_rule_id}"
    )


def test_optical_cable_parts_mpo_fires_as_cable(xfusion_ruleset):
    """xf5 row 139 — Optical Cable Parts MPO must be cable.
    Per Q4 decision: all cable forms (SAS / power / BTB / optical MPO) -> hw_type=cable."""
    desc = (
        "Optical Cable Parts,MPO/PC,MPO/PC,Multi-mode,5m,8 cores,"
        "0m/0m,GJFH-8A1a.2(OM3),3.5mm,LSZH,60mm MPO,Bending insensitive"
    )
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.entity_type == EntityType.HW, f"entity_type={r.entity_type}, rule={r.matched_rule_id}"
    assert r.hw_type == "cable", f"hw_type={r.hw_type}"
    assert r.device_type == "cable", f"device_type={r.device_type}"


# ── PR-2 calibration tests ─────────────────────────────────────────────────

def test_g5500_v7_chassis_fires_as_base(xfusion_ruleset):
    """xf5 row 115 — G5500 V7 chassis line. Plain BASE-XF-001 regex required
    (?:G)?\\d{4}H?\\s+V\\d to admit the G-prefixed model number, otherwise
    the row falls through to HW/storage_hdd via HW-XF-007-STORAGE-HDD."""
    desc = (
        "G5500 V7(24*3.5inch HDD Chassis-Support 16*3.5 SAS/SATA+8*3.5 SAS/SATA/"
        "CPU NVMe, EXP backplane,SWITCH 8 FHFL GPU cards)(For oversea)"
    )
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.entity_type == EntityType.BASE, f"entity_type={r.entity_type}, rule={r.matched_rule_id}"
    assert r.matched_rule_id == "BASE-XF-001-CHASSIS"
    assert r.device_type == "server", f"device_type={r.device_type}"


def test_5885h_v7_chassis_with_backplane_keeps_server_dt(xfusion_ruleset):
    """xf3 row 48 — 5885H V7 chassis with 'EXP backplane' in description.
    Pre-PR-2 ordering let DT-XF-018-ACCESSORY (matches \\bBackplane\\b) fire
    first, mis-tagging the row as device_type=accessory. After reordering
    DT-XF-021-CHASSIS BEFORE DT-XF-018-ACCESSORY, the BASE row must keep
    device_type=server."""
    desc = (
        "5885H V7(25*2.5-inch HDD Chassis,EXP backplane,"
        "supporting GPU,8080 fans)(For oversea)"
    )
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.entity_type == EntityType.BASE, f"entity_type={r.entity_type}, rule={r.matched_rule_id}"
    assert r.matched_rule_id == "BASE-XF-001-CHASSIS"
    assert r.device_type == "server", f"device_type={r.device_type} (must be server, not accessory)"


def test_raid_card_riser_fires_as_riser_not_raid_controller(xfusion_ruleset):
    """xf5 row 126 — 'RAID Card riser' is a RISER, not a RAID controller.
    HW-XF-008C-RAID-CARD-RISER must fire BEFORE HW-XF-009-RAID-CONTROLLER,
    otherwise the broader \\bRAID\\s+(?:Cable\\s+)?Card\\b alternative would
    mis-tag the row as raid_controller / storage_controller."""
    desc = "1*8X SLOT(PCIE4.0),RAID Card riser,Suitable for G5500 3.5-inch integrated equipment"
    r = classify_row(_row(desc), xfusion_ruleset)
    assert r.entity_type == EntityType.HW, f"entity_type={r.entity_type}, rule={r.matched_rule_id}"
    assert r.matched_rule_id == "HW-XF-008C-RAID-CARD-RISER"
    assert r.device_type == "riser", f"device_type={r.device_type}"
    assert r.hw_type == "riser", f"hw_type={r.hw_type}"
