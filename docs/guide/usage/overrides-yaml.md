---
title: overrides.yaml
description: The single config file you maintain. Workspaces, repos, data dictionary (Snowflake / Looker / Mixpanel), defaults, RAG config — read by every skill at every run.
order: 4
---

# `$ADK_CONFIG_HOME/overrides.yaml`

This is the only file you hand-edit. Skills read it on every run, merge any `<repo>/.adk/overrides.yaml` on top, and use the result to resolve entities and defaults.

## Schema (overview)

```yaml
workspaces: [...]            # work + personal + side orgs
repos: [...]                 # repos you actively work in
data_sources: { ... }        # Snowflake / Looker / Mixpanel — manual hints + auto-augmented
rag: { ... }                 # optional company RAG MCP
defaults: { ... }            # tuned over time by /adk-improve

# auto-managed (don't hand-edit)
enriched: { ... }            # written by /adk-setup --enrich
learning_state: { ... }      # written by /adk-improve
```

## workspaces

Each workspace = one identity context (work email + github user + org list).

```yaml
workspaces:
  - name: personal
    type: personal
    email: sujeet@gmail.com
    github_user: sujeet-pro
    orgs: [sujeet-pro]
  - name: personal-work
    type: work
    default: true                # used when no other workspace matches
    email: you@example.com
    github_user: sujeet-pro       # or a different work GH identity
    orgs: [acme, acme-internal]
  # add as many work / side / personal workspaces as you need
```

`default: true` workspace is used when the active repo or cwd doesn't match any other workspace's repo paths.

## repos

The "table" — one entry per repo you actively work in. The keys here are what every skill resolves against when you mention a service / repo / Jira project.

```yaml
repos:
  - name: storefront-bff
    workspace: personal-work
    path: ~/code/acme/storefront-bff
    github: acme/storefront-bff
    base_branch: main
    primary_language: typescript
    description: "BFF for storefront — SSR + edge logic"
    jira_project_key: SF
    datadog: { apm_service: storefront-bff, rum_app: storefront }
    mixpanel: { project_id: 12345 }
    statsig: { project: storefront }
    slack:
      alert_channel: "#datadog-alerts-bff"
      deploy_channel: "#deploys-storefront"
```

`/adk-investigate "checkout broken"` resolves "checkout" → `repos[].datadog.apm_service` for the active workspace.

## data_sources

The data dictionary. Manual hints for Snowflake / Looker / Mixpanel that AI can use to answer "which table has order data?" without re-introspecting on every run.

```yaml
data_sources:
  snowflake:
    workspace: personal-work
    warehouse: PROD_WH
    role: ANALYST
    databases:
      - name: PROD_DB
        description: "main prod warehouse"
        schemas:
          - name: ANALYTICS
            tables:
              - name: USER_EVENTS
                description: "event stream"
                pii_columns: [EMAIL, IP_ADDRESS]    # skills refuse to query these
                columns:
                  - { name: USER_ID, description: "unique user id", purpose: "join key" }
                  - { name: EVENT_NAME, description: "event name", purpose: "filter" }
                  - { name: TS, description: "event ts", purpose: "time filter" }
  looker:
    instance: acme.cloud.looker.com
    dashboards:
      - { id: 42, name: "Storefront SLOs", description: "error budget" }
    explores:
      - { model: ecommerce, name: orders, description: "primary orders explore" }
  mixpanel:
    project_id: 12345
    common_events:
      - { name: signup_completed, description: "finished signup flow" }
      - { name: checkout_started, description: "clicked Begin Checkout" }
```

`/adk-setup --enrich` augments this from MCP introspection — but never overwrites your manual entries.

`pii_columns` lists are enforced — `/adk-investigate` refuses to query them per the constitution.

## rag (optional)

```yaml
rag:
  enabled: true
  mcp_name: adk-mcp-rag
  trigger_keywords: [policy, hr, internal-docs, onboarding]
```

When `enabled: true`, every skill's Phase 0 (context-gather) queries the RAG MCP if the prompt contains any `trigger_keywords` OR the user explicitly says "check our internal docs". Results tagged `[source: rag]` in `context.md`.

## defaults

Tuned over time by `/adk-improve`. Each skill emits decision-log entries naming its `fork_id`s; the proposals refine these.

```yaml
defaults:
  default_reviewer: "@team-lead"
  severity_bar: critical-and-above
  test_framework: jest
  commit_style: conventional
  # per-skill defaults (auto-managed by /adk-improve after enough evidence)
  adk-implement:
    scope: vertical-slice                  # was overridden 5+ times to "full" — proposed default change
    pr-strategy: single
  adk-review:
    severity-bar: critical+should
    nit-tolerance: cap-3
```

## enriched + learning_state (auto-managed)

```yaml
enriched:
  datadog:
    common_dashboards:
      - { id: abc-123, name: "Storefront SLOs" }
    monitors_count: 42
  statsig:
    active_experiments_count: 8
  # ...

learning_state:
  last_improve_run: "2026-05-18T14:22Z"
  last_metadata_refresh: "2026-05-18T14:30Z"
  pending_proposals: []                    # filled by /adk-improve before user reviews
```

Hand-edit only if you know what you're doing. `/adk-setup --enrich` and `/adk-improve` write here.

## Privacy

- **Never put a token in `overrides.yaml`.** Use `${ENV_VAR}` placeholders. The PostToolUse:Edit hook scans every write and refuses if it detects a raw token-looking value.
- Decision logs, metadata cache, and overrides are local-only. No skill uploads them.

## Next

- [Project-scoped overrides](./project-scoped.md) — `<repo>/.adk/` extends this per repo.
- [Decision logs](../concepts/decision-logs.md) — how `/adk-improve` proposes default updates.
