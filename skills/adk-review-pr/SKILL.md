---
name: adk-review-pr
description: Review a remote pull request with severity-tiered findings, evidence per finding, and posted-back comments via the appropriate provider (GitHub, Bitbucket). Use when a PR URL is the target and the deliverable is a structured review (findings + optional posted comments). Do not use for local uncommitted changes (use adk-review-local), addressing existing reviewer feedback (use adk-review-feedback), or auditing the whole repo (use adk-audit-repo).
---

# ADK Review / PR

Standalone task skill under the `adk-review` category router. Produces a findings-first review of a remote PR with explicit severity per finding and clear evidence.

## When to use

- A PR URL on GitHub or Bitbucket is the target.
- Deliverable is a structured review report and (optionally) posted PR comments.
- The reviewer wants severity-tiered, evidence-backed findings, not freeform prose.

## When NOT to use

- Changes are local and not yet pushed -> `adk-review-local`
- Reviewer comments already exist and need to be addressed in code -> `adk-review-feedback`
- Multi-dimensional repo-wide audit -> `adk-audit-repo`
- Doc-only review -> `adk-docs-review`

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<pr-url>` | yes | Full PR URL (provider auto-detected) |
| `<focus>` | optional | `correctness` / `security` / `performance` / `style` / `all` (default) |
| `<post-mode>` | optional | `dry-run` (default - report only) / `post` (post inline + summary) |
| `<scope>` | optional | Path filter inside the PR diff |
| `--auto` | optional | Skip approval gates (still validates) |

## Workflow

1. **Confirm intent** - restate PR, focus, post-mode, scope. Approval gate unless `--auto`.
2. **Fetch context** - retrieve PR diff, description, related issue, branch, base, and any existing comments. Use `gh pr view`, `gh pr diff`, or the relevant MCP. Confirm the diff matches the URL.
3. **Read code** - read the changed files in their post-PR state, plus immediate dependencies and tests. Repo evidence over guessing.
4. **Run dimension passes** - depending on focus, run each dimension as a parallel pass and collect findings:
   - Correctness: logic, edge cases, error handling, types.
   - Security: input validation, secrets, authz/n, injection.
   - Performance: complexity, allocations, network round-trips.
   - Style: naming, structure, repo conventions.
   - Tests: coverage of changed behavior, regression for any bug fixed.
5. **Tier findings** - assign each finding a severity label (Blocker / Critical / Should Have / May Have / Nitpick / Question).
6. **Validate** - reread each finding against the diff to ensure it is real and reproducible. Drop low-evidence findings.
7. **Decide post-mode** - if `post`, draft inline comments (one finding per comment, anchored to a file/line) plus a summary; ask for approval before posting unless `--auto`.
8. **Report** - findings-first markdown with severity ordering, evidence per finding, suggested change, and (if posted) links to inline comments.

## Severity ladder

| Label | Meaning |
| --- | --- |
| `Blocker` | Must fix before merge - bug, security hole, broken contract |
| `Critical` | Strongly recommended fix; would normally block release |
| `Should Have` | Improvement that meaningfully raises quality |
| `May Have` | Optional polish |
| `Nitpick` | Style or taste only |
| `Question` | Reviewer uncertain; needs clarification |

Lead with the highest. Never mix levels in one bullet.

## Finding template

Each finding follows this exact shape:

```markdown
### [<Severity>] <One-line summary>
- **File**: `path/to/file.ts:LINE-LINE`
- **Issue**: <2-3 sentence explanation>
- **Evidence**: <quoted snippet or repro>
- **Suggested change**: <concrete recommendation, code if useful>
- **Why this severity**: <one sentence>
```

## Output format

```
## PR Review: <PR title> (#<number>)
- URL: <pr-url>
- Diff: <files> files, +<additions> / -<deletions>
- Focus: <focus>
- Post mode: <dry-run | posted>

## Verdict
<approve | request-changes | comment>

## Findings

### Blockers
<finding blocks>

### Critical
<finding blocks>

### Should Have
<finding blocks>

### May Have
<finding blocks>

### Nitpicks
<finding blocks>

### Questions
<finding blocks>

## Out of Scope
- <items explicitly not reviewed and why>

## Validation
- Diff fetched: YES
- Code read in context: YES
- Inline comments posted: <count or N/A>
- Summary comment posted: <YES | N/A>

Need more detail on any finding?
```

## Posting rules

- Inline comments anchor to a precise line range from the PR diff.
- Each inline comment = one finding. Do not staple multiple findings into one comment.
- Summary comment lists Blockers and Critical only; everything else stays inline.
- Never auto-approve unless the user explicitly says so.
- Never request changes for nitpicks alone.

## Anti-patterns

- Mixing severities in a single bullet ("nit / blocker?"). Pick one.
- Findings without evidence. If you cannot quote it, do not file it.
- Reviewing the description instead of the code.
- Stating "looks good" without enumerating what was inspected.
- Posting before the user approves (unless `--auto`).
- Letting nitpicks dominate the summary; reorder by severity.

## Examples

```
adk-review-pr https://github.com/org/repo/pull/842 --focus correctness,security
```

```
adk-review-pr https://bitbucket.org/org/repo/pull-requests/17 --post-mode post --auto
```

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/anti-patterns.md` | Things to avoid when running this skill. |
| `references/constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/examples.md` | Example trigger phrases, invocation, and report shape. |
| `references/mcp-fallback.md` | Preferred MCP server and the manual fallback when it is missing. |
| `references/output-format.md` | Verbosity modes, result shape, severity labels. |
| `references/persona.md` | The agent persona that drives this skill. |
| `references/review-comment-format.md` | Standard finding format with stable IDs and severities. |

<!-- adk:references:end -->
