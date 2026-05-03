# `review-code-changes` — baseline detection

The exact algorithm for picking the baseline branch / ref for the diff. The choice + source is surfaced in the status banner so the user can catch a wrong pick.

## Why this matters

The diff is `git diff <baseline>...HEAD` (3-dot for the merge-base diff). Wrong baseline → wrong diff → wrong findings. Common ways to get it wrong:

- Branch's `@{upstream}` set to a stale `origin/old-feature` that's been rebased away.
- Local `main` not synced; the diff includes commits that are already on `origin/main`.
- Branch name doesn't match any remote (just-created local-only branch).
- Detached HEAD.

The detection algorithm is documented + ordered, and the skill always surfaces the source so the user can override.

## Algorithm

```python
def detect_baseline(arg=None) -> tuple[str, str]:
    """
    Returns (baseline_ref, source) where source is one of:
      arg, tracking, remote, main, master, first-parent.
    """

    # 0. explicit arg wins
    if arg:
        if not git.rev_parse_verify(arg):
            stop(f"baseline arg '{arg}' does not resolve")
        return (arg, "arg")

    branch = git.current_branch()
    if branch == "HEAD":
        # detached HEAD
        return (git.first_parent_of("HEAD"), "first-parent")

    # 1. tracking branch
    upstream = git.try_rev_parse("@{upstream}")
    if upstream:
        return (upstream, "tracking")

    # 2. origin/<branch>
    origin_branch = f"origin/{branch}"
    if git.rev_parse_verify(origin_branch):
        return (origin_branch, "remote")

    # 3. main
    if git.rev_parse_verify("main"):
        return ("main", "main")

    # 4. master
    if git.rev_parse_verify("master"):
        return ("master", "master")

    # 5. fallback: first-parent of HEAD~1 (only under --auto)
    if mode_is_auto:
        return (git.first_parent_of("HEAD"), "first-parent")
    else:
        ask_user("no upstream / origin / main / master found; pick a baseline")
```

## Source semantics

| Source | Meaning | Reliability |
| --- | --- | --- |
| `arg` | User explicitly named the baseline. | High (user's responsibility). |
| `tracking` | `git config branch.<branch>.merge` is set. | High when the upstream is a sibling of the branch (the typical PR setup). Low if the upstream is stale or wrong. |
| `remote` | Local `origin/<branch>` exists. | Medium-high. The local cache might be out of date — `git fetch origin <branch>` first if accuracy matters. |
| `main` | The repo's `main` branch exists locally. | High for trunk-based repos. The diff is the entire branch's worth of changes. |
| `master` | Same as `main` for older repos. | Same as `main`. |
| `first-parent` | Fallback; the previous commit on the current branch. | Low — it reviews only the latest commit's worth of changes; misses older commits on the same branch. |

## When the skill warns

- **Source = `first-parent`.** Surface "WARNING: no upstream / origin / main / master found; using HEAD~1. The review covers only your last commit. Consider passing an explicit `<base-branch>`."
- **Source = `tracking`** AND `git fetch <upstream>` shows the upstream has diverged (commits on the upstream that aren't in the local). Surface "Local upstream is behind; the diff may not reflect the actual PR diff. Run `git fetch && git rebase origin/<upstream>` first?"
- **Source = `remote`** AND `git fetch origin <branch>` shows newer commits on `origin/<branch>`. Surface "`origin/<branch>` is behind your local; the diff is correct, but the user should fetch before pushing to know whether they need to rebase."
- **Source = `main` / `master`** AND the branch has many commits ahead of `main`. Surface "Reviewing <N> commits worth of changes; this may be a longer review than expected. Consider `--scope <subdir>` to focus."

## When the user should override

| Situation | Recommended baseline |
| --- | --- |
| You're reviewing your local WIP before pushing | (default detection — usually right) |
| You want to see "everything that's changed in this branch since it diverged from main" | `<base-branch>` = `main` (or `origin/main`) |
| You want to see "what's changed since my colleague's review" | `<base-branch>` = `<reviewed-sha>` (use the SHA from the prior review) |
| You're reviewing a stacked PR and only want the top-of-stack diff | `<base-branch>` = the parent stack PR's head |
| You want to see what's new since the last release | `<base-branch>` = the last release tag (e.g. `v1.2.3`) |
| You want to compare against the merge-base only | `<base-branch>` = `$(git merge-base HEAD main)` |

## Implementation note

The `git diff <baseline>...HEAD` form (3-dot) computes the diff from the merge-base of `baseline` and `HEAD`. This is what the user usually wants — it shows "what's new on this branch", not "what's different between the two refs".

The 2-dot form (`git diff <baseline>..HEAD`) shows raw differences, which can include commits that are on `baseline` but not in `HEAD` (as deletions), making the diff confusing. **Always use 3-dot for this skill.**

```bash
git diff <baseline>...HEAD --name-status   # for the file list
git diff <baseline>...HEAD                 # for the full diff
```

## Output

The chosen baseline + source is recorded in three places:

1. **Status banner.** `baseline=<ref>(<source>)`.
2. **`prompt.txt`.** Written in Phase 0.
3. **`scope.md`.** Written in Phase 2 with the resolved baseline SHA.
4. **`report.md`.** Surfaced in the "Repo snapshot" section.

The user can verify at any time and re-run with `<base-branch>` arg to override.
