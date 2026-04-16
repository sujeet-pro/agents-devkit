# adk-spec

Write product requirements, technical specifications, API specs, or feature acceptance criteria.

## Quick Start

```
npx adk-spec "user notifications system for the mobile app" --type prd
```

Or as a slash command:

```
/adk-spec --type prd user notifications system for the mobile app
```

## What This Skill Does

Writes specifications that define WHAT to build and WHY. Specifications bridge stakeholder intent and implementation reality by capturing requirements, constraints, interfaces, and acceptance criteria in a structured, testable format. Supports five spec types: PRD, technical specification, API specification, feature specification, and acceptance criteria.

## Command Reference

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<topic>` | free text | required | What the spec should cover |
| `--type` | `prd`, `technical`, `api`, `feature`, `acceptance` | auto-detected | Spec type to produce |
| `--scope` | path | none | Limit context gathering to one area of the codebase |
| `--auto` | flag | off | Skip confirmations and emit the spec without interactive review cycles |
| `--help` | flag | off | Show the skill and stop |

## Dependencies

| Dependency | Type | Required | Notes |
| --- | --- | --- | --- |
| `git` | command | yes | Must be on PATH |
| `python3` | command | yes | Must be on PATH |
| Web access | capability | no | Recommended for domain research; WebSearch and WebFetch tools |

## Skill Layout

```
adk-spec/
  SKILL.md                                # Skill definition
  README.md                               # This file
  scripts/
    preflight.py                          # Pre-flight checks
  references/
    workflow.md                           # Workflow guidance
    persona.md                            # Persona guidance
    spec-templates.md                     # Spec type templates
    _shared/
      ai-guidelines-overview.md           # Shared AI guidelines
      constitution.md                     # Shared constitution
      research-protocol.md                # Shared research protocol
      output-format.md                    # Shared output format
```

## Workflow

1. Clarify the topic, spec type, scope, and intended audience.
2. Gather context from the codebase and existing documentation.
3. Research domain constraints, prior art, and relevant standards.
4. Draft the spec using the appropriate template from `spec-templates.md`.
5. Validate completeness: are all requirements testable? Is any language ambiguous? Are non-functional requirements covered?
6. Present the spec with a coverage assessment and open questions for stakeholder review.

## Interaction Protocol

- **Confirm topic and spec type**: before drafting, confirm the topic, spec type, intended audience, and scope with the user (unless `--auto`).
- **Present draft sections for review**: deliver the spec in sections (Overview, Requirements, Constraints, Acceptance Criteria); pause after each major section for feedback.
- **Iterate on requirements**: the user may accept, modify, or reject individual requirements; incorporate feedback before proceeding.
- **Flag ambiguity explicitly**: highlight vague or untestable language and propose concrete alternatives.
- **Open questions are separated**: unknowns that need stakeholder input are listed at the end.
- **Suggest next step**: after the spec is approved, recommend the logical follow-up (usually `adk-plan`).

## Output Format

Each spec includes:
- **Spec document**: full specification in markdown using the appropriate template
- **Spec type**: which template was used
- **Coverage assessment**: what is fully specified vs. what has gaps
- **Open questions**: items needing stakeholder input
- **Suggested next step**: usually `adk-plan`

## Examples

Write a PRD:
```
/adk-spec --type prd user notifications system for the mobile app
```

Write an API spec:
```
/adk-spec --type api REST API for the billing service --scope src/billing
```

Write acceptance criteria:
```
/adk-spec --type acceptance checkout flow including edge cases for failed payments
```

## What Success Looks Like

- [ ] Every requirement is testable or explicitly marked as aspirational
- [ ] Ambiguous language is flagged with a resolution request
- [ ] Non-functional requirements are present where applicable
- [ ] Dependencies and assumptions are called out
- [ ] The spec is internally consistent (no contradictions between sections)
- [ ] Open questions are separated from the spec body
- [ ] The spec type matches the user's intent
