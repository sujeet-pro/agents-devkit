# `investigate-rca` — clarifying questions

Asked in order, one at a time, **only when the answer changes the plan**. Under `--auto`, defaults apply silently.

## Phase 1 questions

1. **Symptom + window: `<symptom>` at `<symptom-time>`, window `<window>`. OK?**
   - _When asked:_ symptom-time was not parsed cleanly from the prompt.
   - _Default under `--auto`:_ parse from prompt; default `±2h`; if both fail, stop and ask (this is critical — wrong window means wrong RCA).

## Phase 4 questions (git blame)

2. **Implicated files (from incident.md hypothesis): `<list>`. Blame these?**
   - _When asked:_ only under `-i`. Under `--auto`, blame all listed files.
   - _Default under `--auto`:_ blame; cap at 5 files (avoid runaway blame on a wide-touching deploy).

3. **PR `<num>` identified as the suspect. Pull diff + author + reviewer?**
   - _When asked:_ only under `-i`. Under `--auto`, pull.
   - _Default under `--auto`:_ pull.

## Phase 5 questions (Mixpanel)

4. **User-facing flow: `<funnel>` affected. Pull Mixpanel impact?**
   - _When asked:_ only under `-i`. Under `--auto`, pull if `mixpanel-workspace` MCP reachable.
   - _Default under `--auto`:_ pull if reachable; skip with note if not.

## Phase 6 questions (aggregation)

5. **Action item draft `<title>` says "be more careful". This isn't testable. Rewrite suggestion: `<rewrite>`. Accept, edit, or skip?**
   - _When asked:_ always for any flagged action item — even under `--auto`.
   - _Default under `--auto`:_ apply the rewrite; log to `blameless-rewrite-log.md`. The operator can review post-emit.

6. **Root cause sentence names `<individual>`. Rewriting to system-shaped: `<rewrite>`. Accept, edit, or skip?**
   - _When asked:_ always — even under `--auto`. This is a HARD rule (no individuals as root cause).
   - _Default under `--auto`:_ apply the rewrite.

## Phase 7 questions

7. **RCA ready. Want to publish to Confluence now (`/adk-docs:docs-publish-confluence`)?**
   - _When asked:_ only under `-i`. Under `--auto`, NEVER auto-publishes; surfaces the suggestion in the report's `Follow-up` section.
   - _Default under `--auto`:_ DO NOT auto-publish. Stop at `.temp/`.

## Anti-rules for asking

- Never ask 3 questions stacked in one turn.
- Never ask about something the meta-info already answers.
- Never ask under `--auto` EXCEPT the two HARD rule questions (5 and 6 above).
- If the user already answered earlier, don't re-ask.
- Don't ask "are you sure?" before a read-only call.
- NEVER ask "should I skip the timeline?" — the timeline is mandatory.
- NEVER ask "should I skip the blameless rewrite?" — it's mandatory.
