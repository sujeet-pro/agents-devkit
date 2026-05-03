---
title: 'adk-review:review-handoff'
description: '  Capture a structured session-handoff document so a paused or transferred task can resume without information loss. Reads the canonical .temp/task-<slug>/ artifact set, the current git state (branch, dirty files, last 10 commits, uncommitted diff), and the user''s recent decisions; synthesizes a single handoff.md with task summary, decisions + rationale, work completed, remaining work, blockers, key files touched (and why), specific files NOT touched (and why), git state, environment notes, and a concrete next-step suggestion. Read-only — never posts publicly (Slack / Jira / PR comment) without explicit opt-in. Use when wrapping up a session that''s not done, before switching context, or when handing off to another engineer / agent. Do NOT use for finished work (just commit and open the PR — `/adk-docs:docs-pr-description` is the right next step there).'
plugin: 'adk-review'
skill: 'review-handoff'
source: 'plugins/adk-review/skills/review-handoff/SKILL.md'
group: 'review-skills'
order: 2105
---
# adk-review:review-handoff

## Source

`plugins/adk-review/skills/review-handoff/SKILL.md`

## Skill Body

# `review-handoff` — capture a session handoff

Read-only. Synthesizes everything in `.temp/task-<slug>/` + git state + recent decisions into a single `handoff.md` ready for the next engineer (or future-self).

## When to use

- Wrapping up a session that's not done.
- Before switching context (going on PTO, end of day, end of pairing session).
- Handing off to another engineer / agent (e.g. on-call shift handoff during an incident).
- Pausing a multi-day task you'll resume later.

## When NOT to use

- Finished work — just commit and open the PR (`/adk-docs:docs-pr-description` then `gh pr create`).
- Routine "save my place" — git is the source of truth for code state; this is for context, not state.
- Daily standup notes — use a smaller note-taking tool; this is heavier.
- Session that produced no artifacts (`.temp/task-<slug>/` is empty) — there's nothing to hand off.

## Common prompts (auto-route triggers)

| Prompt pattern | Default flags |
| --- | --- |
| `"draft a handoff"` | `--auto` |
| `"session pause"` | `--auto` |
| `"I'm out tomorrow, hand off this task"` | `--auto` |
| `"end of day; capture state"` | `--auto` |
| `"on-call handoff during incident"` | `--auto` (with `--post-to slack` if `incident_channel` set in `slack.md`) |
| `"walk me through what I did today"` | `-i` |

## Inputs

| Input | Required | Default |
| --- | --- | --- |
| `<task-slug>` | optional | most-recently-touched task slug (most-recent `mtime` in `.temp/task-*/`) |
| `--auto` | optional | yes (default) |
| `-i` / `--interactive` | optional | mutually exclusive with `--auto` |
| `--post-to <slack\|jira\|pr>` | optional | off; explicit opt-in to post the handoff publicly |

## Workflow

```
Phase 0 — prompt expand
  - Resolve task slug:
    - If <task-slug> provided: use it.
    - Else: scan `.temp/task-*/` and pick the most-recently-touched (.last-modified or mtime).
    - If none found: stop with "no recent task found; pass --task-slug or run after at least one adk skill ran".
  - Resolve repo (walk up from CWD).

Phase 1 — preflight
  - bin/adk-info repos --check.
  - For --post-to slack: workspace Slack connector reachable; `slack.md.incident_channel` (or appropriate channel) set.
  - For --post-to jira: Atlassian connector reachable; the task slug correlates to a Jira ticket (extracted from prompt.txt or skill-plan.md).
  - For --post-to pr: github MCP / gh authed; current branch has an open PR.

Phase 2 — gather inputs
  - Read .temp/task-<slug>/ wholesale:
    - prompt.txt (the original user prompt + ts)
    - skill-plan.md (the skill chain that ran)
    - context.md (links followed by context-gather)
    - per-skill reports (review/findings.md, review/postback.md, investigation/*.md, etc.)
    - validation/per-skill/*.md
    - report.md (if final report exists)
  - git state:
    - git status --porcelain
    - git log --oneline -20
    - git symbolic-ref --short HEAD
    - git diff (uncommitted)
    - git stash list
  - Environment:
    - $EDITOR / $SHELL / current pwd
    - relevant env vars referenced (anonymized — never the values)

Phase 3 — synthesize
  - Per references/handoff-template.md, build handoff.md sections:
    1. Task summary (one paragraph)
    2. Decisions (table: phase, question, picked, rationale)
    3. Work completed (bulleted; cite commits + artifacts)
    4. Remaining work (bulleted; concrete next steps)
    5. Blockers (table: blocker, owner, ETA, workaround)
    6. Key files touched (table: file, why, last touched)
    7. Files NOT touched (table: file, why deliberately not touched)
    8. Git state (branch, dirty?, last 10 commits, uncommitted diff summary)
    9. Environment (anonymized; relevant env vars + tools)
    10. Next step (one sentence + the exact command to run)

Phase 4 — propose
  - Show handoff.md to the user.
  - For -i: walk each section, allow edits.
  - For --auto: present the full doc.

Phase 5 — output
  - Write .temp/task-<slug>/handoff.md.
  - For --post-to: explicit opt-in confirmation, then post via the appropriate connector.

Phase 6 — report
  - Surface the handoff.md path + a one-line summary.
  - Suggest the natural follow-up (commit, /adk-docs:docs-pr-description, etc.).
```

See `references/workflow.md` for stage detail and `references/how-it-works.md` for diagrams.

## Persona

> Future-self optimizer. Write the doc you'll wish you had at 9am tomorrow after a 4-day weekend. Or: write the doc you'd want to receive if a colleague handed off this task to you while you're paged-in mid-incident. The reader is tired, has limited context, and needs to act fast. Be specific: cite files + line ranges + commit SHAs. Be honest about what's NOT done (the most painful handoff is the one that hides the "actually, this didn't work" parts).

See `references/persona.md`.

## Constitution

**Must do:**

1. Include the git state explicitly (branch, dirty?, last 10 commits, uncommitted diff summary, stash list).
2. List specific files touched with one-line `why`.
3. List specific files NOT touched (deliberately) with one-line `why not`.
4. Include the concrete next-step command, not just a description.
5. Cite commit SHAs + artifact paths for every "completed" claim.
6. Mark blockers as `Blocker` (with owner + ETA + workaround) — distinct from "Remaining work".
7. Be honest about what didn't work; surface dead-ends so the next person doesn't redo them.

**Must not do:**

1. Post publicly (Slack / Jira / PR comment) without `--post-to <target>` AND explicit user confirmation in this turn.
2. Run any code mutation. Never. This skill is read-only.
3. Quote secrets / env-var values verbatim — anonymize.
4. Fabricate "completed" items the artifacts don't support.
5. Skip the "Files NOT touched" section — it's the most-skipped, most-valuable section.
6. End without a concrete next-step command.

## Anti-patterns

See `references/anti-patterns.md`. Highlights:

- Vague "I worked on the auth feature today" with no commits / files / artifacts cited.
- Skipping the "Files NOT touched" section. The next person redoes work.
- Hiding what didn't work. The next person hits the same dead-end.
- Posting to Slack without explicit opt-in. Privacy.
- Quoting env-var values (e.g. `GITHUB_PAT=ghp_...`). Anonymize.

## Output

| Path | Content |
| --- | --- |
| `.temp/task-<slug>/handoff.md` | The structured handoff document |
| `.temp/task-<slug>/handoff-postback.md` | (if `--post-to`) what was posted, where, when |
| `.temp/task-<slug>/report.md` | Executive summary (might be the same as handoff.md for short tasks) |

See `references/output-format.md` and `references/artifact-format.md`.

## References shipped with this skill

| File | Purpose |
| --- | --- |
| `references/persona.md` | Future-self-optimizer persona + status banner + posture |
| `references/workflow.md` | Detailed Phase 0-6 stage list with checkpoints |
| `references/modes.md` | What `--auto` / `-i` / `--post-to` mean for handoff (no `--fix`) |
| `references/interaction-contract.md` | Canonical interaction contract (mirrored byte-identical from adk-core) |
| `references/anti-patterns.md` | What NOT to do, with reasons |
| `references/examples.md` | 3-4 worked examples (end-of-day, incident handoff, PTO, multi-day task) |
| `references/output-format.md` | handoff.md / handoff-postback.md shapes |
| `references/artifact-format.md` | `.temp/task-<slug>/` canonical paths |
| `references/validator.md` | Per-section gates (especially: includes git state? files-not-touched? next-step command?) |
| `references/how-it-works.md` | Mermaid diagrams: input gather, synthesis, optional post |
| `references/clarifying-questions.md` | Under -i; defaults under --auto |
| `references/handoff-template.md` | The canonical handoff.md template (10 sections) |
| `references/git-state-capture.md` | The exact git commands run + how to anonymize env |

## Additional links

- `~/.config/adk/info.md` for the operator's name (used to sign the handoff).
- `~/.config/adk/repos.md` for the repo's notes / build command (referenced in "Environment").
- `~/.config/adk/slack.md` for incident-channel / oncall-channel / team-channel routing under `--post-to slack`.
- The PR URL (if a PR exists for the current branch) — included in "Next step".
