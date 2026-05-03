# `docs-diagram` — output format

## Per-turn status

```
[adk-docs:docs-diagram] task=<slug> phase=<0|1|2|3|4|5> type=<type> nodes=<N>/15 rendered=<yes|no> mode=<auto|interactive>
```

## `.mermaid` file shape

```
%% <subject> — drawn by adk-docs:docs-diagram on YYYY-MM-DD %%
<mermaid type declaration, e.g. sequenceDiagram>
    <content>
```

Rules:

- First line: single-line Mermaid comment with the subject + date.
- Second line onwards: valid Mermaid source.
- Mermaid type declaration is always on its own line.
- Node IDs: kebab-case, 1-3 words (`cart-svc`, not `CartService`).
- Node labels: human-readable, quoted if they contain spaces.
- Edges: always directed unless the relation is genuinely undirected.
- Avoid subgraphs unless they add clarity — each subgraph counts
  toward the node budget.

## Naming

- Subject kebab-cased: `oidc-login.mermaid`, `orders-schema.mermaid`.
- Pair / split files: `<subject>.overview.mermaid`,
  `<subject>.<zoom>.mermaid`.
- SVG outputs: `<basename>.light.svg` + `<basename>.dark.svg`
  when diagramkit is available.

## Final report shape

`.temp/task-<slug>/report.md`:

```markdown
# docs-diagram report — <slug>

## Result
Authored OIDC login sequence diagram (10 nodes).

## Decisions
| Phase | Question | Picked | Rationale |
| --- | --- | --- | --- |
| 0 | diagram type | sequence | actor + request-response pattern |
| 2 | node budget | 10/15 | under the budget; no split needed |
| 4 | render | light + dark | docs.md.mermaid_render_mode |

## Validation evidence
- mermaid parser: valid
- diagramkit: rendered light.svg + dark.svg in 1.4s

## Residual risk / follow-ups
- None

## Artifact index
.temp/task-<slug>/
  prompt.txt
  oidc-login.mermaid
  oidc-login.light.svg
  oidc-login.dark.svg
  report.md
```

## Embed snippet

For the user to paste into a Markdown doc, the report surfaces:

```
```mermaid
%% <subject> — drawn by adk-docs:docs-diagram on YYYY-MM-DD %%
<content>
```
```

GitHub renders this as a diagram natively (as of 2022-02-14+).
Confluence renders via the Mermaid macro.

## When diagramkit is missing

Report includes:

```
Rendering skipped — @adk/diagramkit not found on PATH.
Install with: `npm i -g @adk/diagramkit`.
Then re-run with `--auto` (or render manually:
`npx @adk/diagramkit render --input <file>.mermaid --output <file>.svg --mode light_and_dark`).
```
