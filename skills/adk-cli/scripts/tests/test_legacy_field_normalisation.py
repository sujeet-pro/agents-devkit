"""Read-shim normalisation of legacy field names in pr-queue.json5.

W1 added a read-shim in queue_io.read_queue() that idempotently renames:
  pr_link → pr_url
  head_oid → head_sha
  last_reviewed_head_oid → last_reviewed_head_sha
  status "declined" → "closed"

Test asserts:
  1. A legacy-shaped queue is normalised on first read.
  2. The file on disk is rewritten with the new field names.
  3. Re-reading the now-normalised file is a no-op (idempotent).
"""
import json
from pathlib import Path
import sys

THIS_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = THIS_DIR.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from queue_io import read_queue  # noqa: E402


def test_legacy_fields_normalised_on_read(tmp_path):
    p = tmp_path / "pr-queue.json5"
    legacy = {
        "filters": None,
        "prs": [
            {
                "pr_link": "https://github.com/acme/foo/pull/1",
                "status": "declined",
                "head_oid": "abc123",
                "last_reviewed_head_oid": "def456",
                "last_checked_at": "2026-05-21T10:00:00Z",
            },
            {
                "pr_link": "https://bitbucket.org/ws/foo/pull-requests/2",
                "status": "pending",
                "head_oid": "xyz789",
                "last_checked_at": None,
            },
        ],
    }
    p.write_text(json.dumps(legacy, indent=2), encoding="utf-8")

    q = read_queue(p)
    prs = q["prs"]
    assert prs[0]["pr_url"] == "https://github.com/acme/foo/pull/1"
    assert "pr_link" not in prs[0]
    assert prs[0]["status"] == "closed"
    assert prs[0]["head_sha"] == "abc123"
    assert "head_oid" not in prs[0]
    assert prs[0]["last_reviewed_head_sha"] == "def456"
    assert "last_reviewed_head_oid" not in prs[0]

    assert prs[1]["pr_url"].endswith("/pull-requests/2")
    assert prs[1]["status"] == "pending"
    assert prs[1]["head_sha"] == "xyz789"

    # Idempotency: file on disk now has new names; re-reading is a no-op.
    on_disk = json.loads(p.read_text())
    assert on_disk["prs"][0]["pr_url"] == "https://github.com/acme/foo/pull/1"
    assert "pr_link" not in on_disk["prs"][0]

    q2 = read_queue(p)
    assert q2["prs"][0]["pr_url"] == "https://github.com/acme/foo/pull/1"
