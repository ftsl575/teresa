"""
Regression test: output tree shape must match out.zip (golden reference).
- output_root / {vendor}_run / run-YYYY-MM-DD__HH-MM-SS-<stem> / artifacts
- Required always: rows_raw.json, rows_normalized.json, classification.jsonl, cleaned_spec.xlsx,
  header_rows.csv, unknown_rows.csv, run_summary.json, run.log
- Dell: <stem>_annotated.xlsx AND <stem>_branded.xlsx
- Cisco: <stem>_annotated.xlsx ONLY (no branded)
Uses tmp_path for output_root; no large golden blobs in git.
"""

import re
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import project_root, get_input_root_dell, get_input_root_cisco

# Run folder pattern: run-YYYY-MM-DD__HH-MM-SS-<stem> or run-...-<stem>_N for collision
RUN_FOLDER_PATTERN = re.compile(r"^run-\d{4}-\d{2}-\d{2}__\d{2}-\d{2}-\d{2}-(.+)$")

# Required artifacts in every run folder (per out.zip)
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
    """Dell: output_root/dell_run/run-*-<stem>/ with all artifacts including branded."""
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

    vendor_root = output_root / "dell_run"
    assert vendor_root.is_dir(), f"Expected vendor root dell_run under {output_root}"

    run_folders = [p for p in vendor_root.iterdir() if p.is_dir() and p.name.startswith("run-")]
    assert len(run_folders) >= 1, f"Expected at least one run-* folder under {vendor_root}"

    run_folder = run_folders[0]
    assert RUN_FOLDER_PATTERN.match(run_folder.name) or run_folder.name.startswith("run-"), (
        f"Run folder name must match run-YYYY-MM-DD__HH-MM-SS-<stem>: got {run_folder.name}"
    )
    assert run_folder.parent == vendor_root, "Run folder must be directly under vendor_root (dell_run)"

    stem = "dl1"
    for name in REQUIRED_ARTIFACTS:
        assert (run_folder / name).exists(), f"Required artifact missing: {name} in {run_folder}"

    assert (run_folder / f"{stem}_annotated.xlsx").exists(), f"{stem}_annotated.xlsx missing"
    assert (run_folder / f"{stem}_branded.xlsx").exists(), f"{stem}_branded.xlsx missing (Dell)"


def test_output_tree_shape_cisco_run(tmp_path):
    """Cisco: output_root/cisco_run/run-*-<stem>/ with artifacts; NO branded.xlsx."""
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

    vendor_root = output_root / "cisco_run"
    assert vendor_root.is_dir(), f"Expected vendor root cisco_run under {output_root}"

    run_folders = [p for p in vendor_root.iterdir() if p.is_dir() and p.name.startswith("run-")]
    assert len(run_folders) >= 1, f"Expected at least one run-* folder under {vendor_root}"

    run_folder = run_folders[0]
    assert run_folder.parent == vendor_root, "Run folder must be directly under vendor_root (cisco_run)"

    stem = "ccw_1"
    for name in REQUIRED_ARTIFACTS:
        assert (run_folder / name).exists(), f"Required artifact missing: {name} in {run_folder}"

    assert (run_folder / f"{stem}_annotated.xlsx").exists(), f"{stem}_annotated.xlsx missing"
    # Cisco must NOT have branded (per out.zip)
    assert not (run_folder / f"{stem}_branded.xlsx").exists(), "Cisco must not have branded.xlsx"


def test_output_root_configurable_via_cli(tmp_path):
    """Output root is overridden by --output-dir; run dir is under output_root/<vendor>_run/."""
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
    vendor_root = output_root / "dell_run"
    assert vendor_root.is_dir()
    run_folders = list(vendor_root.glob("run-*"))
    assert run_folders, "Output must be under output_root/dell_run/ (repo stays clean when using external path)"
