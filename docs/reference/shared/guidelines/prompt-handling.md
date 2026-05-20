---
title: 'guidelines/prompt-handling'
description: '1. **Tokenize the prompt** into: imperative verb(s), entities (URLs / paths / IDs / quoted strings), modifiers (deadlines, constraints, mode flags).'
source: 'shared/guidelines/prompt-handling.md'
group: 'shared-guidelines'
order: 6307
---
# shared/guidelines/prompt-handling

> Source: `shared/guidelines/prompt-handling.md`

# guideline: prompt-handling

> Referenced from `AGENTS.md`. Loaded by every skill — it's how the agent interprets the user's prompt.

## Steps

1. **Tokenize the prompt** into: imperative verb(s), entities (URLs / paths / IDs / quoted strings), modifiers (deadlines, constraints, mode flags).
2. **Classify the verb**: implement | review | investigate | document | sync | explain | improve | setup. Multiple verbs → multiple skills in sequence.
3. **Resolve entities** against `~/.agents-devkit/config/overrides.yaml` + `<repo>/.adk/overrides.yaml`. If unresolved: surface to user.
4. **Detect mode flags**: `--auto`, `-i`, `--fix`, `--dry-run`, `--target X`, etc.
5. **Pick the skill (or chain)** per `AGENTS.md §2` table.
6. **Compose with non-adk skills** if available — see §3 of AGENTS.md.
7. **Run the chosen skill(s)** through advisor + question-first + workflows.

## Verb hints

| Word in prompt | Most-likely verb |
|---|---|
| implement, build, add, write (code), ship | implement |
| review, audit, look at, check, sanity-check | review |
| investigate, why, debug, troubleshoot, RCA, root cause | investigate |
| document, write up, draft, summarize, runbook, RCA doc, ADR, PR description | document |
| publish, sync, push to, update <X> page, post to | sync |
| set up, bootstrap, configure, install | setup |
| improve, learn, refresh metadata | improve |
| explain, what is, help me decide, I don't know | explain |

## Entity hints

| Entity shape | Resolves as |
|---|---|
| `<KEY>-<NUM>` | Jira ticket (look up project key in overrides.workspaces[*].jira_projects if not explicit) |
| `#<num>` after a repo reference | GitHub PR or issue (context disambiguates) |
| `<service>.<verb>` | Datadog APM service tag |
| `<repo-name>` from `overrides.repos[]` | local checkout path |

## Ambiguous prompts

- "fix this" with no context → ask which file / PR / error.
- "the usual" → look at the user's last decision log entry for this skill+repo; offer that as default.
- "do everything" → refuse the open-ended scope; offer 3 narrowed options.

## Mode escalation

- If a prompt looks like it needs multiple skills, run them sequentially with explicit hand-offs (not all in parallel).
- If a skill in the chain fails (validator fail, gap surfaced), STOP the chain; don't auto-proceed.

## Anti-patterns

- "I think you meant X" without confirming. Ask.
- Inferring a deadline from "soon". Ask if relevant.
- Treating a URL paste as a full request. The URL provides context; the user still needs to say what they want done with it.
