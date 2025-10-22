---
name: generate-docs
description: |
  Use when user requests actual documentation generation with accuracy tracking. Triggers include:
  - Korean: "문서 생성해줘", "문서 작성해줘", "코드 문서화해줘"
  - English: "generate documentation", "write documentation", "document this code"
  - Context: User has a plan from plan-docs skill with sources, doc type, structure, and threshold

  This skill focuses on Phase 2: Analyzing sources and generating documentation with per-sentence
  accuracy tracking, inline citations, and rigorous fact-checking. Excludes statements below threshold.
---

# Documentation Generation Skill (Phase 2)

## Overview

This skill generates technical documentation with **per-sentence accuracy tracking**. Each statement includes:
- Inline source citation with URL (relative paths for local files)
- Accuracy percentage (0-100%)
- Rationale blockquote for statements with accuracy < 90%

Statements below the user-defined threshold are **excluded** from the final document.

**When to use this skill:**
- User completed plan-docs and ready to generate
- "코드 문서화해줘" / "generate API documentation"

**Prerequisites:**
- Plan from plan-docs skill with sources, doc type, structure, threshold

---

## ⚠️ CRITICAL RULES (Read Before Every Task)

Before starting documentation generation, verify you understand these **2 non-negotiable** rules:

### 1. Citation Format (MANDATORY)
- [ ] **Every statement** has `([Source](URL)) [accuracy%]` format
- [ ] Local files use **relative paths from document location**: `../src/file.rs#L50` (NO `file://` prefix)
- [ ] Statements with `accuracy < threshold` are **EXCLUDED** (don't write them)
- [ ] Statements with `accuracy < 90%` **MUST have rationale blockquote** below

### 2. Accuracy Calculation (MANDATORY)
- [ ] **90-100%**: Direct facts from source code/docs
- [ ] **70-89%**: Clear inference combining multiple facts
- [ ] **50-69%**: Speculation involved (usually below threshold → excluded)
- [ ] **Below threshold**: DO NOT WRITE (mark as Analysis Gap instead)

**⚠️ If you forget these rules during generation, STOP and re-read this section.**

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

## Workflow: Documentation Generation

### Step 1: Receive Plan from plan-docs

Receive from plan-docs skill:
- Source list with accessibility confirmed
- Document type (API Reference, System Overview, Tutorial, Custom)
- Document structure (sections to include)
- Accuracy threshold (e.g., 70%)
- Gap analysis with filling decisions

**Then access sources using:** Read (local files), WebFetch (web/remote), MCP (Drive/Notion), `gh` (PR comments)

---

### Step 2: Analyze Sources and Write Documentation

#### Accuracy Calculation

For each statement, calculate accuracy:

| Accuracy | Criteria | Example |
|----------|----------|---------|
| **90-100%** | Direct fact from source | "Function `parse()` accepts `String`" (visible in signature) |
| **70-89%** | Clear inference from multiple facts | "Module handles auth" (from function names + module name) |
| **50-69%** | Speculation, pattern-based | "Likely retries on failure" (pattern but not documented) |
| **0-49%** | Mostly speculation | "Probably uses caching" (no evidence) |

**Key principle**: Be honest. If guessing, accuracy should be low. Below threshold = exclude.

---

#### Writing with Citations

Every statement format:
```markdown
Statement ([Source](URL)) [accuracy%]
```

**Local file citation (relative path from document location):**
```markdown
The Parser struct implements recursive descent algorithm ([Source](../src/parser.rs#L120)) [93%]
```

If document is at `docs/api-reference.md` and source is at `src/parser.rs`, use `../src/parser.rs#L120`.

**If accuracy < 90%, add rationale:**
```markdown
Statement ([Source](URL)) [accuracy%]
> Rationale: [Explain inference process: what evidence led to this conclusion]
```

**Example:**
```markdown
This module handles user authentication ([Source1](../src/auth.rs#L10), [Source2](../README.md#L23)) [82%]
> Rationale: Module is named 'auth', contains login/logout/verify functions, and README explicitly states it "handles authentication"
```

**High-confidence statement (no rationale needed):**
```markdown
The `calculate()` function performs matrix multiplication ([Source](https://github.com/org/repo/blob/main/src/math.rs#L45)) [95%]
```

---

### Step 3: Verify Source Links

After completing document generation:

1. **Check all source links** for validity
   - Local files: Verify relative paths resolve correctly from document location
   - Remote URLs: Verify URLs are accessible
   - Line numbers: Verify line ranges exist in source files

2. **Fix broken links** before finalizing
   - Update paths if files moved
   - Remove line numbers if file changed significantly
   - Flag links that cannot be verified

3. **Report any unverifiable links** to user

---

## Handling Contradictions and Gaps

### Contradictions Between Sources

If two sources provide conflicting information:

1. **Document both claims** with their sources
2. **Add TODO comment** for human verification
3. **Never auto-resolve conflicts**

**Example:**
```markdown
The `parse()` function returns `Result<AST, ParseError>` on failure ([Source](../src/parser.rs#L50)) [95%]

<!-- TODO: Conflict detected
- Code (src/parser.rs#L50): Returns Result<AST, ParseError>
- Docs (design.md#L30): Claims it returns Option<AST>
Please verify which is correct. Code is likely more authoritative. -->

> [!WARNING]
> Conflicting information found between code and documentation. Recommend verifying with maintainer.
```

---

### Analysis Gaps

When important information cannot be documented with sufficient confidence:

**Add Analysis Gap comment in document body** where it belongs:

```markdown
## Performance Characteristics

<!-- Analysis Gap: Unable to determine performance characteristics with sufficient confidence
Sources analyzed: src/parser.rs, tests/
Recommendation: Check for benches/ directory or ask maintainer for benchmark data -->
```

Do NOT create separate gap summary. Document gaps clearly in-place where information should appear.

---

## Tips for Effective Generation

1. **Read sources thoroughly** - Don't skim. Read entire relevant sections to understand context and avoid missing critical details.

2. **Use rationale for transparency** - For all statements with accuracy < 90%, explain the inference process so readers understand how you arrived at the conclusion.

3. **Follow project conventions** - Match existing terminology and style from the codebase. If code uses "handler", use "handler" not "processor".

---

## Handoff to update-docs

After generating documentation, inform user:

> "문서 생성이 완료되었습니다. PR 피드백을 받으시면 update-docs 스킬로 문서를 업데이트할 수 있습니다."
>
> (Documentation generation complete. If you receive PR feedback, you can update the documentation using the update-docs skill.)

---

## Conclusion

After completing this generation workflow, you should have:

✅ Analyzed all sources thoroughly
✅ Generated documentation with per-sentence citations and accuracy scores
✅ Used relative paths for local file citations (from document location)
✅ Excluded statements below threshold
✅ Added rationale for all statements with accuracy < 90%
✅ Flagged contradictions with TODO comments
✅ Documented analysis gaps in-place (no separate summary)
✅ Verified all source links are valid

**Next action:** User reviews document, optionally creates PR, uses update-docs for refinement.
