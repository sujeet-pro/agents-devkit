# `docs-commit-message` — anti-patterns

## Subject

- **"updates", "changes", "fix bug".** Noise. The reader opens the
  diff. Name the thing.
- **Subject > 72 chars.** GitHub and `git log --oneline` truncate.
- **Past tense / gerund.** "added", "adding" → "add".
- **Capital first letter after `:` in Conventional Commits.** The
  spec reserves the type (`feat`, `fix`) capitalized-or-not; the
  message after `:` is lowercase unless it's a proper noun.
- **Area-only subject.** "checkout: changes" — what changed?
- **Trailing period.** The subject isn't a sentence.

## Body

- **Repeating the diff in prose.** "Added a new file `Foo.ts`
  containing a class `Foo` with methods `bar` and `baz`" —
  reviewers read the diff.
- **No blank line between subject and body.** `git log` renders
  incorrectly.
- **Line width > 72 in paragraphs.** Wraps poorly in `git log`.
- **Missing the why.** "Fix the bug" — what was the bug? How would
  future-you reproduce it?
- **Marketing phrases.** "This meaningfully improves X" — no.

## Trailers

- **Inventing ticket refs from the branch name.** Only reference
  tickets the diff / branch explicitly names AND that match the
  repo's ticket-ref convention.
- **Co-authored-by that isn't real.** Only when actual co-authoring
  happened.
- **Duplicated trailers** (two `Signed-off-by` on the same author).

## Process

- **Running `git commit --no-verify`.** Pre-commit hooks are sacred.
- **Running `git commit --amend`.** Out of scope; the user owns
  amend.
- **Running `git add` or `git add -p`.** Staging is the user's
  decision.
- **Running `git commit -a`.** Includes unstaged tracked changes;
  the user chose staging for a reason.
- **Auto-committing without a confirmation.** Even under `--auto`.
- **Retrying with `--no-verify` after a hook rejection.** Fix the
  reason or stop.

## Scope

- **One giant commit across 5 logical changes.** If the staged diff
  spans multiple logical changes, surface to the user: "Consider
  splitting via `git add -p` or committing in pieces." The skill
  will still draft a single message if you proceed, but the draft
  will read worse.

## Convention

- **Imposing Conventional Commits on a free-form repo.** Match the
  repo. Detection is per `references/convention-detector.md`.
- **Ignoring a detected convention because "the user probably wants
  Conventional".** The repo's history is the authority.
