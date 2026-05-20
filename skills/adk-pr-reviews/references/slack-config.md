# slack.json5 config — adk-pr-reviews

Default location: `~/.agents-devkit/config/pr-reviews-slack.json5`. Template at `skills/adk-pr-reviews/templates/pr-reviews-slack.json5`.

This config is read by **both** scripts:

- `scan_slack.py` — to know which channels to scan, what counts as a PR URL, who to filter by.
- `run_batch.py` — to know which emoji corresponds to which status (for reactions) and how to format reminders.

## Auth — user token preferred

The scan + reactions + reminders all run **as you** (using your user token), which means:

- The bot does NOT need to be invited to channels — you already are a member.
- Reactions appear from your account, not a bot account.
- Reminder messages post as you (most natural for the readers in the thread).

Lookup order (first hit wins):

1. `$SLACK_USER_TOKEN_CRED` (xoxp- token; canonical adk naming)
2. `$SLACK_USER_TOKEN`
3. `$SLACK_BOT_TOKEN_CRED` (xoxb- token; fallback)
4. `$SLACK_BOT_TOKEN`
5. `~/.config/creds/slack/slack.token.json` → `user_token` (preferred), else `bot_token`

The script logs only the **kind** of token (`user` or `bot`) and the **source** name — never the value (constitution §VII).

### Required OAuth scopes

For a **user token** (xoxp-) — these scopes are granted to the user identity at app-install time:

- `channels:history`, `groups:history`, `im:history`, `mpim:history` — read messages.
- `channels:read`, `groups:read` — resolve channel names to IDs.
- `users:read`, `users:read.email` — resolve `@Display Name` and email filter tokens.
- `chat:write` — post thread-reply reminders.
- `reactions:write` — add/remove reactions.

For a **bot token** (xoxb-) — same scopes, plus the bot must be `/invite`d to every channel it scans.

## Field reference

### `channels: []` (required)

List of channel IDs (`C…` / `G…`) or names (`#eng-reviews`, `eng-reviews`). Names are resolved at scan time and cached into `channel_id_cache` to avoid repeated lookups.

Empty list → the scan refuses to run.

### `url_patterns: []` (required)

Case-insensitive prefix patterns. Any URL in a slack message that **starts with** any of these is considered a PR link. Examples:

```json5
url_patterns: [
  "https://github.com/",                  // all of GH
  "https://github.com/acme/",             // only the `acme` org
  "https://bitbucket.org/lastbrand/",     // only the `lastbrand` workspace
]
```

If `url_patterns` is empty → scan refuses.

The scanner ALSO uses these to count `n_pr_links_in_message`, which gates whether reactions can be applied unambiguously.

### `status_emoji: {…}` (recommended)

Mapping of status → emoji name (without the surrounding `:`). `null` means "don't react for this status".

```json5
status_emoji: {
  pending:    null,
  in_review:  "eyes",
  reviewed:   "white_check_mark",    // reviewed clean, not yet host-approved
  comments:   "warning",             // findings > 0
  needs_fix:  "warning",             // back-compat alias of `comments`
  approved:   "heavy_check_mark",    // host APPROVED or recommendation:approve
  merged:     "tada",
  error:      "x",
  reminded:   "bell",
}
```

Two transition modes:

**Normal transition** (e.g. `in_review` → `comments`):
1. Remove the previous emoji (per `last_reaction_status`).
2. Add the new emoji.

**Terminal-positive transition** (`* → approved` or `* → merged`):
1. Sweep **every** configured status emoji off the message. Defensive — catches any stale reaction (e.g. an old `:warning:` that wasn't removed because `last_reaction_status` was empty or pointed to something else).
2. Add the final emoji.

So once a PR is approved or merged, only the final emoji remains; the prior `:eyes:` / `:warning:` are gone.

If a status's mapping is `null`, no emoji is added for that status. The transition itself still gets recorded in `slack.last_reaction_status`.

### `filter_mentioned_users: []` (optional)

A scan-time filter. Only include PRs where **at least one** of these users appears in either:

- the **main message** that contains the PR link, OR
- **any reply** in the same thread.

Tokens can be `@display-name`, `@username`, or a raw `U…` user ID. The script resolves names → IDs at scan time.

Empty list / omitted → no user filter (every PR-link message counts). Set to a multi-user list for a team — any-of semantics.

### `scan_days_default: 14` (optional, default 14)

How many days back the scan reads. Override per-invocation with `--since N`.

### `reminder: {…}` (optional, default enabled)

```json5
reminder: {
  enabled: true,
  after_hours: 24,                       // remind only when last_reviewed > this
  tag_users: ["author", "thread_starter"],
  message_template: "PR review pending — please address the {pending_findings} open comments above. cc {author} {thread_starter}",
  min_hours_between_reminders: 24,       // per-PR rate limit
}
```

`tag_users` tokens:

| Token | Resolves to |
|---|---|
| `"author"` | The PR author (from gh/bb metadata). |
| `"thread_starter"` | The slack user who started the thread. |
| `"@<name>"` | Literal slack user. |
| `"U…"` | Literal slack user ID. |

Each resolved user gets wrapped as `<@U…>` in the posted reply (slack's mention syntax). The template's `{author}` / `{thread_starter}` placeholders are filled with the corresponding mentions; any tag_users token that doesn't appear in the template gets appended at the end of the message.

`{pending_findings}` is substituted with the integer count of open findings from the last review.

### `channel_id_cache: {…}` (auto-managed)

The scanner writes resolved channel-name → ID pairs here so subsequent scans skip the lookup. You can edit but don't have to.

## When the scan refuses

| Condition | Refusal |
|---|---|
| `channels` empty | "nothing to scan" |
| `url_patterns` empty | "nothing to recognise as a PR" |
| `SLACK_BOT_TOKEN_CRED` unset | "no token; see references/slack-config.md auth section" |
| Bot can't see a channel | warning logged, channel skipped, other channels still scan |

## What the scan does NOT do

- Post anything (except merged-emoji reactions on merged PRs — and only on single-PR-link messages).
- Modify slack settings, channel topics, pinned items.
- Read DMs or messages the bot wasn't invited to.
- Persist any PII. The queue file holds only IDs (channel, message, user) — no display names, no message bodies.

## Generating the config

Use the template as a starting point:

```bash
mkdir -p ~/.agents-devkit/config
cp skills/adk-pr-reviews/templates/pr-reviews-slack.json5 \
   ~/.agents-devkit/config/pr-reviews-slack.json5
${EDITOR:-vi} ~/.agents-devkit/config/pr-reviews-slack.json5
```

Edit `channels`, `url_patterns`, optionally `filter_mentioned_users`. Save.

Then:

```bash
# First scan — dry-run shows what WOULD be added.
python3 skills/adk-pr-reviews/scripts/scan_slack.py --dry-run

# Live scan — populates ~/.agents-devkit/pr-reviews/queue.json5
python3 skills/adk-pr-reviews/scripts/scan_slack.py

# Or, combined with a batch run:
/adk-pr-reviews --scan -p 3
```

The scan is idempotent on the queue (additive merge by `repo+pr-number`) — re-running is safe.
