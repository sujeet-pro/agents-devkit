# adk-implement — hard rules + refusals

## Hard rules (extend `shared/constitution.md` §V)

1. **Read every file before writing it.**
2. Smallest correct change. No drive-by cleanup. No opportunistic refactor.
3. Tests for new behavior — happy + ≥1 boundary + ≥1 error per behavior.
4. No commits to `main` / `master` / `release/*` / `prod/*` (or any pattern in `overrides.yaml.protected_branches`).
5. Branch name derived from task-slug; never on the user's checked-out branch if that branch is protected.
6. Never force-push. Never `git reset --hard`. Never `--no-verify`.
7. Never merge a PR. Open it; let the human click merge.
8. Edit-format is SEARCH/REPLACE blocks (`shared/edit-format.md`). Whole-file rewrites are forbidden unless the file is being created.
9. New dependencies require user confirmation (size + maintenance + license summary).

## Refusals

- Repo is not a git repo → ask user to `git init` or specify the right cwd.
- Input is a URL the classifier doesn't recognize → ask for a hint or use `/adk-explain`.
- No clarification answered within 3 rounds → hand off to `/adk-explain`.
- Validators fail after exhausting `--auto` retries (default 2) → stop and report; don't paper over.
- Diff > 2000 LOC requested in a single PR → recommend `pr-strategy: split-by-area`.
- Required MCP unreachable (e.g., adk-mcp-github when the task needs a PR) → stop in Phase 1 with named gap.
