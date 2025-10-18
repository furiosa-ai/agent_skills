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

Analyze final diff and suggest atomic commit organization with smart base branch detection.

**Triggers**: "PR 히스토리 정리해줘", "clean up commits", "restructure PR"

**Example**:
```bash
# Ask Claude
> PR 히스토리 정리해줘

# Claude finds base branch candidates:
Found 3 base branch candidate(s):

1. upstream/master (99cafb6bc3) - 6 commits
2. origin/master (0d7c549be3) - 4346 commits

# User selects or specifies custom base:
> Use 078889590a (refactor/aten-infrastructure-improvements)

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

### 3. Create Pull Request

Generate PR title and description from commit history and create a new pull request.

**Triggers**: "PR 만들어줘", "PR 생성해줘", "create PR", "open PR", "PR open"

**Example**:
```bash
# Ask Claude
> PR 만들어줘

# Claude finds base branch:
Found 2 base branch candidate(s):
1. origin/main (abc1234) - 3 commits

Which base branch should I use? [1]

# Claude analyzes commits and shows:
I'll create a PR with the following:

Title: Add user authentication system
Base: origin/main

Body:
## Summary
- Implement JWT-based authentication middleware
- Add user login and registration endpoints
- Include comprehensive test coverage

## Changes
- 8 files changed, +245 insertions, -12 deletions

## Commits
- abc1234 Add JWT token validation
- def5678 Implement login endpoint
- ghi9012 Add authentication tests

🤖 Generated with Claude Code

Should I proceed?

# User confirms, Claude creates:
✅ Pull request created: https://github.com/owner/repo/pull/456
```

**Features**:
- Automatically detects and uses project's PR template (`.github/PULL_REQUEST_TEMPLATE.md`)
- Analyzes **final diff** (NOT individual commits) to generate meaningful title and description
- Follows Chris Beams' rules for PR title (imperative mood, 50 chars max)
- Reuses analysis if recently ran "PR 히스토리 정리해줘"
- Requires user confirmation before creating

**Key principle**: Like commit restructuring, PR description is based on final diff (`base..HEAD`), not intermediate commits. This ensures the PR accurately describes what actually changed.

### 4. Update Pull Request

Refresh PR title and description based on latest commit history.

**Triggers**: "PR 업데이트해줘", "PR 수정해줘", "update PR", "refresh PR"

**Example**:
```bash
# Ask Claude
> PR 업데이트해줘

# Claude checks current PR:
Current PR #456:
Title: Add user authentication system
Body preview: ## Summary\n- Implement JWT-based authentication...

# After new commits, Claude suggests:
Proposed update:
Title: Add user authentication and authorization system
Body preview: ## Summary\n- Implement JWT-based authentication...
              - Add role-based access control...

The body was generated using .github/PULL_REQUEST_TEMPLATE.md.

Should I update the PR?

# User confirms:
✅ Pull request #456 updated
View at: https://github.com/owner/repo/pull/456
```

**Features**:
- Detects existing PR for current branch
- Analyzes latest **final diff** to regenerate title/description
- Preserves PR template structure
- Shows comparison before updating
- Warns if manual edits will be overwritten
- Reuses analysis if recently ran with same base branch

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

### Smart Base Detection

Two-step base branch detection with user confirmation:

**Step 1 - Find candidates** (`find_base_branch.py`):
```python
for remote in all_remotes:
    for branch in ['master', 'main']:
        merge_base = git merge-base remote/branch HEAD
        commit_count = count commits from merge_base to HEAD
        candidates.append({branch, merge_base, commit_count})

# Rank by commit count (ascending) - closer bases first
```

**Step 2 - User selection**:
- Shows ranked candidates with commit counts
- User selects from list or specifies custom base
- Handles feature-from-feature branch scenarios

Works perfectly with forked repositories and complex branch hierarchies!

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

### find_base_branch.py

Finds and ranks base branch candidates for PR history restructuring.

```bash
python scripts/find_base_branch.py [--json] [--limit N]
```

**Smart detection**: Analyzes merge-bases from all master/main branches, ranks by commit count (closer = better).

**Output**:
```json
{
  "current_branch": "feature/auth",
  "candidates": [
    {
      "rank": 1,
      "branch": "upstream/master",
      "base_commit": "99cafb6bc3...",
      "base_commit_short": "99cafb6bc3",
      "base_commit_message": "Merge #14774",
      "commit_count": 6
    }
  ]
}
```

**Why user selection?**:
- Feature branches from feature branches won't appear in candidates
- Forked repositories may have multiple valid bases
- User knows the actual parent branch better than heuristics

### suggest_commits.py

Analyzes PR and suggests atomic commit restructuring.

```bash
python scripts/suggest_commits.py <base-commit> --json
```

**Requires base commit** from find_base_branch.py or user specification.

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

**Workflow**:
```bash
# Step 1: Find base branch candidates
> PR 히스토리 정리해줘

Found 3 base branch candidate(s):
1. upstream/master (99cafb6bc3) - 6 commits
2. origin/master (0d7c549be3) - 4346 commits

# Step 2: User selects correct base
> Use upstream/master (99cafb6bc3)

# Step 3: Analyze and suggest atomic commits
Current: 7 commits with WIP/typo fixes
Suggested: 3 atomic commits
```

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
/plugin marketplace add https://github.com/furiosa-ai/agent_skills
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
