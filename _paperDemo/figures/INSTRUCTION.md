# `figures/` — how the figures are produced, and what is open

**Figure design is the scientist's call.** The scripts here own the mechanics only; restyling them
without reading this file is not wanted. When a figure changes, record what changed here.

## Producing the figures

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python     # the only env with ase/AGOX
cd /home/think/Desktop/research/_paperDemo
$PY scripts/ensemble_analysis.py        # rebuilds analysis/pes_structures.csv + ensemble_stats.json
$PY scripts/plot_pes_figure.py          # pes_<n>_systems.png, flat_state_summary.png
$PY scripts/export_flat_xsf.py          # analysis/flat_structures/*.xsf
$PY scripts/preview_flat_xsf.py         # flat_vs_ground_preview.png
$PY scripts/iteration_budget.py         # figures/iteration_budget.png (SI-9, §S4)
$PY scripts/lattice_constraint.py       # figures/lattice_constraint.png (SI-10, §S5)
$PY scripts/mgo_on_fe.py                # figures/mgo_on_fe.png (SI-11, §S6 — qualified finding)
```

## Styling conventions (do not change silently)

- **Palette:** `tab10` **solid** colours only — no dashed/dotted markers, no `viridis` (its pale
  yellow is unreadable in a presentation), no per-point colouring by density.
- **Line width** ≈ 1.8; grids `alpha=0.25, lw=0.5`.
- Fe host = `tab10[0]` (blue), Fe-B = `tab10[3]` (red). The old four-system palettes assigned
  `len10[2]/[4]` to the Co systems, which are gone.
- DPI 300 for manuscript figures, 200 for the preview render.

## Changed mechanically in v9 (scope: Fe/MgO + Fe-B/MgO only)

These changes follow from archiving the Co host; they are not styling decisions, but they do change
the look of the figures, so they are listed for review.

1. **`pes_four_systems.png` → `pes_<n>_systems.png`.** With two systems in scope the script now
   writes `pes_2_systems.png` as a **1×2** grid. The panel count, the grid shape and the file name
   are derived from the systems actually present in `analysis/pes_structures.csv`
   (`--all-systems` restores the 2×2 four-panel version under `pes_4_systems.png`).
2. **`flat_state_summary.png` lost its B×Co design.** It was a 2×2 comparison (four bars: Fe, Fe-B,
   Fe-Co, Fe-Co-B, with one bracket per host pair). It is now one bar per system in scope plus a
   single "B effect" bracket. **This is the figure most in need of a scientist's redesign** — see
   the open questions below.
3. **y-limits are now data-driven** (`max(0.5, 1.05·max ΔE)`) instead of a fixed `(0, 0.5)`. The
   fixed frame clipped real structures: Fe-B has flat-basin points up to 0.726 eV/atom, over 45 %
   above the old ceiling. Revert to a fixed frame only if that clipping was intentional.
4. **Axis/figure wording:** "ΔZ over Fe+Co" → "ΔZ over the film metal" (the metric is
   `pes_analysis.METAL = ('Fe','Co')`, so boron never entered it).
5. **`flat_vs_ground_preview.png`** now renders one row per system in scope (2, not 4).

## Open questions for the scientist

- [ ] **`flat_state_summary.png`:** with one host, is a two-bar chart still the right figure, or
      should it become e.g. a two-panel (flat / island) comparison, or a ΔE/N-shift plot with the
      per-replica spread shown? The B effect (−0.040 eV/atom) is the paper's headline number and
      currently appears as a single bracket label.
- [ ] **`pes_2_systems.png`:** 1×2 side by side, or stacked vertically for a single-column layout?
      Should the flat window (ΔZ ≤ 1.0 Å) shading stay?
- [ ] **No section cites any main-text figure yet** (`paper_status.md`: Tables 1–3 + Figure 1 are in
      Methods; the PES maps are uncited). Figure numbering is unassigned — decide whether the PES
      maps become Figure 2 and the summary Figure 3 before the LaTeX port.
- [ ] **`exploration_performance_femgo.png` and `method_sensitivity_*.png`** are SI figures and are
      untouched by the Co archive (they are all `femgo`-based). They keep their own `S` numbering.
- [ ] **`iteration_budget.png` (new, §S4, SI-9).** Three panels: (a) the absolute ground state still
      improving with budget, (b) the flat–island separation not shrinking, (c) the per-search change
      from 100 to the full budget. Panel (c) is the primary evidence. Open: whether to add the
      pooled-per-arm curve to (c), and whether the per-run lines in (a)/(b) should be thinned (17
      lines is busy) — e.g. show the median ± range per arm instead.
- [ ] **`mgo_on_fe.png` (new, §S6, SI-11 — qualified finding).** Three panels: (a) per-seed best
      energy of the inverted stack (shows the 59 eV spread), (b) the MgO film's ΔZ at each search's
      best against the 1.0 Å threshold, (c) the flat-basin fraction per search. Open: whether a
      fourth panel comparing the two stacks' film-ΔZ distributions would make the inversion clearer
      than Table S6 does.
- [ ] **`lattice_constraint.png` (new, §S5, SI-10).** Three panels: (a) separation vs the constraint
      with per-search scatter, (b) ΔZ distributions per arm, (c) per-search spread. Open: whether
      the main-text reference (f = 0) should be a distinct marker in (a) — it currently is the leftmost
      point — and whether the a_Fe difference (2.866 vs 2.87019 Å) should be annotated on the axis.
