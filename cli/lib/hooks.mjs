// Hook config install — single file symlink per runtime (claude/cursor/codex).

import { existsSync } from "node:fs";
import { join } from "node:path";

import { ensureSymlink, pruneRepoLink } from "./symlinks.mjs";

export function installHookForRuntime({ runtime, hookPath, repoDir, dryRun, log, force = false }) {
  if (!runtime.hookSource || !hookPath) {
    return { runtime: runtime.id, skipped: true, reason: "no-hook-surface" };
  }
  const source = join(repoDir, runtime.hookSource);
  if (!existsSync(source)) {
    return { runtime: runtime.id, skipped: true, reason: "source-missing" };
  }
  const pruned = pruneRepoLink(hookPath, repoDir, { dryRun, log });
  // Hook paths often share a file with user-managed config (e.g.
  // ~/.claude/settings.json may be a symlink to a dot-files repo). Refuse
  // to clobber a foreign symlink — caller can re-run with `--force-hooks`
  // (not exposed yet) once they've moved their own settings out of the way.
  const result = ensureSymlink(source, hookPath, {
    dryRun,
    log,
    force,
    allowForeignReplace: false,
  });
  return { runtime: runtime.id, pruned, result };
}
