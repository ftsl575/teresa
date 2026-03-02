# Spec Classifier — Makefile
# Run from spec_classifier/ (e.g. make generate_golden).
#
# INPUT paths: all vendor XLSX files live outside the repo.
# Default: C:\Users\G\Desktop\INPUT\ (set in config.local.yaml → paths.input_root).
# Override per-call: make generate_golden INPUT=D:/other/path
#
# Dell/Cisco: INPUT\ (flat, e.g. INPUT\dl1.xlsx)
# HPE:        INPUT\ (flat, e.g. INPUT\hp1.xlsx)
# All paths use forward slashes — GNU Make / Git Bash compatible.

PYTHON ?= python
DL_FILES  = dl1 dl2 dl3 dl4 dl5
CCW_FILES = ccw_1 ccw_2
HP_FILES  = hp1 hp2 hp3 hp4 hp5 hp6 hp7 hp8

# Default INPUT root — matches config.local.yaml paths.input_root.
# Override on command line: make generate_golden INPUT=/d/specs/INPUT
INPUT     ?= C:/Users/G/Desktop/INPUT

.PHONY: generate_golden generate_golden_dell generate_golden_cisco generate_golden_hpe \
        test test-unit test-smoke \
        test-regression test-regression-cisco test-regression-hpe \
        test-unknown test-unknown-cisco test-unknown-hpe

# ── Golden generation ────────────────────────────────────────────────────────

generate_golden: generate_golden_dell generate_golden_cisco generate_golden_hpe

generate_golden_dell:
	@for d in $(DL_FILES); do \
		xlsx="$(INPUT)/$$d.xlsx"; \
		if [ -f "$$xlsx" ]; then \
			echo "Generating golden for $$d (Dell)..."; \
			$(PYTHON) main.py --save-golden --input "$$xlsx" || exit 1; \
		else \
			echo "Skipping $$d: $$xlsx not found (set paths.input_root in config.local.yaml)"; \
		fi; \
	done
	@echo "Done. Dell golden files in golden/"

generate_golden_cisco:
	@for f in $(CCW_FILES); do \
		xlsx="$(INPUT)/$$f.xlsx"; \
		if [ -f "$$xlsx" ]; then \
			echo "Generating golden for $$f (Cisco)..."; \
			$(PYTHON) main.py --save-golden --vendor cisco --input "$$xlsx" || exit 1; \
		else \
			echo "Skipping $$f: $$xlsx not found (set paths.input_root in config.local.yaml)"; \
		fi; \
	done
	@echo "Done. Cisco golden files in golden/"

# HPE XLSX expected at INPUT\hpN.xlsx (flat, like Dell/Cisco)
generate_golden_hpe:
	@for f in $(HP_FILES); do \
		xlsx="$(INPUT)/$$f.xlsx"; \
		if [ -f "$$xlsx" ]; then \
			echo "Generating golden for $$f (HPE)..."; \
			$(PYTHON) main.py --save-golden --vendor hpe --input "$$xlsx" || exit 1; \
		else \
			echo "Skipping $$f: $$xlsx not found (set paths.input_root in config.local.yaml)"; \
		fi; \
	done
	@echo "Done. HPE golden files in golden/"

# ── Tests ────────────────────────────────────────────────────────────────────

test: test-unit test-smoke test-regression test-regression-cisco test-regression-hpe \
      test-unknown test-unknown-cisco test-unknown-hpe

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
