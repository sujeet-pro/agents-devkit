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

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/clarifying-questions.md`) and reports the choices.

1. **Doc type: README / runbook / API / ADR / onboarding / migration / tech-radar / changelog / custom?** — _How to pick:_ README = first-touch repo intro. Runbook = on-call mitigation. API = developer reference. ADR = single decision record. Onboarding = day-1 to first-PR. Migration = move from A to B. Tech-radar = ring placement. Changelog = release notes. Custom = anything else.
2. **Audience and the action they take after reading?** — _How to pick:_ On-call → mitigation steps. New hire → setup commands. Consumer → API signatures + examples. Decision-maker → trade-offs + recommendation.
3. **Where will it live so it stays discoverable?** — _How to pick:_ Pick a path inside the repo's existing docs structure. Avoid orphan files at the root.
4. **Are there extra repos that supply context (clones to read, paths to local checkouts)?** — _How to pick:_ Pass URLs to clone or paths to local clones. Useful for cross-repo migration guides, integration docs, multi-service onboarding.

**Default report:** Final doc markdown + 3-bullet TL;DR + validation results (commands run, links checked).

**Detailed report (on request or `--verbose`):** Add: outline before the draft, source-evidence per section (file:line), drift-from-code log if refreshing, follow-up TODOs by section.

**Artifact:** `documentation-page` — Markdown file at the chosen path inside the repo. Outline + working notes mirrored in .temp/drafts/.

**Artifact path:** .temp/drafts/docs-<slug>.md (working draft). Final lands at the repo path the user chose (README.md, docs/runbooks/<slug>.md, docs/adr/NNN-<slug>.md, etc.).

Pass extra repos via `--repo <url-or-path>` (repeatable). URLs are cloned into `.temp/reference-repos/<owner>__<repo>/`; paths are read in place. Each repo is processed independently and findings/citations are tagged with the repo of origin. See `references/multi-repo.md` for full handling.

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/clarifying-questions.md`) and reports the choices.

1. **Doc type: README / runbook / API / ADR / onboarding / migration / tech-radar / changelog / custom?** — _How to pick:_ README = first-touch repo intro. Runbook = on-call mitigation. API = developer reference. ADR = single decision record. Onboarding = day-1 to first-PR. Migration = move from A to B. Tech-radar = ring placement. Changelog = release notes. Custom = anything else.
2. **Audience and the action they take after reading?** — _How to pick:_ On-call → mitigation steps. New hire → setup commands. Consumer → API signatures + examples. Decision-maker → trade-offs + recommendation.
3. **Where will it live so it stays discoverable?** — _How to pick:_ Pick a path inside the repo's existing docs structure. Avoid orphan files at the root.
4. **Are there extra repos that supply context (clones to read, paths to local checkouts)?** — _How to pick:_ Pass URLs to clone or paths to local clones. Useful for cross-repo migration guides, integration docs, multi-service onboarding.

## Default vs detailed output

**Default report:** Final doc markdown + 3-bullet TL;DR + validation results (commands run, links checked).

**Detailed report (on request or `--verbose`):** Add: outline before the draft, source-evidence per section (file:line), drift-from-code log if refreshing, follow-up TODOs by section.

**Artifact:** `documentation-page` — Markdown file at the chosen path inside the repo. Outline + working notes mirrored in .temp/drafts/.

**Artifact path:** .temp/drafts/docs-<slug>.md (working draft). Final lands at the repo path the user chose (README.md, docs/runbooks/<slug>.md, docs/adr/NNN-<slug>.md, etc.).

## Multi-repo context

Pass extra repos via `--repo <url-or-path>` (repeatable). URLs are cloned into `.temp/reference-repos/<owner>__<repo>/`; paths are read in place. Each repo is processed independently and findings/citations are tagged with the repo of origin. See `references/multi-repo.md` for full handling.

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/anti-patterns.md` | Things to avoid when running this skill. |
| `references/artifact-format.md` | The deliverable's format and where it lives (.temp/ contract). |
| `references/clarifying-questions.md` | The default-ask questions for this skill, with how-to-pick rubrics. |
| `references/constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/examples.md` | Example trigger phrases, invocation, and report shape. |
| `references/interaction-contract.md` | Default-ask, explained-options, --auto contract every skill must follow. |
| `references/multi-repo.md` | How to consume context from extra cloned or local-path repos. |
| `references/output-format.md` | Default vs detailed report shapes; severity labels; verbosity rules. |
| `references/persona.md` | The agent persona that drives this skill. |
| `references/research-protocol.md` | Source ordering, stop conditions, evidence buckets, citation discipline. |
| `references/working-artifacts.md` | Legacy: superseded by artifact-format.md; kept for back-compat. |

<!-- adk:references:end -->
