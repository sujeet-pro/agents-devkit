# `review-doc` — output format

## Status banner (each turn)

```
[adk:review-doc] mode=<X> auto-flag=<on|off> phase=<1|2|3|4>
```

## Default report

```
## Result
<one sentence>

## Decisions
<each decision picked under --auto, with one-line rationale>

## Validation
<fresh evidence: command output, screenshots, link checks>

## Residual risk / follow-ups
<bulleted, prioritized>
```

## Detailed report (`--verbose`)

Adds: full per-phase narrative, every validator entry, all command outputs.
