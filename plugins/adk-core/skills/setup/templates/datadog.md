---
# ~/.config/adk/datadog.md
# Datadog conventions. Used by adk-investigate:investigate-datadog,
# investigate-incident, investigate-rca, code-perf.

site: datadoghq.com              # datadoghq.com | datadoghq.eu | us3.datadoghq.com | us5.datadoghq.com | ap1.datadoghq.com
default_env: prod
default_window: last 1h
auth:
  # Canonical: DATADOG_API_KEY / DATADOG_APP_KEY. Legacy DD_API_KEY / DD_APP_KEY
  # are also accepted — adk-mcp-health treats either as "present". To use the
  # legacy names with the canonical .mcp.json wiring, alias them in your shell rc:
  #   export DATADOG_API_KEY="$DD_API_KEY"
  #   export DATADOG_APP_KEY="$DD_APP_KEY"
  api_key_env: DATADOG_API_KEY
  app_key_env: DATADOG_APP_KEY
service_aliases:
  # short-name -> canonical service tag in DD
  checkout: checkout-api
  storefront: storefront-web
  search: search-api
common_dashboards:
  - id: abc-123-xyz
    name: Production Overview
    url: https://app.datadoghq.com/dashboard/abc-123-xyz
  - id: def-456-uvw
    name: Checkout SLO
    url: https://app.datadoghq.com/dashboard/def-456-uvw
common_queries:
  - name: error rate by service
    type: metrics
    query: "sum:trace.servlet.request.errors{env:prod} by {service}.as_count()"
  - name: latest deploy events
    type: events
    query: "sources:my_apps tags:deploy"
slo_thresholds:
  checkout_p99_ms: 500
  storefront_p99_ms: 800
---

# Notes

- The Production Overview dashboard is the on-call default page during incidents.
- The deploys event stream is sourced from the GitHub Actions notify-datadog job.
- For non-US1 sites, also override DD_MCP_URL in your shell env (see SETUP.md).
