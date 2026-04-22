---
title: 'adk-sync-contracts'
description: 'adk-sync-contracts'
artifact_kind: bin
---

# adk-sync-contracts

adk-sync-contracts

Propagates byte-identical copies of every file in `bin/canonical/`
into every `skills/<name>/references/`. Idempotent. Run by `bin/adk-validate`
before each validation pass; safe to run by hand any time.

Usage:
  bin/adk-sync-contracts            # propagate
  bin/adk-sync-contracts --check    # exit non-zero if any copy is out-of-sync
  bin/adk-sync-contracts --verbose  # show every file copied

## Usage

```bash
node bin/adk-sync-contracts
```

From an installed plugin the script is in `PATH`:

```bash
adk-sync-contracts
```

## Source

`bin/adk-sync-contracts` — Node.js CLI script.
