# Agent Development Kit (ADK)

Principal-engineer-grade skills for software development agents. Code review, documentation, research, codebase audits, diagrams, planning, migrations, refactoring, and MCP-native publishing.

> **Designed for Claude Code.** ADK is built and tested as a Claude Code plugin. Features like custom sub-agents with persistent memory, hooks, and plugin-scoped MCP servers rely on Claude Code. You can install individual skills via `npx skills` for other agents (Codex, etc.), but these Claude-specific features will not be available.

Route general prompts through `/adk:use` first. Invoke a specific skill directly only when you explicitly name it or clearly want that exact workflow. Every skill supports `--help`.

Inspired by [superpowers](https://github.com/obra/superpowers). Diagram skills from [diagramkit](https://github.com/sujeet-pro/diagramkit). Markdown capabilities from [pagesmith](https://github.com/sujeet-pro/pagesmith).

## At a Glance

| What | Count | Details |
|------|------:|---------|
| **Skills** | 52 | 30 task, 17 guideline/helper, 5 routing/orchestrator |
| **Agents** | 18 | Reusable child-agent definitions for parallel work |
| **Reference files** | 251 | Including 16 coding guidelines and 24 doc-writing guidelines |
| **Stage files** | 58 | Conditional stages loaded per mode/context |
| **Scripts** | 67 | Preflight checks, setup, and platform connectors |
| **Total instructions** | ~42,000 lines | But only ~200-500 lines load per task (see lazy loading below) |

### Token-Efficient Lazy Loading

ADK never loads all 42,000 lines at once. Each task loads only what it needs:

1. **Primary skill** (~100-300 lines) — the SKILL.md for the task at hand
2. **Conditional stages** (~50-150 lines) — only the stage matching the detected mode (e.g., `debug` vs `implement` vs `tdd`)
3. **Conditional references** (~50-200 lines) — only the guidelines matching the detected stack (e.g., Python backend guidelines, not all 16 coding guideline files)
4. **Guideline skills** (~50-100 lines each) — loaded on demand, skipped if not installed (inline fallback summaries are ~1 line each)

A typical PR review loads ~400 lines. A Mermaid diagram loads ~250 lines (1 type reference out of 21). A full-stack feature implementation loads ~600 lines across multiple skills. The remaining ~41,000 lines stay on disk.

## Philosophy

- **Human-in-the-loop** — decisions happen interactively, execution happens automatically
- **Plan first, then implement** — every non-trivial task follows a 6-phase workflow with approval gates
- **Concise by default** — output is compact and decision-oriented; show the short version first, then offer to elaborate if the user needs more detail
- **Self-sufficient skills** — every skill works independently with inline fallbacks for shared knowledge; can invoke other skills when available
- **Parallel agentic teams** — non-trivial work uses child agents with distinct roles
- **Principal engineer lens** — do we need this? What's the simplest version? What are the alternatives?
- **Lazy loading** — only the relevant skill, stage, and reference files load per task; ~200-500 lines per invocation out of ~42,000 total
- **Markdown by default** — all outputs are markdown unless the user requests otherwise
- **Auto mode** — pass `--auto` to skip confirmations and execute the full workflow automatically
- **Claude-first** — designed for Claude Code as a plugin (`/adk:<skill-name>`). Also installable via `npx skills` for other agents, though some features (custom sub-agents, memory) require Claude

## The 6-Phase Workflow

Every non-trivial skill follows a standardized 6-phase workflow. Human interaction happens first, not after hidden research.


| Phase | Name                   | What Happens                                                                                       |
| ----- | ---------------------- | -------------------------------------------------------------------------------------------------- |
| 0     | **Intent Expansion**   | Expand the prompt, show concise reasoning, identify skills/tools/MCPs, and confirm direction early |
| 1     | **Research & Options** | Research the problem, scan the codebase, and surface 2-3 viable options                            |
| 2     | **Approach Selection** | Let the user choose, mix, or simplify the direction                                                |
| 3     | **Planning**           | Produce an executable plan with files, sequencing, and verification                                |
| 4     | **Execute**            | Run the approved plan                                                                              |
| 5     | **Validate & Learn**   | Validate the result, simplify when needed, and explain the key takeaway                            |


### Complexity-Adaptive Skipping


| Complexity | Files | Phases Used                                     |
| ---------- | ----- | ----------------------------------------------- |
| Trivial    | 1     | 0 inline, 4, 5 quick                            |
| Small      | 2-3   | 0 inline, 1 lite, 3 brief, 4, 5                 |
| Medium     | 4-8   | All 6 phases                                    |
| Large      | >8    | All 6 phases with PE check and phased execution |


## Install

### Using Claude Code (Recommended)

```bash
# Add the marketplace and install the plugin
/plugin marketplace add sujeet-pro/agents-devkit
/plugin install adk@adk-marketplace
```

Skills become available as `/adk:<skill-name>` immediately.

### Using skills.sh (Claude / Codex)

```bash
# Install all skills
npx skills add sujeet-pro/agents-devkit

# Install specific skills
npx skills add sujeet-pro/agents-devkit/skills/code-review-pr
npx skills add sujeet-pro/agents-devkit/skills/dev-build
```

When installed via skills.sh, skills use the `name` field from frontmatter (e.g., `/code-review-pr`, `/dev-build`). Works with Claude Code, Codex, and other skills.sh-compatible agents. Some features — custom sub-agents with memory, hooks — require Claude Code.

Visit [skills.sh](https://skills.sh) for more details.

### Cross-Agent Installation

ADK skills use the universal SKILL.md format. Individual skills work in any agent that supports it — copy the skill directory to the agent's skill path:

| Agent | Skill Path | Invocation |
|-------|-----------|------------|
| Claude Code | `.claude/skills/` or via plugin | `/adk:<skill-name>` |
| Cursor | `.cursor/skills/` | Auto-detected from SKILL.md |
| Codex CLI | `.codex/skills/` | `/<skill-name>` |
| Gemini CLI | `.gemini/skills/` | `/<skill-name>` |
| OpenCode | `.opencode/skills/` | `/<skill-name>` |
| Universal | `.agent/skills/` | Agent-dependent |

```bash
# Example: install a single skill into Cursor
cp -r skills/code-review-pr ~/.cursor/skills/code-review-pr
```

**Feature availability by platform:**

| Feature | Claude Code | Other Agents |
|---------|:-----------:|:------------:|
| SKILL.md instructions | Full | Full |
| Stages & references | Full | Full |
| Preflight scripts | Full | Full |
| Custom sub-agents (18 agents) | Full | Not available |
| Agent memory (`memory: project`) | Full | Not available |
| Plugin hooks | Full | Not available |
| Plugin namespace (`adk:`) | Full | Not available |
| Inline fallbacks for missing helpers | Full | Full |

### Local Development

```bash
git clone https://github.com/sujeet-pro/agents-devkit.git ~/.devkit
claude --plugin-dir ~/.devkit
```

### Recommended System Prompt

After installing, add this to your project's `CLAUDE.md` (or `~/.claude/CLAUDE.md` for global use) to enable skill-first routing on every prompt:

```markdown
## ADK Skill Routing

On every user prompt, follow this workflow before doing any work:

1. **Expand intent** — restate the goal in one line, surface assumptions, estimate complexity
2. **Identify skills** — check installed ADK skills (`/adk:use` or `/use`) and select the minimum pipeline
3. **Show phase summary** — display a concise phase plan:
   - Goal (one line)
   - Skills to use (with brief rationale)
   - Phases that will run (based on complexity)
   - Complexity level (Trivial/Small/Medium/Large)
4. **Confirm with user** — wait for approval before executing (unless `--auto`)
5. **Execute with concise output** — lead with conclusions, offer to elaborate
6. **Validate** — verify the result, self-review, simplify if possible

Output is concise by default. After completing a task, show the short summary and ask:
"Need a detailed breakdown?" — only elaborate when the user says yes.
```

Run `/adk:setup --type config` to apply this automatically.

## Update

### Using Claude Code

```bash
/plugin update adk
```

### Using skills.sh

```bash
npx skills update sujeet-pro/agents-devkit
```

## Uninstall

### Using Claude Code

```bash
/plugin uninstall adk

# Remove the marketplace (optional)
/plugin marketplace remove adk-marketplace
```

### Using skills.sh

```bash
npx skills remove sujeet-pro/agents-devkit
```

---

## Skill Categories

ADK's 52 skills are organized into four categories. Only the relevant skill files load per task (see [lazy loading](#token-efficient-lazy-loading)).

### Guideline Skills (17 helpers)

Provide reusable knowledge and standards. Auto-invoked by task skills when available. Each task skill includes one-line inline fallback summaries, so it works even if the guideline skill is not installed.


| Skill                | Invocation                | What It Provides                                                                  |
| -------------------- | ------------------------- | --------------------------------------------------------------------------------- |
| `workflow`           | `/adk:workflow`           | 6-phase workflow framework with complexity-adaptive phase skipping                |
| `communication`      | `/adk:communication`      | Communication style: lead with conclusion, no preamble, concise by default        |
| `principal-engineer` | `/adk:principal-engineer` | PE questioning: need? simplest? alternatives? maintenance? clarity?               |
| `agentic-teams`      | `/adk:agentic-teams`      | Child-agent contract: team shapes for review, research, docs, security, migration |
| `output-format`      | `/adk:output-format`      | Verbosity modes, PR comment templates, priority/principle labels                  |
| `interaction`        | `/adk:interaction`        | Inline protocols: intent confirm, approach select, plan approve, review findings  |
| `preflight-check`    | `/adk:preflight-check`    | Preflight validations for dependencies, MCP, and tool readiness                   |
| `review-standards`   | `/adk:review-standards`   | Review pipeline, comment template, source routing, postback rules                 |
| `coding`             | `/adk:coding`             | Detects repo stack, lazy-loads matching coding guidelines (16 guideline files)    |
| `docs-guidelines`    | `/adk:docs-guidelines`    | Detects document type, lazy-loads matching writing guidelines (24 guideline files)|
| `docs-md`            | `/adk:docs-md`            | Detects markdown target (pagesmith/GitHub/plain), loads formatting guidelines     |
| `architecture`       | `/adk:architecture`       | Architecture patterns, principles, and anti-pattern detection                     |
| `workspace-conventions` | `/adk:workspace-conventions` | Workspace file conventions: temp files, diagram output, artifact locations     |

Connector skills (auto-invoked by task skills for platform APIs):

| Skill          | Invocation          | What It Provides                                     |
| -------------- | ------------------- | ---------------------------------------------------- |
| `github`       | `/adk:github`       | GitHub PR, issue, review, and repo operations via `gh` CLI |
| `bitbucket`    | `/adk:bitbucket`    | Bitbucket PR, comment, and repo operations via API   |
| `confluence`   | `/adk:confluence`   | Confluence page, comment, and space operations       |
| `jira`         | `/adk:jira`         | Jira issue, board, project, and search operations    |


### Task Skills (30 user-facing)

Perform specific engineering tasks. Each is self-sufficient with inline fallback summaries for all shared knowledge.


| Skill                | Area        | Invocation                | Description                                                  |
| -------------------- | ----------- | ------------------------- | ------------------------------------------------------------ |
| `code-review-pr`     | Review      | `/adk:code-review-pr`     | Code review: PR, local, branch + fix/comment/interactive     |
| `code-review-repo`   | Review      | `/adk:code-review-repo`   | Whole-repo review with prioritized improvement plan          |
| `code-review-fix`    | Review      | `/adk:code-review-fix`    | Fix PR comments, reply to reviewers, mark resolved           |
| `docs-review`        | Review      | `/adk:docs-review`        | Review documents (local, Confluence, Google Docs)            |
| `dev-build`          | Dev         | `/adk:dev-build`          | Implement features, fix bugs, enhance code, TDD              |
| `dev-refactor`       | Dev         | `/adk:dev-refactor`       | Extract, rename, restructure, simplify, modernize code       |
| `dev-migrate`        | Dev         | `/adk:dev-migrate`        | Framework/library migration with breaking change analysis    |
| `dev-commit`         | Dev         | `/adk:dev-commit`         | Smart commit messages and PR descriptions                    |
| `docs-write`         | Docs        | `/adk:docs-write`         | Create/update formal documents (ADR, RFC, blog, changelog)   |
| `docs-repo`          | Docs        | `/adk:docs-repo`          | Generate comprehensive repo documentation (pagesmith)        |
| `docs-crud`          | Docs        | `/adk:docs-crud`          | Manage doc lifecycle: create, update, improve, comment-reply |
| `docs-confluence`    | Docs        | `/adk:docs-confluence`    | Confluence-specific read/write with format mapping           |
| `plan`               | Plan        | `/adk:plan`               | Brainstorm, write, execute, and track implementation plans   |
| `spec`               | Spec        | `/adk:spec`               | Write specs, analyze consistency, generate checklists        |
| `research`           | Research    | `/adk:research`           | Multi-agent research with citations                          |
| `diagram-mermaid`    | Diagram     | `/adk:diagram-mermaid`    | Mermaid diagrams with full syntax reference (21 types)       |
| `diagram-excalidraw` | Diagram     | `/adk:diagram-excalidraw` | Excalidraw hand-drawn style architecture diagrams            |
| `diagram-graphviz`   | Diagram     | `/adk:diagram-graphviz`   | Graphviz DOT diagrams for dependency graphs                  |
| `diagram-drawio`     | Diagram     | `/adk:diagram-drawio`     | Draw.io precise layout for network/enterprise architecture   |
| `design`             | Design      | `/adk:design`             | UI/UX design direction + visual audit                        |
| `audit`              | Quality     | `/adk:audit`              | Audit: codebase, security, performance, dependencies         |
| `test`               | QA          | `/adk:test`               | User acceptance testing with interactive verification        |
| `project`            | Project     | `/adk:project`            | Initialize projects, manage milestones and ideas             |
| `handoff`            | Session     | `/adk:handoff`            | Pause/resume work sessions, context threads                  |
| `setup`              | Setup       | `/adk:setup`              | Configure CLI tools, MCP servers, hooks, and system prompt   |
| `deps-tracker`       | Project     | `/adk:deps-tracker`       | Track upstream dependencies and sync updates                 |
| `interactivity`      | Interaction | `/adk:interactivity`      | Structured interaction: options, data capture, approvals     |
| `chart`              | Data        | `/adk:chart`              | Data charts (bar, line, pie, scatter, 30+ types) from CSV/JSON |
| `team`               | Team        | `/adk:team`               | Multi-model review, agent team dispatch                        |
| `create-skill`       | Meta        | `/adk:create-skill`       | Scaffold a new ADK skill with proper structure and frontmatter |


### Routing Skills (5 orchestrators)

Coordinate and route work across other skills. Category routers auto-detect the right sub-skill.


| Skill         | Invocation         | Description                                                               |
| ------------- | ------------------ | ------------------------------------------------------------------------- |
| `use`         | `/adk:use`         | Default orchestrator: expand intent, identify skills, confirm, execute    |
| `code-review` | `/adk:code-review` | Code review router: detects type, routes to code-review-pr/repo/fix      |
| `docs`        | `/adk:docs`        | Documentation router: routes to docs-write/crud/repo/review/confluence   |
| `dev`         | `/adk:dev`         | Development router: routes to dev-build/refactor/migrate/commit          |
| `diagram`     | `/adk:diagram`     | Diagram router: detects engine, routes to mermaid/excalidraw/drawio/graphviz |


---

## Recipe Table

**If you want to do X, use these skills:**


| Goal                          | Primary Skill                     | Also Uses                                    |
| ----------------------------- | --------------------------------- | -------------------------------------------- |
| **Review a PR**               | `code-review-pr`                  | `coding`, `review-standards`                 |
| **Fix PR review comments**    | `code-review-fix`                 | `coding`, `review-standards`                 |
| **Review entire codebase**    | `code-review-repo`                | `architecture`, `coding`, `review-standards` |
| **Implement a new feature**   | `dev-build`                       | `coding`, `architecture`                     |
| **Fix a bug**                 | `dev-build --mode debug`          | `coding`                                     |
| **Refactor code**             | `dev-refactor`                    | `coding`, `architecture`                     |
| **Migrate a framework**       | `dev-migrate`                     | `research`, `coding`                         |
| **Create a commit**           | `dev-commit`                      | —                                            |
| **Create a PR description**   | `dev-commit --action pr-describe` | —                                            |
| **Write an ADR/RFC**          | `docs-write`                      | `docs-guidelines`, `docs-md`                 |
| **Write a blog post**         | `docs-write --type blog`          | `docs-guidelines`, `docs-md`                 |
| **Generate repo docs**        | `docs-repo`                       | `docs-md`, `docs-guidelines`                 |
| **Review documentation**      | `docs-review`                     | `docs-guidelines`, `review-standards`        |
| **Update docs from comments** | `docs-crud`                       | `docs-guidelines`, `docs-md`                 |
| **Create a diagram**          | `diagram` (routes to engine)      | engine-specific skill                        |
| **Mermaid sequence diagram**  | `diagram-mermaid`                 | —                                            |
| **Architecture overview**     | `diagram-excalidraw`              | —                                            |
| **Dependency graph**          | `diagram-graphviz`                | —                                            |
| **Network topology**          | `diagram-drawio`                  | —                                            |
| **Design a UI**               | `design`                          | `architecture`                               |
| **Security audit**            | `audit --focus security`          | `coding`, `review-standards`                 |
| **Performance audit**         | `audit --focus performance`       | `coding`                                     |
| **Plan an implementation**    | `plan`                            | `architecture`, `principal-engineer`         |
| **Write a spec**              | `spec`                            | `docs-guidelines`                            |
| **Research a topic**          | `research`                        | —                                            |
| **Run acceptance tests**      | `test`                            | —                                            |
| **Set up new project**        | `project`                         | `setup`                                      |
| **Hand off session**          | `handoff`                         | —                                            |
| **Configure tools/MCP**       | `setup`                           | —                                            |
| **Create a data chart**       | `chart`                           | —                                            |
| **Multi-model review**        | `team`                            | any review skill                             |
| **Any task (auto-route)**     | `use`                             | routes to the right skill(s)                 |


---

## Agents

18 shared agent definitions in `agents/` provide reusable prompts for child agents spawned by skills during parallel execution. All agents use `memory: project` for cross-session learning and `effort: high` for quality output.


| Agent                    | Purpose                                                  |
| ------------------------ | -------------------------------------------------------- |
| `adk-code-reviewer`      | Multi-perspective code review                            |
| `adk-repo-auditor`       | Whole-codebase architecture and maintainability review   |
| `adk-security-reviewer`  | Security-focused code review (OWASP, auth, data)         |
| `adk-pr-fixer`           | Read PR comments and apply targeted code fixes           |
| `adk-doc-reviewer`       | Technical document review                                |
| `adk-doc-writer`         | Technical document creation with audience-aware structure |
| `adk-code-snippet-agent` | Code snippet extraction and formatting                   |
| `adk-research-agent`     | Primary-source and implementation research               |
| `adk-migration-analyst`  | Framework/library migration analysis                     |
| `adk-frontend-designer`  | Frontend and design system direction                     |
| `adk-intent-analyst`     | Expand user intent, assumptions, complexity, and routing |
| `adk-plan-reviewer`      | Review plans for completeness and sequencing             |
| `adk-progress-tracker`   | Monitor execution progress, stalls, and recovery         |
| `adk-consensus-agent`    | Merge and reconcile multi-agent outputs                  |
| `adk-source-publisher`   | Publish to GitHub, Bitbucket, Confluence, or Google Docs |
| `adk-guideline-auditor`  | Audit guidelines against authoritative sources           |
| `adk-test-agent`         | Test writing, coverage analysis, and failure diagnosis    |
| `adk-debugger`           | Root cause analysis and systematic fault isolation        |


## MCP Integrations

Some skills use MCP servers for source-native operations. Most skills work without any MCP.


| MCP Server   | Used By                                  | Transport                                   |
| ------------ | ---------------------------------------- | ------------------------------------------- |
| GitHub       | code-review-pr, code-review-fix, publish | HTTP (`https://api.githubcopilot.com/mcp/`) |
| Bitbucket    | code-review-pr, code-review-fix          | detect-from-input                           |
| Confluence   | docs-review, publish, docs-write         | detect-from-input                           |
| Google Drive | docs-review, docs-write                  | detect-from-input                           |


## Workspace Context

ADK skills can pick up project-specific defaults from a `.adk/context.yaml` file in your workspace root. This avoids repeated questions about your stack, conventions, and preferences.

```yaml
# .adk/context.yaml — optional, placed in your project root
project:
  name: my-app
  description: E-commerce platform

stack:
  language: typescript
  framework: next.js
  runtime: node
  test_runner: vitest
  package_manager: pnpm

conventions:
  commit_format: conventional
  branch_pattern: "feat|fix|chore|docs/<ticket>-<description>"
  review_checklist: .github/review-checklist.md

preferences:
  verbosity: standard
  diagram_engine: mermaid
  doc_format: markdown
```

When a context file is present, skills use it to:
- Skip "what framework are you using?" questions
- Auto-detect coding guidelines to load
- Apply the right commit format and branch naming
- Use preferred diagram engine and doc format

## Composable Workflows

Define reusable multi-skill pipelines in `workflows/`. See [`workflows/README.md`](./workflows/README.md) for the format.

Included pipelines:

| Workflow | Description |
|----------|-------------|
| `full-feature.yaml` | Spec → Plan → Implement → Commit → Review → Changelog |
| `quick-review.yaml` | Review → Fix → PR Description |
| `doc-update.yaml` | Review docs → Update → Regenerate repo docs |

Run a workflow: `Run the workflow in workflows/full-feature.yaml for <your task>`

## Hooks

ADK includes hooks that run automatically:


| Event                      | Purpose                                    |
| -------------------------- | ------------------------------------------ |
| `PreToolUse` (Bash)        | Blocks dangerous git operations (force push, hard reset on main) |
| `PostToolUse` (Edit/Write) | Validates SKILL.md frontmatter conventions |
| `Stop`                     | Checks task completion before ending       |
| `SessionStart` (compact)   | Re-injects ADK context after compaction    |


## Naming Convention


| Install Method   | Invocation Pattern  | Example               |
| ---------------- | ------------------- | --------------------- |
| Claude Plugin    | `/adk:<skill-name>` | `/adk:code-review-pr` |
| skills.sh        | `/<skill-name>` | `/code-review-pr` |
| Local plugin-dir | `/adk:<skill-name>` | `/adk:code-review-pr` |


The `name` field in each skill's frontmatter matches the directory name (e.g., `code-review-pr`). No `adk-` prefix — the plugin provides the `adk:` namespace automatically. When installed via skills.sh, the `name` field is used directly as `/<skill-name>`. The `description` field retains an `adk -` prefix for identification when skills are used outside the plugin.

## Output Style

All ADK output follows **concise by default**:

- **Lead with the conclusion**, then supporting reasoning
- **Short version first** — after completing a task, show the compact result
- **Offer to elaborate** — end with "Need a detailed breakdown?" when the output could be expanded
- **No preamble** — skip "Great question!", "I'd be happy to help", "Let me think about this..."
- **No trailing summaries** — don't restate what was just done
- **Verbosity flag** — pass `--verbosity detailed` to get full output without asking, or `--verbosity short` for one-liners

## Plugin Structure

```
agents-devkit/                        52 skills · 18 agents · ~42K lines
├── .claude-plugin/
│   └── plugin.json                   Plugin manifest (name: adk)
├── mcp-config.json                   MCP server configurations
├── hooks/hooks.json                  Hook configurations
├── settings.json                     Default settings (routes to /adk:use)
├── agents/                           18 shared agent definitions
├── settings/                         MCP setup guides
├── templates/skill/                  Canonical templates and propagation
│   ├── common/                       Cross-skill files (help-format, project-guidelines)
│   └── scripts/                      Preflight and propagation scripts
├── skills/                           52 skills (only relevant ones load per task)
│   ├── use/                          Routing — default orchestrator
│   ├── code-review/                  Routing — review type detection
│   ├── docs/                         Routing — documentation task routing
│   ├── dev/                          Routing — development task routing
│   ├── diagram/                      Routing — diagram engine detection
│   │
│   ├── workflow/                     Guideline — 6-phase workflow (lazy-loaded)
│   ├── communication/                Guideline — concise-by-default output rules
│   ├── coding/                       Guideline — 16 coding guideline files (lazy-loaded by stack)
│   ├── docs-guidelines/              Guideline — 24 doc guideline files (lazy-loaded by type)
│   ├── (+ 12 more guideline skills)
│   │
│   ├── github/                       Connector — GitHub via gh CLI
│   ├── bitbucket/                    Connector — Bitbucket via API
│   ├── confluence/                   Connector — Confluence via API
│   ├── jira/                         Connector — Jira via API
│   │
│   ├── code-review-pr/              Task — PR review (11 conditional stages)
│   ├── dev-build/                    Task — implement/debug/TDD (7 conditional stages)
│   ├── docs-write/                   Task — formal docs (16 conditional stages)
│   ├── team/                         Task — multi-model agent dispatch
│   ├── (+ 26 more task skills)
├── manifest.json                     Upstream source tracking
├── skills-manifest.json              Programmatic skill discovery index
├── workflows/                        Composable workflow pipelines (YAML)
├── scripts/                          Repo-level utilities
│   ├── generate-skills-manifest.py   Regenerate skills-manifest.json
│   └── add-maturity-field.py         Add maturity to new SKILL.md files
└── docs/                             Documentation site (@pagesmith/docs)
```

## Guidelines

Skills automatically load relevant guidelines based on repository type:

- **Coding guidelines** (`skills/coding/references/coding-guidelines/`) — 16 files: general, architecture, frontend, backend (Java, Kotlin, Node.js, Python), design system, JS/TS library, scripts, API design, testing, observability, security, expressive code
- **Document guidelines** (`skills/docs-guidelines/references/doc-guidelines/`) — 24 files: general, RFC, ADR, article, blog, changelog, runbook, system design, tool evaluation, research, deep dive, and more
- **Architecture guidelines** (`skills/architecture/`) — frontend, backend, fullstack, and infrastructure patterns with anti-pattern detection

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for how to add skills, agents, and guidelines.

## AI-Readable Summary

See [llms.txt](./llms.txt) for a compact AI-readable summary of this repository.

## License

MIT