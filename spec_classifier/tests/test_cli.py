"""
CLI smoke test: run main.py via subprocess and assert exit code, stdout, and artifacts.
"""

import subprocess
import sys
from pathlib import Path

from conftest import project_root


def test_cli_exit_code_stdout_artifacts():
    """Run main.py with dl1.xlsx; assert exit 0, stdout has total_rows, run folder has cleaned_spec.xlsx and run_summary.json."""
    root = project_root()
    input_xlsx = root / "test_data" / "dl1.xlsx"
    if not input_xlsx.exists():
        import pytest
        pytest.skip(f"test_data/dl1.xlsx not found at {input_xlsx}")

    result = subprocess.run(
        [sys.executable, "main.py", "--input", str(input_xlsx), "--config", "config.yaml", "--output-dir", "output"],
        cwd=str(root),
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, f"CLI failed: stderr={result.stderr!r}"
    assert "total_rows" in result.stdout, f"Expected 'total_rows' in stdout: {result.stdout!r}"

    output_dir = root / "output"
    assert output_dir.exists(), "output/ should exist"
    run_folders = list(output_dir.glob("run-*"))
    assert run_folders, "At least one output/run-* folder should exist"
    latest = max(run_folders, key=lambda p: p.stat().st_mtime)
    assert (latest / "cleaned_spec.xlsx").exists(), f"cleaned_spec.xlsx missing in {latest}"
    assert (latest / "run_summary.json").exists(), f"run_summary.json missing in {latest}"
