---
name: update-docs
description: |
  Use when user requests updating documentation based on PR comments. Triggers include:
  - Korean: "PR 코멘트 반영해줘", "PR 피드백 반영", "문서 업데이트해줘"
  - English: "update docs from PR comments", "incorporate PR feedback", "apply PR suggestions"
  - Context: User has PR with comments on documentation file and wants to incorporate feedback

  This skill focuses on Step 3 of automated workflow: Integrating PR comments into existing documentation
  while maintaining accuracy tracking, citations, and consistency with original style.
---

# Documentation Update Skill (Automated Workflow - Step 3)

## Overview

This skill updates existing documentation based on PR comments and feedback. Each update:
- Incorporates new information from PR comments
- Maintains per-sentence accuracy tracking
- Cites PR comments as sources alongside original sources
- Preserves existing structure and style

**When to use this skill:**
- User received PR feedback on documentation
- "PR #123 코멘트 반영해줘" / "update docs from PR comments"

**Prerequisites:**
- Existing documentation file
- PR with comments on documentation file

---

## ⚠️ Critical Execution Rules

**Script execution:**
- You know where this skill's SKILL.md is located when you load it
- Marketplace root = parent directory of the skill directory
- Scripts are at: `<marketplace_root>/scripts/`
  - `fetch_pr_comments.py` - Fetch PR comments
  - `reply_to_comment.py` - Reply to PR comments
- Compute the path, then execute from user's current working directory

---

## ⚠️ CRITICAL RULES (Read Before Every Task)

Before starting documentation update, verify you understand these **2 non-negotiable** rules:

### 1. Citation Format (MANDATORY)
- [ ] **Every statement** has `([Source](URL)) [accuracy%]` format
- [ ] Local files use **relative paths from document location**: `../src/file.rs#L50` (NO `file://` prefix)
- [ ] Statements with `accuracy < 70%` **MUST have rationale blockquote** below

### 2. Accuracy Calculation (MANDATORY)
- [ ] **90-100%**: Direct facts from source code/docs
- [ ] **70-89%**: Clear inference combining multiple facts
- [ ] **Below 70%**: Speculation involved → **MUST include rationale explaining confidence breakdown**

**⚠️ If you forget these rules during update, STOP and re-read this section.**

---

## 📋 Recommended Practices

Use GitHub's rich formatting features for clearer, more expressive documentation:

- **Mermaid diagrams**: Visual representation of architecture, data flow, sequences
- **Tables**: Structured parameter lists, type definitions, comparison charts
- **GitHub alerts**: Highlight important notes, warnings, deprecations (`> [!NOTE]`, `> [!WARNING]`)
- **LaTeX math**: Mathematical formulas and equations (`$inline$` or `$$block$$`)
- **Code highlighting**: Language-specific syntax highlighting
- **Collapsible sections**: Hide detailed content until needed (`<details>`)

These formats improve readability and make complex information easier to understand.

---

## Workflow: Documentation Update

### Step 1: Extract Unresolved Comment Content and Scope

Use Python script to fetch **unresolved PR comments only**.

**Fetch unresolved comments:**

```bash
python3 <marketplace_root>/scripts/fetch_pr_comments.py {owner} {repo} {pr_number} --json
```

**Script automatically:**
- Queries GraphQL for all review threads
- Filters `isResolved: false` threads only
- Returns JSON with comment details

**Example output:**
```json
{
  "pr_number": 123,
  "unresolved_count": 3,
  "comments": [
    {
      "comment_id": "123456",
      "thread_id": "RT_kwDOABC123",
      "body": "Parser also validates syntax during parsing",
      "path": "docs/parser-api.md",
      "line": 42,
      "author": "reviewer_username",
      "is_resolved": false
    }
  ]
}
```

For each unresolved comment, extract:

**1. Comment Type:**
- **Line-specific**: Has `path` and `line` → Scope is that line/section
- **General**: No `path` → Scope determined by comment content (keywords)

**2. New Information:**
- What new facts or corrections does the comment provide?
- Which document section does it relate to?

---

### Step 2: Update Document

For each comment with new information:

**1. Locate target section:**
- Line-specific: Go directly to commented line
- General: Search document for relevant section using keywords

**2. Update statement:**
- Add new information or correct existing statement
- Include PR comment as additional source: `([Source](original), [PR Comment](comment-url)) [accuracy%]`
- Recalculate accuracy if needed
- Add rationale if accuracy < 70%

**Example:**
```markdown
The parser uses recursive descent algorithm and supports error recovery ([Source](../src/parser.rs#L50), [PR Comment](https://github.com/org/repo/pull/123#discussion_r456)) [88%]
> Rationale: Code shows recursive descent implementation (60%), PR comment confirms error recovery feature exists (28%)
```

**3. Handle conflicts:**
If PR comment contradicts existing statement:
- Document both with TODO comment
- Flag for user verification
- Do not auto-resolve

**Example:**
```markdown
<!-- TODO: Conflict detected
- Original doc: Returns Result<AST, ParseError>
- PR Comment #456: Claims it returns Option<AST>
Please verify which is correct. -->
```

**4. Mark updated sections:**
Optionally add comment noting update source:
```markdown
<!-- Updated from PR #123 comment - 2025-10-22 -->
```

---

### Step 3: Verify Source Links

After completing all updates:

1. **Check all source links** for validity
   - Local files: Verify relative paths resolve correctly from document location
   - Remote URLs: Verify URLs are accessible
   - PR comment links: Verify comment URLs are valid
   - Line numbers: Verify line ranges exist in source files

2. **Fix broken links** before finalizing
   - Update paths if files moved
   - Remove line numbers if file changed significantly
   - Flag links that cannot be verified

3. **Report any unverifiable links** to user

---

### Step 4: Reply to Comments

After updating the document, post replies to each incorporated PR comment.

**Reply templates:**

**For successfully incorporated comments:**
```markdown
Thanks for the feedback! I've updated the documentation:

- **File**: `docs/parser-api.md`, line 42
- **Change**: Added error recovery information with citation
- **Accuracy**: Updated to 88% with rationale

**Updated statement:**
> The parser uses recursive descent algorithm and supports error recovery ([Source](../src/parser.rs#L50), [PR Comment](https://github.com/org/repo/pull/123#discussion_r456)) [88%]

Please review and resolve if this addresses your comment.
```

**For conflicting comments:**
```markdown
Thanks for the comment. I've documented both versions with a TODO for verification:

- **Original**: Returns Result<AST, ParseError>
- **Your comment**: Returns Option<AST>

**Location**: `docs/parser-api.md`, line 67

Could you help verify which is correct? I've added a TODO comment in the documentation.

I've left this unresolved until we can confirm the correct information.
```

**Post reply using Python script:**

```bash
python3 <marketplace_root>/scripts/reply_to_comment.py {owner} {repo} {comment_id} \
  --body "Thanks for the feedback! I've updated..." [--json]
```

**Script automatically:**
- Posts reply via GitHub REST API
- Adds Claude signature: `🤖 *Updated by Claude Code*`
- Returns reply URL

**Example output:**
```json
{
  "success": true,
  "comment_id": "123456",
  "reply_id": "789012",
  "reply_url": "https://github.com/owner/repo/pull/123#discussion_r789012"
}
```

**Important:**
- Post replies to all incorporated comments (successful or conflict)
- Resolve is done by user manually on GitHub UI
- User can easily identify Claude's replies by 🤖 signature

---

## Handling Contradictions

If PR comment contradicts existing statement:

1. **Document both claims** with their sources
2. **Add TODO comment** for human verification
3. **Never auto-resolve conflicts**

**Example:**
```markdown
The `parse()` function returns `Result<AST, ParseError>` ([Source](../src/parser.rs#L50)) [95%]

<!-- TODO: Conflict detected
- Original doc (from src/parser.rs#L50): Returns Result<AST, ParseError>
- PR Comment #456: Claims it returns Option<AST>
Please verify which is correct. -->

> [!WARNING]
> Conflicting information found between original documentation and PR comment. Recommend verifying with maintainer.
```

---

## Tips for Effective Updates

1. **Read PR comments carefully** - Understand the intent behind feedback, not just literal text

2. **Use rationale for transparency** - For all statements with accuracy < 70%, explain the inference process

3. **Preserve existing style** - Match the tone and terminology of the original document

---

## Conclusion

After completing this update workflow, you should have:

✅ Fetched unresolved comments only (`isResolved: false`)
✅ Extracted new information from PR comments
✅ Updated document with PR comment citations
✅ Maintained per-sentence accuracy tracking
✅ Added rationale for all statements with accuracy < 70%
✅ Flagged contradictions with TODO comments
✅ Verified all source links are valid (including PR comment links)
✅ Posted replies to all incorporated comments (with 🤖 Claude Code signature)

**Next action:** User reviews Claude's replies on GitHub, manually resolves conversations, and pushes updated documentation.
