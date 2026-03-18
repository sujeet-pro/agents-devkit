# Project Repository

This repository uses the **claude-devkit** plugin system for enhanced Claude Code capabilities.

## Devkit Integration

The claude-devkit is installed at `~/.claude/` and provides skills, agents, guidelines, and MCP integrations. The following resources are available in every session:

### Guidelines

General coding guidelines are automatically loaded from:

```
~/.claude/guidelines/general.md
```

These cover: correctness, error handling, naming conventions, DRY principle, security, testing, documentation, git hygiene, accessibility, performance, comments, and code style.

### Available Skills

Invoke skills with the `/` command:

| Skill | Command | Description |
|-------|---------|-------------|
| PR Review | `/pr-review <pr-number>` | Multi-agent code review for GitHub and Bitbucket PRs |
| Slack Compose | `/slack-compose <prompt>` | Compose and send Slack messages with context awareness |
| Diagram | `/diagram <description>` | Generate Mermaid or Excalidraw diagrams |
| Doc Review | `/doc-review <url>` | Review Confluence or Google Docs with inline comments |
| Doc Write | `/doc-write <topic>` | Write comprehensive documents with diagrams and research |
| Frontend Design | `/frontend-design <description>` | Generate 5 design variations with interactive selection |

### Available Agents

Agents are specialized sub-processes that can be spawned for focused tasks:

- **code-reviewer** — Multi-perspective code analysis (bugs, security, performance, architecture)
- **diagram-agent** — Technical diagram generation specialist
- **doc-reviewer** — Document review for accuracy, clarity, and completeness
- **research-agent** — Deep research with web search, synthesis, and citations

### MCP Integrations

The following MCP servers are configured and available:

| MCP Server | Use For |
|------------|---------|
| Google Drive | Google Docs, Sheets, Slides, Drive file management |
| Confluence | Confluence pages, comments, attachments, search |
| Bitbucket | Pull requests, pipelines, repos, branching models |
| Slack | Messages, channels, threads, canvases, user profiles |
| Gmail | Emails, drafts, labels, search |
| Google Calendar | Events, scheduling, free time, RSVPs |
| Multi | Multi-model chat, code review, comparison, debate |

## General Coding Best Practices

### Code Quality

- Write clear, self-documenting code with meaningful names
- Follow existing project conventions for style, formatting, and structure
- Keep functions focused and short (under ~50 lines)
- Keep files focused (under ~300-400 lines)
- Use early returns to reduce nesting
- Handle errors explicitly — never swallow exceptions silently

### Testing

- Write tests for new features and bug fixes
- Test behavior, not implementation details
- Keep tests deterministic and independent
- Use descriptive test names that explain the expected behavior

### Security

- Never commit secrets (API keys, passwords, tokens)
- Validate all external input at system boundaries
- Use parameterized queries for database access
- Follow the principle of least privilege

### Git

- **Use the system git identity.** Never override `user.name` or `user.email` via `git -c` flags or `GIT_AUTHOR_*`/`GIT_COMMITTER_*` env vars. The `.gitconfig` resolves the correct name and email per directory — just run `git commit` normally.
- **Do NOT add `Co-Authored-By` trailers.** Commits should appear as authored solely by the configured git user.
- **Do NOT modify git config** — no `git config user.name`, `git config user.email`, or any other config changes.
- Write meaningful commit messages that explain *why*
- Keep commits atomic (one logical change per commit)
- Remove debug code before committing

## Validation

Commands for `/self-review` to run during iterative review. Update these to match your project:

- lint: `npm run lint`
- lint-fix: `npm run lint -- --fix`
- test: `npm test`
- build: `npm run build`
- typecheck: `npx tsc --noEmit`

## PR Reviews

To trigger a PR review, use the `/pr-review` skill:

```
/pr-review 42
/pr-review https://github.com/org/repo/pull/42
/pr-review 42 --tags=fe
```

### Review Tags

Tags customize the review focus. Add them to the PR title, description, or pass them explicitly:

| Tag | Focus Area |
|-----|-----------|
| `[ds]` | Design system — tokens, accessibility, API stability, visual regression |
| `[fe]` | Frontend — performance, accessibility, SEO, server/client components |
| `[lib]` | Library — public API, bundle size, tree-shaking, semver, types |
| `[be]` | Backend — security, error handling, database patterns, API contracts |
| `[script]` | Scripts — error handling, idempotency, portability |

If no tag is provided, the system auto-detects the repo type from project files.

## Document Tools

### Writing Documents

Use `/doc-write` to create comprehensive documents:

```
/doc-write "Migration guide for React 18 to 19" --format=confluence --depth=deep-dive
/doc-write "API authentication architecture" --format=markdown --audience=senior
```

Output formats: `markdown` (local file), `confluence` (creates a Confluence page), `google-doc` (creates a Google Doc).

### Reviewing Documents

Use `/doc-review` to review existing documents on Confluence or Google Docs:

```
/doc-review https://yourcompany.atlassian.net/wiki/spaces/ENG/pages/12345
/doc-review https://docs.google.com/document/d/abc123 --focus=accuracy,completeness
```

The review spawns multiple agents that check accuracy, clarity, and completeness, then posts inline comments after your approval.

## Customizing This File

This is the **default** CLAUDE.md template. To get more specific instructions for your repo type, re-install with a targeted template:

```bash
/path/to/claude-devkit/install.zsh --repo-config=design-system
/path/to/claude-devkit/install.zsh --repo-config=frontend-nextjs
/path/to/claude-devkit/install.zsh --repo-config=library
/path/to/claude-devkit/install.zsh --repo-config=backend
```

You can also edit this file directly to add project-specific instructions. Lines you add will not be overwritten unless you re-run the repo-config install.
