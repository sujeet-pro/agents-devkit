---
name: pr-review
description: Exhaustive multi-agent PR code review for GitHub and Bitbucket with context-aware guidelines
user_invocable: true
arguments:
  - name: pr
    description: "PR number or URL"
    required: true
  - name: tags
    description: "Comma-separated guideline tags (ds,lib,fe,be,script)"
    required: false
  - name: confidence
    description: "Minimum confidence threshold (0-100, default: 80)"
    required: false
---

# PR Review Skill

> **Dependencies**: This skill works best with the full devkit installed (`/plugin install devkit-full@claude-devkit` or `zsh install.zsh`). It uses guidelines from `guidelines/coding/` and delegates to the `code-reviewer` agent. If guidelines are missing, the skill still works but reviews against general best practices only.

Perform an exhaustive, multi-agent code review on a pull request. This skill works
with both GitHub and Bitbucket repositories, auto-detects the project type, loads
the appropriate review guidelines, spawns specialized review agents, and interactively
posts findings as PR comments.

---

## Phase 1: Pre-flight Checks

Before doing anything else, run **all** of the following checks. If any check fails,
stop and report the failure to the user immediately.

> **CLI tool note**: When searching code patterns during review, use `rg` (ripgrep)
> instead of `grep` — it is faster and respects `.gitignore` by default.

### 1a. Verify clean working tree

```bash
git status --porcelain
```

If the output is non-empty, stop and tell the user:

> Cannot run PR review: the working tree has uncommitted changes.
> Please commit or stash your changes before running the review.

### 1b. Detect VCS platform

Read the git remote URL to determine whether this repository is hosted on GitHub or
Bitbucket.

```bash
git remote get-url origin
```

Apply these rules in order:

| Remote URL pattern | Platform |
|-|-|
| Contains `github.com` | **GitHub** |
| Contains `bitbucket.org` | **Bitbucket** |
| Contains `bitbucket` (e.g. Bitbucket Server / Data Center) | **Bitbucket** |
| Otherwise | Ask the user which platform to use |

Store the detected platform as `VCS_PLATFORM` (either `github` or `bitbucket`).

For Bitbucket, also extract `workspace` and `repo_slug` from the remote URL:
- SSH format: `git@bitbucket.org:<workspace>/<repo_slug>.git`
- HTTPS format: `https://bitbucket.org/<workspace>/<repo_slug>.git`

For GitHub, extract `owner` and `repo` from the remote URL:
- SSH format: `git@github.com:<owner>/<repo>.git`
- HTTPS format: `https://github.com/<owner>/<repo>.git`

### 1c. Parse the PR identifier

The `$ARGUMENTS.pr` value may be:
- A bare number (e.g. `42`) -- treat as a PR number in the detected repo
- A full URL (e.g. `https://github.com/org/repo/pull/42`) -- extract the PR number
- A Bitbucket URL (e.g. `https://bitbucket.org/workspace/repo/pull-requests/42`)

Normalize this to a numeric `PR_NUMBER`.

### 1d. Detect repo type and load guidelines

Use `fd` to find config files efficiently (e.g., `fd -t f 'package.json' --max-depth 2`)
instead of `find`. Use `jq` to parse JSON config files (e.g., `jq -r '.dependencies | keys[]' package.json`).

Check for project marker files in the repository root to detect the type:

| Marker file / pattern | Detected type | Guideline tag |
|-|-|-|
| `next.config.js`, `next.config.ts`, `next.config.mjs` | Next.js frontend | `fe` |
| `package.json` containing `"storybook"` or directory named `.storybook/` | Design system | `ds` |
| `package.json` with `"main"` + `"types"` fields and no framework | JS/TS library | `lib` |
| `pom.xml`, `build.gradle`, `build.gradle.kts` | Java backend | `be` |
| `pyproject.toml`, `setup.py`, `requirements.txt` with FastAPI/Django/Flask | Python backend | `be` |
| `Makefile` only, or shell scripts in `bin/`, `scripts/` | Scripts | `script` |

### 1e. Apply tag overrides

Tags can come from three sources (in priority order, highest first):

1. **Explicit `$ARGUMENTS.tags`** argument (comma-separated)
2. **PR title/description tags** -- look for bracket tags like `[ds]`, `[fe]`, `[be]`, `[lib]`, `[script]` in the PR title or description
3. **Auto-detected** from step 1d above

If explicit tags are provided, they **replace** (not supplement) auto-detected tags.
If PR title/description tags are found and no explicit tags were given, they **replace** auto-detected tags.

### 1f. Load guideline files

Based on the resolved tags, load the corresponding guideline files. **Always** load
`coding/general.md` as the baseline. Then load tag-specific guidelines:

| Tag | Guideline file |
|-|-|
| `fe` | `guidelines/coding/frontend-nextjs.md` |
| `ds` | `guidelines/coding/design-system.md` |
| `lib` | `guidelines/coding/js-ts-library.md` |
| `be` (detected Java) | `guidelines/coding/backend-java.md` |
| `be` (detected Python) | `guidelines/coding/backend-python.md` |
| `script` | `guidelines/coding/scripts.md` |

**Repo-level guideline discovery** (highest priority — overrides devkit guidelines):

| Category | Paths to Check (in priority order) |
|----------|-----------------------------------|
| **Coding guidelines** | `docs/guidelines/coding/`, `guidelines/coding/`, `coding-guidelines/`, `.github/guidelines/`, `CLAUDE.md` (section: `## Coding Guidelines` or `## Code Style`) |

If repo-level coding guidelines are found, load them **first** (higher priority), then load devkit guidelines as fallback for uncovered areas.

Read the contents of each applicable guideline file from both the repo and the devkit
installation directory (typically `~/.claude/guidelines/coding/`). Pass all to each review
agent as context.

### 1g. Set confidence threshold

```
CONFIDENCE_THRESHOLD = $ARGUMENTS.confidence ?? 80
```

---

## Phase 2: Fetch PR Data

Retrieve all data needed for the review. The exact tools depend on `VCS_PLATFORM`.

### For Bitbucket

Use the Bitbucket MCP tools in parallel:

1. **PR metadata**: Call `mcp__bitbucket__getPullRequest` with the workspace, repo_slug, and PR_NUMBER. Extract the title, description, source branch, destination branch, and author.

2. **Diff**: Call `mcp__bitbucket__getPullRequestDiff` to get the full unified diff.

3. **Existing comments**: Call `mcp__bitbucket__getPullRequestComments` to see what has already been reviewed. Avoid duplicating existing review comments.

4. **Commits**: Call `mcp__bitbucket__getPullRequestCommits` to understand the change history and intent.

### For GitHub

Use the `gh` CLI:

1. **PR metadata**:
   ```bash
   gh pr view $PR_NUMBER --json title,body,headRefName,baseRefName,author,labels
   ```

2. **Diff**:
   ```bash
   gh pr diff $PR_NUMBER
   ```

3. **Existing comments**:
   ```bash
   gh api repos/$OWNER/$REPO/pulls/$PR_NUMBER/comments
   ```

4. **Commits**:
   ```bash
   gh pr view $PR_NUMBER --json commits
   ```

### Parse PR tags from metadata

After fetching the PR, re-check the title and description for bracket tags (`[ds]`,
`[fe]`, `[be]`, `[lib]`, `[script]`). If tags were not explicitly provided via
arguments, use these discovered tags (per the priority rules in Phase 1e).

### Switch to PR branch locally

```bash
git fetch origin <source_branch>
git checkout <source_branch>
```

This allows the review agents to read the actual source files for full context beyond
just the diff.

---

## Phase 3: Multi-Agent Review

Spawn **five** parallel sub-agents using the Agent tool (by issuing
five parallel tool calls). Each agent receives:

- The full diff
- The list of changed files
- The loaded guideline text (all applicable guidelines concatenated)
- The commit messages for intent context
- The PR title and description

Each agent must return findings as a structured list. Every finding must include:

```
- file: <file path>
- line_start: <starting line number in the new file>
- line_end: <ending line number in the new file>
- severity: CRITICAL | WARNING | SUGGESTION | NICE-TO-HAVE | QUESTION
- confidence: <0-100>
- description: <clear explanation with specific code reference>
- suggested_fix: <code suggestion, or null if not applicable>
- guideline: <which guideline rule triggered this, if any>
```

### Agent 1: Guidelines Compliance

**Focus**: Check the code against the loaded guideline rules.

Prompt the agent with:

> You are a code review agent focused on **guideline compliance**. You have been
> given a set of project-specific guidelines and a PR diff. Your job is to find
> every place where the code violates or could better follow these guidelines.
>
> Guidelines to enforce:
> <Insert loaded guideline text here>
>
> Rules:
> - Only flag violations you are confident about (confidence >= 60)
> - Reference the specific guideline rule being violated
> - Provide a suggested fix for each violation
> - Use SUGGESTION severity for style/convention issues
> - Use WARNING for guidelines that prevent bugs or maintainability issues
> - Use CRITICAL only for guidelines violations that will cause production issues
> - Do NOT flag issues in deleted lines (lines starting with `-` in the diff)

### Agent 2: Bug & Logic

**Focus**: Find bugs, logic errors, edge cases, and correctness issues.

Prompt the agent with:

> You are a code review agent focused on **bugs and logic errors**. Analyze the
> diff for:
>
> - Logic errors and incorrect conditions
> - Off-by-one errors
> - Null/undefined safety issues
> - Unhandled edge cases (empty arrays, zero values, negative numbers)
> - Race conditions and concurrency bugs
> - Resource leaks (unclosed handles, missing cleanup)
> - Incorrect error handling (swallowed errors, wrong error types)
> - Type mismatches or unsafe casts
> - Incorrect assumptions about data shapes
> - Missing validation at boundaries
>
> Rules:
> - Read the surrounding source files when you need more context
> - Be precise: reference exact variable names, function calls, and line numbers
> - Distinguish between definite bugs (CRITICAL) and potential issues (WARNING)
> - For edge cases that are unlikely but possible, use SUGGESTION
> - If you are unsure whether something is a bug, use QUESTION severity
> - Do NOT flag issues in deleted lines

### Agent 3: Security

**Focus**: Identify security vulnerabilities.

Prompt the agent with:

> You are a code review agent focused on **security**. Analyze the diff for:
>
> - Injection vulnerabilities (SQL, NoSQL, command, LDAP, XPath)
> - Cross-site scripting (XSS) -- both reflected and stored
> - Cross-site request forgery (CSRF)
> - Authentication and authorization flaws
> - Secrets, API keys, passwords, or tokens in code
> - Insecure cryptography or hashing
> - Path traversal
> - Insecure deserialization
> - Server-side request forgery (SSRF)
> - Missing security headers
> - Insecure direct object references (IDOR)
> - Mass assignment / over-posting
> - Sensitive data exposure (PII in logs, unencrypted storage)
> - Dependency vulnerabilities (if new deps are added)
>
> Rules:
> - Security issues are CRITICAL unless they require unlikely preconditions (WARNING)
> - Always explain the attack vector and potential impact
> - Provide a concrete fix, not just "sanitize input"
> - Check environment variable usage -- ensure secrets are not hardcoded
> - If a new dependency is added, note that it should be audited
> - Do NOT flag issues in deleted lines
> - Do NOT flag test files unless they contain real secrets

### Agent 4: Performance

**Focus**: Identify performance issues and regressions.

Prompt the agent with:

> You are a code review agent focused on **performance**. Analyze the diff for:
>
> - N+1 query patterns (database calls inside loops)
> - Missing database indexes (for new query patterns)
> - Unnecessary re-renders (React: missing memo, unstable references)
> - Large bundle size impacts (new heavy dependencies, missing code splitting)
> - Memory leaks (event listeners not cleaned up, growing caches)
> - Expensive operations in hot paths (regex compilation, JSON parsing in loops)
> - Missing pagination for potentially large datasets
> - Synchronous blocking operations where async is possible
> - Unoptimized images or assets
> - Missing caching opportunities
> - Inefficient algorithms (O(n^2) where O(n) or O(n log n) is possible)
> - Unnecessary data fetching (over-fetching fields, missing GraphQL fragments)
>
> Rules:
> - Performance issues are WARNING unless they will cause visible user impact (CRITICAL)
> - Include estimated impact when possible (e.g., "adds ~200ms per request")
> - Suggest specific optimizations, not vague advice
> - Consider the scale context (is this a hot path or a rarely-called admin function?)
> - Use NICE-TO-HAVE for micro-optimizations that improve code but have minimal impact
> - Do NOT flag issues in deleted lines

### Agent 5: Architecture

**Focus**: Review design patterns, abstractions, and system design.

Prompt the agent with:

> You are a code review agent focused on **architecture and design**. Analyze the
> diff for:
>
> - Inappropriate abstractions (too early, too complex, wrong level)
> - Violation of SOLID principles
> - Incorrect layering (business logic in controllers, UI logic in models)
> - API contract issues (breaking changes, inconsistent naming, missing versioning)
> - Dependency management (circular deps, inappropriate coupling)
> - Missing or incorrect error boundaries
> - State management issues (duplicated state, derived state stored unnecessarily)
> - Missing interfaces/types at module boundaries
> - God classes/functions (doing too much)
> - Copy-paste code that should be abstracted (but only if 3+ occurrences)
> - Missing factory/strategy patterns where polymorphism would simplify code
> - Incorrect use of design patterns
>
> Rules:
> - Architecture issues are typically SUGGESTION or WARNING
> - Use CRITICAL only for breaking API changes or severe design flaws
> - Be pragmatic -- not every PR needs perfect architecture
> - Consider the size of the change: small PRs get lighter architecture review
> - If the PR is a refactoring, hold it to higher architecture standards
> - Frame suggestions as questions when you are not sure about the broader context
> - Do NOT flag issues in deleted lines

---

## Phase 4: Consolidate & Filter

After all five agents return their findings:

### 4a. Merge all findings

Combine all findings from all agents into a single list.

### 4b. Deduplicate

Two findings are considered duplicates if they:
- Reference the same file AND
- Have overlapping line ranges (within 3 lines of each other) AND
- Describe the same underlying issue (use judgment)

When deduplicating, keep the finding with the higher confidence score. If the
duplicate has a better suggested fix, merge the fix into the kept finding. If the
findings have different severities, use the higher severity.

### 4c. Filter by confidence

Remove all findings where `confidence < CONFIDENCE_THRESHOLD`.

### 4d. Sort

Sort findings by:
1. Severity (CRITICAL first, then WARNING, SUGGESTION, NICE-TO-HAVE, QUESTION)
2. Within same severity, by confidence (highest first)

### 4e. Group by file

Group the sorted findings by file path. Within each file group, sort by line number.

### 4f. Finding Quality Verification Loop

Before presenting to the user, verify each finding against the actual source code. **Max 2 iterations.**

```
iteration = 0
max_iterations = 2

while iteration < max_iterations:
    iteration += 1
    for each finding:
        read the actual source file at the referenced lines
        if finding is inaccurate or line numbers are wrong: fix or remove
        if suggested_fix would break other code: revise or remove
    if no findings were corrected or removed: break  # converged
```

**Verification checklist:**

| Check | Action |
|---|---|
| Referenced file and line numbers exist | Remove finding if file/lines don't match |
| Code snippet in finding matches actual code | Fix snippet or remove finding |
| Suggested fix compiles/parses correctly | Revise fix or remove suggestion |
| Finding is not a false positive from diff context | Remove false positives |
| Finding is not a duplicate of an existing PR comment | Remove duplicates |

This loop ensures only accurate, verified findings reach the user. Findings that fail verification are silently dropped.

---

## Phase 5: Interactive Review

Present the consolidated findings to the user for approval before posting.

### Display format

For each file group, display:

```
=== path/to/file.ts (3 findings) ===

1. [CRITICAL] (confidence: 95)
   Lines 42-48: SQL injection vulnerability in user query
   > const query = `SELECT * FROM users WHERE id = ${userId}`;
   Suggested fix: Use parameterized queries
   ```ts
   const query = 'SELECT * FROM users WHERE id = $1';
   const result = await db.query(query, [userId]);
   ```
   Guideline: general / security-basics

2. [WARNING] (confidence: 87)
   Line 63: Unhandled promise rejection in async handler
   > await processOrder(order);
   Suggested fix: Wrap in try/catch with proper error handling
   Guideline: general / error-handling

3. [SUGGESTION] (confidence: 82)
   Lines 71-75: Consider extracting repeated validation logic
   Guideline: general / dry-principle
```

### User interaction

After displaying each file group, ask the user:

> **Actions for path/to/file.ts:**
> - `post` or `p` -- Post all findings for this file
> - `skip` or `s` -- Skip all findings for this file
> - `pick` -- Choose individual findings (e.g., "pick 1,3" to post findings 1 and 3)
> - `edit <n>` -- Edit finding n before posting (change severity or description)
> - `done` -- Stop reviewing and post all approved findings so far
> - `abort` -- Cancel the entire review without posting anything

Track which findings are approved for posting.

---

## Phase 6: Post Comments

Post all approved findings as PR comments.

### For Bitbucket

Use `mcp__bitbucket__addPullRequestComment` for each approved finding.

Format the comment body as:

```
**[SEVERITY]** Description of the issue

> ```
> relevant code snippet from the diff
> ```

**Suggested fix:**
```language
corrected code here
```

_Confidence: NN/100 | Agent: agent-name | Guideline: guideline-reference_
```

For inline comments, pass the file path and line number so the comment appears in
the right place in the Bitbucket diff view.

### For GitHub

Use `gh api` to post review comments:

```bash
gh api repos/$OWNER/$REPO/pulls/$PR_NUMBER/comments \
  -f body="<formatted comment>" \
  -f path="<file path>" \
  -f line=<line number> \
  -f side="RIGHT" \
  -f commit_id="<latest commit sha>"
```

Format the comment body as:

```
**[SEVERITY]** Description of the issue

> ```
> relevant code snippet from the diff
> ```

**Suggested fix:**
```suggestion
corrected code here
```

_Confidence: NN/100 | Agent: agent-name | Guideline: guideline-reference_
```

Note: GitHub supports the special `suggestion` code fence syntax which allows the
reviewer to apply the suggestion with a single click.

### Post summary comment

After all individual comments are posted, post a summary comment on the PR:

**For Bitbucket:**
```
mcp__bitbucket__addPullRequestComment
```

**For GitHub:**
```bash
gh pr comment $PR_NUMBER --body "<summary>"
```

Summary format:

```
## Code Review Summary

Reviewed by claude-devkit PR Review skill.

| Severity | Count |
|----------|-------|
| CRITICAL | N |
| WARNING | N |
| SUGGESTION | N |
| NICE-TO-HAVE | N |
| QUESTION | N |

**Guidelines applied**: general, frontend-nextjs
**Confidence threshold**: 80
**Files reviewed**: N
**Total findings posted**: N (of M total before filtering)
```

### Optionally set PR status

After posting, ask the user whether to set a review status:

- If there are any CRITICAL findings: recommend **Request Changes**
- If there are only WARNINGs and below: recommend **Comment only**
- If there are only SUGGESTIONs and below: recommend **Approve**

For Bitbucket, there is no direct approval API through the MCP tools, so just inform
the user of the recommendation.

For GitHub:
```bash
gh pr review $PR_NUMBER --approve  # or --request-changes or --comment
```

---

## Important Rules

1. **Accuracy above all**: Every finding MUST be technically accurate and backed by a
   specific code reference in the diff or source file. Never guess. If you are unsure,
   use QUESTION severity or drop the finding.

2. **No speculation**: Do not post findings based on assumptions about code you
   have not read. If you need more context, read the file.

3. **Verify before posting**: Before posting any finding, verify it against the
   actual source code (not just the diff). Use `Read` or `Bash` to check the full
   file contents when the diff alone is ambiguous.

4. **Respect existing comments**: Check existing PR comments to avoid duplicating
   feedback that has already been given.

5. **Be constructive**: Frame findings as helpful suggestions, not criticisms.
   Explain the *why* behind each finding.

6. **Scale the review**: A 10-line PR does not need the same depth as a 1000-line PR.
   Adjust your thoroughness to match the scope of the change.

7. **Context matters**: Consider the PR description and commit messages. A
   "quick fix" PR for a production incident has different standards than a feature PR.

8. **Do not review generated code**: Skip auto-generated files (lockfiles, compiled
   output, generated types from schemas, etc.).

9. **Do not review deleted code**: Only review additions and modifications, not
   removals. The exception is if a deletion breaks something in the remaining code.

10. **Tag-specific strictness**: When specific tags are active, enforce those
    guidelines more strictly:
    - `ds` (design system): Extra scrutiny on accessibility, token usage, API stability,
      visual regression test coverage, and cross-browser compatibility.
    - `lib` (library): Extra scrutiny on public API surface, backward compatibility,
      bundle size, documentation, and semantic versioning.
    - `fe` (frontend): Extra scrutiny on performance (Core Web Vitals), accessibility,
      state management, and SEO.
    - `be` (backend): Extra scrutiny on error handling, logging, security, database
      patterns, and API contracts.
    - `script` (scripts): Extra scrutiny on error handling, idempotency, portability,
      and documentation.
