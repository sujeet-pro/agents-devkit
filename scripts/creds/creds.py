#!/usr/bin/env python3
"""Unified entrypoint: validate | rotate | login | status.

  ./creds.py status            # what each service supports
  ./creds.py validate [svc..]  # same as ./validate.py
  ./creds.py rotate <svc>      # same as ./rotate.py
  ./creds.py login [svc]       # same as ./login.py
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from creds_lib.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
