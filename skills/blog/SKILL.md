---
name: blog
description: Write, review, or update blog posts with narrative structure, clear opinions, and engaging formatting
user_invocable: true
arguments:
  - name: mode
    description: "Mode: write, review, update (default: write). 'review' analyzes existing content and suggests improvements. 'update' applies improvements directly."
    required: false
  - name: topic
    description: "Blog post topic or title (required for write mode)"
    required: false
  - name: source
    description: "Path to existing blog post (required for review/update modes)"
    required: false
  - name: audience
    description: "Target audience: developers, managers, general (default: developers)"
    required: false
  - name: tone
    description: "Tone: conversational, technical, opinionated (default: conversational)"
    required: false
  - name: format
    description: "Output format: markdown, confluence, google-doc (default: markdown)"
    required: false
---

# Blog Post — Write, Review & Update

> **Dependencies**: This skill works best with the full devkit installed (`/plugin install devkit-full@claude-devkit` or `./install.sh`). It uses guidelines from `guidelines/document/` and `guidelines/coding/`, and delegates to agents (`research-agent`, `code-snippet-agent`, `diagram-agent`). If guidelines or agents are missing, the skill still works but with reduced quality enforcement.

Write new blog posts, review existing ones for quality, or update them with improvements. Blog posts are shorter, opinion-driven, and narrative — designed to be read in one sitting.

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

## Word Count Targets

| Type | Word Count |
|---|---|
| Standard post | 800–1500 words |
| Deep-dive post | Up to 2500 words |

Prefer shorter. Every sentence must earn its place.

---

## Write Mode

### Step 1 — Research

Invoke the `/research` skill with `depth=standard`:

```
/research --topic="<topic>" --depth=standard
```

The research must gather:

- Current facts and data relevant to the topic
- Relevant real-world examples and anecdotes
- Counterarguments and alternative viewpoints
- Recent developments or news (if time-sensitive topic)

Standard research ensures enough depth for a well-supported blog post — not just surface-level facts.

### Step 2 — Load Guidelines

Load the following guidelines in order. If a guideline file is not found, log a warning and continue — the skill works without them, just with less specific quality checks.

1. `guidelines/document/blog.md` — blog-specific structure and voice rules
2. `guidelines/document/general.md` — baseline markdown and document conventions
3. `guidelines/coding/expressive-code.md` — if the post includes code blocks (technical audience)

**Repo-level guideline discovery** (highest priority — overrides devkit guidelines):

Check these locations in order. Load the first match found in each category:

| Category | Paths to Check (in priority order) |
|----------|-----------------------------------|
| **Document guidelines** | `docs/guidelines/document/`, `guidelines/document/`, `.github/guidelines/`, `CLAUDE.md` (section: `## Document Guidelines` or `## Writing Guidelines`) |
| **Coding guidelines** | `docs/guidelines/coding/`, `guidelines/coding/`, `coding-guidelines/`, `CLAUDE.md` (section: `## Coding Guidelines` or `## Code Style`) |
| **Markdown conventions** | `.markdown-guidelines.md`, `MARKDOWN.md`, `docs/markdown-style.md` |

Repo-level guidelines take **higher priority** than devkit guidelines. If both exist, load repo guidelines first, then devkit guidelines as fallback for uncovered areas.

### Step 3 — Outline

Present an outline to the user for approval before writing. The outline must follow the blog guideline structure:

1. **Hook** — Opening that grabs attention (question, bold claim, relatable frustration, surprising fact)
2. **Context** — Brief background so the reader understands why this matters
3. **Thesis** — The one core idea or opinion the post argues
4. **Supporting Arguments** — 2–4 sections that build the case (each with a scannable H2)
5. **Practical Takeaway** — What the reader should do differently after reading
6. **Conclusion / CTA** — Wrap up and call to action (try it, share it, comment, etc.)

Wait for user approval or revision requests before proceeding.

### Step 4 — Writing

Delegate to specialized agents:

**Main writing:**
- Follow blog guidelines: short paragraphs (2–4 sentences max), conversational tone, scannable headings.
- One idea per post — if you find yourself covering two big ideas, suggest splitting into a series.
- Use the author's voice: first person, direct, opinionated where appropriate.
- Vary sentence length for rhythm. Mix short punchy sentences with longer explanatory ones.
- Use concrete examples over abstract explanations.

**Code blocks** (if technical):
- Delegate to the **code-snippet-agent**.
- Apply expressive-code features: `title=`, `collapse={}`, `{highlighting}`.
- Keep code blocks short and focused — blog readers skim code.
- Every code block needs a 1–2 sentence explanation before it.

**Diagrams** (if visual aids help):
- Delegate to `/diagram` skill.
- Prefer simple, clean diagrams — blogs are not architecture docs.
- One or two diagrams max for a standard post.

### Step 5 — Output

Use the `/markdown` skill for file generation:

- `title` = blog post title
- `frontmatter` = depends on format (yes for markdown blogs with metadata needs)
- `confluence-sync` = yes if `format=confluence`

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

**Quality checklist** (verify against `guidelines/document/blog.md`):

| Check | Severity | Action |
|---|---|---|
| Hook exists and is compelling | CRITICAL | Fix if missing or weak |
| Single thesis is clear | CRITICAL | Refocus if muddled |
| At least 1 diagram for technical posts | WARNING | Generate via `/diagram` |
| Paragraphs ≤ 4 sentences | WARNING | Break up long paragraphs |
| Headings are scannable | WARNING | Rewrite vague headings |
| Code blocks have titles + context | WARNING | Add missing metadata via **code-snippet-agent** |
| Word count in target range | WARNING | Trim or expand as needed |
| CTA is present | WARNING | Add if missing |
| All factual claims verified by research | CRITICAL | Correct or remove unsourced claims |
| Diagrams render correctly and have alt text | WARNING | Fix broken diagrams |
| References are spec-first | INFO | Reorder if needed |

**Convergence rules:**

| Condition | Action |
|-----------|--------|
| No CRITICAL or WARNING issues remain | **Done** — present to user |
| `iteration >= 3` | **Max reached** — present remaining issues to user |
| No fixes applied in this iteration | **Stuck** — present remaining issues for human decision |
| Same issue reappears after fix | **Stuck** — stop and report |

Fix **CRITICAL** and **WARNING** issues automatically each iteration. Present **INFO**-level suggestions to the user after the loop completes.

**Diagram requirements:**
- Technical blog posts MUST have at least 1 diagram (concept visualization, flow, or architecture)
- Generate via `/diagram` skill — prefer Mermaid for inline rendering, Excalidraw for header/overview
- Every diagram must have descriptive alt text

---

## Review Mode

Analyze an existing blog post and provide structured feedback.

### Step 1 — Load Content

Read the blog post from `source` path. If the source is a URL (Confluence, Google Docs), fetch it using the appropriate MCP tool.

### Step 2 — Load Guidelines

Same as Write Mode Step 2.

### Step 3 — Research (Fact-Check)

Invoke the `/research` skill with `depth=standard` to verify:
- Factual claims made in the post
- Whether any referenced tools/libraries/APIs have changed since the post was written
- Whether the topic has significant new developments that should be addressed

### Step 4 — Multi-Dimensional Review

Evaluate the blog post across these dimensions:

| Dimension | What to Check |
|---|---|
| **Structure** | Does it follow Hook → Context → Thesis → Arguments → Takeaway → CTA? |
| **Voice & Tone** | Is it consistent? Does it match the specified tone? First person, direct? |
| **Accuracy** | Are all claims supported? Any outdated information? |
| **Engagement** | Is the hook compelling? Are headings scannable? Is there a clear CTA? |
| **Readability** | Paragraphs ≤ 4 sentences? Varied sentence length? Concrete examples? |
| **Code Quality** | Code blocks have titles, highlighting, and context? Realistic examples? |
| **Word Count** | Within target range? |

### Step 5 — Present Findings

Present findings grouped by severity (CRITICAL → WARNING → INFO), with specific line references and suggested fixes. Ask the user if they want to apply fixes (transition to Update mode).

---

## Update Mode

Apply improvements to an existing blog post.

### Step 1 — Load & Analyze

Read the existing post from `source`. If `topic` is also provided, use it as guidance for the direction of updates.

### Step 2 — Research (if needed)

If the update involves adding new content or the post has outdated information, invoke `/research --depth=standard` to gather current information.

### Step 3 — Load Guidelines

Same as Write Mode Step 2.

### Step 4 — Propose Changes

Present a summary of proposed changes to the user:
- Sections to add/remove/rewrite
- Factual corrections
- Structural improvements
- Code block updates

Wait for user approval before applying changes.

### Step 5 — Apply Changes

Edit the existing file in-place, preserving the author's voice and style. Do not rewrite sections that don't need changes.

### Step 6 — Iterative Quality Loop

Run the same iterative quality loop as Write Mode Step 6 on the updated content. Same convergence rules apply (max 3 iterations, stuck detection).

---

## Tone Guide

| Tone | Characteristics |
|---|---|
| `conversational` | First person, contractions, rhetorical questions, humor OK |
| `technical` | Clear and precise, still accessible, minimal jargon without definition |
| `opinionated` | Strong thesis, explicit disagreement with alternatives, "I believe" statements |

## Output Formats

| Format | Handling |
|---|---|
| `markdown` | Direct output via `/markdown` skill |
| `confluence` | Generate markdown, then `/confluence-publish` |
| `google-doc` | Generate markdown, then convert via Google Drive MCP |
