#!/usr/bin/env python3
"""Probe MCP-server credentials against their live APIs.

  ./validate.py              # all services
  ./validate.py slack jira   # selected services (names or aliases)

Exit code: 1 if any FAIL, 2 if any MISCONFIGURED, else 0.
Services flagged LOGIN need an interactive login — see ./login.py.
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from creds_lib.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main(["validate", *sys.argv[1:]]))
