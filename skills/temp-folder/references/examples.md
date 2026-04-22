# `temp-folder` — examples

## Slug derivation examples

| Prompt | Slug |
| --- | --- |
| "Build the export-to-CSV button on the data grid" | `csv-export-button` |
| "Fix dashboard showing 0 active users" | `dashboard-active-users-zero` |
| "Refactor the auth module" | `auth-refactor` (date-prefixed if folder exists: `2026-04-22-auth-refactor`) |
| "Audit security of the payments API" | `audit-payments-api` |
| "Migrate from React 18 to React 19" | `react-19-migrate` |

## Path resolution examples

```
resolveTempPath("csv-export", "preview/2") -> .temp/task-csv-export/preview/sample-2.html
resolveTempPath("auth-refactor", "spec")   -> .temp/task-auth-refactor/spec.md
resolveTempPath("api-audit", "report")     -> .temp/task-api-audit/report.md
resolveTempPath("dash-fix", "browser/verify-fix") -> .temp/task-dash-fix/browser-validation/verify-fix/
```
