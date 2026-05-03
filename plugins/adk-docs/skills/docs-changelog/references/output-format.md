# `docs-changelog` — output format

## Per-turn status

```
[adk-docs:docs-changelog] task=<slug> phase=<0|1|2|3|4> style=<kaC|semantic|free> range=<from>..<to> entries=<N> breaking=<M> mode=<auto|fix>
```

## `changelog-entry.md` — shape (Keep a Changelog default)

```markdown
## [<VERSION>] - <YYYY-MM-DD>

### Breaking changes
- <sentence describing the break + migration pointer> ([#<NN>][])
- <sentence> ([#<NN>][])

### Added
- <sentence describing the addition> ([#<NN>][])

### Changed
- <sentence> ([#<NN>][])

### Deprecated
- <sentence> ([#<NN>][])

### Removed
- <sentence> ([#<NN>][])

### Fixed
- <sentence> ([#<NN>][])

### Security
- <sentence> ([#<NN>][])

[#<NN>]: <PR URL>
```

## `changelog-entry.md` — shape (semantic-release variant)

```markdown
## [<VERSION>](<compare URL>) (<YYYY-MM-DD>)

### ⚠ BREAKING CHANGES
* <sentence> ([<sha>](<commit URL>))

### Features
* **<scope>:** <user-readable phrase> ([<sha>](<commit URL>))

### Bug Fixes
* **<scope>:** <user-readable phrase> ([<sha>](<commit URL>))
```

Note: if the existing file uses the `⚠ BREAKING CHANGES` heading
spelling (with warning symbol), match it exactly even if it contains
a non-ASCII character. The skill preserves the existing file's exact
spelling.

## `changelog-entry.md` — shape (free-form)

```markdown
## <Header matching existing pattern> <YYYY-MM-DD>

- <sentence>. (#<NN>)
- <sentence>. (#<NN>)
```

## Insertion point under `--fix`

The new block goes:

1. After the top-of-file preamble (anything before the first `##`).
2. After the "Unreleased" section (if present).
3. Before the most-recent previous version block.

The skill preserves blank lines around the insertion point to avoid
visual drift.

## Final report

`.temp/task-<slug>/report.md`:

```markdown
# docs-changelog report — <slug>

## Result
Generated changelog entry for v1.2.0 covering 12 commits
(v1.1.3..HEAD). Under --fix, inserted into CHANGELOG.md and staged.

## Decisions
| Phase | Question | Picked | Rationale |
| --- | --- | --- | --- |
| 1 | style | keep-a-changelog | file has `### Added` / `### Fixed` headers |
| 2 | breaking changes | 0 | no `!` or BREAKING CHANGE: footers |
| 3 | date | 2026-05-03 | today (ISO) |

## Validation evidence
- 12 commits; 12 entries; 0 invented
- breaking changes: 0; section omitted
- matched Keep a Changelog group order

## Residual risk / follow-ups
- v1.1.4 was released but has no changelog entry in the file —
  out of scope for this run; recommend a separate backfill pass.

## Artifact index
.temp/task-<slug>/
  prompt.txt
  commits.txt
  classified.md
  detected-style.txt
  changelog-entry.md
  backup/CHANGELOG.md
  report.md
CHANGELOG.md (staged under --fix)
```
