# `setup` — output format

Stdout report (always). Under `--auto`, also `.temp/setup-report.md`.

```
[adk-core:setup] platform=<darwin|linux> target=<all|topic> mode=<auto|fix>

CLI tools:
- brew         present (4.5.2)                                   [or: MISSING — install: ...]
- gh           present (2.62.0) authed=ok                        [or: present, NOT authed — run: gh auth login]
- jq           present (1.7.1)
- fd           present (10.2.0)
- ripgrep      present (14.1.1)
- fzf          present (0.55.0)
- node         present (v22.7.0)
- docker       present (27.3.1)                                  [or: MISSING — install: brew install --cask docker]

meta-info (~/.config/adk/):
- info.md         present, valid
- repos.md        present, 3 repos defined
- github.md       present, valid
- datadog.md      present, valid (3 service aliases)
- mixpanel.md     MISSING — run: /adk-core:setup --target mixpanel
- statsig.md      present, valid
- snowflake.md    present, valid
- slack.md        present, valid
- review.md       present, valid
- docs.md         MISSING — run: /adk-core:setup --target docs

env vars (referenced by .mcp.json):
- GITHUB_PAT                present
- GITHUB_TOOLSETS           present (context,repos,issues,pull_requests,actions,users)
- GITHUB_READ_ONLY          present (1)
- DD_API_KEY                present
- DD_APP_KEY                MISSING — add to ~/.zshenv: export DD_APP_KEY="..."
                             mint at https://app.datadoghq.com/organization-settings/application-keys
- DD_SITE                   present (datadoghq.com)
- STATSIG_CONSOLE_API_KEY   present

mcp servers (resolved from .mcp.json):
- github            ready
- datadog           missing-env (DD_APP_KEY)
- statsig           ready

doctor: 2 warnings, 0 errors
  - mixpanel.md missing — run: /adk-core:setup --target mixpanel
  - DD_APP_KEY missing in ~/.zshenv (datadog MCP disabled)

next steps:
  1. Add the missing exports to ~/.zshenv.
  2. source ~/.zshenv && restart Claude Code (env vars are read at process start).
  3. Re-run /adk-core:setup --auto to verify.
```

## Status legend

- `present` — found and validated.
- `MISSING` — not found; remediation printed.
- `present, NOT authed` — installed but unauthenticated (e.g. `gh`).
- `valid` / `invalid` — meta-info file passes / fails `adk-info <topic> --check`.
- `missing-env` — MCP server config exists but a referenced env var isn't set.
- `ready` — MCP server should resolve cleanly given current env.

## Doctor counts

- `errors` — anything that BLOCKS adk usage (e.g. `gh` missing).
- `warnings` — anything DEGRADED (e.g. one MCP disabled because of a missing env var).

## Why the verbose format

Setup is run rarely; verbosity is appropriate. Other skills produce shorter reports.
