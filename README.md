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

### Code Documentation 🧪 (Experimental)

> **⚠️ Experimental Feature**: This skill is under active development. The workflow, accuracy calculation methods, and output formats may change based on user feedback. Use with caution in production environments.

Generate rigorous documentation from multiple sources with accuracy tracking and source citations.

**Features**:
- Multi-source support (GitHub, web pages, Google Drive, Notion, local files)
- Per-sentence confidence scoring (accuracy percentage)
- Accuracy threshold filtering (exclude low-confidence statements)
- Inline source citations for every statement
- PR comment integration for progressive refinement
- Multiple document types (API Reference, System Overview, Tutorial)
- MCP server integration for cloud platforms

**Known Limitations**:
- Accuracy calculation uses subjective inference (no formal verification)
- Large documentation sets may require manual chunking
- PR comment integration requires GitHub CLI (`gh`)

## 🎯 Quick Start

### Git Commit Helper Usage

```bash
# Generate commit message
커밋 메시지 만들어줘
# or: create commit message

# Restructure PR history
PR 히스토리 정리해줘
# or: clean up commits

# Create pull request
PR 만들어줘
# or: create PR

# Update existing PR
PR 업데이트해줘
# or: update PR

# ⚠️ If skill doesn't activate, use explicit prefix:
git-commit-helper 커밋 메시지 만들어줘
```

**See full trigger phrase list**: [git-commit-helper/SKILL.md](git-commit-helper/SKILL.md#trigger-phrases)

### Code Documentation Usage 🧪

```bash
# Generate documentation
코드 문서화해줘
# or: document this code

API 레퍼런스 만들어줘
# or: generate API reference

시스템 오버뷰 작성해줘
# or: write system overview

# Update documentation from PR comments
PR #123 코멘트 반영해줘

# ⚠️ If skill doesn't activate, use explicit prefix:
code-documentation API 문서 만들어줘
```

**See full trigger phrase list**: [code-documentation/SKILL.md](code-documentation/SKILL.md#trigger-phrases)

## 🚀 Installation

### For Claude Code

#### Requirements

- **Python**: 3.6 or higher
- **Git**: 2.23 or higher
- **Claude Code**: Latest version recommended

#### Quick Install

```bash
/plugin marketplace add https://github.com/furiosa-ai/agent_skills
```

#### Manual Install

```bash
git clone https://github.com/furiosa-ai/agent_skills
cp -r agent_skills/git-commit-helper ~/.claude/skills/
```

### For AMP Code

#### Requirements

- **Python**: 3.6 or higher
- **Git**: 2.23 or higher
- **gh CLI**: For PR commands (`brew install gh` or `apt install gh`)
- **AMP Code**: Latest version

#### Install

```bash
git clone https://github.com/furiosa-ai/agent_skills
cd agent_skills
./install-amp.sh
```

This installs:
- Slash commands to `~/.config/amp/commands/`
- Python scripts to `~/.config/amp/scripts/`
- Documentation to `~/.config/amp/`

#### Usage in AMP Code

```bash
# Stage changes first
git add <files>

# Generate commit message
/commit-msg

# Find base branch and prepare PR analysis
/pr-analyze

# Create pull request
/pr-create

# Update existing PR
/pr-update
```

**How it works:**
1. Slash commands output JSON data + workflow instructions
2. AMP follows the workflow steps from `AGENTS.md`
3. AMP parses diff, applies Chris Beams' seven rules, generates output
4. You review and approve before any Git operations

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

---

### Code Documentation Generation 🧪

**Scenario**: Document a module with accuracy tracking

```bash
> API 문서 만들어줘. src/parser.rs 분석해서, 최소 정확도 80%로
```

**Claude's workflow**:
1. Collects configuration (source, doc type, threshold)
2. Analyzes source code
3. Generates documentation with inline sources and confidence scores

**Sample output** (`parser-api.md`):
```markdown
# Parser API Reference

**Generated**: 2025-10-21
**Accuracy Threshold**: 80%
**Last Updated**: 2025-10-21
**Sources Analyzed**: 3

## Functions

### `parse(input: String)`

Parses input string into AST ([Source](https://github.com/org/repo/blob/main/src/parser.rs#L45)) [95%]

**Parameters:**
- `input` (String): Source code to parse ([Source](https://github.com/org/repo/blob/main/src/parser.rs#L46)) [95%]

**Returns:**
- `Result<AST, ParseError>`: Parsed AST or error ([Source](https://github.com/org/repo/blob/main/src/parser.rs#L47)) [92%]

The parser uses recursive descent algorithm ([Source1](https://github.com/org/repo/blob/main/src/parser.rs#L100), [Source2](https://github.com/org/repo/blob/main/docs/design.md#L23)) [85%]
```

**User adds PR comment**: "Line 15: Parser also validates syntax during parsing"

```bash
> PR #456 코멘트 반영해줘
```

**Updated line**:
```markdown
Parses input string into AST and validates syntax ([Source](https://github.com/org/repo/blob/main/src/parser.rs#L45), [PR Comment](https://github.com/org/repo/pull/456#discussion_r12345)) [95%]
```

## 🔧 Troubleshooting

### Skill Activation Issues

**Problem**: Claude doesn't recognize trigger phrases like "커밋 메시지 만들어줘" or "코드 문서화해줘"

**Solutions**:

1. **Use explicit skill name prefix**:
   ```bash
   # Instead of: 커밋 메시지 만들어줘
   git-commit-helper 커밋 메시지 만들어줘

   # Instead of: API 문서 만들어줘
   code-documentation API 문서 만들어줘
   ```

2. **Try English alternatives**:
   - "create commit message" (instead of 커밋 메시지 만들어줘)
   - "generate API documentation" (instead of API 문서 만들어줘)
   - "create pull request" (instead of PR 만들어줘)

3. **Be more specific with context**:
   - ❌ Too vague: "문서 만들어줘"
   - ✅ Better: "src/parser.rs 코드 분석해서 API 레퍼런스 만들어줘"
   - ❌ Too vague: "PR 만들어"
   - ✅ Better: "현재 브랜치에서 main으로 PR 만들어줘"

4. **Check skill installation**:
   ```bash
   # Verify skills are installed
   ls ~/.claude/skills/
   # Should show: git-commit-helper, code-documentation

   # Reinstall if needed
   /plugin marketplace add https://github.com/furiosa-ai/agent_skills
   ```

5. **Try variations of trigger phrases**:
   - Commit: "write commit", "generate commit message", "create commit"
   - PR: "open PR", "make pull request", "create PR"
   - Docs: "document this", "write documentation", "generate docs"

**Why this happens**: Claude uses the `description` field in SKILL.md to decide when to activate skills. If your phrase doesn't match the triggers listed, Claude might not recognize it. Using the explicit prefix (`skill-name command`) always works.

---

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
├── .agents/              # AMP Code slash commands
│   └── commands/
│       ├── commit-msg
│       ├── pr-analyze
│       ├── pr-create
│       └── pr-update
├── .claude-plugin/
│   └── marketplace.json  # Plugin marketplace configuration
├── git-commit-helper/    # Skills at root level
│   ├── SKILL.md
│   ├── scripts/
│   └── references/
├── AGENTS.md             # AMP Code LLM guidance
├── CLAUDE.md             # Architecture documentation
├── install-amp.sh        # AMP Code installer
└── README.md
```

### Testing Skills Locally

#### Claude Code
```bash
# Copy skill for local testing
cp -r git-commit-helper ~/.claude/skills/

# Test with trigger phrases
# "커밋 메시지 만들어줘"
# "PR 히스토리 정리해줘"
```

#### AMP Code
```bash
# Install globally
./install-amp.sh

# Test in a git repository
cd /path/to/repo
git add <files>

# In AMP Code, use slash commands:
# /commit-msg
# /pr-analyze
```

### Testing Python Scripts

```bash
# Test staged changes analysis
cd git-commit-helper
python3 scripts/analyze_diff.py --staged --json

# Test base branch detection
python3 scripts/find_base_branch.py --json

# Test PR diff analysis
python3 scripts/analyze_diff.py <base-commit> --json

# Test with large diff fallback
python3 scripts/analyze_diff.py <base-commit> --json --allow-large
```

### Developing AMP Code Integration

When adding new slash commands or modifying workflows:

1. **Update slash command** in `.agents/commands/`
   - Ensure script paths work for both workspace and global install
   - Include JSON output + workflow hints
   - Reference AGENTS.md sections

2. **Update AGENTS.md**
   - Add/modify workflow sections
   - Keep in sync with SKILL.md principles
   - Provide complete step-by-step instructions

3. **Test both installation modes**:
   ```bash
   # Test workspace mode
   cd /path/to/test-repo
   /commit-msg  # Should find scripts in git-commit-helper/scripts/

   # Test global mode
   ./install-amp.sh
   cd /path/to/another-repo
   /commit-msg  # Should find scripts in ~/.config/amp/scripts/
   ```

4. **Update documentation**:
   - README.md (user-facing)
   - CLAUDE.md (architecture)
   - install-amp.sh (if paths change)

## 📄 License

Apache 2.0

## 🤝 Contributing

Contributions welcome! Please follow the skill creation guidelines in Claude Code documentation.

## 🔗 Resources

- [Claude Code Documentation](https://docs.claude.com/en/docs/claude-code)
- [Plugin Marketplaces Guide](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces)
- [Chris Beams' Commit Guide](https://cbea.ms/git-commit/)
