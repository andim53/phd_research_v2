# README — 15_bPt analysis results (Pt host, B interstitial)

This directory holds the analysed results for the **Pt–B** system: boron
interstitials in a platinum (fcc) host, from the GPR+LCB AGOX search.

## Result leaves

Each leaf below is a **dataset dir** that directly contains `seed_*/1_db/db_*.db`
databases:

| Leaf | Description | Seeds |
|---|---|---|
| `1_pt0b`   | Pt, 0 % B   | 8 |
| `2_pt1b`   | Pt, 1 % B   | 4 |
| `3_pt3b`   | Pt, 3 % B   | 4 |
| `4_p_pt10b`| Pt, 10 % B  | 1 |

Run the analysis **per leaf** with `run_analysis_indices.py`. Point `--dataset`
at one leaf and `--outdir` at its analysis output.

## How to run the analysis

From `/home/think/Desktop/research/_run/0_lcb/_analysist`, using the `agox_v2`
conda env:

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
$PY run_analysis_indices.py \
    --dataset 15_bPt/1_pt0b \
    --outdir 15_bPt/1_pt0b/analysis_indices
```

Repeat for each leaf, changing `--dataset` and `--outdir` accordingly:

```bash
$PY run_analysis_indices.py --dataset 15_bPt/2_pt1b    --outdir 15_bPt/2_pt1b/analysis_indices
$PY run_analysis_indices.py --dataset 15_bPt/3_pt3b    --outdir 15_bPt/3_pt3b/analysis_indices
$PY run_analysis_indices.py --dataset 15_bPt/4_p_pt10b --outdir 15_bPt/4_p_pt10b/analysis_indices
```

### Optional flags

- `--e-max <eV/atom>` — cap the Stage 2/3 energy axis. Pt–B energy-per-atom range
  differs from other systems; set it to a sensible value for this system (e.g.
  `--e-max 0.5`) if the default `1.5` window clips your data.
- `--normalize-density` — normalize the Stage 2 state-density panel to [0,1].
- `--start-iter <N>` — keep only structures with AGOX iteration `>= N` (default 10).

### Outputs (per leaf, under `<outdir>`)

- `progression_plots/progression_seed_split_0.png` — per-seed best-so-far
- `conf_space.png` — PCA landscape + state density
- `binding_probability_vs_temperature.png` — Boltzmann P(T)

## Notes

- Analysis outputs (`*.png`, `*.xsf`) are regenerable and gitignored; only this
  README (and the canonical runner) is tracked.
- The runner is system-agnostic: it reads the atom count from each structure, so
  no per-system code change is needed to analyse Pt–B.
