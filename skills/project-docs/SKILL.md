---
name: project-docs
description: Write, review, or update project documentation by scanning a codebase — produces architecture diagrams, quick starts, and API references
user_invocable: true
arguments:
  - name: mode
    description: "Mode: write, review, update (default: write). 'review' analyzes existing docs against the codebase. 'update' refreshes docs to match current code."
    required: false
  - name: repo
    description: "Path to repository root (default: current directory)"
    required: false
  - name: source
    description: "Path to existing documentation to review/update (for review/update modes)"
    required: false
  - name: format
    description: "Output format: markdown, confluence, google-doc (default: markdown)"
    required: false
  - name: depth
    description: "Depth: quick, standard, comprehensive (default: standard)"
    required: false
---

# Project Documentation — Write, Review & Update

> **Dependencies**: This skill works best with the full devkit installed (`/plugin install devkit-full@claude-devkit` or `./install.sh`). It uses guidelines from `guidelines/document/`, and delegates to agents (`code-snippet-agent`, `diagram-agent`). If guidelines or agents are missing, the skill still works but with reduced quality enforcement.

Generate, review, or update project documentation by scanning a codebase. Produces architecture diagrams, quick start guides, configuration references, and API documentation — all derived from what actually exists in the code.

## Mode Detection

If `mode` is not specified, auto-detect:
- If `source` is provided → `review` (analyze existing docs against the codebase)
- If `source` is not provided and docs already exist (README.md, docs/) → `update` (refresh existing docs)
- If no existing docs found → `write` (generate from scratch)

## Agent & Skill Delegation

**Always use the devkit's own agents and skills for delegation:**

| Task | Delegate To |
|------|-------------|
| Research (external context) | `/research` skill (spawns **research-agent**) — for framework docs, best practices, etc. |
| Architecture diagrams | `/diagram` skill → **diagram-agent** → excalidraw-agent or mermaid-agent |
| Code blocks | **code-snippet-agent** (expressive-code conventions) |
| Markdown output | `/markdown` skill |
| Confluence publishing | `/confluence-publish` skill |

---

## Write Mode

### Step 1 — Codebase Scanning

Use Glob, Grep, and Read to discover the project's structure and conventions:

**Package managers and build systems:**
- `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
- `pom.xml`, `build.gradle`, `build.gradle.kts`
- `pyproject.toml`, `setup.py`, `requirements.txt`, `Pipfile`
- `go.mod`, `go.sum`
- `Cargo.toml`, `Cargo.lock`
- `Makefile`, `Justfile`, `Taskfile.yml`

**Entry points and application structure:**
- Main files (`main.go`, `main.py`, `index.ts`, `App.tsx`, `Program.cs`)
- Route definitions, controllers, handlers
- Middleware and plugin registrations
- Event listeners and message consumers

**Data layer:**
- Database models, entities, schemas
- Migration files and their sequence
- ORM configuration files
- Database connection/pool setup

**Infrastructure and deployment:**
- `Dockerfile`, `docker-compose.yml`
- Kubernetes manifests (`k8s/`, `helm/`, `kustomize/`)
- Terraform/Pulumi/CDK files
- CI/CD configs (`.github/workflows/`, `Jenkinsfile`, `.gitlab-ci.yml`, `bitbucket-pipelines.yml`)

**Testing:**
- Test directories and naming conventions
- Test configuration files (jest.config, pytest.ini, etc.)
- Test fixtures and factories
- Coverage configuration

**Existing documentation:**
- `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`
- `docs/` directory contents
- API documentation (OpenAPI/Swagger specs)
- Inline documentation patterns (JSDoc, docstrings, godoc)

### Step 2 — Load Guidelines

Load the following guidelines:

1. `guidelines/document/project.md` — project documentation structure and conventions
2. `guidelines/document/general.md` — baseline markdown and document conventions

**Repo-level guideline discovery** (highest priority — overrides devkit guidelines):

| Category | Paths to Check (in priority order) |
|----------|-----------------------------------|
| **Document guidelines** | `docs/guidelines/document/`, `guidelines/document/`, `.github/guidelines/`, `CLAUDE.md` (section: `## Document Guidelines` or `## Writing Guidelines`) |
| **Coding guidelines** | `docs/guidelines/coding/`, `guidelines/coding/`, `coding-guidelines/`, `CLAUDE.md` (section: `## Coding Guidelines` or `## Code Style`) |
| **Markdown conventions** | `.markdown-guidelines.md`, `MARKDOWN.md`, `docs/markdown-style.md` |

Repo-level guidelines take **higher priority** than devkit guidelines.

### Step 3 — Architecture Diagram

Delegate to `/diagram` skill:

```
/diagram --engine=excalidraw --description=analyze
```

The diagram skill should analyze the codebase and generate an architecture diagram showing:
- Major components/services and their responsibilities
- Data flow between components
- External dependencies (databases, caches, queues, APIs)
- Client-facing interfaces (HTTP, gRPC, WebSocket, CLI)

This diagram goes at the top of the Architecture section.

### Step 4 — Outline

Present the outline to the user for approval:

1. **Project Overview** — What the project does, who it is for, why it exists. Extract from existing README or infer from code.
2. **Architecture** — Diagram + component descriptions. Each major component gets a subsection explaining its role, key files, and design decisions.
3. **Getting Started / Quick Start** — Install dependencies, configure environment, run the project, verify it works. Must be completeable in under 5 minutes.
4. **Configuration Reference** — All environment variables, config files, feature flags, and their defaults. Extract from actual code (env parsing, config loading).
5. **API Reference** (if applicable) — Routes, endpoints, methods, request/response shapes. Extract from route definitions, OpenAPI specs, or handler signatures.
6. **Deployment Guide** — Docker, cloud platforms, local production-like setup. Extract from Dockerfiles, CI configs, and deployment scripts.
7. **Contributing Guide** — PR process, testing requirements, code style, branch naming. Extract from existing CONTRIBUTING.md or infer from CI checks.

Wait for user approval before proceeding.

### Step 5 — Writing

Delegate to specialized agents:

**Main writing:**
- Consumer-first explanations — write for someone who just cloned the repo.
- Working examples — every command and code snippet must actually work.
- Explain the "why" behind architectural decisions where visible from the code.
- Link to source files where relevant: "See `src/middleware/auth.ts` for implementation."

**Code blocks:**
- Delegate to the **code-snippet-agent**.
- Commands must be realistic and copy-pasteable.
- Extract real commands from `package.json` scripts, Makefiles, etc. — do not invent commands.
- Show expected output where it helps verify success.

**Quick Start verification:**
- The quick start section must contain commands extracted from actual project tooling.
- If the project uses `make dev`, document `make dev` — not a guessed `npm start`.
- Include a "verify it works" step (e.g., `curl localhost:3000/health`).

### Step 6 — Output

Use the `/markdown` skill for file generation:

- `title` = project name (from package.json, go.mod, etc.)
- `frontmatter` = yes (project docs benefit from metadata: version, last updated, maintainers)
- `confluence-sync` = yes if `format=confluence`
- `doc-type` = project

For non-markdown formats:
- `confluence` → Generate markdown first, then publish via `/confluence-publish`
- `google-doc` → Generate markdown first, then convert via Google Drive MCP tools

### Step 7 — Depth Adjustments

| Depth | Sections Included | Detail Level |
|---|---|---|
| `quick` | Overview + Architecture + Quick Start | Minimal — just enough to get running |
| `standard` | All sections | Moderate — covers each section with practical detail |
| `comprehensive` | All sections + extras below | Full — exhaustive reference documentation |

**Comprehensive extras:**
- Detailed API documentation with request/response examples for every endpoint
- Deployment variants (Docker, Docker Compose, Kubernetes, bare metal)
- Troubleshooting section (common errors and their fixes)
- Performance tuning guide (if applicable)
- Security considerations
- Monitoring and observability setup

### Step 8 — Iterative Quality Loop

Run an iterative verify-fix cycle. **Max 3 iterations.**

```
iteration = 0
max_iterations = 3

while iteration < max_iterations:
    iteration += 1
    issues = verify_against_codebase_and_guidelines()
    if no CRITICAL or WARNING issues: break
    fix(issues)
    if no fixes applied this iteration: break  # stuck — stop
```

**Quality checklist:**

| Check | Severity | Action |
|---|---|---|
| Every command matches actual package.json/Makefile scripts | CRITICAL | Fix from source |
| Every env var/config matches what code actually reads | CRITICAL | Fix from code scanning |
| Architecture diagram exists and reflects codebase | WARNING | Generate/update via `/diagram` |
| Quick Start steps actually work (commands are valid) | CRITICAL | Test and fix |
| All internal links and file references resolve | WARNING | Fix broken references |
| Code blocks have titles and are copy-pasteable | WARNING | Fix via **code-snippet-agent** |
| All diagrams render correctly and have alt text | WARNING | Fix broken diagrams |

**Convergence rules:**

| Condition | Action |
|-----------|--------|
| No CRITICAL or WARNING issues remain | **Done** — present to user |
| `iteration >= 3` | **Max reached** — present remaining issues |
| No fixes applied this iteration | **Stuck** — needs human decision |
| Same issue reappears after fix | **Stuck** — stop and report |

**Diagram requirements:**
- Architecture overview diagram is MANDATORY (Excalidraw)
- Data flow diagrams for complex pipelines (Mermaid)
- Minimum 1 diagram for quick depth, 2 for standard, 4+ for comprehensive

---

## Review Mode

Analyze existing project documentation against the current state of the codebase.

### Step 1 — Load Content & Scan Codebase

1. Read the existing documentation from `source` (or auto-detect from README.md, docs/).
2. Scan the codebase using the same discovery process as Write Mode Step 1.

### Step 2 — Load Guidelines

Same as Write Mode Step 2.

### Step 3 — Drift Analysis

Compare documentation against the actual codebase to find:

| Check | How to Detect |
|---|---|
| **Missing features** | Code has routes/handlers/modules not mentioned in docs |
| **Outdated commands** | package.json scripts or Makefile targets differ from documented commands |
| **Wrong config** | Documented env vars don't match what the code actually reads |
| **Stale architecture** | New services/components exist that aren't in the architecture diagram |
| **Dead links** | Internal file references point to moved/deleted files |
| **Outdated dependencies** | Documented versions don't match lock files |

### Step 4 — Present Findings

Present findings grouped by severity:
- **CRITICAL**: Incorrect information that would mislead users (wrong commands, wrong config)
- **WARNING**: Missing information about significant features or components
- **INFO**: Minor gaps, style improvements, or nice-to-have additions

Ask the user if they want to apply fixes (transition to Update mode).

---

## Update Mode

Refresh existing documentation to match the current codebase.

### Step 1 — Load & Analyze

1. Read the existing documentation from `source`.
2. Scan the codebase (Write Mode Step 1).
3. Run the drift analysis (Review Mode Step 3).

### Step 2 — Propose Changes

Present a summary of proposed changes:
- Sections that need updating (with specific diffs)
- New sections to add
- Architecture diagram updates needed
- Commands/config that need correction

Wait for user approval before applying changes.

### Step 3 — Apply Changes

Edit existing files in-place. Preserve the document's structure and style. Only change what needs changing. Update the architecture diagram if the codebase has structurally changed.

### Step 4 — Iterative Quality Loop

Run an iterative verify-fix cycle against the codebase. **Max 3 iterations.**

```
iteration = 0
max_iterations = 3

while iteration < max_iterations:
    iteration += 1
    issues = verify_against_codebase()
    if no CRITICAL or WARNING issues: break
    fix(issues)
    if no fixes applied this iteration: break  # stuck — stop
```

**Quality checklist:**

| Check | Severity | Action |
|---|---|---|
| Every command is copy-pasteable and correct | CRITICAL | Fix command against actual scripts/Makefile |
| Every config/env reference matches code | CRITICAL | Correct from actual code parsing |
| Architecture diagram reflects current components | WARNING | Regenerate via `/diagram` |
| All internal file links resolve | WARNING | Fix broken links |
| Quick Start is completeable in < 5 min | WARNING | Simplify or split steps |
| API reference matches actual routes/handlers | WARNING | Update from code |
| All diagrams render and have alt text | WARNING | Fix broken diagrams |

**Convergence rules:** Same as Write Mode — max 3 iterations, stuck detection, same-issue-reappears detection.

---

## Scanning Heuristics

When scanning the codebase, use these heuristics to prioritize what to document:

| Signal | Inference |
|---|---|
| Multiple `Dockerfile` variants | Document each build target |
| `.env.example` exists | Extract all env vars and document them |
| OpenAPI/Swagger spec exists | Generate API reference from spec |
| Monorepo structure (`packages/`, `apps/`) | Document each package/app separately |
| Database migrations present | Document data model and migration process |
| CI/CD config present | Extract test/build/deploy commands |
| `Makefile` or `Justfile` present | Use these as the canonical command reference |
