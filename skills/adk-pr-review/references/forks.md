# forks — adk-pr-review

Canonical fork IDs the skill emits to `$ADK_DATA_HOME/improve/learning/decisions.jsonl`. `/adk-improve` reads these to propose default updates.

| fork_id | options | default | trained by |
|---|---|---|---|
| `severity-bar` | `blocker` / `critical` / `should-have` / `may-have` / `nitpick` | `should-have` | repeat user picks per repo |
| `dimensions` | csv of: `correctness,security,performance,tests,docs,api,observability,concurrency,feature-flow,style,pre-merge-sanity` | all except `style` | per-repo skip patterns |
| `scope` | `security` / `correctness` / `tests` / `all` | `all` (until diff > 5000 LOC) | scale guards |
| `post-policy` | `confirm-each` / `confirm-batch` / `no-post` | `confirm-batch` | per-user-per-repo |
| `resolve-policy` | `strict-evidence` / `lenient-offline-aligned` / `manual-only` | `strict-evidence` | per-user, rarely loosened |
| `embed-model` | `nomic-embed-text` / `granite-embedding:278m` / `mxbai-embed-large` / `<other>` | `nomic-embed-text` | rarely changes; per-host |
| `rebuild-on-rerun` | `resume` / `rebuild` | `resume` | situational |

## When the skill records these

- Phase 0: `embed-model` is `inferred` if pulled from overrides; `user-answered` only on `--embed-model <name>`.
- Phase 1 (advise): the orchestrator asks up to 3 questions: scope, post-policy, resolve-policy. Each answer logs one line.
- Phase 4: `severity-bar` is `inferred` from the user's prior PR-review decisions in this repo; if no history, `should-have` is the default.
- Phase 5: the post-confirmation isn't a fork — it's a constitution §I.4 gate; not logged here.

## Reading the log

```bash
jq -c 'select(.skill == "adk-pr-review")' $ADK_DATA_HOME/improve/learning/decisions.jsonl
```

## What does NOT get logged

- Per-finding decisions (the model decides; no user fork).
- Comment-resolver classifications (resolve / reopen / leave) — internal to the run, not a user-trainable signal.
- Embedding-store internals (chunk count, vector dim).
