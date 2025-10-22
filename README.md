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

**Workflow** (hands-off after initial questions):
1. **prepare-docs**: Discover sources, analyze requirements, save to file
2. **write-docs**: Generate documentation automatically from requirements file
3. **update-docs**: Integrate PR comments into existing documentation

**Features**:
- Multi-source support (GitHub, web pages, Google Drive, Notion, local files)
- Per-sentence confidence scoring (accuracy percentage)
- Inline source citations with relative paths for every statement
- PR comment integration for progressive refinement
- Multiple document types (API Reference, System Overview, Tutorial)
- Active source discovery (tests, types, examples, design docs)
- MCP server integration for cloud platforms
- Rationale required for low-confidence statements (< 70%)

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
# Step 1: Prepare requirements
문서 준비해줘
# or: prepare documentation

# Step 2: Generate from requirements
write-docs 실행해줘
# or: run write-docs

# Step 3: Update from PR comments
PR #123 코멘트 반영해줘
# or: update docs from PR comments
```

**⚠️ If skill doesn't activate, use explicit prefix:**
```bash
prepare-docs 문서 준비해줘
write-docs 실행해줘
update-docs PR 코멘트 반영해줘
```

**See full trigger phrase lists**:
- [prepare-docs/SKILL.md](prepare-docs/SKILL.md)
- [write-docs/SKILL.md](write-docs/SKILL.md)
- [update-docs/SKILL.md](update-docs/SKILL.md)

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

**Scenario**: Document a module with accuracy tracking using automated workflow

#### Step 1: Prepare Requirements
```bash
> 문서 준비해줘
```

**Claude asks**:
1. What sources to analyze? (GitHub, web, local files, etc.)
2. Any specific keywords or topics to focus on?
3. What document type? (API Reference, System Overview, Tutorial, Custom)

**User provides**:
- Sources: `src/parser.rs`
- Focus: Parser implementation details
- Type: API Reference

**Claude's workflow**:
1. Analyzes core sources (src/parser.rs)
2. **Actively discovers related sources**:
   - Searches for test files → finds `tests/parser_test.rs`
   - Finds type definitions → discovers `src/types.rs`
   - Searches docs/ → finds `docs/design.md`
3. Builds Content Map showing primary + related sources per function/type
4. **Saves complete requirements to `docs/doc-requirements.md`**

**Claude outputs**:
```
문서 요구사항을 docs/doc-requirements.md에 저장했습니다.
'write-docs 실행해줘'를 입력하면 자동으로 문서를 생성합니다.
```

#### Step 2: Generate Documentation
```bash
> write-docs 실행해줘
```

**Claude's workflow** (fully automated):
1. Loads requirements from `docs/doc-requirements.md`
2. Accesses all discovered sources
3. Generates documentation with per-sentence citations and accuracy scores
4. Adds mandatory rationale for statements with accuracy below 70%

**Sample output** (`docs/parser-api.md`):
```markdown
# Parser API Reference

## Functions

### `parse(input: String)`

Parses input string into AST ([Source](../src/parser.rs#L45)) [95%]

**Parameters:**
- `input` (String): Source code to parse ([Source](../src/parser.rs#L46)) [95%]

**Returns:**
- `Result<AST, ParseError>`: Parsed AST or error ([Source](../src/parser.rs#L47)) [92%]

The parser uses recursive descent algorithm ([Source1](../src/parser.rs#L100), [Source2](../docs/design.md#L23)) [75%]

The parser likely implements error recovery ([Source](../src/parser.rs#L200-250)) [65%]
> Rationale: Code shows try-catch patterns and continues after errors, but no explicit error recovery documentation found. Inference based on code structure only.
```

#### Step 3: PR Comment Integration
**User creates PR with documentation, reviewer adds comment**:
"Line 5: Parser also validates syntax during parsing"

```bash
> PR #456 코멘트 반영해줘
```

**Claude's workflow**:
1. Fetches PR comments via `gh` CLI
2. Extracts new information from comment
3. Locates target section in document
4. Updates statement with PR comment as additional source

**Updated line**:
```markdown
Parses input string into AST and validates syntax ([Source](../src/parser.rs#L45), [PR Comment](https://github.com/org/repo/pull/456#discussion_r12345)) [95%]
```

---

## 🔧 Troubleshooting

### Skill Activation Issues

**Problem**: Claude doesn't recognize trigger phrases like "커밋 메시지 만들어줘" or "문서 준비해줘"

**Solutions**:

1. **Use explicit skill name prefix**:
   ```bash
   # Git Commit Helper
   git-commit-helper 커밋 메시지 만들어줘

   # Documentation
   prepare-docs 문서 준비해줘
   write-docs 실행해줘
   update-docs PR 코멘트 반영해줘
   ```

2. **Try English alternatives**:
   - Git: "create commit message", "create pull request"
   - Docs: "prepare documentation", "run write-docs", "update docs from PR"

3. **Be more specific with context**:
   - ❌ Too vague: "문서 만들어줘"
   - ✅ Better: "문서 준비해줘 - src/parser.rs 분석해서 API Reference"
   - ❌ Too vague: "PR 만들어"
   - ✅ Better: "현재 브랜치에서 main으로 PR 만들어줘"

4. **Check skill installation**:
   ```bash
   # Verify skills are installed
   ls ~/.claude/skills/
   # Should show: git-commit-helper, prepare-docs, write-docs, update-docs

   # Reinstall if needed
   /plugin marketplace add https://github.com/furiosa-ai/agent_skills
   ```

5. **Try variations of trigger phrases**:
   - Commit: "write commit", "generate commit message", "create commit"
   - PR: "open PR", "make pull request", "create PR"
   - Docs (Interactive): "plan documentation structure", "generate API reference", "update docs from PR"
   - Docs (Automated): "prepare doc requirements", "write documentation", "improve docs"

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
