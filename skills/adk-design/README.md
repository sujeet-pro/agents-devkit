# adk-design

Design, audit, or polish interfaces with clear UX goals, accessibility constraints, and implementation realism.

## Quick Start

```bash
npx adk-design "create a settings page for notification preferences" --action create --focus ui
```

## What This Skill Does

Handles interface quality work: designing new UI directions, auditing existing flows for UX and accessibility issues, and polishing features before release. The skill keeps recommendations concrete enough to build or review, with accessibility and responsiveness treated as core requirements.

## Command Reference

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<design-task>` | free text | required | What should be designed, reviewed, or polished |
| `--action` | `create`, `audit`, `polish` | `create` | Design task type |
| `--focus` | `ui`, `ux`, `accessibility`, `frontend` | `ui` | Primary design lens |
| `--scope` | path or surface | none | Limit the area under review |
| `--auto` | flag | off | Skip confirmations and use defaults |
| `--help` | flag | off | Show the skill and stop |

## Dependencies

| Dependency | Type | Required |
| --- | --- | --- |
| `git` | command | yes |
| `python3` | command | yes |

## Skill Layout

```
adk-design/
  SKILL.md
  README.md
  scripts/
    preflight.py
  references/
    workflow.md
    persona.md
    _shared/
      ai-guidelines-overview.md
      constitution.md
      research-protocol.md
      output-format.md
```

## Workflow

1. Confirm the product goal, audience, and constraints before proposing design direction.
2. Inspect the current UI, code, or screenshots relevant to the task.
3. Identify the strongest usability, accessibility, and visual hierarchy issues first.
4. Propose a clear direction or audit findings with implementation-aware guidance.
5. Keep design recommendations concrete enough to build or review.
6. Finish with trade-offs, constraints, and the next best iteration step.

## Interaction Protocol

Unless `--auto` is set, the skill follows an interactive workflow:

1. **Intent confirmation** -- confirms the design task, product goal, focus area, scope, and constraints.
2. **Design options** -- presents 2-3 design options or variations with trade-offs before committing to a direction.
3. **Iterative feedback** -- after choosing a direction, iterates based on user feedback with inline revisions.
4. **User response** -- `a`/`b`/`c` to pick an option, feedback text to refine, `ok` to approve, `more` to expand detail.

## Output Format

Each run produces:
- Design goal or findings
- Key decisions or issues
- Accessibility and responsiveness notes
- Implementation constraints
- Remaining trade-offs

## Examples

### Create a UI for a feature
```bash
npx adk-design "create a settings page for user notification preferences" --action create --focus ui
```
Confirms the feature goal, inspects existing UI patterns, presents layout options, details the chosen direction.

### Audit accessibility
```bash
npx adk-design "audit the checkout flow for WCAG compliance" --action audit --focus accessibility
```
Reviews the checkout flow code and markup, presents findings with severity levels and remediation guidance.

### Polish an existing component
```bash
npx adk-design "polish the dashboard sidebar" --action polish --scope src/components/sidebar/ --auto
```
Skips confirmations, inspects the sidebar code, proposes visual and interaction improvements.

## What Success Looks Like

- [ ] Recommendations tie back to the product goal and current surface
- [ ] Accessibility and responsiveness are treated as core requirements
- [ ] Design options include clear trade-offs
- [ ] Unresolved implementation constraints stay explicit
- [ ] The skill reports findings, decisions, and remaining trade-offs
