# CLAUDE.md — Project Context: Teresa / spec_classifier
> This file is read automatically by Cowork and Claude Desktop.
> Purpose: avoid loading the repo into every window. Update after each significant cycle.
> Last updated: 2026-05-10
> Last commit: 06d64c1 PR-4c: Lenovo final (Bezel + UNKNOWN-3 + drive_cage alias flip + goldens creation)
> Last run: 2026-04-30 21:17 (4 vendors, 26 files, 4338 rows; see OUTPUT/audit_report.json)

---

## Project

**Teresa** — a pipeline that classifies hardware from Excel BOM (Bill of Materials) files.
Vendors: **Dell / Cisco / HPE / Lenovo / xFusion / Huawei**.
Every row is classified by the following fields:

| Field / Values | Values |
|---|---|
| `entity_type` | BASE / HW / CONFIG / SOFTWARE / SERVICE / LOGISTIC / NOTE / UNKNOWN |
| `hw_type` | server / switch / cpu / memory / gpu / storage_drive / … |
| `device_type` | refinement: ram, nic, raid_controller, cable, chassis, … |
| `state` | PRESENT / ABSENT / DISABLED (DISABLED — for rows like "Disabled" in Lenovo/Dell, see E4) |
| `row_kind` | HEADER / ITEM ← added in annotated_writer in the recent cycle |

---

## Paths (Windows)

```
Repo:    C:\Users\<USERNAME>\Desktop\teresa\spec_classifier
Input:   C:\Users\<USERNAME>\Desktop\INPUT  (dell/, hpe/, cisco/)
Output:  C:\Users\<USERNAME>\Desktop\OUTPUT
Temp:    C:\Users\<USERNAME>\Desktop\temporary
```

---

## Current State (v1.3.x, after audit_1G → PASS)

> Historical state snapshot archived to `.planning/archive/CURRENT_STATE-2026-05-10.md`. Live source-of-truth for project status going forward: `.planning/STATE.md`.

### Tests
```
pytest --collect-only: 420 tests collected (244 def-functions across 31 files)
  — 71 batch_audit
  — 43 cluster_audit
  — 51 lenovo (parser + normalizer + rules)
  — 30 hpe_rules_unit
  — others: dell/cisco/normalizers/writers/regression/smoke/state_detector/...
All PASS as of 2026-04-30.
```

### INPUT layout
```
INPUT/
  dell/    dl1.xlsx … dl5.xlsx
  cisco/   ccw_1.xlsx, ccw_2.xlsx
  hpe/     hp1.xlsx … hp8.xlsx
  lenovo/  L1.xlsx … L11.xlsx
```

### OUTPUT layout (after full run + audit)
```
OUTPUT/  (outside the repo: C:\Users\<USERNAME>\Desktop\OUTPUT, gitignored)
  dell_run/  cisco_run/  hpe_run/  lenovo_run/
    run-YYYY-MM-DD__HH-MM-SS-<stem>/
      classification.jsonl, run_summary.json
      cleaned_spec.xlsx, <stem>_annotated.xlsx
      <stem>_branded.xlsx           ← all vendors (since f2a2300)
      <stem>_annotated_audited.xlsx ← batch_audit.py writes inside the run folder
      unknown_rows.csv, rows_raw.json, rows_normalized.json
      header_rows.csv, run.log
    run-…-TOTAL/   ← aggregation (contains branded.xlsx copies for every file)
  audit_report.json       ← batch_audit.py (at OUTPUT/ root)
  audit_summary.xlsx      ← batch_audit.py (at OUTPUT/ root)
  cluster_summary.xlsx    ← cluster_audit.py (at OUTPUT/ root)
```

### Key repo files
```
spec_classifier/
  batch_audit.py          — E-code audit (E1–E18) + AI mismatch, 1489 LOC
  cluster_audit.py        — clustering of UNKNOWN/AI_MISMATCH rows, 547 LOC
  scripts/update_golden_from_tests.py  — DOES NOT EXIST as a standalone script
                            ↑ functionality lives in main.py --update-golden
  rules/  dell_rules.yaml (93), cisco_rules.yaml (63), hpe_rules.yaml (143),
          lenovo_rules.yaml (112)   ← rule_id count
  golden/ dl1..dl5, ccw_1..ccw_2, hp1..hp8 _expected.jsonl
          (lenovo golden absent — not yet generated)
  docs/   (normative documents; see archive at `.planning/archive/CURRENT_STATE-2026-05-10.md`, CHANGELOG.md)
  src/core/   classifier.py, normalizer.py, parser.py (Dell-specific, see Tech Debt)
  src/vendors/  dell/, cisco/, hpe/, lenovo/
  src/outputs/  annotated_writer.py, excel_writer.py, branded_spec_writer.py, …
  tests/  test_batch_audit.py (def 31 / collected 71)
          test_cluster_audit.py (def 29 / collected 43)
          test_hpe_rules_unit.py (def 6 / collected 30)
          test_lenovo_rules_unit.py + test_lenovo_normalizer.py
            + test_lenovo_parser.py (def 27 / collected 51)
          plus test_dec_acceptance, test_device_type, test_state_detector,
          test_normalizer, test_rules_traceability, test_schema_validation,
          regression/unknown_threshold per vendor — total: 31 files, 420 collected
```

---

## CLI Commands

```powershell
# Run the pipeline
python main.py --batch-dir <INPUT/vendor> --vendor <vendor>

# Audit without AI (fast)
python batch_audit.py --output-dir C:\Users\<USERNAME>\Desktop\OUTPUT --no-ai

# Audit a single vendor with AI
python batch_audit.py --output-dir C:\Users\<USERNAME>\Desktop\OUTPUT --vendor hpe

# Clustering
python cluster_audit.py --output-dir C:\Users\<USERNAME>\Desktop\OUTPUT

# Tests
pytest tests/ -v --tb=short

# Update golden
python main.py --update-golden
```

---

## Business Rules (do not violate when editing)

- **LOGISTIC** = packaging, documents, delivery, freight only
- **Power cord, stacking cable, rail, bracket** → HW, not LOGISTIC
- **power_cord**: `hw_type=None` — intentionally unmapped. Sources of truth:
  `rules/dell_rules.yaml:278`, `rules/cisco_rules.yaml:196`, `rules/hpe_rules.yaml:360`
  all contain the comment `# hw_type: intentionally unmapped — power_cord has no hw_type`.
  power_cord is absent from device_type_map in all 4 YAML files.
  In `batch_audit.py:449` it is excluded from E8: `_E8_NO_HW_TYPE_DEVICES = {"power_cord", "enablement_kit"}`.
  The power_cord ≈ cable semantic alias exists only in `batch_audit.py:DEVICE_TYPE_ALIASES`
  and is applied solely to suppress AI_MISMATCH (when the AI says "cable"
  — it does not count as disagreement with the pipeline). It is NOT a hw_type mapping.
  See git: `c3c7cb6 fix(taxonomy): restore power_cord hw_type=None`.
- **BASE** without device_type → normal (E15 = INFO, not a bug)
- **BASE with device_type** → valid (BASE-*-DT-* YAML rules); E6/E10 MUST NOT fire
- **blank_filler + state=ABSENT** → placeholder in slot, not an error (E16 = INFO)
- **Dummy PID for Airflow** → HW/accessory, not CONFIG
- **Factory Integrated** rows (is_factory_integrated=True) → CONFIG; AI does not check them
- **hw_type applies_to** → `[HW]` (not [HW, BASE]) — code won, taxonomy updated

### device_type Aliases (semantic equivalents, not mismatches)

Source: `batch_audit.py:DEVICE_TYPE_ALIASES`. Used SOLELY to suppress AI_MISMATCH
(semantic equality), NOT as a hw_type mapping.

```
ram              = memory
nic              = network_adapter
raid_controller  = storage_controller
hba              = storage_controller
sfp_cable        = cable
fiber_cable      = cable
power_cord       = cable        ← AI alias only; in YAML power_cord has NO hw_type (see business rule above)
drive_cage       = backplane    ← AI_MISMATCH suppression only, NOT a hw_type mapping.
                                  PR-4c flip (06d64c1) aligns with pipeline output:
                                  HPE `hpe_rules.yaml device_type_map` maps drive_cage→backplane,
                                  so an AI saying "backplane" should not disagree with the pipeline
                                  saying "drive_cage". Previously `chassis` — now obsolete.
bezel            = chassis      ← HPE precedent (HPE bezel→chassis). Lenovo-local override:
                                  `lenovo_rules.yaml` maps bezel→accessory (PR-4c). The global
                                  alias is NOT changed to avoid breaking HPE.
storage_nvme     = storage_drive
storage_ssd      = storage_drive
storage_hdd      = storage_drive
```

### Canonical Field Names (batch_audit _ALIASES)
```
config_name       → module_name   (HPE extension!)
description       → option_name
product_description → option_name
part_number       → skus
product_#         → skus          (HPE extension!)
```

---

## E-codes (batch_audit.py)

Complete list of E-codes from `batch_audit.py:421–518`. Table is sorted by code number.

| Code | Description | Severity |
|---|---|---|
| E1 | invalid_entity (entity not in VALID_ENTITY_TYPES) | P0 |
| E2 | UNKNOWN_no_rule (no rule matched) | BLOCKER |
| E3 | invalid_state (state not in VALID_STATES) | P0 |
| E4 | state mismatch by vendor (data-driven, see E4_STATE_VALIDATORS) | P1 |
| E5 | hw_type on non-HW row (entity ∉ {HW, BASE}) | P0 |
| E6 | device_type on wrong entity (entity ∉ {HW, LOGISTIC, BASE}) | P0 — BASE excluded |
| E7 | hw_type not in HW_TYPE_VOCAB | P1 |
| E8 | HW + PRESENT without hw_type (power_cord, enablement_kit excluded) | P1 |
| E9 | device_type → hw_type mapping mismatch / missing | P1 |
| E10 | hw_type on BASE — narrowed: device_type on BASE is valid; fires only when BASE has hw_type | P0 |
| E11 | hw_type on CONFIG | P0 |
| E12 | hw_type or device_type on NOTE | P0 |
| E13 | LOGISTIC with physical device_type (power_cord/cable/sfp_cable/fiber_cable) | P0 |
| E14 | CONFIG resembling blank_filler (Dummy/Blank/Filler in name, no device_type; SKU NXK-AF-PE excluded) | P1 |
| E15 | BASE without device_type (normal, INFO) | INFO |
| E16 | blank_filler + ABSENT (placeholder in slot; SKUs 412-AASK, 470-BCHP excluded) | INFO |
| E17 | HW without device_type and without hw_type (pipeline could not determine type) | P1 |
| E18 | LOGISTIC with physical keyword (cord/cable/rail/bracket/mount/kit/rack/pdu/ups), no device_type | P0 |

### pipeline_check tags in *_audited.xlsx
- **AI_MISMATCH** — AI disagrees with pipeline (light blue)
- **AI_SUGGEST** — pipeline did not determine device_type; AI suggests one (green)
- **MANUAL_CHECK** — AI is unsure (orange)
- **E2** — UNKNOWN (red, BLOCKER)

---

## Known Tech Debt (P2, out of scope for the current plan)

> Capture as `ARCHITECTURE_RISKS.md` before adding a 4th vendor

1. `batch_audit.py` reads Excel (`pd.read_excel`) instead of `classification.jsonl` — Excel leakage persists
2. Alias sprawl in `batch_audit.py` (`DEVICE_TYPE_ALIASES`, `_ALIASES`, `HW_TYPE_TRUST`,
   `DEVICE_TYPE_TRUST`, `ENTITY_TRUST_PIPELINE`) — to be resolved by a single canonical schema
3. `batch_audit.py` = 1489 LOC (grew from 1280), potential god-object
4. TOTAL folders cause confusion during runs (branded/audited files are duplicated)
5. ✅ DONE (audit_1E Step 2, 6147b3a): DEVICE_TYPE_MAP is loaded from YAML;
   `detect_vendor_from_path()` accepts known_vendors; `--vendor` choices are dynamic;
   E4 is data-driven via `E4_STATE_VALIDATORS` + `_check_e4()`. See archive at `.planning/archive/CURRENT_STATE-2026-05-10.md` § audit_1E
6. ✅ DONE (audit_1E Step 1, a5e15d3): `VENDOR_EXTRA_COLS` removed;
   replaced with `VendorAdapter.get_extra_cols()` (default []), overridden
   in `HPEAdapter` (5 cols) and `CiscoAdapter` (2 cols); `annotated_writer` takes `extra_cols` as a parameter
7. `core/parser.py` is actually Dell-specific (sentinel "Module Name", see docstring),
   but lives in core/ — Cisco/HPE/Lenovo use their own `parser.py` files under `src/vendors/<vendor>/`
8. `lenovo_rules.yaml` still lacks full golden coverage — `golden/` contains only dl/ccw/hp;
   `tests/test_lenovo_*.py` rely on rules-unit + parser/normalizer tests
9. `run_audit.ps1` runs only Dell + HPE + Cisco (lenovo not wired); the 2026-04-30 21:17 run
   (see OUTPUT/audit_report.json) processed lenovo manually or via `main.py --batch-dir`

For broader BLOCKER/IMPORTANT/NICE-TO-FIX context see `.planning/codebase/CONCERNS.md`.

---

## Tool Roles

| Tool | Role |
|---|---|
| **Cursor** (Pro) | writes / modifies code and docs — executor |
| **Claude** (Pro) | architectural conclusions, audit, change design |
| **ChatGPT** (Plus) | drives steps, PowerShell commands, final verdict |
| **Gemini** | optional — "second opinion" on the final report |

---

## Development Cycle

```
PRE-CHECK → PLAN (Master Plan) → CURSOR IMPLEMENT → POST-CHECK → AUDIT (1A–1G) → DOC UPDATE
```

| Scenario | Steps |
|---|---|
| Small YAML edit | PRE → BATCH AUDIT MASTER PLAN → Cursor → POST |
| New feature / refactor | PRE → MASTER PLAN A → Cursor → POST → 1A–1G |
| After FAIL audit | MASTER PLAN B (fix) → Cursor → POST → 1G |
| Documentation update | 1A–1G → DOC UPDATE MASTER PLAN → Cursor |

---

## Hard Rules for Claude Windows

- **R1.** Each step = a separate new Claude window (Cowork mode is exempt).
- **R2.** Read ONLY the files explicitly listed for that window.
- **R3.** Every reply ends with a SUMMARY block:
  ```
  CLAIMS: …
  EVIDENCE: claim_id → file + location + quote ≤2 lines
  SEVERITY: P0/P1/P2 per claim
  ACTION: what to do
  ```
- **R4.** A "tracked in git" claim requires a SHA — otherwise UNCONFIRMED.
- **R5.** Only SUMMARY blocks reach the final 1G window — never the full text.

### Severity Levels
- **P0** — BLOCKER: cannot proceed (tests broken, UNKNOWN rose, contract violated)
- **P1** — IMPORTANT: fix in the next cycle (docs drift, blind spots)
- **P2** — NICE: quality improvements (refactor, cosmetics)

---

## Recommended Models per Step

| Step | Model | Extended |
|---|---|---|
| PRE-CHECK, POST-CHECK, checklist (1A, 1C, 1G) | Sonnet 4.6 | OFF |
| Architecture, integration points, docs, tests (1B, 1D, 1E, 1F) | Opus 4.6 | ON |
| Master Plan generation | Opus 4.6 | ON |
| Batch Audit analysis | Opus 4.6 | ON |

---

## Prompts — Location

Ready-to-use prompts for every step:
**`prompts/`** (folder with one .md file per step)
See `prompts/README.md` for navigation.
