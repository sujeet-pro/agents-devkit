---
name: review-local
description: Self-review uncommitted, staged, or branch-vs-base changes before pushing or committing - with severity-tiered findings and explicit evidence. Use when the change has not yet been pushed and the goal is to catch issues before they land in a remote PR. Do not use for an existing remote PR (use adk-review-pr) or for addressing reviewer feedback (use adk-review-feedback).
metadata:
  category: review
  kind: task
  layer: 5
  modes: [auto, review, fix]
---

# ADK Review / Local

Standalone task skill under the `@adk:review` (a.k.a. `adk-review`) category router. Produces a findings-first self-review of local working-tree changes (unstaged, staged, or branch-vs-base).

## When to use

- Reviewing uncommitted edits before staging.
- Reviewing staged changes before committing.
- Reviewing the current branch against its base before pushing.
- Catching issues that are cheaper to fix locally than on a remote PR.

## When NOT to use

- The change is already on a remote PR -> `@adk:review-pr` (a.k.a. `adk-review-pr`)
- Reviewer comments already exist -> `@adk:review-feedback` (a.k.a. `adk-review-feedback`)
- Multi-dimensional repo audit -> `@adk:audit-repo` (a.k.a. `adk-audit-repo`)
- Doc-only review -> `@adk:docs-review` (a.k.a. `adk-docs-review`)

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<target>` | yes | `unstaged` / `staged` / `branch` (default `branch` vs origin's tracking base or `main`) |
| `<base>` | optional | Base ref for `branch` mode (default: tracking branch or `main`) |
| `<focus>` | optional | `correctness` / `security` / `performance` / `style` / `all` (default) |
| `<scope>` | optional | Path filter |
| `--auto` | optional | Skip approval gates |

## Workflow

1. **Confirm intent** - restate target, base, focus, scope. Approval gate unless `--auto`.
2. **Capture diff** - run the appropriate `git diff` (unstaged / staged / `<base>...HEAD`). Confirm files changed and line counts.
3. **Read code** - read changed files in working-tree state, plus immediate dependencies and tests. Repo evidence over guessing.
4. **Run dimension passes** - same dimensions as `adk-review-pr` (correctness / security / performance / style / tests).
5. **Tier findings** - assign severity (Blocker / Critical / Should Have / May Have / Nitpick / Question).
6. **Validate** - reread each finding against the diff to confirm it is real and actionable in this branch.
7. **Report** - findings-first markdown ordered by severity; recommend the next move (fix locally now, or proceed to commit / PR).

## Severity ladder

| Label | Meaning |
| --- | --- |
| `Blocker` | Fix before pushing - bug, security hole, broken contract |
| `Critical` | Strongly recommended fix; would normally block a PR |
| `Should Have` | Improvement that meaningfully raises quality |
| `May Have` | Optional polish |
| `Nitpick` | Style or taste only |
| `Question` | Reviewer uncertain; needs clarification |

## Finding template

```markdown
### [<Severity>] <One-line summary>
- **File**: `path/to/file.ts:LINE-LINE`
- **Issue**: <2-3 sentence explanation>
- **Evidence**: <quoted snippet>
- **Suggested change**: <concrete recommendation, code if useful>
- **Why this severity**: <one sentence>
```

## Output format

```
## Local Review: <target> (<files> files, +<add> / -<del>)
- Base: <base ref> (for branch mode)
- Focus: <focus>

## Verdict
<ready-to-commit | needs-fixes | needs-discussion>

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

## Recommended Next Step
- <e.g. "fix Blockers in src/auth/", or "ready for `@adk:publish-commit` (a.k.a. `adk-publish-commit`)">

Need more detail on any finding?
```

## Pre-commit gates

If the repo has pre-commit hooks (`pre-commit`, husky, lefthook, etc.), the report must:

- Note whether they were run (the hook output goes through the dimension passes too).
- Distinguish hook failures (from the tooling) from review findings (from this skill).

## Branch-mode specifics

- Default base is the tracking branch (`git rev-parse --abbrev-ref --symbolic-full-name @{u}`); fall back to `origin/main` then `main`.
- Use `git diff <base>...HEAD` (three dots) to compare merge bases, not the moving base ref.
- For multi-commit branches, also skim each commit message for inconsistencies.

## Anti-patterns

- Reviewing the diff without reading the surrounding code.
- Posting nitpicks ahead of Blockers.
- Marking "ready to commit" while validation has not been run.
- Generic "looks good" without enumerating what was inspected.
- Treating linter complaints as Blockers automatically; classify by impact.

## Examples

```
adk-review-local --target staged --focus correctness,security
```

```
adk-review-local --target branch --base origin/main --scope src/auth/
```

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/review-local-clarifying-questions.md`) and reports the choices.

1. **What is the base for comparison (origin/<branch>, main, last commit, custom)?** — _How to pick:_ Default = upstream of current branch; fallback to main. Custom = pass an explicit base ref.
2. **Scope: full diff or only staged changes?** — _How to pick:_ Default = full diff (catches unstaged forgotten work). Staged-only when preparing a commit.
3. **Focus: correctness, security, performance, style, all?** — _How to pick:_ All by default; narrow when re-reviewing after fixes.

**Default report:** Verdict + severity-grouped findings + commit-readiness call.

**Detailed report (on request or `--verbose`):** Add: per-file diff summary, lint/typecheck output, test-coverage delta vs base, suggested patches.

**Artifact:** `local-review-report` — Markdown report. The working tree is unchanged.

**Artifact path:** .temp/reports/review-local-<slug>.md

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/review-local-clarifying-questions.md`) and reports the choices.

1. **What is the base for comparison (origin/<branch>, main, last commit, custom)?** — _How to pick:_ Default = upstream of current branch; fallback to main. Custom = pass an explicit base ref.
2. **Scope: full diff or only staged changes?** — _How to pick:_ Default = full diff (catches unstaged forgotten work). Staged-only when preparing a commit.
3. **Focus: correctness, security, performance, style, all?** — _How to pick:_ All by default; narrow when re-reviewing after fixes.

## Default vs detailed output

**Default report:** Verdict + severity-grouped findings + commit-readiness call.

**Detailed report (on request or `--verbose`):** Add: per-file diff summary, lint/typecheck output, test-coverage delta vs base, suggested patches.

**Artifact:** `local-review-report` — Markdown report. The working tree is unchanged.

**Artifact path:** .temp/reports/review-local-<slug>.md

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/review-local-anti-patterns.md` | Things to avoid when running this skill. |
| `references/review-local-artifact-format.md` | The deliverable's format and where it lives (.temp/ contract). |
| `references/review-local-clarifying-questions.md` | The default-ask questions for this skill, with how-to-pick rubrics. |
| `references/review-local-constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/review-local-examples.md` | Example trigger phrases, invocation, and report shape. |
| `references/interaction-contract.md` | Default-ask, explained-options, --auto contract every skill must follow. |
| `references/review-local-output-format.md` | Default vs detailed report shapes; severity labels; verbosity rules. |
| `references/review-local-persona.md` | The agent persona that drives this skill. |
| `references/review-local-research-protocol.md` | Source ordering, stop conditions, evidence buckets, citation discipline. |
| `references/review-local-review-comment-format.md` | Standard finding format with stable IDs and severities. |
| `references/review-local-validator.md` | The four-phase validator gate (pre-execution, mid-flow, pre-handoff, post-execution) this skill MUST run. |

<!-- adk:references:end -->
