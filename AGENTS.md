# AGENTS.md — adk master prompt-handling guide

> **For agents, not humans.** This document is referenced from `~/.claude/CLAUDE.md`, `~/.cursor/rules/_adk.mdc`, `~/.codex/instructions.md`, and `~/.junie/guidelines.md` after `install.sh` runs. It tells the active agent how to interpret any prompt and route it through adk.

---

## 1. Read order on every prompt

1. **`<repo>/.adk/overrides.yaml`** (if working inside a repo with one)
2. **`<repo>/ai-guidelines/`** or **`<repo>/docs/`** (repo-specific conventions)
2a. **`<repo>/MEMORY.md`** and **`<repo>/ERRORS.md`** (if present — project-local decision log + failure log; templates at `shared/templates/`)
3. **`$ADK_CONFIG_HOME/core.json5`** (user identity, org, bot persona, defaults) + **`$ADK_CONFIG_HOME/workspaces.json5`** + **`$ADK_CONFIG_HOME/teams.json5`** + **`$ADK_CONFIG_HOME/repos.json5`** + **`$ADK_CONFIG_HOME/services.json5`** + **`$ADK_CONFIG_HOME/channels.json5`** + **`$ADK_CONFIG_HOME/relations.json5`** (entity graph) + **`$ADK_CONFIG_HOME/connectors/*.json5`** (one per data source)
4. **`<this-repo>/shared/constitution.md`** (universal hard rules)
5. **The triggered skill's `SKILL.md`** (loaded after step 6 routes)
6. **`<this-repo>/shared/model-depth.md`** when the prompt or skill args mention `--detailed`, `--deep`, planning, ambiguous model choice, or large/complex work
7. **`<this-repo>/shared/guidelines/*.md`** — load only the guideline files relevant to the task type identified in step 6 below

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
| "review my PR queue" / "next PR to review" / "drain the queue" / "go through the open PRs" | `/adk-pr-review` with no arg — atomically claims the next eligible row from `$ADK_CONFIG_HOME/pr-queue.json5`. Run in N terminals for parallel review. Refresh the queue beforehand via the shell binary: `adk pr-scan` (walks configured Slack channels — main message + thread replies — and upserts rows). Inspect via `adk pr-queue list / show / ready-to-merge / clean / release`. |
| "re-sync the PR" / "pull fresh comments" / "re-validate without re-indexing" | `adk pr-task sync <url>` then `adk pr-task validate <url>` (or chain via `adk pr-task post <url>`) |
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

_For per-stage re-runs see `skills/adk-pr-review/references/stages.md`._

---

## 3. ADK-only routing and tool ownership

This installation is ADK-only. If the host agent exposes non-ADK skills, plugins, commands, or MCP servers from a marketplace, built-in cache, previous install, or project cache, treat them as unavailable unless the user explicitly asks to bypass ADK for that single invocation.

Rules:

1. Route every task through the `/adk-*` skill table above or the shared ADK guidance files in this repo.
2. Prefer ADK subagents named `adk-agent-*` for delegated work. Do not choose non-ADK agents when an ADK persona exists for the task.
3. Prefer MCP servers configured from `mcp/adk-mcp-*.json`. In Cursor these may appear in the project descriptor cache as `user-adk-mcp-*`; those are the ADK-backed servers. Do not call plugin MCP servers such as `plugin-*` when an ADK MCP covers the same source.
4. If an ADK-required MCP is missing or unhealthy, stop and report the gap. Do not silently fall back to a plugin MCP, browser workflow, or direct API unless the user explicitly approves that fallback.
5. Built-in agent utilities that are not domain skills (for example file editing, shell execution, reading files, browser control, or mode switching) may still be used when they are the host tool surface needed to execute ADK workflows.

---

## 3a. Sub-agent inheritance

When a skill spawns a child agent via the `Agent` tool (e.g. `/adk-pr-review` dispatches a Haiku reranker, `/adk-implement` spawns a focused security pass, `/adk-investigate` fans out a multi-MCP context gather), the child inherits:

- **The constitution (`shared/constitution.md`)** — every hard rule applies; the child cannot waive a parent's constraint.
- **The narration contract (`shared/narration.md`)** — child reports back with a structured summary the parent stitches into its own report.
- **The decision-log obligation** — child logs its forks to the same `$ADK_MEMORY_HOME/learning/decisions.jsonl` under the parent's `skill` + a `sub_flow: child:<name>` discriminator.
- **The shared-state gate (§I.4)** — a child cannot post / merge / push without the human confirmation gate, even when the parent already passed one for a different action.
- **Project-local context** — child reads the same `<repo>/MEMORY.md` / `<repo>/ERRORS.md` / `<repo>/.adk/overrides.yaml` the parent was loaded with.

The child does NOT inherit:
- **The parent's tool list** — children get the smallest tool surface needed for their slice.
- **The parent's scope** — a child must operate inside its named slice; out-of-scope findings are returned to the parent for triage, never acted on by the child directly.

This rule applies whether the child is an adk subagent (`adk-agent-*`) or a freshly spawned `general-purpose` / `Explore` / `Plan` agent.

---

## 4. Every skill, every time: question-first (auto by default; `-i` for interactive)

Every skill walks the question-first contract in `shared/question-first.md`. The **default mode is auto** — the agent picks the recommended default for every fork and proceeds without waiting. Each choice is logged as `auto-defaulted` to `$ADK_MEMORY_HOME/learning/decisions.jsonl` AND narrated live so the user can stop / correct.

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

Every non-trivial fork — every question asked, every default picked, every override, every approach chosen — gets one JSONL line appended to `$ADK_MEMORY_HOME/learning/decisions.jsonl`. Schema in `shared/decision-log-schema.md`. These are the substrate for `/adk-improve`.

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
| **Global** (`/adk-pr-review`, `/adk-investigate`, `/adk-sync` on a remote-only doc, `/adk-setup`, `/adk-improve`, `/adk-explain`) | `$ADK_DATA_HOME/<area>/<task>/` |

A global skill can be invoked from anywhere — your cwd is irrelevant to what it does. A repo-bound skill must be invoked from inside a repo (or with `--repo <path>`).

Special folders under `$ADK_DATA_HOME/`:

- `repos/<repo-name>/` — checkouts owned by adk; used as the base for PR-review worktrees.
- `pr-reviews/<repo>_pr-<n>/` — one folder per PR being reviewed; contains a worktree, the diff, the embeddings, supporting docs, findings, report.
- `investigations/<task>/`, `reviews/<task>/`, `sync/<task>/`, `setup/<ts>/`, `improve/<ts>/`, `explain/<ts>/`.

Project-scoped extensions (still respected):

- `<dir>/.adk/overrides.yaml` extends/narrows the config bundle at runtime. Skills merge these at runtime.
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
- Model depth: `shared/model-depth.md`
- Personas: `shared/personas/*.md`
- Workflows: `shared/workflows/*.md`
- Input classifiers: `shared/input-classifiers/*.md`
- Generic guidelines (frontend, api, security, …): `shared/guidelines/*.md`
- Skills: `skills/adk-*/SKILL.md`
- MCP configs: `mcp/adk-mcp-*.json`
- User config: `$ADK_CONFIG_HOME/` (core.json5 + workspaces.json5 + teams.json5 + repos.json5 + services.json5 + channels.json5 + relations.json5 + connectors/*.json5 + adk-cli.json5 + pr-queue.json5)
- Learning state: `$ADK_MEMORY_HOME/learning/`
- Metadata cache: `$ADK_DATA_HOME/metadata/`
