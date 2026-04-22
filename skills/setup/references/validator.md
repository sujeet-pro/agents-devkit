# `setup` — validator

## Phase 1 — pre-execution
- [ ] Platform is macOS.
- [ ] User has shell access (we run via `claude`'s Bash tool).

## Phase 2 — mid-flow (after each install)
- [ ] `command -v <tool>` returns a path.
- [ ] `<tool> --version` exits 0.

## Phase 3 — pre-handoff (before final report)
- [ ] Every required tool is present.
- [ ] `bin/adk-doctor` ran and produced output.

## Phase 4 — post-execution
- [ ] No write to `~/.zshenv` happened.
- [ ] All MCP servers the user accepted are installed (`claude mcp ls` shows them).
- [ ] Final report exists at `.temp/reports/setup-<timestamp>.md`.
