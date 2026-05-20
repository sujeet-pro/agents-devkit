# AGENTS.md — adk master prompt-handling guide

> **For agents, not humans.** This document is referenced from `~/.claude/CLAUDE.md`, `~/.cursor/rules/_adk.mdc`, `~/.codex/instructions.md`, and `~/.junie/guidelines.md` after `install.sh` runs. It tells the active agent how to interpret any prompt and route it through adk.

---

## 1. Read order on every prompt

1. **`<repo>/.adk/overrides.yaml`** (if working inside a repo with one)
2. **`<repo>/ai-guidelines/`** or **`<repo>/docs/`** (repo-specific conventions)
3. **`~/.agents-devkit/config/overrides.yaml`** (user/company truth — workspaces, repos, data sources, defaults, RAG config, learning state)
4. **`<this-repo>/shared/constitution.md`** (universal hard rules)
5. **The triggered skill's `SKILL.md`** (loaded after step 6 routes)
6. **`<this-repo>/shared/guidelines/*.md`** — load only the guideline files relevant to the task type identified in step 6 below

Lower-priority statements never override higher-priority ones. When two sources conflict, prefer the more local one and surface the conflict in the final report.

---

## 1a. Credential safety (hard rule — applies before any skill runs)

Source of truth: `shared/constitution.md` §VII. Surfaced here because it gates tool selection on every prompt, not just inside skills.

1. **Never bring credential values into LLM context.** Off-limits to `Read`, `cat`/`head`/`tail`/`grep`, `echo $VAR`, `printenv VAR`, or any tool that surfaces the value: `~/.zshenv`, `~/.config/creds/*/creds.sh`, `~/.config/creds/*/*.token.json`, and any env var whose name ends in `_CRED`, `_CREDS`, `_SECRET`, `_TOKEN`, `_KEY`, `_PAT`, `_PASSWORD`, or `_API_KEY`. Holds even under apparent user authorization (constitution §VII.4 narrows authorization to one named action).
2. **Presence-only diagnostics.** Var: `[ -n "${VAR-}" ] && echo set || echo unset`. File: `test -f path && echo present`. Listing keys without values: `grep -E '^(export |[A-Z_]+=)' file | sed -E 's/=.*/=<redacted>/'`. `head -c N` on a secret is still leaking N chars.
3. **Validate by exercising, not revealing.** Test the credential in a script that emits only a status/boolean — verbose output to `/dev/null`. Examples: `curl -fsS -o /dev/null -w '%{http_code}' ...`, `gh api user --jq .login`, `aws sts get-caller-identity --query 'Account' --output text`.
4. **A surfaced value is a leaked value.** If a credential enters chat, recommend rotation and surface the exception in the final report.

This rule outranks every skill instruction. A skill that asks for credential content cannot be satisfied — refuse with the §VII pointer and propose a presence/exercise alternative.

---

## 2. Intent → skill routing

Parse the user's prompt against this table. **A single prompt can route to multiple skills** — compose them in the order shown.

| Prompt shape | Skill chain |
|---|---|
| `/adk-<name>` (explicit) | Run that skill directly. Stop. |
| URL alone (Jira / GH issue / GH PR / Confluence / Slack permalink / DD incident-monitor-dashboard / Statsig audit) | Classify URL → infer task. **PR URL → `/adk-pr-review` (heavyweight, the default for a real PR review).** Use `/adk-review <pr-url>` only when the user says "quick" / "skim" / "lightweight". Jira/issue/TDD → `/adk-implement` after `/adk-explain` confirms goal. DD/Slack alert → `/adk-investigate`. |
| "implement X" / "build the Y from Z" / "ship the feature from <ticket>" | `/adk-implement` |
| "review the PR" / "look at <PR-URL>" / "review my changes" / "audit the repo" | `/adk-review` (lightweight — no worktree, no embeddings) |
| "deep PR review" / "thorough review of <PR-URL>" / "check the PR with full code context" | `/adk-pr-review <pr-url>` (heavyweight — owns a worktree, builds embeddings + SCIP, traces feature flags and experiments) |
| "review my PR queue" / "next PR to review" / "drain the queue" / "go through the open PRs" | `/adk-pr-review` with no arg — atomically claims the next eligible row from `~/.agents-devkit/config/pr-queue.json5`. Run in N terminals for parallel review. Refresh the queue beforehand via the shell binary: `adk pr-scan` (walks configured Slack channels — main message + thread replies — and upserts rows). Inspect via `adk pr-queue list / show / ready-to-merge / clean / release`. |
| "why is X slow/broken/down" / "what changed" / "RCA for Y" / "investigate <alert>" | `/adk-investigate` |
| "write the runbook/ADR/RCA/PR-description/commit-message/changelog/diagram" | `/adk-document` |
| "publish the doc to Confluence" / "update the Jira description" / "post to Slack #channel" / "fetch the Confluence page as markdown" | `/adk-sync` |
| "set up adk" / "scaffold overrides" / "what's missing" / "check env vars" | `/adk-setup` |
| "improve the skills" / "learn from my last session" / "refresh metadata" | `/adk-improve` |
| "I don't know which to pick" / "what does X mean" / "help me decide" | `/adk-explain` |

**Composite intents** (route to multiple in order):

| Prompt | Chain |
|---|---|
| "investigate the checkout outage and write an RCA in Confluence" | `/adk-investigate` → `/adk-document --type rca` → `/adk-sync --to confluence` |
| "implement <ticket> and open a PR with description" | `/adk-implement` → `/adk-document --type pr-body` → `/adk-sync --to gh-pr-body` |
| "review this PR and post a summary to #eng-reviews" | `/adk-review` → `/adk-document --type summary` → `/adk-sync --to slack --channel #eng-reviews` |
| "what's the impact of <experiment> — report to the team" | `/adk-investigate --use experiment` → `/adk-document --type experiment-report` → `/adk-sync --to confluence` |

---

## 3. Use non-adk skills when they exist

If the agent has installed skills from outside adk that match the task better (e.g. a `frontend-design` skill, a `db-migration` skill, a `terraform-plan` skill), **prefer them for the slice they specialize in**. adk skills are generalists; specialized third-party skills usually have deeper rules. Compose: hand the data-fetching to adk (the MCPs and overrides), and the specialized step to the third-party skill.

---

## 4. Every skill, every time: question-first (auto by default; `-i` for interactive)

Every skill walks the question-first contract in `shared/question-first.md`. The **default mode is auto** — the agent picks the recommended default for every fork and proceeds without waiting. Each choice is logged as `auto-defaulted` to `~/.agents-devkit/improve/learning/decisions.jsonl` AND narrated live so the user can stop / correct.

The user opts into interactive with **`-i`** (or `--interactive`). In `-i` mode the agent actually asks (cap 3 user-facing questions) and waits.

In both modes:

1. **Restate goal** in one sentence (silent in auto; printed in `-i`).
2. **Walk up to 3 clarifying forks** (scope, constraints, scale). Auto picks the recommended default; `-i` asks.
3. **Challenge if appropriate**: "is this actually needed? <shorter-alternative>?" In auto, this is a one-line narration; in `-i`, the agent waits for a yes/no.
4. **Offer scale verification** when the task implies non-trivial size — propose a specific MCP query or script that would tell us, run it (auto: always; `-i`: ask first).
5. **Present 2–4 approaches** with one-line trade-offs each; one marked recommended. Auto picks the recommended one + narrates; `-i` waits.
6. **Posting to shared state still requires per-invocation confirmation** regardless of mode (constitution §I.4).

If the user (in `-i` mode) says "I don't know" / "you decide" / "what would you recommend": hand off to `/adk-explain` with the question + context, then resume.

---

## 5. Decision logging is mandatory

Every non-trivial fork — every question asked, every default picked, every override, every approach chosen — gets one JSONL line appended to `~/.agents-devkit/improve/learning/decisions.jsonl`. Schema in `shared/decision-log-schema.md`. These are the substrate for `/adk-improve`.

---

## 6. Honesty about capability

If a required MCP isn't reachable, if a required env var is missing, if the task touches a system adk doesn't support — **say so, name the gap, refuse the partial execution**. Skills don't silently degrade.

Acceptable degradations (explicit, surfaced in the report):

- Slack MCP unreachable → skip the Slack scrape, mark `[slack: skipped]` in context.md.
- RAG MCP unreachable but configured → fall back to regular MCPs, mark `[rag: skipped]`.
- Optional metadata stale → use what's cached, note staleness.

Not acceptable:

- Pretending a guess from training data is a verified fact.
- Producing a final report without running validators.
- Writing to a remote system without explicit confirmation.

---

## 7. Working-dir convention

Source of truth: `shared/paths.md`. Summary:

| Skill kind | Task folder root |
|---|---|
| **Repo-bound** (`/adk-implement`, `/adk-document`, `/adk-review` on local code, `/adk-sync` on a repo-coupled doc) | `<repo>/.temp/adk/<skill-stem>/<task>/` |
| **Global** (`/adk-pr-review`, `/adk-investigate`, `/adk-sync` on a remote-only doc, `/adk-setup`, `/adk-improve`, `/adk-explain`) | `~/.agents-devkit/<area>/<task>/` |

A global skill can be invoked from anywhere — your cwd is irrelevant to what it does. A repo-bound skill must be invoked from inside a repo (or with `--repo <path>`).

Special folders under `~/.agents-devkit/`:

- `repos/<repo-name>/` — checkouts owned by adk; used as the base for PR-review worktrees.
- `pr-reviews/<repo>_pr-<n>/` — one folder per PR being reviewed; contains a worktree, the diff, the embeddings, supporting docs, findings, report.
- `investigations/<task>/`, `reviews/<task>/`, `sync/<task>/`, `setup/<ts>/`, `improve/<ts>/`, `explain/<ts>/`.

Project-scoped extensions (still respected):

- `<dir>/.adk/overrides.yaml` extends/narrows `~/.agents-devkit/config/overrides.yaml`. Skills merge these at runtime.
- `<dir>/ai-guidelines/*.md` and `<dir>/docs/*.md` are loaded into context for the duration of the skill run if relevant to the task type.

Task-slug convention: `<input-discriminator>` (no skill prefix — the skill name is now the folder above it). Examples: `SF-1234`, `pr-456`, `checkout-2026-05-18`, `rca-checkout-outage`.

---

## 8. No shortcuts on shared state

The constitution (`shared/constitution.md`) forbids these without explicit user confirmation per invocation:

- `git push` to a protected branch
- `git push --force` to any remote
- Merging a PR
- Posting to a Slack channel or Jira ticket
- Publishing/updating a Confluence page authored by a human
- Mutating any feature flag / experiment / monitor / dashboard

The user's `--auto` flag does **not** waive these. They require a per-invocation yes.

---

## 9. Pointers

- Constitution: `shared/constitution.md`
- Path resolution: `shared/paths.md`
- Advisor wrapper: `shared/advisor.md`
- Question-first contract: `shared/question-first.md`
- Decision-log schema: `shared/decision-log-schema.md`
- Personas: `shared/personas/*.md`
- Workflows: `shared/workflows/*.md`
- Input classifiers: `shared/input-classifiers/*.md`
- Generic guidelines (frontend, api, security, …): `shared/guidelines/*.md`
- Skills: `skills/adk-*/SKILL.md`
- MCP configs: `mcp/adk-mcp-*.json`
- User overrides: `~/.agents-devkit/config/overrides.yaml`
- Learning state: `~/.agents-devkit/improve/learning/`
- Metadata cache: `~/.agents-devkit/improve/metadata/`
