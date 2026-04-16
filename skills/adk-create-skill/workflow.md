# Skill Architect Workflow

## Phase 1: Define

**Goal**: Clarify the skill's purpose, scope, persona, and dependencies.

1. Parse the user request to extract: skill name, area, tier, MCP dependency
2. Validate the name: must be kebab-case, no special characters, no spaces
3. Check for naming conflicts: scan `skills/` for existing skills with the same or similar names
4. Challenge scope: can this be handled by an existing skill? Is a new skill justified?
5. Determine which constitution pillars are most relevant for this skill's domain
6. **Gate**: Confirm the skill name, area, tier, persona direction, and MCP dependency with the user (skip if `--auto`)

## Phase 2: Scaffold

**Goal**: Create the directory structure and generate all required files.

1. Run `python3 scripts/scaffold.py <name>` to bootstrap the skill directory structure
2. The scaffold script creates: `skills/adk-<name>/` with subdirectories `scripts/`, `references/`, `references/_shared/`
3. Generate `scripts/preflight.py` with dependency checks for declared requirements
4. Copy shared reference files to `references/_shared/`:
   - `ai-guidelines-overview.md`
   - `constitution.md`
   - `research-protocol.md`
   - `output-format.md`
5. Generate skeleton files from `references/skill-template.md`: `SKILL.md`, `persona.md`, `workflow.md`

## Phase 3: Author

**Goal**: Write the skill content with constitution pillars embedded.

1. **SKILL.md**: Generate complete file using `references/skill-template.md` as the structural reference, with all required sections:
   - Frontmatter with all required fields (name, description, compatibility, tools, dependencies)
   - Constitution section with 3-5 relevant pillars adapted for this skill
   - Persona summary with reference to `references/persona.md`
   - When To Use / When NOT To Use with concrete examples
   - Parameters table with all flags
   - Pre-flight steps
   - Workflow summary table with phases and gates
   - Interaction Protocol rules
   - Parallel Agents (if applicable)
   - Validation rules
   - Output Format with example block
   - Examples (2-3 invocations)
   - Anti-Patterns / Red Flags
   - Related Skills
2. **persona.md**: Generate with Mission, Scope, Hard Rules, Evidence Expectations, Output Style
3. **workflow.md**: Generate with full phase definitions including gates and validation rules

## Phase 4: Validate

**Goal**: Verify the generated skill meets all ADK requirements.

1. Parse SKILL.md frontmatter as YAML and verify all required fields are present
2. Verify the skill name follows `adk-` prefix and kebab-case conventions
3. Verify all required sections exist in SKILL.md
4. Verify persona.md has all required sections (Mission, Scope, Hard Rules, Evidence Expectations, Output Style)
5. Verify workflow.md has numbered phases with gates
6. Execute the generated preflight script to confirm it runs without error
7. Report any validation failures with specific fix suggestions

## Phase 5: Register

**Goal**: Update the skill manifest and provide installation instructions.

1. Run `python3 scripts/generate-skills-manifest.py` to update the manifest
2. Verify the new skill appears in the manifest
3. Report the installation command: `npx skills add . adk-<name>`
4. List remaining customization work:
   - Persona tuning (refine hard rules and evidence expectations)
   - Workflow detailing (add specific substeps and edge cases)
   - Example writing (add real-world invocation examples)
   - Testing (run the skill end-to-end on a sample task)

## Validation Rules

- All required files exist: SKILL.md, persona.md, workflow.md, scripts/preflight.py, references/_shared/
- Frontmatter is valid YAML with all required fields
- Skill name is unique within `skills/`
- Preflight script executes without error
- SKILL.md contains all required sections
- Constitution pillars are relevant to the skill's domain (not just copy-pasted generically)
