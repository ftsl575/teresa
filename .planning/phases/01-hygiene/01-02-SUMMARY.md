---
phase: 01-hygiene
plan: "02"
subsystem: repo-hygiene
tags: [gitignore, hygiene, consolidation]
dependency_graph:
  requires: []
  provides: [single-root-gitignore]
  affects: [phase-02-docs, phase-03-workflow]
tech_stack:
  added: []
  patterns: [single-root-gitignore, repo-root-relative-paths]
key_files:
  created: []
  modified: [".gitignore"]
  deleted: ["spec_classifier/.gitignore"]
decisions:
  - "D-06: Rewrote all spec_classifier/.gitignore relative paths to repo-root-relative (spec_classifier/* prefix)"
  - "D-07: Union coverage retained - all 18 D-07 patterns verified effective via git check-ignore"
  - "Conservative: all legacy root entries preserved (for cursor/, out/, test_Dell_R770.xlsx, make_run_results.ps1, teresa.zip)"
metrics:
  duration: "~1 minute"
  completed: "2026-05-10"
  tasks_completed: 1
  files_modified: 2
---

# Phase 1 Plan 2: gitignore Consolidation Summary

**One-liner:** Merged dual `.gitignore` files into a single root file with all D-07 patterns verified via `git check-ignore`, removing `spec_classifier/.gitignore` from tracking.

## What Was Done

Task 2.1 executed two operations:

1. **Root `.gitignore` rewritten** — merged all patterns from both files, organized into sections, deduplicated, with inner-file relative paths rewritten to repo-root-relative form per D-06.

2. **`spec_classifier/.gitignore` deleted** via `git rm` — removed from both the index and the working tree.

## Pattern Source Map

| Pattern | Source | Notes |
|---------|--------|-------|
| `**/__pycache__/` | root (was `**/__pycache__/`) | Kept glob form |
| `*.pyc`, `*.pyo` | inner only | Added to root |
| `.venv/`, `venv/` | both | Deduplicated |
| `env/` | inner only | Added to root |
| `.pytest_cache/` | both | Deduplicated |
| `.coverage`, `htmlcov/` | inner only | Added to root |
| `.ruff_cache/`, `.mypy_cache/` | inner only | Added to root |
| `.DS_Store`, `Thumbs.db` | inner only | Added to root |
| `input/`, `output/`, `test_data/` | both (inner was relative) | Kept top-level fallbacks |
| `OUTPUT/` | root only | Preserved |
| `spec_classifier/input/` | inner `input/` rewritten | D-06: relative path made absolute from repo root |
| `spec_classifier/output/` | both (inner `output/` rewritten) | D-06 |
| `spec_classifier/test_data/` | both (inner `test_data/` rewritten) | D-06 |
| `spec_classifier/temporary/` | inner `temporary/` rewritten | D-06 |
| `spec_classifier/diag/` | inner `diag/` rewritten | D-06 |
| `spec_classifier/config.local.yaml` | inner `config.local.yaml` rewritten | D-06 |
| `spec_classifier/audit_run.txt` | inner `audit_run.txt` rewritten | D-06 |
| `spec_classifier/audit_run_ai.txt` | inner `audit_run_ai.txt` rewritten | D-06 |
| `spec_classifier/baseline.txt` | inner `baseline.txt` rewritten | D-06 |
| `*.log` | inner only | Kept glob (matches anywhere in tree) |
| `commits.txt` | root only | Preserved |
| `*.zip` | root only | Preserved |
| `.cursor/`, `.claude/` | root only | Preserved |
| `for cursor/`, `out/`, `test_Dell_R770.xlsx`, `make_run_results.ps1`, `teresa.zip` | root only | Legacy entries preserved (conservative D-07) |

## git check-ignore Verification (W-2 Closure)

All 18 spot-checks passed (exit 0):

| Path | Pattern matched | Result |
|------|----------------|--------|
| `spec_classifier/config.local.yaml` | `spec_classifier/config.local.yaml` | IGNORED |
| `spec_classifier/temporary/foo.txt` | `spec_classifier/temporary/` | IGNORED |
| `spec_classifier/diag/foo.txt` | `spec_classifier/diag/` | IGNORED |
| `spec_classifier/output/run-.../foo.txt` | `spec_classifier/output/` | IGNORED |
| `spec_classifier/htmlcov/index.html` | `htmlcov/` | IGNORED |
| `spec_classifier/.coverage` | `.coverage` | IGNORED |
| `spec_classifier/.pytest_cache/foo` | `.pytest_cache/` | IGNORED |
| `spec_classifier/.ruff_cache/foo` | `.ruff_cache/` | IGNORED |
| `spec_classifier/.mypy_cache/foo` | `.mypy_cache/` | IGNORED |
| `spec_classifier/x.pyc` | `*.pyc` | IGNORED |
| `spec_classifier/x.pyo` | `*.pyo` | IGNORED |
| `env/lib/python.txt` | `env/` | IGNORED |
| `.DS_Store` | `.DS_Store` | IGNORED |
| `Thumbs.db` | `Thumbs.db` | IGNORED |
| `spec_classifier/audit_run.txt` | `spec_classifier/audit_run.txt` | IGNORED |
| `spec_classifier/audit_run_ai.txt` | `spec_classifier/audit_run_ai.txt` | IGNORED |
| `spec_classifier/baseline.txt` | `spec_classifier/baseline.txt` | IGNORED |
| `spec_classifier/foo.log` | `*.log` | IGNORED |

**Regression check:** `git ls-files | xargs git check-ignore | wc -l` = 0 (no tracked file became ignored).

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

None.

## Threat Flags

None. No new attack surface introduced; this is purely ignore-rule reorganization. All previously-ignored paths (config.local.yaml, OUTPUT/, test_data/, etc.) remain ignored per verified spot-checks.

## Commit

- `7a451e8`: `chore(01-02): consolidate dual .gitignore into single root file (HYG-02)`

## Self-Check: PASSED
