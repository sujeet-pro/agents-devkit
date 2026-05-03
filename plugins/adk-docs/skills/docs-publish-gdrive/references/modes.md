# `docs-publish-gdrive` — modes

Supports `--auto` (default) and `-i`. Does NOT support `--fix`:
publishing IS the mutation.

## `--auto` (default)

- Phases 0–3 run without approval gates.
- Phase 4 STILL asks once before publishing. Shared-state write.
- Phase 5 verifies and reports.

## `-i` / `--interactive`

- Per-phase approval gates.
- Useful when:
  - Folder or format are ambiguous.
  - You want to inspect the converted artifact before upload.
  - Human last-editor was detected.

## Guardrails (all modes)

1. Single ask before publish, every run.
2. Never overwrite human-authored item without second explicit
   opt-in.
3. **Never change sharing.** Zero exceptions.
4. Never move items.
5. Never delete items.
6. Cap of 1 item per invocation.
7. Pre- and post-publish sharing snapshot must match (modulo the
   service account). Drift = abort success.

## Flag combinations

| Combination | Effect |
| --- | --- |
| (no flags) | convert + existence-check + ask-once + publish + verify |
| `-i` | per-phase approval; ask-once still required |
| `--folder <id>` | override folder (CLI wins over `docs.md`) |
| `--format gdoc` | default; convert to GDoc ops |
| `--format md` | upload .md verbatim |
| `--format pdf` | render PDF via pandoc |

## Error behavior

- If pandoc is not installed (format=pdf): stop with:
  `brew install pandoc` (macOS) or the user's package-manager
  equivalent.
- If the connector is not connected: stop with:
  `claude mcp list` to verify, then the Google Drive workspace
  connector's enable flow.
