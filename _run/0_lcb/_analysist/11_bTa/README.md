# README — 11_bTa analysis results (Ta host, B interstitial)

This directory holds the analysed results for the **Ta–B** system: boron
interstitials in a tantalum host, from the GPR+LCB AGOX search.

> Note: this tree was previously gitignored as "off-scope" in an earlier session
> (the project's primary focus was Pt–P / `17_PPt`). It is included here because it
> holds real, on-disk results and is now covered by the analysis runner. Only this
> README and the canonical runner are tracked in git; the run data/scripts remain
> excluded via the project `.gitignore` (`_analysist/11_bTa/`).

## Result leaves

Each leaf below is a **dataset dir** that directly contains `seed_*/1_db/db_*.db`
databases:

| Leaf | Description | Seeds |
|---|---|---|
| `7_fxg_0b`   | Ta, 0 % B     | 37 |
| `8_fxg_1b`   | Ta, 1 % B     | 9 |
| `9_fxg_3b`   | Ta, 3 % B     | 6 |
| `10_fxg_5b`  | Ta, 5 % B     | 6 |
| `11_p_Ta10b` | Ta, 10 % B    | 3 |

Run the analysis **per leaf** with `run_analysis_indices.py`. Point `--dataset`
at one leaf and `--outdir` at its analysis output.

## How to run the analysis

From `/home/think/Desktop/research/_run/0_lcb/_analysist`, using the `agox_v2`
conda env:

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
$PY run_analysis_indices.py \
    --dataset 11_bTa/7_fxg_0b \
    --outdir 11_bTa/7_fxg_0b/analysis_indices
```

Repeat for each leaf, changing `--dataset` and `--outdir` accordingly:

```bash
$PY run_analysis_indices.py --dataset 11_bTa/8_fxg_1b   --outdir 11_bTa/8_fxg_1b/analysis_indices
$PY run_analysis_indices.py --dataset 11_bTa/9_fxg_3b   --outdir 11_bTa/9_fxg_3b/analysis_indices
$PY run_analysis_indices.py --dataset 11_bTa/10_fxg_5b  --outdir 11_bTa/10_fxg_5b/analysis_indices
$PY run_analysis_indices.py --dataset 11_bTa/11_p_Ta10b --outdir 11_bTa/11_p_Ta10b/analysis_indices
```

### Optional flags

- `--e-max <eV/atom>` — cap the Stage 2/3 energy axis. Ta–B energy-per-atom range
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
  no per-system code change is needed to analyse Ta–B.
