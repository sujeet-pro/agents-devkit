# adk-write-docs

Write, update, improve, or publish engineering documentation using named templates or a custom template URL or file.

## Quick Start

```bash
npx adk-write-docs "docs/adr/003-auth-migration.md" --action create --type adr
```

## What This Skill Does

Creates or maintains engineering documentation that stays grounded in the repository, uses a predictable structure, and supports both named templates and custom templates from a local file or URL. The skill covers the full documentation lifecycle: create, update, improve, and publish.

## Command Reference

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<doc-task-or-target>` | free text or doc path | required | What document to create, update, improve, or publish |
| `--action` | `create`, `update`, `improve`, `publish` | `create` | Documentation lifecycle action |
| `--type` | `adr`, `api-reference`, `erd`, `guide`, `hld`, `incident-report`, `lld`, `onboarding`, `prd`, `project`, `reference`, `release-notes`, `rfc`, `runbook`, `status-report`, `tdd` | none | Named built-in template |
| `--template` | path or URL | none | Custom template from a local file, Confluence URL, or Google Docs URL |
| `--scope` | path | none | Limit repo reading to the relevant surface |
| `--publish` | `markdown`, `source`, `both` | `markdown` | Keep markdown local, publish to source system, or both |
| `--publish-space` | text | none | Publishing space or workspace target |
| `--publish-parent` | text | none | Parent doc hint for hosted destination |
| `--publish-update` | text | none | Update an existing hosted page |
| `--auto` | flag | off | Skip confirmations and use defaults |
| `--help` | flag | off | Show the skill and stop |

## Dependencies

| Dependency | Type | Required |
| --- | --- | --- |
| `git` | command | yes |
| `python3` | command | yes |

## Skill Layout

```
adk-write-docs/
  SKILL.md
  README.md
  scripts/
    preflight.py
  references/
    workflow.md
    persona.md
    _shared/
      ai-guidelines-overview.md
      constitution.md
      research-protocol.md
      output-format.md
    doc-templates/
      README.md
      adr.md
      api-reference.md
      erd.md
      guide.md
      hld.md
      incident-report.md
      lld.md
      onboarding.md
      prd.md
      project.md
      reference.md
      release-notes.md
      rfc.md
      runbook.md
      status-report.md
      tdd.md
```

## Workflow

1. Confirm the document purpose, audience, lifecycle action, and destination.
2. Inspect local code and nearby docs first.
3. Choose a named built-in template or load the custom template from the provided path or URL.
4. Preserve template structure and boilerplate unless the user asks to change it.
5. Write, update, or improve the document with repo-backed facts and explicit uncertainty.
6. Publish only after the markdown source is coherent and the destination requirements are clear.
7. Report what changed, how it was validated, and what still needs review.

## Interaction Protocol

Unless `--auto` is set, the skill follows an interactive workflow:

1. **Intent confirmation** -- confirms doc type, target path, lifecycle action, audience, scope, and template.
2. **Outline review** -- presents the document outline for approval before writing body content.
3. **Iterative drafting** -- shows draft sections one at a time for review rather than writing silently.
4. **User response** -- `ok`/`next` to approve, feedback text to revise, `skip` to move on, `done` to finalize.

## Output Format

Each run produces:
- Summary of what was created or changed
- Target path and lifecycle action
- Template used (named or custom)
- Validation results
- Remaining risk or items needing review

## Examples

### Create an ADR
```bash
npx adk-write-docs "docs/adr/003-auth-migration.md" --action create --type adr
```
Confirms the decision topic, presents the ADR outline, writes each section iteratively.

### Update an API reference
```bash
npx adk-write-docs "docs/api/users.md" --action update --scope src/api/users/
```
Reads the current doc and source code, proposes changes, updates the reference in place.

### Write an onboarding guide
```bash
npx adk-write-docs "docs/onboarding/new-hire.md" --action create --type onboarding --auto
```
Skips confirmations, uses the onboarding template, writes the full guide grounded in repo structure.

## What Success Looks Like

- [ ] The document follows the chosen template structure
- [ ] All claims are grounded in code or cited sources
- [ ] Uncertain or unverified items are labeled
- [ ] The markdown renders correctly and links are valid
- [ ] Publish steps are only claimed when the destination write actually ran
- [ ] The skill reports what changed, validation results, and remaining risk
