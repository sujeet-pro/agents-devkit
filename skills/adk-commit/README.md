# adk-commit

Generate accurate commit messages, PR descriptions, or changelog summaries from real repository changes.

## Quick Start

Install via npx skills, then invoke:

```
/adk-commit --action commit
```

```
/adk-commit --action pr-describe --convention conventional
```

```
/adk-commit --action changelog --scope src/
```

```
/adk-commit --action commit --auto
```

## What This Skill Does

Produces change narratives grounded in the actual repository state. It inspects the real diff, staged work, or branch history, identifies the primary change type and impacted scope, surfaces breaking changes and validation gaps, and drafts the smallest message or summary that explains why the change exists.

## Command Reference

| Invocation | Description |
| --- | --- |
| `/adk-commit` | Generate a commit message (default action) |
| `/adk-commit --action commit` | Generate a commit message from staged changes |
| `/adk-commit --action pr-describe` | Write a PR description from branch history |
| `/adk-commit --action changelog` | Generate a changelog-ready summary |
| `/adk-commit --convention plain` | Use plain message style instead of conventional |
| `/adk-commit --scope <path>` | Limit the analyzed change surface |
| `/adk-commit --auto` | Skip confirmations, use defaults |
| `/adk-commit --help` | Show the skill description and stop |

## Dependencies

| Dependency | Required? | Install Command |
| --- | --- | --- |
| git | Yes | `brew install git` |
| python3 | Yes | `brew install python@3` |

## Skill Layout

```
adk-commit/
  SKILL.md              # Skill definition and instructions
  README.md             # This file
  scripts/
    preflight.py        # Pre-flight dependency checker
  references/
    workflow.md          # Commit workflow details
    persona.md           # Agent persona guidance
    _shared/
      ai-guidelines-overview.md
      constitution.md
      output-format.md
      research-protocol.md
```

## Workflow

1. **Inspect changes** -- read the real diff, staged work, or branch history
2. **Identify change type** -- determine primary purpose and impacted scope
3. **Surface breaking changes** -- flag breaking changes and missing validation explicitly
4. **Draft message** -- write the smallest message that explains why the change exists
5. **Align to convention** -- match the repository's established commit convention
6. **Present** -- show the proposed artifact and any follow-up steps still needed

## Interaction Protocol

- **Confirmations**: The skill shows the generated commit message or PR description for approval before finalizing. Use `--auto` to skip.
- **Findings format**: The draft message is presented in a code block. Breaking changes and validation gaps are called out separately.
- **User response syntax**: Reply with "commit", "edit: ...", or "regenerate with ..." after reviewing the draft.

## Output Format

1. **Summary** -- the proposed commit message, PR description, or changelog entry
2. **Scope** -- files and change areas covered
3. **Findings** -- breaking changes, validation status, and convention alignment
4. **Validation** -- whether the message reflects actual git state
5. **Remaining risk** -- unverified claims or missing context
6. **Next steps** -- push, tag, publish, or other follow-up actions

## Examples

### Generate a commit message
```
> /adk-commit --action commit

Analyzed: 3 files changed, 47 insertions, 12 deletions
Primary change type: feat (new retry logic in HTTP client)

Proposed message:
  feat(http): add configurable retry policy for failed requests

  - RetryPolicy class with exponential backoff
  - wrap fetch calls with retry middleware
  - default 3 retries with 1s base delay

  Breaking changes: none
  Validation: 14 new tests pass

Accept? [commit / edit / regenerate]
```

### Write a PR description
```
> /adk-commit --action pr-describe --convention conventional

Branch: feature/oauth2-flow (4 commits ahead of main)

Proposed PR description:
  ## Summary
  Add OAuth2 authorization code flow for API gateway

  ## Changes
  - OAuth2 client with PKCE support
  - Token refresh middleware
  - Integration tests against mock provider

  ## Breaking Changes
  None

  ## Validation
  All tests pass, manual flow tested against dev environment
```

### Changelog summary
```
> /adk-commit --action changelog --scope src/

Changelog entry for src/ changes since last tag (v2.3.0):
  - feat: add retry policy for HTTP client
  - fix: resolve pagination boundary error
  - refactor: extract shared validation module
```

## What Success Looks Like

- [ ] Message reflects actual git state, not guesswork
- [ ] Breaking changes are explicitly flagged
- [ ] Validation gaps are stated rather than hidden
- [ ] Wording is concise and reviewable
- [ ] Convention matches the repository's established style
- [ ] User approves before any commit is created
