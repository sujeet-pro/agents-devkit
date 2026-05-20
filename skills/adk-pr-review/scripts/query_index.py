#!/usr/bin/env python3
"""Compat shim — moved to scripts/lib/code_index/query_index.py in Phase 2."""
import runpy
import sys
from pathlib import Path

_LIB = Path(__file__).resolve().parent.parent.parent.parent / "scripts" / "lib" / "code_index"
sys.path.insert(0, str(_LIB))
if __name__ == "__main__":
    runpy.run_path(str(_LIB / "query_index.py"), run_name="__main__")
