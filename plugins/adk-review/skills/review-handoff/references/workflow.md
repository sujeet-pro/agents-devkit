# `review-handoff` — workflow detail

Detailed phase-by-phase stage list. Logs to `.temp/task-<slug>/validation/per-skill/review-handoff.md`.

## Phase 0 — prompt expand

1. **Resolve task slug.**
   - If `<task-slug>` arg passed → use it (verify `.temp/task-<slug>/` exists).
   - Else: scan `.temp/task-*/` for `.last-modified` (or fall back to mtime), pick the most recent.
   - If no recent task found: stop with "no recent task found; pass `<task-slug>` or run after at least one adk skill ran".
2. **Resolve repo.** Walk up from CWD to `.git`. Stop with "not a git repo" otherwise.
3. **Determine mode.** `--auto` (default) or `-i`. (`--fix` not applicable; this skill is read-only.)
4. **Capture `--post-to <target>`** if set; will trigger Phase 5 post step (with confirmation gate).

## Phase 1 — preflight

1. **`bin/adk-info repos --check`** must return 0.
2. **For `--post-to slack`:** check workspace Slack connector via `claude mcp list`; check `~/.config/adk/slack.md.<channel>` is set (default channel: `team_channel`; for incident handoff: `incident_channel`).
3. **For `--post-to jira`:** check Atlassian connector; check the task slug or `prompt.txt` correlates to a Jira ticket (regex match on `[A-Z]+-\d+`).
4. **For `--post-to pr`:** check `gh auth status`; check current branch has an open PR (`gh pr view --json number`).
5. **No code-mutation tools required** (read-only); skip the `--fix` preflight checks.

## Phase 2 — gather inputs

Parallel reads where possible.

### From `.temp/task-<slug>/`

| Read | Used for |
| --- | --- |
| `prompt.txt` | "Task summary" + signature timestamp |
| `skill-plan.md` (if present) | "Decisions" — which skills ran + why |
| `context.md` (if present) | "Task summary" — links followed |
| `review/findings.md` (if present) | "Work completed" — what was reviewed |
| `review/postback.md` (if present) | "Work completed" — what was posted |
| `feedback/classification.md` (if present) | "Work completed" — feedback addressed |
| `feedback/replies-postback.md` (if present) | "Work completed" — replies sent |
| `investigation/*.md` (if present) | "Work completed" — what was investigated |
| `code/*.md` (if present) | "Work completed" — what was implemented |
| `validation/per-skill/*.md` | "Decisions" + "Work completed" — per-phase validation evidence |
| `report.md` (if present) | "Task summary" — already-aggregated summary |
| `dispatch.md` (if present) | "Decisions" — subagent dispatch details |
| `handoff.md` (if from prior run) | move to `.archive/<iso-ts>/` |

### From git (per `references/git-state-capture.md`)

```bash
git symbolic-ref --short HEAD                    # branch
git status --porcelain                           # dirty files (paths only)
git log --oneline -20                            # recent commits
git diff --stat                                  # uncommitted change stat
git diff                                         # full uncommitted diff (truncated to 200 lines for the doc)
git stash list                                   # stash entries
git remote -v                                    # remote URLs (anonymized — strip tokens)
git rev-parse @{upstream} 2>/dev/null            # upstream ref (if any)
gh pr view --json number,url,state 2>/dev/null   # open PR for current branch (if any)
```

### From environment

```bash
# Anonymized — only NAMES, never VALUES
echo $EDITOR
echo $SHELL
pwd
node --version 2>/dev/null
go version 2>/dev/null
python --version 2>/dev/null
# Plus the .mcp.json env-var names referenced by enabled plugins (names only)
```

### From meta-info (read-only)

```bash
adk-info info name              # for the signature
adk-info repos . notes          # for the build/test command in "Environment"
adk-info github default_org     # for context
```

## Phase 3 — synthesize

Per `references/handoff-template.md`, build the 10 sections:

1. **Task summary** (one paragraph). Source: `prompt.txt` + `skill-plan.md` + `report.md` (if present).
2. **Decisions** (table). Source: per-skill validation logs + `skill-plan.md`.
3. **Work completed** (bulleted with citations). Source: per-skill reports + git log diff vs upstream.
4. **Remaining work** (bulleted with concrete next steps). Source: TODOs in `.temp/task-<slug>/*` + open items in per-skill reports.
5. **Blockers** (table: blocker / owner / ETA / workaround). Source: explicit `BLOCKER:` markers in any artifact + items in `validation/per-skill/*.md` marked as failures with no resolution.
6. **Key files touched** (table: file / why / last touched). Source: `git diff --name-only @{upstream}..HEAD` + uncommitted file list.
7. **Files NOT touched** (table: file / why not). Source: cross-reference candidate files (e.g. mentioned in `findings.md` or `skill-plan.md`) NOT in the touched list. Heuristic; the user verifies under `-i`.
8. **Git state** (branch, dirty?, last 10 commits, uncommitted diff summary, stash). Source: Phase 2 git commands.
9. **Environment** (anonymized). Source: Phase 2 env commands.
10. **Next step** (one sentence + the exact command). Source: derived from the most-recent unfinished step in any per-skill validator.

Write `.temp/task-<slug>/handoff.md`.

## Phase 4 — propose

1. **Show `handoff.md`** to the user.
2. **Mode branch:**
   - `-i`: walk each section, allow edits.
   - `--auto`: present full doc.
3. **Approval gate** (unless `--auto`): user confirms; or under `-i`, edits a section then re-confirms.

## Phase 5 — post (only when `--post-to <target>` is set)

This is a SHARED-STATE action (per the universal interaction contract); always asks before posting, even under `--auto`.

### `--post-to slack`

1. Resolve channel: `--channel <name>` flag → else `~/.config/adk/slack.md.<context-appropriate>` (incident-handoff → `incident_channel`; default → `team_channel`).
2. **Confirmation gate:** "Post handoff to Slack channel `<channel>`? Preview: `<first 3 lines of handoff>`. [y/N]". Default `N` even under `--auto` (the `--auto` defaults the user's prior question approvals; this one is mandatory).
3. Post via Slack workspace connector. Capture message URL.
4. Write `handoff-postback.md` with destination + URL + ts.

### `--post-to jira`

1. Resolve ticket: extract from `prompt.txt` or `skill-plan.md` (regex `[A-Z]+-\d+`). If unclear, ask.
2. **Confirmation gate:** "Post handoff as comment on Jira ticket `<key>`? [y/N]". Default `N`.
3. Post via Atlassian workspace connector. Capture comment URL.
4. Write `handoff-postback.md`.

### `--post-to pr`

1. Resolve PR: from current branch's open PR.
2. **Confirmation gate:** "Post handoff as a comment on PR `<repo>#<num>`? [y/N]". Default `N`.
3. Post via `gh pr comment <num> --body-file handoff.md`. Capture comment URL.
4. **POST-CONFIRMATION** per `/adk-review:review-pr` `references/post-confirmation.md` (5/10/20s retry; never re-post).
5. Write `handoff-postback.md`.

## Phase 6 — report

1. **Surface to user:** the handoff.md path + a one-line summary + the next-step command (which is also in handoff.md, but worth surfacing inline).
2. **Suggest the natural follow-up** based on the handoff content:
   - "Work completed but not pushed → suggest `git push` then `/adk-docs:docs-pr-description`."
   - "PR exists with open comments → suggest `/adk-review:review-feedback`."
   - "Task involves an experiment → suggest `/adk-investigate:investigate-experiment` before resuming."

## Loop control

- **Most-recently-touched task is empty** (skill ran but produced nothing). Surface "task is empty; nothing to hand off; pass an explicit `<task-slug>` or run a skill first".
- **Heuristic-derived "Files NOT touched" is wrong.** Under `-i`, the user fixes; under `--auto`, the user reviews + re-runs.
- **Post-confirmation final miss on `--post-to pr`.** Same protocol as `review-pr`: surface; do NOT re-post.

## Key differences from other review skills

| Concern | Other review-* | `review-handoff` |
| --- | --- | --- |
| Modifies code | yes (with `--fix`) | NEVER |
| Pushes | yes (with `--fix`) | NEVER |
| Posts comments | review-pr posts findings; review-feedback posts replies | only when `--post-to <target>` AND user confirms |
| Reads `.temp/task-<slug>/` wholesale | partial (each skill writes its own) | yes (synthesizes everything) |
| Has dimension passes | yes | NO — read-only synthesis |
| Includes git state | informational | first-class section |
