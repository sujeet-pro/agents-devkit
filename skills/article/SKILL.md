---
name: article
description: Write, review, or update deep technical articles with exhaustive research, principal engineer voice, and comprehensive edge case coverage
user_invocable: true
arguments:
  - name: mode
    description: "Mode: write, review, update (default: write). 'review' analyzes existing content and suggests improvements. 'update' applies improvements directly."
    required: false
  - name: topic
    description: "Article topic (required for write mode)"
    required: false
  - name: source
    description: "Path to existing article (required for review/update modes)"
    required: false
  - name: depth
    description: "Depth level: standard, exhaustive (default: exhaustive)"
    required: false
  - name: audience
    description: "Target audience: senior, staff, principal (default: senior)"
    required: false
  - name: format
    description: "Output format: markdown, confluence, google-doc (default: markdown)"
    required: false
---

# Technical Article — Write, Review & Update

> **Dependencies**: This skill works best with the full devkit installed (`/plugin install devkit-full@claude-devkit` or `./install.sh`). It uses guidelines from `guidelines/document/` and `guidelines/coding/`, and delegates to agents (`research-agent`, `code-snippet-agent`, `diagram-agent`). If guidelines or agents are missing, the skill still works but with reduced quality enforcement.

Write new deep technical articles, review existing ones, or update them with current information. Articles are long-form, evidence-based, and authoritative — the kind of content that becomes a reference bookmark.

## Mode Detection

If `mode` is not specified, auto-detect:
- If `source` is provided and `topic` is not → `review`
- If both `source` and `topic` are provided → `update`
- If only `topic` is provided → `write`

## Agent & Skill Delegation

**Always use the devkit's own agents and skills for delegation:**

| Task | Delegate To |
|------|-------------|
| Research | `/research` skill (spawns **research-agent**) — NEVER do ad-hoc web searches yourself |
| Code blocks | **code-snippet-agent** (expressive-code conventions) |
| Diagrams | `/diagram` skill → **diagram-agent** → excalidraw-agent or mermaid-agent |
| Markdown output | `/markdown` skill |
| Confluence publishing | `/confluence-publish` skill |

---

## Write Mode

### Step 1 — Research

Invoke the `/research` skill with `depth=exhaustive`:

```
/research --topic="<topic>" --depth=exhaustive
```

The research must cover:

- **Official specs and RFCs** — The canonical source of truth
- **Authoritative documentation** — Official project/language/framework docs
- **Real-world case studies** — How companies applied this in production
- **Performance benchmarks** — Numbers, not opinions
- **Edge cases and gotchas** — Hard-won production experience

**Source priority** (highest to lowest):

| Priority | Source Type | Example |
|---|---|---|
| 1 | Specs / RFCs | RFC 7540 (HTTP/2), ECMAScript spec |
| 2 | Official docs | MDN, Go docs, Rust reference |
| 3 | Core maintainers | Blog posts or talks by project leads |
| 4 | Source code | Reading the actual implementation |
| 5 | Academic papers | Peer-reviewed research |
| 6 | Industry experts | Staff+ engineers with production experience |

Every factual claim in the article must trace back to one of these sources. No unsourced claims.

### Step 2 — Load Guidelines

Load the following guidelines in order:

1. `guidelines/document/article.md` — article-specific structure and voice rules
2. `guidelines/document/general.md` — baseline markdown and document conventions
3. `guidelines/coding/expressive-code.md` — code block formatting rules

**Repo-level guideline discovery** (highest priority — overrides devkit guidelines):

Check these locations in order. Load the first match found in each category:

| Category | Paths to Check (in priority order) |
|----------|-----------------------------------|
| **Document guidelines** | `docs/guidelines/document/`, `guidelines/document/`, `.github/guidelines/`, `CLAUDE.md` (section: `## Document Guidelines` or `## Writing Guidelines`) |
| **Coding guidelines** | `docs/guidelines/coding/`, `guidelines/coding/`, `coding-guidelines/`, `CLAUDE.md` (section: `## Coding Guidelines` or `## Code Style`) |
| **Markdown conventions** | `.markdown-guidelines.md`, `MARKDOWN.md`, `docs/markdown-style.md` |

Repo-level guidelines take **higher priority** than devkit guidelines. If both exist, load repo guidelines first, then devkit guidelines as fallback for uncovered areas.

### Step 3 — Outline

Present a detailed outline to the user for approval. The outline must follow the article guideline structure:

1. **H1 Title** — Clear, specific, searchable
2. **Description paragraphs** — First 1–2 paragraphs auto-extracted as meta description. Write for both humans and search engines.
3. **Overview diagram** — Excalidraw-based (via `/diagram`). High-level visual that orients the reader before diving in.
4. **Abstract** — A mental model or framework for thinking about the topic. This is NOT a summary of sections. It is the conceptual lens through which the reader should understand everything that follows.
5. **Deep Analysis sections** (H2/H3) — The core content. Each section explores one facet of the topic in depth.
6. **Edge Cases & Gotchas** — Dedicated section for things that bite you in production.
7. **Benchmarks / Evidence** — Data-driven section with numbers, comparisons, methodology.
8. **Practical Application** — How to apply the knowledge. Working examples, step-by-step.
9. **Conclusion** — Synthesis, not summary. What mental model should the reader walk away with?
10. **Appendix** — Prerequisites, Terminology, Summary table, References.

Wait for user approval or revision requests before proceeding.

### Step 4 — Writing

Use the **principal engineer voice**: peer-to-peer, authoritative but not condescending, precise but not dry.

**Main writing rules:**
- Explain "why" before "how" — motivation first, implementation second.
- Make trade-offs explicit — every design choice has costs. Name them.
- Use real-world examples — "At Company X, this caused a 3-hour outage because..."
- Anticipate objections — address "but what about..." before the reader thinks it.
- Layer complexity — start with the simple mental model, then reveal nuance.
- No hedging without substance — "it depends" must always be followed by "on what."

**Code blocks:**
- Delegate to the **code-snippet-agent**.
- **Mandatory**: every code block has `title="filename.ext"`.
- **Mandatory**: collapse import blocks with `collapse={1-N}`.
- **Mandatory**: highlight key lines with `{line-numbers}`.
- Code must be realistic — no `foo/bar` examples. Use domain-relevant names.
- Show the full picture: setup, execution, and output where relevant.

**Diagrams:**
- Delegate to `/diagram` skill.
- Overview / architecture diagrams → **Excalidraw** (hand-drawn aesthetic for high-level views).
- Detailed flow / sequence / state diagrams → **Mermaid** (text-based, version-controllable).
- Multiple diagrams expected: at minimum an overview diagram plus detail diagrams for complex sections.
- Save source + rendered SVG in `diagrams/`.

### Step 5 — Output

Use the `/markdown` skill for file generation:

- `title` = article title
- `frontmatter` = yes (articles benefit from metadata)
- `confluence-sync` = yes if `format=confluence`
- `doc-type` = article

Multiple diagrams are expected. The output folder should have a populated `diagrams/` directory.

For non-markdown formats:
- `confluence` → Generate markdown first, then publish via `/confluence-publish`
- `google-doc` → Generate markdown first, then convert via Google Drive MCP tools

### Step 6 — Iterative Quality Loop

Run an iterative review-fix cycle on the draft. **Max 3 iterations.** Each iteration:

```
iteration = 0
max_iterations = 3

while iteration < max_iterations:
    iteration += 1
    issues = review_against_checklist()
    if no CRITICAL or WARNING issues: break
    fix(issues)
    if no fixes applied this iteration: break  # stuck — stop
```

**Quality checklist** (verify against `guidelines/document/article.md`):

| Check | Severity | Action |
|---|---|---|
| Every claim has a traceable source | CRITICAL | Add source or remove claim |
| Every code block has `title=` + `collapse=` | CRITICAL | Add missing metadata via **code-snippet-agent** |
| Abstract is a mental model, not a section summary | CRITICAL | Rewrite if it reads like a TOC |
| Heading hierarchy is sequential | CRITICAL | Fix skipped levels |
| Overview diagram exists (Excalidraw) | WARNING | Generate via `/diagram` |
| Detail diagrams for complex sections (Mermaid) | WARNING | Generate via `/diagram` |
| Edge cases section is substantive | WARNING | Expand with real examples |
| Benchmarks include methodology | WARNING | Add methodology or qualify claims |
| All diagrams render correctly and have alt text | WARNING | Fix broken diagrams |
| References are spec-first | INFO | Reorder if needed |
| Consistent terminology throughout | INFO | Standardize terms |

**Convergence rules:**

| Condition | Action |
|-----------|--------|
| No CRITICAL or WARNING issues remain | **Done** — present to user |
| `iteration >= 3` | **Max reached** — present remaining issues to user |
| No fixes applied in this iteration | **Stuck** — present remaining issues for human decision |
| Same issue reappears after fix | **Stuck** — stop and report |

Fix **CRITICAL** and **WARNING** issues automatically each iteration. Present **INFO**-level suggestions after the loop completes.

**Diagram requirements:**
- Articles MUST have an overview diagram (Excalidraw) at the top
- Each complex section SHOULD have a detail diagram (Mermaid)
- Minimum 2 diagrams for standard depth, 4+ for exhaustive
- Every diagram must have descriptive alt text and a source file in `diagrams/`

---

## Review Mode

Analyze an existing article and provide structured feedback.

### Step 1 — Load Content

Read the article from `source` path. If the source is a URL (Confluence, Google Docs), fetch it using the appropriate MCP tool.

### Step 2 — Load Guidelines

Same as Write Mode Step 2.

### Step 3 — Research (Fact-Check & Currency)

Invoke the `/research` skill with `depth=exhaustive` to:
- Verify all factual claims and cited sources
- Check if referenced technologies, APIs, or libraries have had breaking changes
- Identify significant new developments in the topic since the article was written
- Find any new benchmarks or case studies that should be incorporated

### Step 4 — Multi-Dimensional Review

Evaluate the article across these dimensions:

| Dimension | What to Check |
|---|---|
| **Accuracy** | Are all claims correct and properly sourced? Any outdated information? |
| **Completeness** | Are there significant aspects of the topic not covered? Missing edge cases? |
| **Depth** | Does the analysis go deep enough? Are trade-offs explicit? |
| **Structure** | Follows article guideline structure? Abstract is a mental model? |
| **Voice** | Principal engineer voice? Peer-to-peer, not condescending? |
| **Code Quality** | All blocks have title, collapse, highlighting? Realistic examples? |
| **Diagrams** | Overview diagram exists? Detail diagrams for complex sections? |
| **Evidence** | Benchmarks include methodology? Claims backed by data? |
| **Edge Cases** | Dedicated section? Substantive? Real production examples? |
| **References** | Spec-first ordering? All sources valid and accessible? |

### Step 5 — Present Findings

Present findings grouped by severity (CRITICAL → WARNING → INFO), with specific locations and suggested fixes. Ask the user if they want to apply fixes (transition to Update mode).

---

## Update Mode

Apply improvements to an existing article.

### Step 1 — Load & Analyze

Read the existing article from `source`. If `topic` is also provided, use it as guidance for the direction of updates.

### Step 2 — Research

Invoke `/research --depth=exhaustive` to gather current information relevant to the updates needed. Focus on:
- Areas identified as outdated or incomplete
- New developments since the original was written
- Updated benchmarks or case studies

### Step 3 — Load Guidelines

Same as Write Mode Step 2.

### Step 4 — Propose Changes

Present a summary of proposed changes:
- Sections to add/remove/rewrite
- Factual corrections with sources
- New edge cases or benchmarks to include
- Structural improvements
- Code block updates

Wait for user approval before applying changes.

### Step 5 — Apply Changes

Edit the existing file in-place. Preserve the author's voice, structure, and style where possible. Do not rewrite sections that don't need changes. Ensure new content matches the quality bar of existing content.

### Step 6 — Iterative Quality Loop

Run the same iterative quality loop as Write Mode Step 6 on the updated content. Same convergence rules apply (max 3 iterations, stuck detection).

---

## Voice Guide

| Audience | Calibration |
|---|---|
| `senior` | Explain architectural context, skip basic syntax |
| `staff` | Assume systems thinking, focus on trade-offs and failure modes |
| `principal` | Peer discussion, challenge assumptions, explore second-order effects |

## Depth Levels

| Depth | Research Time | Sections | Word Count |
|---|---|---|---|
| `standard` | Moderate | Core sections + practical application | 2000–4000 |
| `exhaustive` | Extensive | All sections including appendix | 4000–8000+ |
