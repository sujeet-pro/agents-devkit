---
name: adk-docs-write
description: Author or refresh a technical document - README, runbook, API reference, ADR, onboarding guide, migration guide, tech-radar entry - grounded in the actual code and configs of the repo. Use when the deliverable is a markdown doc that real engineers will read and follow. Do not use for product specs (use adk-plan-spec), architecture write-ups (use adk-plan-design), or commit/PR text (use adk-publish-commit).
---

# ADK Docs / Write

Standalone task skill under the `adk-docs` category router. Produces engineer-grade docs grounded in the actual code, with verifiable examples and minimal padding.

## When to use

- A new doc must be authored: README, runbook, API reference, ADR, onboarding guide, migration guide, tech-radar entry, changelog stub.
- An existing doc must be refreshed because the code has drifted from it.
- A scattered set of notes must be consolidated into a single canonical doc.

## When NOT to use

- Product spec / PRD / RFC -> `adk-plan-spec`
- Architecture / design write-up -> `adk-plan-design`
- Commit message / PR description / changelog from a diff -> `adk-publish-commit`
- UI copy for a product surface -> `adk-frontend-design`
- Critique of an existing doc -> `adk-docs-review`

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<doc type>` | yes | `readme` / `runbook` / `api` / `adr` / `onboarding` / `migration` / `tech-radar` / `changelog` / `custom` |
| `<topic>` | yes | What the doc is about |
| `<output path>` | optional | Defaults to a sensible place (`README.md`, `docs/runbooks/<slug>.md`, `docs/adr/NNN-<slug>.md`, etc.) |
| `<scope>` | optional | Path to limit reads |
| `--auto` | optional | Skip approval gates |

## Workflow

1. **Confirm intent** - restate doc type, topic, audience, destination, and how the doc will be discovered. Approval gate unless `--auto`.
2. **Gather** - read the source-of-truth: code, configs, scripts, env files, prior docs, related tickets. Pull repo evidence first.
3. **Outline** - draft headings only; check the outline against the doc-type template below.
4. **Draft** - fill each section with concrete content. Every example must be real (a command that runs, a code block that compiles, a config that loads).
5. **Validate** - run the validation checklist below. Fix the doc, not just call out the gap.
6. **Report** - file path, 3-bullet TL;DR, validation results, follow-up notes.

## Doc-type templates

### README

```markdown
# <Project>

<one-paragraph what + why>

## Quick Start
```bash
<install + run minimum>
```

## Features
- <bullet>

## Install
<concrete steps with version requirements>

## Usage
<minimal worked example>

## Configuration
| Var | Required | Default | Purpose |
| --- | --- | --- | --- |

## Development
<setup, tests, lint, scripts>

## Contributing
<link to CONTRIBUTING.md or short policy>

## License
<spdx identifier or link>
```

### Runbook

```markdown
# Runbook: <symptom or alert>

## When this fires
<trigger conditions; alert name; dashboard link>

## Severity
<page / ticket / log>

## Immediate mitigation
1. <action>
2. <action>

## Diagnose
<commands, dashboards, log queries with concrete examples>

## Recover
<steps to return to healthy>

## Validate
<how to confirm we are healthy>

## Postmortem hooks
<what to capture for follow-up>

## Related
- <links>
```

### API Reference (per endpoint or function)

```markdown
## <name>
<one-line purpose>

### Signature
<exact signature, language-tagged>

### Parameters
| Name | Type | Required | Description |
| --- | --- | --- | --- |

### Returns
<type and meaning>

### Errors
| Condition | Code | Message |
| --- | --- | --- |

### Example
<minimal runnable example>
```

### ADR

Use the template from `adk-plan-design` (ADR section). This skill writes the doc; `adk-plan-design` is for the design write-up itself.

### Onboarding

```markdown
# Onboarding: <team or repo>

## Day 1
- [ ] <step>
- [ ] <step>

## Environment Setup
<exact commands and links>

## First PR
<small starter task>

## Who to Ask
| Topic | Person | Channel |
| --- | --- | --- |

## Glossary
- <term>: <definition>
```

### Migration Guide

```markdown
# Migrate: <from> -> <to>

## Why
<motivation in 2-3 sentences>

## Scope
- In: <bullets>
- Out: <bullets>

## Breaking Changes
- <change> - before:`...` after:`...`

## Steps
1. <action>
2. <action>

## Validation
<how to know it worked>

## Rollback
<how to revert>
```

### Tech Radar Entry

```markdown
## <Item>

- **Ring**: Adopt | Trial | Assess | Hold
- **Quadrant**: Tools | Techniques | Platforms | Languages
- **Date**: <YYYY-MM>
- **Signals**: <2-3 bullets - why we changed ring>
- **Notes**: <2-3 sentences>
```

## Validation checklist

- Every command shown actually runs in the repo today.
- Every config row matches the code that reads it.
- Every link resolves.
- Code blocks have language tags.
- TL;DR or first paragraph stands alone (someone scanning gets the point).
- No "this guide will explain..." preamble.
- No HTML-only structures - safe markdown only.

## Output format

```
## Doc written: <type>
- File: `<path>`
- Topic: <topic>
- TL;DR:
  - <bullet>
  - <bullet>
  - <bullet>
- Validation: <PASS or list of fixed issues>
- Follow-up: <bullets if any>

Want a deeper look at any section?
```

## Anti-patterns

- Documenting wished-for behavior. Read the code first.
- Generic best-practice advice that applies to no specific repo.
- Examples that drift from the code (commands that no longer work).
- Padding with throat-clearing ("In this guide...").
- Splitting the doc across many tiny files when one would be clearer.
- Missing language tags on code blocks.

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/anti-patterns.md` | Things to avoid when running this skill. |
| `references/constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/examples.md` | Example trigger phrases, invocation, and report shape. |
| `references/output-format.md` | Verbosity modes, result shape, severity labels. |
| `references/persona.md` | The agent persona that drives this skill. |
| `references/working-artifacts.md` | The .temp/ rule for intermediate artifacts. |

<!-- adk:references:end -->
