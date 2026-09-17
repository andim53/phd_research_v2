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
   *(Superseded for the PES maps on 2026-09-18 — they now share one range anchored to the boron-free
   reference, which clips the Fe-B tail by decision. See "Changed 2026-09-18" below. The
   `flat_state_summary.png` bar frame is still per-figure data-driven.)*
4. **Axis/figure wording:** "ΔZ over Fe+Co" → "ΔZ over the film metal" (the metric is
   `pes_analysis.METAL = ('Fe','Co')`, so boron never entered it).
5. **`flat_vs_ground_preview.png`** now renders one row per system in scope (2, not 4).

## Changed 2026-09-18 (two corrections requested by the scientist)

Neither is a restyle: one is a shared axis scale, the other is a placement bug.

1. **`pes_2_systems.png` — one energy range on both panels, anchored to the boron-free reference.**
   The panels were each framed on their own data, so the Fe/MgO panel spanned 0–0.64 eV/atom while
   the Fe-B/MgO panel spanned 0–2.26: side by side, the same ΔE/N meant two different things. Both
   panels now use the Fe/MgO range, **(−0.01, 0.636) eV/atom**. This is a *deliberate ceiling*, not
   the union of the data: Fe-B/MgO reaches 2.149 eV/atom, and framing the reference on that union
   squashes the flat-island region the figure exists to show.
   - **Consequence, by decision: 25 of the 543 Fe-B/MgO points (4.6 %, 2 of them inside the flat
     window) lie above the ceiling and are not drawn.** `plot_pes_figure.py` prints that count on
     every run so it stays on the record; it is not annotated on the figure.
   - The reference panel is the first system in `SYSTEMS_IN_SCOPE` (`femgo`), so `--all-systems`
     keeps the same rule.
2. **`mgo_on_fe.png` — the two branch labels were outside the figure.** The labels were drawn with
   `transform=ax2.get_yaxis_transform()`, whose **y is in data units, not axes fractions**, so
   "flat film lower" at `y=1.0` was placed at 1.0 eV/atom — with the panel's range at
   (−0.026, 0.199) that is ≈0.8 eV/atom, i.e. ~4.6 panel-heights above the top edge, off the
   figure. Both labels now use `transAxes` and sit at the midpoint of the region each one names
   (island band / flat-film band), in the right margin just outside the panel. Verified by
   comparing rendered text boxes against the axes box.

Both scripts keep their version bump convention (`plot_pes_figure.py` 1.2.0, `mgo_on_fe.py` 2.0.1);
no number in any analysis result moved — the regenerated `analysis/mgo_on_fe.json` differs from the
previous one in its `version` field only, and the flat-basin minima are unchanged at 0.1888 / 0.1493
eV/atom.

## Changed 2026-09-18 (figure titles removed, at the scientist's request)

The figure-level title on every manuscript figure was removed — it duplicated the LaTeX caption.
Each affected script had its `fig.suptitle(...)` call deleted (and the `tight_layout(rect=...)` top
margin restored to a full-height `rect=[0, 0, 1, 1]`); for `flat_state_summary.png`, whose title was
a single-axes `ax.set_title('Flat film vs ground state: effect of B')`, that call was deleted too.
Panel labels are untouched — the per-panel titles in `pes_2_systems.png` (system names), the
`(a)/(b)/(c)` panel headings, and the two group titles in `interface_registry_topview.png` all stay,
since the captions refer to them.

Scripts touched (VERSION bumped by one patch level where they define one): `plot_pes_figure.py`
(1.2.1), `plot_registry.py`, `exploration_performance.py` (1.0.1), `pdos_flat_vs_island.py`,
`method_sensitivity.py`, `iteration_budget.py` (1.0.1), `lattice_constraint.py` (1.0.1),
`mgo_on_fe.py` (2.0.2). All 11 manuscript figures were regenerated from the agox_v2 env; no analysis
number changed (only the `version` fields and the plot text).

## Open questions for the scientist

> These are the figure-level decisions of the consolidated checklist in `paper_status.md` → OPEN
> (items **D1–D6**, 2026-09-18). Detail and reasoning stay here; the checklist is the index.

- [ ] **`flat_state_summary.png`:** with one host, is a two-bar chart still the right figure, or
      should it become e.g. a two-panel (flat / island) comparison, or a ΔE/N-shift plot with the
      per-replica spread shown? The B effect (−0.040 eV/atom) is the paper's headline number and
      currently appears as a single bracket label.
- [ ] **`pes_2_systems.png`:** 1×2 side by side, or stacked vertically for a single-column layout?
      Should the flat window (ΔZ ≤ 1.0 Å) shading stay?
- [ ] **Figure numbering — assigned 2026-09-18 by order of appearance** (`paper_status.md` →
      "Float numbering"): the PES maps are **Figure 2** (§2.1) and the flat-basin summary is
      **Figure 3** (§2.2); both are captioned and called out in `02_results.md` v5, so no main-text
      float is uncited. Still open: whether the side-view render (`flat_vs_ground_preview.png`)
      becomes a **Figure 4** in §2.1 — it is a 200 dpi preview and would need a 300 dpi re-render.
- [ ] **`exploration_performance_femgo.png` and `method_sensitivity_*.png`** are SI figures and are
      untouched by the Co archive (they are all `femgo`-based). They keep their own `S` numbering.
- [ ] **`iteration_budget.png` (new, §S4, SI-9).** Three panels: (a) the absolute ground state still
      improving with budget, (b) the flat–island separation not shrinking, (c) the per-search change
      from 100 to the full budget. Panel (c) is the primary evidence. Open: whether to add the
      pooled-per-arm curve to (c), and whether the per-run lines in (a)/(b) should be thinned (17
      lines is busy) — e.g. show the median ± range per arm instead.
- [ ] **`mgo_on_fe.png` (new, §S6, SI-11 — a ground-state comparison).** Two panels: (a) ΔZ of the
      deposited film at the ground state of each stack (Fe-on-MgO island 3.65 Å vs MgO-on-Fe flat
      film 0.39 Å), against the 1.0 Å threshold; (b) where the flat film lies relative to the island
      for each stack (+0.189 / −0.016 eV/atom), so the sign of the wetting preference is visible.
      Open: whether to add the two ground-state structures as an inset.
- [ ] **`lattice_constraint.png` (new, §S5, SI-10).** Three panels: (a) separation vs the constraint
      with per-search scatter, (b) ΔZ distributions per arm, (c) per-search spread. Open: whether
      the main-text reference (f = 0) should be a distinct marker in (a) — it currently is the leftmost
      point — and whether the a_Fe difference (2.866 vs 2.87019 Å) should be annotated on the axis.
