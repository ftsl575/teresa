"""
Tests for rules file hash (SHA-256) traceability in run_summary.json.
"""

import hashlib
import pytest

from conftest import project_root
from src.diagnostics.stats_collector import compute_file_hash


def test_compute_file_hash_matches_manual():
    rules_path = project_root() / "rules" / "dell_rules.yaml"
    computed = compute_file_hash(str(rules_path))
    manual = hashlib.sha256(rules_path.read_bytes()).hexdigest()
    assert computed == manual
    assert len(computed) == 64
    assert all(c in "0123456789abcdef" for c in computed)


def test_compute_file_hash_file_not_found():
    with pytest.raises((FileNotFoundError, OSError)):
        compute_file_hash("/nonexistent/path.yaml")
