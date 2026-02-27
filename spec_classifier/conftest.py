"""
Shared pytest configuration and helpers.
project_root() returns spec_classifier/ (project root) based on __file__, not CWD.
"""

from pathlib import Path


def project_root() -> Path:
    """Return spec_classifier/ (directory containing conftest.py, i.e. project root) based on __file__, not CWD."""
    return Path(__file__).resolve().parent
