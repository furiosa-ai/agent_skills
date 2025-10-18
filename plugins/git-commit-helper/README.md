# Git Commit Helper

Professional Git commit message generation and PR history management following Chris Beams' seven rules.

## Features

### 1. Staged Changes → Commit Message

Generate professional commit messages from your staged changes.

**Triggers**: "커밋 메시지 만들어줘", "create commit message", "write commit"

**Example**:
```bash
# Stage your changes
git add src/auth.js tests/auth.test.js

# Ask Claude
> 커밋 메시지 만들어줘

# Claude generates:
Prevent token expiration race condition

Expired tokens were accepted during brief window between
expiry and cache invalidation, allowing unauthorized access.

Add expiry validation before processing requests and
implement immediate cache invalidation on token expiry.

Fixes #1234
```

### 2. PR History Restructuring

Analyze final diff and suggest atomic commit organization.

**Triggers**: "PR 히스토리 정리해줘", "clean up commits", "restructure PR"

**Example**:
```bash
# Ask Claude
> PR 히스토리 정리해줘

# Claude analyzes and suggests:
Current: 7 commits with WIP/typo fixes
Suggested: 3 atomic commits

1. Refactor ATen ops macro system
   +271 -1179 (2 files)

2. Enhance FromArgument trait
   +395 -1170 (5 files)

3. Add symbolic shape operations
   +211 -272 (1 file)
```

## Core Principles

### Chris Beams' Seven Rules

1. **Separate subject from body** with blank line
2. **Limit subject to 50 characters**
3. **Capitalize subject line**
4. **No period at end** of subject
5. **Use imperative mood** ("Fix bug" not "Fixed bug")
6. **Wrap body at 72 characters**
7. **Explain what and why**, not how

### Atomic Commits

**One commit = One logical change**

Benefits:
- Easier code review
- Clearer git history
- Simpler rollback/cherry-pick
- Better git bisect debugging

### Safety First

- Always creates backup branches before restructuring
- Provides restore commands
- Non-destructive workflow

### Auto-detection

Smart base branch detection:
```python
for remote in all_remotes:
    for branch in ['master', 'main']:
        merge_base = git merge-base remote/branch HEAD
        if timestamp(merge_base) > most_recent:
            most_recent = merge_base
```

Works perfectly with forked repositories!

## Scripts

### analyze_staged.py

Extracts staged changes for commit message generation.

```bash
python scripts/analyze_staged.py --json
```

**Output**:
```json
{
  "files": ["auth.js", "tests/auth.test.js"],
  "stats": {"insertions": 45, "deletions": 12, "files_changed": 2},
  "diff": "full diff content..."
}
```

### suggest_commits.py

Analyzes PR and suggests atomic commit restructuring.

```bash
python scripts/suggest_commits.py --json
```

**Automatically detects base branch** (finds most recent merge-base across all remotes).
⚠️ No need to specify base branch - auto-detection works in 99% of cases.

**Output**:
```json
{
  "base_branch": "99cafb6bc3...",
  "current_branch": "feature/auth",
  "total_diff": "FINAL diff (source of truth)",
  "stats": {"insertions": 120, "deletions": 45, "files_changed": 8},
  "current_commits": [...],
  "backup_command": "git branch backup/...",
  "restore_command": "git reset --hard backup/..."
}
```

## Examples

### Simple Commit Message

```
Prevent null pointer in token validation

Token validator crashed when receiving null tokens from
malformed requests. Add null check at validation entry point
and return 400 Bad Request for invalid input.

Fixes #789
```

### PR Restructuring

**Before** (7 commits):
```
- Add auth
- Fix typo
- WIP
- Add JWT
- Fix test
- Update docs
- Final cleanup
```

**After** (3 atomic commits):
```
1. Add JWT authentication system
   - auth.js, middleware/auth.js, utils/jwt.js
   +83 -0

2. Add protected route middleware
   - middleware/protected.js, routes/api.js
   +42 -5

3. Add authentication test coverage
   - tests/auth.test.js, tests/jwt.test.js
   +67 -0
```

## Installation

### Via Plugin Marketplace

```bash
/plugin marketplace add <username>/agent_skills
/plugin install git-commit-helper
```

### Manual

```bash
cp -r git-commit-helper ~/.claude/skills/
```

## Dependencies

- Python 3.6+
- Git
- No external Python packages required

## License

Apache 2.0

## References

- [Chris Beams' Commit Guide](https://cbea.ms/git-commit/)
- [Atomic Commits](references/commit-guide.md)
