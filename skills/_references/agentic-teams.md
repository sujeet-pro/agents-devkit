# DevKit Child-Agent Contract

Every non-trivial DevKit skill must use parallel child agents when the current platform supports them.

## Core Rules

1. Launch at least 2 child agents in parallel for analysis, review, research, writing, or generation work.
2. Child agents receive the full task context they need, not partial fragments or hidden session history.
3. Keep agent roles distinct so each one owns a perspective or deliverable.
4. Merge results in the parent session with explicit confidence notes and duplicate removal.
5. If the platform does not support child agents, simulate the same role split sequentially and say that parallel execution was unavailable.

## Platform Rules

- **Claude / Claude Code**: use Agentic Teams or child agents in parallel.
- **Codex**: use child agents with full context; keep them focused by role.
- **Gemini CLI**: prefer Gemini's native agents or extensions. If native child agents are unavailable, run role-based passes sequentially.
- **Cursor / Cursor CLI**: stay inside Cursor. Use Cursor's built-in agent/model capabilities only. Do **not** shell out to `claude`, `codex`, or `gemini` from Cursor.
- **OpenCode and similar CLIs**: use built-in agent or multi-model features first; only call external CLIs when the current tool has no equivalent and the host is not Cursor.

## Standard Team Shapes

### Review Team

- **Context reader**: reads the diff, source material, and existing comments.
- **Architecture reviewer**: checks boundaries, coupling, migrations, and long-term maintainability.
- **Quality reviewer**: checks correctness, security, performance, tests, and code patterns.
- **Documentation reviewer**: checks docs, naming, comments, and reviewer ergonomics.
- **Domain specialist**: frontend, backend, design system, docs, or platform-specific concerns.

### Research Team

- **Landscape mapper**: frames the problem and subtopics.
- **Primary-source researcher**: collects official docs, specs, and maintainers' guidance.
- **Implementation researcher**: checks real repositories, examples, and migration notes.
- **Risk analyst**: finds edge cases, tradeoffs, and open questions.

### Documentation Team

- **Source analyst**: reads code, docs, tickets, or external source material.
- **Outline editor**: designs the information architecture.
- **Fact checker**: verifies claims, versions, links, and examples.
- **Code or diagram specialist**: prepares examples and visuals.
- **Publisher**: prepares markdown plus source-specific output such as Confluence or Google Docs.

### Diagram Team

- **Structure agent**: identifies entities, flows, and grouping.
- **Notation agent**: chooses Mermaid, Excalidraw, or draw.io.
- **Validation agent**: checks renderability, naming, and consistency with the written narrative.

### Security Audit Team

- **Auth reviewer**: authentication and authorization flows, session management, JWT handling.
- **Data flow analyzer**: traces sensitive data through the system, checks encryption, logging, exposure.
- **Dependency scanner**: checks for known CVEs, outdated packages, license issues.
- **OWASP checker**: systematic OWASP Top 10 review against the codebase.

### Migration Team

- **Usage analyzer**: finds all usage of the source framework/library in the codebase.
- **Changelog researcher**: reads official migration guides, changelogs, and breaking change lists.
- **Migration planner**: maps breaking changes to specific files and creates step-by-step plan.
- **Risk assessor**: evaluates effort, risk, and identifies codemods or automation available.

### Engineering Workflow Team

- **Analyst**: reads source material (PR comments, git history, codebase structure, configs).
- **Researcher**: gathers authoritative sources (official docs, specs, community best practices).
- **Writer**: produces the deliverable (ADR, runbook, changelog, onboarding guide, API docs).
- **Reviewer**: checks accuracy, completeness, and actionability of the output.

## Merge Rules

- Merge only overlapping findings that describe the same issue.
- Preserve minority opinions when they change risk assessment.
- Mark single-agent findings as lower confidence until verified.
- Prefer official docs, repository code, and existing source comments over generic advice.
