# `investigate-deploy` — anti-patterns

## Naming a deploy as the cause without correlation

- "Deploy at 12:58. Symptom at 13:02. Deploy caused it." Maybe. Maybe not.
- The cause requires a second signal: a log line from the new code path, a metric movement timed to the deploy, a trace showing the new span is slow.
- **Fix:** this skill marks deploys as "near-symptom candidates"; it does not name causes. The cause verdict belongs to `/adk-investigate:investigate-incident`.

## Pulling without a window

- `gh run list --limit 50` returns the last 50 runs, which may span weeks. During incident triage, "old" deploys are noise.
- **Fix:** always apply a window. Default `last 2h`.

## Forgetting the workflow URL

- The operator wants to drill into the workflow run logs. Without the URL, they have to navigate from `gh` output → GitHub UI → repo → Actions → find the run.
- **Fix:** every row has a `URL` column with the direct link.

## Wrong workflow name

- Repos use `deploy.yml`, `release.yml`, `cd.yml`, `prod-deploy.yml`. The default `deploy` fallback may return zero rows.
- **Fix:** read `repos.md.repos[<repo>].deploy_workflow` first. If zero rows from fallback `deploy`, warn and suggest `gh workflow list --repo <repo>` to discover.

## Pasting raw `gh` JSON

- 50 lines of JSON is unreadable.
- **Fix:** render as a markdown table with the seven columns: `Time | Status | Duration | SHA | Author | Title | URL`.

## Ignoring failed deploys

- A failed deploy at 12:55 may be the actual story (a deploy that never went out → backend changes that *did* go out a different way → silent inconsistency).
- **Fix:** dedicated `Failed deploys` section in the report. Not buried in the timeline.

## Triggering / cancelling / retrying

- This skill is read-only.
- **Fix:** any operation requiring `gh run rerun`, `gh run cancel`, or any deploy-system mutation is rejected. Out of scope.

## Cross-pod misattribution

- Service `checkout` is split across `acme/checkout-api` and `acme/checkout-web`. A symptom in `checkout-api` might be caused by a deploy to `checkout-web`.
- **Fix:** when correlating with a service, list deploys for ALL repos that map to the service (per `repos.md.repos[].datadog_service`). Not just the first match.

## Forgetting timezone

- `gh` returns timestamps in ISO with timezone. The report should display in UTC by default to match Datadog and Slack timestamps; never strip the timezone marker.
- **Fix:** always include `UTC` (or the operator's chosen timezone) in the column header.

## Cross-referencing without DD

- The skill is `gh`-only by design. The DD cross-reference is opt-in (only if `datadog` MCP reachable).
- **Fix:** if DD isn't reachable, skip the cross-source section silently; don't error. The `gh` timeline alone is the deliverable.
