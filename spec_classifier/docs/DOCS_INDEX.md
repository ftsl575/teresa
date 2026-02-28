# Documentation Index — Spec Classifier (Dell + Cisco CCW)

## Structure

| Folder | Purpose |
|---|---|
| `docs/product/` | **Normative.** Architecture, baseline, data pipeline. Must match current code. |
| `docs/user/` | **Normative.** User guide, CLI reference. How to operate the tool. |
| `docs/schemas/` | **Normative.** Data contracts: field specs for all output formats. |
| `docs/rules/` | **Normative.** Rules authoring guide. |
| `docs/dev/` | **Normative.** Contributing, testing, operational notes. |
| `docs/roadmap/` | **Reference only.** Completed plans. Not normative. |
| `docs/prompts/` | **Archival.** AI prompts (Cursor/Claude). Do not treat as specification. |
| `docs/taxonomy/` | **Normative.** Source of truth for controlled vocabularies (e.g., hw_type). |

## Key Documents

| Document | What it answers |
|---|---|
| `README.md` | How do I install and run this? |
| `docs/user/USER_GUIDE.md` | How do I interpret the output? |
| `docs/user/CLI_CONFIG_REFERENCE.md` | What are all CLI options and config keys? |
| `docs/user/RUN_PATHS_AND_IO_LAYOUT.md` | Where do inputs/outputs go? Default paths (Desktop INPUT/OUTPUT), vendor run layout, no TEMP. |
| `docs/schemas/DATA_CONTRACTS.md` | What are the exact output schemas? |
| `docs/rules/RULES_AUTHORING_GUIDE.md` | How do I add or change a rule safely? |
| `docs/dev/TESTING_GUIDE.md` | How do I run tests and update golden? |
| `docs/dev/CONTRIBUTING.md` | How do I work in this repo? |
| `docs/dev/OPERATIONAL_NOTES.md` | How do I run batch jobs and manage artifacts? |
| `docs/product/TECHNICAL_OVERVIEW.md` | How does the pipeline work internally? |
| `CHANGELOG.md` | What changed in each version? |
| `docs/taxonomy/hw_type_taxonomy.md` | What are the allowed hw_type values and the exact meaning/boundaries? |

## Conventions

- **Normative docs** (`product/`, `user/`, `schemas/`, `rules/`, `dev/`): must stay in sync
  with code. Update docs in the same commit as any behavior change.
- **Roadmap**: historical reference, status "completed". Do not edit.
- **Prompts**: archival. Do not use as product specification.
