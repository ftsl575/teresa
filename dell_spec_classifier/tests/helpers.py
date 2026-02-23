"""
Shared test helpers for pipeline execution. Imported by test_regression.py and test_unknown_threshold.py.
"""

from pathlib import Path

from src.core.parser import parse_excel
from src.core.normalizer import normalize_row
from src.rules.rules_engine import RuleSet
from src.core.classifier import classify_row


def run_pipeline_in_memory(input_path: Path, rules_path: Path) -> tuple[list, list]:
    """Run parse → normalize → classify in memory. Returns (normalized_rows, classification_results). No disk I/O."""
    raw_rows = parse_excel(str(input_path))
    normalized = [normalize_row(r) for r in raw_rows]
    ruleset = RuleSet.load(str(rules_path))
    results = [classify_row(r, ruleset) for r in normalized]
    return (normalized, results)


def build_golden_rows(normalized_rows: list, classification_results: list) -> list[dict]:
    """Build golden-format dicts from pipeline results. Matches golden JSONL schema."""
    out = []
    for row, result in zip(normalized_rows, classification_results):
        out.append({
            "source_row_index": row.source_row_index,
            "row_kind": result.row_kind.value,
            "entity_type": result.entity_type.value if result.entity_type else None,
            "state": result.state.value if result.state else None,
            "matched_rule_id": result.matched_rule_id,
            "device_type": getattr(result, "device_type", None),
            "skus": list(row.skus),
        })
    return out
