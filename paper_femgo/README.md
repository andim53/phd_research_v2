# paper_femgo

Scientific paper project: **Machine Learning-Based Partition Function Sampling: Application to Fe on MgO(001) Growth** (Andi Muhammad Nur Fitrah Syamsul, Kohji Nakamura — Mie University).

This project initializes the `scientific-paper-writing` workflow on a finished draft and regenerates all figures from the underlying AGOX/GPAW data.

---

## 1. Overview (human)

### What's here
- `papers/paper1/` — main manuscript (RevTeX 4.2) split into `sections/`, plus `supplementary/` (SPIE-class SI). Both compile with tectonic.
- `codes/` — figure-regeneration scripts (PCA landscape, energy progression, Boltzmann, DOS, state-density convergence).
- `analysis/` — regenerated figures + result JSONs.
- `data/` — raw AGOX `.db` databases, GPAW logs, DOS CSVs (read-only reference).
- `tmp/draft_paper/` — the original finished-draft zips (provenance).

### Key decisions
| Decision | Choice |
|----------|--------|
| Manuscript layout | Full skill layout: `papers/paper1/` with per-section `.tex` |
| Draft handling | Ported verbatim; structure split only, prose unchanged |
| Figure code | `_analysist` style (rcParams, iter≥10 filter), all paper + SI figures |
| Numbers | Manuscript corrected to current results (13 runs, 1,180 configs, 0.079/0.259) |
| Fig_flow schematic | Excluded from regeneration (hand-drawn, reused from draft) |

### VESTA generation (canonical writer)
Any VESTA `.vesta` structure file emitted for this project MUST go through
**`codes/vesta_writer.py`** — the single canonical writer (custom colors
Fe #4C9F38 / Mg #FF7F0E / O #D62728, space-filling `MODEL 1`, fractional coords,
`O1`/`Mg1`/`Fe1` labels, optional opt-in Fe height-darkening). Do not
hand-roll a `.vesta`. Example: `write_vesta(atoms, path, "title", darken_fe=True)`.

### Data-consistency note
The manuscript reports **13 independent runs, 1,180 configurations** (seeds 3–15, `stop_16` excluded), matching the on-disk `data/femgo/` ensemble. Peak positions are the regenerated values (0.079 / 0.259 eV/atom). Finite-size data lives in `data/femgo_3x3` and `data/femgo_4x4`. These current values are canonical; older draft figures (14 runs / 1,207 configs, 0.074/0.255) were superseded when the manuscript was corrected.

---

## 2. Agent spec

### Purpose
Initialize the `scientific-paper-writing` workflow on a finished Fe/MgO manuscript and regenerate all figures from raw AGOX/GPAW data. The manuscript's prose is frozen (ported verbatim); the agent's job is structure, figure regeneration, and data-consistency auditing.

### File layout
```
paper_femgo/
├── AGENTS.md            # governing rules (read first)
├── README.md            # this file — human overview + agent spec + tutorial
├── LOG.md               # append-only action log
├── VERSIONS.md          # per-file __version__ manifest
├── papers/
│   ├── paper1/            # original draft fork (figures from draft zips)
│   └── paper2/            # current-results fork — figures from analysis/figures/
│       ├── main.tex
│       ├── sections/      # 01_abstract … 06_ack_dataavail (.tex per section)
│       ├── figures/       # only Fig_flow.png (hand-drawn; other figs from analysis/)
│       ├── references.bib
│       ├── CLAIMS.md
│       ├── paper_status.md
│       └── supplementary/ # SI: article.tex (SPIE), report.bib, spieman.cls, spiejour.bst
├── codes/               # figure-regeneration scripts (each has __version__)
├── analysis/            # regenerated figures + result JSONs
├── data/                # raw results (read-only reference)
│   ├── femgo/           # Fe-on-MgO: seed_3..15 (1_db/db_*.db), stop_16 (truncated, excluded)
│   ├── femgo_3x3/       # finite-size 3x3 (Fe9Mg9O9) — copied from _analysist/1_result
│   ├── femgo_4x4/       # finite-size 4x4 (Fe16Mg16O16) — copied from _analysist/1_result
│   ├── mgofe/           # reverse deposition (SI Fig_mgo): seed_0..5
│   └── dos_femgo_flatngs/  # DOS CSVs (dos_seed_3.csv, dos_seed_4.csv) + xsf
└── tmp/draft_paper/     # original finished-draft zips (provenance)
```

### Entry points & commands
- **Compile main:** `cd papers/paper1 && ~/.local/bin/tectonic main.tex`
- **Compile SI:** `cd papers/paper1/supplementary && ~/.local/bin/tectonic article.tex`
- **Regenerate figures:** `cd codes && /home/think/miniconda3/envs/agox_v2/bin/python <script>.py` (see Tutorial below)
- **Env python:** `/home/think/miniconda3/envs/agox_v2/bin/python` (AGOX 3.10.2, ASE 3.25.0). Set `matplotlib.use('Agg')` before plotting.

### Data model (AGOX databases)
- Load: `Database(filename=db); db.restore_to_memory()` (REQUIRED before `get_all_candidates()`).
- Per-atom relative energy: `(E_i - gmin)/len(atoms)`, global min = 0, per system.
- **Minimum-ensemble filter:** keep only `iteration >= 10` (Phase II onward, GPR-relaxed). This is the paper's ensemble definition.
- ΔZ (film flatness) = `z(Fe_max) - z(Fe_min)` over Fe atoms.
- PCA: AGOX `Fingerprint` descriptors → center → covariance → top eigenvector → `psi_1d = Xc @ evecs[:,0]`.

### Expected inputs/outputs
- **Input:** `data/femgo/seed_*/1_db/db_*.db`, `data/mgofe/seed_*/1_db/db_*.db`, `data/dos_femgo_flatngs/dos_seed_*.csv`.
- **Output:** `analysis/figures/*.png` (Fig_Prog, Fig_ConDen, Fig_Boltz, Fig_dos, Fig_convStateDens, Fig_env, Fig_sup, Fig_mgo) + result JSONs.

### Error handling & edge cases
- `stop_16/` (36 configs, iters 1–37) and `mgofe/seed_5` (26 configs) are **truncated** — exclude from pooled statistics; flag in report.
- Only 2 DOS seeds exist (`dos_seed_3.csv`, `dos_seed_4.csv`) — Fig_dos is limited to these.
- **Current values are canonical:** the manuscript states seeds 3–15, 13 runs, 1,180 configs, peaks 0.079/0.259 eV/atom, matching on-disk data. The older draft numbers (seeds 0–13, 1,207 configs, 0.074/0.255) were corrected in the manuscript and are no longer authoritative.

### Provenance
Draft ported from `tmp/draft_paper/RevTeX 4.2 Manuscript.zip` + `Supplementary.zip` (extracted to `tmp/draft_paper/_extracted/`). Figure PNGs copied from the zips; regenerated versions live in `analysis/figures/`.

---

## 3. Tutorial (reproduction)

How to reproduce the paper build and figure regeneration.

### Prerequisites
- **Python env:** `agox_v2` (`/home/think/miniconda3/envs/agox_v2/bin/python`) — AGOX 3.10.2, ASE 3.25.0, scipy, matplotlib.
- **LaTeX:** tectonic 0.17.0 at `~/.local/bin/tectonic` (no system TeX).

### 1. Compile the main manuscript
```bash
cd papers/paper1
~/.local/bin/tectonic main.tex        # → main.pdf
```
`main.tex` `\input`s `sections/01_abstract … 06_ack_dataavail.tex` in order. Figures live in `figures/`.

### 2. Compile the Supplementary
```bash
cd papers/paper1/supplementary
~/.local/bin/tectonic article.tex     # → article.pdf
```
Uses `spieman.cls` + `spiejour.bst` + `report.bib`; figures in `figures/`.

### 3. Regenerate figures (emit → plot)
All figure scripts live in `codes/` and run under the `agox_v2` env python. **Two-step pattern:** first emit the datasets (CSV + per-figure JSON) you and the owner can inspect, then plot from them.

```bash
cd codes
# Step 1 — emit datasets (CSV + JSON) into analysis/
/home/think/miniconda3/envs/agox_v2/bin/python emit_datasets.py

# Step 2 — plot from the emitted datasets
/home/think/miniconda3/envs/agox_v2/bin/python draw_energy_progression.py   # Fig_Prog
/home/think/miniconda3/envs/agox_v2/bin/python draw_landscape.py            # Fig_ConDen
/home/think/miniconda3/envs/agox_v2/bin/python draw_boltzmann.py           # Fig_Boltz
/home/think/miniconda3/envs/agox_v2/bin/python draw_dos.py                  # Fig_dos
/home/think/miniconda3/envs/agox_v2/bin/python draw_state_density_conv.py   # Fig_convStateDens
/home/think/miniconda3/envs/agox_v2/bin/python draw_si_mgo.py                # Fig_mgo (SI)
/home/think/miniconda3/envs/agox_v2/bin/python draw_si_env.py               # Fig_env (SI, structure)
/home/think/miniconda3/envs/agox_v2/bin/python draw_si_supercell.py          # Fig_sup (SI, structure)
```

Emitted datasets: `analysis/dataset_femgo.csv`, `dataset_mgofe.csv`, `dataset_femgo_3x3.csv`, `dataset_femgo_4x4.csv` (columns: seed, iteration, energy_eV, rel_energy_eV_per_atom, delta_z_A, psi_1d) + per-figure JSONs (`Fig_Prog.json`, `Fig_ConDen.json`, `Fig_Boltz.json`, `Fig_dos.json`, `Fig_convStateDens.json`, `Fig_mgo.json`).

### Figure conventions (match `_analysist`)
- **rcParams:** serif font 12, ticks-in on all sides, no grid, dpi 300, `figure.autolayout=True`.
- **Energy axis:** `$E_{i}-E_{glob}$ (eV/atom)`, per-atom, global min = 0.
- **Minimum-ensemble filter:** keep only AGOX `iteration >= 10` (Phase II onward).
- **ΔZ coloring:** `z(Fe_max) - z(Fe_min)` over Fe atoms; flat ≈ 0 Å, island ≈ 5 Å.
- **PCA:** AGOX `Fingerprint` descriptors → center → covariance → top eigenvector → `psi_1d`.

### Verification checklist
- [ ] `main.pdf` and `article.pdf` build with no undefined citations.
- [ ] Each `codes/*.py` runs under `agox_v2` and writes its PNG to `analysis/figures/`.
- [ ] Regenerated figures visually match the draft's PNGs (owner inspects).
- [ ] `__version__` bumped on every code edit; `VERSIONS.md` + `LOG.md` updated.

### Pitfalls
- **`restore_to_memory()`** must be called before `get_all_candidates()` on an AGOX db, else it returns `[]`.
- **Truncated runs:** `data/femgo/stop_16` (36 configs) and `data/mgofe/seed_5` (26 configs) are incomplete — exclude from pooled statistics.
- **Manuscript numbers are current:** the draft's "seeds 0–13, 1,207 configs" was corrected to seeds 3–15, 13 runs, 1,180 configs, peaks 0.079/0.259 eV/atom, matching on-disk data.
- **`eprint` fields with raw URLs** break LaTeX — wrap in `\url{}` (already done in `references.bib`).
