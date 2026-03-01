"""
Smoke test for annotated source Excel export.
Uses robust header detection so annotated files with a preamble (e.g. Solution Info) are parsed correctly.
"""

import pytest
import pandas as pd
from pathlib import Path

from main import _get_adapter
from src.rules.rules_engine import RuleSet
from src.core.classifier import classify_row
from src.outputs.annotated_writer import generate_annotated_source_excel

from conftest import project_root
from tests.helpers import find_annotated_header_row, read_annotated_excel


def test_annotated_excel_exists_same_rows_has_entity_type_state_and_item_values(tmp_path):
    """Run pipeline on dl1.xlsx, generate annotated Excel; assert file exists, row count matches, has Entity Type/State columns, ITEM rows filled."""
    root = project_root()
    input_path = root / "test_data" / "dl1.xlsx"
    if not input_path.exists():
        pytest.skip(f"test_data/dl1.xlsx not found at {input_path}")

    adapter = _get_adapter("dell", {})
    raw_rows, header_row_index = adapter.parse(str(input_path))
    normalized_rows = adapter.normalize(raw_rows)
    ruleset = RuleSet.load(str(root / "rules" / "dell_rules.yaml"))
    classification_results = [classify_row(r, ruleset) for r in normalized_rows]

    out_path = generate_annotated_source_excel(
        raw_rows, normalized_rows, classification_results, input_path, tmp_path,
        header_row_index=header_row_index,
    )

    assert out_path.exists(), "annotated workbook should exist"
    assert out_path.name == f"{input_path.stem}_annotated.xlsx"

    df_orig = pd.read_excel(input_path, header=None, engine="openpyxl")
    header_row_index, df_ann = read_annotated_excel(out_path)

    # Row count: annotated has same total rows as original; df_ann is header + data, so data rows = total - header - 1
    expected_data_rows = len(df_orig) - header_row_index - 1
    assert len(df_ann) == expected_data_rows, (
        f"Data row count must match: expected {expected_data_rows}, got {len(df_ann)}"
    )
    for col in ("Entity Type", "State", "device_type", "hw_type"):
        assert col in df_ann.columns, f"Annotated file must have column {col!r}"
    # At least one ITEM row has non-empty Entity Type (e.g. BASE, HW)
    non_empty = df_ann["Entity Type"].dropna().astype(str).str.strip()
    non_empty = non_empty[(non_empty != "") & (non_empty != "Entity Type")]
    assert len(non_empty) > 0, "At least one ITEM row should have Entity Type filled"


def test_annotated_header_row_detection_with_preamble(tmp_path):
    """Regression: annotated xlsx with preamble (e.g. dl4) — parser must find header and read by Option ID."""
    root = project_root()
    input_path = root / "test_data" / "dl4.xlsx"
    if not input_path.exists():
        pytest.skip(f"test_data/dl4.xlsx not found at {input_path}")

    adapter = _get_adapter("dell", {})
    raw_rows, header_row_index = adapter.parse(str(input_path))
    normalized_rows = adapter.normalize(raw_rows)
    ruleset = RuleSet.load(str(root / "rules" / "dell_rules.yaml"))
    classification_results = [classify_row(r, ruleset) for r in normalized_rows]

    out_path = generate_annotated_source_excel(
        raw_rows, normalized_rows, classification_results, input_path, tmp_path,
        header_row_index=header_row_index,
    )

    header_row_index = find_annotated_header_row(out_path)
    assert header_row_index is not None, "Header row must be found in annotated file"
    _, df = read_annotated_excel(out_path)
    assert "Option ID" in df.columns, "Option ID column must be present"
    assert "Entity Type" in df.columns and "hw_type" in df.columns

    # Spot-check: read a row by Option ID (e.g. GBEZWO8) — no KeyError
    option_col = df["Option ID"].astype(str).str.strip()
    row = df[option_col == "GBEZWO8"]
    assert len(row) >= 1, "Expected at least one row with Option ID GBEZWO8"
    first = row.iloc[0]
    assert first["Entity Type"] in ("HW", "BASE", "CONFIG", "LOGISTIC", "NOTE", "SOFTWARE", "SERVICE"), (
        "Entity Type should be a known type"
    )
