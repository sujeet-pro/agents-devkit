# `info` workflow

## Step 1 — parse invocation

| User invocation | Shell-out |
| --- | --- |
| `/adk-core:info` | `adk-info` (dump all topics as JSON) |
| `/adk-core:info <topic>` | `adk-info <topic>` |
| `/adk-core:info <topic> <key>` | `adk-info <topic> <key>` (dotted path supported) |
| `/adk-core:info --check` | `adk-info --check` (validate schemas) |
| `/adk-core:info --missing` | `adk-info --missing` (recommended-but-unset fields) |
| `/adk-core:info --resolve-env` | `adk-info --resolve-env` (substitute env vars) |

## Step 2 — execute

Run the shell-out. Capture stdout + exit code.

## Step 3 — surface

- If the script exits 0 and the user invoked interactively, render a summary table.
- If the script exits non-zero, surface the validation errors verbatim.
- If `--resolve-env` was used and any field is `<unset>`, list those fields explicitly.

## Step 4 — log (only on `--check`)

- Write `.temp/notes/adk-info-check.md` with the validation result + timestamp (audit trail).

## Edge cases

- **Topic file missing** — surface "topic '<topic>' not found in ~/.config/adk/" with suggestion to run `/adk-core:setup --target <topic>`.
- **Key not found** — surface "key '<key>' not found in <topic>.md" with the closest sibling keys (Levenshtein <=2).
- **Malformed YAML** — surface the parse error verbatim with line:col.
- **`${ENV_VAR}` unresolved (under `--resolve-env`)** — print `<unset>` placeholder, NEVER the literal env-var name as if it were a value.
