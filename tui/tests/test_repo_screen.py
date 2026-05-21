"""Pilot tests for the `b` (repos) action + RepoScreen — η §7.4.

`b` from the main screen pushes a RepoScreen that reads the test
`fake_repos_dir`. `escape` returns. `+` and `a` push PromptScreens.
"""
from __future__ import annotations

import asyncio
from pathlib import Path

from textual.widgets import Tree

from tui.app import AdkApp
from tui.screens.prompt_screen import PromptScreen
from tui.screens.repo_screen import RepoScreen


async def _poll_until(predicate, *, pilot, timeout_s: float = 5.0,
                      tick_s: float = 0.05) -> bool:
    elapsed = 0.0
    while elapsed < timeout_s:
        await pilot.pause()
        if predicate():
            return True
        await asyncio.sleep(tick_s)
        elapsed += tick_s
    return False


def _make_app(fake_queue_path: Path, fake_plan_path: Path,
              fake_repos_dir: Path, fake_adk_script: Path) -> AdkApp:
    return AdkApp(
        queue_path=fake_queue_path,
        plan_path=fake_plan_path,
        adk_bin=fake_adk_script,
        repos_dir=fake_repos_dir,
        worker_script=Path("tui/worker.py").resolve(),
        poll_interval=0.05,
    )


def test_b_opens_repo_screen(
    fake_queue_path: Path, fake_plan_path: Path,
    fake_repos_dir: Path, fake_adk_script: Path,
) -> None:
    app = _make_app(fake_queue_path, fake_plan_path, fake_repos_dir, fake_adk_script)

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            assert len(app.screen_stack) == 1
            await pilot.press("b")
            ok = await _poll_until(
                lambda: isinstance(app.screen, RepoScreen),
                pilot=pilot, timeout_s=3.0,
            )
            assert ok, "RepoScreen never became active"

    asyncio.run(_run())


def test_repo_screen_renders_fixture_repos_and_branches(
    fake_queue_path: Path, fake_plan_path: Path,
    fake_repos_dir: Path, fake_adk_script: Path,
) -> None:
    app = _make_app(fake_queue_path, fake_plan_path, fake_repos_dir, fake_adk_script)

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("b")
            ok = await _poll_until(
                lambda: isinstance(app.screen, RepoScreen),
                pilot=pilot, timeout_s=3.0,
            )
            assert ok
            # Wait for the tree to be populated by on_mount → _refresh().
            tree_ok = await _poll_until(
                lambda: len(app.screen.query_one(Tree).root.children) >= 1,
                pilot=pilot, timeout_s=3.0,
            )
            assert tree_ok, "Tree never populated"
            tree = app.screen.query_one(Tree)
            repo_nodes = list(tree.root.children)
            assert len(repo_nodes) == 1
            repo_node = repo_nodes[0]
            repo_label = str(repo_node.label)
            assert "fake-repo" in repo_label
            assert "acme/fake" in repo_label
            branch_labels = [str(c.label) for c in repo_node.children]
            assert len(branch_labels) == 2
            joined = " | ".join(branch_labels)
            assert "main" in joined
            assert "feat/x" in joined
            assert "user" in joined
            assert "auto" in joined

    asyncio.run(_run())


def test_escape_from_repo_screen_returns_to_main(
    fake_queue_path: Path, fake_plan_path: Path,
    fake_repos_dir: Path, fake_adk_script: Path,
) -> None:
    app = _make_app(fake_queue_path, fake_plan_path, fake_repos_dir, fake_adk_script)

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("b")
            ok = await _poll_until(
                lambda: isinstance(app.screen, RepoScreen),
                pilot=pilot, timeout_s=3.0,
            )
            assert ok
            await pilot.press("escape")
            ok2 = await _poll_until(
                lambda: not isinstance(app.screen, RepoScreen),
                pilot=pilot, timeout_s=2.0,
            )
            assert ok2, "escape did not pop RepoScreen"
            assert len(app.screen_stack) == 1

    asyncio.run(_run())


def test_plus_on_repo_screen_opens_add_repo_prompt(
    fake_queue_path: Path, fake_plan_path: Path,
    fake_repos_dir: Path, fake_adk_script: Path,
) -> None:
    app = _make_app(fake_queue_path, fake_plan_path, fake_repos_dir, fake_adk_script)

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("b")
            ok = await _poll_until(
                lambda: isinstance(app.screen, RepoScreen),
                pilot=pilot, timeout_s=3.0,
            )
            assert ok
            await pilot.press("plus")
            ok2 = await _poll_until(
                lambda: any(isinstance(s, PromptScreen) for s in app.screen_stack),
                pilot=pilot, timeout_s=3.0,
            )
            assert ok2, "PromptScreen never appeared after `+`"

    asyncio.run(_run())


def test_a_on_repo_screen_with_cursor_on_repo_opens_branch_prompt(
    fake_queue_path: Path, fake_plan_path: Path,
    fake_repos_dir: Path, fake_adk_script: Path,
) -> None:
    app = _make_app(fake_queue_path, fake_plan_path, fake_repos_dir, fake_adk_script)

    async def _run() -> None:
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("b")
            ok = await _poll_until(
                lambda: isinstance(app.screen, RepoScreen),
                pilot=pilot, timeout_s=3.0,
            )
            assert ok
            tree_ok = await _poll_until(
                lambda: len(app.screen.query_one(Tree).root.children) >= 1,
                pilot=pilot, timeout_s=3.0,
            )
            assert tree_ok
            tree = app.screen.query_one(Tree)
            # Expand the implicit root so the cursor can move onto the repo node.
            tree.root.expand()
            await pilot.pause()
            await pilot.press("j")
            cursor_ok = await _poll_until(
                lambda: tree.cursor_node is not None
                        and getattr(tree.cursor_node, "data", None) is not None,
                pilot=pilot, timeout_s=2.0,
            )
            assert cursor_ok, "cursor never landed on a data-carrying node"
            await pilot.press("a")
            ok2 = await _poll_until(
                lambda: any(isinstance(s, PromptScreen) for s in app.screen_stack),
                pilot=pilot, timeout_s=3.0,
            )
            assert ok2, "branch-add PromptScreen never appeared"

    asyncio.run(_run())
