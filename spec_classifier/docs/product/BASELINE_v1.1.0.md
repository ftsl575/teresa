# Baseline v1.1.0

**Date:** 2026-02-23  
**Status:** Stable / Frozen

This document records the formal baseline of the Dell Specification Classifier repository after full implementation of the MVP and vNext plans. No functional changes are implied by this document; it serves as a reference point before further expansion.

---

## 1. Scope of this Baseline

This baseline covers:

- **Full MVP pipeline:** Excel → parse → normalize → classify → run artifacts (JSON, CSV, Excel) + cleaned spec + diagnostics.
- **Complete test coverage:** unit tests (rules, state detector, normalizer, device_type), smoke tests (dl1–dl5), regression tests (row-by-row vs golden), unknown-threshold tests (UNKNOWN ≤ 5%), and device_type unit tests.
- **UNKNOWN closure:** All previously UNKNOWN rows from dl1–dl5 are classified by the added rules (LOGISTIC-004-CORD, LOGISTIC-005-SFP-CABLE, HW-005 through HW-009); UNKNOWN count is 0 on all five datasets.
- **device_type support:** Second-pass classification for HW and LOGISTIC rows; `device_type` in `classification.jsonl` and `device_type_counts` in `run_summary.json`; rules and tests in place.
- **Documented rules and workflows:** README (Installation, Quick Start, CLI, Artifacts, entity_type, row_kind, State, Rules Change Process, tests, test_data); design and planning documents archived under `docs/architecture/` and `docs/roadmap/`.

---

## 2. Implemented Features

- **row_kind detection** — HEADER (empty Module Name, Option Name, SKUs) vs ITEM; HEADER rows are not entity-classified.
- **entity_type classification** — BASE, HW, CONFIG, SOFTWARE, SERVICE, LOGISTIC, NOTE, UNKNOWN; priority order and first-match rules.
- **state detection** — PRESENT, ABSENT, DISABLED from option_name patterns (e.g. "No TPM", "Disabled").
- **YAML-driven rules engine** — `rules/dell_rules.yaml` for state_rules, entity rules (base, service, logistic, software, note, config, hw), and device_type_rules; first-match semantics.
- **device_type second-pass classification** — For ITEM rows with entity_type HW or LOGISTIC and matched_rule_id ≠ UNKNOWN-000; assigns power_cord, storage_ssd, storage_nvme, psu, nic, sfp_cable, hba, raid_controller, cpu.
- **Golden files and regression testing** — `golden/dl1_expected.jsonl` … `dl5_expected.jsonl`; row-by-row comparison of entity_type, state, matched_rule_id, device_type, skus; `scripts/generate_golden.ps1` and Makefile target.
- **Annotated and cleaned Excel outputs** — `annotated_source.xlsx` (source + Entity Type, State); `cleaned_spec.xlsx` (filtered by config: include_types, include_only_present, exclude_headers).
- **Deterministic run artifacts** — Timestamped run folder with rows_raw.json, rows_normalized.json, classification.jsonl, unknown_rows.csv, header_rows.csv, run_summary.json, run.log, cleaned_spec.xlsx, annotated_source.xlsx.
- **Documentation and planning archives** — [docs/architecture/dell_mvp_technical_spec.md](architecture/dell_mvp_technical_spec.md), [docs/roadmap/vnext_plan1.md](roadmap/vnext_plan1.md); README and [TECHNICAL_OVERVIEW.md](TECHNICAL_OVERVIEW.md) for current behavior.

---

## 3. Validation and Acceptance Criteria

- **All tests passing** — `pytest tests/` (unit, smoke, regression, unknown threshold, device_type) passes with no failures.
- **UNKNOWN = 0 for dl1–dl5** — With test_data/dl1.xlsx … dl5.xlsx present, `run_summary.json` shows `unknown_count: 0` for each run.
- **Reproducible runs from clean environment** — `pip install -r requirements.txt` and `python main.py --input test_data/dlN.xlsx` produce identical classification and artifacts for the same input and rules.
- **main branch synchronized with GitHub** — Baseline assumes main is pushed and tagged as appropriate for v1.1.0.

---

## 4. Reference Documents

- [docs/architecture/dell_mvp_technical_spec.md](architecture/dell_mvp_technical_spec.md) — Original MVP technical architecture and specification.
- [docs/roadmap/vnext_plan1.md](roadmap/vnext_plan1.md) — vNext execution and closure plan.
- [docs/TECHNICAL_OVERVIEW.md](TECHNICAL_OVERVIEW.md) — Current implementation overview.
- [README.md](../README.md) — Installation, CLI, artifacts, entity_type, row_kind, State, Rules Change Process, tests.

---

## 5. Out of Scope / Deferred

The following are **not** part of baseline v1.1.0:

- **Normalized hardware taxonomy (hw_type)** — A single normalized hardware type derived from device_type / rule_id (e.g. for reporting or integration). Deferred to Phase B.
- **Multi-vendor expansion** — Support for non-Dell specifications or multiple rule sets; architecture may allow it later but is out of scope here.
- **External system integration** — APIs, databases, or upstream/downstream systems; pipeline is file-in, file-out only.

---

## 6. Next Planned Phase

**Phase B: Normalized hardware taxonomy (hw_type)**

- Introduce a normalized hardware type field (`hw_type`) derived from `matched_rule_id` and/or `device_type` (e.g. mapping table or rules).
- Define contract: where `hw_type` appears (e.g. classification.jsonl, run_summary), and when it is null vs set.
- Add tests and update golden files after implementation.
- No change to existing entity_type, device_type, or rule semantics; additive only.

---

*End of Baseline v1.1.0*
