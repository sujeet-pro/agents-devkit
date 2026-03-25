/**
 * AKIT plugin for OpenCode.ai
 *
 * Registers the shared skills directory and injects the using-akit bootstrap
 * text into the system prompt.
 */

import fs from 'fs';
import os from 'os';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const extractAndStripFrontmatter = (content) => {
  const match = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!match) return { frontmatter: {}, content };

  const frontmatter = {};
  for (const line of match[1].split('\n')) {
    const colonIdx = line.indexOf(':');
    if (colonIdx > 0) {
      const key = line.slice(0, colonIdx).trim();
      const value = line.slice(colonIdx + 1).trim().replace(/^["']|["']$/g, '');
      frontmatter[key] = value;
    }
  }

  return { frontmatter, content: match[2] };
};

const normalizePath = (value, homeDir) => {
  if (!value || typeof value !== 'string') return null;
  const trimmed = value.trim();
  if (!trimmed) return null;
  if (trimmed === '~') return homeDir;
  if (trimmed.startsWith('~/')) return path.join(homeDir, trimmed.slice(2));
  return path.resolve(trimmed);
};

export const AkitPlugin = async () => {
  const homeDir = os.homedir();
  const akitSkillsDir = path.resolve(__dirname, '../../skills');
  const envConfigDir = normalizePath(process.env.OPENCODE_CONFIG_DIR, homeDir);
  const configDir = envConfigDir || path.join(homeDir, '.config/opencode');

  const getBootstrapContent = () => {
    const skillPath = path.join(akitSkillsDir, 'using-akit', 'SKILL.md');
    if (!fs.existsSync(skillPath)) return null;

    const fullContent = fs.readFileSync(skillPath, 'utf8');
    const { content } = extractAndStripFrontmatter(fullContent);

    const toolMapping = `**Tool mapping for OpenCode**
- \`Skill\` tool -> OpenCode's native \`skill\` tool
- \`Task\` / subagent calls -> OpenCode subagents or @mentions
- \`Read\`, \`Write\`, \`Edit\`, \`Bash\` -> native OpenCode tools

**Skills location**
AKIT skills are available from \`${configDir}/skills/akit/\` when installed through the plugin bridge.`;

    return `<EXTREMELY_IMPORTANT>
You have access to AKIT.

The using-akit bootstrap skill is included below and is already available. Do not try to load it again before reading it.

${content}

${toolMapping}
</EXTREMELY_IMPORTANT>`;
  };

  return {
    config: async (config) => {
      config.skills = config.skills || {};
      config.skills.paths = config.skills.paths || [];
      if (!config.skills.paths.includes(akitSkillsDir)) {
        config.skills.paths.push(akitSkillsDir);
      }
    },

    'experimental.chat.system.transform': async (_input, output) => {
      const bootstrap = getBootstrapContent();
      if (bootstrap) {
        (output.system ||= []).push(bootstrap);
      }
    }
  };
};
