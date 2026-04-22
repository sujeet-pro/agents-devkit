# Clarifying Questions for `adk-docs-review` (default-ask mode)

When running without `--auto`, the skill asks these questions in order, one at a time, and waits for an answer before moving on. Each question presents 2-3 explained options where applicable; the "How to pick" guidance is the rubric the user (or the skill under `--auto`) uses to choose.

Under `--auto`, the skill picks the option marked `(default)` in each question without asking, and lists every choice it auto-picked in the final report.

### Question 1

**Q:** Where is the doc (path or URL)?

**How to pick:** Required. Local path → `--mode local`. `https://*.atlassian.net/wiki/...` URL → `--mode confluence`. Other public URL → `--mode local` (fetched read-only; no comments posted).

### Question 2

**Q:** Where is the source-of-truth (path, URL, or 'inferred from doc')?

**How to pick:** Explicit > inferred. State the file/dir/URL the doc claims to describe. If you say "inferred from doc", the validator will surface the inference in WARN — fine for low-stakes reviews, not for pre-publish checks.

### Question 3

**Q:** Mode: local (Markdown report only) or confluence (post inline + footer comments)?

**How to pick:**

- `local` `(default)` — Markdown / RST / HTML files on disk or fetched read-only. Output is a Markdown report under `.temp/reports/`.
- `confluence` — page is on Confluence; the skill posts inline + footer comments back. Requires Atlassian MCP or REST credentials.

### Question 4

**Q:** Focus: accuracy / freshness / structure / readability / completeness / all?

**How to pick:** `all` `(default)` — first review of a doc; broad coverage. Narrow when iterating after a fix pass or when the doc is huge.

### Question 5 (Confluence mode only)

**Q:** Post mode: dry-run (report only) or post (inline + footer)?

**How to pick:**

- `dry-run` `(default)` — first run, so the user can inspect findings before they hit the page.
- `post` — after explicit approval, OR when `--auto` is set, OR after iterating on the dry-run findings.

### Question 6 (Confluence mode only)

**Q:** Reconciliation aggressiveness on existing comments?

**How to pick:**

- `validate-then-keep` `(default)` — re-validate every existing thread; reply on the ones that drifted; do not unilaterally close anything.
- `aggressive-cleanup` — also dismiss threads that are clearly no-longer-applicable. Use when the page has been edited many times and old threads are noise.
- `read-only` — do NOT reply on existing threads at all; just produce new findings. Use when re-reviewing without authority over the previous reviewer's comments.

## Standard option-presentation shape

Where the answer is multiple-choice, present each option as:

```
### Option <A | B | C>: <short label>
- What it does: <one sentence>
- Pros: <2-3 bullets>
- Cons: <2-3 bullets>
- Best when: <one sentence with a concrete signal>
- Blast radius: surgical | bounded | transformative
- Reversibility: easy | moderate | hard
```

Mark exactly one option `(default)` and say in one sentence why it is the safest pick for the current evidence.
