---
name: git-commit-helper
description: This skill should be used when creating commit messages from staged changes or restructuring commit history for PRs. Triggers include requests like "create commit message", "write commit", "clean up commits", "restructure PR history", or "organize commits". Applies Chris Beams' seven rules for professional commit messages and atomic commit principles.
---

# Git Commit Helper

## Overview

Guide commit message creation and PR history restructuring following professional Git practices based on Chris Beams' seven rules. Supports two main workflows: generating commit messages from staged changes, and reorganizing commit history based on final diff analysis.

## Core Capabilities

### 1. Generate Commit Message from Staged Changes

Create professional commit messages following the seven rules from staged changes.

**When to use**: User has staged changes (`git add`) and needs a commit message.

**Trigger phrases**:
- "Create commit message"
- "Write commit for staged changes"
- "Generate commit"
- "커밋 메시지 만들어줘"

**Workflow**:

1. **Extract staged changes**:
   ```bash
   python scripts/analyze_staged.py --json
   ```

   Returns:
   ```json
   {
     "files": ["auth.js", "tests/auth.test.js"],
     "stats": {"insertions": 45, "deletions": 12, "files_changed": 2},
     "diff": "full diff content..."
   }
   ```

2. **Analyze the diff**: Read the actual code changes to understand:
   - What changed (high-level)
   - Why this change matters
   - Appropriate imperative verb (Add/Fix/Refactor/Update/etc.)

3. **Generate commit message** following the seven rules:
   - Subject: 50 chars max, imperative mood, capitalized, no period
   - Blank line separator
   - Body: 72 chars per line, explain WHY and WHAT (not HOW)

4. **Present to user**:
   ```
   Subject line:
   Prevent token expiration race condition

   Body:
   Expired tokens were accepted during brief window between
   expiry and cache invalidation, allowing unauthorized access.

   Add expiry validation before processing requests and
   implement immediate cache invalidation on token expiry.

   Fixes #1234
   ```

**Reference**: See `references/commit-guide.md` for seven rules and examples.

### 2. Restructure PR Commit History

Analyze PR changes and suggest atomic commit organization based on final diff.

**When to use**: User wants to clean up messy commit history before merge.

**Trigger phrases**:
- "Clean up commit history"
- "Restructure PR commits"
- "Organize commits"
- "PR 히스토리 정리해줘"

**IMPORTANT PRINCIPLES**:
- **Only final diff matters**: Intermediate commits are reference only
- **Safety first**: Always create backup before restructuring
- **Atomic commits**: One logical change per commit

**Workflow**:

1. **Extract PR information**:
   ```bash
   python scripts/suggest_commits.py --json
   # Or specify base: python scripts/suggest_commits.py develop --json
   ```

   Returns:
   ```json
   {
     "base_branch": "main",
     "current_branch": "feature/auth",
     "total_diff": "FINAL diff (source of truth)",
     "stats": {"insertions": 120, "deletions": 45, "files_changed": 8},
     "current_commits": [
       {"hash": "abc123", "message": "Add auth", "files": [...], "stats": {...}},
       {"hash": "def456", "message": "Fix typo", "files": [...], "stats": {...}}
     ],
     "backup_command": "git branch backup/feature-auth-20250118-143022",
     "restore_command": "git reset --hard backup/feature-auth-20250118-143022"
   }
   ```

2. **Analyze final diff** (NOT current commits):
   - Read `total_diff` to understand final state
   - Identify logical groups of changes
   - Ignore intermediate commits that were reverted/changed
   - Focus on what actually changed from base to HEAD

3. **Suggest atomic commits**:
   ```
   Current: 5 commits with WIP/typo fixes mixed in

   Suggested restructuring (3 atomic commits):

   1. Add user authentication middleware
      - auth.js: Token validation logic
      - middleware/auth.js: Express middleware
      Files: 2, +45 -0

   2. Add JWT token generation utilities
      - utils/jwt.js: Token create/verify functions
      - config/jwt.js: JWT configuration
      Files: 2, +38 -5

   3. Add authentication test suite
      - tests/auth.test.js: Middleware tests
      - tests/jwt.test.js: Token tests
      Files: 2, +37 -0
   ```

4. **Provide restructuring strategy**:

   **If user wants guidance** (NOT automatic):
   ```
   Interactive rebase approach:

   git rebase -i main

   Then in editor:
   pick abc123 Add auth
   fixup def456 Fix typo       # Squash into previous
   reword ghi789 Add JWT       # Rewrite message
   pick jkl012 Add tests
   fixup mno345 Fix test       # Squash into previous
   ```

   **If user requests automatic execution**:
   ```
   ⚠️ SAFETY FIRST:

   Step 1 - Create backup (REQUIRED):
   git branch backup/feature-auth-20250118-143022

   Step 2 - Perform rebase:
   [Execute git rebase commands]

   Step 3 - Verify result:
   git log --oneline main..HEAD

   If problems occur, restore:
   git reset --hard backup/feature-auth-20250118-143022
   ```

**Reference**: See `references/commit-guide.md` for atomic commit principles.

## The Seven Rules (Quick Reference)

1. Separate subject from body with blank line
2. Limit subject to 50 characters
3. Capitalize subject line
4. No period at end of subject
5. Use imperative mood ("Fix bug" not "Fixed bug")
6. Wrap body at 72 characters
7. Explain what and why, not how

**Note**: This skill follows Chris Beams' original seven rules only. No scope prefixes like `feat(auth):` or `fix(api):` are used. Subject lines use imperative verbs directly: `Add feature`, `Fix bug`, `Refactor code`.

## Resources

### scripts/

**analyze_staged.py**: Extract staged changes for commit message generation
- Usage: `python scripts/analyze_staged.py --json`
- Returns: Files, stats, and full diff of staged changes
- Claude analyzes diff to generate meaningful commit message

**suggest_commits.py**: Extract PR changes for history restructuring
- Usage: `python scripts/suggest_commits.py [base_branch] --json`
- Returns: Final diff (source of truth), current commits (reference), backup commands
- Claude analyzes final diff to suggest atomic commit organization

### references/

**commit-guide.md**: Comprehensive guide to seven rules, atomic commits, and examples
- Load when detailed guidance needed
- Includes anti-patterns and best practices
- Imperative verbs, body structure templates

## Examples

### Example 1: Simple Commit Message

**User**: "커밋 메시지 만들어줘"

**Action**:
1. Run `analyze_staged.py --json`
2. Analyze diff: Added null check to prevent crash
3. Generate message following seven rules

**Output**:
```
Prevent null pointer in token validation

Token validator crashed when receiving null tokens from
malformed requests. Add null check at validation entry point
and return 400 Bad Request for invalid input.

Fixes #789
```

### Example 2: Complex PR Restructuring

**User**: "PR 커밋 히스토리 정리해줘"

**Action**:
1. Run `suggest_commits.py --json`
2. Analyze `total_diff` (final changes): Auth system + tests
3. Review `current_commits`: 7 commits including WIP/typos
4. Identify final diff has only 3 logical changes

**Output**:
```
Current history has 7 commits with temporary changes.
Final diff shows 3 logical changes.

Suggested restructuring:

1. Add JWT authentication system
   - auth.js, middleware/auth.js, utils/jwt.js
   +83 -0

2. Add protected route middleware
   - middleware/protected.js, routes/api.js
   +42 -5

3. Add authentication test coverage
   - tests/auth.test.js, tests/jwt.test.js
   +67 -0

⚠️ Before restructuring:
git branch backup/feature-auth-20250118-143022

Then use interactive rebase:
git rebase -i main

Restore if needed:
git reset --hard backup/feature-auth-20250118-143022
```

### Example 3: Multiple Files, Clear Purpose

**User**: "커밋 메시지 작성해줘"

**Staged**: `database/connection.js`, `database/pool.js`, `config/db.js`

**Output**:
```
Refactor database connection pooling

Connection pool exhaustion occurred under high load due to
connections not being properly released after queries.

Implement connection pool with configurable size limits and
automatic connection release using try-finally blocks.

See: docs/database-pooling.md
```
