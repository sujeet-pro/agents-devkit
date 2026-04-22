// Stricter content validator for skills, agents, hooks, global prompts and
// workflows. Wraps the spec validator (validate.mjs) and adds:
//
//   - Markdown well-formedness: balanced ``` code fences; no obviously
//     broken headings (e.g. trailing trailing-hash-only lines).
//   - Frontmatter completeness: required keys per artifact type.
//   - Non-empty body.
//   - Local link integrity: every relative `[text](path)` and every
//     `references/foo.md` mention must resolve to a real file.
//   - Containment: a skill MUST NOT reference any path that escapes its
//     own folder (no `../`, no absolute paths outside the repo, no links
//     into another skill's tree). Allow-list: pure URLs, anchors (`#foo`),
//     mailto, and the explicit allow-list passed in.
//
// The validator returns `{ errors, warnings, info }` and is callable from
// `npm run validate:content` and from CI.

import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { dirname, join, relative, resolve } from "node:path";

import { runValidation } from "./validate.mjs";

const SKILL_REQUIRED = ["name", "description"];
const AGENT_MD_REQUIRED = ["name", "description"];
const AGENT_TOML_REQUIRED = ["name", "description", "model", "developer_instructions"];

// Files allowed at the package root that skills MAY reference by name
// (kept tiny on purpose — extending this list weakens the containment rule).
const ROOT_ALLOWED_REFS = new Set([
  "README.md",
  "AGENTS.md",
  "CLAUDE.md",
  "REFERENCE.md",
  "LICENSE",
  "skills-manifest.json",
]);

/* ────────────────────────────── frontmatter ────────────────────────────── */

function loadFrontmatter(text) {
  const m = /^---\s*\n([\s\S]*?)\n---/m.exec(text);
  if (!m) return { ok: false, error: "missing-frontmatter", body: text };
  const out = {};
  let currentKey = null;
  for (const raw of m[1].split("\n")) {
    if (!raw.trim() || raw.trim().startsWith("#")) continue;
    const indented = raw.startsWith(" ") || raw.startsWith("\t");
    if (indented && currentKey) {
      const kv = /^\s+([a-zA-Z][a-zA-Z0-9_-]*)\s*:\s*(.+)$/.exec(raw);
      if (kv) {
        if (typeof out[currentKey] !== "object" || Array.isArray(out[currentKey])) out[currentKey] = {};
        out[currentKey][kv[1]] = stripQuotes(kv[2].trim());
      }
      continue;
    }
    const top = /^([a-zA-Z][a-zA-Z0-9_-]*)\s*:\s*(.*)$/.exec(raw.trim());
    if (!top) continue;
    currentKey = top[1];
    const v = top[2].trim();
    if (v === "") out[currentKey] = {};
    else out[currentKey] = stripQuotes(v);
  }
  const body = text.slice(m[0].length).replace(/^\s*\n/, "");
  return { ok: true, frontmatter: out, body };
}

function stripQuotes(v) {
  if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) {
    return v.slice(1, -1);
  }
  return v;
}

/* ────────────────────────────── markdown ────────────────────────────── */

/**
 * Strip fenced code blocks AND inline code spans from a Markdown body so the
 * heading / link extractors do not flag content inside code as broken.
 *
 * Handles:
 *   - Triple-or-more backtick fences (```, ````, etc.) with optional language
 *     tags. The fence's closing line must use at least the same number of
 *     backticks.
 *   - Triple-or-more tilde fences (~~~).
 *   - Inline code spans (`x` and ``x``) on a single line.
 *
 * Lines inside code are replaced with empty lines so line numbers and offsets
 * stay aligned for downstream regex error messages.
 */
function stripCodeBlocks(body) {
  const lines = body.split("\n");
  let inFence = false;
  let fenceMarker = ""; // the opening fence string (e.g., "```" or "~~~~")
  for (let i = 0; i < lines.length; i++) {
    const raw = lines[i];
    const trimmed = raw.trimStart();
    const fenceOpen = /^(`{3,}|~{3,})/.exec(trimmed);
    if (!inFence && fenceOpen) {
      inFence = true;
      fenceMarker = fenceOpen[1];
      lines[i] = "";
      continue;
    }
    if (inFence) {
      // Closing fence: same character class, length >= opening.
      if (fenceOpen && fenceOpen[1][0] === fenceMarker[0] && fenceOpen[1].length >= fenceMarker.length) {
        inFence = false;
        fenceMarker = "";
      }
      lines[i] = "";
      continue;
    }
    // Outside fence: strip inline code spans so `[text](path)` inside backticks
    // is also ignored.
    lines[i] = raw.replace(/`+[^`\n]*`+/g, "");
  }
  return lines.join("\n");
}

function checkMarkdownStructure(file, body, errors, warnings) {
  // Balanced fenced code blocks (``` openers must equal closers).
  const fences = [...body.matchAll(/^```/gm)];
  if (fences.length % 2 !== 0) {
    errors.push(`${file}: unbalanced \`\`\` code fences (${fences.length} found)`);
  }
  // Non-empty body
  if (body.trim().length === 0) {
    errors.push(`${file}: body is empty`);
    return;
  }
  // ATX headings: '# foo' good; '#foo' (no space) is broken. Skip code blocks.
  const proseOnly = stripCodeBlocks(body);
  for (const m of proseOnly.matchAll(/^(#{1,6})([^ \t#\n].*)$/gm)) {
    warnings.push(`${file}: heading '${m[0].trim()}' missing space after '${m[1]}'`);
  }
}

/* ───────────────────────── link / reference extraction ───────────────────────── */

const URL_RE = /^(https?:|mailto:|#|<)/i;

function extractLocalLinks(body) {
  // Strip fenced code blocks and inline code spans first; example links inside
  // code are documentation, not real link targets.
  const proseOnly = stripCodeBlocks(body);
  const links = [];
  // Markdown links: [text](target)  — only the target part.
  for (const m of proseOnly.matchAll(/\[([^\]]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)/g)) {
    const target = m[2];
    if (URL_RE.test(target)) continue;
    // Skip template placeholders: `<name>`, `<other>`, etc. These are
    // documentation, not real link targets.
    if (target.includes("<") || target.includes(">")) continue;
    links.push({ kind: "md-link", target });
  }
  // Bare `references/foo.md` mentions in prose / lists.
  for (const m of proseOnly.matchAll(/(?<![.\w/])references\/([\w.-]+)/g)) {
    links.push({ kind: "ref-mention", target: `references/${m[1]}` });
  }
  return links;
}

/* ─────────────────────────── containment check ─────────────────────────── */

function isOutsideSkill(skillDir, packageDir, target) {
  // Strip anchor / query.
  const clean = target.split("#")[0].split("?")[0];
  if (!clean) return false; // pure anchor
  const abs = resolve(skillDir, clean);
  const inSkill = abs === skillDir || abs.startsWith(skillDir + "/");
  if (inSkill) return false;
  // Allow listed root files
  const fromRoot = relative(packageDir, abs);
  if (!fromRoot.startsWith("..") && ROOT_ALLOWED_REFS.has(fromRoot)) return false;
  return true;
}

/* ─────────────────────────── skill validator ─────────────────────────── */

function validateSkill(skillDir, errors, warnings, info) {
  const skillFile = join(skillDir, "SKILL.md");
  if (!existsSync(skillFile)) {
    errors.push(`${skillDir}/SKILL.md missing`);
    return;
  }
  const text = readFileSync(skillFile, "utf8");
  const fm = loadFrontmatter(text);
  if (!fm.ok) {
    errors.push(`${skillFile}: missing or invalid frontmatter`);
    return;
  }
  for (const k of SKILL_REQUIRED) {
    if (!fm.frontmatter[k]) errors.push(`${skillFile}: missing required '${k}' in frontmatter`);
  }
  checkMarkdownStructure(skillFile, fm.body, errors, warnings);

  // references/* must be flat *.md
  const refDir = join(skillDir, "references");
  let refFiles = new Set();
  if (existsSync(refDir)) {
    for (const name of readdirSync(refDir)) {
      const full = join(refDir, name);
      const st = statSync(full);
      if (st.isDirectory()) {
        errors.push(`${refDir}: nested folder '${name}' is not allowed (references/ must be flat)`);
        continue;
      }
      if (!name.endsWith(".md")) {
        warnings.push(`${refDir}/${name}: non-markdown file in references/`);
        continue;
      }
      refFiles.add(name);
    }
  }

  // Walk SKILL.md + every reference for link integrity & containment.
  const allFiles = [
    { path: skillFile, body: fm.body },
    ...[...refFiles].map((name) => {
      const p = join(refDir, name);
      const t = readFileSync(p, "utf8");
      const f = loadFrontmatter(t);
      // references don't need frontmatter; if present, it's fine
      const body = f.ok ? f.body : t;
      checkMarkdownStructure(p, body, errors, warnings);
      return { path: p, body };
    }),
  ];

  const packageDir = resolve(skillDir, "..", "..");
  for (const { path: file, body } of allFiles) {
    for (const { kind, target } of extractLocalLinks(body)) {
      const cleanTarget = target.split("#")[0].split("?")[0];
      if (!cleanTarget) continue;

      // `references/foo.md` mentions are conventionally relative to the
      // skill folder — not to the file that contains them — so a reference
      // file can mention its sibling references without writing `./foo.md`.
      // Markdown link syntax `[](path)` keeps the standard relative-to-file
      // resolution.
      const baseDir = kind === "ref-mention" ? skillDir : dirname(file);
      const abs = resolve(baseDir, cleanTarget);

      // Containment: must stay inside the skill folder OR be in ROOT_ALLOWED_REFS.
      const inSkill = abs === skillDir || abs.startsWith(skillDir + "/");
      if (!inSkill) {
        const fromRoot = relative(packageDir, abs);
        if (fromRoot.startsWith("..") || !ROOT_ALLOWED_REFS.has(fromRoot)) {
          errors.push(
            `${file}: link target '${target}' escapes skill folder '${relative(packageDir, skillDir)}'`,
          );
          continue;
        }
      }
      if (!existsSync(abs)) {
        // Reference-style mentions are doc-internal; if they don't resolve,
        // it's almost always a broken doc. Treat as hard error. Other links
        // (e.g. `[](./img.png)` to a file the author hasn't added yet) are
        // warnings.
        const refMention = kind === "ref-mention";
        const msg = `${file}: link target '${target}' does not exist (resolved to ${relative(packageDir, abs)})`;
        if (refMention) errors.push(msg);
        else warnings.push(msg);
      }
    }
  }
  info.push(`skill ok: ${relative(resolve(skillDir, "..", ".."), skillDir)} (refs: ${refFiles.size})`);
}

/* ─────────────────────────── agent validators ─────────────────────────── */

function validateAgentMd(file, errors, warnings, info) {
  const text = readFileSync(file, "utf8");
  const fm = loadFrontmatter(text);
  if (!fm.ok) {
    errors.push(`${file}: missing or invalid frontmatter`);
    return;
  }
  for (const k of AGENT_MD_REQUIRED) {
    if (!fm.frontmatter[k]) errors.push(`${file}: missing required '${k}' in frontmatter`);
  }
  checkMarkdownStructure(file, fm.body, errors, warnings);
  info.push(`agent-md ok: ${file}`);
}

function validateAgentToml(file, errors, _warnings, info) {
  const text = readFileSync(file, "utf8");
  for (const k of AGENT_TOML_REQUIRED) {
    if (!new RegExp(`^${k}\\s*=`, "m").test(text)) {
      errors.push(`${file}: missing required key '${k}'`);
    }
  }
  // Minimal "value present" check for top-level string keys
  for (const k of ["name", "description", "model"]) {
    const m = new RegExp(`^${k}\\s*=\\s*"([^"\\n]*)"`, "m").exec(text);
    if (m && !m[1].trim()) errors.push(`${file}: '${k}' is empty`);
  }
  info.push(`agent-toml ok: ${file}`);
}

/* ─────────────────────────── prompt / hook / workflow ─────────────────────────── */

function validateGlobalPromptMd(file, errors, warnings, info) {
  const text = readFileSync(file, "utf8");
  if (!text.trim()) {
    errors.push(`${file}: empty`);
    return;
  }
  checkMarkdownStructure(file, text, errors, warnings);
  info.push(`prompt ok: ${file}`);
}

function validateHookJson(file, errors, info) {
  try {
    JSON.parse(readFileSync(file, "utf8"));
    info.push(`hook ok: ${file}`);
  } catch (err) {
    errors.push(`${file}: invalid JSON (${err.message})`);
  }
}

function validateWorkflowYaml(file, errors, info) {
  // We avoid pulling in a YAML library — do a cheap structural check:
  // every non-empty, non-comment line must be `key: value` or list/indent.
  const text = readFileSync(file, "utf8");
  let bad = 0;
  for (const raw of text.split("\n")) {
    const line = raw.replace(/#.*$/, "").trimEnd();
    if (!line.trim()) continue;
    if (/^\s*- /.test(line)) continue;
    if (/^\s*[\w.-]+\s*:/.test(line)) continue;
    if (/^\s+\S/.test(line)) continue;
    bad++;
  }
  if (bad > 0) errors.push(`${file}: ${bad} unparseable line(s)`);
  else info.push(`workflow ok: ${file}`);
}

/* ─────────────────────────── runner ─────────────────────────── */

function listEntries(dir, predicate) {
  if (!existsSync(dir)) return [];
  return readdirSync(dir)
    .filter((n) => !n.startsWith("."))
    .map((n) => join(dir, n))
    .filter(predicate)
    .sort();
}

export function runContentValidation({ root, verbose = false } = {}) {
  const errors = [];
  const warnings = [];
  const info = [];

  // Skills
  const skillsRoot = join(root, "skills");
  for (const skillDir of listEntries(skillsRoot, (p) => statSync(p).isDirectory())) {
    validateSkill(skillDir, errors, warnings, info);
  }

  // Agents
  for (const folder of ["agents-claude", "agents-cursor"]) {
    const dir = join(root, folder);
    for (const f of listEntries(dir, (p) => p.endsWith(".md") && statSync(p).isFile())) {
      validateAgentMd(f, errors, warnings, info);
    }
  }
  const codexDir = join(root, "agents-codex");
  for (const f of listEntries(codexDir, (p) => p.endsWith(".toml") && statSync(p).isFile())) {
    validateAgentToml(f, errors, warnings, info);
  }

  // Hooks
  for (const f of listEntries(join(root, "hooks"), (p) => p.endsWith(".json") && statSync(p).isFile())) {
    validateHookJson(f, errors, info);
  }

  // Global prompts (skip README.md, only managed prompt files)
  const promptDir = join(root, "global-prompts");
  for (const f of listEntries(
    promptDir,
    (p) => p.endsWith(".md") && !p.endsWith("/README.md") && statSync(p).isFile(),
  )) {
    validateGlobalPromptMd(f, errors, warnings, info);
  }

  // Workflows (yaml)
  const workflowDir = join(root, "workflows");
  for (const f of listEntries(workflowDir, (p) => /\.ya?ml$/.test(p) && statSync(p).isFile())) {
    validateWorkflowYaml(f, errors, info);
  }

  // Also fold in the spec-level validator (descriptions ≤ 1024 chars, etc.)
  const spec = runValidation({ root });
  errors.push(...spec.errors);
  warnings.push(...spec.warnings);

  if (verbose) {
    for (const i of info) console.log(`info  ${i}`);
  }
  return { errors, warnings, info };
}

const isMain = import.meta.url === `file://${process.argv[1]}`;
if (isMain) {
  const verbose = process.argv.includes("--verbose") || process.argv.includes("-v");
  const root = resolve(new URL("../..", import.meta.url).pathname);
  const { errors, warnings, info } = runContentValidation({ root, verbose });
  if (verbose) console.log(`\n${info.length} info, ${warnings.length} warnings, ${errors.length} errors`);
  for (const w of warnings) console.warn(`warn  ${w}`);
  for (const e of errors) console.error(`error ${e}`);
  console.log(
    verbose
      ? ""
      : `\n${errors.length} error(s), ${warnings.length} warning(s), ${info.length} item(s) checked.`,
  );
  process.exit(errors.length > 0 ? 1 : 0);
}
