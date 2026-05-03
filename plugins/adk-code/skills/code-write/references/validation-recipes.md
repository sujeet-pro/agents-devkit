# `code-write` — validation recipes

Per-stack typecheck + lint + test commands. Each row is the "if no `repos.md` `notes` and no `package.json scripts` say otherwise, default to this" recipe. The skill **always prefers the repo's documented commands** — these are last-resort defaults.

## Resolution order

1. `~/.config/adk/repos.md` `repos[].notes` — operator-supplied per-repo guidance.
2. `package.json scripts` (Node), `pyproject.toml [tool.poe.tasks]` / `Makefile` (Python), `Makefile` / `build.gradle` (JVM), `Cargo.toml` (Rust), `go.mod` + `Makefile` (Go).
3. `CONTRIBUTING.md` — sometimes documents the canonical commands.
4. `AGENTS.md` / `CLAUDE.md` — sometimes pins the dev-loop commands.
5. The recipe table below.

## Recipes

### TypeScript (Node, plain)

```bash
# typecheck
npx tsc --noEmit

# lint
npx eslint . --max-warnings 0

# test (Vitest)
npx vitest run

# test (Jest)
npx jest --ci

# test (node:test)
node --test
```

### TypeScript (monorepo with pnpm + turbo)

```bash
pnpm typecheck      # if defined as turbo task
pnpm lint --max-warnings 0
pnpm test --filter <pkg>     # scope to one package
```

### React / Next.js

```bash
npm run typecheck
npm run lint -- --max-warnings 0
npm run test -- src/<area>     # scoped
npm run build                  # only as a final smoke check; expensive
```

### Node + ESM (pure)

```bash
node --test --experimental-vm-modules src/**/*.test.mjs
```

### Python (pip)

```bash
# typecheck
mypy <pkg>

# lint
ruff check <pkg>
ruff format --check <pkg>

# test
pytest <pkg> -x
```

### Python (poetry)

```bash
poetry run mypy <pkg>
poetry run ruff check <pkg>
poetry run pytest <pkg>
```

### Python (uv)

```bash
uv run mypy <pkg>
uv run ruff check <pkg>
uv run pytest <pkg>
```

### Kotlin (Gradle)

```bash
./gradlew :<module>:compileKotlin
./gradlew :<module>:detekt          # if detekt configured
./gradlew :<module>:test
./gradlew :<module>:check           # superset; expensive — last
```

### Java (Maven)

```bash
./mvnw -pl <module> compile
./mvnw -pl <module> spotless:check
./mvnw -pl <module> test
```

### Java (Gradle)

```bash
./gradlew :<module>:compileJava
./gradlew :<module>:check
./gradlew :<module>:test
```

### Go

```bash
go build ./...
go vet ./...
golangci-lint run ./...
go test ./...
```

### Rust

```bash
cargo check
cargo clippy --all-targets -- -D warnings
cargo fmt -- --check
cargo test
```

### Ruby (Rails / bundler)

```bash
bundle exec rubocop
bundle exec rspec spec/<area>
bundle exec rake test         # for Minitest
```

### Swift

```bash
swift build
swift test
swiftlint
```

## Scoping rules

- **Always scope to the affected package / area** when the commands support it. Running the whole monorepo's tests is wasteful when you changed one package.
- **Run typecheck first** — fastest signal. Lint second. Tests last (slowest, gives behavior signal).
- **`--max-warnings 0` only if the repo's CI does.** Some repos run lint with warnings allowed; mirror that policy. Find it in `.github/workflows/*.yml` or `CONTRIBUTING.md`.

## Build is NOT default validation

`npm run build`, `./gradlew build`, `cargo build --release`, etc. are expensive and rarely add signal beyond typecheck + tests. Run them only:

- When the change touches build config (webpack, esbuild, gradle, etc.).
- When the change introduces a new dependency.
- As a final smoke check before reporting done — under `--auto`, optional; under `-i`, ask first.

## Capturing output

Capture each command's stdout + stderr to `.temp/task-<slug>/validation/per-skill/code-write.md` under a `## Validation log` heading. Truncate stdout to the last 100 lines if it's longer (warn that it was truncated; full output is in the terminal scrollback).

```markdown
## Validation log

### typecheck — `npx tsc --noEmit`
Exit: 0
Output:
<stdout, truncated if >100 lines>

### lint — `npx eslint . --max-warnings 0`
Exit: 0
Output:
<stdout>

### test — `npx vitest run src/foo`
Exit: 0
Output:
14 tests passed in 0.42s
```

## Handling missing tooling

If a documented command's tool is not installed (`tsc: command not found`, `mypy: command not found`):

1. Don't auto-install.
2. Surface in `validation/per-skill/code-write.md`: "MISSING tool: `<tool>` — install with `<install command>`".
3. Skip that step + record as `skipped` in the validation evidence; do NOT silently treat as pass.
4. If the missing tool is critical (typecheck on a typed repo, tests on any repo), STOP and ask the operator.
