# `review-code-changes` — dimension passes

Same six passes as `review-pr`. The full per-dimension checklists live at `/adk-review:review-pr` `references/dimension-passes.md` (canonical). This file documents the self-review-specific differences.

## Same six dimensions

| Dimension | Agent | Skip when |
| --- | --- | --- |
| correctness | `code-reviewer` | rename / move / config-only changes |
| security | `security-reviewer` | scope doesn't touch a boundary, auth, data store, or dependency manifest |
| performance | `code-reviewer` | non-hot-path / one-shot scripts |
| tests | `code-reviewer` | scope is test-only or pure refactor with green tests |
| docs | `code-reviewer` | internal refactor; no public surface change |
| style | `code-reviewer` | repo's lint config is silent on the rule (cheap lint pre-pass at Phase 1 informs this) |

## Differences from `review-pr`

### 1. Source content, not source diff

In `review-pr`, the agent reads the diff plus the post-diff file. In `review-code-changes`, the agent reads the **current working-tree state** — there's no canonical "diff" to read because three of the four scope sources are open work.

Per-source mapping:

| Scope source | What the agent reads |
| --- | --- |
| branch | Current working tree (post-commit state) |
| staged | Current working tree (the staged change is in the index, but the working tree usually agrees; review the latest state) |
| unstaged | Current working tree (the latest edit) |
| untracked | Current working tree (the whole file is new) |

For files that appear in multiple sources (e.g. modified + then more changes unstaged), the agent reads the latest state.

### 2. Cheap lint pre-pass at Phase 1

`review-code-changes` runs a cheap lint pre-pass at Phase 1 if the repo has a fast lint command (<30s):

- `npm run lint` / `eslint --quiet`
- `golangci-lint run --fast`
- `ruff check`
- `cargo clippy --no-deps`
- `pnpm lint`

The output is captured to `lint-output.txt`. The style dimension reads this file and avoids re-raising lint-already-catches-this issues. This makes the style pass much quieter.

If the repo has no quick lint command (or none that runs in <30s), the pre-pass is skipped and the style dimension proceeds normally.

### 3. Performance dimension uses `~/.config/adk/datadog.md.slo_thresholds` more cautiously

In `review-pr`, observed regressions (DD signals) bump performance findings up a tier. In `review-code-changes`, there's no observed-regression evidence yet (the change isn't deployed). Performance findings stay at their default tier.

If `~/.config/adk/datadog.md` has SLO thresholds for the changed service AND the change touches a hot path, the agent surfaces the SLO as additional context in the `Impact if unfixed:` line — but doesn't auto-bump severity.

### 4. Tests dimension flags untracked test files

Untracked test files are common in self-review (the user wrote a new feature + new tests; they haven't `git add`-ed yet). The tests dimension treats untracked test files as first-class — they count toward "is the new behavior tested?" — but separately surfaces "untracked test file: remember to `git add`" as a `Nitpick`.

### 5. Docs dimension flags untracked CHANGELOG / README updates

If the user added a CHANGELOG entry or README update as untracked, the docs dimension counts it as covered (no finding) but surfaces "untracked doc file: remember to `git add`".

### 6. Security dimension is more aggressive on untracked files

Untracked files are less reviewed (no peer eyes yet) so the security dimension is a bit more aggressive on them — particularly on:

- New `requirements.txt` / `package.json` entries (untracked → never been audited).
- New `.env` / `.envrc` / `secrets.yml`-style files (high risk of secret in diff).
- New shell scripts (high risk of injection / unsafe file operations).
- New CI workflow files (`.github/workflows/`) (high risk of supply-chain footgun).

### 7. Style dimension is more lenient on the user's own naming

The user's own naming choices are usually consistent with the rest of their work, but may diverge from the codebase. The style pass:

- DOES flag divergence vs the file's own conventions.
- DOES flag divergence vs the codebase's CI-enforced rules.
- Does NOT bikeshed the user's personal naming preferences (e.g. `userId` vs `user_id`) unless the file or codebase already picks a convention.

## Per-dimension parallelism

Same as `review-pr` — max 4 parallel subagents at once, with the dispatcher rule.

```
Group 1 (in parallel): correctness, security, performance, tests
Group 2 (after Group 1): docs, style
```

If the user passes `--dimensions security,perf`, only those two run.

## De-noise

Same as `review-pr`:

1. **Same root cause across multiple lines.** Collapse to 1 finding + `references` to the others.
2. **Same dimension flagging the same line.** Pick the highest-severity wording.
3. **Conflicting findings across dimensions.** Surface both, mark as `discuss-with-future-self`.
4. **Lint already covers it (informed by `lint-output.txt`).** The style dimension drops findings whose pattern matches a rule already in the lint output — those will be caught by the user's regular `npm run lint`.
