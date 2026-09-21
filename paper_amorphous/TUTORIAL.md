# TUTORIAL.md — paper_amorphous

How to reproduce the paper build and figure regeneration.

## Prerequisites
- **Python env:** `agox_v2` (`/home/think/miniconda3/envs/agox_v2/bin/python`) — AGOX, ASE, scipy, matplotlib.
- **FLAPW/SHC env:** `flapw_2` conda env (HPC, pjsub).
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

## 3. Regenerate figures (emit → plot)
All figure scripts live in `codes/` and run under the `agox_v2` env python. **Two-step pattern:** first emit the datasets (CSV + per-figure JSON) you and the owner can inspect, then plot from them. *(Scripts to be written — see `paper_status.md`.)*

```bash
cd codes
# Step 1 — emit datasets (CSV + JSON) into analysis/
/home/think/miniconda3/envs/agox_v2/bin/python emit_datasets.py
# Step 2 — plot from the emitted datasets
/home/think/miniconda3/envs/agox_v2/bin/python draw_*.py
```

## Figure conventions (match `_analysist`)
- **rcParams:** serif font 12, ticks-in on all sides, no grid, dpi 300, `figure.autolayout=True`.
- **Energy axis:** `$E_{i}-E_{glob}$ (eV/atom)`, per-atom, global min = 0.
- **Minimum-ensemble filter:** keep only AGOX `iteration >= 10` (Phase II onward).
- **XRD crystallinity:** peak-fraction CI + integrated CI (see `data/17_PPt/DISCUSSION.md`).

## SHC workflow (in progress)
- Example: `tmp/SHC Calculation/HEA_SHC_Auto_Python_FLAPW/` — `main.py` (SCF → SOC → optics → xoptics), `job_genkai_mpi.sh` (conda `flapw_2`, pjsub).
- Input: a `.traj` file of structures. Which amorphous structures feed the SHC is **TBD**.

## Verification checklist
- [ ] `main.pdf` and `article.pdf` build with no undefined citations.
- [ ] Each `codes/*.py` runs under `agox_v2` and writes its PNG to `analysis/figures/`.
- [ ] `__version__` bumped on every code edit; `VERSIONS.md` + `LOG.md` updated.

## Pitfalls
- **`restore_to_memory()`** must be called before `get_all_candidates()` on an AGOX db, else it returns `[]`.
- **`3_plus10cell` (+10%) is excluded** by scope — do not include it in pooled statistics.
- **`main.py` `SCALE_CELL=1.05` is stale** for the +0/+3 families — use the xsf cell dimensions (11.927 / 12.284 / 12.523 Å).
- **SHC section is a placeholder** — no SHC numbers/claims until the calculation is done.
