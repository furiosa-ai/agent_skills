---
description: Generate accuracy-tracked documentation from requirements file (Step 2 of 3-phase workflow)
---

# Generate Documentation

Use the **write-docs** skill to automatically generate documentation from requirements file.

**Prerequisites:**
- Must have `docs/doc-requirements.md` from `/furiosa:prepare-docs`

**This skill will automatically:**

1. **Load requirements file** - Read `docs/doc-requirements.md` with complete specification
2. **Analyze all sources** - Process core sources + related files (tests, types, examples)
3. **Generate documentation** - Create markdown with accuracy tracking per statement
4. **Apply citation format** - Every statement includes `([Source](URL)) [accuracy%]`
5. **Add rationale** - Blockquote explanations for statements with accuracy < 70%
6. **Include metadata** - Generated date, threshold, sources analyzed, changelog
7. **Save output file** - Write to location specified in requirements

**Output format:**
- Every statement has inline citation and accuracy score
- Low-confidence statements include rationale explaining confidence breakdown
- Analysis gaps documented with recommendations
- Rich GitHub formatting (Mermaid diagrams, tables, alerts)

**Next step:**
After PR creation, run `/furiosa:update-docs <pr-number>` to integrate feedback from PR comments.

**Workflow:** prepare-docs → write-docs → update-docs (from PR comments)
