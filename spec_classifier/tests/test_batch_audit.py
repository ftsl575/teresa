"""Tests for batch_audit.py — validate_row() E1-E18 + REAL_BUG classification."""

import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from batch_audit import (
    validate_row, _generate_report, detect_vendor_from_path,
    issue_color, _is_known_fp, KNOWN_FP_CASES,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _row(**kw) -> dict:
    """Minimal row dict with sensible defaults."""
    defaults = {
        "entity_type": "HW",
        "state": "PRESENT",
        "hw_type": "cpu",
        "device_type": "cpu",
        "option_name": "Intel Xeon Gold 5416S",
    }
    defaults.update(kw)
    return defaults


# ---------------------------------------------------------------------------
# validate_row: clean / HEADER baseline
# ---------------------------------------------------------------------------

def test_clean_row_returns_ok():
    issues = validate_row(_row(), "hpe")
    assert issues == []


def test_header_row_skipped():
    row = _row(row_kind="HEADER", entity_type="", state="", hw_type="", device_type="")
    assert validate_row(row, "hpe") == []


# ---------------------------------------------------------------------------
# E1 — invalid entity type
# ---------------------------------------------------------------------------

def test_e1_invalid_entity():
    issues = validate_row(_row(entity_type="FOOBAR", hw_type="", device_type=""), "hpe")
    assert any("E1:" in i for i in issues)


# ---------------------------------------------------------------------------
# E2 — UNKNOWN
# ---------------------------------------------------------------------------

def test_e2_unknown_entity():
    issues = validate_row(_row(entity_type="UNKNOWN", hw_type="", device_type=""), "hpe")
    assert any("E2:" in i for i in issues)


# ---------------------------------------------------------------------------
# E3 — invalid state
# ---------------------------------------------------------------------------

def test_e3_invalid_state():
    issues = validate_row(_row(state="BOGUS"), "hpe")
    assert any("E3:" in i for i in issues)


# ---------------------------------------------------------------------------
# E4 — state logic by vendor (parametrized)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("vendor, option_name, state, expect_e4", [
    # Dell: "No ..." should be ABSENT
    ("dell", "No Hard Drive", "PRESENT", True),
    # Dell: "No 2 Rear Blanks" override — should NOT fire
    ("dell", "No 2 Rear Blanks Included", "PRESENT", False),
    # Dell: "Disabled" keyword
    ("dell", "RAID Disabled", "PRESENT", True),
    # Dell: "None" keyword
    ("dell", "None Selected", "PRESENT", True),
    # Dell: "Without" keyword
    ("dell", "Without RAID Controller", "PRESENT", True),
    # Cisco: "No ... Selected"
    ("cisco", "No Option Selected", "PRESENT", True),
    # HPE: ABSENT is unexpected
    ("hpe", "Some HPE Component", "ABSENT", True),
    # HPE: PRESENT is fine
    ("hpe", "Some HPE Component", "PRESENT", False),
])
def test_e4_state_logic(vendor, option_name, state, expect_e4):
    row = _row(option_name=option_name, state=state, hw_type="cpu", device_type="cpu")
    issues = validate_row(row, vendor)
    has_e4 = any("E4:" in i for i in issues)
    assert has_e4 == expect_e4


# ---------------------------------------------------------------------------
# E5 — hw_type on non-HW entity
# ---------------------------------------------------------------------------

def test_e5_hw_type_on_config():
    issues = validate_row(_row(entity_type="CONFIG", hw_type="cpu", device_type=""), "hpe")
    assert any("E5:" in i for i in issues)


def test_e5_logistic_with_hw_type():
    issues = validate_row(_row(entity_type="LOGISTIC", hw_type="cable", device_type="power_cord"), "hpe")
    assert any("E5:hw_type_on_non_hw" in i for i in issues)


# ---------------------------------------------------------------------------
# E6 — device_type on wrong entity
# ---------------------------------------------------------------------------

def test_e6_device_type_on_config():
    issues = validate_row(_row(entity_type="CONFIG", device_type="cpu", hw_type=""), "hpe")
    assert any("E6:" in i for i in issues)


def test_e6_not_fired_for_base():
    issues = validate_row(_row(entity_type="BASE", device_type="server", hw_type=""), "hpe")
    assert not any("E6:" in i for i in issues)


# ---------------------------------------------------------------------------
# E7 — hw_type not in vocab
# ---------------------------------------------------------------------------

def test_e7_hw_type_not_in_vocab():
    issues = validate_row(_row(hw_type="flux_capacitor"), "hpe")
    assert any("E7:" in i for i in issues)


# ---------------------------------------------------------------------------
# E8 — HW missing hw_type
# ---------------------------------------------------------------------------

def test_e8_hw_missing_hw_type():
    issues = validate_row(_row(hw_type="", device_type=""), "hpe")
    assert any("E8:" in i for i in issues)


# ---------------------------------------------------------------------------
# E9 — device_type → hw_type mapping mismatch
# ---------------------------------------------------------------------------

def test_e9_mapping_mismatch():
    issues = validate_row(_row(device_type="cpu", hw_type="memory"), "hpe")
    assert any("E9:" in i for i in issues)
    assert any("mapping_mismatch" in i for i in issues)


def test_e9_hw_type_missing_for_device_type():
    row = _row(device_type="cpu", hw_type="", state="ABSENT")
    issues = validate_row(row, "hpe")
    assert any("E9:" in i and "missing_for_device_type" in i for i in issues)


# ---------------------------------------------------------------------------
# E10 — hw_type on BASE
# ---------------------------------------------------------------------------

def test_e10_hw_type_on_base():
    issues = validate_row(_row(entity_type="BASE", hw_type="server", device_type="server"), "hpe")
    assert any("E10:" in i for i in issues)


def test_e10_device_type_on_base_ok():
    """device_type on BASE should NOT trigger E10 after P0-2 fix."""
    issues = validate_row(_row(entity_type="BASE", device_type="server", hw_type=""), "hpe")
    assert not any("E10:" in i for i in issues)


# ---------------------------------------------------------------------------
# E11 — hw_type on CONFIG
# ---------------------------------------------------------------------------

def test_e11_hw_type_on_config():
    issues = validate_row(_row(entity_type="CONFIG", hw_type="cpu", device_type=""), "hpe")
    assert any("E11:" in i for i in issues)


# ---------------------------------------------------------------------------
# E12 — hw/device_type on NOTE
# ---------------------------------------------------------------------------

def test_e12_hw_type_on_note():
    issues = validate_row(_row(entity_type="NOTE", hw_type="cpu", device_type=""), "hpe")
    assert any("E12:" in i for i in issues)


def test_e12_device_type_on_note():
    issues = validate_row(_row(entity_type="NOTE", hw_type="", device_type="cpu"), "hpe")
    assert any("E12:" in i for i in issues)


# ---------------------------------------------------------------------------
# E13 — LOGISTIC with physical cable
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("dt, hw", [
    ("power_cord", None),
    ("cable", "cable"),
    ("sfp_cable", "cable"),
    ("fiber_cable", "cable"),
])
def test_e13_logistic_with_physical_cable(dt, hw):
    row = _row(entity_type="LOGISTIC", device_type=dt, hw_type=hw or "")
    issues = validate_row(row, "hpe")
    assert any("E13:" in i for i in issues)


# ---------------------------------------------------------------------------
# E14 — CONFIG looks like blank_filler
# ---------------------------------------------------------------------------

def test_e14_config_blank_filler():
    row = _row(entity_type="CONFIG", option_name="Dummy PID for Airflow Selection",
               device_type="", hw_type="")
    issues = validate_row(row, "dell")
    assert any("E14:" in i for i in issues)


# ---------------------------------------------------------------------------
# E15 — BASE without device_type (info)
# ---------------------------------------------------------------------------

def test_e15_base_no_device_type():
    row = _row(entity_type="BASE", device_type="", hw_type="")
    issues = validate_row(row, "hpe")
    assert any("E15:" in i for i in issues)


# ---------------------------------------------------------------------------
# E16 — blank_filler + ABSENT (info)
# ---------------------------------------------------------------------------

def test_e16_blank_filler_absent():
    row = _row(entity_type="HW", device_type="blank_filler", hw_type="blank_filler", state="ABSENT")
    issues = validate_row(row, "dell")
    assert any("E16:" in i for i in issues)


# ---------------------------------------------------------------------------
# E17 — HW without device_type and hw_type, PRESENT
# ---------------------------------------------------------------------------

def test_e17_hw_no_type_determined():
    row = _row(entity_type="HW", device_type="", hw_type="", state="PRESENT")
    issues = validate_row(row, "hpe")
    assert any("E17:" in i for i in issues)


# ---------------------------------------------------------------------------
# E18 — LOGISTIC with physical keyword, no device_type
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("option_name", [
    "Power cord 2m",
    "Rack mounting bracket",
    "Rail kit for DL380",
    "Cable management arm",
    "PDU 16A basic unit",
    "UPS battery replacement kit",
])
def test_e18_logistic_physical_keyword_no_device_type(option_name):
    row = _row(entity_type="LOGISTIC", option_name=option_name, device_type="", hw_type="")
    issues = validate_row(row, "hpe")
    assert any("E18:" in i for i in issues)


def test_e8_excluded_for_power_cord():
    row = _row(entity_type="HW", state="PRESENT", device_type="power_cord", hw_type="")
    issues = validate_row(row, "hpe")
    assert not any("E8:" in i for i in issues)


def test_e18_not_fired_when_device_type_set():
    row = _row(entity_type="LOGISTIC", option_name="Power cord 2m",
               device_type="power_cord", hw_type="")
    issues = validate_row(row, "hpe")
    assert not any("E18:" in i for i in issues)


# ---------------------------------------------------------------------------
# _generate_report: REAL_BUG / FALSE_POSITIVE / REVIEW_NEEDED classification
# ---------------------------------------------------------------------------

def _make_issue(file: str, vendor: str, tag: str) -> dict:
    return {"file": file, "vendor": vendor, "tag": tag}


class TestRealBugClassification:
    """Test the bug classification logic inside _generate_report by feeding
    crafted report_files with pre-baked results strings."""

    def _run_report(self, results_tags: list[str], *, vendor="hpe", tmpdir=None) -> dict:
        """Run _generate_report with minimal stubs and return the parsed report."""
        report_files = [{
            "file": "fake_annotated.xlsx",
            "vendor": vendor,
            "total_rows": len(results_tags),
            "ok": 0,
            "issues": len(results_tags),
            "cost_usd": 0.0,
            "results": results_tags,
        }]
        out = str(tmpdir)
        _generate_report(report_files, out, "no-model", 0, 0, use_ai=False)
        report_path = Path(out) / "audit_report.json"
        return json.loads(report_path.read_text(encoding="utf-8"))

    def test_device_mismatch_3_items_is_real_bug(self, tmp_path):
        tags = [
            "AI_MISMATCH:device_type[pipeline:server→ai:cable]",
            "AI_MISMATCH:device_type[pipeline:server→ai:cable]",
            "AI_MISMATCH:device_type[pipeline:server→ai:cable]",
        ]
        report = self._run_report(tags, tmpdir=tmp_path)
        real_bugs = [b for b in report["bugs"] if b["type"] == "REAL_BUG"]
        assert len(real_bugs) >= 1
        assert real_bugs[0]["pattern"].startswith("device_mismatch:")

    def test_device_mismatch_1_item_is_review(self, tmp_path):
        tags = ["AI_MISMATCH:device_type[pipeline:cpu→ai:gpu]"]
        report = self._run_report(tags, tmpdir=tmp_path)
        review = [b for b in report["bugs"] if b["type"] == "REVIEW_NEEDED"]
        assert len(review) >= 1

    def test_entity_mismatch_fp_pattern_is_false_positive(self, tmp_path):
        tags = [
            "AI_MISMATCH:entity[pipeline:HW→ai:LOGISTIC]",
            "AI_MISMATCH:entity[pipeline:HW→ai:LOGISTIC]",
        ]
        report = self._run_report(tags, tmpdir=tmp_path)
        fps = [b for b in report["bugs"] if b["type"] == "FALSE_POSITIVE"]
        assert len(fps) >= 1

    def test_entity_mismatch_not_in_fp_is_review(self, tmp_path):
        tags = [
            "AI_MISMATCH:entity[pipeline:HW→ai:SERVICE]",
        ]
        report = self._run_report(tags, tmpdir=tmp_path)
        reviews = [b for b in report["bugs"] if b["type"] == "REVIEW_NEEDED"]
        assert len(reviews) >= 1

    def test_device_mismatch_2_files_is_real_bug(self, tmp_path):
        """2 items from 2 different files → REAL_BUG."""
        report_files = [
            {
                "file": "file_a.xlsx", "vendor": "hpe",
                "total_rows": 1, "ok": 0, "issues": 1, "cost_usd": 0.0,
                "results": ["AI_MISMATCH:device_type[pipeline:ram→ai:gpu]"],
            },
            {
                "file": "file_b.xlsx", "vendor": "hpe",
                "total_rows": 1, "ok": 0, "issues": 1, "cost_usd": 0.0,
                "results": ["AI_MISMATCH:device_type[pipeline:ram→ai:gpu]"],
            },
        ]
        out = str(tmp_path)
        _generate_report(report_files, out, "no-model", 0, 0, use_ai=False)
        report = json.loads((tmp_path / "audit_report.json").read_text(encoding="utf-8"))
        real_bugs = [b for b in report["bugs"] if b["type"] == "REAL_BUG"]
        assert len(real_bugs) >= 1


# ---------------------------------------------------------------------------
# Known-case suppression (_is_known_fp)
# ---------------------------------------------------------------------------

class TestKnownFPSuppression:
    """Tests for KNOWN_FP_CASES + _is_known_fp narrow suppression."""

    def test_hpe_cable_kit_cable_to_accessory(self):
        items = [
            {"vendor": "hpe", "option_name": "OCPA Cable Kit"},
            {"vendor": "hpe", "option_name": "GPU Power Cable Kit"},
        ]
        assert _is_known_fp(items, "device_mismatch", "cable→accessory") is True

    def test_hpe_hybrid_capacitor_battery_to_accessory(self):
        items = [
            {"vendor": "hpe", "option_name": "HPE Smart Storage Hybrid Capacitor with 260mm Cable Kit"},
        ]
        assert _is_known_fp(items, "device_mismatch", "battery→accessory") is True

    def test_hpe_nvlink_bridge_accessory_to_gpu(self):
        items = [
            {"vendor": "hpe", "option_name": "NVIDIA 4-way NVLink Bridge for H200 NVL"},
        ]
        assert _is_known_fp(items, "device_mismatch", "accessory→gpu") is True

    def test_hpe_cable_management_arm_accessory_to_cable(self):
        items = [{"vendor": "hpe", "option_name": "HPE DL38X Gen10 Plus 2U Cable Management Arm for Rail Kit"}]
        assert _is_known_fp(items, "device_mismatch", "accessory→cable") is True

    def test_dell_cable_to_accessory_not_suppressed(self):
        """Dell row with cable→accessory but no Cable Kit → NOT false positive."""
        items = [
            {"vendor": "dell", "option_name": "Random Cable Assembly"},
        ]
        assert _is_known_fp(items, "device_mismatch", "cable→accessory") is False


# ---------------------------------------------------------------------------
# detect_vendor_from_path
# ---------------------------------------------------------------------------

class TestDetectVendorFromPath:

    def test_dell_run(self):
        assert detect_vendor_from_path(Path("OUTPUT/dell_run/file.xlsx")) == "dell"

    def test_lenovo_run_returns_unknown(self):
        assert detect_vendor_from_path(Path("OUTPUT/lenovo_run/file.xlsx")) == "unknown"

    def test_no_vendor_keyword_returns_unknown(self):
        assert detect_vendor_from_path(Path("/some/random/path/file.xlsx")) == "unknown"


# ---------------------------------------------------------------------------
# Alias product_# → skus
# ---------------------------------------------------------------------------

def test_product_hash_alias(tmp_path):
    """Column 'product_#' should be normalized to 'skus' via _ALIASES."""
    from batch_audit import write_audited_excel
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["entity_type", "state", "hw_type", "device_type", "option_name", "product_#"])
    ws.append(["HW", "PRESENT", "cpu", "cpu", "CPU Module", "ABC-123"])
    tmp_in = tmp_path / "input.xlsx"
    wb.save(tmp_in)
    tmp_out = tmp_path / "output.xlsx"
    success, results, option_names = write_audited_excel(tmp_in, tmp_out, "hpe", None)
    assert success
    assert all(r == "OK" or "product_#" not in r for r in results)


# ---------------------------------------------------------------------------
# issue_color
# ---------------------------------------------------------------------------

class TestIssueColor:

    def test_e1_returns_orange(self):
        assert issue_color("E1:invalid_entity_type[FOOBAR]") == "FFE0B2"

    def test_e2_returns_red(self):
        assert issue_color("E2:unknown_entity") == "FFC7CE"

    def test_e15_returns_grey(self):
        assert issue_color("E15:base_no_device_type") == "F5F5F5"

    def test_e18_returns_yellow(self):
        assert issue_color("E18:logistic_with_physical_keyword[no_device_type:cord]") == "FFFDE7"


# ---------------------------------------------------------------------------
# E18 edge cases
# ---------------------------------------------------------------------------

class TestE18EdgeCases:

    def test_logistic_bracket_fires_e18(self):
        row = _row(entity_type="LOGISTIC", option_name="Mounting bracket kit",
                   device_type="", hw_type="")
        issues = validate_row(row, "hpe")
        assert any("E18:" in i for i in issues)

    def test_logistic_pdu_fires_e18(self):
        row = _row(entity_type="LOGISTIC", option_name="PDU 16A basic unit",
                   device_type="", hw_type="")
        issues = validate_row(row, "hpe")
        assert any("E18:" in i for i in issues)

    def test_logistic_with_device_type_no_e18(self):
        row = _row(entity_type="LOGISTIC", option_name="Mounting bracket kit",
                   device_type="accessory", hw_type="accessory")
        issues = validate_row(row, "hpe")
        assert not any("E18:" in i for i in issues)


# ---------------------------------------------------------------------------
# Negative: mismatch without known-case suppression → NOT FALSE_POSITIVE
# ---------------------------------------------------------------------------

def test_unknown_device_mismatch_not_suppressed():
    """A device_mismatch with no KNOWN_FP_CASES entry should be REAL_BUG or REVIEW_NEEDED."""
    items = [
        {"vendor": "cisco", "option_name": "Some Cisco Part"},
        {"vendor": "cisco", "option_name": "Another Cisco Part"},
        {"vendor": "cisco", "option_name": "Third Cisco Part"},
    ]
    assert _is_known_fp(items, "device_mismatch", "fan→gpu") is False
