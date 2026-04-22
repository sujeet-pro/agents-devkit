# `review-doc` — dimension passes

Run each pass independently; collect findings per pass; merge at the end.

## Accuracy
For every factual claim in the doc:
- Resolve the file/URL it cites.
- Read the current state.
- If they disagree → finding (Blocker if user-facing; Critical if dev-facing).

## Freshness
- "Last updated" timestamp (if present) — flag if > 6 months and core area.
- Deprecated APIs / library versions — flag.
- Dead links — flag (run quick HEAD requests; ignore intranet that requires auth).
- References to obsolete tools (e.g. recommends a tool the team replaced).

## Structure
- Heading hierarchy: only one H1; H3 should not skip H2.
- Table of contents present for docs > 500 lines.
- Sections in expected order (overview / prereqs / steps / verification / troubleshooting / refs).
- Code blocks have language hints.

## Completeness
- Prereqs section.
- Failure modes / troubleshooting section.
- "Last verified by" / owner.
- Cross-links to related docs.
- Examples for non-obvious behavior.

## Readability
- Avg sentence < 25 words.
- Jargon defined on first use.
- Terminology consistent (e.g. "user" vs "customer" — pick one).
- Paragraphs < 5 sentences.
- Lists where prose is repetitive.
- Active voice.
