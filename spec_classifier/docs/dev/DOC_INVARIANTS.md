# Doc Invariants

## Purpose

This file is a doc-of-record for mechanical drift invariants — claims about the codebase that documentation makes and that mechanical checks can verify in one Bash line.

It exists because the v1.0 milestone shipped with a real drift incident: `RUN_PATHS_AND_IO_LAYOUT.md:22` claimed `PYTHONPYCACHEPREFIX` was wired up by the launcher, when in fact it was only set by the (since-deleted) `scripts/run_full.ps1`. The v1.0 read-pass DOC-03 audit missed it. The v1.1 milestone retrospective (Phase 6) materialized the lesson: every "code does X" claim that documentation makes should have a one-line mechanical check, sitting in one place, where a future contributor can run them all in 5 seconds before opening a PR.

Each invariant below is one such check. They are intentionally short (Bash one-liners). They run in Git Bash on Windows and on POSIX. They have no runtime dependencies beyond `grep`, `test`, and standard shell utilities — matching the v1.1 no-new-tech-stack stance.

This is a doc, not a tool: there is no runner script, no pre-commit hook, no CI integration. To re-sweep, open this doc and paste the lines into Git Bash. The doc IS the tool.

## How to run

Open Git Bash at the repo root. Either run each invariant individually (copy the fenced one-liner and paste), or run them all at once with this composite loop (also useful for SC #4 verification gates):

```bash
fail=0
for line in \
  'grep -q "PYTHONPYCACHEPREFIX" run.ps1' \
  'grep -q "PYTHONPYCACHEPREFIX" teresa_gui.py' \
  'grep -q "PYTEST_ADDOPTS" run.ps1' \
  'grep -q "clean.ps1" run.ps1' \
  '! grep -rqI "run_full" --include="*.toml" --include="*.example" --exclude-dir=.planning --exclude=CHANGELOG.md --exclude=LAUNCHER_README.md .' \
  'grep -q "intentionally unmapped" spec_classifier/rules/dell_rules.yaml' \
  'for v in dell cisco hpe lenovo huawei xfusion; do grep -q "\"$v\"" run.ps1 || exit 1; done' \
  'grep -q ".SYNOPSIS" run.ps1' \
; do
  if eval "$line" >/dev/null 2>&1; then
    echo "PASS: $line"
  else
    echo "FAIL: $line"
    fail=$((fail + 1))
  fi
done
echo "$fail failing invariants"
exit $fail
```

A passing run prints 8 PASS lines and exits 0. Any FAIL means a doc claim has drifted from code reality — fix the code, fix the doc, or both, then re-run.

## Invariants

### 1. PYTHONPYCACHEPREFIX wired in run.ps1

The `run.ps1` launcher must export the `PYTHONPYCACHEPREFIX` environment variable so Python redirects `__pycache__/` directories to `$temp_root` instead of writing them inside the repo working tree. This was the v1.0 drift incident that motivated the entire DOC_INVARIANTS.md doc.

```bash
grep -q "PYTHONPYCACHEPREFIX" run.ps1
```

**Why this matters:** Surfaced by Phase 4 CACHE-01; this is the literal example given in ROADMAP §SC-2 and the exact regression that v1.0 DOC-03 read-pass audit missed — recovery is to re-add the `$env:PYTHONPYCACHEPREFIX` assignment in `run.ps1`'s path-discovery block.

### 2. PYTHONPYCACHEPREFIX wired in teresa_gui.py

The GUI entry point `teresa_gui.py` must independently export `PYTHONPYCACHEPREFIX` so users who launch the pipeline from the GUI get the same cache-redirect behavior as users who launch from `run.ps1`. This is defense-in-depth: a partial revert that leaves only the launcher side wired would still leak `__pycache__/` into the repo when the GUI is used.

```bash
grep -q "PYTHONPYCACHEPREFIX" teresa_gui.py
```

**Why this matters:** Surfaced by Phase 4 D-13 (defense-in-depth decision) — recovery is to re-add the env-var assignment block in `teresa_gui.py` `main()` so both entry points set the variable independently.

### 3. PYTEST_ADDOPTS wired in run.ps1

The `run.ps1` launcher must export `PYTEST_ADDOPTS` with `--cache-dir=$temp_root\.pytest_cache` so pytest's cache directory is also redirected outside the repo. `PYTHONPYCACHEPREFIX` alone covers `__pycache__/` but leaves `.pytest_cache/` landing inside the repo working tree.

```bash
grep -q "PYTEST_ADDOPTS" run.ps1
```

**Why this matters:** Surfaced by Phase 4 D-08 as the cache_dir partner to `PYTHONPYCACHEPREFIX` — recovery is to re-add the `$env:PYTEST_ADDOPTS = "--cache-dir=..."` line alongside the `PYTHONPYCACHEPREFIX` assignment.

### 4. clean.ps1 invoked by run.ps1

The `run.ps1` launcher must invoke `scripts/clean.ps1` by default at the start of every run (with `-NoClean` as the documented opt-out). This sweeps stale cache artifacts before each pipeline run.

```bash
grep -q "clean.ps1" run.ps1
```

**Why this matters:** Surfaced by Phase 4 CACHE-03 and mirrors the Phase 4 verification gate that `clean.ps1` and `-NoClean` co-occur in launcher docs — recovery is to re-add the `& $CleanScript` invocation guarded by `if (-not $NoClean)` near the top of `run.ps1`.

### 5. No scripts/run_full.ps1 orphan refs

After Phase 5 deleted `scripts/run_full.ps1`, no `*.toml` or `*.example` file in the repo (excluding `.planning/`, `CHANGELOG.md`, and `LAUNCHER_README.md` historical content) may reference the orphan path. References creeping back indicate either a botched delete or a copy-paste from old docs.

```bash
! grep -rqI "run_full" --include="*.toml" --include="*.example" --exclude-dir=.planning --exclude=CHANGELOG.md --exclude=LAUNCHER_README.md .
```

**Why this matters:** Surfaced by Phase 5 ORPH-01/ORPH-02; this is the verbatim Phase 5 §SC-1 grep so a future drift here trips the same contract Phase 5 enforced — recovery is to identify the file the grep matched and remove the orphan reference.

### 6. power_cord intentionally unmapped

`spec_classifier/rules/dell_rules.yaml` must contain the `intentionally unmapped` comment marking that `power_cord` deliberately has `hw_type=None` (per CLAUDE.md root rule #1 and recovery commit `c3c7cb6`). PRs that "fix" this by adding `power_cord` to `device_type_map` revert the recovery commit and re-break the same business rule.

```bash
grep -q "intentionally unmapped" spec_classifier/rules/dell_rules.yaml
```

**Why this matters:** Surfaced by recovery commit `c3c7cb6` and CLAUDE.md root rule #1; this is the single most repeatedly-broken business rule in the codebase — recovery is to revert the change that removed the `intentionally unmapped` comment and restore `power_cord`'s absence from `device_type_map`.

### 7. Six vendors registered in run.ps1

The `$ALL_VENDORS` list in `run.ps1` must contain all six supported vendor names: dell, cisco, hpe, lenovo, huawei, xfusion. Drift here breaks the `-Vendor <name>` filter and silently skips a vendor in the default all-vendors run.

```bash
for v in dell cisco hpe lenovo huawei xfusion; do grep -q "\"$v\"" run.ps1 || exit 1; done
```

**Why this matters:** Surfaced by any new-vendor onboarding (CLAS-02 v2.x scope); catches vendor-list drift between `run.ps1`, `teresa_gui.py:VENDORS_ACTIVE`, and `main.py:VENDOR_REGISTRY` — recovery is to identify which vendor name the loop failed on and restore it to `$ALL_VENDORS`.

### 8. Phase 6 help block survives in run.ps1

The `<#.SYNOPSIS .DESCRIPTION .PARAMETER .EXAMPLE#>` comment-based help block added to `run.ps1` in Phase 6 must remain present so `Get-Help .\run.ps1` and `.\run.ps1 -?` continue to return useful help (which is what the trim docs in DRIFT-02 point to).

```bash
grep -q ".SYNOPSIS" run.ps1
```

**Why this matters:** Surfaced by Phase 6 D-05 (self-protect — this is the deliverable the doc itself depends on); accidental removal would re-stale the DRIFT-02 doc pointers — recovery is to re-insert the `<#.SYNOPSIS .DESCRIPTION .PARAMETER .EXAMPLE#>` block above `param()` per the Plan 04 Task 1 specification.

## Adding new invariants

- Must exit 0 against the current tree (run it first)
- Must be a Bash one-liner (no scripts, no helpers)
- Must cite a real drift incident: which commit / phase / requirement surfaced the underlying claim. Hypotheticals don't earn an entry.
