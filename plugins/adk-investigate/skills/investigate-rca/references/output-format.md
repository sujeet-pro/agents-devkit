# `investigate-rca` — output format

## Per-turn status banner

```
[adk-investigate:investigate-rca] task=<slug> phase=<1..7> mode=<auto|interactive>
```

## Final report

Written to `.temp/task-<slug>/investigation/rca.md`. Sections in this exact order, per `rca-template.md`:

```markdown
# RCA: <symptom> on <date> <time> UTC

## Summary
<one paragraph; exec audience; what happened, when, who was affected, what we did, current state>

## Timeline
| Time (UTC) | Event | Source |
| --- | --- | --- |

(Each row has a clickable source link — DD UI, Slack permalink, PR URL, etc. The first row may pre-date the symptom by hours / days if relevant — e.g. the migration that set up the bug.)

## Detection
- **Time to alert:** <duration>
- **Time to acknowledge:** <duration>
- <bullet about what worked / didn't in detection>

## Mitigation
- **Time to mitigate:** <duration>
- <action taken: rollback / flag-off / restart / etc.>
- <bullet about what worked / didn't>

## Root cause
<one paragraph, system-shaped. Never names an individual. Anchored to ≥2 corroborating sources cited in the timeline.>

**The system gap:** <one sentence naming the structural issue>

## Contributing factors
1. <factor 1: another system gap>
2. <factor 2>
3. ...

## Action items (5W frame)
1. **<short title>** [WHO: <owner>] [WHAT: <concrete deliverable>] [WHEN: <date>] [WHERE: <path or system>] [WHY: <one sentence>]
2. ...

## References
- Incident.md: <path>
- Statsig audit: <path>
- Git blame: <path>
- Mixpanel impact: <path> (if applicable)
- PR / commits: <links>
- Migration history (if applicable): <links>
- Slack thread: <permalink>
- Datadog dashboard at incident time: <link>
- Statsig audit entry (if applicable): <link>
- Vendor status pages (if applicable): <links>
```

## Rules

1. **Every timeline row has a source link.** No exceptions.
2. **"What worked" bullets in `Detection` and `Mitigation`.** The team learns what to keep.
3. **Root cause is system-shaped.** Never names an individual.
4. **Action items use the 5W frame.** Every item is testable.
5. **Contributing factors get their own action items** (or are explicitly marked "no action — this is fine").
6. **References are exhaustive.** Every artifact cited in the body has a link.
7. **No auto-publish.** The file lives in `.temp/`; the operator publishes via `/adk-docs:docs-publish-confluence` after review.

## Action item testability check

For each action item, the validator runs:

```text
test_phrase = ACTION_ITEM_WHAT.lower()
if any(weak_word in test_phrase for weak_word in [
  "be more careful", "improve", "communicate better", "watch closely",
  "pay attention", "make sure", "remember to"
]):
    REJECT — not testable. Re-write with a concrete deliverable.
```

Acceptable shapes for `WHAT`:
- "Add `<test>` in `<path>`" → testable: the test exists.
- "Configure `<setting>` to `<value>` in `<system>`" → testable: setting matches.
- "Document `<thing>` at `<path>`" → testable: file exists with the documented content.
- "Reduce `<X>` from `<Y>` to `<Z>`" → testable: measurement.

## Executive summary mode

If the operator passes `--exec` (future flag; not in v0.1):

- The `Summary` section becomes the lead.
- Timeline is collapsed to 5 key events.
- Action items are summarized as a bulleted list with ETAs.
- Other sections are linked rather than inlined.

For v0.1, no `--exec` flag; the standard format is used. The operator can manually extract the `Summary` for an exec audience.
