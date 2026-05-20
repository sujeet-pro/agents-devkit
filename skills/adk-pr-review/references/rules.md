# rules — adk-pr-review hard rules + refusals

## Must do

1. **Always isolated.** Operate from `~/.agents-devkit/pr-reviews/<repo>_pr-<n>/`. Never read or write the user's working repo. (Constitution §IV.1, `shared/paths.md`.)
2. **Serialize worktree creation.** `scripts/create_worktree.py` acquires `~/.agents-devkit/repos/.worktree-lock` before `git worktree add` and releases it after. No concurrent worktree adds against the same clone.
3. **Reset the clone before worktree.** Before adding a worktree, ensure `~/.agents-devkit/repos/<repo>/` is on its default branch at the remote HEAD with no local changes. Refuse if there are unexpected local commits.
4. **Read every existing comment before flagging.** Per the persona's anti-pattern — don't re-raise pushed-back items.
5. **Cite evidence by `path:line`.** Every finding has at least one `evidence[]` entry with a verifiable ref.
6. **Quote ≤ 15 words verbatim** from any source (PR body, comment, doc, code) per constitution §II.1.
7. **State confidence on every claim** (`low / med / high`). High = code read. Med = reasoned. Low = pattern-match.
8. **Honor the schema.** Output strictly matches `finding.template.json`. Invalid findings are dropped, not patched.
9. **Classify every existing comment thread.** Every thread MUST appear in `existing_comment_actions[]`. Threads the AI omits are auto-classified by `comment_resolver.py` (flagged with `auto_classified: true`) — but explicit beats implicit. See `references/comment-resolution.md`.
10. **Prefer MCP for writes.** `post_comments.py` emits `posting-plan.json` listing each step as an `mcp__adk-mcp-{github,bitbucket}__*` tool + args. The host agent dispatches; direct API is only the headless fallback. See `references/platform-mcp.md`.
11. **Approve when mergeable.** Set `recommendation: "approve"` when there are zero blocker/critical findings AND no thread requires `reopen`. The post step queues an approve action (GitHub: bundled in the review's APPROVE event; Bitbucket: separate `approvePullRequest` call).

## Must not

1. **Never edit the worktree.** `code/` is read-only to the review session. No `Edit`, no `Write`, no `Bash` that mutates files under `code/`.
2. **Never post without confirmation.** Constitution §I.4. The orchestrator gates posting; you don't propose to bypass.
3. **Never resolve a comment whose decision you can't justify with quoted evidence.** "Looks fine" is not a justification. See `references/comment-resolution.md`.
4. **Never modify a Statsig gate / experiment / dynamic config / segment.** Read-only. Constitution §I.5.
5. **Never run DDL / DML / GRANT.** Constitution §I.6.
6. **Never invent files / symbols / flags.** If retrieval returns nothing, the finding's confidence drops to `low` and the body says "couldn't verify caller".
7. **Never quote a secret value.** Constitution §VII. If the diff contains a secret, the finding cites the line range without the value.
8. **Never merge the PR.** Approving (when applicable) is the skill's last act. `posting-plan.json.never_merge` is always `true`. The MCP `merge_pull_request` / `mergePullRequest` tools are forbidden from any plan the skill emits. If the user explicitly asks for a merge, refuse and tell them to click merge themselves.

## Refusals (Phase 0 stops; the rest don't run)

| Condition | Refusal text |
|---|---|
| URL host is not github.com / bitbucket.org | "Only GitHub and Bitbucket Cloud are supported. Got `<host>`. Constitution §VI.1." |
| ollama not on PATH | "ollama binary not found. Install: `brew install ollama` (macOS). Refusing to fall back to a non-local embedder." |
| ollama daemon not responding at :11434 | "ollama daemon not running. Start: `ollama serve &`. Then re-run." |
| Embedding model not pulled | "Model `<name>` not present. Pull: `ollama pull <name>`. Refusing to embed without a verified model." |
| GH PR + `gh` CLI missing + no adk-mcp-github | "GitHub PR but neither `gh` CLI nor `adk-mcp-github` reachable. Install gh or enable the MCP." |
| BB PR + adk-mcp-bitbucket missing | "Bitbucket PR but `adk-mcp-bitbucket` not reachable. Wire it via `install.sh` or run `/adk-setup --check`." |
| Diff > 5000 LOC + no `--scope` flag | "Diff is `<n>` LOC. Refusing single-pass. Pass `--scope security` or `--scope correctness` to narrow." |
| `~/.agents-devkit/repos/<repo>/` has uncommitted changes | "adk-owned clone has local changes — unexpected. Inspect or delete the folder, then re-run." |
| Worktree lock held > 5 min by another process | "Worktree lock held by pid `<n>` since `<ts>`. Inspect — likely a stuck prior run." |

## Degradations (allowed; surfaced)

- **SCIP binary missing for some languages** → mark `not_installed` in `code-index/meta.json`; review uses chunker-only symbol view; surface in `report.md`.
- **adk-mcp-statsig unreachable** → feature-flow tracing falls back to repo grep only; flag findings are `low` confidence; surfaced.
- **adk-mcp-atlassian unreachable** → supporting docs from Confluence / Jira skipped; mark `[confluence: skipped]` / `[jira: skipped]` in the report.
- **GH GraphQL `resolveReviewThread` unavailable for this token** → fall back to a status comment on the thread; flagged in the report.
