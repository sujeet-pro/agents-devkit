// Read + append `~/.zshenv`. We treat it as a thin key/value store of
// `export KEY="VAL"` lines, ignoring everything else.

import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

const ZSHENV = join(homedir(), ".zshenv");

const EXPORT_RE = /^\s*export\s+([A-Z_][A-Z0-9_]*)\s*=\s*(.+?)\s*$/;

export function zshenvPath() {
  return ZSHENV;
}

/** Parse exports out of ~/.zshenv. Returns { KEY: "value" }. */
export function readZshenv() {
  if (!existsSync(ZSHENV)) return {};
  const out = {};
  const content = readFileSync(ZSHENV, "utf8");
  for (const line of content.split("\n")) {
    const m = line.match(EXPORT_RE);
    if (!m) continue;
    let val = m[2];
    // Strip surrounding quotes if present.
    if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
      val = val.slice(1, -1);
    }
    out[m[1]] = val;
  }
  return out;
}

/**
 * Append (or update) the given variables in ~/.zshenv.
 * Values present in `current` (parsed previously) are skipped if unchanged.
 */
export function upsertZshenv(vars, { dryRun = false, log = () => {} } = {}) {
  const current = readZshenv();
  const toWrite = [];
  for (const [key, value] of Object.entries(vars)) {
    if (current[key] === value) continue;
    toWrite.push([key, value]);
  }
  if (toWrite.length === 0) return { skipped: true, reason: "no-changes" };
  if (dryRun) {
    for (const [key, value] of toWrite) {
      log(`[dry-run] zshenv export ${key}=${redact(value)}`);
    }
    return { dryRun: true, count: toWrite.length };
  }
  let original = existsSync(ZSHENV) ? readFileSync(ZSHENV, "utf8") : "";
  if (original.length > 0 && !original.endsWith("\n")) original += "\n";
  const banner = "\n# Added by agents-devkit `npm run setup` on " + new Date().toISOString() + "\n";
  const lines = toWrite
    .map(([key, value]) => `export ${key}="${value.replace(/"/g, '\\"')}"`)
    .join("\n");
  writeFileSync(ZSHENV, original + banner + lines + "\n", "utf8");
  for (const [key] of toWrite) {
    log(`zshenv export ${key} written`);
  }
  return { written: true, count: toWrite.length };
}

function redact(v) {
  if (!v) return v;
  if (v.length <= 6) return "***";
  return v.slice(0, 2) + "***" + v.slice(-2);
}
