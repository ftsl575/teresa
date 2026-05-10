# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository layout

The repo is two things stacked:

- **Repo root** — a thin Windows launcher (`run.ps1`, `teresa_gui.py`, `teresa.bat`)
  that orchestrates the pipeline. There is no Python package here.
- **`spec_classifier/`** — the actual codebase: a deterministic, rule-based Excel-spec
  classifier for six hardware vendors (Dell, Cisco CCW, HPE, Lenovo DCSC, xFusion, Huawei).
  Pipeline: `Excel → parse → normalize → classify → artifacts`. No ML; all classification
  is YAML rules + regex.

The deeper, frequently-updated reference for the pipeline (taxonomy, E-codes, business
rules, alias tables, current state, development cycle) lives in `spec_classifier/CLAUDE.md`
— read that file when working inside `spec_classifier/`. Do not duplicate that content
here; update it there.

## Code-only repository policy

- The repo holds **only code**. Test fixtures, INPUT specs, OUTPUT runs, and the venv
  all live **outside the repo**.
- Default external roots (Windows): `%USERPROFILE%\Desktop\INPUT`,
  `%USERPROFILE%\Desktop\OUTPUT`, venv at `C:\venv` (override via
  `spec_classifier/config.local.yaml`, gitignored; copy from `config.local.yaml.example`).
- `OUTPUT/`, `output/`, `test_data/`, `.venv/`, `commits.txt`, and `*.zip` are gitignored.
  Do not commit anything from those.

## Critical business rules — do not violate

These five rules keep flipping during edits. Source of truth for the long form is
`spec_classifier/CLAUDE.md` § "Business Rules".

1. **`power_cord` has `hw_type=None` intentionally.** It is absent from `device_type_map`
   in every vendor YAML, with explicit comments.
   `batch_audit.py:_E8_NO_HW_TYPE_DEVICES = {"power_cord", "enablement_kit"}` excludes
   it from E8. Do not "fix" the missing mapping. The `power_cord ≈ cable` alias in
   `batch_audit.DEVICE_TYPE_ALIASES` is **only** for AI-mismatch suppression.

2. **LOGISTIC = packaging, documents, freight only.** Power cords, stacking cables,
   rails, brackets are HW, not LOGISTIC.

3. **BASE without `device_type`** is normal (E15 = INFO).
   **BASE with `device_type`** is valid; E6/E10 must not fire. Only `hw_type` on BASE
   triggers E10.

4. **`is_factory_integrated=True`** rows are CONFIG; AI does not check them.

5. **`hw_type_rules.applies_to`** is `[HW]` only — never `[HW, BASE]`.

YAML rule order is also load-bearing — first-match-wins. Reordering rule blocks during
cosmetic edits can silently flip classification.

## Where to look first

| Question | Authoritative file |
|---|---|
| Pipeline stages, E-codes, alias-table semantics, dev cycle | `spec_classifier/CLAUDE.md` |
| Run a vendor end-to-end on Windows | `run.ps1`, `LAUNCHER_README.md` |
| Vendor adapter contract | `spec_classifier/src/vendors/base.py` |
| Add a new vendor | `spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md` |
| Rules authoring | `spec_classifier/docs/rules/RULES_AUTHORING_GUIDE.md`, `spec_classifier/docs/taxonomy/hw_type_taxonomy.md` |
| Recent changes | `spec_classifier/CHANGELOG.md` |
| Project status / current focus | `.planning/STATE.md` |
| Tech-debt items NOT to fix | `.planning/codebase/CONCERNS.md` (BLOCKER + IMPORTANT sections) |

## Tooling roles

The repo carries a `.cursor/` tree (gitignored) used by the GSD (Get Shit Done) workflow
when driving from Cursor; treat it as informational. The current canonical development
cycle (PRE-CHECK → PLAN → IMPLEMENT → POST-CHECK → AUDIT 1A–1G) is documented in
`spec_classifier/CLAUDE.md`.
