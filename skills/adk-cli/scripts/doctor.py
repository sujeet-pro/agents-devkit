"""doctor.py — `adk doctor` subcommand.

Validates the local environment: required CLIs, the Ollama server + embed
model, Slack token PRESENCE (never reads the value — constitution §VII),
optional scip-* indexers, and importable Python deps. Each check returns a
status (pass / warn / fail) and a short remediation hint.

Exit code:
  0 — no failures (warnings OK).
  1 — at least one fail, OR (with --strict) at least one warn.

Flags:
  --tui      render a live textual table when `textual` is importable; plain
             text otherwise.
  --strict   non-zero exit on warnings too.
  -y / --yes accepted but no-op (doctor is read-only).
  --json     emit machine-readable results instead of the table.
"""
from __future__ import annotations

import argparse
import importlib
import json
import os
import shutil
import socket
import subprocess
import sys
from pathlib import Path
from typing import Callable

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))
ADK_PR_REVIEW_SCRIPTS = THIS_DIR.parent.parent / "adk-pr-review" / "scripts"
sys.path.insert(0, str(ADK_PR_REVIEW_SCRIPTS))


# ----- check primitives ----------------------------------------------------

PASS = "pass"
WARN = "warn"
FAIL = "fail"


def _check_binary(name: str, *, required: bool = True, hint: str = "") -> dict:
    p = shutil.which(name)
    if p:
        return {"status": PASS, "label": f"{name} on PATH", "detail": p}
    return {
        "status": FAIL if required else WARN,
        "label": f"{name} on PATH",
        "detail": hint or f"`{name}` not found",
    }


def _check_python_version() -> dict:
    v = sys.version_info
    ok = (v.major, v.minor) >= (3, 10)
    return {
        "status": PASS if ok else FAIL,
        "label": "python ≥ 3.10",
        "detail": f"{v.major}.{v.minor}.{v.micro}",
    }


def _check_python_module(module: str, *, required: bool = True, pkg: str | None = None) -> dict:
    try:
        importlib.import_module(module)
        return {"status": PASS, "label": f"import {module}", "detail": ""}
    except ImportError:
        return {
            "status": FAIL if required else WARN,
            "label": f"import {module}",
            "detail": f"pip install {pkg or module}",
        }


def _check_ollama_server() -> dict:
    """Probe http://localhost:11434/api/tags via raw socket — no requests dep."""
    host = os.environ.get("OLLAMA_HOST", "127.0.0.1")
    port = int(os.environ.get("OLLAMA_PORT", "11434"))
    try:
        with socket.create_connection((host, port), timeout=1.5):
            return {"status": PASS, "label": "ollama server reachable", "detail": f"{host}:{port}"}
    except OSError as e:
        return {
            "status": FAIL,
            "label": "ollama server reachable",
            "detail": f"{host}:{port} — start with `ollama serve` (or `brew services start ollama`)",
        }


def _check_ollama_model(model: str) -> dict:
    """`ollama list` must include `model`. Server-level call avoided to skip the
    `requests` import; the CLI does this fine.
    """
    if not shutil.which("ollama"):
        return {"status": FAIL, "label": f"ollama model {model}", "detail": "ollama binary missing"}
    try:
        cp = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
    except (subprocess.TimeoutExpired, OSError) as e:
        return {"status": FAIL, "label": f"ollama model {model}", "detail": str(e)}
    if cp.returncode != 0:
        return {"status": FAIL, "label": f"ollama model {model}",
                "detail": cp.stderr.strip()[:120]}
    have = {line.split()[0].rsplit(":", 1)[0] for line in cp.stdout.splitlines()
            if line and not line.startswith("NAME")}
    if model.rsplit(":", 1)[0] in have:
        return {"status": PASS, "label": f"ollama model {model}", "detail": ""}
    return {
        "status": FAIL,
        "label": f"ollama model {model}",
        "detail": f"`ollama pull {model}`",
    }


def _check_token_present(env_vars: list[str], file_hint: Path | None = None, label: str = "") -> dict:
    """Presence-only — value never enters this process. Constitution §VII."""
    for v in env_vars:
        if os.environ.get(v):
            return {"status": PASS, "label": f"{label} token", "detail": f"set: {v}"}
    if file_hint and file_hint.exists():
        return {"status": PASS, "label": f"{label} token", "detail": f"file present: {file_hint}"}
    hint = " or ".join(env_vars)
    return {
        "status": WARN,
        "label": f"{label} token",
        "detail": f"none of {hint} is set" + (f" and {file_hint} missing" if file_hint else ""),
    }


def _check_queue_readable() -> dict:
    from queue_io import DEFAULT_QUEUE_PATH, read_queue  # type: ignore[import-not-found]
    try:
        q = read_queue(DEFAULT_QUEUE_PATH)
    except Exception as e:
        return {"status": FAIL, "label": "queue readable", "detail": f"{DEFAULT_QUEUE_PATH}: {e}"}
    n = len(q.get("prs") or [])
    return {"status": PASS, "label": "queue readable", "detail": f"{n} rows at {DEFAULT_QUEUE_PATH}"}


def _check_file_present(path: Path, *, label: str, hint: str) -> dict:
    if path.exists():
        return {"status": PASS, "label": label, "detail": str(path)}
    return {"status": FAIL, "label": label, "detail": hint}


def _check_zsh_completion_registered() -> dict:
    if not shutil.which("zsh"):
        return {"status": WARN, "label": "zsh completion registered",
                "detail": "zsh not found on PATH"}
    cmd = (
        "autoload -Uz compinit; "
        "compinit -u >/dev/null 2>&1; "
        "compdef -p adk >/dev/null 2>&1"
    )
    try:
        cp = subprocess.run(["zsh", "-ic", cmd], capture_output=True, text=True, timeout=8)
    except Exception as e:
        return {"status": FAIL, "label": "zsh completion registered",
                "detail": f"verification failed: {e}"}
    if cp.returncode == 0:
        return {"status": PASS, "label": "zsh completion registered",
                "detail": "`compdef -p adk` returned a handler"}
    return {
        "status": FAIL,
        "label": "zsh completion registered",
        "detail": (
            "Add this before `compinit` in ~/.zshrc, then open a new shell: "
            '[[ -d "$HOME/.zsh/completions" ]] && '
            'fpath=("$HOME/.zsh/completions" $fpath)'
        ),
    }


# ----- check registry ------------------------------------------------------

def all_checks() -> list[dict]:
    """Run every check, in display order. Each entry: {status, label, detail}."""
    results: list[dict] = []
    results.append(_check_python_version())
    # CLIs.
    results.append(_check_binary("git", required=True, hint="brew install git"))
    results.append(_check_binary("gh", required=True, hint="brew install gh"))
    results.append(_check_binary("ollama", required=True,
                                 hint="brew install ollama (mac) / curl https://ollama.com/install.sh | sh"))
    # Server + models.
    results.append(_check_ollama_server())
    results.append(_check_ollama_model("nomic-embed-text"))
    # Optional scip-* (warn).
    for s in ("scip-typescript", "scip-python", "scip-go", "scip-java"):
        results.append(_check_binary(s, required=False,
                                     hint=f"see https://github.com/sourcegraph/{s}"))
    # Python deps.
    for mod, pkg, required in (
        ("slack_sdk", "slack_sdk", True),
        ("json5", "json5", True),
        ("yaml", "PyYAML", True),
        ("requests", "requests", True),
        ("lancedb", "lancedb", True),
        ("tree_sitter_language_pack", "tree_sitter_language_pack", True),
        ("textual", "textual", False),
    ):
        results.append(_check_python_module(mod, required=required, pkg=pkg))
    # Token presence (no values).
    results.append(_check_token_present(
        ["SLACK_USER_TOKEN_CRED", "SLACK_USER_TOKEN",
         "SLACK_BOT_TOKEN_CRED", "SLACK_BOT_TOKEN"],
        file_hint=Path.home() / ".config" / "creds" / "slack" / "slack.token.json",
        label="slack",
    ))
    results.append(_check_token_present(
        ["BITBUCKET_TOKEN_CRED"], file_hint=None, label="bitbucket",
    ))
    # Queue file.
    results.append(_check_queue_readable())
    return results


def completion_checks() -> list[dict]:
    """Focused checks for `adk doctor --completion`."""
    zsh_completion = Path.home() / ".zsh" / "completions" / "_adk"
    return [
        _check_file_present(
            zsh_completion,
            label="zsh completion file",
            hint=f"Run `adk completion zsh > {zsh_completion}`",
        ),
        _check_zsh_completion_registered(),
    ]


# ----- rendering -----------------------------------------------------------

_GLYPH = {PASS: "✓", WARN: "⚠", FAIL: "✗"}


def _render_plain(results: list[dict]) -> None:
    w_status = 4
    w_label = max(len(r["label"]) for r in results)
    for r in results:
        g = _GLYPH[r["status"]]
        st = r["status"].upper()
        print(f"  {g} {st.ljust(w_status)}  {r['label'].ljust(w_label)}  {r['detail']}")


def _render_tui(results: list[dict]) -> None:
    """Live textual app — graceful fallback if textual isn't importable."""
    try:
        from textual.app import App, ComposeResult  # type: ignore
        from textual.widgets import DataTable, Header, Footer  # type: ignore
    except ImportError:
        sys.stderr.write("textual not installed; falling back to plain text. "
                         "pip install textual\n\n")
        _render_plain(results)
        return

    style = {PASS: "green", WARN: "yellow", FAIL: "red"}

    class DoctorApp(App):  # type: ignore[misc]
        BINDINGS = [("q", "quit", "Quit")]

        def compose(self) -> ComposeResult:
            yield Header(name="adk doctor")
            yield DataTable(zebra_stripes=True)
            yield Footer()

        def on_mount(self) -> None:
            t = self.query_one(DataTable)
            t.add_columns("Status", "Check", "Detail")
            for r in results:
                t.add_row(
                    f"[{style[r['status']]}]{_GLYPH[r['status']]} {r['status'].upper()}[/]",
                    r["label"],
                    r["detail"],
                )

    DoctorApp().run()


# ----- entrypoint ---------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="adk doctor",
                                 description="Validate env, deps, MCPs, ollama, tokens.")
    ap.add_argument("--tui", action="store_true",
                    help="render via textual (falls back to plain text if textual missing)")
    ap.add_argument("--strict", action="store_true",
                    help="non-zero exit on warnings too")
    ap.add_argument("--json", action="store_true",
                    help="machine-readable output (overrides --tui)")
    ap.add_argument("--completion", action="store_true",
                    help="only check shell-completion wiring")
    ap.add_argument("-y", "--yes", action="store_true", help="no-op; accepted for uniformity")
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="write a structured DEBUG log to ~/.agents-devkit/logs/")
    args = ap.parse_args(argv)
    if getattr(args, "verbose", False):
        from _verbose import setup_verbose  # type: ignore  # noqa: WPS433
        setup_verbose("doctor", enabled=True, argv=argv)

    results = completion_checks() if args.completion else all_checks()
    fails = [r for r in results if r["status"] == FAIL]
    warns = [r for r in results if r["status"] == WARN]

    if args.json:
        print(json.dumps({"checks": results, "fail": len(fails), "warn": len(warns)},
                         indent=2, ensure_ascii=False))
    elif args.tui:
        _render_tui(results)
    else:
        print("adk doctor")
        print("==========")
        _render_plain(results)
        print()
        print(f"  {len(fails)} fail · {len(warns)} warn · "
              f"{sum(1 for r in results if r['status'] == PASS)} pass")

    if fails:
        return 1
    if args.strict and warns:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
