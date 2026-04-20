// Persistent CLI settings.
//
//   - User-level:    ~/.config/adk/settings.json5
//   - Project-level: <project-root>/.adk/settings.json5  (only when --mode project)
//
// Project settings, when present, override user settings field-by-field.
// We do NOT keep a `projects: {}` map keyed by absolute path inside the user
// file any more; per-project preferences live in the project tree alongside
// the project's source.

import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, join, resolve } from "node:path";

import JSON5 from "json5";

const USER_SETTINGS_PATH = join(homedir(), ".config", "adk", "settings.json5");
const PROJECT_SETTINGS_REL = join(".adk", "settings.json5");

const DEFAULT_USER_SETTINGS = {
  // 'auto' means: decide from detection (project npm install -> project,
  // otherwise -> global).
  installMode: "auto",
  runtimes: [],
  surfaces: ["skills", "agents", "hooks", "mcp", "global-prompts"],
  skills: "all",
  mcpServers: [],
  globalPrompts: "all",
  // Every install location of this package we have ever seen. Used to
  // prune stale symlinks in <root>/.agents/skills/ when the package moves.
  knownPackagePaths: [],
};

const DEFAULT_PROJECT_SETTINGS = {
  // Each field is optional; missing fields fall back to the user settings.
};

export function userSettingsPath() {
  return USER_SETTINGS_PATH;
}

export function projectSettingsPath(projectRoot) {
  return projectRoot ? resolve(projectRoot, PROJECT_SETTINGS_REL) : null;
}

// Backwards-compat name (used by index.mjs --help text).
export function settingsPath() {
  return USER_SETTINGS_PATH;
}

function readJson5OrEmpty(path, fallback) {
  if (!existsSync(path)) return { ...fallback };
  try {
    const raw = readFileSync(path, "utf8");
    return { ...fallback, ...JSON5.parse(raw) };
  } catch (err) {
    console.error(`[adk] failed to read ${path}: ${err.message}`);
    return { ...fallback };
  }
}

export function loadUserSettings() {
  return readJson5OrEmpty(USER_SETTINGS_PATH, DEFAULT_USER_SETTINGS);
}

export function loadProjectSettings(projectRoot) {
  const path = projectSettingsPath(projectRoot);
  if (!path) return { ...DEFAULT_PROJECT_SETTINGS };
  return readJson5OrEmpty(path, DEFAULT_PROJECT_SETTINGS);
}

// Backwards-compat name (used by index.mjs).
export function loadSettings() {
  return loadUserSettings();
}

function writeJson5(path, body, banner, { dryRun, log }) {
  if (dryRun) {
    log(`[dry-run] would write settings to ${path}`);
    return { dryRun: true };
  }
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, banner + JSON5.stringify(body, null, 2) + "\n", "utf8");
  log(`wrote ${path}`);
  return { written: true };
}

export function saveUserSettings(settings, { dryRun = false, log = () => {} } = {}) {
  return writeJson5(
    USER_SETTINGS_PATH,
    settings,
    "// agents-devkit user settings — managed by `adk-install`.\n// Edit by hand at your own risk; the CLI reads this on next run.\n",
    { dryRun, log },
  );
}

export function saveProjectSettings(projectRoot, settings, { dryRun = false, log = () => {} } = {}) {
  const path = projectSettingsPath(projectRoot);
  if (!path) return { skipped: true, reason: "no-project-root" };
  return writeJson5(
    path,
    settings,
    "// agents-devkit project settings — managed by `adk-install` from this project.\n// Overrides the user-level ~/.config/adk/settings.json5 field-by-field.\n",
    { dryRun, log },
  );
}

// Backwards-compat name. Defaults to user-level save unless a project root is
// passed via the second argument shape (existing index.mjs uses single-arg).
export function saveSettings(settings, opts) {
  return saveUserSettings(settings, opts);
}

/**
 * Merge a path into the user-level `knownPackagePaths` list, deduping and
 * preserving order with the most recent path first.
 */
export function rememberPackagePath(settings, path) {
  const existing = (settings.knownPackagePaths || []).filter((p) => p !== path);
  return { ...settings, knownPackagePaths: [path, ...existing] };
}

/**
 * Effective defaults for the next prompt session.
 *
 *   - In `global` mode: just user settings.
 *   - In `project` mode: project settings overlaid on user settings.
 */
export function effectiveDefaults({ mode, projectRoot, userSettings }) {
  if (mode !== "project" || !projectRoot) {
    return {
      runtimes: userSettings.runtimes,
      surfaces: userSettings.surfaces,
      skills: userSettings.skills,
      mcpServers: userSettings.mcpServers,
      globalPrompts: userSettings.globalPrompts,
    };
  }
  const proj = loadProjectSettings(projectRoot);
  return {
    runtimes: proj.runtimes ?? userSettings.runtimes,
    surfaces: proj.surfaces ?? userSettings.surfaces,
    skills: proj.skills ?? userSettings.skills,
    mcpServers: proj.mcpServers ?? userSettings.mcpServers,
    globalPrompts: proj.globalPrompts ?? userSettings.globalPrompts,
  };
}

// Backwards-compat name. The old API was `projectDefaults(settings, projectRoot)`.
export function projectDefaults(userSettings, projectRoot) {
  return effectiveDefaults({ mode: "project", projectRoot, userSettings });
}

// Backwards-compat name. The old API stuffed per-project overrides inside
// the user file at `settings.projects[projectRoot]`. We now write them to
// the project's own `.adk/settings.json5` file instead. This shim accepts
// the same call signature as before so the index.mjs caller does not have
// to change in this slice.
export function setProjectDefaults(userSettings, projectRoot, overrides, opts = {}) {
  if (!projectRoot) return userSettings;
  const existing = loadProjectSettings(projectRoot);
  const merged = { ...existing, ...overrides };
  saveProjectSettings(projectRoot, merged, opts);
  return userSettings;
}
