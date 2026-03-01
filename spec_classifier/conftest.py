"""
Shared pytest configuration and helpers.
project_root() returns spec_classifier/ based on __file__, not CWD.
"""

import yaml
from pathlib import Path


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
