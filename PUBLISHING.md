# Publishing Guide

How to publish this plugin marketplace to GitHub and make it available to Claude Code users.

## Prerequisites

- GitHub account
- Git configured with your credentials
- Repository created on GitHub

## Step 1: Create GitHub Repository

```bash
# On GitHub, create new repository:
# Name: agent_skills
# Description: Community-curated collection of Claude Code skills
# Visibility: Public
# Initialize: Do NOT initialize with README (we already have one)
```

## Step 2: Push to GitHub

```bash
cd /workspace/agent_skills

# Add GitHub remote (replace with your username)
git remote add origin https://github.com/<USERNAME>/agent_skills.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 3: Verify Marketplace

Check that these files are accessible:
- `https://github.com/<USERNAME>/agent_skills/blob/main/.claude-plugin/marketplace.json`
- `https://github.com/<USERNAME>/agent_skills/blob/main/README.md`

## Step 4: Test Installation

In Claude Code:

```bash
# Add marketplace
/plugin marketplace add <USERNAME>/agent_skills

# Install plugin
/plugin install git-commit-helper

# Verify installation
ls ~/.claude/skills/git-commit-helper/
```

## Step 5: Update README

Update the README.md installation instructions with your actual GitHub username:

```markdown
/plugin marketplace add <your-actual-username>/agent_skills
```

## Step 6: Share with Community (Optional)

Submit to community directories:

1. **Claude Code Marketplace** (https://claudecodemarketplace.com)
   - Automatic discovery from GitHub

2. **Community Collections**:
   - https://github.com/ccplugins/marketplace
   - https://github.com/jeremylongshore/claude-code-plugins-plus

Create PR to add your marketplace to their `marketplace.json`.

## Continuous Updates

### Adding New Skills

1. Create skill in `plugins/new-skill/`
2. Add entry to `.claude-plugin/marketplace.json`
3. Update main README.md
4. Commit and push:
   ```bash
   git add .
   git commit -m "Add new-skill plugin"
   git push
   ```

### Versioning

Use semantic versioning in `marketplace.json`:
- **Patch** (1.0.1): Bug fixes, documentation
- **Minor** (1.1.0): New skills added
- **Major** (2.0.0): Breaking changes

## Team Configuration

For organization-wide deployment, add to team's `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": [
    {
      "source": "github",
      "repo": "<USERNAME>/agent_skills"
    }
  ]
}
```

## Troubleshooting

### Plugin Not Found

Check marketplace.json is valid:
```bash
python3 -m json.tool .claude-plugin/marketplace.json
```

### Skills Not Loading

Verify SKILL.md has valid YAML frontmatter:
```yaml
---
name: skill-name
description: Skill description
---
```

### Permission Issues

Ensure scripts are executable:
```bash
chmod +x plugins/*/scripts/*.py
```

## Support

- Documentation: https://docs.claude.com/en/docs/claude-code/plugin-marketplaces
- Issues: Create GitHub issue in your repository
- Community: Claude Code Discord/Forums

## License

This marketplace uses Apache 2.0 license. Skills may have their own licenses.
