"""
CLI smoke test: run main.py via subprocess and assert exit code, stdout, and artifacts.
Uses tmp_path for output so the repo stays code-only.
"""

import subprocess
import sys
from pathlib import Path

import pytest

from conftest import project_root, get_input_root_dell


def test_cli_exit_code_stdout_artifacts(tmp_path):
    """Run main.py with dl1.xlsx; assert exit 0, stdout has total_rows, run folder has cleaned_spec.xlsx and run_summary.json."""
    root = project_root()
    input_xlsx = get_input_root_dell() / "dl1.xlsx"
    if not input_xlsx.exists():
        pytest.skip(f"Input not found: {input_xlsx} (set paths.input_root in config.local.yaml)")

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

    split_folder = output_dir / "SPLIT" / "dell" / "dl1"
    assert split_folder.is_dir(), f"SPLIT/dell/dl1 folder must exist under {output_dir}"
    assert (split_folder / "cleaned_spec.xlsx").exists(), f"cleaned_spec.xlsx missing in {split_folder}"
    assert (split_folder / "run_summary.json").exists(), f"run_summary.json missing in {split_folder}"
