# paper_femgo

Scientific paper project: **Machine Learning-Based Partition Function Sampling: Application to Fe on MgO(001) Growth** (Andi Muhammad Nur Fitrah Syamsul, Kohji Nakamura — Mie University).

This project initializes the `scientific-paper-writing` workflow on a finished draft and regenerates all figures from the underlying AGOX/GPAW data.

## What's here
- `papers/paper1/` — main manuscript (RevTeX 4.2) split into `sections/`, plus `supplementary/` (SPIE-class SI). Both compile with tectonic.
- `codes/` — figure-regeneration scripts (PCA landscape, energy progression, Boltzmann, DOS, state-density convergence).
- `analysis/` — regenerated figures + result JSONs.
- `data/` — raw AGOX `.db` databases, GPAW logs, DOS CSVs (read-only reference).
- `tmp/draft_paper/` — the original finished-draft zips (provenance).

## Key decisions
| Decision | Choice |
|----------|--------|
| Manuscript layout | Full skill layout: `papers/paper1/` with per-section `.tex` |
| Draft handling | Ported verbatim; structure split only, prose unchanged |
| Figure code | `_analysist` style (rcParams, iter≥10 filter), all paper + SI figures |
| Numbers | Manuscript's stated numbers kept as-is; discrepancies flagged in report only |
| Fig_flow schematic | Excluded from regeneration (hand-drawn, reused from draft) |

## Build
```bash
cd papers/paper1 && ~/.local/bin/tectonic main.tex          # main manuscript
cd papers/paper1/supplementary && ~/.local/bin/tectonic article.tex   # SI
```

## Data-consistency note
The manuscript states "seeds 0–13, 1,207 configurations"; on-disk `data/femgo/` holds seeds 3–15 (1,180 under the iter≥10 filter). See the data-consistency report for details.
