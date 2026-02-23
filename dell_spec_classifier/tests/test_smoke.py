"""
Smoke test: full pipeline on test_data/dl1.xlsx and assert all diagnostic artifacts exist.
"""

import pytest
from pathlib import Path

from src.core.parser import parse_excel
from src.core.normalizer import normalize_row
from src.rules.rules_engine import RuleSet
from src.core.classifier import classify_row
from src.diagnostics.run_manager import create_run_folder
from src.outputs.json_writer import (
    save_rows_raw,
    save_rows_normalized,
    save_classification,
    save_unknown_rows,
    save_header_rows,
)
from src.diagnostics.stats_collector import collect_stats, save_run_summary


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def test_smoke_full_pipeline_artifacts_created():
    """Parse dl1.xlsx, normalize, classify, create run folder, save all artifacts; assert files exist."""
    root = _project_root()
    input_path = root / "test_data" / "dl1.xlsx"
    if not input_path.exists():
        pytest.skip(f"test_data/dl1.xlsx not found at {input_path}")

    rules_path = root / "rules" / "dell_rules.yaml"
    assert rules_path.exists(), f"rules/dell_rules.yaml not found at {rules_path}"

    output_base = root / "output"

    rows_raw = parse_excel(str(input_path))
    rows_normalized = [normalize_row(r) for r in rows_raw]
    ruleset = RuleSet.load(str(rules_path))
    classification_results = [classify_row(r, ruleset) for r in rows_normalized]

    run_folder = create_run_folder(str(output_base), input_path.name)
    assert run_folder.exists()

    save_rows_raw(rows_raw, run_folder)
    save_rows_normalized(rows_normalized, run_folder)
    save_classification(classification_results, run_folder)
    save_unknown_rows(rows_normalized, classification_results, run_folder)
    save_header_rows(rows_normalized, run_folder)

    stats = collect_stats(classification_results)
    save_run_summary(stats, run_folder)

    required_files = [
        "rows_raw.json",
        "rows_normalized.json",
        "classification.jsonl",
        "unknown_rows.csv",
        "header_rows.csv",
        "run_summary.json",
    ]
    for name in required_files:
        path = run_folder / name
        assert path.exists(), f"Expected artifact {name} at {path}"
        assert path.stat().st_size >= 0, f"File {name} should be readable"
