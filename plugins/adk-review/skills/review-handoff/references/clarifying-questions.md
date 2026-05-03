# `review-handoff` — clarifying questions

Asked in order, one at a time, **only when the answer changes the plan**. Under `--auto`, defaults apply silently; surface in the final report.

## Phase 0 questions

1. **Detected task slug: `<slug>`. Use this?**
   - _How to pick:_ default = most-recently-touched `.temp/task-*/`.
   - _Skip when:_ `<task-slug>` arg explicitly passed.
   - _Always show under --auto:_ as info in the status banner; only ask if `--auto` and the inferred slug is older than 24h (suggests it might be a wrong pick).

## Phase 3 questions (under `-i`)

2. **For each section: accept, edit, or skip?**
   - _How to pick:_ default `accept`.
   - _Skip when:_ `--auto`.
   - For "Files NOT touched" specifically: ALWAYS show under `-i` because the heuristic guess is the most likely to be wrong.

## Phase 4 questions

3. **Handoff is `<n>` lines. Show full doc, or just an executive summary?**
   - _How to pick:_ default `executive summary` + offer-depth.
   - _Skip when:_ `--auto`.

## Phase 5 questions (only when `--post-to <target>` set)

4. **(--post-to slack) Resolved channel: `<channel>`. Use this?**
   - _How to pick:_ default = `slack.md.team_channel`; for incident-context slugs, default = `slack.md.incident_channel`.
   - _Skip when:_ `--channel <name>` explicitly passed.

5. **(--post-to jira) Resolved ticket: `<key>`. Use this?**
   - _How to pick:_ extracted from `prompt.txt` / `skill-plan.md` via regex.
   - _Skip when:_ `--ticket <key>` explicitly passed.

6. **(--post-to ANY) Post handoff to `<target>`? Preview: `<first 3 lines>`.**
   - _How to pick:_ NO DEFAULT. Always asks (default `N` even under `--auto`). This is the explicit-opt-in for shared-state action.
   - _Skip when:_ NEVER.

## Anti-rules for asking

- **Never ask about something the meta-info answers.**
- **Never stack 3 questions in one turn.**
- **Never ask under `--auto`** UNLESS the question is about a SHARED-STATE action (e.g. `--post-to`).
- **The post-to confirmation gate ALWAYS asks.** Even under `--auto`.
- **Once-per-session.** If the user already answered the same question (e.g. "yes, use slack channel #incidents"), don't re-ask within the same task slug.
- **Never ask about whether to mutate code.** This skill is read-only; no question makes sense.
- **Never ask about whether to push.** This skill never pushes.

## Why this skill asks fewer questions than `review-pr`

- No new findings → no severity tier / dimension question.
- No code mutation → no fix-application question.
- No reconciliation → no per-comment classification question.
- The 10-section template is fixed; no per-section content questions under `--auto`.

Under `--auto` (no `--post-to`), this skill typically asks ZERO questions and runs end-to-end.

Under `--auto --post-to slack`, the typical interaction is:

1. Skill: "Post handoff to Slack channel #incidents? Preview: '...'. [y/N]"
2. User: `y`
3. Skill: posts; surfaces report.
