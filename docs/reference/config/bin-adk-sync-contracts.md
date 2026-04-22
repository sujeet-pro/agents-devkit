---
title: 'adk-sync-contracts'
description: 'Propagates byte-identical copies of bin/canonical/interaction-contract.md into every skills/<name>/references/ folder.'
artifact_kind: bin
---

# adk-sync-contracts

Propagates byte-identical copies of `bin/canonical/interaction-contract.md` into every `skills/<name>/references/interaction-contract.md`. Idempotent — safe to run by hand any time. Also invoked indirectly by `bin/adk-validate --fix`.

Other files in `bin/canonical/` (e.g. `system-prompt.md` used by the `SessionStart` hook) intentionally stay at the canonical path only and are NOT propagated into each skill.

## Usage

```bash
node bin/adk-sync-contracts            # propagate
node bin/adk-sync-contracts --check    # exit non-zero if any copy is out-of-sync
node bin/adk-sync-contracts --verbose  # show every file copied
```

From an installed plugin the script is on `PATH`:

```bash
adk-sync-contracts
```

Or via npm scripts:

```bash
npm run sync-contracts        # propagate
npm run validate:sync         # --check (CI-friendly)
```

## Source

`bin/adk-sync-contracts` — Node.js CLI script.
