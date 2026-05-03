# `review-handoff` — git state capture

The exact git commands run in Phase 2 + how the captured state is filtered / anonymized for the handoff.

## Commands run (in order)

```bash
# Branch
git symbolic-ref --short HEAD 2>/dev/null || echo "(detached HEAD: $(git rev-parse --short HEAD))"

# Status (paths only, no content)
git status --porcelain

# Recent commits (configurable count; default 10)
git log --oneline -<commits>

# Uncommitted change stat
git diff --stat
git diff --cached --stat   # (staged-stat too)

# Full uncommitted diff (truncated for the doc)
git diff
git diff --cached

# Stash
git stash list

# Remote URLs (anonymized)
git remote -v

# Upstream
git rev-parse @{upstream} 2>/dev/null

# Open PR for the current branch (if any)
gh pr view --json number,url,state,title 2>/dev/null
```

## Anonymization rules

### Remote URLs

```bash
# Raw output:
# origin  https://oauth2:gho_xxxxxxxxxxxxxxxxxxxxxxx@github.com/acme/checkout-api.git (fetch)
# origin  https://oauth2:gho_xxxxxxxxxxxxxxxxxxxxxxx@github.com/acme/checkout-api.git (push)

# Anonymized (token stripped):
# origin  https://github.com/acme/checkout-api.git (fetch)
# origin  https://github.com/acme/checkout-api.git (push)
```

Strip any `:<token>@` segment from HTTPS URLs. Keep SSH URLs as-is (they don't carry secrets).

### Uncommitted diff

The full diff can be hundreds of lines. The handoff truncates per these rules:

```
if total_diff_lines == 0:
    output = "(no uncommitted changes)"
elif total_diff_lines <= 200:
    output = full_diff
elif total_diff_lines <= 500:
    output = first_200_lines + "\n... (truncated; full diff available via `git diff` from this branch)"
else:
    output = "(diff is " + total_diff_lines + " lines; see `git diff` from this branch for the full diff)\n" + diff_stat
```

Override with `--no-diff-truncate` (rare — usually surfaces 500+ lines of noise).

### Diff content scrubbing

If the diff contains any line that LOOKS like a secret value (matched against the same regexes as `security-reviewer`'s `secret_in_diff` check — `AKIA[0-9A-Z]{16}`, `ghp_[A-Za-z0-9]{36}`, `sk-[A-Za-z0-9]{40}`, `BEGIN PRIVATE KEY`, etc.), the matching LINE is redacted to `[REDACTED <secret-type> at <file>:<line>]`.

The full secret value is NEVER written to `handoff.md`.

### Author / committer info in `git log`

`git log --oneline` shows only commit + subject. The full author/email is in the commit object but not surfaced in the doc.

If a commit subject contains a secret (rare; e.g. accidentally `git commit -m "added GITHUB_PAT=ghp_..."`), apply the same redaction.

## Stash entries

```bash
git stash list
# stash@{0}: WIP on feature/pricing: temp-debug-print
# stash@{1}: On feature/pricing: half-baked retry logic
```

Surfaced as-is in the handoff (the subjects are usually short + benign). If a stash subject contains a secret, redact.

## Open PR

```bash
gh pr view --json number,url,state,title 2>/dev/null
```

If the current branch has an open PR, surface in the handoff's "Next step" section as:

> Open PR: [#<num> — <title>](<url>) (state: <state>)

If no open PR (branch hasn't been pushed, or push didn't trigger a PR-create), surface:

> No open PR for this branch. After push, run `/adk-docs:docs-pr-description --auto` then `gh pr create`.

## Edge cases

### Detached HEAD

```bash
git symbolic-ref --short HEAD 2>/dev/null
# fails with "fatal: ref HEAD is not a symbolic ref"
```

Surface in the handoff:

> Branch: (detached HEAD: `<short-sha>`) — likely from a `git checkout <sha>`. To resume: create a branch with `git checkout -b <new-branch>`.

### Empty repo

```bash
git log --oneline
# fails: "fatal: your current branch '<branch>' does not have any commits yet"
```

Surface:

> No commits yet on this branch. (Working tree is the only state.)

### Branch with no upstream

```bash
git rev-parse @{upstream} 2>/dev/null
# (silent fail)
```

Surface in "Git state":

> Upstream: (none) — branch is local-only. After push, set with `git push -u origin <branch>`.

### Conflict mid-merge / rebase

```bash
git status --porcelain
# UU src/foo.ts
# UU src/bar.ts
```

Surface as a Blocker:

> | Blocker | Owner | ETA | Workaround |
> | --- | --- | --- | --- |
> | merge conflict in 2 files (src/foo.ts, src/bar.ts) | self | unknown | `git merge --abort` to back out, OR resolve manually |

### `git fsck` warnings

Not run by default (slow; not relevant to handoff). Surface only if the user explicitly asks.

## What's intentionally NOT captured

- **Reflog.** Not in scope for handoff; the reader can `git reflog` if they need it.
- **All branch refs.** Just the current branch.
- **All remotes' tracking state.** Just `origin`.
- **GPG signing status.** Not relevant.
- **`.git/config` contents.** Sensitive (may contain credentials).
- **Hooks installed.** Not relevant unless the user explicitly asks.

## Output shape (in `handoff.md` Section 8)

```markdown
## 8. Git state

- Branch: `feature/pricing-rework`
- Dirty: yes (3 files: `src/billing/tier.test.ts`, `CHANGELOG.md`, `docs/api.md`)
- Last 10 commits:
  - d4e5f6g unit tests for Tier (8/9 cases)
  - c3d4e5f add POST /v1/customers/<id>/tier
  - b2c3d4e Tier and TierResolver
  - a1b2c3d migration: add customer_tier table
  - 9f8e7d6 (older, on main) ...
  - ... (5 more)
- Uncommitted diff: +124/-12 across 3 files

```diff
diff --git a/src/billing/tier.test.ts b/src/billing/tier.test.ts
index 1234567..abcdefg 100644
--- a/src/billing/tier.test.ts
+++ b/src/billing/tier.test.ts
@@ -119,6 +119,30 @@ describe("Tier", () => {
+  it("transitions free -> pro -> enterprise", () => {
+    // ...
+  });
... (truncated; full diff available via `git diff` from this branch)
```

- Stash: 1 entry
  - `stash@{0}: WIP on feature/pricing: experiment with cache TTL`
- Remote: `origin  https://github.com/acme/storefront.git`
- Upstream: `origin/feature/pricing-rework`
- Open PR: [#103 — feat: tiered pricing for B2B](https://github.com/acme/storefront/pull/103) (state: OPEN)
```

## Privacy guarantee

The skill commits to:

1. NEVER write a token / secret / API key value into `handoff.md` or `handoff-postback.md`.
2. NEVER write a customer name / PII from logs.
3. NEVER quote the contents of `.env` / `.envrc` / `secrets.yml` etc. — only file existence + path.

Violation → bug; surface to user with a redacted re-write.
