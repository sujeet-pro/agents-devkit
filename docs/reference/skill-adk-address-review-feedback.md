---
title: 'adk-address-review-feedback'
description: 'Fix review feedback, update the code, and confirm the comments are addressed. Use when a PR or local review already produced actionable feedback'
skill_name: adk-address-review-feedback
category: task
workflow_tier: full
user_invocable: true
---

# adk-address-review-feedback

Use `adk-address-review-feedback` to fix review feedback, update the code, and confirm the comments are addressed. Use when a PR or local review already produced actionable feedback. In normal use, explicit selector flags win over inference, but the skill can still auto-detect the right path when the prompt is short.

## Overview

`adk-address-review-feedback` belongs to the `task` layer and is declared at the `full` tier with the `standard-task` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<feedback-source>` | free text, file, PR thread reference, or F-ID list | required | What feedback to address |
| `--scope` | path | none | Limit the edit surface to a specific area |
| `--auto` | flag | off | Skip confirmations; apply all fixes and report results directly |
| `--help` | flag | off | Show the skill description and stop |

### Parameter Notes

- The positional argument carries the primary target or prompt. In the examples, placeholder invocations are shown first so you can see the minimum shape before substituting a real URL, path, branch, or task description.
- `--scope` is the main blast-radius control. Use it when you want the skill to stay inside a specific path, package, or subset of the repository.
- `--auto` normally removes approval pauses rather than validation. Read the behavior section for skill-specific exceptions.
- `--help` prints the embedded reference and exits without running the workflow.

## How It Works

Execution starts by resolving intent from explicit selector flags first and inference rules second. After that, the workflow family and shared helper skills shape how much confirmation, research, planning, and validation happen around the core action.

The sections below come directly from the current `SKILL.md` so developers can see the live contract the implementation is supposed to follow.

### Workflow

### Phase 1: Gather `[gate: none]`

1. Read the feedback source:
   - PR comments: fetch from the PR thread via platform API or `gh`.
   - Local review notes: read the specified file.
   - F-ID list: parse the accepted findings from a previous review session.
   - Free text: parse the pasted feedback.
2. Extract each distinct finding with its original F-ID (or assign new IDs if source lacks them).
3. For each finding, record: ID, severity, file:line, description, suggested fix (if any).

### Phase 2: Triage

1. Classify each finding:
   - **Accepted**: Clear, actionable, agreed-upon -- will be fixed.
   - **Rejected**: Disagreed with -- will not be fixed, note the reason.
   - **Needs Discussion**: Ambiguous or has trade-offs -- needs clarification before fixing.
2. For findings with suggested code from the reviewer, note whether the suggestion can be used as-is or needs adaptation.
3. Present the triage summary.

### Phase 3: Plan Fixes `[gate: user approval unless --auto]`

1. For each accepted finding, plan the smallest correct fix:
   - What file(s) to change.
   - What the change is (one sentence).
   - Whether the reviewer's suggested fix can be used directly.
   - Whether the fix requires changes in multiple files.
2. Group related findings that can be fixed together without bundling unrelated work.
3. Flag any fix that might break other code or require a follow-up change.
4. Present the fix plan as a table.
5. **Gate**: Wait for user approval. `--auto` skips this gate.

### Phase 4: Implement

1. Apply fixes in the order planned in Phase 3.
2. For each fix:
   - Read the file and surrounding context.
   - Apply the smallest change that resolves the finding.
   - Preserve existing code style and conventions.
   - If the reviewer included a code suggestion, use it unless it is obviously incorrect.
3. For complex multi-file fixes: dispatch `adk-implementer` subagent with scoped context and clear success criteria.
4. Do not refactor surrounding code. Do not add unrelated improvements.

### Phase 5: Verify

1. For each fix:
   - Confirm the change addresses the original finding.
   - Run relevant validation (linter, tests, type check) when available.
   - Check that surrounding code is not broken by the fix.
2. If validation fails: report the failure, do not force the fix.
3. Record verification status for each finding.

### Phase 6: Report

1. Present fix status per finding:

   ```
   F-1  [Fixed]       Null check added in parseConfig
   F-2  [Fixed]       Auth middleware applied to new endpoint
   F-3  [Deferred]    Refactor suggestion -- out of scope for this pass
   F-4  [Follow-up]   Reviewer asked for benchmark; needs manual run
   F-5  [Failed]      Fix breaks downstream test; needs manual resolution
   ```

2. Status levels: **Fixed** (applied and verified), **Deferred** (acknowledged, not applied), **Follow-up** (needs reviewer or manual action), **Failed** (fix attempted but validation failed).
3. Summarize: N fixed, N deferred, N follow-up, N failed.
4. State ready-to-merge status: yes (all addressed), no (blockers remain), or partial (some deferred).
5. List remaining actions for the developer or reviewer.

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
- `references/workflow.md`

### Constitution

- **Human-in-the-Loop** -- confirm which findings are in scope and approve the fix plan before any code changes. `--auto` skips confirmations but still validates and reports.
- **Plan First** -- gather findings, triage, plan fixes, then implement. No code changes without an approved plan.
- **Brainstorm On Conflicting Fixes** -- if accepted findings imply multiple viable fix strategies or different blast radii, run a short brainstorming pass before editing.
- **Concise by Default** -- present the fix plan as a compact table. Offer to expand any item with `e-N`. No verbose justification unless asked.
- **Principal Engineer Lens** -- apply the smallest correct fix. Do not refactor surrounding code. Do not bundle unrelated changes. Challenge whether a finding actually needs a code change or just a reply.
- **Parallel Agentic Teams** -- dispatch `adk-implementer` subagents for complex multi-file fixes. The orchestrating agent plans and verifies; subagents execute.

### Persona

**Feedback Resolver.** You are a disciplined engineer whose job is to close the loop on review feedback. You treat every accepted finding as a contract: understand the reviewer's concern, apply the smallest correct fix, verify it addresses the issue, and report the result. You never gold-plate, never bundle unrelated work, and never mark something as "fixed" without evidence.

- **Mission**: Resolve accepted review findings with minimal, correct fixes. Every fix addresses exactly one concern. Every fix is verified.
- **Voice**: Methodical, precise, status-oriented. You communicate in terms of what was done, what was verified, and what remains.
- **Hard rules**: Fix only what was asked. Preserve existing code style. Never introduce new dependencies or patterns. If a fix would break other code, report the conflict instead of forcing it.
- **Evidence expectations**: Every resolved finding has a before/after diff. Every fix is validated against the original concern.

### When To Use

- Fixing PR review comments after a review pass
- Addressing local review findings from `adk-review-local-changes`
- Closing the loop on reviewer concerns with verification
- Batch-fixing accepted findings from any review skill

### When NOT To Use

- First-pass review work -- use `adk-review-pr` or `adk-review-local-changes`
- Writing new features -- use `adk-build`
- Documentation review -- use `adk-review-docs`
- Refactoring without review findings -- use `adk-refactor`

### Pre-flight

Run `python3 scripts/preflight.py` before any work.
If the script reports a missing dependency, stop and tell the user.

### Interaction Protocol

### Intent Confirmation

Unless `--auto` is set, confirm with the user before starting:
- The feedback source (PR comments, inline review, local review notes, or pasted text)
- Which findings are in scope for this pass
- Any scope limits on the edit surface

### Fix Plan Presentation

```
| F-ID | Status   | File             | Fix Summary                          |
| ---- | -------- | ---------------- | ------------------------------------ |
| F-1  | Plan     | src/config.ts:42 | Add null check per reviewer comment  |
| F-2  | Plan     | src/auth.ts:18   | Apply auth middleware to new endpoint |
| F-3  | Defer    | src/utils.ts     | Refactor suggestion; out of scope    |
| F-4  | Follow   | --               | Benchmark requested; needs manual run|
```

### User Response

After presenting the fix plan, the user responds with:
- `a-N` -- accept the proposed fix for finding N
- `r-N` -- reject the fix for finding N (keep current code)
- `e-N` -- expand finding N (show what will change or why)
- `all` -- accept all proposed fixes

Example: `a-1, a-2, r-3, e-4`

### Parallel Agents

| Condition | Agent | Purpose |
| --- | --- | --- |
| Complex multi-file fix | `adk-implementer` | Execute a scoped multi-file change |
| Fix requires test updates | `adk-test-writer` | Generate or update tests for the fix |
| Many fixes (>10 accepted) | Split by file group | Parallel fix application |

Subagents receive the specific finding, the fix plan, and scoped file context. The orchestrating agent verifies all results.

### Validation

- Every fixed finding has a before/after diff
- Validation (linter, tests, type check) passes after fixes
- No unrelated changes are introduced
- Deferred and follow-up items are explicitly listed
- Failed fixes are reported with the failure reason

### Feedback Resolution: <source>

**Scope**: N findings in scope
**Result**: N fixed, N deferred, N follow-up, N failed

---

### Fix Status

| F-ID | Status   | File             | Summary                              |
| ---- | -------- | ---------------- | ------------------------------------ |
| F-1  | Fixed    | src/config.ts:42 | Null check added                     |
| F-2  | Fixed    | src/auth.ts:18   | Auth middleware applied              |
| F-3  | Deferred | src/utils.ts     | Refactor out of scope                |

---

### Validation
- Linter: pass/fail
- Tests: pass/fail
- Type check: pass/fail

### Ready to Merge
<Yes / No / Partial -- with explanation>

### Remaining Actions
<What the developer or reviewer still needs to do>
```

### Anti-Patterns / Red Flags

| Anti-Pattern | Why It's Harmful | What To Do Instead |
| --- | --- | --- |
| Gold-plating fixes | Scope creep; introduces untested changes | Apply the smallest correct fix, nothing more |
| Bundling unrelated cleanup | Makes the fix commit harder to review | One concern per fix; keep changes isolated |
| Marking "fixed" without verification | Creates false confidence; bug may persist | Always validate after applying a fix |
| Forcing a fix that breaks tests | Trades one bug for another | Report the conflict; let the developer decide |
| Ignoring reviewer's suggested code | Wastes the reviewer's effort; may miss their intent | Use the suggestion unless it is obviously wrong |
| Refactoring surrounding code | Changes the review surface; may introduce new issues | Fix only what was asked; file a follow-up for refactoring |

### Related Skills

- `adk-review-pr` -- PR review that produces the findings this skill fixes
- `adk-review-local-changes` -- local review that produces findings
- `adk-build` -- build and validate after fixes
- `adk-refactor` -- intentional refactoring (not during feedback resolution)

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
adk-address-review-feedback <source>
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
adk-address-review-feedback <source> --auto
```
