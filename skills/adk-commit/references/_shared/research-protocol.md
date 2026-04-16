# Research Protocol

## Purpose

Use this protocol when a skill needs deep research, upstream comparison, or fact-sensitive updates.

## Default Order

1. Inspect the local repository.
2. Inspect the exact tool or framework version in use.
3. Read official docs.
4. Read maintained implementation references.
5. Compare local behavior against sources.
6. Record what is verified and what is still uncertain.

## Structured Deep Research

- Define the research question in one sentence.
- Capture the current state, target state, change tolerance, desired confidence, and requested artifact before searching.
- Split the question into claims that can be checked.
- Collect repo evidence first.
- Collect official-source evidence second.
- Collect implementation-pattern evidence third.
- Note conflicts explicitly.
- Resolve conflicts before recommending changes.

## Brainstorming-Assisted Design Closure

When research is part of a broader decision workflow:

- state the current state and target state explicitly
- state how much blast radius is acceptable: `surgical`, `bounded`, or `transformative`
- state the desired confidence threshold before finalizing direction
- state whether the next artifact should be `none`, `proposal`, `prd`, `rfc`, `hld`, `lld`, `tdd`, `plan`, or `all`
- track which uncertainty is blocking direction and which is merely informative
- stop asking questions once the remaining unknowns no longer change the chosen path

## Evidence Buckets


| Bucket   | What belongs here                                            |
| -------- | ------------------------------------------------------------ |
| Verified | Directly supported by code, config, docs, or runtime output  |
| Inferred | Strong conclusion from partial evidence, marked as inference |
| Open     | Not yet verified, requires follow-up                         |


## Output Shape

- Question
- Current state / target state
- Desired confidence / change tolerance
- Repo evidence
- External evidence
- Conflicts
- Recommendation
- Recommended route
- Validation plan
- Open issues

## Research Rules

- Prefer official docs over blog posts.
- Prefer maintained repos over abandoned examples.
- Prefer the exact branch or released version in use.
- If the docs and the code disagree, call it out.
- If research changes skill behavior, record the source in `ai-guidelines/sources/registry.json`.

## Mandatory Checks For Skill Updates

- Did the upstream source materially change behavior or only wording?
- Is the change relevant to one skill, one family, or the full catalog?
- Does the change affect user-facing instructions, validation commands, or attribution?
- Can the change be validated locally?
- Does the change alter brainstorming thresholds, fallback behavior, or artifact routing?

## Concise Reporting

Use bullets, not essays:

- what was checked
- what source was used
- what changed
- what action follows

Then ask whether a deeper explanation is needed.