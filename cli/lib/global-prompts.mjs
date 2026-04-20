// Manage a "global prompts" block inside each runtime's memory file.
//
// The block is fenced by START/END markers so it can be regenerated
// idempotently. Existing user content outside the block is preserved.

import { existsSync, mkdirSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";

const START = "<!-- adk:global-prompts:start -->";
const END = "<!-- adk:global-prompts:end -->";

export function discoverGlobalPrompts(repoDir) {
  const dir = join(repoDir, "global-prompts");
  if (!existsSync(dir)) return [];
  let names;
  try {
    names = readdirSync(dir);
  } catch {
    return [];
  }
  return names
    .filter((n) => n.endsWith(".md") && n !== "README.md")
    .map((n) => ({ name: n, path: join(dir, n) }))
    .sort((a, b) => a.name.localeCompare(b.name));
}

function buildBlock(prompts) {
  const lines = [
    START,
    "<!-- Managed by agents-devkit. Re-run `npm run setup` to update. -->",
    "",
    "# Global Prompts (always read and obey)",
    "",
    "The following prompts are managed by agents-devkit and apply to **every**",
    "session, regardless of project. Read them in full at the start of each",
    "session and obey them throughout.",
    "",
  ];
  for (const p of prompts) {
    lines.push(`- \`${p.path}\``);
  }
  lines.push("", END);
  return lines.join("\n");
}

function stripBlock(content) {
  if (!content.includes(START)) return content;
  const startIdx = content.indexOf(START);
  const endIdx = content.indexOf(END, startIdx);
  if (endIdx === -1) return content;
  const before = content.slice(0, startIdx);
  const after = content.slice(endIdx + END.length);
  // Collapse the surrounding blank lines so re-running doesn't grow the file.
  return (before.replace(/\s+$/, "") + "\n\n" + after.replace(/^\s+/, "")).trimEnd() + "\n";
}

export function applyGlobalPrompts({
  memoryPath,
  selectedPrompts,
  dryRun = false,
  log = () => {},
}) {
  if (!memoryPath) return { skipped: true, reason: "no-memory-path" };

  let original = "";
  if (existsSync(memoryPath)) {
    original = readFileSync(memoryPath, "utf8");
  }
  const stripped = stripBlock(original);
  let next;
  if (selectedPrompts.length === 0) {
    // No prompts selected → leave the file without the managed block.
    next = stripped.endsWith("\n") ? stripped : stripped + "\n";
  } else {
    const block = buildBlock(selectedPrompts);
    const base = stripped.length === 0 ? "" : stripped.replace(/\n+$/, "") + "\n\n";
    next = base + block + "\n";
  }
  if (next === original) {
    return { skipped: true, reason: "unchanged" };
  }
  if (dryRun) {
    log(`[dry-run] write ${memoryPath} (${selectedPrompts.length} prompt(s) in managed block)`);
    return { dryRun: true };
  }
  mkdirSync(dirname(memoryPath), { recursive: true });
  writeFileSync(memoryPath, next, "utf8");
  log(`updated ${memoryPath}`);
  return { written: true, count: selectedPrompts.length };
}
