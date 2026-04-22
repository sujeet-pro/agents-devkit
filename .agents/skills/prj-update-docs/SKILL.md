---
name: prj-update-docs
description: |
  Full documentation refresh for the agents-devkit (ADK) repo. Walks every skill, agent, hook,
  bin, MCP server, and config in the repo, regenerates one canonical Pagesmith page per artifact
  under `docs/`, embeds and validates Mermaid/Excalidraw/Drawio/Graphviz diagrams via diagramkit,
  and proves the docs site builds and is in sync with the actual implementation. Use when the
  user says "update the docs", "refresh the doc site", "review and regenerate everything",
  "make sure docs match the code", or before a release. Do not use to author one specific doc
  (use `adk-docs-write`) or to set up the docs site for the first time (use `adk-doc-site-setup`).
metadata:
  category: docs
  kind: task
  layer: 7
  modes: [auto, review, fix]
  needs_mcp: []
disable-model-invocation: false
---

# prj-update-docs — full doc + diagram sync for this repo

The single command/skill the user runs to bring `docs/` back in sync with what the repo
actually ships. It is the project-local wrapper around two upstream skill packs:

| Pack             | Where it lives                                     | Owns                                                      |
| ---------------- | -------------------------------------------------- | --------------------------------------------------------- |
| `@pagesmith/docs` | `node_modules/@pagesmith/docs/`                    | doc structure, frontmatter, markdown features, dev/build  |
| `diagramkit`     | `node_modules/diagramkit/`                         | diagram authoring + render + validate (incl. WCAG 2.2 AA) |

This skill never re-implements either pack — it **delegates** to their version-pinned
references and skills (read order in [`references/read-order.md`](references/read-order.md)).

## Usage

Invoke as a Claude Code plugin skill (this repo is published as the `adk` plugin and exposes
project-local skills via `.agents/skills/`):

```text
/adk:prj-update-docs                # full interactive run
/adk:prj-update-docs --auto         # unattended; pick safe defaults
/adk:prj-update-docs --mode review  # report drift only, no writes
/adk:prj-update-docs --mode fix     # apply doc + diagram fixes
/adk:prj-update-docs --scope skills # limit to one artifact category
```

In Cursor / Codex / generic agents the same skill is reachable through the matching pointer
in `.cursor/skills/prj-update-docs/SKILL.md`, `.codex/skills/prj-update-docs/SKILL.md`,
or `.agents/skills/prj-update-docs/SKILL.md` (this file).

Plain prompts that should auto-trigger this skill:

- "Update the docs for this to reflect what is actually implemented."
- "Regenerate one page per skill / agent."
- "Run the full doc + diagram refresh and tell me what changed."
- "Make sure every diagram still renders and passes contrast."

## What it does (high level)

For every artifact in the repo (skills, agents, hooks, bin scripts, MCP servers, monitors,
config files, top-level memory files), produce one canonical Pagesmith page that contains:

1. **How to use it** — copy-pasteable Claude / Cursor / Codex invocations.
2. **What it does** — one-paragraph high-level summary written from the actual source.
3. **Workflow / decision tree** — the steps it runs, with a Mermaid diagram when there is a
   real branching flow.
4. **Inputs / brainstorming questions / outputs** — what the artifact asks, what it expects,
   what it produces.
5. **Cross-links** — to every other skill / agent / hook the artifact delegates to or is
   delegated to from.

Then re-render and validate every diagram, then build the docs site, then write a single
report under `.temp/prj-update-docs/<timestamp>/report.md`.

## Read first (every run)

In this exact order, before touching any file:

1. [`references/read-order.md`](references/read-order.md) — the full read-order, with one
   line on what each upstream file unblocks.
2. `node_modules/@pagesmith/docs/REFERENCE.md` — version-pinned config, frontmatter,
   `meta.json5` schema, layout overrides, build flags.
3. `node_modules/@pagesmith/docs/ai-guidelines/docs-guidelines.md` — AI-first authoring
   rules (lead with the task, skimmable structure, deliberate organisation, diagram
   guidance).
4. `node_modules/@pagesmith/docs/ai-guidelines/markdown-guidelines.md` — exact markdown
   features supported (GFM, alerts, math, code-block meta, image embed patterns).
5. `node_modules/@pagesmith/docs/ai-guidelines/setup-docs.md` — for any retrofit-style
   reorganisation of `docs/`.
6. `node_modules/diagramkit/REFERENCE.md` — version-pinned CLI + API + supported
   extensions for the installed `diagramkit`.
7. `node_modules/diagramkit/skills/diagramkit-auto/SKILL.md` — engine selection table for
   any *new* diagram this run might produce.
8. `node_modules/diagramkit/skills/diagramkit-review/SKILL.md` — the cross-engine
   audit + repair workflow used in the validation phase.
9. The matching engine skill for any source extension found in this repo:
   - `node_modules/diagramkit/skills/diagramkit-mermaid/SKILL.md`
   - `node_modules/diagramkit/skills/diagramkit-excalidraw/SKILL.md`
   - `node_modules/diagramkit/skills/diagramkit-draw-io/SKILL.md`
   - `node_modules/diagramkit/skills/diagramkit-graphviz/SKILL.md`
10. [`AGENTS.md`](../../../AGENTS.md), [`CLAUDE.md`](../../../CLAUDE.md), and
    [`pagesmith.config.json5`](../../../pagesmith.config.json5) for the project-specific
    constitution and current site config.

If any of the `node_modules/...` paths are missing, run `npm install` first — never fall
back to a globally installed `diagramkit` or `pagesmith-docs`.

## Inputs

| Input              | Required | Notes                                                                                                                |
| ------------------ | -------- | -------------------------------------------------------------------------------------------------------------------- |
| `<scope>`          | optional | `all` (default), `skills`, `agents`, `hooks`, `bin`, `mcp`, `monitors`, `config`, `diagrams-only`                    |
| `<since>`          | optional | Git ref (e.g. `HEAD~10` or a tag); only re-render pages whose source has changed since that ref                      |
| `--mode`           | optional | `auto` (default; write + validate), `review` (read-only report), `fix` (only apply diff to existing pages)           |
| `--auto`           | optional | Skip approval gates; pick the safest answer for every clarifying question (logged in the report)                     |
| `--no-diagrams`    | optional | Skip the diagram render + validate phase (still surfaces drift)                                                      |
| `--no-build`       | optional | Skip the `pagesmith-docs build` smoke test                                                                           |
| `--report-only`    | optional | Alias for `--mode review`                                                                                            |

## Workflow

The full decision tree, including stop-loss and re-entry points, lives in
[`references/how-it-works.md`](references/how-it-works.md). Summary:

| Phase | Goal                                              | Tool / Delegated skill                                          |
| ----- | ------------------------------------------------- | --------------------------------------------------------------- |
| 0     | Confirm intent + load read-order                  | This SKILL.md + `references/read-order.md`                      |
| 1     | Inventory the repo (artifacts to document)        | `references/inventory-rules.md`                                 |
| 2     | Brainstorm scope + audience                       | `references/inputs-and-brainstorming.md` (skipped under `--auto`) |
| 3     | Read existing docs, diff against current source   | `references/drift-rules.md`                                     |
| 4     | Per-artifact page generation / refresh            | `references/page-template.md` + `adk-docs-write` for prose      |
| 5     | Diagram authoring (only where prose is unclear)   | `diagramkit-auto` → engine SKILL                                 |
| 6     | Diagram render + validate (cross-engine)          | `diagramkit-review` (force re-render + validate + WCAG fixes)   |
| 7     | Pagesmith build smoke test                        | `npx pagesmith-docs build` (and `dev` if interactive)           |
| 8     | Final report + links checklist                    | `references/output-format.md`                                   |

Each phase is interactive by default per the project [interaction
contract](../../../bin/canonical/interaction-contract.md); `--auto` short-circuits the gates
and logs every choice to the report.

## Per-artifact page template

This is the **only** template every generated page must follow. Implementation details and
worked examples live in [`references/page-template.md`](references/page-template.md).

```markdown
---
title: '<artifact-name>'
description: '<one-sentence purpose lifted from the source frontmatter or top-of-file>'
skill_name: <artifact-name>            # for skills only
artifact_kind: skill | agent | hook | bin | mcp | monitor | config | memory
category: <from manifest or inferred>  # for skills only
---

# <artifact-name>

<2-3 sentence high-level summary written from the actual source — never aspirational.>

## Usage

> Examples assume this repo is installed as the `adk` Claude Code plugin
> (see [Quick Start](../../guide/...)).

```text
/adk:<artifact>          # interactive run
/adk:<artifact> --auto   # unattended
```

Plus one Cursor and one Codex invocation when the artifact is exposed there.

## What it does

<1-2 paragraphs, high-level — what problem does it solve, who is it for, what does it
produce. Pulled from the SKILL.md / agent.md description and the constitution / persona
references when present.>

## Workflow

<Numbered steps. Mermaid `flowchart TD` only when there is real branching — never as
decoration. Source `.mermaid` lives next to the page under `diagrams/`, rendered SVG
embedded with the `<picture>` pattern.>

## Decision tree

<Only when the artifact branches on inputs. Otherwise omit the section.>

## Inputs

| Input | Required | Notes |
| ----- | -------- | ----- |

## Brainstorming questions

<Only for skills/agents that ship clarifying questions. List each question + the
"how to pick" rubric from `clarifying-questions.md`.>

## Outputs

<Final artifact(s), report shape, where they land on disk.>

## Related

- Skills: <links to every skill it delegates to or is delegated from>
- Agents: <links to every agent it invokes>
- Hooks: <links to hook entries that gate it>
- Upstream: links to the matching `node_modules/...` reference when applicable
```

## Diagram policy

Per the upstream guidance in `node_modules/@pagesmith/docs/ai-guidelines/docs-guidelines.md`
(Diagram Guidance section) and in `node_modules/diagramkit/skills/diagramkit-auto/SKILL.md`:

- Add a diagram **only** when prose is unclear — flow, lifecycle, dependency graph, or
  architecture. A short list or table is preferred when it is clearer.
- The editable source (`*.mermaid`, `*.excalidraw`, `*.drawio`, `*.dot`) lives in a
  page-local `diagrams/` folder, alongside the rendered SVG.
- Embed with the theme-aware `<picture>` pattern (see
  [`references/diagram-policy.md`](references/diagram-policy.md)).
- Engine selection follows the table in `diagramkit-auto`. **Default to Mermaid** unless a
  tie-break rule applies.
- Every Mermaid source meant to be embedded as `<img>` starts with
  `%%{init: {'htmlLabels': false}}%%`.
- Every diagram is rendered **and** validated; runs do not finish while any of these are
  open: render failure, `LOW_CONTRAST_TEXT`, `ASPECT_RATIO_EXTREME`, or any
  `severity: "error"` from `diagramkit validate`.

## Validation

After page generation and diagram render:

1. `npx diagramkit render . --force --json` — rerender every source, even if the manifest
   hash matches.
2. `npx diagramkit validate . --recursive --json` — surface every issue.
3. Iterative fix loop, capped at 8 per file, delegated to the engine `Review Mode` from
   each diagramkit engine SKILL. Residuals are logged into the final report.
4. `npx pagesmith-docs build` — production build must exit 0. Build warnings are surfaced
   in the report.
5. Optional `npx pagesmith-docs dev` smoke test (when interactive) — confirm `/` and one
   freshly-generated section index page each return 200.
6. Internal markdown link checker (every relative link to another generated page must
   resolve under `basePath`).

## Output

A single report at `.temp/prj-update-docs/<timestamp>/report.md` plus an updated `docs/`
tree. The report shape is fully specified in
[`references/output-format.md`](references/output-format.md). Highlights:

- **Pages**: created / updated / unchanged / deleted, grouped by artifact kind.
- **Drift**: each documented behaviour that diverged from the source, with `file:line`.
- **Diagrams**: rendered, validated, residual issues, contrast fixes applied.
- **Build**: pagesmith-docs build status, warnings.
- **Links**: broken internal links + the page that owns each.
- **Choices**: every default the skill picked under `--auto` (so the user can override).

## Anti-patterns

- Re-implementing `pagesmith-docs` or `diagramkit` CLI commands inside this skill — always
  shell out to `npx` against the **locally installed** package.
- Documenting wished-for behaviour. Every page must be grounded in `git ls-files` evidence.
- Hand-editing rendered SVGs in `.diagramkit/`.
- Adding diagrams as decoration — read the diagram policy first.
- Changing `pagesmith.config.json5` without surfacing the diff in the report.
- Splitting a single artifact across multiple pages, or merging multiple artifacts into one.
- Skipping the `pagesmith-docs build` smoke test.
- Skipping the WCAG 2.2 AA contrast loop in `diagramkit validate`.
- Using a globally installed `pagesmith-docs` or `diagramkit` (always `npx ...` against
  `node_modules/`).

## References shipped with this skill

| File                                                | Purpose                                                                                       |
| --------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| [`references/read-order.md`](references/read-order.md)                       | The full upstream read-order with one line per file.                  |
| [`references/how-it-works.md`](references/how-it-works.md)                   | Phase-by-phase workflow + decision tree (with Mermaid diagram).       |
| [`references/inventory-rules.md`](references/inventory-rules.md)             | How to enumerate skills / agents / hooks / bin / mcp / config.        |
| [`references/inputs-and-brainstorming.md`](references/inputs-and-brainstorming.md) | Clarifying questions + safe `--auto` defaults.                  |
| [`references/page-template.md`](references/page-template.md)                 | The exact per-artifact page template, section by section.             |
| [`references/diagram-policy.md`](references/diagram-policy.md)               | When to add a diagram, engine routing, embed pattern.                 |
| [`references/drift-rules.md`](references/drift-rules.md)                     | How to detect that a doc has drifted from its source artifact.        |
| [`references/output-format.md`](references/output-format.md)                 | Final report shape, severity labels.                                  |
| [`references/anti-patterns.md`](references/anti-patterns.md)                 | Things to avoid — mirrors the section above with examples.            |
