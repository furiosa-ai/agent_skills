# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-10-18

### Changed
- **BREAKING**: Restructured repository to follow Anthropic's agent-skills pattern
- Moved skills from `plugins/` subdirectory to root level
- Updated `marketplace.json` to use `skills` array pattern
- Plugin name changed from `git-commit-helper` to `git-tools` for better grouping
- Updated installation command: `/plugin install git-tools` (previously `git-commit-helper`)

### Added
- Added `metadata` section in marketplace.json
- Added skill update instructions in README
- Added CHANGELOG.md for version tracking
- Added repository structure documentation

### Migration Guide
If you previously installed `git-commit-helper`:
```bash
# Uninstall old version
/plugin uninstall git-commit-helper

# Install new version
/plugin install git-tools
```

## [1.0.0] - 2025-10-18

### Added
- Initial release with git-commit-helper skill
- Generate professional commit messages from staged changes
- Restructure PR commit history based on final diff analysis
- Smart base branch detection with user confirmation
- Support for atomic commit suggestions
- Scripts: analyze_staged.py, find_base_branch.py, suggest_commits.py
- Chris Beams' seven rules implementation
