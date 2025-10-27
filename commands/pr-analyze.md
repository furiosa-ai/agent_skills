---
description: Find base branch candidates for PR creation or commit history restructuring
---

# Analyze Base Branch Candidates

!python3 git-commit-helper/scripts/find_base_branch.py --json

---

The base branch candidates are listed above, ranked by commit count.

**Next steps:**

1. Review the candidate branches
2. Ask the user to select the correct base branch
3. Use that base branch for PR creation or commit history analysis

This is typically used as a preliminary step before running `/furiosa:pr-create` or when restructuring commit history.
