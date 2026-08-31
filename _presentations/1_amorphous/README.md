# Presentation: 1_amorphous

<!-- One-paragraph abstract of this presentation. What story does it tell? Fill after
     the content is drafted. -->

Short description of the presentation's scope (amorphous structure research — topic,
system, and the narrative arc across the four sections below).

## Audience / Purpose

- Who is this presentation for (group meeting, thesis defense, conference)?
- What is the single takeaway?

## Directory structure

```
1_amorphous/
├── README.md
├── AGENTS.md                # governing rules for agents working in this project
├── a_introduction/          # Section A — context, motivation, prior work
│   ├── CONTENT.md           #   slide/section narrative text
│   ├── DISCUSSION.md        #   analysis / interpretation of the section's figures
│   └── pngs/                #   figure images (added as they are produced)
├── b_method/                # Section B — methods & computational setup
│   ├── CONTENT.md
│   ├── DISCUSSION.md
│   └── pngs/
├── c_result/                # Section C — results
│   ├── CONTENT.md
│   ├── DISCUSSION.md
│   └── pngs/
└── d_conclusion/            # Section D — conclusions, outlook, open questions
    ├── CONTENT.md
    ├── DISCUSSION.md
    └── pngs/
```

## Section conventions

- Each section lives in a prefixed dir (`a_`, `b_`, `c_`, `d_`) so the deck order is
  implicit in the names.
- **CONTENT.md** — the section's slide/narrative text. Embed figures inline with
  markdown image links (see below). This is what would be read aloud / shown.
- **DISCUSSION.md** — analysis & interpretation of that section's figures: what each
  plot shows, caveats, and how it supports the argument.
- **pngs/** — the raw figure images. Figures are referenced from both CONTENT.md and
  DISCUSSION.md by filename.

## Embedding figures

Reference a figure in `a_introduction/pngs/fig1.png` from either file in that dir as:

```markdown
![fig1 — short caption](pngs/fig1.png)
```

Keep the caption descriptive; the caption is what renders when the image cannot.

## Key decisions & tradeoffs

| Decision | Choice | Rationale / tradeoff |
|----------|--------|----------------------|
| Section split | a_introduction / b_method / c_result / d_conclusion | Classic IMRD-style presentation arc |
| Figure placement | per-section `pngs/` dir | Keeps each section self-contained |
| Content vs Discussion | CONTENT=narrative, DISCUSSION=analysis | Separates what is said from what it means |

_Add rows as decisions are made._

## Build / render

How the final deck is assembled from these sections (e.g. markdown → slides via a
tool, or a script that concatenates CONTENT.md files). Fill in once a workflow exists.
