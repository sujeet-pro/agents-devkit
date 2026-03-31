# Codebase Audit Stage

This stage is loaded when `--focus` includes `codebase` or defaults to `all`.

## Scope

Review:

- repository structure and ownership boundaries
- build, test, and release ergonomics
- public APIs and documentation quality
- code patterns, duplication, and modernization opportunities
- missing diagrams or architecture docs

## Required Child Agents

Run at least these child agents in parallel:

- **repo-auditor**: system-level architecture and maintainability. Evaluates directory structure, module boundaries, dependency graph between internal packages, and configuration hygiene.
- **code-reviewer**: correctness, security, performance, and code patterns. Scans for anti-patterns, dead code, duplication, and modernization opportunities across the codebase.
- **doc-reviewer**: docs drift, onboarding quality, and examples. Checks README accuracy, API docs completeness, inline comment quality, and whether architecture decisions are documented.
- **domain specialist**: one specialist based on the detected repo type (frontend, backend, or design system). Applies domain-specific best practices and checks framework conventions.

## Workflow

1. **Detect repo type.** Analyze the repository to determine the primary technology stack, frameworks, and domain (frontend, backend, fullstack, design system, library, CLI tool, etc.).
2. **Load coding guidelines.** Invoke `/adk-coding` to detect repo frameworks and load matching coding guidelines. Use full detection (not scoped to changed files).
3. **Scan repository structure.** Audit directory layout, module boundaries, dependency graph, and configuration files. Check for clear ownership boundaries and separation of concerns.
4. **Analyze code quality.** Scan for anti-patterns, dead code, duplication, inconsistent patterns, and modernization opportunities. Evaluate test coverage and testing strategy.
5. **Review build and release.** Check build configuration, CI/CD setup, release process, and developer experience tooling (linting, formatting, type checking).
6. **Review documentation.** Evaluate README, API docs, architecture docs, inline comments, and onboarding materials. Identify gaps where diagrams or architecture decision records are missing.
7. **Synthesize findings.** Merge all child agent results, deduplicate, and produce the final report sections.

## Output Sections

- **Executive Summary**: overall health assessment with top 3-5 action items
- **Repository Structure**: directory layout analysis, module boundaries, ownership model
- **Code Quality**: anti-patterns, duplication, modernization opportunities
- **Build & Release**: CI/CD health, developer experience, test infrastructure
- **Documentation**: gaps, drift, onboarding quality
- **Prioritized Improvement Backlog**: all findings ranked by impact
- **Quick Wins**: changes that can be made immediately with high confidence
- **Strategic Initiatives**: larger efforts that require planning
- **Documentation Follow-Ups**: missing diagrams, architecture docs, and decision records
