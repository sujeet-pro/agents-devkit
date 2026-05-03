# `investigate-snowflake` — PII guardrail

Hard rule: this skill refuses to query columns matching the PII block list in `~/.config/adk/snowflake.md.pii_columns`.

## Block lists

### `block_substring` (case-insensitive substring match)

Default value:

```yaml
block_substring: ["email", "phone", "address", "ssn", "name_full"]
```

Matching rule: if any column name *contains* any substring (case-insensitive), the column is blocked.

| Column name | Match against `["email", "phone", "address", "ssn", "name_full"]` | Result |
| --- | --- | --- |
| `email` | matches `email` | BLOCKED |
| `EMAIL_HASH` | matches `email` | BLOCKED |
| `customer_email_md5` | matches `email` | BLOCKED |
| `phone_number` | matches `phone` | BLOCKED |
| `address_line_1` | matches `address` | BLOCKED |
| `ip_address` | matches `address` | BLOCKED |
| `name_full` | matches `name_full` | BLOCKED |
| `first_name` | no match (`name_full` is the substring; `name` alone isn't) | ALLOWED |
| `user_id` | no match | ALLOWED |

> **Note on `first_name`:** the default block list deliberately uses `name_full` (not `name`) to keep first-name and last-name fields available for non-PII contexts. If the operator wants to block all name fields, they update `pii_columns.block_substring` to include `"name"`.

### `block_token_columns` (regex / glob match)

Default value:

```yaml
block_token_columns: ["DET_*", "RAND_*"]
```

Matching rule: glob pattern against the column name. Used to block columns named with deterministic / random encoding prefixes that conventionally hold PII.

| Column name | Match | Result |
| --- | --- | --- |
| `DET_USER_EMAIL` | `DET_*` | BLOCKED |
| `RAND_PHONE_HASH` | `RAND_*` | BLOCKED |
| `USER_DET_EMAIL` | no leading `DET_` | ALLOWED (but caught by `block_substring` if `email` is in the substring list) |

## How the precheck runs

The skill runs the precheck **twice**:

1. **Phase 0 — question precheck.** Tokenize the user's question; check tokens against the block lists. (Catches obvious cases: "list emails of users".)
2. **Phase 2 — SQL precheck.** Parse the built SQL `SELECT` clause; check each named column. (Catches cases the question precheck missed: e.g. the user asked for "user data" and the candidate view has an `email` column.)

If either precheck matches, the skill REFUSES.

## Refusal output

Per `output-format.md`'s refusal shape. The skill names the matched column and suggests alternatives:

1. Re-phrase the question without PII.
2. If genuinely needed, escalate to a service account with proper access controls (security team / DE engineer).

## How to extend the block list

The operator edits `~/.config/adk/snowflake.md`:

```yaml
pii_columns:
  block_substring: ["email", "phone", "address", "ssn", "name_full", "credit_card", "tax_id"]
  block_token_columns: ["DET_*", "RAND_*", "PII_*", "GDPR_*"]
```

After editing, run `bin/adk-info --check snowflake` to validate.

## How to bypass

You cannot bypass in-conversation. The block list is enforced by the skill. To allow a previously blocked column:

- The operator edits `snowflake.md` to remove the relevant entry from `block_substring` / `block_token_columns`.
- This is a deliberate friction point — PII access should require an explicit, durable change to the per-user policy file, not a one-off prompt override.

## Why the rule is conservative

- Snowflake reads happen with a real user identity attached. Logs persist; queries are audited. PII access creates compliance liability.
- The cost of a false-positive (refusing a legitimate query) is a minor inconvenience.
- The cost of a false-negative (executing a PII query that shouldn't have run) is much higher: data exposure, audit issues, possible regulatory consequences.
- Skills should NEVER trade-off conservatism on PII for convenience.
