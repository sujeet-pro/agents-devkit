from __future__ import annotations

from queue_io import merge_scan_results, slack_threads_for


def _row(pr_url: str, channel_id: str, thread_ts: str, *, permalink: str | None = None) -> dict:
    slack = {
        "channel_id": channel_id,
        "message_ts": thread_ts,
        "thread_ts": thread_ts,
    }
    if permalink:
        slack["permalink"] = permalink
    return {"pr_url": pr_url, "slack": slack}


def test_merge_scan_results_keeps_all_slack_threads_for_same_pr():
    pr_url = "https://github.com/acme/foo/pull/1"
    merged = merge_scan_results({}, [
        _row(pr_url, "C1", "100.000", permalink="https://slack/C1/100"),
        _row(pr_url, "C2", "200.000", permalink="https://slack/C2/200"),
    ])

    [row] = merged["prs"]
    assert row["slack"] == row["slack_threads"][0]
    assert [(t["channel_id"], t["thread_ts"]) for t in row["slack_threads"]] == [
        ("C1", "100.000"),
        ("C2", "200.000"),
    ]


def test_merge_scan_results_dedupes_same_slack_thread_preserving_existing_fields():
    pr_url = "https://github.com/acme/foo/pull/1"
    existing = {"prs": [{
        "pr_url": pr_url,
        "slack": {
            "channel_id": "C1",
            "thread_ts": "100.000",
            "permalink": "https://slack/original",
        },
    }]}

    merged = merge_scan_results(existing, [
        _row(pr_url, "C1", "100.000", permalink="https://slack/scanned"),
        _row(pr_url, "C1", "101.000", permalink="https://slack/second"),
    ])

    [row] = merged["prs"]
    threads = slack_threads_for(row)
    assert len(threads) == 2
    assert threads[0]["permalink"] == "https://slack/original"
    assert threads[1]["permalink"] == "https://slack/second"
