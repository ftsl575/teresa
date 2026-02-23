"""
Smoke test for annotated source Excel export.
"""

import pytest
import pandas as pd
from pathlib import Path

from src.core.parser import parse_excel
from src.core.normalizer import normalize_row
from src.rules.rules_engine import RuleSet
from src.core.classifier import classify_row
from src.outputs.annotated_writer import generate_annotated_source_excel

from conftest import project_root


def test_annotated_excel_exists_same_rows_has_entity_type_state_and_item_values(tmp_path):
    """Run pipeline on dl1.xlsx, generate annotated Excel; assert file exists, row count matches, has Entity Type/State columns, ITEM rows filled."""
    root = project_root()
    input_path = root / "test_data" / "dl1.xlsx"
    if not input_path.exists():
        pytest.skip(f"test_data/dl1.xlsx not found at {input_path}")

    raw_rows = parse_excel(str(input_path))
    normalized_rows = [normalize_row(r) for r in raw_rows]
    ruleset = RuleSet.load(str(root / "rules" / "dell_rules.yaml"))
    classification_results = [classify_row(r, ruleset) for r in normalized_rows]

    out_path = generate_annotated_source_excel(
        raw_rows, normalized_rows, classification_results, input_path, tmp_path
    )

    assert out_path.exists(), "annotated_source.xlsx should exist"
    assert out_path.name == "annotated_source.xlsx"

    df_orig = pd.read_excel(input_path, header=None, engine="openpyxl")
    df_ann = pd.read_excel(out_path, header=None, engine="openpyxl")

    assert len(df_ann) == len(df_orig), (
        f"Row count must match original: expected {len(df_orig)}, got {len(df_ann)}"
    )
    assert df_ann.shape[1] == df_orig.shape[1] + 2, (
        "Annotated file must have two extra columns (Entity Type, State)"
    )
    # Last two columns are Entity Type and State
    entity_col = df_ann.iloc[:, -2].astype(str).str.strip()
    state_col = df_ann.iloc[:, -1].astype(str).str.strip()
    # Header row contains "Entity Type" and "State" in those columns
    assert (entity_col == "Entity Type").any(), "Entity Type column header must appear"
    assert (state_col == "State").any(), "State column header must appear"
    # At least one ITEM row has non-empty Entity Type (e.g. BASE, HW)
    non_empty = entity_col[(entity_col != "") & (entity_col != "Entity Type")]
    assert len(non_empty) > 0, "At least one ITEM row should have Entity Type filled"
