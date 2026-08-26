# Processing a PROMPTS.md entry (the project prompt log)

`PROMPTS.md` logs every future-work prompt the owner drops in. Per `AGENTS.md` §3b
the agent must process each entry: assign a flag code, split original/fixed grammar,
and fold fixes into one shared `## Grammar notes`. This is the concrete recipe that
emerged from multiple sessions (flags `20260826_2333`, `_2354`, `20260827_0024`,
`_0041`).

## When to run this

- User says "process the PROMPTS.md" (or similar).
- You find a `# FLAG:` stub with **empty code** followed by raw prompt text — that is
  an unprocessed entry.
- After a code request, the same text may have already been logged; check for an
  existing `# FLAG: <YYYYMMDD_HHMM>` heading before re-adding.

## Recipe

1. **Get the flag code.** `date "+%Y%m%d_%H%M"` (local time). This is `YYYYMMDD_HHMM`.
2. **Newest prompts sit ABOVE older ones.** Insert the new processed entry at the top
   (after the scaffold header block), above all existing flags.
3. **Preserve the original verbatim** under `## Original (before grammar fix)` — do
   NOT clean the raw text; keep line-breaks/typos as-is so the fix is visible.
4. **Write `## Fixed grammar (after)`** — the corrected, idiomatic prompt.
5. **Fold every fix into the single shared `## Grammar notes` section** (concept-based,
   not per-prompt). Reuse an existing concept if the mistake matches; add a NEW concept
   only if genuinely new.
6. **Remove the now-redundant empty-flag stub** (the raw `# FLAG:\n<text>` that was
   the marker). Leave the processed entry.
7. **Append a LOG.md entry** (append-only) and **commit** PROMPTS.md + LOG.md.

## Grammar-notes concept taxonomy (built up across sessions)

These are the generalized concepts currently in use — reuse them rather than inventing
parallel labels:

1. **Formatting that breaks machine-readable content** — paths/identifiers split
   mid-token by line wraps (e.g. `/home/thin k/...`, `It' s`). Keep paths/filenames
   on one line, intact, in backticks.
2. **Incomplete clauses** — missing verb/object/noun (e.g. "under different energy
   range" → "energy ranges").
3. **Non-idiomatic phrasing** — unnatural preposition/filler (e.g. "use MAE" →
   "using MAE"; "add an additional Analysist" → "analysis").
4. **Redundant / misplaced comma** — comma splitting a verb from its object (e.g.
   "analysis, showing" → "analysis showing").
5. **Misspelling / dangling punctuation** — a misspelled word ("ratteling" →
   "rattling") or a trailing comma with no following verb.
6. **Terminology / clarity** — a loosely-used term pinned to its precise definition
   (e.g. "Fe z axist" → "Fe z-axis"; reorder a definition so the lead term names the
   quantity).

## Example (fixed grammar)

Raw: `Add an additional Analysist. I want to check the accuracy+uncertainty across
different delta Fe_z (distance between the highest Fe z axist height minus the lowest
Fe z axist height, i.e., the Fe island height).`

Fixed: `Add an additional analysis. I want to check the accuracy + uncertainty across
different delta Fe_z (the Fe island height: the distance between the highest Fe
z-axis height and the lowest Fe z-axis height).`

## Pitfalls

- **Don't skip the empty-flag detection.** New prompts arrive as a bare
  `# FLAG:` + text near the top. If you don't process it, it stays unflaged and
  unlogged.
- **Never re-word the "Original" block** — verbatim is the point (the fixed block is
  where the correction lives).
- **One shared Grammar notes section**, not one per prompt. Fold in, don't duplicate.
- These prompt entries are **future tasks** — processing the log is NOT building the
  code. Unless the user also asks to implement, just log/flag and stop.
