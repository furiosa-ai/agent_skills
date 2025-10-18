# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Claude Code plugin marketplace that provides agent skills - specialized workflows that extend Claude's capabilities. The repository follows Anthropic's agent-skills pattern, where skills are defined at the root level with `SKILL.md` files containing YAML frontmatter.

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

This skill implements a two-phase workflow:

**Phase 1: Staged Changes → Commit Message**
- `analyze_staged.py` extracts staged changes using `git diff --cached`
- Returns JSON with files, stats, and full diff
- Claude analyzes the diff to generate commit messages following Chris Beams' seven rules

**Phase 2: PR History Restructuring**
- `find_base_branch.py` scans all remote master/main branches and ranks candidates by commit count
- User selects the correct base branch (important for feature-from-feature branches)
- `suggest_commits.py` analyzes the final diff (`base..HEAD`) - this is the source of truth
- Intermediate commits are reference only; restructuring is based on final state
- Always creates backup branches before any destructive operations

**Key Design Principle**: Only the final diff matters for restructuring. Intermediate WIP/fixup commits are ignored - the goal is to reorganize the final state into atomic, logical commits.

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
python3 scripts/analyze_staged.py --json

# Test base branch detection
python3 scripts/find_base_branch.py --json

# Test PR diff analysis (requires base commit)
python3 scripts/suggest_commits.py <base-commit> --json
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

## Adding New Skills

1. Create skill directory at root: `new-skill/`
2. Create `new-skill/SKILL.md` with proper YAML frontmatter
3. Add optional `scripts/` and `references/` as needed
4. Update `.claude-plugin/marketplace.json`:
   - Add skill path to appropriate plugin's `skills` array
   - Increment `metadata.version`
5. Test locally before committing
6. Update main `README.md` with skill documentation

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
