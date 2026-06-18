#!/usr/bin/env python3
"""Rotate provider-side credentials and write the new values into ~/.zshenv.

  ./rotate.py slack    # rotate Slack app-config access+refresh tokens

Only services that support programmatic rotation do anything; others report
SKIPPED with a pointer to ./login.py. After a successful rotation run
`source ~/.zshenv` to reload the new values into your shell.
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from creds_lib.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main(["rotate", *sys.argv[1:]]))
