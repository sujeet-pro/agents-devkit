"""Dispatcher shared by validate.py / rotate.py / login.py.

Subcommands:
  validate [svc ...]   probe one/many/all services against their live API
  status               list services + what each supports
  rotate <svc>         rotate provider-side credentials (writes ~/.zshenv)
  login  <svc>         print interactive-login guidance and open the console
"""

from __future__ import annotations

import sys
import webbrowser

import connectors
from creds_lib import env as _env
from creds_lib.status import LOGIN, Result, render


def _load_env() -> None:
    """Populate os.environ from ~/.zshenv (no-op for vars already exported)."""
    _env.load_zshenv()


def _resolve_many(names: list[str]) -> list[str]:
    out: list[str] = []
    for n in names:
        try:
            out.append(connectors.resolve(n))
        except KeyError as e:
            print(f"error: {e}", file=sys.stderr)
            raise SystemExit(64)
    return out


def cmd_validate(names: list[str]) -> int:
    _load_env()
    targets = _resolve_many(names) if names else connectors.NAMES
    results: list[Result] = []
    for name in targets:
        mod = connectors.load(name)
        try:
            results.append(mod.validate())
        except Exception as e:  # noqa: BLE001
            results.append(Result(name, "FAIL", f"validator crashed: {e}"))
    code = render(results)

    login_needed = [r.connector for r in results if r.state == LOGIN]
    if login_needed:
        print(
            "\nneeds interactive login (run `login.py <svc>`): "
            + ", ".join(login_needed)
        )
    return code


def cmd_rotate(names: list[str]) -> int:
    if not names:
        print("usage: rotate.py <service>", file=sys.stderr)
        return 64
    _load_env()
    results: list[Result] = []
    for name in _resolve_many(names):
        mod = connectors.load(name)
        rotate = getattr(mod, "rotate", None)
        if rotate is None:
            hint = getattr(mod, "LOGIN_HINT", "no automated rotation for this service")
            results.append(Result(name, "SKIPPED", f"no rotate(); {hint}"))
        else:
            try:
                results.append(rotate())
            except Exception as e:  # noqa: BLE001
                results.append(Result(name, "FAIL", f"rotate crashed: {e}"))
    return render(results)


def cmd_login(names: list[str]) -> int:
    _load_env()
    if not names:
        print("usage: login.py <service>\n\nservices:")
        for name in connectors.NAMES:
            mod = connectors.load(name)
            print(f"  {name:<11} {getattr(mod, 'LOGIN_HINT', '').splitlines()[0] if getattr(mod, 'LOGIN_HINT', '') else ''}")
        return 0

    for name in _resolve_many(names):
        mod = connectors.load(name)
        hint = getattr(mod, "LOGIN_HINT", "no login guidance available")
        url = getattr(mod, "MINT_URL", "")
        print(f"\n── {name} ──")
        print(hint)
        if url:
            print(f"opening: {url}")
            try:
                webbrowser.open(url)
            except Exception:  # noqa: BLE001
                pass
        print("\nAfter logging in / updating ~/.zshenv, run:")
        print(f"  source ~/.zshenv && {_self('validate.py')} {name}")
    return 0


def cmd_status(_names: list[str]) -> int:
    print(f"{'service':<11} {'validate':<9} {'rotate':<7} {'login'}")
    print("-" * 48)
    for name in connectors.NAMES:
        mod = connectors.load(name)
        has_rotate = "yes" if getattr(mod, "rotate", None) else "—"
        needs_login = "yes" if getattr(mod, "LOGIN_HINT", "") else "—"
        has_validate = "yes" if getattr(mod, "validate", None) else "—"
        print(f"{name:<11} {has_validate:<9} {has_rotate:<7} {needs_login}")
    return 0


def _self(script: str) -> str:
    return f"scripts/creds/{script}"


_COMMANDS = {
    "validate": cmd_validate,
    "rotate": cmd_rotate,
    "login": cmd_login,
    "status": cmd_status,
}


def main(argv: list[str]) -> int:
    if not argv:
        return cmd_status([])
    cmd, rest = argv[0], argv[1:]
    if cmd in ("-h", "--help", "help"):
        print(__doc__)
        return 0
    fn = _COMMANDS.get(cmd)
    if fn is None:
        print(f"error: unknown command {cmd!r}", file=sys.stderr)
        print(__doc__, file=sys.stderr)
        return 64
    return fn(rest)
