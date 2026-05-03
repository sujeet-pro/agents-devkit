# Convention detector

`docs-commit-message` detects the repo's commit-message convention
from the last 10 subjects. The detection drives subject formatting
and validator rules.

## Inputs

- `recent-subjects.txt` = `git log -10 --pretty=format:%s`.
- Optionally: `git log -20 --pretty=format:%s%n%b%n---` to read body
  for `BREAKING CHANGE:` footer detection.
- Optionally: `.github/COMMIT_MESSAGE_TEMPLATE.md` if the repo has
  one. If present, its pattern overrides the empirical detection.

## Styles

### `conventional` — Conventional Commits

Regex: `^(feat|fix|chore|refactor|docs|test|perf|build|ci|style|revert)(\([^)]+\))?(!)?: .+`

Accepted types (extended): `feat`, `fix`, `chore`, `refactor`,
`docs`, `test`, `perf`, `build`, `ci`, `style`, `revert`. A repo may
use a subset; the detector only requires the regex match.

Scope: optional; inside `()`. Any non-empty non-`)` string.

Breaking: `!` after type/scope OR a `BREAKING CHANGE:` footer.

**Confidence rule:** ≥ 7 of 10 subjects match → `conventional`.

### `semantic` — semantic-release (a Conventional Commits variant)

Stricter: requires `BREAKING CHANGE:` footers for any major-version
signal; may include `Fixes #N` / `Closes #N` trailers.

**Confidence rule:** all subjects match Conventional AND at least
one commit body in the last 20 contains `BREAKING CHANGE:` →
`semantic`. If Conventional matches but no `BREAKING CHANGE:` footer
exists, use plain `conventional`.

### `free` — free-form

Anything else. The detector then extracts:

- Typical first-word casing (`Fix ...` vs `fix ...`).
- Presence of `[tag]` prefixes (`[hotfix] ...`).
- Ticket-ref placement (inline in subject vs in trailer).

**Fallback:** if the last 10 subjects are a mix with no dominant
pattern (< 7 same-style), free-form is the safest default — the skill
mirrors the most recent non-merge commit's structure.

## Body conventions

- **Hard-wrap width:** default 72. Some repos use 100; detect by
  reading the bodies of the last 20 commits and measuring the 95th-
  percentile line length. Use the detected width, clamped to
  [72, 100].
- **Trailer presence:** detect `Co-authored-by`, `Signed-off-by`,
  ticket-ref trailers from existing bodies; include them in the
  draft only when the diff context warrants.

## Ticket-ref convention

- `CHK-1238`, `PROJ-1234` → Jira-style (Project key + digits).
- `#42` → GitHub-issue-style.
- `LIN-ABCDE` → Linear.
- Compose from the repo's existing usage; never invent a pattern.

## Output

`detected-style.txt`:

```
style: conventional
confidence: 0.8
matches: 8 of 10
body-width: 72
ticket-pattern: CHK-\d+
trailers-seen: [Refs, Co-authored-by]
override: none
```

## Hard rules

1. **Detection is empirical, not aspirational.** If the repo uses
   `fix:` / `feat:` in 8 of 10 commits, it's conventional — even if
   the operator prefers free-form.
2. **`--style` always overrides detection.** Noted in the report as
   "user override".
3. **Fresh repos (no commits) default to `conventional`** unless
   `--style free` is passed. Principle: the next committer will
   likely use a modern convention.
4. **Merge commits and auto-release commits are excluded from the
   sample.** They distort the distribution.
5. **`CONTRIBUTING.md` / `COMMIT_MESSAGE_TEMPLATE.md` can override
   detection.** If the repo documents the expected style explicitly,
   use it.
