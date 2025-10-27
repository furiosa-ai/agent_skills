---
description: Prepare documentation requirements through interactive setup (Step 1 of 3-phase workflow)
---

# Prepare Documentation Requirements

Use the **prepare-docs** skill to set up automated documentation generation.

**This skill will interactively:**

1. **Collect source links** - Ask what sources to analyze (GitHub, web pages, local files, Google Drive, Notion)
2. **Select document type** - Choose from API Reference, System Overview, Tutorial, or Custom
3. **Define document structure** - Customize sections and templates
4. **Set accuracy threshold** - Determine minimum confidence level (e.g., 70%)
5. **Discover related sources** - Automatically find tests, types, examples
6. **Save requirements file** - Output complete specification to `docs/doc-requirements.md`

**Output:**
- `docs/doc-requirements.md` - Complete specification for automated generation

**Next step:**
After this completes, run `/furiosa:write-docs` to automatically generate the documentation from the requirements file.

**Workflow:** prepare-docs → write-docs → update-docs (from PR comments)
