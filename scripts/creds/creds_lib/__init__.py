"""adk creds toolkit — shared library.

Self-contained, stdlib-only credential validation + rotation for the MCP
servers declared in plugins/adk/.mcp.json. The source of truth for every
secret is ``~/.zshenv`` (override with $ZSHENV_FILE); rotation writes new
values back into that same file in place.

Public surface:
  creds_lib.status  — Result, render(), required_env(), state constants
  creds_lib.http    — request(), json_or_text(), basic_auth()
  creds_lib.env     — load_zshenv()  (populate os.environ for non-login shells)
  creds_lib.zshenv_io — get_value(), set_value()  (read/write ~/.zshenv lines)
  creds_lib.cli     — main()  (validate / rotate / login / status dispatcher)
"""

from __future__ import annotations

__all__ = ["status", "http", "env", "zshenv_io", "cli"]
