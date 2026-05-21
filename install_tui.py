#!/usr/bin/env python3
"""Interactive textual TUI for `install.sh --interactive`.

When textual isn't installed, falls back to a numbered-menu prompt that
works in any terminal. The TUI is purely a wrapper: it gathers the
target list + dry-run/uninstall flags and shells out to install.py.

Usage (from install.sh):
    python3 install_tui.py --repo-root /path/to/agents-devkit

Or directly:
    ./install.sh --interactive
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent


def _load_install(repo_root: Path):
    sys.path.insert(0, str(repo_root))
    try:
        import install as _install  # type: ignore
        return _install
    except ImportError as e:
        sys.stderr.write(f"could not import install.py from {repo_root}: {e}\n")
        return None


def supported_targets(repo_root: Path) -> list[str]:
    """Single source of truth lives in install.py — read it from there."""
    inst = _load_install(repo_root)
    return list(inst.SUPPORTED) if inst else []


def detect(repo_root: Path) -> dict[str, bool]:
    """Import install.py's detectors without running it. Returns {target: detected}."""
    inst = _load_install(repo_root)
    if inst is None:
        return {}
    return {t: inst.DETECTORS[t]() for t in inst.SUPPORTED}


def run_install(repo_root: Path, targets: list[str], dry_run: bool, uninstall: bool) -> int:
    cmd = [sys.executable, str(repo_root / "install.py"), "--repo-root", str(repo_root)]
    if targets:
        cmd += ["--target", ",".join(targets)]
    if dry_run:
        cmd += ["--dry-run"]
    if uninstall:
        cmd += ["--uninstall"]
    return subprocess.call(cmd)


def _tui_available() -> bool:
    try:
        import textual  # noqa: F401
        return True
    except ImportError:
        return False


def _fallback_prompt(repo_root: Path) -> int:
    """Plain numbered-menu prompt. Works without textual."""
    supported = supported_targets(repo_root)
    detected = detect(repo_root)
    print()
    print("adk install — interactive (textual not installed; using plain prompt)")
    print("──────────────────────────────────────────────────────────────────────")
    for i, t in enumerate(supported, 1):
        mark = "✓ detected" if detected.get(t) else "  not detected"
        print(f"  [{i}] {t:<8}  {mark}")
    print()
    print("Enter comma-separated targets (e.g. 1,2) or `all` for everything,")
    print("then add flags: `1,2 --dry-run` or `all --uninstall`.")
    print("Empty input = use detected targets, no flags.")
    try:
        line = input("targets+flags > ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return 130

    dry_run = "--dry-run" in line
    uninstall = "--uninstall" in line
    sel = line.replace("--dry-run", "").replace("--uninstall", "").strip()
    if not sel:
        targets = [t for t, d in detected.items() if d]
        if not targets:
            print("no agents detected; pass `all` to force install for everything.")
            return 1
    elif sel == "all":
        targets = list(supported)
    else:
        try:
            idxs = [int(x) for x in sel.split(",")]
            targets = [supported[i - 1] for i in idxs if 1 <= i <= len(supported)]
        except (ValueError, IndexError):
            print(f"could not parse selection: {sel!r}")
            return 2
    return run_install(repo_root, targets, dry_run, uninstall)


def _run_textual(repo_root: Path) -> int:
    from textual.app import App, ComposeResult
    from textual.binding import Binding
    from textual.containers import Vertical, Horizontal
    from textual.widgets import Checkbox, Footer, Header, Label, RichLog, Button

    supported = supported_targets(repo_root)
    detected = detect(repo_root)

    class InstallApp(App):
        CSS = """
        Screen { layout: vertical; }
        #agents { padding: 1; border: round $accent; height: auto; }
        #buttons { height: auto; padding: 0 1; }
        RichLog { height: 1fr; border: solid $accent; }
        Button { margin: 0 1; }
        """
        BINDINGS = [
            Binding("q", "quit", "Quit"),
        ]

        def compose(self) -> ComposeResult:
            yield Header(show_clock=False)
            with Vertical(id="agents"):
                yield Label("Targets — check to include in this run:")
                for t in supported:
                    mark = " (detected)" if detected.get(t) else ""
                    yield Checkbox(f"{t}{mark}", value=detected.get(t, False), id=f"cb_{t}")
            with Horizontal(id="buttons"):
                yield Button("Dry-run", id="btn_dryrun", variant="primary")
                yield Button("Install", id="btn_install", variant="success")
                yield Button("Uninstall", id="btn_uninstall", variant="warning")
                yield Button("Quit", id="btn_quit")
            yield RichLog(id="log", highlight=True, markup=True)
            yield Footer()

        def on_mount(self) -> None:
            self.title = "adk install — interactive"
            self.sub_title = "select agents → click action"

        def _selected_targets(self) -> list[str]:
            return [t for t in supported if self.query_one(f"#cb_{t}", Checkbox).value]

        def _exec(self, dry_run: bool, uninstall: bool) -> None:
            targets = self._selected_targets()
            if not targets:
                self.query_one("#log", RichLog).write("[red]no targets selected[/]")
                return
            label = "uninstall" if uninstall else ("dry-run" if dry_run else "install")
            log: RichLog = self.query_one("#log", RichLog)
            log.write(f"[bold]{label}[/] → {', '.join(targets)}")
            with self.suspend():
                rc = run_install(repo_root, targets, dry_run, uninstall)
            log.write(f"[{'green' if rc == 0 else 'red'}]exit code: {rc}[/]")

        def on_button_pressed(self, event: Button.Pressed) -> None:
            bid = event.button.id
            if bid == "btn_dryrun":
                self._exec(dry_run=True, uninstall=False)
            elif bid == "btn_install":
                self._exec(dry_run=False, uninstall=False)
            elif bid == "btn_uninstall":
                self._exec(dry_run=False, uninstall=True)
            elif bid == "btn_quit":
                self.exit(0)

        def action_quit(self) -> None:
            self.exit(0)

    InstallApp().run()
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo-root", type=Path, default=REPO)
    args = ap.parse_args()
    repo_root: Path = args.repo_root.resolve()

    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        sys.stderr.write("install_tui requires a TTY. Run install.sh non-interactively instead.\n")
        return 2
    if _tui_available():
        return _run_textual(repo_root)
    return _fallback_prompt(repo_root)


if __name__ == "__main__":
    raise SystemExit(main())
