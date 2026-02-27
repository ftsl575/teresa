#!/usr/bin/env python3
"""
Shim: delegate to spec_classifier/main.py.
Sets CWD to spec_classifier/ so relative paths (config, rules, test_data, output) resolve correctly.
"""
import os
import sys
from pathlib import Path

_SHIM_DIR = Path(__file__).resolve().parent
_SPEC_ROOT = _SHIM_DIR.parent / "spec_classifier"

if not _SPEC_ROOT.is_dir():
    print("Error: spec_classifier/ not found. Run from repository root.", file=sys.stderr)
    sys.exit(1)

os.chdir(_SPEC_ROOT)
if str(_SPEC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SPEC_ROOT))

# Optional: hint that the new path is preferred
if "--help" in sys.argv or "-h" in sys.argv:
    print("(Tip: preferred project root is spec_classifier/ — run from there for development.)\n", file=sys.stderr)

from main import main

if __name__ == "__main__":
    sys.exit(main())
