# AGENTS.md — 2_febmgo (presentation project)

This file governs how an AI agent (or any contributor) works inside this
**presentation** project. Read it first before editing, adding, or removing
anything here. It is distinct from the research-project workflow: this is a deck,
not a run — no code, no runs, no version manifest. The deliverable is a structured,
figure-driven presentation.

## What this project is

`2_febmgo` is a presentation on FeB/MgO structure research, organized as four
sequential sections. The presentation is authored as markdown text files that embed
figure images. It is **not** a computational run project.

## Directory structure

```
2_febmgo/
├── README.md
├── AGENTS.md            # this file
├── a_introduction/      # context, motivation, prior work
├── b_method/            # methods & computational setup
├── c_result/            # results
└── d_conclusion/        # conclusions, outlook, open questions
```

Each section directory **must contain exactly**:

- `CONTENT.md`  — the section's slide / narrative text. What is said and shown.
- `DISCUSSION.md` — analysis and interpretation of the section's figures.
- `pngs/`       — the figure images for that section.

Both `CONTENT.md` and `DISCUSSION.md` reference the figures in the section's `pngs/`
inline via markdown image links:

```markdown
![fig1 — short caption](pngs/fig1.png)
```

## Operating rules

1. **Clarify before every step.** Confirm task, approach, and outputs with the
   owner before writing content or running anything. Do not assume. Batch
   independent clarify questions into one call.
2. **Ground everything in the repo.** Read existing CONTENT.md / DISCUSSION.md
   files and the README before editing. Never invent figures or filenames that
   don't exist in `pngs/`.
3. **Every figure reference must resolve.** A markdown image link in CONTENT.md or
   DISCUSSION.md must point at a file that actually exists in that section's `pngs/`.
   When the figure does not exist yet, use a placeholder caption and note it rather
   than fabricating a path.
4. **CONTENT vs DISCUSSION separation.** CONTENT.md is the spoken/visual narrative;
   DISCUSSION.md is the analysis. Keep the two roles distinct — do not bury
   interpretation inside CONTENT.md, and do not repeat the narrative in
   DISCUSSION.md.
5. **Keep sections self-contained.** A section's figures live only in its own
   `pngs/`. Do not reference another section's png path from a sibling section; if a
   figure belongs to multiple sections, duplicate it locally or note the cross-ref.
6. **Do not add runs/code here.** This is a presentation. Analysis scripts and heavy
   computation belong in the research `_run/` / `_analysist/` projects, not in this
   deck. Figures are produced there and copied (or referenced) into the sections.
7. **Append, don't rewrite (LOG-less note).** This project keeps no LOG.md by
   design (owner chose README + AGENTS.md only). Keep prior text edits traceable via
   git history; do not silently delete a section's content without the owner's
   approval.
8. **Commit after every change.** Make a git commit for each meaningful change.
   Confirm with the owner first when the change is a milestone (e.g. a full section
   drafted) or has side effects.
9. **Verify before claiming done.** Check that all figure references resolve and the
   markdown renders before reporting a section complete.

## Naming / content conventions

- Sections are order-encoded by prefix: `a_` → `b_` → `c_` → `d_`. Never reorder by
  renaming content; keep the prefixes stable.
- Figures: meaningful, lowercase, dash-separated filenames in `pngs/` (e.g.
  `radial-distribution.png`, `method-flowchart.png`).
- Captions on every embedded figure; the caption doubles as the alt-text.

## Non-goals / boundaries

- No `VERSIONS.md`, `TUTORIAL.md`, or `LOG.md` at the root unless the owner asks.
- No code, batch scripts, or computational outputs inside this tree.
- No fabrication: never invent data, results, or figure content in CONTENT.md or
  DISCUSSION.md. Content must be grounded in actual research outputs.
