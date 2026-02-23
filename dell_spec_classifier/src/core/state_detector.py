"""
State detection for Dell specification rows (PRESENT / ABSENT / DISABLED).
Uses regex patterns from rules; default is PRESENT.
"""

import re
from enum import Enum
from typing import List


class State(Enum):
    """Row state: present/absent/disabled."""

    PRESENT = "PRESENT"   # Installed / active / enabled
    ABSENT = "ABSENT"     # Not selected / empty
    DISABLED = "DISABLED" # Turned off / disabled


def detect_state(option_name: str, state_rules: List[dict]) -> State:
    """
    Determine state from option name using regex patterns from state_rules.

    Each rule is a dict with "pattern" (regex) and "state" (str: ABSENT or DISABLED).
    First matching rule wins; if none match, returns PRESENT.
    """
    if not option_name:
        return State.PRESENT
    text = str(option_name).strip()
    for rule in state_rules:
        pattern = rule.get("pattern")
        state_str = rule.get("state")
        if not pattern or not state_str:
            continue
        if re.search(pattern, text, re.IGNORECASE):
            try:
                return State(state_str)
            except ValueError:
                continue
    return State.PRESENT
