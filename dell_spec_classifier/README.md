# Dell Specification Classifier MVP

MVP pipeline for classifying Dell Excel specifications (Excel → JSON + cleaned spec + diagnostics).

## Regression

Regression tests compare the current pipeline output to **golden files** row-by-row (`entity_type`, `state`, `matched_rule_id`, `skus`).

- **Generate golden** (first time or after adding a new input file):
  ```bash
  python main.py --input test_data/dl1.xlsx --save-golden
  ```
  This creates `golden/dl1_expected.jsonl`. Repeat for `dl2.xlsx`, etc.

- **Update golden** after intentionally changing rules or logic (prompts for confirmation):
  ```bash
  python main.py --input test_data/dl1.xlsx --update-golden
  ```
  Answer `y` to overwrite `golden/dl1_expected.jsonl`.

- **Run regression tests**:
  ```bash
  pytest tests/test_regression.py -v
  ```
  Each test runs the pipeline for one input file, loads the corresponding `golden/<stem>_expected.jsonl`, and fails if any row differs.
