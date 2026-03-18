---
name: doc-review
description: Exhaustive multi-agent document review with type auto-detection, guideline loading, and interactive approval
user_invocable: true
arguments:
  - name: source
    description: "File path, Confluence URL, or Google Docs URL of the document to review"
    required: true
  - name: doc-type
    description: "Document type tag: tdd, hld, lld, prd, erd, tool-eval, community, coding-guide, appraisal, feedback, blog, article, project (auto-detected if not specified)"
    required: false
  - name: coding-tags
    description: "Comma-separated coding guideline tags for code block review (ds,lib,fe,be,script)"
    required: false
  - name: confidence
    description: "Minimum confidence threshold (0-100, default: 75)"
    required: false
---

# Document Review Skill

> **Dependencies**: This skill works best with the full devkit installed (`/plugin install devkit-full@claude-devkit` or `zsh install.zsh`). It uses guidelines from `guidelines/document/` and `guidelines/coding/`, and delegates to the `doc-reviewer` agent. If guidelines are missing, the skill still works but reviews against general best practices only.

Perform an exhaustive, multi-agent review on a document. This skill works with local
files, Confluence pages, and Google Docs. It auto-detects the document type, loads
appropriate review guidelines, spawns specialized review agents, and interactively
posts findings as comments or generates a review report.

---

## Phase 1: Pre-flight Checks

Before doing anything else, run **all** of the following checks. If any check fails,
stop and report the failure to the user immediately.

> **CLI tool note**: When searching patterns within document content during review,
> use `rg` (ripgrep) instead of `grep` — it is faster and respects `.gitignore` by
> default. Use `fd` instead of `find` for file searching.

### 1a. Detect document source platform

Examine the `$ARGUMENTS.source` value to determine the platform:

| Source pattern | Platform | Fetch method |
|-|-|-|
| Contains `atlassian.net/wiki` | **Confluence** | `mcp__atlassian-confluence__confluence_get_page` |
| Contains `docs.google.com/document` | **Google Docs** | `mcp__google-drive__readGoogleDoc` |
| Local file path (passes `test -f`) | **Local file** | `Read` tool |
| Otherwise | Unknown — ask the user to clarify |

Store the detected platform as `DOC_PLATFORM` (one of `confluence`, `google-docs`, or `local`).

For **Confluence**, extract the page ID from the URL:
- Cloud format: `https://<instance>.atlassian.net/wiki/spaces/<SPACE>/pages/<pageId>/<title>`
- Extract the numeric `pageId` segment.

For **Google Docs**, extract the document ID:
- Format: `https://docs.google.com/document/d/<documentId>/edit`
- Extract the `documentId` segment between `/d/` and the next `/`.

For **local files**, resolve the absolute path:
```bash
realpath "$ARGUMENTS_SOURCE"
```

If the path does not exist (`test -f` fails), stop and tell the user:
> Cannot run document review: file not found at `<path>`.

### 1b. Fetch document content and existing comments

Fetch the document content and any existing comments in parallel. The exact tools
depend on `DOC_PLATFORM`.

#### For Confluence

Use the Confluence MCP tools in parallel:

1. **Page content**: Call `mcp__atlassian-confluence__confluence_get_page` with the
   extracted page ID. This returns the page title, body (storage format or view format),
   and metadata.

2. **Existing comments**: Call `mcp__atlassian-confluence__confluence_get_comments` with
   the page ID to see what feedback has already been given. Avoid duplicating existing
   review comments.

3. **Labels**: Call `mcp__atlassian-confluence__confluence_get_labels` to check for any
   doc-type labels that may assist in type detection.

#### For Google Docs

Use the Google Drive MCP tools in parallel:

1. **Document content**: Call `mcp__google-drive__readGoogleDoc` with the extracted
   document ID. This returns the full document text with structure.

2. **Existing comments**: Call `mcp__google-drive__listComments` with the document ID
   to see what feedback has already been given. Avoid duplicating existing review comments.

3. **Document info**: Call `mcp__google-drive__getDocumentInfo` with the document ID
   to retrieve title, owner, and last modified date.

#### For Local Files

1. **File content**: Use the `Read` tool to read the entire file. For very large files
   (over 2000 lines), read in chunks.

2. **Existing review**: Check if a `<filename>.review.md` file already exists alongside
   the document. If it does, read it to understand what was previously reviewed and avoid
   duplicating findings.

### 1c. Auto-detect document type from content

Analyze the fetched document content to determine its type. Check headings, keywords,
and structural signals.

Apply these detection rules **in order** — use the **first** match:

| Content Signals | Detected Type | Tag |
|-|-|-|
| "Problem Statement" + "Proposed Solution" + ("Technical Architecture" OR "System Design") | Technical Design Doc | `tdd` |
| "System Context" + "Architecture Overview" + "Non-Functional Requirements" | High Level Design | `hld` |
| ("Class Diagram" OR "Module") + "API Specification" + "Sequence Diagram" | Low Level Design | `lld` |
| "User Stories" + "Acceptance Criteria" + "Success Metrics" | Product Requirements | `prd` |
| "Technical Requirements" + "System Constraints" + "Performance Requirements" | Engineering Requirements | `erd` |
| "Evaluation Criteria" + "Candidates" + ("POC" OR "Proof of Concept") | Tool Evaluation | `tool-eval` |
| "Code of Conduct" + "Contributing" | Community Guidelines | `community` |
| "Rule Categories" + "Enforcement" + "Exceptions" | Coding Guidelines Doc | `coding-guide` |
| "Review Period" + "Accomplishments" + "Goals" | Appraisal Review | `appraisal` |
| "Observations" + "Impact" + ("Suggestions" OR "Action Items") | Feedback Doc | `feedback` |
| Short paragraphs + conversational tone + "Hook" or narrative structure + <2000 words | Blog Post | `blog` |
| "Abstract" + deep technical content + edge cases + benchmarks + >2000 words | Technical Article | `article` |
| "Quick Start" + "Architecture" + ("API Reference" OR "Configuration") | Project Doc | `project` |

**Keyword matching rules:**
- Match keywords case-insensitively against section headings (H1-H4) first, then body text.
- A keyword "matches" if it appears as a heading or a prominent term (not just buried in a paragraph).
- For `blog` detection: "short paragraphs" means average paragraph length < 100 words; "conversational tone" means first/second person pronouns ("I", "you", "we") appear in > 20% of paragraphs.
- For `article` detection: "deep technical" means code blocks, formulas, or data tables present; "edge cases" means phrases like "edge case", "corner case", "caveat", or "limitation" appear.

If **no rule matches**, default to a general document review — no type-specific
guidelines will be loaded, but `document/general.md` still applies.

### 1d. Display detection results before proceeding

**CRITICAL**: Always display the detection results and wait for implicit user confirmation
before proceeding. This gives the user a chance to abort and re-run with overrides.

```
Document Review Pre-flight:
  Source:    [path or URL]
  Platform:  [local / confluence / google-docs]
  Detected:  Technical Design Document (tdd)
  Word count: ~3,200
  Code blocks: 5 found

  Guidelines to load:
    - document/general.md (always)
    - document/tdd.md
    - coding/general.md (code blocks found)
    - coding/expressive-code.md (code blocks found)

  Proceed? (Re-run with --doc-type=<tag> to override detection)
```

Include word count and code block count to help the user verify the detection is
reasonable.

### 1e. Apply tag overrides

Tags can come from two sources (in priority order, highest first):

1. **Explicit `$ARGUMENTS.doc-type`** argument — directly specifies the document type tag.
2. **Auto-detected** from step 1c above.

If an explicit doc-type is provided, it **replaces** (not supplements) the auto-detected
type. The user may also provide `$ARGUMENTS.coding-tags` to specify which coding
guidelines should apply to code blocks in the document.

### 1f. Load guideline files

Based on the resolved tags, load the corresponding guideline files from the devkit
installation directory (typically `~/.claude/guidelines/`).

**Always** load `guidelines/document/general.md` as the baseline.

Then load type-specific document guidelines:

| Doc Type Tag | Guideline file |
|-|-|
| `tdd` | `guidelines/document/tdd.md` |
| `hld` | `guidelines/document/hld.md` |
| `lld` | `guidelines/document/lld.md` |
| `prd` | `guidelines/document/prd.md` |
| `erd` | `guidelines/document/erd.md` |
| `tool-eval` | `guidelines/document/tool-eval.md` |
| `community` | `guidelines/document/community.md` |
| `coding-guide` | `guidelines/document/coding-guide.md` |
| `appraisal` | `guidelines/document/appraisal.md` |
| `feedback` | `guidelines/document/feedback.md` |
| `blog` | `guidelines/document/blog.md` |
| `article` | `guidelines/document/article.md` |
| `project` | `guidelines/document/project.md` |

If **code blocks are found** in the document, also load:

| Guideline | Purpose |
|-|-|
| `guidelines/coding/general.md` | General code quality rules |
| `guidelines/coding/expressive-code.md` | Expressive-code annotation standards |

If `$ARGUMENTS.coding-tags` are provided, additionally load coding-specific guidelines:

| Coding Tag | Guideline file |
|-|-|
| `ds` | `guidelines/design-system.md` |
| `lib` | `guidelines/js-ts-library.md` |
| `fe` | `guidelines/frontend-nextjs.md` |
| `be` | `guidelines/backend-java.md` or `guidelines/backend-python.md` (auto-detect from code block languages) |
| `script` | `guidelines/scripts.md` |

**Repo-level guideline discovery** (highest priority — overrides devkit guidelines):

| Category | Paths to Check (in priority order) |
|----------|-----------------------------------|
| **Document guidelines** | `docs/guidelines/document/`, `guidelines/document/`, `.github/guidelines/`, `CLAUDE.md` (section: `## Document Guidelines` or `## Writing Guidelines`) |
| **Coding guidelines** | `docs/guidelines/coding/`, `guidelines/coding/`, `coding-guidelines/`, `CLAUDE.md` (section: `## Coding Guidelines` or `## Code Style`) |

Repo-level guidelines take **higher priority** than devkit guidelines. If both exist, load repo guidelines first, then devkit guidelines as fallback for uncovered areas.

Read the contents of each applicable guideline file. If a guideline file does not exist,
log a warning but continue — do not fail the review because of a missing guideline.

### 1g. Set confidence threshold

```
CONFIDENCE_THRESHOLD = $ARGUMENTS.confidence ?? 75
```

---

## Phase 2: Multi-Agent Review

Spawn **five** parallel sub-agents using the Agent tool (by issuing
five parallel tool calls). Each agent receives:

- The full document content
- The list of section headings (extracted from the document structure)
- The loaded guideline text (all applicable guidelines concatenated)
- Any existing comments on the document
- The detected document type and tag

Each agent must return findings as a structured list. Every finding must include:

```
- section: "<section heading or paragraph reference>"
- severity: CRITICAL | WARNING | SUGGESTION | NICE-TO-HAVE | QUESTION
- confidence: <0-100>
- description: "<clear explanation with specific text reference>"
- suggested_fix: "<concrete improvement text>"
- guideline: "<which guideline rule triggered this, if any>"
```

Severity definitions:

- **CRITICAL**: Factually wrong, technically dangerous, security risk, or will cause
  failures if followed. Missing required sections for the document type.
- **WARNING**: Misleading, ambiguous, likely to confuse the reader, or violates a
  document type requirement in a non-critical way.
- **SUGGESTION**: Would improve the document but is not incorrect as-is. Better
  phrasing, additional context, or improved structure.
- **NICE-TO-HAVE**: Polish, style, or minor enhancement. Formatting improvements.
- **QUESTION**: Reviewer is unsure whether something is an issue — flagged for the
  author to clarify.

### Agent 1: Structure & Completeness

**Focus**: Check the document structure against type-specific requirements.

Prompt the agent with:

> You are a document review agent focused on **structure and completeness**. You have
> been given a document, its detected type, and the type-specific guideline that lists
> required and recommended sections. Your job is to verify the document's structure.
>
> Check for:
>
> - **Required sections**: Compare the document's headings against the required sections
>   listed in the type-specific guideline. Flag every missing required section as CRITICAL.
> - **Section ordering**: Verify sections appear in the recommended order from the guideline.
>   Flag out-of-order sections as SUGGESTION.
> - **Incomplete sections**: Flag sections that exist as headings but contain little or no
>   content (stub sections). Mark as WARNING.
> - **Table of Contents**: If the document has a ToC, verify every entry links to a real
>   section and every section is listed. Flag mismatches as WARNING.
> - **Cross-references**: Check that internal references (e.g., "see Section 3.2" or
>   "as described in the Architecture section") actually resolve to real sections. Flag
>   broken cross-references as WARNING.
> - **Section depth**: Flag sections that are excessively nested (> 4 levels deep) as
>   SUGGESTION. Flag sections that are too shallow for their content as SUGGESTION.
> - **Document length**: For document types with length guidance in the guideline, flag
>   documents that are significantly too short or too long.
>
> Rules:
> - Only flag structural issues you are confident about (confidence >= 60)
> - Reference the specific guideline requirement being violated
> - Provide a suggested fix for each finding (e.g., "Add a Security Considerations section
>   covering authentication, encryption, and input validation")
> - If no type-specific guideline was loaded, review structure against general document
>   best practices
> - Adapt expectations to document type: a blog post needs far less structure than a TDD

### Agent 2: Technical Accuracy

**Focus**: Verify technical claims, data, and references in the document.

Prompt the agent with:

> You are a document review agent focused on **technical accuracy**. Analyze the
> document for:
>
> - **Unverified claims**: Technical assertions that are stated as fact but not supported
>   by evidence or citation. Use `WebSearch` to verify claims about technologies,
>   performance characteristics, market data, or statistics.
> - **Code examples**: Check every code block for syntactic correctness, proper imports,
>   realistic usage patterns, and whether the code actually achieves what the surrounding
>   text claims. If a language identifier is present, validate syntax for that language.
> - **Diagram consistency**: If diagrams (Mermaid, Excalidraw, images) are present,
>   verify they match the textual description. Flag mismatches between diagram components
>   and the text.
> - **Version numbers**: Check that referenced library versions, API versions, and tool
>   versions are current and not deprecated. Use `WebSearch` for verification.
> - **URLs and links**: Verify that referenced URLs are valid and point to the expected
>   content. Use `WebFetch` to check link validity when feasible.
> - **Library and tool names**: Verify correct spelling and capitalization of technology
>   names (e.g., "PostgreSQL" not "Postgres SQL", "Next.js" not "NextJS").
> - **API contracts and data models**: Check that API schemas, request/response examples,
>   and data model definitions are internally consistent. Flag fields that appear in one
>   place but not another.
> - **Outdated information**: Flag content that refers to deprecated features, old versions,
>   or superseded approaches.
> - **Math and calculations**: Verify any calculations, formulas, or numeric derivations.
>
> Rules:
> - Only flag accuracy issues you have verified or have strong evidence for (confidence >= 70)
> - When using WebSearch to verify a claim, note the source in the finding
> - Distinguish between definitely wrong (CRITICAL) and potentially outdated (WARNING)
> - For claims you cannot verify, use QUESTION severity
> - Do NOT flag opinions or subjective assessments as inaccurate — only factual claims
> - Be especially thorough for `tdd`, `hld`, `lld`, and `article` document types

### Agent 3: Clarity & Communication

**Focus**: Evaluate readability, flow, and communication effectiveness.

Prompt the agent with:

> You are a document review agent focused on **clarity and communication**. Analyze
> the document for:
>
> - **Logical flow**: Does the document progress in a logical order? Are ideas introduced
>   before they are referenced? Flag sections where the reader would need to jump ahead
>   to understand the current section.
> - **Readability**: Assess sentence length, paragraph density, and use of active vs.
>   passive voice. Flag paragraphs over 150 words that could be broken up. Flag sentences
>   over 40 words that could be simplified.
> - **Undefined jargon**: Identify technical terms, acronyms, or abbreviations that are
>   used without definition on first occurrence. Flag as SUGGESTION.
> - **Audience appropriateness**: Assess whether the language matches the expected audience
>   for the document type. A PRD should be understandable by non-engineers; a LLD can
>   assume deep technical knowledge.
> - **Ambiguous language**: Flag vague terms like "fast", "scalable", "easy", "simple",
>   "few", "many", "soon", "later" when used without quantification in technical contexts.
>   These need specific numbers or criteria.
> - **Grammar and spelling**: Flag clear grammatical errors, typos, and spelling mistakes.
>   Do not flag regional spelling differences (color/colour) or stylistic choices.
> - **Section transitions**: Check that sections flow into each other naturally. Flag
>   abrupt topic changes without transition.
> - **Redundancy**: Flag content that is repeated verbatim or near-verbatim in multiple
>   sections. Suggest consolidating or cross-referencing.
> - **Tone consistency**: Flag shifts in tone (formal to informal, first person to third
>   person) that appear unintentional.
>
> Rules:
> - Clarity issues are typically SUGGESTION or NICE-TO-HAVE
> - Use WARNING for ambiguity that could lead to misunderstanding or incorrect implementation
> - Use CRITICAL only for text that means the opposite of what the author likely intended
> - Be calibrated to the document type: blog posts can be conversational; TDDs should be precise
> - When suggesting rewrites, match the document's existing voice and style
> - Frame suggestions constructively — "Consider rephrasing for clarity" not "This is unclear"

### Agent 4: Code Quality

**Focus**: Review code blocks against coding guidelines. **Only runs if the document
contains code blocks** (fenced with triple backticks or indented code blocks).

If no code blocks are found, this agent should return an empty findings list immediately.

Prompt the agent with:

> You are a document review agent focused on **code quality within documents**. You
> review code blocks embedded in the document against coding guidelines and documentation
> best practices.
>
> Check for:
>
> - **Guideline compliance**: Check each code block against the loaded coding guidelines.
>   Apply the same standards you would in a code review, adjusted for the documentation
>   context (snippets may be simplified for illustration).
> - **Expressive-code features**: If the document uses expressive-code features (common
>   in Astro/MDX documentation), verify proper usage:
>   - Title annotation: `title="filename.ts"` should be present for file-specific code
>   - Collapse: `collapse={1-5}` syntax should be valid
>   - Line highlighting: `{4-6}` syntax should reference valid line ranges
>   - Diff markers: `ins={3}` and `del={2}` should be consistent
> - **Syntax validity**: Verify that each code block is syntactically valid for its
>   declared language. Flag code that would cause syntax errors.
> - **Text-code consistency**: Verify that the surrounding text accurately describes
>   what the code does. Flag mismatches between explanation and implementation.
> - **Language identifiers**: Check that every fenced code block has a language identifier
>   (e.g., ` ```typescript ` not just ` ``` `). Flag missing identifiers as SUGGESTION.
> - **Missing titles**: For code blocks that represent specific files (e.g., a component,
>   a config file), flag missing `title` annotations as SUGGESTION.
> - **Import completeness**: Check that code examples include necessary imports or clearly
>   indicate what should be imported. Flag examples that would fail due to missing imports.
> - **Error handling**: For code examples that demonstrate real-world patterns (not toy
>   examples), check for missing error handling that could mislead readers.
> - **Security in examples**: Flag code examples that demonstrate insecure patterns
>   (hardcoded secrets, SQL injection, XSS) without explicit warnings. Mark as CRITICAL.
>
> Rules:
> - Only flag code quality issues you are confident about (confidence >= 65)
> - Understand that documentation code is often simplified — do not flag missing error
>   handling in a "Hello World" example
> - Reference the specific coding guideline rule when applicable
> - Provide corrected code as the suggested fix
> - If the code block language does not match any loaded coding guideline, review against
>   general best practices only
> - Use CRITICAL for code that would cause security issues or data loss if copy-pasted
> - Use WARNING for code that would fail or produce incorrect results
> - Use SUGGESTION for code style and best practice improvements

### Agent 5: Consistency & Formatting

**Focus**: Review formatting, terminology, and presentation consistency throughout
the document.

Prompt the agent with:

> You are a document review agent focused on **consistency and formatting**. Analyze
> the entire document holistically for:
>
> - **Terminology consistency**: Check that the same concept is referred to by the same
>   term throughout. Flag when a term switches (e.g., "user" in one section, "customer"
>   in another, "client" in a third — unless explicitly defined as different).
> - **Heading level consistency**: Verify heading levels follow a proper hierarchy (no
>   skipping from H2 to H4, no H1 used mid-document). Flag violations as WARNING.
> - **Date format consistency**: Check that all dates use the same format throughout
>   (e.g., all ISO 8601, or all "Month Day, Year"). Flag mixed formats as SUGGESTION.
> - **List style consistency**: Check that lists consistently use the same style (all
>   bullet points or all numbered, not a mix of both for similar content). Check that
>   list items consistently end with or without periods.
> - **Image and diagram alt text**: If images are embedded, check for alt text or
>   captions. Flag missing alt text as SUGGESTION for accessibility.
> - **Link validity**: Check that all internal cross-references resolve. Check for
>   obvious broken external links (malformed URLs, known dead domains).
> - **Brand and voice consistency**: Check that the document maintains a consistent
>   tone and formality level throughout. Flag jarring shifts.
> - **Capitalization consistency**: Check that technical terms are capitalized the same
>   way throughout (e.g., "Kubernetes" vs "kubernetes" vs "K8s" — pick one and use it
>   consistently unless there is a reason for variation).
> - **Table formatting**: Check that tables are well-formed, have headers, and use
>   consistent alignment. Flag ragged or misaligned tables.
> - **Whitespace and spacing**: Flag inconsistent spacing (e.g., sometimes two blank
>   lines between sections, sometimes one). Flag trailing whitespace if the platform
>   renders it visibly.
> - **Metadata completeness**: For document types that expect metadata (author, date,
>   version, status), check that it is present and complete.
>
> Rules:
> - Consistency issues are typically SUGGESTION or NICE-TO-HAVE
> - Use WARNING only for inconsistencies that could cause confusion (e.g., using the
>   same term for two different things)
> - Be pragmatic — a few minor formatting variations in a long document are acceptable
> - Group related consistency issues together rather than flagging each instance separately
> - Provide specific examples of the inconsistency ("Line 12 uses 'user', line 45 uses
>   'customer' for the same concept")
> - Do not flag platform-specific formatting constraints (e.g., Confluence wiki markup
>   limitations) as issues

---

## Phase 3: Consolidate & Filter

After all five agents return their findings:

### 3a. Merge all findings

Combine all findings from all agents into a single list.

### 3b. Deduplicate

Two findings are considered duplicates if they:
- Reference the **same section** (or overlapping text within a section) AND
- Describe the **same underlying issue** (use judgment — "missing section" from Agent 1
  and "referenced section does not exist" from Agent 5 are the same issue)

When deduplicating, keep the finding with the higher confidence score. If the duplicate
has a better suggested fix, merge the fix into the kept finding. If the findings have
different severities, use the higher severity.

### 3c. Filter by confidence

Remove all findings where `confidence < CONFIDENCE_THRESHOLD`.

### 3d. Sort

Sort findings by:
1. Severity (CRITICAL first, then WARNING, SUGGESTION, NICE-TO-HAVE, QUESTION)
2. Within same severity, by confidence (highest first)

### 3e. Group by section

Group the sorted findings by document section. Within each section group, maintain
the severity/confidence sort order.

For documents without clear sections (e.g., short blog posts), group by paragraph
or logical content block.

### 3f. Finding Quality Verification Loop

Before presenting to the user, verify each finding. **Max 2 iterations.**

```
iteration = 0
max_iterations = 2

while iteration < max_iterations:
    iteration += 1
    for each finding:
        re-read the actual document section referenced
        if finding is inaccurate (misquotes text, wrong section): fix or remove
        if suggested fix contradicts the document's purpose: revise
        if finding duplicates an already-posted comment: remove
    if no findings corrected or removed: break  # converged
```

This ensures only accurate, actionable findings reach the user. False positives are silently dropped.

---

## Phase 4: Interactive Review

Present the consolidated findings to the user for approval before posting.

### Display format

For each section group, display:

```
=== Section: "Technical Architecture" (4 findings) ===

1. [CRITICAL] (confidence: 92)
   Missing required section: No "Security Considerations" found.
   Guideline: document/tdd.md / Required Sections
   Suggested fix: Add a Security Considerations section covering authentication,
   encryption at rest and in transit, input validation, and authorization model.

2. [WARNING] (confidence: 85)
   Line 42: Claim "Redis handles 1M ops/sec" is unverified and likely context-dependent.
   Guideline: document/general.md / Claims must be supported
   Suggested fix: Add citation or benchmark context: "Redis can handle ~1M ops/sec
   for simple GET/SET operations on commodity hardware (source: Redis benchmarks)."

3. [SUGGESTION] (confidence: 78)
   The term "service" is used to refer to both the HTTP API and the background worker.
   Consider using distinct terms.
   Guideline: document/general.md / Terminology consistency
   Suggested fix: Use "API service" for the HTTP layer and "worker service" for
   background processing throughout.

4. [NICE-TO-HAVE] (confidence: 76)
   Code block on line 55 is missing a language identifier.
   Guideline: coding/general.md / Code blocks must specify language
   Suggested fix: Add ```python to the opening fence.
```

### User interaction

After displaying each section group, prompt the user:

> **Actions for section "Technical Architecture":**
> - `approve_all` or `a` — Approve all findings in this section
> - `reject_all` or `r` — Skip all findings in this section
> - `select_few` or `pick` — Choose specific findings (e.g., "pick 1,3")
> - `edit <n>` — Edit finding n before approving (change severity, description, or fix)
> - `done` — Stop reviewing and post all approved findings so far
> - `abort` — Cancel the entire review without posting anything

Track which findings are approved for posting.

**Interaction flow:**

1. Display the first section group.
2. Wait for user action.
3. If user chooses `approve_all`, mark all findings in this section as approved.
4. If user chooses `reject_all`, mark all findings in this section as rejected.
5. If user chooses `pick`, mark only the specified findings as approved.
6. If user chooses `edit <n>`, display the finding and allow the user to modify the
   description, suggested fix, or severity. Then mark it as approved with the edits.
7. If user chooses `done`, skip remaining sections and proceed to posting.
8. If user chooses `abort`, discard everything and stop.
9. Move to the next section group and repeat.

---

## Phase 5: Post Comments / Generate Report

Post all approved findings to the document platform. The format and method depend
on the `DOC_PLATFORM`.

### For Confluence

Use `mcp__atlassian-confluence__confluence_add_comment` for each approved finding.

Format each comment using Confluence wiki markup:

```
*[SEVERITY]* Description of the issue.

{quote}Suggested: The improved text or approach.{quote}

_Confidence: NN/100 | Agent: agent-name | Guideline: guideline-reference_
```

For section-specific findings, include the section reference in the comment so the
author can locate the relevant content:

```
*[WARNING]* In section "Technical Architecture": Claim "Redis handles 1M ops/sec"
is unverified and likely context-dependent.

{quote}Suggested: Add citation or benchmark context.{quote}

_Confidence: 85/100 | Agent: Technical Accuracy | Guideline: document/general.md_
```

If the Confluence API supports inline/anchor comments for the page format, prefer
those for section-specific feedback.

### For Google Docs

Use `mcp__google-drive__addComment` for each approved finding.

Use the relevant text from the document section as the `quotedText` anchor so the
comment attaches to the correct location in the document.

Format in plain text (Google Docs comments do not support markdown or HTML):

```
[SEVERITY] Description of the issue.

Suggested: The improved text or approach.

Confidence: NN/100 | Guideline: guideline-reference
```

Keep comments concise — Google Docs comment UI has limited space. If the suggested
fix is long, summarize it in the comment and note "See review summary for full
suggestion."

### For Local Files

Generate a review report file named `<document-name>.review.md` in the same directory
as the source document.

Format the report as structured markdown:

```markdown
# Document Review: <document title>

**Source**: <file path>
**Reviewed**: <date>
**Document type**: <detected type> (<tag>)
**Guidelines applied**: <list>
**Confidence threshold**: <threshold>

---

## Findings

### Section: "<section heading>"

#### 1. [CRITICAL] (confidence: 92)

**Description**: Missing required section: No "Security Considerations" found.

**Guideline**: document/tdd.md / Required Sections

**Suggested fix**: Add a Security Considerations section covering authentication,
encryption at rest and in transit, input validation, and authorization model.

---

#### 2. [WARNING] (confidence: 85)

**Description**: Line 42: Claim "Redis handles 1M ops/sec" is unverified.

**Guideline**: document/general.md / Claims must be supported

**Suggested fix**: Add citation or benchmark context.

---

### Section: "<next section>"

...
```

After generating the report, inform the user of the file path.

### Error handling

If any comment fails to post:
- Log the error (include the platform error message).
- Continue posting remaining comments.
- Report all failures at the end with details.

---

## Phase 6: Summary

After posting all approved findings (or generating the report), display a summary:

```
## Document Review Summary

Reviewed by claude-devkit Doc Review skill.

| Severity     | Count |
|--------------|-------|
| CRITICAL     | N     |
| WARNING      | N     |
| SUGGESTION   | N     |
| NICE-TO-HAVE | N     |
| QUESTION     | N     |

**Document type**: Technical Design Document (tdd)
**Guidelines applied**: document/general, document/tdd, coding/general, coding/expressive-code
**Confidence threshold**: 75
**Sections reviewed**: N
**Total findings posted**: N (of M total before filtering)
```

Include platform-specific information:

- **Confluence**: Include a link to the page.
- **Google Docs**: Include a link to the document.
- **Local**: Include the path to the generated `.review.md` file.

If any comments failed to post, include a failures section:

```
### Failed to post

| # | Section | Severity | Error |
|---|---------|----------|-------|
| 3 | "API Design" | WARNING | 403 Forbidden — insufficient permissions |
```

---

## Important Rules

1. **Accuracy above all**: Every finding MUST be backed by specific text in the document.
   Never guess. If you are unsure whether something is an issue, use QUESTION severity
   or drop the finding. Do not invent problems that do not exist in the text.

2. **No speculation**: Do not post findings based on assumptions about content you have
   not read. If you need more context about a reference in the document, use WebSearch
   or WebFetch to verify before flagging.

3. **Verify before flagging**: Before flagging a technical claim as inaccurate, verify
   it using WebSearch. Do not flag something as wrong based solely on your training
   data — external verification is required for accuracy findings.

4. **Respect existing comments**: Check existing document comments to avoid duplicating
   feedback that has already been given. If a previous reviewer already flagged an issue,
   do not flag it again unless you have additional context to add.

5. **Adapt to document type**: Different document types have fundamentally different
   review criteria. An appraisal review needs empathy and constructiveness. A TDD needs
   rigorous technical scrutiny. A blog post needs engagement and readability focus.
   A PRD needs stakeholder clarity. Do not apply TDD standards to a blog post.

6. **Code blocks get full treatment**: When code blocks are present, they deserve the
   same scrutiny as code in a PR review. Apply coding guidelines rigorously. Code in
   documents is often copy-pasted by readers, so correctness matters even more than in
   a codebase (where tests catch issues).

7. **Be constructive**: Frame findings as helpful improvements, not criticisms. Explain
   the *why* behind each finding. Suggest concrete fixes, not just "this is wrong."

8. **Scale review depth to document length**: A 500-word blog post does not need the
   same depth as a 10,000-word TDD. Adjust the number and granularity of findings to
   match the scope of the document. For short documents, each agent should aim for
   3-5 findings max. For long documents, up to 15-20 per agent is reasonable.

9. **One issue per finding**: Each finding should address exactly one issue. Do not
   bundle multiple problems into a single finding. This makes it easier for the author
   to address findings individually.

10. **Match the document's voice**: When suggesting rewrites or improvements, match
    the existing tone and style of the document. Do not impose a different voice.
