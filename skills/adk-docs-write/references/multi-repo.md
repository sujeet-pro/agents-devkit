# Multi-repo Context

`adk-docs-write` can pull context from one or more additional repositories beyond the host repo. This is useful when the deliverable describes a system that spans multiple repos (cross-repo migration, integration docs, multi-service onboarding, audit of a meta-project).

## How to pass repos

The user can supply additional repos via:

- **Cloned URL** — `https://github.com/<owner>/<repo>.git` (or any git URL). The skill clones into `.temp/reference-repos/<owner>__<repo>/` if not already present. Default branch unless a ref is specified (`<url>#<ref>`).
- **Local path** — absolute or relative path to an existing checkout. Used as-is; never modified.
- **Mix** — pass a list mixing URLs and paths.

## Where clones live

```
.temp/reference-repos/
  <owner>__<repo>/        # one folder per cloned repo
  <owner>__<repo>@<ref>/  # if a non-default ref was requested
```

`.temp/` is gitignored, so clones never enter the host repo's history.

## Per-repo handling

The skill processes each repo independently:

1. Run the skill's research/audit/doc-extraction steps inside the repo.
2. Tag every finding / quote / example with the repo of origin (`[<owner>/<repo>]` prefix).
3. Aggregate at the end with a per-repo section in the report.

## Auth

For private repos, the skill assumes `git` already has credentials configured (SSH agent, gh auth, credential helper). It will NOT prompt for tokens; if a clone fails with auth error, the skill stops and tells the user how to fix it.

## Ref discipline

If you want a stable reference, pass a tagged ref (`<url>#v2.4.0`) so re-runs read the same code. Branch refs (`<url>#main`) re-resolve at clone time and may drift between runs.
