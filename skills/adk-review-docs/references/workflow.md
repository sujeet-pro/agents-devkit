# ADK Review Docs Workflow

## Phase 1: Inventory

**Gate**: User approval of scope (skipped with `--auto`)

1. Scan the doc target:
   - Single file: read the file, identify its type and audience.
   - Directory: list all markdown/doc files recursively, sort by modification time.
   - URL: fetch the page, identify structure and content type.
2. For each document, record:
   - Title and path
   - Approximate size (word count or line count)
   - Document type (README, API reference, guide, tutorial, changelog)
   - Intended audience (inferred from content, path, or frontmatter)
3. Identify source material the docs claim to describe:
   - Code files referenced in examples
   - API endpoints documented
   - Config files or CLI commands mentioned
4. Present scope summary:
   - Document count and total size
   - Identified audience(s)
   - Source material to cross-reference
   - Focus dimension
5. Wait for user confirmation or scope adjustment.

**Edge cases**:
- Path does not exist: stop and tell the user.
- URL not accessible: report the error and stop.
- No markdown/doc files found in directory: report and stop.
- Very large doc set (>20 files): suggest scoping or prioritization.

## Phase 2: Accuracy Check

1. For each document, extract factual claims:
   - API signatures: method names, parameters, return types
   - Config values: key names, default values, valid ranges
   - Behavior descriptions: "when X happens, Y occurs"
   - Command examples: CLI flags, argument order, expected output
   - Code examples: imports, function calls, expected behavior
2. Verify each claim against source:
   - Read the referenced code files. Compare documented signatures against actual code.
   - Trace command examples: do the flags exist? Are paths valid?
   - Cross-reference config values against actual defaults in code.
   - Use `WebSearch` for external claims (library versions, external API behavior) when available.
3. Record findings:
   - Verified mismatch: Blocker severity, High confidence.
   - Likely mismatch but cannot fully verify: Critical severity, Medium confidence.
   - Cannot verify at all: Question severity, state what would verify it.

## Phase 3: Clarity Review

1. **Structure check**:
   - Required sections present for the doc type.
   - Logical ordering: setup before usage, overview before details.
   - No orphan stubs, TODO placeholders, or empty sections.
2. **Completeness check**:
   - Topics the audience would expect: prerequisites, installation, basic usage, advanced usage, troubleshooting, FAQ.
   - Missing error scenarios or edge case documentation.
   - Cross-references to related docs.
3. **Audience fit**:
   - Jargon appropriate for the target reader.
   - Prerequisites stated explicitly (not assumed).
   - Progressive disclosure: simple case first, complexity later.
4. **Example quality**:
   - Syntax correct for the language.
   - Realistic values (not placeholder `foo`/`bar` in user-facing docs).
   - Runnable where claimed: imports present, dependencies noted.
   - Expected output shown when non-obvious.
5. **Consistency**:
   - Terminology consistent within and across documents.
   - Heading levels correct and uniform.
   - Formatting patterns uniform (code blocks, lists, tables).
   - Internal links valid.

## Phase 4: Findings

1. Collect all findings from Phases 2 and 3.
2. Apply doc-specific severity mapping:
   - **Blocker**: Factually wrong (will cause user failure).
   - **Critical**: Misleading (likely to cause confusion).
   - **Should Have**: Incomplete (missing section or important detail).
   - **May Have**: Unclear (could be misunderstood by target audience).
   - **Nitpick**: Style or formatting.
   - **Question**: Unverifiable claim.
3. Sort by severity.
4. Group by document or section when reviewing multiple files.
5. Present using the format defined in `references/review-comment-format.md`, including before/after examples for accuracy and clarity findings.
6. End with triage summary.

## Phase 5: Recommendations

1. For each finding, provide a specific fix recommendation.
2. Include before/after examples:
   ```
   **Before**: "Use `GET /users` to fetch all users."
   **After**: "Use `POST /users/search` with a JSON body to fetch users matching your criteria."
   ```
3. Prioritize fixes: "fix factual errors first, then structure, then style."
4. Wait for user response: `a-N`, `r-N`, `e-N`, `all`.

## Phase 6: Summary

1. **Doc health score**:
   - Verified claims: N out of M checked (percentage).
   - Coverage: expected topics present vs. missing.
   - Example status: N verified, M unverified, K broken.
2. **Remaining gaps**: topics not covered, claims not verified.
3. **Recommended next action**:
   - Fix critical findings (factual errors).
   - Schedule deeper pass for completeness.
   - Publish if no blockers remain.
4. Offer hand-off to `adk-address-review-feedback` for accepted findings.

## Validation Rules

- Every accuracy finding cites both the doc section AND the source code or reference.
- Lower-confidence findings are labeled as Questions.
- Missing code or runtime verification for examples is called out explicitly.
- Style findings are never Blocker or Critical.
- Before/after examples accompany accuracy and clarity findings.
- The review covers the focus dimension at minimum; other dimensions are checked opportunistically.

## Edge Case Handling

| Situation | Action |
| --- | --- |
| Doc references code that does not exist | Blocker finding: documented feature may be removed or never implemented |
| Example uses deprecated API | Critical finding with suggested replacement |
| Doc is clearly a draft (TODO stubs) | Note draft status, review what exists, flag stubs as Should Have |
| Multiple docs contradict each other | Blocker finding on both, note the contradiction |
| Doc references external URL that is dead | Should Have finding, suggest updated URL or removal |
| Generated docs (JSDoc, Swagger) | Review the source annotations, not the generated output |
| Non-English docs | Review structure and accuracy; note language-specific clarity limits |
