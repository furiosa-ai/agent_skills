---
name: git-commit-helper
description: Generate professional Git commit messages and manage pull request workflow. Use when user stages changes and requests commit message, wants to restructure PR commit history, or needs to create/update pull requests. Triggers include "커밋 메시지 만들어줘", "commit message", "PR 만들어줘", "create PR", "PR 히스토리 정리", "restructure commits", "clean up commits", "PR 업데이트", "update PR". Applies Chris Beams' seven rules for commit messages and atomic commit principles.
---

# Git Commit Helper

## Overview

Guide commit message creation and PR history restructuring following professional Git practices based on Chris Beams' seven rules. Supports two main workflows: generating commit messages from staged changes, and reorganizing commit history based on final diff analysis.

## Trigger Phrases

This skill activates automatically when you use phrases like:

**Korean (한국어)**:
- 커밋 메시지 만들어줘 / 작성해줘
- PR 만들어줘 / 생성해줘
- PR 히스토리 정리해줘 / 정리하자
- PR 업데이트해줘 / 수정해줘

**English**:
- Create/generate/write commit message
- Make/create/open pull request (PR)
- Clean up/restructure/organize commits
- Update PR / modify PR description

**💡 Tip**: If skill doesn't activate automatically, use explicit prefix:
- `git-commit-helper 커밋 메시지 만들어줘`
- `git-commit-helper create commit message`

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
   python scripts/analyze_diff.py --staged --json
   ```

   Returns:
   ```json
   {
     "files": ["auth.js", "tests/auth.test.js"],
     "stats": {"insertions": 45, "deletions": 12, "files_changed": 2},
     "diff": "full diff content...",
     "diff_type": "full"
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

1. **Find base branch candidates and let user select**:

   ⚠️ **IMPORTANT: Always let user select the correct base branch**

   **Step 1 - Find candidates**:
   ```bash
   python scripts/find_base_branch.py
   ```

   **Step 2 - Show candidates to user**:

   Example output:
   ```
   Current branch: refactor/aten-macro-refactoring

   Found 3 base branch candidate(s):

   1. upstream/master
      Base: 99cafb6bc3 (Merge #14774)
      Commits: 6

   2. origin/master
      Base: 0d7c549be3 (Merge #14116)
      Commits: 4346
   ```

   **Step 3 - Ask user to select**:
   - "Which base branch is correct?"
   - "Or specify a different base (branch name or commit SHA)"

   **Step 4 - Run with selected base**:
   ```bash
   # If user selects candidate #1 (99cafb6bc3)
   python scripts/analyze_diff.py 99cafb6bc3 --json

   # If user specifies custom base (e.g., refactor/aten-infrastructure-improvements)
   python scripts/analyze_diff.py refactor/aten-infrastructure-improvements --json
   ```

   **Why user selection is needed**:
   - Feature branches from feature branches won't appear in candidates (only master/main)
   - User knows the actual parent branch (e.g., `078889590a` in this case)
   - Commit count helps identify the closest branch

   **Common scenarios**:
   - ✅ Direct from master → Select candidate #1 (lowest commit count)
   - ⚠️ Feature from feature → Specify parent feature branch manually
   - ⚠️ Forked repo → Check which remote is correct

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

### 3. Create Pull Request

Generate PR title and description from commit history and create a new pull request.

**When to use**: User wants to create a PR for their current branch.

**Trigger phrases**:
- "Create PR"
- "Open PR"
- "PR open"
- "PR 만들어줘"
- "PR 생성해줘"

**IMPORTANT PRINCIPLES**:
- **Check PR existence first**: Use `gh pr view` to check if PR already exists
- **User confirmation required**: Always show generated title/body before creating
- **Use PR template if available**: Respect project's PR template structure
- **Chris Beams' rules apply**: PR title follows same rules as commit subject

**Workflow**:

1. **Check if PR already exists**:
   ```bash
   gh pr view --json number,title,body 2>&1
   ```

   If PR exists, suggest using update workflow instead.

2. **Find base branch** (same as restructuring workflow):
   ```bash
   python scripts/find_base_branch.py --json
   ```

   Show candidates to user and let them select.

3. **Analyze final diff with smart fallback**:

   ⚠️ **IMPORTANT: Use final diff as source of truth, same as restructuring workflow**

   If recently ran `analyze_diff.py` with same base:
   - Check if analysis succeeded (no large PR error)
   - Reuse the analysis results if available
   - Skip re-analysis for efficiency

   Otherwise, analyze now. The script uses **three-tier strategy** for large PRs:

   **Tier 1 - Full diff** (total <= 5000 lines):
   - Returns complete diff with all changes
   - Best quality analysis possible
   - `diff_type: "full"`

   **Tier 2 - Additions only** (total > 5000 BUT additions <= 5000):
   - Returns only added/modified lines (deletions omitted)
   - Still provides good analysis of new functionality
   - Shows warning: "Showing additions only, deletions omitted"
   - Claude can generate meaningful PR description from additions
   - `diff_type: "additions_only"`

   **Tier 3 - Error** (additions > 5000):
   - Script returns error without diff
   - Suggests splitting PR into smaller pieces
   - Can override with `--allow-large` flag
   - `diff_type: "full_forced"` if forced
   - ⚠️ Forced analysis may fail due to context limits

   ```bash
   # Normal execution (auto-fallback)
   python scripts/analyze_diff.py <base> --json

   # Force large PR (if additions > 5000)
   python scripts/analyze_diff.py <base> --json --allow-large
   ```

   **Key principle**: Individual commits are reference only. The final diff shows what actually changed and that's what matters for PR description.

4. **Check for PR template**:

   Check common locations in order:
   - `.github/PULL_REQUEST_TEMPLATE.md`
   - `.github/pull_request_template.md`
   - `.github/PULL_REQUEST_TEMPLATE/*.md` (if multiple templates, list them and ask user)
   - `docs/PULL_REQUEST_TEMPLATE.md`
   - `PULL_REQUEST_TEMPLATE.md` (root)

   If found, read the template content for structure.

5. **Generate PR title**:

   Analyze the **final diff** (NOT commit messages) to understand the overall change:
   - Read the actual code changes to identify the high-level purpose
   - Create title that describes the complete feature/fix/refactor
   - Follow Chris Beams' rules: imperative mood, 50 chars max, capitalized, no period
   - Examples:
     - "Add user authentication system" (not "Add JWT + Add login + Fix tests")
     - "Refactor database connection pooling" (describes the end state)

   **Note**: Commit messages are hints, but final diff is the truth. If commits were messy WIP messages, ignore them and describe the actual final change.

6. **Generate PR body**:

   **If template found**:
   - Read template content
   - Preserve template structure (headers, checkboxes, sections)
   - Fill in content based on **final diff analysis**:
     - Description/Summary: Analyze final diff for high-level changes (what was added/changed/fixed)
     - Changes/Modifications: List key logical changes from diff (e.g., "Authentication layer", "Database refactoring")
     - Testing/Test Plan: Check if test files were added/modified in final diff
     - Related Issues: Extract "Fixes #123" from commit messages (if present)
   - Keep template placeholders if unable to fill
   - Add Claude Code attribution at the end

   **If no template**:
   ```markdown
   ## Summary
   - [Key logical change 1 from final diff analysis]
   - [Key logical change 2]
   - [Key logical change 3]

   ## Related Commits
   - [Commit list for reference, if helpful]

   🤖 Generated with [Claude Code](https://claude.com/claude-code)
   ```

   **Important**: The summary bullets should describe logical groups of changes from the final diff, NOT just list commit messages. For example:
   - ❌ "Add JWT", "Fix tests", "Update docs" (commit-based)
   - ✅ "Implement JWT authentication with role-based access control" (diff-based)

7. **Show to user for confirmation**:
   ```
   I'll create a PR with the following:

   Title: [generated title]
   Base: [selected base branch]

   Body:
   [generated body with template structure if applicable]

   Should I proceed? You can ask me to modify the title or body first.
   ```

8. **Create PR** (only after user approval):
   ```bash
   gh pr create --title "..." --body "..." --base <base-branch>
   ```

9. **Return PR URL**:
   ```
   ✅ Pull request created: https://github.com/owner/repo/pull/123
   ```

**Template handling notes**:
- Preserve markdown formatting (headers, lists, checkboxes)
- Keep template comments (<!-- ... -->) if present
- If template has multiple variants in `.github/PULL_REQUEST_TEMPLATE/`, ask user which one to use
- Always add Claude Code attribution unless template explicitly forbids it

**Reference**: PR titles follow same seven rules as commit subjects.

### 4. Update Pull Request

Refresh PR title and description based on latest commit history.

**When to use**: User wants to update existing PR with latest changes.

**Trigger phrases**:
- "Update PR"
- "Refresh PR"
- "PR 업데이트해줘"
- "PR 수정해줘"

**IMPORTANT PRINCIPLES**:
- **Must have existing PR**: Check PR exists for current branch
- **User confirmation required**: Show old vs new content before updating
- **Respect PR template**: Use same template as creation workflow

**Workflow**:

1. **Get current PR information**:
   ```bash
   gh pr view --json number,title,body,baseRefName
   ```

   If no PR exists, suggest creation workflow instead.

   Returns:
   ```json
   {
     "number": 123,
     "title": "Old PR title",
     "body": "Old PR body...",
     "baseRefName": "main"
   }
   ```

2. **Analyze latest final diff with smart fallback**:

   ⚠️ **IMPORTANT: Use final diff as source of truth**

   If recently analyzed with `analyze_diff.py`:
   - Check if analysis succeeded (no large PR error)
   - Reuse existing analysis results if available

   Otherwise, run `analyze_diff.py` with base from PR.

   The script uses **three-tier strategy** for large PRs:
   - **Tier 1** (<=5000 lines): Full diff
   - **Tier 2** (>5000 total, <=5000 additions): Additions only
   - **Tier 3** (>5000 additions): Error (use `--allow-large` to force)

   See PR Creation workflow Step 3 for detailed tier descriptions.

3. **Check for PR template** (same as creation workflow):
   - Look in common locations
   - Use template if found for consistency

4. **Generate new title and body**:
   - Same logic as creation workflow
   - Analyze **final diff** (NOT commits) to describe overall change
   - Use PR template if available

5. **Show comparison to user**:
   ```
   Current PR #123:
   Title: [old title]
   Body preview: [first 3 lines...]

   Proposed update:
   Title: [new title]
   Body preview: [first 3 lines...]

   The body was generated using [template name / default format].

   Should I update the PR? You can ask me to:
   - Modify the title or body
   - Show the full body comparison
   - Cancel the update
   ```

6. **Update PR** (only after user approval):
   ```bash
   gh pr edit --title "..." --body "..."
   ```

7. **Confirm update**:
   ```
   ✅ Pull request #123 updated
   View at: https://github.com/owner/repo/pull/123
   ```

**Note**: If user has manually edited PR description on GitHub, warn before overwriting. Consider asking if they want to preserve any manual additions.

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

**analyze_diff.py**: Unified diff analyzer for both staged changes and PR analysis
- Usage:
  - Staged mode: `python scripts/analyze_diff.py --staged --json`
  - Range mode: `python scripts/analyze_diff.py <base_commit> --json [--allow-large]`
- Returns: Diff, stats, diff_type, and mode-specific fields
- Supports three-tier fallback strategy for large diffs (>5000 lines)
- Claude uses output for commit messages (staged) or PR restructuring/creation (range)

**find_base_branch.py**: Find base branch candidates for PR analysis
- Usage: `python scripts/find_base_branch.py --json [--limit N]`
- Returns: Ranked list of base branch candidates with commit counts
- Scans all remote branches and finds merge-bases, sorted by proximity (fewer commits = closer base)
- User selects the correct base from candidates before running analyze_diff.py

### references/

**commit-guide.md**: Comprehensive guide to seven rules, atomic commits, and examples
- Load when detailed guidance needed
- Includes anti-patterns and best practices
- Imperative verbs, body structure templates

## Examples

### Example 1: Simple Commit Message

**User**: "커밋 메시지 만들어줘"

**Action**:
1. Run `analyze_diff.py --staged --json`
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
1. Run `find_base_branch.py` to get candidates
2. **Show candidates to user**:
   ```
   1. upstream/master (99cafb6bc3) - 6 commits
   2. origin/master (0d7c549be3) - 4346 commits
   ```
3. **Ask user**: "Which base is correct? Or specify a different one?"
4. **User responds**: "Use `078889590a` (refactor/aten-infrastructure-improvements)"
5. Run `analyze_diff.py 078889590a --json`
6. Analyze `total_diff`: 1 commit with macro refactoring changes
7. Suggest atomic commit organization if needed

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
