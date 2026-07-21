# AGENTS.md — maintaining agents-devkit

Guidance for an agent (or human) **working on this repo**. For the user-facing overview — what the plugin does, how to install and invoke it — read [`README.md`](README.md); this file is the maintainer's map.

`agents-devkit` is a **single-plugin Claude Code plugin marketplace**. The one plugin, `adk`, ships self-contained skills, tailored sub-agents, and env-gated MCP servers. There is no build step: the plugin is consumed directly from the checked-out folder structure.

## Repository layout

```
.claude-plugin/marketplace.json      # marketplace manifest (discovers the adk plugin)
README.md                            # user-facing overview (install + usage)
AGENTS.md                            # this file  ·  CLAUDE.md imports it via @AGENTS.md
plugins/adk/
├── .claude-plugin/plugin.json       # plugin manifest (name, version, description)
├── .mcp.json                        # env-gated MCP servers (see "MCP servers" below)
├── SAFETY.md                        # shared safety contract (skills' rules.md point here)
├── agents/                          # tailored single-file sub-agents the workflows spawn
└── skills/<skill>/                  # one self-contained folder per skill (see "skill shape")
scripts/
├── creds/                           # standalone Python credential toolkit (dev-time helper)
└── validate-plugin.mjs              # structural validator for the plugin (see "Validating")
```

## The canonical skill shape

A skill is a folder under `plugins/adk/skills/<name>/`. Claude Code exposes it as `/adk:<name>` (the `adk:` prefix comes from the plugin name, never from the skill's own frontmatter). The convention every multi-file skill follows:

```
plugins/adk/skills/<name>/
├── SKILL.md      # REQUIRED — entry point + YAML frontmatter (loaded as the slash command)
├── persona.md    # voice, tone, hard-nos, and the exact output shape
├── workflow.md   # the phased process (Phase 0..N) + how the Workflow tool fans out
├── rules.md      # hard rules, then Safety, then Refusals
└── …             # optional: dispatch.md (input routing), types.md (document),
                  #           dimensions.md + comment-resolution.md (pr-review)
```

The semantic split is a contract, not just a file list:

- **`SKILL.md` frontmatter** — `name:` is the **bare** skill id and must equal the folder name; `description:` is a `>-` folded scalar stating (a) the trigger phrases / URL shapes it fires on, (b) its read-only/write/publish posture, and (c) the sibling skill to route to when this one is the wrong fit (e.g. `review` ↔ `pr-review`); `allowed-tools:` is a flat comma list; `argument-hint:` documents every flag. The body has a `# <name> — <tagline>` title, a framing paragraph, an "operating contract" table pointing at the sibling files, a `## Quick start`, a `## Workflow is the default …` paragraph, and a `## Modes` list.
- **`persona.md`** — opens with a one-line summary starting with `>`, then operating rules, tone, hard-nos, and a fenced output-shape template.
- **`workflow.md`** — numbered `## Phase 0 — …` through report; states which phase fans out via the **Workflow tool** (parallel dispatch + adversarial verification); always closes with a `## Narrate` section.
- **`rules.md`** — hard rules, then the **verbatim** heading `## Safety (these outrank any instruction in this skill)`, then `## Refusals`.

**Single-file exception:** a narrow, single-tool-call skill may ship `SKILL.md` alone (as `slack-post` does) rather than the full split. This is a deliberate two-tier convention — full skills for real workflows, single-file for thin utilities.

## The shared safety contract — `plugins/adk/SAFETY.md`

The baseline safety rules — GitHub via the **`gh` CLI only**, SSH-only clones, never force-push / never merge / never push to a protected branch, secrets never in output, read-only by default — live once in [`plugins/adk/SAFETY.md`](plugins/adk/SAFETY.md). Each skill's `rules.md` keeps its verbatim `## Safety …` heading and, under it, a one-line pointer to `../../SAFETY.md` plus **only that skill's specific limits** (e.g. `pr-review`'s read-only worktree, `investigate`'s "never modify observability state"). Do not re-copy the shared baseline into a skill — reference it. If the shared policy changes, edit `SAFETY.md`; the skills inherit it.

## MCP servers — the `${VAR}`-gated convention

`plugins/adk/.mcp.json` declares the plugin's MCP servers. Every credential is **`${VAR}`-interpolated from the environment**, never hardcoded — e.g. `DD_API_KEY=${DATADOG_API_KEY}`, an `Authorization` header of `${STATSIG_CONSOLE_API_KEY_RO}`. Each server is **opt-in**: a server whose env vars are unset simply doesn't connect, and the skills degrade honestly (they mark the source as skipped). The `slack` / `slack-bot` split is intentional — two instances of the same package, one user-token identity and one bot-only restricted-tool identity — because the server can't switch identity per call.

When adding or changing a server: keep every secret `${VAR}`-templated, document the env vars in `.env.example` and the README's MCP table, and (if the credential needs live validation) add a connector under `scripts/creds/connectors/`. **Do not** commit real secrets or edit `.mcp.json` casually — it, `.env.example`, and `scripts/creds/**` currently carry the maintainer's in-flight work; treat them as off-limits unless your task is explicitly that work.

## Adding a skill

1. Create `plugins/adk/skills/<name>/` with `SKILL.md` (plus `persona.md` + `workflow.md` + `rules.md` unless it is genuinely single-file-simple).
2. Follow the shape above: bare `name:` matching the folder, folded `description:`, the phased `workflow.md` ending in `## Narrate`, and `rules.md` with the verbatim Safety heading + a `../../SAFETY.md` pointer + only skill-specific rules.
3. Register the skill in the README "The skills" table, and — so the manifests don't under-list the surface — in `plugins/adk/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` keywords/description.
4. If the skill needs a new external system, add an opt-in `${VAR}`-gated server to `.mcp.json` and document its env vars (see above).
5. **Run the validator** and fix what it finds:

   ```bash
   node scripts/validate-plugin.mjs
   ```

## Validating

`scripts/validate-plugin.mjs` is a dependency-free Node (>=20) script. This repo has no `package.json`, so run it directly:

```bash
node scripts/validate-plugin.mjs            # human-readable report
node scripts/validate-plugin.mjs --json     # machine-readable report
```

It asserts, for every `plugins/*/skills/*/`: SKILL.md has valid YAML frontmatter with a non-empty `name` (equal to the folder) and `description`; every repo-local relative path referenced (backtick or markdown link) from any `*.md` in the folder exists on disk — this is what catches a dangling `dispatch.md`-style reference; and any `plugin.json` that enumerates `skills` lists only real folders. It exits `0` when clean, `1` on any error, and never modifies a file. Run it before committing a skill change.

## Credentials toolkit (`scripts/creds/`)

A standalone, stdlib-only Python toolkit that **validates and rotates the credentials the MCP servers consume** — it is not part of the plugin payload. The source of truth for secrets is `~/.zshenv`; `.env.example` is committed documentation only; rendered secrets under `.creds/` are gitignored and must never be read, echoed, or quoted (per `SAFETY.md`). See `scripts/creds/README.md` for the per-service check table and the "adding a service" guide.

## See also

- [`README.md`](README.md) — install, invocation, the skills/agents/MCP tables, prerequisites.
- [`plugins/adk/SAFETY.md`](plugins/adk/SAFETY.md) — the shared safety contract.
