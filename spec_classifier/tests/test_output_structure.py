"""
Regression test: output tree shape for the new bucket layout.
- output_root / SPLIT / <vendor> / <spec> / artifacts   (nine per-spec artifacts)
- output_root / READY / <vendor> / <spec> / Коммерческое предложение_<spec>.xlsx  (branded — all vendors)
Required always: rows_raw.json, rows_normalized.json, classification.jsonl, cleaned_spec.xlsx,
  header_rows.csv, unknown_rows.csv, run_summary.json, run.log
Dell: <stem>_annotated.xlsx in SPLIT + Коммерческое предложение_<stem>.xlsx in READY
Cisco: <stem>_annotated.xlsx in SPLIT + Коммерческое предложение_<stem>.xlsx in READY (all vendors brand)
Uses tmp_path for output_root; no large golden blobs in git.
"""

import subprocess
import sys
from pathlib import Path

import pytest

from conftest import project_root, get_input_root_dell, get_input_root_cisco

# Required artifacts in every SPLIT/<vendor>/<spec>/ folder
REQUIRED_ARTIFACTS = [
    "rows_raw.json",
    "rows_normalized.json",
    "classification.jsonl",
    "cleaned_spec.xlsx",
    "header_rows.csv",
    "unknown_rows.csv",
    "run_summary.json",
    "run.log",
]


def test_output_tree_shape_dell_run(tmp_path):
    """Dell: output_root/SPLIT/dell/<stem>/ with all artifacts + READY/dell/<stem>/branded."""
    root = project_root()
    input_root = get_input_root_dell()
    input_xlsx = input_root / "dl1.xlsx"
    if not input_xlsx.exists():
        pytest.skip(f"Input not found: {input_xlsx} (set paths.input_root in config.local.yaml, files expected at INPUT\\ or INPUT\\dell\\)")

    output_root = tmp_path / "output"
    output_root.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        [
            sys.executable, "main.py",
            "--input", str(input_xlsx),
            "--config", str(root / "config.yaml"),
            "--output-dir", str(output_root),
        ],
        cwd=str(root),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"CLI failed: {result.stderr!r}"

    # New assertions — bucket layout:
    stem = "dl1"
    split_folder = output_root / "SPLIT" / "dell" / stem
    ready_folder = output_root / "READY" / "dell" / stem

    assert split_folder.is_dir(), f"SPLIT/dell/{stem} folder must exist under {output_root}"
    assert not (output_root / "dell_run").exists(), "Old dell_run/ folder must NOT exist"

    for name in REQUIRED_ARTIFACTS:
        assert (split_folder / name).exists(), f"Required artifact missing: {name} in {split_folder}"

    assert (split_folder / f"{stem}_annotated.xlsx").exists(), f"{stem}_annotated.xlsx missing in {split_folder}"

    assert ready_folder.is_dir(), f"READY/dell/{stem} folder must exist under {output_root}"
    branded_name = f"Коммерческое предложение_{stem}.xlsx"
    assert (ready_folder / branded_name).exists(), f"{branded_name} missing in {ready_folder} (Dell)"


def test_output_tree_shape_cisco_run(tmp_path):
    """Cisco: output_root/SPLIT/cisco/<stem>/ with artifacts + branded in READY/cisco/<stem>/."""
    root = project_root()
    input_xlsx = get_input_root_cisco() / "ccw_1.xlsx"
    if not input_xlsx.exists():
        pytest.skip(f"Input not found: {input_xlsx} (set paths.input_root in config.local.yaml)")

    output_root = tmp_path / "output"
    output_root.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        [
            sys.executable, "main.py",
            "--input", str(input_xlsx),
            "--vendor", "cisco",
            "--config", str(root / "config.yaml"),
            "--output-dir", str(output_root),
        ],
        cwd=str(root),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"CLI failed: {result.stderr!r}"

    # New assertions — bucket layout:
    stem = "ccw_1"
    split_folder = output_root / "SPLIT" / "cisco" / stem

    assert split_folder.is_dir(), f"SPLIT/cisco/{stem} folder must exist under {output_root}"
    assert not (output_root / "cisco_run").exists(), "Old cisco_run/ folder must NOT exist"

    for name in REQUIRED_ARTIFACTS:
        assert (split_folder / name).exists(), f"Required artifact missing: {name} in {split_folder}"

    assert (split_folder / f"{stem}_annotated.xlsx").exists(), f"{stem}_annotated.xlsx missing in {split_folder}"

    # Cisco brands like every vendor — single source: VendorAdapter.generates_branded_spec() → True
    ready_folder = output_root / "READY" / "cisco" / stem
    assert ready_folder.is_dir(), f"READY/cisco/{stem} folder must exist under {output_root}"
    branded_name = f"Коммерческое предложение_{stem}.xlsx"
    assert (ready_folder / branded_name).exists(), f"{branded_name} missing in {ready_folder} (Cisco)"


def test_output_root_configurable_via_cli(tmp_path):
    """Output root is overridden by --output-dir; artifacts are under output_root/SPLIT/dell/."""
    root = project_root()
    input_xlsx = get_input_root_dell() / "dl1.xlsx"
    if not input_xlsx.exists():
        pytest.skip(f"Input not found: {input_xlsx} (set paths.input_root in config.local.yaml)")

    output_root = tmp_path / "custom_out"
    result = subprocess.run(
        [
            sys.executable, "main.py",
            "--input", str(input_xlsx),
            "--config", str(root / "config.yaml"),
            "--output-dir", str(output_root),
        ],
        cwd=str(root),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0
    assert output_root.exists()
    split_vendor = output_root / "SPLIT" / "dell"
    assert split_vendor.is_dir(), \
        "Output must be under output_root/SPLIT/dell/ (repo stays clean when using external path)"
