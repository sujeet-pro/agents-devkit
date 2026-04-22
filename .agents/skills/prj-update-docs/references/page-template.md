# Per-artifact page template

The exact section ordering every generated page must follow. Sections marked **required**
are non-negotiable. Sections marked **conditional** are emitted only when the source
artifact actually has the matching content.

## Frontmatter (required)

Per `node_modules/@pagesmith/docs/schemas/docs-page-frontmatter.schema.json`:

```yaml
---
title: '<artifact-name>'
description: '<single sentence, lifted from the source description / one-line purpose>'
artifact_kind: skill | agent | hook | bin | mcp | monitor | config | memory
skill_name: <artifact-name>            # only when artifact_kind = skill
category: top | router | task | standalone   # only when artifact_kind = skill
---
```

`title` and `description` follow the AI-first guideline from
`node_modules/@pagesmith/docs/ai-guidelines/docs-guidelines.md` — lead with what the page
is, never with throat-clearing. Description is at most one sentence.

## Section order

| # | Section                | Required?       | Source of truth                                                   |
| - | ---------------------- | --------------- | ----------------------------------------------------------------- |
| 1 | `# <artifact-name>`    | required        | Filename / frontmatter `name`.                                    |
| 2 | One-paragraph summary  | required        | Source frontmatter `description` + first paragraph of source body. |
| 3 | `## Usage`             | required        | Concrete `/adk:<name>` (Claude), Cursor, Codex invocations.       |
| 4 | `## What it does`      | required        | High-level prose grounded in the source. **No aspirational behaviour.** |
| 5 | `## Workflow`          | required when source has steps | Numbered steps; Mermaid `flowchart TD` only when there is real branching. |
| 6 | `## Decision tree`     | conditional     | Only when the workflow branches on inputs.                        |
| 7 | `## Inputs`            | conditional     | Source's `Inputs` table or function signature.                    |
| 8 | `## Brainstorming questions` | conditional | Only when the source ships `clarifying-questions.md`.            |
| 9 | `## Outputs`           | required        | Final artifact(s), report shape, where they land on disk.         |
| 10 | `## Modes`            | conditional     | When source frontmatter `metadata.modes` is set.                  |
| 11 | `## Anti-patterns`    | conditional     | When source ships `anti-patterns.md` or has an `## Anti-patterns` section. |
| 12 | `## Examples`         | conditional     | When source ships `examples.md`.                                  |
| 13 | `## Related`          | required        | Skills / agents / hooks / upstream packages it links to.          |

## Section guidance — ground rules

Every section follows the AI-first authoring rules from
`node_modules/@pagesmith/docs/ai-guidelines/docs-guidelines.md`:

- Lead with the task, decision, or takeaway before background.
- Short paragraphs, concrete lists, copy-pasteable commands.
- Use [GitHub Alerts](https://docs.github.com/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#alerts)
  (`> [!NOTE]`, `> [!WARNING]`) only for genuine callouts, never as filler.
- One `# h1` per page. Sequential heading depth — never jump from `##` to `####`.
- Every command shown actually runs in the repo today.
- Every internal link uses a relative path (`../guide/getting-started/README.md`) so the
  pagesmith link transform rewrites it under `basePath`.

## Worked example — skill page

```markdown
---
title: 'plan-brainstorm'
description: 'Iteratively narrow ambiguous goals into a recommended path with explicit
trade-offs.'
artifact_kind: skill
skill_name: plan-brainstorm
category: task
---

# plan-brainstorm

Iterative facilitator for problem framing. Drives the user from a fuzzy ask to a single
recommended direction by surfacing assumptions, options, and trade-offs.

## Usage

```text
/adk:plan-brainstorm                        # interactive
/adk:plan-brainstorm --auto                 # safe defaults, no gates
/adk:plan-brainstorm --topic "auth model"   # seed with a concrete topic
```

In Cursor: invoke via the `prj-update-docs`-installed pointer at
`.cursor/skills/plan-brainstorm/SKILL.md`.

In Codex: same pointer at `.codex/skills/plan-brainstorm/SKILL.md`.

## What it does

Hosts a structured brainstorm: restates the goal, lists 2-3 viable options, asks one
clarifying question at a time, then picks a recommendation with explicit blast-radius and
confidence. Routes downstream to `@adk:plan-spec`, `@adk:plan-design`, `@adk:plan-roadmap`,
or directly to `@adk:build-feature` based on the chosen scope.

## Workflow

1. Restate the ambiguous goal in one sentence.
2. List 2-3 viable directions with one-line trade-offs each.
3. Ask the highest-leverage clarifying question.
4. Update the option set.
5. Loop steps 3-4 until confidence ≥ 80% or 5 rounds.
6. Recommend one direction + the next ADK skill to invoke.

## Decision tree

[Mermaid diagram lives at `diagrams/plan-brainstorm-flow.mermaid` and is embedded with
the `<picture>` pattern.]

## Inputs

| Input    | Required | Notes                                       |
| -------- | -------- | ------------------------------------------- |
| `topic`  | optional | Seed for the brainstorm                     |
| `--auto` | optional | Skip approval gates; pick safe defaults     |

## Brainstorming questions

1. **What's the smallest version of this that's valuable?** — *How to pick:* prefer the
   smallest scope that exercises every layer (data → API → UI).
2. **What's the blast radius if we're wrong?** — *How to pick:* irreversible / cross-team
   = bias to spec; reversible / single-file = bias to build.

## Outputs

A single `.temp/task-<slug>/brainstorm.md` file containing the option set, decision,
rationale, and the next-skill recommendation.

## Related

- `@adk:plan-spec` (a.k.a. `adk-plan-spec`)
- `@adk:plan-design` (a.k.a. `adk-plan-design`)
- `@adk:plan-roadmap` (a.k.a. `adk-plan-roadmap`)
- Subagent: [`agents/brainstorm-facilitator.md`](../agents/brainstorm-facilitator.md)
```

## Worked example — agent page

```markdown
---
title: 'brainstorm-facilitator'
description: 'Subagent that hosts the iterative narrowing loop driven by `plan-brainstorm`.'
artifact_kind: agent
---

# brainstorm-facilitator

## Usage

Invoked automatically by `@adk:plan-brainstorm` and by `@adk:auto` when the prompt is
ambiguous. Direct invocation in Claude:

```text
/agent brainstorm-facilitator
```

## What it does

[...]

## Related

- Driven by skill: [`plan-brainstorm`](../skill-adk-plan-brainstorm.md)
```

## Worked example — config page (single-file aggregate)

For aggregates like `hooks/hooks.json` or `.mcp.json`, use one page with one section per
entry. Section heading = the entry key. Each section follows the same usage / what it does
/ inputs / outputs ordering, scoped down to that entry.

## Cross-link rules

- Every reference to another ADK skill uses the dual-form on first mention:
  `@adk:plan-spec` (a.k.a. `adk-plan-spec`).
- Every reference to a subagent uses a relative link to its doc page.
- Every reference to an upstream package file uses the on-disk path:
  `node_modules/diagramkit/REFERENCE.md` (no link wrap, since the path itself is the
  contract).
- Every internal page-to-page link uses a relative `../section/README.md` path so the
  pagesmith link transform rewrites it under `basePath`.
