# Dell Spec Classifier — Makefile
# Run from spec_classifier/ (e.g. make generate_golden).

PYTHON ?= python
DL_FILES = dl1 dl2 dl3 dl4 dl5

.PHONY: generate_golden test test-unit test-smoke test-regression test-unknown

generate_golden:
	@for d in $(DL_FILES); do \
		xlsx="test_data/$$d.xlsx"; \
		if [ -f "$$xlsx" ]; then \
			echo "Generating golden for $$d..."; \
			$(PYTHON) main.py --save-golden --input "$$xlsx" || exit 1; \
		else \
			echo "Skipping $$d: $$xlsx not found"; \
		fi; \
	done
	@echo "Done. Golden files in golden/"

test: test-unit test-smoke test-regression test-unknown

test-unit:
	$(PYTHON) -m pytest tests/test_rules_unit.py tests/test_state_detector.py tests/test_normalizer.py -v

test-smoke:
	$(PYTHON) -m pytest tests/test_smoke.py -v

test-regression:
	$(PYTHON) -m pytest tests/test_regression.py -v

test-unknown:
	$(PYTHON) -m pytest tests/test_unknown_threshold.py -v
