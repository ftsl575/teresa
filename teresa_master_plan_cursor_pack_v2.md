# TERESA — MASTER PLAN + CURSOR PROMPT PACK
Version: v2.0  |  Date: 2026-02-25  |  Single source of truth. Ignore previous chats.

---

## RULE PRIORITY REFERENCE (DO NOT MODIFY)

```
Entity priority (frozen):
BASE (1) → SERVICE (2) → LOGISTIC (3) → SOFTWARE (4) → NOTE (5) → CONFIG (6) → HW (7) → UNKNOWN (8)

Within hw_type assignment:
device_type_map → rule_id_map → regex rules (first match wins, ORDER MATTERS)

State priority (after P1):
present_override_keywords → absent_keywords → default PRESENT
```

**This priority model is frozen. Do NOT reorder rule blocks unless explicitly required by a prompt.**
**DEC-* decisions are final. Do NOT reinterpret.**

---

## EXECUTION RULES (MANDATORY)

- Prompts MUST be executed strictly in order **P1 → P9**. No parallel changes.
- Each prompt = **separate PR / commit**. No bundling.
- Golden files may be updated **ONLY in P9** and ONLY with documented diffs.
- Python changes in P1: **≤ 15 LOC total**. No new functions or classes.
- Do NOT reorder rule blocks unless explicitly required.
- New tests require **explicit approval** and must:
  - Follow existing test file naming and structure
  - Use deterministic assertions
  - Not duplicate golden coverage
- Before committing any regex change, run the **Regex Sandbox** (see each prompt).
- **Failure protocol**: If any prompt fails acceptance criteria —
  1. Stop execution immediately. Do not proceed to next prompt.
  2. Revert the PR (`git revert` or `git reset --hard <baseline>`).
  3. Report the exact failing case: file, row, OptionID, expected vs actual.
  4. Fix root cause and re-run the failed prompt from scratch before continuing.

---

## PART 1 — MASTER PLAN

### Phase 0 — Discovery (done, this document)
All root causes traced. Seven atomic fixes required, one Python touch, six YAML-only.

```
Baseline commit: <insert git rev-parse HEAD before starting P1>
All diffs must be relative to this commit.
```

Run before starting P1:
```powershell
git rev-parse HEAD  # record this hash; paste above
```

### Phase 1 — Architecture

| # | Finding | Layer | Files |
|---|---------|-------|-------|
| P1 | Blank state override (DEC-003, F7) | YAML + Python | `dell_rules.yaml`, `state_detector.py`, `rules_engine.py`, `classifier.py` |
| P2 | Blank hw_type plural fix (DEC-003, F7) | YAML only | `dell_rules.yaml` |
| P3 | HDD hw_type pattern (F1) | YAML only | `dell_rules.yaml` |
| P4 | No Cable → CONFIG (DEC-001, DEC-002) | YAML only | `dell_rules.yaml` |
| P5 | BOSS taxonomy (DEC-006, F5) | YAML only | `dell_rules.yaml` |
| P6 | Optics/Transceiver → network_adapter (DEC-004, F6) | YAML only | `dell_rules.yaml` |
| P7 | DAC/SFP cables LOGISTIC→HW (DEC-007) | YAML only | `dell_rules.yaml` |
| P8 | PERC device_type (DEC-005) | YAML only | `dell_rules.yaml` |
| P9 | Golden files + regression tests + CHANGELOG | Tests + docs | `golden/`, `tests/`, `CHANGELOG.md` |

### Phase 2 — Implementation
Execute Cursor Prompt Pack P1–P9 **strictly in order**, one PR per prompt.

### Phase 3 — QA
- Run full pipeline on dl1–dl6 after each prompt.
- Verify acceptance criteria per prompt using PowerShell commands.
- Execute `pytest` and confirm no regressions.
- After each prompt: `unknown_count` must not increase; `HW_items` count must remain stable (±0).
- Update golden files only in P9.

### Phase 4 — Release
- Bump `dell_rules.yaml` `version` to `1.1.0`.
- Tag: `git tag v1.1.0`.
- CHANGELOG entry in P9.

### Phase 5 — Monitoring
- Track `hw_type_null_count` in `run_summary.json`. Target: 0 for dl1–dl6.
- Track `unknown_count` — must not increase vs baseline.

---

## ROOT CAUSE SUMMARY

| Finding | Root Cause |
|---------|-----------|
| F1 – HDD null | Pattern `\b\d+K\s*RPM\b` requires "RPM"; "10K 512e" has no RPM |
| F2/F3/F4 – No Cable as HW/cable | HW-002 fires on `module_name Cables` before CONFIG; no CONFIG rule for "No Cable" |
| F5 – BOSS as nvme | `rule_id_map: HW-004: nvme` overrides all BOSS rows; "No BOSS Card" not routed to CONFIG |
| F6 – Optics as cable | `module_name (?i)\bCables?\b` fires before any optics rule (none existed) |
| F7 – Rear Blanks ABSENT+null | STATE-001 `^\s*No\s+` fires; blank regex uses `\bBlank\b` not `\bBlanks?\b` |
| PERC device_type | `device_type_rules` only matches PERC+CK/DIB suffix; plain "PERC … Controller" unmatched |

---

## PART 2 — CURSOR PROMPT PACK

**Template for every prompt:**
```
[CONTEXT]    — why this fix is needed
[TASK]       — exact changes (YAML patches / Python LOC)
[PATCH_SCOPE]— files to touch, max LOC
[ACCEPTANCE] — before/after rows + OptionID checks
[COMMANDS]   — PowerShell verification (full paths from dell_spec_classifier\)
```

---

### PROMPT 1 — Blank state override (DEC-003 / F7 — state fix)

**[CONTEXT]**
`state_detector.py` derives state from `option_name` via `state_rules.absent_keywords`. No mechanism exists to override ABSENT → PRESENT when `option_name` contains "Blank(s)". "No OCP - 2 Rear Blanks" → ABSENT (wrong; DEC-003 requires PRESENT).

**[TASK]**

**Step A — `dell_rules.yaml`**: Add `present_override_keywords` to `state_rules`:
```yaml
state_rules:
  present_override_keywords:
    - pattern: '(?i)\bBlanks?\b'
      rule_id: STATE-OVERRIDE-001
  absent_keywords:
    ...  # unchanged
```

**Step B — `src/rules/rules_engine.py`**: In `RuleSet.__init__`, add (2 LOC):
```python
self._state_override_list: List[dict] = sr.get("present_override_keywords") or []
```
Add method (3 LOC):
```python
def get_state_override_rules(self) -> List[dict]:
    return self._state_override_list
```

**Step C — `src/core/state_detector.py`**: Update `detect_state` signature and insert override loop (6 LOC):
```python
def detect_state(option_name: str, state_rules: List[dict],
                 override_rules: Optional[List[dict]] = None) -> State:
    if not option_name:
        return State.PRESENT
    text = str(option_name).strip()
    for rule in (override_rules or []):           # present-override first
        pattern = rule.get("pattern")
        if pattern and re.search(pattern, text, re.IGNORECASE):
            return State.PRESENT
    for rule in state_rules:                      # absent/disabled — unchanged
        ...
    return State.PRESENT
```

**Step D — `src/core/classifier.py`**: Update `detect_state` call (1 LOC change):
```python
state = detect_state(
    row.option_name,
    ruleset.get_state_rules(),
    override_rules=ruleset.get_state_override_rules(),
)
```

**[PATCH_SCOPE]**
- Files: `dell_rules.yaml`, `state_detector.py`, `rules_engine.py`, `classifier.py`
- Python: ≤ 15 LOC total. No new functions beyond `get_state_override_rules`. No new classes.

**[ACCEPTANCE]**

Before/after for representative rows (dl6, module "OCP 3.0 Accessories"):

| Row | Option Name | Before state | After state |
|-----|-------------|-------------|------------|
| 133 | No OCP - 2 Rear Blanks | ABSENT | PRESENT |
| 186 | No OCP - 2 Rear Blanks | ABSENT | PRESENT |
| 239 | No OCP - 2 Rear Blanks | ABSENT | PRESENT |

Positive test strings (must return PRESENT):
- `"No OCP - 2 Rear Blanks"`
- `"No BOSS card, Rear Blank"`

Negative test strings (must NOT trigger override → must return ABSENT):
- `"No Cable"` → ABSENT
- `"2 OCP - No Cable"` → ABSENT
- `"No TPM Module"` → ABSENT

After each prompt invariants:
- `unknown_count` must not increase
- `HW_items` count must remain stable (±0)

**[COMMANDS]**
```powershell
# Regex sandbox — run BEFORE committing, inspect 10+ affected rows
python main.py --input test_data\dl6.xlsx --output output\regex_sandbox_p1.xlsx

# Spot-check: confirm "Rear Blanks" rows are PRESENT
python -c "
import openpyxl
wb = openpyxl.load_workbook('output\regex_sandbox_p1.xlsx')
ws = wb.active
h = [c.value for c in ws[1]]
oi=h.index('option_id')+1; st=h.index('state')+1
for row in ws.iter_rows(min_row=2):
    if row[oi-1].value == 'G5PJAF3':
        print(f'Row {row[0].row}: state={row[st-1].value}')
"

# Unit tests
python -m pytest tests/test_state_detector.py -v

# Invariant check
python -c "
import json, glob
runs = sorted(glob.glob('output/run_*/run_summary.json'))
if runs:
    with open(runs[-1]) as f: s = json.load(f)
    print('unknown_count:', s.get('unknown_count'))
    print('HW_items:', s.get('hw_items_count', 'check key name'))
"
```

---

### PROMPT 2 — Blank hw_type plural fix (DEC-003 / F7 — hw_type)

**[CONTEXT]**
`hw_type_rules.rules` has `option_name: (?i)\b(Blank|Filler|Dummy|Slot\s+Filler)\b → hw_type: blank`. "No OCP - 2 Rear **Blanks**" (plural) does not match → `hw_type=null`.

**[TASK]**
In `dell_rules.yaml`, `hw_type_rules.rules`, change the `option_name` blank pattern:
```yaml
# BEFORE:
- field: option_name
  pattern: '(?i)\b(Blank|Filler|Dummy|Slot\s+Filler)\b'
  hw_type: blank

# AFTER:
- field: option_name
  pattern: '(?i)\b(Blanks?|Filler|Dummy|Slot\s+Filler)\b'
  hw_type: blank
```

**[PATCH_SCOPE]**
- File: `dell_rules.yaml` only. 1 line change. No Python.

**[ACCEPTANCE]**

| OptionID | Option Name | Before hw_type | After hw_type |
|----------|-------------|---------------|--------------|
| G5PJAF3 | No OCP - 2 Rear Blanks | null | blank |

Positive matches (must hit `hw_type=blank`):
- `"No OCP - 2 Rear Blanks"` → blank
- `"GPU Blank"` → blank (existing, must not regress)

Negative (must NOT match blank):
- `"Blanking panel safety"` — verify in sandbox that this is not a real row
- `"10K warranty"` — irrelevant, must not match

After-prompt invariants: `unknown_count` stable, `HW_items` stable (±0).

**[COMMANDS]**
```powershell
# Regex sandbox
python main.py --input test_data\dl6.xlsx --output output\regex_sandbox_p2.xlsx

python -c "
import openpyxl
wb = openpyxl.load_workbook('output\regex_sandbox_p2.xlsx')
ws = wb.active
h = [c.value for c in ws[1]]
oi=h.index('option_id')+1; ht=h.index('hw_type')+1; st=h.index('state')+1
fails = []
for row in ws.iter_rows(min_row=2):
    if row[oi-1].value == 'G5PJAF3':
        ht_v = row[ht-1].value; st_v = row[st-1].value
        if ht_v != 'blank' or st_v != 'PRESENT':
            fails.append(f'Row {row[0].row}: hw_type={ht_v} state={st_v}')
print('PASS' if not fails else 'FAIL: ' + str(fails))
"
```

---

### PROMPT 3 — HDD hw_type pattern fix (F1)

**[CONTEXT]**
Pattern `(?i)\b(HDD|\d+(\.\d+)?K\s*RPM|7200\s*RPM|10K\s*RPM|15K\s*RPM)\b` requires "RPM". "2.4TB Hard Drive SAS FIPS-140 **10K** 512e" contains "10K" but no "RPM" → `hw_type=null`. Also "Hard Drive" is not covered.

**[TASK]**
In `dell_rules.yaml`, `hw_type_rules.rules`, update the hdd option_name rule and add a module_name backup:

```yaml
# BEFORE:
- field: option_name
  pattern: '(?i)\b(HDD|\d+(\.\d+)?K\s*RPM|7200\s*RPM|10K\s*RPM|15K\s*RPM)\b'
  hw_type: hdd

# AFTER:
- field: option_name
  pattern: '(?i)\b(HDD|Hard\s+Drive|\d+(\.\d+)?K(?:\s*RPM)?)\b'
  hw_type: hdd

# ADD immediately after (new rule):
- field: module_name
  pattern: '(?i)\bHard\s+Drives?\b'
  hw_type: hdd
```

**[PATCH_SCOPE]**
- File: `dell_rules.yaml` only. 2 rules modified/added. No Python.

**[ACCEPTANCE]**

| OptionID | Option Name | Before hw_type | After hw_type |
|----------|-------------|---------------|--------------|
| GEVNB9T | 2.4TB Hard Drive SAS FIPS-140 10K 512e 2.5in Hot-Plug | null | hdd |

All 3 occurrences in dl6 (rows 16, 68, 119) must show `hw_type=hdd`.

Positive matches:
- `"2.4TB Hard Drive SAS FIPS-140 10K 512e"` → hdd
- `"900GB SAS 15K RPM 2.5in"` → hdd (existing, must not regress)

Negative (must NOT match hdd):
- `"480GB SSD SATA 6Gbps"` → must remain ssd
- `"10K warranty"` → no match (not a drive row; verify in sandbox)

After-prompt invariants: `unknown_count` stable, `HW_items` stable, `hw_type_null_count` decreases by 6.

**[COMMANDS]**
```powershell
# Regex sandbox — check 10 Hard Drive module rows
python main.py --input test_data\dl6.xlsx --output output\regex_sandbox_p3.xlsx

python -c "
import openpyxl
wb = openpyxl.load_workbook('output\regex_sandbox_p3.xlsx')
ws = wb.active
h = [c.value for c in ws[1]]
oi=h.index('option_id')+1; ht=h.index('hw_type')+1
for row in ws.iter_rows(min_row=2):
    if row[oi-1].value == 'GEVNB9T':
        print(f'Row {row[0].row}: hw_type={row[ht-1].value}')
"
```

---

### PROMPT 4 — No Cable / No Cables Required → CONFIG (DEC-001, DEC-002)

**[CONTEXT]**
"No Cable", "2 OCP - No Cable", "No Cables Required, No GPU Blanks" are classified as `HW` (via HW-002 `module_name Cables`) with `hw_type=cable`. Per DEC-001/002 they must be `CONFIG + ABSENT + hw_type=NULL`. CONFIG (priority 6) fires before HW (priority 7), so adding `config_rules` option_name entries is sufficient.

**[TASK]**
In `dell_rules.yaml`, `config_rules`, append at end:

```yaml
  # DEC-002: No Cables Required (GPU/FPGA empty row)
  - field: option_name
    pattern: '(?i)\bNo\s+Cables?\s+Required\b'
    entity_type: CONFIG
    rule_id: CONFIG-010-NO-CABLES-REQUIRED

  # DEC-001: No Cable / No Cables — negative lookahead prevents overlap with DEC-003 blank rows
  - field: option_name
    pattern: '(?i)\bNo\s+Cables?\b(?!.*\bBlanks?\b)'
    entity_type: CONFIG
    rule_id: CONFIG-011-NO-CABLE
```

CONFIG-010 must come BEFORE CONFIG-011 (more specific first).

**[PATCH_SCOPE]**
- File: `dell_rules.yaml` only. 2 new config_rules entries. No Python.
- Do NOT touch hw_type_rules cable patterns.

**[ACCEPTANCE]**

| OptionID | Option Name | Before entity/hw_type | After entity/hw_type |
|----------|-------------|----------------------|---------------------|
| GDIOK4A  | No Cables Required, No GPU Blanks | HW / cable | CONFIG / NULL |
| GN1I836  | No Cables Required, No GPU Blanks | HW / cable | CONFIG / NULL |
| G0PNZWL  | 2 OCP - No Cable | HW / cable | CONFIG / NULL |
| G5PJAF3  | No OCP - 2 Rear Blanks | HW / blank | HW / blank (must NOT change) |

Positive matches (must become CONFIG):
- `"No Cables Required, No GPU Blanks"` → CONFIG
- `"2 OCP - No Cable"` → CONFIG

Negative (must NOT become CONFIG):
- `"No OCP - 2 Rear Blanks"` → must remain HW (contains "Blanks")
- `"SFP+ SR Optic, 10GbE"` — no "No Cable", must not match

After-prompt invariants: `unknown_count` stable, `HW_items` count may decrease (No Cable rows move from HW to CONFIG — expected and acceptable; document delta).

**[COMMANDS]**
```powershell
# Regex sandbox — run all datasets
foreach ($n in 1..6) {
    python main.py --input "test_data\dl$n.xlsx" --output "output\dl${n}_sandbox_p4.xlsx"
}

python -c "
import openpyxl, glob
check = {
    'GDIOK4A': ('CONFIG','ABSENT', None),
    'GN1I836': ('CONFIG','ABSENT', None),
    'G0PNZWL': ('CONFIG','ABSENT', None),
    'G5PJAF3': ('HW',    'PRESENT','blank'),
}
for path in sorted(glob.glob('output/dl*_sandbox_p4.xlsx')):
    wb = openpyxl.load_workbook(path)
    ws = wb.active
    h = [c.value for c in ws[1]]
    oi=h.index('option_id')+1; et=h.index('entity_type')+1
    st=h.index('state')+1; ht=h.index('hw_type')+1
    for row in ws.iter_rows(min_row=2):
        oid = row[oi-1].value
        if oid in check:
            exp = check[oid]
            got = (row[et-1].value, row[st-1].value, row[ht-1].value)
            status = 'OK' if got == exp else f'FAIL got {got} expected {exp}'
            print(f'{path} | {oid} | {status}')
"
```

---

### PROMPT 5 — BOSS taxonomy (DEC-006 / F5)

**[CONTEXT]**
`hw_type_rules.rule_id_map: HW-004: nvme` maps all Boot Optimized Storage rows to `nvme`. This overrides BOSS-N1 (should be `storage_controller`), "No BOSS Card" (should be `CONFIG + ABSENT`), and Rear Blank rows. Three sub-cases need distinct outcomes per DEC-006.

**[TASK]**

**Step A** — Remove `HW-004: nvme` from `rule_id_map`:
```yaml
# hw_type_rules.rule_id_map — DELETE this line:
    HW-004: nvme
```

**Step B** — Remove BOSS/Boot Optimized nvme rule from `hw_type_rules.rules` Layer 3:
```yaml
# DELETE:
    - field: module_name
      pattern: '(?i)\b(Boot\s+Optimized|BOSS)\b'
      hw_type: nvme
```

**Step C** — Add CONFIG rule for "No BOSS Card" in `config_rules`:
```yaml
  # DEC-006: No BOSS Card → CONFIG + ABSENT
  - field: option_name
    pattern: '(?i)\bNo\s+BOSS\b'
    entity_type: CONFIG
    rule_id: CONFIG-012-NO-BOSS
```

**Step D** — Add BOSS → storage_controller in `hw_type_rules.rules` (after existing PERC rule):
```yaml
    - field: option_name
      pattern: '(?i)\bBOSS\b'
      hw_type: storage_controller
```

Order check: blank rule fires BEFORE storage_controller. "No BOSS … Rear Blank" → blank ✓. "BOSS-N1 controller card" → no Blank → falls to new BOSS rule → storage_controller ✓.

**[PATCH_SCOPE]**
- File: `dell_rules.yaml` only. 2 deletions + 2 additions. No Python.
- Do NOT reorder existing rule blocks.

**[ACCEPTANCE]**

| OptionID | Option Name | Before entity/hw_type | After entity/hw_type |
|----------|-------------|----------------------|---------------------|
| G2ITOYM  | BOSS-N1 controller card | HW / nvme | HW / storage_controller |
| GIEP1Z6  | No BOSS Card | HW / nvme | CONFIG / NULL |
| (Rear Blank) | No BOSS … Rear Blank | HW / nvme | HW / blank |

Positive matches:
- `"BOSS-N1 controller card"` → `hw_type=storage_controller`
- `"No BOSS Card"` → `entity_type=CONFIG`

Negative:
- `"No BOSS … Rear Blank"` → must NOT be CONFIG (Blank override wins in state; entity must remain HW)
- NVMe SSD rows — must still show `hw_type=nvme` (via option_name NVMe rule)

After-prompt invariants: `unknown_count` stable. `BOSS_absent_as_nvme` = 0 in dl2/dl3/dl5.

**[COMMANDS]**
```powershell
foreach ($n in 1..6) {
    python main.py --input "test_data\dl$n.xlsx" --output "output\dl${n}_sandbox_p5.xlsx"
}

python -c "
import openpyxl, glob
boss_checks = {'GIEP1Z6': ('CONFIG','ABSENT',None)}
for path in sorted(glob.glob('output/dl*_sandbox_p5.xlsx')):
    wb = openpyxl.load_workbook(path)
    ws = wb.active
    h = [c.value for c in ws[1]]
    oi=h.index('option_id')+1; et=h.index('entity_type')+1
    st=h.index('state')+1; ht=h.index('hw_type')+1; on=h.index('option_name')
    for row in ws.iter_rows(min_row=2):
        oid = row[oi-1].value
        if oid in boss_checks:
            exp = boss_checks[oid]
            got = (row[et-1].value, row[st-1].value, row[ht-1].value)
            status = 'OK' if got == exp else f'FAIL got {got}'
            print(f'{path} | {oid} | {status}')
        opt = str(row[on].value or '')
        if 'BOSS-N1 controller' in opt:
            ht_v = row[ht-1].value
            status = 'OK' if ht_v == 'storage_controller' else f'FAIL hw_type={ht_v}'
            print(f'{path} | BOSS-N1 row {row[0].row} | {status}')
"
```

---

### PROMPT 6 — Optics/Transceiver → network_adapter (DEC-004 / F6)

**[CONTEXT]**
`hw_type_rules.rules` Layer 3: `module_name: (?i)\bCables?\b → hw_type: cable`. Module "Optics & Cables for Network Cards" contains "Cables" → all rows in that module, including SFP+ optics and transceivers, get `hw_type=cable`. Per DEC-004 they must be `hw_type=network_adapter`.

**[TASK]**
In `dell_rules.yaml`, `hw_type_rules.rules`, insert two new rules **immediately BEFORE** the existing `module_name Cables?` rule:

```yaml
    # DEC-004: Optics / Transceivers → network_adapter (must precede cable catch-all)
    - field: option_name
      pattern: '(?i)\b(Optic|Transceiver|SFP\+|SFP28|QSFP)\b'
      hw_type: network_adapter

    - field: module_name
      pattern: '(?i)\bOptics?\b'
      hw_type: network_adapter

    # --- cable (existing — DO NOT MODIFY) ---
    - field: module_name
      pattern: '(?i)\bCables?\b'
      hw_type: cable
    ...
```

**[PATCH_SCOPE]**
- File: `dell_rules.yaml` only. 2 new rules inserted. Do NOT modify the cable rule.

**[ACCEPTANCE]**

| OptionID | Option Name | Before hw_type | After hw_type |
|----------|-------------|---------------|--------------|
| G0FVJIE | SFP+ SR Optic, 10GbE, for all SFP+ ports… | cable | network_adapter |
| GNID9SB | Dell Networking, Transceiver, 25GbE SFP28 SR… | cable | network_adapter |

All 12 `Optics_as_cable` occurrences in dl6 must be resolved.

Positive matches:
- `"SFP+ SR Optic, 10GbE …"` → network_adapter
- `"Dell Networking, Transceiver, 25GbE SFP28"` → network_adapter

Negative (must NOT become network_adapter):
- `"1m Passive DAC SFP+ Cable"` → must remain cable (SFP+ is in name but "Cable" is explicit)

> Note: Check sandbox carefully — the option_name rule for `SFP\+` could match DAC cable rows. If so, add negative lookahead: `(?i)\b(Optic|Transceiver|SFP\+|SFP28|QSFP)\b(?!.*\bCable\b)`.

After-prompt invariants: `unknown_count` stable, `HW_items` stable.

**[COMMANDS]**
```powershell
# Regex sandbox — inspect all 'Optics & Cables' module rows
python main.py --input test_data\dl6.xlsx --output output\regex_sandbox_p6.xlsx

python -c "
import openpyxl
wb = openpyxl.load_workbook('output\regex_sandbox_p6.xlsx')
ws = wb.active
h = [c.value for c in ws[1]]
oi=h.index('option_id')+1; ht=h.index('hw_type')+1; mn=h.index('module_name')
targets = {'G0FVJIE', 'GNID9SB'}
fails = []
for row in ws.iter_rows(min_row=2):
    oid = row[oi-1].value
    if oid in targets:
        got = row[ht-1].value
        if got != 'network_adapter':
            fails.append(f'Row {row[0].row}: {oid} hw_type={got}')
    # Also check real cable rows are not broken
    mod = str(row[mn].value or '')
    opt = str(row[h.index('option_name')].value or '') if 'option_name' in h else ''
    if 'Cable' in opt and 'Optic' not in opt and 'Transceiver' not in opt:
        ht_v = row[ht-1].value
        if ht_v == 'network_adapter':
            fails.append(f'Row {row[0].row}: cable row became network_adapter: {opt[:50]}')
print('PASS' if not fails else 'FAIL: ' + str(fails))
"
```

---

### PROMPT 7 — DAC/SFP cables LOGISTIC→HW (DEC-007)

**[CONTEXT]**
`LOGISTIC-005-SFP-CABLE` routes rows like "Dell Networking, Cable, SFP28 to SFP28, 25GbE, Passive Copper Twinax Direct Attach Cable" into `entity_type=LOGISTIC`. DAC/Twinax cables are physical network components inserted into SFP ports providing real data connectivity — they are HW, not packaging or shipping items. LOGISTIC must be reserved for shipping kits, labels, documentation, and delivery-only items.

**[TASK]**

**Step A** — Remove `LOGISTIC-005-SFP-CABLE` from `logistic_rules`:
```yaml
# DELETE both entries from logistic_rules:
  - field: option_name
    pattern: '(?i)(sfp|twinax|dac).*(cable|direct\s+attach)'
    entity_type: LOGISTIC
    rule_id: LOGISTIC-005-SFP-CABLE

  - field: module_name
    pattern: '(?i)sfp\s+module'
    entity_type: LOGISTIC
    rule_id: LOGISTIC-005-SFP-CABLE
```

After deletion, these rows will fall through to `HW-002` (module_name `Cables` is already in HW-002 pattern) — no new HW rule needed.

**Step B** — `device_type_rules` already applies to `[HW, LOGISTIC]` and already has `LOGISTIC-005-SFP-CABLE → sfp_cable`. After moving entity to HW, the device_type match still fires. **No change needed in device_type_rules.**

**Step C** — `hw_type`: after entity becomes HW, Layer 3 module_name `Cables?` rule fires → `hw_type=cable`. This is correct. **No change needed in hw_type_rules.**

**[PATCH_SCOPE]**
- File: `dell_rules.yaml` only. 2 rule deletions from `logistic_rules`. No Python. No new rules added.

**[ACCEPTANCE]**

| Option Name (example) | Before entity/device_type | After entity/device_type |
|-----------------------|--------------------------|-------------------------|
| Dell Networking, Cable, SFP28 … Twinax Direct Attach | LOGISTIC / sfp_cable | HW / sfp_cable |
| Any DAC / Twinax cable row | LOGISTIC | HW |

Positive (must become HW):
- `"Dell Networking, Cable, SFP28 to SFP28, 25GbE, Passive Copper Twinax Direct Attach Cable, 3 Meter"` → entity_type=HW
- `"SFP+ DAC cable, 1m"` → entity_type=HW

Negative (must NOT be affected):
- Power cord rows (`LOGISTIC-004-CORD`) — must remain LOGISTIC
- Optics rows (P6 fix) — must remain HW / network_adapter
- Shipping / packaging module rows — must remain LOGISTIC

After-prompt invariants: `unknown_count` stable. `HW_items` count increases by number of DAC rows (expected — document delta). `LOGISTIC_items` count decreases by same amount.

**[COMMANDS]**
```powershell
# Regex sandbox — inspect all SFP/DAC/Twinax rows across datasets
foreach ($n in 1..6) {
    python main.py --input "test_data\dl$n.xlsx" --output "output\dl${n}_sandbox_p7.xlsx"
}

python -c "
import openpyxl, glob
for path in sorted(glob.glob('output/dl*_sandbox_p7.xlsx')):
    wb = openpyxl.load_workbook(path)
    ws = wb.active
    h = [c.value for c in ws[1]]
    et=h.index('entity_type')+1; on=h.index('option_name'); ht=h.index('hw_type')+1; dt=h.index('device_type')+1
    for row in ws.iter_rows(min_row=2):
        opt = str(row[on].value or '')
        if any(kw in opt.lower() for kw in ['twinax','dac','direct attach','sfp28 to sfp28']):
            et_v = row[et-1].value; ht_v = row[ht-1].value; dt_v = row[dt-1].value
            ok = et_v == 'HW'
            print(f"{'OK' if ok else 'FAIL'}: {path} | et={et_v} ht={ht_v} dt={dt_v} | {opt[:60]}")
"

# Confirm power cords still LOGISTIC
python -c "
import openpyxl, glob
for path in sorted(glob.glob('output/dl*_sandbox_p7.xlsx')):
    wb = openpyxl.load_workbook(path)
    ws = wb.active
    h = [c.value for c in ws[1]]
    et=h.index('entity_type')+1; on=h.index('option_name')
    for row in ws.iter_rows(min_row=2):
        opt = str(row[on].value or '')
        if 'power cord' in opt.lower() or 'jumper cord' in opt.lower():
            et_v = row[et-1].value
            ok = et_v == 'LOGISTIC'
            print(f"{'OK' if ok else 'FAIL'}: power cord | et={et_v} | {opt[:50]}")
"
```

---

### PROMPT 8 — PERC device_type (DEC-005)

**[CONTEXT]**
`device_type_rules` sets `device_type=raid_controller` only for PERC rows with suffix `(dib|ck|full_height|low_profile)`. Plain "PERC H755 SAS Front Controller" rows get `device_type=null`. Per DEC-005 they must have `device_type=raid_controller` + `hw_type=storage_controller`. hw_type Layer 3 already has the PERC rule so only device_type is missing.

**[TASK]**
In `dell_rules.yaml`, `device_type_rules.rules`, append after the `HW-008-HBA-PERC-CUS` rules and before the CPU rule:

```yaml
    # DEC-005: PERC + Controller (broader match, no suffix required)
    - field: option_name
      pattern: '(?i)\bPERC\b.*\bController\b'
      device_type: raid_controller
      rule_id: DEC-005-PERC-CONTROLLER

    # DEC-005: RAID Controllers module → raid_controller
    - field: module_name
      pattern: '(?i)\bRAID.*Controllers?\b'
      device_type: raid_controller
      rule_id: DEC-005-RAID-MODULE
```

**[PATCH_SCOPE]**
- File: `dell_rules.yaml` only. 2 new device_type_rules entries. No Python. Do NOT touch hw_type_rules.

**[ACCEPTANCE]**

| File | Option Name pattern | Before device_type | After device_type |
|------|---------------------|-------------------|------------------|
| dl3, dl5, dl6 | PERC … Controller | null | raid_controller |

Positive matches:
- `"PERC H755 SAS Front Controller"` → raid_controller
- `"PERC H345 Controller"` → raid_controller

Negative (must NOT gain raid_controller):
- `"PERC H755 Customer Kit"` → already handled by HW-008-HBA-PERC-CUS; must not double-match (first-match wins — HW-008 fires first, so no problem)
- `"Non-RAID module name"` — verify no accidental module match

`PERC_Controller_missing_device_type` counters: dl3 0, dl5 0, dl6 0.

After-prompt invariants: `unknown_count` stable, `HW_items` stable.

**[COMMANDS]**
```powershell
foreach ($n in 3,5,6) {
    python main.py --input "test_data\dl$n.xlsx" --output "output\dl${n}_sandbox_p7.xlsx"
}

python -c "
import openpyxl, glob
for path in sorted(glob.glob('output/dl[356]_sandbox_p7.xlsx')):
    wb = openpyxl.load_workbook(path)
    ws = wb.active
    h = [c.value for c in ws[1]]
    on=h.index('option_name'); dt=h.index('device_type'); ht=h.index('hw_type')
    for row in ws.iter_rows(min_row=2):
        opt = str(row[on].value or '')
        if 'PERC' in opt and 'Controller' in opt:
            dt_v = row[dt].value; ht_v = row[ht].value
            ok = dt_v == 'raid_controller' and ht_v == 'storage_controller'
            print(f\"{'OK' if ok else 'FAIL'}: {path} row {row[0].row} | dt={dt_v} ht={ht_v} | {opt[:60]}\")
"
```

---

### PROMPT 9 — Golden files + regression tests + CHANGELOG

**[CONTEXT]**
After P1–P8 all acceptance criteria pass. Golden files reflect pre-fix outputs. Tests must be updated and CHANGELOG written.

**[TASK]**

**Step A** — Regenerate golden files (dl1–dl5):
```powershell
# Use project's golden-export mechanism (check main.py --help or Makefile)
foreach ($n in 1..5) {
    python main.py --input "test_data\dl$n.xlsx" --output "output\dl${n}_final.xlsx" --export-golden "golden\dl${n}_expected.jsonl"
}
```
Golden files may be updated **ONLY here**. Provide `git diff --stat golden/` before committing.

**Step B** — Add unit tests to `tests/test_state_detector.py`:
```python
def test_blank_override_present():
    from src.core.state_detector import detect_state
    from src.rules.rules_engine import RuleSet
    rs = RuleSet.load("rules/dell_rules.yaml")
    assert detect_state("No OCP - 2 Rear Blanks",
                        rs.get_state_rules(),
                        rs.get_state_override_rules()).value == "PRESENT"

def test_no_cable_absent():
    from src.core.state_detector import detect_state
    from src.rules.rules_engine import RuleSet
    rs = RuleSet.load("rules/dell_rules.yaml")
    assert detect_state("2 OCP - No Cable",
                        rs.get_state_rules(),
                        rs.get_state_override_rules()).value == "ABSENT"

def test_boss_blank_present():
    from src.core.state_detector import detect_state
    from src.rules.rules_engine import RuleSet
    rs = RuleSet.load("rules/dell_rules.yaml")
    assert detect_state("No BOSS card, Rear Blank",
                        rs.get_state_rules(),
                        rs.get_state_override_rules()).value == "PRESENT"
```

**Step C** — Add DEC acceptance tests to `tests/test_dec_acceptance.py` (new file, following existing test structure). Cover all OptionIDs from the QA checklist below. New tests must:
- Follow existing test file naming and structure.
- Use deterministic assertions.
- Not duplicate golden coverage.

**Step D** — Update `CHANGELOG.md`:
```markdown
## [1.1.0] — 2026-02-25
### Fixed
- DEC-003: "Blanks" plural now recognized; state overridden to PRESENT
- DEC-001/002: "No Cable" / "No Cables Required" classified as CONFIG+ABSENT
- DEC-004: Optics and transceivers classified as hw_type=network_adapter
- DEC-005: PERC Controller rows now have device_type=raid_controller
- DEC-006: BOSS-N1 → storage_controller; No BOSS Card → CONFIG+ABSENT
- F1: Hard Drive / 10K rows now classified as hw_type=hdd
```

**Step E** — Bump `dell_rules.yaml` version to `1.1.0`.

**[PATCH_SCOPE]**
- `golden/dl1–dl5_expected.jsonl` — regenerate only
- `tests/test_state_detector.py` — append tests
- `tests/test_dec_acceptance.py` — new file
- `CHANGELOG.md` — append entry
- `dell_rules.yaml` — version bump only

**[ACCEPTANCE]**
- `pytest tests\ -v` passes with 0 failures, 0 errors.
- `hw_type_null_count` in latest `run_summary.json` for dl6 = 0.
- `unknown_count` ≤ baseline across all datasets.

**[COMMANDS]**
```powershell
# Full test suite
python -m pytest tests\ -v --tb=short 2>&1 | Tee-Object -FilePath output\pytest_final.log

# Check golden diff
git diff --stat golden/

# Check run summary
python -c "
import json, glob
runs = sorted(glob.glob('output/run_*/run_summary.json'))
if runs:
    with open(runs[-1]) as f: s = json.load(f)
    print('hw_type_null_count:', s.get('hw_type_null_count'))
    print('unknown_count:', s.get('unknown_count'))
"

# Tag release
git tag v1.1.0
```

---

## PART 3 — HUMAN QA SIGN-OFF CHECKLIST

After all 8 prompts applied and `pytest` green, open each annotated xlsx and verify:

| ✅ | OptionID | Expected entity | state | hw_type | device_type |
|----|----------|----------------|-------|---------|------------|
| ☐ | GEVNB9T | HW | PRESENT | hdd | — |
| ☐ | GDIOK4A | CONFIG | ABSENT | NULL | — |
| ☐ | GN1I836 | CONFIG | ABSENT | NULL | — |
| ☐ | G0PNZWL | CONFIG | ABSENT | NULL | — |
| ☐ | G0FVJIE | HW | PRESENT | network_adapter | — |
| ☐ | GNID9SB | HW | PRESENT | network_adapter | — |
| ☐ | (PERC+Controller) | HW | PRESENT | storage_controller | raid_controller |
| ☐ | G5PJAF3 | HW | PRESENT | blank | — |
| ☐ | G2ITOYM / G937ZBP / GKM2QOA | HW | PRESENT | storage_controller | — |
| ☐ | GIEP1Z6 | CONFIG | ABSENT | NULL | — |
| ☐ | All files | — | — | `unknown_count` stable | `hw_type_null_count`=0 (dl6) |
