# `prompt-expand` — anti-patterns

- **Re-writing the prompt instead of quoting it verbatim.** The verbatim quote is the contract — without it, the user can't tell whether you understood them.
- **Inventing an entity that doesn't appear in meta-info.** Mark it `inferred`, never `verified`.
- **Recommending a skill that doesn't exist.** The catalog is fixed; check `auto/references/dispatch-matrix.md` before recommending.
- **Skipping `Alternatives considered`.** "There's only one way" is rarely true.
- **Skipping `Missing inputs`.** Even `(None)` is a valid value — it tells the user the chain is ready to dispatch.
- **Calling any other skill or MCP from this skill.** It's read-only on local files. If you need MCP data, recommend the skill that uses it; don't fetch it yourself.
- **Modifying any meta-info file.** Read-only on `~/.config/adk/*.md`.
- **Producing the plan in prose form when the structured output is required.** The downstream consumer (often `auto`) parses the table format.
