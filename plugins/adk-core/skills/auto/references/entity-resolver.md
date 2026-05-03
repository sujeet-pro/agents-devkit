# `auto` — entity resolver

How to resolve user shorthand against `~/.config/adk/*.md` files.

## Resolution order

For each entity in the prompt, walk this order until a match is found. Mark each match as `verified` (matched a meta-info file) or `inferred` (heuristic match).

### 1. Repo

1. If the prompt names a repo path (`acme/checkout-api`) → look up in `repos.md`.
2. If the prompt is run from inside a checkout, walk up to `.git`, then match `git remote get-url` against `repos.md.repos[].name`.
3. If the prompt names a service shorthand (`checkout`), look up `repos.md.repos[].datadog_service` for a matching service tag and back-resolve the repo.
4. If still unresolved, ask the user.

### 2. Service (Datadog)

1. Look up `datadog.md.service_aliases` for the user's shorthand → canonical service tag.
2. Look up the resolved repo's `datadog_service` field in `repos.md`.
3. Otherwise, treat the shorthand as the literal tag and mark `inferred`.

### 3. Time window

1. Explicit `--time` flag wins.
2. Otherwise, parse natural language: "last 1h", "yesterday", "since 13:00", "between 12:00 and 14:00".
3. Otherwise, default to `datadog.md.default_window` (or `last 1h` if unset) — for DD queries.
4. Otherwise, default to `mixpanel.md.default_window` (or `last 7d`) — for Mixpanel.

### 4. Environment

1. Explicit `--env` flag wins.
2. Otherwise, default to `datadog.md.default_env` (typically `prod`).

### 5. PR

1. URL parses to `(host, owner, repo, number)`.
2. Match `host` to provider (github.com / GHE → `github`; bitbucket.org → `bitbucket`).
3. Look up the repo in `repos.md` for the local checkout path.

### 6. Experiment / gate (Statsig)

1. Look up `statsig.md.common_experiments[].name` or `statsig.md.common_gates[].name`.
2. Otherwise, treat as a literal name and mark `inferred`.

### 7. Mixpanel event / funnel

1. Look up `mixpanel.md.common_events` for direct event name.
2. Look up `mixpanel.md.common_funnels[].id` for funnel id.

### 8. Confluence space / GDrive folder

1. Look up `docs.md.default_confluence_space` / `docs.md.default_gdrive_folder_id`.
2. Otherwise, ask the user.

## Output shape (in skill-plan.md)

```markdown
## Resolved entities
| Kind | Surface | Resolved | Source |
| --- | --- | --- | --- |
| repo | "checkout" | acme/checkout-api | repos.md (verified) |
| service | "checkout" | checkout-api | datadog.md.service_aliases (verified) |
| time | "yesterday" | 2026-05-02T00:00..23:59 | NL parse (inferred) |
| env | (omitted) | prod | datadog.md.default_env (verified) |
```

## Failure modes

- **Ambiguous shorthand**: "the api" matches 3 services. Ask the user to disambiguate.
- **Stale meta-info**: `repos.md.path` points at a path that doesn't exist. Surface in preflight; suggest `setup --target repos`.
- **Cross-source disagreement**: a repo's `datadog_service` doesn't match `datadog.md.service_aliases`. Prefer the repo-local value (more specific); flag the inconsistency in the report.

