# Experiment Log — Metal-film wetting on MgO: Fe vs Fe-Co, with/without B (MTJ)

## Contribution (one sentence — DRAFT, pending scientist confirmation)
Boron consistently lowers the relative energy of the flat metal-film wetting state on
MgO — by ~0.04 eV/atom — in both a pure-Fe host and a Fe-Co host, while Co alone has
little effect. B therefore promotes flat-film wetting character independently of the
host metal, relevant to interface flatness in CoFeB/MgO MTJ stacks.

## Context (search method)
- Runs are AGOX/**GOFEE** global optimization (GPR surrogate + LCB): a **biased**
  exploration seeded from a reference **flat** metal layer.
- **Three-phase biased exploration** (see `sections/01_methods.md` §1.2): Phase I
  (0 ≤ i < 10) small-scale generator N=20; Phase II (10 ≤ i < 25) small 10 + large 10;
  Phase III (25 ≤ i) large-scale N=20. Small = `HeteroStructRandomize` (rattle 1.5),
  large = `RattleGenerator` (rattle 2.3). Matches `num_candidates={0:[20,0],10:[10,10],25:[0,20]}`.
- Relaxation starts at **iteration 10**; only structures with **iteration >= 10** are used.

## Data inventory

**Main-text systems (4)** — the wetting / B-effect / Co-effect study:
| System | Composition | n (iter>=10) | seeds | cell z (Å) |
|--------|-------------|--------------|-------|-----------|
| femgo | Fe25Mg25O25 | 1180 | 13 | 20 |
| febmgo | B3Fe25Mg25O25 | 543 | 7 | 20 |
| fecomgo | Co7Fe18Mg25O25 | 355 | 5 | 41.5 |
| fecobmgo | B2Co7Fe18Mg25O25 | 330 | 4 | 41.5 |

**Supplementary datasets (all on Fe25Mg25O25 unless noted):**
| Dataset | What it varies | dirs | status |
|---------|----------------|------|--------|
| DOS/PDOS | electronic structure, flat vs island (+ Fe-B GS) | `dos_femgo_flatngs`, `dos_febmgo_gs` | SI |
| Rattle strength | rattle −0.5 / −1.0 vs baseline 1.5/2.3 | `param_ratt05`, `param_ratt1` | SI |
| Kappa (LCB) | kappa = 1 / 3 / 4 vs baseline 2 | `femgo_kappa/{1_k1,0_k3,2_k4}` | SI |
| Dipole correction | `dipolelayer: xy` on/off | `femgo_dip` | SI |

Note: SI analyses use the fuller `femgo` set including `stop_16` (n=1207, 14 seeds); the
main-text PES table above uses the 13 `seed_*` dirs (n=1180). Both consistent within their study.

Level of theory: GPAW LCAO/PBE, kpts (1,1,1), vacuum 20 Å. Data loaders must skip scratch
`trash/` dbs and filter to the target composition (see `femgo_kappa` Fe9Mg9O9 contamination).

## Metrics
- **ΔZ (flatness)** = z(metal_max) − z(metal_min) over ALL metal film atoms (Fe+Co)
  [Å]. ΔZ≈0 = flat film (wet); ΔZ large = island / 3D clustering (dewet).
- **dE/N (PES coordinate)** = (E_i − E_globalmin)/N_atoms [eV/atom], global min = 0,
  per system over the iteration>=10 set.
- **B_contact_frac** = fraction of B with an O within 2.6 Å.

## Key results (flat = ΔZ ≤ 1.0 Å)
| System | global-min ΔZ | mean ΔZ | flat frac | **flat-basin min dE/N** |
|--------|---------------|---------|-----------|--------------------------|
| Fe/MgO | 3.65 Å | 2.66 | 0.165 | **0.1888 eV/atom** |
| Fe-B/MgO | 3.77 Å | 2.25 | 0.208 | **0.1493 eV/atom** |
| Fe-Co/MgO | 2.75 Å | 2.01 | 0.214 | **0.1941 eV/atom** |
| Fe-Co-B/MgO | 3.45 Å | 2.03 | 0.242 | **0.1494 eV/atom** |

## 2×2 analysis (B effect × Co effect)
- **B effect, Fe host**: 0.1888 → 0.1493 (−0.040 eV/atom)
- **B effect, Fe-Co host**: 0.1941 → 0.1494 (−0.045 eV/atom)
- **Co effect, without B**: 0.1888 → 0.1941 (+0.005 eV/atom) — small
- **Co effect, with B**: 0.1493 → 0.1494 (+0.000 eV/atom) — negligible
→ **B lowers the flat-state relative energy robustly in both hosts; Co alone barely moves it.**

## Interpretation
- The lowest-energy structure found is an **island** in all four systems (ΔZ ≈ 2.8–3.8 Å);
  the **flat configuration is a distinct, higher-energy structural basin** (not proven
  metastable — see caveat below) — consistent with the biased search seeded from a flat layer.
- **B brings the flat wetting state closer to the lowest-energy state in both hosts**
  (≈ −0.04 eV/atom).
- **B increases the flat fraction** sampled in both hosts (0.165→0.208; 0.214→0.242).
- **B does not bond to MgO** (B stays in the film).
- **Co alone** has little effect on the flat-state energy.

**Language note:** the flat state is described as a "higher-energy flat basin" /
"lowest-energy state", NOT as "metastable". Metastability is not established (see caveats).

## Supplementary Material: PDOS — origin of island formation (flat vs island)

**Status: SUPPLEMENTARY (SI).** The electronic-structure analysis of the flat→island
transition, reported as supporting material (also the site-resolved / registry subsection
below).

**Data** (femgo DOS runs, same orbital projections → directly comparable):
- FLAT reference: `data/dos_femgo_flatngs/dos_seed_4.csv` (4.xsf, ΔZ = 0.000 Å)
- ISLAND ground state: `data/dos_femgo_flatngs/dos_seed_3.csv` (3.xsf, ΔZ = 3.652 Å)
- GPAW LCAO/dzp, PBE, kpts (12,12,1), npts 2000, width 0.15 eV, Fermi-shifted.
- Projections: Fe `dz2` (l=2, m=2), O `pz` (l=1, m=0), per atom.

**Metrics** (analysis/pdos_metrics.csv; d-band moments over [-5, +3] eV around E_F):
| Quantity | FLAT | ISLAND | Δ (island − flat) |
|----------|------|--------|-------------------|
| d-band centre | −0.229 eV | +0.601 eV | **+0.83 eV (up)** |
| d-band width | 1.417 eV | 1.314 eV | −0.10 (narrower) |
| Fe-dz2 integral | 31.71 | 33.88 | +2.16 (more filled) |
| O-pz integral | 43.88 | 42.37 | −1.51 (less O-p) |
| spin polarization | 5.81 | 4.37 | −1.44 (less magnetic) |
| DOS at E_F | 104.0 | 78.1 | −25.9 (−25%) |

**Interpretation (origin of the island):**
- Going flat → island, the **Fe d-band centre rises by +0.83 eV** and the **O-pz weight
  drops** — i.e. **Fe–O hybridization is REDUCED** in the island. The flat layer, held in
  registry with MgO (3.77% lattice strain), has more Fe–O orbital mixing (lower d-centre,
  higher O-p involvement); the island relaxes away from that coupling toward more bulk-like,
  more metallic Fe-d character.
- The **d-band narrows** slightly and **Fe-dz2 occupation increases** — consistent with a
  more localized, bulk-like Fe-d manifold in the island.
- **Spin polarization falls** (5.81 → 4.37) and **DOS(E_F) drops ~25%** — the flat layer
  is the more magnetically/electronically "hot" configuration (higher DOS at E_F), while
  the island is electronically quieter.
- Net picture: the flat layer is strained and strongly coupled to MgO; the island relieves
  that coupling. The electronic fingerprint is a **d-band-centre upshift + reduced O-p
  hybridization + weakened spin polarization** on going flat → island.
- **Caveat:** DOS alone gives no total energy — the energy ordering (island lower by
  ~14 eV/cell) comes from the AGOX search energies, and this PDOS is a single-point
  electronic structure on those (non-converged) geometries. `[VERIFY]` any quantitative
  claim on re-relaxed geometries.

### [SI] Interface Fe: true contact group + Fe-on-O registry

Grouping corrected from the earlier arbitrary bottom-8/top-8 split to a **geometric
interface criterion**: interface Fe = Fe with a **nearest O within 2.8 Å** (actually in
contact with MgO). Registry: is each interface Fe's in-plane nearest substrate atom O or Mg?

| Structure | interface Fe (d_Fe-O < 2.8 Å) | atop O | atop Mg | mean in-plane offset | mean d_Fe-O |
|-----------|-------------------------------|--------|---------|----------------------|-------------|
| FLAT | **25 / 25** | 25 | 0 | **0.000 Å** | 2.300 Å |
| ISLAND | **9 / 25** | 9 | 0 | 0.372 Å | 2.331 Å |

**Registry result — Fe sits directly ATOP oxygen.** Every in-contact Fe — 25/25 in the flat
monolayer, 9/9 in the island — has O as its in-plane nearest substrate atom, and **zero**
sit atop Mg. In the flat layer the registry is perfect (offset = 0.000 Å). This is the
expected Fe/MgO(001) geometry, and the physics is straightforward: the **Fe–O bond is far
stronger than Fe–Mg** (O is the electronegative, reactive species; Fe–Mg is a weak
metallic interaction). The interface therefore maximises Fe–O orbital overlap, which is
exactly the hybridisation seen in the d-band shift.

**PDOS by corrected group** (Fe-dz2, d-band moments over [−5, +3] eV):
| Group | n | d-band centre | width |
|-------|---|---------------|-------|
| FLAT: interface (= all) | 25 | **−0.229 eV** | 1.417 |
| ISLAND: interface (d_Fe-O < 2.8 Å) | 9 | **+0.511 eV** | 1.516 |
| ISLAND: non-interface | 16 | +0.652 eV | 1.181 |
| ISLAND: all | 25 | +0.601 eV | 1.314 |

**Result (unchanged conclusion, now on a rigorous grouping):** the island's *true* interface
Fe (d-centre +0.511 eV) are still **NOT flat-like** (−0.229 eV), even though their mean
Fe–O distance (2.331 Å) is essentially the same as the flat layer's (2.300 Å) and they too
sit atop O. So the flat layer's strong hybridisation is **not** a per-bond distance effect —
it is a **collective** effect of all 25 Fe being registry-locked in one plane (25 Fe–O
contacts, uniform environment), whereas the island brings only 9 Fe into O contact and
those sit in a buckled, non-uniform cluster.

**Refined island-origin picture:** the flat monolayer is uniquely strongly Fe–O coupled
because *every* Fe is registry-locked atop O — at the cost of 3.77% lattice strain. The
island abandons the registry, cutting Fe–O contacts from 25 → 9 and dropping the coupling
for all Fe (d-centre → ~+0.5–0.6 eV, bulk-like). The island's energy gain (~14 eV/cell
from the search) is therefore dominated by **strain relief / Fe cohesion**, not by any
interfacial re-hybridisation.

## Supplementary Material: Method-parameter sensitivity

**Status: SUPPLEMENTARY (SI).** The search is a **custom, biased-exploration scheme**:
GOFEE (GPR surrogate + LCB) seeded from a **flat Fe** reference, with
`HeteroStructRandomize` + `RattleGenerator` controlling the perturbation. This SI varies
**three method parameters** on the same Fe₂₅Mg₂₅O₂₅ system and checks whether the method's
conclusion (island ground state; ~0.05 eV/atom per-seed reach; flat/island basin picture)
**survives** the parameter choice, and which setting performs best.

Common baseline for every family: plain `femgo` (rattle 1.5/2.3, kappa=2, no dipole).
Overall reference minimum: −436.909 eV. Metrics are **per-seed** (seed counts differ).
Figures: `figures/method_sensitivity_{rattle,kappa,dipole}.png`;
data: `analysis/method_sensitivity.csv`. Supersedes the earlier standalone rattle figure.

### SI-1. Rattle strength

| Setting | HeteroStruct / Rattle | seeds | per-seed best ΔE/atom | flat fraction | diversity |
|---------|----------------------|-------|-----------------------|---------------|-----------|
| baseline (`femgo`) | 1.5 / 2.3 | 14 | **0.050 ± 0.055** | **0.181** | 2.52 |
| reduced-0.5 (`param_ratt05`) | 1.0 / 1.8 | 4 | 0.290 ± 0.057 | 0.030 | 3.71 |
| reduced-1.0 (`param_ratt1`) | 0.5 / 1.3 | 5 | 0.274 ± 0.124 | 0.015 | 4.33 |

- **Reducing rattle degrades the search ~5×** (0.050 → 0.27–0.29 eV/atom per seed). The
  baseline rattle is important for escaping into the low-energy basin; **more, not less,
  perturbation is needed** here.
- Reduced rattle **under-samples the flat basin** (0.181 → 0.030 → 0.015).
- Diversity moves the opposite way (2.5 → 3.7 → 4.3) only because the baseline population
  is more *concentrated* (better converged) — not a clean exploration measure.

### SI-2. Kappa (LCB acquisition parameter)

| Setting | kappa | seeds | per-seed best ΔE/atom | flat fraction | diversity |
|---------|-------|-------|-----------------------|---------------|-----------|
| baseline | 2 | 14 | 0.050 ± 0.055 | 0.181 | 2.52 |
| `1_k1` | 1 | 16 | **0.039 ± 0.024** | 0.182 | 2.36 |
| `0_k3` | 3 | 11 | 0.055 ± 0.066 | 0.159 | 2.68 |
| `2_k4` | 4 | 10 | 0.056 ± 0.075 | 0.134 | 2.67 |

- **Kappa barely matters.** All settings land within 0.039–0.056 eV/atom — the method's
  conclusion is **robust** across kappa ∈ {1,2,3,4}.
- **Best: kappa = 1** (lowest and most consistent per-seed best, 0.039 ± 0.024).
- Higher kappa (more exploration relative to exploitation) is marginally worse and samples
  **less of the flat basin** (0.182 → 0.159 → 0.134).

### SI-3. Dipole correction (`poissonsolver={"dipolelayer": "xy"}`)

| Setting | seeds | per-seed best ΔE/atom | flat fraction | diversity |
|---------|-------|-----------------------|---------------|-----------|
| no dipole (baseline) | 14 | 0.050 ± 0.055 | 0.181 | 2.52 |
| dipole xy (`femgo_dip`) | 12 | 0.056 ± 0.066 | 0.160 | 2.63 |

- **Negligible effect** — the dipole correction does not change the outcome (per-seed best
  0.050 → 0.056, within the seed-to-seed spread; flat fraction 0.181 → 0.160).
- **Caveat:** the two runs are **separate searches**, so the difference mixes the correction
  with sampling noise. This is an outcome-level comparison only; isolating the true dipole
  energy shift would require recomputing the *same* structures with/without the correction.

### SI caveats (all three families)

- Seed counts unequal (rattle 14/4/5; kappa 14/16/11/10; dipole 14/12).
- The rattle sweep explores only *lower* rattle (no higher-rattle variant).
- "Diversity" (mean pairwise AGOX-Fingerprint distance) is **inversely correlated with
  convergence** and is not interpreted as exploration breadth.
- Kappa dirs contain a scratch `trash/` db with 41 Fe₉Mg₉O₉ structures — **excluded** in the
  loader (`load_setting` skips `trash/` and filters to Fe₂₅Mg₂₅O₂₅). The rattle/dipole dirs
  are clean.

## Figures
- `figures/pes_four_systems.png` — 2×2 PES maps (dE/N vs ΔZ).
- `figures/flat_state_summary.png` — flat-basin vs lowest-energy comparison (2×2 design).
- `figures/flat_vs_ground_preview.png` — side views, flat vs lowest-energy (4 systems).
- `figures/pdos_flat_vs_island.png` — **[SI]** PDOS (total / Fe-dz2 / O-pz) flat vs island.
- `figures/pdos_sites.png` — **[SI]** Fe site-resolved PDOS, bottom-8/top-8 split (SUPERSEDED by interface_analysis).
- `figures/interface_registry_topview.png` — **[SI]** top view: Fe atop O on the MgO(001) lattice.
- `figures/method_sensitivity_rattle.png` — **[SI]** rattle-strength sensitivity (4 panels).
- `figures/method_sensitivity_kappa.png` — **[SI]** kappa (LCB) sensitivity (4 panels).
- `figures/method_sensitivity_dipole.png` — **[SI]** dipole-correction sensitivity (4 panels).
- `figures/rattle_analysis.png` — **[SI]** superseded by the method_sensitivity figures.
- `figures/wetting_metrics.png` — 4-panel wetting-metric boxplot (SUPERSEDED, early analysis).
- `analysis/flat_structures/{system}_flat_min.xsf` — inspectable flat structures.
- `analysis/flat_structures/{system}_ground_min.xsf` — inspectable lowest-energy structures.

## Drafting & citations status
- **Phase A:** DONE — contribution + claim list signed off (`CLAIMS.md` v1, 2026-09-16).
- **Phase D:** 6 citations verified in `references.bib` (agox2020, gofee2017, oganov2011,
  gpaw2014, pbe1996, greer1993). 3 MTJ placeholders still UNVERIFIED in `03_discussion.md`.
- **Phase E:** `01_methods.md` APPROVED · `02_results.md` APPROVED ·
  `03_discussion.md` drafted v2 (awaiting review; §3.2 includes the Greer confusion principle).
  Block-and-wait before `04_introduction.md`.
- **Phase F/G:** not started.
- Reference PDFs: `papers/confusion_greer1993.pdf` (Greer, Nature 366, 303, 1993 → `greer1993`).

## Caveats
- **Relaxation is NOT DFT-converged.** Candidates are relaxed by the **GPR surrogate**
  (ParallelRelaxPostprocess, 100 steps, start_relax=10) and then evaluated with only
  **1 GPAW step** (`optimizer_run_kwargs={"fmax": 0.05, "steps": 1}`). The exported
  structures carry residual DFT forces of ~1–2 eV/Å (max |F| 1.0–2.4 eV/Å) — they are
  **not** at DFT local minima. "Lowest-energy state"/"basin" therefore mean "lowest DFT
  energy found", not a converged minimum. Establishing true minima/metastability needs a
  full DFT re-relaxation (see `relaxation/`).
- ΔZ ≤ 1.0 Å flat cutoff is a chosen threshold (valley visually distinct).
- Seed counts differ (femgo 13, febmgo 7, fecomgo 5, fecobmgo 4); Co systems have fewer samples.
- febmgo/fecobmgo full energy ranges contain unphysical high-energy hits; excluded by the
  iteration filter + per-system global-min normalization.
- kpts=(1,1,1), single-layer slabs: qualitative/trend-level results only.
