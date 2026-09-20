# Data-Consistency Report — paper_femgo

Audit of the manuscript's stated numbers and figure claims against the on-disk data in `data/` and the sibling `_analysist/1_result/` tree. **The manuscript's numbers are kept as drafted; this report flags every mismatch.** Generated 2026-09-20.

## 1. Ensemble size and seed count — MISMATCH

| Quantity | Manuscript states | On-disk reality |
|----------|-------------------|-----------------|
| Independent runs | **14** (Seeds 0–13) | **13** seeds on disk: `data/femgo/seed_3 … seed_15` |
| Ensemble size | **1,207** DFT-evaluated configs | **1,180** under the paper's own `iteration ≥ 10` filter (1,297 raw) |

- The manuscript's "seed 0" likely maps to disk `seed_3` (the run script `data/femgo/main.py` loops `range(3, 105)`), so the paper renumbers seeds 3–15 as 0–13 — but that yields **13**, not 14, runs.
- `data/femgo/stop_16/` is a **truncated** run (36 configs, iterations 1–37) and is correctly excluded.
- **Impact:** the headline "1,207 configurations from 14 runs" is not reproducible from the data present. The regenerated `Fig_convStateDens` and `Fig_ConDen` use the 1,180-config ensemble.

## 2. State-density peak positions — MINOR MISMATCH

| Peak | Manuscript | Regenerated (KDE) |
|------|-----------|-------------------|
| Island | 0.074 eV/atom | **0.079** eV/atom |
| Flat | 0.255 eV/atom | **0.259** eV/atom |

- The regenerated `Fig_ConDen` finds peaks at 0.079 / 0.259 eV/atom. The ~0.005 eV/atom offset is a KDE-bandwidth (Scott's rule) difference. The paper's 0.074/0.255 values are close but not identical to a fresh KDE over the same ensemble.

## 3. DOS data — LIMITED (only 2 seeds)

- `Fig_dos` is backed by only **2** DOS CSVs: `data/dos_femgo_flatngs/dos_seed_3.csv` (island) and `dos_seed_4.csv` (flat). No other DOS seeds exist.
- The CSVs contain per-atom `Fe*_dz2` columns (25 Fe atoms each) plus O-pz columns; the regenerated `Fig_dos` sums the Fe-dz2 columns. This is consistent with the draft's "Fe-3d PDOS" claim but rests on a single island/flat pair.

## 4. Reverse deposition (SI Fig_mgo) — data present, one truncated seed

- `data/mgofe/seed_0 … seed_4` are complete (100 configs each); **`seed_5` is truncated** (26 configs, iterations 1–26) and excluded.
- Regenerated `Fig_mgo` uses seeds 0–4 → **472 configs** under the iter≥10 filter.

## 5. Finite-size supercells (SI Fig_sup) — data NOT in paper_femgo/data/

- The 3×3 and 4×4 Fe/MgO data is **not** in `paper_femgo/data/`. It lives in the sibling tree:
  - 3×3 (Fe9Mg9O9): `_analysist/1_result/18_kappa2_iter100_trajNoSave_repSeedDat101/`
  - 4×4 (Fe16Mg16O16): `_analysist/1_result/20_kappa2_iter100_trajNoSave_repSeedDat0_4x4/`
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
| Fig_sup (finite-size, SI) | ✅ | `_analysist/1_result/18_*` + `20_*` | 3×3, 4×4 |
| Fig_flow (schematic) | ⛔ excluded | — | hand-drawn, reused from draft |

## 7. Recommendations (not applied — manuscript numbers frozen per owner)

1. **Decide the ensemble number.** Either update the manuscript to "13 runs / 1,180 configs" (matching disk) or locate the missing 14th seed / 27 configs if they exist elsewhere.
2. **Reconcile peak positions** (0.074/0.255 vs 0.079/0.259) — decide which KDE bandwidth the paper intends.
3. **Consider adding DOS seeds** if Fig_dos's 2-seed basis is deemed too thin for a main-text claim.
4. **Document the finite-size data location** (sibling `_analysist/1_result/`) in the SI methods, since it is not in `paper_femgo/data/`.
