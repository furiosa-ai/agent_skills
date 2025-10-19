# Agent Skills for Amp

This file provides guidance for Amp when working with Git commit messages and pull requests.

## Available Slash Commands

When user invokes these commands, the scripts will output JSON data that you must interpret:

- `/commit-msg` - Generate commit message from staged changes
- `/pr-analyze` - Find base branch and prepare for PR analysis
- `/pr-create` - Create pull request with auto-generated description
- `/pr-update` - Update existing PR description

## Core Instructions

For complete workflow details, see:
@git-commit-helper/SKILL.md

## Quick Reference: The Seven Rules

Always follow these rules for commit messages and PR titles:

1. Separate subject from body with blank line
2. Limit subject to 50 characters
3. Capitalize subject line
4. No period at end of subject
5. Use imperative mood ("Add feature" not "Added feature")
6. Wrap body at 72 characters
7. Explain what and why, not how

**Important**: No scope prefixes like `feat(auth):`. Use imperative verbs directly.

## Key Principles for Amp

1. **Slash commands provide JSON + workflow hints** - Parse the data and follow the workflow instructions in the output
2. **Each slash command tells you what to do next** - Follow the numbered steps in the command output
3. **Use final diff as source of truth** - Individual commits are reference only for PR workflows
4. **Always require user confirmation** - Before destructive operations (rebase, PR create/update)
5. **Run scripts only when instructed** - Slash commands tell you when to run Python scripts directly
6. **Refer to this file for details** - Slash commands reference specific sections here for complete workflows

### Core Workflows Summary

#### 1. Generate Commit Message from Staged Changes

**When**: User has staged changes (`git add`) and needs a commit message.

**Steps**:

1. Run the analyzer script:
   ```bash
   python3 git-commit-helper/scripts/analyze_diff.py --staged --json
   ```

2. Analyze the returned diff to understand:
   - What changed (high-level purpose)
   - Why this change matters
   - Appropriate imperative verb (Add/Fix/Refactor/Update)

3. Generate commit message following the seven rules:
   - Subject: 50 chars max, imperative, capitalized, no period
   - Blank line
   - Body: 72 chars/line, explain WHY and WHAT (not HOW)

**Example output**:
```
Prevent null pointer in token validation

Token validator crashed when receiving null tokens from
malformed requests. Add null check at validation entry point
and return 400 Bad Request for invalid input.

Fixes #789
```

#### 2. Restructure PR Commit History

**When**: User wants to clean up messy commit history (WIP commits, typos, etc.)

**Important Principles**:
- Only final diff matters (intermediate commits are reference only)
- Always create backup branch first
- Focus on atomic commits (one logical change per commit)

**Steps**:

1. Find base branch candidates:
   ```bash
   python3 git-commit-helper/scripts/find_base_branch.py --json
   ```

2. **Always show candidates to user and let them select**:
   ```
   Found 3 base branch candidate(s):
   
   1. upstream/master (99cafb6bc3) - 6 commits
   2. origin/master (0d7c549be3) - 4346 commits
   
   Which base branch is correct? Or specify a different base (branch name or commit SHA)?
   ```

3. After user selects, analyze the final diff:
   ```bash
   python3 git-commit-helper/scripts/analyze_diff.py <selected-base> --json
   ```

4. Read the `total_diff` field to understand final state (NOT individual commits)

5. Suggest atomic commit organization based on logical groups

6. If user wants to proceed, provide restructuring instructions:
   ```
   ⚠️ SAFETY FIRST - Create backup:
   git branch backup/feature-name-20250119-123456
   
   Then use interactive rebase:
   git rebase -i <base>
   
   Restore if needed:
   git reset --hard backup/feature-name-20250119-123456
   ```

#### 3. Create Pull Request

**When**: User wants to create a new PR for their branch.

**Important Principles**:
- Check if PR already exists first
- Use final diff as source of truth (not commit messages)
- Respect project's PR template if available
- Always require user confirmation before creating

**Steps**:

1. Check if PR already exists:
   ```bash
   gh pr view --json number,title,body 2>&1
   ```
   If exists, suggest update workflow instead.

2. Find base branch (same as restructuring):
   ```bash
   python3 git-commit-helper/scripts/find_base_branch.py --json
   ```
   Show candidates and let user select.

3. Analyze final diff (may reuse recent analysis):
   ```bash
   python3 git-commit-helper/scripts/analyze_diff.py <base> --json
   ```
   
   **Large PR handling**:
   - ≤5000 lines: Full diff returned
   - >5000 total but ≤5000 additions: Additions only
   - >5000 additions: Error (use `--allow-large` to force)

4. Check for PR template in common locations:
   - `.github/PULL_REQUEST_TEMPLATE.md`
   - `.github/pull_request_template.md`
   - `.github/PULL_REQUEST_TEMPLATE/*.md`
   - `docs/PULL_REQUEST_TEMPLATE.md`
   - `PULL_REQUEST_TEMPLATE.md`

5. Generate PR title from final diff analysis:
   - Describe the complete change (not individual commits)
   - Follow seven rules: imperative, 50 chars, capitalized, no period
   - Example: "Add user authentication system" (not "Add JWT + Add login")

6. Generate PR body:
   - If template exists: Fill template structure with diff analysis
   - If no template: Use default format with Summary + Related Commits
   - Add attribution: `🤖 Generated with Claude Code`

7. Show to user for confirmation with full title and body

8. After approval, create PR:
   ```bash
   gh pr create --title "..." --body "..." --base <base-branch>
   ```

#### 4. Update Pull Request

**When**: User wants to update existing PR with latest changes.

**Steps**:

1. Get current PR information:
   ```bash
   gh pr view --json number,title,body,baseRefName
   ```
   If no PR exists, suggest creation workflow.

2. Analyze latest final diff (may reuse recent analysis):
   ```bash
   python3 git-commit-helper/scripts/analyze_diff.py <base-from-pr> --json
   ```

3. Check for PR template (same as creation)

4. Generate new title and body (same logic as creation)

5. Show comparison to user:
   ```
   Current PR #123:
   Title: [old]
   
   Proposed update:
   Title: [new]
   Body: [preview]
   
   Should I update?
   ```

6. After approval, update PR:
   ```bash
   gh pr edit --title "..." --body "..."
   ```

### Helper Scripts

**analyze_diff.py**:
- Staged mode: `python3 git-commit-helper/scripts/analyze_diff.py --staged --json`
- Range mode: `python3 git-commit-helper/scripts/analyze_diff.py <base> --json [--allow-large]`
- Returns diff, stats, and diff_type (full/additions_only/full_forced)

**find_base_branch.py**:
- Usage: `python3 git-commit-helper/scripts/find_base_branch.py --json [--limit N]`
- Returns ranked list of base branch candidates
- User must select correct base before analyzing diff

### Examples

**Example 1: Simple commit message**
```
User: "커밋 메시지 만들어줘"
→ Run analyze_diff.py --staged
→ Generate message following seven rules
```

**Example 2: PR history cleanup**
```
User: "PR 히스토리 정리해줘"
→ Find base candidates, let user select
→ Analyze final diff with selected base
→ Suggest atomic commits
→ Provide rebase instructions with backup
```

**Example 3: Create PR**
```
User: "PR 만들어줘"
→ Check if PR exists
→ Find base branch, user selects
→ Analyze final diff
→ Check for template
→ Generate title/body from diff analysis
→ Show to user, create after approval
```

### Atomic Commit Principles

- One logical change per commit
- Each commit should be reviewable independently
- Group related changes (e.g., all test files together)
- Separate by concern (feature code vs tests vs docs)

### Common Commands

```bash
# Stage changes
git add <files>

# Create backup
git branch backup/<name>-$(date +%Y%m%d-%H%M%S)

# Interactive rebase
git rebase -i <base>

# Restore from backup
git reset --hard backup/<name>

# Check PR status
gh pr view

# Create PR
gh pr create --title "..." --body "..." --base main

# Update PR
gh pr edit --title "..." --body "..."
```

## Reference Documentation

See `git-commit-helper/references/commit-guide.md` for detailed guidance on:
- The seven rules with examples
- Atomic commit best practices
- Anti-patterns to avoid
- Imperative verb examples
