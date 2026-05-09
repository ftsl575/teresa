# Codebase Concerns

**Analysis Date:** 2026-05-10

This document is grouped by severity:

- **BLOCKER** — actively breaks correctness, security, or portability if mishandled. Mistakes here have caused real regressions and are bait for "fix" PRs that revert recovery work.
- **IMPORTANT** — fragile or load-bearing implementation that will silently degrade output if perturbed.
- **NICE-TO-FIX** — quality / DX issues that don't gate functionality but compound over time.

---

## BLOCKER

### `power_cord` has `hw_type=None` intentionally — do NOT "fix"

- Files:
  - `spec_classifier/rules/dell_rules.yaml:278` — `# hw_type: intentionally unmapped — power_cord has no hw_type`
  - `spec_classifier/rules/cisco_rules.yaml` (same comment near line 196 per project CLAUDE.md)
  - `spec_classifier/rules/hpe_rules.yaml` (same comment near line 360 per project CLAUDE.md)
  - `spec_classifier/batch_audit.py:506` — `_E8_NO_HW_TYPE_DEVICES = {"power_cord", "enablement_kit"}` excludes it from E8
  - `spec_classifier/batch_audit.py:375` — `"power_cord": "cable"` in `DEVICE_TYPE_ALIASES`
- Risk: Adding `power_cord` to `device_type_map` or removing it from the E8 exclusion set will cascade through six vendor YAMLs, change goldens, and trip E10 / E9 mismatch errors. The repo's own root `CLAUDE.md` and `spec_classifier/CLAUDE.md` flag this as a recurring "fix" target. There is a recorded recovery commit: `c3c7cb6 fix(taxonomy): restore power_cord hw_type=None`.
- Current mitigation: Comment in every rules YAML. Project CLAUDE.md describes the rule. `_E8_NO_HW_TYPE_DEVICES` whitelist guards the audit.
- Recommendations: When refactoring rules or audits, treat `power_cord` (and `enablement_kit`) as load-bearing exceptions. Verify both YAMLs and `batch_audit.py` together. The `power_cord ≈ cable` alias in `DEVICE_TYPE_ALIASES` is **only** AI-mismatch suppression — never use it to derive `hw_type`.

### `core/parser.py` is Dell-specific despite living in `core/`

- Files:
  - `spec_classifier/src/core/parser.py` — module docstring: *"Excel parser for column-based specification files (used by DellAdapter). Finds header row by a sentinel column value ('Module Name')"*
  - `spec_classifier/src/core/parser.py:29` — hard-coded sentinel `"Module Name"`
  - `spec_classifier/src/vendors/dell/adapter.py:3` — `from src.core.parser import parse_excel`
  - All other vendors have their own parsers in `src/vendors/<v>/parser.py` (cisco, hpe, lenovo, huawei, xfusion)
- Risk: Naming suggests a generic core utility. A future engineer may re-use `parse_excel` for a new vendor and silently get Dell semantics (sentinel `"Module Name"`, 1-based row index convention). Project CLAUDE.md (`spec_classifier/CLAUDE.md` § Tech Debt #7) and root CLAUDE.md flag this explicitly.
- Current mitigation: Docstring says "used by DellAdapter". Other vendor adapters route through their own `parser.py`.
- Fix approach: Move to `src/vendors/dell/parser.py`, leave a thin compatibility shim in `core/` if needed, or rename to `dell_parser.py`. Update `src/vendors/dell/adapter.py` import. Out of scope of any unrelated PR — file should be moved as a standalone refactor with golden re-verification.

### `batch_audit.py` reads from `*_annotated.xlsx` instead of `classification.jsonl`

- Files:
  - `spec_classifier/batch_audit.py:611` — `df_raw = pd.read_excel(source_path, header=None, dtype=str, engine="openpyxl")`
  - `spec_classifier/batch_audit.py:1339-1351` — `find_annotated_files()` globs `*_annotated.xlsx` (excluding `_audited` and `-TOTAL`)
  - `spec_classifier/batch_audit.py:642-646` — `_ALIASES = {"description": "option_name", ...}` re-aliases vendor columns from Excel headers
- Risk: Excel is a presentation artifact. Reading it back means audit depends on `annotated_writer` column shape, vendor extension columns (`get_extra_cols()`), and de-duplication logic at `batch_audit.py:625-636`. The canonical `classification.jsonl` is bypassed entirely. Column ordering / renaming changes in `annotated_writer.py` will silently break the audit.
- Current mitigation: Header detection is name-based (`"entity type" in vals`), not index-based. Vendor-specific column aliases re-mapped in `batch_audit.py:642-646` and again at `batch_audit.py:1482`.
- Fix approach: Switch reader to `<run_folder>/classification.jsonl` + `rows_normalized.json`. Eliminate `_ALIASES` Excel-column dictionary. Project CLAUDE.md explicitly says **do not "fix" this as part of unrelated work** — it requires a dedicated migration and re-verification of all E-codes.

---

## IMPORTANT

### YAML rule order is load-bearing (first-match-wins)

- Files:
  - `spec_classifier/src/core/classifier.py:218` — `# Layer 3: regex rules (first match wins)`
  - `spec_classifier/src/rules/rules_engine.py:51-70` — `match_rule()` iterates and returns first match
  - `spec_classifier/src/rules/rules_engine.py:73-90` — `match_device_type_rule()` first-match-wins
  - `spec_classifier/src/rules/rules_engine.py:93-107` — `match_hw_type_rule()` first-match-wins
  - `spec_classifier/rules/dell_rules.yaml:322` — `# HW — order matters: more specific first`
  - `spec_classifier/rules/dell_rules.yaml:617` — `# Layer 3: regex rules (first match wins, ORDER MATTERS)`
- Risk: Any YAML reordering during cosmetic edit or merge can silently flip classification. Regression tests catch most cases via `golden/*_expected.jsonl`, but golden coverage is incomplete.
- Current mitigation: Per-YAML comments, `tests/test_huawei_rules_unit.py:212` (`test_first_match_wins_nvme_before_hdd`), regression tests against golden JSONL.
- Recommendations: Add a lint that detects rule reordering across diff hunks; surface "more specific first" pattern explicitly in `RULES_AUTHORING_GUIDE.md`. Never `sort` rule blocks alphabetically.

### `config.local.yaml` overlay logic is duplicated in 4+ places with divergent semantics

- Files:
  - `spec_classifier/main.py:69-86` — `_load_config()` overlays `config.local.yaml` over `config.yaml` (deep-merge dicts)
  - `spec_classifier/conftest.py:22-39` — `load_config()` does the same merge with the same logic
  - `spec_classifier/batch_audit.py:60-70` — `_load_config()` does a *flat* overlay (`cfg.update(local_cfg)`, NOT deep-merge)
  - `spec_classifier/cluster_audit.py:24-36` — `_load_config()` also flat overlay
  - `run.ps1:36-40` — PowerShell regex parsing of `config.local.yaml` to read `input_root` / `output_root`
  - `teresa_gui.py:397-421` — Python regex parsing of `config.local.yaml` from the GUI
- Risk: `main.py` / `conftest.py` deep-merge `paths` dict; `batch_audit.py` / `cluster_audit.py` flat-overlay it. If `config.local.yaml` provides only `paths.input_root` and not `paths.output_root`, behavior diverges between the pipeline and the audit. PowerShell and PyQt6 each re-implement YAML parsing via regex — fragile to YAML quoting / multiline.
- Current mitigation: `config.local.yaml.example` only shows full `paths:` block, masking the divergence in practice.
- Fix approach: Extract a single `load_config_with_local()` helper module under `src/` and import everywhere (including `cluster_audit.py` and `batch_audit.py`). For the launcher and GUI, shell out to `python -m spec_classifier.config.print_paths` rather than re-parsing YAML.

### Test suite gates on `skipped/total > 0.50` — fragile when INPUT data is missing

- Files:
  - `spec_classifier/conftest.py:14` — `MAX_SKIP_RATIO = 0.50`
  - `spec_classifier/conftest.py:141-217` — `pytest_sessionfinish()` forces session failure when ratio exceeded or `passed == 0`
  - `spec_classifier/conftest.py:189-194` — also fails session if `input_root` is missing entirely
- Risk: A clean clone with no INPUT data will always fail with cryptic "Skip guard triggered" rather than the more helpful "no test data". When the team rotates fixture sets between vendors, the ratio can blow past 0.50 even though all *active* tests pass. CI/CD or new contributors hit a hard wall.
- Current mitigation: `conftest.py:166-187` adds a "silent-skip risk detection" warning that prints when `input_root` exists but contains no `*.xlsx`. The README documents the requirement.
- Fix approach: Either drop the gate in favor of a `pytest -m needs_input` marker, or make the threshold configurable via env var (`TERESA_MAX_SKIP_RATIO`). At minimum, lower the noise: distinguish "no fixtures provided" (warn, exit 0) from "fixtures partially missing" (fail).

### Alias-table confusion between `device_type_map` and `DEVICE_TYPE_ALIASES`

- Files:
  - `spec_classifier/batch_audit.py:363-383` — `DEVICE_TYPE_ALIASES` (16 entries; AI-mismatch suppression only)
  - `spec_classifier/batch_audit.py:642-646` — `_ALIASES` (column-name aliases for Excel reading)
  - `spec_classifier/batch_audit.py:1482` — `_AL` (a third copy of column aliases inside `main()`)
  - `spec_classifier/rules/<vendor>_rules.yaml` `hw_type_rules.device_type_map` — the authoritative `device_type → hw_type` mapping
- Risk: Three different "alias" dictionaries with overlapping vocabulary. New contributors routinely confuse `DEVICE_TYPE_ALIASES` (semantic equivalence for AI-mismatch suppression) with `device_type_map` (vendor-specific `device_type → hw_type` mapping). The Lenovo `bezel→accessory` vs HPE `bezel→chassis` divergence is precisely this trap. Root CLAUDE.md and `spec_classifier/CLAUDE.md` warn explicitly.
- Current mitigation: Inline comments at `batch_audit.py:359-362` and `batch_audit.py:386-405`; `HW_TYPE_TRUST` and `DEVICE_TYPE_TRUST` whitelists block AI from disagreeing on physically obvious types.
- Fix approach: Rename `DEVICE_TYPE_ALIASES` to `AI_MISMATCH_SEMANTIC_EQUIVS` to make intent explicit. Move `_ALIASES` (Excel column aliases) into a vendor-aware function that consults `adapter.get_extra_cols()` rather than a hard-coded dict.

### `batch_audit.py` is a 1546-LOC god-object

- Files: `spec_classifier/batch_audit.py` (1546 lines)
- Risk: One file owns: E1–E18 rule logic, LLM prompt construction, OpenAI/Anthropic dispatch, Excel reading + writing, audit Excel writer with conditional formatting, `audit_summary.xlsx` human report builder, `audit_report.json` aggregator, `_build_claude_prompt()` text generator, file discovery, vendor detection from path, `KNOWN_FP_CASES` false-positive registry. Refactor risk is high.
- Current mitigation: 71 collected tests in `tests/test_batch_audit.py` exercise the public surface.
- Fix approach: Split into `audit/{rules.py, llm.py, excel_io.py, report.py, fp_registry.py}` package. Project CLAUDE.md (§ Tech Debt #3) acknowledges this.

### TOTAL aggregation folders cause file-discovery confusion

- Files:
  - `spec_classifier/main.py:315-318` — creates `total_folder` per batch run
  - `spec_classifier/main.py:191-194` — `copy_to_total()` duplicates branded/audited files
  - `spec_classifier/batch_audit.py:1345` — `files = [f for f in files if "-TOTAL" not in f.parent.name]` (defensive filter to avoid double-auditing)
- Risk: Audit and cluster steps must explicitly exclude `-TOTAL` folders or every file gets counted twice. New consumers of OUTPUT artifacts won't know to filter and will silently double-count.
- Current mitigation: Hard-coded filter at `batch_audit.py:1345`.
- Fix approach: Rename TOTAL folders with a leading character that natural globs miss, or replace with a manifest JSON. Project CLAUDE.md (§ Tech Debt #4) acknowledges this.

### LLM cost / latency unbounded under `--batch-dir`

- Files:
  - `spec_classifier/batch_audit.py:296-356` — `run_llm_predictions()` paginates 40 rows / batch with 0.3s sleep between batches (`batch_audit.py:353`)
  - `spec_classifier/batch_audit.py:235-240` — pricing table for `gpt-4o-mini` / `gpt-4o` / `claude-opus-4-5` / `claude-sonnet-4-5`
  - `spec_classifier/batch_audit.py:1255-1258` — `total_cost = (tok_in * pricing["in"] + tok_out * pricing["out"]) / 1_000_000`
- Risk: `run.ps1` runs AI audit by default after every per-vendor pipeline pass (`run.ps1:124-132`). On a 26-file × ~200-row batch the LLM hits ~130 batches per file and there is no `--max-cost-usd` kill switch. Pricing constants are hard-coded — model deprecation will cause silent miscalculation.
- Current mitigation: `--no-ai` flag; per-batch sleep limits API rate. `audit_report.json` records `cost_usd` after the fact.
- Fix approach: Add `--max-cost-usd N` arg that aborts mid-run, validate `llm_model` against `PRICING.keys()` and fail-fast on unknown model.

---

## NICE-TO-FIX

### Windows-only launcher; no POSIX path

- Files:
  - `run.ps1` — PowerShell only (uses `$env:USERPROFILE`, `Get-ChildItem`, `Set-Location`)
  - `teresa.bat` — CMD shim
  - `teresa_gui.py:189-208` — `set_env_key_windows_user()` shells out to `setx` (Windows-only)
  - `teresa_gui.py:518` — `os.startfile(str(p))` (Windows-only API)
  - `spec_classifier/scripts/clean.ps1` — PowerShell only
  - `spec_classifier/Makefile:19` — `INPUT ?= C:/Users/G/Desktop/INPUT` (Windows-style default)
  - `spec_classifier/README.md:21` — `Current venv location: C:\venv` (hard-coded)
- Risk: Linux/macOS contributors must call `python main.py` directly and lose the orchestrated audit + cluster flow. CI on a Linux runner can't use `run.ps1`.
- Current mitigation: `main.py`, `batch_audit.py`, `cluster_audit.py` are pure Python (POSIX-clean). `Path` objects throughout. `Makefile` uses forward slashes.
- Fix approach: Add `run.sh` that mirrors `run.ps1`. Replace `os.startfile` with platform dispatch. Document `C:\venv` as a *suggestion*, not a requirement, in README.

### `OPENAI_API_KEY` absence silently degrades to rule-only audit

- Files:
  - `spec_classifier/batch_audit.py:1418-1424` — when no key found, prints warning and sets `use_ai = False`
  - `run.ps1:79-90` — interactive `Read-Host` prompt only inside the launcher (and only when not `-NoAi`)
  - `teresa_gui.py:504-511` — GUI warns before launching when AI is checked but key absent
- Risk: A contributor can run `python batch_audit.py --output-dir OUTPUT` (default behavior is `use_ai=True`) without `OPENAI_API_KEY`. The script prints a warning and continues silently. The resulting `audit_report.json` records `model: "no-ai"` but the user-visible signal is one line of warning amid hundreds of progress bars.
- Current mitigation: Warning printed; `audit_report.json` `meta.model` field reflects degraded state.
- Fix approach: Promote to error unless `--no-ai` was passed explicitly. Add `--require-ai` flag to fail-fast in CI.

### `OPENAI_API_KEY` storage via `setx` / process env

- Files:
  - `teresa_gui.py:189-208` — `setx OPENAI_API_KEY ...` writes to Windows User-scope registry
  - `run.ps1:80-89` — captures key via `Read-Host -AsSecureString` then immediately decodes back to plaintext into `$env:OPENAI_API_KEY`
- Risk: `setx` persists the key in the user's Windows registry environment block. Any process the user runs inherits it. The `run.ps1` flow decrypts the SecureString back to plaintext (`SecureStringToBSTR` → `PtrToStringAuto`) — defeating the SecureString purpose. No prompt to confirm overwrite.
- Current mitigation: Gitignore covers `config.local.yaml`. No file-on-disk storage outside the registry.
- Fix approach: Use Windows Credential Manager (DPAPI) instead of `setx`. Document the registry storage so users can clear it (`setx OPENAI_API_KEY ""`).

### Excel input is untrusted user data, parsed via openpyxl/pandas

- Files: every `parse_excel` (`src/core/parser.py`, `src/vendors/<v>/parser.py`)
- Risk: `pd.read_excel(... engine="openpyxl")` and direct `openpyxl.load_workbook()` are the only entry points for untrusted user-supplied `.xlsx` files. openpyxl has a history of XML-bomb / zipbomb susceptibility (the file is a zip of XML). No size limit, no XML-entity check, no quarantine.
- Current mitigation: `read_only=True` is used in most adapters (`src/vendors/dell/adapter.py:13`, `src/vendors/hpe/parser.py:28`) which streams rows instead of loading the full document. `data_only=True` avoids formula evaluation.
- Fix approach: Add a pre-parse size cap (`pathlib.Path(p).stat().st_size > 50 * 2**20 → reject`) and a worksheet-count cap.

### TODO/FIXME markers in YAML rule files

- Files:
  - `spec_classifier/rules/xfusion_rules.yaml:25` — `# TODO: HiCare / Premier Support patterns — add when first SERVICE row appears.`
  - `spec_classifier/rules/xfusion_rules.yaml:28` — `# TODO: Freight / Insurance — currently on Summary sheet (not parsed).`
  - `spec_classifier/rules/huawei_rules.yaml:31` — `# TODO: add regex for HiCare/Warranty/Support Service when first SERVICE-file appears`
  - `spec_classifier/rules/huawei_rules.yaml:36` — `# TODO: add regex for Freight/Shipping/Delivery/Packaging`
- Risk: Huawei/xFusion service & logistic rules are placeholders. Files containing these row types will be classified UNKNOWN (E2 BLOCKER) until rules are written.
- Current mitigation: `cluster_audit.py` flags UNKNOWN clusters for human review.
- Fix approach: Track in a small ledger; close as fixtures appear.

### Hard-coded Windows paths in docs and `config.local.yaml.example`

- Files:
  - `spec_classifier/README.md:21,25,30,33,158,186,188,222,226,239,242,245,248,266,269,272,277` — `C:\venv` and `C:\Users\G\Desktop\INPUT` baked into examples
  - `spec_classifier/CLAUDE.md:29-32,61,110,113,116` — same
  - `spec_classifier/config.local.yaml.example:7-8,12` — `C:\\Users\\G\\Desktop\\INPUT` (user-name in committed example)
  - `spec_classifier/Makefile:19` — `INPUT ?= C:/Users/G/Desktop/INPUT`
  - `spec_classifier/docs/dev/TESTING_GUIDE.md:6,47,53,57,91,92,101` — same
- Risk: Onboarding friction. Examples lie about what the user should type. CHANGELOG records earlier rounds of cleanup (`fix: remove hardcoded Windows user paths from argparse defaults (CODE-001)` per `spec_classifier/CHANGELOG.md:191`) but README and example file still ship with `C:\Users\G\...`.
- Current mitigation: README has both relative-path Quick Start and absolute-path examples; runtime defaults via `Path.home() / "Desktop" / "INPUT"` in `teresa_gui.py:408`.
- Fix approach: Replace user-name in example file with `<USERNAME>` placeholder; use `<INPUT_ROOT>` token in docs.

### Generic `except Exception:` swallowing in audit / cluster paths

- Files:
  - `spec_classifier/batch_audit.py:91-94` — module-level config load: `except Exception: _device_type_map = {}` (silently disables E9 mapping check on YAML load failure)
  - `spec_classifier/batch_audit.py:291` — LLM call: `except Exception as e: print(f"⚠ LLM batch error: {e}"); return [], 0, 0`
  - `spec_classifier/batch_audit.py:1005,1492,1524` — Excel I/O / human-report writes
  - `spec_classifier/cluster_audit.py:140,199,510,538` — clustering failures swallowed with `print()`
  - `spec_classifier/conftest.py:136` — config-parse failure returns `None`
  - `spec_classifier/main.py:236` — pipeline-wide `except Exception: log.exception("Pipeline failed")`
- Risk: LLM failures on a single batch silently produce 0 predictions for those rows; downstream `audit_report.json` undercounts AI agreement without warning. Cluster failures degrade to "no clusters" silently.
- Current mitigation: Most `except` blocks log via `print()` or `log.exception()`. Exit code from `main.py` reflects failure.
- Fix approach: Tighten to specific exceptions (`yaml.YAMLError`, `pd.errors.ParserError`, `openai.APIError`, `anthropic.APIError`). For LLM failures, accumulate into `audit_report.json` `meta.errors[]`.

### `*_audited.xlsx` written next to `*_annotated.xlsx`, doubling artifact count

- Files: `spec_classifier/batch_audit.py:1448` — `out_path = f.parent / f"{f.stem}{args.suffix}.xlsx"` (default suffix `_audited`)
- Risk: After a single full run, every per-run folder contains both `<stem>_annotated.xlsx` and `<stem>_annotated_audited.xlsx`, doubling the file count and confusing humans browsing OUTPUT. Re-runs overwrite without versioning.
- Current mitigation: Filename suffix makes the audited variant identifiable.
- Fix approach: Move audited variants into `<run-folder>/audit/` subdirectory.

### `find_header_row` scan limited to first 20 rows (hard-coded)

- Files: `spec_classifier/src/core/parser.py:26` — `for i in range(min(len(df), 20)):`
- Risk: A Dell file with a longer preamble (legal disclaimers, multi-row branding) breaks parse with `ValueError: No header row containing 'Module Name' found`. No tunable.
- Current mitigation: Current fixtures fit. Test `test_smoke.py` exercises the assumption.
- Fix approach: Make scan-limit a constant at module top with a `# in practice header is row 1-3` comment, or make it config-driven.

### Dual `.gitignore` files with overlapping intent

- Files: `.gitignore`, `spec_classifier/.gitignore`
- Risk: Two `.gitignore` files. Root is sparse; `spec_classifier/.gitignore` is more complete. Duplicate intent is fragile to maintain.
- Current mitigation: Both gitignores list `output/` / `OUTPUT/`.
- Fix approach: Consolidate into the root `.gitignore`.

### Test-coverage gaps

- Files / area:
  - `spec_classifier/golden/` — Lenovo / Huawei goldens are partial; xFusion goldens exist (`xf1..xf10`) but xFusion / Lenovo regression coverage trails Dell/Cisco/HPE per `spec_classifier/CLAUDE.md` § Tech Debt #8
  - No tests for `run.ps1` orchestration (PowerShell-only)
  - No tests for `teresa_gui.py` (PyQt6 widget tree)
  - `spec_classifier/batch_audit.py` AI prediction path: `tests/test_batch_audit.py` mocks the LLM layer; live integration smoke is manual
- Risk: Lenovo / Huawei rule changes can land without regression coverage. PowerShell launcher errors only surface when a user runs it.
- Current mitigation: 420 collected tests; rule-unit tests per vendor; cluster_audit has dedicated coverage.
- Fix approach: Backfill Lenovo / Huawei goldens. Add `bats` or pytest-shell smoke for `run.ps1 -TestsOnly`. Snapshot-test GUI layout via `pytest-qt`.

---

*Concerns audit: 2026-05-10*
