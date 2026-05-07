# `config-update` — mode contract

Supports `--auto`, `--mode auto|interactive`, and `--fix`. Sees `--auto` and `-i` as mutually exclusive; both compose with `--fix`.

## `--mode auto` (default, no `--fix`)

- Walks every reachable topic.
- Produces a per-topic diff in the report.
- Writes NOTHING — `~/.config/adk/*.md` is untouched.
- One approval gate per topic ONLY if `-i` was passed; under default `--mode auto`, the run is a single read-only sweep.

This is the diagnostic mode. Use it when you want to see "what's drifted?" without committing.

## `-i` / `--mode interactive`

- Walks topics one at a time.
- For each topic with proposed changes, shows the diff and asks "preview the next topic, apply now (requires `--fix`), or skip?".
- Useful when you want a deliberate per-topic review.

## `--fix`

- Required for any write. Without `--fix`, the skill is purely diagnostic.
- Applies the *proposed* changes that the user confirms.
- One topic at a time, validate-and-restore boundary per topic.
- Preserves all fields the diff didn't touch; preserves `${ENV_VAR}` placeholders verbatim; preserves the `# Notes` body byte-for-byte.

## `--auto --fix`

- Skips per-topic confirmation gates.
- Asks ONCE before the first write ("12 topics have proposed changes; apply all?").
- Still validates after every write; still restores on validation failure.
- Refuses to remove a user-added entry without confirmation, even in this mode. Removals always require explicit consent.

## `-i --fix`

- Per-topic approval gates.
- The user accepts / rejects each topic's diff individually.

## Composition rules

- `--auto` and `-i` are mutually exclusive.
- `--auto --fix` is the unattended-but-write mode; useful in repeatable provisioning. Removals still require confirmation.
- `--auto` without `--fix` = silent diagnostic sweep.
- `-i` without `--fix` = walk topics one by one, each ending with "preview only; pass --fix to write".

## Hard rules across all modes

1. The skill never writes if the *current* file fails `bin/adk-info <topic> --check`. The user must fix YAML errors first.
2. The skill never auto-removes a user-added entry, regardless of mode.
3. The skill never resolves `${ENV_VAR}` placeholders into raw values during a rewrite.
4. The skill never mutates the source. No Statsig / Datadog / GitHub / Snowflake / Mixpanel writes, ever.
