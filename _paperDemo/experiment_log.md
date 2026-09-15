# Experiment Log — Wetting of Fe on MgO vs Fe-B/MgO

## Contribution (one sentence — DRAFT, pending scientist confirmation)
Boron insertion into the Fe deposition layer changes how Fe wets the MgO interface:
B makes the Fe film rougher, lifts it off the interface, and reduces its lateral
footprint, while B itself does not bond to MgO. This is relevant to MTJ stacks where
B diffusion and interface flatness govern performance.

## Data
- `data/femgo/` — Fe25Mg25O25 on MgO(001), 13 seeds, 1297 AGOX candidates.
- `data/febmgo/` — B3Fe25Mg25O25 on MgO(001), 7 seeds, 597 candidates.
- Structure source: `data/{sys}/seed_*/1_db/db_*.db` (AGOX Database).
- Level of theory: GPAW LCAO/PBE, kpts (1,1,1), vacuum 20 Å (from main.py params).

## Analysis scripts
- `scripts/wetting_metrics.py` — per-structure wetting metrics; window = 3.0 eV above
  global min per system. Output: `analysis/wetting_metrics.csv` (187 rows: 136 femgo,
  51 febmgo).
- `scripts/wetting_significance.py` — Mann-Whitney U + Cohen's d between systems.
- `scripts/probe_struct.py` — geometry probe (deposit z-ranges, interface plane).

## Wetting-metric definitions
Interface plane z0 = max z of substrate Mg/O (=10.00 Å in both systems).
- `Fe_contact_frac`: fraction of Fe with an O atom within 2.6 Å (interfacial bonding).
- `Fe_roughness`: std of Fe z-positions (lower = flatter film = better wetting).
- `Fe_height_mean`: mean Fe z above interface.
- `fe_coverage`: fraction of lateral (x,y) grid (1.2 Å bins) covered by Fe within
  1.5 Å of the lowest-Fe plane (2D wetting footprint).
- `B_contact_frac`: fraction of B with an O atom within 2.6 Å.

## Key results (within 3 eV window; values = mean ± std across candidate structures)
| Metric | Fe/MgO (n=136) | Fe-B/MgO (n=51) | MW-U p | Cohen's d |
|--------|----------------|------------------|--------|-----------|
| Fe_contact_frac | 0.296 ± 0.058 | 0.278 ± 0.082 | 0.051 | +0.27 |
| Fe_roughness | 0.989 ± 0.056 | 1.103 ± 0.237 | 0.015 | −0.87 |
| Fe_height_mean | 3.342 ± 0.124 | 3.540 ± 0.386 | 0.009 | −0.87 |
| fe_coverage | 0.181 ± 0.104 | 0.143 ± 0.075 | 0.010 | +0.39 |
| B_contact_frac | — | 0.000 ± 0.000 | — | — |

## Interpretation
- **B roughens the Fe film** (p=0.015, large effect d=−0.87): roughness 0.99 → 1.10 Å.
- **B lifts Fe off the interface** (p=0.009): mean Fe height 3.34 → 3.54 Å.
- **B shrinks the Fe lateral footprint** (p=0.010): coverage 0.181 → 0.143.
- **B does not bond to MgO** (B_contact_frac = 0 in every windowed structure) — B
  sits within the Fe film (best structure: B at z≈14.1, mid-film), not at the interface.
- Fe–O contact fraction drops only marginally (p=0.051, small effect) — NOT a
  conclusive claim on its own.

## Figures
None generated yet. Candidate figures:
- `figures/wetting_boxplot.png` — boxplots of roughness / height / coverage, femgo vs febmgo.
- `figures/b_distribution.png` — B height distribution relative to interface (Febmgo).

## Caveats
- febmgo has fewer seeds (7) and windowed structures (51) than femgo (13 / 136).
- febmgo full energy range (240 eV) contains unphysical high-energy hits; windowing to
  3 eV is essential and is applied throughout.
- kpts=(1,1,1), single-layer slabs: qualitative/trend-level results only.

## Open questions / acknowledgments for the paper
- Confirm the operative mechanism: does B destabilize Fe/MgO bonding or Fe cohesion?
- MTJ relevance framing: B is a known PMA/interface-flatness dopant; tie metrics to that.
