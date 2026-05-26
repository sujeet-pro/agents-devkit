"""scripts/lib/slack/post.py — bot identity decoration for Slack posts.

Single source of truth for: "every message adk sends to Slack ends with the
configured footer, and (when posted via a bot token) appears with the configured
icon and name." Reads ``core.json5`` :: bot + user via the v5 ConfigBundle.

The functions here NEVER call Slack themselves — they decorate a
``chat.postMessage`` payload dict. The actual API call lives in
``slack_helpers.SlackClient`` (which delegates the decoration here).

This split exists so:
  - tests can assert "the footer gets injected" without mocking HTTP
  - any future Slack callsite (incident-response skill, alert routers) can call
    decorate_post_payload before talking to Slack and pick up the same persona
"""

from __future__ import annotations

import sys
from pathlib import Path

# Self-bootstrap: make ``scripts/lib/`` importable so ``config`` resolves.
_LIB_DIR = Path(__file__).resolve().parent.parent
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))


# A zero-width marker we prepend to the rendered footer so that repeated
# decorate_post_payload calls don't stack multiple footers in the text.
# Renders invisibly in Slack but is searchable by code.
AUTOMATION_FOOTER_MARK = "​"  # ZERO-WIDTH SPACE


def bot_name() -> str:
    """Return the configured automation persona name, with first_name interpolated."""
    from config import get_bundle
    return get_bundle().bot_name()


def bot_footer() -> str:
    """Return the rendered footer string (without leading marker / italics)."""
    from config import get_bundle
    return get_bundle().bot_footer()


def _rendered_footer_line() -> str:
    """The exact line we append to message text — italicized, with marker."""
    return f"{AUTOMATION_FOOTER_MARK}_{bot_footer()}_"


def _append_footer_to_text(text: str | None) -> str:
    """Append the footer to `text`, idempotent."""
    footer_line = _rendered_footer_line()
    if not text:
        return footer_line
    if AUTOMATION_FOOTER_MARK in text:
        # already decorated — leave as-is
        return text
    return text.rstrip() + "\n\n" + footer_line


def _append_footer_to_blocks(blocks: list | None) -> list | None:
    """Append a context block carrying the footer, idempotent.

    Returns the unchanged ``blocks`` reference if no blocks supplied.
    """
    if not blocks:
        return blocks
    # idempotency: scan existing blocks for our marker
    for blk in blocks:
        if isinstance(blk, dict) and blk.get("type") == "context":
            for el in blk.get("elements", []):
                if isinstance(el, dict):
                    text = el.get("text", "")
                    if isinstance(text, str) and AUTOMATION_FOOTER_MARK in text:
                        return blocks
    footer_block = {
        "type": "context",
        "elements": [{"type": "mrkdwn", "text": _rendered_footer_line()}],
    }
    return list(blocks) + [footer_block]


def decorate_post_payload(params: dict) -> dict:
    """Return a new dict — same as ``params`` but with bot identity injected.

    Idempotent: calling twice produces the same output.

    What we inject:
      • ``username``        — bot_name() — visible only when posting via bot token
      • ``icon_url`` OR ``icon_emoji`` — preferring icon_url if set on the bundle
      • footer line appended to ``text``       — works under any token
      • footer context block appended to ``blocks`` (if present) — for richer messages

    Caller-set fields win — if you pass username, icon_url, etc., we don't override.
    """
    from config import get_bundle
    bundle = get_bundle()
    bot = bundle.bot

    out = dict(params)
    out.setdefault("username", bundle.bot_name())
    if bot.icon_url:
        out.setdefault("icon_url", bot.icon_url)
    elif bot.icon_emoji:
        out.setdefault("icon_emoji", bot.icon_emoji)

    # Always inject the footer into text, even when blocks present (Slack falls
    # back to text in notifications + accessibility paths).
    out["text"] = _append_footer_to_text(out.get("text"))

    if "blocks" in out and out["blocks"]:
        out["blocks"] = _append_footer_to_blocks(out["blocks"])

    return out


__all__ = [
    "AUTOMATION_FOOTER_MARK",
    "bot_name",
    "bot_footer",
    "decorate_post_payload",
]
