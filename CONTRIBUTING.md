# Contributing to ADK

ADK is a single npm package + Node CLI installer. There is no Python tooling, no `ai-guidelines/` source-of-truth, no `agent-personas/` projection, and no `prj-*` skills in this repo. Everything below assumes a Node 18+ environment.

## Quick start

```bash
git clone https://github.com/sujeet-pro/agents-devkit.git
cd agents-devkit
npm install
npm run validate            # lints skill / agent / hook structure
npm run skills:manifest     # regenerates skills-manifest.json
npm run setup:dry           # preview what the installer would do
npm run docs:build          # build gh-pages/ from docs/
```

## Repository layout

| Path | Contents |
| --- | --- |
| `skills/adk-*` | 39 public, self-contained skills (`SKILL.md` + flat `references/`) |
| `agents-claude/*.md` | Claude custom subagent sources (Markdown + YAML frontmatter) |
| `agents-cursor/*.md` | Cursor custom subagent sources (Markdown + Cursor frontmatter) |
| `agents-codex/*.toml` | Codex custom agent sources (TOML) |
| `hooks/{claude,cursor,codex}.json` | Per-runtime hook configs |
| `mcp-config/servers/<server>.json` | One JSON per MCP server with `${ENV_VAR}` placeholders |
| `global-prompts/*.md` | Always-on prompts injected into runtime memory files |
| `workflows/*.yaml` | Composable multi-skill pipelines |
| `cli/` | The Node installer (`adk-install`) — pure ESM, no Python |
| `docs/`, `gh-pages/` | Pagesmith docs source + built site |

There are **no** shared-source folders. A skill's `references/` is flat: every supporting file lives next to the `SKILL.md` and is the canonical text for that skill. Reference filenames are **task-prefixed** by the skill's task token (e.g., `pr-reviewer-persona.md` and `pr-review-validator.md` for `adk-review-pr`; `feature-persona.md` and `feature-validator.md` for `adk-build-feature`). The single exception is `interaction-contract.md`, which is the global propagated copy and keeps its generic name in every skill.

## Hard rules for skills

- Skill folder names must match `^adk(-[a-z0-9]+)*$`.
- Every `SKILL.md` has YAML frontmatter with `name` and `description`. Optional keys: `compatibility`, `metadata`, `license`, `allowed-tools`. Anything else fails validation.
- `frontmatter.name` must equal the folder name.
- `description` ≤ 1024 chars.
- Body soft cap is 500 lines (warning above that).
- `references/` is flat; no subdirectories; no `_shared/`.
- Every `references/<file>` cited in `SKILL.md` must exist on disk (validation walks the body for `references/<file>` patterns).
- The skill must accept `--auto`. Even routers that mostly hand off should mention `--auto` so the contract is visible.
- The skill must include `references/interaction-contract.md` (the default-ask-with-explained-options + `--auto` contract). Updating the master copy in `global-prompts/interaction-contract.md` is the source of truth — propagate to skill references with a quick `cp` or via a maintenance script in `.temp/scripts/`.

## Adding or updating a skill

1. Create `skills/adk-<name>/` with `SKILL.md` and `references/`. Decide the **task token** — the suffix after `adk-` (e.g., `feature` for `adk-build-feature`, `pr` for `adk-review-pr`, `audit-repo` for `adk-audit-repo`). Every reference filename in this skill (except `interaction-contract.md`) carries this token as a prefix.
2. Author the `SKILL.md`: `When to use`, `When NOT to use`, `Inputs` (mark `--auto` row), `Workflow` (numbered phases with explicit "Approval gate unless `--auto`" calls AND an explicit `Validate (per <task>-validator.md)` step before the final report), `Output format`, `Anti-patterns`, plus the managed `<!-- adk:references:start --> ... <!-- adk:references:end -->` block listing every reference file.
3. Author the **standard skill-specific reference set** (every reference except `interaction-contract.md` MUST carry skill-specific content — no generic templates). All filenames task-prefixed:
   - `<task>-persona.md` — role, mission, focus areas, hard rules, status reporting banner. The hard rules are the source of truth for the constitution's skill-specific section.
   - `<task>-constitution.md` (or `<task>-standards.md` for review-style skills) — shared ADK baseline + skill-specific non-negotiables.
   - `interaction-contract.md` — the global default-ask + `--auto` contract. Identical across all skills; copy from `global-prompts/interaction-contract.md`. **This file is NOT renamed.**
   - `<task>-clarifying-questions.md` — the questions this skill asks in default-ask mode, each with a how-to-pick rubric.
   - `<task>-output-format.md` — default vs detailed report shape, status banner, severity ladder where applicable.
   - `<task>-artifact-format.md` — the deliverable's format and where it lives plus the `.temp/` path matrix.
   - `<task>-anti-patterns.md` — skill-specific anti-patterns.
   - `<task>-validator.md` — the four-phase validator gate (pre-execution, mid-flow, pre-handoff/pre-publish, post-execution) the skill MUST run. **Required for every skill.**
4. Add **task-specific** references when relevant (also task-prefixed):
   - `<task>-research-protocol.md` for any skill that consults primary sources.
   - `<task>-multi-repo.md` for skills that benefit from cross-repo context.
   - `<task>-examples.md`, `<task>-mcp-fallback.md`, `<task>-review-comment-format.md`, etc.
   - For review-style skills (PR review, doc review, audit): `<task>-comment-format.md`, `<task>-reply-templates.md`, `<task>-comment-reconciliation.md`, `<task>-postback-protocol.md` — the bold-label canonical comment shape (see `skills/adk-review-pr/references/pr-review-comment-format.md` for the reference implementation).
   - For frontend skills: `<task>-design-system-master.md`, `<task>-pre-delivery-checklist.md`, `<task>-industry-anti-patterns.md`.
5. Run `npm run validate && npm run validate:content` and fix any error.
6. Run `npm run skills:manifest` so `skills-manifest.json` reflects the new entry.
7. Update the catalog tables in `README.md`, `AGENTS.md`, `REFERENCE.md`, and `llms.txt` (skill count, category table, intent → task mapping).
8. Run `npm run docs:build` to confirm the docs site still renders.

## Adding or updating a custom subagent

Each provider's agent file is independent. Authoring a new agent named `adk-<name>`:

1. Write `agents-claude/adk-<name>.md` (Markdown + YAML frontmatter — at least `name` and `description`).
2. Write `agents-cursor/adk-<name>.md` (Cursor-shaped frontmatter).
3. Write `agents-codex/adk-<name>.toml` (TOML keys: `name`, `description`, `model`, `developer_instructions`).
4. Run `npm run validate`.

Lists may differ per provider — there is no shared persona source. If an agent only makes sense for one runtime, ship it for that runtime only.

## Adding or updating a hook

1. Edit the relevant `hooks/{claude,cursor,codex}.json` file directly.
2. Run `npm run validate` (parses each hook file as JSON).
3. Codex hooks require `[features] codex_hooks = true` in `~/.codex/config.toml` to be active on a user's machine.

## Adding or updating an MCP server

1. Add `mcp-config/servers/<server>.json` with `${ENV_VAR}` placeholders for any required secrets.
2. Include a `description` and a one-line "how to get this" string for each env var so the installer can prompt with helpful context.
3. Run `npm run validate` then `npm run setup:dry` to confirm the installer surfaces the new server in the multiselect.

## Adding or updating a global prompt

1. Drop `global-prompts/<topic>.md` (short, declarative, runtime-agnostic).
2. Re-running `adk-install` rewrites the `<!-- adk:global-prompts:start/end -->` block in every selected runtime's memory file.

When you change `global-prompts/interaction-contract.md`, also propagate it to `skills/*/references/interaction-contract.md` so the in-skill copy stays in sync.

## Workflow files

Workflows in `workflows/*.yaml` chain skills. They are optional convenience presets — keep them up to date with the current skill catalog (e.g. don't reference deleted skills).

## Validation commands

```bash
npm run validate            # validates SKILL.md frontmatter, agent shape, hook JSON
npm run validate:content    # stricter: code-fence balance, link integrity, fence-aware heading + link checks
npm run validate:all        # both of the above
npm run skills:manifest     # regenerate skills-manifest.json from skills/
npm run docs:skills         # regenerate docs/reference/skill-*.md mirrors from each SKILL.md (run before docs:build; included in docs:build)
npm run docs:build          # docs:skills + pagesmith-docs build
npm run setup:dry           # interactive installer plan, no writes
```

## Release checklist

1. `npm run validate:all` — must be `0 error(s), 0 warning(s)`.
2. `npm run skills:manifest` — commit the regenerated manifest.
3. `npm run docs:build` — runs `docs:skills` first so the `docs/reference/skill-*.md` mirrors are in sync; commit `gh-pages/`.
4. `npm run setup:dry` from a temp dir against both a global and a project install — confirm the plan summary lists every skill, agent, hook, and MCP server.
5. Bump `package.json` `version`. Update the skill count anywhere it changed.
6. `git tag v<version> && git push --tags`.
7. `npm publish`.

## What this repo deliberately does NOT have

- No Python anywhere. The old `tests/test_*.py`, `scripts/generate_*.py`, `ai-guidelines/scripts/refresh_adk_skills.py`, and `scripts/sync-links.sh` have all been removed in favor of the Node CLI.
- No `ai-guidelines/` source-of-truth folder. Each skill carries its own copy of the persona, constitution, output format, and interaction contract.
- No `agent-personas/` projection. Each provider's agent file is hand-authored.
- No `prj-*` contributor skills installed at this repo's root. The `prj-doc-site-*` files referenced by `adk-doc-site-setup` only live as `references/` inside that skill — they are written into a *consumer* project when the skill runs.
- No Bash install script. The CLI is the only install path.

If you find a doc that mentions any of the above, it's stale — please fix it in the same PR as your change.
