# VERSIONS.md — paper_femgo

Per-file `__version__` manifest. Bump patch on any edit, minor on behavior change. Update this file + LOG.md on every code change.

| File | Version | Notes |
|------|---------|-------|
| `codes/common.py` | 1.2.0 | TRIAL style: owner's sans-serif rcParams (OLD_SOURCE_STYLE kept for revert) |
| `codes/emit_datasets.py` | 1.1.0 | generates all CSVs + per-figure JSONs; KDE_BW param (None=Scott) |
| `codes/draw_energy_progression.py` | 1.2.0 | Fig_Prog (reads Fig_Prog.json; Run 1–13 labels) |
| `codes/draw_landscape.py` | 1.1.0 | Fig_ConDen (reads Fig_ConDen.json) |
| `codes/draw_boltzmann.py` | 1.1.0 | Fig_Boltz (reads Fig_Boltz.json) |
| `codes/draw_dos.py` | 1.1.0 | Fig_dos (reads Fig_dos.json) |
| `codes/draw_state_density_conv.py` | 1.2.0 | Fig_convStateDens (reads JSON; Run 1–13 labels) |
| `codes/draw_si_mgo.py` | 1.1.0 | Fig_mgo (reads Fig_mgo.json) |
| `codes/draw_si_env.py` | 1.0.0 | Fig_env (structure, data-driven) |
| `codes/draw_si_supercell.py` | 1.0.0 | Fig_sup (reads data/femgo_3x3, femgo_4x4) |
