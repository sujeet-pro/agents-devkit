#!/usr/bin/env python3
"""Guidance for services that need an interactive login.

  ./login.py            # list every service + its login note
  ./login.py google     # show steps for one service and open its console

This does not automate the login — it prints what to do (and opens the
relevant console/OAuth URL), then tells you how to re-validate.
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from creds_lib.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main(["login", *sys.argv[1:]]))
