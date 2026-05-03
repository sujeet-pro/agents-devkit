---
# ~/.config/adk/statsig.md
# Statsig conventions. Used by adk-investigate:investigate-statsig
# and investigate-experiment.

project: acme-prod
console_api_key_env: STATSIG_CONSOLE_API_KEY
server_secret_env: STATSIG_SERVER_SECRET
default_environment: production    # production | staging | development
common_gates:
  - name: checkout_redesign
    owner: alice
    repo: acme/storefront
  - name: search_v2
    owner: bob
    repo: acme/search-api
common_experiments:
  - name: checkout_funnel_v3
    repo: acme/storefront
    primary_metric: checkout_completed
    secondary_metrics:
      - revenue_per_session
      - time_to_checkout
  - name: pdp_image_carousel
    repo: acme/storefront
    primary_metric: add_to_cart
exposure_metric_conventions:
  guardrail_metrics:
    - error_rate
    - p99_latency_ms
---

# Notes

- The Console API key (`$STATSIG_CONSOLE_API_KEY`) needs scope `omni_read_only` for adk's read-only skills.
- For toggling gates / starting experiments (out of scope for adk v0.1), you'd need `omni_write` — keep that key separate.
- Experiment "pulse" = primary metric delta + secondary metric deltas + guardrail movements + sample size + p-value.
