# TUTORIAL.md — Reproduce & use this project

How to work with `_run/0_lcb` (Pt–P interstitial-alloy LCB AGOX search).

## Prerequisites

- conda env **`agox_v2`** (`/home/think/miniconda3/envs/agox_v2/bin/python`) — AGOX,
  ASE, GPAW, numpy, scipy, matplotlib. Base `python3` has **none** of these.
- For HPC pjsub runs: `gpaw_env` (activated inside batch scripts).

## Step 1 — Understand the layout

Read `README.md` (human) and `README.AI.md` (agent spec), and `AGENTS.md` for the
operating rules. The project currently holds:

- `2_analysist/17_PPt/` — the incorporated Pt–P run/analysis tree.
- `1_runs/` — empty; future self-contained runs go here.

## Step 2 — Syntax-check the tracked source

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
cd /home/think/Desktop/research/_run/0_lcb
$PY -m py_compile 2_analysist/run_analysis_indices.py
$PY -m py_compile 2_analysist/17_PPt/2_plus3cell/main.py
$PY -m py_compile 2_analysist/17_PPt/scripts/*.py
```

> If the LSP/Pyright flags AGOX/ASE imports as unresolved, ignore it — judge by the
> **env python's** `py_compile`, not the base-python LSP.

## Step 3 — Run analysis (once the runner is retargeted)

**Important:** `2_analysist/run_analysis_indices.py` is currently an **Fe/MgO-scoped
copy** from `a_lcbnovel`. It does **NOT** match the Pt–P `17_PPt` layout. Do not run
it on `17_PPt` until it has been retargeted (see README.AI.md §5 / §2b).

After retargeting, the intended CLI is the standard 3-stage analysis runner:

```bash
$PY 2_analysist/run_analysis_indices.py \
    --dataset <dir-with-seed_*/1_db/db_*.db> \
    --outdir <out> \
    [--e-max <eV/atom>] [--normalize-density] [--start-iter <N>]
```

Outputs: `progression_*.png`, `conf_space.png`, `binding_probability_vs_temperature.png`.

## Step 3b — JSON data emission + replot from JSON (analysis_indices)

`2_analysist/run_analysis_indices.py` (v2.3.0) writes each stage's plotting data to a
JSON file AND draws the PNG. A separate `--from-json` invocation reads the JSON and
re-draws the PNGs without re-loading the databases.

- Normal run WITH json: add `--json-dir <DIR>` (defaults to `<outdir>/analysis_json`).
  Three files are written (one per graph): `stage1_progression.json`,
  `stage2_landscape.json`, `stage3_probability.json`.
- Replot from JSON only (no DB access): pass `--from-json <DIR> --outdir <OUT>`.

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
cd /home/think/Desktop/research/_run/0_lcb/2_analysist

# full run that ALSO emits the 3 stage JSONs (under <out>/analysis_json)
$PY run_analysis_indices.py --dataset 11_bTa/8_fxg_1b \
    --outdir 11_bTa/8_fxg_1b/analysis_indices --e-max 1.0

# replot all 3 PNGs purely from the saved JSON (no dataset DBs needed)
$PY run_analysis_indices.py \
    --from-json 11_bTa/8_fxg_1b/analysis_indices/analysis_json \
    --outdir /tmp/replot_out
```

> `--from-json` verifiably reproduces the PNGs **byte-identically** (cmp SAME).

## Step 3c — XRD plots: JSON emission + replot (xrd_simulate_crystallinity.py)

The XRD stage runs in the **pymat_xrd** env and writes `xrd_plots.json` when `--json` is
passed, then replots both XRD PNGs from it with `--from-json`.

```bash
PY_X=/home/think/miniconda3/envs/pymat_xrd/bin/python
cd /home/think/Desktop/research/_run/0_lcb/2_analysist

# full XRD run that ALSO emits xrd_plots.json (per-window 2theta grid + intensity + CI)
$PY_X scripts/xrd_simulate_crystallinity.py \
    --manifest 11_bTa/8_fxg_1b/xrd_out/manifest.json \
    --outdir 11_bTa/8_fxg_1b/xrd_out --json

# replot both XRD PNGs from the saved xrd_plots.json
$PY_X scripts/xrd_simulate_crystallinity.py \
    --from-json 11_bTa/8_fxg_1b/xrd_out --outdir /tmp/xrd_replot
```

### Reproduce the narrow-energy run (7_fxg_0b, 0–0.03 eV/atom)

Example that restricts the analysis to a fine energy window near the ground state
(the `11_bTa/7_fxg_0b` case). Stage 1 (`agox_v2`) bins with a fine `--bin-width`
so several windows fit inside a narrow `--e-max`; Stage 2 (`pymat_xrd`) averages
per window and plots CI with the x-axis limited to the same narrow range. Outputs
go to a separate dir (`xrd_out_003`) so the original 0–0.5 analysis is kept.

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
PY_X=/home/think/miniconda3/envs/pymat_xrd/bin/python
cd /home/think/Desktop/research/_run/0_lcb/2_analysist

# Stage 1 — bin 7_fxg_0b structures by rel-E/atom into [0,0.03] in 0.005 bins
# (6 windows). Use bin_width <= e_max so the range is subdivided.
$PY scripts/xrd_extract_structures.py --dataset 11_bTa/7_fxg_0b \
    --outdir 11_bTa/7_fxg_0b/xrd_out_003 \
    --e-max 0.03 --bin-width 0.005

# Stage 2 — simulate + average XRD per window, plot CI with x to 0.03, y to 1
$PY_X scripts/xrd_simulate_crystallinity.py \
    --manifest 11_bTa/7_fxg_0b/xrd_out_003/manifest.json \
    --outdir 11_bTa/7_fxg_0b/xrd_out_003 --json \
    --ci-x-data-max 0.03 --ci-x-max 0.03 --ci-y-max 1.0
```

Produces `xrd_averaged_by_window.png`, `crystallinity_vs_energy.png`,
`crystallinity.csv`, and `xrd_plots.json` under `11_bTa/7_fxg_0b/xrd_out_003/`.
Pitfall: with `bin_width` finer than the label precision (e.g. 0.005 eV/atom) the
window labels must carry enough decimals — the extraction script (v1.1.0+) derives
this from `bin_width`; do not round the window names to 2 decimals.

### Reproduce the ground-state XRD comparison (bTa / bW / PPt per family)

Compares the global ground state (rel-E = 0) of each concentration leaf in an
interstitial family, as one XRD pattern per concentration plus CI vs interstitial
content. Stage 1 (`agox_v2`) extracts each leaf's rel-E=0 structure to a CIF;
Stage 2 (`pymat_xrd`) simulates its powder XRD (true intensity) and draws the two
comparison figures. The scripts are element-agnostic (auto-detect host/interstitial),
so the same command reproduces any family:

- `11_bTa` (Ta–B; leaves `7_fxg_0b …10_fxg_5b`) → legend `Ta₅₄Bₓ`
- `16_bW` (W–B; leaves `1_w0b,2_w1b,3_w3b,4_p_w10b`) → legend `W₅₄Bₓ`
- `17_PPt` (Pt–P; families `1_plus0cell`,`2_plus3cell`,`0_plus5cell`) → legend `Pt₁₀₈Pₓ`

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
PY_X=/home/think/miniconda3/envs/pymat_xrd/bin/python
cd /home/think/Desktop/research/_run/0_lcb/2_analysist

# --- 11_bTa (Ta-B) ---
$PY scripts/xrd_groundstate_extract.py --family 11_bTa --outdir 11_bTa/xrd_gs_compare
$PY_X scripts/xrd_groundstate_compare.py \
    --manifest 11_bTa/xrd_gs_compare/manifest.json \
    --outdir 11_bTa/xrd_gs_compare --json

# --- 16_bW (W-B) ---
$PY scripts/xrd_groundstate_extract.py --family 16_bW --outdir 16_bW/xrd_gs_compare
$PY_X scripts/xrd_groundstate_compare.py \
    --manifest 16_bW/xrd_gs_compare/manifest.json \
    --outdir 16_bW/xrd_gs_compare --json

# --- 17_PPt, family 1_plus0cell ---
$PY scripts/xrd_groundstate_extract.py --family 17_PPt/1_plus0cell \
    --outdir 17_PPt/1_plus0cell/xrd_gs_compare
$PY_X scripts/xrd_groundstate_compare.py \
    --manifest 17_PPt/1_plus0cell/xrd_gs_compare/manifest.json \
    --outdir 17_PPt/1_plus0cell/xrd_gs_compare --json
# ...repeat for 17_PPt/2_plus3cell and 17_PPt/0_plus5cell.
# 0_plus5cell excludes the 4x4 cell (0_PPt_4x4_20P); pass the leaf subset:
#   $PY scripts/xrd_groundstate_extract.py --family 17_PPt/0_plus5cell \
#       --leaves 3_3x3_0P 4_3x3_10p 1_3x3_20P 2_3x3_30P \
#       --outdir 17_PPt/0_plus5cell/xrd_gs_compare
```

Produces `xrd_averaged_by_window.png` (overlaid ground-state XRD patterns) and
`crystallinity_vs_energy.png` (peak-fraction & integrated CI vs interstitial
concentration) under each `<family>/xrd_gs_compare/`, plus `xrd_plots.json`.
The overlay legend uses the subscripted formula + concentration, e.g.
`Ta₅₄B₁ (1.8% B)` / `Pt₁₀₈P₂₇ (20.0% P)`.
Pitfall: intensity is physically meaningful only because both scripts simulate with
pymatgen `scaled=False` (since v1.4.0 / v1.1.0) — do not reintroduce the default
`scaled=True`, which pins every pattern's strongest peak to 100 and hides the real
amplitude drop with increasing interstitial content.

## Step 3d — Run a loop over multiple leaf dataset dirs

The runner analyses ONE leaf per invocation. To analyse every leaf of a family (or every
leaf dir holding `seed_*/1_db/db_*.db`), loop over them:

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
cd /home/think/Desktop/research/_run/0_lcb/2_analysist
FAM=11_bTa
for leaf in "$FAM"/[0-9]*/; do          # e.g. 7_fxg_0b, 8_fxg_1b, ...
    leaf=${leaf%/}
    [ -d "$leaf"/seed_0/1_db ] || continue
    echo "=== analysing $leaf ==="
    $PY run_analysis_indices.py --dataset "$leaf" --outdir "$leaf/analysis_indices" \
        --e-max 1.0
done
```

Add `--json-dir "$leaf/analysis_indices/analysis_json"` (or rely on the default) to emit
the per-leaf JSON alongside the PNGs.

### Run ALL amorphous interstitial systems at once (11_bTa + 16_bW + 17_PPt +5/+0/+3)

The loop above is per-family. To run every leaf of every **amorphous
heavy-metal + dopant** system in the project in one pass — `11_bTa` (Ta–B),
`16_bW` (W–B), and the `17_PPt` (Pt–P) `0_plus5cell` / `1_plus0cell` /
`2_plus3cell` supercell families — but **excluding** the 4×4 cell
(`0_PPt_4x4_20P`), `15_bPt`, `3_plus10cell`, any `trash/`, and the Fe/MgO
interface trees, enumerate the family roots and glob the leaves inside. Each
leaf run writes its **3 stage PNGs** (`progression_seed_split_0.png`,
`conf_space.png`, `binding_probability_vs_temperature.png`) AND its **3 stage
JSONs** into its own `analysis_indices/` (Stage-2 `conf_space.png` + Stage-3
`binding_probability_vs_temperature.png` are the two you asked about; the
progression plot rides along). Use `--e-max 0.5` so every energy axis shares one
window and graphs are directly comparable across systems:

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
cd /home/think/Desktop/research/_run/0_lcb/2_analysist

for root in 11_bTa 16_bW 17_PPt/0_plus5cell 17_PPt/1_plus0cell 17_PPt/2_plus3cell; do
    for leaf in "$root"/*/; do
        leaf=${leaf%/}
        case "$leaf" in *4x4_20P|*trash*) continue;; esac
        [ -d "$leaf"/seed_0/1_db ] || continue
        echo "=== analysing $leaf ==="
        $PY run_analysis_indices.py --dataset "$leaf" \
            --outdir "$leaf/analysis_indices" \
            --json-dir "$leaf/analysis_indices" --e-max 0.5
    done
done
```

Each leaf pass ends `DONE. Outputs under ...` + `JSON data under .../analysis_indices`.
This is the "run all" step — it **extracts** the JSONs as it goes (stage JSONs
land per-leaf under that leaf's `analysis_indices/`).

To then **replot all 3 graphs from the extracted JSONs** (no DB access — pure
figure reproduction), loop the same leaves over `--from-json`:

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
cd /home/think/Desktop/research/_run/0_lcb/2_analysist

for root in 11_bTa 16_bW 17_PPt/0_plus5cell 17_PPt/1_plus0cell 17_PPt/2_plus3cell; do
    for leaf in "$root"/*/; do
        leaf=${leaf%/}
        case "$leaf" in *4x4_20P|*trash*) continue;; esac
        [ -f "$leaf/analysis_indices/stage1_progression.json" ] || continue
        echo "=== replot $leaf ==="
        $PY run_analysis_indices.py \
            --from-json "$leaf/analysis_indices" \
            --outdir "$leaf/analysis_indices"
    done
done
```

Each replot pass ends `Re-plotted all 3 graphs from JSON <leaf>/analysis_indices`.
All 21 target leaves (5×11_bTa, 4×16_bW, 12×17_PPt across +5/+0/+3 minus the
4×4) already hold their 3 stage JSONs today, so this replot-all loop is
immediately runnable (verified on one leaf, 2026-09-08: reproduces
`conf_space.png`, `binding_probability_vs_temperature.png`, and the progression
plot from JSON with no DB re-load).

## Step 3e — Extract JSON data from existing outputs

**Note:** the plotted-data JSONs (`stage1/2/3_*.json`, `xrd_plots.json`) only exist for
outputs produced WITH `--json`. Historical PNGs that predate the `--json` flag have **no**
JSON yet — regenerate them by re-running that leaf with `--json` (Steps 3b/3c) first, then
extract. The only json that exists today for older xrd_out dirs is the Stage-1
`manifest.json` (an input) and the CI table `crystallinity.csv`.

```bash
cd /home/think/Desktop/research/_run/0_lcb/2_analysist

# (1) collect the 3 stage JSONs from every existing analysis_indices/analysis_json dir
find . -path '*/analysis_indices/analysis_json/stage*_*.json' -type f | tee /tmp/stage_json_list.txt
# copy them into one staging dir (optional):
mkdir -p /tmp/all_analysis_json && cp --parents $(cat /tmp/stage_json_list.txt) /tmp/all_analysis_json/

# (2) collect the xrd_out plotted-data json (xrd_plots.json, produced with --json)
find . -path '*/xrd_out/xrd_plots.json' -type f | tee /tmp/xrd_json_list.txt
# plus the Stage-1 input json + CI table that exist today:
find . -path '*/xrd_out/manifest.json' -type f
find . -path '*/xrd_out/crystallinity.csv' -type f
```

## Step 3f — Plot the JSON data

Re-draw PNGs purely from collected JSON with the two `--from-json` modes (no DB / no CIF
needed):

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
PY_X=/home/think/miniconda3/envs/pymat_xrd/bin/python
cd /home/think/Desktop/research/_run/0_lcb/2_analysist

# analysis_indices graphs from one leaf's JSON
$PY run_analysis_indices.py --from-json <leaf>/analysis_indices/analysis_json \
    --outdir /tmp/ai_plot

# XRD graphs from one leaf's xrd_out json
$PY_X scripts/xrd_simulate_crystallinity.py --from-json <leaf>/xrd_out \
    --outdir /tmp/xrd_plot
```

### Self-describing JSON (`description` block) + regenerate all JSONs

Since v2.9.0 (`run_analysis_indices.py`) / v1.4.3 & v2.1.2 (the XRD scripts), every
emitted JSON embeds a top-level **`description`** map — schema, kind, dataset /
family, method (incl. pymatgen Cu-Kα, `scaled=False` true-intensity, 2θ in
degrees), units, and a per-field legend — so a downstream AI agent can interpret
the file **without this working tree**. The plot payload is unchanged under its
original keys (`data` for the stage JSONs, the pattern/CI arrays for XRD), so
`--from-json` replot is unaffected; `description` is purely additive. **Note:**
JSONs written *before* this change do NOT have the block — regenerate them to add
it.

Regenerate all analysis stage JSONs (with `description`) for every leaf of the
amorphous interstitial systems (`11_bTa`, `16_bW`, `17_PPt` +5/+0/+3, excluding
the 4×4, `15_bPt`, `3_plus10cell`, `trash/`, Fe/MgO trees; `--e-max 0.5`):

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
cd /home/think/Desktop/research/_run/0_lcb/2_analysist

for root in 11_bTa 16_bW 17_PPt/0_plus5cell 17_PPt/1_plus0cell 17_PPt/2_plus3cell; do
    for leaf in "$root"/*/; do
        leaf=${leaf%/}
        case "$leaf" in *4x4_20P|*trash*) continue;; esac
        [ -d "$leaf"/seed_0/1_db ] || continue
        echo "=== analysing $leaf ==="
        $PY run_analysis_indices.py --dataset "$leaf" \
            --outdir "$leaf/analysis_indices" \
            --json-dir "$leaf/analysis_indices" --e-max 0.5
    done
done
```

Regenerate the XRD JSONs (with `description`): per-leaf energy-window plots from
each existing Stage-1 manifest, and the family ground-state comparison JSONs:

```bash
PY_X=/home/think/miniconda3/envs/pymat_xrd/bin/python
cd /home/think/Desktop/research/_run/0_lcb/2_analysist

# per-leaf xrd_out energy-window plots (needs the manifest + windowed CIFs)
for m in $(find 11_bTa 16_bW 17_PPt -path '*/xrd_out*/manifest.json' \
               2>/dev/null | grep -v trash); do
    echo "=== xrd sim $m ==="
    $PY_X scripts/xrd_simulate_crystallinity.py --manifest "$m" \
        --outdir "$(dirname "$m")" --json
done

# family ground-state comparison plots (5 xrd_gs_compare dirs)
for gs in 11_bTa/xrd_gs_compare 16_bW/xrd_gs_compare \
          17_PPt/0_plus5cell/xrd_gs_compare \
          17_PPt/1_plus0cell/xrd_gs_compare \
          17_PPt/2_plus3cell/xrd_gs_compare; do
    [ -f "$gs/manifest.json" ] || continue
    echo "=== xrd gs $gs ==="
    $PY_X scripts/xrd_groundstate_compare.py --manifest "$gs/manifest.json" \
        --outdir "$gs" --json
done
```

Verify the block exists after regeneration:

```bash
# any regenerated file should print a description map
python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(json.dumps(d.get('description','MISSING'),indent=1)[:400])" \
    2_analysist/11_bTa/8_fxg_1b/analysis_indices/stage2_landscape.json
```

Output PNGs/JSONs are regenerable and gitignored, so these loops are cosmetic and
safe to run.

## Step 4 — (Future) HPC heavy runs

Heavy runs go in self-contained `1_runs/<NN>_<descriptor>/` dirs (job `j_*.sh` +
`main*.py` + `scripts/`). Batch scripts use `gpaw_env` and PJM:

```bash
# edit the seed / concentration in the script, then:
pjsub j_*.sh            # NEVER pjsub -x
```

## Pitfalls

- **Runner mismatch:** don't run the Fe/MgO-scoped `run_analysis_indices.py` on
  Pt–P data.
- **Duplicated scripts:** many `scripts/*.py` copies exist across `17_PPt` run dirs.
  Edit the **canonical** `17_PPt/scripts/` + family `main.py`, not per-run snapshots.
- **Energy units/windows:** Fe/MgO vs Pt–P energy scales differ; keep assumptions
  per-system.
- **Trailing-space dirs:** never create run dir names with trailing spaces.
- **Git scope:** always stage explicit pathspecs for `0_lcb` (it lives inside the
  parent `research` repo); never `git add -A`.

## Verification checklist

- [ ] `py_compile` passes under `agox_v2` for the tracked source
- [ ] Docs (README/README.AI/TUTORIAL/VERSIONS/AGENTS/PROMPTS/LOG) consistent
- [ ] `17_PPt/` incorporated without reorganization
- [ ] No regenerable outputs (db/xsf/png/log) staged into git
- [ ] Changes committed with explicit pathspec for `0_lcb`
