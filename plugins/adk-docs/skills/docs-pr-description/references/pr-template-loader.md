# PR template loader

How `docs-pr-description` consumes `.github/pull_request_template.md`
(and alternative paths per GitHub's conventions).

## Template discovery order

GitHub honors multiple template locations. The skill checks in order
and uses the first match:

1. `.github/pull_request_template.md`
2. `.github/PULL_REQUEST_TEMPLATE.md`
3. `.github/PULL_REQUEST_TEMPLATE/*.md` (multi-template; uses the
   default named `default.md` if present, else the first
   alphabetically).
4. `docs/pull_request_template.md`
5. (fallback) `~/.config/adk/github.md.pr_template_path` if set.

Store the resolved template in `.temp/task-<slug>/template.md`.

## Applying the template

1. **Adopt the template's section headings verbatim.** Don't rename
   `## Summary` to `## Overview` because you prefer the latter.
2. **Keep the template's required checkboxes.** Fill them with `[x]`
   only when the condition is actually true (e.g. `[x] Added tests`
   only if `tests.diff` is non-empty).
3. **Keep the template's placeholder prompts** (e.g. `<!-- Why is
   this change necessary? -->`) deleted in the final body. Don't
   leave HTML-comment prompts visible.
4. **Add no sections the template doesn't have,** unless the user
   supplies them explicitly. If the template lacks a `Test plan`
   section, add it after the last section (since Test plan is a
   Constitution-mandated section) — and note the addition in the
   report.
5. **Order:** template sections first; skill-mandated sections
   (`Test plan`, `Risks`) after, if the template lacks them.

## Template style guide detection

Some templates embed a style guide in HTML comments, e.g.:

```markdown
<!-- Use sentence case for section bullets. -->
<!-- Keep the summary to 3 bullets or fewer. -->
```

Respect these in draft time. Do not remove them from the final body
(they're markdown comments; they render invisibly).

## Special markers

- `<!-- CURSOR -->` / `<!-- HERE -->` — some teams mark the user's
  attention point. Preserve as-is; place the Summary text
  immediately above.
- `<!-- bot -->` — some teams gate automated edits. If present and
  the skill is running under `--fix`, respect the marker: skip the
  automated write and surface to the user.

## Multi-template selection

When the repo has `.github/PULL_REQUEST_TEMPLATE/*.md`:

- If the branch or commit subject hints the type (e.g. `hotfix/…`
  → `hotfix.md` if present), pick that one.
- Otherwise pick `default.md`, or the first alphabetically.
- Always surface the chosen template in the report.

## When the template is absent

Use the skill's own section order (see
`references/risk-first-format.md`). Don't invent sections the team
doesn't use.
