# `audit-repo` — inventory rules

Detection rules for Phase 2. Each detected fact informs which dimension passes are run and which tools are used.

## Languages (by LOC)

Tools (preferred order; first available wins):

```bash
# Preferred: scc (fast + accurate, supports many languages)
scc --no-cocomo --format json .

# Fallback: cloc
cloc --json .

# Fallback: tokei
tokei --output json .

# Fallback: git ls-files + wc -l (slow; coarse)
for ext in $(git ls-files | grep -oE '\.[a-z]+$' | sort -u); do
  count=$(git ls-files "*$ext" | xargs -I {} wc -l {} 2>/dev/null | awk '{s+=$1} END {print s}')
  echo "$ext $count"
done | sort -k2 -rn | head -20
```

Output table in `inventory.md`: language, LOC, % of total. Sort by LOC desc.

## Framework / runtime

| Hint | Detection |
| --- | --- |
| Next.js | `package.json` has `next` dep; `app/` or `pages/` directory present |
| React | `package.json` has `react` dep |
| Vue | `package.json` has `vue` dep; `.vue` files present |
| Svelte | `package.json` has `svelte` dep; `.svelte` files present |
| Express | `package.json` has `express` dep |
| Fastify | `package.json` has `fastify` dep |
| NestJS | `package.json` has `@nestjs/core` dep |
| FastAPI | `requirements.txt` / `pyproject.toml` has `fastapi` dep |
| Django | `requirements.txt` has `django` dep; `manage.py` present |
| Flask | `requirements.txt` has `flask` dep |
| Spring Boot | `pom.xml` / `build.gradle` references `spring-boot-starter` |
| Gin (Go) | `go.mod` has `github.com/gin-gonic/gin` |
| Echo (Go) | `go.mod` has `github.com/labstack/echo` |
| Rails | `Gemfile` has `rails` |
| Sinatra | `Gemfile` has `sinatra` |
| Actix (Rust) | `Cargo.toml` has `actix-web` |
| Axum (Rust) | `Cargo.toml` has `axum` |
| Phoenix (Elixir) | `mix.exs` references `phoenix` |

If multiple frameworks detected (polyglot repo), list all.

## Node version

```bash
# .nvmrc
cat .nvmrc 2>/dev/null

# .node-version
cat .node-version 2>/dev/null

# package.json engines
jq -r '.engines.node // empty' package.json 2>/dev/null

# Dockerfile FROM line
grep -E 'FROM node:' Dockerfile* 2>/dev/null | head -1
```

## Dep manager

| Detection | Manager |
| --- | --- |
| `pnpm-lock.yaml` exists | pnpm |
| `yarn.lock` exists | yarn |
| `package-lock.json` exists | npm |
| `bun.lockb` exists | bun |
| `uv.lock` or `requirements.in` | uv |
| `poetry.lock` | poetry |
| `requirements.txt` only | pip |
| `Pipfile.lock` | pipenv |
| `go.sum` (with `go.mod`) | go modules |
| `Cargo.lock` | cargo |
| `Gemfile.lock` | bundler |

## Test framework

| Detection | Framework |
| --- | --- |
| `vitest.config.*` OR `package.json` has `vitest` dep | vitest |
| `jest.config.*` OR `package.json` has `jest` dep | jest |
| `package.json` has `mocha` dep | mocha |
| `cypress.config.*` | Cypress (e2e) |
| `playwright.config.*` | Playwright (e2e) |
| `pytest.ini` / `pyproject.toml [tool.pytest]` / `requirements*.txt` has `pytest` | pytest |
| `unittest` (no config; standard lib) | unittest |
| `*_test.go` files exist | go test |
| `Cargo.toml` (cargo test is built-in) | cargo test |
| `spec/` directory + `Gemfile` with `rspec` | RSpec |

## Lint tool

| Detection | Tool |
| --- | --- |
| `eslint.config.*` OR `.eslintrc.*` | eslint |
| `golangci.yml` OR `.golangci.yml` | golangci-lint |
| `pyproject.toml [tool.ruff]` OR `ruff.toml` | ruff |
| `.flake8` OR `setup.cfg [flake8]` | flake8 |
| `Cargo.toml` AND `cargo clippy` available | clippy |
| `.rubocop.yml` | rubocop |

## Type-check

| Detection | Tool |
| --- | --- |
| `tsconfig.json` exists; `strict: true` if mode-strict | tsc |
| `mypy.ini` OR `pyproject.toml [tool.mypy]` | mypy |
| `pyrightconfig.json` | pyright |
| (Go has built-in type-check via `go build`) | go build |
| (Rust has built-in type-check via `cargo check`) | cargo check |

For each, capture mode-strict status (e.g. `tsconfig.strict: true/false`; `mypy.disallow_untyped_defs: true/false`).

## CI provider

| Detection | Provider |
| --- | --- |
| `.github/workflows/*.yml` | GitHub Actions |
| `.gitlab-ci.yml` | GitLab CI |
| `Jenkinsfile` | Jenkins |
| `.circleci/config.yml` | CircleCI |
| `.buildkite/*.yml` | Buildkite |
| `bitbucket-pipelines.yml` | Bitbucket Pipelines |
| `azure-pipelines.yml` | Azure Pipelines |

Capture workflow count + names.

## Deployment

| Hint | Detection |
| --- | --- |
| Vercel | `vercel.json` OR `.vercel/` |
| Netlify | `netlify.toml` |
| AWS ECS | `infrastructure/ecs.tf` OR `task-definition.json` |
| AWS Lambda | `serverless.yml` OR `template.yaml` |
| Cloudflare | `wrangler.toml` |
| Fly.io | `fly.toml` |
| Heroku | `Procfile` |
| Kubernetes | `*.yaml` with `kind: Deployment` / `apiVersion: apps/v1` |
| Docker | `Dockerfile` (lone — no orchestration detected) |

## Observability

| Hint | Stack |
| --- | --- |
| `DD_API_KEY` referenced in CI / src | Datadog |
| `SENTRY_DSN` referenced in CI / src | Sentry |
| `NEW_RELIC_LICENSE_KEY` referenced | New Relic |
| `OTEL_*` env vars referenced | OpenTelemetry |
| `posthog` import | PostHog |

## Top-20 largest files

```bash
# Preferred: scc per-file output
scc --no-cocomo --by-file --format json . | jq -r '.[] | "\(.code) \(.filename)"' | sort -rn | head -20

# Fallback: find + wc
git ls-files | xargs -I {} wc -l {} 2>/dev/null | sort -rn | head -20
```

Outputs: `file path` + `LOC`. Used by the architecture pass for sampling.

## Top-20 most-changed files (last 6 months)

```bash
git log --since='6 months ago' --pretty=format: --name-only | sort | uniq -c | sort -rn | head -20
```

Outputs: `file path` + `commit count`. Used by the performance pass (most-changed often correlates with hot-path) and the quality pass.

## Repo metadata

| Item | Command |
| --- | --- |
| Total commits | `git rev-list --count HEAD` |
| Active contributors (last 30d) | `git log --since='30 days ago' --format=%aN | sort -u | wc -l` |
| Open PRs | `gh pr list --state open --json number | jq length` |
| Open issues | `gh issue list --state open --json number | jq length` |
| Last release tag | `git tag --sort=-v:refname | head -1` |

## Scope filter

When `--scope <path>` is set:

- Languages by LOC: limited to files under `<path>`.
- Top-20 largest: limited to files under `<path>`.
- Top-20 most-changed: limited to files under `<path>` (filter `git log` with `-- <path>`).
- CI / Deployment / Observability: still repo-wide (these are inherently repo-wide).

The inventory surfaces both the scope-limited and repo-wide values when relevant.

## Output: `inventory.md` (final shape)

See `references/output-format.md` (Phase 2 inventory table). Compact; reads top-down: languages → frameworks → dep mgr → test → lint → type → CI → deployment → observability → top-20 largest → top-20 most-changed → metadata.
