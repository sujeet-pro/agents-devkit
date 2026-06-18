# creds toolkit

Self-contained, stdlib-only Python (no `pip install`) for validating and
rotating the credentials behind the MCP servers in
[`plugins/adk/.mcp.json`](../../plugins/adk/.mcp.json).

**Source of truth:** `~/.zshenv` (override with `$ZSHENV_FILE`). The same
variable names are documented with placeholders in
[`.env.example`](../../.env.example). Rotation edits `~/.zshenv` lines in place.

## Usage

```bash
scripts/creds/validate.py            # probe every service against its live API
scripts/creds/validate.py slack jira # probe selected services (names or aliases)
scripts/creds/rotate.py slack        # rotate Slack app-config tokens → ~/.zshenv
scripts/creds/login.py               # list services that need an interactive login
scripts/creds/login.py google        # show login steps + open the console
scripts/creds/creds.py status        # what each service supports (unified entrypoint)
```

`validate.py` exit codes: `1` any FAIL, `2` any MISCONFIGURED, else `0`.

## Result states

| state           | meaning                                                        |
|-----------------|---------------------------------------------------------------|
| `OK`            | probed the live API, the credential works                     |
| `FAIL`          | credential present but rejected, or the endpoint errored      |
| `MISCONFIGURED` | required vars unset or still placeholders (`ADD_VALUE`, …)     |
| `LOGIN`         | needs an interactive login the script can't do — see `login.py` |

## How each service is checked

| service   | check                                          | rotate? | login?                         |
|-----------|------------------------------------------------|---------|--------------------------------|
| datadog   | `GET /api/v1/validate` + `/api/v1/dashboard`   | —       | key-based                      |
| atlassian | Jira `GET /rest/api/3/myself` (+ Confluence)   | —       | key-based                      |
| slack     | `auth.test` for bot + user tokens              | yes     | OAuth to mint bot/user tokens  |
| statsig   | `GET /console/v1/gates`                        | —       | key-based                      |
| mixpanel  | hosted MCP reachability                        | —       | OAuth via MCP client           |
| snowflake | SQL API `SELECT 1` (account from connections.toml) | —   | re-mint short-lived token      |
| looker    | API3 `/login` then `/user`                     | —       | key-based                      |
| google    | OAuth client configured + cached grant present | —       | browser OAuth on first MCP use |

## Adding a service

Drop a module in `connectors/` exposing `NAME` and `validate() -> Result`.
Optional: `rotate() -> Result`, `LOGIN_HINT: str`, `MINT_URL: str`. Add the
name to `connectors/__init__.py:NAMES`. Shared helpers live in `creds_lib/`
(`http`, `status`, `zshenv_io`, `env`).
```
