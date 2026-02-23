"""
Row classifier: entity type (BASE, HW, SERVICE, ...) from rules.
HEADER rows are skipped; ITEM rows follow priority order.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from src.core.normalizer import NormalizedRow, RowKind
from src.core.state_detector import State, detect_state
from src.rules.rules_engine import RuleSet, match_rule


class EntityType(Enum):
    """Entity type for a specification row."""

    BASE = "BASE"
    HW = "HW"
    CONFIG = "CONFIG"
    SOFTWARE = "SOFTWARE"
    SERVICE = "SERVICE"
    LOGISTIC = "LOGISTIC"
    NOTE = "NOTE"
    UNKNOWN = "UNKNOWN"


@dataclass
class ClassificationResult:
    """Result of classifying one row."""

    row_kind: RowKind
    entity_type: Optional[EntityType]
    state: Optional[State]
    matched_rule_id: str
    warnings: List[str] = field(default_factory=list)


def classify_row(row: NormalizedRow, ruleset: RuleSet) -> ClassificationResult:
    """
    Classify a normalized row: HEADER → skip; ITEM → priority: BASE → SERVICE
    → LOGISTIC → SOFTWARE → NOTE → CONFIG → HW → UNKNOWN.
    """
    if row.row_kind == RowKind.HEADER:
        return ClassificationResult(
            row_kind=RowKind.HEADER,
            entity_type=None,
            state=None,
            matched_rule_id="HEADER-SKIP",
        )

    state = detect_state(row.option_name, ruleset.get_state_rules())

    match = match_rule(row, ruleset.base_rules)
    if match:
        return ClassificationResult(
            row_kind=RowKind.ITEM,
            entity_type=EntityType.BASE,
            state=State.PRESENT,
            matched_rule_id=match["rule_id"],
        )

    match = match_rule(row, ruleset.service_rules)
    if match:
        return ClassificationResult(
            row_kind=RowKind.ITEM,
            entity_type=EntityType.SERVICE,
            state=state,
            matched_rule_id=match["rule_id"],
        )

    match = match_rule(row, ruleset.logistic_rules)
    if match:
        return ClassificationResult(
            row_kind=RowKind.ITEM,
            entity_type=EntityType.LOGISTIC,
            state=state,
            matched_rule_id=match["rule_id"],
        )

    match = match_rule(row, ruleset.software_rules)
    if match:
        return ClassificationResult(
            row_kind=RowKind.ITEM,
            entity_type=EntityType.SOFTWARE,
            state=state,
            matched_rule_id=match["rule_id"],
        )

    match = match_rule(row, ruleset.note_rules)
    if match:
        return ClassificationResult(
            row_kind=RowKind.ITEM,
            entity_type=EntityType.NOTE,
            state=State.PRESENT,
            matched_rule_id=match["rule_id"],
        )

    match = match_rule(row, ruleset.config_rules)
    if match:
        return ClassificationResult(
            row_kind=RowKind.ITEM,
            entity_type=EntityType.CONFIG,
            state=state,
            matched_rule_id=match["rule_id"],
        )

    match = match_rule(row, ruleset.hw_rules)
    if match:
        return ClassificationResult(
            row_kind=RowKind.ITEM,
            entity_type=EntityType.HW,
            state=state,
            matched_rule_id=match["rule_id"],
        )

    return ClassificationResult(
        row_kind=RowKind.ITEM,
        entity_type=EntityType.UNKNOWN,
        state=state,
        matched_rule_id="UNKNOWN-000",
        warnings=["No matching rule found"],
    )
