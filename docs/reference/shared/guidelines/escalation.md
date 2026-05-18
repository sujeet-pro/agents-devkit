---
title: 'guidelines/escalation'
description: '- User says: "I don''t know", "you decide", "what would you recommend?", "help me pick", "I''m not sure", "explain X".'
source: 'shared/guidelines/escalation.md'
group: 'shared-guidelines'
order: 6303
---
# shared/guidelines/escalation

> Source: `shared/guidelines/escalation.md`

# guideline: escalation

> When and how to hand off — to `/adk-explain`, to the user, to a different skill, or to refuse.

## When to escalate to `/adk-explain`

- User says: "I don't know", "you decide", "what would you recommend?", "help me pick", "I'm not sure", "explain X".
- The chosen approach has < 3 prior matches in the decision log (weak signal).
- The user keeps overriding the same default in different directions (no clear pattern).

Pass to explain: the question being faced, the options, the context summary, prior decision-log evidence (if any).

## When to escalate to a different adk skill

- Mid-flow discovery: e.g., `/adk-implement` discovers the spec is in Confluence — call `/adk-sync --read` to fetch it, integrate, continue.
- Composite intent recognized: e.g., "investigate and write an RCA" — chain `/adk-investigate` → `/adk-document --type rca`.
- Findings imply a follow-up: e.g., after `/adk-review` produces a Critical finding, suggest `/adk-implement --fix <pr>` as the next-best action.

The current skill never silently delegates. It surfaces the recommended next step in its report and lets the user invoke.

## When to escalate to the user (pause)

- Constitution rule about to be hit (shared-state write): STOP, ask, resume.
- Required MCP / env var missing: STOP, name the gap, suggest the fix.
- Validator gate fails: STOP, report errors, don't paper over.
- Contradiction between sources (code says X, doc says Y): STOP, ask which to trust.
- Cost / time threshold exceeded (LLM-calls per minute, or step taking > 5min): STOP, report progress, ask.

## When to refuse

- Out-of-scope: Bitbucket / GitLab / Windows / non-supported third party.
- Risk class adk can't gate safely: production data mutations, irreversible operations on shared state without rollback.
- PII access without explicit confirmation.
- Skill invoked against a target that doesn't exist (URL 404, path doesn't exist, ID not found).

## How to refuse (well)

```
I can't <X> because <specific reason>.

Closest thing I can do: <Y>.

What you can do manually: <Z>.
```

Don't:
- Apologize repeatedly. One "sorry" max.
- Pretend you'll do it but partially. Refuse cleanly OR proceed cleanly.
- Suggest "you might want to try…" without specifying. Be concrete.

## Recording escalations

Every escalation (regardless of type) gets a decision-log entry with `fork_type: escalation`:

```json
{"ts":"...","skill":"adk-implement","fork_id":"escalation","fork_type":"escalation",
 "to":"adk-explain","reason":"user said I dont know","context_summary":"..."}
```

`/adk-improve` uses these to refine when to offer up-front choice vs hand-off-to-explain.
