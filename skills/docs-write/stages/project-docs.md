# Stage: Project Documentation

Use this stage when the agent should create or directly refresh project documentation by scanning a repository and updating the docs in place.

## Type-Specific Phase Guidance

### Exploration
- Audit the repository structure: modules, packages, entry points, configs
- Scan existing documentation for gaps, stale content, and inaccuracies
- Identify architecture patterns, ownership boundaries, and key abstractions
- If the output destination is Confluence or Google Docs, verify the matching MCP with a lightweight read

### Execute
- Write or update project documentation following the document structure below
- Ground all content in actual repository code and configuration
- Include diagrams for architecture, flows, or ownership boundaries

## Document Structure

### Project Overview
- What the project does and why it exists
- Key features and capabilities
- Technology stack summary

### Quick Start
- Minimal steps to get the project running
- Prerequisites with version requirements
- Installation and first run

### Architecture
- High-level architecture diagram
- Component responsibilities and boundaries
- Data flow between components
- External dependencies and integrations

### API Reference
- Public API surface (if applicable)
- Configuration options with defaults and descriptions
- Environment variables

### Development Guide
- How to set up the development environment
- How to run tests
- How to build and deploy
- Coding conventions and style guide

### Deployment
- Deployment architecture
- Environment configurations
- CI/CD pipeline description
- Monitoring and observability

### Contributing
- How to contribute
- PR process and requirements
- Issue reporting guidelines

## Child Agent Team

- `repo-auditor` for architecture and module boundaries
- `research-agent` for external dependencies and official references
- `code-snippet-agent` for setup, API, and workflow examples
- `doc-reviewer` for structure and onboarding quality
- `/adk-diagram` for architecture, flow, or ownership diagrams

## Writing Rules

- All documentation must be grounded in the actual repository state
- Prefer linking to source code over duplicating it in docs
- Keep documentation close to the code it describes
- Use progressive disclosure: README for quick start, deeper docs in `docs/`

## Type-Specific Output Format

Markdown files in the repository's documentation directory. Typically includes README.md updates and files under `docs/`.

## Validation Checklist

- Documentation matches the current state of the codebase
- Quick start steps work from a clean clone
- Architecture diagrams reflect current structure
- No stale references to removed features or APIs
- Links to source code files are valid
