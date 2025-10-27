---
description: Create pull request from current branch with AI-generated title and description
---

# Create Pull Request

Use the **git-commit-helper** skill to create a pull request for the current branch.

**The skill will:**

1. Check if a PR already exists for this branch
2. Find base branch candidates (or reuse previous analysis if available)
3. Ask you to select the base branch
4. Analyze the final diff between base and HEAD
5. Check for PR template in the repository
6. Generate PR title and body from the final diff
7. Show you the generated content for approval
8. Create the PR using `gh pr create`

**Requirements:**
- `gh` CLI must be installed and authenticated
- Current branch must have commits ahead of base branch
- Push current branch to remote first if needed

Run this command when you're ready to create a pull request from your current branch.
