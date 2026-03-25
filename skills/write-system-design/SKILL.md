---
name: write-system-design
description: Use when creating a system design document that covers architecture, component design, data models, APIs, and operational concerns
user_invocable: true
arguments:
  - name: title
    description: "Title or subject of the system design"
    required: true
  - name: scope
    description: "Scope boundary: what is in and out of scope for this design"
    required: false
  - name: format
    description: "Output format: markdown, google-doc, confluence, pdf (default: markdown)"
    required: false
---

# System Design Document

Use `skills/_references/agentic-teams.md`, `skills/_references/output-formats.md`, and `skills/_references/preflight-validations.md`.

## Preflight

Before research, drafting, or publishing setup, run:

`zsh scripts/check-skill-deps.zsh write-system-design format=<format>`

If the document will be published to Confluence or Google Docs, do a lightweight MCP read before launching the writing team. If diagrams are needed, inherit the `/devkit:diagram` preflight before rendering assets.

## Required Child Agents

Run at least these child agents in parallel:

- `research-agent` for relevant standards, prior art, and ecosystem constraints
- `code-snippet-agent` for grounding the design in actual repository code and APIs
- `doc-reviewer` for structure, clarity, and completeness
- a diagram pass through `/devkit:diagram` for architecture, component, data model, and deployment visuals
- `source-publisher` if the final output is Confluence or Google Docs

## Guideline Loading

Always load:

- `skills/_references/guidelines/document/general.md`
- `skills/_references/guidelines/document/hld.md`
- `skills/_references/guidelines/document/lld.md`
- `skills/_references/guidelines/document/system-design-article.md`

Load coding guidelines when the design includes architecture or code analysis:

- `skills/_references/guidelines/coding/architecture.md`
- `skills/_references/guidelines/coding/general.md`

## Document Structure

Produce a system design with these sections:

### Overview
What the system does and why it exists. One paragraph that a new team member can read to understand the purpose.

### Goals and Non-Goals
Explicit lists of what this design achieves and what it deliberately excludes.

### Architecture
High-level architecture with a diagram (use `/devkit:diagram`). Show major components, their responsibilities, and how they communicate.

### Component Design
For each major component: responsibility, interfaces, internal structure, and dependencies. Include sequence diagrams for critical flows.

### Data Model
Entity-relationship diagram (use `/devkit:diagram` with type=er) and description of key entities, relationships, and storage choices.

### API Design
External and internal API contracts. Include request/response shapes, error handling, and versioning strategy.

### Scalability Considerations
How the system handles growth in traffic, data volume, and team size. Include capacity estimates where relevant.

### Security Considerations
Authentication, authorization, data protection, and threat model for the system boundary.

### Monitoring and Observability
Key metrics, logging strategy, alerting thresholds, and dashboards needed for operations.

### Deployment Strategy
How the system is deployed, rolled back, and promoted across environments. Include a deployment diagram if the topology is non-trivial.

### Timeline and Milestones
Phased delivery plan with key milestones and dependencies between phases.

## Writing Rules

- Produce professional, destination-ready documents with a clear audience and purpose.
- Default to markdown as the source of truth unless the destination requires a native format.
- When describing real code, inspect the repository first instead of inventing APIs.
- Keep both editable diagram source files and rendered outputs.
- Prefer Mermaid, Excalidraw, or draw.io for diagrams. Use Graphviz only when maintaining existing `.dot` assets.
- Use only free or open tooling for conversion and rendering.
- Ground all architecture decisions in concrete constraints, not abstract best practices.

## Final Step

Before publishing, run an internal review loop with the doc-review team and fix all critical issues that block handoff.

## Adjacent Skills

- `/devkit:write-doc` for other document types (PRD, HLD, LLD, article, blog)
- `/devkit:diagram` for standalone architecture diagrams
- `/devkit:write-adr` for recording individual architecture decision records
