---
description: Update existing PR title and description based on latest changes
---

# Update Pull Request

Use the **git-commit-helper** skill to update an existing pull request for the current branch.

**The skill will:**

1. Fetch current PR information using `gh pr view --json`
2. Get the base branch from existing PR
3. Analyze the latest final diff (base..HEAD)
4. Reuse recent analysis if available (efficient workflow)
5. Generate new title and body from current state
6. Show comparison between old and new content
7. Require your confirmation before updating
8. Update PR using `gh pr edit`

**Use cases:**
- Added more commits after PR creation
- Want to regenerate description after changes
- Need to sync PR description with current state

**Warning:** This will overwrite any manual edits made on GitHub. The skill will warn you before proceeding.

**Requirements:**
- `gh` CLI must be installed and authenticated
- Current branch must have an open PR
