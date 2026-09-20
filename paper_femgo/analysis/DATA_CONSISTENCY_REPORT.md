# Data-Consistency Report — paper_femgo

Audit of the manuscript's stated numbers and figure claims against the on-disk data in `data/` and the sibling `_analysist/1_result/` tree. **Updated 2026-09-20 (Session 2): the ensemble and peak mismatches are now RESOLVED in the manuscript.** Generated 2026-09-20.

## 1. Ensemble size and seed count — RESOLVED

| Quantity | Manuscript (now) | On-disk reality |
|----------|------------------|-----------------|
| Independent runs | **13** | **13** seeds: `data/femgo/seed_3 … seed_15` |
| Ensemble size | **1,180** DFT-evaluated configs | **1,180** under the `iteration ≥ 10` filter (1,297 raw) |

- The manuscript was rewritten from "14 runs / 1,207 configs" to "13 runs / 1,180 configs" (prose + all captions + Data Availability). `stop_16` (36 configs, iters 1–37) is truncated and excluded.
- The paper's "seed 0" maps to disk `seed_3` (the run script `data/femgo/main.py` loops `range(3, 105)`); the seed range is now written as "13 independent runs" without an explicit range.

## 2. State-density peak positions — RESOLVED

| Peak | Manuscript (now) | Regenerated (KDE) |
|------|-------------------|-------------------|
| Island | 0.079 eV/atom | 0.079 eV/atom |
| Flat | 0.259 eV/atom | 0.259 eV/atom |

- The manuscript was updated from 0.074/0.255 to the regenerated 0.079/0.259 eV/atom (prose + Fig_ConDen + Fig_Boltz captions + temperature text).

## 3. DOS data — LIMITED (only 2 seeds)

- `Fig_dos` is backed by only **2** DOS CSVs: `data/dos_femgo_flatngs/dos_seed_3.csv` (island) and `dos_seed_4.csv` (flat). No other DOS seeds exist.
- The CSVs contain per-atom `Fe*_dz2` columns (25 Fe atoms each) plus O-pz columns; the regenerated `Fig_dos` sums the Fe-dz2 columns. Consistent with the draft's "Fe-3d PDOS" claim but rests on a single island/flat pair.

## 4. Reverse deposition (SI Fig_mgo) — data present, one truncated seed

- `data/mgofe/seed_0 … seed_4` are complete (100 configs each); **`seed_5` is truncated** (26 configs, iterations 1–26) and excluded.
- Regenerated `Fig_mgo` uses seeds 0–4 → **472 configs** under the iter≥10 filter.

## 5. Finite-size supercells (SI Fig_sup) — RESOLVED (data copied in)

- The 3×3 and 4×4 Fe/MgO data is now **copied into `paper_femgo/data/`**:
  - `data/femgo_3x3/` (Fe9Mg9O9) — from `_analysist/1_result/18_kappa2_iter100_trajNoSave_repSeedDat101/`
  - `data/femgo_4x4/` (Fe16Mg16O16) — from `_analysist/1_result/20_kappa2_iter100_trajNoSave_repSeedDat0_4x4/`
- Regenerated `Fig_sup` Δz: 3×3 = **3.60 Å**, 4×4 = **5.51 Å** — consistent with the paper's "island height increases ~1 Å per area increment" (5×5 ≈ 5.85 Å).
- **Note:** `_analysist/1_result/42_amorph_seed_3x3` is a **BTa54** (boron-tantalum) system, NOT Fe/MgO — do not use it for Fig_sup.

## 6. Figure regeneration status

| Figure | Regenerated? | Source | Notes |
|--------|-------------|--------|-------|
| Fig_Prog (energy progression) | ✅ | `data/femgo/seed_3..15` | 13 seeds |
| Fig_ConDen (landscape + g(E)) | ✅ | `data/femgo` (1,180 configs) | peaks 0.079/0.259 |
| Fig_Boltz (Boltzmann) | ✅ | `data/femgo` | 300–10000 K |
| Fig_dos (Fe-3d PDOS) | ✅ | `dos_seed_3/4.csv` | 2 seeds only |
| Fig_convStateDens (convergence) | ✅ | `data/femgo` | single vs cumulative |
| Fig_mgo (reverse dep, SI) | ✅ | `data/mgofe/seed_0..4` | 472 configs |
| Fig_env (AGOX env, SI) | ✅ | `data/femgo/seed_3/.../heteroStruct.xsf` | top+side |
| Fig_sup (finite-size, SI) | ✅ | `data/femgo_3x3` + `femgo_4x4` | 3×3, 4×4 |
| Fig_flow (schematic) | ⛔ excluded | — | hand-drawn, reused from draft |

## 7. Emit→plot datasets (Session 2)

All analysis now follows a two-step emit→plot pattern. `codes/emit_datasets.py` writes:
- `analysis/dataset_femgo.csv` (1,180 configs), `dataset_mgofe.csv` (472), `dataset_femgo_3x3.csv` (268), `dataset_femgo_4x4.csv` (1,799) — columns: seed, iteration, energy_eV, rel_energy_eV_per_atom, delta_z_A, psi_1d.
- Per-figure JSONs: `Fig_Prog.json`, `Fig_ConDen.json`, `Fig_Boltz.json`, `Fig_dos.json`, `Fig_convStateDens.json`, `Fig_mgo.json`.

The data-driven draw scripts read from these emitted datasets; the structure figures (Fig_env, Fig_sup) read the databases directly.

## 8. Remaining recommendations (not applied)

1. **Consider adding DOS seeds** if Fig_dos's 2-seed basis is deemed too thin for a main-text claim.
2. **Document the finite-size data provenance** (copied from `_analysist/1_result`) in the SI methods if desired.
