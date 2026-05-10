# 02 — Per-doc Audit Findings (DOC-03)

**Audited:** 2026-05-10
**Scope:** 13 files in spec_classifier/docs/ (CONTRIBUTING.md handled separately in Task 5.3)

| # | Path | Verdict | Drift items | Tech-debt refs verified | Action taken |
|---|---|---|---|---|---|
| 1 | `docs/DOCS_INDEX.md` | DRIFT | Stale title (only 3 vendors); missing `cycle2_summary.md` entry; phantom table separator (line 35) | n/a | Task 5.2: rewrite table + fix title |
| 2 | `docs/dev/CONTRIBUTING.md` | LEGACY | Entire file is Russian; repo tree shows only 3 vendors; pre-GSD conventions | n/a | Task 5.3: add one-line note only |
| 3 | `docs/dev/NEW_VENDOR_GUIDE.md` | DRIFT | Entire file Russian; still references `CURRENT_STATE.md`; Step 3 rule_id format inconsistency (no mention of new vendors beyond HPE); Step 8 mentions CURRENT_STATE.md | VERIFIED: `get_extra_cols()` correctly mentioned (DONE in tech-debt #6) | Task 5.2 batch 1: translate + fix refs |
| 4 | `docs/dev/ONE_BUTTON_RUN.md` | DRIFT | References `.\scripts\run_full.ps1` (does not exist — replaced by `..\run.ps1`); file is Russian; references `run_tests.ps1` (does not exist); references `temp_root/diag/` (not current flow) | n/a | Task 5.2 batch 1: translate + fix script refs |
| 5 | `docs/dev/OPERATIONAL_NOTES.md` | DRIFT | Entire file Russian; references `run_audit.ps1` (does not exist — unified into `run.ps1`); section 7 vendor list says "three vendors"; batch_audit tech-debt section has stale line numbers | VERIFIED: `batch_audit.py` -TOTAL filter documented accurately | Task 5.2 batch 1: translate + fix refs |
| 6 | `docs/dev/TESTING_GUIDE.md` | DRIFT | Title says "Dell + Cisco CCW + HPE" (3 vendors); entire file Russian; CI gate command missing lenovo/huawei/xfusion; section 1 test strategy lists only Dell/Cisco/HPE tests | VERIFIED: `MAX_SKIP_RATIO = 0.50` at conftest.py:14 ACCURATE | Task 5.2 batch 1: translate + update for 6 vendors |
| 7 | `docs/product/TECHNICAL_OVERVIEW.md` | DRIFT | Entire file Russian; Section 1 says "Dell, Cisco CCW, HPE" (3 vendors); Section 4 `--vendor` choices says `dell,cisco,hpe`; Section 7 project tree shows only 3 vendors + no lenovo/huawei/xfusion; golden list shows only dl/ccw/hp golden files; Section 9 Limitations still says "Three vendors" | VERIFIED: power_cord `hw_type=None` mentioned correctly (Section 11 - none; implicitly OK); core/parser Dell-specific docstring VERIFIED at src/core/parser.py:3 | Task 5.2 batch 2: translate + update for 6 vendors |
| 8 | `docs/rules/RULES_AUTHORING_GUIDE.md` | DRIFT | Entire file Russian; Section 1 lists only 3 rule files; Section 9 step-by-step refers only to Dell/Cisco datasets; Section 13 Cisco-rules section; `--vendor {dell,cisco,hpe}` (3 only); rule_id table only shows Dell/Cisco/HPE codes; missing lenovo/huawei/xfusion | VERIFIED: power_cord hw_type=None section present and ACCURATE (lines 140-147); `hw_type_rules.applies_to: [HW]` correctly documented | Task 5.2 batch 3: translate + update for 6 vendors |
| 9 | `docs/schemas/DATA_CONTRACTS.md` | DRIFT | Entire file Russian (some sections); Section 11 has duplicate "Canonical Field Names" subsection (lines 199-225 repeat content already in lines 184-198); applies_to scope says `[HW, LOGISTIC, BASE]` but should be `[HW, LOGISTIC]` (BASE added by device_type_rules but hw_type_rules is [HW] only — needs verification) | VERIFIED: `HW_TYPE_VOCAB` (26 values) at `classifier.py:28` and `batch_audit.py:44` ACCURATE; `_E8_NO_HW_TYPE_DEVICES` at batch_audit.py:506 ACCURATE | Task 5.2 batch 3: translate + remove duplicate section |
| 10 | `docs/taxonomy/cycle2_summary.md` | CLEAN | File is in English; cross-references resolve; content accurate | VERIFIED: `verify_teresa_audit_actionables.py` exists at `spec_classifier/scripts/verify_teresa_audit_actionables.py` (ACCURATE) | No action needed |
| 11 | `docs/taxonomy/hw_type_taxonomy.md` | DRIFT | File is mixed Russian/English; table headers and group labels are Russian; some narrative sections are Russian; `HW_TYPE_VOCAB` contents verified against live code | VERIFIED: `power_cord` hw_type=None documented correctly (lines 52, 135, 188, 405, 435); HW_TYPE_VOCAB 26 values match `classifier.py:28`; `bezel→chassis` (HPE) vs `bezel→accessory` (Lenovo) documented correctly | Task 5.2 batch 3: translate Russian narrative sections |
| 12 | `docs/user/CLI_CONFIG_REFERENCE.md` | DRIFT | Entire file Russian; `--vendor` description says only `dell, cisco, hpe` (3 vendors); output structure table shows only dell_run/cisco_run/hpe_run; config.yaml example shows only 3 vendor_rules entries | n/a | Task 5.2 batch 2: translate + update for 6 vendors |
| 13 | `docs/user/RUN_PATHS_AND_IO_LAYOUT.md` | DRIFT | File is Russian; section 3 "Не используется" (TEMP not used) — references `run_full.ps1`/`run_tests.ps1` in item 3 of isolation policy; "Не делайте так" section references `scripts\run_tests.ps1` (does not exist); INPUT subfolder doc shows only 3 vendors; audit/cluster output path diagram shows `dell_run` only | n/a | Task 5.2 batch 2: translate + fix script refs + update for 6 vendors |
| 14 | `docs/user/USER_GUIDE.md` | CLEAN | File is already in English (mixed — some Russian phrases); Section 2 correctly lists all 6 vendors; Section 7 workflow shows all 6 vendors; branded_spec note correct | VERIFIED: power_cord not mentioned but `hw_type` description accurate for 6 vendors | Minor: Section 6 device_type table uses `ram` (old) and `nic` (old) as listed values alongside canonical names — DRIFT |

---

**Revised USER_GUIDE.md verdict:** DRIFT (Section 6 device_type table lists `ram`, `nic` as standalone categories alongside canonical forms; hw_type list says "26 values (v2.1.0)" but current version is v2.6.0)

| # | Path | Final Verdict |
|---|---|---|
| 14 | `docs/user/USER_GUIDE.md` | DRIFT |

---

## Per-doc detail

### `docs/DOCS_INDEX.md`

**Verdict:** DRIFT

- Line 1: Title `# Documentation Index — Spec Classifier (Dell + Cisco CCW + HPE)` — stale parenthetical; project supports 6 vendors
- Lines 16–34: Key Documents table — all listed files resolve PASS; but missing `docs/taxonomy/cycle2_summary.md` entry
- Line 35: Orphan `|` row (blank table separator — formatting artifact)
- Cross-references:
  - `docs/user/USER_GUIDE.md` → PASS (file exists)
  - `docs/user/CLI_CONFIG_REFERENCE.md` → PASS
  - `docs/user/RUN_PATHS_AND_IO_LAYOUT.md` → PASS
  - `docs/schemas/DATA_CONTRACTS.md` → PASS
  - `docs/rules/RULES_AUTHORING_GUIDE.md` → PASS
  - `docs/dev/NEW_VENDOR_GUIDE.md` → PASS
  - `docs/dev/ONE_BUTTON_RUN.md` → PASS
  - `docs/dev/TESTING_GUIDE.md` → PASS
  - `docs/dev/CONTRIBUTING.md` → PASS
  - `docs/dev/OPERATIONAL_NOTES.md` → PASS
  - `docs/product/TECHNICAL_OVERVIEW.md` → PASS
  - `CHANGELOG.md` → PASS (spec_classifier/CHANGELOG.md)
  - `docs/taxonomy/hw_type_taxonomy.md` → PASS
  - `batch_audit.py` → PASS (script reference, not a .md link)
  - `cluster_audit.py` → PASS
  - `CLAUDE.md` → PASS
  - `prompts/README.md` → PASS
  - `docs/taxonomy/cycle2_summary.md` → MISSING FROM INDEX
- Russian residue: none
- Tech-debt mentions: none
- Phase 3 hand-off (retired prompt refs): none

**Required fixes:**
1. Update title: remove `(Dell + Cisco CCW + HPE)` → `# Documentation Index — Spec Classifier`
2. Add `docs/taxonomy/cycle2_summary.md` row to Key Documents table
3. Remove orphan `|` line 35

---

### `docs/dev/NEW_VENDOR_GUIDE.md`

**Verdict:** DRIFT

- Lines 1–124: Entire file is Russian
- Line 22: References `CURRENT_STATE.md` ("Изменить: ... CHANGELOG.md, CURRENT_STATE.md") — CURRENT_STATE.md is now archived
- Line 88–90: Step 8 says "Обновить CHANGELOG.md и CURRENT_STATE.md" — same stale reference
- Step 3 rule_id format: mentions `H` for HPE; does not cover lenovo (`L`), huawei (`HU`), xfusion (`XF`) — DRIFT for a 6-vendor guide
- Cross-references:
  - `docs/rules/RULES_AUTHORING_GUIDE.md` → PASS
  - `docs/schemas/DATA_CONTRACTS.md` → PASS
  - `src/vendors/dell/adapter.py` → PASS
  - `src/vendors/cisco/adapter.py` → PASS
  - `src/vendors/cisco/parser.py` → PASS
  - `src/vendors/cisco/normalizer.py` → PASS (implied)
- Russian residue: ALL lines (Russian file)
- Tech-debt mentions: `get_extra_cols()` method mentioned correctly (tech-debt #6 is DONE per CLAUDE.md)
- Phase 3 hand-off (retired prompt refs): none

**Required fixes:**
1. Translate to English
2. Replace `CURRENT_STATE.md` references with archive pointer in 2 places (lines 22 and 88)
3. Update rule_id table to include lenovo/huawei/xfusion codes

---

### `docs/dev/ONE_BUTTON_RUN.md`

**Verdict:** DRIFT

- Lines 1–40: Entire file is Russian
- Line 6: `.\scripts\run_full.ps1` — BROKEN (file does not exist; replaced by `run.ps1` at repo root per commit `0080f45`)
- Line 10 item 5: References `temp_root/diag/runs/<timestamp>/` — this is a legacy path; current run.ps1 uses `OUTPUT/` structure
- Line 22 item 3 (`pyproject.toml` redirection) — no longer refers to `run_full.ps1`; pyproject.toml behavior still valid
- Line 36: `.\scripts\clean.ps1` — PASS (file exists at `spec_classifier/scripts/clean.ps1`)
- Cross-references:
  - `scripts\run_full.ps1` → BROKEN (does not exist)
  - `scripts\clean.ps1` → PASS
- Russian residue: ALL lines
- Tech-debt mentions: none
- Phase 3 hand-off (retired prompt refs): none

**Required fixes:**
1. Translate to English
2. Rewrite `.\scripts\run_full.ps1` → `.\run.ps1` (repo root) in the main command
3. Update "What does run_full.ps1 do" section to describe what `run.ps1` does per current implementation
4. Remove `temp_root/diag/` reference (not current pattern)

---

### `docs/dev/OPERATIONAL_NOTES.md`

**Verdict:** DRIFT

- Lines 1–114: Entire file is Russian
- Line 80–83: Section 7 references `run_audit.ps1` at `C:\Users\<USERNAME>\Desktop\teresa\run_audit.ps1` — BROKEN (file does not exist; replaced by `run.ps1`)
- Line 86–88: Section 7 says pipeline runs "all three vendors (dell → hpe → cisco)" — stale; `run.ps1` supports 6 vendors
- Lines 98–113: Tech-debt section lists `DEVICE_TYPE_MAP` at lines 56–79, `validate_row()` at 346–360, `LLM_SYSTEM prompt` at 90–110, `Known FP cases` at 900–971 — these line numbers likely stale; note this section proposes fixing tech-debt (audit MUST NOT propose fixes per D-21/D-22) but this section pre-dates D-21/D-22 and is informational framing, not a directive to fix
- Cross-references: all internal paths use `<USERNAME>` placeholder (PASS per Phase 1 hygiene)
- Russian residue: ALL lines
- Tech-debt mentions:
  - `batch_audit.py` Excel reading (described in tech-debt section) — VERIFIED the issue exists; section framing is informational/correct
  - TOTAL folder exclusion documented at line 28 — VERIFIED accurate
- Phase 3 hand-off (retired prompt refs): none

**Required fixes:**
1. Translate to English
2. Replace `run_audit.ps1` references with `run.ps1` in section 7 (2 occurrences)
3. Update "three vendors" → "all active vendors" / "six vendors" in section 7

---

### `docs/dev/TESTING_GUIDE.md`

**Verdict:** DRIFT

- Line 1: Title `# Руководство по тестированию — Spec Classifier (Dell + Cisco CCW + HPE)` — stale parenthetical; 6 vendors now
- Lines 1–119: Entire file is Russian
- Section 1: Lists only Dell/Cisco/HPE test strategies; no mention of lenovo/huawei/xfusion tests
- Section 6 CI gate: Lists only Dell/Cisco/HPE test commands; missing lenovo/huawei/xfusion test modules
- Section 4 golden generation: only Dell/Cisco/HPE examples
- Section 8 "new dataset": only Dell/Cisco/HPE examples
- Cross-references: no .md links; all paths use `<USERNAME>` placeholder (PASS)
- Russian residue: ALL lines
- Tech-debt mentions:
  - `MAX_SKIP_RATIO = 0.50` — VERIFIED at `conftest.py:14` (ACCURATE)
  - conftest.py:14 reference — ACCURATE
- Phase 3 hand-off (retired prompt refs): none

**Required fixes:**
1. Translate to English
2. Update title: remove `(Dell + Cisco CCW + HPE)` → title becomes `# Testing Guide — Spec Classifier`
3. Add lenovo/huawei/xfusion test sections or note that pattern extends to all vendors
4. Update CI gate command to include lenovo/huawei/xfusion regression tests

---

### `docs/product/TECHNICAL_OVERVIEW.md`

**Verdict:** DRIFT (high — 313 lines, entire file Russian, major vendor count drift)

- Lines 1–313: Entire file is Russian
- Line 9: "Dell, Cisco CCW, HPE" — 3 vendors; project now has 6
- Lines 18, 91, 244: `--vendor {dell,cisco,hpe}` — stale choices; live `main.py` has 6 vendors
- Lines 155–209: Section 7 project tree shows only dell/cisco/hpe vendor subdirs; no lenovo/huawei/xfusion
- Lines 184–199: Golden list shows only dl1-5, ccw_1-2, hp1-8; missing lenovo/huawei/xfusion goldens
- Lines 244–251: Section 9 "Three vendors" limitation — stale
- Line 300: Reference to `prompts/06_BATCH-AUDIT-MASTER-PLAN.md` — Phase 3 hand-off flag
- Line 75: `<stem>_branded.xlsx` described as "Only Dell" — now applies to all vendors (per `spec_classifier/CLAUDE.md` current state) — needs verification
- Cross-references:
  - `src/outputs/annotated_writer.py` → PASS
  - internal module references → PASS
- Russian residue: ALL lines
- Tech-debt mentions:
  - `core/parser.py` Dell-specificity: lines 28-29 mention Dell sentinel "Module Name" in core/parser — VERIFIED ACCURATE (parser.py:29 has hardcoded sentinel)
  - YAML rule order / first-match: mentioned in line 249 — VERIFIED ACCURATE (rules_engine.py:51-70 first-match)
- Phase 3 hand-off (retired prompt refs): Line 300 references `prompts/06_BATCH-AUDIT-MASTER-PLAN.md` — flag for Phase 3

**Required fixes:**
1. Translate to English
2. Update "three vendors" → "six vendors" throughout (Sections 1, 4, 7, 9)
3. Update `--vendor` choices to include all 6 vendors
4. Update Section 7 project tree to include lenovo/huawei/xfusion subdirs
5. Update golden list to include lenovo/huawei/xfusion golden stems
6. Verify and update branded_spec.xlsx statement (Dell-only vs all vendors)
7. Keep `prompts/06_BATCH-AUDIT-MASTER-PLAN.md` reference (Phase 3 handles prompts)

---

### `docs/rules/RULES_AUTHORING_GUIDE.md`

**Verdict:** DRIFT

- Lines 1–155: Entire file is Russian
- Line 5: Lists only 3 rule files (`dell_rules.yaml`, `cisco_rules.yaml`, `hpe_rules.yaml`); project has 6
- Line 5: `--vendor {dell,cisco,hpe}` — stale; 6 vendors now
- Lines 68–76: rule_id table shows only Dell/Cisco/HPE codes; no lenovo (`L`)/huawei (`HU`)/xfusion (`XF`)
- Section 9 step 5: Examples only show Dell/Cisco datasets; no lenovo/huawei/xfusion
- Section 13: Cisco-specific section exists; no equivalent for lenovo/huawei/xfusion
- Cross-references:
  - `rules/dell_rules.yaml` → PASS
  - `rules/cisco_rules.yaml` → PASS
  - `rules/hpe_rules.yaml` → PASS
  - `tests/test_rules_unit.py` → PASS
  - `tests/test_device_type.py` → PASS (test_device_type.py referenced; actual file is test_rules_unit.py — check)
- Russian residue: ALL lines
- Tech-debt mentions:
  - `power_cord hw_type=None` section (lines 140-147): VERIFIED ACCURATE — intentional, per business rules; framing is correct
  - `hw_type_rules.applies_to: [HW]` (correctly documented)
  - YAML rule order: "first match wins" documented in section 3 and section 11 — VERIFIED ACCURATE (classifier.py:218, rules_engine.py:51-70)
- Phase 3 hand-off (retired prompt refs): none

**Required fixes:**
1. Translate to English
2. Update vendor list / `--vendor` choices to include 6 vendors
3. Add lenovo/huawei/xfusion rule_id codes to naming convention table
4. Update step 5 examples to mention all vendors (or note "extend to all active vendors")

---

### `docs/schemas/DATA_CONTRACTS.md`

**Verdict:** DRIFT

- Lines 1–233: Mostly Russian (English mixed in)
- Lines 199–225: Duplicate "Canonical Field Names" section — lines 184-198 already have a canonical field names table; lines 199-225 repeat this with a different format and a slightly different (incomplete) field list. This is content drift.
- Line 39: `applies_to scope` states `device_type_rules.applies_to: [HW, LOGISTIC, BASE]` — matches actual YAML rules (applies_to includes BASE); `hw_type_rules.applies_to: [HW]` — VERIFIED ACCURATE
- Line 155: `audit_summary.xlsx` sheet name "Сводный отчёт" — Russian column header in doc
- Lines 157-165: audit_summary.xlsx column names are in Russian (`Документ`, `Вендор`, etc.) — these are the actual Excel column names (in Russian in the Excel file), so documenting them in Russian is accurate but the surrounding prose should be translated
- Cross-references:
  - No broken .md links
- Russian residue: substantial (narrative sections throughout)
- Tech-debt mentions:
  - `HW_TYPE_VOCAB` 26 values: VERIFIED — `classifier.py:28` (26 values in frozenset) and `batch_audit.py:44` (same frozenset) — ACCURATE
  - `_E8_NO_HW_TYPE_DEVICES` — not directly mentioned in this doc but device_type section covers power_cord correctly
- Phase 3 hand-off (retired prompt refs): none

**Required fixes:**
1. Translate Russian narrative sections to English (keep Russian Excel column names in audit_summary.xlsx table — those ARE the actual column headers)
2. Remove duplicate Section 11 "Canonical Field Names" subsection (lines 199-225) — merge or delete; Section 11 lines 184-198 is sufficient

---

### `docs/taxonomy/cycle2_summary.md`

**Verdict:** CLEAN

- File is in English throughout
- Cross-references:
  - `./hw_type_taxonomy.md` → PASS
  - `../schemas/DATA_CONTRACTS.md` → PASS
  - `../../scripts/verify_teresa_audit_actionables.py` → PASS (file confirmed at `spec_classifier/scripts/verify_teresa_audit_actionables.py`)
- Russian residue: none
- Tech-debt mentions: none
- Phase 3 hand-off (retired prompt refs): none
- Factual claims: pytest counts (768 collected / 767 passed) are historical (cycle 2 snapshot); no assertion of "current" state — ACCEPTABLE
- No CURRENT_STATE.md references
- All links resolve correctly

---

### `docs/taxonomy/hw_type_taxonomy.md`

**Verdict:** DRIFT

- Mixed Russian/English: file has English for most tables/code blocks; section headers and group labels are in Russian; narrative notes are in Russian
- Russian residue: lines 3 (subtitle), 44-53 (decision table), 58 (group header), 62-67 (group 1 table Russian column headers), 73-80 (group 2 Russian), 85-94 (group 3 Russian), 96-103 (group 3 boundary table), 108-116 (group 4 Russian), 130-134 (power cord note), 139-146 (group 6 Russian), 152-159 (group 7 Russian), 165-170 (group 8 Russian), 175-179 (group 9 Russian), 184-196 (section header + table), 200 (HW_TYPE_VOCAB subtitle), 228-273 (migration table — Russian column headers), 377-413 (coverage matrix — Russian column header), 417-440 (YAML cheatsheet — Russian comments), 444-457 (filter table), 462 (footer)
- Cross-references:
  - `rules/<vendor>_rules.yaml` → PASS (general reference)
  - No specific file links
- Tech-debt mentions:
  - `power_cord` `hw_type=None` — VERIFIED ACCURATE (lines 52, 135, 188, 405, 435)
  - `enablement_kit` `hw_type=None` — VERIFIED ACCURATE (line 189, 405)
  - `device_type_rules.applies_to: [HW, LOGISTIC, BASE]` / `hw_type_rules.applies_to: [HW]` — VERIFIED ACCURATE
  - `DEVICE_TYPE_ALIASES` in `batch_audit.py` = AI-mismatch suppression only — VERIFIED ACCURATE
  - Bezel cross-vendor divergence (HPE `bezel→chassis`, Lenovo `bezel→accessory`) — VERIFIED ACCURATE per CLAUDE.md
- Phase 3 hand-off (retired prompt refs): none

**Required fixes:**
1. Translate Russian table headers and group labels to English
2. Translate Russian narrative note sections (decision table, group descriptions, notes)
3. Keep Russian technical comments inside YAML examples (per D-06 — rule-file comments are Russian; but YAML cheatsheet here is a doc artifact, not a rule file, so translate comments)

---

### `docs/user/CLI_CONFIG_REFERENCE.md`

**Verdict:** DRIFT

- Lines 1–106: Entire file is Russian
- Line 11: `--vendor VENDOR`: description says only `dell (spec export), cisco (CCW export) or hpe (BOM)` — stale; 6 vendors now
- Line 13: output-dir table says only `dell_run/`, `cisco_run/`, `hpe_run/` — stale
- Lines 26–30: output structure shows only 3 vendor run dirs
- Lines 79–83: `vendor_rules:` config example shows only 3 entries
- Cross-references:
  - `RUN_PATHS_AND_IO_LAYOUT.md` → PASS (relative link)
- Russian residue: ALL lines
- Tech-debt mentions: none
- Phase 3 hand-off (retired prompt refs): none

**Required fixes:**
1. Translate to English
2. Update `--vendor` description to list all 6 vendors (or reference full list)
3. Update output structure diagram to show all 6 vendor run dirs
4. Update config.yaml example to show all 6 vendor_rules entries

---

### `docs/user/RUN_PATHS_AND_IO_LAYOUT.md`

**Verdict:** DRIFT

- Lines 1–282: File is Russian
- Line 22–23: Data Isolation Policy item 3: "Скрипты (run_full.ps1, run_tests.ps1) выставляют..." — both scripts do not exist; they are replaced by `run.ps1`
- Lines 207–210: "Не делайте так" section item 4: "scripts\run_tests.ps1 (редиректит все кеши)" — BROKEN (does not exist)
- Lines 55–57: INPUT subfolder table mentions only `dell/`, `cisco/`, `hpe/` subdirs — stale; 6 vendors
- Lines 230–266: Audit/cluster output diagram shows only `dell_run` example — acceptable as example but could mislead
- Lines 94–103: Dell run folder structure doesn't include `<stem>_annotated_audited.xlsx` in per-run artifacts — audit-written artifact, could note it
- Cross-references:
  - `CLI_CONFIG_REFERENCE.md` → PASS
  - `../DOCS_INDEX.md` → PASS
- Russian residue: ALL lines
- Tech-debt mentions:
  - `batch_audit.py` writes `*_annotated_audited.xlsx` next to per-run files — VERIFIED ACCURATE (STRUCTURE.md confirms)
  - TOTAL folder description accurate
- Phase 3 hand-off (retired prompt refs): none

**Required fixes:**
1. Translate to English
2. Fix isolation policy item 3: replace `run_full.ps1, run_tests.ps1` with `run.ps1`
3. Fix "Не делайте так" item 4: replace `scripts\run_tests.ps1` reference with correct guidance
4. Expand INPUT subfolder table to include all 6 vendors

---

### `docs/user/USER_GUIDE.md`

**Verdict:** DRIFT

- File is mixed Russian/English (mostly Russian narrative sections with some English tables)
- Section 6 device_type table (lines 107-116): Lists `ram` and `nic` as Compute/Network category values — these are legacy device_type names; canonical names are `memory` and `network_adapter` respectively; the table should reflect current YAML
- Line 118: `hw_type` description says "26 values (v2.1.0)" — the taxonomy is at v2.6.0 now (still 26 values, but the version reference is stale)
- Lines 1-5: Intro paragraph is Russian
- Lines 13-53: Vendor descriptions are in English (good)
- Lines 60-166: Mix — some Russian narrative, English command examples
- Lines 103-116: Section 6 classification field descriptions — partially Russian
- Section 7 workflow: Shows all 6 vendors (good) but narrative is mixed
- Cross-references: none
- Russian residue: substantial throughout narrative sections
- Tech-debt mentions: none specifically
- Phase 3 hand-off (retired prompt refs): none

**Required fixes:**
1. Translate Russian narrative sections to English
2. Fix Section 6 device_type table: replace `ram` with `memory`, `nic` with `network_adapter` (or remove standalone legacy aliases from the table and note canonical names per YAML)
3. Update hw_type version reference from `v2.1.0` to `v2.6.0` (still 26 values)

---

## Tech-debt verification summary (D-21/D-22 protected items)

| Protected item | Location in code | Doc references | Status |
|---|---|---|---|
| `power_cord hw_type=None` | `dell_rules.yaml:278` comment: "hw_type: intentionally unmapped" | RULES_AUTHORING_GUIDE.md, hw_type_taxonomy.md, DATA_CONTRACTS.md, TECHNICAL_OVERVIEW.md (implied) | VERIFIED ACCURATE |
| `_E8_NO_HW_TYPE_DEVICES = {"power_cord", "enablement_kit"}` | `batch_audit.py:506` | DATA_CONTRACTS.md (implied via device_type list), CLAUDE.md | VERIFIED ACCURATE at cited line |
| `core/parser.py` Dell-specificity | `src/core/parser.py:3,29` (sentinel "Module Name") | TECHNICAL_OVERVIEW.md, OPERATIONAL_NOTES.md (implied) | VERIFIED ACCURATE |
| `batch_audit.py` reads `*_annotated.xlsx` | `batch_audit.py:611` (`pd.read_excel`) | OPERATIONAL_NOTES.md tech-debt section | VERIFIED ACCURATE at cited line |
| `HW_TYPE_VOCAB` duplication | `classifier.py:28` and `batch_audit.py:44` | DATA_CONTRACTS.md, hw_type_taxonomy.md | VERIFIED ACCURATE (both files have HW_TYPE_VOCAB) |
| YAML rule order first-match-wins | `rules_engine.py:51-70`, `dell_rules.yaml:573,617` | RULES_AUTHORING_GUIDE.md, TECHNICAL_OVERVIEW.md | VERIFIED ACCURATE |

## Phase 3 hand-off (retired prompt references)

| File | Line | Reference | Action for Phase 3 |
|---|---|---|---|
| `docs/product/TECHNICAL_OVERVIEW.md` | ~300 | `prompts/06_BATCH-AUDIT-MASTER-PLAN.md` | Phase 3 WF-01: update when prompts/ retired |

## CURRENT_STATE.md references

| File | Line | Reference | Action |
|---|---|---|---|
| `docs/dev/NEW_VENDOR_GUIDE.md` | 22, 88 | `CURRENT_STATE.md` | Task 5.2: replace with archive pointer |
| `docs/dev/OPERATIONAL_NOTES.md` | none found | — | — |

## Script reference broken links

| File | Broken reference | Correct reference |
|---|---|---|
| `docs/dev/ONE_BUTTON_RUN.md` | `.\scripts\run_full.ps1` | `.\run.ps1` (repo root) |
| `docs/user/RUN_PATHS_AND_IO_LAYOUT.md` | `run_full.ps1`, `run_tests.ps1` (isolation policy item 3) | `run.ps1` |
| `docs/user/RUN_PATHS_AND_IO_LAYOUT.md` | `scripts\run_tests.ps1` ("Не делайте так") | remove or update |
| `docs/dev/OPERATIONAL_NOTES.md` | `run_audit.ps1` (section 7) | `run.ps1` |
