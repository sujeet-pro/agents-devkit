#!/usr/bin/env python3
"""Render config templates into the live creds dir from environment values.

  ./init.py                 # render every template
  ./init.py snowflake       # render one service's templates

Templates live in ``templates/<service>/`` and use ``${VAR}`` placeholders
(stdlib ``string.Template``) resolved from the environment — source of truth is
~/.zshenv, documented with placeholders in ../../.env.example. Real rendered
files land outside git, under the paths the env vars point at (e.g.
``$SNOWFLAKE_HOME``), so secrets never get committed. Re-run any time a value
changes; existing files are overwritten in place.
"""

from __future__ import annotations

import os
import pathlib
import string
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from creds_lib.env import load_zshenv  # noqa: E402

TEMPLATES_DIR = pathlib.Path(__file__).resolve().parent / "templates"


def _snowflake_home() -> pathlib.Path:
    return pathlib.Path(os.path.expanduser(os.environ["SNOWFLAKE_HOME"]))


def _snowflake_service_config() -> pathlib.Path:
    return pathlib.Path(os.path.expanduser(os.environ["SNOWFLAKE_SERVICE_CONFIG_FILE"]))


# (template path relative to templates/) -> resolver for its destination.
MANIFEST: dict[str, callable] = {
    "snowflake/connections.toml": lambda: _snowflake_home() / "connections.toml",
    "snowflake/service-config.yaml": _snowflake_service_config,
}


def _render(rel: str, dest: pathlib.Path) -> list[str]:
    src = TEMPLATES_DIR / rel
    tmpl = string.Template(src.read_text(encoding="utf-8"))
    # Surface any placeholder that has no env value rather than writing a
    # half-empty config that fails opaquely at MCP launch.
    missing = sorted(
        {
            m.group("named") or m.group("braced")
            for m in tmpl.pattern.finditer(tmpl.template)
            if (m.group("named") or m.group("braced"))
            and not os.environ.get(m.group("named") or m.group("braced"))
        }
    )
    rendered = tmpl.safe_substitute(os.environ)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(rendered, encoding="utf-8")
    # Snowflake's connector refuses configs that are group/other-readable.
    dest.chmod(0o600)
    return missing


def main(argv: list[str]) -> int:
    load_zshenv()  # fallback for non-login shells (cron / GUI launchers)
    services = set(argv)
    any_missing = False
    for rel, resolver in MANIFEST.items():
        service = rel.split("/", 1)[0]
        if services and service not in services:
            continue
        dest = resolver()
        missing = _render(rel, dest)
        flag = f"  ⚠ unset: {', '.join(missing)}" if missing else ""
        any_missing = any_missing or bool(missing)
        print(f"  • {rel} → {dest}{flag}")
    if any_missing:
        print("\nSome placeholders were empty — set them in ~/.zshenv and re-run.")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
