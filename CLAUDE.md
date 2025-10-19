# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Claude Code plugin marketplace that provides agent skills - specialized workflows that extend Claude's capabilities. The repository follows Anthropic's agent-skills pattern, where skills are defined at the root level with `SKILL.md` files containing YAML frontmatter.

**Multi-Platform Support**: The git-commit-helper skill is available for both:
- **Claude Code** - Via plugin marketplace system with automatic skill loading
- **AMP Code** - Via slash commands and AGENTS.md guidance (see AMP Code Integration section)

## Key Architecture Concepts

### Plugin Marketplace Structure

The repository uses a plugin marketplace configuration in `.claude-plugin/marketplace.json` that defines:
- Marketplace metadata (name, owner, version)
- Plugin definitions that group related skills
- Skill paths relative to the repository root

Skills are installed to `~/.claude/skills/` on user machines. The marketplace system allows users to discover and install skills via `/plugin install <skill-name>`.

### Skill Definition Pattern

Skills are directories at the root level with:
1. **`SKILL.md`** - Required file with YAML frontmatter defining skill metadata and instructions
   - `name`: Skill identifier (e.g., `git-commit-helper`)
   - `description`: When Claude should invoke this skill (triggers, use cases)
   - Body contains detailed instructions for Claude on how to execute the skill
2. **`scripts/`** - Optional directory for Python helper scripts
3. **`references/`** - Optional directory for reference documentation

The YAML frontmatter in `SKILL.md` is critical - it tells Claude when to invoke the skill and what it does.

### Git Commit Helper Architecture

This skill implements a four-phase workflow with a unified final-diff-based approach:

**Phase 1: Staged Changes → Commit Message**
- `analyze_diff.py --staged` extracts staged changes using `git diff --cached`
- Returns JSON with files, stats, full diff, and diff_type
- Supports three-tier fallback strategy for large staged changes (>5000 lines)
- Claude analyzes the diff to generate commit messages following Chris Beams' seven rules

**Phase 2: PR History Restructuring**
- `find_base_branch.py` scans all remote master/main branches and ranks candidates by commit count
- User selects the correct base branch (important for feature-from-feature branches)
- `analyze_diff.py <base>` analyzes the final diff (`base..HEAD`) - this is the source of truth
- Supports three-tier fallback: full diff → additions only → error (with --allow-large override)
- Intermediate commits are reference only; restructuring is based on final state
- Always creates backup branches before any destructive operations

**Phase 3: Pull Request Creation**
- Uses `gh pr view` to check if PR already exists (if yes, suggests update workflow)
- Reuses `find_base_branch.py` for base branch selection
- **Reuses Phase 2 analysis if available** (same base, same diff) - no redundant work
- Checks for PR template in common locations (`.github/PULL_REQUEST_TEMPLATE.md`, etc.)
- Analyzes **final diff** (`base..HEAD`) to generate PR title and body - NOT individual commits
- If template found, fills template structure; otherwise uses default format
- Requires user confirmation before creating PR via `gh pr create`

**Phase 4: Pull Request Update**
- Uses `gh pr view --json` to get current PR information (including base branch)
- Analyzes latest **final diff** from base to HEAD
- **Reuses recent analysis if available** - efficient workflow
- Generates new title/body using same final-diff-based logic as creation
- Shows comparison between old and new content
- Requires user confirmation before updating via `gh pr edit`
- Warns if manual edits on GitHub will be overwritten

**Key Design Principles**:
1. **Final diff is the source of truth**: For both commit restructuring and PR description, only the final diff (`base..HEAD`) matters. Intermediate WIP/fixup commits are ignored.
2. **Analysis reuse**: If user runs "PR 히스토리 정리해줘" followed by "PR 만들어줘", the same base and diff analysis is reused - no redundant computation.
3. **PR templates respected**: Template detection checks `.github/PULL_REQUEST_TEMPLATE.md`, `.github/pull_request_template.md`, `.github/PULL_REQUEST_TEMPLATE/*.md`, `docs/PULL_REQUEST_TEMPLATE.md`, and root `PULL_REQUEST_TEMPLATE.md`.
4. **User confirmation required**: All destructive operations (restructure, PR create/update) require explicit user approval.

**Three-Tier Fallback Strategy**:
For large PRs/diffs (>5000 lines), `analyze_diff.py` uses progressive degradation:
- **Tier 1** (<=5000 total lines): Full diff with all changes
- **Tier 2** (>5000 total, <=5000 additions): Additions only (deletions omitted)
- **Tier 3** (>5000 additions): Error with suggestion to split (override with --allow-large)

This prevents context window overflow while still handling most large PRs via additions-only mode.

**Efficient workflow example**:
```
> PR 히스토리 정리해줘
# Runs find_base_branch.py + analyze_diff.py <base>, analyzes final diff

> PR 만들어줘
# Reuses the base and final diff analysis from above!
# No need to re-run scripts or re-analyze
```

## Common Development Commands

### Testing Skills Locally

```bash
# Manual copy for local testing
cp -r git-commit-helper ~/.claude/skills/

# Test skill invocation in Claude Code
# Use trigger phrases like "커밋 메시지 만들어줘" or "PR 히스토리 정리해줘"
```

### Testing Python Scripts

```bash
# Test staged changes analysis
cd git-commit-helper
python3 scripts/analyze_diff.py --staged --json

# Test base branch detection
python3 scripts/find_base_branch.py --json

# Test PR diff analysis (requires base commit)
python3 scripts/analyze_diff.py <base-commit> --json

# Test with large diff fallback
python3 scripts/analyze_diff.py <base-commit> --json --allow-large
```

### Validating Marketplace Configuration

```bash
# Validate JSON syntax
python3 -m json.tool .claude-plugin/marketplace.json

# Verify skill YAML frontmatter can be parsed
python3 -c "import yaml; print(yaml.safe_load(open('git-commit-helper/SKILL.md').read().split('---')[1]))"
```

### Publishing Updates

```bash
# Update version in marketplace.json (semver)
# - Patch (1.0.X): Bug fixes, documentation
# - Minor (1.X.0): New skills added
# - Major (X.0.0): Breaking changes

# Commit and push
git add .
git commit -m "Add feature X"
git push

# Users update with:
# /plugin install git-commit-helper (reinstalls latest)
```

## Documentation Consistency Principles

When adding or modifying features, maintain consistency across all documentation layers:

### Three-Layer Documentation Pattern

1. **`SKILL.md`** - Claude's execution guide
   - Update YAML frontmatter `description` with new triggers
   - Add detailed workflow with numbered steps
   - Include ⚠️ IMPORTANT principles and key design decisions
   - Provide code examples for each step

2. **Root `README.md`** - Combined user documentation and project overview
   - Add feature to Available Skills → Features list
   - Add trigger to Usage examples section
   - Include realistic usage examples in 💡 Usage Examples
   - Update Core Principles if new design pattern introduced
   - Keep both project overview and skill details in single file

3. **`CLAUDE.md`** - Architecture documentation (this file)
   - Update architecture description (e.g., "four-phase workflow")
   - Document key design principles and rationale
   - Add to Common Development Commands if needed

### Consistency Checklist

When adding a feature, ensure:
- [ ] All three documentation files updated
- [ ] Trigger phrases consistent across all files
- [ ] Examples use same scenario/data
- [ ] Design principles align with existing patterns
- [ ] Terminology matches (e.g., "final diff", "base branch")

**Note**: We maintain a single README at the root instead of per-skill READMEs to avoid duplication and ensure consistency.

## Adding New Skills

1. Create skill directory at root: `new-skill/`
2. Create `new-skill/SKILL.md` with proper YAML frontmatter
3. Add optional `scripts/` and `references/` as needed
4. Update `.claude-plugin/marketplace.json`:
   - Add skill path to appropriate plugin's `skills` array
   - Increment `metadata.version`
5. Test locally before committing
6. Update root `README.md` with skill documentation (no per-skill README needed)

## Script Requirements

All Python scripts:
- Must be Python 3.6+ compatible
- Use only standard library (no external dependencies)
- Support `--json` flag for structured output
- Exit with status 1 on errors
- Make scripts executable: `chmod +x scripts/*.py`

## Chris Beams' Seven Rules

The git-commit-helper skill enforces these rules:
1. Separate subject from body with blank line
2. Limit subject to 50 characters
3. Capitalize subject line
4. No period at end of subject
5. Use imperative mood ("Fix bug" not "Fixed bug")
6. Wrap body at 72 characters
7. Explain what and why, not how

No scope prefixes (like `feat(auth):`) are used - just imperative verbs directly.

## AMP Code Integration

The git-commit-helper skill has been adapted for AMP Code (Sourcegraph's coding agent) using a different architecture that complements AMP's extension system.

### Architecture Overview

**Key Difference from Claude Code**:
- Claude Code: Skills are auto-loaded with full SKILL.md context when triggers are detected
- AMP Code: Slash commands output data + workflow hints, LLM follows guidance from AGENTS.md

### Components

**1. Slash Commands** (`.agents/commands/`)
- `/commit-msg` - Generate commit message from staged changes
- `/pr-analyze` - Find base branch candidates
- `/pr-create` - Create pull request
- `/pr-update` - Update existing PR

Each slash command:
- Is an executable bash script
- Finds and runs Python scripts from `git-commit-helper/scripts/`
- Works in both workspace (`.agents/commands/`) and global (`~/.config/amp/commands/`) modes
- Outputs JSON data from Python scripts
- Includes workflow hints (numbered steps) for AMP's LLM
- References AGENTS.md sections for complete workflows

**2. AGENTS.md**
- Provides complete workflow guidance for AMP's LLM
- References `@git-commit-helper/SKILL.md` for detailed instructions
- Includes "Key Principles for Amp" specific to slash command usage
- Contains workflow summaries with code examples
- Explains Chris Beams' seven rules

**3. Python Scripts** (reused from Claude Code version)
- `analyze_diff.py` - Unified diff analyzer (staged mode and range mode)
- `find_base_branch.py` - Base branch candidate detection
- No duplication - same scripts work for both Claude Code and AMP Code

**4. install-amp.sh**
- One-command installation to `~/.config/amp/`
- Copies slash commands, Python scripts, and documentation
- Respects `XDG_CONFIG_HOME` environment variable

### Design Principles

**1. Hybrid Approach (Data + Hints + Guidance)**
- Slash commands provide: JSON data + immediate workflow hints
- AGENTS.md provides: Complete workflows + design principles
- SKILL.md provides: Detailed reference (via `@` mention)
- Result: Self-contained workflow that doesn't require AMP to guess next steps

**2. Code Reuse**
- Python scripts are shared between Claude Code and AMP Code
- No duplication of analysis logic
- Slash commands are thin wrappers around existing scripts

**3. Option 1 Strategy** (from design discussion)
- Slash commands find base candidates, AMP runs `analyze_diff.py` directly
- Avoids unused variables and complex state management
- Each command is stateless and single-purpose

**4. Script Location Flexibility**
- Commands check workspace first: `$REPO_ROOT/git-commit-helper/scripts/`
- Fall back to global: `~/.config/amp/scripts/`
- Works for both per-project and global installations

### Workflow Examples

**Commit Message Generation**:
```bash
# User stages changes
git add <files>

# User runs slash command
/commit-msg

# Slash command outputs:
# - JSON with diff, stats, files
# - Workflow hints: "Analyze diff → Apply seven rules → Generate message"
# - Reference: "See AGENTS.md section 'Generate Commit Message'"

# AMP follows workflow from AGENTS.md
# Generates commit message following Chris Beams' rules
```

**PR Creation**:
```bash
# User runs slash command
/pr-create

# Slash command outputs:
# - JSON with base branch candidates
# - Workflow hints: "Select base → I'll run analyze_diff.py → Check template → Generate PR"
# - Reference: "See AGENTS.md section 'Create Pull Request'"

# User selects base branch
# AMP runs: python3 git-commit-helper/scripts/analyze_diff.py <base> --json
# AMP checks for PR template
# AMP generates title/body from final diff
# User approves, AMP creates PR
```

### Directory Structure

```
agent_skills/
├── .agents/
│   └── commands/          # AMP Code slash commands
│       ├── commit-msg     # Executable bash scripts
│       ├── pr-analyze
│       ├── pr-create
│       └── pr-update
├── AGENTS.md              # AMP Code LLM guidance
├── git-commit-helper/     # Shared skill directory
│   ├── SKILL.md           # Claude Code skill definition
│   ├── scripts/           # Shared Python scripts
│   │   ├── analyze_diff.py
│   │   └── find_base_branch.py
│   └── references/        # Shared reference docs
└── install-amp.sh         # AMP Code installer
```

### Installation Locations

**Workspace Installation** (per-project):
```
project/
├── .agents/
│   └── commands/          # Slash commands
└── git-commit-helper/     # Python scripts
```

**Global Installation** (`~/.config/amp/`):
```
~/.config/amp/
├── commands/              # Slash commands
│   ├── commit-msg
│   ├── pr-analyze
│   ├── pr-create
│   └── pr-update
├── scripts/               # Python scripts
│   ├── analyze_diff.py
│   └── find_base_branch.py
├── git-commit-helper/     # SKILL.md for @-mention
│   ├── SKILL.md
│   └── references/
└── AGENTS.md              # Workflow guidance
```

### Differences from Claude Code Version

| Aspect | Claude Code | AMP Code |
|--------|-------------|----------|
| **Activation** | Auto-loaded when trigger detected | User invokes slash command |
| **Context** | Full SKILL.md in context | JSON + hints, AGENTS.md guidance |
| **Script Invocation** | Claude runs scripts directly | Slash command wraps scripts |
| **Workflow State** | Claude maintains conversation state | Stateless commands |
| **Base Selection** | Script output → Claude asks user | Script output → User responds → AMP runs next script |
| **Installation** | `~/.claude/skills/` | `~/.config/amp/` |

### Testing AMP Integration

```bash
# Install to global config
./install-amp.sh

# Test in a git repository
cd /path/to/repo
git add <files>

# Test commit message generation
# (In AMP Code)
/commit-msg

# Verify output includes:
# - JSON with diff data
# - Workflow hints
# - Reference to AGENTS.md
```

### Maintenance Considerations

When updating git-commit-helper:

1. **Python scripts** - Update once, works for both platforms
2. **SKILL.md** - Update for Claude Code workflows
3. **AGENTS.md** - Update for AMP Code workflows (keep in sync with SKILL.md principles)
4. **Slash commands** - Only update if script invocation changes
5. **README.md** - Update both Claude Code and AMP Code sections

**Documentation consistency checklist** still applies:
- Update SKILL.md for Claude Code
- Update AGENTS.md for AMP Code
- Update README.md for user-facing docs
- Update CLAUDE.md (this file) for architecture changes
