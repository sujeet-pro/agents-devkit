#!/usr/bin/env python3
"""Compat shim — moved to scripts/lib/code_index/chunker.py in Phase 2.

This file exists only so manual CLI invocations from operator command
history still work. Will be removed in a future release; new callers
should invoke the lib path directly.
"""
import runpy
import sys
from pathlib import Path

_LIB = Path(__file__).resolve().parent.parent.parent.parent / "scripts" / "lib" / "code_index"
sys.path.insert(0, str(_LIB))
if __name__ == "__main__":
    runpy.run_path(str(_LIB / "chunker.py"), run_name="__main__")
