---
phase: 04-cache-redirect
plan: 02
subsystem: launcher / GUI runtime cache redirect
tags: [pyqt6, runtime-cache, env-vars, launcher, gui]
requires:
  - "Plan 04-01 (run.ps1 cache redirect + clean.ps1 auto-invocation)"
provides:
  - "os.environ['PYTHONPYCACHEPREFIX'] is set from config.local.yaml::temp_root in teresa_gui.main() BEFORE QApplication(sys.argv)"
  - "os.environ['PYTEST_ADDOPTS'] is set with -o cache_dir from temp_root in teresa_gui.main() BEFORE QApplication(sys.argv)"
  - "TeresaWindow._discover_temp_path() instance method, sibling of _discover_input_path / _discover_output_path"
  - "subprocess.Popen children spawned by launch_run_ps1 inherit the cache-redirect env vars from the parent GUI process"
affects:
  - teresa_gui.py
tech_stack:
  added: []
  patterns:
    - "config.local.yaml regex parser extended with a 6th site (teresa_gui.py::_discover_temp_path) — intentional per CONCERNS.md § IMPORTANT; helper consolidation deferred"
    - "Inline regex parser duplicated in teresa_gui.main() (7th site) because the env-var block must run before TeresaWindow is constructed; instance method cannot be self-called from main()"
    - "Defense-in-depth env-var setting (D-13): both teresa_gui.main() and run.ps1 set PYTHONPYCACHEPREFIX/PYTEST_ADDOPTS independently from the same temp_root source"
key_files:
  created: []
  modified:
    - teresa_gui.py
decisions:
  - "Inlined the regex parser inside main() instead of converting _discover_temp_path to a module-level function. Rationale: keeps mechanical consistency with the existing 5-site pattern and preserves the Claude's-discretion clause in CONTEXT.md (D-03 + 'Claude's Discretion' bullet 3 — both meet CACHE-02). The instance method on TeresaWindow stays line-for-line analogous to its siblings; main() carries its own copy because it runs first."
  - "No deviations from CONTEXT.md decisions (D-01, D-03, D-08, D-10, D-13). All 2 edits land at the prescribed locations; ordering invariant (PYTHONPYCACHEPREFIX assignment BEFORE QApplication construction) holds."
metrics:
  duration_minutes: 10
  completed_date: 2026-05-10
  task_count: 1
  files_changed: 1
---

# Phase 4 Plan 2: Cache Redirect — teresa_gui.py wiring Summary

PyQt6 launcher `teresa_gui.py` now sets `PYTHONPYCACHEPREFIX` and `PYTEST_ADDOPTS` from `config.local.yaml::temp_root` in `main()` BEFORE `QApplication(sys.argv)` — so subprocess-spawned PowerShell children inherit the redirect from the parent GUI process and never drop `__pycache__` next to `teresa_gui.py`.

## What Changed

Two coordinated edits to `teresa_gui.py`:

| Edit | Change                                                                                                  | Lines (post-edit) |
| ---- | ------------------------------------------------------------------------------------------------------- | ----------------- |
| 1    | Added `_discover_temp_path()` instance method on `TeresaWindow`, sibling of `_discover_input_path` / `_discover_output_path` | 423-434           |
| 2    | Prepended cache-redirect env-var block to `main()` BEFORE `QApplication(sys.argv)` (inline temp_root parser + assignments + PYTEST_ADDOPTS append-on-existing) | 537-559           |

### Pre/post line-range deltas

| Region                              | Pre-edit       | Post-edit      |
| ----------------------------------- | -------------- | -------------- |
| `_discover_temp_path` method        | n/a            | 423-434 (12 lines new) |
| `main()` env-var block + body       | 523-528 (6 lines)  | 537-565 (29 lines) |
| Total file length                   | 533 lines      | 569 lines (+36) |

### Excerpts (post-edit)

**`_discover_temp_path()` method (teresa_gui.py:423-434):**

```python
    def _discover_temp_path(self) -> str:
        cfg = REPO_ROOT / "spec_classifier" / "config.local.yaml"
        if cfg.exists():
            try:
                text = cfg.read_text(encoding="utf-8")
                for line in text.splitlines():
                    line = line.strip()
                    if line.startswith("temp_root:"):
                        return line.split(":", 1)[1].strip().strip('"').strip("'")
            except Exception:
                pass
        return str(Path.home() / "Desktop" / "temporary")
```

**`main()` body (teresa_gui.py:537-565):**

```python
def main():
    # Redirect runtime cache artifacts (Python bytecode, pytest cache) to temp_root
    # BEFORE QApplication and BEFORE any subprocess.Popen so spawned PowerShell
    # children inherit the env vars. This is defense-in-depth — run.ps1 also sets
    # these from the same temp_root source per D-13.
    cfg = REPO_ROOT / "spec_classifier" / "config.local.yaml"
    temp_root = str(Path.home() / "Desktop" / "temporary")
    if cfg.exists():
        try:
            text = cfg.read_text(encoding="utf-8")
            for line in text.splitlines():
                line = line.strip()
                if line.startswith("temp_root:"):
                    temp_root = line.split(":", 1)[1].strip().strip('"').strip("'")
                    break
        except Exception:
            pass
    os.environ["PYTHONPYCACHEPREFIX"] = str(Path(temp_root) / "__pycache__")
    pytest_cache_arg = f"-o cache_dir={Path(temp_root) / '.pytest_cache'}"
    if os.environ.get("PYTEST_ADDOPTS"):
        os.environ["PYTEST_ADDOPTS"] = f"{os.environ['PYTEST_ADDOPTS']} {pytest_cache_arg}"
    else:
        os.environ["PYTEST_ADDOPTS"] = pytest_cache_arg

    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # consistent base look across Windows versions
    win = TeresaWindow()
    win.show()
    sys.exit(app.exec())
```

## Verification

### Static checks (automated)

| Predicate                                                                  | Result                |
| -------------------------------------------------------------------------- | --------------------- |
| `grep -c 'def _discover_temp_path' teresa_gui.py` == 1                     | PASS (1)              |
| `grep -c 'temp_root:' teresa_gui.py` == 2                                  | PASS (2)              |
| `grep -c '"Desktop" / "temporary"' teresa_gui.py` == 2                     | PASS (2)              |
| `grep -c 'os.environ\["PYTHONPYCACHEPREFIX"\]' teresa_gui.py` == 1         | PASS (1)              |
| `grep -c 'PYTEST_ADDOPTS' teresa_gui.py` >= 2                              | PASS (4 occurrences)  |
| `grep -c '"-o cache_dir=' teresa_gui.py` >= 1                              | PASS (1)              |
| `grep -c 'import yaml' teresa_gui.py` == 0                                 | PASS (0)              |
| PYTHONPYCACHEPREFIX line < QApplication(sys.argv) line                     | PASS (553 < 560)      |

### Class-membership check

```
$ python -c "import ast, sys; tree = ast.parse(open('teresa_gui.py', encoding='utf-8').read()); cls = next(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == 'TeresaWindow'); methods = {m.name for m in cls.body if isinstance(m, ast.FunctionDef)}; sys.exit(0 if {'_discover_input_path', '_discover_output_path', '_discover_temp_path'} <= methods else 1)"
$ echo $?
0
```

PASS — `_discover_temp_path` is an instance method on `TeresaWindow`, sibling of the two existing path-discovery methods.

### Python AST parse check

```
$ python -c "import ast; ast.parse(open('teresa_gui.py', encoding='utf-8').read()); print('AST OK')"
AST OK
```

PASS — file parses as valid Python with zero syntax errors.

### D-22 protected-paths guard

```
$ git diff --stat -- spec_classifier/src spec_classifier/rules \
    spec_classifier/golden spec_classifier/tests \
    spec_classifier/batch_audit.py spec_classifier/cluster_audit.py \
    spec_classifier/main.py spec_classifier/conftest.py
(no output)
```

PASS — zero bytes changed inside any D-22 protected path.

### Goldens byte-equal guard

```
$ git diff --stat -- spec_classifier/golden/
(no output)
```

PASS — all 40 golden fixtures byte-identical.

### Pytest skip-ratio gate

`python -m pytest -q` (run from `spec_classifier/`):

```
774 passed, 1 xfailed, 25 warnings in 22.83s
```

| Counter    | Value |
| ---------- | ----- |
| passed     | 774   |
| skipped    | 0     |
| xfailed    | 1     |
| failed     | 0     |
| total      | 775   |
| skip-ratio | 0/775 = 0% (gate threshold: must be ≤ 50%) |

PASS — `conftest.py::pytest_sessionfinish` skip-guard not tripped. Counts are byte-identical to Plan 04-01's pytest run (no behavior change confirmed).

### GUI smoke test (cache redirect)

This agent runs non-interactively and cannot launch the PyQt6 main window with full GUI semantics. The cache-redirect mechanism is verified two ways:

1. **AST shows env-var assignment precedes QApplication construction** (line 553 < line 560).
2. **End-to-end pytest run under temp_root redirect inherits the same env vars Plan 04-01 set in run.ps1**, and the resulting cache directories materialize under `temp_root` (not the repo). Filesystem state after `pytest -q` from `spec_classifier/`:

| Path                                                              | State after pytest      | Plan expectation |
| ----------------------------------------------------------------- | ----------------------- | ---------------- |
| `C:/Users/G/Desktop/teresa/spec_classifier/__pycache__`           | does not exist          | `$false`         |
| `C:/Users/G/Desktop/teresa/spec_classifier/.pytest_cache`         | does not exist          | implicit `$false` |
| `C:/Users/G/Desktop/teresa/.pytest_cache`                         | does not exist          | `$false`         |
| `C:/Users/G/Desktop/temporary/__pycache__/`                       | exists, contains compiled bytecode (`Forge/`, `Users/`, `venv/`) | `$true` |
| `C:/Users/G/Desktop/temporary/.pytest_cache/`                     | exists, contains `CACHEDIR.TAG`, `README.md`, `v/` | created by pytest under redirect |
| `find spec_classifier -name __pycache__ -type d`                  | 0 hits                  | consistent with redirect |

Full operator-driven GUI smoke (`python teresa_gui.py` → click vendor button → `Test-Path .\spec_classifier\__pycache__`) is the operator's responsibility per `<done>` clause #3 (manual smoke). Mechanism-level verification above demonstrates success criterion #5 will hold for the same reason Plan 04-01's mechanism-level verification did: the GUI's `main()` block sets the same env vars `run.ps1` sets, before any `subprocess.Popen` call.

## Deviations from Plan

### Auto-fixed Issues

None.

### Deviations from CONTEXT.md decisions

None. All 2 edits land at the prescribed locations:

- D-01 (fallback `Path.home() / "Desktop" / "temporary"`) — applied in both the `_discover_temp_path` method and the inline `main()` block.
- D-03 (Python parser is a verbatim clone of `_discover_input_path` / `_discover_output_path`) — `_discover_temp_path` is line-for-line analogous; instance method on `TeresaWindow`, not a module-level function.
- D-08 (`PYTEST_ADDOPTS` set as the symmetric partner to `PYTHONPYCACHEPREFIX`) — both env vars assigned in the same block.
- D-10 (`PYTEST_ADDOPTS` append-on-existing semantics) — implemented via `if os.environ.get("PYTEST_ADDOPTS")` branch, mirrors run.ps1 from Plan 04-01.
- D-13 (env vars set in `main()` BEFORE `app = QApplication(sys.argv)`) — verified via line-number inequality (553 < 560).

### Out-of-scope discoveries

None. Edit scope is confined to `teresa_gui.py` per CONTEXT.md D-22 and the plan's `<action>` "Out-of-scope reaffirmation" block.

## Threat Flags

None — Plan 04-02 introduces no new external-input parsing surface beyond an additional method (`_discover_temp_path`) plus an inline parsing block in `main()`, both reading `config.local.yaml::temp_root`. The config file is gitignored, operator-owned, and was already being parsed for `input_root` / `output_root` by the same line-by-line `text.splitlines()` shape. All threats from the plan's `<threat_model>` (T-04-04 accept; T-04-05 accept; T-04-06 accept) hold unchanged.

## Self-Check: PASSED

- `teresa_gui.py` exists and contains both edits (method + main() block) — FOUND
- File parses as valid Python via `ast.parse` — OK
- `_discover_temp_path` is an instance method on `TeresaWindow` (verified via AST walk) — OK
- `os.environ["PYTHONPYCACHEPREFIX"]` assignment line (553) precedes `QApplication(sys.argv)` line (560) — OK
- `git diff --stat -- spec_classifier/{src,rules,golden,tests,batch_audit.py,cluster_audit.py,main.py,conftest.py}` shows zero rows — OK
- `git diff --stat -- spec_classifier/golden/` shows zero rows — OK
- pytest exits clean (774 pass / 1 xfail / 0 skipped / 0 failed; skip-ratio 0% << 50% gate) — OK
- Cache-redirect env-var smoke test confirms `__pycache__` and `.pytest_cache` materialize under `temp_root` and not the repo tree — OK
- Commit hash for Task 2.1: `9cf94dd` (single commit, files = `teresa_gui.py` only) — FOUND

## Notes for Plan 03 (CACHE-04 — `ONE_BUTTON_RUN.md` doc edits)

After Plan 04-02:

- The cache-redirect mechanism is now fully wired in **both** entry points: `run.ps1` (Plan 04-01) and `teresa_gui.py` (this plan). Defense-in-depth per D-13 is in effect.
- CONCERNS.md § IMPORTANT now stands at **6 sites** of the `config.local.yaml` overlay regex pattern: `run.ps1` ×1, `teresa_gui.py:_discover_input_path`, `teresa_gui.py:_discover_output_path`, `teresa_gui.py:_discover_temp_path` (added by this plan), `teresa_gui.py:main()` inline (added by this plan), plus the pre-existing `main.py` and `conftest.py` overlays. Helper consolidation (`load_config_with_local()`) remains deferred per the v1.1 init decision.
- Plan 04-03 will rewrite three sections of `spec_classifier/docs/dev/ONE_BUTTON_RUN.md` (per CONTEXT.md D-11) to document the new `-NoClean` switch and the auto-clean default. No further code changes required for Phase 4.
