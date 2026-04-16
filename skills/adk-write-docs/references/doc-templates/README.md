# Document Templates

Built-in templates for common engineering documents used by `adk-write-docs`.

## Usage

- If `--type` is provided, use the matching template in this directory as the default structure.
- If `--template <path-or-url>` is provided, read the custom template and preserve its structure instead.
- If both are provided, keep the custom template structure and use the named type only for quality expectations.

## Template Index

| Type | Template | Purpose |
| --- | --- | --- |
| `adr` | [adr.md](./adr.md) | Architecture decisions |
| `api-reference` | [api-reference.md](./api-reference.md) | Endpoint, CLI, or API reference docs |
| `erd` | [erd.md](./erd.md) | Engineering requirements |
| `guide` | [guide.md](./guide.md) | How-to or explainer guide |
| `hld` | [hld.md](./hld.md) | High-level design |
| `incident-report` | [incident-report.md](./incident-report.md) | Incident summary or postmortem |
| `lld` | [lld.md](./lld.md) | Low-level design |
| `onboarding` | [onboarding.md](./onboarding.md) | New-user or new-engineer onboarding |
| `prd` | [prd.md](./prd.md) | Product requirements |
| `project` | [project.md](./project.md) | README or project overview |
| `reference` | [reference.md](./reference.md) | Stable reference material |
| `release-notes` | [release-notes.md](./release-notes.md) | Release summaries and upgrade notes |
| `rfc` | [rfc.md](./rfc.md) | Proposal or request for comments |
| `runbook` | [runbook.md](./runbook.md) | Operational runbook or response procedure |
| `status-report` | [status-report.md](./status-report.md) | Progress or health summary |
| `tdd` | [tdd.md](./tdd.md) | Technical design or implementation design |

## Custom Templates

When `--template <path-or-url>` is provided:
1. Read the template from a local markdown file or supported hosted-doc URL.
2. Preserve headings, tables, and boilerplate unless the user asks to change them.
3. Use the custom template as the structural backbone for `create`, `update`, or `improve`.
