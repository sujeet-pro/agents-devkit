---
title: 'adk-docs:docs-pr-description'
description: '  Draft a PR description from the actual diff and commit history — NOT from the branch name alone. Reads `git log <base>..HEAD`, `git diff <base>...HEAD`, and any linked ticket context; loads `.github/pull_request_template.md` if present. Surfaces what changed (by area), why (from commit bodies), test plan (from test files added/touched), risks, breaking changes, and follow-ups. Lead with risk; bury bookkeeping. Uses `gh` CLI by default; the `github` MCP from adk-review if both plugins are installed. With --fix, updates the PR body via `gh pr edit --body-file <path>`; still asks once before the first remote write, even under --auto. Use when the user is about to open a PR, or wants to regenerate an existing PR body. Do NOT use for commit messages (/adk-docs:docs-commit-message), changelog entries (/adk-docs:docs-changelog), or authoring a new markdown doc (/adk-docs:docs-write).'
plugin: 'adk-docs'
skill: 'docs-pr-description'
source: 'plugins/adk-docs/skills/docs-pr-description/SKILL.md'
group: 'docs-skills'
order: 3104
---
# adk-docs:docs-pr-description

## Source

`plugins/adk-docs/skills/docs-pr-description/SKILL.md`

## Skill Body

# docs-pr-description — draft a PR description from the diff

Reviewer-first. The PR body tells the reviewer what to look at and in
what order. Lead with risk; bury bookkeeping.

## When to use

- About to open a PR ("draft a PR description")
- Regenerate an existing PR's body ("update the PR description")
- "What's the PR body for this diff?"
- Bare GitHub PR URL + "rewrite the description"

## When NOT to use

| Not this → | Use this |
| --- | --- |
| Commit message for the HEAD commit | `/adk-docs:docs-commit-message` |
| Changelog entry for a release | `/adk-docs:docs-changelog` |
| Author a new README / ADR / runbook | `/adk-docs:docs-write` |
| Review someone else's PR | `/adk-review:review-pr` |
| Self-review your own changes pre-PR | `/adk-review:review-code-changes` |

## Common prompts

- "draft PR description"
- "PR body for this"
- "what's the description for this PR?"
- "update the PR description"
- "rewrite the PR body — make risk more obvious"

## Inputs

| Input | Required | Default |
| --- | --- | --- |
| `<base-branch>` | no | tracking branch → `origin/<base_branch from repos.md>` → `main` |
| `-i` / `--interactive` | no | off |
| `--fix` | no | off; with it, runs `gh pr edit --body-file <path>` |

## Workflow

```
Phase 0 — prompt expansion
  - Resolve repo + branch; determine if a PR already exists for this branch.
  - Pick slug (e.g. pr-<branch>); create .temp/task-<slug>/.

Phase 1 — preflight
  - adk-info --check (info, repos, github, docs).
  - Resolve base branch (explicit arg → tracking → origin/<base> → main).
  - If --fix: confirm `gh` auth (`gh auth status`) or github MCP reachable.
  - Load .github/pull_request_template.md if present.

Phase 2 — gather evidence
  - git log <base>..HEAD --pretty=format:%H|%s|%b|%an|%ae > commits.txt.
  - git diff <base>...HEAD --stat > diffstat.txt.
  - git diff <base>...HEAD -- '**/*test*' '**/*spec*' > tests.diff.
  - If Jira / Confluence links found in commit bodies, queue context-gather.

Phase 3 — classify changes by area
  - Group files by top-level folder / feature area.
  - For each area: summarize what changed in 1-2 sentences (evidence-bound).

Phase 4 — draft per references/risk-first-format.md
  - Title (≤70 chars).
  - Summary (1-3 bullets, risk-first).
  - Changes by area (table).
  - Test plan (from tests.diff; include manual steps if no new tests).
  - Risks / breaking changes.
  - Linked tickets (only those actually in commits).
  - Follow-ups (TODOs deferred).

Phase 5 — validate + optional --fix
  - Validator: no invented tickets, test plan present, title ≤70 chars.
  - --fix: gh pr edit --body-file .temp/task-<slug>/pr-body.md  (ask once).
```

See `references/workflow.md`.

## Persona

> "Reviewer-first." The description tells the reviewer what to look
> at and in what order. Lead with risk; bury bookkeeping. Every claim
> is grounded in the diff, the commits, or a linked ticket — never
> invented.

See `references/persona.md`.

## Constitution

**Must do:**

1. Include a Test plan section. "Manual: ran the app locally and
   clicked through X" is a valid test plan; absent is not.
2. Lead with risk — the first bullet tells the reviewer where to look.
3. Base every claim on evidence (commit, diff chunk, or cited
   ticket).
4. Match the repo's PR template if present (`.github/pull_request_template.md`).
5. Under `--fix`, ask once before the first `gh pr edit` write
   (even with `--auto`).

**Must not do:**

1. Invent linked tickets that aren't in the commits.
2. Repeat the diff in prose form — the reviewer can read the diff.
3. Pad with marketing phrases ("this meaningfully improves the
   checkout experience").
4. Auto-merge or auto-approve.
5. Force-push anything.
6. Edit the PR body silently; always re-show and confirm under
   `-i --fix`.

## Anti-patterns

See `references/anti-patterns.md`. Highlights:

- "Updated some files" descriptions.
- Repeating the diff as bullet points.
- Inventing a Jira ticket from the branch name.
- Omitting the test plan because the change is "obvious".

## Output

| Path | Content |
| --- | --- |
| `.temp/task-<slug>/prompt.txt` | Verbatim user prompt + timestamp |
| `.temp/task-<slug>/commits.txt` | Raw `git log` output |
| `.temp/task-<slug>/diffstat.txt` | Raw `git diff --stat` output |
| `.temp/task-<slug>/pr-body.md` | The final PR body (what `gh pr edit` consumes) |
| `.temp/task-<slug>/report.md` | Final consolidated report |

See `references/output-format.md`.

## References shipped with this skill

| File | Purpose |
| --- | --- |
| `references/persona.md` | Reviewer-first describer persona |
| `references/workflow.md` | Phase 0–5 stage detail |
| `references/modes.md` | `--auto / -i / --fix` for this skill |
| `references/interaction-contract.md` | Canonical interaction contract (byte-identical) |
| `references/anti-patterns.md` | What to avoid |
| `references/examples.md` | 4 worked PR descriptions |
| `references/output-format.md` | Exact `pr-body.md` shape |
| `references/artifact-format.md` | `.temp/task-<slug>/` layout |
| `references/validator.md` | Per-phase gates |
| `references/how-it-works.md` | Mermaid flow |
| `references/clarifying-questions.md` | Questions under `-i`; defaults under `--auto` |
| `references/pr-template-loader.md` | Loading `.github/pull_request_template.md` rules |
| `references/risk-first-format.md` | The skill-specific PR body format |

## Additional links

The skill may fetch these when relevant:

- The Jira / Linear / Asana ticket linked from a commit body (via workspace connectors).
- Upstream docs when a change integrates a new vendor API.
- Related merged PRs in the same repo for style matching.
