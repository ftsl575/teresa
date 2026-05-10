# One-Button Run — spec_classifier

## Quick start

```powershell
# From the repo root (teresa/):
.\run.ps1
```

## What run.ps1 does

1. Cleans prior `__pycache__` / `.pytest_cache` from `temp_root` and the working tree (skip with `-NoClean`)
2. Finds the repo root
3. Runs the classification pipeline for each active vendor (dell, cisco, hpe, lenovo, huawei, xfusion)
4. Runs `batch_audit.py` (E-code audit; add `-NoAi` to skip the LLM step)
5. Runs `cluster_audit.py`
6. Saves logs to the OUTPUT directory
7. Runs pytest if not `-SkipTests`
8. Prints a summary

## Configuration

Three levels (lowest to highest priority):

1. **config.yaml** — defaults (relative paths, in repo)
2. **config.local.yaml** — personal paths (NOT in git)
3. CLI parameters / script parameters

## Setting up config.local.yaml

```powershell
cd spec_classifier
copy config.local.yaml.example config.local.yaml
# Edit paths for your machine
```

## Useful run.ps1 switches

```powershell
.\run.ps1 -NoAi                        # rule-based audit only (no OPENAI_API_KEY needed)
.\run.ps1 -Vendor dell                 # one vendor end-to-end
.\run.ps1 -TestsOnly                   # pytest only
.\run.ps1 -SkipTests                   # full run without pytest at the end
.\run.ps1 -NoClean                     # skip the start-of-run clean.ps1 sweep
.\run.ps1 -Vendor huawei -NoAi -SkipTests  # smoke run
```

## Workspace cleanup

`run.ps1` invokes `.\spec_classifier\scripts\clean.ps1` automatically at the start of every run. Pass `-NoClean` to opt out. To clean manually without running the pipeline:

```powershell
.\spec_classifier\scripts\clean.ps1
```
