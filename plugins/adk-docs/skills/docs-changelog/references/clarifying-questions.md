# `docs-changelog` — clarifying questions

Asked under `-i`; defaults apply under `--auto`.

## Phase 0

1. **Range: `<from>..<to>`. Confirm?**
   - _Default under `--auto`:_ the arguments as given.

2. **CHANGELOG.md path: `<resolved>`. Override?**
   - _Default under `--auto`:_ `docs.md.changelog_path` or
     `CHANGELOG.md` at repo root.

## Phase 1

3. **Style: `<detected>`. Override?**
   - _How to pick:_ Default is detected. Override with
     `--style kaC|semantic|free`.
   - _Default under `--auto`:_ detected; Keep a Changelog if
     ambiguous.

## Phase 2

4. **`<N>` commits classified; `<M>` flagged as breaking. Review
   classification?**
   - _Default under `--auto`:_ proceed.
   - _When to ask:_ `-i` mode; user wants to review ambiguous
     commits.

## Phase 3

5. **Entry phrasing: accept, or edit before `--fix`?**
   - _Default under `--auto`:_ accept.
   - _When to ask:_ `-i` mode; user wants to tune phrasing.

## Phase 4 (under `--fix`)

6. **Insert block into `CHANGELOG.md` at `<line>`?**
   - _Default under `--auto --fix`:_ insert silently (no ask) unless
     the target version block already exists.

7. **Target version block `<version>` already exists. Overwrite it?**
   - _Default under `--auto --fix`:_ **ask** — this is the one
     prompt that survives `--auto`.

## Anti-rules

- Never ask the user to pick a group for each commit — classify
  deterministically; surface ambiguities in `classified.md` for `-i`
  review.
- Never stack questions; iterate.
- Never skip the overwrite gate under `--auto --fix`.
