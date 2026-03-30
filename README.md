# DevKit

Shared skills pack for software-development agents: code review, documentation, research, codebase audits, diagrams, engineering workflows, and source-native publishing.

Route general prompts through `/use` first. Invoke a specific skill directly only when the user explicitly names it or clearly wants that exact workflow. Every skill supports `--help` to see parameters and behavior variations.

Inspired by [superpowers](https://github.com/obra/superpowers). Diagram skills from [diagramkit](https://github.com/sujeet-pro/diagramkit). Markdown capabilities informed by [pagesmith](https://github.com/sujeet-pro/pagesmith).

## Philosophy

- **Human-readable, maintainable, extensible** — code and docs should be clear to the next person
- **Minimum changes required** — do only what is needed, no gold-plating
- **No over-engineering** — don't implement features that might be needed in the future
- **Markdown by default** — all outputs are markdown unless the user requests otherwise
- **Self-sufficient skills** — every skill works independently, regardless of installation method
- **Parallel agentic teams** — non-trivial work uses child agents with distinct roles
- **Human-in-the-loop** — decisions happen interactively, execution happens automatically
- **Approach selection** — after initial research, present 2-3 approaches for user to choose from

## The 6-Phase Workflow

Every non-trivial skill follows a standardized 6-phase workflow. Human interaction happens first, not after hidden research.

| Phase | Name | What Happens |
|-------|------|-------------|
| 0 | **Intent Expansion** | Expand the prompt, show concise reasoning, identify skills/tools/MCPs, and confirm direction early |
| 1 | **Research & Options** | Research the problem, scan the codebase, and surface 2-3 viable options |
| 2 | **Approach Selection** | Let the user choose, mix, or simplify the direction |
| 3 | **Planning** | Produce an executable plan with files, sequencing, and verification |
| 4 | **Execute** | Run the approved plan |
| 5 | **Validate & Learn** | Validate the result, simplify when needed, and explain the key takeaway |

### Complexity-Adaptive Skipping

| Complexity | Files | Phases Used |
|------------|-------|-------------|
| Trivial | 1 | 0 inline, 4, 5 quick |
| Small | 2-3 | 0 inline, 1 lite, 3 brief, 4, 5 |
| Medium | 4-8 | All 6 phases |
| Large | >8 | All 6 phases with PE check and phased execution |

## Install

### For All Agents (Recommended)

```bash
# Install all skills
npx skills add sujeet-pro/agents-devkit

# Install specific skills
npx skills add sujeet-pro/agents-devkit/skills/review
npx skills add sujeet-pro/agents-devkit/skills/write
```

Visit [skills.sh](https://skills.sh) for more details.

### Claude Code Only

```bash
/plugin marketplace add sujeet-pro/agents-devkit
/plugin install devkit@devkit-marketplace
```

Skills become available as `/devkit:<skill-name>` immediately.

### Contributors — Local Clone

```bash
git clone https://github.com/sujeet-pro/agents-devkit.git ~/.devkit
```

## Skills (18)

### Core Skills

Each skill auto-detects the right mode from context, or accepts explicit flags. Use `--help` on any skill to see all parameters.

| Skill | Area | Description |
|-------|------|-------------|
| `/review` | Review | Code review: PR, local, branch + fix/comment/interactive |
| `/develop` | Dev | Implement features, fix bugs, enhance code, TDD |
| `/write` | Docs | Create/update any document (ADR, RFC, blog, changelog, etc.) |
| `/plan` | Plan | Brainstorm, write, execute, and track implementation plans |
| `/spec` | Spec | Write specs, analyze consistency, generate checklists |
| `/research` | Research | Multi-agent research with citations |
| `/diagram` | Diagram | Create diagrams (Mermaid, Excalidraw, draw.io, Graphviz) |
| `/design` | Design | UI/UX design direction + visual audit |
| `/audit` | Quality | Audit: codebase, security, performance, dependencies |
| `/review-doc` | Review | Review documents (local, Confluence, Google Docs) |
| `/test` | QA | User acceptance testing with interactive verification |
| `/project` | Project | Initialize projects, manage milestones and ideas |
| `/handoff` | Session | Pause/resume work sessions, context threads |
| `/setup` | Setup | Configure CLI tools and MCP servers |

### Meta Skills

| Skill | Description |
|-------|-------------|
| `/team` | Multi-model review, agent team dispatch |
| `/use` | Orchestrator: expand intent, confirm the route, approve the plan, then execute |

### Helper Skills (auto-invoked)

| Skill | Description |
|-------|-------------|
| `/coding` | Detects repo stack, loads matching coding guidelines |
| `/doc-writing` | Detects document type, loads matching writing guidelines |

## Using --help

Every skill supports `--help` to see parameters and behavior variations:

```
/review --help
/write --help
/develop --help
```

## Output Modes

All skills support `--verbosity short|standard|detailed`:

| Mode | Use | Characteristics |
|------|-----|-----------------|
| `short` | Quick feedback | 1-3 lines, senior dev tone |
| `standard` | PR comments, reviews (default) | Full structured format, all sections |
| `detailed` | Documentation, audits | Expanded with rationale and examples |

For PR comments, verbosity auto-selects based on severity: Blocker/Critical use detailed, Should Have/May Have use standard, Nitpick/Question use short.

## Agents

Shared agent definitions in `agents/` provide reusable prompts for child agents spawned by skills.

| Agent | Purpose |
|-------|---------|
| `code-reviewer` | Multi-perspective code review |
| `repo-auditor` | Whole-codebase architecture and maintainability review |
| `doc-reviewer` | Technical document review |
| `research-agent` | Primary-source and implementation research |
| `source-publisher` | Publish to GitHub, Bitbucket, Confluence, or Google Docs |
| `consensus-agent` | Merge and reconcile multi-agent outputs |
| `frontend-designer` | Frontend and design system direction |
| `pr-fixer` | Read PR comments and apply targeted code fixes |
| `security-reviewer` | Security-focused code review (OWASP, auth, data) |
| `migration-analyst` | Framework/library migration analysis |
| `guideline-auditor` | Audit guidelines against authoritative sources |
| `code-snippet-agent` | Code snippet extraction and formatting |
| `intent-analyst` | Expand user intent, assumptions, complexity, and routing choices |
| `plan-reviewer` | Review implementation plans for completeness and sequencing |
| `progress-tracker` | Monitor execution progress, stalls, and recovery options |

## Guidelines

Skills automatically load relevant guidelines based on repository type:

- **Coding guidelines** (`skills/coding/guidelines/`) — 16 files: general, architecture, frontend, backend (Java, Kotlin, Node.js, Python), design system, JS/TS library, scripts, API design, testing, observability, security, expressive code
- **Document guidelines** (`skills/doc-writing/guidelines/`) — 24 files: general, RFC, ADR, article, blog, changelog, runbook, system design, tool evaluation, research, deep dive, and more

## MCP Integrations

Some skills use MCP servers for source-native operations. Most skills work without any MCP.

| MCP Server | Used By | Setup |
|------------|---------|-------|
| GitHub | review (PR mode), publish | [mcp-setup.md](./settings/mcp-setup.md) |
| Bitbucket | review (PR mode) | [mcp-setup.md](./settings/mcp-setup.md) |
| Confluence | review-doc, publish, write | [mcp-setup.md](./settings/mcp-setup.md) |
| Google Drive | review-doc, write | [mcp-setup.md](./settings/mcp-setup.md) |

## Repo Layout

```
agents-devkit/
├── templates/skill/         Canonical templates and shared references
│   ├── SKILL-TEMPLATE.md    Boilerplate for new skills
│   ├── references/          Master copies of shared reference docs
│   ├── common/              Cross-skill guidelines and conventions
│   └── scripts/             Preflight, propagation, and shared Textual TUI scripts
├── agents/                  Shared agent definitions (15 agents)
├── settings/                MCP setup guides
├── skills/
│   ├── coding/              Helper: coding guidelines loader (16 guidelines)
│   ├── doc-writing/         Helper: document guidelines loader (24 guidelines)
│   ├── review/              Code review
│   ├── develop/             Development
│   ├── write/               Documentation
│   ├── plan/                Planning
│   ├── spec/                Specs
│   ├── research/            Research
│   ├── diagram/             Diagrams
│   ├── design/              UI/UX design
│   ├── audit/               Codebase/security/performance/dependency audits
│   ├── review-doc/          Document review
│   ├── test/                User acceptance testing
│   ├── project/             Project management
│   ├── handoff/             Session management
│   ├── setup/               CLI tools and MCP setup
│   ├── team/                Multi-model review, agent dispatch
│   ├── use/                 Orchestrator
│   └── <skill>/             Each skill directory contains:
│       ├── SKILL.md         Skill definition with the 6-phase workflow
│       ├── stages/          Conditional stage files (multi-stage only)
│       ├── references/      Reference documents (self-contained)
│       └── scripts/         Preflight and utility scripts
├── .claude-plugin/          Claude Code plugin metadata
├── manifest.json            Upstream source tracking
└── README.md
```

## Updating Shared References

Edit files in `templates/skill/references/` or `templates/skill/common/`, then propagate:

```bash
python3 templates/skill/scripts/propagate.py        # Apply to all skills
python3 templates/skill/scripts/propagate.py --dry-run  # Preview changes
```

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for how to add skills, agents, and guidelines.
