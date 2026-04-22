---
name: prj-doc-site-deploy
description: Build and publish this repo's @pagesmith/docs site, primarily to GitHub Pages but also adaptable to Vercel / Netlify / S3 / nginx. Configures origin, basePath, GitHub Actions workflow, custom domain CNAME, and asset passthrough. Reads node_modules/@pagesmith/docs/skills/pagesmith-docs-deploy-gh-pages/SKILL.md when present, falls back to the inline guidance below otherwise.
---

# Project: Deploy the Doc Site

## Read the source skill (locally installed first, fallback to inline)

1. **Try first**: `node_modules/@pagesmith/docs/skills/pagesmith-docs-deploy-gh-pages/SKILL.md`
   - Plus `node_modules/@pagesmith/docs/REFERENCE.md`
   - Plus `node_modules/@pagesmith/docs/schemas/pagesmith-config.schema.json`
2. **Fallback (inline below)**: only when `@pagesmith/docs` is not installed.

When the locally installed files exist, **they win over this inline body** on any conflict.

## When to use

- The user wants to publish the docs to GitHub Pages.
- A `.github/workflows/gh-pages.yml` needs to be created or fixed.
- The site is moving to / from a custom domain.
- Asset URLs are broken after deploy (basePath mismatch, missing `.nojekyll`, 404 fallback issues).
- The deploy needs to render diagrams in CI.

## When NOT to use

- The site isn't built yet → run `npx pagesmith-docs build` and fix errors first.
- Only previewing locally → `npx pagesmith-docs preview` (no deploy involved).

## Workflow

1. **Pick the host** — GitHub Pages (default), Vercel, Netlify, S3 + CloudFront, or self-hosted.
2. **Set `origin` + `basePath`** in `pagesmith.config.json5` (table below).
3. **Build locally**:
   ```bash
   npx pagesmith-docs build
   npx pagesmith-docs preview
   ```
   Both must exit 0 and the preview must serve correctly. If preview is broken, prod will be too.
4. **Wire the host-specific deploy** (GitHub Actions workflow, host config, etc.).
5. **Commit + push**, then watch the deploy run.
6. **Verify after deploy** (checklist below).
7. **Report** — host, URL, workflow file path, verify checklist results.

## Inline fallback

### Origin + basePath

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

`outDir: './gh-pages'` is the convention (already git-ignored in default Pagesmith init).

### Build output

```bash
npx pagesmith-docs build
```

Writes into `outDir` and automatically creates:
- `.nojekyll` (stops GitHub Pages from dropping `_`-prefixed folders)
- `404.html` (Pagesmith router fallback)
- Slashless canonical URLs with matching HTML files
- `sitemap.xml` and `robots.txt` using `origin` + `basePath`

Do not hand-edit any of these.

### GitHub Actions workflow

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
- Default branch is `main` (or adjust `branches:`).

### If diagrams need rendering during deploy

Insert before `pagesmith-docs build`:

```yaml
      - run: npx playwright install --with-deps chromium
      - run: npx diagramkit render . --force
```

(Skip the playwright step if the project is Graphviz-only.)

### Custom domain

1. Set `origin` to the custom domain and `basePath: '/'`.
2. Add a `CNAME` file containing the bare domain (`docs.example.com`) inside `public/`:

```json5
{
  assets: {
    passthrough: ["public/CNAME"],
  },
}
```

### Static asset passthrough

Files the docs site should ship untouched:

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

Path globs are relative to the config file; output paths mirror the source tree inside `outDir`.

### Verify after deploy

1. Open `https://<origin>/<basePath>/` — home loads.
2. Click a sidebar entry — no broken CSS/JS in Network tab.
3. Visit `/<basePath>/does-not-exist` — `404.html` responds with the Pagesmith shell.
4. View source — `<link rel="canonical">` matches the production URL.
5. `curl https://<origin>/<basePath>/sitemap.xml` returns XML with the right hostnames.

### Other hosts (sketches)

- **Vercel** / **Netlify**: build command `npx pagesmith-docs build`, publish dir `gh-pages`. Set `BASE_URL` env to `/` if hosting at root.
- **S3 + CloudFront**: sync `gh-pages/` to the bucket; CloudFront default root object `index.html`; behavior to serve `404.html` on missing paths if you want SPA-style fallback.
- **Self-hosted nginx**: copy `gh-pages/` to web root; `try_files $uri $uri/ $uri.html /404.html;`.

## Gotchas

- `basePath` must start with `/` and not end with `/` (unless it is exactly `/`). Everything else breaks asset URLs.
- If you change `basePath`, invalidate the Pages cache by re-triggering the deploy workflow.
- Custom domains need both `origin` update **and** the `CNAME` file in the deploy artifact.
- Do not run `pagefind` or write into `outDir/` after the build — the deploy artifact ships exactly what's there.
- `gh-pages/` is gitignored. Do not commit the build output.
- On first deploy, Pages may take a minute to propagate. Verify the Actions run succeeded before suspecting Pagesmith.

## Anti-patterns

- Setting `origin` to `http://localhost`. Use the real production origin even for local builds — Pagesmith uses it for canonical URLs and `sitemap.xml`.
- Committing `gh-pages/` because it "feels safer". The build is reproducible from source; committing the output causes merge churn.
- Skipping `npx pagesmith-docs preview` before deploying. Preview catches link / asset breakage before it goes live.
- Running `pagesmith-docs build` in CI without `npm ci` (use `npm ci`, not `npm install`, for reproducible deploys).
