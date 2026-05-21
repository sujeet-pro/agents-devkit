"""slack_helpers.py — Slack Web-API helpers used by the `adk` CLI.

Originally lived under `skills/adk-pr-reviews/scripts/`; moved here because the
CLI is the canonical consumer (the `/adk-pr-review` skill also imports from
here when it needs to react/reply on the Slack thread that referenced a PR).

All credential reading honours constitution §VII — the token value is never
echoed; only its presence is asserted.

Auth (first hit wins):
  $SLACK_USER_TOKEN_CRED · $SLACK_USER_TOKEN · $SLACK_BOT_TOKEN_CRED · $SLACK_BOT_TOKEN
  ~/.config/creds/slack/slack.token.json {user_token | bot_token}

API surface:
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
  hours_ago_ts(hours) → str
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

    Per constitution §VII the value never enters LLM context — only the source name does.
    """
    for env_name in ("SLACK_USER_TOKEN_CRED", "SLACK_USER_TOKEN",
                     "SLACK_BOT_TOKEN_CRED", "SLACK_BOT_TOKEN"):
        v = os.environ.get(env_name)
        if v:
            return v, f"env:{env_name}"

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


_MENTION_RE = re.compile(r"<@([UW][A-Z0-9]+)(?:\|[^>]*)?>")


def find_pr_urls(text: str, url_patterns: list[str]) -> list[str]:
    """Find every URL in `text` that starts with one of the patterns. Case-insensitive.
    Preserves first-seen order.
    """
    if not text or not url_patterns:
        return []
    out: list[str] = []
    seen: set[str] = set()
    # First: Slack's <url> form (often with |display-text).
    for m in re.finditer(r"<(https?://[^>|]+)(?:\|[^>]*)?>", text):
        url = m.group(1)
        for pat in url_patterns:
            if url.lower().startswith(pat.lower()):
                if url not in seen:
                    seen.add(url)
                    out.append(url)
                break
    # Then bare URLs.
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


def hours_ago_ts(hours: float) -> str:
    """Return a slack `oldest=` timestamp for N hours ago."""
    dt = datetime.now(tz=timezone.utc) - timedelta(hours=hours)
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
        s = name_or_id.strip()
        if s in self._channel_cache:
            return self._channel_cache[s]
        if s.startswith(("C", "G")) and s[1:].isalnum():
            self._channel_cache[s] = s
            return s
        bare = s.lstrip("#").strip()

        # 1. users.conversations — channels the calling identity is a MEMBER of.
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

        # 2. conversations.list — any channel visible.
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


# ----- Review reply (§6.y.1) ----------------------------------------------

VERDICT_EMOJI = {
    "approved": "✅",
    "approve": "✅",
    "comments": "⚠",
    "comment_only": "⚠",
    "reviewed": "🚫",
    "request_changes": "🚫",
    "merged": "🔒",
    "closed": "🔒",
}

VERDICT_WORD = {
    "approved": "Approved",
    "approve": "Approved",
    "comments": "Comments",
    "comment_only": "Comments",
    "reviewed": "Changes requested",
    "request_changes": "Changes requested",
    "merged": "Merged",
    "closed": "Closed",
}


def _lookup_slack_user_id(host: str, login: str | None) -> str | None:
    """Resolve a GitHub/Bitbucket login to a Slack user ID via core.yaml's
    user_mappings block. Returns None when no mapping exists.

    core.yaml schema:
      user_mappings:
        github_to_slack:
          sujeet-pro: U123ABC
        bitbucket_to_slack:
          some-nickname: U456DEF
    """
    if not login:
        return None
    try:
        import os
        import yaml  # type: ignore
        home = (os.environ.get("ADK_HOME")
                or str(Path.home() / ".agents-devkit"))
        core = Path(home) / "config" / "core.yaml"
        if not core.exists():
            return None
        cfg = yaml.safe_load(core.read_text(encoding="utf-8")) or {}
        block_key = "github_to_slack" if host == "github" else "bitbucket_to_slack"
        mapping = ((cfg.get("user_mappings") or {}).get(block_key) or {})
        sid = mapping.get(login)
        if sid and isinstance(sid, str):
            return sid
    except Exception:
        pass
    return None


def render_review_reply(
    *,
    host: str,
    owner: str,
    repo: str,
    pr_number: int,
    pr_url: str,
    head_sha: str | None,
    author_login: str | None,
    status: str,
    summary_tldr: str,
    bullets: list[str],
) -> str:
    """Compose the 3-section v4 §6.y.1 Slack reply.

    Line 1: <emoji> *<verdict>* — <tldr>
    Line 2: 📌 `<owner-or-ws>/<repo>#<n>` · status `<status>` · head `<sha[:12]>` · author <@U…> | @login
    Lines 3..: bullet summary

    Hard rules:
      - Line 1 truncated to ~100 chars.
      - PR identifier backticked, never folded into URL anchor.
      - Bullets ≤ 80 chars each, 4-6 bullets max.
      - URL bullet always present.
    """
    emoji = VERDICT_EMOJI.get(status, "ℹ")
    word = VERDICT_WORD.get(status, status.title())
    line1 = f"{emoji} *{word}* — {summary_tldr.strip()}"
    if len(line1) > 100:
        line1 = line1[:97] + "…"

    # Author mention.
    slack_uid = _lookup_slack_user_id(host, author_login)
    if slack_uid:
        author_part = f"<@{slack_uid}>"
    elif author_login:
        author_part = f"@{author_login}"
    else:
        author_part = "(author unknown)"

    head_part = f" · head `{head_sha[:12]}`" if head_sha else ""
    line2 = (f"📌 `{owner}/{repo}#{pr_number}` · status `{status}`"
             f"{head_part} · author {author_part}")

    # Bullets — cap at 6, truncate each at 80.
    capped = []
    for b in (bullets or [])[:6]:
        b = b.strip().rstrip(".")
        if len(b) > 80:
            b = b[:77] + "…"
        capped.append(f"• {b}")
    # Always include the URL bullet, prefixed 🔗.
    if not any(pr_url in c for c in capped):
        capped.append(f"• 🔗 {pr_url}")

    return "\n".join([line1, line2, *capped])


def post_review_slack_reply(
    client: "SlackClient",
    *,
    channel_id: str,
    thread_ts: str,
    text: str,
    log=None,
) -> str | None:
    """Post the rendered review reply into the queue row's Slack thread.

    Returns the new message's ts on success, None on failure (with log).
    Idempotency check is the caller's job — see `post-result.json:slack_reply_ts`.
    """
    ts = client.post_thread_reply(channel_id, thread_ts, text)
    if log:
        if ts:
            log.info("slack: posted review reply ts=%s in channel=%s thread=%s",
                     ts, channel_id, thread_ts)
        else:
            log.warning("slack: post_review_slack_reply returned None — see prior errors")
    return ts


# ----- Auto-approve gate (§6.z) -------------------------------------------

# Severities that block auto-approve. Question / appreciation / nitpick /
# may-have DO NOT count as defects per §6.z.
APPROVE_BLOCKING_SEVERITIES = frozenset({"blocker", "critical", "should-have"})


def compute_approve_ready(
    findings: list[dict],
    existing_comment_actions: list[dict] | None = None,
    *,
    pr_state: str | None = None,
    no_approve_flag: bool = False,
) -> tuple[bool, str | None]:
    """v4 §6.z auto-approve gate. Returns (approve_ready, reason_if_no).

    approve_ready=True iff ALL of:
      1. findings[] contains zero entries with severity in APPROVE_BLOCKING.
      2. existing_comment_actions[] contains zero entries where the bot
         decided to reopen a prior thread because of a FRESH finding (the
         reopen is the bot's call, not an offline-alignment passthrough).
      3. PR is in a non-terminal state (not MERGED / CLOSED / DECLINED /
         closed / merged).
      4. --no-approve flag is NOT set.

    Returns the reason as a short, user-readable string when not approving
    (suitable for inclusion in the Slack reply).
    """
    if no_approve_flag:
        return False, "auto-approve disabled (--no-approve)"

    if pr_state and pr_state.upper() in {"MERGED", "CLOSED", "DECLINED",
                                          "SUPERSEDED"}:
        return False, f"PR is in terminal state ({pr_state})"

    blocking = [f for f in (findings or [])
                if (f.get("severity") or "") in APPROVE_BLOCKING_SEVERITIES]
    if blocking:
        return False, (f"{len(blocking)} blocking finding(s) "
                       f"({', '.join(b.get('severity', '?') for b in blocking[:3])})")

    fresh_reopens = [a for a in (existing_comment_actions or [])
                     if a.get("decision") == "reopen"
                     and not (a.get("offline_alignment_detected") is True)]
    if fresh_reopens:
        return False, f"{len(fresh_reopens)} prior thread(s) reopened by bot review"

    return True, None

    # ----- low-level -----

    def _call(self, method_dot: str, params: dict) -> dict:
        method_name = method_dot
        for attempt in range(3):
            try:
                fn = getattr(self._client, method_name)
                resp = fn(**params)
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
