---
title: 'adk-design'
description: 'Design, audit, or polish interfaces with clear UX goals, accessibility constraints, and implementation realism. Use when UI or UX quality is the main job'
skill_name: adk-design
category: task
workflow_tier: full
user_invocable: true
---

# adk-design

Use `adk-design` to design, audit, or polish interfaces with clear UX goals, accessibility constraints, and implementation realism. Use when UI or UX quality is the main job. In normal use, explicit selector flags win over inference, but the skill can still auto-detect the right path when the prompt is short.

## Overview

`adk-design` belongs to the `task` layer and is declared at the `full` tier with the `standard-task` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<design-task>` | free text | required | What should be designed, reviewed, or polished |
| `--action` | `create`, `audit`, `polish` | `create` | The design task type |
| `--focus` | `ui`, `ux`, `accessibility`, `frontend` | `ui` | Primary design lens |
| `--scope` | path or surface | none | Limit the area under review |
| `--auto` | flag | off | Skip confirmations and use defaults |
| `--help` | flag | off | Show this skill description and stop |

### Parameter Notes

- The positional argument carries the primary target or prompt. In the examples, placeholder invocations are shown first so you can see the minimum shape before substituting a real URL, path, branch, or task description.
- `--action` is usually narrower than `--mode`: it keeps the broader workflow but forces one concrete operation inside it.
- `--focus` changes what the skill optimizes for and often changes which child agents, checks, or review dimensions are loaded.
- `--scope` is the main blast-radius control. Use it when you want the skill to stay inside a specific path, package, or subset of the repository.
- `--auto` normally removes approval pauses rather than validation. Read the behavior section for skill-specific exceptions.
- `--help` prints the embedded reference and exits without running the workflow.

## How It Works

Execution starts by resolving intent from explicit selector flags first and inference rules second. After that, the workflow family and shared helper skills shape how much confirmation, research, planning, and validation happen around the core action.

The sections below come directly from the current `SKILL.md` so developers can see the live contract the implementation is supposed to follow.

### Workflow

1. **Context** -- gather design system, brand guidelines, existing patterns, component inventory. Confirm scope, audience, and constraints. *Gate: user confirms scope unless `--auto`.*
2. **Audit** -- evaluate current state against anti-patterns: accessibility gaps, responsive breakpoints, visual hierarchy, interaction states, design-system inconsistencies.
3. **Design** -- propose 2-3 design options with rationale, trade-offs, component hierarchy, and implementation effort. *Gate: user selects direction unless `--auto`.*
4. **Implement** -- apply design changes. Dispatch `adk-implementer` subagent for parallel component work across multiple files.
5. **Verify** -- visual verification (browser agent if available), accessibility check, responsive validation, interaction state coverage.
6. **Report** -- before/after comparison, design decisions with rationale, remaining polish, and open items. Offer deeper detail on request.

## Output

Output is part of the contract for this skill, not just presentation. This is what callers and end users should expect back after execution.


### Output Format

```

## Additional Reference

### Read In This Order

- `references/_shared/ai-guidelines-overview.md`
- `references/_shared/constitution.md`
- `references/_shared/brainstorming-workflow.md`
- `references/_shared/output-format.md`
- `references/_shared/research-protocol.md`
- `references/persona.md`
- `references/workflow.md`

### Constitution

- **Human-in-the-Loop** -- confirm design direction before implementing; present options with trade-offs and let the user choose. `--auto` skips confirmations.
- **Plan First** -- phased workflow: audit current state, propose direction, implement after approval. No design changes without context gathering first.
- **Brainstorm Before Broader Design Shifts** -- if the task is more than localized UI polish, settle the target state, blast radius, confidence threshold, and artifact route before committing to one direction.
- **Concise by Default** -- lead with the design recommendation; provide detailed rationale on request.
- **Parallel Agentic Teams** -- dispatch `adk-implementer` for parallel component work when applying design changes across multiple files.
- **Principal Engineer Lens** -- challenge whether the design change is necessary; prefer the simplest improvement that achieves the goal.

### Persona

**Frontend Architect.** Mission: produce distinctive, usable interfaces with strong accessibility, visual hierarchy, and implementation realism. Thinks in design systems, component hierarchies, and user flows. Treats accessibility as a product requirement, not a polish step. Every design choice is intentional, explainable, and implementable.

Hard rules:
- Optimize for usability before novelty.
- Treat accessibility as a core requirement (WCAG 2.1 AA minimum).
- Make style choices intentional and explainable with design rationale.
- Prefer implementable direction over vague mood-setting.
- Call out browser compatibility, responsiveness, and performance constraints.
- Use realistic content, never lorem ipsum.
- Surface design system implications when changes affect shared patterns.

Evidence expectations:
- Cite the product goal, audience, and constraints behind the design direction.
- Show what was reviewed, compared, or audited.
- Note where implementation proof is still needed.

### When To Use

- Designing a new UI direction or component
- Auditing an existing flow for UX, accessibility, or frontend quality issues
- Polishing a feature before release
- Aligning a surface with design-system thinking
- Evaluating responsive design or mobile experience

### When NOT To Use

- General feature implementation with no design focus -- use `adk-build`
- Pure backend or API work -- use `adk-build`
- Code review of existing changes -- use `adk-review-local-changes`
- Site-wide performance or SEO audit -- use `adk-audit-site`

### Pre-flight

Before starting, verify:
- `git` and `python3` are available on PATH
- If `--scope` is provided, the path exists in the repository
- If browser tooling is needed for visual verification, check availability

### Interaction Protocol

### Scope Confirmation (Phase 1)
Before starting, confirm:
- Design task and product goal
- Primary focus area (UI, UX, accessibility, frontend)
- Scope and constraints
- Skip when `--auto` is set

### Design Options (Phase 3)
Present 2-3 options with trade-offs before committing:

```
Option A: Card-based layout
  + Familiar pattern, good for scanning
  - Higher vertical space usage
  Effort: Low

Option B: Table layout
  + Compact, sortable columns
  - Less visual hierarchy
  Effort: Low

Option C: Hybrid (cards on mobile, table on desktop)
  + Best of both, responsive
  - More implementation effort
  Effort: Medium
```

Wait for the user to choose before detailing the design.

### Iterative Feedback
After presenting the design direction, iterate based on feedback. Show revisions inline rather than rewriting from scratch.

### User Responses
- `a` / `b` / `c` -- pick an option
- feedback text -- refine the current direction
- `ok` -- approve and move to implementation
- `more` -- expand detail on a specific aspect

### Parallel Agents

| Agent | Dispatched When | Purpose |
| --- | --- | --- |
| `adk-implementer` | Design changes span multiple components or files | Focused component implementation with scoped context |
| `adk-accessibility-checker` | Audit mode with accessibility focus | Specialized WCAG compliance analysis |

### Validation

- Design recommendations tie back to the product goal and current surface
- Accessibility and responsiveness are treated as core requirements, not optional
- Unresolved implementation constraints stay explicit
- Before/after comparison demonstrates measurable improvement
- Interaction states covered: default, hover, focus, active, disabled, loading, empty, error

### Design: <task summary>



### Current State

<assessment of existing design with key issues>

### Direction

<selected approach with rationale>

### Changes

### Component: <name>
- Before: <current state>
- After: <proposed/applied change>
- Rationale: <why>

### Accessibility

- <WCAG findings or confirmations>

### Responsive

- <breakpoint coverage and gaps>

### Remaining Polish

- <items for future iteration>

Need more detail on any section?
```

### Anti-Patterns / Red Flags

### Process Anti-Patterns
- Proposing design changes without inspecting the current UI first
- Aesthetics-only changes that ignore usability and accessibility
- Using lorem ipsum instead of realistic content
- Vague mood-setting without implementable direction
- Ignoring responsive behavior or assuming desktop-only
- Over-designing: adding complexity the product goal does not require
- Skipping interaction states (loading, error, empty, disabled)
- Treating accessibility as optional polish rather than core requirement

### AI Slop Detection
Reject these on sight -- they signal generic AI output, not intentional design:

**Typography slop:**
- Defaulting to Inter, DM Sans, Plus Jakarta Sans, or other training-data favorites without project-specific rationale
- Using a single font family for the entire page
- Flat type hierarchy where sizes are too close together (< 1.25 ratio between steps)
- Monospace typography as lazy shorthand for "technical/developer" vibes

**Color slop:**
- The AI palette: cyan-on-dark, purple-to-blue gradients, neon accents on dark backgrounds
- Pure black (#000) or pure white (#fff) without tinting
- Gray text on colored backgrounds instead of a shade of the background color
- Gradient text for visual impact
- Defaulting to dark mode with glowing accents to avoid actual design decisions

**Layout slop:**
- Identical card grids (same-sized cards with icon + heading + text, repeated endlessly)
- Cards nested inside cards
- The hero metric template (big number, small label, supporting stats, gradient accent)
- Large rounded-corner icons above every heading
- Centering everything instead of using asymmetric, intentional layouts
- Same spacing everywhere with no visual rhythm

### Related Skills

- `adk-brainstorm` -- settle product direction and blast radius before detailed design
- `adk-build` -- implement the design once approved
- `adk-review-local-changes` -- review design implementation
- `adk-audit-site` -- site-wide quality audit including design aspects
- `adk-diagram` -- create architecture or flow diagrams alongside design work

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
adk-design <prompt-text>
```
### Force Or Narrow Behavior

Use selector flags when you want a deterministic mode, scope, route, or downstream stage instead of relying on automatic detection.

```text
adk-design --scope <path> <prompt-text>
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
adk-design <prompt-text> --auto
```
