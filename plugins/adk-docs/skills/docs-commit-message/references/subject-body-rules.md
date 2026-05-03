# Subject + body rules

The exact rules the validator enforces for every commit message.

## Subject

| Rule | Value |
| --- | --- |
| Max length | 72 chars |
| Trailing period | forbidden |
| Mood | imperative (`add`, `fix`, `migrate`) |
| Tense | present (no `-ed`, no `-ing`) |
| Casing after the Conventional-Commits `:` | lowercase (unless proper noun) |
| Empty scope (`()` with nothing in it) | forbidden |
| Leading whitespace | forbidden |

### Imperative mood cheat sheet

| Past tense (forbidden) | Imperative (required) |
| --- | --- |
| added | add |
| fixed | fix |
| moved | move |
| refactored | refactor |
| tested | test / verify |
| updated | update |
| bumped | bump |
| removed | remove |
| deprecated | deprecate |

### Conventional Commits subject grammar

```
<type>(<scope>)?(!)?: <description>
```

- `<type>` from the set listed in `references/convention-detector.md`.
- `(<scope>)` optional; short noun in parens.
- `(!)` optional; signals breaking change.
- `: ` — colon + one space.
- `<description>` — imperative, lowercase-initial unless proper
  noun, no trailing period.

## Body

| Rule | Value |
| --- | --- |
| Separator from subject | exactly one blank line |
| Paragraph width | ≤ 72 (URL + fenced code lines exempt) |
| Bullet points | allowed (`-` or `*`; match `recent-subjects.txt`'s body style) |
| Code fences | allowed; language tag required |
| Trailer separator | one blank line before trailers |

### Body structure

1. **Paragraph 1:** WHY — the problem, user-visible impact, or
   motivating ticket.
2. **Paragraph 2 (optional):** HOW / trade-off — the approach
   picked, the alternative rejected.
3. **Paragraph 3 (optional):** notes for reviewers — feature flag
   default, rollout plan, data migration concern.

### Body DON'T list

- Don't restate the subject. ("Fix the bug" after a subject that
  already says "fix the bug".)
- Don't narrate the diff. ("Added `Foo.ts` which contains class
  `Foo` …")
- Don't include marketing phrases.
- Don't include TODOs ("TODO: fix this later" belongs in code, not
  in a commit body).

## Trailers

| Token | Format | When to include |
| --- | --- | --- |
| `Refs` | `Refs <TICKET>, <TICKET2>` | ticket(s) referenced in commits / branch name matching the repo's pattern |
| `Fixes` | `Fixes <TICKET>` | single-purpose commit closing a ticket |
| `Co-authored-by` | `Co-authored-by: Name <email>` | actual co-author |
| `Signed-off-by` | `Signed-off-by: Name <email>` | DCO-required repos |
| `Reviewed-by` | `Reviewed-by: Name <email>` | pre-commit review in workflow (rare) |

### Hard rules on trailers

- Never invent a ticket reference.
- Never add `Co-authored-by` unless actual co-authoring happened.
- Never add `Signed-off-by` unless the repo requires DCO
  (detect by previous commits).

## Breaking changes

Two acceptable signals:

1. `!` after type/scope: `feat(auth)!: migrate to OIDC`.
2. `BREAKING CHANGE:` footer in the body with a one-line
   description and a one-line migration note.

Both may be present; if only one is used, prefer the `!` form for
short subjects and the footer form for nuanced breaks.

## Examples of validator-rejected subjects

- `fix the bug` — no type prefix under `conventional`.
- `Added new test.` — past tense + trailing period.
- `feat: ` — empty description.
- `feat(): add foo` — empty scope.
- `This commit adds a feature for the checkout page in the
  storefront app` — 76 chars > 72 limit.
- `chore: various` — vague description; the skill can't know what
  "various" means, but the validator allows it syntactically —
  it's just bad style.
