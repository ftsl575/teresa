"""
DEC acceptance tests (P1–P8). Covers OptionIDs from QA checklist.
Deterministic assertions on entity_type, state, hw_type, device_type.
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
    option_id=None,
    skus=None,
    **kwargs,
) -> NormalizedRow:
    defaults = {
        "group_name": None,
        "group_id": None,
        "product_name": None,
        "option_id": option_id,
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


# --- GEVNB9T: HDD (F1 / DEC) ---
def test_dec_gevnb9t_hdd(ruleset):
    row = _row(
        module_name="Hard Drives",
        option_name="2.4TB Hard Drive SAS FIPS-140  10K 512e 2.5in Hot-Plug",
        option_id="GEVNB9T",
    )
    r = classify_row(row, ruleset)
    assert r.entity_type == EntityType.HW
    assert r.state.value == "PRESENT"
    assert r.hw_type == "hdd"


# --- GDIOK4A, GN1I836: No Cable -> CONFIG ABSENT (DEC-001) ---
def test_dec_gdiok4a_no_cable_config(ruleset):
    row = _row(option_name="2 OCP - No Cable", option_id="GDIOK4A")
    r = classify_row(row, ruleset)
    assert r.entity_type == EntityType.CONFIG
    assert r.state.value == "ABSENT"
    assert r.hw_type is None


def test_dec_gn1i836_no_cable_config(ruleset):
    row = _row(option_name="1 OCP - No Cable", option_id="GN1I836")
    r = classify_row(row, ruleset)
    assert r.entity_type == EntityType.CONFIG
    assert r.state.value == "ABSENT"
    assert r.hw_type is None


# --- G0PNZWL: No Cables Required, No GPU Blanks -> CONFIG ABSENT (DEC-002) ---
def test_dec_g0pnzwl_gpu_blanks_config(ruleset):
    row = _row(option_name="No Cables Required, No GPU Blanks", option_id="G0PNZWL")
    r = classify_row(row, ruleset)
    assert r.entity_type == EntityType.CONFIG
    assert r.state.value == "ABSENT"
    assert r.hw_type is None


# --- G0FVJIE, GNID9SB: Optics -> HW network_adapter (DEC-004) ---
def test_dec_g0fvjie_optics_network_adapter(ruleset):
    row = _row(option_name="SFP+ SR Optic, 10GbE, for all SFP+ ports except high temp", option_id="G0FVJIE")
    r = classify_row(row, ruleset)
    assert r.entity_type == EntityType.HW
    assert r.state.value == "PRESENT"
    assert r.hw_type == "network_adapter"
    assert r.matched_rule_id == "HW-OPTICS-001"


def test_dec_gnid9sb_transceiver_network_adapter(ruleset):
    row = _row(option_name="Dell Networking, Transceiver, 25GbE SFP28 SR, No FEC, MMF, Duplex LC", option_id="GNID9SB")
    r = classify_row(row, ruleset)
    assert r.entity_type == EntityType.HW
    assert r.state.value == "PRESENT"
    assert r.hw_type == "network_adapter"
    assert r.matched_rule_id == "HW-OPTICS-001"


# --- PERC Controller -> HW storage_controller, raid_controller (DEC-005) ---
def test_dec_perc_controller_raid(ruleset):
    row = _row(
        module_name="RAID Controllers",
        option_name="PERC H755 SAS Front Controller",
    )
    r = classify_row(row, ruleset)
    assert r.entity_type == EntityType.HW
    assert r.state.value == "PRESENT"
    assert r.hw_type == "storage_controller"
    assert r.device_type == "raid_controller"


def test_dec_perc_h345_controller(ruleset):
    row = _row(option_name="PERC H345 Controller", module_name="RAID Controllers")
    r = classify_row(row, ruleset)
    assert r.entity_type == EntityType.HW
    assert r.hw_type == "storage_controller"
    assert r.device_type == "raid_controller"


# --- G5PJAF3: Rear Blanks -> HW blank PRESENT (DEC-003) ---
def test_dec_g5pjaf3_rear_blanks(ruleset):
    row = _row(
        module_name="Additional Network Cards",
        option_name="No OCP - 2 Rear Blanks",
        option_id="G5PJAF3",
    )
    r = classify_row(row, ruleset)
    assert r.entity_type == EntityType.HW
    assert r.state.value == "PRESENT"
    assert r.hw_type == "blank"


# --- G2ITOYM: BOSS-N1 -> storage_controller (DEC-006) ---
def test_dec_g2itoym_boss_storage_controller(ruleset):
    row = _row(
        option_name="BOSS-N1 controller card +  with 2 M.2 480GB (RAID 1) (22x80) Rear",
        option_id="G2ITOYM",
    )
    r = classify_row(row, ruleset)
    assert r.entity_type == EntityType.HW
    assert r.state.value == "PRESENT"
    assert r.hw_type == "storage_controller"
    assert r.matched_rule_id == "HW-BOSS-001"


# --- GIEP1Z6: No BOSS Card -> CONFIG ABSENT (DEC-006) ---
def test_dec_giep1z6_no_boss_card_config(ruleset):
    row = _row(option_name="No BOSS Card", option_id="GIEP1Z6")
    r = classify_row(row, ruleset)
    assert r.entity_type == EntityType.CONFIG
    assert r.state.value == "ABSENT"
    assert r.hw_type is None
    assert r.matched_rule_id == "CONFIG-NOBOSS-001"
