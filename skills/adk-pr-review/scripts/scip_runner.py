#!/usr/bin/env python3
"""Compat shim — moved to scripts/lib/code_index/scip_runner.py in Phase 2."""
import runpy
import sys
from pathlib import Path

_LIB = Path(__file__).resolve().parent.parent.parent.parent / "scripts" / "lib" / "code_index"
sys.path.insert(0, str(_LIB))
if __name__ == "__main__":
    runpy.run_path(str(_LIB / "scip_runner.py"), run_name="__main__")
