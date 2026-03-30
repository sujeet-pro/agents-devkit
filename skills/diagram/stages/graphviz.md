# Graphviz Diagram

Prefer Mermaid, Excalidraw, or draw.io engines for new documentation work. Use this stage when the repository already uses Graphviz or when strict DOT layout control is clearly the best fit.

## Phase Applicability

| Phase | Applies | Skill-Specific Notes |
|-------|---------|----------------------|
| 0. Intent Expansion | yes | Confirm the goal, assumptions, required tools, and success criteria before acting |
| 1. Research & Options | yes | Analyze requirements, determine diagram type and structure |
| 2. Approach Selection | skip | Direct execution after early confirmation |
| 3. Planning | skip | Direct execution |
| 4. Execute | yes | Generate diagram source files |
| 5. Validate & Learn | yes | Verify renderability, naming, consistency |

## Preflight

Before drafting or rendering Graphviz assets, run:

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

If rendering is required, ensure `dot` is available. Prefer SVG unless the destination requires a raster format.

## Included Helpers

- `scripts/render-graphs.js` extracts `dot` blocks from a skill and renders them
- `references/graphviz-conventions.dot` captures the Graphviz style guide used by this repo

## Rules

- Keep Graphviz usage intentional and limited.
- Do not choose Graphviz by default when Mermaid, Excalidraw, or draw.io would be easier to maintain.
- When updating existing `.dot` assets, preserve their current conventions unless the caller asks for a cleanup.
