# claude-devkit

This repository contains the claude-devkit plugin system: a collection of skills, agents, guidelines, settings, and profiles that extend Claude Code's capabilities.

## Project Structure

```
claude-devkit/
├── .claude-plugin/         # Plugin marketplace manifest
│   └── marketplace.json    # Lists all skills for /plugin install
├── install.sh              # Main installer (--mode=remote|dev)
├── uninstall.sh            # Removes installed devkit items
├── update.sh               # Updates devkit and re-installs
├── CLAUDE.md               # This file — instructions for devkit contributors
├── skills/                 # Skill definitions (each in its own directory)
│   ├── review/             # Generic review orchestrator (PR or doc)
│   ├── pr-review/          # Multi-agent PR code review
│   ├── doc-review/         # Multi-agent document review
│   ├── doc-write/          # General-purpose document writer
│   ├── blog/               # Blog post — write, review, or update
│   ├── article/            # Deep technical article — write, review, or update
│   ├── project-docs/       # Project documentation — write, review, or update
│   ├── markdown/           # GFM markdown generation (folder-based)
│   ├── diagram/            # Diagram orchestrator (Mermaid or Excalidraw)
│   ├── mermaid/            # Mermaid diagram generation
│   ├── excalidraw/         # Excalidraw diagram generation
│   ├── image-transform/    # SVG → JPEG conversion
│   ├── confluence-publish/ # Publish to Confluence
│   ├── research/           # Web research
│   ├── pr-describe/        # Generate and post PR descriptions
│   ├── self-review/        # Iterative self-review with lint/test/build validation
│   ├── create-skill/       # Skill creator with devkit conventions
│   └── ...                 # Other skills
├── agents/                 # Agent definitions (markdown files)
│   ├── code-reviewer.md    # Multi-perspective code reviewer
│   ├── doc-reviewer.md     # Multi-dimensional document reviewer
│   ├── code-snippet-agent.md # Expressive-code block specialist
│   ├── diagram-agent.md    # Diagram orchestration agent
│   ├── mermaid-agent.md    # Mermaid diagram specialist
│   ├── excalidraw-agent.md # Excalidraw diagram specialist
│   ├── research-agent.md   # Web research agent
│   └── ...                 # Other agents
├── guidelines/             # Guideline documents (organized by category)
│   ├── coding/             # Code review guidelines
│   │   ├── general.md      # Baseline for all code reviews
│   │   ├── frontend-nextjs.md
│   │   ├── backend-java.md
│   │   ├── backend-python.md
│   │   ├── design-system.md
│   │   ├── js-ts-library.md
│   │   ├── scripts.md
│   │   └── expressive-code.md  # Code block conventions for docs
│   └── document/           # Document review guidelines
│       ├── general.md      # Baseline for all document reviews
│       ├── tdd.md          # Technical Design Document
│       ├── hld.md          # High Level Design
│       ├── lld.md          # Low Level Design
│       ├── prd.md          # Product Requirements Document
│       ├── erd.md          # Engineering Requirements Document
│       ├── tool-evaluation.md
│       ├── article.md      # Technical articles (deep research)
│       ├── blog.md         # Blog posts
│       ├── project.md      # Project documentation
│       └── ...             # Other document types
├── settings/               # Settings fragments and MCP routing
│   ├── base-settings.json  # Recommended permissions, env, MCP config
│   └── mcp-instructions.md # When to use which MCP server
├── profiles/               # Repo type detection and profile rules
│   ├── detect.md           # Auto-detection rules for repo types
│   └── README.md           # Documentation for the profiles system
└── repo-configs/           # Per-repo CLAUDE.md templates
    ├── design-system/
    │   └── CLAUDE.md
    ├── frontend-nextjs/
    │   └── CLAUDE.md
    ├── library/
    │   └── CLAUDE.md
    ├── backend/
    │   └── CLAUDE.md
    └── default/
        └── CLAUDE.md
```

## How to Add New Skills

1. Create a new directory under `skills/` with the skill name: `skills/my-skill/`
2. Add a `SKILL.md` file inside that directory following the skill format.
3. The SKILL.md should contain:
   - A title and description of what the skill does
   - Instructions for when and how to invoke the skill
   - Any tool usage patterns or workflows the skill enables
4. Test by installing with `--mode=dev` and verifying the skill appears in Claude Code.

## How to Add New Agents

1. Create a new markdown file under `agents/`: `agents/my-agent.md`
2. The agent file should define:
   - The agent's role and purpose
   - System instructions for the agent
   - Any specific tools or workflows the agent should use
3. Test by installing with `--mode=dev` and invoking the agent.

## How to Add New Guidelines

Guidelines are organized into two categories:

- **`guidelines/coding/`** — Code review guidelines (loaded by `/pr-review` and for code blocks in documents)
- **`guidelines/document/`** — Document review guidelines (loaded by `/doc-review`, `/doc-write`, and writing skills)

1. Determine the category: coding guideline or document guideline.
2. Create a new markdown file in the appropriate directory: `guidelines/coding/my-guideline.md` or `guidelines/document/my-guideline.md`
3. Follow the existing guideline structure: numbered sections, actionable rules, review checklist at the end.
4. Update the relevant skill to reference the new guideline (e.g., add a new tag in `/pr-review` Phase 1f or `/doc-review` Phase 1c).

## How to Add Repo Config Templates

1. Create a new directory under `repo-configs/` with the config type name.
2. Add a `CLAUDE.md` file with repo-specific instructions.
3. Users install these via `install.sh --repo-config=<type>`.

## Git Commit Rules

- **Use the system git identity.** Never override `user.name` or `user.email` via `git -c` flags or `GIT_AUTHOR_*`/`GIT_COMMITTER_*` env vars. The `.gitconfig` has folder-based `includeIf` rules that resolve the correct name and email per directory — just run `git commit` normally and let git resolve the identity.
- **Do NOT add `Co-Authored-By` trailers.** Commits should appear as authored solely by the configured git user. No Claude co-author lines.
- **Do NOT modify git config** — no `git config user.name`, `git config user.email`, or any other config changes.

## Conventions

- Skills use the `SKILL.md` format inside a named directory under `skills/`.
- Agents are single `.md` files under `agents/`.
- Guidelines are `.md` files organized under `guidelines/coding/` and `guidelines/document/`.
- Settings files go under `settings/`.
- All markdown files should use ATX-style headers (`#`, `##`, etc.).
- Shell scripts must start with `#!/usr/bin/env bash` and use `set -euo pipefail`.
- Scripts must work on both macOS (darwin) and Linux.

## Testing

1. Install in dev mode from this repo:
   ```bash
   ./install.sh --mode=dev
   ```
2. Open a real project and verify skills, agents, and guidelines are available.
3. Test uninstall:
   ```bash
   ./uninstall.sh
   ```
4. Test repo-config installation:
   ```bash
   cd /path/to/your/project
   /path/to/claude-devkit/install.sh --repo-config=default
   ```

## CLI Tool Preferences

This project runs on macOS and uses modern CLI replacements:
- Use `fd` instead of `find` for file searching
- Use `rg` (ripgrep) instead of `grep` for text searching
- Use `bat` instead of `cat` for file viewing (in scripts that output to users)
- Use `jq` for JSON processing
- Use `gh` for GitHub operations
- Use `mmdc` (mermaid-cli) for Mermaid → image rendering
- Use `excalidraw-cli` for Excalidraw → image rendering
- Use `ast-grep` for structural code search/replace (AST-based, far more precise than regex)
- Use `difft` (difftastic) for syntax-aware diffs when comparing code
- Use `tokei` for quick codebase statistics
- Use `delta` for readable git diff output
- Use `gron` to make JSON greppable

These tools are installed via Homebrew and npm (managed by the dot-files repo).

## Development Workflow

- Use `--mode=dev` during development so changes are reflected immediately via symlinks.
- Run `./install.sh --mode=dev` once, then edit files in-place.
- No rebuild or re-install step needed after editing skill/agent/guideline content.
- When testing the install/uninstall flow itself, use `--mode=remote` to verify copy behavior.
