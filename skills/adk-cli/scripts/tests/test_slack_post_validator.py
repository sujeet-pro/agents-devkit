"""Tests for slack_post_validator.

These tests don't shell out to claude — they pass `_subprocess_run=fake` to
drive the validator through deterministic stubs.
"""
from __future__ import annotations

import json
import logging
import subprocess
from types import SimpleNamespace

import pytest

import slack_post_validator as spv


def _payload(**overrides) -> dict:
    base = {
        "kind": "heads_up",
        "channel": {"id": "C1", "name": "sf-web-pr-reviews"},
        "thread": {
            "parent_ts": "100.000",
            "parent_author": "U_alice",
            "parent_text": "Review these two PRs for STRFRNT-1234.",
            "recent_messages": [],
        },
        "prs": [
            {"url": "https://github.com/acme/foo/pull/1", "owner": "acme",
             "repo": "foo", "number": 1, "state": "open",
             "author": "@alice", "title": "Add FAQ"},
            {"url": "https://github.com/acme/bar/pull/2", "owner": "acme",
             "repo": "bar", "number": 2, "state": "open",
             "author": "@alice", "title": "Add carousel"},
        ],
        "proposed_text": "Heads-up: I see 2 PRs in this thread.",
    }
    base.update(overrides)
    return base


def _fake_subprocess(rc: int = 0, stdout: str = "", stderr: str = "",
                     timeout: bool = False, missing: bool = False):
    def _run(cmd, **kwargs):
        if timeout:
            raise subprocess.TimeoutExpired(cmd=cmd, timeout=kwargs.get("timeout", 1))
        if missing:
            raise FileNotFoundError(2, "no such file: claude")
        return SimpleNamespace(returncode=rc, stdout=stdout, stderr=stderr)
    return _run


def test_validator_returns_post_decision_from_json_response():
    """Happy path — runner returns clean JSON; the validator surfaces it."""
    response = json.dumps({
        "should_post": True, "reason": "ok",
        "improved_text": "Heads-up: <@U_alice>, foo#1 and bar#2 look unrelated.",
        "confidence": 0.9,
    })
    out = spv.validate_slack_post(
        _payload(), _subprocess_run=_fake_subprocess(stdout=response),
        log=logging.getLogger("test"),
    )
    assert out["should_post"] is True
    assert out["reason"] == "ok"
    assert "foo#1" in (out["improved_text"] or "")
    assert out["confidence"] == 0.9


def test_validator_strips_low_confidence_rewrite():
    """When confidence < threshold, the rewrite is discarded but the
    should_post decision is honored.
    """
    response = json.dumps({
        "should_post": True, "reason": "ok",
        "improved_text": "shaky rewrite",
        "confidence": 0.4,
    })
    out = spv.validate_slack_post(
        _payload(), _subprocess_run=_fake_subprocess(stdout=response),
        log=logging.getLogger("test"),
    )
    assert out["should_post"] is True
    assert out["improved_text"] is None  # discarded
    assert out["confidence"] == 0.4


def test_validator_parses_fenced_code_block_response():
    """Some runners wrap responses in ```json fences. Validator must tolerate it."""
    response = '```json\n' + json.dumps({
        "should_post": False, "reason": "all PRs merged",
        "improved_text": None, "confidence": 0.95,
    }) + '\n```'
    out = spv.validate_slack_post(
        _payload(), _subprocess_run=_fake_subprocess(stdout=response),
        log=logging.getLogger("test"),
    )
    assert out["should_post"] is False
    assert "merged" in out["reason"]


def test_validator_extracts_json_from_chatty_prefix():
    """Validator must find the JSON block even if the runner prefixes prose."""
    response = ('Here is the analysis:\n\n' + json.dumps({
        "should_post": True, "reason": "go", "improved_text": None,
        "confidence": 0.8,
    }))
    out = spv.validate_slack_post(
        _payload(), _subprocess_run=_fake_subprocess(stdout=response),
        log=logging.getLogger("test"),
    )
    assert out["should_post"] is True


def test_validator_fail_closed_on_timeout():
    """Timeout → should_post=False by default (silence beats noise)."""
    out = spv.validate_slack_post(
        _payload(), _subprocess_run=_fake_subprocess(timeout=True),
        log=logging.getLogger("test"),
    )
    assert out["should_post"] is False
    assert "timed out" in out["reason"]


def test_validator_fail_open_on_timeout_when_opted_in():
    """For callers where missing a reminder is worse than posting a bad one,
    fail_open=True flips the default.
    """
    out = spv.validate_slack_post(
        _payload(), fail_open=True,
        _subprocess_run=_fake_subprocess(timeout=True),
        log=logging.getLogger("test"),
    )
    assert out["should_post"] is True
    assert "timed out" in out["reason"]


def test_validator_fail_closed_on_missing_binary():
    """When the runner binary isn't installed, treat as unreachable."""
    out = spv.validate_slack_post(
        _payload(), _subprocess_run=_fake_subprocess(missing=True),
        log=logging.getLogger("test"),
    )
    assert out["should_post"] is False
    assert "missing" in out["reason"]


def test_validator_fail_closed_on_nonzero_rc():
    """Runner returning nonzero rc → fail-closed."""
    out = spv.validate_slack_post(
        _payload(),
        _subprocess_run=_fake_subprocess(rc=1, stderr="auth failed"),
        log=logging.getLogger("test"),
    )
    assert out["should_post"] is False
    assert "rc=1" in out["reason"]


def test_validator_fail_closed_on_unparseable_response():
    """If the runner returns something that isn't JSON-shaped, fail closed."""
    out = spv.validate_slack_post(
        _payload(),
        _subprocess_run=_fake_subprocess(stdout="I am sentient now."),
        log=logging.getLogger("test"),
    )
    assert out["should_post"] is False
    assert "not JSON" in out["reason"]


def test_validator_prompt_includes_pr_state_and_proposed_text():
    """The validator's prompt must surface the proposed_text + PR states so
    the runner can reason about staleness — this is the bug the validator
    is meant to catch.
    """
    captured = {}

    def _run(cmd, **kwargs):
        # cmd is [claude, -p, <prompt>, --model, haiku]
        captured["prompt"] = cmd[2] if len(cmd) > 2 else ""
        return SimpleNamespace(
            returncode=0,
            stdout=json.dumps({"should_post": False, "reason": "all merged",
                               "improved_text": None, "confidence": 0.9}),
            stderr="",
        )

    payload = _payload()
    payload["prs"][0]["state"] = "merged"
    payload["prs"][1]["state"] = "merged"
    spv.validate_slack_post(payload, _subprocess_run=_run,
                            log=logging.getLogger("test"))
    p = captured["prompt"]
    assert "Heads-up: I see 2 PRs" in p
    assert "state=merged" in p
    assert "acme/foo#1" in p


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
