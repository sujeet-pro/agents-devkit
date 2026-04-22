# Multi-repo Context for `adk-docs-review`

`adk-docs-review` can pull source-of-truth context from one or more additional repositories beyond the host repo. This is useful when the doc describes a system that spans multiple repos (cross-repo migration guide, integration docs, multi-service onboarding, audit of a meta-project).

## How to pass repos

The user can supply additional repos via:

- **Cloned URL** — `https://github.com/<owner>/<repo>.git` (or any git URL). The skill clones into `.temp/reference-repos/<owner>__<repo>/` if not already present. Default branch unless a ref is specified (`<url>#<ref>`).
- **Local path** — absolute or relative path to an existing checkout. Used as-is; never modified.
- **Mix** — pass a list mixing URLs and paths.

Pass via `--repo <url-or-path>` (repeatable) on the command line.

## Where clones live

```
.temp/reference-repos/
  <owner>__<repo>/        # one folder per cloned repo
  <owner>__<repo>@<ref>/  # if a non-default ref was requested
```

`.temp/` is gitignored, so clones never enter the host repo's history.

## Per-repo handling

The skill processes each repo independently:

1. Run the source-of-truth-resolution and read steps inside the repo.
2. Tag every finding / quote with the repo of origin (`[<owner>/<repo>]` prefix on the finding title).
3. Aggregate at the end with a per-repo section in the report's findings if multi-repo context was used.
4. The validator log (`.temp/notes/doc-review-<slug>-validator.md`) records which repos were consulted for which findings.

## Auth

For private repos, the skill assumes `git` already has credentials configured (SSH agent, gh auth, credential helper). It will NOT prompt for tokens; if a clone fails with auth error, the skill stops and tells the user how to fix it.

## Ref discipline

If you want a stable reference, pass a tagged ref (`<url>#v2.4.0`) so re-runs read the same code. Branch refs (`<url>#main`) re-resolve at clone time and may drift between runs.

## Citation in findings

Multi-repo findings cite source like:

```
**Source-of-truth:** `.temp/reference-repos/owner__repo/src/cli/index.ts:42-58` (cloned 2026-04-21, ref=v3.0.0)
```

The retrieval date AND the ref both matter — without them, a future reviewer cannot reproduce.

## When NOT to use multi-repo

- The doc only describes the host repo.
- The doc references external repos but only for context, not as source-of-truth (don't try to validate against them).
- A finding can be made from the doc alone (e.g., a typo, a broken internal link) — don't clone other repos to confirm.
