# Agent Development Kit (ADK)

Principal-engineer-grade skills for software development agents. Code review, documentation, research, codebase audits, diagrams, planning, migrations, refactoring, and MCP-native publishing.

Route general prompts through `/adk:use` first. Invoke a specific skill directly only when you explicitly name it or clearly want that exact workflow. Every skill supports `--help`.

Inspired by [superpowers](https://github.com/obra/superpowers). Diagram skills from [diagramkit](https://github.com/sujeet-pro/diagramkit). Markdown capabilities from [pagesmith](https://github.com/sujeet-pro/pagesmith).

## Philosophy

- **Human-in-the-loop** — decisions happen interactively, execution happens automatically
- **Plan first, then implement** — every non-trivial task follows a 6-phase workflow with approval gates
- **Self-sufficient skills** — every skill works independently with inline fallbacks for shared knowledge; can invoke other skills when available
- **Parallel agentic teams** — non-trivial work uses child agents with distinct roles
- **Principal engineer lens** — do we need this? What's the simplest version? What are the alternatives?
- **Markdown by default** — all outputs are markdown unless the user requests otherwise
- **Auto mode** — pass `--auto` to skip confirmations and execute the full workflow automatically
- **Dual-install support** — works as a Claude plugin (`/adk:skill`) or via skills.sh (`/adk-skill`)

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

### Using skills.sh

```bash
# Install all skills
npx skills add sujeet-pro/agents-devkit

# Install specific skills
npx skills add sujeet-pro/agents-devkit/skills/code-review-pr
npx skills add sujeet-pro/agents-devkit/skills/dev-build
```

When installed via skills.sh, skills are prefixed with `adk-` (e.g., `/adk-code-review-pr`, `/adk-dev-build`). This prevents conflicts with other skill packs.

Visit [skills.sh](https://skills.sh) for more details.

### Local Development

```bash
git clone https://github.com/sujeet-pro/agents-devkit.git ~/.devkit
claude --plugin-dir ~/.devkit
```

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

ADK skills are organized into three categories:

### Guideline Skills (shared helpers)

Provide reusable knowledge and standards. Auto-invoked by task skills. Each task skill includes inline fallback summaries so it works even if the guideline skill is not installed.


| Skill                | Invocation                | What It Provides                                                                  |
| -------------------- | ------------------------- | --------------------------------------------------------------------------------- |
| `workflow`           | `/adk:workflow`           | 6-phase workflow framework with complexity-adaptive phase skipping                |
| `communication`      | `/adk:communication`      | Communication style: lead with conclusion, no preamble, concrete specifics        |
| `principal-engineer` | `/adk:principal-engineer` | PE questioning: need? simplest? alternatives? maintenance? clarity?               |
| `agentic-teams`      | `/adk:agentic-teams`      | Child-agent contract: team shapes for review, research, docs, security, migration |
| `output-format`      | `/adk:output-format`      | Verbosity modes, PR comment templates, priority/principle labels                  |
| `interaction`        | `/adk:interaction`        | Inline protocols: intent confirm, approach select, plan approve, review findings  |
| `preflight-check`    | `/adk:preflight-check`    | Preflight validations for dependencies, MCP, and tool readiness                   |
| `review-standards`   | `/adk:review-standards`   | Review pipeline, comment template, source routing, postback rules                 |
| `coding`             | `/adk:coding`             | Detects repo stack, loads matching coding guidelines (16 guideline files)         |
| `docs-guidelines`    | `/adk:docs-guidelines`    | Detects document type, loads matching writing guidelines (24 guideline files)     |
| `docs-md`            | `/adk:docs-md`            | Detects markdown target (pagesmith/GitHub/plain), loads formatting guidelines     |
| `architecture`       | `/adk:architecture`       | Architecture patterns, principles, and anti-pattern detection                     |


### Task Skills (user-facing)

Perform specific engineering tasks. Each is self-sufficient with inline fallback summaries for all shared knowledge.


| Skill                | Area     | Invocation                | Description                                                  |
| -------------------- | -------- | ------------------------- | ------------------------------------------------------------ |
| `code-review-pr`     | Review   | `/adk:code-review-pr`     | Code review: PR, local, branch + fix/comment/interactive     |
| `code-review-repo`   | Review   | `/adk:code-review-repo`   | Whole-repo review with prioritized improvement plan          |
| `code-review-fix`    | Review   | `/adk:code-review-fix`    | Fix PR comments, reply to reviewers, mark resolved           |
| `docs-review`        | Review   | `/adk:docs-review`        | Review documents (local, Confluence, Google Docs)            |
| `dev-build`          | Dev      | `/adk:dev-build`          | Implement features, fix bugs, enhance code, TDD              |
| `dev-refactor`       | Dev      | `/adk:dev-refactor`       | Extract, rename, restructure, simplify, modernize code       |
| `dev-migrate`        | Dev      | `/adk:dev-migrate`        | Framework/library migration with breaking change analysis    |
| `dev-commit`         | Dev      | `/adk:dev-commit`         | Smart commit messages and PR descriptions                    |
| `docs-write`         | Docs     | `/adk:docs-write`         | Create/update formal documents (ADR, RFC, blog, changelog)   |
| `docs-repo`          | Docs     | `/adk:docs-repo`          | Generate comprehensive repo documentation (pagesmith)        |
| `docs-review`        | Docs     | `/adk:docs-review`        | Review docs for accuracy, completeness, clarity              |
| `docs-crud`          | Docs     | `/adk:docs-crud`          | Manage doc lifecycle: create, update, improve, comment-reply |
| `plan`               | Plan     | `/adk:plan`               | Brainstorm, write, execute, and track implementation plans   |
| `spec`               | Spec     | `/adk:spec`               | Write specs, analyze consistency, generate checklists        |
| `research`           | Research | `/adk:research`           | Multi-agent research with citations                          |
| `diagram`            | Diagram  | `/adk:diagram`            | Create diagrams (routes to engine-specific skill)            |
| `diagram-mermaid`    | Diagram  | `/adk:diagram-mermaid`    | Mermaid diagrams with full syntax reference (20+ types)      |
| `diagram-excalidraw` | Diagram  | `/adk:diagram-excalidraw` | Excalidraw hand-drawn style architecture diagrams            |
| `diagram-graphviz`   | Diagram  | `/adk:diagram-graphviz`   | Graphviz DOT diagrams for dependency graphs                  |
| `diagram-drawio`     | Diagram  | `/adk:diagram-drawio`     | Draw.io precise layout for network/enterprise architecture   |
| `design`             | Design   | `/adk:design`             | UI/UX design direction + visual audit                        |
| `audit`              | Quality  | `/adk:audit`              | Audit: codebase, security, performance, dependencies         |
| `test`               | QA       | `/adk:test`               | User acceptance testing with interactive verification        |
| `project`            | Project  | `/adk:project`            | Initialize projects, manage milestones and ideas             |
| `handoff`            | Session  | `/adk:handoff`            | Pause/resume work sessions, context threads                  |
| `setup`              | Setup    | `/adk:setup`              | Configure CLI tools, MCP servers, and hooks                  |
| `deps-tracker`       | Project  | `/adk:deps-tracker`       | Track upstream dependencies and sync updates                 |


### Routing Skills (orchestrators)

Coordinate and route work across other skills.


| Skill  | Invocation  | Description                                                               |
| ------ | ----------- | ------------------------------------------------------------------------- |
| `use`  | `/adk:use`  | Default orchestrator: expand intent, confirm route, approve plan, execute |
| `team` | `/adk:team` | Multi-model review, agent team dispatch                                   |


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
| **Multi-model review**        | `team`                            | any review skill                             |
| **Any task (auto-route)**     | `use`                             | routes to the right skill(s)                 |


---

## Agents (15)

Shared agent definitions in `agents/` provide reusable prompts for child agents spawned by skills.


| Agent                | Purpose                                                  |
| -------------------- | -------------------------------------------------------- |
| `code-reviewer`      | Multi-perspective code review                            |
| `repo-auditor`       | Whole-codebase architecture and maintainability review   |
| `doc-reviewer`       | Technical document review                                |
| `research-agent`     | Primary-source and implementation research               |
| `source-publisher`   | Publish to GitHub, Bitbucket, Confluence, or Google Docs |
| `consensus-agent`    | Merge and reconcile multi-agent outputs                  |
| `frontend-designer`  | Frontend and design system direction                     |
| `pr-fixer`           | Read PR comments and apply targeted code fixes           |
| `security-reviewer`  | Security-focused code review (OWASP, auth, data)         |
| `migration-analyst`  | Framework/library migration analysis                     |
| `guideline-auditor`  | Audit guidelines against authoritative sources           |
| `code-snippet-agent` | Code snippet extraction and formatting                   |
| `intent-analyst`     | Expand user intent, assumptions, complexity, and routing |
| `plan-reviewer`      | Review plans for completeness and sequencing             |
| `progress-tracker`   | Monitor execution progress, stalls, and recovery         |


## MCP Integrations

Some skills use MCP servers for source-native operations. Most skills work without any MCP.


| MCP Server   | Used By                                  | Transport                                   |
| ------------ | ---------------------------------------- | ------------------------------------------- |
| GitHub       | code-review-pr, code-review-fix, publish | HTTP (`https://api.githubcopilot.com/mcp/`) |
| Bitbucket    | code-review-pr, code-review-fix          | detect-from-input                           |
| Confluence   | docs-review, publish, docs-write         | detect-from-input                           |
| Google Drive | docs-review, docs-write                  | detect-from-input                           |


## Hooks

ADK includes hooks that run automatically:


| Event                      | Purpose                                    |
| -------------------------- | ------------------------------------------ |
| `PostToolUse` (Edit/Write) | Validates SKILL.md frontmatter conventions |
| `Stop`                     | Checks task completion before ending       |
| `SessionStart` (compact)   | Re-injects ADK context after compaction    |


## Naming Convention


| Install Method   | Invocation Pattern  | Example               |
| ---------------- | ------------------- | --------------------- |
| Claude Plugin    | `/adk:<skill-name>` | `/adk:code-review-pr` |
| skills.sh        | `/adk-<skill-name>` | `/adk-code-review-pr` |
| Local plugin-dir | `/adk:<skill-name>` | `/adk:code-review-pr` |


The `name` field in each skill's frontmatter is set to `adk-<skill-name>`. When installed as a Claude plugin, the plugin namespace `adk:` is used and the folder name determines the command. When installed via skills.sh, the `name` field is used directly, giving `/adk-<skill-name>`.

## Plugin Structure

```
agents-devkit/
├── .claude-plugin/
│   └── plugin.json          Plugin manifest (name: adk)
├── .mcp.json                MCP server configurations
├── hooks/
│   └── hooks.json           Hook configurations
├── settings.json            Default settings (routes to /adk:use)
├── agents/                  15 shared agent definitions
├── settings/                MCP setup guides
├── templates/skill/         Canonical templates and shared references
│   ├── SKILL-TEMPLATE.md    Boilerplate for new skills
│   ├── references/          Master copies (deprecated — now helper skills)
│   ├── common/              Cross-skill guidelines (help-format, project-guidelines)
│   └── scripts/             Preflight and propagation scripts
├── skills/
│   ├── use/                 Routing — orchestrates all other skills
│   ├── team/                Routing — multi-model agent team dispatch
│   │
│   ├── workflow/            Guideline — 6-phase workflow framework
│   ├── communication/       Guideline — communication style rules
│   ├── principal-engineer/  Guideline — PE questioning framework
│   ├── agentic-teams/       Guideline — child-agent contract and team shapes
│   ├── output-format/       Guideline — verbosity modes, templates, labels
│   ├── interaction/         Guideline — inline interaction protocols
│   ├── preflight-check/     Guideline — dependency and MCP validation
│   ├── review-standards/    Guideline — review pipeline and comment template
│   ├── coding/              Guideline — coding guidelines (16 files)
│   ├── docs-guidelines/     Guideline — doc guidelines (24 files)
│   ├── docs-md/             Guideline — markdown formatting guidelines
│   ├── architecture/        Guideline — architecture patterns
│   │
│   ├── code-review-pr/      Task — code review (PR, local, branch)
│   ├── code-review-repo/    Task — whole-repo review
│   ├── code-review-fix/     Task — fix PR comments
│   ├── docs-review/         Task — document review
│   ├── dev-build/           Task — feature implementation, debugging, TDD
│   ├── dev-refactor/        Task — code refactoring
│   ├── dev-migrate/         Task — framework/library migration
│   ├── dev-commit/          Task — smart commits and PR descriptions
│   ├── docs-write/          Task — formal documents (ADR, RFC, blog, etc.)
│   ├── docs-repo/           Task — generate repo documentation
│   ├── docs-review/         Task — review documentation
│   ├── docs-crud/           Task — documentation lifecycle management
│   ├── plan/                Task — implementation planning
│   ├── spec/                Task — specifications and checklists
│   ├── research/            Task — multi-agent research
│   ├── diagram/             Task — diagram routing (to engine-specific skills)
│   ├── diagram-mermaid/     Task — Mermaid diagrams (full reference)
│   ├── diagram-excalidraw/  Task — Excalidraw diagrams (full reference)
│   ├── diagram-graphviz/    Task — Graphviz DOT diagrams (full reference)
│   ├── diagram-drawio/      Task — Draw.io diagrams (full reference)
│   ├── design/              Task — UI/UX design
│   ├── audit/               Task — codebase/security/performance audits
│   ├── test/                Task — user acceptance testing
│   ├── project/             Task — project management
│   ├── handoff/             Task — session management
│   ├── setup/               Task — CLI tools, MCP, hooks setup
│   └── deps-tracker/        Task — upstream dependency tracking
├── manifest.json            Upstream source tracking
└── docs/                    Documentation site (@pagesmith/docs)
```

## Guidelines

Skills automatically load relevant guidelines based on repository type:

- **Coding guidelines** (`skills/coding/references/coding-guidelines/`) — 16 files: general, architecture, frontend, backend (Java, Kotlin, Node.js, Python), design system, JS/TS library, scripts, API design, testing, observability, security, expressive code
- **Document guidelines** (`skills/docs-guidelines/references/doc-guidelines/`) — 24 files: general, RFC, ADR, article, blog, changelog, runbook, system design, tool evaluation, research, deep dive, and more
- **Architecture guidelines** (`skills/architecture/`) — frontend, backend, fullstack, and infrastructure patterns with anti-pattern detection

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for how to add skills, agents, and guidelines.

## License

MIT