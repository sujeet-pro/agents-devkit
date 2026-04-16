# Composable Workflows

Define reusable multi-skill pipelines as YAML files. Workflows chain ADK skills in sequence with optional conditions and parameters.

## Format

```yaml
name: pipeline-name
description: What this workflow accomplishes
steps:
  - skill: <skill-name>
    args: "<arguments>"
    condition: "<optional condition>"
```

Each step invokes an ADK skill. Steps execute in order. If a step fails, the pipeline stops and reports the failure point.

## Usage

Reference a workflow file when prompting:

```
Run the workflow in workflows/full-feature.yaml for user authentication
```

## Parameters

Workflows support parameter substitution with `${PARAM}` syntax:

```yaml
steps:
  - skill: adk-build
    args: "${TASK}"
```

Pass parameters when invoking: `Run workflows/full-feature.yaml with TASK="add OAuth2 login"`.

## Conditions

Steps can declare conditions that are evaluated before execution:

| Condition | Meaning |
|-----------|---------|
| `has-tests` | Only run if the project has a test suite |
| `has-pr` | Only run if a PR exists for the current branch |
| `complexity >= medium` | Only run for medium+ complexity tasks |

## Examples

See the YAML files in this directory for ready-to-use pipelines.

The canonical end-to-end feature flow now starts with `adk-brainstorm`, then routes into `adk-spec`, `adk-plan`, `adk-build`, and follow-up review or docs steps as needed.
