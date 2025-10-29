---
name: pr-create
description: |
  Create pull request from current branch with AI-generated title and description.
  Use when user wants to create a PR for their current branch. Triggers include:
  - Korean: "PR 만들어줘", "PR 생성해줘", "풀 리퀘스트 만들어줘"
  - English: "create PR", "open PR", "make pull request"
  - Context: User has commits on current branch and wants to open PR
---

# Pull Request Creator

## Overview

Generate PR title and description from final diff analysis and create a new pull request.

## ⚠️ Critical Execution Rules

**NEVER cd to skill folder.** Always execute scripts from user's current working directory to preserve git repository context.

**Script execution:**
- You know where this skill's SKILL.md is located when you load it
- Marketplace root = parent directory of the skill directory
- Scripts are at: `<marketplace_root>/scripts/`
  - `find_base_branch.py` - Find base candidates
  - `analyze_diff.py` - Analyze final diff
- Compute the path, then execute from user's current working directory

## Important Principles

1. **Check PR existence first**: Use `gh pr view` to check if PR already exists
2. **User confirmation required**: Always show generated title/body before creating
3. **Use PR template if available**: Respect project's PR template structure
4. **Final diff is source of truth**: PR description based on `base..HEAD` diff, not commit messages
5. **Chris Beams' rules apply**: PR title follows same rules as commit subject

## Workflow

### Step 1: Check if PR Already Exists

```bash
gh pr view --json number,title,body 2>&1
```

If PR exists, inform user that PR already exists for this branch.

### Step 2: Find Base Branch

Execute find_base_branch to get candidates:

```bash
python3 <marketplace_root>/scripts/find_base_branch.py --json
```

Show candidates to user and let them select the correct base.

### Step 3: Analyze Final Diff

⚠️ **IMPORTANT**: Use final diff as source of truth. Individual commits are reference only.

**Three-tier strategy** for large PRs:

**Tier 1 - Full diff** (total ≤ 5000 lines):
- Returns complete diff with all changes
- Best quality analysis
- `diff_type: "full"`

**Tier 2 - Additions only** (total > 5000 BUT additions ≤ 5000):
- Returns only added/modified lines (deletions omitted)
- Still provides good analysis of new functionality
- Shows warning: "Showing additions only, deletions omitted"
- `diff_type: "additions_only"`

**Tier 3 - Error** (additions > 5000):
- Script returns error without diff
- Suggests splitting PR into smaller pieces
- Can override with `--allow-large` flag
- `diff_type: "full_forced"` if forced
- ⚠️ Forced analysis may fail due to context limits

```bash
# Normal execution (auto-fallback)
python3 <marketplace_root>/scripts/analyze_diff.py <base> --json

# Force large PR (if additions > 5000)
python3 <marketplace_root>/scripts/analyze_diff.py <base> --json --allow-large
```

**Reuse recent analysis**: If user ran pr-analyze with same base recently, and got successful diff, can reuse that analysis for efficiency.

### Step 4: Check for PR Template

Check common locations in order:
- `.github/PULL_REQUEST_TEMPLATE.md`
- `.github/pull_request_template.md`
- `.github/PULL_REQUEST_TEMPLATE/*.md` (if multiple, ask user which one)
- `docs/PULL_REQUEST_TEMPLATE.md`
- `PULL_REQUEST_TEMPLATE.md` (root)

If found, read the template content for structure.

### Step 5: Generate PR Title

Analyze the **final diff** (NOT commit messages) to understand the overall change:
- Read the actual code changes to identify the high-level purpose
- Create title that describes the complete feature/fix/refactor
- Follow Chris Beams' rules: imperative mood, 50 chars max, capitalized, no period

**Examples**:
- ✅ "Add user authentication system"
- ✅ "Refactor database connection pooling"
- ❌ "Add JWT + Add login + Fix tests" (too granular)

**Note**: Commit messages are hints, but final diff is the truth. If commits were messy WIP messages, ignore them and describe the actual final change.

### Step 6: Generate PR Body

**If template found**:
- Preserve template structure (headers, checkboxes, sections)
- Fill in content based on **final diff analysis**:
  - Description/Summary: Analyze final diff for high-level changes
  - Changes/Modifications: List key logical changes from diff
  - Testing/Test Plan: Check if test files were added/modified
  - Related Issues: Extract "Fixes #123" from commit messages
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

**Important**: Summary bullets should describe logical groups of changes from final diff, NOT just list commit messages.

- ❌ "Add JWT", "Fix tests", "Update docs" (commit-based)
- ✅ "Implement JWT authentication with role-based access control" (diff-based)

### Step 7: Show to User for Confirmation

```
I'll create a PR with the following:

Title: [generated title]
Base: [selected base branch]

Body:
[generated body with template structure if applicable]

Should I proceed? You can ask me to modify the title or body first.
```

### Step 8: Create PR

Only after user approval:

```bash
gh pr create --title "..." --body "..." --base <base-branch>
```

### Step 9: Return PR URL

```
✅ Pull request created: https://github.com/owner/repo/pull/123
```

## Template Handling Notes

- Preserve markdown formatting (headers, lists, checkboxes)
- Keep template comments (<!-- ... -->) if present
- If template has multiple variants in `.github/PULL_REQUEST_TEMPLATE/`, ask user which one to use
- Always add Claude Code attribution unless template explicitly forbids it

## Requirements

- `gh` CLI must be installed and authenticated
- Current branch must have commits ahead of base branch
- Push current branch to remote first if not already pushed

## Examples

**Simple Feature PR**:
```
Title: Add dark mode toggle

Body:
## Summary
- Implement theme toggle in settings page
- Add localStorage persistence for theme preference
- Update existing components to support both themes

## Testing
- Manually tested theme switching
- Verified persistence across browser sessions
- Checked all major UI components in both modes

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

**Bug Fix PR**:
```
Title: Fix race condition in token refresh

Body:
## Summary
- Add mutex lock around token refresh operations
- Prevent concurrent refresh requests from overriding each other
- Add retry logic for failed refresh attempts

## Related Issues
Fixes #456

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```
