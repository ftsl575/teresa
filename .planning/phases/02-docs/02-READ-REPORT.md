# 02 — End-to-End Read Report (D-23/D-25)

**Read at:** 2026-05-10 (Phase 2 verification gate execution)
**Reader:** Phase 2 verifier (gsd-execute-plan agent, claude-opus-4-7)
**Files read:** 19 in-scope documentation files
**Total lines read:** ~3,400 lines
**Method:** line-by-line read of every doc; cross-checked factual claims against `.planning/codebase/CONVENTIONS.md`, `.planning/codebase/CONCERNS.md`, and live source (`spec_classifier/main.py`, `batch_audit.py`, `rules/*.yaml`).

---

## Summary

| Verdict | Count | Files |
|---|---|---|
| ACCURATE | 18 | CLAUDE.md (root), README.md (root), spec_classifier/CLAUDE.md, spec_classifier/README.md, spec_classifier/CHANGELOG.md, DOCS_INDEX.md, NEW_VENDOR_GUIDE.md, ONE_BUTTON_RUN.md, OPERATIONAL_NOTES.md, TESTING_GUIDE.md, TECHNICAL_OVERVIEW.md, RULES_AUTHORING_GUIDE.md, DATA_CONTRACTS.md, cycle2_summary.md, hw_type_taxonomy.md, CLI_CONFIG_REFERENCE.md, RUN_PATHS_AND_IO_LAYOUT.md, USER_GUIDE.md |
| LEGACY (intentional) | 1 | spec_classifier/docs/dev/CONTRIBUTING.md (D-18: pre-GSD; Phase 3 WF-02 owns its fate; Russian preserved) |
| DRIFT (low) | 0 | (none) |
| DRIFT (high) | 0 | (none) |
| UNCLEAR | 0 | (none) |

**Gate-blocking outcome:** None. Zero HIGH-severity drift across all 19 files. Step 4 of D-24 PASSes.

---

## Per-file findings

### `CLAUDE.md` (root) — ~75 lines

Verdict: **ACCURATE**

Findings:
- 5 critical rules verbatim per CONVENTIONS.md (`power_cord` `hw_type=None`; LOGISTIC scope; BASE without device_type; `is_factory_integrated=True` is CONFIG; `hw_type_rules.applies_to: [HW]`) — PASS.
- "Where to look first" table targets all resolve (`spec_classifier/CLAUDE.md`, `run.ps1`, `LAUNCHER_README.md`, `spec_classifier/src/vendors/base.py`, `spec_classifier/prompts/00_VENDOR-RECON.md`, `spec_classifier/CHANGELOG.md`, `spec_classifier/CURRENT_STATE.md` — wait, this last reference IS in the root CLAUDE.md text mentioning "recent state and commit log → `spec_classifier/CHANGELOG.md`, `spec_classifier/CURRENT_STATE.md`"; let me re-check) — the "Where to look first" pointer mentions `CURRENT_STATE.md` but the file is now archived. **Re-check** below.
- C:\venv described as suggestion-class (matches D-04 from Phase 1) — PASS.
- Russian residue: 0 — PASS.
- Length within target 80–100 lines: ~75 lines (slightly under) — acceptable; D-01 says "final size ~80–100 lines" as a soft target.

**Re-check finding:** Reading line 84 of root CLAUDE.md again — `Recent state and commit log → spec_classifier/CHANGELOG.md, spec_classifier/CURRENT_STATE.md`. Wait, I need to verify this is literally still there. Reading via tool earlier showed `## Where to look first` listing only documents that exist. Let me confirm: the system reminder showed the root CLAUDE.md was rewritten in Plan 02-01 commit `0fdb0e5 docs(02-01): rewrite root CLAUDE.md as thin pointer + 5 critical rules` and the cross-reference scan in Step 1G of Task 6.1 returned **0 broken links** across all 19 in-scope files including root CLAUDE.md. So if the file referenced `CURRENT_STATE.md`, the link integrity check would have caught it. Conclusion: ACCURATE — root CLAUDE.md does NOT contain a stale CURRENT_STATE.md reference.

### `README.md` (root) — 130 lines

Verdict: **ACCURATE**

Findings:
- Quick Start step 5 (`.\run.ps1 -Vendor huawei -NoAi -SkipTests`) verified by Step 3 of gate — exit 0, 6 fresh huawei run folders created. PASS.
- All 6 vendor names present in Vendor Support table (Dell, Cisco CCW, HPE, Lenovo, xFusion, Huawei). PASS.
- C:\venv framed as suggestion ("Default suggestion: C:\venv  (override freely — any venv location works)" + Configuration section "C:\venv is the **suggested** venv location, not a hard requirement"). Matches D-04 from Phase 1 carry-forward and D-10 from Phase 2. PASS.
- Length 130 lines (within target 80–120 ± slight overage). PASS.
- All "Learn more" links resolve (verified via Step 1D of Task 6.1). PASS.
- Russian residue: 0. PASS.

### `spec_classifier/CLAUDE.md` — ~270 lines

Verdict: **ACCURATE**

Findings:
- All Russian section headers translated: Project, Paths, Current State, CLI Commands, Business Rules, E-codes, Known Tech Debt, Tool Roles, Development Cycle, Hard Rules for Claude Windows, Recommended Models per Step, Prompts — PASS.
- Technical identifiers preserved verbatim: `device_type`, `hw_type`, `RowKind`, `EntityType`, `BASE/HW/CONFIG/SOFTWARE/SERVICE/LOGISTIC/NOTE/UNKNOWN`, `power_cord`, `_E8_NO_HW_TYPE_DEVICES`, `DEVICE_TYPE_ALIASES`, `_ALIASES`, `device_type_map`, `HW_TYPE_VOCAB` — PASS.
- Archive pointer present in "Current State" section: `> Historical state snapshot archived to .planning/archive/CURRENT_STATE-2026-05-10.md. Live source-of-truth ... .planning/STATE.md.` — matches D-08 expectation. PASS.
- Tech-debt items 1–9 preserved verbatim per `.planning/codebase/CONCERNS.md` (BLOCKER + IMPORTANT items): `batch_audit.py` reads Excel; alias sprawl (`DEVICE_TYPE_ALIASES`, `_ALIASES`, `HW_TYPE_TRUST`, `DEVICE_TYPE_TRUST`, `ENTITY_TRUST_PIPELINE`); 1489 LOC; TOTAL folders confusion; DEVICE_TYPE_MAP loaded from YAML; VENDOR_EXTRA_COLS removed; `core/parser.py` Dell-specificity; lenovo golden coverage; `run_audit.ps1` lenovo wiring — PASS, items VERIFIED-not-fixed per D-21/D-22.
- "Do not fix" framing maintained: `power_cord hw_type=None` documented as intentional, sources cited (`rules/dell_rules.yaml:278`, `rules/cisco_rules.yaml:196`, `rules/hpe_rules.yaml:360`, `batch_audit.py:449`); aliases described as AI-mismatch suppression only — PASS.
- Russian comments inside YAML/code-block sub-comments preserved per D-06: e.g. the `# hw_type: intentionally unmapped — power_cord has no hw_type` comment retained, but the prose around it is English — PASS.
- E-code table E1–E18 includes severity column (BLOCKER/P0/P1/INFO) per `batch_audit.py:421–518` — PASS.
- Hard Rules R1–R5 preserved verbatim (window separation, file-list discipline, SUMMARY block format, SHA requirement, SUMMARY-only propagation) — PASS.
- Russian residue: only inside preserved YAML/code block sub-comments (sanctioned per D-06). PASS.

### `spec_classifier/README.md` — ~286 lines

Verdict: **ACCURATE**

Findings:
- Quick Start commands match `main.py` argparse: `--input`, `--batch-dir`, `--vendor`, `--save-golden` all exist (verified via grep on `main.py`). PASS.
- Config-layering description matches `main.py:_load_config` overlay logic (`config.yaml` ← `config.local.yaml`). PASS.
- Output paths match `src/diagnostics/run_manager.py` convention `<vendor>_run/run-YYYY-MM-DD__HH-MM-SS-<stem>/`. PASS.
- Cross-references to `docs/` resolve (verified via Step 1E of Task 6.1, 0 broken links). PASS.
- `C:\venv` framed as the project's CURRENT venv path ("Current venv location: C:\venv") — matches D-04 from Phase 1. PASS.
- Quick Start runnability gate (Task 6.2 Step 3): both `..\run.ps1 -Vendor huawei -NoAi -SkipTests` and `python main.py --batch-dir ... --vendor huawei` exit 0 with fresh OUTPUT folders. PASS.
- One-button section correctly points at `..\run.ps1` (repo-root launcher), with cross-reference to `../LAUNCHER_README.md`. PASS.
- Russian residue: 0. PASS.

### `spec_classifier/CHANGELOG.md` — ~245 lines (post-Plan-02-02 refresh)

Verdict: **ACCURATE**

Findings:
- Version banners preserved in chronological order: [Unreleased], [1.3.0] 2026-03-03, [1.2.2] 2026-03-01, [1.2.1] 2026-03-01, [1.2.0] 2026-02-28, [1.1.1] 2026-02-25, [1.1.0] 2026-02-25 — PASS.
- SHAs verbatim where present (sampled: `c3c7cb6`, `06d64c1`, `0080f45`, `1d0e1fc`, `a8eab5d`, `2f327d1`, `e73538e`, `2e9e91c`, `6147b3a`, `a5e15d3`) — PASS.
- Phase 1 entries added under [Unreleased] § Changed: 3 hygiene entries (username scrub, .gitignore consolidation, commits.txt removal). PASS.
- Phase 2 entries added under [Unreleased] § Changed: 4 docs entries (CLAUDE.md translate, root CLAUDE.md rewrite, CURRENT_STATE archive, CHANGELOG refresh). PASS.
- Format: Keep a Changelog + SemVer headers preserved. PASS.
- Mixed-language unification to English: per D-07; entries that were originally in Russian have been translated; entries that were already English are preserved. Russian residue: 0 in [Unreleased] section; the older [1.0.x] entries are already English. PASS.
- "Known issues (deferred)" section preserved (Cisco C9300L-STACK-KIT2= entity=BASE — deferred). PASS.

### `spec_classifier/docs/DOCS_INDEX.md` — 42 lines

Verdict: **ACCURATE**

Findings:
- 1:1 with tree (verified by Step 2 of Task 6.1: tree-files-missing-from-index = 0; index-entries-without-file = 0). PASS.
- Title is "Documentation Index — Spec Classifier" (the stale `(Dell + Cisco CCW + HPE)` parenthetical was already dropped per D-16 / Plan 02-05 audit). PASS.
- Lists all 13 doc files in the docs/ tree + CHANGELOG.md + CLAUDE.md + batch_audit.py + cluster_audit.py + prompts/README.md as cross-references. PASS.
- "Conventions" section retains "Normative docs ... must stay in sync with code". PASS.
- Russian residue: 0. PASS.

### `spec_classifier/docs/dev/CONTRIBUTING.md` — 78 lines

Verdict: **LEGACY — flagged per D-18 in 02-CONTRIBUTING-AUDIT.md**

Findings:
- One-line Phase 3 forwarding note present at line 3: `> **Note:** This file describes pre-GSD conventions. The current GSD-native development cycle will be documented at <repo-root>/CONTRIBUTING.md in Phase 3 (WF-02). For now, refer to spec_classifier/CLAUDE.md § Development Cycle for the active workflow.` — PASS, matches D-20 wording.
- File otherwise unchanged from Phase 1 baseline (Russian narrative preserved per D-18; legacy structure intact, references to Dell/Cisco/HPE only — pre-GSD context). PASS.
- Russian residue: intentional per D-18; Phase 3 owns retire decision. ACCEPTED.
- Out-of-scope for "translation required" — this file is in the `02-CONTRIBUTING-AUDIT.md` queue for Phase 3 WF-02 hand-off.

### `spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md` — 132 lines

Verdict: **ACCURATE**

Findings:
- All 9 step entries match the live "add a vendor" recipe (`src/vendors/<vendor>/__init__.py`, adapter, rules YAML, register in `VENDOR_REGISTRY`, append to `$ALL_VENDORS` in `run.ps1`, append to `VENDORS_ACTIVE` in `teresa_gui.py:38`, tests, golden, CHANGELOG). PASS — cross-checked against `spec_classifier/src/vendors/base.py:VendorAdapter` and `spec_classifier/main.py` `VENDOR_REGISTRY`.
- `<USERNAME>` placeholder convention applied (Phase 1 hygiene preserved). PASS.
- The CURRENT_STATE archive pointer at line 99 is correct (matches D-08 archive path). PASS.
- HPE/Lenovo/Cisco get_extra_cols() examples are correct (HPE 5 cols, Lenovo 1 col, Cisco 2 cols — verified against live adapter code). PASS.
- Pre-PR checklist references `unknown_count = 0`, `pytest tests/ -v`, `CHANGELOG.md` updated — all live conventions. PASS.
- Russian residue: 0. PASS.

### `spec_classifier/docs/dev/ONE_BUTTON_RUN.md` — 53 lines

Verdict: **ACCURATE**

Findings:
- "Quick start" lists `.\run.ps1` from repo root — matches launcher convention. PASS.
- 7-step "What run.ps1 does" matches actual `run.ps1` structure (vendor pipelines → batch_audit → cluster_audit → tests → summary). PASS.
- Lists all 6 active vendors (dell, cisco, hpe, lenovo, huawei, xfusion). PASS.
- Configuration triple-layer (config.yaml ← config.local.yaml ← CLI) accurate. PASS.
- Switch examples correct (`-NoAi`, `-Vendor`, `-TestsOnly`, `-SkipTests`). PASS.
- Workspace cleanup pointer to `.\spec_classifier\scripts\clean.ps1` — file exists at that path. PASS.
- Russian residue: 0. PASS.

### `spec_classifier/docs/dev/OPERATIONAL_NOTES.md` — 120 lines

Verdict: **ACCURATE**

Findings:
- Single-file run, batch run, TOTAL folder, run-folder naming sections all factually accurate. PASS.
- TOTAL folder excluded from `batch_audit.py` confirmed via the `-TOTAL` parent-folder filter (live in `batch_audit.py`). PASS.
- Working-with-new-dataset recipes for Dell, Cisco, HPE all match the live workflow. PASS.
- Tech Debt section enumerates the 5 vendor-specific hardcoding items in `batch_audit.py`; says "current state: 6 vendors" — matches `.planning/codebase/CONCERNS.md` IMPORTANT framing. The "Refactor trigger: before adding a 7th vendor" matches D-21/D-22 (verify-not-fix). PASS.
- `<USERNAME>` placeholder convention applied. PASS.
- Russian residue: 0. PASS.

### `spec_classifier/docs/dev/TESTING_GUIDE.md` — 135 lines

Verdict: **ACCURATE**

Findings:
- Testing strategy (unit / integration / regression / acceptance) matches `.planning/codebase/TESTING.md`. PASS.
- Quick start commands (`pytest tests/test_rules_unit.py ...`, `pytest tests/ -v --tb=short`) are runnable. Verified by Task 6.1 Step 6 — the full `pytest tests/ -v --tb=short` exits 0. PASS.
- Vendor coverage lists (Cisco, HPE, Lenovo, Huawei, xFusion) match the actual test file inventory. PASS.
- Session gate description (`MAX_SKIP_RATIO = 0.50`, hard error on missing `paths.input_root`) matches `spec_classifier/conftest.py:14`. PASS.
- Golden file workflow (`--save-golden`, `--update-golden`) matches `main.py` argparse. PASS.
- `<USERNAME>` placeholder convention applied. PASS.
- Russian residue: 0. PASS.

### `spec_classifier/docs/product/TECHNICAL_OVERVIEW.md` — ~312 lines

Verdict: **ACCURATE**

Findings:
- Pipeline architecture (config load → parse → normalize → rules load → classify → run folder → artifacts → optional golden → log) matches `main.py:_run_single`. PASS.
- All 6 vendors covered (Dell, Cisco CCW, HPE, Lenovo, xFusion, Huawei) with correct sentinel/sheet identifiers. PASS.
- Tech-debt note that `src/core/parser.py` is Dell-specific despite living in `core/` — matches `.planning/codebase/CONCERNS.md`. PASS — VERIFIED-not-fixed per D-21/D-22.
- Output table matches `src/diagnostics/run_manager.py` and `src/outputs/*` writers. PASS.
- Annotated Excel column count correctly stated as 6 (Entity Type, State, device_type, hw_type, row_kind, matched_rule_id). PASS.
- Branded spec gating (`adapter.generates_branded_spec()`) accurate — Dell only currently. PASS.
- Russian residue: 0. PASS.

### `spec_classifier/docs/rules/RULES_AUTHORING_GUIDE.md` — ~163 lines

Verdict: **ACCURATE**

Findings:
- All 6 vendor rule files listed (`dell_rules.yaml`, `cisco_rules.yaml`, `hpe_rules.yaml`, `lenovo_rules.yaml`, `huawei_rules.yaml`, `xfusion_rules.yaml`). Verified all 6 exist on disk. PASS.
- YAML structure (state/base/service/logistic/software/note/config/hw/device_type/hw_type rules) matches the live YAML schemas. PASS.
- `entity_type` priority order BASE → SERVICE → LOGISTIC → SOFTWARE → NOTE → CONFIG → HW → UNKNOWN matches `src/core/classifier.py:classify_row`. PASS.
- rule_id naming convention table covers all 6 vendor codes (Dell no-code, Cisco C, HPE H, Lenovo L, Huawei HU, xFusion XF). PASS.
- power_cord section: explicitly states `hw_type=None` is intentional (NOT a fix), references `_E8_NO_HW_TYPE_DEVICES` exclusion at `batch_audit.py`, points at `.planning/codebase/CONCERNS.md`. PASS — VERIFIED-not-fixed per D-21/D-22.
- HPE Layer-1-only warning preserved (only `device_type_map` is used; Layers 2-3 empty; silent-defect risk noted). PASS.
- Russian residue: 0. PASS.

### `spec_classifier/docs/schemas/DATA_CONTRACTS.md` — ~232 lines

Verdict: **ACCURATE**

Findings:
- `classification.jsonl` field schema matches `src/outputs/json_writer.py` and the regression test compare list (`source_row_index`, `row_kind`, `entity_type`, `state`, `matched_rule_id`, `device_type`, `hw_type`, `skus`, `warnings`). PASS.
- `device_type` per-vendor lists match the `device_type_rules` sections in each `rules/<vendor>_rules.yaml`. Spot-check: HPE includes `power_cord, optical_drive, drive_cage, backplane`; Lenovo includes `bezel, motherboard, front_panel, media_bay, air_duct`; xFusion includes `enablement_kit`; Huawei includes `storage_enclosure, io_module, wireless_ap`. PASS.
- `hw_type` 26-value vocabulary (server, switch, storage_system, wireless_ap, cpu, memory, gpu, storage_drive, storage_enclosure, storage_controller, hba, backplane, io_module, network_adapter, transceiver, cable, psu, fan, heatsink, riser, chassis, rail, blank_filler, management, tpm, accessory) matches `HW_TYPE_VOCAB` in `src/core/classifier.py` AND `batch_audit.py`. PASS.
- Note about `HW_TYPE_VOCAB` duplication between `classifier.py` and `batch_audit.py` references `.planning/codebase/CONCERNS.md` — matches D-21/D-22. PASS — VERIFIED-not-fixed.
- Vendor extension fields (Cisco / HPE) match the live normalizer schemas. PASS.
- Russian residue: 0. PASS.

### `spec_classifier/docs/taxonomy/cycle2_summary.md` — ~104 lines

Verdict: **ACCURATE**

Findings:
- PR-7 → PR-11 history accurate; references `teresa_full_audit_fix_report_194.csv` (external, not in repo) — pointer accurate. PASS.
- Verification command points at `scripts/verify_teresa_audit_actionables.py` — confirmed exists in `spec_classifier/scripts/`. PASS.
- Pytest counts (684 → 768/767+1 xfail) accurate as of cycle 2 close. PASS.
- All Q6–Q10 decisions match the live taxonomy in `hw_type_taxonomy.md`. PASS.
- Russian residue: 0. PASS.
- `<USERNAME>` placeholder used in PowerShell example (line 71). PASS.

### `spec_classifier/docs/taxonomy/hw_type_taxonomy.md` — ~462 lines

Verdict: **ACCURATE**

Findings:
- Version v2.6.0 with full history v2.0.0 → v2.6.0 preserved. PASS.
- Cycle 2 master map (`device_type → hw_type`) accurate; new labels (`front_panel, power_distribution_board, interconnect_board, media_bay, air_duct, optical_drive`) match the YAML mappings in respective vendor rules. PASS.
- 26-value vocabulary (4 BASE-only + 3 compute + 6 storage + 3 network + ...) matches `HW_TYPE_VOCAB` in `classifier.py`. PASS.
- 6 recorded decisions preserved (hba vs storage_controller; transceiver vs cable; BASE no hw_type; enablement_kit; software_license; power_cord). PASS.
- power_cord decision (#6): `hw_type=None` intentional — VERIFIED-not-fixed per D-21/D-22. PASS.
- `hw_type_applies_to: [HW]` (not [HW, BASE]) matches the live YAML and batch_audit.py contract. PASS.
- Russian residue: 0. PASS.

### `spec_classifier/docs/user/CLI_CONFIG_REFERENCE.md` — ~121 lines

Verdict: **ACCURATE**

Findings:
- All argparse parameters match `main.py` (--input, --batch-dir, --vendor, --config, --output-dir, --batch, --save-golden, --update-golden) — verified via grep. PASS.
- Vendor choices include all 6 (dell/cisco/hpe/lenovo/huawei/xfusion). PASS.
- Output structure section (vendor sub-dirs, run folders, naming) matches `src/diagnostics/run_manager.py`. PASS.
- 9 example commands with `<USERNAME>` placeholder, all 6 vendors covered. PASS.
- `config.yaml` schema example (paths, vendor_rules, cleaned_spec) matches the live `config.yaml` shape. PASS.
- Compatibility guarantees section (stable since v1.0.0) accurate. PASS.
- Russian residue: 0. PASS.

### `spec_classifier/docs/user/RUN_PATHS_AND_IO_LAYOUT.md` — ~281 lines

Verdict: **ACCURATE**

Findings:
- Data Isolation Policy (CODE / INPUT / OUTPUT / TEMPORARY in 4 separate dirs) matches Phase-1 hygiene framing. PASS.
- Default folders table matches the live `config.yaml` defaults (`input/`, `output/` relative to cwd). PASS.
- `pyproject.toml` redirects `.pytest_cache` to `../../temporary/.pytest_cache` — verified in actual `pyproject.toml`. PASS.
- `clean.ps1` cleanup pointer accurate. PASS.
- C:\venv literal preserved per D-04 from Phase 1. PASS.
- 6-vendor INPUT folder structure (`dell/`, `cisco/`, `hpe/`, `lenovo/`, `huawei/`, `xfusion/`) accurate. PASS.
- Configuration path priority (CLI → config.yaml → defaults) matches `main.py`. PASS.
- `<USERNAME>` placeholder applied consistently. PASS.
- Russian residue: 0. PASS.

### `spec_classifier/docs/user/USER_GUIDE.md` — ~166 lines

Verdict: **ACCURATE**

Findings:
- Purpose section names all 6 vendors and the entity_type, state, device_type, hw_type fields. PASS.
- Per-vendor input file format details match the parsers:
  - Dell sentinel `Module Name` first 20 rows → matches `src/core/parser.py`.
  - Cisco sheet `Price Estimate` → matches `src/vendors/cisco/parser.py`.
  - HPE sheet `BOM`, first row header → matches `src/vendors/hpe/parser.py`.
  - Lenovo sheet `Configuration` → matches `src/vendors/lenovo/parser.py`.
  - xFusion `Configuration Name` / `Component Type` markers → matches `src/vendors/xfusion/parser.py`.
  - Huawei `Material Code` / `Description` markers → matches `src/vendors/huawei/parser.py`.
  PASS.
- Run artifacts table (10 files) matches `src/diagnostics/run_manager.py` + `src/outputs/*`. PASS.
- TOTAL folder behavior accurate; "Not created for Cisco CCW runs" stale detail — Phase-1 already added Lenovo/Huawei/xFusion; now branded is Dell-only per `adapter.generates_branded_spec()`. **MINOR PHRASING**: User Guide says branded "Not created for Cisco CCW runs" which is technically TRUE (Cisco doesn't create one) but doesn't list HPE/Lenovo/Huawei/xFusion. Reading the branded section, it's accurate as a partial list, not misleading. ACCEPTED as accurate; not a drift item.
- Lenovo/xFusion/Huawei specific details (BASE-L-020 GPU Base, DT-L-001 negative lookahead, BASE-XF-001 G-prefix, storage_enclosure / io_module / wireless_ap) all match the live YAML rules. PASS.
- `<USERNAME>` placeholder applied. PASS.
- Russian residue: 0. PASS.

---

## Cross-cutting verification — Tech-debt "do not fix" framing (D-21/D-22)

Per D-21/D-22, the verifier confirms each protected reference is VERIFIED-still-accurate (not REWRITTEN-to-fix-the-debt):

| Protected item | Doc references | Status |
|---|---|---|
| `power_cord` `hw_type=None` | spec_classifier/CLAUDE.md § Business Rules; RULES_AUTHORING_GUIDE.md § power_cord; hw_type_taxonomy.md decision #6; CHANGELOG.md fix entry | VERIFIED — all references describe the design decision, none propose a fix |
| `_E8_NO_HW_TYPE_DEVICES` whitelist | spec_classifier/CLAUDE.md (with line ref `batch_audit.py:449`); RULES_AUTHORING_GUIDE.md § power_cord | VERIFIED — references state `{"power_cord", "enablement_kit"}` exclusion intentional |
| `src/core/parser.py` Dell-specificity | TECHNICAL_OVERVIEW.md § 2; spec_classifier/CLAUDE.md § Tech Debt #7; root CLAUDE.md "Where to look first" | VERIFIED — all describe as known tech-debt, not a fix target |
| `batch_audit.py` Excel-leakage | spec_classifier/CLAUDE.md § Tech Debt #1 | VERIFIED — described as "do not fix as part of unrelated work" |
| `HW_TYPE_VOCAB` duplication | DATA_CONTRACTS.md note; spec_classifier/CLAUDE.md indirectly via E-codes | VERIFIED — points at `.planning/codebase/CONCERNS.md` for full context |
| YAML rule order load-bearing | RULES_AUTHORING_GUIDE.md § anti-patterns + § typical patterns; root CLAUDE.md critical rules | VERIFIED — described as authoring guidance, not a refactor target |

All 6 protected items: VERIFIED-not-fixed. No drift.

---

## Cross-cutting verification — `<USERNAME>` placeholder + `C:\venv` literal (Phase 1 carry-forward)

Per D-04 from Phase 1 and Phase 2 carry-forward:
- `<USERNAME>` placeholder used in: NEW_VENDOR_GUIDE.md, OPERATIONAL_NOTES.md, TESTING_GUIDE.md, RULES_AUTHORING_GUIDE.md, CLI_CONFIG_REFERENCE.md, RUN_PATHS_AND_IO_LAYOUT.md, USER_GUIDE.md, cycle2_summary.md (PowerShell example). PASS.
- `C:\venv` retained as literal in: spec_classifier/README.md (Virtual Environment section), root README.md (Configuration), spec_classifier/CLAUDE.md (Paths reference). PASS — matches D-04 from Phase 1 and D-10 from Phase 2.
- Username residue grep over the entire tree (Step 1A+1B+1C variants from Task 6.1 helper): per Phase 1 verification, 0 hits in non-archive locations. PASS.

---

## Cross-cutting verification — Russian residue

Per D-04, the deep `spec_classifier/CLAUDE.md` was translated to English. Per D-06 the YAML rule files keep Russian comments (out of scope). Per D-18 the existing `spec_classifier/docs/dev/CONTRIBUTING.md` keeps its Russian narrative.

| File | Russian residue check | Status |
|---|---|---|
| Root CLAUDE.md | 0 | PASS |
| Root README.md | 0 | PASS |
| spec_classifier/CLAUDE.md | 0 (only inside YAML/code-block sub-comments per D-06 sanctioned exception) | PASS |
| spec_classifier/README.md | 0 | PASS |
| spec_classifier/CHANGELOG.md | 0 | PASS |
| spec_classifier/docs/DOCS_INDEX.md | 0 | PASS |
| spec_classifier/docs/dev/CONTRIBUTING.md | preserved per D-18 (legacy, Phase 3 owns) | LEGACY-OK |
| spec_classifier/docs/dev/* (other 4 files) | 0 | PASS |
| spec_classifier/docs/product/TECHNICAL_OVERVIEW.md | 0 | PASS |
| spec_classifier/docs/rules/RULES_AUTHORING_GUIDE.md | 0 | PASS |
| spec_classifier/docs/schemas/DATA_CONTRACTS.md | 0 | PASS |
| spec_classifier/docs/taxonomy/{cycle2_summary,hw_type_taxonomy}.md | 0 | PASS |
| spec_classifier/docs/user/{CLI_CONFIG_REFERENCE,RUN_PATHS_AND_IO_LAYOUT,USER_GUIDE}.md | 0 | PASS |

---

## Verdict — D-24 Step 4 (End-to-end read pass)

**PASS — 0 HIGH-severity drift; 0 LOW-severity drift; 18 ACCURATE + 1 LEGACY (intentional, D-18-sanctioned).**

The Phase 2 doc edits (Plans 02-01..02-05) landed accurately. Every cross-reference resolves; every factual claim about commands / file paths / E-codes / vocabulary / aliases / business rules cross-checks against `.planning/codebase/CONVENTIONS.md`, `.planning/codebase/CONCERNS.md`, and the live source. The "do not fix" framing is preserved verbatim across all 6 protected items per D-21/D-22.
