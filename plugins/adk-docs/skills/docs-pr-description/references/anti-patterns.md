# `docs-pr-description` — anti-patterns

## Content

- **"Updated some files."** Name the areas. What problem does this
  solve? What's the user-visible behavior change?
- **Repeating the diff as bullet points.** Reviewers can read the
  diff. The PR body maps the diff to intent.
- **Marketing padding.** "This meaningfully improves the checkout
  experience" — replace with "reduces p99 on `POST /cart/add` from
  820ms to 310ms per the attached DD screenshot".
- **Inventing linked tickets.** If the commits say "fix the
  checkout bug", don't write "Fixes CHK-1234" unless CHK-1234
  actually appears in a commit body.
- **Omitting the test plan.** Even for a one-line fix, state what
  you did to verify.
- **Claiming "no risk".** Every change has a risk. Name it even if
  it's small ("touches a new file; zero regression surface for
  existing behavior").
- **Claiming "no breaking changes" when a public fn was renamed.**
  A renamed public function IS a breaking change.

## Structure

- **Title exceeds 70 chars.** GitHub truncates at 72 in some views;
  keep under 70.
- **Missing code-fence language tags.** GitHub renders fenced blocks
  only when the tag is set.
- **Dumping commit messages as the summary.** The PR body is not
  `git log`.

## Process

- **Running `gh pr edit` without confirmation under `--auto --fix`.**
  Reviewers get notifications; always ask once before the first
  remote write.
- **Running `gh pr review --approve` or `gh pr merge`.** Out of
  scope; never.
- **Editing a PR owned by someone else.** Only the PR author's own
  description; `--fix` must check `gh pr view --json author` and
  refuse if the current user isn't the author.
- **Forgetting to re-fetch after `gh pr edit`.** Always verify the
  body landed.

## Scope

- **Writing a README-length PR body.** Reviewers don't read past
  the first fold. Keep to 30-80 lines.
- **Including dashboard screenshots inline.** Link instead; the
  screenshot is noise in the diff review.
- **Including your chat-session reasoning.** The reviewer doesn't
  need "I considered doing X but chose Y because…" as PR body
  copy. Put that in a commit message body.
