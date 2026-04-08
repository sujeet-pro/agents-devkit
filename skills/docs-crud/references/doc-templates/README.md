# Document Templates

Structural templates for common software engineering document types. Each template provides a ready-to-fill skeleton with sections, placeholders, and tables.

## Usage

When `docs-crud create` receives a `--type` flag, load the matching template from this directory and use it as the document skeleton. When `--template <path-or-url>` is provided, download/read the custom template instead.

## Template Index

| Type Flag | Template File | Document Type |
|-----------|---------------|---------------|
| `tdd` | [tdd.md](./tdd.md) | Technical Design Document / Tech Spec |
| `hld` | [hld.md](./hld.md) | High Level Design |
| `lld` | [lld.md](./lld.md) | Low Level Design |
| `prd` | [prd.md](./prd.md) | Product Requirements Document |
| `erd` | [erd.md](./erd.md) | Engineering Requirements Document |
| `adr` | [adr.md](./adr.md) | Architecture Decision Record |
| `rfc` | [rfc.md](./rfc.md) | Request for Comments |
| `runbook` | [runbook.md](./runbook.md) | Operational Runbook |
| `incident-report` | [incident-report.md](./incident-report.md) | Incident Postmortem / Report |
| `status-report` | [status-report.md](./status-report.md) | Sprint / Weekly Status Report |
| `api-reference` | [api-reference.md](./api-reference.md) | API Reference Documentation |
| `onboarding` | [onboarding.md](./onboarding.md) | Onboarding / Getting Started Guide |
| `release-notes` | [release-notes.md](./release-notes.md) | Release Notes |
| `project` | [project.md](./project.md) | Project Documentation / README |

## Diagram Placeholders

Templates use `<!-- DIAGRAM: description -->` placeholders to mark where diagrams should be inserted. During execution, these are replaced by invoking `/adk:diagram` with the description and rendering the output.

## Chart Placeholders

Templates use `<!-- CHART: type | data-description -->` placeholders to mark where data charts should be inserted. During execution, these are replaced by invoking `/adk:chart` with the chart type and data.

## Custom Templates

When `--template <path-or-url>` is provided:
1. Read the template from local path, Confluence URL, or Google Docs URL
2. Extract the heading structure, placeholder patterns, and boilerplate
3. Use the extracted structure as the skeleton instead of a built-in template
4. Merge with type-specific quality rules from `/adk:docs-guidelines` if `--type` is also set
