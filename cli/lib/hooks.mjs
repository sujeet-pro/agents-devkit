// Hook config install — single file symlink per runtime (claude/cursor/codex).

import { existsSync } from "node:fs";
import { join } from "node:path";

import { ensureSymlink, pruneRepoLink } from "./symlinks.mjs";

export function installHookForRuntime({ runtime, hookPath, repoDir, dryRun, log }) {
  if (!runtime.hookSource || !hookPath) {
    return { runtime: runtime.id, skipped: true, reason: "no-hook-surface" };
  }
  const source = join(repoDir, runtime.hookSource);
  if (!existsSync(source)) {
    return { runtime: runtime.id, skipped: true, reason: "source-missing" };
  }
  const pruned = pruneRepoLink(hookPath, repoDir, { dryRun, log });
  const result = ensureSymlink(source, hookPath, { dryRun, log });
  return { runtime: runtime.id, pruned, result };
}
