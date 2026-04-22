# `validate-browser` — auto-fix recipes (`--mode fix`)

When `--mode fix` is set, the skill attempts auto-fixes for findings that match a known recipe. Then re-runs `--mode review` to confirm zero residual.

## a11y-audit recipes

| Rule | Pattern | Auto-fix |
| --- | --- | --- |
| `image-alt` | `<img src="..."` without `alt` | Add `alt=""` (decorative) by default; flag for human review |
| `label` | input without associated label | Add `aria-label="<inferred from name attr>"`; flag for human |
| `html-has-lang` | `<html>` missing `lang` | Add `lang="en"` |
| `landmark-one-main` | no `<main>` | Wrap primary content; flag for human review |
| `button-name` | `<button>` empty | Add `aria-label="Action"` placeholder; flag for human |
| `link-name` | `<a>` empty | Add `aria-label="Link"` placeholder; flag for human |
| `color-contrast` | low contrast | NEVER auto-fix (requires design judgment); always flag for human |
| `outline-none` | `outline: none` without replacement | Add `:focus-visible { outline: 2px solid currentColor; outline-offset: 2px }`; flag for human review |

## console-audit recipes

| Pattern | Auto-fix |
| --- | --- |
| `Failed to load resource: 404` for known dev URLs | Add a `// TODO: fix path` comment near the source; never silently rewrite |
| Deprecated React lifecycle (`componentWillMount` etc.) | Suggest the modern equivalent in a comment; never auto-rewrite |

## visual-check / verify-fix / interaction-test

No auto-fix possible. Findings always require human judgment. `--mode fix` for these is a no-op (logged as such).
