# README for AI Agents — Project 0 (`0_lcb`)

Machine-readable spec for agents working on this project. Complements the
human-facing `README.md`. **Read `AGENTS.md` first** for the operating rules.

## 1. Project identity

- **Dir:** `/home/think/Desktop/research/_run/0_lcb/`
- **Purpose:** Lower Confidence Bound (LCB) AGOX search over **interstitial
  alloys** — a heavy-metal host (Pt, Ta, W) doped with an interstitial
  (B or P). Home to the pre-existing `17_PPt` analysis/run tree, now under the
  AI-Agent Project Workflow, plus the family analysis runner under `2_analysist/`.
  Also hosts two **Fe/MgO interface LCB runs** (`0_lcb_femgo`, `1_lcb_febmgo`)
  analysed with the same project-agnostic runner (see §2e).
- **Physics:** heavy-metal hosts (Pt fcc `a = 3.975534 Å`, Ta, W) with cells
  scaled +0/+3/+5/+10 %, supercells 3×3×3 (and variants), interstitials at
  0–30 %, `LowerConfidenceBoundAcquisitor`, GPR + Fingerprint,
  GPAW LCAO/dzp/PBE. **Fe/MgO interface runs**: Fe(001) overlayer on MgO(001),
  5×5 supercell `a ≈ 14.35 Å`, LCAO/dzp/PBE spin-polarized (see §2e).
- **Environment (invariant):** `/home/think/miniconda3/envs/agox_v2/bin/python`
  (AGOX + ASE + GPAW) for analysis/local work; `pymat_xrd`
  (`/home/think/miniconda3/envs/pymat_xrd/bin/python`, pymatgen, no ASE) for the
  XRD crystallinity stage; `gpaw_env` on HPC (activated in batch scripts). Base
  `python3` has **no** AGOX/ASE/GPAW/pymatgen.

## 2. File layout

```
0_lcb/
├── README.md            # human overview
├── README.AI.md         # this file (agent spec)
├── LOG.md               # curated, append-only action log
├── transcript.log       # raw tool-call / run-output transcript (gitignored, *.log)
├── TUTORIAL.md          # reproduce/usage guide with pitfalls + verification
├── VERSIONS.md          # source version manifest
├── AGENTS.md            # governing rules for AI agents
├── PROMPTS.md           # future-work prompt log (+ shared grammar notes)
├── .gitignore           # project-level ignores (regenerable outputs)
├── 2_analysist/          # analysed/intermediate results + family analysis code
│   ├── run_analysis_indices.py   # family analysis runner (v2.9.0, project-agnostic)
│   ├── scripts/                  # runner deps + XRD stage
│   │   ├── plot_structure_landscape.py   # Stage-2 landscape (v1.1.0)
│   │   ├── xrd_extract_structures.py     # XRD Stage 1 (v1.0.0, agox_v2)
│   │   └── xrd_simulate_crystallinity.py # XRD Stage 2 (v1.1.0, pymat_xrd)
│   ├── json_export/                # JSON (re)generation driver scripts
│   │   ├── extract_all_analysis_json.sh     # run all 25 analysis leaves with --json
│   │   ├── regenerate_analysis_json.sh      # per-leaf analysis regenerate + json
│   │   └── regenerate_xrd_json.sh           # per-leaf XRD json regenerate
│   ├── 11_bTa/                   # Ta–B family (5 leaves)
│   ├── 15_bPt/                   # Pt–B family (4 leaves)
│   ├── 16_bW/                    # W–B family (4 leaves)
│   ├── 17_PPt/                  # incorporated Pt–P run/analysis tree
│   ├── 0_lcb_femgo/            # Fe/MgO interface LCB run, no B (13 seeds) [§2e]
│   └── 1_lcb_febmgo/           # Fe/MgO + B hollow-adsorbate LCB run (7 seeds) [§2e]
└── 1_runs/               # (empty) future self-contained run dirs
```

> `2_analysist/11_bTa/` (a Ta–B system) is present on disk but **gitignored** — it
> is off-scope for the Pt–P project identity and excluded from commits (see
> `.gitignore`). `0_lcb_femgo/` and `1_lcb_febmgo/` are Fe/MgO interface runs —
> distinct physics from the Pt–P/Ta–W interstitial families, but **tracked code**
> (main.py, job `*.sh`, `scripts/`) and analysable by the same project-agnostic
> runner (they use the same `seed_*/1_db/db_*.db` layout). The family analysis
> output PNGs/JSONs are regenerable and gitignored; only the analysis **code**
> (`run_analysis_indices.py`, `scripts/`, `json_export/*.sh`) and tracked docs are
> committed.

### 2a. `2_analysist/17_PPt/` — incorporated analysis tree

- The bulk of this project's run content. It is a **pre-existing Pt–P run tree**
  that was placed here before the workflow scaffold, and is **kept as-is, not
  reorganized**.
- Organised by **supercell family** (`0_plus5cell`, `1_plus0cell`, `2_plus3cell`,
  `3_plus10cell`) and, within each, by **P concentration** (`0_0P`, `1_10P`,
  `2_20P`, `3_30P`, plus `0_PPt_4x4_20P`). Each leaf has `seed_*/1_db/db_*.db`
  databases (gitignored), `0_result/` (xsf/figs, gitignored), `scripts/`, and
  `generated_structures/` + `gpaw_logs/` (gitignored).
- **Many files are duplicated** script snapshots (`scripts/*.py` copied into each
  run dir) and PJM job scripts (`j_*.sh`). The project-level `.gitignore` keeps
  per-run generated outputs out of git; the canonical source lives in
  `17_PPt/scripts/` and each family's `main.py`.

### 2b. `run_analysis_indices.py` — family analysis runner (project-agnostic)

- **`__version__ = "2.9.0"`.** A **project-agnostic** analysis runner that globs
  `seed_*/1_db/db_*.db` and reads the atom count from each structure, so it runs
  on **any** interstitial-alloy family under `2_analysist/` — `11_bTa` (5 leaves),
  `15_bPt` (4), `16_bW` (4), `17_PPt` (12) = **25 leaves total**. It is NOT
  Fe/MgO-scoped and IS used on `17_PPt`.
- **Dependency:** imports `scripts/plot_structure_landscape.py` (self-contained;
  stdlib/numpy/scipy/matplotlib). Compile-gate under `agox_v2` (LSP/Pyright false
  positives on AGOX/ASE imports are expected — judge by `py_compile`).
- **3-stage pipeline** (CLI `--dataset --outdir [--e-max --normalize-density
  --start-iter --json-dir --from-json]`):
  1. **Stage 1** — per-seed best-so-far progression plot
     (`progression_plots/progression_seed_split_0.png`) + bullet/xsf exports of
     low-energy window minima + global ground state.
  2. **Stage 2** — PCA landscape + per-atom KDE state density
     (`conf_space.png`, via `plot_structure_landscape.py`).
  3. **Stage 3** — Boltzmann probability vs temperature
     (`binding_probability_vs_temperature.png`).
- **JSON data emission (v2.3.0):** each stage's plotted data is dumped to a JSON
  AND the PNG is drawn. Add `--json-dir <DIR>` (default `<outdir>/analysis_json`);
  writes `stage1_progression.json`, `stage2_landscape.json`,
 `stage3_probability.json`. Re-draw the PNGs from a saved JSON (no DB access)
 with `--from-json <DIR> --outdir <OUT>`. Per current owner convention the
 JSONs are saved **per-leaf, multiple files**, directly inside that leaf's own
 `analysis_indices/` dir (pass `--json-dir <leaf>/analysis_indices`); there is no
 central staging. `plot_structure_landscape.py` accepts `return_data=True` to
 expose Stage-2's computed arrays (energy grid, densities, peaks) for the JSON.
 - **Self-describing JSON (v2.9.0):** each stage JSON's top level embeds a
 `description` block (schema, kind, dataset path, num_atoms/formula, origin,
 energy units, and a per-field legend) so a downstream AI agent can interpret
 the file **without the working tree**. The plot payload is unchanged under
 `data`, so `--from-json` replot is unaffected; `description` is additive.

### 2c. XRD crystallinity scripts (two-env bridge)

- **`scripts/xrd_extract_structures.py`** (v1.0.0, `agox_v2`): reads DB structures,
  computes relative energy/atom `(E−E_glob)/n`, bins into energy windows, writes
  windowed CIFs + `manifest.json` (Stage 1).
- **`scripts/xrd_simulate_crystallinity.py`** (v1.4.3, **`pymat_xrd`**): simulates
  powder XRD per CIF (pymatgen `XRDCalculator`, Cu Kα), averages per window, and
  computes crystallinity indices (peak-fraction + integrated). Writes
  `xrd_averaged_by_window.png`, `crystallinity_vs_energy.png`,
  `crystallinity.csv`. With `--json` also writes `xrd_plots.json` (per-window
  2θ grid + intensity + CI rows); `--from-json <dir>` replots both PNGs from it.
  `--manifest`/`--dataset` are non-required so `--from-json` runs without CIF/DB.
- **`scripts/xrd_groundstate_compare.py`** (v2.1.2, **`pymat_xrd`**): simulates
  the single ground-state (rel-E=0) powder pattern per concentration leaf of a
  family and overlays them (one curve per dopant %), plus CI vs concentration.
  Writes `xrd_averaged_by_window.png`, `crystallinity_vs_energy.png`, and with
  `--json` an `xrd_plots.json` (`family` + `leaves`). A `--figsize 'W,H'` flag
  controls the overlay figure size (default `8,4.5`).
- **Self-describing JSON:** both XRD scripts embed a top-level `description`
  block (schema, kind, method = pymatgen Cu-Kα, scaled=False true-intensity,
  units incl. 2θ in degrees, and a per-field legend) in their `xrd_plots.json`,
  so a downstream AI agent can interpret the file without the working tree. The
  block is additive — the pattern/CI arrays under their original keys are
  unchanged, so `--from-json` replot is unaffected.
- Why two envs: `agox_v2` has ASE/AGOX but no pymatgen; `pymat_xrd` has pymatgen
  + XRD but no ASE. The bridge is CIF files on disk.

### 2d. `json_export/` — JSON (re)generation drivers

- `extract_all_analysis_json.sh` — runs the analysis with `--json` on **all 25**
  analysis leaves, each writing its 3 stage JSONs into its own `analysis_indices/`.
- `regenerate_analysis_json.sh` — 25 per-leaf commands (one per structure) to
  regenerate each analysis PNG + its 3 stage JSONs in place.
- `regenerate_xrd_json.sh` — 5 per-leaf commands to regenerate each `xrd_out` PNG
  + `xrd_plots.json`.

### 2e. Fe/MgO interface LCB run trees (`0_lcb_femgo`, `1_lcb_febmgo`)

Two **Fe(001)/MgO(001) interface** LCB AGOX runs. Distinct from the Pt–P/Ta–W
interstitial-alloy identity above (different physics), but they live under
`2_analysist/` and follow the **same `seed_*/1_db/db_*.db` layout**, so the
project-agnostic runner (`run_analysis_indices.py`) analyses them the same way —
point `--dataset` at one of these dirs. Seed dirs `seed_N/` each hold `0_result/`
(xsf/fig) + `1_db/db_N.db`; run data is regenerable/gitignored, code tracked.

- **`0_lcb_femgo/`** — Fe/MgO, **no B dopant**. Seeds **3–15** (13 DBs present;
  `main.py` loops seeds `3..104`, `N_iterations=100`). Each seed's heterostructure
  = 75 atoms: Fe(001) overlayer **Fe₂₅** (5×5, one ML) on an MgO(001) substrate
  (**Mg₂₅ O₂₅**). Supercell 5×5×1, `a ≈ 14.35 Å`, `c = 40 Å` vacuum.
- **`1_lcb_febmgo/`** — Fe/MgO **with B added into Fe-layer hollows** (script
  `add_adsorbate_to_hollows`, `symbol_add='B'`, `num_atoms_add=3`, `z=0`).
  Seeds **0–6** (7 DBs present; `main.py` loops `0..102`, 100 iters; seed_6 DB is
  empty). Each seed's heterostructure = **Fe₂₅ B₃** overlayer on Mg₂₅ O₂₅
  (78 atoms). Same 5×5 supercell.
- **Shared run params:** matched interface (`a_mgo=4.212 Å` → `/√2` matched to
  Fe `a_fe=2.870190 Å`, ~2.6% strain), Fe bcc(001), 1 ML Fe + 1 ML MgO,
  `dist_z_fe2o=0.5 Å` interface gap, confinement height ×4, generators
  `HeteroStructRandomize` + `RattleGenerator`, GPR + Fingerprint, LCB
  (`kappa=2`), GPAW LCAO/dzp/PBE, `kpts=(1,1,1)`, spin-polarized, `ncores=24`.
  Both also carry stray HPC artifacts on disk: `job_*.sh.*.out` run logs and
  `.d00052*` / `.d00052*_nodeinfo` pjsub remnants (untracked / gitignored),
  plus a `trash/` (old `main.py`, `db_0.db`) and — in `0_lcb_femgo` — a `stop_16/`
  dir (seed 16 aborted after ~37 iterations; `trash/` holds an earlier seed-0 run
  that reached ~50).
- **Scripts:** `0_lcb_femgo/scripts/` holds the run's build/generator/analysis
  helpers (e.g. `build_fe_stack.py`, `build_mgo_stack.py`, `hetero_struct_randomize.py`);
  `1_lcb_febmgo/scripts/` additionally has `remove_random_atoms_by_species.py`,
  `add_adsorbate_to_hollows.py` and a `running_scripts/` subdir with alternate
  mains (`main_amorph.py`, `main_boron.py`, `main_dos.py`). These are per-run
  snapshots local to each dir — treat `main.py` at each tree root as canonical
  for that tree.

## 3. Entry points & commands

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
PY_X=/home/think/miniconda3/envs/pymat_xrd/bin/python
cd /home/think/Desktop/research/_run/0_lcb

# Compile-check tracked source (syntax gate)
$PY -m py_compile 2_analysist/run_analysis_indices.py
$PY -m py_compile 2_analysist/scripts/plot_structure_landscape.py
$PY -m py_compile 2_analysist/17_PPt/2_plus3cell/main.py
$PY_X -m py_compile 2_analysist/scripts/xrd_simulate_crystallinity.py
```

> LSP/Pyright under base `python3` flags AGOX/ASE imports as unresolved even when
> code compiles under `agox_v2` — judge by the env python's `py_compile`, not the LSP.

### Analysis run (one leaf)
```bash
cd /home/think/Desktop/research/_run/0_lcb/2_analysist
# full analysis + emit 3 stage JSONs into that leaf's own analysis_indices/
$PY run_analysis_indices.py --dataset 11_bTa/8_fxg_1b \
    --outdir 11_bTa/8_fxg_1b/analysis_indices \
    --json-dir 11_bTa/8_fxg_1b/analysis_indices --e-max 0.5
# replot the 3 PNGs from saved JSON (no DB)
$PY run_analysis_indices.py --from-json 11_bTa/8_fxg_1b/analysis_indices \
    --outdir /tmp/ai_plot
```

### Analysis run (Fe/MgO interface tree — one of 0_lcb_femgo / 1_lcb_febmgo)
```bash
cd /home/think/Desktop/research/_run/0_lcb/2_analysist
# Fe/MgO no-B tree: 13 seeds
$PY run_analysis_indices.py --dataset 0_lcb_femgo \
    --outdir 0_lcb_femgo/analysis_indices \
    --json-dir 0_lcb_femgo/analysis_indices --e-max 0.5
# Fe/MgO + B tree: 7 seeds (note seed_6 DB is empty; runner must skip it)
$PY run_analysis_indices.py --dataset 1_lcb_febmgo \
    --outdir 1_lcb_febmgo/analysis_indices \
    --json-dir 1_lcb_febmgo/analysis_indices --e-max 0.5
```
> Each seed in these trees holds a **fixed-composition** heterostructure
> (substrate Mg₂₅O₂₅ constant; only Fe/B overlayer atoms move), so per-atom
> relative-energy windows are meaningful per seed. Because composition differs
> between the no-B and +B trees, keep the two trees separate (never mix their DBs
> into one analysis). An empty seed DB (`1_lcb_febmgo/seed_6`) must be skipped,
> not treated as a zero-row leaf.

### Analysis run (all 25 leaves — JSON extraction driver)
```bash
cd /home/think/Desktop/research/_run/0_lcb/2_analysist
bash json_export/extract_all_analysis_json.sh    # ~1 h, heavy
```

### XRD crystallinity run (one leaf)
```bash
cd /home/think/Desktop/research/_run/0_lcb/2_analysist
$PY scripts/xrd_extract_structures.py --dataset 11_bTa/8_fxg_1b \
    --outdir 11_bTa/8_fxg_1b/xrd_out --e-max 0.5     # agox_v2 (writes manifest.json + CIFs)
$PY_X scripts/xrd_simulate_crystallinity.py \
    --manifest 11_bTa/8_fxg_1b/xrd_out/manifest.json \
    --outdir 11_bTa/8_fxg_1b/xrd_out --json          # pymat_xrd
# replot XRD PNGs from xrd_plots.json
$PY_X scripts/xrd_simulate_crystallinity.py \
    --from-json 11_bTa/8_fxg_1b/xrd_out --outdir /tmp/xrd_plot
```

### HPC run (future / existing)
Batch scripts use `gpaw_env` and the `#PJM` scheduler. Launch with
`pjsub j_*.sh` (seed/concentration edited in the script; never `pjsub -x`).

## 4. Dependencies

- `agox_v2` conda env: AGOX 3.10.2, ASE, GPAW, numpy, scipy, matplotlib.
- `pymat_xrd` conda env: pymatgen (+XRD), numpy/scipy/matplotlib; used only for
  `xrd_simulate_crystallinity.py`.
- HPC `gpaw_env` for pjsub runs.

## 5. Known gaps / error handling & edge cases

- **Duplicated scripts:** many `scripts/*.py` copies exist across run dirs. Edit
  the **canonical** `17_PPt/scripts/` + `2_analysist/scripts/` and family
  `main.py`; per-run copies are snapshots.
- **Two envs for XRD:** run Stage 1 in `agox_v2` and Stage 2 in `pymat_xrd`; do
  not run `xrd_simulate_crystallinity.py` under `agox_v2` (no pymatgen) and do
  not run `xrd_extract_structures.py` / the analysis runner under `pymat_xrd`
  (no ASE/AGOX).
- **`--from-json` needs `--outdir`:** when replotting from JSON you must pass both
  `--from-json <dir>` and `--outdir <out>`; `--dataset`/`--manifest` are ignored.
- **Energy units/windows:** energy scales differ by system (Ta–B vs Pt–P vs
  Fe/MgO). Use a per-system `--e-max`; keep assumptions consistent across the
  progression / landscape / probability windows. The XRD `--e-max` filter also
  drops high-energy outliers (e.g. `10_fxg_5b` relE up to ~93 eV/atom). For the
  Fe/MgO trees, do not mix the no-B and +B DBs in one run (composition differs).
- **JSONs only after `--json`:** historical PNGs that predate the `--json` flags
  have **no** companion JSON until re-run with `--json`/the drivers.
- **`.xsf` side output is DB-only:** Stage-1 window-minima + ground-state `.xsf`
  are written during a live run (need the DB); a `--from-json` replot redraws the
  PNG but cannot regenerate the `.xsf` structures.

## 6. Provenance

- `17_PPt/` predates this scaffold (runs dated Jul–Aug 2026). It was incorporated
  verbatim into `_run/0_lcb/`.
- `run_analysis_indices.py` adapted from the `b_nestedsampling`/`a_lcbnovel`
  Fe/MgO runner and generalized to be **project-agnostic** (v2.1.0 → v2.2.0
  energy-window fix → v2.3.0 JSON emit/replot). It IS the intended runner for all
  interstitial families including `17_PPt`.
- `scripts/xrd_extract_structures.py`, `scripts/xrd_simulate_crystallinity.py`
  added 2026-09-02 (proposal → code).
- `json_export/` drivers added 2026-09-02.
- `2_analysist/0_lcb_femgo/` and `1_lcb_febmgo/` (Fe/MgO interface LCB runs, dated
  Sep 2026) placed under `2_analysist/` and documented in README.AI on 2026-09-06.
  They share the project-agnostic runner layout and are tracked for their code
  (main.py, job `*.sh`, `scripts/`); DB/xsf/out data stays gitignored.
- Scaffold (this doc set) created 2026-08-31 under the AI-Agent Project Workflow.
