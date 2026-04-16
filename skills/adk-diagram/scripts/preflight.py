#!/usr/bin/env python3
"""Pre-flight checks for ADK skill."""
from __future__ import annotations

import platform
import shutil
import sys
from pathlib import Path

BREW_PACKAGES = {
    "git": "git",
    "python3": "python@3",
    "node": "node",
    "npx": "node",
    "gh": "gh",
    "jq": "jq",
}


def has_diagramkit() -> bool:
    if shutil.which("diagramkit"):
        return True
    local_bin = Path.cwd() / "node_modules" / ".bin" / "diagramkit"
    return local_bin.exists()


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 preflight.py <skill-dir>")
        raise SystemExit(1)

    is_mac = platform.system() == "Darwin"
    missing = []
    for command in ("git", "node", "npx", "python3"):
        if shutil.which(command):
            print(f"ok {command}")
        else:
            print(f"missing {command}")
            missing.append(command)
            if is_mac and command in BREW_PACKAGES:
                print(f"  hint: brew install {BREW_PACKAGES[command]}")

    if has_diagramkit():
        print("ok diagramkit")
        print("hint warmup browser-backed engines with: npx diagramkit warmup")
    else:
        print("warn diagramkit not found in PATH or local node_modules/.bin")
        print("hint install with: npm install -g diagramkit")
        print("hint or add locally: npm install --save-dev diagramkit")

    raise SystemExit(1 if missing else 0)


if __name__ == "__main__":
    main()
