# `info` — output format

## Default: JSON to stdout

```json
{
  "info": {
    "name": "Sujeet Jaiswal",
    "email": "sujeet@example.com",
    "role": "Principal Engineer",
    "default_editor": "cursor"
  },
  "repos": {
    "repos": [
      {
        "name": "acme/checkout-api",
        "path": "~/code/acme/checkout-api",
        "primary_language": "kotlin",
        "base_branch": "main",
        "datadog_service": "checkout-api"
      }
    ],
    "defaults": {
      "base_branch": "main"
    }
  },
  "datadog": { ... },
  ...
}
```

## Single topic

```bash
/adk-core:info datadog
```

→

```json
{
  "site": "datadoghq.com",
  "default_env": "prod",
  "service_aliases": {
    "checkout": "checkout-api",
    "storefront": "storefront-web"
  },
  ...
}
```

## Single key (dotted path)

```bash
/adk-core:info datadog service_aliases.checkout
```

→

```json
"checkout-api"
```

## --check

```json
{ "ok": true }
```

or (on failure, exit 1):

```
ERROR: datadog.md: required field 'site' missing or empty
ERROR: github.md: looks like a raw secret at github.auth.token; use ${ENV_VAR} placeholder instead
```

## --missing

```json
[
  { "topic": "mixpanel", "status": "missing-file" },
  { "topic": "docs", "status": "missing-fields", "fields": ["default_confluence_space"] }
]
```

## --resolve-env

Same shape as default, but `${VAR}` placeholders are substituted. Missing env vars become the literal string `<unset>`.

```json
{
  "github": {
    "auth": { "token_env": "<unset>" }
  }
}
```

(NB: this still doesn't print the actual token value; the `<unset>` is a sentinel, not a leak.)

## Interactive markdown summary

When invoked interactively without specific args, render:

```markdown
# adk knows about you (~/.config/adk/)

## Operator
- name: Sujeet Jaiswal
- email: sujeet@example.com
- role: Principal Engineer

## Repos (3)
- acme/checkout-api (~/code/acme/checkout-api, kotlin, main)
- acme/storefront (~/code/acme/storefront, typescript, main)
- acme/search-api (~/code/acme/search-api, kotlin, main)

## Datadog
- site: datadoghq.com
- default env: prod
- 3 service aliases configured
- 5 common dashboards

## Statsig
- project: acme-prod
- 4 common gates, 6 common experiments
```
