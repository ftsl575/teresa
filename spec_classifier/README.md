# Dell Specification Classifier

Deterministic rule-based pipeline for classifying Dell Excel specification files.

**Excel in → parse → normalize → classify → Excel/JSON/CSV out.**
Classification uses YAML rules + regex. No ML. Fully reproducible.

---

## Requirements

- Python 3.10+
- `pip install -r requirements.txt`

---

## Quick Start

```bash
cd spec_classifier
pip install -r requirements.txt

# Single file (Dell default)
python main.py --input test_data/dl1.xlsx

# Cisco CCW export
python main.py --input data/ccw_quote.xlsx --vendor cisco

# Batch: process all xlsx in a directory
python main.py --batch-dir test_data --output-dir output
```

---

## Output

Each run creates a timestamped folder:

**Single run:** `output/run-YYYY-MM-DD__HH-MM-SS-<stem>/`
**Batch:** per-file folders + `output/run-YYYY-MM-DD__HH-MM-SS-TOTAL/`

### Per-run artifacts

| File | Description |
|---|---|
| `classification.jsonl` | Classification result per row (entity_type, state, device_type, hw_type) |
| `run_summary.json` | Aggregate counts: entity types, states, hw_types, unknown count |
| `cleaned_spec.xlsx` | Filtered spec (types from config: BASE, HW, SOFTWARE, SERVICE; PRESENT only) |
| `<stem>_annotated.xlsx` | Original file + 4 added columns: Entity Type, State, device_type, hw_type |
| `<stem>_branded.xlsx` | Branded spec grouped by server and entity type sections |
| `unknown_rows.csv` | Rows that matched no rule — review these after each run |
| `rows_raw.json` | Raw parsed rows (debug) |
| `rows_normalized.json` | Normalized rows with row_kind (debug) |
| `header_rows.csv` | Section separator rows |
| `run.log` | Pipeline log for this run |

### TOTAL folder (batch mode)

`run-YYYY-MM-DD__HH-MM-SS-TOTAL/` aggregates the three presentation files from every
per-run folder: `<stem>_annotated.xlsx`, `<stem>_branded.xlsx`, `<stem>_cleaned_spec.xlsx`.

---

## CLI Reference

| Option | Default | Description |
|---|---|---|
| `--vendor {dell,cisco}` | `dell` | Vendor adapter: Dell spec export or Cisco CCW export |
| `--input PATH` | — | **Required** (single-file mode). Path to input .xlsx |
| `--batch-dir PATH` | — | Batch mode: process all .xlsx in this directory |
| `--config PATH` | `config.yaml` | Config YAML |
| `--output-dir PATH` | `output` | Base directory for run folders |
| `--save-golden` | — | Save golden/<stem>_expected.jsonl without confirmation |
| `--update-golden` | — | Overwrite golden with interactive confirmation |

Either `--input` or `--batch-dir` is required. Full reference: `docs/user/CLI_CONFIG_REFERENCE.md`.

---

## Vendor Support

- **Dell (default):** Parses Dell export (header row by "Module Name"). All artifacts including branded spec. Use `--vendor dell` or omit.
- **Cisco CCW:** Parses Cisco Commerce Workspace export (sheet **"Price Estimate"**). Same pipeline; annotated Excel gets extra columns (line_number, service_duration_months). Branded spec is not generated for Cisco. `run_summary.json` includes `vendor_stats` (e.g. top_level_bundles_count, max_hierarchy_depth).

**Config:** Rules per vendor in `config.yaml`:

```yaml
vendor_rules:
  dell: "rules/dell_rules.yaml"
  cisco: "rules/cisco_rules.yaml"
```

**Cisco parser limitations:**
- Sheet name must be exactly `"Price Estimate"` (no fallback).
- Empty Part Number within data is allowed; parser uses last non-empty Part Number row to determine data end.
- Trailing `=` on Part Number (e.g. `SFP-10G-SR-S=`) is stripped automatically.

---

## Test Data

Test files (`test_data/dl1.xlsx` … `dl6.xlsx`) are **not in git**.
Place them under `spec_classifier/test_data/`.
Smoke, regression, and threshold tests skip automatically if files are absent.

---

## Running Tests

```bash
# Unit tests only (no xlsx needed)
pytest tests/test_rules_unit.py tests/test_state_detector.py tests/test_normalizer.py -v

# Full suite (requires test_data/ + golden/)
pytest tests/ -v --tb=short

# Regression only
pytest tests/test_regression.py -v
```

---

## Updating Golden (after rule changes)

```bash
python main.py --input test_data/dl1.xlsx --save-golden
# Repeat for dl2..dl6 as needed
pytest tests/test_regression.py -v
```

---

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `Input file not found` | Wrong `--input` path | Use absolute path or run from `spec_classifier/` |
| `Config file not found` | Wrong `--config` path | Default is `config.yaml` in CWD |
| `No header row found` | Excel missing `"Module Name"` cell | Verify first sheet has `Module Name` header in first 20 rows |
| `Rules file not found` | `rules_file` in config invalid | Check `config.yaml` → `rules_file` path |
| Regression test fails | Rules changed without golden update | Run `--save-golden`, review diff carefully |
| `unknown_rows.csv` not empty | Input has rows matching no rule | Review patterns; add rules per `docs/rules/RULES_AUTHORING_GUIDE.md` |

---

## Documentation

Full documentation: [`docs/DOCS_INDEX.md`](docs/DOCS_INDEX.md)

Changelog: [`CHANGELOG.md`](CHANGELOG.md)
