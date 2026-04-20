# Research Protocol

## Default order
1. Inspect the local repository.
2. Inspect the exact tool/framework version in use.
3. Read official docs.
4. Read maintained implementation references.
5. Compare local behavior against sources.
6. Record what is verified vs still uncertain.

## Evidence buckets
| Bucket | What belongs here |
| --- | --- |
| Verified | Directly supported by code, config, official docs, or runtime output |
| Inferred | Strong conclusion from partial evidence, marked as inference |
| Open | Not yet verified, requires follow-up |

## Output shape
- Question
- Current state / target state
- Repo evidence
- External evidence
- Conflicts (if any)
- Recommendation with confidence (high / medium / low)
- Validation plan
- Open issues

## Research rules
- Prefer official docs over blog posts.
- Prefer maintained repos over abandoned examples.
- Prefer the exact branch or released version in use.
- If docs and code disagree, call it out.
- Memory is never a `Verified` source.
