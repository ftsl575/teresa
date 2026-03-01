"""
Unit tests for cleaned spec Excel generation.
"""

import pytest
import pandas as pd
import yaml
from pathlib import Path

from main import _get_adapter
from src.rules.rules_engine import RuleSet
from src.core.classifier import classify_row
from src.core.normalizer import RowKind
from src.core.state_detector import State
from src.outputs.excel_writer import generate_cleaned_spec

from conftest import project_root


@pytest.fixture
def config():
    root = project_root()
    config_path = root / "config.yaml"
    if config_path.exists():
        with open(config_path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {
        "cleaned_spec": {
            "include_types": ["BASE", "HW", "SOFTWARE", "SERVICE"],
            "include_only_present": True,
            "exclude_headers": True,
        }
    }


def test_excel_writer_file_exists_no_headers_only_include_types_and_present(config, tmp_path):
    """Run pipeline on dl1.xlsx, generate cleaned spec; assert file exists, no HEADER, only include_types, only PRESENT."""
    root = project_root()
    input_path = root / "test_data" / "dl1.xlsx"
    if not input_path.exists():
        pytest.skip(f"test_data/dl1.xlsx not found at {input_path}")

    adapter = _get_adapter("dell", {})
    rows_raw, _ = adapter.parse(str(input_path))
    rows_normalized = adapter.normalize(rows_raw)
    ruleset = RuleSet.load(str(root / "rules" / "dell_rules.yaml"))
    classification_results = [classify_row(r, ruleset) for r in rows_normalized]

    out_path = generate_cleaned_spec(rows_normalized, classification_results, config, tmp_path)

    assert out_path.exists(), "cleaned_spec.xlsx should exist"
    assert out_path.name == "cleaned_spec.xlsx"

    df = pd.read_excel(out_path, engine="openpyxl")

    include_types = set(config["cleaned_spec"]["include_types"])
    assert "Entity Type" in df.columns
    assert "State" in df.columns

    # No HEADER rows (all rows in Excel are ITEM by construction)
    assert not (df.get("Entity Type") == "HEADER").any(), "Excel must not contain HEADER rows"
    # All entity_type in include_types
    assert set(df["Entity Type"].dropna().unique()).issubset(include_types), (
        "All Entity Type values must be in include_types"
    )
    # No state != PRESENT
    if "State" in df.columns and config["cleaned_spec"].get("include_only_present", True):
        assert (df["State"] == "PRESENT").all(), "All rows must have State == PRESENT"
