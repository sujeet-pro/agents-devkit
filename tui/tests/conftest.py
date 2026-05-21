from __future__ import annotations

import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

_FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def frozen_now() -> datetime:
    return datetime(2026, 5, 21, 18, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def fake_queue_path(tmp_path: Path) -> Path:
    src = _FIXTURES_DIR / "sample_queue.json5"
    dst = tmp_path / "pr-queue.json5"
    shutil.copyfile(src, dst)
    return dst


@pytest.fixture
def missing_queue_path(tmp_path: Path) -> Path:
    return tmp_path / "does-not-exist.json5"


@pytest.fixture
def tui_app(fake_queue_path: Path):
    from tui.app import AdkApp

    return AdkApp(queue_path=fake_queue_path, poll_interval=0.05)
