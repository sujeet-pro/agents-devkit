"""slack_helpers.py — slack Web-API helpers for /adk-pr-reviews.

All credential reading honours constitution §VII — the token value is never
echoed; only its presence is asserted.

Auth: $SLACK_BOT_TOKEN_CRED preferred, falls back to $SLACK_BOT_TOKEN.

API surface (kept minimal):
  client = SlackClient()                                  # raises if no token
  client.resolve_channel(name_or_id) → channel_id
  client.iter_channel_messages(channel_id, oldest_ts) → iter[message]
  client.iter_thread_replies(channel_id, thread_ts) → iter[reply]
  client.get_message_permalink(channel_id, ts) → str
  client.get_user(user_id) → {id, name, real_name}
  client.add_reaction(channel_id, ts, emoji_name) → bool
  client.remove_reaction(channel_id, ts, emoji_name) → bool
  client.post_thread_reply(channel_id, thread_ts, text) → ts

Module-level helpers (no auth needed):
  find_pr_urls(text, url_patterns) → list[str]
  count_pr_urls(text, url_patterns) → int
  extract_mentioned_user_ids(text) → list[user_id]
  days_ago_ts(days) → str          # slack oldest= argument
"""
from __future__ import annotations

import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator

# Reuse helpers from sibling skill.
ADK_PR_REVIEW_SCRIPTS = Path(__file__).resolve().parent.parent.parent / "adk-pr-review" / "scripts"
sys.path.insert(0, str(ADK_PR_REVIEW_SCRIPTS))
from _common import die, get_logger  # noqa: E402


def _get_token() -> tuple[str, str]:
    """Return (token, source). Prefers user-token (xoxp-) so reads/posts appear as
    the user. Falls back to bot-token (xoxb-) if no user token is configured.

    Lookup order:
      1. $SLACK_USER_TOKEN_CRED              (user token, _CRED naming)
      2. $SLACK_USER_TOKEN
      3. $SLACK_BOT_TOKEN_CRED
      4. $SLACK_BOT_TOKEN
      5. ~/.config/creds/slack/slack.token.json `user_token` field
      6. ~/.config/creds/slack/slack.token.json `bot_token`  field

    Per constitution §VII the value never enters LLM context — only the source name does.
    """
    # 1–4: env vars.
    for env_name in ("SLACK_USER_TOKEN_CRED", "SLACK_USER_TOKEN",
                     "SLACK_BOT_TOKEN_CRED", "SLACK_BOT_TOKEN"):
        v = os.environ.get(env_name)
        if v:
            return v, f"env:{env_name}"

    # 5–6: token.json (canonical adk-creds location).
    token_json = Path.home() / ".config" / "creds" / "slack" / "slack.token.json"
    if token_json.exists():
        try:
            import json as _json
            data = _json.loads(token_json.read_text(encoding="utf-8"))
            for key in ("user_token", "bot_token"):
                v = data.get(key)
                if v:
                    return v, f"file:{token_json.name}:{key}"
        except Exception:
            pass

    die(
        "No Slack token found. Set one of:\n"
        "  SLACK_USER_TOKEN_CRED (preferred — posts/reads as you)\n"
        "  SLACK_BOT_TOKEN_CRED\n"
        "or ensure ~/.config/creds/slack/slack.token.json has `user_token` / `bot_token`.\n"
        "Per constitution §VII the value is never echoed."
    )
    return "", ""  # unreachable


# Mention pattern in slack text: <@U…>
_MENTION_RE = re.compile(r"<@([UW][A-Z0-9]+)(?:\|[^>]*)?>")
_BARE_LOOKING_RE = re.compile(r"@([a-zA-Z0-9_\.-]+)")


def find_pr_urls(text: str, url_patterns: list[str]) -> list[str]:
    """Find every URL in `text` that starts with one of the patterns. Case-insensitive."""
    if not text or not url_patterns:
        return []
    # Liberal URL match — slack messages often wrap URLs in <…>.
    out: list[str] = []
    seen: set[str] = set()
    # First: try slack's own <url> form.
    for m in re.finditer(r"<(https?://[^>|]+)(?:\|[^>]*)?>", text):
        url = m.group(1)
        for pat in url_patterns:
            if url.lower().startswith(pat.lower()):
                if url not in seen:
                    seen.add(url)
                    out.append(url)
                break
    # Then bare URLs (not inside <>).
    for m in re.finditer(r"https?://[^\s<>\]\)]+", text):
        url = m.group(0).rstrip(".,);:")
        for pat in url_patterns:
            if url.lower().startswith(pat.lower()):
                if url not in seen:
                    seen.add(url)
                    out.append(url)
                break
    return out


def count_pr_urls(text: str, url_patterns: list[str]) -> int:
    return len(find_pr_urls(text, url_patterns))


def extract_mentioned_user_ids(text: str) -> list[str]:
    """Return Slack user IDs (e.g. ['U0ABC123', 'U0XYZ']) mentioned in the text."""
    if not text:
        return []
    return list({m.group(1) for m in _MENTION_RE.finditer(text)})


def days_ago_ts(days: int) -> str:
    """Return a slack `oldest=` timestamp for N days ago."""
    dt = datetime.now(tz=timezone.utc) - timedelta(days=days)
    return f"{dt.timestamp():.6f}"


class SlackClient:
    """Thin wrapper around slack_sdk.WebClient with read-only-ish defaults."""

    def __init__(self):
        try:
            from slack_sdk import WebClient  # type: ignore
            from slack_sdk.errors import SlackApiError  # type: ignore
        except ImportError:
            die(
                "slack-sdk not installed. pip install -r "
                f"{Path(__file__).parent / 'requirements.txt'}"
            )
        self.WebClient = WebClient
        self.SlackApiError = SlackApiError
        token, source = _get_token()
        # Detect token kind from prefix — `xoxp-` = user token, `xoxb-` = bot token.
        # We do NOT log the value, only the prefix.
        kind = "user" if token.startswith("xoxp-") else ("bot" if token.startswith("xoxb-") else "unknown")
        self.token_kind = kind
        self.token_source = source
        self._client = WebClient(token=token)
        self._user_cache: dict[str, dict] = {}
        self._channel_cache: dict[str, str] = {}
        self.log = get_logger("slack")
        self.log.info("slack auth: token_kind=%s source=%s", kind, source)

    # ----- channels -----

    def resolve_channel(self, name_or_id: str) -> str:
        """Accept '#name', 'name', or 'C…' / 'G…'; return channel ID.

        Strategy:
          1. If it's already an ID-shaped string, accept it.
          2. With a USER token: list the channels the user is a member of (cheap +
             includes private channels). This covers the common case where the user
             is in the channel they want to scan.
          3. Fall back to `conversations.list` over public + private channels (works
             for bot tokens; for user tokens it also enumerates public channels the
             user can SEE but isn't in).
        """
        s = name_or_id.strip()
        if s in self._channel_cache:
            return self._channel_cache[s]
        if s.startswith(("C", "G")) and s[1:].isalnum():
            self._channel_cache[s] = s
            return s
        bare = s.lstrip("#").strip()

        # 1. users.conversations — channels the calling identity is a MEMBER of.
        # Works for both user and bot tokens; user-token users typically ARE in their
        # own review channels, so this is the fast path.
        cursor = None
        while True:
            resp = self._call(
                "users_conversations",
                {"types": "public_channel,private_channel", "limit": 1000, "cursor": cursor},
            )
            for ch in resp.get("channels", []):
                if ch.get("name") == bare:
                    cid = ch["id"]
                    self._channel_cache[s] = cid
                    return cid
            cursor = resp.get("response_metadata", {}).get("next_cursor") or None
            if not cursor:
                break

        # 2. conversations.list — any channel visible (membership not required).
        for kind in ("public_channel", "private_channel"):
            cursor = None
            while True:
                try:
                    resp = self._call(
                        "conversations_list",
                        {"types": kind, "limit": 1000, "cursor": cursor},
                    )
                except self.SlackApiError:
                    break
                for ch in resp.get("channels", []):
                    if ch.get("name") == bare:
                        cid = ch["id"]
                        self._channel_cache[s] = cid
                        return cid
                cursor = resp.get("response_metadata", {}).get("next_cursor") or None
                if not cursor:
                    break

        hint = (
            "as a user, you may not have access — confirm you're a member of the channel"
            if self.token_kind == "user"
            else "as a bot, you likely need /invite @bot in that channel"
        )
        die(f"slack: channel `{name_or_id}` not found ({hint}).")
        return ""  # unreachable

    # ----- history / threads -----

    def iter_channel_messages(self, channel_id: str, oldest_ts: str) -> Iterator[dict]:
        cursor = None
        while True:
            resp = self._call(
                "conversations_history",
                {"channel": channel_id, "oldest": oldest_ts, "limit": 200, "cursor": cursor},
            )
            for m in resp.get("messages", []):
                yield m
            cursor = resp.get("response_metadata", {}).get("next_cursor") or None
            if not cursor:
                return

    def iter_thread_replies(self, channel_id: str, thread_ts: str) -> Iterator[dict]:
        cursor = None
        while True:
            resp = self._call(
                "conversations_replies",
                {"channel": channel_id, "ts": thread_ts, "limit": 200, "cursor": cursor},
            )
            for m in resp.get("messages", []):
                yield m
            cursor = resp.get("response_metadata", {}).get("next_cursor") or None
            if not cursor:
                return

    def get_message_permalink(self, channel_id: str, ts: str) -> str:
        resp = self._call("chat_getPermalink", {"channel": channel_id, "message_ts": ts})
        return resp.get("permalink", "")

    # ----- users -----

    def get_user(self, user_id: str) -> dict:
        if user_id in self._user_cache:
            return self._user_cache[user_id]
        try:
            resp = self._call("users_info", {"user": user_id})
        except Exception:
            return {"id": user_id, "name": user_id, "real_name": user_id}
        info = resp.get("user", {})
        d = {"id": info.get("id", user_id), "name": info.get("name", user_id),
             "real_name": info.get("real_name", info.get("name", user_id))}
        self._user_cache[user_id] = d
        return d

    def resolve_user_token(self, token: str) -> str | None:
        """Resolve a token like '@sujeet', '@Sujeet Jaiswal', 'sujeet@x.com', or 'U…'
        to a user ID. Matches `name`, `profile.display_name`, `profile.real_name`,
        `real_name`, and `profile.email`. Case-insensitive comparison."""
        if not token:
            return None
        if token.startswith(("U", "W")) and token[1:].isalnum():
            return token
        bare = token.lstrip("@").strip()
        bare_lower = bare.lower()
        cursor = None
        while True:
            resp = self._call("users_list", {"limit": 200, "cursor": cursor})
            for u in resp.get("members", []):
                if u.get("deleted") or u.get("is_bot"):
                    continue
                prof = u.get("profile") or {}
                candidates = [
                    u.get("name"),
                    u.get("real_name"),
                    prof.get("display_name"),
                    prof.get("real_name"),
                    prof.get("display_name_normalized"),
                    prof.get("real_name_normalized"),
                    prof.get("email"),
                ]
                if any((c or "").lower() == bare_lower for c in candidates):
                    uid = u.get("id")
                    if uid:
                        self._user_cache[uid] = {
                            "id": uid,
                            "name": u.get("name", bare),
                            "real_name": u.get("real_name", bare),
                        }
                        return uid
            cursor = resp.get("response_metadata", {}).get("next_cursor") or None
            if not cursor:
                return None

    # ----- reactions / posting -----

    def add_reaction(self, channel_id: str, ts: str, emoji_name: str) -> bool:
        emoji = emoji_name.strip(":")
        try:
            self._call("reactions_add", {"channel": channel_id, "timestamp": ts, "name": emoji})
            return True
        except self.SlackApiError as e:
            err = (getattr(e, "response", {}) or {}).get("error", "")
            if err == "already_reacted":
                return True
            self.log.warning("add_reaction(%s, %s, :%s:) → %s", channel_id, ts, emoji, err or e)
            return False

    def remove_reaction(self, channel_id: str, ts: str, emoji_name: str) -> bool:
        emoji = emoji_name.strip(":")
        try:
            self._call("reactions_remove", {"channel": channel_id, "timestamp": ts, "name": emoji})
            return True
        except self.SlackApiError as e:
            err = (getattr(e, "response", {}) or {}).get("error", "")
            if err in ("no_reaction", "message_not_found"):
                return True
            self.log.warning("remove_reaction(%s, %s, :%s:) → %s", channel_id, ts, emoji, err or e)
            return False

    def post_thread_reply(self, channel_id: str, thread_ts: str, text: str) -> str | None:
        try:
            resp = self._call(
                "chat_postMessage",
                {"channel": channel_id, "thread_ts": thread_ts, "text": text, "link_names": True},
            )
            return resp.get("ts")
        except self.SlackApiError as e:
            self.log.error("post_thread_reply failed: %s", e)
            return None

    # ----- low-level -----

    def _call(self, method_dot: str, params: dict) -> dict:
        """Call slack via the WebClient. `method_dot` uses underscore form (e.g.
        'conversations_history'); we map it to slack's dotted form internally.
        """
        method_name = method_dot
        # slack_sdk uses underscore form for method names → no transformation needed.
        for attempt in range(3):
            try:
                fn = getattr(self._client, method_name)
                resp = fn(**params)
                # Honour rate limit
                if resp.get("ok") is False:
                    raise self.SlackApiError("slack error", response=resp)
                return resp.data if hasattr(resp, "data") else dict(resp)
            except self.SlackApiError as e:
                err = (getattr(e, "response", {}) or {}).get("error", "")
                if err == "ratelimited":
                    retry = int((getattr(e, "response", {}) or {}).get("headers", {}).get("Retry-After", "2"))
                    time.sleep(retry + 1)
                    continue
                raise
        raise RuntimeError(f"slack call {method_dot} failed after retries")
