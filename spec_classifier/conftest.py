"""
Shared pytest configuration and helpers.
project_root() returns spec_classifier/ based on __file__, not CWD.

MAX_SKIP_RATIO controls CI/data-availability guard:
pytest session fails when skipped/total > MAX_SKIP_RATIO
or when passed == 0 while total > 0.
"""

import yaml
import pytest
from pathlib import Path

MAX_SKIP_RATIO = 0.50


def project_root() -> Path:
    """Return spec_classifier/ (directory containing tests/) based on __file__, not CWD."""
    return Path(__file__).resolve().parent


def load_config() -> dict:
    """Load config.yaml with config.local.yaml overlay (same logic as main._load_config)."""
    root = project_root()
    config_path = root / "config.yaml"
    if not config_path.exists():
        return {}
    with open(config_path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    local_path = root / "config.local.yaml"
    if local_path.exists():
        with open(local_path, encoding="utf-8") as f:
            local_data = yaml.safe_load(f) or {}
        for key, value in local_data.items():
            if isinstance(value, dict) and isinstance(data.get(key), dict):
                data[key].update(value)
            else:
                data[key] = value
    return data


def get_input_root() -> Path:
    """Resolve paths.input_root from config (for tests that use INPUT folder, not test_data)."""
    config = load_config()
    raw = (config.get("paths") or {}).get("input_root") or "input"
    p = Path(raw)
    if p.is_absolute():
        return p
    return project_root() / raw


def get_input_root_dell() -> Path:
    """Resolve input path for Dell files: paths.input_root/dell or INPUT directly."""
    config = load_config()
    raw = (config.get("paths") or {}).get("input_root") or "input"
    p = Path(raw)
    base = p if p.is_absolute() else project_root() / p
    sub = base / "dell"
    return sub if sub.exists() else base


def get_input_root_cisco() -> Path:
    """Resolve input path for Cisco files: paths.input_root/cisco or INPUT directly."""
    config = load_config()
    raw = (config.get("paths") or {}).get("input_root") or "input"
    p = Path(raw)
    base = p if p.is_absolute() else project_root() / p
    sub = base / "cisco"
    return sub if sub.exists() else base


def get_input_root_hpe() -> Path:
    """Resolve input path for HPE files: paths.input_root/hpe or INPUT directly."""
    config = load_config()
    raw = (config.get("paths") or {}).get("input_root") or "input"
    p = Path(raw)
    base = p if p.is_absolute() else project_root() / p
    sub = base / "hpe"
    return sub if sub.exists() else base


def _resolve_input_root_for_skip_guard():
    """Resolve input_root with precedence: config.local.yaml, then config.yaml.

    Returns Path when resolved, or None when config cannot be read/parsed.
    """
    root = project_root()
    local_cfg = root / "config.local.yaml"
    base_cfg = root / "config.yaml"
    cfg_path = local_cfg if local_cfg.exists() else base_cfg

    if not cfg_path.exists():
        return root / "input"

    try:
        with open(cfg_path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if not isinstance(data, dict):
            return None
        paths_cfg = data.get("paths") or {}
        if not isinstance(paths_cfg, dict):
            return None
        raw = paths_cfg.get("input_root") or "input"
        p = Path(raw)
        return p if p.is_absolute() else (root / raw)
    except Exception:
        # Keep current behavior when config is malformed/unreadable.
        return None


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Fail session if too many tests were skipped due to missing data."""
    # collect-only mode never executes tests; passed==0 is not an error here.
    if getattr(session.config.option, "collect_only", False):
        return

    terminal = session.config.pluginmanager.get_plugin("terminalreporter")
    stats = getattr(terminal, "stats", {}) if terminal else {}

    total = int(getattr(session, "testscollected", 0) or 0)
    passed = len(stats.get("passed", []))
    skipped = len(stats.get("skipped", []))
    failed = len(stats.get("failed", []))

    if total == 0:
        return

    # Nothing actually ran (e.g. -k filter matched nothing, deselected all).
    # passed==0 is not actionable in that case.
    if passed + skipped + failed == 0:
        return

    skip_ratio = skipped / total
    input_root = _resolve_input_root_for_skip_guard()
    missing_input_root = (
        input_root is not None
        and (not input_root.exists())
        and (skipped > 0 or passed == 0)
    )
    should_fail = missing_input_root or (skip_ratio > MAX_SKIP_RATIO) or (passed == 0)
    if not should_fail:
        return

    if missing_input_root:
        message = (
            f"Skip guard triggered: input_root is missing: {input_root}. "
            f"skipped={skipped}, total={total}, passed={passed}, failed={failed}, "
            f"threshold={MAX_SKIP_RATIO:.2f}. "
            "Restore input_root or point paths.input_root to the correct directory (config.local.yaml)."
        )
    else:
        message = (
            f"Skip guard triggered: skipped={skipped}, total={total}, passed={passed}, "
            f"failed={failed}, threshold={MAX_SKIP_RATIO:.2f}. "
            "Too many tests were skipped or no tests passed. "
            "Please provide input/*.xlsx or set paths.input_root."
        )
    if terminal:
        terminal.write_line(f"ERROR: {message}", red=True, bold=True)
    else:
        print(f"ERROR: {message}")

    session.exitstatus = 1
