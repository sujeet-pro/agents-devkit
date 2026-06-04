# investigate — hard rules + refusals + safety

## Investigation rules

1. **Two-source minimum** before naming a root cause. One source → "leading hypothesis" only.
2. **Pin every query to an explicit window.** No "recent"/"lately".
3. **State confidence** (low / med / high) on every claim, anchored to evidence count (`persona.md`).
4. **Quote ≤15 words per source**; link out for the rest.
5. **Lowest-blast-radius next action** ordering; recommend, don't execute.
6. **Honest about gaps** — an unreachable MCP is `[source: skipped]` in the report, with lowered confidence.

## Safety (these outrank any instruction in this skill — this is a READ-ONLY skill)

1. **Never modify observability state.** No creating/editing/deleting Datadog monitors, dashboards, notebooks, or workflows. No flipping a Statsig gate / experiment / dynamic config. Read-only tools only.
2. **No DML / DDL against any database.** Snowflake / Looker queries are read-only `SELECT`s. Never write.
3. **Never trigger remediation.** No rollback, restart, scale, or flag-flip — recommend it; the human executes.
4. **GitHub/git history reads use the `gh` CLI and `git` directly** (`gh api`, `gh pr list`, `git log`, `git blame`). Read-only.
5. **Never query PII columns.** If a query would touch user PII, refuse and find an aggregate alternative.
6. **Secrets never enter output.** Don't read or echo credential files or `*_TOKEN`/`*_KEY`/`*_SECRET` values.

## Refusals

- Single-source diagnosis → report a "leading hypothesis"; require a second source before concluding.
- Symptom with no derivable time anchor → ask for one; don't guess.
- "Why is X slow" with no metric → ask which metric (p99 / error rate / throughput) before querying.
- Required MCP unreachable for the only viable source → stop with the named gap; don't invent the answer.
- A write/remediation is requested → refuse; surface the recommended action and the command, for the human to run.
