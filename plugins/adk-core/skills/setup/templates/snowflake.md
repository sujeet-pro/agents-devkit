---
# ~/.config/adk/snowflake.md
# Snowflake conventions. Used by adk-investigate:investigate-snowflake.

account: wya41754              # short identifier from your Snowflake URL
default_warehouse: COMPUTE_WH
default_role: ANALYST_RO
default_database: DW_PROD_STRUCTURED
default_schema_search_path:
  - OMS
  - COMMERCE
  - CATALOG
pii_columns:
  block_substring:
    - email
    - phone
    - address
    - ssn
    - name_full
    - dob
  block_token_columns:
    - DET_*
    - RAND_*
common_views:
  - name: orders_daily
    db: DW_PROD_STRUCTURED
    schema: OMS
  - name: skus_active
    db: DW_PROD_STRUCTURED
    schema: CATALOG
  - name: shipments_recent
    db: DW_PROD_STRUCTURED
    schema: OMS
---

# Notes

- Queries go through the claude.ai workspace Snowflake MCP connector (e.g. QDP_SNOWFLAKE_MCP_SERVER).
- This file is about WHAT to query and WHAT to refuse, not HOW to authenticate.
- The PII guardrail rules are enforced by the skill: any column matching `block_substring` or `block_token_columns` patterns is refused.
- The skill is read-only — no DML, no DDL, no GRANT.
