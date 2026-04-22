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
---

# prj-update-docs

Follow the canonical project-local skill at:

→ [`.agents/skills/prj-update-docs/SKILL.md`](../../../.agents/skills/prj-update-docs/SKILL.md)

It defers in turn to the version-pinned upstream packs in:

- `node_modules/@pagesmith/docs/REFERENCE.md` and `node_modules/@pagesmith/docs/ai-guidelines/*`
- `node_modules/diagramkit/REFERENCE.md` and `node_modules/diagramkit/skills/*`

Do not duplicate the canonical content here — Claude Code reads this pointer, follows the
link, and uses the version-pinned references inside `node_modules/`. That keeps every
`/adk:prj-update-docs` invocation in lockstep with the installed `@pagesmith/docs` and
`diagramkit` versions.
