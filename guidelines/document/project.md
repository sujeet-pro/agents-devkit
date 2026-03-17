# Project Documentation Guidelines

Guidelines for writing and reviewing project documentation. These ensure docs are comprehensive, accurate, and usable by developers who need to get productive quickly.

---

## 1. Purpose & Audience

Project documentation serves developers who need to understand, use, configure, deploy, or contribute to a project. The primary audience ranges from first-time users (who need a quick start) to maintainers (who need architecture context and configuration reference). Every section should be written with a specific audience in mind.

---

## 2. Required Sections

Every project documentation set must contain these sections:

| Section | Audience | Purpose |
|---------|----------|---------|
| **Project Overview** | Everyone | What the project does and who it is for |
| **Architecture** | Contributors, maintainers | System design with diagram |
| **Getting Started / Quick Start** | New users | Install and first usage in under 5 minutes |
| **Configuration Reference** | Users, operators | All options with defaults and descriptions |
| **API Reference** | Integrators (if applicable) | Endpoints, methods, types, examples |
| **Deployment Guide** | Operators | How to deploy and run in production |
| **Contributing Guide** | Contributors | How to set up a dev environment and submit changes |

---

## 3. Content Standards

### Project Overview

- First sentence: what the project does in one line ("X is a Y that does Z").
- Second paragraph: who should use it and what problem it solves.
- Include a feature list (bullet points, not prose) covering the major capabilities.
- State what the project is NOT. Explicit non-goals prevent misuse and misplaced feature requests.
- If the project has alternatives, briefly state how it differs (1-2 sentences, not a comparison matrix).

### Architecture

- **A diagram is mandatory.** Use Mermaid, Excalidraw, or a static image, but there must be a visual representation of the system.
- The diagram must show: major components, data flow direction, external dependencies, and trust boundaries.
- Accompany the diagram with a written description that explains each component's responsibility.
- Document key design decisions with reasoning: "We use a message queue between X and Y because direct HTTP calls created a tight coupling that made Y's deployments dependent on X's availability."
- State the tech stack and the rationale for major technology choices.

### Getting Started / Quick Start

- **The quick start must work.** Test every command before publishing. A broken quick start destroys trust immediately.
- Target: a developer with the prerequisites installed goes from zero to a working example in under 5 minutes.
- Structure as numbered steps. Each step has exactly one command or action.
- Show expected output after commands that produce meaningful output.
- End with a "you should now see..." confirmation so the reader knows they succeeded.

```markdown
### Example structure:

1. Install dependencies
   ```bash
   npm install
   ```

2. Start the development server
   ```bash
   npm run dev
   ```
   You should see: `Server running at http://localhost:3000`

3. Open http://localhost:3000 in your browser
```

- State prerequisites explicitly at the top: required language version, OS, tools.

### Configuration Reference

- Document every configuration option. Undocumented options are bugs.
- Use a table format for each option:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `port` | `number` | `3000` | The port the server listens on |
| `logLevel` | `string` | `"info"` | Log verbosity: `"debug"`, `"info"`, `"warn"`, `"error"` |
| `maxRetries` | `number` | `3` | Maximum retry attempts for failed requests |

- Group related options under sub-headings (Database, Authentication, Logging, etc.).
- For each option, document: the name, type, default value, description, and valid values or constraints.
- Include a complete example configuration file with comments.

### API Reference

- Document every public endpoint or method.
- For each: method/signature, parameters (with types and constraints), return value, error responses, and a working example.
- Examples must be copy-pasteable. Include full curl commands or code snippets that work against a running instance.
- Document rate limits, authentication requirements, and pagination behavior at the top of the API section, not repeated per endpoint.

### Deployment Guide

- Cover at least one deployment target (Docker, cloud platform, bare metal).
- Document environment variables required in production (with descriptions, not just names).
- Include health check endpoints and how to verify the deployment succeeded.
- Document backup and rollback procedures.
- State resource requirements: minimum CPU, memory, disk.

### Contributing Guide

- Document how to set up the development environment (step by step, tested).
- State the branching strategy and PR process.
- Document how to run tests locally.
- State code style requirements and how to run linters/formatters.
- Describe the review process: who reviews, what the expectations are, typical turnaround time.

---

## 4. Structure & Flow

- Order sections by audience need: Overview first (everyone reads), then Quick Start (most common entry point), then deeper sections.
- Use a table of contents for documents longer than 3 screens.
- Cross-reference between sections: "For configuration details, see [Configuration Reference](#configuration-reference)."
- Keep each section self-contained enough that a reader can jump directly to it from a search result.
- Use consistent heading levels: H1 for the project name, H2 for major sections, H3 for sub-sections.

---

## 5. Common Issues

- **Broken quick start**: Commands that do not work, missing prerequisites, outdated versions. Test the quick start from a clean environment before publishing.
- **Missing architecture diagram**: Text-only architecture descriptions are insufficient for complex systems. Always include a visual.
- **Undocumented configuration**: Options that exist in code but not in documentation. Audit the codebase for all configuration entry points.
- **Stale examples**: Code examples that reference deprecated APIs or old versions. Pin examples to a specific version and update with each release.
- **Unpasteable commands**: Commands that include placeholder values without clearly marking them (e.g., `curl https://api.example.com` when the reader needs to substitute their own URL). Use `<angle-brackets>` for placeholder values.
- **Missing error guidance**: The quick start works on the happy path but provides no help when something goes wrong. Include a troubleshooting section or FAQ for common issues.
- **Contributor-hostile setup**: A contributing guide that requires 15 steps and 6 tools to get a dev environment running. Simplify or provide a containerized setup.

---

## 6. Review Checklist

- [ ] Project overview states what the project does in the first sentence
- [ ] Non-goals or out-of-scope items are stated explicitly
- [ ] Architecture section includes a diagram (Mermaid, Excalidraw, or image)
- [ ] Architecture diagram shows components, data flow, and external dependencies
- [ ] Quick start has been tested from a clean environment and works end to end
- [ ] Quick start completes in under 5 minutes for a prepared developer
- [ ] Every configuration option is documented with type, default, and description
- [ ] A complete example configuration file is provided
- [ ] API examples are copy-pasteable and work against a running instance
- [ ] Deployment guide covers environment variables, health checks, and resource requirements
- [ ] Contributing guide includes dev setup, testing, and PR process
- [ ] All commands show expected output where applicable
- [ ] Placeholder values in commands use `<angle-brackets>` notation
- [ ] No TODO/TBD markers or stub sections remain
