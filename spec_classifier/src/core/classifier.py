"""
Row classifier: entity type (BASE, HW, SERVICE, ...) from rules.
HEADER rows are skipped; ITEM rows follow priority order.
"""

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import List, Optional

from src.core.normalizer import NormalizedRow, RowKind
from src.core.state_detector import State, detect_state
from src.rules.rules_engine import RuleSet, match_rule, match_device_type_rule, match_hw_type_rule


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


HW_TYPE_VOCAB = frozenset({
    # Основное изделие (BASE rows)
    "server", "switch", "storage_system", "wireless_ap",
    # Вычислительные компоненты
    "cpu", "memory", "gpu",
    # Подсистема хранения
    "storage_drive", "storage_controller", "hba", "backplane", "io_module",
    # Сеть
    "network_adapter", "transceiver", "cable",
    # Питание
    "psu",
    # Охлаждение
    "fan", "heatsink",
    # Расширение и механика
    "riser", "chassis", "rail", "blank_filler",
    # Управление
    "management", "tpm",
    # Аксессуары
    "accessory",
})


@dataclass
class ClassificationResult:
    """Result of classifying one row."""

    row_kind: RowKind
    entity_type: Optional[EntityType]
    state: Optional[State]
    matched_rule_id: str
    device_type: Optional[str] = None
    hw_type: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


def classify_row(row: NormalizedRow, ruleset: RuleSet) -> ClassificationResult:
    """
    Classify a normalized row: HEADER → skip; ITEM → priority: BASE → SERVICE
    → LOGISTIC → SOFTWARE → NOTE → CONFIG → HW → UNKNOWN.
    For ITEM rows with entity_type HW or LOGISTIC, run second pass to set device_type.
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
        result = ClassificationResult(
            row_kind=RowKind.ITEM,
            entity_type=EntityType.BASE,
            state=State.PRESENT,
            matched_rule_id=match["rule_id"],
        )
        result = _apply_device_type(row, result, ruleset)
        return _apply_hw_type(row, result, ruleset)

    match = match_rule(row, ruleset.service_rules)
    if match:
        result = ClassificationResult(
            row_kind=RowKind.ITEM,
            entity_type=EntityType.SERVICE,
            state=state,
            matched_rule_id=match["rule_id"],
        )
        result = _apply_device_type(row, result, ruleset)
        return _apply_hw_type(row, result, ruleset)

    match = match_rule(row, ruleset.logistic_rules)
    if match:
        result = ClassificationResult(
            row_kind=RowKind.ITEM,
            entity_type=EntityType.LOGISTIC,
            state=state,
            matched_rule_id=match["rule_id"],
        )
        result = _apply_device_type(row, result, ruleset)
        return _apply_hw_type(row, result, ruleset)

    match = match_rule(row, ruleset.software_rules)
    if match:
        result = ClassificationResult(
            row_kind=RowKind.ITEM,
            entity_type=EntityType.SOFTWARE,
            state=state,
            matched_rule_id=match["rule_id"],
        )
        result = _apply_device_type(row, result, ruleset)
        return _apply_hw_type(row, result, ruleset)

    match = match_rule(row, ruleset.note_rules)
    if match:
        result = ClassificationResult(
            row_kind=RowKind.ITEM,
            entity_type=EntityType.NOTE,
            state=State.PRESENT,
            matched_rule_id=match["rule_id"],
        )
        result = _apply_device_type(row, result, ruleset)
        return _apply_hw_type(row, result, ruleset)

    match = match_rule(row, ruleset.config_rules)
    if match:
        result = ClassificationResult(
            row_kind=RowKind.ITEM,
            entity_type=EntityType.CONFIG,
            state=state,
            matched_rule_id=match["rule_id"],
        )
        result = _apply_device_type(row, result, ruleset)
        return _apply_hw_type(row, result, ruleset)

    match = match_rule(row, ruleset.hw_rules)
    if match:
        result = ClassificationResult(
            row_kind=RowKind.ITEM,
            entity_type=EntityType.HW,
            state=state,
            matched_rule_id=match["rule_id"],
        )
        result = _apply_device_type(row, result, ruleset)
        return _apply_hw_type(row, result, ruleset)

    result = ClassificationResult(
        row_kind=RowKind.ITEM,
        entity_type=EntityType.UNKNOWN,
        state=state,
        matched_rule_id="UNKNOWN-000",
        warnings=["No matching rule found"],
    )
    return _apply_hw_type(row, result, ruleset)


def _apply_device_type(row: NormalizedRow, result: ClassificationResult, ruleset: RuleSet) -> ClassificationResult:
    """
    Second pass: for ITEM rows with entity_type in device_type_rules.applies_to
    and matched_rule_id != UNKNOWN-000, set device_type from first matching rule.
    """
    if result.entity_type is None or result.matched_rule_id == "UNKNOWN-000":
        return result
    if result.entity_type.value not in ruleset.device_type_applies_to:
        return result
    match = match_device_type_rule(row, ruleset.device_type_rules)
    if match and match.get("device_type"):
        return replace(result, device_type=match["device_type"])
    return result


def _apply_hw_type(
    row: NormalizedRow,
    result: ClassificationResult,
    ruleset: RuleSet,
) -> ClassificationResult:
    """
    Third pass: compute hw_type for HW rows.
    Priority: device_type_map > rule_id_map > regex rules > null.
    Only applies to entity_types in hw_type_rules.applies_to.
    """
    if result.entity_type is None or result.matched_rule_id == "UNKNOWN-000":
        return result
    if result.entity_type.value not in ruleset.hw_type_applies_to:
        return result

    # Layer 1: device_type → hw_type
    if result.device_type and result.device_type in ruleset.hw_type_device_type_map:
        return replace(result, hw_type=ruleset.hw_type_device_type_map[result.device_type])

    # Layer 2: rule_id → hw_type
    if result.matched_rule_id in ruleset.hw_type_rule_id_map:
        return replace(result, hw_type=ruleset.hw_type_rule_id_map[result.matched_rule_id])

    # Layer 3: regex rules (first match wins)
    match = match_hw_type_rule(row, ruleset.hw_type_rules)
    if match and match.get("hw_type"):
        return replace(result, hw_type=match["hw_type"])

    if result.entity_type and result.entity_type.value in ruleset.hw_type_applies_to:
        return replace(result, warnings=result.warnings + ["hw_type unresolved for HW row"])
    return result
