# Pagesmith Deploy-to-GitHub-Pages Reference (fallback)

> Inline fallback for deploying a `@pagesmith/docs` site to GitHub Pages. When the package is installed, prefer:
> - `node_modules/@pagesmith/docs/skills/pagesmith-docs-deploy-gh-pages/SKILL.md`
> - `node_modules/@pagesmith/docs/REFERENCE.md`
> - `node_modules/@pagesmith/docs/schemas/pagesmith-config.schema.json`

## Config

Set the right `origin` and `basePath` in `pagesmith.config.json5`:

| Hosting                                            | `origin`                    | `basePath` |
| -------------------------------------------------- | --------------------------- | ---------- |
| `https://<owner>.github.io/<repo>` (repo page)     | `https://<owner>.github.io` | `/<repo>`  |
| `https://<owner>.github.io` (user/org page)        | `https://<owner>.github.io` | `/`        |
| `https://docs.example.com` (custom domain root)    | `https://docs.example.com`  | `/`        |
| `https://example.com/docs` (custom domain subpath) | `https://example.com`       | `/docs`    |

```json5
{
  origin: "https://acme.github.io",
  basePath: "/my-docs",
  outDir: "./gh-pages",
}
```

`outDir: './gh-pages'` is the convention — already git-ignored in the default Pagesmith init.

## Build output

```bash
npx pagesmith-docs build
```

Writes into `outDir` and automatically creates:

- `.nojekyll` — stops GitHub Pages from dropping folders that start with `_`.
- `404.html` — ensures unknown paths still render through the Pagesmith router.
- Slashless canonical URLs with matching HTML files.
- `sitemap.xml` and `robots.txt` using `origin` + `basePath`.

Do not hand-edit any of these.

## GitHub Actions workflow

`.github/workflows/gh-pages.yml`:

```yaml
name: Deploy Docs

on:
  push:
    branches: [main]
  workflow_dispatch: {}

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-node@v5
        with:
          node-version: 24
          cache: npm
      - run: npm ci
      - run: npx pagesmith-docs build
      - uses: actions/upload-pages-artifact@v5
        with:
          path: gh-pages

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v5
```

Repo requirements:
- Settings → Pages → Source = "GitHub Actions".
- Default branch is `main` (or adjust the `branches:` field).

If diagrams need rendering during deploy, add a step before `pagesmith-docs build`:

```yaml
      - run: npx playwright install --with-deps chromium
      - run: npx diagramkit render . --force
```

## Custom domain

1. Set `origin` to the custom domain and `basePath: '/'`.
2. Add a `CNAME` file containing the bare domain (`docs.example.com`) inside `public/` or in `outDir`:
   - If committed to the repo, keep it under `public/CNAME`.
   - If you want Pagesmith to copy it during build, declare it in `assets`:

```json5
{
  assets: {
    passthrough: ["public/CNAME"],
  },
}
```

## Preview before deploying

```bash
npx pagesmith-docs preview
```

Preview serves directly from `outDir` so rebuilds apply without restarting. If links break in preview, they will break in production — fix before pushing.

## Static asset passthrough

Files the docs site should ship untouched (`llms.txt`, `robots.txt`, schema JSON, prompt files, research PDFs) go through passthrough assets:

```json5
{
  assets: {
    passthrough: [
      "llms.txt",
      "llms-full.txt",
      "public/prompts/**/*.md",
      "public/schemas/**/*.json",
    ],
  },
}
```

Path globs are relative to the config file. Output paths mirror the source tree inside `outDir`.

## Verify after deploy

1. Open `https://<origin>/<basePath>/` — home loads.
2. Click a sidebar entry — no broken CSS/JS (check Network for 404s).
3. Visit a non-existent URL — `404.html` responds with the Pagesmith shell, not GitHub's default 404.
4. View source — `<link rel="canonical">` matches the expected production URL.
5. `curl https://<origin>/<basePath>/sitemap.xml` returns XML with the right hostnames.

## Other hosts (sketch)

- **Vercel** / **Netlify**: build command `npx pagesmith-docs build`, publish dir `gh-pages`. Set `BASE_URL` env to `/` if hosting at root.
- **S3 + CloudFront**: sync `gh-pages/` to the bucket; set CloudFront default root object to `index.html`; add a behavior to serve `404.html` on missing paths if you want SPA-style fallback.
- **Self-hosted nginx**: copy `gh-pages/` to web root; ensure `try_files $uri $uri/ $uri.html /404.html;`.

## Gotchas

- `basePath` must start with `/` and not end with `/` (unless it is exactly `/`).
- If you change `basePath`, invalidate the Pages cache by re-triggering the deploy workflow.
- Custom domains require both `origin` update **and** a `CNAME` in the deploy artifact.
- Do not run `pagefind` or write into `outDir/` after the build — the deploy artifact ships exactly what's there.
- `gh-pages/` is in `.gitignore`. Do not commit build output.
- On first deploy, Pages may take a minute to propagate. Verify the Actions run succeeded before suspecting Pagesmith.
