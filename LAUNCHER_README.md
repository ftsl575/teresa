# teresa launcher

One launcher to rule them all. Replaces three legacy scripts (`run_audit.ps1`,
`scripts/run_full.ps1`, `scripts/run_tests.ps1`) with a single PowerShell
entry point and a PyQt6 GUI on top.

## Files

- `run.ps1` — single PowerShell entry script. All flags handled here.
- `teresa_gui.py` — PyQt6 GUI front-end. Spawns `run.ps1` in a new
  PowerShell window so you see raw progress.
- `teresa.bat` — double-click launcher for the GUI. Auto-installs PyQt6 if
  missing.
- `requirements-gui.txt` — `PyQt6` (only needed for GUI; CLI works without).

## Usage

### GUI (recommended for daily use)

Double-click `teresa.bat` (or its Desktop shortcut). Window opens with:

- **Left**: per-vendor buttons (Dell / Cisco / HPE / Lenovo / Huawei),
  full-pipeline button, AI toggle, tests toggle.
- **Right**: OpenAI key field with "Save to env" button, INPUT/OUTPUT
  paths with quick-open buttons, last-action log.

When you click any run button, a **new PowerShell window** opens showing
full Python output. The GUI window stays available for next run.

### CLI (PowerShell)

```powershell
.\run.ps1                              # full pipeline + AI audit + cluster + pytest
.\run.ps1 -NoAi                        # no OpenAI call (rule-based audit only)
.\run.ps1 -Vendor dell                 # one vendor only
.\run.ps1 -TestsOnly                   # pytest only
.\run.ps1 -SkipTests                   # full run, skip pytest at the end
.\run.ps1 -Vendor huawei -NoAi -SkipTests   # minimal smoke on one vendor
```

## OpenAI key

The GUI saves the key via `setx OPENAI_API_KEY ...` at User scope. This
persists across reboots. Already-open shells won't see it; new shells (and
new PowerShell windows spawned by the GUI) will.

If you don't have a key or don't want AI audit, uncheck "AI audit" in the
GUI or pass `-NoAi` to the CLI — rule-based audit (E1–E18) still runs.

## Adding a new vendor (e.g. xFusion)

1. Implement adapter (see `prompts/00_VENDOR-RECON.md`).
2. In `run.ps1`: append `"xfusion"` to `$ALL_VENDORS`.
3. In `teresa_gui.py`: move `"xfusion"` from `VENDORS_DISABLED` to
   `VENDORS_ACTIVE`.

## Paths

INPUT/OUTPUT roots are read from `spec_classifier/config.local.yaml` if
`input_root:` / `output_root:` keys are present; otherwise default to
`%USERPROFILE%\Desktop\INPUT` and `%USERPROFILE%\Desktop\OUTPUT`.

## Troubleshooting

**`run.ps1 not found`** in GUI error dialog: GUI expects `run.ps1` next to
`teresa_gui.py`. Make sure both are in the repo root.

**`pythonw` not found**: edit `teresa.bat`, replace `pythonw` with
`python` (you'll get a console window alongside GUI, but GUI still works).

**setx fails**: try running `teresa.bat` as Administrator, or set the env
variable manually via System Properties → Environment Variables.
