# `context-gather` — MCP fallback

| Source | Preferred MCP | Fallback | Skip if |
| --- | --- | --- | --- |
| Jira | `jira` | none (manual paste from user) | env vars missing |
| Confluence | `confluence` | none | env vars missing |
| Google Doc | `google-drive` | `WebFetch` if doc is publicly shared | private + no MCP |
| Slack | `slack` | none (cannot fetch private channels otherwise) | env vars missing |
| Gmail | `gmail` | none | env vars missing |
| GitHub | `gh` CLI (always preferred) | `github` MCP if installed | `gh auth status` not authed |

When a source is skipped, write a section in `context.md` with the URL, the type, status `skipped`, and the reason — never silently drop.
