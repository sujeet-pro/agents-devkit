#!/usr/bin/env node

import { existsSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(__dirname, "..");
const pluginsDir = join(repoRoot, "plugins");
const packageJsonPath = join(repoRoot, "package.json");
const packageLockPath = join(repoRoot, "package-lock.json");
const marketplacePath = join(repoRoot, ".claude-plugin", "marketplace.json");
const versionPattern =
  /^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$/u;

function usage() {
  console.error("Usage: npm run version:bump -- <patch|minor|major|actual-version>");
}

function readJson(path) {
  return JSON.parse(readFileSync(path, "utf8"));
}

function readText(path) {
  return readFileSync(path, "utf8");
}

function writeText(path, text) {
  writeFileSync(path, text);
}

function writeJson(path, data) {
  writeFileSync(path, `${JSON.stringify(data, null, 2)}\n`);
}

function rel(path) {
  return relative(repoRoot, path);
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/gu, "\\$&");
}

function parseVersion(version) {
  const match = versionPattern.exec(version);
  if (!match) {
    throw new Error(`Invalid semver version: ${version}`);
  }

  return {
    major: Number(match[1]),
    minor: Number(match[2]),
    patch: Number(match[3]),
  };
}

function bumpVersion(currentVersion, bump) {
  const current = parseVersion(currentVersion);

  if (bump === "major") {
    return `${current.major + 1}.0.0`;
  }

  if (bump === "minor") {
    return `${current.major}.${current.minor + 1}.0`;
  }

  if (bump === "patch") {
    return `${current.major}.${current.minor}.${current.patch + 1}`;
  }

  const explicitVersion = bump.replace(/^v/u, "");
  if (!versionPattern.test(explicitVersion)) {
    throw new Error(`Expected patch, minor, major, or an explicit semver version. Received: ${bump}`);
  }

  return explicitVersion;
}

function pluginManifestPaths() {
  if (!existsSync(pluginsDir)) return [];

  return readdirSync(pluginsDir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => join(pluginsDir, entry.name, ".claude-plugin", "plugin.json"))
    .filter((path) => existsSync(path))
    .sort();
}

function updatePackageLock(nextVersion, updatedPaths) {
  if (!existsSync(packageLockPath)) return;

  const packageLock = readJson(packageLockPath);
  if (packageLock.name && packageLock.version) {
    packageLock.version = nextVersion;
  }

  if (packageLock.packages?.[""]?.version) {
    packageLock.packages[""].version = nextVersion;
  }

  writeJson(packageLockPath, packageLock);
  updatedPaths.push(packageLockPath);
}

function replaceFirstVersionField(text, nextVersion, path) {
  let replaced = false;
  const updatedText = text.replace(/("version"\s*:\s*")[^"]+(")/u, (_match, before, after) => {
    replaced = true;
    return `${before}${nextVersion}${after}`;
  });

  if (!replaced) {
    throw new Error(`${rel(path)} missing version field`);
  }

  return updatedText;
}

function replaceMarketplaceVersion(text, nextVersion) {
  let replaced = false;
  const updatedText = text.replace(
    /("metadata"\s*:\s*\{[\s\S]*?"version"\s*:\s*")[^"]+(")/u,
    (_match, before, after) => {
      replaced = true;
      return `${before}${nextVersion}${after}`;
    },
  );

  if (!replaced) {
    throw new Error(`${rel(marketplacePath)} missing metadata.version field`);
  }

  return updatedText;
}

function replaceInternalDependencyVersions(text, manifest, pluginNames, nextVersion) {
  if (!Array.isArray(manifest.dependencies)) return text;

  let updatedText = text;

  for (const dependency of manifest.dependencies) {
    if (!pluginNames.has(dependency.name) || typeof dependency.version !== "string") continue;

    const dependencyName = escapeRegExp(dependency.name);
    const pattern = new RegExp(
      `(\\{\\s*"name"\\s*:\\s*"${dependencyName}"\\s*,\\s*"version"\\s*:\\s*")([^"]+)(")`,
      "u",
    );

    updatedText = updatedText.replace(pattern, (_match, before, currentRange, after) => {
      const prefix = currentRange.match(/^[~^]/u)?.[0] ?? "";
      return `${before}${prefix}${nextVersion}${after}`;
    });
  }

  return updatedText;
}

function main() {
  const bump = process.argv[2];
  if (!bump || process.argv.length > 3) {
    usage();
    process.exit(1);
  }

  const packageJson = readJson(packageJsonPath);
  const nextVersion = bumpVersion(packageJson.version, bump);
  const updatedPaths = [];

  writeText(packageJsonPath, replaceFirstVersionField(readText(packageJsonPath), nextVersion, packageJsonPath));
  updatedPaths.push(packageJsonPath);

  updatePackageLock(nextVersion, updatedPaths);

  const marketplace = readJson(marketplacePath);
  if (!marketplace.metadata || typeof marketplace.metadata !== "object") {
    throw new Error(`${rel(marketplacePath)} missing metadata object`);
  }
  writeText(marketplacePath, replaceMarketplaceVersion(readText(marketplacePath), nextVersion));
  updatedPaths.push(marketplacePath);

  const manifestPaths = pluginManifestPaths();
  const pluginNames = new Set(manifestPaths.map((path) => readJson(path).name));
  for (const manifestPath of manifestPaths) {
    const manifest = readJson(manifestPath);
    let manifestText = replaceFirstVersionField(readText(manifestPath), nextVersion, manifestPath);
    manifestText = replaceInternalDependencyVersions(manifestText, manifest, pluginNames, nextVersion);
    writeText(manifestPath, manifestText);
    updatedPaths.push(manifestPath);
  }

  console.log(`Updated marketplace version to ${nextVersion}`);
  for (const path of updatedPaths) {
    console.log(`- ${rel(path)}`);
  }
}

try {
  main();
} catch (error) {
  console.error(`ERROR ${error.message}`);
  process.exit(1);
}
