# `review-handoff` — output format

## Per-turn status (each turn opens with this)

```
[adk-review:review-handoff] task=<slug> repo=<repo-name> branch=<branch> dirty=<yes|no> phase=<0|1|2|3|4|5|6> mode=<auto|interactive>[+post-to <target>] sections=<n-of-10>
```

`<sections>` is a populate-counter (e.g. `7-of-10` after Phase 3 partial; `10-of-10` after Phase 3 complete).

## Final report

Written to `.temp/task-<slug>/report.md`. For short tasks, the report is just a pointer to `handoff.md`:

```markdown
# review-handoff report — <slug>

## Result
Wrote handoff.md (10 sections, 124 lines). Next: <one-line next-step>.

## Artifact index
.temp/task-<slug>/
  handoff.md           the canonical handoff document
  handoff-postback.md  (if --post-to ran) where it was posted, when
  report.md            this file (pointer)
```

## `handoff.md` shape (the canonical 10-section template)

```markdown
# Handoff — <task-slug>

_Authored <ISO-ts>Z by adk-review:review-handoff for <operator-name from info.md>._

## 1. Task summary
<one paragraph — restate the task, name the goal, name what's done vs what's not, in the operator's own voice (not "the agent did X"; rather "implemented X")>

## 2. Decisions
| Phase | Question | Picked | Rationale |
| --- | --- | --- | --- |
| <phase> | <q> | <a> | <one-line rationale> |
| ... |

## 3. Work completed
- <action> — <commit SHA / artifact path> — <one-line evidence>
- ...

## 4. Remaining work
1. <action> at <file:line> — <one-line context>
2. ...

## 5. Blockers
| Blocker | Owner | ETA | Workaround |
| --- | --- | --- | --- |
| <description> | <name or @login> | <date or `unknown`> | <one-line workaround if any> |

## 6. Key files touched
| File | Why | Last touched |
| --- | --- | --- |
| <path> | <one-line> | <commit SHA or "uncommitted"> |

## 7. Files NOT touched (deliberately)
| File | Why not |
| --- | --- |
| <path> | <one-line — the reason this was considered + skipped> |

## 8. Git state
- Branch: <branch>
- Dirty: <yes|no> (<n> files)
- Last <n> commits:
  - <SHA> <subject>
  - ...
- Uncommitted diff: +<add>/-<del> across <n> files (full diff: see `git diff` from this branch; truncated below)

```diff
<truncated diff — first 200 lines max; refer to `git diff` for full>
```

- Stash: <empty | <n> entries>

## 9. Environment
- Editor: <from $EDITOR>
- Shell: <from $SHELL>
- pwd: <from `pwd`>
- Tools: <relevant; e.g. node v22.7, go 1.23, python 3.13, docker 27.3>
- Env vars relied on (names only): <e.g. GITHUB_PAT, DD_API_KEY> (values NEVER quoted)

## 10. Next step
<one sentence — the concrete action to take>

```
<the exact command(s)>
```

<optional: alternate paths if the next step depends on a decision>
```

## `handoff-postback.md` shape (only when `--post-to` ran)

```markdown
# Handoff postback

## Posted
| Target | Channel / Ticket / PR | URL | Posted at | Confirmed at |
| --- | --- | --- | --- | --- |
| slack | #incidents | <slack-message-url> | 2026-05-03T18:50Z | n/a (Slack confirms synchronously) |
| OR jira | CHK-1340 | <jira-comment-url> | 2026-05-03T18:50Z | n/a |
| OR pr | acme/storefront#103 | <pr-comment-url> | 2026-05-03T18:50Z | yes (5s) |

## NOT posted
| Target | Reason |
| --- | --- |
| (empty when all targets succeeded) | |

## Post-confirmation timeline (PR only)
- t=0s   : posted via gh pr comment
- t=5s   : re-fetch → c-7891 visible (confirmed).

## Privacy notes
- handoff.md was posted as-is (no transformation).
- Public Slack post: handoff was truncated to 30 lines + link (full doc remains in .temp/).
- No env-var values were quoted; only names.
```

## Section-specific format rules

### "Task summary" (section 1)

- One paragraph, 2-5 sentences.
- First-person voice (the operator's voice), past tense for completed work.
- No agent-self-reference (`/adk-review:review-handoff` doesn't say "I read the artifacts").

### "Decisions" (section 2)

- Table format. 3-8 rows.
- Each row: phase + question (1 line) + picked (1 line) + rationale (1 line).
- Group multiple-step decisions with the same `Phase` value.

### "Work completed" (section 3)

- Bulleted list. 3-15 items.
- Each item: action + commit SHA / artifact path + one-line evidence.
- "Tested" items include the test command + result (e.g. `npm test src/billing/ → 14/14 PASS`).

### "Remaining work" (section 4)

- Numbered list (so the next person can refer "I did #1, blocked on #2").
- Each item: action + file:line + one-line context.
- DO NOT list blockers here (they go in section 5).

### "Blockers" (section 5)

- Table format. Common case: empty (`| (none) | — | — | — |`).
- Owner is `@login` or "self" or "unknown". ETA is a date or `unknown`. Workaround is "(none)" or one line.

### "Key files touched" (section 6)

- Table. Sorted by importance (the file most-changed first).
- Cite the commit SHA OR "uncommitted" — never both for one file (latest state wins).

### "Files NOT touched (deliberately)" (section 7)

- Table.
- The most-skipped section across all handoffs. The skill's heuristic identifies candidates; the user verifies under `-i`.
- Include only files that were CONSIDERED + REJECTED (or deferred). Don't list every file in the repo that wasn't touched.

### "Git state" (section 8)

- Branch + dirty status + last N commits (default 10) + diff stat + truncated diff (200 lines max) + stash list.
- The truncated diff is appended only when `--no-diff-truncate` is NOT set AND the total uncommitted diff is <500 lines. Larger diffs reference `git diff` only.

### "Environment" (section 9)

- Anonymized. Tool versions, editor, shell, pwd. Env-var names ONLY.
- If `--no-env` set, the section reads "(omitted by --no-env)".

### "Next step" (section 10)

- One sentence describing the next action.
- The exact command(s), in a fenced bash block.
- Optional alternate paths if the next step depends on a decision (e.g. "if the test passes, ...; if it fails, ...").

## Length budget

- Target: ~80-150 lines for the typical handoff.
- Hard upper bound: ~300 lines. If the synthesis exceeds this, the skill warns the user — handoffs longer than 300 lines are read-skip-skim territory.
- Truncation strategy: keep all sections; truncate within section 8 (git diff), then section 9 (env), then section 6 (files touched).

## Slack-friendly mode (when `--post-to slack`)

For Slack publishing, the skill emits a TRUNCATED view:

```
*Handoff for <slug>* (full doc: <link>)

Done: <bullet, 3 max>
Remaining: <numbered, 3 max>
Next: `<exact command>`

Files touched: <count>; not touched (deliberately): <count>; blockers: <count>.
```

The full handoff.md is published separately (e.g. as a Confluence page or a Gist); the Slack message links to it.
