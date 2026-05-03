---
# ~/.config/adk/repos.md
# Repo -> local-folder mapping + per-repo defaults.
# Used by every code/review/docs/investigate skill.

repos:
  - name: acme/checkout-api
    path: ~/code/acme/checkout-api
    primary_language: kotlin
    base_branch: main
    datadog_service: checkout-api
    statsig_project: backend
    mixpanel_project: 12345
    notes: |
      Spring Boot 3.x. Use `./gradlew :app:bootRun` for local.
      CI: github actions, .github/workflows/ci.yml.

  - name: acme/storefront
    path: ~/code/acme/storefront
    primary_language: typescript
    base_branch: main
    datadog_service: storefront-web
    statsig_project: frontend
    notes: |
      Next.js 15 App Router. Build with `npm run build`.
      Tests with `npm run test` (vitest).

  # Add more repos here as you onboard them.

defaults:
  base_branch: main
  primary_language: typescript
---

# Notes

Resolution rule: a skill resolves "the current repo" by walking up from CWD to a `.git` directory, then matching by `path` first, then by `git remote get-url`.

If a repo isn't listed here, skills will surface "unknown repo; add to ~/.config/adk/repos.md to enable shorthand resolution".
