---
name: agox-run-code
description: "Use when writing or generating AGOX global-optimization run scripts (heterostructure, interstitial-alloy, order-parameter systems) following the user's canonical skeleton from main_test.ipynb."
version: 1.0.0
author: Calyx
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [agox, global-optimization, run-script, ase, gpaw, structure-search, materials-science]
    related_skills: [agox, gpaw, simulation-analysis]
---

# AGOX Structure-Search Run Scripts (user conventions)

## Overview

This skill encodes the user's canonical AGOX active-learning structure-search *run* script
pattern, extracted from `/home/think/Desktop/research/_run/2_run_agox/main_test.ipynb`.
It automates WRITING the run code (the AGOX global-optimization searches) — **not** the
analysis/post-processing code (DOS, PCA, energy progression — that is the
`simulation-analysis` skill).

The notebook's code has already been extracted, verbatim, into
`/home/think/Desktop/research/_run/2_run_agox/extracted/` (see its `README.md`). This skill
captures the *pattern* so new run scripts can be generated for new systems without
re-deriving the boilerplate.

## When to Use

- Writing a new AGOX structure-search run script for a new system (heterostructure,
  interstitial alloy, or order-parameter alloy).
- Adapting one of the extracted scripts to new lattice parameters / composition / species.
- Answering "what's the order/gets/sets wiring" or "which generator for which system".

Do NOT use for: the AGOX package API itself (see the `agox` skill), GPAW/DFT details (the
`gpaw` skill), or analysis/DOS/plotting (the `simulation-analysis` skill).

## Environment

- Python: `/home/think/miniconda3/envs/agox_v2/bin/python` (base `python3` has no AGOX/ASE).
- Run scripts live under `/home/think/Desktop/research/_run/2_run_agox/`; the local
  `scripts/` package holds the user's custom builders/generators. Extracted scripts carry a
  `sys.path` shim that auto-locates `scripts/`.
- `matplotlib.use('Agg')` before plotting imports (headless).

## The canonical skeleton (memorize this shape)

Every run script follows the same 16-step pattern inside `for seed in range(...)`:

1. **Directory routing** — `seed_{seed}/0_result/{0_xsf,1_fig}`, `seed_{seed}/1_db`,
   plus `0_result/latt_log.md` (lattice/strain log).
2. **Structure build** — `bulk` → `surface` → custom stack builder → `.repeat(supercell)`
   → defect/dopant modification.
3. **Confinement box** — `confinement_cell` (Z scaled by `confinement_cell_height_multiplyer`)
   and `confinement_corner` (substrate top + `dist_z_interface`).
4. **Environment** — `Environment(template=substrate, symbols=deposition.get_chemical_formula(),
   confinement_cell=…, confinement_corner=…, box_constraint_pbc=[True, True, False])`.
5. **Generators** — custom generator + `RattleGenerator` + permutation generator, each
   splatted with `**environment.get_confinement()`.
6. **Dry-run candidates** — call each generator once (`sampler=None` for gen 0, `FixedSampler`
   of the previous output for the rest), `write(...xsf)`, wrapped in try/except.
7. **Database + descriptor** — `Database(filename=f"{db_dir}/db_{seed}.db", order=5)`,
   `Fingerprint(environment=environment)`.
8. **GPR model** (invariant recipe) — see below.
9. **KMeansSampler** — `KMeansSampler(descriptor, database, sample_size)`.
10. **ParallelCollector** — `order=1`, `num_candidates={iteration: [per-generator counts]}`.
11. **LCB acquisitor** — `LowerConfidenceBoundAcquisitor(model, kappa, order=3)`.
12. **Relax postprocess** — `ParallelRelaxPostprocess(model=acquisitor.get_acquisition_calculator(),
    constraints=…, optimizer_run_kwargs={"steps": 100}, start_relax=10, order=2)`.
13. **GPAW backend** — `SubprocessGPAW` (invariant recipe below).
14. **Evaluator** — `LocalOptimizationEvaluator(calc, gets={"get_key": "prioritized_candidates"},
    optimizer_run_kwargs={"fmax": 0.05, "steps": 1}, constraints=…, store_trajectory=False, order=4)`.
15. **Orchestrate** — `AGOX(collector, relaxer, acquisitor, evaluator, database, seed=seed)`.
16. **Run** — `agox.run(N_iterations=N_iterations)`.

**Order assignments (invariant):** collector `1` → relaxer `2` → acquisitor `3` →
evaluator `4` → database `5`.

**GPR kernel recipe (invariant):**
```python
beta = 0.01
kernel = (C(5000, (1, 1e5))
          * (C(beta, (beta, beta)) * RBF()
             + C(1 - beta, (1 - beta, 1 - beta)) * RBF())
          + Noise(0.01, (0.01, 0.01)))
model = GPR(descriptor=descriptor, kernel=kernel, database=database, prior=Repulsive())
```

**GPAW backend recipe (invariant; drop `hund`/`spinpol` for non-magnetic systems):**
```python
calc = SubprocessGPAW(
    ncores=ncores, mode={"name": "lcao"}, basis="dzp", xc="PBE",
    mixer={"backend": "pulay", "beta": 0.05, "nmaxold": 5, "weight": 100},
    convergence={"energy": 1e-4, "density": 1e-3, "eigenstates": 1e-3},
    txt=f"output_seed_{seed}.txt", kpts=kpts, symmetry="off", nbands="nao",
    maxiter=100, occupations={"name": "fermi-dirac", "width": 0.05},
    hund=True, spinpol=True)   # magnetic (Fe-containing) systems only
```

A complete fill-in template is in `templates/run_agox_template.py`.

## Three system archetypes

| Archetype | Builders | Custom generator(s) | Examples |
|---|---|---|---|
| **Heterostructure** (Fe/MgO + dopant) | `build_mgo_stack`, `build_fe_stack`, `build_heteroStruct`, `remove_random_atoms_by_species`, `add_adsorbate_to_hollows` | `HeteroStructRandomize` + `GlobalPermutationGenerator` | `run_agox_fe_mgo_b.py`, `run_agox_mgo_on_fe.py` |
| **Interstitial alloy** (Pt-P, Ta-B) | `generate_interstitial_alloy` / `add_B_concentration` | `AmorphStructRandomize` + `AmorphPermutationGenerator` | `run_agox_amorph_ptp.py` |
| **Order-parameter alloy** (FePt/Fe3Pt) | `read(.cif)` + `make_supercell` | `BraggGenerator` | `run_agox_bragg_fept.py` |

Details and custom-module signatures in `references/systems.md`.

## User conventions

- **Config at top** in `# === SECTION ===` blocks; seed loop below; flat scripts (no
  `if __name__ == "__main__"`).
- **Seed loop** over `range(103)` (hetero) or `range(100)` (alloy/bragg).
- **Directory tree** `seed_N/0_result/0_xsf`, `seed_N/0_result/1_fig`, `seed_N/1_db`.
- **Lattice log** `latt_log.md` records `a_deposition`, `a_substrate`, `a_substrate_matched`,
  `strain`.
- **`num_candidates`** maps iteration → per-generator candidate counts (e.g.
  `{0: [20, 0, 0], 10: [10, 5, 5], 25: [0, 10, 10]}`) — staged exploration.
- **Interstitial count formula** `num_to_add = round(C*A/(1-C))` where `A` = host atom count,
  `C` = target concentration fraction.

## Common Pitfalls

1. **`mode={"name": "lcao"}` is a dict**, not `mode="lcao"` (SubprocessGPAW convention).
2. **`hund`/`spinpol` only for magnetic systems** (Fe, FePt). Pt-P / Ta-B runs omit them.
3. **Order assignments are load-bearing** — collector(1) < relaxer(2) < acquisitor(3) <
   evaluator(4) < database(5). Reordering breaks the `prioritized_candidates` dataflow.
4. **`gets={"get_key": "prioritized_candidates"}`** on the evaluator (the LCB acquisitor
   feeds it), not `"candidates"`.
5. **Splat `**environment.get_confinement()` into every generator** and pass
   `constraints=environment.get_constraints()` to relaxer + evaluator.
6. **Dry-run candidates** (`write(...xsf)`) catch generator misconfiguration before the
   expensive search starts — keep them, they're the user's smoke test.
7. **`scripts/` must be importable** — extracted scripts self-locate it; new scripts placed
   outside `2_run_agox/` need the same `sys.path` shim or `PYTHONPATH`.
8. **Custom scripts drift from the notebook** — e.g. `build_mgo_stack(slab_fe, num_layers,
   dist_fe2o=2.3, dist_mgo=2.106, output_path=None, vacuum=10, rotate_system=False)`; the
   notebook passes keyword args, so prefer keyword invocation.
9. **`agox.run(...)` is sometimes left commented** in the source (dry-run mode); uncomment
   to actually run the search.

## Reference files

- `templates/run_agox_template.py` — complete fill-in-the-blanks skeleton (heterostructure).
- `references/systems.md` — per-archetype structure-building + generator recipes and the
  custom-module signature index.

## Verification Checklist

- [ ] New script follows the 16-step skeleton with correct `order` assignments
- [ ] `SubprocessGPAW` uses `mode={"name": "lcao"}`, dzp/PBE/pulay/fermi-dirac settings
- [ ] `hund`/`spinpol` present iff the system is magnetic
- [ ] Every generator splatted with `**environment.get_confinement()`
- [ ] GPR kernel recipe unchanged; evaluator `get_key` is `prioritized_candidates`
- [ ] Directory tree + `latt_log.md` written per seed
- [ ] Script placed so `scripts/` resolves (shim or `2_run_agox/` root)
