# Cross-Review Stage

Multi-model peer review that runs code or document review through multiple Claude models and synthesizes findings with consensus indicators.

This stage is triggered by `--cross`. It does not modify the target. It produces a consolidated review artifact with consensus indicators across multiple models.

Uses the shared contracts in `references/agentic-teams.md` and multi-model dispatch patterns.

---

## Parameters (inherited from parent)

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--models` | comma-separated model names (e.g., `opus,sonnet`) | auto (2+ models) | Which models to use for review |
| `--focus` | `correctness`, `security`, `performance`, `architecture`, `all` | `all` | Weight review toward a specific concern |
| `--mode` | `interactive`, `auto-approve` | `interactive` | Whether to present findings one-by-one or auto-accept by consensus |

---

## Phase 1: Target Resolution

1. Detect target type from the `target` argument.
2. For PRs: fetch the full diff, file list, commit messages, and existing review comments.
3. For local files: read file contents and surrounding context (imports, exports, tests).
4. For documents: read the full document content.
5. Build a self-contained review prompt that includes all necessary context so each model can review independently.

## Phase 2: Build Review Prompt

Construct a review prompt that includes:

- The full diff or file contents
- The review focus area (`focus` argument or "all")
- Instructions to produce structured findings in a consistent format:
  ```
  FINDING_START
  severity: critical|high|medium|low
  file: <path:line>
  category: correctness|security|performance|architecture|maintainability|testing|documentation
  issue: <description>
  suggestion: <recommended fix or improvement>
  confidence: <0-100>
  FINDING_END
  ```
- Request for a brief overall assessment summary

Each model receives the identical prompt to ensure comparable output.

## Phase 3: Parallel Dispatch

Launch multiple child agents using Claude Code's Agent tool with different models:

```
Agent(model: "opus", prompt: "<review-prompt>")
Agent(model: "sonnet", prompt: "<review-prompt>")
```

Launch all agents in a single message for true parallel execution. If a model fails or times out, continue with remaining results. Require at least 2 successful responses for consensus.

## Phase 4: Collect and Parse

1. Collect raw output from each model.
2. Parse each model's findings into a normalized structure: severity, file, line, category, issue description, suggestion, confidence.
3. Parse each model's overall assessment summary.
4. Record model metadata: model name, number of findings produced.

## Phase 5: Merge and Reconcile

Run a consensus pass over all model findings:

1. **Group similar findings**: match findings that reference the same file and line range (within 5 lines) and describe the same underlying issue. Use semantic similarity, not exact string matching.
2. **Classify consensus level** for each unique finding:
   - **Unanimous**: all models flagged this issue
   - **Majority**: more than half of models flagged this issue
   - **Split**: exactly half flagged it (only possible with even model count)
   - **Single**: only one model flagged this issue
3. **Compute weighted confidence**:
   - Start with the average confidence across models that flagged the finding
   - Unanimous: multiply by 1.2 (cap at 99)
   - Majority: keep as-is
   - Split: multiply by 0.75
   - Single: multiply by 0.6
4. **Deduplicate**: merge grouped findings into a single canonical finding, preserving each model's specific wording as a "perspective"
5. **Detect contradictions**: if one model explicitly says something is fine while another flags it as an issue, mark it as a contradiction requiring human judgment
6. **Sort**: order findings by severity (critical > high > medium > low), then by consensus level (unanimous > majority > split > single), then by weighted confidence descending

## Phase 6: Present Findings

### Interactive Mode (default)

Present each finding to the user one at a time:

```text
## Finding [N/total] - [severity: critical|high|medium|low] - Consensus: [unanimous|majority|split|single]

Models that flagged this: <model-a>, <model-b>
File: <path:line>
Category: <correctness|security|performance|architecture|maintainability|testing|documentation>

Issue: <description>
Confidence: NN% (weighted by consensus)

Model perspectives:
- Model A: "<position>"
- Model B: "<position>"
- Model C: "<different take>" (DISSENT)

Suggested fix:
<merged suggestion>

Action: [A]ccept | [E]dit | [R]eject | [S]kip
```

#### Actions

- **Accept**: include the finding in the final review output as-is.
- **Edit**: let the user revise the finding description or suggestion before including it.
- **Reject**: discard the finding entirely.
- **Skip**: defer to the end. After all other findings are processed, return to skipped items for a final decision.

#### Loop Rules

1. Process findings in severity order, then consensus order.
2. If the user says "accept all remaining", accept all unprocessed findings.
3. If the user says "reject all remaining", discard all unprocessed findings.
4. Contradictions (where models explicitly disagree) must be presented individually and cannot be bulk-accepted; the user must make a judgment call.

### Auto-Approve Mode

When `mode=auto-approve`:

1. Automatically accept all findings with unanimous or majority consensus and confidence >= 70%.
2. Automatically reject all single-model findings with confidence < 50%.
3. Present only split findings and contradictions to the user for manual decision.
4. If no findings require manual decision, skip the interactive loop entirely.

## Phase 7: Output

Produce a consolidated review artifact:

```text
## Cross-Review Summary

Target: <target description>
Models: <model-a>, <model-b>, <model-c>
Focus: <focus area>
Mode: <interactive|auto-approve>

### Model Stats
| Model   | Findings | Unique Contributions |
|---------|----------|----------------------|
| Model A | N        | N                    |
| Model B | N        | N                    |

### Consensus Matrix
| Consensus Level | Count | Avg Confidence |
|-----------------|-------|----------------|
| Unanimous       | N     | NN%            |
| Majority        | N     | NN%            |
| Split           | N     | NN%            |
| Single          | N     | NN%            |

### Findings

[Accepted findings in severity order, each with consensus indicator and model perspectives]

### Contradictions Requiring Judgment

[Any unresolved contradictions where models explicitly disagreed]

### Rejected Findings

[Brief list of rejected findings with reason, for auditability]

### Overall Assessment

[Synthesized summary combining the overall assessments from each model]
```
