# One-Button Run — spec_classifier

## Quick start

```powershell
# From the repo root (teresa/):
.\run.ps1
```

## What run.ps1 does

1. Cleans prior `__pycache__` / `.pytest_cache` from `temp_root` and the working tree (skip with `-NoClean`)
2. Runs the classification pipeline for each active vendor (dell, cisco, hpe, lenovo, huawei, xfusion)
3. Runs `batch_audit.py` (E-code audit; add `-NoAi` to skip the LLM step)
4. Runs `cluster_audit.py`
5. Runs pytest if not `-SkipTests`
6. Prints a summary

## Configuration

Three levels (lowest to highest priority):

1. **config.yaml** — defaults (relative paths, in repo)
2. **config.local.yaml** — personal paths (NOT in git)
3. CLI parameters / script parameters

Set up `config.local.yaml` once:

```powershell
cd spec_classifier
copy config.local.yaml.example config.local.yaml
# Edit paths for your machine
```

## Useful run.ps1 switches

These switches are also documented in `run.ps1`'s comment-based help (run `.\run.ps1 -?`).

```powershell
.\run.ps1 -NoAi                        # rule-based audit only (no OPENAI_API_KEY needed)
.\run.ps1 -Vendor dell                 # one vendor end-to-end
.\run.ps1 -TestsOnly                   # pytest only
.\run.ps1 -SkipTests                   # full run without pytest at the end
.\run.ps1 -NoClean                     # skip the start-of-run clean.ps1 sweep
.\run.ps1 -Vendor huawei -NoAi -SkipTests  # smoke run
```

## Workspace cleanup

`run.ps1` invokes `.\spec_classifier\scripts\clean.ps1` automatically at the start of every run. Pass `-NoClean` to opt out. To clean manually without running the pipeline, run `.\spec_classifier\scripts\clean.ps1` directly.
