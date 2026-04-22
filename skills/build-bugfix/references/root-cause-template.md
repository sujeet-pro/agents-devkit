# `build-bugfix` — root-cause template

`.temp/task-<slug>/root-cause.md`:

```markdown
# Root cause — <bug summary>

## Symptom
<observable behavior the user/customer sees>

## Trigger
<the action / input / state that causes the symptom>

## Repro
1. <step>
2. <step>
3. Observe: <buggy outcome>

Expected: <correct outcome>

## Investigation
- Read: `path/to/file.ts:lines`
- Hypothesis 1: ... — ruled out because ...
- Hypothesis 2: ... — confirmed because ...

## Cause (one paragraph)
<concise explanation of what's wrong: which code, which condition, why it produces the symptom>

## Fix (one paragraph)
<concise explanation of the patch: what changes, why this is the minimal correct fix>

## Risk
<what else might this affect; what's the blast radius of the fix>

## Test that locks the regression
<file + brief description of the test>
```
