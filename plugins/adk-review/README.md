# adk-review

> Code review for self and others. Six skills covering remote PR review, local working-tree self-review, addressing existing PR feedback, capturing session handoff, and quick / whole-repo audits. Ships the GitHub MCP (Docker, read-only by default) with `gh` CLI as the equally-supported fallback.

## What it ships


| Component           | What                                                                                              |
| ------------------- | ------------------------------------------------------------------------------------------------- |
| **Skills (6)**      | `review-pr`, `review-code-changes`, `review-feedback`, `review-handoff`, `audit-pr`, `audit-repo` |
| **Agents (2)**      | `code-reviewer`, `security-reviewer`                                                              |
| **MCP servers (1)** | `github` (Docker, pinned `v1.0.3`, read-only by default; `gh` CLI fallback)                       |
| **Hard deps**       | `adk-core`                                                                                        |


All review skills follow the universal `--auto / -i / --fix` mode contract documented in `/adk-core:mode-contract` and the canonical interaction contract mirrored in every skill's `references/interaction-contract.md`.

## Skills

### `review-pr` — review a remote PR (the flagship)

Review a remote PR (your own or a peer's). Performs a fresh full-scope review every run (not just delta-since-last-review), reconciles against existing inline comments / replies / resolved tasks, and posts validated non-duplicate findings to the PR. Ownership-aware: detects `author.login` vs the local git identity and switches between *review-and-post* (peer's PR) and *validate-and-reply* (your PR). Under `--fix`, applies accepted feedback locally, validates with the repo's tests / typecheck / lint, and pushes (NEVER merges, NEVER force-pushes to protected branches).

```text
/adk-review:review-pr <pr-url-or-number>            # default --auto: post validated findings
/adk-review:review-pr <pr-url> -i                   # walk each finding interactively
/adk-review:review-pr <pr-url> --fix                # apply accepted feedback + push (asks first)
/adk-review:review-pr <pr-url> --auto --fix         # both; never merges, never force-pushes
```

### `review-code-changes` — self-review of LOCAL changes

Review your own working tree (uncommitted + staged + untracked) plus the branch-vs-baseline diff. Picks up the baseline automatically: tracking branch → `origin/<current-branch>` → `main`/`master`. Same dimension passes as `review-pr` minus comment-posting. `--fix` applies findings locally; never pushes.

```text
/adk-review:review-code-changes                     # default --auto: report findings
/adk-review:review-code-changes -i                  # walk each interactively
/adk-review:review-code-changes --fix               # apply findings locally; no push
/adk-review:review-code-changes main                # explicit baseline branch
```

### `review-feedback` — address existing reviewer comments

Triage existing reviewer comments on a PR and apply each as code changes with traceable per-comment replies (commit SHA + one-line summary). Different from `review-pr --fix`: this skill ASSUMES the comments are already valid feedback and does NOT re-perform a full review.

```text
/adk-review:review-feedback <pr-url>                # default --auto: classify + draft replies
/adk-review:review-feedback <pr-url> --fix          # apply accepted, push, post replies (asks first)
```

### `review-handoff` — session handoff document

Capture a structured session-handoff document so a paused or transferred task can resume without information loss. Read-only: never posts publicly without explicit opt-in.

```text
/adk-review:review-handoff                          # auto-detects current task slug
/adk-review:review-handoff <task-slug> -i           # walk through sections interactively
```

### `audit-pr` — fast pre-merge sanity audit

Fixed-set parallel audit on a single PR diff (NOT a deep review). Runs lint-clean, typecheck, tests-added vs LOC heuristic, secrets-in-diff, license headers, dependency licenses, accessibility / perf / bundle-size regressions where relevant, and doc-updated-for-behavior-change. Pass / Warn / Fail per check. `--fix` only auto-fixes the safely-fixable subset (lint, license headers, docs TOC).

```text
/adk-review:audit-pr <pr-url>                       # default --auto: parallel checks
/adk-review:audit-pr <pr-url> --checks lint,tests   # subset
/adk-review:audit-pr <pr-url> --fix                 # auto-fix the safe subset
```

### `audit-repo` — whole-repo multi-dimensional audit

Repo-wide audit across security / performance / quality / dependencies / test coverage / architecture. Read-only: produces a single severity-tiered report with file-anchored evidence. Top-10 findings; explicitly includes "what's healthy" alongside problems.

```text
/adk-review:audit-repo .                            # current repo
/adk-review:audit-repo ~/code/acme/checkout-api     # explicit path
/adk-review:audit-repo . --dimensions security,deps # subset
/adk-review:audit-repo . --scope src/auth/          # focused scope
```

## Agents


| Agent               | Persona                                                          | Used by                                                                         |
| ------------------- | ---------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| `code-reviewer`     | Findings-first. Severity-tiered. Quote evidence. Never bikeshed. | `review-pr`, `review-code-changes`, `review-feedback`, `audit-pr`, `audit-repo` |
| `security-reviewer` | Adversarial. Threat-modeled. Boundary-aware. Never theatrical.   | `review-pr` (security pass), `audit-pr`, `audit-repo`, `code-security`          |


Agents are kept thin — they hold persona + hard rules, not workflow logic. The skill orchestrates; the agent specializes.

## GitHub MCP

`adk-review` ships a single MCP — `github` — via Docker (`ghcr.io/github/github-mcp-server` pinned to `v1.0.3`).


| Setting            | Default                                            | Notes                                                                                                                                                                                |
| ------------------ | -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `GITHUB_PAT`       | unset                                              | Required; fine-grained PAT with `Contents: Read`, `Pull Requests: Read+Write`, `Issues: Read+Write`, `Actions: Read`, `Metadata: Read`, `read:org`, `read:project`, `notifications`. |
| `GITHUB_TOOLSETS`  | `context,repos,issues,pull_requests,actions,users` | Deliberately omits `code_security`, `dependabot`, `gists`, `discussions`, `secret_protection`. Skills that need these set the env explicitly.                                        |
| `GITHUB_READ_ONLY` | `1`                                                | Skills that post (`review-pr`, `review-feedback`, `audit-pr` postback) flip to `0` for the post stage only, then back to `1`.                                                        |


**Fallback (equal priority):** every skill that uses the GitHub MCP also supports `gh` CLI for the same operations. Phase 1 preflight prefers `gh` if both Docker and `gh` are available (faster cold start, no Docker daemon required).

See `plan/02-mcp-servers.md §2.1` for the canonical block, env-var setup, and verifier curl commands.

## Composition with `/adk-core:auto`

`/adk-core:auto` (the marketplace dispatcher) routes to the right `adk-review` skill automatically. Common patterns it picks up:


| Prompt the user types                                     | Routed to                                                            | Default mode |
| --------------------------------------------------------- | -------------------------------------------------------------------- | ------------ |
| Bare GitHub PR URL                                        | `/adk-review:review-pr`                                              | `--auto`     |
| `"review PR <url>"` / `"look at #N"`                      | `/adk-review:review-pr`                                              | `--auto`     |
| `"fix the review comments"` / `"address the PR feedback"` | `/adk-review:review-pr --fix` or `/adk-review:review-feedback --fix` | `--fix`      |
| `"review my changes"` / `"self review"` / `"before push"` | `/adk-review:review-code-changes`                                    | `--auto`     |
| `"draft a handoff"` / `"session pause"`                   | `/adk-review:review-handoff`                                         | `--auto`     |
| `"sanity check this PR"`                                  | `/adk-review:audit-pr`                                               | `--auto`     |
| `"audit the repo"` / `"security posture of X"`            | `/adk-review:audit-repo`                                             | `--auto`     |


Inside `/adk-core:auto`'s Phase 4 dispatch, review skills frequently follow code skills (e.g. `code-bugfix` → `review-code-changes`) or precede publish steps (e.g. `review-pr --fix` → push → notify). The dispatcher sequences these through `agents/dispatcher.md` (in `adk-core`).

## Meta-info consumed

Every `adk-review` skill reads from `~/.config/adk/`:


| File        | Used for                                                                                                                         |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `info.md`   | Operator name + email (used to detect `author.login` ownership and to sign comment replies)                                      |
| `repos.md`  | Resolve a PR URL → local repo checkout path; pick the right base branch                                                          |
| `github.md` | Default reviewers, PR template path, CODEOWNERS conventions, `forbid_force_push_branches`, label conventions                     |
| `review.md` | Severity bar overrides, comment template overrides, "ignore these checks for this repo" lists, `auto_post_comments_to_pr` toggle |


If any required field is missing, the skill stops with a copy-pastable suggestion — never auto-edits the meta-info file. See `/adk-core:setup --target review` to populate `review.md`.

## Hard mode rules (universal)

These apply across every `adk-review` skill, regardless of `--auto / -i / --fix`:

1. **Never auto-merge a PR.** Even under `--auto --fix`. Approval can be granted; merge is the author's call.
2. **Never force-push to `main` / `master` / `develop`** or any branch listed in `~/.config/adk/github.md.forbid_force_push_branches`.
3. **Push always asks before the first push of a session.** Even under `--auto --fix`.
4. **Comment-post is a shared-state action** — same rule as push.
5. **Post-confirmation re-fetch is mandatory** after every batch comment-post (`review-pr` only). Wait 5s, re-fetch, confirm IDs reappear; retry at 10s and 20s on miss; never re-post on a miss (creates duplicates).

## Installation

```text
/plugin install adk-review@adk
/reload-plugins

export GITHUB_PAT="<fine-grained-PAT>"
gh auth login

/adk-core:setup --target github
/adk-core:setup --target review
```

`adk-core` is auto-installed as a dependency.

## Repo layout

```
adk-review/
├── .claude-plugin/plugin.json
├── README.md
├── .mcp.json
├── agents/
│   ├── code-reviewer.md
│   └── security-reviewer.md
└── skills/
    ├── review-pr/{SKILL.md, references/*.md}
    ├── review-code-changes/{SKILL.md, references/*.md}
    ├── review-feedback/{SKILL.md, references/*.md}
    ├── review-handoff/{SKILL.md, references/*.md}
    ├── audit-pr/{SKILL.md, references/*.md}
    └── audit-repo/{SKILL.md, references/*.md}
```

