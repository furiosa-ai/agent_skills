---
name: commit-msg
description: |
  Generate professional commit messages from staged changes following Chris Beams' seven rules.
  Use when user stages changes and requests commit message. Triggers include:
  - Korean: "커밋 메시지 만들어줘", "커밋 메시지 작성해줘", "commit message 생성"
  - English: "create commit message", "generate commit message", "write commit"
  - Context: User has staged changes (git add) and needs a commit message
---

# Commit Message Generator

## Overview

Generate professional commit messages from staged changes following Chris Beams' seven rules for commit messages.

## ⚠️ Critical Execution Rules

**NEVER cd to skill folder.** Always execute scripts from user's current working directory to preserve git repository context.

**Script execution:**
- You know where this skill's SKILL.md is located when you load it
- Marketplace root = parent directory of the skill directory
- Scripts are at: `<marketplace_root>/scripts/analyze_diff.py`
- Compute the path, then execute from user's current working directory

## Workflow

### Step 1: Extract Staged Changes

Execute the analyze_diff script from the marketplace scripts directory:

```bash
# Example: If skill is at ~/.claude/plugins/marketplaces/agent-skills/commit-msg/SKILL.md
# Then marketplace root is ~/.claude/plugins/marketplaces/agent-skills/
# And script is at ~/.claude/plugins/marketplaces/agent-skills/scripts/analyze_diff.py
python3 <marketplace_root>/scripts/analyze_diff.py --staged --json
```

This returns:
```json
{
  "files": ["auth.js", "tests/auth.test.js"],
  "stats": {"insertions": 45, "deletions": 12, "files_changed": 2},
  "diff": "full diff content...",
  "diff_type": "full"
}
```

### Step 2: Analyze the Diff

Read the actual code changes to understand:
- What changed (high-level)
- Why this change matters
- Appropriate imperative verb (Add/Fix/Refactor/Update/etc.)

### Step 3: Generate Commit Message

Follow Chris Beams' seven rules:

1. **Separate subject from body with blank line**
2. **Limit subject line to 50 characters**
3. **Capitalize the subject line**
4. **Do not end the subject line with a period**
5. **Use imperative mood** ("Fix bug" not "Fixed bug")
6. **Wrap body at 72 characters**
7. **Explain what and why, not how**

**Format**:
```
Subject line (50 chars max, imperative, capitalized, no period)

Body paragraph explaining WHY this change was needed and WHAT
it accomplishes (not HOW). Wrap at 72 characters per line.

Can include multiple paragraphs, bullet points, or issue refs.

Fixes #1234
```

### Step 4: Present to User

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

## Reference

See `references/commit-guide.md` for detailed explanation of the seven rules with examples.

## Examples

**Simple change**:
```
Add user email validation

Email addresses were accepted without format validation,
causing database errors when invalid emails were stored.

Add regex validation before saving to ensure valid format.
```

**Bug fix**:
```
Fix race condition in token refresh

Background token refresh could override user-initiated
refresh, causing authentication failures.

Add mutex lock around refresh operations to prevent
concurrent modifications.

Fixes #456
```

**Feature addition**:
```
Add dark mode toggle to settings

Users requested ability to switch between light and dark
themes without changing system preferences.

Implement theme toggle in settings page with localStorage
persistence across sessions.
```
