# README for AI Agents — `d_landauPlus`

Machine-readable spec for agents working on this project. Complements the
governing `AGENTS.md` and the action `LOG.md`. Read both first.

## 1. Project identity

- **Dir:** `/home/think/Desktop/research/_run/d_landauPlus/`
- **Purpose:** Inherent-structure (basin-hopping) **Wang–Landau sampling** of the
  flat↔island transition in Fe/MgO, on an **AGOX GPR surrogate** only — **no DFT
  evaluation anywhere**.
- **Physics:** 75-atom Fe₂₅Mg₂₅O₂₅ (25 mobile Fe on a fixed MgO substrate). Two
  motifs: the **flat monolayer** (Fe z-spread ≈ 0 Å, metastable, E_rel ≈ 0.67
  eV/atom) and the **island** 3D cluster (Fe z-spread ≳ 2 Å, global minimum).
- **Sibling of** `c_landausampling` (same data, same Wang–Landau estimator, but
  that project does a *rattle-only* walk with no relax; this project does the
  **basin-hopping** variant: every proposal is rattle → GPR-relax → WL-accept).
- **Environment (invariant):** `/home/think/miniconda3/envs/agox_v2/bin/python`
  (AGOX 3.10.2 + ASE 3.25.0). Base `python3` has **no** AGOX/ASE. Heavy runs are
  HPC (`gpaw_env` pjsub); see §4 caveat.

## 2. File layout

```
d_landauPlus/
├── main.py                    # CLI: load data -> train GPR -> LandauPlusSampler -> thermodynamics
├── landau_plus/               # package
│   ├── __init__.py            #   re-exports LandauPlusSampler, load_all_seeds, build_gpr, validate_gpr, K_B, g_of_E_to_thermodynamics
│   ├── wang_landau_sampler.py #   LandauPlusSampler (basin-hopping WL, v1.0.0)
│   ├── gpr_training.py        #   load_all_seeds, build_gpr, validate_gpr
│   ├── thermodynamics.py      #   g_of_E_to_thermodynamics, heat_capacity_from_thermo
│   └── utils.py               #   K_B, shift_energies, _logsumexp
├── smoke_test_landau_plus.py  # cheap local validation (fake 2-Fe double-well GPR)
├── data/femgo/                # GOFEE/AGOX GO run: seed DBs + build/generator scripts
│   └── seed_*/1_db/db_*.db    #   the 13 seed databases (>stop_16 excluded by design)
├── README.AI.md / AGENTS.md / LOG.md
└── lp_output/                 # sampler output (regenerable, gitignored)
```

### 2a. Source versioning
Every source file carries a module-level `__version__` (semver). `VERSIONS.md` is
the manifest; bump the file's patch on every edit, minor on API/behavior change;
append old→new to `LOG.md`. In-scope: `main.py`, `landau_plus/`,
`smoke_test_landau_plus.py`. `data/` snapshots are **not** versioned.

## 3. Entry points & commands

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
cd /home/think/Desktop/research/_run/d_landauPlus

# Compile-check
$PY -m py_compile main.py smoke_test_landau_plus.py landau_plus/*.py

# Cheap smoke test (fake double-well GPR on 2-Fe motif; ~10 s)
$PY smoke_test_landau_plus.py

# Production run (default data/femgo)
$PY main.py --mc-steps 50000 --rattle 1.5 --relax-steps 100 \
    --e-max 0.75 --n-bins 50 --temperatures 100,200,300,500,1000 \
    --output ./lp_output --rng 42
```

### `main.py` CLI
| Flag | Default | Meaning |
|---|---|---|
| `--dataset` | `data/femgo` | Dir with `seed_*/1_db/db_*.db`. |
| `--n-bins` | `50` | Energy bins. |
| `--e-min` / `--e-max` | `0.0` / `0.75` | Bin range (eV/atom rel). `0.75` gives margin over the flat-basin top (~0.67). |
| `--e-reject` | `5×e_max` | Rel energy above which a trial is rejected as GPR extrapolation. |
| `--rattle` | `1.5` | Uniform-in-volume rattle of Fe atoms (Å). **TEST MULTIPLE VALUES — the flat/island weight is δ-sensitive.** |
| `--relax-steps` | `100` | GPR BFGS steps per trial (GO run's cap; `fmax OR steps`). |
| `--perturb-symbols` | `Fe` | Mobile atoms to rattle/relax. |
| `--flat-island-spread` | `1.0` | Fe z-spread threshold (Å) for flat vs island labelling. |
| `--flatness-criterion` | `0.80` | WL flatness threshold. |
| `--check-interval` | `5000` | Flatness check interval. |
| `--n-stages-standard` | `14` | Standard halvings before 1/t switch. |
| `--mc-steps` | `50000` | WL MC steps. |
| `--temperatures` | `100,200,300,500,1000` | Thermodynamics T (K). |
| `--output` | `./lp_output` | Output dir. |
| `--rng` | `42` | Seed. |
| `--use-ray` | off | Ray in GPR training. |

## 4. Dependencies & environment

- Conda env **`agox_v2`** (AGOX 3.10.2, ASE 3.25.0) — **local** compile/smoke/validation.
- Heavy runs target the **HPC** (`gpaw_env` pjsub). **Caveat:** the sampler needs
  the AGOX/ASE stack; if `gpaw_env` lacks it, switch `conda activate` to `agox_v2`.
- `matplotlib.use("Agg")` before plotting in headless runs.
- `GPR(..., use_ray=False)` default (single-process).

## 5. Inputs / Outputs

**Inputs:** `data/femgo/seed_*/1_db/db_*.db` (13 DBs, Fe₂₅Mg₂₅O₂₅, 75 atoms;
`stop_16` excluded by the `seed_*` glob by design).

**Outputs** (under `--output`): `g_of_E.csv/.png`, `thermodynamics.csv`,
`heat_capacity.csv`, `ensemble.traj` + `ensemble.csv`
(`energy_eV,rel_eV_per_atom,fe_z_spread_A,flat_island`). All regenerable/gitignored.

**Ensemble caveat (load-bearing):** the ensemble stores every *accepted relaxed*
trial; it is a **1/g(E)-biased** sample (Wang–Landau samples ∝ 1/g(E)), NOT a
Boltzmann sample. It is reweightable to any `T` via
`w_i(T) = exp(−E_i/k_B T) / g(E_i)`. Because every trial is relaxed to a basin
minimum, these are **inherent-structure** (basin) samples, not configurational
— the same caveat applies to `Z`, `F`, `C_V`.

## 6. Error handling & edge cases

1. **No DBs matched** → `FileNotFoundError` from `load_all_seeds` (check `--dataset`).
2. **Composition mismatch** → one global `Fingerprint` = one stoichiometry; don't mix.
3. **Init structure out of window** → the flat reference (highest-E DB structure)
   sits at E_rel ≈ 0.67 < e-max 0.75; if a different dataset's max exceeds e-max,
   lower it or raise `--e-max`.
4. **GPR extrapolation** → `|E|>1e4` or rel E > e-reject is rejected (revisits bin).
5. **Relax hits constraint wall / step cap** → BFGS returns the end-of-relax
   structure (`fmax OR steps`), not necessarily a converged minimum.
6. **BFGS singular in the toy** → the smoke test uses a 2-mobile-atom motif with
   per-atom full-rank forces deliberately (25-Fe motifs have 23 zero-force atoms
   → singular Hessian); the production 25-Fe relax is expected to converge because
   the real GPR gives all Fe atoms nonzero forces.

## 7. Provenance / references

- Data: `data/femgo/main.py` — the original GOFEE/AGOX GO run (HeteroStructRandomize
  + RattleGenerator, LCB acquisition, GPAW lcao/PBE; constraint =
  `environment.get_constraints()` = FixAtoms(substrate) + BoxConstraint(Fe)).
- Algorithm sibling: `_run/c_landausampling/` (Wang–Landau, rattle-only; here the
  basin-hopping variant).
- Literature: Wang & Landau 2001 (PRL 86, 2050); Belardinelli & Pereyra 2007
  (JCP 127, 184105) — 1/t algorithm; Stillinger–Weber inherent structures.
- Skills: `ai-agent-project-workflow`, `agox`, `agox-wang-landau`, `agox-run-code`.