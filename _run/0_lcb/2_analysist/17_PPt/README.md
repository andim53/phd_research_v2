# README — 17_PPt analysis results (Pt host, P interstitial)

This directory holds the analysed results for the **Pt–P** system: phosphorus
interstitials in a platinum (fcc) host, from the GPR+LCB AGOX search. This is the
project's original focus system.

## Result leaves

Each leaf below is a **dataset dir** that directly contains `seed_*/1_db/db_*.db`
databases. They are organised by **supercell family** (`0_plus5cell`,
`1_plus0cell`, `2_plus3cell`, `3_plus10cell`) and **P concentration**
(`0P/10P/20P/30P`, plus a `4×4` 20 % run):

| Leaf | Seeds |
|---|---|
| `0_plus5cell/0_PPt_4x4_20P` | 1 |
| `0_plus5cell/1_3x3_20P`     | 5 |
| `0_plus5cell/2_3x3_30P`     | 5 |
| `0_plus5cell/3_3x3_0P`      | 10 |
| `0_plus5cell/4_3x3_10p`     | 2 |
| `1_plus0cell/0_0P`          | 11 |
| `1_plus0cell/1_10P`         | 5 |
| `1_plus0cell/2_20P`         | 5 |
| `1_plus0cell/3_30P`         | 6 |
| `2_plus3cell/0_0P`          | 9 |
| `2_plus3cell/1_10P`         | 5 |
| `2_plus3cell/2_20P`         | 5 |
| `2_plus3cell/3_30P`         | 4 |
| `3_plus10cell/0_0P`         | 4 |

Run the analysis **per leaf** with `run_analysis_indices.py`. Point `--dataset`
at one leaf and `--outdir` at its analysis output.

## How to run the analysis

From `/home/think/Desktop/research/_run/0_lcb/_analysist`, using the `agox_v2`
conda env:

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
$PY run_analysis_indices.py \
    --dataset 17_PPt/2_plus3cell/2_20P \
    --outdir 17_PPt/2_plus3cell/2_20P/analysis_indices
```

Repeat for each leaf. Examples for the other families:

```bash
$PY run_analysis_indices.py --dataset 17_PPt/0_plus5cell/1_3x3_20P --outdir 17_PPt/0_plus5cell/1_3x3_20P/analysis_indices
$PY run_analysis_indices.py --dataset 17_PPt/1_plus0cell/0_0P      --outdir 17_PPt/1_plus0cell/0_0P/analysis_indices
$PY run_analysis_indices.py --dataset 17_PPt/3_plus10cell/0_0P     --outdir 17_PPt/3_plus10cell/0_0P/analysis_indices
```

### Optional flags

- `--e-max <eV/atom>` — cap the Stage 2/3 energy axis. Pt–P energy-per-atom range
  differs from other systems; set it to a sensible value for this system (e.g.
  `--e-max 0.5`) if the default `1.5` window clips your data.
- `--normalize-density` — normalize the Stage 2 state-density panel to [0,1].
- `--start-iter <N>` — keep only structures with AGOX iteration `>= N` (default 10).

### Outputs (per leaf, under `<outdir>`)

- `progression_plots/progression_seed_split_0.png` — per-seed best-so-far
- `conf_space.png` — PCA landscape + state density
- `binding_probability_vs_temperature.png` — Boltzmann P(T)

## Notes

- Analysis outputs (`*.png`, `*.xsf`) are regenerable and gitignored.
- The runner is system-agnostic: it reads the atom count from each structure, so
  no per-system code change is needed to analyse Pt–P.
- The canonical analysis/build scripts for this tree live in `17_PPt/scripts/`.
