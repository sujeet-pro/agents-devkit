# `docs-write` — anti-patterns

## Content

- **Generic README full of placeholders.** Every section must carry
  the repo's actual values — no `<your service name>`, no `[fill in]`,
  no lorem ipsum. If a value is genuinely unknown, leave a `TODO:
  verify` and surface it in the report.
- **Marketing copy.** "A blazing-fast, enterprise-grade order service"
  is adjective soup. Replace with "Handles ~2k orders/min at p99
  420ms" — cite `docs.md.slo_thresholds` or the latest DD dashboard
  screenshot path.
- **Training-data defaults.** The reader cares what THIS repo does,
  not what a generic Spring Boot app does. Don't describe "typical"
  Spring-Boot config; describe `application.yml` at the exact path.
- **Speculation.** "The service probably retries on 5xx" without
  opening `RetryPolicy.kt` is a Blocker-level hallucination.
  Verify or omit.
- **Paraphrasing code snippets.** Copy verbatim with the actual
  variable names. "The method returns the user id" is weaker than the
  three-line snippet that shows the signature and return type.

## Structure

- **Nested headings for a 200-word section.** If you need `###` inside
  a section that short, the section is mis-sized — flatten.
- **Cross-references that don't resolve.** "See §5.2 below" when
  §5.2 doesn't exist. Link concretely or delete the pointer.
- **Duplication across sections.** The "Install" section and the
  "Quick start" section saying the same thing. Keep one; link from
  the other.
- **TODOs in the shipped doc.** Resolve them before `--fix` promotes
  to the canonical path.

## External content

- **Quoting >15 words from upstream docs.** Copyright + it's already
  on the web. Link instead.
- **Copying a vendor's 50-line "how to set up X" section.** Link to
  the vendor; add the 3 lines specific to this repo.

## Process

- **Writing before reading.** The cost of a wrong paragraph is weeks
  of wrong mental model for readers. Read first.
- **Skipping the evidence map.** If `sources.md` is empty, the prose
  has no spine. The skill validator blocks `--fix` when evidence is
  missing.
- **Running `git commit` or `git push`.** This skill writes and
  stages; the user commits via `/adk-docs:docs-commit-message --fix`.
- **Overwriting a human-authored file without asking.** The `--fix`
  gate asks once, even under `--auto`.

## Audience

- **One doc for both PM and engineer without a TL;DR.** If you need
  to serve both, the `mixed` calibration gives you a 3-sentence TL;DR
  for the PM at the top and the full body for the engineer below.
- **Over-explaining to an engineer.** If the audience is `engineer`,
  don't define what a Docker container is.
- **Under-explaining to a PM.** If the audience is `pm`, outcome
  first, mechanism second. The PM doesn't care what
  `@Transactional(isolation = REPEATABLE_READ)` means.
