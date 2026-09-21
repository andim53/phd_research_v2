# VERSIONS.md — paper_femgo

Per-file `__version__` manifest. Bump patch on any edit, minor on behavior change. Update this file + LOG.md on every code change.

| File | Version | Notes |
|------|---------|-------|
| `codes/common.py` | 1.4.0 | ACCEPTED sans-serif; ticks outward; no inner ticks |
| `codes/emit_datasets.py` | 1.3.0 | + Fig_mgo boltzmann data; mgo state-density grid reaches axis cap (3.7) |
| `codes/draw_energy_progression.py` | 1.3.0 | Fig_Prog: 13 viridis colors, solid lines |
| `codes/draw_landscape.py` | 1.5.0 | Fig_ConDen: s=10 no-edge; YlGnBu_r; peak lines zorder=20 + white shadow |
| `codes/draw_boltzmann.py` | 1.4.0 | Fig_Boltz: line lw=1.0; peak lines zorder=20 + white shadow |
| `codes/draw_dos.py` | 1.1.0 | Fig_dos (reads Fig_dos.json) |
| `codes/draw_state_density_conv.py` | 1.4.0 | Fig_convStateDens: lw=1.0/0.9 |
| `codes/draw_si_mgo.py` | 1.4.0 | Fig_mgo: 3-panel (a/b/c) + Boltzmann; rel-E cap 3.7; YlGnBu_r |
| `codes/draw_si_env.py` | 1.0.0 | Fig_env (structure, data-driven) |
| `codes/draw_si_supercell.py` | 1.0.0 | Fig_sup (reads data/femgo_3x3, femgo_4x4) |
