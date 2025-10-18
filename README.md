# Agent Skills for Claude Code

Community-curated collection of Claude Code skills and agent tools to enhance your development workflow.

## 📦 Available Skills

### Git Commit Helper

Professional Git commit message generation and PR history management following industry best practices.

**Features**:
- Generate commit messages from staged changes following Chris Beams' seven rules
- Restructure PR commit history based on final diff analysis
- Automatic base branch detection for forked repositories
- Atomic commit suggestions with safety-first approach

**Usage**:
```bash
# Generate commit message
커밋 메시지 만들어줘

# Restructure PR history
PR 히스토리 정리해줘
```

## 🚀 Installation

### Quick Install

```bash
/plugin marketplace add https://github.com/furiosa-ai/agent_skills
/plugin install git-commit-helper
```

### Manual Install

```bash
git clone https://github.com/furiosa-ai/agent_skills
cp -r agent_skills/plugins/git-commit-helper ~/.claude/skills/
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
- **Auto-detection**: Smart merge-base detection across all remotes

**Scripts**:
- `analyze_staged.py`: Extract staged changes for commit message generation
- `suggest_commits.py`: Analyze PR and suggest atomic commit restructuring

## 🛠️ Development

### Adding New Skills

1. Create skill directory in `plugins/`
2. Add `SKILL.md` with YAML frontmatter
3. Update `marketplace.json`
4. Submit PR

### Skill Structure

```
plugins/your-skill/
├── SKILL.md              # Skill definition with YAML frontmatter
├── references/           # Optional: Reference documentation
└── scripts/              # Optional: Helper scripts
```

## 📄 License

Apache 2.0

## 🤝 Contributing

Contributions welcome! Please follow the skill creation guidelines in Claude Code documentation.

## 🔗 Resources

- [Claude Code Documentation](https://docs.claude.com/en/docs/claude-code)
- [Plugin Marketplaces Guide](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces)
- [Chris Beams' Commit Guide](https://cbea.ms/git-commit/)
