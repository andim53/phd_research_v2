# README — 16_bW analysis results (W host, B interstitial)

This directory holds the analysed results for the **W–B** system: boron
interstitials in a tungsten host, from the GPR+LCB AGOX search.

## Result leaves

Each leaf below is a **dataset dir** that directly contains `seed_*/1_db/db_*.db`
databases:

| Leaf | Description | Seeds |
|---|---|---|
| `1_w0b`   | W, 0 % B   | 47 |
| `2_w1b`   | W, 1 % B   | 8 |
| `3_w3b`   | W, 3 % B   | 4 |
| `4_p_w10b`| W, 10 % B  | 4 |

Run the analysis **per leaf** with `run_analysis_indices.py`. Point `--dataset`
at one leaf and `--outdir` at its analysis output.

## How to run the analysis

From `/home/think/Desktop/research/_run/0_lcb/2_analysist`, using the `agox_v2`
conda env:

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
$PY run_analysis_indices.py \
    --dataset 16_bW/1_w0b \
    --outdir 16_bW/1_w0b/analysis_indices
```

Repeat for each leaf, changing `--dataset` and `--outdir` accordingly:

```bash
$PY run_analysis_indices.py --dataset 16_bW/2_w1b    --outdir 16_bW/2_w1b/analysis_indices
$PY run_analysis_indices.py --dataset 16_bW/3_w3b    --outdir 16_bW/3_w3b/analysis_indices
$PY run_analysis_indices.py --dataset 16_bW/4_p_w10b --outdir 16_bW/4_p_w10b/analysis_indices
```

### Optional flags

- `--e-max <eV/atom>` — cap the Stage 2/3 energy axis. W–B energy-per-atom range
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
  no per-system code change is needed to analyse W–B.
