# Extracted from main_test.ipynb

Each `.py` file below was extracted verbatim from `main_test.ipynb` (the "Active Learning
Global Optimization of B-Doped Fe/MgO Heterostructures" notebook). A 2-line header docstring
records the source cell + section. Files that import the local `scripts/` package get a small
`sys.path` shim at the top so they run regardless of cwd.

Run from anywhere (they self-locate `scripts/`):

```
/home/think/miniconda3/envs/agox_v2/bin/python extracted/running/run_agox_fe_mgo_b.py
```

## running/  (AGOX global-optimization structure search)

| File | Source cell | Purpose |
|---|---|---|
| build_fe_mgo_hetero_interface.py | 2 | Build Fe/MgO heterostructure + B adsorbate (no AGOX) |
| run_agox_fe_mgo_b.py | 4 | MAIN: B-doped Fe/MgO active-learning search |
| generate_interstitial_alloy_demo.py | 7 | Insert interstitials into host unit cell |
| sweep_cell_scale_ptp.py | 9 | Pt-P cell-scale sweep (find valid scale) |
| run_agox_amorph_ptp.py | 11 | Pt-P interstitial alloy AGOX search (amorph) |
| setup_tab_amorph.py | 16 | Ta-B amorph environment setup |
| run_agox_mgo_on_fe.py | 18 | MgO-on-Fe 5x5, lattice constraint |
| generate_bragg_order_structures.py | 31 | FePt/Fe3Pt anti-site order-parameter structures |
| disorder_generator.py | 32 | Custom `DisorderGenerator` (incomplete) |
| run_agox_bragg_fept.py | 34 | FePt/Fe3Pt BraggGenerator AGOX search |
| run_agox_fe_mgo_b_variant.py | 36 | "Trash" variant of B-doped Fe/MgO search |
| test_tab_concentration.py | 37 | Ta-B concentration test |

## analysis/  (post-processing, DOS, plotting)

| File | Source cell | Purpose |
|---|---|---|
| thermal_expansion_plot.py | 13 | Pt thermal-expansion % vs T |
| calc_dft_single_ta.py | 15 | Single Ta bulk GPAW SCF |
| filter_traj.py | 20 | Filter atoms from a .traj |
| run_dos_pdos_workflow.py | 22 | DOS + PDOS (Fe dz2 / O pz) -> CSV |
| create_dos_test_traj.py | 23 | Build test .traj of BCC Fe |
| run_scf_to_gpw.py | 24 | SCF -> .gpw (mode='all') |
| run_dos_from_gpw.py | 26 | DOS from .gpw (modern API) |
| plot_dos_from_csv.py | 27 | Plot spin-resolved DOS/PDOS from CSV |

## Custom `scripts/` modules used (not extracted — already in `../scripts/`)

Structure builders: `build_fe_stack`, `build_mgo_stack`, `build_heteroStruct`,
`remove_random_atoms_by_species`, `add_adsorbate_to_hollows`, `generate_interstitial_alloy`,
`add_B_concentration`, `buld_amorp_slab`.

Custom generators: `HeteroStructRandomize`, `GlobalPermutationGenerator`,
`AmorphStructRandomize`, `AmorphPermutationGenerator`, `BraggGenerator`.
