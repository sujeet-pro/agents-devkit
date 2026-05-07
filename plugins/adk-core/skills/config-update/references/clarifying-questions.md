# `config-update` — clarifying questions

Asked one at a time, only when the answer changes the plan. The interaction contract forbids stacking unrelated confirmations in a single turn.

## Initial gate (before phase 0)

1. **Target: all topics or just `<topic>`?**
   - Default: `all`.
   - Asked only if the user invocation didn't specify `--target`.

2. **`--since <duration>` window?**
   - Default: per-topic defaults from `references/source-discovery.md` (e.g. 90d for statsig, 30d for mixpanel, none for repos).
   - Asked only if a topic's discovery returns > 200 candidates and the user is in interactive mode (the prompt is a way to narrow).

## Per-topic gate (under `-i`)

For every topic with proposed changes:

3. **Proposed changes for `<topic>.md` — preview, apply (requires `--fix`), or skip?**
   - Default: preview.
   - Apply requires `--fix` to be set on the original invocation.

## Per-removal gate (under `--fix`)

When a removal is proposed (e.g. "service_alias `legacy_orders` not seen in last 30d → propose removal"), the skill ALWAYS asks before removing — even under `--auto --fix`:

4. **`<field>.<entry>` is proposed for removal: `<reason>`. Remove?**
   - Default: NO. User opts in per removal.
   - Bulk-accept option: "remove all proposed".
   - Reason: removal is the only operation that destroys user-visible state. The skill is conservative.

## Code-cross-reference flag (under `--fix`)

When an addition is proposed but the source name doesn't appear in any configured repo:

5. **`<entry>` is in the source but not referenced in any configured repo (low confidence). Add anyway?**
   - Default: NO.
   - The skill annotates such entries in the diff so the user can still pre-approve via `--auto --fix --include-low-confidence` if they want.

## Source-unreachable confirmation

6. **Source `<datadog | statsig | mixpanel | snowflake | github>` is unreachable. Skip and continue, or stop?**
   - Default: skip and continue.
   - The skill never invents data when a source is down — skipping is the correct behavior.

## Anti-rules

- Never ask under `--auto` for any question whose default is documented (the skill picks the default silently).
- Never stack two questions in one turn. Iterate.
- Never re-ask a question the user already answered earlier in this same session.
- Never ask for confirmation on a read-only action (a smoke-ping, a code grep, a file read).
- Never ask "are you sure?" twice for the same operation. One confirmation, one execution.
