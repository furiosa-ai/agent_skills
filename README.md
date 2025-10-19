# Agent Skills for Claude Code

Community-curated collection of Claude Code skills and agent tools to enhance your development workflow.

## 📦 Available Skills

### Git Commit Helper

Professional Git commit message generation and PR history management following industry best practices.

**Features**:
- Generate commit messages from staged changes following Chris Beams' seven rules
- Restructure PR commit history based on final diff analysis
- Create pull requests with auto-generated title and description
- Update existing PR descriptions based on latest changes
- Smart base branch detection with user confirmation (handles feature-from-feature branches)
- Atomic commit suggestions with safety-first approach

**Usage**:
```bash
# Generate commit message
커밋 메시지 만들어줘

# Restructure PR history
PR 히스토리 정리해줘

# Create pull request
PR 만들어줘

# Update existing PR
PR 업데이트해줘

# If skill is not recognized, prefix with skill name:
git-commit-helper 커밋 메시지 만들어줘
git-commit-helper PR 히스토리 정리해줘
```

## 🚀 Installation

### Requirements

- **Python**: 3.6 or higher
- **Git**: 2.23 or higher
- **Claude Code**: Latest version recommended

### Quick Install

```bash
/plugin marketplace add https://github.com/furiosa-ai/agent_skills
```

### Manual Install

```bash
git clone https://github.com/furiosa-ai/agent_skills
cp -r agent_skills/git-commit-helper ~/.claude/skills/
```

## 📚 Skills Documentation

### Git Commit Helper

Implements Chris Beams' seven rules for great Git commit messages:

1. Separate subject from body with blank line
2. Limit subject to 50 characters
3. Capitalize subject line
4. No period at end of subject
5. Use imperative mood
6. Wrap body at 72 characters
7. Explain what and why, not how

**Core Principles**:
- **Atomic Commits**: One logical change per commit
- **Safety First**: Always create backup branches before restructuring
- **Final Diff Based**: Analyze final changes, ignore intermediate commits
- **Smart Detection**: Two-step workflow: find base branch candidates → user confirms → analyze PR
- **PR Template Support**: Automatically detects and uses project's PR templates
- **Analysis Reuse**: Efficient workflow when chaining restructure → PR creation

**How Base Branch Detection Works**:
1. `find_base_branch.py` scans all remotes and ranks candidates by commit count
2. User selects the correct base (important for feature-from-feature branches)
3. `analyze_diff.py` analyzes the final diff against selected base with smart fallback for large changes

**Scripts**:
- `analyze_diff.py`: Unified diff analyzer supporting both staged changes and PR analysis with three-tier fallback for large diffs
- `find_base_branch.py`: Find and rank base branch candidates with smart detection

## 💡 Usage Examples

### Commit Message Generation

**Input**: Staged changes fixing a bug
```bash
커밋 메시지 만들어줘
```

**Output**:
```
Prevent null pointer in token validation

Token validator crashed when receiving null tokens from
malformed requests. Add null check at validation entry point
and return 400 Bad Request for invalid input.

Fixes #789
```

### PR History Restructuring

**Before**: 7 commits with "WIP", "fix typo", "oops" messages

**After Request**: "PR 히스토리 정리해줘"

**Result**: 3 atomic commits:
```
1. Add JWT authentication system
   Files: auth.js, middleware/auth.js, utils/jwt.js
   +83 -0

2. Add protected route middleware
   Files: middleware/protected.js, routes/api.js
   +42 -5

3. Add authentication test coverage
   Files: tests/auth.test.js, tests/jwt.test.js
   +67 -0
```

### PR Creation

**Request**: "PR 만들어줘"

**Claude's Response**:
```
Found 2 base branch candidate(s):
1. origin/main (abc1234) - 3 commits

Analyzing final diff...

I'll create a PR with the following:

Title: Add JWT authentication system
Base: origin/main

Body:
## Summary
- Implement JWT-based authentication middleware
- Add user login and registration endpoints
- Include comprehensive test coverage

## Changes
- 8 files changed, +245 insertions, -12 deletions

🤖 Generated with Claude Code

Should I proceed?
```

**Result**: PR created at https://github.com/owner/repo/pull/456

### PR Update

**Request**: "PR 업데이트해줘" (after adding new commits)

**Claude's Response**:
```
Current PR #456:
Title: Add JWT authentication system

Proposed update:
Title: Add JWT authentication and authorization system

Body updated with:
- New role-based access control features
- Updated statistics

Should I update the PR?
```

**Result**: PR #456 updated with latest changes

### Efficient Workflow

**Combine restructure and PR creation**:
```bash
# Step 1: Clean up commits
> PR 히스토리 정리해줘
# Claude analyzes base and final diff

# Step 2: Create PR immediately
> PR 만들어줘
# Claude reuses the analysis from step 1!
# No redundant computation
```

## 🔧 Troubleshooting

### Script Execution Errors

**Problem**: `python: command not found`
```bash
# Solution: Use python3 explicitly
python3 ~/.claude/skills/git-commit-helper/scripts/analyze_diff.py --staged --json
```

**Problem**: No base branch candidates found
```bash
# Solution: Ensure you have remote branches
git fetch --all
python scripts/find_base_branch.py
```

**Problem**: Script fails with "No commits found"
```bash
# Solution: Verify base branch exists
git log <base_branch>..HEAD  # Should show commits
```

### Permission Issues

**Problem**: Permission denied on scripts
```bash
# Solution: Make scripts executable
chmod +x ~/.claude/skills/git-commit-helper/scripts/*.py
```

## 🛠️ Development

### Adding New Skills

1. Create skill directory at root level (e.g., `new-skill/`)
2. Add `SKILL.md` with YAML frontmatter
3. Update `.claude-plugin/marketplace.json` to include skill in `skills` array
4. Update version in `metadata.version`
5. Submit PR

### Skill Structure

```
your-skill/
├── SKILL.md              # Skill definition with YAML frontmatter
├── references/           # Optional: Reference documentation
└── scripts/              # Optional: Helper scripts
```

### Repository Structure

Following Anthropic's agent-skills pattern:

```
agent_skills/
├── .claude-plugin/
│   └── marketplace.json  # Plugin marketplace configuration
├── git-commit-helper/    # Skills at root level
│   ├── SKILL.md
│   ├── scripts/
│   └── references/
└── README.md
```

## 📄 License

Apache 2.0

## 🤝 Contributing

Contributions welcome! Please follow the skill creation guidelines in Claude Code documentation.

## 🔗 Resources

- [Claude Code Documentation](https://docs.claude.com/en/docs/claude-code)
- [Plugin Marketplaces Guide](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces)
- [Chris Beams' Commit Guide](https://cbea.ms/git-commit/)
