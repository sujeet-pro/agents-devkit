"""adk Slack helpers — bot identity decoration for chat.postMessage payloads.

Public API:
    from scripts.lib.slack import decorate_post_payload, bot_footer, bot_name

Behavior:
    - `decorate_post_payload(params)` injects username + icon + footer into a
      chat_postMessage params dict (idempotent).
    - When posting via a Slack bot token (xoxb-), username + icon_emoji/icon_url
      are honored. Under a user token (xoxp-) Slack ignores those fields, but
      the footer text still appears, which is the load-bearing piece of the
      "Sent by …'s Automation Setup" attribution.
"""

from .post import (
    bot_footer,
    bot_name,
    decorate_post_payload,
    AUTOMATION_FOOTER_MARK,
)

__all__ = [
    "bot_footer", "bot_name", "decorate_post_payload",
    "AUTOMATION_FOOTER_MARK",
]
