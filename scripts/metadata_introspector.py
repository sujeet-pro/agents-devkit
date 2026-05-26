#!/usr/bin/env python3
"""metadata_introspector.py — thin orchestrator that calls enrich_metadata.py for
each configured source, writes $ADK_DATA_HOME/improve/metadata/<source>.json, and archives
the previous version.

Called by /adk-improve --metadata and /adk-setup --enrich.
"""
from __future__ import annotations

import argparse
import datetime as dt
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_LIB_DIR = HERE / "lib"
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))
from config import adk_metadata_home  # noqa: E402

METADATA_DIR = adk_metadata_home()
ARCHIVE_DIR = METADATA_DIR / "archive"


def archive_existing() -> Path | None:
    if not METADATA_DIR.exists():
        return None
    has_existing = any(p.is_file() for p in METADATA_DIR.iterdir())
    if not has_existing:
        return None
    ts = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dest = ARCHIVE_DIR / ts
    dest.mkdir(parents=True, exist_ok=True)
    for p in METADATA_DIR.iterdir():
        if p.is_file():
            shutil.copy2(p, dest / p.name)
    return dest


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="all")
    ap.add_argument("--no-archive", action="store_true",
                    help="skip archiving the prior version before overwriting")
    args = ap.parse_args()

    if not args.no_archive:
        archived = archive_existing()
        if archived:
            print(f"archived prior metadata to {archived}", file=sys.stderr)

    result = subprocess.run(
        [sys.executable, str(HERE / "enrich_metadata.py"), "--source", args.source],
        check=False,
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
