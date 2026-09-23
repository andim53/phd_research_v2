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

## VESTA generation (canonical writer)
Any VESTA `.vesta` structure file emitted for this project MUST go through
**`codes/vesta_writer.py`** — the single canonical writer (custom colors
Fe #4C9F38 / Mg #FF7F0E / O #D62728, space-filling `MODEL 1`, fractional coords,
`O1`/`Mg1`/`Fe1` labels, optional opt-in Fe height-darkening). Do not
hand-roll a `.vesta`. Example: `write_vesta(atoms, path, "title", darken_fe=True)`.

## Build
```bash
cd papers/paper1 && ~/.local/bin/tectonic main.tex          # main manuscript
cd papers/paper1/supplementary && ~/.local/bin/tectonic article.tex   # SI
```

## Data-consistency note
The manuscript states "13 independent runs, 1,180 configurations" (seeds 3–15, `stop_16` excluded), matching the on-disk `data/femgo/` ensemble. Peak positions updated to the regenerated values (0.079 / 0.259 eV/atom). Finite-size data lives in `data/femgo_3x3` and `data/femgo_4x4`.
