# _skills — Research skills snapshot

A snapshot of the Hermes skills used in this research (`_run/<NN>_<name>`
projects: Fe/MgO AGOX global optimisation, GPR / Novelty-LCB / nested sampling /
novel-filter, GPAW, and the AI-Agent project workflow).

Copied from the live skill store (`~/.hermes/skills/`) preserving the category
layout. This is a **snapshot**, not auto-synced — refresh by re-copying the skills
that already exist here (see the "Sync" section below).

## Snapshot info

- **Snapshot date:** 2026-08-27 (refreshed from the 2026-08-25 initial snapshot)
- **Source:** `/home/think/.hermes/skills/`
- **Count:** 22 skills (117 + 6 + 13 + 2 = 139 files), full dirs incl. `references/`,
  `templates/`, `scripts/`.
  - research: 18 skills, 117 files
  - mlops: 1 skill, 6 files
  - software-development: 1 skill, 13 files
  - devops: 2 skills, 2 files

## Sync

Only the skills that **already exist** here are synced from the live store (changed
`SKILL.md` overwritten + new `references/`/`scripts/`/`templates/` added). Brand-new
live skills are **not** added. `devops/api-rate-limiter` is a local custom skill (not
in the live store) and is kept as-is. `devops/sdlc-review` is a new addition copied
from the live store.

## Layout

```
_skills/
├── research/                      # full research category (18 skills)
│   ├── agox/                      #   AGOX global optimisation (writing/debugging)
│   ├── agox-custom-modules/       #   custom AGOX module/acquisitor
│   ├── agox-nested-sampling/      #   nested sampling on an AGOX GPR surrogate
│   ├── agox-novel-filter/         #   dedup AGOX DB structures
│   ├── agox-novelty-lcb/          #   Novelty-LCB searches
│   ├── agox-run-code/             #   AGOX global-optimization run code
│   ├── arxiv/                     #   arXiv search
│   ├── benchmark-results-discussion/  # analyze benchmark results -> DISCUSSION.md
│   ├── blocked-page-recovery/     #   recover blocked/paywalled pages
│   ├── blogwatcher/               #   blog/RSS monitoring
│   ├── competitor-news-monitor/   #   company material-news digests
│   ├── gpaw/                      #   GPAW DFT code
│   ├── granular-academic-synthesis/   #   synthesize sources into analyses
│   ├── grounded-citations/        #   cite/verify sources
│   ├── llm-wiki/                  #   Karpathy-style markdown KB
│   ├── polymarket/                #   Polymarket queries
│   ├── research-paper-writing/    #   academic writing
│   └── simulation-analysis/       #   AGOX simulation/database analysis
├── mlops/
│   └── agox-gpr-analysis/         #   AGOX .db + GPR model training
├── software-development/
│   └── ai-agent-project-workflow/ #   README/LOG/TUTORIAL/AGENTS + versioning
└── devops/
    ├── api-rate-limiter/          #   local custom: API quota 429 backoff retry
    └── sdlc-review/               #   Kanban handoffs / SDLC review routing
```

## Related

Older flat snapshots (`agox-skill/`, `gpaw-skill/`) were archived to
`../_skills_archive_flat_20260825/` when this categorized snapshot was created.
