# global-prompts/

Plain-text prompt fragments that should be loaded **globally** by every agent
on this machine, regardless of project. Each file in this folder represents
one self-contained instruction that the agent must read and obey at the start
of every session.

## How it gets installed

The interactive installer (`npm run setup`) walks every detected runtime's
top-level memory file:

| Runtime | Memory file |
| --- | --- |
| Claude Code (CLI) | `~/.claude/CLAUDE.md` |
| Claude Desktop | `~/Library/Application Support/Claude/CLAUDE.md` (macOS) |
| Codex CLI | `~/.codex/AGENTS.md` |
| Cursor (App + CLI) | `~/.cursor/AGENTS.md` |
| Generic `.agents/*` | `~/.agents/AGENTS.md` |
| Antigravity | `~/.antigravity/AGENTS.md` |
| Junie | `~/.junie/AGENTS.md` |
| Gemini CLI | `~/.gemini/GEMINI.md` |

For each global prompt file in this folder, the installer ensures the runtime's
memory file contains a managed block that **imports** the prompt by absolute
path. The block looks like:

```markdown
<!-- adk:global-prompts:start -->
The following prompts are managed by agents-devkit. Always read and obey them
before doing any work.

- /Users/<you>/path/to/agents-devkit/global-prompts/temp-folder.md
<!-- adk:global-prompts:end -->
```

Re-running the installer will:

1. Strip the existing managed block.
2. Re-emit the block with whatever files are currently in `global-prompts/`.

So renames and removals propagate cleanly — exactly like the skill symlinks.

## Authoring a new global prompt

1. Create `global-prompts/<topic>.md`.
2. Keep it short, declarative, and runtime-agnostic.
3. Re-run `npm run setup` and pick the runtimes you want it installed for.
