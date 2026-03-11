"""Tests for YAML rules schema — structural checks, not format enforcement."""

import yaml
import pytest
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_RULES_FILES = list((_ROOT / "rules").glob("*_rules.yaml"))
_VALID_ENTITIES = {"BASE", "HW", "CONFIG", "SOFTWARE", "SERVICE", "LOGISTIC", "NOTE", "UNKNOWN"}

_ENTITY_SECTIONS = (
    "base_rules", "service_rules", "logistic_rules",
    "software_rules", "note_rules", "config_rules", "hw_rules",
)


def _load_yaml(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _collect_all_rules(data):
    """Yield (section, rule) for every rule dict with rule_id."""
    for section in _ENTITY_SECTIONS:
        for rule in (data.get(section) or []):
            if isinstance(rule, dict):
                yield section, rule
    dtr = data.get("device_type_rules") or {}
    for rule in (dtr.get("rules") or []):
        if isinstance(rule, dict):
            yield "device_type_rules", rule
    # hw_type_rules may have rules list too
    htr = data.get("hw_type_rules") or {}
    for rule in (htr.get("rules") or []):
        if isinstance(rule, dict):
            yield "hw_type_rules", rule
    # state_rules
    sr = data.get("state_rules") or {}
    for sub in ("absent_keywords", "present_override_keywords"):
        for rule in (sr.get(sub) or []):
            if isinstance(rule, dict):
                yield f"state_rules.{sub}", rule


@pytest.fixture(params=[str(p) for p in _RULES_FILES], ids=[p.stem for p in _RULES_FILES])
def rules_data(request):
    return _load_yaml(request.param), request.param


def test_all_rule_ids_are_well_formed(rules_data):
    """Every rule_id must be uppercase, dash-separated, contain a 3-digit number."""
    import re
    data, filepath = rules_data
    bad = []
    for section, rule in _collect_all_rules(data):
        rid = rule.get("rule_id", "")
        if not rid:
            continue
        # Basic structural checks:
        # 1. All uppercase + digits + dashes only
        if not re.match(r"^[A-Z0-9-]+$", rid):
            bad.append(f"{section}: '{rid}' contains invalid characters")
        # 2. Must contain at least one 3-digit group
        if not re.search(r"\d{3}", rid):
            bad.append(f"{section}: '{rid}' missing 3-digit number")
        # 3. No empty segments (double dashes)
        if "--" in rid:
            bad.append(f"{section}: '{rid}' has empty segment (--)")
    assert not bad, f"Malformed rule_ids in {filepath}:\n" + "\n".join(bad)


def test_all_entity_types_are_valid(rules_data):
    """Every entity_type in rules must be a known enum value."""
    data, filepath = rules_data
    bad = []
    for section, rule in _collect_all_rules(data):
        et = rule.get("entity_type", "")
        if et and et not in _VALID_ENTITIES:
            bad.append(f"{section}: rule_id={rule.get('rule_id')} entity_type={et}")
    assert not bad, f"Invalid entity_types in {filepath}: {bad}"


def test_device_type_applies_to_valid(rules_data):
    """device_type_rules.applies_to must contain only valid entity_type values."""
    data, filepath = rules_data
    dtr = data.get("device_type_rules") or {}
    applies = dtr.get("applies_to") or []
    bad = [a for a in applies if a not in _VALID_ENTITIES]
    assert not bad, f"Invalid applies_to in device_type_rules ({filepath}): {bad}"


def test_hw_type_applies_to_valid(rules_data):
    """hw_type_rules.applies_to must contain only valid entity_type values."""
    data, filepath = rules_data
    htr = data.get("hw_type_rules") or {}
    applies = htr.get("applies_to") or []
    bad = [a for a in applies if a not in _VALID_ENTITIES]
    assert not bad, f"Invalid applies_to in hw_type_rules ({filepath}): {bad}"


def test_no_duplicate_rule_ids(rules_data):
    """No duplicate rule_id within the same rule namespace.

    Entity sections (base/service/logistic/…/hw_rules) share one namespace.
    device_type_rules and hw_type_rules are separate namespaces.
    Cross-namespace reuse (e.g. same rule_id in hw_rules and device_type_rules)
    is intentional: it links entity classification to type-enrichment passes.
    """
    data, filepath = rules_data

    _ENTITY_SECTION_SET = set(_ENTITY_SECTIONS)

    namespaces: dict[str, dict] = {"entity": {}, "device_type_rules": {}, "hw_type_rules": {}}

    for section, rule in _collect_all_rules(data):
        rid = rule.get("rule_id")
        if not rid:
            continue
        if section in _ENTITY_SECTION_SET:
            ns = "entity"
        elif section == "device_type_rules":
            ns = "device_type_rules"
        elif section == "hw_type_rules":
            ns = "hw_type_rules"
        else:
            continue  # state_rules etc. — no dedup needed

        seen = namespaces[ns]
        if rid in seen:
            pytest.fail(
                f"Duplicate rule_id '{rid}' in namespace '{ns}' ({filepath}): "
                f"first in {seen[rid]}, again in {section}"
            )
        seen[rid] = section
