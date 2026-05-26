"""slack_post_validator.py — AI pre-flight for bot-authored Slack posts.

Wraps the existing `agent_harness.build_agent_cmd` to ask the configured ACP
runner (default: claude -p with haiku) whether a proposed Slack message
should actually be posted, and, optionally, to rewrite it for personalization.

The validator is **fail-closed by default**: if the runner is unreachable or
the output can't be parsed as JSON, we skip the post. The motivation —
silence is cheaper than another bad heads-up. Callers can opt into
fail-open via `fail_open=True` for paths where missing a reminder is worse
than posting a noisy one (e.g. stalled-PR pings).

Contract — `validate_slack_post(payload)`:
  payload: {
    "kind": "heads_up" | "stalled_reminder" | <free-form>,
    "channel": {"id": "C…", "name": "sf-web-pr-reviews"},
    "thread": {
      "parent_ts": "…", "parent_author": "U…", "parent_text": "…",
      "recent_messages": [{"ts": "…", "user": "U…", "text": "…"}, …]
    },
    "prs": [
      {"url": "…", "owner": "…", "repo": "…", "number": 1,
       "state": "open|merged|closed", "author": "@login",
       "title": "…", "jira": "STRFRNT-1234"|null}, …
    ],
    "proposed_text": "…"
  }
  returns: {
    "should_post": bool,
    "reason": str,
    "improved_text": str | None,
    "confidence": float in [0,1],
  }

Latency budget: ~1.5s at haiku. The CLI invocation is the bulk of it.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))
ADK_PR_REVIEW_SCRIPTS = THIS_DIR.parent.parent / "adk-pr-review" / "scripts"
sys.path.insert(0, str(ADK_PR_REVIEW_SCRIPTS))
from _common import get_logger  # noqa: E402

from agent_harness import build_agent_cmd, resolve_runner_model  # noqa: E402


DEFAULT_RUNNER = "claude"
DEFAULT_MODEL = "haiku"
DEFAULT_TIMEOUT_S = 30.0
DEFAULT_REWRITE_CONFIDENCE = 0.7


# Compact JSON-only contract. Keeping the prompt short keeps haiku fast.
_PROMPT_TEMPLATE = """You are a Slack-message validator for a PR-review bot.
Decide whether the proposed message should be posted to the thread. If yes, optionally rewrite it for personalization.

# Thread context
Channel: #{channel_name}
Parent author: <@{parent_author}>
Parent text (≤500 chars):
{parent_text}

# Recent activity (last 5)
{recent}

# PRs detected in thread
{prs}

# Bot proposes to post
{proposed_text}

# Reject (should_post=false) if any are true
- Every PR in the thread is terminal (merged/closed/declined).
- A bot post with the same intent already exists in this thread within the last 24h.
- The "I see N PRs" count is wrong (must equal unique non-terminal PRs).
- The PRs are clearly related (same Jira, similar branches, same author within minutes) — heads-up is preachy then.
- The thread is dormant (no human reply ≥7d) and the message isn't time-sensitive.

# Personalize when posting
- @-mention authors when their Slack user ID is provided.
- Reference the Jira key if visible.
- Use repo names, not generic "PR".
- Tone: friendly, brief, not preachy.
- Cap at 280 chars.
- Include the footer "_Sent by Sujeet's Automation Setup_" on its own line.

# Output — JSON only, no prose:
{{"should_post": true|false, "reason": "<one short sentence>", "improved_text": "<rewritten text or null>", "confidence": 0.0}}
"""


def _format_recent(msgs: list[dict]) -> str:
    if not msgs:
        return "(none)"
    out = []
    for m in msgs[-5:]:
        author = m.get("user") or m.get("username") or "?"
        text = (m.get("text") or "").replace("\n", " ⏎ ")
        if len(text) > 160:
            text = text[:157] + "…"
        out.append(f"- <@{author}>: {text}")
    return "\n".join(out)


def _format_prs(prs: list[dict]) -> str:
    if not prs:
        return "(none)"
    out = []
    for p in prs:
        ref = f"{p.get('owner', '?')}/{p.get('repo', '?')}#{p.get('number', '?')}"
        state = p.get("state", "?")
        author = p.get("author") or "?"
        title = (p.get("title") or "").strip()
        if len(title) > 80:
            title = title[:77] + "…"
        jira = f" · jira={p['jira']}" if p.get("jira") else ""
        out.append(f"- `{ref}` · state={state} · author={author}{jira} · {title!r}")
    return "\n".join(out)


def _build_prompt(payload: dict) -> str:
    channel = payload.get("channel") or {}
    thread = payload.get("thread") or {}
    parent_text = (thread.get("parent_text") or "")[:500]
    return _PROMPT_TEMPLATE.format(
        channel_name=channel.get("name") or channel.get("id") or "?",
        parent_author=thread.get("parent_author") or "?",
        parent_text=parent_text,
        recent=_format_recent(thread.get("recent_messages") or []),
        prs=_format_prs(payload.get("prs") or []),
        proposed_text=payload.get("proposed_text") or "",
    )


_JSON_BLOCK_RE = re.compile(r"\{[\s\S]*\}")


def _parse_response(raw: str) -> dict | None:
    """Extract the JSON object from the runner's stdout. Tolerant of leading
    chatter (some runners prefix `Result:` etc.), but the body must be JSON.
    """
    raw = (raw or "").strip()
    if not raw:
        return None
    # Strip fenced code blocks if present.
    raw = re.sub(r"^```[a-z]*\s*", "", raw)
    raw = re.sub(r"```\s*$", "", raw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    m = _JSON_BLOCK_RE.search(raw)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def _safe_default(*, should_post: bool, reason: str) -> dict:
    return {"should_post": should_post, "reason": reason,
            "improved_text": None, "confidence": 0.0}


def validate_slack_post(
    payload: dict,
    *,
    runner: str | None = None,
    model: str | None = None,
    timeout_s: float = DEFAULT_TIMEOUT_S,
    fail_open: bool = False,
    rewrite_confidence_threshold: float = DEFAULT_REWRITE_CONFIDENCE,
    log=None,
    _subprocess_run=None,
) -> dict:
    """Ask the configured ACP runner to validate `payload`.

    Returns a dict with keys `should_post`, `reason`, `improved_text`, `confidence`.

    When the runner is unreachable / errors / returns unparseable output:
      - `fail_open=False` (default) → returns `should_post=False` (skip the post).
      - `fail_open=True`            → returns `should_post=True`  (post anyway).

    `_subprocess_run` is the test seam — pass a callable mimicking
    `subprocess.run` to stub out the runner.
    """
    if log is None:
        log = get_logger("slack-validator")

    runner = runner or os.environ.get("ADK_VALIDATOR_RUNNER", DEFAULT_RUNNER)
    model = model or os.environ.get("ADK_VALIDATOR_MODEL", DEFAULT_MODEL)
    # `resolve_runner_model` accepts a friendly tier name; pass model through.
    chosen_model = resolve_runner_model(runner=runner, explicit_model=model)

    prompt = _build_prompt(payload)
    try:
        cmd = build_agent_cmd(prompt, runner=runner, model=chosen_model)
    except Exception as e:
        log.warning("validator: build_agent_cmd failed (%s) — fail_open=%s", e, fail_open)
        return _safe_default(
            should_post=fail_open,
            reason=f"validator unreachable: {e!r}",
        )

    runner_fn = _subprocess_run or subprocess.run
    try:
        proc = runner_fn(
            cmd, capture_output=True, text=True, timeout=timeout_s, check=False,
        )
    except subprocess.TimeoutExpired:
        log.warning("validator: timeout after %.1fs — fail_open=%s", timeout_s, fail_open)
        return _safe_default(should_post=fail_open, reason="validator timed out")
    except FileNotFoundError as e:
        log.warning("validator: runner binary missing (%s) — fail_open=%s", e, fail_open)
        return _safe_default(should_post=fail_open,
                             reason=f"validator binary missing: {e!r}")
    except Exception as e:
        log.warning("validator: subprocess crashed (%s) — fail_open=%s", e, fail_open)
        return _safe_default(should_post=fail_open,
                             reason=f"validator crashed: {e!r}")

    if proc.returncode != 0:
        log.warning("validator: runner rc=%d stderr=%r — fail_open=%s",
                    proc.returncode, (proc.stderr or "")[:200], fail_open)
        return _safe_default(should_post=fail_open,
                             reason=f"validator rc={proc.returncode}")

    parsed = _parse_response(proc.stdout or "")
    if not isinstance(parsed, dict):
        log.warning("validator: unparseable output (%r) — fail_open=%s",
                    (proc.stdout or "")[:200], fail_open)
        return _safe_default(should_post=fail_open,
                             reason="validator output not JSON")

    should_post = bool(parsed.get("should_post"))
    reason = str(parsed.get("reason") or "")
    improved = parsed.get("improved_text")
    if improved is not None and not isinstance(improved, str):
        improved = None
    try:
        confidence = float(parsed.get("confidence", 0.0))
    except (TypeError, ValueError):
        confidence = 0.0
    confidence = max(0.0, min(1.0, confidence))

    # Only honour an improved_text when the model is confident enough.
    if improved and confidence < rewrite_confidence_threshold:
        improved = None

    return {"should_post": should_post, "reason": reason,
            "improved_text": improved, "confidence": confidence}
