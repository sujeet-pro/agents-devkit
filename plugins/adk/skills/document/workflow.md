# document — workflow

Five phases. The phased process is the contract; the **Workflow tool** drives multi-source synthesis and the completeness critic.

## Phase 0 — gather

- Resolve `--type` (or infer it from the intent and state the inference) and `--audience` (default engineer).
- Pull the evidence the doc will cite:
  - **repo facts** — Read / Grep / Glob for the code, configs, and tests the doc describes.
  - **GitHub context** (PR body, issue, commit history) — the `gh` CLI (`gh pr view <url> --json`, `gh issue view`, `gh api`).
  - **external links** — `WebFetch`; **Jira/Confluence** — Atlassian MCP; **dashboards/data** — only if already provided (this skill does not investigate; see `rules.md`).
- For a doc spanning multiple systems, fan out the `context-gatherer` agent (one hop per source).

## Phase 1 — shape

- Read `types.md` for the chosen artifact's contract: what to lead with, the length cap, the must-include sections.
- Pick the single audience voice (`persona.md`) — engineer / pm / exec / mixed. The voice does **not** mix; a "mixed" doc is layered (exec summary up top, engineer detail below), not blended sentence-by-sentence.
- In `-i` mode, confirm the type + audience + outline before drafting.

## Phase 2 — draft (Workflow for multi-source docs)

For a doc that synthesizes more than one system (RCA, ADR weighing alternatives, migration guide across services), drive a **Workflow**:

1. Fan out `context-gatherer` per source + per-section drafting in parallel (each section author gets only the evidence its section needs).
2. Stitch the sections into the type's structure.
3. Run a **completeness-critic** pass: "what's missing, what's uncited, what did we assert without evidence, which must-include section is thin?" Its findings become the next revision.

A simple single-source doc (commit message, a README section, a small changelog entry) is drafted inline. Say you skipped the Workflow.

Cite as you write: every non-trivial claim gets a `path:line` or a ≤15-word quoted source. Concrete before abstract.

## Phase 3 — validate

- **Anti-pattern grep** the draft for filler: `in conclusion`, `it's worth noting`, `robust`, `scalable`, `modern`, `enterprise-grade`, decorative emoji headers. Cut or replace each hit with a fact.
- **Citation check** — every non-trivial claim resolves to a real `path:line` or a real quoted source. No invented paths.
- **Length cap** — within the type's cap (`types.md`). Over → cut, don't append a summary.
- **External-quote cap** — no quoted block over 15 words; paraphrase + cite instead.

## Phase 4 — report

- Write the draft to `--write-to <path>` if given, else the type's suggested local path. Report the path and a one-line summary.
- **This skill never publishes.** It stops at a clean markdown file. Posting to Confluence / Jira / Slack / GitHub is a separate, explicitly-out-of-scope concern (`rules.md`) — tell the user where the draft is and let them publish.

## Narrate

State the type + audience chosen (and any inference), each source gathered, the Workflow fan-out for multi-source docs, and every validator result.
