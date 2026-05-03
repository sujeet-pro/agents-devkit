# `review-code-changes` — scope collection

How the four scope sources (branch / staged / unstaged / untracked) are gathered into one unified scope map. The output is `scope.md` plus an in-memory map that drives Phase 3.

## The four sources

| Source | Command | Means |
| --- | --- | --- |
| **branch** | `git diff <baseline>...HEAD` | Committed work since the branch diverged from the baseline. |
| **staged** | `git diff --cached` | Staged-but-not-committed changes (`git add` but no `git commit`). |
| **unstaged** | `git diff` | Tracked-file edits in the working tree, not yet `git add`-ed. |
| **untracked** | `git ls-files --others --exclude-standard` | New files not yet `git add`-ed. |

A given file may appear in multiple sources at the same time (e.g. modified + staged + then more changes unstaged). The scope map merges these into a single per-file entry.

## Algorithm

```python
def gather_scope(baseline: str, scope_path: str | None = None,
                 include_untracked: bool = True,
                 include_deleted: bool = False) -> dict[str, ScopeEntry]:

    scope: dict[str, ScopeEntry] = {}

    # 1. branch (committed work since divergence)
    for line in git("diff", f"{baseline}...HEAD", "--name-status").splitlines():
        status, path = parse(line)
        if status == "D" and not include_deleted:
            continue
        scope[path] = ScopeEntry(file=path, sources=["branch"], status=status,
                                 current_content=read_working_tree(path))

    # 2. staged
    for line in git("diff", "--cached", "--name-status").splitlines():
        status, path = parse(line)
        if status == "D" and not include_deleted:
            continue
        scope.setdefault(path, ScopeEntry(file=path, sources=[], status=status,
                                           current_content=read_working_tree(path)))
        scope[path].sources.append("staged")

    # 3. unstaged (tracked edits)
    for line in git("diff", "--name-status").splitlines():
        status, path = parse(line)
        if status == "D" and not include_deleted:
            continue
        scope.setdefault(path, ScopeEntry(file=path, sources=[], status=status,
                                           current_content=read_working_tree(path)))
        scope[path].sources.append("unstaged")

    # 4. untracked
    if include_untracked:
        for path in git("ls-files", "--others", "--exclude-standard").splitlines():
            scope.setdefault(path, ScopeEntry(file=path, sources=[], status="A",
                                               current_content=read_full(path)))
            scope[path].sources.append("untracked")

    # 5. apply --scope filter
    if scope_path:
        scope = {p: e for p, e in scope.items() if p.startswith(scope_path.rstrip("/") + "/")}

    return scope
```

## Per-file content reading rules

| Source | Read strategy |
| --- | --- |
| branch (M / R) | Read full file from working tree (post-diff). The diff hunks alone miss helper functions called by changed code. |
| branch (A) | Read full file from working tree. |
| branch (D) | (skipped unless `--include-deleted`) Read from `git show <baseline>:<path>` for context. |
| staged | Read full file from working tree (the staged change is in the index, but the working tree often agrees; the dimension passes review the latest state). |
| unstaged | Read full file from working tree. |
| untracked | Read full file from working tree (it has no diff — the whole file is new). |

**Important:** the dimension passes review the **current** state, not the diff. The diff tells the skill *which* files to look at; the file content tells the agent *what's there now*.

## `ScopeEntry` shape

```typescript
type ScopeEntry = {
  file: string;                            // path relative to repo root
  sources: ("branch" | "staged" | "unstaged" | "untracked")[];
  status: "A" | "M" | "D" | "R" | "C";     // git's diff-status code
  current_content: string;                 // full file content from working tree
  mtime_t0: number;                        // mtime at end of Phase 2 (for change-during-review detection)
  size: number;                            // size of current_content in bytes
}
```

## `--scope <path>` filter semantics

- The path is a prefix matched against the scope-relative file path.
- Trailing `/` is normalized off; `src/auth` and `src/auth/` are equivalent.
- The filter is applied AFTER the four sources are gathered (so the user can see in `scope.md` what they're excluding).
- A file outside the `--scope` path but in scope (e.g. by source) is **not** removed from `scope.md`; it's listed in `scope.md`'s `Excluded` section with reason `outside --scope <path>`.

## `--no-untracked` semantics

- Untracked files are not gathered.
- Surfaced in `scope.md`'s decisions: `--no-untracked: true (untracked files excluded; <n> untracked files NOT in scope)`.
- The user typically uses this when they want a "tracked-only" review (e.g. before a `git commit -a` that wouldn't include untracked).

## `--include-deleted` semantics

- Deleted files (status = `D`) are included.
- For each, the previous content is read via `git show <baseline>:<path>` (or `git show :<path>` for staged deletions).
- Used rarely — for sanity-checking that the deletion was intentional.

## Per-source counts in `scope.md`

```markdown
## Per-source counts
| Source | File count | Lines added | Lines deleted |
| --- | --- | --- | --- |
| branch (committed vs baseline) | 14 | +1240 | -180 |
| staged | 3 | +12 | -4 |
| unstaged | 7 | +84 | -22 |
| untracked | 2 | +120 (new files) | n/a |

## Files in scope
| File | Sources | Status | Size |
| --- | --- | --- | --- |
| src/pricing/calc.ts | unstaged | M | 2.3 KB |
| src/pricing/calc.test.ts | unstaged | M | 1.1 KB |
| src/pricing/types.ts | untracked | A | 1.8 KB |
| ... |
```

## What's NOT in scope

- **Files outside the working tree.** The skill is single-repo; no submodule traversal by default.
- **`.git/` internals.** Ignored.
- **`.temp/` and other gitignored paths.** Ignored.
- **Submodules** that are themselves changed (the submodule's diff is opaque from the parent repo). Listed in `scope.md`'s `Excluded` with reason `submodule (review separately)`.
- **Lockfiles** (`package-lock.json`, `go.sum`, `Cargo.lock`, etc.) — included but the dimension passes downweight them (they're auto-generated; reviewing them as if they were hand-written is noise).

## Scope size warnings

| File count in scope | Warning |
| --- | --- |
| < 50 | (none — fast review) |
| 50-200 | "scope is large; consider `--scope <subdir>` to focus" |
| > 200 | "scope exceeds 200 files; recommend `--scope` filter; review otherwise will be shallow due to context budget" |

## Mid-review change detection

After Phase 3, the skill compares each in-scope file's mtime against `mtime_t0`. If any file changed during the review, those findings are annotated as potentially stale (see `validator.md` and `examples.md` Example 6). The change-detection is informational; it doesn't block the report.
