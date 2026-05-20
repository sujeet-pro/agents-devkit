# rules — adk-pr-reviews

## Must do

1. **Surface the plan + posting + slack scope before starting.** The invocation IS the per-invocation confirmation for posting PR comments AND for slack reactions/reminders (the user explicitly asked for these by configuring slack.json5). The skill prints a one-line plan first: "About to review N PRs (M would be skipped) and apply slack reactions / reminders per `pr-reviews-slack.json5`." Under `--dry-run`, NO writes to PRs or slack.
2. **Always honor per-PR lock.** Two workers never operate on the same `<repo>_pr-<n>` concurrently. Same PR appearing twice in the queue: second row gets `skipped-locked`.
3. **Always honor clone-lock.** All `git fetch / reset / worktree add` go through the per-repo clone-lock from `/adk-pr-review`.
4. **Additive on the queue.** Only `status`, `last_checked_at`, and the `slack` sub-object are auto-written. `notes`, `supporting_docs[]`, `pr_link`, comments, and column ordering are preserved verbatim.
5. **One `claude -p` per non-skipped row.** Each is a billed API call.
6. **Source of truth = per-PR `state.json`.** Queue `status` is a UX hint. Re-review decisions read state.json.

## Must not

1. **Never react on multi-PR-link messages.** When `slack.n_pr_links_in_message > 1`, a reaction is ambiguous (which PR is it for?) — the script skips reactions for that row entirely. Reminders still work because they name the specific `pr_link` in the text.
2. **Never post a slack reminder more frequently than `reminder.min_hours_between_reminders`.** Per-PR rate-limit.
3. **Never react with an emoji whose status mapping is `null`.** A `null` mapping means "explicitly silent for this status".
4. **Never overwrite a `merged` queue entry.** Terminal state — scan ignores it, batch skips it, no status downgrade.
5. **Never write slack message bodies / user display names to the queue.** Only IDs (channel, message, user) — no PII.
6. **Never include credentials in any URL in the queue.** Refuse rows where `pr_link` contains `user:token@`.
7. **Never spawn `claude -p` for a row whose status is `merged`.**

## Refusals (Phase 0 stops)

| Condition | Refusal |
|---|---|
| `queue.json5` not found AND `--scan` not passed | "queue not found at `<path>`. Run with `--scan` to generate, or copy `templates/queue.json5`." |
| `slack.json5` required (you passed `--scan`) but missing | "slack config not found. Copy `templates/pr-reviews-slack.json5` and edit channels/url_patterns." |
| `SLACK_BOT_TOKEN_CRED` unset AND `--scan` passed | "no token; see references/slack-config.md auth section." |
| `claude` CLI missing | "claude CLI not on PATH — the batch spawns it per row." |
| `--parallelism` outside [1, 16] | "parallelism out of range." |
| Any row has unsupported PR host | row marked `status=error`, batch continues. |
| Row PR URL embeds credentials | row marked `status=refused`, never processed. |

## Degradations (allowed; surfaced in the per-row summary)

- **Slack config missing in non-scan mode** → reactions + reminders silently disabled; reviews + posts still run. Logged as "slack: disabled".
- **`SLACK_BOT_TOKEN_CRED` unset in non-scan mode** → same as above.
- **`adk-mcp-statsig` unreachable** → per-row feature-flow tracing falls back to grep. Inherited from `/adk-pr-review`.
- **`adk-mcp-atlassian` unreachable** → Confluence/Jira from PR bodies skipped; `supporting_docs[]` from the queue are still read (they're file URLs we can fetch directly or via the agent's MCP after the row's review starts).
- **A single row's claude-p fails** → row marked `status=error`, batch continues.

## Composition with `/adk-pr-review`

`/adk-pr-reviews` wraps `/adk-pr-review` — all of that skill's hard rules apply per row:

- Always isolated to `~/.agents-devkit/pr-reviews/<repo>_pr-<n>/`.
- Serialised worktree creation via per-repo clone-lock.
- Multi-dimension review (correctness + security + tests minimum).
- Comment resolution per `/adk-pr-review/references/comment-resolution.md`.
- Posting gated by constitution §I.4 confirmation (which the batch invocation IS).
