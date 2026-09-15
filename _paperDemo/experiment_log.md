# Experiment Log — Wetting of Fe on MgO vs Fe-B/MgO

## Contribution (one sentence — DRAFT, pending scientist confirmation)
Boron insertion into the Fe deposition layer roughens the Fe film and lifts it off the
MgO interface, while B itself does not bond to MgO (stays within the Fe film) — relevant
to interface flatness and B segregation in MTJ stacks.

## Data
- `data/femgo/` — Fe25Mg25O25 on MgO(001), 13 seeds, 1297 AGOX candidates.
- `data/febmgo/` — B3Fe25Mg25O25 on MgO(001), 7 seeds, 597 candidates.
- Structure source: `data/{sys}/seed_*/1_db/db_*.db` (AGOX Database).
- Level of theory: GPAW LCAO/PBE, kpts (1,1,1), vacuum 20 Å (from main.py params).

## Analysis scripts
- `scripts/wetting_metrics.py` — per-structure wetting metrics; selection window =
  **relative energy per atom** `dE/N = (E_i - E_globalmin)/N_atoms`, global min = 0 eV/atom,
  per system, default `--e-window-per-atom 0.05`. Output: `analysis/wetting_metrics.csv`
  (280 rows: 208 femgo, 72 febmgo).
- `scripts/wetting_significance.py` — Mann-Whitney U + Cohen's d between systems.
- `scripts/probe_struct.py` — geometry probe (deposit z-ranges, interface plane).
- `scripts/plot_wetting_figure.py` — 4-panel boxplot figure.

Note: the runs are AGOX **GOFEE** global-optimization searches (GPR surrogate + LCB
acquisition). The reference energy is the system's global-minimum structure.

## Wetting-metric definitions
Interface plane z0 = max z of substrate Mg/O (=10.00 Å in both systems).
- `Fe_contact_frac`: fraction of Fe with an O atom within 2.6 Å (interfacial bonding).
- `Fe_roughness`: std of Fe z-positions (lower = flatter film = better wetting).
- `Fe_height_mean`: mean Fe z above interface.
- `fe_coverage`: fraction of lateral (x,y) grid (1.2 Å bins) covered by Fe within
  1.5 Å of the lowest-Fe plane (2D wetting footprint).
- `B_contact_frac`: fraction of B with an O atom within 2.6 Å.

## Key results (within 0.05 eV/atom window; values = mean ± std across candidate structures)
| Metric | Fe/MgO (n=208) | Fe-B/MgO (n=72) | MW-U p | Cohen's d |
|--------|----------------|------------------|--------|-----------|
| Fe_roughness | 1.015 ± 0.096 | 1.104 ± 0.227 | 0.015 | −0.63 |
| Fe_height_mean | 3.387 ± 0.175 | 3.569 ± 0.378 | 0.001 | −0.75 |
| fe_coverage | 0.152 ± 0.099 | 0.147 ± 0.074 | 0.967 | +0.05 |
| Fe_contact_frac | 0.284 ± 0.062 | 0.272 ± 0.084 | 0.106 | +0.17 |
| B_contact_frac | — | 0.005 ± 0.039 | — | — |

## Interpretation
- **B roughens the Fe film** (p=0.015, d=−0.63): roughness 1.02 → 1.10 Å.
- **B lifts Fe off the interface** (p=0.001, d=−0.75): mean Fe height 3.39 → 3.57 Å.
- **B does NOT change lateral coverage** (p=0.967) — the coverage claim is NOT supported
  under the per-atom window (was significant under the looser absolute window; dropped out).
- **B does not bond to MgO**: B_contact_frac ≈ 0 (one of 72 structures shows a single
  B–O contact within 2.6 Å) — B stays essentially inside the Fe film.
- Fe–O contact fraction difference is NOT significant (p=0.106) — do not claim.

## Caveats
- febmgo has fewer seeds (7) and windowed structures (72) than femgo (13 / 208).
- febmgo full energy range (240 eV) contains unphysical high-energy hits; the 0.05 eV/atom
  window excludes them.
- kpts=(1,1,1), single-layer slabs: qualitative/trend-level results only.
- Changing the energy window changes which structures are included and thus the
  wetting-metric means; the robust claims are roughness and height. Coverage was sensitive
  to the window choice and is NOT a robust claim.

## Open questions / acknowledgments for the paper
- Confirm the operative mechanism: does B destabilize Fe/MgO bonding or Fe cohesion?
- MTJ relevance framing: B is a known PMA/interface-flatness dopant; tie metrics to that.
