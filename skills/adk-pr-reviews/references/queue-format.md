# queue.json5 format — adk-pr-reviews

Default location: `~/.agents-devkit/pr-reviews/queue.json5`. Template at `skills/adk-pr-reviews/templates/queue.json5`.

JSON5 is a superset of JSON that allows `// line comments` and trailing commas. Hand-edit freely — the script preserves your `notes` and `supporting_docs` and never touches comments on read.

## Top-level shape

```json5
{
  filters: null,    // optional batch-level filters (see slack.json5 for the global one)
  prs: [
    { /* per-PR entry */ },
    …
  ],
}
```

## Per-PR entry

| Field | Required? | Owner | Purpose |
|---|---|---|---|
| `pr_link` | **yes** | user / scan | The PR URL (GitHub or Bitbucket Cloud). |
| `slack` | optional | user / scan | Slack context for status reactions + reminders. See *Slack sub-object* below. |
| `supporting_docs[]` | optional | user / scan | URLs (Jira / Confluence / GDoc / Figma) that the reviewer must consult. **Forced** — used even if the PR body doesn't link them. Scan adds these by parsing the slack thread. |
| `status` | auto | script | `pending` / `in_review` / `comments` / `reviewed` / `approved` / `merged` / `error` / `reminded`. `needs_fix` is a legacy alias of `comments`. |
| `last_checked_at` | auto | script | ISO8601 — bumped on every batch touch, even skip-stable. |
| `notes` | optional | **user** | Free-form. Script never writes this. |

The unique key per entry is **`(host, repo, pr_number)`** — derived from `pr_link`. The same repo at the same PR number, regardless of owner spelling or trailing-slash differences, dedupes to a single entry.

## Slack sub-object

```json5
slack: {
  permalink:                "https://acme.slack.com/archives/C0123456/p1745432100000123",
  channel_id:               "C0123456",
  message_ts:               "1745432100.000123",  // the message that contains the PR link
  thread_ts:                "1745432100.000123",  // top-level of the thread (== message_ts if root)
  thread_starter_user_id:   "U0ABCDEFG",
  n_pr_links_in_message:    1,                    // ≥2 means reactions are ambiguous and get skipped
  last_reaction_status:     null,                 // what we last reacted with — internal bookkeeping
  last_reminder_at:         null,                 // ISO8601 — gates the reminder rate-limit
}
```

The scan populates everything except `last_reaction_status` and `last_reminder_at`. You can hand-edit `permalink` and the script will leave you alone, BUT if you change `channel_id` or `message_ts` you'll get a fresh reaction series — the script doesn't know it's the same thread.

### When `n_pr_links_in_message > 1`

The slack message had multiple PR links in one post. Reactions become ambiguous — a `:white_check_mark:` on the message could mean any of the linked PRs is reviewed. The script:

- **Skips ALL reactions** for these entries (status transitions don't react).
- **Still posts thread reminders** — those name the specific PR in the text, so they're unambiguous.

If you want reactions on a multi-PR message, split the message in slack and re-scan.

## Status lifecycle

```
                  scan or hand-add
                       │
                       ▼
                   pending ─────────► merged   (terminal; never downgrades)
                       │                 ▲      (PR merged on host)
              first review               │
                       │                 │
                       ▼                 │
                  in_review ─────────────┤
                       │                 │
       ┌───────────────┼──────────────┐  │
       │               │              │  │
       ▼               ▼              ▼  │
  comments         reviewed        approved
  (findings>0)   (clean, not       (clean, host
                  yet approved)     APPROVED OR
                                    recommendation:
                                    approve)
       │               │              │
   new commit      new commit      new commit
       │           (back to        (re-check on
       ▼            in_review)      new push)
   in_review ─────────┘              │
                                     ▼
       │                          merged
   re_review_required
   + > reminder.after_hours
   + slack thread present
       ▼
   reminded   (slack reply posted; rate-limited)
```

Transitions INTO `approved` or `merged` sweep all OTHER configured status emojis off the slack message — only the final emoji remains.

The script only writes the `status` field, never reads it as authoritative — `<task_dir>/state.json` is the source of truth for `last_reviewed_head_oid` etc. Queue `status` is a UX hint.

## Status → emoji (governed by slack.json5)

The script doesn't hard-code an emoji-per-status mapping. The mapping lives in `~/.agents-devkit/config/pr-reviews-slack.json5` under `status_emoji.*`. `null` means "no emoji for this status".

## Hand-adding a PR

Minimum entry:

```json5
{
  prs: [
    { pr_link: "https://github.com/acme/foo/pull/42" },
  ],
}
```

That's enough — the next batch run picks it up, runs the review, posts comments. No slack context = no reactions / reminders.

Add supporting docs:

```json5
{
  prs: [
    {
      pr_link: "https://github.com/acme/foo/pull/42",
      supporting_docs: [
        "https://acme.atlassian.net/browse/SF-1234",
        "https://docs.google.com/document/d/abc/edit",
      ],
      notes: "design doc was updated yesterday",
    },
  ],
}
```

## Editing while a batch is running

Safe — every write goes through `<queue-path>.lock` (fcntl). In-flight reviews already past the queue read won't see your edit until next batch invocation; that's fine.

## Migrating from the old CSV

```bash
# One-time conversion. The script writes JSON5 with default fields.
python3 - <<'PY'
import csv, json
from pathlib import Path
csv_path = Path.home() / ".agents-devkit" / "pr-reviews" / "queue.csv"
out_path = Path.home() / ".agents-devkit" / "pr-reviews" / "queue.json5"
prs = []
with csv_path.open() as fh:
    for r in csv.DictReader(fh):
        if r.get("pr_url"):
            prs.append({"pr_link": r["pr_url"].strip(),
                        "status": (r.get("status") or "pending").strip(),
                        "notes": (r.get("notes") or "").strip()})
out_path.write_text(json.dumps({"filters": None, "prs": prs}, indent=2) + "\n")
print(f"wrote {len(prs)} entries to {out_path}")
PY
```

(The CSV format is no longer supported. The conversion is a one-shot.)
