# Source-driven discipline — citing official docs over training data

Optional reference loaded by `plan-research` (and recommended for `build-feature` / `build-migrate`) when the work depends on framework / library / runtime behavior. Encodes the "training data is not authority" discipline.

## Why this matters

LLM training data:

- Is months-to-years stale relative to current versions.
- Is sampled from the public web, where wrong answers outweigh right ones.
- Conflates major versions of the same framework into one mental model.
- Confidently asserts deprecated APIs as current.

The fix: **detect the version the user is on, fetch the current official docs for the feature, cite the URL in your output.**

## Source hierarchy

Use sources in this order. Stop at the highest authoritative one that answers the question.

1. **Official documentation** at the version the user uses.
   - React: `react.dev` for v18+; older versions at `legacy.reactjs.org`.
   - Node: `nodejs.org/docs/latest-v<X>.x/api/` (pin the major).
   - TypeScript: `typescriptlang.org` (release notes for behavior change).
   - Vite / Vitest / Rollup / esbuild / oxc / Bun / Deno: their own docs sites.
   - Python: `docs.python.org/3.<x>/`.
   - Django / Flask / FastAPI: their docs at the version on `requirements.txt`.
   - Go / Rust / Ruby / etc.: official.
2. **Official changelog / release notes / migration guide** for the version transition.
3. **MDN / web.dev** for browser / DOM / web platform features.
4. **caniuse.com** for browser support matrices.
5. **node.green** for Node feature support.
6. **TC39 proposal repos** for JS proposals.
7. **W3C / WHATWG specs** for protocol-level questions.
8. Vendor official docs (AWS, GCP, Azure) for cloud APIs.
9. The library's own GitHub repo (README, examples folder, issues for known bugs).

## Anti-sources (do not use as authority)

- **Stack Overflow answers** — often outdated; the accepted answer is years old; comment threads contain the correction.
- **Random blog posts** ("How to use X in 2022") — usually outdated within months.
- **AI-generated tutorials** (other LLM output, summarized articles) — propagates errors.
- **Course materials** without a date and version — assume stale.
- **The training data itself** — never cite "based on what I know about X".

You CAN read these for ideas / examples, but the FINAL claim must be backed by an official source.

## Detection: what version is the user on?

Read the lockfile / manifest before claiming framework behavior.

| Stack | File to read | Field |
| --- | --- | --- |
| Node / npm | `package.json` + `package-lock.json` | `dependencies.<name>` (resolved) |
| Python | `pyproject.toml` / `requirements.txt` / `Pipfile.lock` / `uv.lock` / `poetry.lock` | direct + transitive |
| PHP | `composer.json` + `composer.lock` | `require` |
| Go | `go.mod` | `require` |
| Rust | `Cargo.toml` + `Cargo.lock` | `[dependencies]` |
| Ruby | `Gemfile` + `Gemfile.lock` | locked version |
| Java / Kotlin | `pom.xml` / `build.gradle` / `build.gradle.kts` | `dependencies` |
| iOS | `Package.swift` / `Podfile.lock` | resolved |
| Android | `build.gradle.kts` | `implementation(...)` |

For runtimes (Node, Python, Bun, Deno):

- `.nvmrc` / `.tool-versions` / `engines` field.
- `python-version` / `pyproject.toml [tool.poetry.dependencies] python`.
- `Dockerfile` `FROM` line for containerized runs.

## Output discipline

When you make a claim about framework behavior, format your output as:

```markdown
- **Verified** (cite official source): React 19 Server Components do X (https://react.dev/reference/rsc/...).
- **Inferred** (from version + behavior nearby): Likely supported on the user's pinned 19.0.5 because X.
- **Unverified** (no doc found, or doc unclear): Behavior of X under condition Y is not documented; verify manually.
```

Use this **three-bucket** structure (`Verified` / `Inferred` / `Unverified`) explicitly in any research output, including the report from `plan-research`.

## Citation format

For verified claims, include the **deep link** with anchor when possible:

```
React docs (v19) — useDeferredValue: https://react.dev/reference/react/useDeferredValue#parameters
Vite config — server.proxy: https://vite.dev/config/server-options.html#server-proxy
PostgreSQL 16 docs — CREATE INDEX CONCURRENTLY: https://www.postgresql.org/docs/16/sql-createindex.html#SQL-CREATEINDEX-CONCURRENTLY
```

Avoid:

- Citing the search engine result page.
- Citing "the docs" without a URL.
- Citing an archived blog post when the current docs cover it.

## When the docs disagree with the code

Surface the conflict explicitly. Do not paper over it.

- "React docs say `useEffect` cleanup runs before re-render; the codebase has a comment saying it runs after — which is correct depends on the version, please confirm."

## When you cannot verify

Mark the claim **UNVERIFIED** in the output. Do not silently downgrade your confidence and present the claim anyway.

## Anti-patterns

- "I'm confident about this API" — confidence is not citation.
- "Fetching docs wastes tokens" — wrong code wastes far more.
- "The docs won't have what I need" — check first; you'd be surprised.
- "I'll just mention it might be outdated" — too vague; pick Verified / Inferred / Unverified.
- "This is a simple task, no need to check" — simple tasks built on stale APIs still break.
