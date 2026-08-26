# PROMPTS.md: keep exactly ONE shared `## Grammar notes` section (user correction)

The user explicitly corrected how `## Grammar notes` must be structured in
`PROMPTS.md`: "You don't create multiple `## Grammar notes` tags. That only needs to
be one flag. That one Grammar notes will contain a generalized grammar mistake
concept from all grammar flags." (Project `b_nestedsampling`, 2026-08-27.)

## The rule

- There is **exactly ONE** `## Grammar notes` section for the whole file.
- It holds the **generalized, deduplicated grammar-mistake concepts** drawn from ALL
  flagged prompts (concept-based, not per-prompt).
- Each flag entry carries **only** its `## Original (before grammar fix)` and
  `## Fixed grammar (after)` blocks — no per-flag Grammar notes.

## When to consolidate

An existing PROMPTS.md can drift to one Grammar-notes block per flag (e.g. from
earlier sessions that added a block under each entry). When you encounter that:

1. Merge all per-flag blocks into **one** shared `## Grammar notes` section placed
   near the top (after the intro).
2. **Deduplicate** the concepts — identical or near-identical concepts collapse into
   one numbered item; keep the examples that name their originating flag.
3. Reduce each flag entry to just its Original + Fixed grammar blocks.
4. Keep flags in descending order (newest at top).
5. Verify with `grep -c "^## Grammar notes" <file>` → must return `1`.

## Reference

Full processing recipe + the concept taxonomy (7 concepts) lives in
`ai-agent-project-workflow/references/prompts-md-processing.md`. Treat the
one-shared-section rule here as the hard constraint on top of that recipe.
