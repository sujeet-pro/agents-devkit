# AGENTS.md — adk master prompt-handling guide

> **For agents, not humans.** This document is referenced from `~/.claude/CLAUDE.md`, `~/.cursor/rules/_adk.mdc`, `~/.codex/instructions.md`, and `~/.junie/guidelines.md` after `install.sh` runs. It tells the active agent how to interpret any prompt and route it through adk.

---

## 1. Read order on every prompt

1. **`<repo>/.adk/overrides.yaml`** (if working inside a repo with one)
2. **`<repo>/ai-guidelines/`** or **`<repo>/docs/`** (repo-specific conventions)
3. **`~/.config/adk/overrides.yaml`** (user/company truth — workspaces, repos, data sources, defaults, RAG config, learning state)
4. **`<this-repo>/shared/constitution.md`** (universal hard rules)
5. **The triggered skill's `SKILL.md`** (loaded after step 6 routes)
6. **`<this-repo>/shared/guidelines/*.md`** — load only the guideline files relevant to the task type identified in step 6 below

Lower-priority statements never override higher-priority ones. When two sources conflict, prefer the more local one and surface the conflict in the final report.

---

## 2. Intent → skill routing

Parse the user's prompt against this table. **A single prompt can route to multiple skills** — compose them in the order shown.

| Prompt shape | Skill chain |
|---|---|
| `/adk-<name>` (explicit) | Run that skill directly. Stop. |
| URL alone (Jira / GH issue / GH PR / Confluence / Slack permalink / DD incident-monitor-dashboard / Statsig audit) | Classify URL → infer task. PR URL → `/adk-review`. Jira/issue/TDD → `/adk-implement` after `/adk-explain` confirms goal. DD/Slack alert → `/adk-investigate`. |
| "implement X" / "build the Y from Z" / "ship the feature from <ticket>" | `/adk-implement` |
| "review the PR" / "look at <PR-URL>" / "review my changes" / "audit the repo" | `/adk-review` |
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

## 4. Every skill, every time: question-first

No skill executes without going through the question-first contract in `shared/question-first.md`. Even under `--auto`, the agent **records** the questions it would have asked and the defaults it picked, into the decision log (`~/.config/adk/learning/decisions.jsonl`). User-answered questions are the highest-quality training signal.

Steps:

1. **Restate goal** in one sentence; confirm with user (or proceed if `--auto`).
2. **Ask up to 3 clarifying questions** (scope, constraints, scale).
3. **Challenge if appropriate**: "is this actually needed?" / "is there a smaller version that works?"
4. **Offer scale verification** when the task implies non-trivial size — propose a specific MCP query or script that would tell us, and run it on confirm.
5. **Present 2–4 approaches** with one-line trade-offs each.
6. **Wait for choice OR proceed with default** (only if overrides.yaml allows silent default for this skill).

If the user says "I don't know" / "you decide" / "what would you recommend": hand off to `/adk-explain` with the question + context, then resume.

---

## 5. Decision logging is mandatory

Every non-trivial fork — every question asked, every default picked, every override, every approach chosen — gets one JSONL line appended to `~/.config/adk/learning/decisions.jsonl`. Schema in `shared/decision-log-schema.md`. These are the substrate for `/adk-improve`.

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

## 7. Project-scoped overrides

When working inside a directory:

- `<dir>/.adk/overrides.yaml` extends/narrows `~/.config/adk/overrides.yaml`. Skills merge these at runtime.
- `<dir>/ai-guidelines/*.md` and `<dir>/docs/*.md` are loaded into context for the duration of the skill run if relevant to the task type.
- `<dir>/.temp/<task-slug>/` is the working dir. Every artifact a skill creates goes here. The folder is gitignored; the user can inspect it after the run.

Task-slug convention: `<skill-name-stem>-<input-discriminator>`, e.g. `implement-SF-1234`, `review-pr-456`, `investigate-checkout-2026-05-18`, `rca-checkout-outage`.

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
- Advisor wrapper: `shared/advisor.md`
- Question-first contract: `shared/question-first.md`
- Decision-log schema: `shared/decision-log-schema.md`
- Personas: `shared/personas/*.md`
- Workflows: `shared/workflows/*.md`
- Input classifiers: `shared/input-classifiers/*.md`
- Generic guidelines (frontend, api, security, …): `shared/guidelines/*.md`
- Skills: `skills/adk-*/SKILL.md`
- MCP configs: `mcp/adk-mcp-*.json`
- User overrides: `~/.config/adk/overrides.yaml`
- Learning state: `~/.config/adk/learning/`
- Metadata cache: `~/.config/adk/metadata/`
