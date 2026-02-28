"""
CLI smoke test: run main.py via subprocess and assert exit code, stdout, and artifacts.
Uses tmp_path for output so the repo stays code-only.
"""

import subprocess
import sys
from pathlib import Path

import pytest

from conftest import project_root


def test_cli_exit_code_stdout_artifacts(tmp_path):
    """Run main.py with dl1.xlsx; assert exit 0, stdout has total_rows, run folder has cleaned_spec.xlsx and run_summary.json."""
    root = project_root()
    input_xlsx = root / "test_data" / "dl1.xlsx"
    if not input_xlsx.exists():
        pytest.skip(f"test_data/dl1.xlsx not found at {input_xlsx}")

    output_dir = tmp_path / "out"
    output_dir.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        [
            sys.executable, "main.py",
            "--input", str(input_xlsx),
            "--config", str(root / "config.yaml"),
            "--output-dir", str(output_dir),
        ],
        cwd=str(root),
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, f"CLI failed: stderr={result.stderr!r}"
    assert "total_rows" in result.stdout, f"Expected 'total_rows' in stdout: {result.stdout!r}"

    vendor_root = output_dir / "dell_run"
    assert vendor_root.exists(), "output_root/dell_run should exist"
    run_folders = list(vendor_root.glob("run-*"))
    assert run_folders, "At least one run-* folder under dell_run should exist"
    latest = max(run_folders, key=lambda p: p.stat().st_mtime)
    assert (latest / "cleaned_spec.xlsx").exists(), f"cleaned_spec.xlsx missing in {latest}"
    assert (latest / "run_summary.json").exists(), f"run_summary.json missing in {latest}"
