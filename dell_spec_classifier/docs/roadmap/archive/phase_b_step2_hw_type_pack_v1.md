# Phase B Step 2 Implementation Pack — hw_type Field and Resolution Logic

**Project:** Dell Specification Classifier  
**Baseline:** v1.1.1 + Phase B Step 2 commit 1 (`dataclasses.replace` in `_apply_device_type`)  
**Date:** 2026-02-24  
**Revision:** 2 (added Pack 3 and Pack 4 roadmap for outputs and traceability)  
**Author:** Senior Technical Architect (automated)  
**Purpose:** Execution-ready plan for Phase B Step 2 commit 2 — add `hw_type` field to `ClassificationResult` and wire YAML-driven resolution logic

---

## 1. Overview / Motivation

### 1.1 Problem

`ClassificationResult` currently has `entity_type=HW` for all hardware rows, but no sub-categorization. A row classified as HW could be a processor, memory module, power supply, GPU, or any other server component. Downstream consumers (summary reports, analytics, filtering) cannot distinguish hardware categories without parsing `module_name` / `option_name` themselves — duplicating classification logic outside the classifier.

### 1.2 Why hw_type

`device_type` already sub-classifies some HW/LOGISTIC rows, but only those matched by `device_type_rules` (Customer Kit / Install patterns, cables). Most HW rows matched by broad module_name rules (HW-001 through HW-004) have `device_type=None` because they don't match any device_type_rule. These rows represent the majority of hardware components in a typical Dell specification.

`hw_type` fills this gap: it provides a hardware sub-category for **all** HW entity_type rows, based on their `module_name` and `option_name` content. This is a second-pass resolution — identical in pattern to `device_type`, but scoped to HW rows and using a dedicated rule set.

### 1.3 Design: Mirrors device_type Exactly

The implementation follows the established `device_type` pattern precisely:

| Aspect | device_type (existing) | hw_type (new) |
|--------|----------------------|---------------|
| YAML section | `device_type_rules` in `dell_rules.yaml` | `hw_type_rules` in `dell_rules.yaml` |
| YAML structure | `applies_to` + `rules` list | `applies_to` + `rules` list |
| applies_to | `[HW, LOGISTIC]` | `[HW]` |
| Rule format | `field` + `pattern` + `device_type` + `rule_id` | `field` + `pattern` + `hw_type` + `rule_id` |
| Matcher | `match_device_type_rule()` | Reuse `match_rule()` (identical logic) |
| Resolver | `_apply_device_type()` | `_apply_hw_type()` (same pattern) |
| Field on result | `device_type: Optional[str] = None` | `hw_type: Optional[str] = None` |
| Default | `None` (no match) | `None` (no match) |

### 1.4 hw_type Values (Deterministic, YAML-Driven)

Each hw_type value is derived from module_name or option_name regex patterns. First match wins.

| hw_type | Matches (module_name unless noted) | Typical Components |
|---------|------------------------------------|--------------------|
| `processor` | Processor, Additional Processor; option_name: Xeon Customer Kit/Install | CPUs |
| `memory` | Memory Capacity | DIMMs, RAM modules |
| `storage` | Hard Drives, BACKPLANE, FRONT/REAR STORAGE, Boot Optimized Storage, BOSS; option_name: SSD/NVMe/SATA CK | Drives, backplanes, BOSS cards |
| `power_supply` | Power Supply; option_name: PSU Customer Kit | PSUs |
| `network` | Network Cards/Adapters, OCP; option_name: NIC/OCP CK/Install | NICs, OCP adapters |
| `storage_controller` | RAID Controllers; option_name: PERC/HBA/FC | RAID, HBA, Fibre Channel |
| `gpu` | GPU, FPGA, Acceleration | GPUs, FPGAs |
| `cooling` | Fans, Thermal | Fans, heat sinks |
| `expansion` | PCIe, Riser | PCIe slots, risers |
| `security` | TPM, Trusted Platform | TPM modules |
| `chassis` | Chassis Configuration, Bezel, Rack Rails, Server Accessories | Chassis, bezels, rails |
| `cable` | Cables | Internal cables |
| `motherboard` | Motherboard | System boards |
| `management` | Quick Sync, Password, BMC, KVM | Management / KVM |

### 1.5 Interaction with device_type

`hw_type` and `device_type` are **independent**. A row can have both:

- HW row with module_name "Power Supply" → `device_type=None`, `hw_type=power_supply`
- HW row with option_name "750W PSU Customer Kit" → `device_type=psu`, `hw_type=power_supply`
- LOGISTIC row with option_name "Power Cord C13" → `device_type=power_cord`, `hw_type=None`

`hw_type` applies only to entity_type=HW. `device_type` applies to HW and LOGISTIC.

### 1.6 Risk Assessment

**Risk: Low.** The new field defaults to `None`, so all existing code paths that don't reference `hw_type` are unaffected. The `_apply_device_type` function uses `dataclasses.replace` (commit 1), so it automatically preserves `hw_type` when overriding `device_type`. Output serialization (json_writer, stats_collector, golden format) is NOT modified in this commit — `hw_type` exists on ClassificationResult but is not yet surfaced to files or golden comparisons. All existing tests pass unchanged.

### 1.7 Prerequisite Confirmation

Phase B Step 2 commit 1 is verified complete:
- `_apply_device_type` uses `replace(result, device_type=match["device_type"])`
- `replace` is imported from `dataclasses`
- All 80 tests pass

Because `_apply_device_type` uses `dataclasses.replace`, the new `hw_type` field will be automatically preserved through device_type resolution. No further changes to `_apply_device_type` are needed.

---

## 2. Scope

| Item | In Scope | Rationale |
|------|----------|-----------|
| Add `hw_type: Optional[str] = None` field to `ClassificationResult` | ✅ | Core field addition |
| Add `hw_type_rules` section to `dell_rules.yaml` | ✅ | YAML-driven mapping (mirrors device_type_rules) |
| Add `hw_type_rules` / `hw_type_applies_to` loading to `RuleSet` | ✅ | Required by resolver |
| Add `_apply_hw_type()` function to `classifier.py` | ✅ | Second-pass resolver |
| Wire `_apply_hw_type` into `classify_row` after `_apply_device_type` | ✅ | Integration |
| Create `tests/test_hw_type.py` with focused unit tests | ✅ | Validation |
| Modify json_writer / stats_collector / golden format | ❌ | Output format changes are a **separate commit** |
| Regenerate golden files | ❌ | Golden schema unchanged — hw_type not in golden format yet |
| Modify test_regression.py / helpers.py / conftest.py | ❌ | Existing tests unaffected |
| Modify main.py | ❌ | Orchestration unchanged |

---

## 3. Files to Modify / Create

```
rules/dell_rules.yaml        — MODIFY: add hw_type_rules section (append at end of file)
src/rules/rules_engine.py    — MODIFY: add hw_type_rules + hw_type_applies_to loading to RuleSet.__init__
src/core/classifier.py       — MODIFY: add hw_type field, add _apply_hw_type, wire into classify_row
tests/test_hw_type.py        — CREATE: focused unit tests for hw_type assignment
```

### 3.1 What Must NOT Change

- **`_apply_device_type` function.** Commit 1 is preserved exactly as-is.
- **`ClassificationResult` existing fields.** All 6 current fields unchanged; `hw_type` is added after `device_type` and before `warnings`.
- **Golden files.** Zero changes to `golden/*.jsonl`.
- **Output serialization.** `json_writer.py` is untouched — `_classification_result_to_dict` does NOT include `hw_type` yet.
- **Statistics.** `stats_collector.py` is untouched — no `hw_type_counts` yet.
- **Test harness.** `helpers.py`, `conftest.py`, `test_regression.py`, `test_unknown_threshold.py` all untouched.
- **main.py.** Orchestration unchanged.
- **normalizer.py, state_detector.py, parser.py.** Upstream pipeline untouched.
- **Existing entity/state/device_type rules in dell_rules.yaml.** Only new content appended.

---

## 4. Step-by-Step Implementation Instructions

### Step A — Add `hw_type_rules` section to `rules/dell_rules.yaml`

**Append** the following section at the end of the file, after the `device_type_rules` section. Do NOT modify any existing content above.

```yaml
# ============================================================
# HW TYPE (second pass: only for ITEM rows with entity_type HW)
# Categorizes hardware rows into sub-types.
# First match wins. hw_type appears only when entity_type is HW.
# ============================================================
hw_type_rules:
  applies_to: [HW]

  rules:
    # Processor
    - field: module_name
      pattern: '\b(Processor|Additional\s+Processor)\b'
      hw_type: processor
      rule_id: HWT-001

    # Memory
    - field: module_name
      pattern: '\bMemory\s+Capacity\b'
      hw_type: memory
      rule_id: HWT-002

    # Storage (drives, backplane, BOSS)
    - field: module_name
      pattern: '\b(Hard\s+Drives|BACKPLANE|FRONT\s+STORAGE|REAR\s+STORAGE|Boot\s+Optimized\s+Storage|BOSS)\b'
      hw_type: storage
      rule_id: HWT-003

    # Power Supply
    - field: module_name
      pattern: '\bPower\s+Supply\b'
      hw_type: power_supply
      rule_id: HWT-004

    # Network
    - field: module_name
      pattern: '\b(Network\s+(Cards?|Adapters?)|OCP)\b'
      hw_type: network
      rule_id: HWT-005

    # RAID / Storage Controllers
    - field: module_name
      pattern: '\bRAID.*Controllers?\b'
      hw_type: storage_controller
      rule_id: HWT-006

    # GPU / Accelerators
    - field: module_name
      pattern: '\b(GPU|FPGA|Acceleration)\b'
      hw_type: gpu
      rule_id: HWT-007

    # Cooling
    - field: module_name
      pattern: '\b(Fans|Thermal)\b'
      hw_type: cooling
      rule_id: HWT-008

    # Expansion (PCIe, Riser)
    - field: module_name
      pattern: '\b(PCIe|Riser)\b'
      hw_type: expansion
      rule_id: HWT-009

    # Security (TPM)
    - field: module_name
      pattern: '\b(TPM|Trusted\s+Platform)\b'
      hw_type: security
      rule_id: HWT-010

    # Chassis / Mechanical
    - field: module_name
      pattern: '(^Chassis\s+Configuration$|\b(Bezel|Rack\s+Rails|Server\s+Accessories)\b)'
      hw_type: chassis
      rule_id: HWT-011

    # Cables
    - field: module_name
      pattern: '\bCables\b'
      hw_type: cable
      rule_id: HWT-012

    # Motherboard
    - field: module_name
      pattern: '\bMotherboard\b'
      hw_type: motherboard
      rule_id: HWT-013

    # Management
    - field: module_name
      pattern: '\b(Quick\s+Sync|Password|BMC|KVM)\b'
      hw_type: management
      rule_id: HWT-014

    # --- option_name rules for Customer Kit / Install rows ---
    # These rows have generic module_name but specific option_name

    - field: option_name
      pattern: '(?i)(xeon|intel\s+xeon).*(customer\s+install|cus(tomer)?\s+kit|ck)'
      hw_type: processor
      rule_id: HWT-020

    - field: option_name
      pattern: '(?i)(ssd|nvme|sata|hot-plug).*(cus(tomer)?\s+kit|ck)'
      hw_type: storage
      rule_id: HWT-021

    - field: option_name
      pattern: '(?i)power\s+supply.*(cus(tomer)?\s+kit|ck)'
      hw_type: power_supply
      rule_id: HWT-022

    - field: option_name
      pattern: '(?i)(gbe|sfp28|sfp\+|nic|ocp).*(cus(tomer)?\s+(kit|install)|ck)'
      hw_type: network
      rule_id: HWT-023

    - field: option_name
      pattern: '(?i)(hba|perc|fibre\s+channel|fc\s+hba|raid\s+controller).*(dib|ck|full\s+height|low\s+profile)'
      hw_type: storage_controller
      rule_id: HWT-024
```

### Step B — Add `hw_type_rules` loading to `RuleSet` in `src/rules/rules_engine.py`

**Locate** the `__init__` method of `RuleSet`. Find the block that loads `device_type_rules`:

```python
dtr = self._data.get("device_type_rules") or {}
self.device_type_rules: List[dict] = dtr.get("rules") or []
applies = dtr.get("applies_to") or []
self.device_type_applies_to = set(applies) if isinstance(applies, list) else set()
```

**After** that block (before the method ends), **add** the equivalent for hw_type_rules:

```python
htr = self._data.get("hw_type_rules") or {}
self.hw_type_rules: List[dict] = htr.get("rules") or []
hw_applies = htr.get("applies_to") or []
self.hw_type_applies_to = set(hw_applies) if isinstance(hw_applies, list) else set()
```

**No other changes** to `rules_engine.py`. No new functions needed — `match_rule()` already handles the `field + pattern` matching that `hw_type_rules` uses.

### Step C — Add `hw_type` field to `ClassificationResult` in `src/core/classifier.py`

**Locate** the `ClassificationResult` dataclass. Current fields:

```python
@dataclass
class ClassificationResult:
    """Result of classifying one row."""

    row_kind: RowKind
    entity_type: Optional[EntityType]
    state: Optional[State]
    matched_rule_id: str
    device_type: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
```

**Add** `hw_type` after `device_type` and before `warnings`:

```python
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
```

**Position is critical:** `hw_type` must appear after `device_type` (both are `Optional[str] = None`) and before `warnings` (which uses `field(default_factory=list)`). Dataclass field ordering requires fields with defaults to come after fields without defaults.

### Step D — Add `_apply_hw_type` function to `src/core/classifier.py`

**Add** a new function after `_apply_device_type`. It mirrors `_apply_device_type` exactly, substituting `hw_type` for `device_type`:

```python
def _apply_hw_type(row: NormalizedRow, result: ClassificationResult, ruleset: RuleSet) -> ClassificationResult:
    """
    Second pass: for ITEM rows with entity_type in hw_type_rules.applies_to
    and matched_rule_id != UNKNOWN-000, set hw_type from first matching rule.
    """
    if result.entity_type is None or result.matched_rule_id == "UNKNOWN-000":
        return result
    if result.entity_type.value not in ruleset.hw_type_applies_to:
        return result
    match = match_rule(row, ruleset.hw_type_rules)
    if match and match.get("hw_type"):
        return replace(result, hw_type=match["hw_type"])
    return result
```

**Key differences from `_apply_device_type`:**
- Checks `ruleset.hw_type_applies_to` (not `device_type_applies_to`)
- Uses `match_rule` (not `match_device_type_rule`) — they are functionally identical; `match_rule` is the canonical implementation
- Checks `match.get("hw_type")` (not `"device_type"`)
- Sets `hw_type=match["hw_type"]` via `replace`

### Step E — Wire `_apply_hw_type` into `classify_row`

In `classify_row`, every entity type branch currently ends with:

```python
return _apply_device_type(row, result, ruleset)
```

**Replace** each of these 7 return statements with:

```python
result = _apply_device_type(row, result, ruleset)
return _apply_hw_type(row, result, ruleset)
```

This applies to all 7 branches: BASE, SERVICE, LOGISTIC, SOFTWARE, NOTE, CONFIG, HW.

The `_apply_hw_type` function self-filters via `applies_to: [HW]`, so calling it for all entity types is safe — non-HW rows return immediately from the guard clause.

**The UNKNOWN fallback** (`return ClassificationResult(..., entity_type=EntityType.UNKNOWN, ...)`) stays unchanged — UNKNOWN rows do not go through either second pass.

**Do NOT change** the `_apply_device_type` function — it remains exactly as committed in Phase B Step 2 commit 1.

### Step F — Create `tests/test_hw_type.py`

**Create** a new test file `tests/test_hw_type.py` with focused unit tests that validate hw_type assignment. These tests create `NormalizedRow` instances with controlled `module_name` / `option_name` values, call `classify_row`, and assert the expected `hw_type` value.

```python
"""
Unit tests for hw_type assignment on ClassificationResult.
Validates that HW rows receive correct hw_type based on hw_type_rules.
"""

import pytest
from pathlib import Path

from conftest import project_root
from src.core.normalizer import NormalizedRow, RowKind
from src.core.classifier import classify_row, EntityType
from src.rules.rules_engine import RuleSet


@pytest.fixture
def ruleset():
    """Load the production rule set."""
    root = project_root()
    rules_path = root / "rules" / "dell_rules.yaml"
    return RuleSet.load(str(rules_path))


def _make_item_row(module_name: str = "", option_name: str = "") -> NormalizedRow:
    """Build a minimal ITEM NormalizedRow for testing."""
    return NormalizedRow(
        source_row_index=1,
        row_kind=RowKind.ITEM,
        group_name=None,
        group_id=None,
        product_name=None,
        module_name=module_name,
        option_name=option_name,
        option_id=None,
        skus=[],
        qty=1,
        option_price=0.0,
    )


class TestHwTypeModuleNameRules:
    """Test hw_type assignment from module_name patterns."""

    @pytest.mark.parametrize("module_name, expected_hw_type", [
        ("Processor", "processor"),
        ("Additional Processor", "processor"),
        ("Memory Capacity", "memory"),
        ("Hard Drives", "storage"),
        ("Power Supply", "power_supply"),
        ("Network Cards", "network"),
        ("Network Adapters", "network"),
        ("Fans", "cooling"),
        ("Thermal", "cooling"),
        ("PCIe", "expansion"),
        ("Riser", "expansion"),
        ("TPM", "security"),
        ("Trusted Platform", "security"),
        ("Chassis Configuration", "chassis"),
        ("Bezel", "chassis"),
        ("Rack Rails", "chassis"),
        ("Server Accessories", "chassis"),
        ("Cables", "cable"),
        ("Motherboard", "motherboard"),
        ("Quick Sync", "management"),
        ("BMC", "management"),
    ])
    def test_hw_type_from_module_name(self, ruleset, module_name, expected_hw_type):
        row = _make_item_row(module_name=module_name)
        result = classify_row(row, ruleset)
        assert result.entity_type == EntityType.HW, (
            f"Expected HW for module_name={module_name!r}, got {result.entity_type}"
        )
        assert result.hw_type == expected_hw_type, (
            f"Expected hw_type={expected_hw_type!r} for module_name={module_name!r}, got {result.hw_type!r}"
        )


class TestHwTypeOptionNameRules:
    """Test hw_type assignment from option_name patterns (Customer Kit / Install)."""

    @pytest.mark.parametrize("option_name, expected_hw_type", [
        ("Intel Xeon Silver 4410Y Customer Install", "processor"),
        ("1.92TB SSD SATA Read Intensive Customer Kit", "storage"),
        ("800W Power Supply Customer Kit", "power_supply"),
        ("Broadcom 5720 Dual Port 1GbE OCP Customer Kit", "network"),
        ("PERC H965i Front DIB", "storage_controller"),
    ])
    def test_hw_type_from_option_name(self, ruleset, option_name, expected_hw_type):
        row = _make_item_row(option_name=option_name)
        result = classify_row(row, ruleset)
        assert result.entity_type == EntityType.HW, (
            f"Expected HW for option_name={option_name!r}, got {result.entity_type}"
        )
        assert result.hw_type == expected_hw_type, (
            f"Expected hw_type={expected_hw_type!r} for option_name={option_name!r}, got {result.hw_type!r}"
        )


class TestHwTypeNonHwRows:
    """Verify hw_type is None for non-HW entity types."""

    def test_header_row_has_no_hw_type(self, ruleset):
        row = NormalizedRow(
            source_row_index=0,
            row_kind=RowKind.HEADER,
            group_name=None, group_id=None, product_name=None,
            module_name="", option_name="", option_id=None,
            skus=[], qty=0, option_price=0.0,
        )
        result = classify_row(row, ruleset)
        assert result.hw_type is None

    def test_service_row_has_no_hw_type(self, ruleset):
        row = _make_item_row(module_name="ProSupport Plus")
        result = classify_row(row, ruleset)
        assert result.entity_type == EntityType.SERVICE
        assert result.hw_type is None

    def test_logistic_row_has_no_hw_type(self, ruleset):
        row = _make_item_row(module_name="Shipping")
        result = classify_row(row, ruleset)
        assert result.entity_type == EntityType.LOGISTIC
        assert result.hw_type is None

    def test_software_row_has_no_hw_type(self, ruleset):
        row = _make_item_row(module_name="Operating System")
        result = classify_row(row, ruleset)
        assert result.entity_type == EntityType.SOFTWARE
        assert result.hw_type is None

    def test_unknown_row_has_no_hw_type(self, ruleset):
        row = _make_item_row(module_name="", option_name="Some Random Thing XYZ123")
        result = classify_row(row, ruleset)
        assert result.entity_type == EntityType.UNKNOWN
        assert result.hw_type is None


class TestHwTypePreservedByDeviceType:
    """Verify hw_type survives the device_type second pass (dataclasses.replace)."""

    def test_hw_type_preserved_when_device_type_set(self, ruleset):
        """Row with both device_type and hw_type must have both populated."""
        row = _make_item_row(option_name="1.92TB SSD SATA Customer Kit")
        result = classify_row(row, ruleset)
        assert result.entity_type == EntityType.HW
        assert result.device_type is not None, "Expected device_type to be set"
        assert result.hw_type == "storage", (
            f"Expected hw_type='storage', got {result.hw_type!r} — "
            "hw_type may have been lost by _apply_device_type"
        )
```

---

## 5. Constraints

| Constraint | Rationale |
|------------|-----------|
| `_apply_device_type` function is NOT modified | Commit 1 is preserved exactly |
| No output format changes | `json_writer.py` is untouched — `hw_type` is not serialized yet |
| No statistics changes | `stats_collector.py` is untouched — no `hw_type_counts` yet |
| No golden regeneration | Golden format does not include `hw_type`; golden comparisons unaffected |
| No golden format changes | `helpers.py` `build_golden_rows` is untouched |
| No test_regression.py changes | `_compare_row` does not check `hw_type` |
| No main.py changes | Orchestration unchanged |
| Existing entity_type / device_type rules in dell_rules.yaml unchanged | Only append new `hw_type_rules` section |
| `hw_type` defaults to `None` | Non-HW rows and unmatched HW rows are unaffected |
| One atomic PR | Single commit, reviewable diff |

---

## 6. Definition of Done

- [ ] `ClassificationResult` has field `hw_type: Optional[str] = None` after `device_type` and before `warnings`
- [ ] `dell_rules.yaml` has `hw_type_rules` section with `applies_to: [HW]` and 19 rules (HWT-001 through HWT-024)
- [ ] `RuleSet.__init__` loads `hw_type_rules`, `hw_type_applies_to` (parallel to `device_type_rules`)
- [ ] `_apply_hw_type` function exists in `classifier.py` (mirrors `_apply_device_type`)
- [ ] `classify_row` chains `_apply_device_type` → `_apply_hw_type` for all 7 entity type branches
- [ ] `_apply_device_type` function is completely unmodified from commit 1
- [ ] `tests/test_hw_type.py` exists with tests covering: module_name rules, option_name rules, non-HW rows, and hw_type preservation through device_type pass
- [ ] `pytest tests/ -v --tb=short` passes — all existing tests pass, new hw_type tests pass
- [ ] `pytest tests/test_regression.py -v --tb=long` passes — golden comparisons unchanged
- [ ] No changes to: `json_writer.py`, `stats_collector.py`, `helpers.py`, `conftest.py`, `main.py`, `normalizer.py`, `state_detector.py`, `test_regression.py`
- [ ] No changes to golden files

---

## 7. Verification

### 7.1 Verification Commands

```bash
cd dell_spec_classifier

# 1. Verify only expected files changed
git diff --name-only
# Expected:
#   rules/dell_rules.yaml
#   src/core/classifier.py
#   src/rules/rules_engine.py
# New (untracked):
#   tests/test_hw_type.py

# 2. Verify dell_rules.yaml diff is append-only
git diff rules/dell_rules.yaml
# Expected: only additions at end of file (hw_type_rules section), no deletions

# 3. Verify _apply_device_type is unchanged
git diff src/core/classifier.py | grep "_apply_device_type"
# Expected: no lines modified inside _apply_device_type function body

# 4. Run full test suite
pytest tests/ -v --tb=short
# Expected: all existing 80 tests pass + new hw_type tests pass

# 5. Run regression tests specifically (golden comparison)
pytest tests/test_regression.py -v --tb=long
# Expected: all pass, no golden diffs

# 6. Run new hw_type tests specifically
pytest tests/test_hw_type.py -v --tb=long
# Expected: all pass

# 7. Run threshold tests
pytest tests/test_unknown_threshold.py -v
# Expected: all pass, identical ratios (hw_type does not affect entity_type counts)

# 8. Verify output format unchanged
python main.py --input test_data/dl1.xlsx
# Expected: run_summary.json and classification.jsonl do NOT contain hw_type
# (output serialization is a separate commit)
```

### 7.2 Critical Verification: hw_type Preserved Through device_type Pass

The most important correctness check is that `hw_type` is not lost when `_apply_device_type` sets `device_type`. This is guaranteed by commit 1 (`dataclasses.replace`), but verified explicitly:

```bash
pytest tests/test_hw_type.py::TestHwTypePreservedByDeviceType -v --tb=long
# Must pass — proves hw_type survives the device_type second pass
```

If this test fails, it means `_apply_device_type` is NOT using `dataclasses.replace` — commit 1 was not applied correctly. **This is a blocking failure.**

---

## 8. Cursor Prompt

```
Context: Dell Specification Classifier project at dell_spec_classifier/.
Baseline v1.1.1 + Phase B Step 2 commit 1 (dataclasses.replace in _apply_device_type).
All 80 tests passing.
This is Phase B Step 2 commit 2: add hw_type field and resolution logic.

PREREQUISITE ALREADY DONE: _apply_device_type uses dataclasses.replace.
This means any new field on ClassificationResult is automatically preserved
through device_type resolution. Do NOT modify _apply_device_type.

TASK: Add hw_type field to ClassificationResult and wire YAML-driven resolution,
mirroring the existing device_type pattern exactly.

=== FILE 1: rules/dell_rules.yaml (MODIFY — append only) ===

APPEND the following section at the END of the file, after device_type_rules.
Do NOT modify any existing content above.

# ============================================================
# HW TYPE (second pass: only for ITEM rows with entity_type HW)
# Categorizes hardware rows into sub-types.
# First match wins. hw_type appears only when entity_type is HW.
# ============================================================
hw_type_rules:
  applies_to: [HW]

  rules:
    - field: module_name
      pattern: '\b(Processor|Additional\s+Processor)\b'
      hw_type: processor
      rule_id: HWT-001

    - field: module_name
      pattern: '\bMemory\s+Capacity\b'
      hw_type: memory
      rule_id: HWT-002

    - field: module_name
      pattern: '\b(Hard\s+Drives|BACKPLANE|FRONT\s+STORAGE|REAR\s+STORAGE|Boot\s+Optimized\s+Storage|BOSS)\b'
      hw_type: storage
      rule_id: HWT-003

    - field: module_name
      pattern: '\bPower\s+Supply\b'
      hw_type: power_supply
      rule_id: HWT-004

    - field: module_name
      pattern: '\b(Network\s+(Cards?|Adapters?)|OCP)\b'
      hw_type: network
      rule_id: HWT-005

    - field: module_name
      pattern: '\bRAID.*Controllers?\b'
      hw_type: storage_controller
      rule_id: HWT-006

    - field: module_name
      pattern: '\b(GPU|FPGA|Acceleration)\b'
      hw_type: gpu
      rule_id: HWT-007

    - field: module_name
      pattern: '\b(Fans|Thermal)\b'
      hw_type: cooling
      rule_id: HWT-008

    - field: module_name
      pattern: '\b(PCIe|Riser)\b'
      hw_type: expansion
      rule_id: HWT-009

    - field: module_name
      pattern: '\b(TPM|Trusted\s+Platform)\b'
      hw_type: security
      rule_id: HWT-010

    - field: module_name
      pattern: '(^Chassis\s+Configuration$|\b(Bezel|Rack\s+Rails|Server\s+Accessories)\b)'
      hw_type: chassis
      rule_id: HWT-011

    - field: module_name
      pattern: '\bCables\b'
      hw_type: cable
      rule_id: HWT-012

    - field: module_name
      pattern: '\bMotherboard\b'
      hw_type: motherboard
      rule_id: HWT-013

    - field: module_name
      pattern: '\b(Quick\s+Sync|Password|BMC|KVM)\b'
      hw_type: management
      rule_id: HWT-014

    - field: option_name
      pattern: '(?i)(xeon|intel\s+xeon).*(customer\s+install|cus(tomer)?\s+kit|ck)'
      hw_type: processor
      rule_id: HWT-020

    - field: option_name
      pattern: '(?i)(ssd|nvme|sata|hot-plug).*(cus(tomer)?\s+kit|ck)'
      hw_type: storage
      rule_id: HWT-021

    - field: option_name
      pattern: '(?i)power\s+supply.*(cus(tomer)?\s+kit|ck)'
      hw_type: power_supply
      rule_id: HWT-022

    - field: option_name
      pattern: '(?i)(gbe|sfp28|sfp\+|nic|ocp).*(cus(tomer)?\s+(kit|install)|ck)'
      hw_type: network
      rule_id: HWT-023

    - field: option_name
      pattern: '(?i)(hba|perc|fibre\s+channel|fc\s+hba|raid\s+controller).*(dib|ck|full\s+height|low\s+profile)'
      hw_type: storage_controller
      rule_id: HWT-024


=== FILE 2: src/rules/rules_engine.py (MODIFY — RuleSet.__init__ only) ===

In RuleSet.__init__, AFTER the device_type_rules loading block:

    dtr = self._data.get("device_type_rules") or {}
    self.device_type_rules: List[dict] = dtr.get("rules") or []
    applies = dtr.get("applies_to") or []
    self.device_type_applies_to = set(applies) if isinstance(applies, list) else set()

ADD these 4 lines (identical pattern):

    htr = self._data.get("hw_type_rules") or {}
    self.hw_type_rules: List[dict] = htr.get("rules") or []
    hw_applies = htr.get("applies_to") or []
    self.hw_type_applies_to = set(hw_applies) if isinstance(hw_applies, list) else set()

Do NOT add any new functions to rules_engine.py.
Do NOT modify match_rule or match_device_type_rule.


=== FILE 3: src/core/classifier.py (MODIFY — 3 changes) ===

CHANGE 1 — Add hw_type field to ClassificationResult:
After the line:
    device_type: Optional[str] = None
Add:
    hw_type: Optional[str] = None
Before the line:
    warnings: List[str] = field(default_factory=list)

CHANGE 2 — Add _apply_hw_type function AFTER _apply_device_type:

def _apply_hw_type(row: NormalizedRow, result: ClassificationResult, ruleset: RuleSet) -> ClassificationResult:
    """
    Second pass: for ITEM rows with entity_type in hw_type_rules.applies_to
    and matched_rule_id != UNKNOWN-000, set hw_type from first matching rule.
    """
    if result.entity_type is None or result.matched_rule_id == "UNKNOWN-000":
        return result
    if result.entity_type.value not in ruleset.hw_type_applies_to:
        return result
    match = match_rule(row, ruleset.hw_type_rules)
    if match and match.get("hw_type"):
        return replace(result, hw_type=match["hw_type"])
    return result

CHANGE 3 — Wire _apply_hw_type into classify_row:
In classify_row, find every line that says:
    return _apply_device_type(row, result, ruleset)
There are exactly 7 of these (one per entity type: BASE, SERVICE, LOGISTIC, SOFTWARE, NOTE, CONFIG, HW).
Replace EACH with:
    result = _apply_device_type(row, result, ruleset)
    return _apply_hw_type(row, result, ruleset)

Do NOT change the UNKNOWN fallback return at the end of classify_row.
Do NOT change _apply_device_type function — it stays exactly as-is.


=== FILE 4: tests/test_hw_type.py (CREATE — new file) ===

Create tests/test_hw_type.py with the following test classes:

1. TestHwTypeModuleNameRules — parametrized test with module_name → expected hw_type pairs:
   Processor→processor, Additional Processor→processor, Memory Capacity→memory,
   Hard Drives→storage, Power Supply→power_supply, Network Cards→network,
   Fans→cooling, Thermal→cooling, PCIe→expansion, Riser→expansion,
   TPM→security, Chassis Configuration→chassis, Bezel→chassis,
   Rack Rails→chassis, Cables→cable, Motherboard→motherboard,
   Quick Sync→management, BMC→management

2. TestHwTypeOptionNameRules — parametrized test with option_name → expected hw_type pairs:
   "Intel Xeon Silver 4410Y Customer Install"→processor,
   "1.92TB SSD SATA Read Intensive Customer Kit"→storage,
   "800W Power Supply Customer Kit"→power_supply,
   "Broadcom 5720 Dual Port 1GbE OCP Customer Kit"→network,
   "PERC H965i Front DIB"→storage_controller

3. TestHwTypeNonHwRows — verify hw_type is None for HEADER, SERVICE, LOGISTIC, SOFTWARE, UNKNOWN

4. TestHwTypePreservedByDeviceType — verify a row with BOTH device_type and hw_type
   has both populated (e.g., "1.92TB SSD SATA Customer Kit" → device_type set + hw_type=storage)

Each test creates a NormalizedRow with _make_item_row helper, calls classify_row, asserts hw_type.
Load ruleset via fixture from rules/dell_rules.yaml.


CONSTRAINTS:
- Do NOT modify _apply_device_type — it stays exactly as committed
- Do NOT modify json_writer.py — hw_type is NOT serialized to outputs yet
- Do NOT modify stats_collector.py — no hw_type_counts yet
- Do NOT modify helpers.py or test_regression.py — golden format unchanged
- Do NOT modify golden files — golden comparisons do not check hw_type
- Do NOT modify main.py or conftest.py
- Do NOT modify normalizer.py or state_detector.py
- In dell_rules.yaml, do NOT modify any existing rules — only APPEND new section
- hw_type defaults to None for all non-HW rows and unmatched HW rows

VERIFY:
1. pytest tests/ -v --tb=short → all existing tests pass + new hw_type tests pass
2. pytest tests/test_regression.py -v --tb=long → golden comparisons unchanged
3. pytest tests/test_hw_type.py -v --tb=long → all new tests pass
4. pytest tests/test_hw_type.py::TestHwTypePreservedByDeviceType -v → CRITICAL: proves hw_type survives device_type pass
5. git diff rules/dell_rules.yaml shows only additions at end of file
6. git diff src/core/classifier.py shows _apply_device_type body unchanged
```

---

## 9. What Is Explicitly NOT In Scope (Commit 2)

| Item | Reason | When |
|------|--------|------|
| `hw_type` in `classification.jsonl` output | Output format change is a separate commit | Commit 3 |
| `hw_type_counts` in `run_summary.json` | Statistics change is a separate commit | Commit 4 |
| `hw_type` in golden files | Golden format change requires regeneration | Commit 3 |
| `hw_type` in `build_golden_rows` / `_compare_row` | Golden comparison change is a separate commit | Commit 3 |
| `hw_type_rules` hash in `run_summary.json` | Traceability — reuses existing `compute_file_hash` | Commit 4 |
| Separate `hw_type_map.yaml` file | Actual implementation uses `dell_rules.yaml` for consistency with `device_type_rules` | Not planned |

---

# Next Steps (Outputs & Traceability)

The following two atomic PRs complete the hw_type feature by surfacing it in outputs. Each is a separate commit with its own scope and constraints. **Commit 2 must be merged before either is started.**

---

## 10. Pack 3 — Expose hw_type in Outputs and Golden Files

### 10.1 Motivation

After commit 2, `hw_type` is computed correctly on every `ClassificationResult` in memory, but no file on disk contains it. Downstream DB ingestion reads `classification.jsonl` — if `hw_type` is not there, the value is lost at the file boundary. Golden files must also include `hw_type` so that regression tests guard against accidental hw_type changes in the future.

This commit makes `hw_type` visible to the outside world: `classification.jsonl`, golden JSONL, and golden comparison logic.

### 10.2 Files to Modify

```
src/outputs/json_writer.py       — MODIFY: add hw_type to _classification_result_to_dict
tests/helpers.py                 — MODIFY: add hw_type to build_golden_rows
tests/test_regression.py         — MODIFY: add "hw_type" to _compare_row key list
golden/dl1_expected.jsonl        — REGENERATE
golden/dl2_expected.jsonl        — REGENERATE
golden/dl3_expected.jsonl        — REGENERATE
golden/dl4_expected.jsonl        — REGENERATE
golden/dl5_expected.jsonl        — REGENERATE
```

No other files modified. `classifier.py`, `rules_engine.py`, `dell_rules.yaml`, `stats_collector.py`, `main.py`, `conftest.py` all untouched.

### 10.3 Step-by-Step Implementation Instructions

#### Step A — Add `hw_type` to `_classification_result_to_dict` in `src/outputs/json_writer.py`

**Locate** the `_classification_result_to_dict` function. Current device_type logic:

```python
if result.row_kind.value == "ITEM" and result.matched_rule_id != "UNKNOWN-000" and result.entity_type is not None:
    out["device_type"] = result.device_type
else:
    out["device_type"] = None
```

**After** the `device_type` block, **add** the `hw_type` block using the same conditional pattern:

```python
if result.row_kind.value == "ITEM" and result.matched_rule_id != "UNKNOWN-000" and result.entity_type is not None:
    out["hw_type"] = result.hw_type
else:
    out["hw_type"] = None
```

This ensures `hw_type` appears in `classification.jsonl` for every row — `None` for non-applicable rows, the resolved value for HW rows.

**Do NOT** modify `save_classification`, `save_rows_raw`, `save_rows_normalized`, `save_unknown_rows`, `save_header_rows`, or `_normalized_row_to_dict`.

#### Step B — Add `hw_type` to `build_golden_rows` in `tests/helpers.py`

**Locate** the dict construction inside `build_golden_rows`. Current:

```python
out.append({
    "source_row_index": row.source_row_index,
    "row_kind": result.row_kind.value,
    "entity_type": result.entity_type.value if result.entity_type else None,
    "state": result.state.value if result.state else None,
    "matched_rule_id": result.matched_rule_id,
    "device_type": getattr(result, "device_type", None),
    "skus": list(row.skus),
})
```

**Add** `hw_type` after `device_type` and before `skus`:

```python
out.append({
    "source_row_index": row.source_row_index,
    "row_kind": result.row_kind.value,
    "entity_type": result.entity_type.value if result.entity_type else None,
    "state": result.state.value if result.state else None,
    "matched_rule_id": result.matched_rule_id,
    "device_type": getattr(result, "device_type", None),
    "hw_type": getattr(result, "hw_type", None),
    "skus": list(row.skus),
})
```

**Do NOT** modify `run_pipeline_in_memory`.

#### Step C — Add `"hw_type"` to `_compare_row` in `tests/test_regression.py`

**Locate** the key tuple in `_compare_row`. Current:

```python
for key in ("entity_type", "state", "matched_rule_id", "device_type", "skus"):
```

**Replace** with:

```python
for key in ("entity_type", "state", "matched_rule_id", "device_type", "hw_type", "skus"):
```

**No other changes** to `test_regression.py`.

#### Step D — Regenerate all 5 golden files

**Run** the golden regeneration command for each dataset:

```bash
cd dell_spec_classifier

python main.py --input test_data/dl1.xlsx --save-golden
python main.py --input test_data/dl2.xlsx --save-golden
python main.py --input test_data/dl3.xlsx --save-golden
python main.py --input test_data/dl4.xlsx --save-golden
python main.py --input test_data/dl5.xlsx --save-golden
```

**Important:** The exact `--save-golden` flag name may differ. Use whatever mechanism the project uses to write golden JSONL files. If golden generation is done differently (e.g., a script, or by copying `classification.jsonl`), use that method.

**After regeneration**, the golden files will contain `hw_type` for every row. Verify:

```bash
# Spot-check: HW rows should have non-null hw_type
grep '"entity_type": "HW"' golden/dl1_expected.jsonl | head -5
# Expected: each line contains "hw_type": "processor" / "memory" / "storage" / etc.

# Spot-check: non-HW rows should have null hw_type
grep '"entity_type": "SERVICE"' golden/dl1_expected.jsonl | head -5
# Expected: each line contains "hw_type": null
```

### 10.4 Constraints

| Constraint | Rationale |
|------------|-----------|
| No classifier.py changes | hw_type logic is already done in commit 2 |
| No dell_rules.yaml changes | Rules are finalized in commit 2 |
| No rules_engine.py changes | RuleSet loading is finalized in commit 2 |
| No stats_collector.py changes | Statistics are a separate commit (Pack 4) |
| No main.py changes | Orchestration unchanged |
| Golden regeneration is REQUIRED | Schema changed — golden files must include hw_type |
| Golden diff review is MANDATORY | Verify that ONLY hw_type fields changed; no entity_type / state / device_type / matched_rule_id regressions |

### 10.5 Definition of Done

- [ ] `_classification_result_to_dict` includes `hw_type` field in output dict
- [ ] `build_golden_rows` includes `hw_type` in golden-format dict
- [ ] `_compare_row` checks `hw_type` key
- [ ] All 5 golden files regenerated with `hw_type` values
- [ ] `pytest tests/ -v --tb=short` passes (all tests including regression)
- [ ] `pytest tests/test_regression.py -v --tb=long` passes with new golden files
- [ ] Golden diff review: only `hw_type` key added — no regressions in other fields
- [ ] `python main.py --input test_data/dl1.xlsx` produces `classification.jsonl` containing `hw_type`

### 10.6 Verification Commands

```bash
cd dell_spec_classifier

# 1. Verify changed files
git diff --name-only
# Expected:
#   src/outputs/json_writer.py
#   tests/helpers.py
#   tests/test_regression.py
#   golden/dl1_expected.jsonl
#   golden/dl2_expected.jsonl
#   golden/dl3_expected.jsonl
#   golden/dl4_expected.jsonl
#   golden/dl5_expected.jsonl

# 2. Verify json_writer change is additive
git diff src/outputs/json_writer.py
# Expected: ~4 lines added (hw_type block), no deletions

# 3. Verify helpers.py change is additive
git diff tests/helpers.py
# Expected: 1 line added (hw_type key), no deletions

# 4. Verify test_regression.py change is minimal
git diff tests/test_regression.py
# Expected: 1 line changed (_compare_row key tuple), no other changes

# 5. Golden diff review — CRITICAL
# For each golden file, verify ONLY hw_type was added:
git diff golden/dl1_expected.jsonl | grep -c '"hw_type"'
# Expected: positive number (hw_type added to every row)
git diff golden/dl1_expected.jsonl | grep -v '"hw_type"' | grep '^[+-]' | grep -v '^[+-][+-][+-]'
# Expected: no output (no other fields changed)

# 6. Run full test suite
pytest tests/ -v --tb=short
# Expected: all tests pass

# 7. Run regression tests specifically
pytest tests/test_regression.py -v --tb=long
# Expected: all 5 datasets pass with new golden files

# 8. Verify classification.jsonl contains hw_type
python main.py --input test_data/dl1.xlsx
grep '"hw_type"' output/*/classification.jsonl | head -5
# Expected: every line has hw_type field
```

### 10.7 Cursor Prompt

```
Context: Dell Specification Classifier project at dell_spec_classifier/.
Phase B Step 2 commit 2 is merged: hw_type field exists on ClassificationResult,
_apply_hw_type is wired, hw_type_rules exist in dell_rules.yaml.
All tests pass. hw_type is computed in memory but NOT yet in any output file.

Task: Pack 3 — Expose hw_type in classification.jsonl output and golden files.

=== FILE 1: src/outputs/json_writer.py (MODIFY) ===

In _classification_result_to_dict, AFTER the device_type block:

    if result.row_kind.value == "ITEM" and result.matched_rule_id != "UNKNOWN-000" and result.entity_type is not None:
        out["device_type"] = result.device_type
    else:
        out["device_type"] = None

ADD the hw_type block (identical conditional):

    if result.row_kind.value == "ITEM" and result.matched_rule_id != "UNKNOWN-000" and result.entity_type is not None:
        out["hw_type"] = result.hw_type
    else:
        out["hw_type"] = None

Do NOT modify any other function in json_writer.py.

=== FILE 2: tests/helpers.py (MODIFY) ===

In build_golden_rows, in the dict being appended, AFTER:
    "device_type": getattr(result, "device_type", None),
ADD:
    "hw_type": getattr(result, "hw_type", None),
BEFORE:
    "skus": list(row.skus),

Do NOT modify run_pipeline_in_memory.

=== FILE 3: tests/test_regression.py (MODIFY) ===

In _compare_row, change the key tuple from:
    for key in ("entity_type", "state", "matched_rule_id", "device_type", "skus"):
To:
    for key in ("entity_type", "state", "matched_rule_id", "device_type", "hw_type", "skus"):

No other changes to test_regression.py.

=== GOLDEN FILES: Regenerate all 5 ===

After the code changes, regenerate golden files:
    python main.py --input test_data/dl1.xlsx --save-golden
    python main.py --input test_data/dl2.xlsx --save-golden
    python main.py --input test_data/dl3.xlsx --save-golden
    python main.py --input test_data/dl4.xlsx --save-golden
    python main.py --input test_data/dl5.xlsx --save-golden

If --save-golden is not the correct flag, use whatever mechanism the project
has for golden file generation.

CONSTRAINTS:
- Do NOT modify classifier.py, rules_engine.py, dell_rules.yaml
- Do NOT modify stats_collector.py — hw_type_counts is a separate commit
- Do NOT modify main.py or conftest.py
- Do NOT modify normalizer.py or state_detector.py
- Do NOT modify test_hw_type.py
- Only touch: json_writer.py, helpers.py, test_regression.py, golden files

VERIFY:
1. pytest tests/ -v --tb=short → all tests pass
2. pytest tests/test_regression.py -v --tb=long → regressions pass with new goldens
3. git diff golden/dl1_expected.jsonl — verify ONLY hw_type added, no other field changes
4. python main.py --input test_data/dl1.xlsx → classification.jsonl contains hw_type
```

---

## 11. Pack 4 — Add hw_type_counts to run_summary.json and Traceability Hash

### 11.1 Motivation

After Pack 3, `hw_type` is in `classification.jsonl` and golden files — the classification contract is complete. But `run_summary.json` still has no hw_type statistics, so operators cannot see the hardware sub-type distribution at a glance. Additionally, `run_summary.json` should trace the `dell_rules.yaml` hash (which now includes `hw_type_rules`), but this is already covered by Phase A.5 PR2's `rules_file_hash` — no new hash is needed because `hw_type_rules` live inside the same `dell_rules.yaml` file.

This commit adds `hw_type_counts` to `collect_stats` output, mirroring the existing `device_type_counts` pattern.

### 11.2 Files to Modify

```
src/diagnostics/stats_collector.py   — MODIFY: add hw_type_counts to collect_stats
tests/test_stats_hw_type.py          — CREATE: unit test for hw_type_counts in stats
```

No other files modified. `classifier.py`, `rules_engine.py`, `dell_rules.yaml`, `json_writer.py`, `helpers.py`, `test_regression.py`, `main.py`, golden files — all untouched.

### 11.3 Step-by-Step Implementation Instructions

#### Step A — Add `hw_type_counts` to `collect_stats` in `src/diagnostics/stats_collector.py`

**Locate** the `device_type_counts` block inside `collect_stats`. Current:

```python
device_type_counts = {}
for r in classification_results:
    if r.row_kind != RowKind.ITEM or not getattr(r, "device_type", None):
        continue
    dt = r.device_type
    if dt:
        device_type_counts[dt] = device_type_counts.get(dt, 0) + 1
```

**After** this block and **before** the `return` statement, **add** the equivalent for `hw_type`:

```python
hw_type_counts = {}
for r in classification_results:
    if r.row_kind != RowKind.ITEM or not getattr(r, "hw_type", None):
        continue
    ht = r.hw_type
    if ht:
        hw_type_counts[ht] = hw_type_counts.get(ht, 0) + 1
```

**Then**, in the `return` dict, **add** `"hw_type_counts": hw_type_counts` after `"device_type_counts"`:

```python
return {
    "total_rows": total_rows,
    "header_rows_count": header_rows_count,
    "item_rows_count": item_rows_count,
    "entity_type_counts": entity_type_counts,
    "state_counts": state_counts,
    "unknown_count": unknown_count,
    "rules_stats": rules_stats,
    "device_type_counts": device_type_counts,
    "hw_type_counts": hw_type_counts,
}
```

**Do NOT** modify `compute_file_hash`, `save_run_summary`, or any other function.

#### Step B — Create `tests/test_stats_hw_type.py`

**Create** a focused unit test file that verifies `hw_type_counts` appears correctly in `collect_stats` output.

```python
"""
Unit tests for hw_type_counts in collect_stats output.
"""

import pytest
from pathlib import Path

from conftest import project_root
from tests.helpers import run_pipeline_in_memory
from src.diagnostics.stats_collector import collect_stats


@pytest.fixture
def dl1_stats():
    """Run pipeline on dl1.xlsx and collect stats."""
    root = project_root()
    input_path = root / "test_data" / "dl1.xlsx"
    if not input_path.exists():
        pytest.skip("test_data/dl1.xlsx not found")
    rules_path = root / "rules" / "dell_rules.yaml"
    _, results = run_pipeline_in_memory(input_path, rules_path)
    return collect_stats(results)


class TestHwTypeCounts:
    """Verify hw_type_counts is present and consistent in stats."""

    def test_hw_type_counts_key_exists(self, dl1_stats):
        """collect_stats must return hw_type_counts dict."""
        assert "hw_type_counts" in dl1_stats
        assert isinstance(dl1_stats["hw_type_counts"], dict)

    def test_hw_type_counts_values_are_positive(self, dl1_stats):
        """Every hw_type count must be > 0."""
        for hw_type, count in dl1_stats["hw_type_counts"].items():
            assert isinstance(hw_type, str), f"hw_type key must be str, got {type(hw_type)}"
            assert isinstance(count, int), f"count must be int, got {type(count)}"
            assert count > 0, f"hw_type={hw_type!r} has count={count}, expected > 0"

    def test_hw_type_counts_sum_le_hw_entity_count(self, dl1_stats):
        """Sum of hw_type_counts must be ≤ HW entity_type count (some HW rows may have hw_type=None)."""
        hw_entity_count = dl1_stats["entity_type_counts"].get("HW", 0)
        hw_type_total = sum(dl1_stats["hw_type_counts"].values())
        assert hw_type_total <= hw_entity_count, (
            f"hw_type_counts total ({hw_type_total}) > HW entity count ({hw_entity_count})"
        )

    def test_hw_type_counts_keys_are_valid(self, dl1_stats):
        """All hw_type keys must be from the known set."""
        valid_hw_types = {
            "processor", "memory", "storage", "power_supply", "network",
            "storage_controller", "gpu", "cooling", "expansion", "security",
            "chassis", "cable", "motherboard", "management",
        }
        for hw_type in dl1_stats["hw_type_counts"]:
            assert hw_type in valid_hw_types, (
                f"Unknown hw_type={hw_type!r}. Valid: {valid_hw_types}"
            )
```

### 11.4 Traceability Note

`hw_type_rules` live inside `dell_rules.yaml`. Phase A.5 PR2 already injects `rules_file_hash` (SHA-256 of `dell_rules.yaml`) into `run_summary.json` via `main.py`. Because `hw_type_rules` is part of `dell_rules.yaml`, any change to hw_type rules changes the hash automatically. **No additional traceability work is needed.** If `hw_type_rules` were in a separate file (e.g., `hw_type_map.yaml`), a second hash injection would be required — but the design decision in commit 2 to keep everything in `dell_rules.yaml` avoids this.

### 11.5 Constraints

| Constraint | Rationale |
|------------|-----------|
| No classifier.py changes | Classification logic is finalized |
| No dell_rules.yaml changes | Rules are finalized |
| No json_writer.py changes | Output format finalized in Pack 3 |
| No helpers.py / test_regression.py changes | Golden format finalized in Pack 3 |
| No golden regeneration | Golden schema unchanged by this commit |
| No main.py changes | `save_run_summary(stats, ...)` already saves whatever collect_stats returns |
| `save_run_summary` is NOT modified | It saves any dict — adding a key to collect_stats output is sufficient |

### 11.6 Definition of Done

- [ ] `collect_stats` returns dict with `"hw_type_counts"` key containing a `dict[str, int]`
- [ ] `hw_type_counts` is computed using the same pattern as `device_type_counts`
- [ ] `save_run_summary` is NOT modified (it serializes any dict)
- [ ] `tests/test_stats_hw_type.py` exists and passes
- [ ] `pytest tests/ -v --tb=short` passes — all existing + new tests
- [ ] `pytest tests/test_regression.py -v --tb=long` passes — golden comparisons unchanged
- [ ] `python main.py --input test_data/dl1.xlsx` produces `run_summary.json` with `hw_type_counts`

### 11.7 Verification Commands

```bash
cd dell_spec_classifier

# 1. Verify only expected files changed
git diff --name-only
# Expected:
#   src/diagnostics/stats_collector.py
# New (untracked):
#   tests/test_stats_hw_type.py

# 2. Verify stats_collector change is additive
git diff src/diagnostics/stats_collector.py
# Expected: ~8 lines added (hw_type_counts block + return key), no deletions

# 3. Run full test suite
pytest tests/ -v --tb=short
# Expected: all tests pass

# 4. Run new stats test specifically
pytest tests/test_stats_hw_type.py -v --tb=long
# Expected: all pass

# 5. Run regression tests (golden comparisons unaffected)
pytest tests/test_regression.py -v --tb=long
# Expected: all pass, no golden diffs

# 6. Verify run_summary contains hw_type_counts
python main.py --input test_data/dl1.xlsx
python -c "import json; d=json.load(open('output/$(ls -t output | head -1)/run_summary.json')); print(json.dumps(d.get('hw_type_counts'), indent=2))"
# Expected: dict with hw_type keys and positive integer counts
```

### 11.8 Cursor Prompt

```
Context: Dell Specification Classifier project at dell_spec_classifier/.
Phase B Step 2 commits 1-3 are merged:
  - commit 1: dataclasses.replace in _apply_device_type
  - commit 2: hw_type field + _apply_hw_type + hw_type_rules in dell_rules.yaml
  - commit 3 (Pack 3): hw_type in classification.jsonl + golden files regenerated
All tests pass. hw_type is in outputs and golden comparisons.

Task: Pack 4 — Add hw_type_counts to collect_stats and run_summary.json.

=== FILE 1: src/diagnostics/stats_collector.py (MODIFY) ===

In collect_stats, AFTER the device_type_counts block:

    device_type_counts = {}
    for r in classification_results:
        if r.row_kind != RowKind.ITEM or not getattr(r, "device_type", None):
            continue
        dt = r.device_type
        if dt:
            device_type_counts[dt] = device_type_counts.get(dt, 0) + 1

ADD the hw_type_counts block (identical pattern):

    hw_type_counts = {}
    for r in classification_results:
        if r.row_kind != RowKind.ITEM or not getattr(r, "hw_type", None):
            continue
        ht = r.hw_type
        if ht:
            hw_type_counts[ht] = hw_type_counts.get(ht, 0) + 1

THEN in the return dict, AFTER:
    "device_type_counts": device_type_counts,
ADD:
    "hw_type_counts": hw_type_counts,

Do NOT modify compute_file_hash or save_run_summary.


=== FILE 2: tests/test_stats_hw_type.py (CREATE) ===

Create a test file with:

1. Fixture dl1_stats: runs pipeline on dl1.xlsx, calls collect_stats, returns stats dict
2. test_hw_type_counts_key_exists: assert "hw_type_counts" in stats, assert it's a dict
3. test_hw_type_counts_values_are_positive: every value is int > 0
4. test_hw_type_counts_sum_le_hw_entity_count: sum of hw_type_counts ≤ entity_type_counts["HW"]
5. test_hw_type_counts_keys_are_valid: every key is in the known hw_type set
   (processor, memory, storage, power_supply, network, storage_controller,
    gpu, cooling, expansion, security, chassis, cable, motherboard, management)


CONSTRAINTS:
- Do NOT modify classifier.py, rules_engine.py, dell_rules.yaml
- Do NOT modify json_writer.py, helpers.py, test_regression.py
- Do NOT modify main.py or conftest.py
- Do NOT regenerate golden files
- Do NOT modify save_run_summary — it already serializes any dict
- Only touch: stats_collector.py (modify), test_stats_hw_type.py (create)

VERIFY:
1. pytest tests/ -v --tb=short → all tests pass
2. pytest tests/test_stats_hw_type.py -v --tb=long → new tests pass
3. pytest tests/test_regression.py -v --tb=long → golden comparisons unchanged
4. python main.py --input test_data/dl1.xlsx → run_summary.json contains hw_type_counts
```

---

## 12. Complete Phase B Step 2 Roadmap

| Commit | Pack | Scope | Status |
|--------|------|-------|--------|
| 1 | phase_b_step2_preparation_pack_v1.md | `dataclasses.replace` in `_apply_device_type` | ✅ Done |
| 2 | This document, sections 1–8 | `hw_type` field + `_apply_hw_type` + `hw_type_rules` YAML + unit tests | ⬜ Ready |
| 3 | This document, section 10 | `hw_type` in outputs (`json_writer`, `helpers`, `test_regression`) + golden regeneration | ⬜ Blocked by commit 2 |
| 4 | This document, section 11 | `hw_type_counts` in `collect_stats` / `run_summary.json` + unit test | ⬜ Blocked by commit 3 |

After commit 4, the hw_type feature is complete:
- In-memory: `ClassificationResult.hw_type` is computed via `_apply_hw_type` from `hw_type_rules` in YAML.
- On disk: `classification.jsonl` includes `hw_type`; `run_summary.json` includes `hw_type_counts`.
- Regression contract: golden files include `hw_type`; `_compare_row` asserts it.
- Traceability: `rules_file_hash` (SHA-256 of `dell_rules.yaml`, which contains `hw_type_rules`) already in `run_summary.json` from Phase A.5 PR2.

---

*End of Phase B Step 2 Implementation Pack (hw_type) — Revision 2*
