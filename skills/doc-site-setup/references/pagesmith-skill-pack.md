# Pagesmith skill pack — what each skill does

After `npx pagesmith-core skills`, the following skills land in the consumer's `.claude/skills/` and `.cursor/skills/`:

| Skill | Purpose | When to use |
| --- | --- | --- |
| `pagesmith-docs-setup` | (covered by `@adk:doc-site-setup`) | Bootstrap |
| `pagesmith-docs-add-page` | Author a new doc page | Add page to existing site |
| `pagesmith-docs-configure-nav` | Sidebar / chrome / breadcrumbs | Restructure navigation |
| `pagesmith-docs-customize-theme` | Colors / fonts / layout overrides | Visual customization |
| `pagesmith-docs-add-search` | Pagefind setup | Add or tune search |
| `pagesmith-docs-deploy-gh-pages` | GitHub Pages workflow | First deploy or workflow tweaks |
| `pagesmith-generate-docs` | Bulk page generation from sources | Generate API reference / changelog |

(There are additional `pagesmith-core-*` and `pagesmith-site-*` skills if the consumer needs the lower-level pieces.)
