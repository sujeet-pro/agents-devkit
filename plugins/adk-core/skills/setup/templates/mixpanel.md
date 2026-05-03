---
# ~/.config/adk/mixpanel.md
# Mixpanel conventions. Used by adk-investigate:investigate-mixpanel
# and investigate-experiment.

project_id: 12345
project_token_env: MIXPANEL_PROJECT_TOKEN
default_window: last 7d
identity_property: user_id
common_events:
  - signup_completed
  - first_export
  - checkout_started
  - checkout_completed
  - add_to_cart
common_funnels:
  - id: signup_to_first_export
    steps:
      - signup_completed
      - first_export
  - id: cart_to_checkout
    steps:
      - add_to_cart
      - checkout_started
      - checkout_completed
common_cohorts:
  - id: power_users
    definition: "user did checkout_completed >= 5 times in last 30d"
  - id: new_signups
    definition: "user did signup_completed in last 7d"
---

# Notes

- Read access goes through the claude.ai workspace Mixpanel connector.
- This file holds project metadata so the skill knows which IDs / events to use.
- Mixpanel is for product analytics; use Datadog for system / infra metrics.
