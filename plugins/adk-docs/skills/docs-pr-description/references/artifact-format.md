# `docs-pr-description` — artifact format

```
.temp/task-<slug>/
├── prompt.txt                  # verbatim user prompt + timestamp
├── commits.txt                 # git log output (ASCII-unit-separated)
├── diffstat.txt                # git diff --stat output
├── tests.diff                  # diff scoped to test files
├── template.md                 # .github/pull_request_template.md (if present)
├── pr-title.txt                # 1-line title (≤70 chars)
├── pr-body.md                  # final PR body (what `gh pr edit` consumes)
├── validation/
│   └── docs-pr-description.md  # per-phase validator log
└── report.md                   # final consolidated report
```

## Slug rules

1. `pr-<branch-basename>` when no PR exists yet.
2. `pr-<number>` when a PR already exists for the branch (reuse
   across re-runs).
3. Branch-basename kebab-cased, stripped of leading `feat/` / `fix/`
   / etc. — (so `feat/chk-1238-clamp-qty` → `chk-1238-clamp-qty`).

## Rules

1. Never write outside `.temp/task-<slug>/` before the validator
   passes.
2. Never modify `pr-body.md` after the `--fix` remote write succeeds
   — keep the in-flight version pristine for audit.
3. Back up the existing PR body (fetched via `gh pr view --json body`)
   to `.temp/task-<slug>/backup/pr-body.md` before overwriting.
4. Never include environment secrets (API keys, tokens) in
   `pr-body.md`. The validator greps for obvious patterns and
   blocks.

## `commits.txt` format

Produced with:

```
git log <base>..HEAD --pretty=format:%H%x1f%an%x1f%ae%x1f%s%x1f%b%x1e
```

Each record is separated by ASCII `0x1e`; fields by `0x1f`. Fields:
`sha`, `author-name`, `author-email`, `subject`, `body`. Tooling in
the skill parses this deterministically.

## PR-template layering

If `.github/pull_request_template.md` exists, it drives section
order. See `references/pr-template-loader.md` for the rules.

## No-pr-yet flow

If no PR exists for the current branch, the skill still produces
`pr-body.md`. The user then runs `gh pr create --body-file
pr-body.md --title "$(cat pr-title.txt)"` — the skill does **not**
run `gh pr create` (that opens a shared-state artifact and is out
of scope; use `/adk-review:review-code-changes --fix` or raise the
PR manually).
