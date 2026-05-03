# Cycle 2 — post-cycle summary (PR-11)

**Date:** 2026-05-02  
**Scope:** Taxonomy + rules + goldens (`PR-7` … `PR-10` code path); documentation and regression consolidation in **`PR-11`**.  
**Principle:** `HW_TYPE_VOCAB` stays at **26** literals — cycle 2 only introduced new **`device_type`** labels mapped through existing buckets (see [`hw_type_taxonomy.md`](./hw_type_taxonomy.md) § Cycle 2 master map).

---

## Stakeholder Q&A (Q6–Q10)

| # | Topic | Decision |
|---|--------|----------|
| **Q6** | xFusion RAID SuperCap naming | **`device_type=battery`** (align with Lenovo/HPE wording); **`hw_type=accessory`** unchanged — **PR-8**. |
| **Q7a** | Lenovo front operator LCD / ASM panel | **`device_type=front_panel`**, **`hw_type=management`** — **PR-9a**. |
| **Q7b** | TPM vs Root of Trust literature | **`tpm` bucket** for literal TPM 2.0 modules **and** RoT modules (Lenovo prose often merges both) — **PR-9a**. |
| **Q8** | Internal PDB vs PCIe switch / retimer boards | **`power_distribution_board`** and **`interconnect_board`** (both **`hw_type=chassis`**) vs mainboard-only **`motherboard`** — **PR-9b** (Lenovo + HPE PDB; interconnect primarily Lenovo today). |
| **Q9** | HDD Cage vs Media Bay | **`drive_cage` → `backplane`** for disk enclosures; **`media_bay` → `chassis`** for generic front/side bays — **PR-9c** (Lenovo; HPE `drive_cage` precedent **PR-3**). |
| **Q10** | Air duct, optical, riser, stray GPU keyword | **`air_duct` → `accessory`** (no `cooling` vocab); **`optical_drive` → `storage_drive`** (HPE); Cable Riser → **`riser`**; C3RP air duct no longer hijacked by GPU rule — **PR-10**. |

---

## Actionable rows (70) — closure by PR

The authoritative SKU list lives in the external **`teresa_full_audit_fix_report_194.csv`** (not committed). Rows with status **`CONFIRMED_BUG`**, **`LIKELY_BUG`**, or **`TAXONOMY_DECISION`** were targeted across **PR-7 … PR-10**; groupings map to the table above (Q6–Q10).

| PR band | Primary themes |
|---------|----------------|
| **PR-7** | Pre-cycle rule/golden prep (feeds later PRs; keep CSV row IDs in your tracker). |
| **PR-8** | xFusion **`battery` / SuperCap** unification. |
| **PR-9a** | **`front_panel`**, RoT / **`tpm`** bucket. |
| **PR-9b** | **`power_distribution_board`**, **`interconnect_board`**, HPE PDB / reserved interconnect. |
| **PR-9c** | **`drive_cage`**, **`media_bay`**, chassis vs backplane split. |
| **PR-10** | **`air_duct`**, **`optical_drive`**, riser / negative routing fixes. |

**Verification (required for sign-off):**

```bash
python scripts/verify_teresa_audit_actionables.py ^
  --csv path\to\teresa_full_audit_fix_report_194.csv ^
  --output-dir "%USERPROFILE%\Desktop\OUTPUT"
```

The script loads the **newest** `classification.jsonl` tree under each vendor run folder, matches **SKU** from the CSV, and checks `device_type` / `hw_type` against expected columns (see script docstring). Exit code **0** only if every filtered row passes.

> **PR-11 note:** The CSV was not present in the repo snapshot used for this commit; run the command locally after copying the report next to the latest pipeline output.

---

## Pytest

| Milestone | Collected | Passed | Notes |
|-----------|-----------|--------|-------|
| Pre-cycle 2 baseline (stakeholder) | — | **684** | Reference point from cycle 2 kickoff. |
| Post-cycle 2 / PR-11 | **768** | **767** (+ **1** xfail) | `pytest tests/ -q` on 2026-05-02. Delta reflects new regression + golden coverage, not a loss of quality. |

---

## Batch audit & pipeline (2026-05-02)

| Metric | Pre-cycle 2 (AI, stakeholder) | Post-cycle 2 (this doc) |
|--------|------------------------------|-------------------------|
| **`batch_audit.py` model** | `gpt-4o-mini` | **`no-ai`** snapshot + optional full `run.ps1` |
| **`stats.issues` (AI layer)** | **180** | *Re-run with API key:* `.\run.ps1` **without** `-NoAi`, then read `OUTPUT/audit_report.json`. |
| **`stats.issues` (rule-only)** | — | **0** on **110** annotated workbooks, **16 958** rows (`meta.model`: `no-ai`, `2026-05-02 20:49`). |
| **`by_vendor` (rule-only issues)** | — | All vendors **0** (cisco, dell, hpe, huawei, lenovo, xfusion). |
| **`unknown_count` (sampled run_summary.json)** | **0** | **0** (no regression). |

**Commands used for rule-only snapshot:**

```powershell
Set-Location C:\Users\G\Desktop\teresa\spec_classifier
python batch_audit.py --output-dir "$env:USERPROFILE\Desktop\OUTPUT" --no-ai
```

**AI delta vs 180:** Not re-measured in-repo (needs `OPENAI_API_KEY`). After a full AI audit, paste `stats.issues` and `stats.by_vendor` into the next revision of this file or attach `audit_report.json` to the PR.

---

## Regression layout (PR-4c pattern)

Cycle 2 **signature** SKUs and themes are consolidated in:

- `tests/test_regression_lenovo.py` — drive cage, media bay, interconnect, PDB, front panel, RoT/tpm, air duct, cable riser, BM8X, power cable, C9JT fan board, etc.
- `tests/test_regression_hpe.py` — PDB, optical drive, drive cage, power-cord vs PDB negatives.
- `tests/test_regression_xfusion.py` — air duct, fan bracket, RAID SuperCap (`battery` / `accessory`).

Finer-grained YAML order / edge cases remain in `test_*_rules_unit.py` + goldens.

---

## Cycle 3 — open follow-ups (out of scope for PR-11)

1. **~109 `FALSE_POSITIVE_AUDIT` rows** — pipeline/taxonomy OK; optional suppression list in `batch_audit.py` for quieter `audit_report.json`.
2. **11 `REVIEW` + 4 `NEEDS_OFFICIAL_CHECK`** — residual SKU drilldown; consider a micro-PR if the list shrinks below five after the next AI pass.
3. **Audit model** — `gpt-4o-mini` is noisy; experiment with **`gpt-4o`** or **`claude-haiku`** for the LLM step if cost allows.

---

## References

- [`hw_type_taxonomy.md`](./hw_type_taxonomy.md) v2.6.0 — master `device_type → hw_type` matrix + taxonomy notes.
- [`../schemas/DATA_CONTRACTS.md`](../schemas/DATA_CONTRACTS.md) — per-vendor `device_type` examples + still **26** `hw_type` literals.
- [`../../scripts/verify_teresa_audit_actionables.py`](../../scripts/verify_teresa_audit_actionables.py) — CSV ↔ `classification.jsonl` verifier.
