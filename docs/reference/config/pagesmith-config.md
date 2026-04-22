---
title: 'pagesmith.config.json5'
description: 'Pagesmith documentation site configuration for the ADK docs.'
artifact_kind: config
---

# pagesmith.config.json5

Configuration for the Pagesmith-built ADK documentation site. Defines content directory, base path, search behavior, footer links, and edit-on-GitHub.

For the full set of supported keys see `node_modules/@pagesmith/docs/REFERENCE.md` and the JSON schema at `node_modules/@pagesmith/docs/schemas/pagesmith-config.schema.json`.

## Current configuration

```json5
{
  // ADK Documentation Site
  name: "ADK",
  title: "Agent Development Kit",
  description: "Principal-engineer-grade skills for software development agents",

  // Paths
  contentDir: "./docs",
  outDir: "gh-pages",

  // Site — basePath must match the URL path (e.g. /repo-name for https://user.github.io/repo-name/)
  origin: "https://projects.sujeet.pro/agents-devkit",
  basePath: "/agents-devkit",

  // Sidebar
  sidebar: {
    collapsible: true,
  },

  // Search
  search: {
    enabled: true,
  },

  // Footer links
  footerLinks: [
    { label: "GitHub", path: "https://github.com/sujeet-pro/agents-devkit" },
    { label: "Maintained by Sujeet", path: "https://sujeet.pro" },
  ],

  // Edit link
  editLink: {
    repo: "https://github.com/sujeet-pro/agents-devkit",
    branch: "main",
    label: "Edit on GitHub",
  },

  // Show git-based last updated date on each page
  lastUpdated: true,
}
```

## Build & preview

```bash
npx pagesmith-docs build       # production build → gh-pages/
npx pagesmith-docs dev         # local dev server with live reload
npx pagesmith-docs preview     # serve the built output
```

## Source

`pagesmith.config.json5` at repo root.
