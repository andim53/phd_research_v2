# TUTORIAL.md — paper_femgo

How to reproduce the paper build and figure regeneration.

## Prerequisites
- **Python env:** `agox_v2` (`/home/think/miniconda3/envs/agox_v2/bin/python`) — AGOX 3.10.2, ASE 3.25.0, scipy, matplotlib.
- **LaTeX:** tectonic 0.17.0 at `~/.local/bin/tectonic` (no system TeX).

## 1. Compile the main manuscript
```bash
cd papers/paper1
~/.local/bin/tectonic main.tex        # → main.pdf
```
`main.tex` `\input`s `sections/01_abstract … 06_ack_dataavail.tex` in order. Figures live in `figures/`.

## 2. Compile the Supplementary
```bash
cd papers/paper1/supplementary
~/.local/bin/tectonic article.tex     # → article.pdf
```
Uses `spieman.cls` + `spiejour.bst` + `report.bib`; figures in `figures/`.

## 3. Regenerate figures
All figure scripts live in `codes/` and run under the `agox_v2` env python. Each reads the AGOX databases in `data/` and writes PNGs to `analysis/figures/`.

```bash
cd codes
/home/think/miniconda3/envs/agox_v2/bin/python draw_energy_progression.py   # Fig_Prog
/home/think/miniconda3/envs/agox_v2/bin/python draw_landscape.py            # Fig_ConDen
/home/think/miniconda3/envs/agox_v2/bin/python draw_boltzmann.py           # Fig_Boltz
/home/think/miniconda3/envs/agox_v2/bin/python draw_dos.py                  # Fig_dos
/home/think/miniconda3/envs/agox_v2/bin/python draw_state_density_conv.py   # Fig_convStateDens
/home/think/miniconda3/envs/agox_v2/bin/python draw_si_env.py               # Fig_env (SI)
/home/think/miniconda3/envs/agox_v2/bin/python draw_si_supercell.py          # Fig_sup (SI)
/home/think/miniconda3/envs/agox_v2/bin/python draw_si_mgo.py                # Fig_mgo (SI)
```

## Figure conventions (match `_analysist`)
- **rcParams:** serif font 12, ticks-in on all sides, no grid, dpi 300, `figure.autolayout=True`.
- **Energy axis:** `$E_{i}-E_{glob}$ (eV/atom)`, per-atom, global min = 0.
- **Minimum-ensemble filter:** keep only AGOX `iteration >= 10` (Phase II onward).
- **ΔZ coloring:** `z(Fe_max) - z(Fe_min)` over Fe atoms; flat ≈ 0 Å, island ≈ 5 Å.
- **PCA:** AGOX `Fingerprint` descriptors → center → covariance → top eigenvector → `psi_1d`.

## Verification checklist
- [ ] `main.pdf` and `article.pdf` build with no undefined citations.
- [ ] Each `codes/*.py` runs under `agox_v2` and writes its PNG to `analysis/figures/`.
- [ ] Regenerated figures visually match the draft's PNGs (owner inspects).
- [ ] `__version__` bumped on every code edit; `VERSIONS.md` + `LOG.md` updated.

## Pitfalls
- **`restore_to_memory()`** must be called before `get_all_candidates()` on an AGOX db, else it returns `[]`.
- **Truncated runs:** `data/femgo/stop_16` (36 configs) and `data/mgofe/seed_5` (26 configs) are incomplete — exclude from pooled statistics.
- **Manuscript numbers are frozen:** the draft's "seeds 0–13, 1,207 configs" stays as-is; on-disk reality (seeds 3–15, 1,180) is flagged in the report, not edited into prose.
- **`eprint` fields with raw URLs** break LaTeX — wrap in `\url{}` (already done in `references.bib`).
