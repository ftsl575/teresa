"""
Shared pytest configuration and helpers.
project_root() returns dell_spec_classifier/ based on __file__, not CWD.
"""

from pathlib import Path


def project_root() -> Path:
    """Return dell_spec_classifier/ (directory containing tests/) based on __file__, not CWD."""
    return Path(__file__).resolve().parent
