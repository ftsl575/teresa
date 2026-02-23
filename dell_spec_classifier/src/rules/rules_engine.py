"""
Rules engine: load Dell rules from YAML and match rows against entity rules.
"""

import re
from pathlib import Path
from typing import List, Optional

import yaml

from src.core.normalizer import NormalizedRow


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
        if field == "module_name":
            value = row.module_name or ""
        elif field == "option_name":
            value = row.option_name or ""
        else:
            continue
        if re.search(pattern, str(value), re.IGNORECASE):
            return rule
    return None


class RuleSet:
    """
    Loaded Dell classification rules from YAML.
    Exposes state_rules list and entity rule lists (base_rules, service_rules, ...).
    """

    def __init__(self, data: dict):
        self._data = data
        sr = self._data.get("state_rules") or {}
        self._state_rules_list: List[dict] = sr.get("absent_keywords") or []
        self.base_rules: List[dict] = self._data.get("base_rules") or []
        self.service_rules: List[dict] = self._data.get("service_rules") or []
        self.logistic_rules: List[dict] = self._data.get("logistic_rules") or []
        self.software_rules: List[dict] = self._data.get("software_rules") or []
        self.note_rules: List[dict] = self._data.get("note_rules") or []
        self.config_rules: List[dict] = self._data.get("config_rules") or []
        self.hw_rules: List[dict] = self._data.get("hw_rules") or []

    def get_state_rules(self) -> List[dict]:
        """Return the list of state rules (absent_keywords) for detect_state."""
        return self._state_rules_list

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
