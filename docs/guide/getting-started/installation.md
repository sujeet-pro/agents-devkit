---
title: Installation
description: Install ADK as a Claude Code plugin (primary), via npm, by cloning the repo, or with the npx skills loader. Then run setup to wire MCP, CLI deps, and user memory.
order: 1
---

# Installation

ADK ships as a Claude Code plugin first. The same skills are also reachable from Cursor, Codex, Gemini, and Antigravity through a parallel `agents-skills/adk-<name>` symlink farm. Pick one of the four paths below — they all land at the same `/adk:setup` (or `npx adk`) finishing step.

> [!IMPORTANT]
> The Claude plugin install does **not** automatically register MCP servers or write to your user-level `~/.claude/CLAUDE.md`. You must finish with **`/adk:setup`** (Claude) or **`npx adk`** (any other harness) for ADK to be fully wired.

## Requirements

- **macOS** (the bin scripts shell out to Homebrew).
- **Node.js ≥ 18** — `brew install node`.
- **Homebrew** — install from [brew.sh](https://brew.sh).
- **Claude Code** — install via `brew install --cask claude-code` if you want the Claude Code plugin path.

## Path 1 — Claude Code plugin (primary)

This is the canonical path because the repo IS the `adk` Claude Code plugin (`.claude-plugin/plugin.json`). The Claude plugin host loads every skill, subagent, hook, monitor, and the bundled MCP registry in one shot.

### From the marketplace

```text
# Inside Claude Code:
/plugin marketplace add sujeet-pro/agents-devkit
/plugin install adk@sujeet-pro-adk
/reload-plugins
```

### From a local clone (development)

```bash
git clone https://github.com/sujeet-pro/agents-devkit.git
cd agents-devkit
npm install
claude --plugin-dir "$(pwd)"
```

### Then finish with `/adk:setup`

```text
/adk:setup            # interactive (recommended first run)
/adk:setup --auto     # unattended; safe defaults
```

`/adk:setup` will:

1. Verify and (with approval) install Homebrew CLI deps: `gh`, `jq`, `fd`, `ripgrep`, `fzf`, `claude`, `node`.
2. Check `gh auth status` and prompt you to `gh auth login` if needed.
3. Read `.mcp.json`, resolve `${ENV_VAR}` placeholders from `~/.zshenv`, and run `claude mcp add` for each accepted server.
4. Write a managed `<!-- adk:start --> ... <!-- adk:end -->` block into `~/.claude/CLAUDE.md` (and the AGENTS.md / GEMINI.md of every other harness it detects) so each harness auto-discovers ADK.
5. Run `bin/adk-doctor` and surface the report.

> [!NOTE]
> The user-memory step is what makes ADK discoverable from a fresh Claude session without anyone typing `/adk:auto` first. The block is idempotent — re-runs replace it in place.

## Path 2 — npm module (works for every harness)

Use this when you want a pinned version, are not on Claude Code yet, or are driving setup from a non-Claude harness (Cursor / Codex / Gemini / Antigravity).

### One-shot

```bash
npx --yes agents-devkit adk
```

`adk` (alias for `adk-setup`) auto-detects which agents are present and installs into all of them. Equivalent to the `/adk:setup` flow above, but driven from the shell.

### Project-pinned (CI-friendly)

```bash
cd <your-project>
npm install --save-dev agents-devkit
npx adk
```

Add `npx adk --auto` to your project's bootstrap script for reproducible CI provisioning.

### Global

```bash
npm install -g agents-devkit
adk
```

### Per-step CLIs

```bash
npx adk-install                # symlink agents-skills/adk-<name> into detected harnesses
npx adk-install --target cursor,codex
npx adk-install --mode project          # link into <cwd>/.cursor/skills/ etc.
npx adk-install --dry-run

npx adk-mcp-install            # interactive picker for MCP servers
npx adk-mcp-install --auto     # enable every server with env vars present
npx adk-mcp-install --list     # report status only

npx adk-update-memory                       # write managed block into every detected harness
npx adk-update-memory --target claude       # only ~/.claude/CLAUDE.md
npx adk-update-memory --remove              # delete the managed block

npx adk-doctor                 # health check
npx adk-validate               # structural + content validator
```

## Path 3 — Clone + symlink (for contributors)

Best when you want every edit live (no `npm install` step) and full git access to skills, agents, hooks, MCP, monitors.

```bash
git clone https://github.com/sujeet-pro/agents-devkit.git ~/code/agents-devkit
cd ~/code/agents-devkit
npm install
node bin/adk-setup            # interactive — same as `/adk:setup` and `npx adk`
```

Symlinks point back at the clone, so:

- `git pull` instantly refreshes every linked harness.
- Edits to `skills/<name>/SKILL.md` show up live in Claude / Cursor / Codex without a reload.

### Selective install

```bash
node bin/adk-install --target cursor                  # only Cursor
node bin/adk-install --target cursor,codex            # multiple
node bin/adk-install --mode project                   # project-local symlinks
node bin/adk-install --dry-run

node bin/adk-update-memory --plugin-root /custom/path # override install location
node bin/adk-update-memory --target cursor            # only one harness
```

## Path 4 — `npx skills add` (skills only)

The third-party [`skills`](https://skills.sh) loader picks up the `agents-skills/adk-<name>` folders. Useful when you want **just the skills** — no subagents, no hooks, no MCP servers, no user-memory wiring.

```bash
npx skills add sujeet-pro/agents-devkit                                # all skills, all detected agents
npx skills add sujeet-pro/agents-devkit -a claude-code                 # one harness
npx skills add sujeet-pro/agents-devkit -a cursor -a codex             # multiple harnesses
npx skills add sujeet-pro/agents-devkit -s adk-plan-brainstorm         # specific skill
```

> [!WARNING]
> `npx skills add` does **not** install subagents, hooks, MCP servers, monitors, or update your user-level memory file. Use Path 1, 2, or 3 if you want the full kit.

## Verify

After any path, confirm everything is wired up:

```bash
npx adk-doctor
# or
node bin/adk-doctor
```

Expected output sections:

- **CLI tools** — every entry should be `present`.
- **gh auth status** — `authed`.
- **MCP servers** — every server you accepted should be `installed`.
- **User memory** — every detected harness should be `up-to-date`.
- Final line: `doctor: 0 errors, N warnings`.

## Updating

```bash
# Claude plugin (marketplace path)
/plugin update adk@sujeet-pro-adk
/reload-plugins
/adk:setup --auto       # re-run setup; idempotent

# npm module
npm update -g agents-devkit
adk --auto

# Clone path
cd ~/code/agents-devkit
git pull
npm install
node bin/adk-setup --auto
```

The setup script is idempotent — re-runs only act on missing pieces and refresh the user-memory block in place.

## Uninstall

```bash
# Remove the user-memory block from every harness (non-destructive — your other content is preserved)
node bin/adk-update-memory --remove

# Remove agent symlinks
# (no built-in uninstaller — agents-skills are simple symlinks under ~/.cursor/skills/, ~/.codex/skills/, etc.; remove the adk-* entries by hand)

# Claude plugin
/plugin uninstall adk@sujeet-pro-adk

# npm
npm uninstall -g agents-devkit
```

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `/adk:` commands missing in Claude | Plugin not loaded or marketplace not added. | `/plugin marketplace list`, `/plugin install adk@sujeet-pro-adk`, `/reload-plugins`. |
| Skills present but MCP tools missing | Setup not run, or `${ENV_VAR}` missing in `~/.zshenv`. | `npx adk-mcp-install --list` then add the missing exports to `~/.zshenv`, re-run `--auto`. |
| Cursor / Codex don't see ADK | `agents-skills/` symlinks not installed for that harness. | `node bin/adk-install --target cursor,codex` (or `--target auto`). |
| Fresh Claude session doesn't auto-discover ADK | User-memory block not written. | `npx adk-update-memory` (or `--target claude` for just Claude). |
| `adk-doctor` reports a missing tool | Homebrew install of that tool failed. | Re-run `npx adk --auto` or `brew install <tool>` manually. |

## Next

- [First skill](./first-skill.md) — run `/adk:auto` on a real task.
- [Memory files](../../concepts/memory-files.md) — how `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` compose.
- [Reference](../../reference/skills/README.md) — one page per skill, agent, hook, MCP server, and CLI script.
