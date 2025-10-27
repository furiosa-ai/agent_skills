---
description: Update documentation by incorporating unresolved PR comments and feedback (Step 3 of 3-phase workflow)
---

# Update Documentation from PR Comments

Use the **update-docs** skill to integrate PR feedback into existing documentation.

**Usage:**
```
/furiosa:update-docs <pr-number>
```

**This skill will:**

1. **Fetch unresolved PR comments** - Run script to get only unresolved review threads
2. **Determine update scope** - Analyze which sections need updates based on comment locations
3. **Process each comment** - Incorporate new information while maintaining style
4. **Update citations** - Add PR comment URLs as sources: `([Source](url), [PR Comment](comment-url)) [accuracy%]`
5. **Maintain accuracy tracking** - Recalculate confidence scores with new information
6. **Handle conflicts** - Replace contradictory info and add TODO comments for verification
7. **Update metadata** - Refresh "Last Updated" timestamp and add changelog entry

**Requirements:**
- `gh` CLI must be installed and authenticated
- Existing documentation file from `/furiosa:write-docs`
- PR with unresolved comments on the documentation

**Information from PR comments is high-confidence (90-95%)** as it comes from domain experts and code reviewers.

**Workflow:** prepare-docs → write-docs → update-docs (from PR comments)
