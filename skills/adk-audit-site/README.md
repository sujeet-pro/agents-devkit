# adk-audit-site

Audit a live site or webapp for SEO, performance, accessibility, security signals, metadata, and broken-user-flow issues.

## Quick Start

```bash
npx adk-audit-site "https://example.com"
```

## What This Skill Does

Audits a live website or webapp when the primary question is user-visible site quality, discoverability, or health. Groups findings by category (SEO, performance, accessibility, security, content) and severity, each with a unique finding ID. Proposes highest-leverage fixes first and offers re-audit after approved changes.

## Command Reference

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<url>` | live URL | required | What site or webapp should be audited |
| `--focus` | `seo`, `performance`, `accessibility`, `security`, `content`, `all` | `all` | Primary audit lens |
| `--scope` | path, route group, or page hint | none | Limit the audit to one surface |
| `--auto` | flag | off | Skip confirmations and execute with defaults |
| `--help` | flag | off | Show the skill and stop |

## Dependencies

| Dependency | Type | Required |
| --- | --- | --- |
| `git` | CLI command | yes |
| `python3` | CLI command | yes |
| `squirrel` | CLI command | yes |
| Web access | runtime | yes |
| Browser tooling | runtime | recommended |

## Skill Layout

```
skills/adk-audit-site/
  SKILL.md                              # Skill definition and frontmatter
  README.md                             # This file
  scripts/
    preflight.py                        # Pre-flight dependency checks
  references/
    persona.md                          # Skill-specific persona
    workflow.md                         # Skill-specific workflow detail
    _shared/
      ai-guidelines-overview.md         # Shared ADK guidance
      constitution.md                   # Shared constitution
      output-format.md                  # Shared output format
      research-protocol.md              # Shared research protocol
```

## Workflow

1. Confirm the live target, focus, and whether the user wants audit only or fix proposals too.
2. Prefer live-site evidence before source-only guesses.
3. Run the smallest useful audit pass first, then deepen only where evidence says it matters.
4. Group findings by severity, fixability, and whether they need code, content, or product judgment.
5. Propose the highest-leverage fixes first and re-audit after approved changes.
6. Finish with health summary, remaining risks, and any manual follow-up still needed.

## Interaction Protocol

- **Confirm URL and focus** -- before auditing, confirm the target URL and which focus area(s) apply.
- **Present findings with F-IDs** -- group findings by category and severity, each with a unique finding ID (e.g., F-01).
- **Severity ordering** -- critical and high-severity findings appear first; informational items appear last.
- **Offer re-audit after fixes** -- when fixes are applied, offer to re-audit affected pages.
- **Surface evidence** -- every finding cites a URL, tool output, or page observation.

## Output Format

- Health summary
- Findings by severity with F-IDs
- Affected URLs or surfaces
- Validation or re-audit status
- Remaining judgment calls

## Examples

Full site audit:
```
/adk-audit-site https://example.com
```

Performance-focused audit:
```
/adk-audit-site https://example.com --focus performance
```

Accessibility audit of a specific page:
```
/adk-audit-site https://example.com/contact --focus accessibility --scope /contact
```

## What Success Looks Like

- [ ] Target URL and focus are confirmed before auditing
- [ ] Findings are grouped by category with unique F-IDs
- [ ] Severity ordering is clear (critical first, informational last)
- [ ] Every finding cites evidence from live-site observation
- [ ] Fix proposals are ordered by leverage
- [ ] Re-audit is offered after changes are applied
- [ ] Remaining risks and manual follow-ups are listed
