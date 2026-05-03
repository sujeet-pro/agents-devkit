# `investigate-incident` — anti-patterns

## Single-source diagnosis

- "Logs show 5xx; the recent deploy must have caused it." Maybe — but check the deploy diff, the metrics, the traces, the Slack chatter. The deploy might be coincidental.
- **Fix:** the multi-source protocol requires at least 2 independent signals before naming a cause. If only one source agrees, the verdict is "leading candidate", not "root cause".

## High-confidence claim without correlation

- "Confidence: high. Cause: deploy `a3f9c2e`."
- High confidence requires multiple corroborating signals. See `confidence-language.md` for the anchoring.
- **Fix:** confidence is a function of the evidence, not the operator's hunch.

## Recommending rollback without checking the diff

- "Rollback `a3f9c2e`." But the diff is a one-line README change. Rollback won't help.
- **Fix:** before naming rollback as the action, run `gh pr view <pr>` (or read the diff inline). If the diff doesn't touch the affected service / endpoint / module, demote the rollback recommendation.

## Forgetting Slack

- The team in `#incidents` is already discussing the cause. They've named a culprit. They've considered (and ruled out) the recent deploy. Skipping the Slack scrape misses all this.
- **Fix:** if `slack-workspace` MCP is reachable, scrape the channel. Quote ≤15 words per message; preserve thread permalinks. Surface the team's leading hypothesis even if it differs from the skill's.

## Pasting raw incident chatter

- 30 messages of "anyone seeing 500s?" / "yeah" / "who's on call?" is noise.
- **Fix:** summarize the channel state in 2-3 sentences. List threads that named a cause or shared evidence. Quote ≤15 words per quoted message.

## Auto-triggering rollback

- `--auto` does NOT trigger rollback. Ever.
- **Fix:** the skill outputs a recommended action with the exact command to
  run. The operator executes it. A future explicitly write-enabled rollback
  workflow could opt into auto-rollback; this skill does not.

## Naming an individual as root cause

- "Alice's PR caused the incident."
- That's a person, not a system gap. The system gap is "the new query path has no integration test for renamed columns".
- **Fix:** the root-cause sentence names the system gap. Author + reviewer of the implicated PR are metadata (cited for context), not the cause.

## Inventing a hypothesis when no signal correlates

- 4 monitors are firing. No deploy in window. No Slack chatter. No log signal.
- "Maybe a third-party outage?" — possibly, but it's a guess.
- **Fix:** "no leading hypothesis" is a valid output. Surface what was checked, list the suspected upstream dependencies, suggest the next probe (e.g. status pages, infra dashboards). Do not invent a cause to fill the section.

## Letting the symptom-window be wider than necessary

- A 24h window for a "10 minutes ago" symptom buries the signal in noise.
- **Fix:** if `--symptom-time` is set, use `[T-30m, T+30m]`. Wider only when the operator explicitly opts.

## Forgetting to surface the gap

- "DD reachable, deploys reached, Slack workspace MCP unreachable — Slack scrape skipped."
- The operator needs to know the report is missing one source.
- **Fix:** the report's `Sources` table lists every source attempted with status (`pulled` / `skipped` / `failed`). Gaps are visible at a glance.

## Skipping the deploy diff inspection

- Deploy `a3f9c2e` is the leading candidate. The skill recommends rollback. But it never checked if the diff is even relevant.
- **Fix:** before recommending rollback as a high-priority action, fetch the PR title + author + first 50 lines of the diff. If the diff is unrelated, downgrade to "investigate which PR".
