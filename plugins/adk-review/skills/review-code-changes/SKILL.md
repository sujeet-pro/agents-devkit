---
name: review-code-changes
description: |
  Self-review of LOCAL working-tree changes (uncommitted, staged, or branch-vs-baseline) — before pushing or opening a PR. Picks up the baseline automatically: the branch's tracking branch, then `origin/<current-branch>`, then `main`/`master`. Includes uncommitted, staged, and untracked files in scope. Same dimension passes as `review-pr` (correctness, security, performance, tests, docs, style) but no comment-posting and no remote write. Under `--fix`, applies findings to the working tree but does NOT push; pushing is intentionally a separate, explicit `git push` / `gh` step. Use when the user says "review my changes", "review before I push", "self-review", or implies a pre-PR check. Do NOT use for an existing remote PR (use `review-pr`) or for addressing reviewer comments (use `review-feedback`) or for repo-wide audits (use `audit-repo`).
metadata:
  category: review
  kind: task
  layer: 6
  modes: [auto, interactive, fix]
  needs_meta_info: [info, repos, review]
argument-hint: "[<base-branch>] [--auto] [-i] [--fix] [--scope <path>]"
---

# `review-code-changes` — self-review of local changes

Pre-push self-review. Reviews uncommitted + staged + untracked + branch-vs-baseline diff. Same dimension passes as `review-pr` minus comment-posting. `--fix` applies findings locally; never pushes.

## When to use

- "review my changes" — uncommitted work in the working tree.
- "review before I push" / "self review" — branch is committed but not pushed.
- "look at my diff vs main" — a branch-wide review against an explicit baseline.
- Bare `/adk-review:review-code-changes` from inside a repo — auto-detects baseline and includes everything dirty.

## When NOT to use

- A remote PR exists for this branch → `/adk-review:review-pr`.
- Reviewer comments exist on the PR → `/adk-review:review-feedback`.
- Repo-wide audit (not tied to recent work) → `/adk-review:audit-repo`.
- Doc-only review (markdown / Confluence / GDoc) → `/adk-docs:docs-review`.

## Common prompts (auto-route triggers)

| Prompt pattern | Default flags |
| --- | --- |
| `"review my changes"` | `--auto` |
| `"self review"` | `--auto` |
| `"review before push"` | `--auto` |
| `"look at my diff vs main"` | `--auto` (with `--scope main` if implied) |
| `"review my code and fix the nits"` | `--fix` |
| `"walk through my changes with me"` | `-i` |

## Inputs

| Input | Required | Default |
| --- | --- | --- |
| `<base-branch>` | optional | tracking branch → `origin/<current-branch>` → `main` → `master` (first match wins) |
| `--auto` | optional | yes (default) |
| `-i` / `--interactive` | optional | mutually exclusive with `--auto` |
| `--fix` | optional | off; applies findings to the working tree, no push |
| `--scope <path>` | optional | restrict to a sub-path of the repo |
| `--dimensions <list>` | optional | default all six (correctness, security, performance, tests, docs, style) |

## Workflow

```
Phase 0 — prompt expand
  - Resolve repo (walk up from CWD to .git directory).
  - Resolve baseline per references/baseline-detection.md:
    1. branch's `@{upstream}` (i.e. tracking branch)
    2. `origin/<current-branch>`
    3. `main`
    4. `master`
    5. (--auto fallback) the first parent commit of the current branch
  - Slug from current branch name.
  - Determine mode: review (default) | review+fix | interactive.

Phase 1 — preflight
  - In a git repo. Stop otherwise.
  - For --fix: working tree must be writeable.
  - bin/adk-info repos --check + bin/adk-info review --check.

Phase 2 — gather scope
  - Per references/scope-collection.md:
    - branch-vs-baseline diff (committed work)
    - staged changes (git diff --cached)
    - unstaged changes (git diff)
    - untracked files (git ls-files --others --exclude-standard)
  - Build a unified scope list (file -> kind: branch|staged|unstaged|untracked).
  - Apply --scope <path> filter if provided.

Phase 3 — full-scope review (always)
  - Read each in-scope file in its CURRENT state (post-diff for tracked, full file for untracked).
  - Run dimension passes (parallel, max 4):
    - correctness, security, performance, tests, docs, style
  - For each issue, build a finding card.

Phase 4 — propose
  - Sort findings by severity (Blocker / Critical / Should-Have / May-Have / Nitpick / Question).
  - For -i: walk each, ask accept/edit/discard.
  - For --auto: keep all validated findings.

Phase 5a — report (review-only mode)
  - Write .temp/task-<slug>/review/findings.md.
  - Surface the count by severity + the top issue.

Phase 5b — fix (--fix mode only)
  - Apply each accepted fix to the working tree.
  - Validate via repo-native tests / typecheck / lint.
  - DO NOT push. Surface "ready for `git push` after explicit approval".
  - Write .temp/task-<slug>/review/fix-log.md.

Phase 6 — final report
  - .temp/task-<slug>/report.md
```

See `references/workflow.md` for stage detail and `references/how-it-works.md` for diagrams.

## Persona

> Yourself, a few hours later, with fresh eyes. You're catching what you'll regret pushing. You're not lenient because it's your code; you're STRICTER because nobody else will catch it before the reviewer does. You include the messy stuff — the `console.log` you forgot, the half-typed TODO, the test you skipped to debug something. The reviewer will find them; better you find them first.

See `references/persona.md`.

## Constitution

**Must do:**

1. Include uncommitted + staged + untracked + branch-vs-baseline in scope. All four. Per-source breakdown surfaced in `findings.md`.
2. Pick the baseline by the documented order (`@{upstream}` → `origin/<current-branch>` → `main` → `master` → first parent). Surface the choice in the status banner.
3. Read every changed file in its CURRENT state, not just the diff hunks.
4. Tier every finding by severity per `references/severity-bar.md`.
5. Honor `~/.config/adk/review.md.severity_bar` overrides + `ignore_in_repos` filter.
6. Under `--fix`: validate with repo-native tests / typecheck / lint after applying fixes.
7. Stay local. Never push, never `gh pr` anything, never call any remote write.

**Must not do:**

1. Push under `--fix`. Pushing is intentionally a separate gated step; use
   explicit `git push` / `gh` only after the user asks.
2. Open a PR from this skill.
3. Skip untracked files. New files are usually the most-changed code in the diff.
4. Limit scope to staged changes when the working tree has more.
5. Comment on lines outside the diff scope (drive-by).
6. Re-write the meta-info file (`~/.config/adk/review.md`).

## Anti-patterns

See `references/anti-patterns.md`. Highlights:

- Reviewing only the staged changes when the working tree has more.
- Skipping the baseline diff and only reading the latest commit.
- Skipping untracked files (often the bulk of new work).
- Re-tiering findings down because "it's just my code". The reviewer won't.
- Pushing under `--fix`. The push is intentionally a separate step.

## Output

| Path | Content |
| --- | --- |
| `.temp/task-<slug>/review/findings.md` | All findings, severity-tiered, with evidence + per-source breakdown |
| `.temp/task-<slug>/review/scope.md` | What was in scope (per source) and what was excluded |
| `.temp/task-<slug>/review/fix-log.md` | (`--fix` only) per-finding fix + validation evidence |
| `.temp/task-<slug>/report.md` | Executive summary |

See `references/output-format.md` and `references/artifact-format.md`.

## References shipped with this skill

| File | Purpose |
| --- | --- |
| `references/persona.md` | Future-self-with-fresh-eyes persona + status banner + posture |
| `references/workflow.md` | Detailed Phase 0-6 stage list with checkpoints |
| `references/modes.md` | What `--auto` / `-i` / `--fix` mean here (no push, ever) |
| `references/interaction-contract.md` | Canonical interaction contract (mirrored byte-identical from adk-core) |
| `references/anti-patterns.md` | What NOT to do, with reasons |
| `references/examples.md` | 3-4 worked examples (uncommitted only, branch vs main, --fix flow) |
| `references/output-format.md` | findings.md / scope.md / fix-log.md / report.md shapes |
| `references/artifact-format.md` | `.temp/task-<slug>/review/*` canonical paths |
| `references/validator.md` | Per-phase gates |
| `references/how-it-works.md` | Mermaid: phase flow, scope-source fan-in, --fix loop |
| `references/clarifying-questions.md` | Under -i; defaults under --auto |
| `references/baseline-detection.md` | The exact algorithm for picking the baseline branch |
| `references/scope-collection.md` | How uncommitted + staged + unstaged + untracked are gathered into one scope |
| `references/severity-bar.md` | Same 6-tier rubric as review-pr (honors review.md overrides) |
| `references/dimension-passes.md` | Per-dimension checklists (mirrored from review-pr; same content for self-review) |

## Additional links

- The repo's `AGENTS.md` / `CLAUDE.md` / `.cursorrules` (always; small files; cheap to read).
- The repo's CI config (e.g. `.github/workflows/`, `.gitlab-ci.yml`) — to know which lint / typecheck / test commands the reviewer will run.
- The repo's existing PR template (`.github/pull_request_template.md`) — to surface anything the user will need to fill in when they open the PR (e.g. "test plan", "screenshot").
