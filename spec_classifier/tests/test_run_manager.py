"""Tests for run_manager.py — detect_vendor_from_path + write_manifest."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.diagnostics.run_manager import detect_vendor_from_path, write_manifest


# ---------------------------------------------------------------------------
# detect_vendor_from_path
# ---------------------------------------------------------------------------

class TestDetectVendorFromPath:
    """Consolidated vendor-detection tests for the shared run_manager function.

    Reference contract: test_batch_audit.TestDetectVendorFromPath (Phase 8 D-07 state).
    Assertions from test_cluster_audit that encode dropped *_run/ccw_export aliases
    are intentionally excluded (D-13: ccw dropped; D-14: *_run aliases gone).
    """

    KNOWN = ["cisco", "dell", "hpe"]

    def test_dell_split_layout(self):
        assert detect_vendor_from_path(Path("OUTPUT/SPLIT/dell/dl1/dl1_annotated.xlsx"), self.KNOWN) == "dell"

    def test_hpe_split_layout(self):
        assert detect_vendor_from_path(Path("OUTPUT/SPLIT/hpe/hp1/hp1_annotated.xlsx"), self.KNOWN) == "hpe"

    def test_cisco_split_layout(self):
        assert detect_vendor_from_path(Path("OUTPUT/SPLIT/cisco/ccw_1/ccw_1_annotated.xlsx"), self.KNOWN) == "cisco"

    def test_hp_run_alias_removed_returns_unknown(self):
        # The hp_run -> hpe alias was removed in Phase 8 (D-07) and does not exist
        # in the unified function. A bare hp_run-style path no longer maps to hpe.
        assert detect_vendor_from_path(Path("OUTPUT/hp_run/file.xlsx"), self.KNOWN) == "unknown"

    def test_lenovo_run_returns_unknown(self):
        # lenovo not in KNOWN; the {vendor}_run matcher is gone -> unknown.
        assert detect_vendor_from_path(Path("OUTPUT/lenovo_run/file.xlsx"), self.KNOWN) == "unknown"

    def test_no_vendor_keyword_returns_unknown(self):
        assert detect_vendor_from_path(Path("/some/random/path/file.xlsx"), self.KNOWN) == "unknown"

    def test_new_vendor_in_known_vendors(self):
        extended = self.KNOWN + ["lenovo"]
        assert detect_vendor_from_path(Path("OUTPUT/SPLIT/lenovo/L1/L1_annotated.xlsx"), extended) == "lenovo"

    def test_vendor_in_directory_path(self):
        assert detect_vendor_from_path(Path("OUTPUT/dell/subdir/file.xlsx"), self.KNOWN) == "dell"

    def test_prefix_segment_does_not_shadow_real_vendor(self):
        # CR-01 regression: a vendor-named prefix segment (e.g. a Windows username
        # `C:\Users\dell\...`) must NOT shadow the real <vendor> segment that sits
        # next to the file in the canonical <bucket>/<vendor>/<spec>/<file> layout.
        # Built from explicit parts so the path splits identically on POSIX and Windows.
        p = Path("Users", "dell", "Desktop", "OUTPUT", "AUDIT", "hpe", "hp1",
                 "hp1_annotated_audited.xlsx")
        assert detect_vendor_from_path(p, self.KNOWN) == "hpe"


# ---------------------------------------------------------------------------
# write_manifest
# ---------------------------------------------------------------------------

def test_write_manifest_creates_readme(tmp_path):
    """write_manifest creates README.md at output_root with static artifact table."""
    write_manifest(tmp_path)
    readme = tmp_path / "README.md"
    assert readme.exists(), "write_manifest must create README.md at output_root"
    content = readme.read_text(encoding="utf-8")

    # Three bucket sections present
    assert "## READY" in content, "READY section missing from manifest"
    assert "## SPLIT" in content, "SPLIT section missing from manifest"
    assert "## AUDIT" in content, "AUDIT section missing from manifest"

    # Russian/Cyrillic characters present in purpose column
    assert any(ord(c) > 127 for c in content), \
        "Purpose text must contain Russian (Cyrillic) characters"

    # At least 14 artifact rows (count non-header, non-separator table lines)
    table_rows = [
        line for line in content.splitlines()
        if line.startswith("|") and "---" not in line and "Файл" not in line
    ]
    assert len(table_rows) >= 14, \
        f"Expected >= 14 artifact rows in manifest, got {len(table_rows)}"

    # Key artifact patterns present
    assert "Коммерческое предложение_<spec>.xlsx" in content, \
        "READY branded artifact missing from manifest"
    assert "_annotated.xlsx" in content, \
        "SPLIT annotated artifact missing from manifest"
    assert "_annotated_audited.xlsx" in content, \
        "AUDIT audited artifact missing from manifest"
    assert "audit_report.json" in content, \
        "AUDIT root audit_report.json missing from manifest"
    assert "cluster_summary.xlsx" in content, \
        "AUDIT root cluster_summary.xlsx missing from manifest"


def test_write_manifest_idempotent(tmp_path):
    """Calling write_manifest twice produces identical bytes."""
    write_manifest(tmp_path)
    first = (tmp_path / "README.md").read_bytes()
    write_manifest(tmp_path)
    second = (tmp_path / "README.md").read_bytes()
    assert first == second, "write_manifest must be idempotent (same bytes on re-run)"


def test_write_manifest_creates_output_root_if_missing(tmp_path):
    """write_manifest creates output_root directory if it does not exist."""
    target = tmp_path / "new_output"
    assert not target.exists()
    write_manifest(target)
    assert (target / "README.md").exists(), \
        "README.md must be created even when output_root did not pre-exist"
