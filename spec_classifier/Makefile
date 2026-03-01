# Spec Classifier — Makefile
# Run from spec_classifier/ (e.g. make generate_golden).

PYTHON ?= python
DL_FILES = dl1 dl2 dl3 dl4 dl5
CCW_FILES = ccw_1 ccw_2
HP_FILES = hp1 hp2 hp3 hp4 hp5 hp6 hp7 hp8

.PHONY: generate_golden generate_golden_cisco generate_golden_hpe test test-unit test-smoke test-regression test-regression-cisco test-regression-hpe test-unknown test-unknown-cisco test-unknown-hpe

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
	@for f in $(CCW_FILES); do \
		xlsx="test_data/$$f.xlsx"; \
		if [ -f "$$xlsx" ]; then \
			echo "Generating golden for $$f (Cisco)..."; \
			$(PYTHON) main.py --save-golden --vendor cisco --input "$$xlsx" || exit 1; \
		else \
			echo "Skipping $$f: $$xlsx not found"; \
		fi; \
	done
	@for f in $(HP_FILES); do \
		xlsx="input/hpe/$$f.xlsx"; \
		if [ -f "$$xlsx" ]; then \
			echo "Generating golden for $$f (HPE)..."; \
			$(PYTHON) main.py --save-golden --vendor hpe --input "$$xlsx" || exit 1; \
		else \
			echo "Skipping $$f: $$xlsx not found (expected at input/hpe/ or paths.input_root/hpe/)"; \
		fi; \
	done
	@echo "Done. Golden files in golden/"

generate_golden_cisco:
	@for f in $(CCW_FILES); do \
		xlsx="test_data/$$f.xlsx"; \
		if [ -f "$$xlsx" ]; then \
			echo "Generating golden for $$f (Cisco)..."; \
			$(PYTHON) main.py --save-golden --vendor cisco --input "$$xlsx" || exit 1; \
		else \
			echo "Skipping $$f: $$xlsx not found"; \
		fi; \
	done
	@echo "Done. Cisco golden files in golden/"

# HPE: XLSX from paths.input_root/hpe/ (config). Default relative path input/hpe/ (no test_data).
generate_golden_hpe:
	@for f in $(HP_FILES); do \
		xlsx="input/hpe/$$f.xlsx"; \
		if [ -f "$$xlsx" ]; then \
			echo "Generating golden for $$f (HPE)..."; \
			$(PYTHON) main.py --save-golden --vendor hpe --input "$$xlsx" || exit 1; \
		else \
			echo "Skipping $$f: $$xlsx not found (set paths.input_root in config.local.yaml or use input/hpe/)"; \
		fi; \
	done
	@echo "Done. HPE golden files in golden/"

test: test-unit test-smoke test-regression test-regression-cisco test-regression-hpe test-unknown test-unknown-cisco test-unknown-hpe

test-unit:
	$(PYTHON) -m pytest tests/test_rules_unit.py tests/test_state_detector.py tests/test_normalizer.py -v

test-smoke:
	$(PYTHON) -m pytest tests/test_smoke.py -v

test-regression:
	$(PYTHON) -m pytest tests/test_regression.py -v

test-unknown:
	$(PYTHON) -m pytest tests/test_unknown_threshold.py -v

test-regression-cisco:
	$(PYTHON) -m pytest tests/test_regression_cisco.py -v

test-unknown-cisco:
	$(PYTHON) -m pytest tests/test_unknown_threshold_cisco.py -v

test-regression-hpe:
	$(PYTHON) -m pytest tests/test_regression_hpe.py -v

test-unknown-hpe:
	$(PYTHON) -m pytest tests/test_unknown_threshold_hpe.py -v
