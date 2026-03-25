---
name: agent-multi
description: Run a task through multiple providers or models in parallel and merge the result with a consensus pass, while respecting host-platform constraints
user_invocable: true
arguments:
  - name: task
    description: "Task description or skill invocation to run in multi mode"
    required: true
  - name: models
    description: "Optional comma-separated providers or models to use"
    required: false
  - name: strategy
    description: "Consensus strategy: merge, vote, best-of (default: merge)"
    required: false
  - name: timeout
    description: "Optional timeout per provider"
    required: false
---

# Multi

Use `skills/_references/agentic-teams.md`.

## Host Rules

### Claude Code / Codex / Gemini CLI

These platforms support spawning child agents or running external CLIs:

1. **Native child agents** (preferred): Use the platform's built-in agent spawning (e.g., Claude Code's Agent tool, Codex child agents, Gemini native agents)
2. **ACP (Agent Communication Protocol)**: If the platform supports ACP, use it to coordinate between agents with different models
3. **Shell-based fallback**: Spawn external CLIs in parallel via shell:
   ```bash
   # Example: run claude and codex in parallel
   claude --print "task prompt" > /tmp/result-claude.md &
   codex --print "task prompt" > /tmp/result-codex.md &
   wait
   ```

### Cursor / Cursor CLI / Junie / OpenCode

These platforms have built-in multi-model support:

- **Cursor**: Use Cursor's model selector to run the same prompt with different models (e.g., claude-sonnet, gpt-4o, gemini-pro). Do NOT shell out to external CLIs.
- **Junie (IntelliJ)**: Use Junie's provider configuration to switch models
- **OpenCode**: Use OpenCode's multi-provider feature to run against different configured models

### General Rules

- Do not require paid review or orchestration services
- Prefer installed local CLIs when available
- If only one model/provider is available, run it twice with different temperature or system prompts for diversity

## Workflow

1. **Normalize the task**: Convert the skill invocation or description into a self-contained prompt that any model can execute independently
2. **Select providers**: Choose at least 2 from available models/CLIs. If `models` specified, use those. Otherwise auto-detect:
   - Check for: `claude`, `codex`, `gemini`, `cursor-cli`, `opencode`
   - Fall back to native child agents with different system prompts
3. **Dispatch in parallel**: Send the same prompt to each provider simultaneously
4. **Collect results**: Wait for all providers (respect `timeout` if set)
5. **Consensus pass**: Run `consensus-agent` with all results using the chosen `strategy`:
   - **merge** (default): Combine unique insights, deduplicate, resolve conflicts
   - **vote**: Majority wins on each point, minority views noted
   - **best-of**: Score each result holistically, select the best, supplement with unique insights from others
6. **Preserve minority views**: When they materially affect correctness or risk

## Output

Return:

- provider-by-provider status (model, latency, result summary)
- merged result (the consensus output)
- disagreements that need human judgment (with context from each provider)
- confidence assessment (higher when providers agree, lower when they diverge)
