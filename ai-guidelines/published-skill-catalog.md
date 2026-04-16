# Published Skill Catalog

## Goal

Keep the default public catalog focused, non-duplicative, and aligned with common engineering use cases without dropping important specialist workflows.

## Default Published Skills


| Skill                         | Primary Use                                                                   |
| ----------------------------- | ----------------------------------------------------------------------------- |
| `adk-plan`                    | Turn a request into an executable plan                                        |
| `adk-research`                | Run structured technical research with evidence                               |
| `adk-build`                   | Implement or enhance code with validation                                     |
| `adk-refactor`                | Restructure code safely without changing intent                               |
| `adk-migrate`                 | Upgrade frameworks, libraries, or patterns                                    |
| `adk-diagram`                 | Create or update markdown docs with editable diagrams and rendered SVG output |
| `adk-review-pr`               | Review a pull request                                                         |
| `adk-review-local-changes`    | Review local work before commit or PR                                         |
| `adk-address-review-feedback` | Fix review comments and close the loop                                        |
| `adk-review-docs`             | Review documentation for accuracy and clarity                                 |
| `adk-write-docs`              | Write or refresh engineering documentation                                    |
| `adk-audit-repo`              | Audit a repository for quality, risk, or maintainability                      |
| `adk-audit-site`              | Audit a live site or webapp for health, SEO, and user-facing quality          |
| `adk-test`                    | Verify behavior through acceptance, regression, or webapp testing             |
| `adk-design`                  | Design or audit interfaces and frontend experience                            |
| `adk-chart`                   | Turn data into reusable charts and rendered assets                            |
| `adk-commit`                  | Draft commit, PR, and changelog-ready summaries from real changes             |


## Naming Rules

- Keep the `adk-` prefix.
- Use direct verbs and nouns.
- Keep families grouped in autocomplete:
  - `adk-review-*`
  - `adk-build`, `adk-refactor`, `adk-migrate`
  - `adk-audit-*`
- Avoid overloaded router names unless they are truly the best entrypoint.

## Legacy Policy

- Legacy plugin-era skills can remain during migration.
- Legacy skills should be hidden from default discovery once a new published replacement exists.
- New docs should focus on this catalog first.