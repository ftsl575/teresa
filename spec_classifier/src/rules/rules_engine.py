"""
Rules engine: load classification rules from YAML and match rows against entity rules.
"""

import logging
import re
from pathlib import Path
from typing import List, Optional

import yaml

from src.core.normalizer import NormalizedRow

_log = logging.getLogger(__name__)

_KNOWN_FIELDS = frozenset({
    "module_name", "option_name", "sku",
    "is_bundle_root", "service_duration_months",
})


def _get_field_value(row, field: str):
    """
    Extract field value from NormalizedRow (or duck-type compatible) for rule matching.

    Returns:
      str value — for known fields (may be empty string if value absent)
      None — for UNKNOWN fields (caller must skip the rule)
    """
    if field == "module_name":
        return str(row.module_name or "")
    elif field == "option_name":
        return str(row.option_name or "")
    elif field == "sku":
        return str(row.skus[0]) if row.skus else ""
    elif field == "is_bundle_root":
        val = getattr(row, "is_bundle_root", None)
        if val is None:
            return ""
        return "true" if val else "false"
    elif field == "service_duration_months":
        val = getattr(row, "service_duration_months", None)
        return str(val) if val is not None else ""
    else:
        _log.warning("Unknown field in rule: %s — rule will be skipped", field)
        return None


def match_rule(row: NormalizedRow, rules: List[dict]) -> Optional[dict]:
    """
    Match a normalized row against a list of entity rules (field + regex).

    Uses field (module_name or option_name), matches pattern case-insensitively.
    Returns the first matching rule dict (with rule_id, entity_type, etc.) or None.
    """
    if not rules:
        return None
    for rule in rules:
        field = rule.get("field")
        pattern = rule.get("pattern")
        if not field or not pattern:
            continue
        value = _get_field_value(row, field)
        if value is None:
            continue
        if re.search(pattern, str(value), re.IGNORECASE):
            return rule
    return None


def match_device_type_rule(row: NormalizedRow, rules: List[dict]) -> Optional[dict]:
    """
    Match a normalized row against device_type_rules (same field + regex).
    Returns the first matching rule dict (device_type, rule_id) or None.
    """
    if not rules:
        return None
    for rule in rules:
        field = rule.get("field")
        pattern = rule.get("pattern")
        if not field or not pattern:
            continue
        value = _get_field_value(row, field)
        if value is None:
            continue
        if re.search(pattern, str(value), re.IGNORECASE):
            return rule
    return None


def match_hw_type_rule(row: NormalizedRow, rules: List[dict]) -> Optional[dict]:
    """Match row against hw_type regex rules. First match wins."""
    if not rules:
        return None
    for rule in rules:
        field = rule.get("field")
        pattern = rule.get("pattern")
        if not field or not pattern:
            continue
        value = _get_field_value(row, field)
        if value is None:
            continue
        if re.search(pattern, str(value), re.IGNORECASE):
            return rule
    return None


class RuleSet:
    """
    Loaded classification rules from a vendor YAML file.
    Exposes state_rules list and entity rule lists (base_rules, service_rules, ...).
    """

    def __init__(self, data: dict):
        self._data = data
        sr = self._data.get("state_rules") or {}
        self._state_rules_list: List[dict] = sr.get("absent_keywords") or []
        self._state_override_list: List[dict] = sr.get("present_override_keywords") or []
        self.base_rules: List[dict] = self._data.get("base_rules") or []
        self.service_rules: List[dict] = self._data.get("service_rules") or []
        self.logistic_rules: List[dict] = self._data.get("logistic_rules") or []
        self.software_rules: List[dict] = self._data.get("software_rules") or []
        self.note_rules: List[dict] = self._data.get("note_rules") or []
        self.config_rules: List[dict] = self._data.get("config_rules") or []
        self.hw_rules: List[dict] = self._data.get("hw_rules") or []

        dtr = self._data.get("device_type_rules") or {}
        self.device_type_rules: List[dict] = dtr.get("rules") or []
        applies = dtr.get("applies_to") or []
        self.device_type_applies_to = set(applies) if isinstance(applies, list) else set()

        htr = self._data.get("hw_type_rules") or {}
        self.hw_type_rules: List[dict] = htr.get("rules") or []
        self.hw_type_device_type_map: dict = htr.get("device_type_map") or {}
        self.hw_type_rule_id_map: dict = htr.get("rule_id_map") or {}
        ht_applies = htr.get("applies_to") or []
        self.hw_type_applies_to = set(ht_applies) if isinstance(ht_applies, list) else set()

    def get_state_rules(self):
        """Return (absent_keywords, present_override_keywords) for detect_state."""
        return (self._state_rules_list, self._state_override_list)

    def get_state_override_rules(self) -> List[dict]:
        return self._state_override_list

    @property
    def version(self) -> str:
        return self._data.get("version") or "0.0.0"

    @classmethod
    def load(cls, filepath: str) -> "RuleSet":
        """Load rules from a YAML file (UTF-8)."""
        path = Path(filepath)
        if not path.is_absolute():
            # Allow relative to cwd or to package
            path = path.resolve()
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not data:
            data = {}
        return cls(data)
