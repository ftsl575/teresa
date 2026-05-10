# Archived Prompt Library (Pre-GSD)

> **Archived:** 2026-05-10
> **Status:** Historical record — superseded by the GSD-native development cycle documented in [`/CONTRIBUTING.md`](../../../CONTRIBUTING.md).

This folder is the retired pre-GSD prompt library that documented the legacy
PRE-CHECK → MASTER-PLAN → CURSOR-IMPLEMENT → POST-CHECK → AUDIT 1A–1G workflow.
The original 10 prompt files (00..08, plus `COWORK_OPUS_FULL_AUDIT.md`) are
preserved verbatim in their original Russian as a historical record. They are
NOT the active workflow — see the per-file mapping below for the GSD-native
replacement of each retired prompt.

## Per-file Mapping

| Retired prompt | GSD-native equivalent |
|---|---|
| `00_VENDOR-RECON.md` | [`spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md`](../../../spec_classifier/docs/dev/NEW_VENDOR_GUIDE.md) |
| `01_PRE-CHECK.md` | `/gsd-discuss-phase` (or `/gsd-progress` for status) |
| `02_MASTER-PLAN.md` | `/gsd-plan-phase` |
| `03_CURSOR-IMPLEMENT.md` | `/gsd-execute-phase` |
| `04_POST-CHECK.md` | `/gsd-verify-work` |
| `05_AUDIT-1A-1G.md` | `/gsd-audit-fix` (and `/gsd-code-review` for the focused review pieces) |
| `06_BATCH-AUDIT-MASTER-PLAN.md` | run `python batch_audit.py` then `/gsd-plan-phase` against the findings |
| `07_DOC-UPDATE-MASTER-PLAN.md` | `/gsd-docs-update` |
| `08_CHATGPT-SYSTEM-PROMPTS.md` | no GSD equivalent (these were ChatGPT-specific system prompts) |
| `COWORK_OPUS_FULL_AUDIT.md` | `/gsd-audit-fix` or `/gsd-code-review` for the audit cycle (audit-mode, not a per-step prompt) |
| `README.md` | superseded by this English README + [`/CONTRIBUTING.md`](../../../CONTRIBUTING.md) |

## Canonical Doc

The current development cycle (Discuss → Plan → Execute → Verify, GSD-native),
pytest invocation, PR conventions, and the project's "do not fix" tech-debt
rules are documented in [`/CONTRIBUTING.md`](../../../CONTRIBUTING.md).
Run `/gsd-help` for the full list of GSD commands.
