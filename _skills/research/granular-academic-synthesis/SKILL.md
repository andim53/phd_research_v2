---
name: granular-academic-synthesis
description: Use when synthesizing academic sources into analytical prose with verbatim clippings, LaTeX citations, and BibTeX references.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [research, academic-synthesis, citations, bibtex, latex, analysis, writing]
    related_skills: [hermes-agent, arxiv]
---

# Granular Academic Synthesis

## Overview

This skill defines a rigorous, reproducible workflow for transforming a set of provided research papers or academic articles into a structured analytical response. The output walks through concepts, mechanisms, implications, and contrasts drawn strictly from the source material, pairing every analytical claim with an exact verbatim sentence clipping and a standardized LaTeX citation. A complete BibTeX reference section is generated for every cited work — both primary and any secondary sources cited inside the clippings.

The discipline here is granularity: each distinct point in the analytical body must be anchored to its supporting evidence from the sources, and every citation must resolve to a valid, matching BibTeX entry.

## When to Use

- The user provides one or more primary source papers and asks for analysis, synthesis, clarification, or discussion of a specific topic or prompt.
- The user wants citations converted into a standardized `\cite{nameYear}` format with full BibTeX.
- The user wants verbatim sentence clippings attached to each analytical claim.
- The analysis must cross-synthesize perspectives across multiple papers.

Don't use for:
- Summarizing papers without analytical synthesis.
- Creative writing, storytelling, or non-academic content.
- Topics requiring live web search or external knowledge beyond the provided papers.

## Prerequisites

Before beginning, confirm:

- [ ] All primary source papers are loaded and readable (PDF, HTML, or plain text).
- [ ] You can extract reference metadata (title, authors, year, journal/conference, volume, pages, DOI) for each primary paper.
- [ ] You can identify and extract reference metadata for any secondary sources cited inside the clippings (from the primary papers' bibliographies).

If a paper is not available in full, flag it and skip it rather than fabricating citations.

## Step-by-Step Workflow

### Step 1 — Catalog All Primary Sources

For each provided primary paper:

1. Record the full title.
2. Capture the original reference style used by the paper (e.g., APA author-year, IEEE numerical `[1]`, numbered, Chicago author-date).
3. Assign a primary LaTeX citation key using the format `nameYear` (e.g., `Smith2024`, `ZhangAndLee2025`).
4. Extract and record the complete reference metadata needed for a valid BibTeX `@article`, `@inproceedings`, `@book`, or `@techreport` entry.

> Example catalog entry:
>
> | Title | Original Style | LaTeX Key |
> |---|---|---|
> | "Attention Is All You Need" | Numerical `[1]` | Vaswani2017 |

### Step 2 — Identify and Convert Secondary Citations in Clippings

As you extract verbatim clippings during Step 4, scan each clipping for internal citations. These can appear in multiple formats:

- **Numerical:** `[14]`, `[1,12,13]`, `[3--5]`
- **Parenthetical author-year:** `(Davis, 2021)`, `(Miller et al., 2020)`
- **Narrative:** `as demonstrated by Miller [14]`, `(Smith, 2019)`

**Critical sub-step — Build the Citation Map FIRST:**

Before writing any clippings, create a mapping table from the primary paper's bibliography:

| Original Ref | Authors | Year | LaTeX Key |
|---|---|---|---|
| `[1]` | Doye & Wales | 1997 | `Doye1997` |
| `[12]` | Li & Scheraga | 1987 | `Li1987` |
| `[13]` | Wales & Scheraga | 1999 | `Wales1999` |
| `[24]` | Wales | 2013 | `Wales2013` |
| ... | ... | ... | ... |

**Then, for each verbatim clipping:**

1. Scan the entire clipping text for ALL citation patterns (numerical, parenthetical, narrative).
2. For each citation found:
   a. Look it up in your citation map.
   b. Replace the raw citation (e.g., `[1,12,13]`) with the corresponding `\cite{Key1,Key2,Key3}` tag.
   c. Extract the secondary source's metadata and assign a `nameYear` key.
3. **After replacement, verify every `\cite{}` tag in the clipping resolves to a BibTeX entry.**
4. Do NOT leave any raw numerical, parenthetical, or narrative citations in the clipping text.

**Failure mode to avoid:** Writing a clipping verbatim with `[14]` or `(Davis, 2021)` intact — these MUST all be converted to `\cite{dest}` format.

### Step 3 — Assign Citation Keys

Use these conventions:

- **Single author:** `AuthorLastNameYear` (e.g., `Brown2023`)
- **Two authors:** `Author1AndAuthor2Year` (e.g., `SmithAndJones2022`)
- **Three or more authors:** `FirstAuthorEtAlYear` (e.g., `LeeEtAl2024`)
- **Disambiguation:** If two works share the same key, append a lowercase letter (`Smith2023a`, `Smith2023b`).

### Step 4 — Write the Analytical Body with Granular Clippings

Structure the body using the funnel approach: broad theoretical context first, narrowing to specific mechanisms, outcomes, and nuances.

For each distinct analytical point, follow this structure:

```
> **[Full analytical sentence exploring the topic, mechanism, or comparison]**
>
> _Exact source clipping:_ "[Verbatim sentence from the specific paper]" \cite{SourceAuthorYear}

> **[Analytical sentence drawing from a second paper]**
>
> _Exact source clipping:_ "[Verbatim sentence from the second paper]" \cite{SecondAuthorYear}
```

Guidelines for each analytical sentence:

- Write in complete, thinking-like prose.
- Address the specific prompt, topic, or clarification requested.
- Eliminate conversational fluff, AI meta-talk, and superficial transitions.
- When a synthesis point draws from multiple papers sequentially, append a separate clipping block for each supporting paper.

### Step 5 — Construct the References Section

1. Create a `## References (BibTeX)` header.
2. Inside a fenced ` ```bibtex ` code block, emit BibTeX entries for:
   - Every primary paper (keyed as `PrimaryAuthorYear`).
   - Every secondary paper cited inside any clipping (keyed as `SecondaryAuthorYear`).
3. Verify every `\\cite{...}` tag used in the body and clippings has a corresponding BibTeX entry.
4. Verify every BibTeX entry is syntactically valid.

### Step 5b — Write Output to Obsidian Vault

After assembling the full output (analytical body + References/BibTeX block):

1. Resolve the Obsidian vault directory: `/home/think/MEGA/Obsidian-Notes/wiki/wiki-research`.
2. Create the output as a new markdown file in the `raw/syntheses/` subdirectory:
   `raw/syntheses/<topic_or_prompt_slug>_synthesis.md`.
   - Use a slugified version of the topic/prompt (lowercase, spaces replaced with hyphens, punctuation stripped).
3. Write the complete content (body + References section) into that file using the markdown format defined in this skill's Formatting Rules.
4. Return the absolute file path to the user so they can open it directly in Obsidian.

### Step 6 — Final Verification

Before returning the response, run this checklist:

- [ ] Every analytical claim is paired with at least one verbatim source clipping.
- [ ] Every clipping with an internal secondary citation has that citation converted to `\cite{SecondaryAuthorYear}`.
- [ ] Every `\cite{...}` tag in the body and clippings has a matching BibTeX entry.
- [ ] All primary papers have BibTeX entries with correct `nameYear` keys.
- [ ] All secondary papers cited inside clippings have BibTeX entries.
- [ ] The references section uses a fenced ` ```bibtex ` code block.
- [ ] No analytical sentence was left unanchored to a source clipping.

## Formatting Rules

- Use a blockquote (`>`) for each analytical sentence.
- Use an italicized `_Exact source clipping:_` label for each verbatim excerpt.
- Wrap clippings in double quotation marks `"..."`.
- Place the `\cite{Key}` tag immediately after the closing quotation mark of each clipping.
- Use the header `## References (BibTeX)` for the references section.
- Place all BibTeX entries inside a single ` ```bibtex ` code block.

## Example Cases

### Case 1 — Primary-only citation

> **The transformer architecture eliminates recurrence in favor of self-attention, enabling greater parallelization during training.**
>
> _Exact source clipping:_ "The dominant sequence transduction models are based on the use of recurrence or attention. The best recent results in machine translation were achieved by incorporating recurrence as well, but the recurrent models are expensive to train." \cite{Vaswani2017}

### Case 2 — Multi-paper synthesis with secondary citation

> **While transformers removed recurrence, earlier recurrent models had already identified the computational bottleneck of sequential processing.**
>
> _Exact source clipping:_ "The best recent results in machine translation were achieved by incorporating recurrence as well, but the recurrent models are expensive to train." \cite{Vaswani2017}

> **Gradient-based attention was explored as a lighter alternative to full recurrence in earlier work.**
>
> _Exact source clipping:_ "As demonstrated by Miller [14], gradient-based attention mechanisms can approximate sequential dependencies with reduced computational cost." \cite{Vaswani2017}
>
> _Secondary source clipping:_ (metadata resolved from Miller [14] in the primary bibliography) "Gradient attention provides linear-time approximation of sequential processing." \cite{Miller2016}

### Case 3 — Cross-paper comparison

> **Convolutional approaches and attention-based approaches differ fundamentally in how they capture long-range dependencies.**
>
> _Exact source clipping:_ "Convolutional sequence to sequence networks differ from recurrent models by relying on kernel operations rather than iterative state updates." \cite{Gehring2017}

> **Self-attention provides a global receptive field from a single layer, whereas convolutions require multiple stacked layers.**
>
> _Exact source clipping:_ "Multi-head attention allows every position to attend to all positions, providing a global context in a single layer." \cite{Vaswani2017}

## Common Pitfalls

1. **Missing clippings:** Writing analytical sentences without attaching supporting verbatim clippings. Every claim must be anchored.

2. **Fabricated citations:** Inventing BibTeX entries or quoting papers that were not provided. If a source is unavailable, skip it rather than hallucinate.

3. **Unresolved secondary citations:** Forgetting to convert an internal citation like `[14]` into `\cite{Miller2016}` and failing to include the secondary's BibTeX entry. **This includes leaving raw numerical refs (`[1,12,13]`), parenthetical author-years (`(Davis, 2021)`), or narrative citations intact inside verbatim clippings.**

4. **Mismatched keys:** The `nameYear` in a `\cite{}` tag does not match the `authorYear` key in any BibTeX entry.

5. **Shallow synthesis:** Writing high-level summaries without descending to specific mechanisms, contrasts, or nuances within the funnel structure.

6. **Conversational fluff:** Inserting phrases like "It is interesting that" or "We can see that" instead of direct analytical reasoning.

7. **Over-citing:** Attaching clippings that do not directly support the analytical sentence. The clipping must be the evidentiary basis for the claim.

8. **BibTeX formatting errors:** Missing braces, incorrect entry types, or swapped field names. Validate syntax.

## Verification Checklist

- [ ] All primary source papers are cataloged with titles, original styles, and LaTeX keys.
- [ ] Every analytical sentence in the body is followed by `_Exact source clipping:_` with a verbatim excerpt and `\\cite{Key}`.
- [ ] Secondary citations inside clippings are converted to `\\\\cite{SecondaryAuthorYear}`.
- [ ] Grep all clippings for leftover raw numerical refs `[0-9]`, parenthetical author-years `(Davis, 2021)`, or narrative citations — none should remain.
- [ ] Every `\\\\cite{...}` tag resolves to a BibTeX entry.
- [ ] The `## References (BibTeX)` header precedes a single ` ```bibtex ` block.
- [ ] The block contains entries for all primary and all cited secondary papers.
- [ ] All BibTeX keys match the `nameYear` convention established in Step 3.
- [ ] No analytical sentence is left without a source clipping.
- [ ] Output is written to `/home/think/MEGA/Obsidian-Notes/wiki/wiki-research/raw/syntheses/<slug>_synthesis.md`.
