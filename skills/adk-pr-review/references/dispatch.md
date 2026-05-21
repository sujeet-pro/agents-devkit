# dispatch — URL → review target

Accepted inputs:

| URL shape | Host | Identifier | Fetcher |
|---|---|---|---|
| `https://github.com/<owner>/<repo>/pull/<n>` | GitHub | `owner/repo#n` | `gh` CLI or `adk-mcp-github` |
| `https://bitbucket.org/<workspace>/<repo>/pull-requests/<n>` | Bitbucket Cloud | `workspace/repo!n` | `adk-mcp-bitbucket` (REST) |

Anything else is **out of scope** (constitution §VI.1) — refuse with the host name and the supported list. Bitbucket Server (`bitbucket.<company>.com`) and GitLab fail this check.

## Parse rules (implemented by `scripts/parse_pr_url.py`)

```text
github.com/<owner>/<repo>/pull/<n>          → host=github,  owner=<owner>,    repo=<repo>, pr=<n>
bitbucket.org/<ws>/<repo>/pull-requests/<n> → host=bitbucket, owner=<ws>,     repo=<repo>, pr=<n>
```

Trailing slashes, fragments (`#diff`), and query strings are stripped. Case-insensitive on the host part; case-preserving on owner/repo.

## Task-folder naming

The slug under `~/.agents-devkit/skill-pr-review/` is `<repo>_pr-<n>`. If two PRs across hosts share the same `<repo>_pr-<n>` name, the second invocation gets `<repo>_pr-<n>-2`. The host is recorded in `pr.json.host` so downstream scripts pick the right fetcher.

## Repo-name aliasing

`config/repos.md` frontmatter `repos[*]` may define `path`, `host`, `workspace`, `name`. When the PR URL's `<owner>/<repo>` matches a `repos[i]` entry, the orchestrator reuses that entry's `path` if it's already on disk as a clone of the same remote; otherwise it clones into `~/.agents-devkit/repos/<repo-name>/` regardless of where the user's working copy lives. The user's working copy is never touched.

## Out-of-scope refusal template

```
adk-pr-review only supports GitHub and Bitbucket Cloud PRs. Got: <url>.
Reason: <host> is not <github.com | bitbucket.org>.
Constitution §VI.1.
```
