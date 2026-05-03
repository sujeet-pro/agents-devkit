# `investigate-incident` — clarifying questions

Asked in order, one at a time, **only when the answer changes the plan**. Under `--auto`, defaults apply silently and are surfaced in the report's `Decisions` section.

## Phase 0 questions

1. **Service: `<resolved>`. Right one?**
   - _When asked:_ shorthand resolves to multiple candidates; OR no service in the symptom and no `--service` flag.
   - _Default under `--auto`:_ pick the verified-aliased candidate; if ambiguous and no `--service` flag, stop and ask (this is a critical entity).

2. **Window: `<resolved>`. OK?**
   - _When asked:_ no `--window`, no `--symptom-time`, and the symptom doesn't name a time.
   - _Default under `--auto`:_ `last 2h`.

3. **Slack channel: `<#name>`. Scrape?**
   - _When asked:_ only under `-i`. Under `--auto`, default = scrape if reachable.
   - _Default under `--auto`:_ scrape `slack.md.incident_channel` if `slack-workspace` MCP reachable. Skip silently if unreachable; flag the gap in the report.

## Phase 5 questions (Slack)

4. **Slack scrape returned `<N>` messages, `<K>` of which mention the service. Surface top-`<M>` threads, or all?**
   - _When asked:_ N > 25.
   - _Default under `--auto`:_ top-10 threads by relevance (mention count + recency).

## Phase 6 questions (correlation)

5. **Multiple plausible hypotheses found. Surface all, or just the highest-confidence?**
   - _When asked:_ rare; only when 2+ hypotheses tie at the same confidence.
   - _Default under `--auto`:_ surface all (transparency wins).

## Phase 8 questions (next actions)

6. **Suggested next action: `<action>` (cost `<duration>`, reversible in `<duration>`). Trigger now?**
   - _When asked:_ NEVER. The skill never triggers; it always describes. Under `-i`, the operator may say "yes" but this skill still doesn't run the action — it produces the command for the operator to copy-paste.
   - _Default under `--auto`:_ describe only; never trigger.

## Phase 9 questions

7. **Chain to `/adk-code:code-bugfix` for the fix?**
   - _When asked:_ only under `-i` if a code-cause hypothesis was named with high confidence.
   - _Default under `--auto`:_ list the suggested invocation in the `Follow-up` section; do not auto-chain.

## Anti-rules for asking

- Never ask 3 questions stacked in one turn.
- Never ask about something the meta-info already answers.
- Never ask under `--auto` EXCEPT the question about ambiguous service in Phase 0 (this is critical).
- If the user already answered earlier, don't re-ask.
- Don't ask "are you sure?" before a read-only call.
- NEVER ask "should I trigger the rollback?" — this skill never triggers actions; it always describes.
