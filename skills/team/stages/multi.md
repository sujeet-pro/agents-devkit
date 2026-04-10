# Multi Stage

Run a task through multiple models in parallel using Claude Code child agents and merge the result with a consensus pass.

Invoke /adk:agentic-teams for the child-agent contract.

## Workflow

This stage uses the **Quick Action** workflow: confirm → execute → verify.

1. **Normalize the task**: Build a self-contained prompt with the full task description, relevant context from the codebase, and any skill instructions needed.

2. **Select models**: Use the `models` argument if provided (comma-separated model names like `opus,sonnet,haiku`). If not specified, default to running the task with at least 2 different approaches:
   - Run with different system prompts or focus areas
   - Or use different Claude models via the Agent tool's `model` parameter

3. **Dispatch in parallel**: Launch multiple child agents using Claude Code's Agent tool, each with the same task but different model or perspective:
   ```
   Agent(model: "opus", prompt: "<task>")
   Agent(model: "sonnet", prompt: "<task>")
   ```
   Launch all agents in a single message for true parallel execution.

4. **Collect results**: Gather outputs from all child agents.

5. **Consensus pass**: Merge results using the chosen `strategy`:
   - **merge** (default): Combine unique insights, deduplicate, resolve conflicts
   - **vote**: Majority wins on each point, minority views noted
   - **best-of**: Score each result holistically, select the best, supplement with unique insights from others

6. **Preserve minority views**: When they materially affect correctness or risk.

## Output

Return:

- model-by-model status (model, result summary)
- merged result (the consensus output)
- disagreements that need human judgment (with context from each model)
- confidence assessment (higher when models agree, lower when they diverge)
