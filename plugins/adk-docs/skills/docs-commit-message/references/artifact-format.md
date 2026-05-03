# `docs-commit-message` — artifact format

```
.temp/task-<slug>/
├── prompt.txt                  # verbatim user prompt + timestamp
├── diffstat.txt                # git diff --cached --stat
├── staged.diff                 # git diff --cached
├── recent-subjects.txt         # git log -10 --format=%s
├── detected-style.txt          # conv | semantic | free + rationale
├── commit-msg.txt              # the final commit message
├── hook-rejection.txt          # (only if --fix and hook rejected)
├── validation/
│   └── docs-commit-message.md  # per-phase validator log
└── report.md                   # final consolidated report
```

## Slug rules

1. `commit-<YYYYMMDD>-<first-6-of-sha1-of-staged-diff>`. Deterministic
   across re-runs on the same staged diff — lets the user re-invoke
   without creating a new task folder.
2. If the staged diff changes between runs, the slug changes, which
   is the intended signal.

## Rules

1. Never write outside `.temp/task-<slug>/` or `.git/` (and `.git/`
   is only written by `git commit` under `--fix`).
2. `staged.diff` is potentially large — keep it in the task folder,
   not inlined into the final report.
3. The `commit-msg.txt` line endings are `\n`, not `\r\n`.
   `git commit --file` expects `\n`.
4. The `commit-msg.txt` final line has a trailing newline (per POSIX
   text-file conventions). The validator checks.

## Staging-drift detection

Before Phase 4 runs `git commit`, re-compute
`git diff --cached | sha1sum` and compare with the slug's hash prefix.
If they don't match:

1. The user staged more (or unstaged some) since Phase 1.
2. The skill refuses to commit.
3. Offers to re-run Phase 1 with the current staged set.

## `detected-style.txt` format

```
style: conventional
confidence: 0.8
matches: 8 of 10
override: none
rationale: |
  8 of the last 10 subjects match /^(feat|fix|chore|...)(\(...\))?:/.
  Example matches:
    - feat(checkout): add ExportService
    - fix(ui): guard missing order id
  Example non-matches:
    - Merge pull request #2840 from alice/...
    - [hotfix] revert auth migration
```
