---
name: cross-review
description: "Use when you need multi-model peer review that runs code or document review through multiple AI providers and synthesizes findings with consensus indicators"
user_invocable: true
arguments:
  - name: target
    description: "What to review: PR URL, file paths, or document path"
    required: true
  - name: providers
    description: "Comma-separated provider list (default: uses available providers)"
    required: false
  - name: focus
    description: "Review focus: correctness, security, performance, architecture, all (default: all)"
    required: false
  - name: mode
    description: "Workflow mode: interactive (default), auto-approve"
    required: false
---

# Cross-Review

Use the shared contracts in `skills/_references/agentic-teams.md` and the multi-provider dispatch patterns from `skills/agent-multi/SKILL.md`.

This skill is review-only. It does not modify the target. It produces a consolidated review artifact with consensus indicators across multiple AI providers.

## Preflight

1. Detect the target type:
   - **PR**: URL or `owner/repo#number` format -> resolve via source MCP (GitHub or Bitbucket)
   - **Local files**: one or more file paths or glob patterns -> resolve to absolute paths and confirm they exist
   - **Document**: path to a markdown, text, or other document file -> read contents
2. Validate that at least 2 providers are available. Check for installed CLIs (`claude`, `codex`, `gemini`, `cursor-cli`, `opencode`) and native child agent support on the current platform. If `providers` is specified, verify each one is reachable.
3. If the target is a PR, read the diff, metadata, and existing comments through the matching source MCP before dispatching to providers.

## Host Rules

Follow the platform-specific dispatch rules from `skills/agent-multi/SKILL.md`:

### Claude Code / Codex / Gemini CLI

Use native child agents (preferred), ACP, or shell-based parallel dispatch:

```bash
# Example: dispatch review to multiple providers in parallel
claude --print "<review-prompt>" > /tmp/cross-review-claude.md &
codex --print "<review-prompt>" > /tmp/cross-review-codex.md &
gemini "<review-prompt>" > /tmp/cross-review-gemini.md &
wait
```

### Cursor / Cursor CLI / Junie / OpenCode

Use the platform's built-in multi-model capabilities. Do NOT shell out to external CLIs from Cursor.

### General Rules

- Do not require paid review or orchestration services.
- Prefer installed local CLIs when available.
- If only one provider is available, run it twice with different system prompts (e.g., one focused on correctness, one on architecture) for diversity.

## Workflow

### Phase 1: Target Resolution

1. Detect target type from the `target` argument.
2. For PRs: fetch the full diff, file list, commit messages, and existing review comments.
3. For local files: read file contents and surrounding context (imports, exports, tests).
4. For documents: read the full document content.
5. Build a self-contained review prompt that includes all necessary context so each provider can review independently.

### Phase 2: Build Review Prompt

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

Each provider receives the identical prompt to ensure comparable output.

### Phase 3: Parallel Dispatch

1. Select providers: use the `providers` argument if specified, otherwise auto-detect at least 2 available providers.
2. Dispatch the review prompt to all selected providers simultaneously using the host-appropriate method.
3. Apply a timeout of 120 seconds per provider (or the value from `timeout` if the caller passes one through to the underlying multi dispatch).
4. If a provider fails or times out, continue with remaining results. Note the failure in the output. Require at least 2 successful responses to proceed with consensus.

### Phase 4: Collect and Parse

1. Collect raw output from each provider.
2. Parse each provider's findings into a normalized structure: severity, file, line, category, issue description, suggestion, confidence.
3. Parse each provider's overall assessment summary.
4. Record provider metadata: model name, latency, number of findings produced.

### Phase 5: Merge and Reconcile

Run a consensus pass over all provider findings:

1. **Group similar findings**: match findings that reference the same file and line range (within 5 lines) and describe the same underlying issue. Use semantic similarity, not exact string matching.
2. **Classify consensus level** for each unique finding:
   - **Unanimous**: all providers flagged this issue
   - **Majority**: more than half of providers flagged this issue
   - **Split**: exactly half flagged it (only possible with even provider count)
   - **Single**: only one provider flagged this issue
3. **Compute weighted confidence**:
   - Start with the average confidence across providers that flagged the finding
   - Unanimous: multiply by 1.2 (cap at 99)
   - Majority: keep as-is
   - Split: multiply by 0.75
   - Single: multiply by 0.6
4. **Deduplicate**: merge grouped findings into a single canonical finding, preserving each provider's specific wording as a "perspective"
5. **Detect contradictions**: if one provider explicitly says something is fine while another flags it as an issue, mark it as a contradiction requiring human judgment
6. **Sort**: order findings by severity (critical > high > medium > low), then by consensus level (unanimous > majority > split > single), then by weighted confidence descending

### Phase 6: Present Findings

#### Interactive Mode (default)

Present each finding to the user one at a time:

```text
## Finding [N/total] - [severity: critical|high|medium|low] - Consensus: [unanimous|majority|split|single]

Providers that flagged this: <provider-a>, <provider-b>
File: <path:line>
Category: <correctness|security|performance|architecture|maintainability|testing|documentation>

Issue: <description>
Confidence: NN% (weighted by consensus)

Provider perspectives:
- Provider A: "<position>"
- Provider B: "<position>"
- Provider C: "<different take>" (DISSENT)

Suggested fix:
<merged suggestion>

Action: [A]ccept | [E]dit | [R]eject | [S]kip
```

##### Actions

- **Accept**: include the finding in the final review output as-is.
- **Edit**: let the user revise the finding description or suggestion before including it.
- **Reject**: discard the finding entirely.
- **Skip**: defer to the end. After all other findings are processed, return to skipped items for a final decision.

##### Loop Rules

1. Process findings in severity order, then consensus order.
2. If the user says "accept all remaining", accept all unprocessed findings.
3. If the user says "reject all remaining", discard all unprocessed findings.
4. Contradictions (where providers explicitly disagree) must be presented individually and cannot be bulk-accepted; the user must make a judgment call.

#### Auto-Approve Mode

When `mode=auto-approve`:

1. Automatically accept all findings with unanimous or majority consensus and confidence >= 70%.
2. Automatically reject all single-provider findings with confidence < 50%.
3. Present only split findings and contradictions to the user for manual decision.
4. If no findings require manual decision, skip the interactive loop entirely.

### Phase 7: Output

Produce a consolidated review artifact with these sections:

```text
## Cross-Review Summary

Target: <target description>
Providers: <provider-a (model)>, <provider-b (model)>, <provider-c (model)>
Focus: <focus area>
Mode: <interactive|auto-approve>

### Provider Stats
| Provider   | Model       | Latency | Findings | Unique Contributions |
|------------|-------------|---------|----------|----------------------|
| Provider A | <model>     | N.Ns    | N        | N                    |
| Provider B | <model>     | N.Ns    | N        | N                    |
| Provider C | <model>     | N.Ns    | N        | N                    |

### Consensus Matrix
| Consensus Level | Count | Avg Confidence |
|-----------------|-------|----------------|
| Unanimous       | N     | NN%            |
| Majority        | N     | NN%            |
| Split           | N     | NN%            |
| Single          | N     | NN%            |

### Findings

[Accepted findings in severity order, each with consensus indicator and provider perspectives]

### Contradictions Requiring Judgment

[Any unresolved contradictions where providers explicitly disagreed]

### Rejected Findings

[Brief list of rejected findings with reason, for auditability]

### Per-Provider Contribution

[Which providers caught issues others missed, and which providers had the most rejected findings -- useful for calibrating provider selection over time]

### Overall Assessment

[Synthesized summary combining the overall assessments from each provider, noting areas of agreement and disagreement]
```

## Adjacent Skills

- `review-code-pr`: single-provider PR review with comment reconciliation and source posting. Use cross-review when you want multi-provider consensus; use review-code-pr when you want deep single-provider review with interactive comment management.
- `agent-multi`: general-purpose multi-provider task execution. Cross-review uses agent-multi dispatch patterns but adds review-specific consensus scoring and interactive finding presentation.
- `agent-team`: multi-agent team orchestration. Use agent-team for general collaborative workflows; use cross-review specifically for review tasks where consensus indicators matter.
