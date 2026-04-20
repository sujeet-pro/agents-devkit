// MCP server enumeration + merge into runtime config files.
//
// Source of truth for server definitions: mcp-config/servers/<name>.json
// Each server may declare an `env` object whose values reference shell vars
// like ${JIRA_URL}; we collect those, prompt the user for the missing ones,
// and (optionally) persist them to ~/.zshenv.

import { existsSync, mkdirSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import { dirname, join, basename } from "node:path";

const ENV_REF_RE = /\$\{([A-Z_][A-Z0-9_]*)(?::-[^}]*)?\}/g;

const SERVER_HELP = {
  github: {
    title: "GitHub",
    instructions:
      "Generate a Personal Access Token at https://github.com/settings/tokens (classic, with `repo`, `read:org`, `gist` scopes).",
  },
  jira: {
    title: "Atlassian Jira",
    instructions:
      "Create an API token at https://id.atlassian.com/manage-profile/security/api-tokens. Use your Atlassian account email as the username and your full Jira URL (e.g. https://yourcompany.atlassian.net).",
  },
  confluence: {
    title: "Atlassian Confluence",
    instructions:
      "Same API token as Jira — https://id.atlassian.com/manage-profile/security/api-tokens. Use your Confluence URL (e.g. https://yourcompany.atlassian.net/wiki).",
  },
  bitbucket: {
    title: "Bitbucket",
    instructions:
      "Create an app password at https://bitbucket.org/account/settings/app-passwords/ with at least `repository:read` and `pullrequest:read` scopes. Use your Bitbucket username, not your email.",
  },
  brainstorming: {
    title: "Local brainstorming MCP",
    instructions:
      "Clone https://github.com/sujeet-pro/mcp-brainstorming somewhere and point BRAINSTORMING_MCP_ROOT at the absolute path.",
  },
  "google-drive": {
    title: "Google Drive",
    instructions:
      "Follow https://github.com/piotr-agier/google-drive-mcp to obtain OAuth credentials and run the bootstrap once. Defaults to ~/.config/google-drive-mcp/.",
  },
};

export function discoverMcpServers(repoDir) {
  const dir = join(repoDir, "mcp-config", "servers");
  if (!existsSync(dir)) return [];
  const files = readdirSync(dir).filter((f) => f.endsWith(".json"));
  return files
    .map((f) => {
      const name = basename(f, ".json");
      const config = JSON.parse(readFileSync(join(dir, f), "utf8"));
      const envVars = collectEnvVars(config);
      return {
        name,
        title: SERVER_HELP[name]?.title ?? name,
        instructions: SERVER_HELP[name]?.instructions ?? "No setup notes available.",
        description: config.description ?? "",
        config,
        envVars,
      };
    })
    .sort((a, b) => a.name.localeCompare(b.name));
}

function collectEnvVars(config) {
  const found = new Set();
  const visit = (node) => {
    if (typeof node === "string") {
      let m;
      ENV_REF_RE.lastIndex = 0;
      while ((m = ENV_REF_RE.exec(node)) !== null) {
        found.add(m[1]);
      }
    } else if (Array.isArray(node)) {
      node.forEach(visit);
    } else if (node && typeof node === "object") {
      Object.values(node).forEach(visit);
    }
  };
  visit(config);
  return [...found].sort();
}

/**
 * Merge selected servers into a runtime's MCP config file. Preserves any
 * pre-existing servers the user has already configured.
 */
export function mergeMcpServers({
  configPath,
  serversKey,
  servers,
  dryRun = false,
  log = () => {},
}) {
  if (!configPath) return { skipped: true, reason: "no-config-path" };

  let config = {};
  if (existsSync(configPath)) {
    try {
      config = JSON.parse(readFileSync(configPath, "utf8"));
    } catch (err) {
      log(`mcp parse-failed ${configPath} (${err.message}) — leaving file alone`);
      return { skipped: true, reason: "parse-failed" };
    }
  }
  if (!config[serversKey] || typeof config[serversKey] !== "object") {
    config[serversKey] = {};
  }
  const before = JSON.stringify(config);
  for (const server of servers) {
    const cfg = { ...server.config };
    delete cfg.description;
    config[serversKey][server.name] = cfg;
  }
  const after = JSON.stringify(config);
  if (after === before) return { skipped: true, reason: "unchanged" };
  if (dryRun) {
    log(`[dry-run] mcp write ${configPath} (${servers.length} server(s))`);
    return { dryRun: true };
  }
  mkdirSync(dirname(configPath), { recursive: true });
  writeFileSync(configPath, JSON.stringify(config, null, 2) + "\n", "utf8");
  log(`mcp wrote ${configPath} (${servers.length} server(s))`);
  return { written: true, count: servers.length };
}
