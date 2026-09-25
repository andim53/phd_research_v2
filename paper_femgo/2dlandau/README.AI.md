# README.AI.md — `paper_femgo/2dlandau` (agent spec)

## 1. Project identity

- **Dir:** `/home/think/Desktop/research/paper_femgo/2dlandau/`
- **Purpose:** Inherent-structure **2D Wang–Landau sampling** of the Fe/MgO
  flat↔island transition, binned over **(E, ΔZ)** — the joint density of states
  g_IS(E, ΔZ) where E is the GPR-surrogate-relaxed energy and ΔZ the **film
  height** = `z(Fe_max) − z_substrate_top` (the island height above the fixed
  MgO surface). **No DFT anywhere.**
- **Physics:** 75-atom Fe₂₅Mg₂₅O₂₅ (25 Fe on a fixed 50-atom MgO substrate).
  Film height spans ≈2.08 (flat monolayer) to ≈5.73 Å (natural island, the
  global-min structure). Two motifs: **flat monolayer** (film height ≈ 2.08 Å,
  metastable) and **island** 3D cluster (≳3 Å, global minimum).
- **Sub-project of** `paper_femgo` (governed by its `AGENTS.md`; no separate
  AGENTS.md / TUTORIAL.md here). Sibling of `_run/d_landauPlus` (1D g(E)).
- **Environment (invariant):** `/home/think/miniconda3/envs/agox_v2/bin/python`
  (AGOX 3.10.2 + ASE 3.25.0). Base `python3` has no AGOX/ASE. Heavy runs are
  HPC (`gpaw_env` pjsub; switch to `agox_v2` if the stack is missing).

## 2. File layout

```
2dlandau/
├── main.py                    # CLI: load -> train GPR -> 2D WL -> reweight -> save
├── landau_2d/                 # package
│   ├── __init__.py
│   ├── generator.py           # DeltaZGenerator (Fe on adsorption sites, target dZ)
│   ├── wang_landau_2d.py      # WangLandau2DSampler (2D WL, jump move, dZ ceiling)
│   ├── gpr_training.py        # load_all_seeds, build_gpr, validate_gpr (reused)
│   ├── thermodynamics.py      # reweight_2d, E_min_curve
│   └── utils.py               # K_B, _logsumexp
├── smoke_test_2dlandau.py     # cheap local validation (fake 2-Fe double-well GPR)
├── real_gpr_check.py          # real-GPR wiring + M3 extrapolation spot-check
├── j_2dlandau.sh              # HPC pjsub launcher
├── README.AI.md / LOG.md
└── output/                    # results (regenerable, gitignored)
```

## 3. Entry points & commands

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
cd /home/think/Desktop/research/paper_femgo/2dlandau

# Compile-check
$PY -m py_compile main.py smoke_test_2dlandau.py real_gpr_check.py landau_2d/*.py

# Cheap smoke test (fake 2-Fe double-well GPR; ~10 s)
$PY smoke_test_2dlandau.py

# Real-GPR wiring + extrapolation check (trains GPR, ~2 min + tiny walk)
$PY real_gpr_check.py

# Production run (dz-min/max default to [contact gap, natural island height])
$PY main.py --dataset ../data/femgo \
    --n-e-bins 35 --e-min 0.0 --e-max 0.7 \
    --relax-steps 100 --reference-steps 5000 --mc-steps 100000 \
    --temperatures 100,200,300,500,1000 --output ./output --rng 42

# HPC
pjsub j_2dlandau.sh
```

### `main.py` CLI
| Flag | Default | Meaning |
|---|---|---|
| `--dataset` | `../data/femgo` | Dir with `seed_*/1_db/db_*.db` |
| `--n-e-bins` / `--e-min` / `--e-max` | `35` / `0.0` / `0.7` | E bins (eV/atom rel). `0.7` = margin over flat branch (~0.67). |
| `--e-reject` | `5×e_max` | Rel E above which a trial is rejected as GPR extrapolation. |
| `--n-dz-bins` | `12` | ΔZ (film height) bins. |
| `--dz-min` / `--dz-max` | auto | ΔZ film-height range (Å). Default: contact gap / natural-island height (measured from the global-min structure). |
| `--relax-steps` | `100` | GPR BFGS steps per trial (GO-run cap). |
| `--flat-island-spread` | `1.0` | Fe z-spread threshold (Å) for flat vs island labelling (label uses z-spread, not film height). |
| `--contact-gap` | `2.08` | Bottom-Fe adsorption height above MgO (Å). |
| `--flatness-criterion` | `0.80` | WL flatness (2D, over visited cells). |
| `--check-interval` | `5000` | Flatness check interval. |
| `--n-stages-standard` | `14` | Halvings before 1/t switch. |
| `--reference-steps` | `2000` | Torbrügge initial pass (accessible-cell map). |
| `--mc-steps` | `50000` | WL MC steps. |
| `--temperatures` | `100,200,300,500,1000` | Reweighting temperatures (K). |
| `--output` | `./output` | Output dir. |
| `--rng` | `42` | Seed. |

## 4. Algorithm (2D generalisation of d_landauPlus)

1. **Load + train GPR** (`load_all_seeds` + `build_gpr`, verbatim from
   `d_landauPlus`; Fingerprint/Repulsive, `use_ray=False`).
2. **Generator (jump move):** draw target ΔZ (film height) ~ U[ΔZ_min, ΔZ_max]
   (ΔZ_max = natural island height); place the 25 Fe at the substrate's
   **adsorption sites** (the reference structure's Fe in-plane positions — a
   5×5 MgO(001) hollow-site lattice) with z-heights realizing exactly ΔZ
   (bottom at `z_contact`, top at `z_substrate_top + ΔZ`, rest uniform between).
   **In-plane is NOT randomized** — random placement drives the GPR into
   catastrophic extrapolation (M3).
3. **Constrained relax:** BFGS on the GPR under `FixAtoms(Mg/O)` + a hard
   **z-ceiling BoxConstraint** on Fe at `z_substrate_top + ΔZ`. Because the
   range is capped at the natural island height, the ceiling always binds — the
   Fe want to be taller than any target below the natural island, so `max(z_Fe)`
   presses against the ceiling and ΔZ = target holds. `fmax=0.05, steps=100`.
4. **2D WL accept:** bin relaxed (E, ΔZ); accept `ln(r) < ln_g[cur] − ln_g[trial]`;
   `f → f/2` flatness then 1/t (Belardinelli–Pereyra). Flatness over *visited*
   cells only; a Torbrügge initial pass maps the accessible (E, ΔZ) region and
   never-visited cells are rejected.
5. **Reweight:** `w_i(T) = exp(−E_total_i/k_B T) / g_IS(E_i, ΔZ_i)` with
   `E_total = E_rel × N` (total energy). Yields ⟨ΔZ(T)⟩, std, and
   ΔF_flat_island(T) = −k_B T ln(Σ_flat w / Σ_island w).

**Caveats (load-bearing):** (a) g_IS is the *inherent-structure* (basin-minimum)
DOS — no basin entropy; (b) it is proposal-biased (generator reachability, not
true basin volume); (c) WL is non-Markovian by design (Fort et al. 2015) — correct,
not a bug; (d) the top film-height bin (≈5.73 Å) is extrapolation-dominated by design.

## 5. Inputs / Outputs

**Inputs:** `paper_femgo/data/femgo/seed_*/1_db/db_*.db` (13 DBs, 1297 structs;
`stop_16` excluded by the `seed_*` glob by design).

**Outputs** (under `--output`; all machine-readable CSV/JSON, PNGs derived):
`g_of_E_dZ.json` (2D ln_g, H, accessible mask, E_min curve, metadata),
`g_of_E_dZ.csv` (long form), `g_of_E_dZ.png` (heatmap),
`delta_z_distribution.csv` (T, ⟨ΔZ⟩, std, ΔF_flat_island),
`delta_z_distribution.png`, `ensemble.json` (reweightable accepted structures).

## 6. Error handling & edge cases

1. **No DBs matched** → `FileNotFoundError` (check `--dataset`).
2. **GPR extrapolation** → `e_reject = 5×e_max` guard rejects rel E above it;
   `|E|>1e4` or non-finite E also rejected (revisits current bin).
3. **Relax fails** (singular Hessian etc.) → returns the unrelaxed trial.
4. **Never-visited cell** → rejected (Torbrügge reference-histogram rule).
5. **M3 extrapolation** → verified physical on the real GPR (E −413.9 eV flat /
   −385.3 eV tall); keep `in_plane_jitter=0` unless re-validating.
6. **ΔZ top bin** → ≈5.73 Å (natural island) is extrapolation-dominated (accepted, flagged).

## 7. Provenance

- Data: `paper_femgo/data/femgo` (the GO/GOFEE run; `data/femgo/main.py` is the
  reference for substrate/composition/confinement constants).
- Algorithm: Wang & Landau 2001 (PRL 86, 2050); Belardinelli & Pereyra 2007
  (JCP 127, 184105, 1/t); Fort, Jourdain, Kuhn, Lelièvre & Stoltz 2015
  (Math. Comp. 84, 2297; non-Markov convergence); Torbrügge & Schnack 2007
  (arXiv:cond-mat/0612320; 2D g(E,M) + reference histogram).
- Spec: `$SPEC_PATH/202609221952-2dlandau-g-e-deltaz.md` (v5, approved).
