# VERSIONS.md — paper_femgo

Per-file `__version__` manifest. Bump patch on any edit, minor on behavior change. Update this file + LOG.md on every code change.

| File | Version | Notes |
|------|---------|-------|
| `codes/common.py` | 1.5.0 | + febmgo_db_paths (completion-filtered) + _db_max_iteration |
| `codes/emit_datasets.py` | 1.4.0 | + Fig_mgo boltzmann data; mgo state-density grid reaches axis cap (3.7) |
| `codes/draw_energy_progression.py` | 1.3.1 | Fig_Prog: 13 viridis colors, solid lines; framed legend box |
| `codes/draw_landscape.py` | 1.5.0 | Fig_ConDen: s=10 no-edge; YlGnBu_r; peak lines zorder=20 + white shadow |
| `codes/draw_boltzmann.py` | 1.5.1 | Fig_Boltz: line lw=1.0; peak lines zorder=20 + white shadow; framed legend box |
| `codes/draw_dos.py` | 1.1.1 | Fig_dos (reads Fig_dos.json); framed legend box |
| `codes/draw_state_density_conv.py` | 1.4.1 | Fig_convStateDens: lw=1.0/0.9; framed legend box |
| `codes/draw_si_mgo.py` | 1.5.1 | Fig_mgo: 3-panel (a/b/c) + Boltzmann; rel-E cap 3.7; YlGnBu_r; framed legend box |
| `codes/draw_si_env.py` | 1.0.0 | Fig_env (structure, data-driven) |
| `codes/draw_si_supercell.py` | 1.0.0 | Fig_sup (reads data/femgo_3x3, femgo_4x4) |
| `codes/emit_fig_sup_vesta.py` | 1.1.1 | Fig S2 ground states → .vesta (3x3 + 4x4); Fe height-darkening (darken_factor 0.8, max_cbar = actual ΔZ) |
| `codes/emit_fig_sup_png.py` | 2.0.0 | Fig S2 panels from VESTA renders: separate Fig_sup_a.png / Fig_sup_b.png (no embedded labels; 300 dpi) |
| `codes/emit_wetting_modes.py` | 1.3.0 | mode-gap + PCA landscape (Fe/MgO vs Fe-B/MgO); pooled, no LOOCV; + branch modes in landscape |
| `codes/draw_wetting_modes.py` | 1.2.0 | Fig_wetModes four-curve overlay + mode markers + top gap arrows; framed legend box |
| `codes/draw_wet_landscape.py` | 1.4.0 | Fig_wetLandscape two-panel PCA+Δz landscape; flat/island mode dashed lines (white shadow) |
