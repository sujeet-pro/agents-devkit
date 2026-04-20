#!/usr/bin/env node
// Tiny non-interactive postinstall hint. We never auto-run setup — that would
// break CI and surprise users. We just print a one-screen banner pointing at
// the right command for the install scenario we detect.

import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { readFileSync } from "node:fs";

import { detectInstall, describeInstall } from "./lib/install-mode.mjs";

const __filename = fileURLToPath(import.meta.url);
const PACKAGE_DIR = resolve(dirname(__filename), "..");

// Skip when running inside this repo's own install (we just installed deps for
// development; the dev runs `npm run setup` themselves).
if (process.env.npm_lifecycle_event !== "postinstall") process.exit(0);

let version = "0.0.0";
try {
  version = JSON.parse(readFileSync(resolve(PACKAGE_DIR, "package.json"), "utf8")).version;
} catch {}

const install = detectInstall(PACKAGE_DIR);

const cmd = install.kind === "npm-global" ? "adk-install" : "npx adk-install";
const scope =
  install.kind === "npm-project"
    ? `into project ${install.projectRoot}`
    : install.kind === "npm-global"
      ? "into your home (~/.agents/skills, ~/.claude/skills, …)"
      : "from this clone";

const lines = [
  "",
  `agents-devkit v${version} installed.`,
  `  ${describeInstall(install)}`,
  "",
  `Run the interactive setup ${scope}:`,
  `  ${cmd}`,
  "",
  "Preview without writing anything:",
  `  ${cmd} --dry-run`,
  "",
];

process.stdout.write(lines.join("\n"));
