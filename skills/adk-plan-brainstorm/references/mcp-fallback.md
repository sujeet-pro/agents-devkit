# MCP fallback: brainstorming

If the `brainstorming` MCP server is configured, prefer it as the structured session store. It tracks current state / target state / options / confidence and routes the handoff cleanly.

## When the server is missing
Print this warning once, then run the same workflow manually:

> Warning: brainstorming MCP server not configured. Continuing with the fallback workflow. Install it for structured state, stronger iteration support, and cleaner handoff between design and implementation.

The workflow itself does not change. All required inputs and stop conditions still apply.

## Install pointer
Clone https://github.com/sujeet-pro/mcp-brainstorming and point `BRAINSTORMING_MCP_ROOT` at the absolute path. Then re-run `adk-install` and pick `brainstorming` in the MCP step.
