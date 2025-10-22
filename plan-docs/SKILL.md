---
name: plan-docs
description: |
  Use when user requests documentation planning or structure definition. Triggers include:
  - Korean: "문서화 계획", "문서 구조", "문서화 설계", "문서 계획 세워줘"
  - English: "documentation plan", "plan documentation", "document structure", "outline documentation"
  - Context: User wants to define WHAT to document before generating actual documentation

  This skill focuses on Phase 1: Planning what sources to analyze, what document type to create,
  what sections/information to include, and how to fill any gaps. After planning, hand off to generate-docs skill.
---

# Documentation Planning Skill (Phase 1)

## Overview

This skill helps you create a thorough documentation plan BEFORE generating the actual documentation. Planning ensures:

1. **All relevant sources are identified** - No critical information missed
2. **Document structure matches purpose** - API reference vs tutorial vs overview have different needs
3. **Analysis scope is clear** - Know what information to extract from each source
4. **Gaps are identified with filling strategies** - Know what's missing and how to obtain it
5. **Efficient generation** - generate-docs skill has clear instructions to follow

**When to use this skill:**
- User says "문서화 계획 세워줘" or "plan documentation structure"
- Starting a large documentation project with multiple sources
- User wants to define scope before diving into generation

---

## Workflow: 4-Step Planning Process

### Step 1: Collect Source Links

**Questions to ask:**

1. "어떤 소스를 분석할까요?" (What sources should I analyze?)
   - GitHub repositories (URLs or local paths)
   - Web pages (documentation sites, blog posts)
   - Local files (code files, markdown docs, PDFs)
   - Google Drive documents (check for MCP server)
   - Notion pages (check for MCP server)

2. "중점적으로 분석할 키워드나 토픽이 있나요?" (Any specific keywords or topics to focus on?)

---

### Step 2: Select Document Type

Ask: "어떤 문서를 만들까요?" (What type of documentation should I create?)

**Options:**

1. **API Reference**
   - Audience: Developers integrating with the code
   - Focus: Functions, classes, parameters, return values, examples
   - Structure: Organized by module/class/function

2. **System Overview**
   - Audience: Engineers understanding architecture
   - Focus: Components, data flow, design principles, communication patterns
   - Structure: Top-down from high-level to implementation details

3. **Tutorial**
   - Audience: Users learning how to use the system
   - Focus: Step-by-step instructions, practical examples, common pitfalls
   - Structure: Sequential steps with verification checkpoints

4. **Custom**
   - User specifies their own document type and purpose

---

### Step 3: Define Document Structure

Based on document type, outline sections to include.

**For API Reference:**
- Overview (purpose of this module/API)
- Core Concepts (key abstractions)
- Functions (organized by category)
- Types (data structures)
- Constants
- Usage Patterns
- Limitations
- Related APIs

**For System Overview:**
- Introduction (purpose, use cases)
- Architecture (high-level design)
- Components (individual parts + responsibilities)
- Data Flow (how information moves)
- State Management
- Communication Patterns
- Configuration
- Error Handling
- Performance Characteristics

**For Tutorial:**
- Introduction (what you'll learn, time estimate)
- Prerequisites (required knowledge, tools)
- Step 1, 2, 3... (sequential instructions)
- Testing Your Implementation
- Common Pitfalls
- Next Steps

**Check for existing templates:**
- Ask: "프로젝트에 문서 템플릿이 있나요?" (Does the project have a documentation template?)
- If yes, use that structure instead of defaults
- Common locations: `docs/templates/`, `.github/`, `CONTRIBUTING.md` references

**⚠️ Customization:**
- Remove sections not relevant to this specific documentation
- Add sections if user needs special coverage (e.g., "Migration Guide")
- Order sections logically (general → specific)

---

### Step 4: Analyze Sources and Identify Gaps

#### Part A: Source Inventory

For each source, document:
1. What information is available?
2. Which document sections does it support?

**⚠️ Trust all sources** - Don't judge quality or note contradictions. If contradictions exist, generate-docs will handle them during writing.

**Example:**
```
### Source 1: src/parser.rs (427 lines)
- parse() function (L45-60) → Functions section
- Token enum (L10-25) → Types section
- Error handling (L300-350) → Error Handling section

### Source 2: docs/design.md (150 lines)
- Recursive descent rationale → Introduction
- Token design decisions → Core Concepts
```

---

#### Part B: Gap Analysis with Filling Strategies

Identify planned sections that have **no information in any source**, then suggest how to fill those gaps.

**Example:**
```
### Gap 1: Performance Characteristics
**Planned section**: Performance Characteristics
**Status**: No performance data found

**Suggestions to fill this gap:**
- Check for benches/ directory
- Search commit history for "benchmark"
- Ask user for benchmark data
- **Alternative**: Mark as Analysis Gap in final document

### Gap 2: Configuration Options
**Planned section**: Configuration
**Status**: Partial information - config file exists but no explanations

**Suggestions to fill this gap:**
- Analyze config file with inline comments
- Search docs/ for config documentation
- **Alternative**: Document only observable structure
```

---

#### User Interaction After Gap Analysis

Present gaps and ask user to choose actions:

```
"Gap을 X개 발견했습니다. 각각에 대해 어떻게 할까요?"

1. [Gap name]: [filling suggestions]
2. [Gap name]: [filling suggestions]

또는 "있는 정보만으로 진행"하시면 generate-docs가 Analysis Gap 코멘트를 추가합니다.
```

---

### Optional Step 5: Save Plan File

**Ask user:** "계획을 파일로 저장할까요?" (Should I save this plan as a file?)

**If yes:**
Create a `docs/documentation-plan.md` file with:
- All 4 steps documented
- Gap-filling checklist for tracking progress
- Timestamp and version info

**If no:**
Keep plan in conversation context only, proceed directly to generation

**File format example:**
```markdown
# Documentation Plan: Parser Module API Reference

**Created**: 2025-10-21
**Document Type**: API Reference
**Target Audience**: Developers integrating the parser

## Sources
- [ ] src/parser.rs (427 lines)
- [ ] docs/design.md (150 lines)
- [ ] tests/parser_test.rs (320 lines)

## Structure
- [ ] Introduction
- [ ] Core Concepts
- [ ] Functions (parse, tokenize, validate)
- [ ] Types (Token, AST, ParseError)
- [ ] Usage Patterns
- [ ] Limitations

## Gaps and Actions
- [ ] Gap 1: Performance Characteristics
  - Action: Check benches/ directory
  - Alternative: Mark as Analysis Gap
- [ ] Gap 2: Migration Guide
  - Action: Exclude section (out of scope)

## Next Steps
1. Fill gaps (if user requested)
2. Run `generate-docs` skill with this plan
3. Set accuracy threshold (recommended: 70-80%)
4. Review generated document for remaining gaps
5. Iterate with `update-docs` if needed
```

---

## Handoff to generate-docs

After completing the plan (and optional gap-filling), say:

> "문서화 계획이 완료되었습니다. 이제 generate-docs 스킬을 사용해서 실제 문서를 생성하겠습니다."

---

## Tips for Effective Planning

1. **Ask before assuming** - If user's intent is unclear, ask clarifying questions
2. **Suggest recommendations** - "parser 모듈이니까 API Reference가 적합해 보입니다"
3. **Flag gaps early with actionable suggestions** - Not just "information missing" but "check benches/ or exclude section?"
4. **Reuse existing structure** - If project has templates, prefer those over defaults
5. **Give user control over gaps** - Let them decide: fill, exclude, or mark as Analysis Gap

---

## Conclusion

After completing this planning workflow, you should have:

✅ Clear list of sources with accessibility confirmed
✅ Document type chosen based on audience and purpose
✅ Section structure defined (with or without template)
✅ Source inventory showing what information is available
✅ Gap analysis with filling strategies or exclusion decisions
✅ Optional: Saved plan file with checklist for tracking

**Next action:** Invoke `generate-docs` skill with this plan as context.
