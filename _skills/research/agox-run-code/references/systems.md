# System archetypes + custom module index

Three recurring system types appear in the user's run code. Each has its own structure
builder + custom generator set; everything else (Environment, GPR model, GPAW backend,
orchestration) is shared.

## 1. Heterostructure (Fe/MgO + dopant)

Structure: `bulk` → `surface` → `build_mgo_stack` (substrate) + `build_fe_stack`
(deposition) → `.repeat(supercell)` → `remove_random_atoms_by_species` (vacancies) →
`add_adsorbate_to_hollows` (dopant, e.g. B) → `build_heteroStruct` (stack them).

Generators:
1. `HeteroStructRandomize` — large-scale structural randomization of the deposition slab.
2. `RattleGenerator` — local coordinate rattle (`n_rattle=int(0.5*N)`, `rattle_amplitude=2.3`).
3. `GlobalPermutationGenerator` — element permutation (`max_number_of_swaps=num_atoms_add`,
   `rattle_strength=0.5`).

`box_constraint_pbc=[True, True, False]` (slab — non-periodic in z). Magnetic →
`hund=True, spinpol=True`.

Reference scripts: `run_agox_fe_mgo_b.py`, `run_agox_mgo_on_fe.py`,
`run_agox_fe_mgo_b_variant.py`, `build_fe_mgo_hetero_interface.py`.

## 2. Interstitial alloy (Pt-P, Ta-B)

Structure: `bulk(HOST, CRYSTAL_STRUCTURE, a=...)` → optional `.set_cell(cell*scale)`
→ `generate_interstitial_alloy(host_unit, interstitial_element, supercell_dim, num_to_add,
lattice_type)` (or `add_B_concentration` for Ta-B). `num_to_add = round(C*A/(1-C))`.

Generators:
1. `AmorphStructRandomize` — amorphization (`amorph=alloy`, `rattle_amplitude`, `attempts`,
   `n_rattle`, `generate_pristine=False`, `check_covalent`).
2. `RattleGenerator`.
3. `AmorphPermutationGenerator` — permutation with overlap validation (`check_overlap`,
   `min/max_distance_scale`).

`box_constraint_pbc=[True, True, True]` (bulk — periodic). Non-magnetic → omit `hund`/`spinpol`.

Reference scripts: `run_agox_amorph_ptp.py`, `sweep_cell_scale_ptp.py`,
`generate_interstitial_alloy_demo.py`, `setup_tab_amorph.py`, `test_tab_concentration.py`.

## 3. Order-parameter alloy (FePt / Fe3Pt)

Structure: `read(cif_file)` → `atoms.set_cell(new_lattice_params, scale_atoms=True)` →
`make_supercell(atoms, np.diag(supercell))`. Ideal sublattices (Fe sites / Pt sites) are
identified from the ordered CIF; `S = (p - r)/(1 - r)` with `r = x_Fe² + x_Pt²`
(0.5 for FePt, 0.625 for Fe3Pt).

Generators:
1. `BraggGenerator` — anti-site swap to a target long-range order parameter
   (`atoms_template`, `S_target`, `randomize_seed=True`, `min_distance_scale`, `write_struct`).
2. `RattleGenerator` (`rattle_amplitude=0.3`).

`box_constraint_pbc=[True, True, True]` (bulk). Magnetic → `hund=True, spinpol=True`.

Reference scripts: `run_agox_bragg_fept.py`, `generate_bragg_order_structures.py`,
`disorder_generator.py`.

## Custom module signature index (in `scripts/`)

Builders:
- `build_fe_stack(slab_fe, num_layers, vacuum, output_path) -> Atoms`
- `build_mgo_stack(slab_fe, num_layers, dist_fe2o=2.3, dist_mgo=2.106, output_path=None,
  vacuum=10, rotate_system=False) -> Atoms`
- `build_heteroStruct(slab_substrate, slab_deposition, dist_inter=2.3, vacuum=10,
  output_path=None, ratio_slab="2:2") -> (hetero, substrate, deposition, sub_heights, dep_heights)`
- `remove_random_atoms_by_species(atoms, species, count) -> Atoms`
- `add_adsorbate_to_hollows(atoms, symbol, height, num_atoms, seed) -> Atoms`
- `generate_interstitial_alloy(host_unit, interstitial_element, supercell_dim, num_to_add,
  lattice_type, seed) -> Atoms`
- `add_B_concentration(ta, cB, interstitial_type=None, fracs=None, seed=None,
  make_structure=True) -> (atoms, n_b, n_ta)`
- `buld_amorp_slab.py` — `build_amorphous_TaB_layer`, `build_Si_oxide_TaB_stack`,
  `build_amorphous_WTaB_layer`, etc.

Custom generators (all subclass AGOX `GeneratorBaseClass`; instantiate with
`**environment.get_confinement()` + their own kwargs):
- `HeteroStructRandomize(slab_deposition, depos_pos_mean, write_struct, attempts,
  hetero_slab_dist, replace, rattle_amplitude, n_rattle, generate_pristine,
  add_inter_layer_space, boltzmann_rattle, output_dir)`
- `GlobalPermutationGenerator(max_number_of_swaps, rattle_strength, ignore_H,
  write_candidates_to_disk, replace, attempts)`
- `AmorphStructRandomize(amorph, write_struct, write_temp_struct, attempts, replace,
  rattle_amplitude, n_rattle, generate_pristine, output_dir, check_covalent,
  min_distance_scale, print_result)`
- `AmorphPermutationGenerator(max_number_of_swaps, rattle_strength, use_xy_only,
  ignore_species, write_candidates_to_disk, replace, attempts, check_overlap,
  min_distance_scale, max_distance_scale, print_result, output_dir, write_struct)`
- `BraggGenerator(atoms_template, S_target, S_options, seed, randomize_seed, write_struct,
  output_dir, min_distance_scale, print_result, replace)`

## Shared invariant blocks

GPR kernel:
```python
beta = 0.01
kernel = (C(5000, (1, 1e5))
          * (C(beta, (beta, beta)) * RBF()
             + C(1 - beta, (1 - beta, 1 - beta)) * RBF())
          + Noise(0.01, (0.01, 0.01)))
model = GPR(descriptor=descriptor, kernel=kernel, database=database, prior=Repulsive())
```

GPAW (magnetic — drop `hund`/`spinpol` otherwise):
```python
SubprocessGPAW(ncores=ncores, mode={"name": "lcao"}, basis="dzp", xc="PBE",
    mixer={"backend": "pulay", "beta": 0.05, "nmaxold": 5, "weight": 100},
    convergence={"energy": 1e-4, "density": 1e-3, "eigenstates": 1e-3},
    txt=f"output_seed_{seed}.txt", kpts=kpts, symmetry="off", nbands="nao",
    maxiter=100, occupations={"name": "fermi-dirac", "width": 0.05},
    hund=True, spinpol=True)
```
