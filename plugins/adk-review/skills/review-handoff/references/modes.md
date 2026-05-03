# `review-handoff` — mode contract

`review-handoff` supports `--auto` (default) and `-i` / `--interactive`. It does **not** support `--fix` (the skill is read-only). It supports `--post-to <slack|jira|pr>` for explicit-opt-in publishing.

| Mode | Effect |
| --- | --- |
| `--auto` (default) | Gather + synthesize + write `handoff.md`. No public post. No per-section gating. |
| `-i` / `--interactive` | Walk each of the 10 sections; allow edits before writing. |
| `--post-to slack` | Adds Phase 5 (post to Slack channel). Confirmation gate ALWAYS asks (even under `--auto`). |
| `--post-to jira` | Adds Phase 5 (post as Jira comment). Confirmation gate ALWAYS asks. |
| `--post-to pr` | Adds Phase 5 (post as PR comment). Confirmation gate ALWAYS asks. POST-CONFIRMATION applies. |
| `--auto -i` | Invalid; refused at parse. |

## `--auto` (default mode)

- Skips per-section approval gates.
- Picks the documented defaults at every decision (most-recent task slug; standard 10-section template).
- Writes `handoff.md` to `.temp/task-<slug>/handoff.md`.
- Does NOT post anywhere.
- Surfaces the doc + next-step command.

## `-i` / `--interactive`

- Mutually exclusive with `--auto`.
- Per-section approval: walks each of the 10 sections, allows edits.
- Particularly useful for the "Files NOT touched" section (the heuristic guess often needs human-in-the-loop refinement).

## `--post-to <target>` (orthogonal to `--auto` / `-i`)

The post step is a SHARED-STATE action per the universal interaction contract. Even under `--auto`, the post step **always asks** with a preview of the first 3 lines of the handoff.

| Target | Channel resolution | Post mechanism | Confirmation gate |
| --- | --- | --- | --- |
| `slack` | `--channel <name>` flag → `~/.config/adk/slack.md.<context-channel>` (incident → `incident_channel`; else `team_channel`) | Slack workspace connector | ASKS (default N) |
| `jira` | extract `[A-Z]+-\d+` from `prompt.txt` / `skill-plan.md`; else ask | Atlassian workspace connector | ASKS (default N) |
| `pr` | current branch's open PR | `gh pr comment <num> --body-file handoff.md` | ASKS (default N); plus POST-CONFIRMATION |

## What this skill will NOT do, ever

1. Modify code. Read-only.
2. `git push`, `git commit`, `git stash`, `git merge`, `git rebase`. Read-only.
3. `gh pr merge`, `gh pr close`, `gh pr edit`. Read-only.
4. Modify `~/.config/adk/*.md`.
5. Modify `.temp/task-<slug>/` files OTHER than its own outputs (`handoff.md`, `handoff-postback.md`).
6. Post to a channel without `--post-to <target>` AND user confirmation in the same turn.
7. Quote env-var values verbatim (e.g. `GITHUB_PAT=ghp_...`). Anonymize.
8. Quote secrets / customer names / PII from logs. Anonymize.

## Subset / specialized flags

- `--post-to <target>` (already covered above).
- `--channel <name>` — overrides the auto-derived Slack channel.
- `--ticket <key>` — overrides the auto-derived Jira ticket key.
- `--no-files-not-touched` — skip the "Files NOT touched" section. Default: include. (Section is the most valuable; rarely skipped.)
- `--no-env` — skip the "Environment" section. Default: include. (Section is small and useful.)
- `--commits <n>` — number of recent commits to include in "Git state". Default: 10.

## Default vs override

| Decision | Default | Override |
| --- | --- | --- |
| Task slug | most-recently-touched (`mtime` of `.temp/task-*/`) | `<task-slug>` arg |
| Sections | all 10 | `--no-<section-name>` for the optional ones |
| Recent-commit count | 10 | `--commits <n>` |
| Public post | NO | `--post-to <target>` (still asks) |
| Slack channel | `team_channel` (or `incident_channel` if context is incident) | `--channel <name>` |
| Jira ticket | extracted from prompt | `--ticket <key>` |
| PR | current branch's open PR | (not overrideable; if multiple PRs are open for the branch, ask) |

## Composability

`review-handoff` is the natural last step at end-of-session for any other skill chain that didn't finish. Common chains:

- `code-bugfix` → `review-code-changes` → (didn't finish) → `review-handoff` (next-day pickup).
- `investigate-incident` → (paged out) → `review-handoff --post-to slack` (oncall handoff).
- `review-pr` → (mid-review interruption) → `review-handoff` (resume tomorrow).
- `code-migrate` → (multi-day task) → `review-handoff` daily at end-of-day; final day → `/adk-docs:docs-pr-description` then `gh pr create`.
