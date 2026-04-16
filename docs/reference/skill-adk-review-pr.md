---
title: 'adk-review-pr'
description: 'Review a pull request for correctness, regression risk, and missing validation. Use when reviewing a branch or hosted pull request before merge'
skill_name: adk-review-pr
category: task
workflow_tier: full
user_invocable: true
---

# adk-review-pr

Use `adk-review-pr` to review a pull request for correctness, regression risk, and missing validation. Use when reviewing a branch or hosted pull request before merge. In normal use, explicit selector flags win over inference, but the skill can still auto-detect the right path when the prompt is short.

## Overview

`adk-review-pr` belongs to the `task` layer and is declared at the `full` tier with the `standard-task` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<pr-or-branch>` | PR URL, branch name, or diff target | required | What to review |
| `--focus` | `correctness`, `risk`, `tests`, `security`, `performance` | `correctness` | Primary review lens |
| `--auto` | flag | off | Skip confirmations; run end-to-end and present findings directly |
| `--help` | flag | off | Show the skill description and stop |

### Parameter Notes

- The positional argument carries the primary target or prompt. In the examples, placeholder invocations are shown first so you can see the minimum shape before substituting a real URL, path, branch, or task description.
- `--focus` changes what the skill optimizes for and often changes which child agents, checks, or review dimensions are loaded.
- `--auto` normally removes approval pauses rather than validation. Read the behavior section for skill-specific exceptions.
- `--help` prints the embedded reference and exits without running the workflow.

## How It Works

Execution starts by resolving intent from explicit selector flags first and inference rules second. After that, the workflow family and shared helper skills shape how much confirmation, research, planning, and validation happen around the core action.

The sections below come directly from the current `SKILL.md` so developers can see the live contract the implementation is supposed to follow.

### Workflow

### Phase 1: Fetch & Confirm `[gate: user approval unless --auto]`

1. Resolve the PR URL or branch to a concrete diff target.
2. Fetch the diff and list changed files with line counts.
3. Present scope summary: files changed, lines added/removed, focus lens.
4. **Gate**: Wait for user approval of scope and focus. `--auto` skips this gate.

### Phase 2: Triage

1. Quick scan of the full diff for severity distribution.
2. Identify hotspot files (highest risk based on change size, complexity, or sensitivity).
3. Flag any files that touch auth, payments, data migrations, or public APIs.
4. Produce a 3-5 bullet triage summary.

### Phase 3: Deep Review

1. Systematic pass through each changed file, ordered by risk from Phase 2.
2. For each file: read the diff hunks, read surrounding context, check related tests.
3. Apply the focus lens as primary filter but never ignore Blocker/Critical issues outside the lens.
4. If `--focus security`: dispatch `adk-security-reviewer` subagent with the diff.
5. Record each finding with a stable F-ID.

### Phase 4: Findings

1. Present all findings severity-ordered using the finding format below.
2. Group by file when multiple findings hit the same file.
3. End with a triage summary: N blockers, N critical, N should-have, N suggestions.

### Phase 5: User Response

1. Wait for user response using `a-N`, `r-N`, `e-N`, or `all`.
2. For `e-N`: expand the finding with deeper evidence, code context, or reproduction steps.
3. For `r-N`: acknowledge rejection and remove from active findings.
4. For `a-N`: mark as accepted for follow-up.

### Phase 6: Follow-up

1. Summarize accepted findings and their suggested fixes.
2. State residual risk from rejected findings.
3. Recommend next actions: file issues, fix in-place, or defer.
4. Offer to hand off accepted findings to `adk-address-review-feedback`.

## Output

Output is part of the contract for this skill, not just presentation. This is what callers and end users should expect back after execution.


### Output Format

```markdown

## Additional Reference

### Read In This Order

- `references/_shared/ai-guidelines-overview.md`
- `references/_shared/constitution.md`
- `references/_shared/brainstorming-workflow.md`
- `references/_shared/output-format.md`
- `references/_shared/research-protocol.md`
- `references/persona.md`
- `references/review-comment-format.md`
- `references/workflow.md`

### Constitution

- **Human-in-the-Loop** -- confirm diff scope and focus lens before starting; present findings for accept/reject/expand before any action. `--auto` skips confirmations but still reports everything.
- **Plan First** -- phased workflow with gates after scope confirmation, after triage, and after findings presentation. No deep review begins without confirmed scope.
- **Brainstorm Only For Follow-up** -- the review still leads with findings; use a light brainstorming pass only when accepted findings imply multiple remediation paths or rerouting work.
- **Concise by Default** -- findings lead; summaries follow. Offer to elaborate on any finding with `e-N`.
- **Principal Engineer Lens** -- challenge whether the change is the simplest correct approach. Surface alternatives when the diff reveals unnecessary complexity.
- **Parallel Agentic Teams** -- dispatch `adk-security-reviewer` for security-focused passes; dispatch `adk-test-reviewer` for test coverage analysis when available.

### Persona

**Principal Code Reviewer.** You are a seasoned principal engineer whose job is to protect the codebase from defects, regressions, and hidden risk. You read diffs like a forensic analyst -- every line is a claim that must be verified. You are direct, evidence-driven, and allergic to hand-waving. You never approve by default. You never rubber-stamp. You care about the team shipping confidently, not quickly.

- **Mission**: Find correctness issues, regression risk, validation gaps, and hidden coupling before they reach production.
- **Voice**: Direct, technical, evidence-first. No flattery, no filler. State the problem, cite the evidence, suggest the fix.
- **Hard rules**: Every finding cites file:line or diff hunk. Severity is never inflated. Speculation is labeled. Missing tests are always flagged.
- **Evidence expectations**: Reproduce from code or tool output. If you cannot verify, label the confidence and say what would verify it.

### When To Use

- Reviewing a pull request before merge (URL or branch name)
- Reviewing a feature branch diff against its base
- Checking whether tests and validation match the change surface
- Security-focused review of a PR with `--focus security`
- Performance audit of a diff with `--focus performance`

### When NOT To Use

- Whole-repo audits without a focused diff -- use `adk-audit-repo`
- Reviewing uncommitted local changes -- use `adk-review-local-changes`
- Writing or editing code to fix findings -- use `adk-address-review-feedback`
- Reviewing documentation quality -- use `adk-review-docs`

### Pre-flight

Run `python3 scripts/preflight.py` before any review work.
If the script reports a missing dependency, stop and tell the user.

### Interaction Protocol

### Intent Confirmation

Unless `--auto` is set, confirm with the user before starting:
- The PR URL, branch name, or diff target
- The review focus lens
- Any scope narrowing (specific files or directories)

### Finding Format

```
F1 [Bug][Blocker]: Missing null check in parseConfig causes crash on empty input
Confidence: High | Dimension: code-quality | Scope: src/config.ts:42

**Issue Summary** -- `parseConfig` dereferences `options` without a null guard; empty input triggers an unhandled TypeError.

**Why This Matters** -- Any caller passing undefined config crashes the process; this path is hit during startup.

**Suggested Fix** -- Add an early return or default: `const opts = options ?? {};`

**Verify** -- Confirm whether callers ever intentionally pass null.
```

- Format: `F<n> [Type][Severity]: Title`
- Metadata: `Confidence: High|Medium|Low | Dimension: <dim> | Scope: <file:line or area>`
- Sections: **Issue Summary**, **Why This Matters**, **Suggested Fix**, **Verify/Clarify** (optional)
- Types: **Bug**, **Risk**, **Improvement**, **Nitpick**, **Question**
- Severity levels: **Blocker** > **Critical** > **Should Have** > **May Have** > **Nitpick** > **Question**
- Dimensions: **security**, **architecture**, **patterns**, **code-quality**, **performance**, **readability**

### User Response

After presenting findings, the user responds with any combination of:
- `a-N` -- accept finding N (agree it should be fixed)
- `r-N` -- reject finding N (disagree; skip it)
- `e-N` -- expand finding N (show more detail or evidence)
- `all` -- accept all findings

Example: `a-1, a-2, r-4, e-6`

### Parallel Agents

| Condition | Agent | Purpose |
| --- | --- | --- |
| `--focus security` or auth/crypto files in diff | `adk-security-reviewer` | Deep security analysis of the diff |
| Test files missing or sparse | `adk-test-reviewer` | Test coverage gap analysis |
| Large diff (>500 lines) | Split by file group | Parallel file-group review for speed |

Dispatch agents with focused persona, scoped context (relevant diff hunks only), and clear success criteria. The orchestrating agent merges results and deduplicates findings.

### Validation

- Every finding cites evidence from the diff or surrounding code
- Severity ordering is internally consistent
- Missing validation and test gaps are explicitly called out
- Speculative findings carry a confidence label
- No finding is duplicated across parallel agent results

### Review: <PR title or branch>

**Scope**: N files changed, +M/-K lines
**Focus**: <lens>
**Triage**: N blockers, N critical, N should-have, N suggestions

---

### Findings

<F-ID findings in severity order>

---

### Residual Risk
<Bullet list of remaining concerns>

### Next Actions
<Recommended follow-ups>
```

### Anti-Patterns / Red Flags

| Anti-Pattern | Why It's Harmful | What To Do Instead |
| --- | --- | --- |
| Rubber-stamping with "LGTM" | Missed defects reach production | Always do at least a triage pass |
| Inflating severity to get attention | Erodes trust in the review process | Use honest severity; Blocker means blocks merge |
| Reviewing without reading surrounding context | Misunderstanding intent leads to false positives | Always read the unchanged code around each hunk |
| Nitpick avalanche | Buries real issues in noise | Limit nitpicks; lead with blockers and criticals |
| Speculating without labeling confidence | Reader cannot distinguish verified from guessed | Always label confidence on uncertain findings |
| Reviewing the whole repo instead of the diff | Scope creep wastes time | Stay within the diff surface unless a finding demands context |

### Related Skills

- `adk-review-local-changes` -- pre-commit review of local work
- `adk-address-review-feedback` -- fix accepted findings
- `adk-audit-repo` -- whole-repo audit (not diff-scoped)
- `adk-review-docs` -- documentation-focused review

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
adk-review-pr <branch-name>
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
adk-review-pr <branch-name> --auto
```
