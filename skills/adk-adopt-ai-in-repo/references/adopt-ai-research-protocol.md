# Research Protocol for `adk-adopt-ai-in-repo`

The skill consults sources in the order below. Higher-ranked sources win conflicts. Stop researching when the stop condition is met — diminishing returns past that point.

The goal is to inform `ai-guidelines/coding-guidelines.md`, `testing-guidelines.md`, and the workflow files with current external best practices, NOT to write a textbook. Stay narrow.

## Sources, in order

1. **The repo itself** — every signal from `repo-analysis-playbook.md` is higher-ranked than any external source. If the repo's actual pattern disagrees with an external best practice, the repo wins (but flag the disagreement in `ai-guidelines/coding-guidelines.md` for the user to consider).
2. **Official upstream docs** for the dominant detected stacks — framework docs, language docs, build-tool docs. Always cite with retrieval date.
3. **Repo's own docs** — `README.md`, `CONTRIBUTING.md`, `docs/`, ADRs. Treat as authoritative for project terminology.
4. **The framework's official "best practices" guide or "patterns" doc** — most modern frameworks publish one. Always prefer over community blog posts.
5. **Recent (≤6 months) authoritative blog posts or talks from the framework's core team** — only when the official docs are silent on a question that matters for `coding-guidelines.md`.
6. **Tutorials / Stack Overflow / community blogs** — last resort. Only cite when the question is uncontroversial and the community answer is consensus.

## Stop condition

Each detected stack has enough sourced guidance to populate the relevant sections of `ai-guidelines/coding-guidelines.md`, `testing-guidelines.md`, and the workflow files. The `Sources` section of `ai-guidelines/research/sources.md` lists every source with retrieval date.

## What to research

Research is targeted. For each dominant detected stack (NOT every dependency):

- 2-3 sources for "modern best practices" relevant to the repo's actual usage
- 1-2 sources for the framework's recommended testing patterns
- 1-2 sources for the framework's recommended file organization (only if the repo lacks a clear pattern)

Skip researching: minor dependencies, low-priority tools (formatter, build runner), one-off scripts.

## Evidence buckets

For every sourced claim that lands in the generated guidelines, label it (in `.temp/notes/adopt-ai-<repo-slug>-evidence.md`):

- `Verified` — official source with retrieval date, or repo evidence with file:line.
- `Inferred` — extrapolated from related sources; explicitly note in the guideline if the inference matters.
- `Open` — could not verify; goes in the "open questions" section of the evidence summary, not in the generated guideline.

## Citation discipline

- Cite official docs as `Source: <name>, <url>, fetched <YYYY-MM-DD>`.
- Cite repo evidence as `path/to/file.ext:LINE-LINE` or `<file>` if the whole file is the source.
- Cite git commits as short SHAs from the host repo.
- The list lands in `ai-guidelines/research/sources.md`.

## Freshness

Treat any external web source older than 6 months for fast-moving libraries (React, Vite, Next.js, browser APIs, Node) as suspect — verify against the latest official changelog before using.

For language-level docs (Python `typing`, Go `errors`, etc.), older sources are usually fine.

## Multi-stack repos

For a monorepo with multiple stacks, research each dominant stack independently. Do NOT try to create a "unified" guideline that papers over real differences. Use per-package sections in `ai-guidelines/coding-guidelines.md` if the patterns diverge.

## When NOT to research

- The user passed `--scope <stack>` and the question is about a different stack.
- The repo has a clear ADR / RFC that decides the question (the ADR is the source of truth).
- The question is about repo conventions, not external best practice (read the repo).
- Time pressure: under `--auto`, cap external research to a fixed budget (e.g., 5 minutes wall-clock per stack); fall back to repo evidence + flag as "needs more research" in the manual follow-up.
