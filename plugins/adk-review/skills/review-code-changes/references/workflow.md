# `review-code-changes` — workflow detail

Detailed phase-by-phase stage list. Every checkpoint logs to `.temp/task-<slug>/validation/per-skill/review-code-changes.md`.

## Phase 0 — prompt expand

1. **Resolve repo.** Walk up from CWD to a `.git` directory. Stop with "not a git repo" if none found.
2. **Resolve baseline** per `references/baseline-detection.md`:
   - If `<base-branch>` arg passed → use it (source: `arg`).
   - Else: `git rev-parse --abbrev-ref @{upstream}` (source: `tracking`).
   - Else: `git rev-parse --verify origin/<current-branch>` (source: `remote`).
   - Else: `git rev-parse --verify main` (source: `main`).
   - Else: `git rev-parse --verify master` (source: `master`).
   - Else (`--auto` fallback): `git rev-list --first-parent --max-count=1 HEAD~1` (source: `first-parent`).
   - Surface the choice + source in the status banner.
3. **Slug.** Derive from the current branch name (`git symbolic-ref --short HEAD`). Kebab-case, max 6 words.
4. **Create `.temp/task-<slug>/`** + write `prompt.txt` (verbatim user prompt + ISO timestamp + repo name + branch + baseline ref + baseline source).
5. **Determine mode.** `--auto` (default), `-i`, `--fix`, or compositions. `--auto -i` invalid → refuse.

## Phase 1 — preflight

1. **Repo state.** `git status --porcelain` → record.
2. **For `--fix`:** working tree must be writeable (no read-only mount). Stop with "working tree not writeable" otherwise.
3. **`bin/adk-info repos --check`** + **`bin/adk-info review --check`** must return 0.
4. **Repo conventions.** Read `AGENTS.md` / `CLAUDE.md` / `.cursorrules` if present; pass to dimension passes as context.
5. **Cheap lint pre-pass (optional).** If the repo has a quick lint command (`npm run lint`, `golangci-lint run --fast`, `ruff check`, `cargo clippy --no-deps`) AND it runs in <30s, run it and capture the output. The findings inform Phase 3 (saves the style pass from raising lint-already-catches-this issues).

## Phase 2 — gather scope

Per `references/scope-collection.md`:

1. **Branch-vs-baseline diff.**

   ```
   git diff <baseline>...HEAD --name-status
   git diff <baseline>...HEAD
   ```

2. **Staged changes.**

   ```
   git diff --cached --name-status
   git diff --cached
   ```

3. **Unstaged changes.**

   ```
   git diff --name-status
   git diff
   ```

4. **Untracked files.**

   ```
   git ls-files --others --exclude-standard
   ```

   For each, read the full file content (it has no diff — the whole file is new).

5. **Build the unified scope list.** A map `file -> {kind, current_content}` where `kind ∈ {branch, staged, unstaged, untracked}`. A file may appear in multiple kinds (e.g. modified + then more changes unstaged); merge into the latest state.

6. **Apply `--scope <path>` filter** if provided.

7. **Write `.temp/task-<slug>/review/scope.md`** with the per-source breakdown and counts.

## Phase 3 — full-scope review

1. **Read each in-scope file in its CURRENT state.** For tracked files: post-diff state from the working tree. For untracked: the full file. Don't read the diff hunks alone.
2. **Spawn dimension passes** in parallel (max 4 — see `agents/dispatcher.md` rule). Each loads `code-reviewer` (or `security-reviewer` for the security pass):

   | Dimension | Skip when |
   | --- | --- |
   | correctness | rename / move / config-only changes |
   | security | scope doesn't touch a boundary, auth, data store, or dependency manifest |
   | performance | non-hot-path / one-shot scripts |
   | tests | scope is test-only or pure refactor with green tests |
   | docs | internal refactor; no public surface change |
   | style | repo's lint config is silent on the rule (see Phase 1 cheap lint pre-pass) |

3. **Each agent emits findings** in the canonical card shape (see `references/severity-bar.md` and the cross-skill `comment-template.md` shape). Findings collected at `.temp/task-<slug>/review/raw-findings.md`.
4. **Apply `~/.config/adk/review.md` overrides** (severity bar + ignore_in_repos).
5. **De-noise** — collapse same-root-cause findings.
6. **Tag each finding with its scope source** (branch / staged / unstaged / untracked). Lets the user prioritize: "1 Critical in unstaged means I shouldn't push yet".

## Phase 4 — propose

1. **Sort by severity** (Blocker → Critical → Should-Have → May-Have → Nitpick → Question).
2. **Write `findings.md`** at `.temp/task-<slug>/review/findings.md`.
3. **Mode branch:**
   - `-i`: walk each finding. For each, ask `accept | edit | discard`.
   - `--auto`: keep all validated findings.
4. **Approval gate** (unless `--auto`): show counts + top issue, ask "show full report?".

## Phase 5 — report or fix

### Phase 5a — review-only

1. **Surface** to the user: severity counts + top issue + per-source breakdown.
2. **Suggest next step:**
   - 0 Blockers + 0 Criticals → "ready to push" or "ready to open PR".
   - Blockers / Criticals present → "fix before push; run with `--fix` or address manually".

### Phase 5b — `--fix` mode only

1. **Build the fix queue.** Accepted findings, severity-prioritized.
2. **Apply each fix.** For trivial edits (style, nits, simple bug fixes), do it inline. For non-trivial fixes (refactor, test addition), delegate to `/adk-code:code-bugfix` (passes the finding card as the brief).
3. **Validate after each (or once at end if scope is small):**
   - Use `repos[<name>].notes` build/test command if listed.
   - Else common defaults: `npm test` / `go test ./...` / `pytest` / `cargo test`.
   - Plus typecheck (`tsc --noEmit`, `mypy`, etc.) and lint.
4. **Capture per-fix evidence** in `fix-log.md`: file changed, command run, exit code, stdout summary.
5. **STOP HERE.** Do NOT push. Do NOT open a PR. Do NOT call `gh pr`
   anything. Surface "fixes applied; ready for explicit `git push` / PR
   follow-up when the user asks".

## Phase 6 — final report

1. **Write `report.md`** per `references/output-format.md`.
2. **Surface to user** the executive summary.
3. **Offer depth** — "Need more detail on any finding?" — never dump long context unprompted.

## Loop control

- **Lint pre-pass repeatedly fails the same issue.** Surface and continue; the style dimension can pick it up.
- **Working tree changed mid-review.** If the user edits files between Phase 2 and Phase 3, the findings might be stale by the time they're reported. Detect via mtime check; surface "working tree changed during review; re-run for accuracy".
- **`--fix` validation fails after applying a fix.** Stop applying further fixes from the queue. Surface the failure. Don't try to "fix the fix" — that's a `/adk-code:code-bugfix` invocation, not this skill.
- **More than 4 parallel subagents.** Refuse — coordination overhead grows past 4.

## Key differences from `review-pr`

| Concern | `review-pr` | `review-code-changes` |
| --- | --- | --- |
| Source of diff | Remote PR (gh / MCP) | Local git (committed + staged + unstaged + untracked) |
| Baseline | PR's base branch | auto-detected (tracking → origin/branch → main → master → first-parent) |
| Untracked files | N/A (PR has only tracked files) | First-class; full-file read |
| Comment posting | Phase 6a (post + post-confirmation) | None — never posts |
| Reconciliation | Walks existing PR comments | None — there's no remote yet |
| Push | `--fix` pushes (gated) | `--fix` does NOT push (intentional) |
| Ownership detection | author.login vs local identity | N/A — always own work |
| Worktree isolation | yes (`.temp/.../review-checkout/`) | no — works on the actual working tree |
