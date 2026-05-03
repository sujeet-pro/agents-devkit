# `investigate-deploy` — `gh run list` recipes

Common invocations. The skill always uses the `--json` form for stable parsing.

## Default recipe

```bash
gh run list \
  --repo <owner>/<repo> \
  --workflow=<workflow-file-or-name> \
  --limit 50 \
  --json status,conclusion,createdAt,event,headBranch,headSha,actor,url,name,displayTitle
```

Returns a JSON array of objects. Each object:

```json
{
  "status": "completed",
  "conclusion": "success",
  "createdAt": "2026-05-03T13:01:42Z",
  "event": "push",
  "headBranch": "main",
  "headSha": "a3f9c2eabcd...",
  "actor": { "login": "alice" },
  "url": "https://github.com/acme/checkout-api/actions/runs/123456789",
  "name": "deploy",
  "displayTitle": "deploy v3 checkout funnel"
}
```

## Filter by status

`--status` filters at the API level:

```bash
gh run list --repo <r> --workflow=<w> --status failure --limit 20 \
  --json status,conclusion,createdAt,headSha,actor,url
```

Statuses: `queued`, `in_progress`, `completed`. (`completed` covers all `conclusion` values.)

## Filter by branch

```bash
gh run list --repo <r> --workflow=<w> --branch main --limit 50 \
  --json status,conclusion,createdAt,headSha,actor,url
```

For prod-deploy timelines, filtering to `main` keeps non-prod branches out.

## Filter by event

```bash
gh run list --repo <r> --workflow=<w> --event push --limit 50 \
  --json status,conclusion,createdAt,headSha,actor,url
```

Useful for excluding `workflow_dispatch` (manual) runs from a CI-driven view.

## Window filter (post-process)

`gh run list` lacks a window flag. Filter the JSON in post-processing:

```bash
gh run list ... --json ... | jq '[.[] | select(.createdAt >= "2026-05-03T11:00:00Z")]'
```

The skill does this in code, not `jq`, but the shape is the same.

## Per-run detail (drilling in)

If a specific run needs more detail (jobs, steps, logs):

```bash
gh run view <run-id> --repo <r> --json status,conclusion,jobs,createdAt,updatedAt
gh run view <run-id> --repo <r> --log              # full logs (verbose)
gh run view <run-id> --repo <r> --log-failed       # only failed-step logs
```

This skill calls `view --log-failed` only when the operator asks (under `-i`) — it does NOT auto-pull logs.

## Discovering the workflow name

If the default `deploy` returns zero runs:

```bash
gh workflow list --repo <r>
```

Returns a list of workflows. Look for likely deploy candidates: `deploy.yml`, `release.yml`, `cd.yml`, `prod-deploy.yml`. Update `~/.config/adk/repos.md.repos[<repo>].deploy_workflow` for next session.

## Rate limits

- `gh` authenticated user: 5,000 req/h.
- Each `gh run list --limit 50` is one request.
- The skill caps at 200 runs per session per repo to leave headroom.

## Cross-pod multi-repo

When the operator asks about a service that maps to multiple repos:

```bash
for repo in acme/checkout-api acme/checkout-web acme/order-service; do
  gh run list --repo "$repo" --workflow=deploy.yml --limit 20 \
    --json createdAt,conclusion,headSha,actor,url
done
```

The skill iterates per repo; the report aggregates with one section per repo and a top-level summary.

## Error handling

| Symptom | Cause | Fix |
| --- | --- | --- |
| `gh: command not found` | `gh` not installed | Stop with install instructions |
| `error connecting to github.com` | Network / auth issue | `gh auth status`; re-auth if needed |
| `0 runs` returned | Wrong `--workflow` name OR window too narrow | Suggest `gh workflow list`; widen window |
| `403 rate limited` | API quota exhausted | Surface and stop; suggest waiting / using a different token |
