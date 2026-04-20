// Detect how the CLI is being executed and propose an install mode.
//
// Three install scenarios:
//
//   - `clone`    The user `git clone`d this repo and is running `npm run
//                setup` from inside it. Default proposal: global.
//   - `npm-global`  Installed via `npm install -g agents-devkit`. The
//                package lives under the global npm prefix. Default: global.
//   - `npm-project` Installed via `npm install agents-devkit` in some
//                consumer project. The package lives under that project's
//                `node_modules/agents-devkit`. Default: project install
//                rooted at that project (parent of `node_modules`).

import { existsSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, join, resolve } from "node:path";

/**
 * @param {string} packageDir Absolute path to this package's root (the dir
 *   containing this CLI's `package.json`).
 */
export function detectInstall(packageDir) {
  const home = homedir();

  // Are we inside a `node_modules` tree?
  const nm = "/node_modules/";
  const idx = packageDir.indexOf(nm);
  if (idx === -1) {
    // Running from a clone (or a tarball install in a non-standard layout).
    return {
      kind: "clone",
      packageDir,
      projectRoot: null,
      defaultMode: "global",
      defaultRoot: home,
    };
  }

  const enclosingRoot = packageDir.slice(0, idx); // parent of node_modules
  const enclosingPkg = join(enclosingRoot, "package.json");

  // Inspect the enclosing project to decide between npm-global and
  // npm-project. A globally-installed package lives in a directory whose
  // package.json is missing or whose name is not a real consumer project.
  if (!existsSync(enclosingPkg)) {
    return {
      kind: "npm-global",
      packageDir,
      projectRoot: null,
      defaultMode: "global",
      defaultRoot: home,
    };
  }

  let pkg;
  try {
    pkg = JSON.parse(readFileSync(enclosingPkg, "utf8"));
  } catch {
    pkg = {};
  }

  // Heuristic: if the enclosing dir's package.json belongs to npm itself
  // (global install layout) treat as global.
  if (pkg?.name === "agents-devkit" || pkg?.name === "npm") {
    return {
      kind: "npm-global",
      packageDir,
      projectRoot: null,
      defaultMode: "global",
      defaultRoot: home,
    };
  }

  return {
    kind: "npm-project",
    packageDir,
    projectRoot: enclosingRoot,
    defaultMode: "project",
    defaultRoot: enclosingRoot,
  };
}

/**
 * Resolve the absolute root path the installer should write into for the
 * chosen mode. For 'global' this is `$HOME`. For 'project' it is the
 * detected project root (when running from npm install) or the current
 * working directory (clone install).
 */
export function resolveRoot({ mode, install, cwd }) {
  if (mode === "global") return homedir();
  if (install.projectRoot) return install.projectRoot;
  return resolve(cwd);
}

export function describeInstall(install) {
  switch (install.kind) {
    case "clone":
      return `Running from a clone at ${install.packageDir}`;
    case "npm-global":
      return `Installed globally; package at ${install.packageDir}`;
    case "npm-project":
      return `Installed into project ${install.projectRoot}; package at ${install.packageDir}`;
    default:
      return `Unknown install kind at ${install.packageDir}`;
  }
}

void dirname;
