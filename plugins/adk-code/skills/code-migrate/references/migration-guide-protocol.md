# `code-migrate` — migration-guide protocol

How to read, quote, and apply an upstream migration guide. The guide is the source of truth; everything that follows must trace back to it.

## What counts as an "official upstream migration guide"

Authoritative (use these):

| Source | Example URL pattern |
| --- | --- |
| The framework's own documentation site | `https://react.dev/blog/<release>`, `https://vuejs.org/guide/migration/`, `https://nextjs.org/docs/app/upgrading` |
| The framework's GitHub release notes | `https://github.com/<org>/<repo>/releases/tag/v<version>` |
| The framework's GitHub Wiki | `https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.0-Release-Notes` |
| The destination tool's "Migrating from X" page | `https://vitest.dev/guide/migration.html`, `https://vite.dev/guide/migration.html` |
| Runtime release notes | `https://nodejs.org/en/blog/release/v20.0.0`, `https://kotlinlang.org/docs/whatsnew20.html` |
| Java JEPs (for JDK upgrades) | `https://openjdk.org/jeps/<n>` |

NOT authoritative (use only as supplementary context):

- Blog posts (even high-quality ones).
- StackOverflow answers.
- Older release notes (read the LATEST guide for X→Y, not Y-1→Y).
- AI-generated migration guides.
- Community migration codemods (use them to apply changes, but verify each transformation against the official guide).

## Fetching protocol

1. Identify the canonical guide URL (table above; if uncertain, ask under `-i`; under `--auto`, search the official docs domain).
2. **WebFetch** the URL.
3. If the page returns a JS-only client (rare for docs sites), try the GitHub mirror or print version.
4. Save the fetched content to `.temp/task-<slug>/migration-notes.md` with:
    - The source URL.
    - The ISO timestamp of the fetch.
    - The version observed (sometimes the page is "preview" or "RC").

If the fetch fails (404, paywall, rate-limit), STOP. Do not proceed with a half-remembered guide.

## Quoting (≤15 words per quote)

For every breaking-change rule we are applying, quote ≤15 words from the guide verbatim. Why:

- The reviewer can verify the change against the guide quickly.
- It prevents "AI-paraphrased migration" syndrome where the model mis-remembers the rule.
- It bounds the legal risk of long quotation.

### Good quote shapes

- `"useRef must now be called with one argument"` — 8 words.
- `"javax.* is replaced by jakarta.* in Spring Boot 3"` — 9 words.
- `"context can render directly: <Context value={...}>"` — 6 words.

### Bad quote shapes

- A 60-word block describing the rule + rationale + example. (Trim to the rule.)
- A 3-word fragment that loses meaning ("`useRef` is now required"). (Add the predicate.)
- A paraphrase ("The new useRef requires an argument"). (Verbatim, not paraphrase.)

If the rule cannot be expressed in ≤15 words, the rule is probably "this thing changed in 5 ways"; split it into 5 sub-rules each with its own ≤15-word quote.

## Applies / partial / no

For each rule, label its applicability with one-line evidence:

- **`applies: yes`** — "we use this pattern in 38 sites across 11 files (`grep` confirmed)".
- **`applies: partial`** — "we use this in 4 sites, but they're all already on the new shape because of an earlier refactor".
- **`applies: no`** — "we don't use this pattern (`grep` returned 0 matches)".

The label drives whether the rule is in the inventory.

## Translating a rule into a group

A guide rule like "useRef must be called with one argument" becomes a group with:

- **Pattern**: `useRef\(\s*\)` (regex) or `useRef()` (literal).
- **Strategy**: mechanical — for each match, change `useRef()` to `useRef(null)` (or `useRef<T>(null)` if generic).
- **Validation**: typecheck (TypeScript will flag any miss) + tests scoped to the changed files.

Some rules don't translate to mechanical changes:

- **"Component <Foo> is removed; use <Bar>"** — manual: each call-site needs the Foo→Bar refactor, possibly with prop changes.
- **"Behavior of useEffect cleanup runs at a different lifecycle"** — semantic change; needs careful review of each useEffect that uses cleanup.

Mark these "manual" in the plan; budget more time per call-site.

## Deferring rules

Not every guide rule must be applied in this task:

- **Required rules** — must apply or the new version doesn't work. Address all in this task.
- **Recommended (highly) rules** — strongly suggested by the guide. Default: apply. Surface in Decisions.
- **Recommended (optional) rules** — best-practice for the new version. Default: defer. List in residual risk for a follow-up `code-write`.
- **Removed APIs (deprecated, not gone)** — the old API still works but logs a warning. Default: defer; flag in residual risk.

The report's `## Items NOT applied` section is the explicit log of deferrals.

## Cross-checking

After Phase 5 (execute), cross-check:

- Every "applies: yes" rule from the inventory has a corresponding group in the plan.
- Every group in the plan has a per-group validation entry.
- Every rule applied has a quote in `migration-notes.md`.

If the cross-check fails, the migration is incomplete; surface the gap.

## Codemods

Some migrations have official codemods (e.g. `npx react-codemod`, `@codemod-com/cli`). Using them:

- **Read the codemod's source / docs** to know exactly what it changes. Don't run blind.
- **Run the codemod under the same group structure**: one group = one codemod transform.
- **Verify the codemod's output** matches the guide's rule. Codemods sometimes lag; cross-check.
- **Run with `--dry-run` first** if the codemod supports it. Inspect the diff before applying.

## Long-tail rules

Some migration guides have ~80 rules; most don't apply to any given codebase. The protocol:

- Skim the guide; identify "Required" vs "Recommended" sections.
- For each Required rule, do the inventory check.
- For Recommended rules, only inventory if the operator opts in (under `-i`) or if the rule is "highly recommended".

This keeps `migration-notes.md` and `migration-inventory.md` focused on what matters for THIS codebase.
