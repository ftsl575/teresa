"""
State detection for Dell specification rows (PRESENT / ABSENT / DISABLED).
Uses regex patterns from rules; default is PRESENT.
"""

import re
from enum import Enum
from typing import List, Optional


class State(Enum):
    """Row state: present/absent/disabled."""

    PRESENT = "PRESENT"   # Installed / active / enabled
    ABSENT = "ABSENT"     # Not selected / empty
    DISABLED = "DISABLED" # Turned off / disabled


def detect_state(option_name: str, state_rules, state_override_rules: Optional[List[dict]] = None) -> State:
    """
    Determine state from option name using regex patterns from state_rules.

    Each rule is a dict with "pattern" (regex) and "state" (str: ABSENT or DISABLED).
    First matching rule wins; if none match, returns PRESENT.
    If a rule would yield ABSENT and state_override_rules has a matching pattern (e.g. Blank(s)), returns PRESENT.
    state_rules may be a list (absent rules) or a tuple (absent_list, override_list).
    """
    if not option_name:
        return State.PRESENT
    if isinstance(state_rules, tuple) and len(state_rules) == 2:
        state_rules, state_override_rules = state_rules[0], state_rules[1]
    text = str(option_name).strip()
    for rule in state_rules:
        pattern = rule.get("pattern")
        state_str = rule.get("state")
        if not pattern or not state_str:
            continue
        if re.search(pattern, text, re.IGNORECASE):
            if state_str == "ABSENT" and state_override_rules:
                for ov in state_override_rules:
                    if re.search(ov.get("pattern") or "", text, re.IGNORECASE):
                        return State.PRESENT
            try:
                return State(state_str)
            except ValueError:
                continue
    return State.PRESENT
