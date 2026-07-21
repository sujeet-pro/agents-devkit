#!/usr/bin/env node
// =============================================================================
// validate-plugin.mjs — structural validator for the adk plugin marketplace.
//
// This repo has no package.json, so run the script directly with Node (>=20):
//
//     node scripts/validate-plugin.mjs            # human-readable report
//     node scripts/validate-plugin.mjs --json     # machine-readable report
//
// Exit code: 0 = clean, 1 = one or more errors. (Also documented in AGENTS.md.)
// The validator is READ-ONLY — it never writes, stages, or modifies any file.
//
// For every plugins/<plugin>/skills/<skill>/ it asserts:
//   1. SKILL.md exists and has YAML frontmatter (--- … ---) with a non-empty
//      `name` and `description`.
//   2. frontmatter `name` equals the skill's folder name (→ /<plugin>:<name>).
//   3. every intra-repo relative path referenced from any *.md in the skill
//      folder — as a backtick code span or a markdown link — resolves to a
//      file that exists on disk (this is what catches a dangling `dispatch.md`).
//   4. each plugin.json that enumerates `skills` lists only folders that exist.
//
// Reference-checking is deliberately conservative to avoid false positives.
// A backtick/link token is CHECKED (must exist, resolved relative to the file
// that mentions it) only when it looks like a path AND is clearly meant to be
// repo-local: an explicit relative path (`./…` / `../…`) or a bare sibling
// basename (no slash). Tokens that name files living in the *reviewed* repo or
// a consumer's install — `CLAUDE.md`, `AGENTS.md`, `package.json`,
// `.mcp.json`, `node_modules/…`, `docs/<placeholder>.md`, etc. — are skipped.
// =============================================================================

import { readFileSync, readdirSync, existsSync, statSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join, resolve, relative, basename } from 'node:path';

const REPO_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const PLUGINS_DIR = join(REPO_ROOT, 'plugins');
const JSON_OUT = process.argv.includes('--json');

// Path-like token: no whitespace, ends in a doc/code extension we care about.
const PATHLIKE = /^[^\s`]+\.(?:md|json|mjs|cjs|ts|js|py|ya?ml|toml)$/i;

// Basenames that skills legitimately reference but that live in the reviewed
// repo / a consumer install, not here — so their absence is never an error.
const EXTERNAL_BASENAMES = new Set([
  'CLAUDE.md', 'AGENTS.md', 'GEMINI.md', 'README.md', 'CHANGELOG.md',
  'report.md', 'llms.txt', 'llms-full.txt',
  'package.json', 'pyproject.toml', 'tsconfig.json', 'go.mod',
  'marketplace.json', 'plugin.json', '.mcp.json',
  'settings.json', 'settings.local.json', 'content.config.ts',
]);

const errors = [];
const warnings = [];
const infos = [];
const err = (skill, msg) => errors.push({ skill, msg });
const warn = (skill, msg) => warnings.push({ skill, msg });
const info = (skill, msg) => infos.push({ skill, msg });

// --- helpers ----------------------------------------------------------------

function listDirs(dir) {
  if (!existsSync(dir)) return [];
  return readdirSync(dir, { withFileTypes: true })
    .filter((d) => d.isDirectory())
    .map((d) => d.name);
}

function listFilesRec(dir, filterExt) {
  const out = [];
  for (const d of readdirSync(dir, { withFileTypes: true })) {
    const p = join(dir, d.name);
    if (d.isDirectory()) out.push(...listFilesRec(p, filterExt));
    else if (!filterExt || d.name.toLowerCase().endsWith(filterExt)) out.push(p);
  }
  return out;
}

// Parse the leading YAML frontmatter into a map of top-level key → text
// (inline value plus any indented continuation lines, e.g. a `>-` folded
// scalar). Returns null when there is no `--- … ---` block.
function parseFrontmatter(content) {
  const lines = content.split(/\r?\n/);
  if (lines[0].trim() !== '---') return null;
  let end = -1;
  for (let i = 1; i < lines.length; i++) {
    if (lines[i].trim() === '---') { end = i; break; }
  }
  if (end === -1) return null;

  const block = lines.slice(1, end);
  const keys = {};
  let current = null;
  for (const line of block) {
    const m = line.match(/^([A-Za-z0-9_-]+):(.*)$/);
    if (m && !/^\s/.test(line)) {
      current = m[1];
      keys[current] = m[2].trim();
    } else if (current !== null) {
      // continuation (indented) line of the current key's value
      keys[current] = (keys[current] + ' ' + line.trim()).trim();
    }
  }
  return keys;
}

function unquote(s) {
  const t = s.trim();
  if ((t.startsWith('"') && t.endsWith('"')) || (t.startsWith("'") && t.endsWith("'"))) {
    return t.slice(1, -1);
  }
  return t;
}

// A folding indicator (`>-`, `|`, …) alone is not real description content.
function hasContent(v) {
  if (!v) return false;
  return v.replace(/^[>|][+-]?\s*/, '').trim().length > 0;
}

// Pull candidate path references out of a markdown file's body.
function extractReferences(content) {
  const body = content.replace(/```[\s\S]*?```/g, '').replace(/~~~[\s\S]*?~~~/g, '');
  const refs = new Set();

  for (const m of body.matchAll(/`([^`\n]+)`/g)) {
    refs.add(m[1].trim());
  }
  for (const m of body.matchAll(/\[[^\]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)/g)) {
    let t = m[1].trim();
    if (t.startsWith('<') && t.endsWith('>')) t = t.slice(1, -1);
    refs.add(t.replace(/[#?].*$/, ''));
  }
  return [...refs];
}

// Decide whether a token is a repo-local reference we should verify.
function shouldCheck(token) {
  if (!token) return false;
  if (token.includes('<') || token.includes('>')) return false; // placeholder
  if (token.includes('://') || token.startsWith('#') || token.startsWith('mailto:')) return false;
  if (!PATHLIKE.test(token)) return false;                       // not path-shaped
  if (token.startsWith('node_modules/')) return false;           // consumer install
  if (EXTERNAL_BASENAMES.has(basename(token))) return false;     // reviewed-repo file
  const isExplicitRel = token.startsWith('./') || token.startsWith('../');
  const isBareSibling = !token.includes('/');
  return isExplicitRel || isBareSibling;
}

// --- checks -----------------------------------------------------------------

function validateSkill(pluginName, skillsDir, skillName) {
  const label = `${pluginName}/skills/${skillName}`;
  const skillDir = join(skillsDir, skillName);
  const skillMd = join(skillDir, 'SKILL.md');

  if (!existsSync(skillMd)) {
    err(label, 'missing SKILL.md (every skill folder must have an entry point)');
    return;
  }

  const content = readFileSync(skillMd, 'utf8');
  const fm = parseFrontmatter(content);
  if (!fm) {
    err(label, 'SKILL.md has no YAML frontmatter (--- … --- block)');
  } else {
    const name = fm.name ? unquote(fm.name) : '';
    if (!name) err(label, 'frontmatter is missing a non-empty `name`');
    else if (name !== skillName) {
      err(label, `frontmatter name "${name}" != folder "${skillName}"`);
    }
    if (!hasContent(fm.description)) {
      err(label, 'frontmatter is missing a non-empty `description`');
    }
    if (!fm['allowed-tools']) {
      warn(label, 'frontmatter has no `allowed-tools` (every shipped skill sets one)');
    }
  }

  // Reference existence across every markdown file in the skill folder.
  for (const file of listFilesRec(skillDir, '.md')) {
    const fileDir = dirname(file);
    const rel = relative(REPO_ROOT, file);
    let refs;
    try {
      refs = extractReferences(readFileSync(file, 'utf8'));
    } catch {
      continue;
    }
    for (const token of refs) {
      if (!shouldCheck(token)) continue;
      const target = resolve(fileDir, token);
      if (!existsSync(target)) {
        err(label, `${rel} references \`${token}\` → not found on disk`);
      }
    }
  }
}

function validatePluginManifestSkills(pluginName, pluginDir) {
  const manifest = join(pluginDir, '.claude-plugin', 'plugin.json');
  if (!existsSync(manifest)) {
    warn(pluginName, 'no .claude-plugin/plugin.json found');
    return;
  }
  let json;
  try {
    json = JSON.parse(readFileSync(manifest, 'utf8'));
  } catch (e) {
    err(pluginName, `plugin.json is not valid JSON: ${e.message}`);
    return;
  }
  if (!('skills' in json)) {
    info(pluginName, 'plugin.json does not enumerate `skills`; folders under skills/ are the source of truth');
    return;
  }
  const listed = Array.isArray(json.skills) ? json.skills : [];
  for (const entry of listed) {
    // entry may be a folder name or a path to a folder / SKILL.md
    const candidateDir = resolve(pluginDir, entry);
    const okDir = existsSync(join(candidateDir, 'SKILL.md'));
    const okFile = entry.endsWith('SKILL.md') && existsSync(candidateDir);
    if (!okDir && !okFile) {
      err(pluginName, `plugin.json lists skill "${entry}" with no matching folder/SKILL.md`);
    }
  }
}

// --- run --------------------------------------------------------------------

if (!existsSync(PLUGINS_DIR)) {
  console.error(`No plugins/ directory at ${PLUGINS_DIR}`);
  process.exit(1);
}

let skillCount = 0;
for (const pluginName of listDirs(PLUGINS_DIR)) {
  const pluginDir = join(PLUGINS_DIR, pluginName);
  const skillsDir = join(pluginDir, 'skills');
  validatePluginManifestSkills(pluginName, pluginDir);
  for (const skillName of listDirs(skillsDir)) {
    // ignore dotfolders (e.g. a stray .DS_Store dir) and non-skill dirs
    if (skillName.startsWith('.')) continue;
    if (!statSync(join(skillsDir, skillName)).isDirectory()) continue;
    skillCount++;
    validateSkill(pluginName, skillsDir, skillName);
  }
}

if (JSON_OUT) {
  console.log(JSON.stringify({ skillCount, errors, warnings, infos }, null, 2));
} else {
  for (const i of infos) console.log(`  info   ${i.skill}: ${i.msg}`);
  for (const w of warnings) console.log(`  warn   ${w.skill}: ${w.msg}`);
  for (const e of errors) console.log(`  ERROR  ${e.skill}: ${e.msg}`);
  console.log('');
  if (errors.length === 0) {
    console.log(`OK — ${skillCount} skill(s) validated, no errors` +
      (warnings.length ? `, ${warnings.length} warning(s)` : '') + '.');
  } else {
    console.log(`FAILED — ${errors.length} error(s) across ${skillCount} skill(s).`);
  }
}

process.exit(errors.length === 0 ? 0 : 1);
