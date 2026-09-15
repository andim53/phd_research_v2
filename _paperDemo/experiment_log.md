# Experiment Log — Wetting of Fe on MgO vs Fe-B/MgO (PES / flat-vs-island)

## Contribution (one sentence — DRAFT, pending scientist confirmation)
Boron insertion lowers the relative energy of the flat Fe wetting state on MgO,
bringing it closer to the island ground state — i.e. B promotes flat-Fe wetting
character, relevant to interface flatness in MTJ stacks.

## Context (search method — important for interpretation)
- Runs are AGOX/**GOFEE** global optimization (GPR surrogate + LCB acquisition):
  a **biased exploration**, not unbiased sampling.
- The search **starts from a reference FLAT Fe layer** (HeteroStructRandomize,
  `generate_pristine=False`), so the database samples a mixture of basins.
- Relaxation starts at **iteration 10**; only structures with **iteration >= 10** are
  used (iterations 1–9 are pre-relaxation placements, excluded).

## Data
- `data/femgo/` — Fe25Mg25O25 on MgO(001), 13 seeds. `data/febmgo/` — B3Fe25Mg25O25, 7 seeds.
- After the iteration>=10 filter: femgo n=1180, febmgo n=543.
- Level of theory: GPAW LCAO/PBE, kpts (1,1,1), vacuum 20 Å.

## Metrics
- **dZ (flatness)** = z(Fe_max) − z(Fe_min) over all Fe atoms [Å]. dZ≈0 = flat Fe
  interface (good wetting); dZ large = island / 3D Fe clustering (dewetting).
- **dE/N (PES coordinate)** = (E_i − E_globalmin)/N_atoms [eV/atom], global min = 0,
  computed **per system** over the iteration>=10 set.
- **B_contact_frac** = fraction of B with an O within 2.6 Å.

## Key results
| Quantity | Fe/MgO | Fe-B/MgO |
|----------|--------|----------|
| n (iteration>=10) | 1180 | 543 |
| global-min ΔZ (Å) | 3.65 | 3.77 |
| mean ΔZ (Å) | 2.66 | 2.25 |
| flat fraction (ΔZ≤1.0 Å) | 0.165 | 0.208 |
| **flat-basin min dE/N (eV/atom)** | **0.1888** | **0.1493** |
| flat-basin min ΔZ (Å) | 0.90 | 0.33 |

## Interpretation
- **The ground state is an ISLAND in both systems** (global min at ΔZ ≈ 3.7 Å), not flat.
  Flat Fe is a metastable state — consistent with the biased search starting from flat Fe.
- **B lowers the flat-basin relative energy**: 0.1888 → 0.1493 eV/atom (a drop of
  ~0.04 eV/atom). B brings the flat wetting state **closer to the ground state**.
- **B increases the flat fraction** of sampled structures (0.165 → 0.208).
- **B does not bond to MgO** (B stays in the Fe film; earlier per-structure analysis).
- Consistent with prior pooled analysis: B's effect is on the Fe layer's flatness/energy
  landscape, not on direct B–O bonding.

## Figures
- `figures/pes_flat_island.png` — PES map (dE/N vs ΔZ) per system + flat-basin
  ground-state comparison bar.

## Caveats
- The ΔZ≤1.0 Å "flat" cutoff is a chosen threshold; the flat basin is visibly distinct
  (sharp peak at ΔZ≈0–0.3) so the separation is robust, but the exact boundary is a choice.
- febmgo has fewer seeds (7) than femgo (13); its flat-basin value comes from fewer samples.
- kpts=(1,1,1), single-layer slabs: qualitative/trend-level results only.
- Global minima reported are the best found by the (biased) search, not guaranteed true
  global minima.
