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
  `03_discussion.md` revised to v3 (2026-09-17, awaiting review): the §3.2 confusion-principle
  claim is now restricted to the B addition (Co alone raises the flat energy, so element count
  is not the driver), the unsupported "bulk-like" d-centre comparison was removed, and the
  unequal-seed-count limitation was added to §3.5. Block-and-wait before `04_introduction.md`.
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

## Ensemble / motif investigation (2026-09-17) — `scripts/ensemble_analysis.py` v1.0.0

**Motivation.** The main-text claims rest on two hand-picked structures (single flat-basin
minimum, single island global minimum). Both PES branches are in fact ensembles: islands of
many heights (ΔZ 1.0–6.1 Å, no clean height quantisation) and many flat arrangements
differing only in where B/Co sits.

**Script.** `scripts/ensemble_analysis.py` (agox_v2). Rebuilds `analysis/pes_structures.csv`
(reproduces the existing file numerically exactly — max |Δ| = 0.0 — and the frozen values
0.1888 / 0.1493 / 0.1941 / 0.1494), inventories replicas, describes each branch as a
distribution, and runs a motif test. Outputs `analysis/ensemble_stats.json` (self-describing)
and `analysis/pes_structures_with_partial.csv`.

**1. Replica inventory (corrects the docs).**
| system | replica dirs | with data | note |
|---|---|---|---|
| femgo | 14 | 13 | + `stop_16` partial run (36 candidates / 27 at iter≥10) |
| febmgo | 7 | **6** | `seed_6/1_db/db_6.db` is EMPTY (0 candidates) — "7 seeds" was wrong |
| fecomgo | 5 | 5 | `seed_4` holds only 1 structure at iter≥10 |
| fecobmgo | 4 | 4 | `seed_3` truncated (max iter 73) |

**2. Dataset-definition inconsistency.** `method_sensitivity.py` globs
`data/<system>/**/*.db` (recursive → includes `stop_*`); `pes_analysis.py` globs
`seed_*/` only. The same "femgo baseline" is therefore described two ways:
main text **1180 structures / 13 replicas / flat fraction 0.165** vs SI baseline
**1207 / 14 / 0.181**. Including `stop_16` leaves the flat minimum unchanged (0.1888) but
raises the flat fraction 0.165 → 0.181. One definition must be chosen (see Paper status).

**3. Branch distributions (per-replica flat minima — the independent unit).**
| system | replicas | per-replica flat min, median (sd) | structures within +0.02 of the flat min |
|---|---|---|---|
| Fe | 13 | 0.2185 (0.021) | 5 |
| Fe-B | 6 | 0.1834 (0.037) | 4 |
| Fe-Co | 5 | 0.2086 (0.026) | 10 |
| Fe-Co-B | 4 | 0.1766 (0.118) | 3 |
Every replica independently reaches the low-flat window, so the flat minimum is NOT one
seed's accident — but the per-replica spread overlaps between systems.

**4. Motif test** (AGOX global Fingerprint = radial+angular distribution functions, invariant
under permutation/translation/rotation; "same motif" calibrated against the branch's
random-pair distance scale). Low-energy sets are only 1.4–2.4× tighter than random pairs
(ratio 0.32–0.72) and split into 2–4 (flat) / 1–3 (island) single-linkage clusters — they do
not collapse to one structure. However, the lowest flat structures do favour a recurring
motif: femgo's 5 lowest flat structures (from 5 different replicas) fall into 2 clusters, with
4 replicas in the dominant one. **Caveat:** the descriptor is computed on the whole
template+film slab, so the 50 fixed MgO atoms dominate and compress all distances; a
film-resolved descriptor/RMSD would be sharper.

**5. Statistical power — the real vulnerability.** Effects as shifts of the flat branch,
resampling replicas (the independent unit), permutation test on per-replica minima:
| comparison | per-replica min A vs B | min-of-min shift | perm-p |
|---|---|---|---|
| B in Fe host (Fe vs Fe-B) | 0.2171 vs 0.1882 | **+0.0395** | **0.005** |
| B in Fe-Co host (Fe-Co vs Fe-Co-B) | 0.2140 vs 0.2257 | **+0.0447** | **0.744** |
| Co alone (Fe vs Fe-Co) | 0.2171 vs 0.2140 | −0.0053 | 0.726 |
MT-3 (B lowers the flat energy in the Fe host) survives replica-level resampling
(p = 0.005). MT-5 (Co alone has little effect) is confirmed (p = 0.73, shift ≈ 0).
**MT-4 (B in the Fe-Co host) is NOT statistically resolvable** at 5 vs 4 replicas (p = 0.74;
median shift CI95 spans zero, driven by one Fe-Co-B replica whose flat minimum is 0.400).

## Core-framing revision (2026-09-17) — MT-6 WITHDRAWN (CLAIMS v1 → v2)

**Revised core (scientist-confirmed).** The subject is the **wetting of Fe on MgO** (the
property that matters for MTJ stacks). Co, B and CoB are **not the subject but the parameter
series** — a three-arm perturbation of the Fe reference. The system is a degenerate,
island-forming, amorphous-like one that converged/conventional approaches cannot address
directly, so we **design a biased exploration**: a global optimiser (GOFEE, built to find the
global minimum) seeded from a **flat reference**, so both phases of interest — flat (wetting)
and island (dewetting) — are guaranteed to be represented. What is returned is therefore **not
a thermodynamic density of states but an exploration density** — a sampling map over the two
phases — and because it is biased the **weights are not physically usable**. The legitimate
evidence is the map itself plus the phase-resolved comparison: for each of the two phases, how
do Co, B and CoB shift things relative to pure Fe? The biased search is the **instrument**, not
a limitation, and "we seeded toward flat yet GOFEE still found the island" is a **positive
control**, not a caveat.

**Why MT-6 was withdrawn.** MT-6 ("B increases the fraction of flat-basin structures sampled",
0.165 → 0.208; 0.214 → 0.242) is a *weight* of a biased exploration, and a cross-system
comparison of weights additionally requires a **fixed exploration operator**. It is not fixed.
Verified from the run scripts:

| system | generators | `num_candidates` schedule |
|---|---|---|
| femgo (`data/femgo/main.py:55`) | HeteroStructRandomize (1.5) + RattleGenerator (2.3) | `{0:[20,0], 10:[10,10], 25:[0,20]}` |
| febmgo (`:70`) | same two | same |
| fecobmgo (`:78`) | same two | same |
| **fecomgo** (`:75, 172–175`) | **three** — the two above **plus `PermutationGenerator`** (`max_number_of_swaps=n_rattle`, `rattle_strength=0.3`) | `{0:[20,0,0], 10:[10,5,5], 25:[0,10,10]}` |

Phase totals are equal (20 per phase) but Fe-Co spends half its large-scale budget (10 of 20)
on permutation in phases II–III, an operator the other three systems do not have. The **flat
reference** also differs in kind across systems: pure Fe layer (femgo), Fe layer + B
(`febmgo`), **randomised Fe/Co layer** via `feco_randamize_generater` (`fecomgo:125`,
`fecobmgo:134`), plus `add_adsorbate_to_hollows` for B placement (`febmgo:125`,
`fecobmgo:147`) and `remove_random_atoms_by_species` for composition control. So "the flat
reference" ranges from a pure ordered layer to a configurationally random alloy layer.

**Consequence:** MT-6 is not restated, it is removed, and it moves to the CLAIMS "NOT claimed"
table with this reason. `sections/03_discussion.md` §3.2 has had its flat-fraction clause
struck. **SI-7 retains the flat fraction legitimately** — it compares one system against itself
under a changed method parameter (rattle strength), which is exactly what a sampling density is
for; it is not a cross-system population claim.

**Corrections applied:** `sections/01_methods.md:95` seed count 7 → 6 (Fe-B; `seed_6`'s db is
empty). **Still open:** `sections/02_results.md:36–38,58` (approved) still reports the
withdrawn MT-6 flat-fraction comparison and needs sign-off to edit; `sections/01_methods.md`
§1.2 (lines 34–45) still presents the two-generator schedule as common to all four models,
which is inaccurate for Fe-Co.

## Results reconstruction (2026-09-17) — 02_results.md v2, organized by phase

`sections/02_results.md` rewritten under the revised core framing. Previous structure was
single-lever (island GS → B lowers flat → Co minor → B not bonding); the new structure is
**by phase**:

- **§2.1 The two-phase landscape.** The design stated as the deliverable: a GOFEE search seeded
  from a flat reference yields a sampled ΔZ–energy distribution ("an *exploration* density, not
  a thermodynamic density of states"), with the caveat that only unweighted structural and
  energetic comparisons are used and basin counts are descriptive attributes. Table 1 gives
  n / island / flat / global-min ΔZ / flat-basin min for the four models. **MT-1 is reframed as
  a positive control**: every search was seeded from a flat reference and perturbed only at
  small scale in the early phases, yet the global minimum is an island in all four models — so
  the flat bias did not manufacture the result. MT-2 unchanged (flat is a distinct,
  higher-energy basin, 0.149–0.194 eV/atom). New: the branches are families of structures, not
  single configurations.
- **§2.2 The flat (wetting) phase under Co, B and CoB.** MT-3 (−0.040), MT-4 (−0.045), MT-5
  (+0.005) and MT-7, the last now stated with its energy window made explicit and verified:
  within dE/N ≤ 0.05 eV/atom, 1 of 72 Fe-B and 1 of 21 Fe-Co-B structures has any B–O contact
  (max contact fraction 0.33 and 0.5). Across *all* structures the picture is different
  (102/543 Fe-B structures have some B–O contact), so the window is essential to the claim.
- **§2.3 The island phase and the separation between phases.** The parameter series leaves the
  island phase qualitatively similar (ΔZ ≈ 1–6 Å in every model; global-min ΔZ 2.75–3.77 Å);
  what B changes is the **flat–island separation**, since each model is referenced to its own
  minimum. States explicitly that the data do not resolve whether B stabilises the flat phase or
  destabilises the island.
- **§2.4 Summary**, reflecting the two-phase framing.

**Withdrawn MT-6 has been removed** — no flat-fraction comparison remains in the section.

**Two [NEW]/[PENDING] blocks need sign-off** (not covered by CLAIMS v2):
(a) §2.1 "branches are families, not single structures" — continuous ΔZ and 1–3 recurring
motifs per branch (from `analysis/ensemble_stats.json`); needs a CLAIMS v3 claim or should move
wholly to the SI. (b) §2.2 "[PENDING SIGN-OFF] Uncertainty of the B effect at the level of
independent searches" — Fe host +0.040 (p = 0.005, 13 vs 6 searches), Fe-Co host +0.045
(**p = 0.74**, 5 vs 4), Co alone −0.005 (p = 0.73). This **challenges MT-4's "strong" rating in
CLAIMS v2**. (c) §2.3's phase-separation wording is already the §3.2 interpretation but is not
in CLAIMS.

Because an approved section was rewritten, `02_results.md` is marked as **awaiting
re-approval** in `paper_status.md`.

## CLAIMS v3 (2026-09-17) — MT-8 added, MT-4 flagged, framing recorded

Scientist decisions on the three items flagged in the reconstructed Results:

1. **"Branches are families" kept in the main text as a result → `MT-8` added.**
   *The low-energy structures of each branch form a small set of recurring motifs rather than
   one repeated structure; ΔZ is continuous, with no discrete island heights.* Value: island
   branch ΔZ ≈ 1–6 Å with no quantisation; low-energy sets split into 1–3 single-linkage motifs
   (flat 2/2/3/2, island 2/2/3/1 for Fe / Fe-B / Fe-Co / Fe-Co-B); within-set fingerprint
   distance 0.32–0.72 × the branch's random-pair scale; Fe/MgO's five lowest flat structures
   (five independent searches) fall into two motifs, four in the dominant one. Source:
   `analysis/ensemble_stats.json`. Confidence: **moderate**, with a **paired caveat** that must
   travel with the claim — the AGOX global fingerprint is computed on the whole template+film
   structure, so the 50-atom MgO template dominates and compresses all distances, making the
   motif count a *lower bound* on structural diversity. A film-resolved descriptor would be
   sharper.
2. **`MT-4` flagged CHALLENGED — pending more searches.** Value unchanged (0.1941 → 0.1494),
   but the replica-resampled permutation test gives p = 0.74 at 5 vs 4 searches, versus
   p = 0.005 for MT-3 at 13 vs 6. MT-4 is reported in the Results as a *trend* of the same size
   as MT-3. The confidence rating is deliberately **not** downgraded in v3; the agreed resolution
   is to run more Fe-Co / Fe-Co-B searches.
3. **Phase-separation wording → added to CLAIMS' *Discussion-only interpretations*.** Boron is
   described as changing the flat–island separation, not as stabilising the flat phase or
   destabilising the island, because each model is referenced to its own minimum.

**Also recorded in v3's *Method & scope*:** the governing epistemic principle — the biased
search returns an *exploration* density, not a thermodynamic density of states, so basin weights
are not physical and only unweighted structural/energetic comparisons are admissible; plus the
positive-control framing of MT-1 (the island is the ground state despite the flat bias).

**Also updated in v3:** MT-3 and MT-5 now carry their replica-resampled p-values (0.005 and
0.73); MT-7's evidence cell now states the energy window explicitly
(`--e-window-per-atom 0.05`, i.e. dE/N ≤ 0.05 eV/atom → 1 of 72 Fe-B, 1 of 21 Fe-Co-B), because
outside that window 102 of 543 Fe-B structures do have a B–O contact.

**Sections updated to match:** `02_results.md` — inline `[NEW]`/`[PENDING SIGN-OFF]` markers
removed, MT-8 tagged in §2.1, MT-4 stated as a trend in §2.2, §2.3 wording left in place;
header now cites CLAIMS v3. `03_discussion.md` header now cites CLAIMS v3.

## 01_methods.md v3 RE-APPROVED (2026-09-17)

The scientist's second round of edits to `sections/01_methods.md` (committed as `52ff713` and
`34a8cd8`) is **approved as v3**:

- §1.1 — dropped the `pbc = [True, True, False]` flag and the matched MgO lattice constant
  (`a_MgO/√2 = 2.978 Å`) from the lattice-mismatch sentence. **Review note recorded and
  accepted:** the 3.77 % strain remains in the text while one of the two lattice constants it
  derives from is now absent; the scientist elected to keep it that way, since the value is
  recorded in `data/<system>/<replica>/0_result/latt_log.md` (`strain=3.77%`).
- §1.3 — removed the `dzp` code from "double-zeta polarised basis, `dzp`" → "double-zeta
  polarised basis".
- §1.6 — "A full re-relaxation of representative structures is prepared for this purpose" →
  "**is necessary** for this purpose". This now agrees with §3.5 (edited the same way earlier)
  and is the more honest reading: `relaxation/` holds 116 selected structures but has never
  been run.

**Status: `01_methods.md` is APPROVED (v3) and is the only fully approved section.**
`02_results.md` (reconstructed v2) awaits re-approval and `03_discussion.md` (v3) awaits its
first review.

## Supplementary Material: biased-exploration performance (2026-09-17)

New SI section drafted as **§S1 of `sections/SI.md`** (new file), using **Fe/MgO only** (13
searches) and **all iterations 1–100** — unlike the PES analysis, which keeps only i ≥ 10.
Script: `scripts/exploration_performance.py` v1.0.0. Outputs:
`analysis/exploration_performance.json` (self-describing), and
`figures/exploration_performance_femgo.png` — **[SI]** 3-panel figure: (a) best-so-far ΔE/N per
search + median, (b) lowest energy found per iteration and the best-known curve with threshold
crossings, (c) fraction of searches within 0.05 / 0.02 eV/atom of the global minimum.

**Measured behaviour (13 searches, 1297 candidates, global min = −436.909 eV at 75 atoms):**

| stage | best-known ΔE/N | share of total descent |
|---|---|---|
| i = 1 | 0.494 eV/atom | — |
| i = 9 (last pre-relaxation) | 0.435 | 12 % |
| **i = 10 (relaxation onset)** | **0.250** | **49 %** |
| i = 20 | 0.219 | 56 % |
| i = 30 | 0.078 | 84 % |
| i = 50 | 0.030 | 94 % |
| i = 77 (global minimum first found) | 0.000 | 100 % |

- **Pre-relaxation iterations barely descend**: 1–9 gives only 12 % of the descent, and most
  searches do not improve at all between i = 2 and i = 9 — unrelaxed placements cannot be ranked.
- **Relaxation onset is the single largest step**: 0.435 → 0.250 eV/atom in one iteration, about
  half the entire descent. Per-search drop across the onset: median 0.165, range 0.084–0.233.
- **Descent is front-loaded but the minimum arrives late**: 84 % done by i = 30, 94 % by i = 50;
  threshold crossings 0.20 @ i = 23, 0.10 @ i = 29, 0.05 @ i = 46, 0.02 @ i = 57, 0.005 @ i = 72;
  **global minimum at i = 77**.
- **Searches disagree about the answer**: only 10 / 13 end within 0.05 eV/atom and 4 / 13 within
  0.02; median final best 0.040 eV/atom (range 0.000–0.086); one search supplies the global
  minimum, a second comes within 0.001 eV/atom of it.

⚠ **The stated intent does not match the data.** The request was to show "how it finds the
lowest energy at very early iterations". For Fe/MgO that is **not** what happens: the global
minimum is found at iteration 77, and the pre-relaxation iterations produce no improvement at
all. What *is* true, and is the defensible version of the statement, is that (a) the largest
single energy drop occurs at the *earliest relaxed* iteration (i = 10) and (b) roughly half the
total descent is complete by then. The SI text is written to the data, not to the premise.

⚠ **New SI claim is NOT yet in CLAIMS** — needs a **CLAIMS v4** bump with an `SI-8` entry.
Candidate wording is in the `paper_status.md` claim table marked `[PENDING — needs CLAIMS v4]`.

⚠ **Limitation raised (needs a decision):** the searches are still improving at i = 100 (the
best-known energy falls to the last few iterations), so the per-model reference energies are not
converged with respect to search length. Every relative energy in the main text (MT-2 … MT-5)
therefore carries a systematic uncertainty that the replica-level statistics do not capture.

**Not visually inspected:** no image-viewing tool was available in the session that produced it,
so the figure was validated numerically (monotonicity of all running-best curves, pooled curve
reaching 0 at i = 77, plotted ranges vs axis limits) rather than by eye. It needs a human look.

### Follow-up (same day): §S1 reframed, SI-8 drafted

- **§S1 reframed around the relaxation-onset step**, per the scientist's decision. The "how early
  / how late" angle was dropped entirely; the section now runs pre-relaxation plateau → the onset
  step (the pivot) → the long refinement sequence → disagreement between searches. All facts are
  still reported (including the global minimum first reached at i = 77) but without an early/late
  narrative.
- **`SI-8` added to `CLAIMS.md` v4 (draft), awaiting sign-off.** Claim: *the onset of relaxation
  is the pivot of the biased search — the pre-relaxation iterations provide almost no ranking
  information, and roughly half the total descent occurs at the first relaxed iteration.* Paired
  caveat: Fe/MgO only; the quantities describe the search scheme, not any individual structure.
  v3 remains frozen; v4 becomes the frozen list once SI-8 is signed off.
- **Convergence-with-search-length limitation: HELD.** The scientist elected to discuss at review
  rather than write it into the limitations now; recorded in CLAIMS v4's changelog as explicitly
  not yet reflected.

## Fe/MgO experimental literature (2026-09-17) — one supplied paper contradicts the intended use

Three PDFs added by the scientist to `papers/`: `mgofe_urano1988.pdf`, `mgofe_butler2001.pdf`,
`mgofe_yuasa2004.pdf`. Intent: use them as **experimental validation that Fe deposited on MgO
forms islands**. The verification outcome changed the claim.

**Reading the papers.** Urano's scan had no text layer (`pdftotext` yielded only the 648-char
watermark), so it was OCR'd: `apt-get install tesseract-ocr` (5.3.4), then
`pdftoppm -r 300 -gray -png` + `tesseract` per page → 23 kB of usable text.

| Paper | Reports | Islanding? |
|---|---|---|
| **Urano & Kanaji**, JPSJ **57**, 3403 (1988) | *"Iron film deposited on a MgO(001) surface **grows layer by layer** and forms an epitaxial film at room temperature."* 1 ML pseudomorphic, **Fe just above O at ~2.0 Å**; bct → bcc at ≈10 Å | **No — the opposite** |
| **Butler et al.**, PRB **63**, 054416 (2001) | First-principles TMR; cites LEED for **Fe atop O**; Fe–O 2.169 Å (calc) / 2.0 Å (LEED) / 2.3 Å (FLAPW); ~3.5 % mismatch; *"only weak interactions between the electronic structures of Fe and MgO"* | Not a growth-mode paper |
| **Yuasa et al.**, Nat. Mater. **3**, 868 (2004) | Giant-TMR MBE MTJ; **flatness** of epitaxial Fe used as the quality criterion; RT top-Fe growth gives higher dislocation density than 200 °C | No — treats flat Fe as the benchmark |

The word "island" appears **nowhere** in Urano (grepped the full OCR). Two of the three papers
are about *flat* Fe.

**The islanding literature exists — located and verified.** `fahsold2000` (Fahsold, Pucci,
Rieder, PRB **61**, 8475 (2000), He-atom scattering): *"The observed **three-dimensional metal
island growth** behavior is suppressed at low temperature (140 K) where a monolayer film almost
completely covers the substrate."* This is the intended validation, **and it is at ≈1 ML
coverage** — so the scientist's "islanding at one monolayer" point is correct, just not
supported by the paper supplied for it. Second reference: `reitinger2007` (JAP **102**, 034310)
— Volmer–Weber at RT, but on **five** monolayers.

**Resolution — the two basins map onto two experimental outcomes.** RT deposition gives 3D
islands (`fahsold2000` ≈1 ML; `reitinger2007` 5 ML); a flat layer requires low temperature
(140 K) or slow deposition on a cleaved, oxygen-annealed crystal (`urano1988`). So our flat
basin ↔ the experimentally realised pseudomorphic monolayer, and our island basin ↔ the
experimentally observed 3D clusters. Framed as a correspondence between **structural
configurations, not energies**, since the growth mode is also kinetically set.
**Urano's layer-by-layer result at RT is the literature outlier, not ours.**

**What else the papers validate (and contradict):**
- **Supported:** Fe-atop-O registry (Urano's LEED I–V; Butler cites LEED for the same) ↔ our SI-4
  (25/25 flat, 9/9 island atop O, 0 atop Mg; flat in-plane offset 0.000 Å). Mismatch magnitude:
  Butler 3.5 % vs ours 3.77 %. Weak Fe–MgO coupling (Butler) consistent with our strain-relief
  island origin (SI-3).
- **Contradicted — Fe–O separation:** ours 2.300 Å (flat) / 2.331 Å (island), regenerated by
  re-running `scripts/interface_analysis.py`; Urano LEED ~2.0 Å, Butler calc 2.169 Å. Scientist's
  decision: **not** treated as a discrepancy — 2.3 Å is the value Butler cites from the earlier
  FLAPW monolayer study — with the LCAO basis-set effect now stated in Methods §1.3 and
  `larsen2009` as the supporting citation (LCAO is *"much less complete"* than plane waves).
- **Contradicted — lattice structure:** experiment gives **bct** Fe below ≈10 Å; our island
  branch (ΔZ ≈ 1–6 Å) lies in that regime and we build from **bcc**. Now a limitation in Methods
  §1.6 and in CLAIMS v5.

**Traceability gap found:** CLAIMS cites `analysis/interface_analysis.csv` as the source for the
Fe–O distances (2.33/2.30 Å), but those values are only *printed* by the script — they are not
columns in that CSV. Either add them to the CSV or restate the source.

**Citations written:** six verified via DOI content negotiation (Crossref) and added to
`references.bib`: `urano1988`, `butler2001`, `yuasa2004`, `reitinger2007`, `fahsold2000`,
`larsen2009`. `yuasa2004` is currently uncited (candidate for the `cofebmgo_mtj` placeholder).
All `\cite{}` keys in `sections/` now resolve except the three known MTJ placeholders.

**Sections edited:** §2.1 new "Experimental correspondence" paragraph (`02_results.md`); §3.1
registry + weak-coupling citations (`03_discussion.md`); §1.3 LCAO/basis-set note and §1.6
lattice-model limitation (`01_methods.md`). **`01_methods.md` was approved and has been revised
again, so it is marked as needing re-approval.**

### Follow-up (same day): v5 frozen, MTJ placeholders cleared, full texts unavailable

- **`CLAIMS.md` v5 is FROZEN** (2026-09-17), with `SI-8` signed off in the same act. v5 carries
  the bcc/bct lattice-model limitation, the basis-set limitation, and the
  experimental-correspondence framing (with its scope bound: configurations, not energies).
- **`01_methods.md` re-approved as revised** — it is again the only fully approved section
  (§1.3 LCAO note + §1.6 lattice-model limitation included).
- **MTJ placeholder debt cleared.** `cofebmgo_mtj`, `cofebmgo_pma` and `b_diffusion_mtj` were
  withdrawn from §3.3/§3.4; the CoFeB-specific assertions they supported were **dropped** rather
  than sourced, and the verified `yuasa2004` now carries the MTJ context. §3.3 now reads: the
  metal film in an MgO-based MTJ must be flat and coherently matched for the TMR to be high.
  §3.4 opens with coherent tunnelling across a lattice-matched interface, dislocations
  accommodating the residual mismatch, and growth conditions chosen to minimise them.
  **All `\cite{}` keys in `sections/` now resolve against `references.bib`; no UNVERIFIED
  placeholders remain.**
- **Full texts of the two islanding references could not be obtained.** `fahsold2000`
  (PRB 61, 8475) and `reitinger2007` (JAP 102, 034310) are both **closed access** — Semantic
  Scholar reports `openAccessPdf.status = CLOSED` with the URL empty, and the Masaryk University
  institutional copy of the Reitinger paper exposes no PDF link (404 on the guessed paths).
  They are therefore cited from **verified abstracts only**, which is what the §2.1 quotes come
  from. Note the Urano PDF's watermark — *"Downloaded from journals.jps.jp by 三重大学"* —
  confirms the scientist has institutional access, so downloading these two would settle it.
  A briefer secondary confirmation of the Fahsold result exists: *Applied Surface Science*
  **137**, 224–235 (1999), DOI 10.1016/s0169-4332(98)00533-9, same group — *"Three-dimensional
  metal island growth of Fe was suppressed by evaporation of a first atomic layer at 140 K and
  of a second layer at room temperature."*
- **Extended abstract for `fahsold2000`** (from the APS listing, beyond the earlier snippet):
  *"The measurements at various substrate temperatures (140 < T < 670 K) start with bare
  MgO(001) and extend to film thicknesses beyond the complete coverage of the substrate."* —
  consistent with the framing already written.

## Float numbering (2026-09-17)

Scientist's instruction: promote the tables and the mermaid diagram in `01_methods.md` to
**numbered, captioned floats cited in the running text**, and renumber the counters across the
manuscript (the Results tables were already labelled "Table 1"/"Table 2", which collided).

Now numbered sequentially in order of appearance across the drafted section sequence:

| Float | Location | Content | Was |
|---|---|---|---|
| **Table 1** | `01_methods.md` §1.1 | four interface models: film constitution, atom counts | unnumbered, uncited |
| **Table 2** | `01_methods.md` §1.2 | generation schedule, two generators | unnumbered, uncited |
| **Table 3** | `01_methods.md` §1.2 | generation schedule, three generators (Fe-Co) | unnumbered, uncited |
| **Figure 1** | `01_methods.md` §1.2 | biased-exploration loop (mermaid workflow) | unnumbered, uncited |
| **Table 4** | `02_results.md` §2.1 | the two phases in each model | "Table 1" |
| **Table 5** | `02_results.md` §2.2 | flat-basin minimum dE/N | "Table 2" |
| **Figure S1** | `SI.md` §S1 | exploration-performance panels | unchanged (separate `S` series) |

Caption style unified to `**Table N.** …` (above tables) and `**Figure N.** …` (below figures);
`02_results.md`'s earlier em-dash captions were converted. Every float is now cited in text:
Table 1 in §1.1; Tables 2–3 and Fig. 1 in §1.2 (the Figure 1 caption carries the workflow
sentence that previously appeared in the body text, which was then removed to avoid
duplication); Table 4 in §2.1 (three citations); Table 5 in §2.2 and §2.3.

Verified gapless: Tables 1–5 and Figure 1 each have exactly one caption, and no stale
"Table 1"/"Table 2" references remain in `02_results.md`.

⚠ **Numbering assumption:** it follows the **drafting** order, in which Methods is section `01`
and therefore takes the low numbers. If the final layout puts the Introduction (currently `04`)
first *and* it introduces floats of its own, every number shifts — renumber once at port time.

⚠ **Still open:** the three main-text figure files (`pes_four_systems.png`,
`flat_state_summary.png`, `flat_vs_ground_preview.png`) are **not cited by any section**.
Wiring them in would make them Figure 2 (PES maps, §2.1), Figure 3 (flat-state summary, §2.2)
and possibly Figure 4. Awaiting the scientist's decision.

**`01_methods.md` remains awaiting re-approval** (edited after approval, again).

### Approved (2026-09-17)

The scientist approved `sections/01_methods.md` at the state committed in `c89e1e1`. Approved
content:

- §1.1 — strain direction: the cell takes the DFT-optimised Fe lattice constant, so the **MgO**
  is compressed 3.6 % relative to bulk and the substrate is frozen in that state while the
  **film is unstrained in-plane**.
- §1.2 — the exploration schedule stated **per model**, with Fe-Co's third
  (species-permutation) generator in its own table; seed count corrected 7 → 6.
- §1.3 — the interfacial Fe–O separation stated as a **construction parameter** rather than a
  computed quantity, with the LCAO basis-set caveat kept as a separate statement.
- §1.6 — the bcc/bct lattice-model limitation.
- Floats: **Tables 1–3** and **Figure 1**, numbered, captioned and cited; caption style unified.

**Explicitly *not* covered by this approval** (all still open):

1. the `CLAIMS` **v6** items — restating SI-3's mechanism, reframing SI-4's registry;
2. the **inverse-strain-convention** limitation (would go in §1.6) — held;
3. the three **main-text figures** (`pes_four_systems`, `flat_state_summary`,
   `flat_vs_ground_preview`) — still cited by no section, would become Figures 2–4;
4. `02_results.md`'s re-approval and `03_discussion.md`'s first review.

So `01_methods.md` is approved as it stands, but a fourth revision is likely once items 1–3 are
settled — worth batching them into a single pass rather than approving again in between.

## Model geometry correction — the strain sits on the MgO, not the film (2026-09-17)

Scientist's correction: the cell uses the **Fe-optimised lattice constant**, so **MgO** is the
component constrained to match Fe; the strain is on the substrate, not the film. **Confirmed**,
and the verification went to the code and the stored structures rather than the prose:

| Check | Result | Source |
|---|---|---|
| Cell in-plane | **14.35 Å = 5 × 2.870** → cell = Fe lattice | `data/femgo/seed_3`, first candidate |
| O–O in-plane NN | **2.8700 Å** vs bulk `a_MgO/√2 = 2.9783` → **3.6 % MgO compression** | same structure (substrate is frozen, so this holds for every candidate) |
| Registry | O built **directly above an Fe site** → Fe-atop-O **inherited from construction** | `scripts/build_mgo_stack.py:33` (`pos_o = fe_top_atom.position`, `z += dist_fe2o`) |
| Fe–O separation | build parameter `dist_fe2o = 2.3 Å` (default; `main.py:84` does not override it) → **2.300 Å** flat, **2.331 Å** island | `interface_analysis.py` re-run |
| Film strain | Fe film at its own equilibrium, substrate frozen compressed → **no imposed in-plane film strain** | combination of the above |

**Numeric nuance:** "3.77 %" is the mismatch expressed **relative to Fe**;
`(2.9783 − 2.8702)/2.8702`. The compression of MgO **relative to its own bulk** is **3.64 %**.
Methods §1.1 now states both.

**Two consequences beyond the wording:**
1. **"Strain relief" loses its object.** With no imposed film strain, the island cannot be
   relieving film strain. What it does is abandon the exact registry (Fe–O contacts 25 → 9,
   interface d-centre −0.23 → +0.51 eV) and restore 3D Fe–Fe coordination. → the island's
   driver is to be restated as **reduced forced interfacial coupling + metal cohesion** (SI-3).
2. **The Fe-atop-O registry is built in.** `build_mgo_stack` starts the reference perfectly
   registered, so SI-4's "25/25 atop O, offset 0.000 Å" is **inherited**, not predicted — a
   consistency check (now externally supported by Urano's LEED I–V), not a search result.
   The same applies to SI-3's "~equal d_Fe–O": that follows from the 2.3 Å build parameter
   surviving relaxation, not from the electronic-structure method.

**Applied now (description only, per the scientist's instruction):**
`01_methods.md` §1.1 now states the strain direction explicitly (cell = Fe lattice; MgO
compressed 3.6 % relative to bulk; substrate frozen compressed; **film unstrained in-plane**),
and §1.3 now states the Fe–O separation is a **construction parameter**, not a computed value.

**Held (recorded in `CLAIMS.md` → "PENDING v6"):** restating SI-3's mechanism, reframing SI-4's
registry, adding the inverse-strain-convention limitation, and any inverted re-run (bulk MgO
with a strained Fe film, which has **not** been calculated).

**No numbers change** — the structures were always built this way. ΔZ, dE/N, flat-basin minima,
registry counts and d-band centres are untouched; this is a re-description, not a recomputation.
`01_methods.md` is again **awaiting re-approval** because it was edited after approval.

## Growth mode at 1 ML — checked (2026-09-17)

**Question:** does 1 ML of Fe on MgO(001) grow as an island? **This is our model's coverage** —
25 metal atoms on 25 substrate sites = 1 ML average — so the answer matters directly.

| Source | Coverage studied | Reported mode |
|---|---|---|
| **Fahsold, Pucci & Rieder 2000** (PRB 61, 8475; He-atom scattering) | bare MgO(001) up to beyond complete coverage, 140 ≤ T ≤ 670 K | **3D metal island growth**; island densities, sizes and shapes quantified and a coalescence thickness calculated. *"suppressed at low temperature (140 K) where a monolayer film almost completely covers the substrate"* → **at RT, 1 ML is islands** |
| **Torelli et al. 2009** (PRB 79, 035408; XMCD + STM) | sub-nm → several ML | *"sub-nanometer Fe grows three-dimensionally on MgO"*; island coalescence between **3.5 and 6.5 ML**; **transition to a 2D growth mode above ≈6.5 ML** |
| **Reitinger et al. 2007** (JAP 102, 034310; GISAXS) | **5 ML**, RT | **Volmer–Weber** growth, spherical islands |
| **Urano & Kanaji 1988** (JPSJ 57, 3403) — *local paper* | **1 ML**, RT | **Layer by layer**, pseudomorphic, Fe just above O at ~2.0 Å. **Opposite** to the above |
| **Butler et al. 2001** (PRB 63, 054416) — *local paper* | monolayer + bilayer, *theory* | Adsorption geometry only (Fe atop O, O–Fe = 2.3 Å); **no growth-mode statement** |
| **Yuasa et al. 2004** (Nat. Mater. 3, 868) — *local paper* | 1000 Å and 100 Å Fe | Thick films; no 1-ML statement. **Consistent** once the >6.5 ML 2D transition is accounted for |

**Answer:** at room temperature, **yes** — 1 ML Fe on MgO(001) is reported to grow as 3D islands,
and the growth mode is thickness-dependent with a 3D → 2D transition around 6.5 ML. The local
Urano paper is the **dissent**, at exactly 1 ML — most plausibly because of its conditions
(very slow deposition, ~0.2 Å/min, onto a cleaved crystal annealed at 800 °C in O₂), i.e. low
supersaturation favouring 2D layer growth.

**Consequence for our model, which is favourable:** our two basins correspond to the two
experimentally accessible outcomes **at 1 ML** — the 3D island (RT growth) and the 2D
pseudomorphic monolayer (140 K, `fahsold2000`; slow deposition, `urano1988`). The >6.5 ML 2D
transition also means our result should be framed as **1-ML specific** and not extrapolated to
thick films — which the existing bct limitation (§1.6) already supports.

**Added to `references.bib`:** `torelli2009` (verified via Crossref). **Now cited** in
`02_results.md` §2.1's experimental-correspondence paragraph, together with the thickness
dependence (sub-nanometre 3D growth; coalescence 3.5–6.5 ML; 2D only above ≈6.5 ML), which
also frames the comparison as **1-ML specific**.

**Butler not cited for the construction geometry** (scientist's decision): it reports no growth
mode, so its monolayer/bilayer study stays out of the §1.3 discussion; it remains cited in
`03_discussion.md` §3.1 for the Fe-atop-O registry and the weak interfacial coupling.

## v6 — mechanism wording applied, SI registry reframed (2026-09-17)

Scientist: "Update the current results and discussions md, also, update the other md for these
changes." This executes the decisions held in the v5 "PENDING v6" block.

- `CLAIMS.md` -> **v6 FROZEN**. SI-3 restated (the island's gain is **reduced forced interfacial
  coupling + restored metal cohesion**, *not* lattice-strain relief); SI-4 reframed as a
  **construction-inherited consistency check**; the inverse-strain-convention limitation added to
  the limitations list; the "~equal d_Fe-O" re-attributed to the `dist_fe2o = 2.3 A` construction
  parameter; `torelli2009` added to the experimental-correspondence evidence; version history
  updated. MT-6 stays withdrawn; MT-4 stays CHALLENGED.
- `03_discussion.md` -> **v4**. S3.1 rewritten: the strain sits on the **substrate** and the film is
  unstrained, so there is no film strain for the island to relieve; the registry wording now notes
  that it is both the reference construction's registry and the measured one. S3.4 no longer says
  the flat film is "intrinsically strained". S3.5 extended with the two model-bound limitations
  (inverse strain convention; bcc vs the experimental bct) and the stale seed count 13/7/5/4
  corrected to **13/6/5/4**.
- `02_results.md` S2.1 already carries the 1-ML experimental correspondence with `torelli2009`;
  header moved to CLAIMS v6. **No numbers in Results change.**
- `01_methods.md` S1.6 gained the inverse-strain-convention scope note (cross-referencing S3.5) and
  the header moved to CLAIMS v6. **This edit voids the 2026-09-17 approval** -> `01_methods.md` is
  DRAFT v4 and again awaits re-approval.
- `sections/SI.md` header moved to v6; the stale "SI-8 not yet in CLAIMS" note replaced by a
  requirement that S2, when drafted, carry the v6 reframing (SI-3, SI-4).
- `paper_status.md` and `AGENTS.md`: CLAIMS v6, **13** verified citations, the "mechanism wording
  HELD" item closed, and the closed-access caveat extended from fahsold/reitinger to `torelli2009`.

**No numbers change.** dZ, dE/N, flat-basin minima, registry counts and d-band centres are
untouched; this is a re-description plus a citation addition.

**Ordering note (housekeeping):** the "Growth mode at 1 ML" block was inserted mid-file rather
than appended; it has been relocated to the end of this log so entries stay chronological in time.
Content unchanged.

## S2 drafted; truncated searches found in the method-sensitivity families (2026-09-17)

**S2 written** (`sections/SI.md`) — *Electronic-structure origin of the flat -> island
transition*, carrying the v6 mechanism wording. Adds Table S1 (`pdos_metrics.csv`, claims SI-1 /
SI-2) and Table S2 (`interface_analysis.csv`, claims SI-3 / SI-4), plus Figure S2
(`pdos_flat_vs_island.png`) and Figure S3 (`interface_registry_topview.png`). The superseded
bottom-8/top-8 split (`pdos_site_metrics.csv`, `pdos_sites.png`) is explicitly marked as not to be
used. **Every number in S2 was verified against the two CSVs (38/38 checks passed).** S2 is
written so that no "bulk-like" comparison is made (no bulk-Fe reference exists) and the registry
is presented as construction-inherited consistency check, per v6.

**Traceability gap closed.** `scripts/interface_analysis.py` now also writes
`mean_nearest_d_FeO_A` and `mean_inplane_offset_A` into `analysis/interface_analysis.csv` — the
Fe-O distance (2.300/2.331 A) and the in-plane offset (0.000/0.372 A) were previously only printed
to stdout while CLAIMS SI-3/SI-4 cited the CSV for them. Re-ran; **all pre-existing columns
numerically identical**, registry rows unchanged.

**S3 NOT drafted — data-integrity finding.** `method_sensitivity.load_setting` counts every
non-trash db under a family root, *including searches that stopped early*. Every family except
`kappa=1` contains at least one truncated search, and in every case the truncated search has the
**worst per-seed best by a wide margin** (0.23-0.35 eV/atom vs ~0.03-0.09):

| family | setting | seeds | truncated search (iteration max -> per-seed best eV/atom) |
|--------|---------|-------|------------------------------------------------------------|
| rattle | baseline (`data/femgo`) | 14 | `stop_16` @37 -> 0.22541 |
| rattle | reduced-0.5 (`param_ratt05`) | 4 | `plus1_db` @90 -> 0.32608; `seed_5` @60 -> 0.31315 |
| rattle | reduced-1.0 (`param_ratt1`) | 5 | `seed_7` @37 -> 0.34660 |
| kappa | kappa=2 (baseline) | 14 | `stop_16` @37 -> 0.22541 |
| kappa | kappa=1 (`1_k1`) | 16 | **none — all run to 100** |
| kappa | kappa=3 (`0_k3`) | 11 | `seed_13` @25 -> 0.25371 |
| kappa | kappa=4 (`2_k4`) | 10 | `seed_12` @11 -> 0.27451 |
| dipole | no dipole (baseline) | 14 | `stop_16` @37 -> 0.22541 |
| dipole | dipole xy (`femgo_dip`) | 12 | `seed_14` @12 -> 0.26066 |

Because the truncation is **not uniform across settings**, it biases the comparison itself. Three
treatments of the same data (probe: `scripts/probe_truncation_effect.py`), per-seed best in
eV/atom:

| setting | as-reported (current CSV) | full-only (truncated dropped) | common window <= 37 |
|---------|---------------------------|-------------------------------|---------------------|
| baseline (kappa=2, no dipole) | 0.05030 +- 0.05454 | 0.03683 +- 0.02575 | 0.14375 +- 0.05225 |
| rattle reduced-0.5 | 0.29017 +- 0.05659 (n=4) | 0.26073 +- 0.06804 (n=2) | 0.32588 +- 0.00812 |
| rattle reduced-1.0 | 0.27399 +- 0.12427 (n=5) | 0.25583 +- 0.13287 (n=4) | 0.33923 +- 0.08238 |
| kappa=1 | 0.03947 +- 0.02371 (n=16) | 0.03947 +- 0.02371 (n=16) | 0.16336 +- 0.05313 |
| kappa=3 | 0.05497 +- 0.06620 (n=11) | 0.03509 +- 0.02182 (n=10) | 0.16097 +- 0.04814 |
| kappa=4 | 0.05633 +- 0.07486 (n=10) | 0.03209 +- 0.01872 (n=9) | 0.16140 +- 0.06280 |
| dipole xy | 0.05628 +- 0.06589 (n=12) | 0.03770 +- 0.02436 (n=11) | 0.16129 +- 0.04922 |

**What survives and what does not:**

- **SI-7 (reduced rattle degrades the search): holds** in direction and significance under all
  three treatments. The *factor* is treatment-dependent: ~5.4x as-reported, ~7x full-only, ~2.3x
  on an equal iteration budget. The CLAIMS wording "~5x" is therefore not treatment-independent.
- **SI-5 (result robust to kappa): holds** under all three (all four settings within ~25 %
  full-only, ~14 % equal-budget, SDs overlapping). However **the log's "Best: kappa = 1 (lowest
  and most consistent per-seed best)" does NOT survive** — it is an artefact of kappa=1 being the
  only family with no truncated outlier. Full-only favours kappa=4 (0.0321); on an equal budget
  the baseline kappa=2 is nominally best (0.1438). The CLAIMS v5 evidence cell
  "per-seed best 0.039-0.056 eV/atom across kappa in {1,2,3,4}" is a mixed-treatment range.
- **SI-6 (dipole negligible): holds**, and is cleaner under full-only (0.0368 vs 0.0377, within SD).
- **Seed accounting inconsistency:** the sensitivity baseline's "14 seeds" = 13 full searches +
  the truncated `stop_16`, whereas the main text and SI S1 use **13**. The sensitivity baseline is
  therefore not the same population as the rest of the paper.

**Decision needed from the scientist before S3 is drafted** (all three options change no structure,
only the statistic): (a) report as-is with a disclosure caveat, (b) recompute on a common
iteration budget and bump CLAIMS to v7 with sign-off, or (c) report as-is as the primary number
with the common-budget comparison alongside.

Probes added: `scripts/probe_stop16_bias.py`, `scripts/probe_family_seeds.py`,
`scripts/probe_truncation_effect.py`.

## S3 drafted on an equal-iteration statistic; CLAIMS v7 (2026-09-17)

Scientist's decision on the truncation finding: recompute on **full searches only** (equal
iteration count) as the primary, keep the as-reported values as a footnote, correct the SI-5/6/7
evidence cells, and bump CLAIMS to v7. Also: the confound is disclosed in the SI prose, not only
in the log.

- **`scripts/method_sensitivity.py`** now computes both variants via `split_truncated()` (a search
  is "full" if its iteration max >= `MIN_ITER` = 100), writes **both** to
  `analysis/method_sensitivity.csv` with a new `variant` column, and prints the excluded truncated
  searches for each setting. The figures use the primary variant. **The `asreported` rows
  reproduce the previous CSV exactly**, field by field — the change is additive, not a
  redefinition of the old numbers.
- **Primary numbers** (per-seed best dE/N, eV/atom): baseline (kappa=2, no dipole)
  **0.03683 +- 0.02575**, 13 searches, flat 0.165, div 2.22; kappa=1 0.03947 +- 0.02371 (16);
  kappa=3 0.03509 +- 0.02182 (10); kappa=4 0.03209 +- 0.01872 (9); dipole xy 0.03770 +- 0.02436
  (11); rattle reduced-0.5 0.26073 +- 0.06804 (**2** searches), flat 0.023; rattle reduced-1.0
  0.25583 +- 0.13287 (4), flat 0.017.
- **RETRACTED: "Best: kappa = 1".** On the primary statistic all four kappa settings span
  0.0321-0.0395 eV/atom (0.0074 total), far inside the SDs (0.019-0.026), so **no kappa is
  distinguishable from another**. The old ranking came from the truncated `stop_16` search sitting
  in the baseline, not from any property of kappa=1. SI-5's conclusion (robustness to kappa) holds;
  its ranking never existed.
- **SI-7 factor corrected: ~5x -> ~7x** (0.03683 -> 0.26073 / 0.25583 = 7.08x / 6.95x), flat
  fraction 0.165 -> 0.023 / 0.017. Direction and significance unchanged. Caveat recorded: the
  reduced-rattle arms retain only 2 and 4 full searches, so the **magnitude** is weakly determined.
- **SI-6 unchanged in substance** and cleaner on the primary statistic: 0.03683 +- 0.02575 vs
  0.03770 +- 0.02436, a difference of 0.0009 eV/atom.
- **Seed accounting:** the primary baseline is **13** searches, matching the main text and S1; the
  as-reported baseline counted 14 (13 + truncated `stop_16`).
- **`sections/SI.md`** gained **S3** with Table S3 (all nine settings, primary variant) and Figures
  S4/S5/S6; the truncation confound is stated in the section, together with the seed accounting.
  All 20 numbers in S3 were verified against the CSV.
- **`CLAIMS.md` -> v7**: SI-5/SI-6/SI-7 evidence cells restated on the primary variant, the
  retraction recorded, the truncated-search limitation added, version history updated.
  `paper_status.md` and `AGENTS.md` moved to v7; all four section headers moved to v7.

## v8 — completed searches only, across all analysis (2026-09-17)

Scientist's instruction: *"ignore the stopped early seed, across all analysis. Only use one that
actually finished 100 Iterations."* Applied project-wide; a second, independent defect in the
significance test surfaced while verifying the recomputation.

### Run selection

**Audit of all 196 dbs.** Truncation was NOT confined to the sensitivity families: the main-text
loaders globbed `seed_*/1_db/db_*.db`, which drops runs *named* `stop_*` but silently accepts a
`seed_*` run that stopped early. Two main-text systems had one:

| run | iteration max | before | from v8 |
|---|---|---|---|
| `fecomgo/seed_4` | 10 | included (10 structures) | excluded |
| `fecobmgo/seed_3` | 73 | included (66 structures) | excluded |
| `femgo/stop_16` | 37 | excluded (by name only) | excluded |
| `febmgo/seed_6` | no data | excluded (empty) | excluded |

`data/mgofe`, `data/extraIteration` and `data/latt_conc` also contain unfinished runs, but nothing
in the paper, CLAIMS or analysis reads those trees (exploratory only).

**Enforcement (scientist's chosen option: a single shared rule).** New `scripts/run_selection.py`
(`FULL_ITERATIONS = 100`, `completed_dbs()` / `select_completed()` / `db_iteration_range()`), now
imported by `pes_analysis.py`, `wetting_metrics.py`, `exploration_performance.py`,
`method_sensitivity.py` and `ensemble_analysis.py`. Completion is read from **max(iteration) in the
database, not from the directory name** — that naming assumption is what hid these two runs.

- `ensemble_analysis.py` v1.1.0: `load_system(system)` returns `(recs, used_dbs, rejected)`; the
  integrity inventory now records `unfinished_runs_excluded` (replica + max_iteration +
  required_iterations) per system, replacing the naming-based `partial_replicas_on_disk` which had
  reported `[]` for Fe-Co and Fe-Co-B. The `include_partial` option and the
  `pes_structures_with_partial.csv` output are **gone** (a variant built from unfinished runs
  contradicts the rule); the orphan CSV was deleted.
- `method_sensitivity.py`: `split_truncated`/`MIN_ITER` replaced by `select_completed`; the
  `variant` column and the as-reported computation are removed per the scientist's decision to
  purge those numbers.
- `exploration_performance.py`, `pes_analysis.py`, `wetting_metrics.py`: glob replaced by
  `completed_dbs(...)`, with the exclusions printed.

### A second defect: the permutation test was not a permutation test

`clustered_bootstrap_effect` drew **two independent permutations** of the pooled minima (one per
group) instead of one permutation split into groups. The two groups were therefore sampled
independently rather than partitioning the pool — a **narrower null than a true permutation null**,
which inflates significance. Fixed: one permutation per replicate, split at `na`, with a +1
correction so p is never 0. `perm_n_partitions` and `perm_resolution` are now recorded per
comparison so the test's resolution cannot be over-read.

| comparison | v6/v7 (all runs, old test) | completed runs, old test | **v8 (completed + fixed test)** |
|---|---|---|---|
| B in Fe host (13 vs 6) | 0.005 | 0.005 | **0.045** |
| B in Fe-Co host (5v4 -> 4v3) | 0.74 | 0.008 | **0.092** |
| Co alone (13v5 -> 13v4) | 0.73 | 0.116 | **0.245** |

The two corrections pull in opposite directions for MT-4: removing the truncated outlier raised its
apparent significance (0.74 -> 0.008), fixing the test lowered it again (0.008 -> 0.092). **MT-4 is
under-powered, not absent** (median shift +0.048 eV/atom, 92 % same-sign, floor p = 0.029 at 4 vs 3).
Its status flag is **left for the scientist** — not changed here.

### Recomputed headline numbers

- Completed searches **13 / 6 / 4 / 3** (was 13 / 6 / 5 / 4); canonical structures **2350** (was 2408).
- Flat-basin minima **unchanged**: 0.1888 / 0.1493 / 0.1941 / 0.1494 eV/atom. In every system the
  global minimum belongs to a completed search (shift exactly 0.00000 eV/atom), so all dE/N values
  are unchanged. The excluded replicas were outliers: their per-search best sat 0.26 (Fe-Co) and
  0.40 (Fe-Co-B) eV/atom above the minimum.
- **Changed:** Fe-Co-B flat fraction 0.242 -> **0.289**; Fe-Co 0.214 -> 0.212; Fe-Co-B flat
  per-replica SD 0.118 -> 0.028; motif counts **1-4** per branch (flat 2/2/4/2, island 2/2/3/1);
  within-set fingerprint distance **0.37-0.71** x random-pair scale.
- **Unchanged:** SI S1 (its JSON is byte-identical), SI S2 (fixed structures — the PDOS and registry
  analyses read two XSF files and never touched the search databases), MT-1, MT-2, the experimental
  correspondence, and MT-7's window counts (1 of 72 Fe-B, 1 of 21 Fe-Co-B).
- `pes_analysis.py` and `ensemble_analysis.py` still rebuild `pes_structures.csv` identically
  (max numeric diff 0.0; only row order and `nan` vs `0.0` for the B-free system differ).

### Content propagated (full propagation, per the scientist's decision)

- `01_methods.md` S1.2: counts 13/6/4/3, and a new **"Only completed searches are used"** paragraph
  naming the four excluded runs and stating that the rule reads the iteration number, not the
  directory name. **This voids the 2026-09-17 approval again** -> DRAFT v4, needs re-approval.
- `02_results.md`: MT-8 motif count 1-3 -> **1-4** plus the ratio range and a single-search caveat;
  MT-7 extended with the outside-window figures (101 of 471 Fe-B; 25 of 252 Fe-Co-B) and a
  weak-support caveat (the Fe-Co-B window comes from 2 searches); the uncertainty paragraph carries
  the new counts and p-values (0.045 / 0.245 / 0.092) and states the test's resolution floor.
- `03_discussion.md`: S3.3 cobalt sentence now gives p = 0.245 and frames it as a bound on the
  effect size; S3.5 gained a **third model-bound limitation** on the search-level statistics.
- `sections/SI.md`: S3's as-reported variant **purged** (numbers removed, single disclosure sentence
  kept, per the scientist's decision); Table S3 reframed as "completed searches only" with no number
  changes.
- `CLAIMS.md` -> **v8**: MT-3/MT-4/MT-5 evidence restated with the corrected p-values, MT-7 and MT-8
  evidence updated, the run-selection rule and the permutation-resolution limit added as
  limitations, MT-6's supporting fractions refreshed, version history. Two v7 statements corrected:
  kappa=1 *does* contain an unfinished run (`seed_19`, iteration 6 — it contributed no records under
  the iteration>=10 floor) and the v7 "as-reported variant retained" note no longer holds.
- `paper_status.md` / `AGENTS.md`: v8, the enforcement map, the corrected evidence table, and three
  OPEN items (MT-4's status; the dangling "detailed motif analysis is in the Supplementary Material"
  pointer with no SI motif section; the voided Methods approval).

Probes added earlier and still used here: `probe_stop16_bias.py`, `probe_family_seeds.py`,
`probe_truncation_effect.py`, `probe_truncated_seed_effect.py`.

## Dropped runs: iteration at which each stops; strain-convention split found (2026-09-17)

**Scientist's question:** *"the dropped CoFeB, in what iterations does it stop."*

### Answer

| dropped run | last recorded iteration | structures | at the analysis floor (it >= 10) |
|---|---|---|---|
| **`fecobmgo/seed_3`** (the CoFe-B one) | **73** | 66, one per iteration over 1-73 | **57** |
| `fecomgo/seed_4` | **10** | 10 | **1** |
| `femgo/stop_16` | 37 | 36 | 27 |
| `febmgo/seed_6` | no data | 0 | 0 |

`fecobmgo/seed_3` has 7 iteration numbers absent inside its 1-73 range (38, 44, 47, 54, 55, 62, 64).
Those gaps are **not** evidence of anything: completed runs have gaps too (`femgo/seed_12` 3 gaps,
`febmgo/seed_3` 3, `fecomgo/seed_0` 10). The truncation is purely that the maximum iteration is 73,
27 short of the budget. Neither dropped run directory retains a crash or timeout log — only
`0_result/latt_log.md` and the database — so the local record does not say *why* they stopped.

The CoFe-B truncation is the consequential one: 57 structures against 1 for the Fe-Co one.

### Finding (from reading those latt_logs): the four models are NOT on the same cell

`fecobmgo/seed_3/0_result/latt_log.md` records `strain=4.90%`, not the 3.77% the paper states.
It is not a typo. The build files carry an explicit strain switch, with the comment
*"Control Strain / 0.0 = Fe lattice / 1.0 = Fe stretch to fit MgO"*:

    a_custom = a_own + interpolation_factor * (a_mgo_matched - a_own)

| model | own lattice constant | `interpolation_factor` | actual cell in-plane | strained component |
|---|---|---|---|---|
| Fe/MgO | `a_fe = 2.870190` (`femgo/main.py:41`) | absent (== 0) | **2.87000** | substrate compressed 3.6 %; film unstrained |
| Fe-B/MgO | same | **0** (`febmgo/main.py:48`) | **2.87019** | substrate compressed 3.6 %; film unstrained |
| Fe-Co/MgO | `a_fe = 2.839177` (`fecomgo/main.py:38`) | **1** (`:53`) | **2.97833** | **film stretched 4.9 %**; substrate at bulk |
| Fe-Co-B/MgO | `a_feco = 2.839177` (`fecobmgo/main.py:41`) | **1** (`:56`) | **2.97833** | **film stretched 4.9 %**; substrate at bulk |

Verified against the cells actually stored in the databases (not only the logs):
`femgo` cell a = 14.35000 (= 5 x 2.870), `febmgo` 14.35095 (= 5 x 2.87019),
`fecomgo` and `fecobmgo` 14.89167 (= 5 x 2.978334 = 5 x a_MgO/sqrt2).

So the Co-containing models put the mismatch on the **film** (stretched 4.9 %) with the substrate at
bulk, and the Fe models put it on the **substrate** (compressed 3.6 %) with the film unstrained.
`data/latt_conc/` already contains a strain sweep along this axis
(`0_latt_0` = 0.0, `1_latt_1` = 0.5, `2_latt_075`, `3_latt_025`, `4_latt_100` = 1).

### Consequences if the paper is left as-is

1. **Methods S1.1** states one convention for all four models ("the MgO in-plane parameter is forced
   to 2.870 A ... the mismatch is accommodated by the substrate, not by the film"). True for Fe and
   Fe-B; the reverse holds for Fe-Co and Fe-Co-B.
2. **Discussion S3.1** says "the Fe film sits at its own equilibrium lattice constant and is not
   strained in-plane, so there is no film strain for the island to relieve". Unstrained applies only
   to the Fe models; the Co models have 4.9 % film strain available to relieve.
3. **The 2x2 comparison** (MT-3/MT-4/MT-5) compares the Fe host at 3.77 % mismatch with the strain on
   the *substrate* against the Co host at 4.90 % with the strain on the *film*. The central
   cross-host claim ("boron acts the same in both hosts") therefore confounds boron with the strain
   convention.

### Status

**No section, CLAIMS entry, table or figure was changed.** This is a claims-level decision and was
put to the scientist, whose answer did not come back; it is recorded here and in `paper_status.md`
as OPEN so it cannot be lost. Options put to the scientist: (a) state both conventions explicitly
plus a Table 1 column and treat the convention as a stated confound; (b) re-run the two Co models at
`interpolation_factor = 0` so the series is uniform (needs HPC; invalidates the Co numbers);
(c) restrict the cross-host claim until unified; (d) record only.

### Non-issue checked and cleared

`dist_z_fe2o = 0.5  #2.3` appears in all four `main.py` files and looks like a contradiction of
Methods S1.3. It is a *different* quantity: it is passed as `hetero_slab_dist` to
`HeteroStructRandomize` (the initial deposition-slab offset), whereas the Fe-O construction distance
is `build_mgo_stack(dist_fe2o=2.3)` (`femgo/scripts/build_mgo_stack.py:6`), which `main.py` calls
without overriding. S1.3's claim stands. The naming is a trap for future readers.

---

## 2026-09-17 — CLAIMS v9: the Co host is archived; the paper becomes Fe/MgO vs Fe-B/MgO

### The instruction

> *"archive the current CoFe host results, considering it has so many problem. For now, write the
> main and supplementary based on the Fe host, with and without B."*

Four follow-up decisions, all from the scientist: (1) MT-4/MT-5 go to a new **"ARCHIVED — out of
scope"** block, *not* to "NOT claimed"; (2) **no Co sentence anywhere in the manuscript**; (3) the
Greer framing stays as it is, on the boron-only argument; (4) the Co data moves to
`data/_archive/`, the records to `_archive/cofe/`, and the analysis scripts keep their four-system
capability but default to the Fe-host scope. No new searches are run.

### What was archived, and why it is not a refutation

See `_archive/cofe/README.md` for the full record. In one line: the Co host is not a clean
counterfactual — it sat on a different strain convention (`a_MgO/√2`, film stretched 4.9 %, vs
`a_Fe`, substrate compressed 3.6 %), 4 vs 3 completed searches cannot reach p < 0.029 however the
data fall, and `data/fecomgo/main.py:75,172–175` adds a third `PermutationGenerator`. MT-4 (p =
0.092 then, 0.0857 exact now) is **under-powered, not absent**; MT-5 (p = 0.245 / 0.2357 exact) was
never a demonstrated null. The frozen values, the two effect blocks, both branch/motif sets and both
replica inventories are preserved in `_archive/cofe/cofe_evidence.json`, and the 627 Co rows of the
canonical CSV in `_archive/cofe/pes_structures_cofe.csv`.

### A new defect found while re-running the analysis: the permutation p was scope-dependent

The first re-run of `ensemble_analysis.py` under the new scope **reproduced** every frozen number
(0.1888 / 0.1493 eV/atom, 13 vs 6 searches, global-min ΔZ 3.65 / 3.77 Å, flat fraction 0.165,
motif counts) but gave **p = 0.046** where CLAIMS recorded 0.0452. The cause was not the scope
change as such: the bootstrap CIs and the Monte-Carlo permutation p drew from the **module-level
shared RNG**, whose stream position depends on how many systems were processed before them. So
analysing the two archived Co systems first moved a number the manuscript reports:

| run | p for the Fe-host boron effect |
|---|---|
| Fe host alone (in scope) | 0.0452 |
| all four systems (`--all-systems`) | 0.0480 |

**Fix, in two parts.** Each effect now seeds its own bootstrap generator (`EFFECT_SEEDS`), and the
permutation test **enumerates all partitions of the pool exactly** instead of sampling 5 000 of
them — 27 132 for 13 vs 6, 35 for 4 vs 3, 2 380 for 13 vs 4. The result is deterministic, seedless,
and reaches the resolution `perm_resolution` advertises. `analysis/ensemble_stats.json` v1.2.0
records `perm_method` per comparison. **Verified:** the Fe-host p is byte-identical in scope and
with `--all-systems`.

| comparison | v8 (Monte-Carlo) | v9 (exact) |
|---|---|---|
| B in the Fe host — MT-3, 13 vs 6 | 0.0452 (0.0480 if the Co systems were loaded) | **0.04438** |
| B in the Fe-Co host — archived MT-4 | 0.0924 | 0.08571 |
| Co alone — archived MT-5 | 0.2454 | 0.23571 |

This is the **third** revision of the significance test: the v1 test drew two independent
permutations instead of one split (fixed in v8), the v8 test was Monte-Carlo from a shared RNG
(fixed here), and the test is now exact. The v8 changelog's 0.045 / 0.092 / 0.245 stand as the
record of what v8 reported.

### What changed in the repository

- **Claims:** `CLAIMS.md` **v9** — MT-4, MT-5 and the combined 2×2 statement archived; MT-1, MT-2,
  MT-7 and MT-8 restricted to the two systems; the contribution rewritten (it no longer claims host
  independence); a new limitation for the lost third-element control; the permutation-resolution
  limitation and the strain-convention confound both resolved by the scope restriction; MT-6 stays
  withdrawn on its primary reason only. SI-1…SI-8 are untouched.
- **Code:** `scripts/scope.py` added as the single scope switch; `pes_analysis.py`,
  `ensemble_analysis.py` (v1.2.0), `plot_pes_figure.py`, `export_flat_xsf.py`,
  `preview_flat_xsf.py`, `check_forces.py`, `probe_forces_dist.py`, `probe_geometry_all.py` and
  `relaxation/select_structures.py` now import it. `probe_truncated_seed_effect.py` deliberately
  still spans all four systems — it is this project's v8 audit record.
- **Artifacts:** `analysis/pes_structures.csv` 2350 → **1723 rows**; `figures/pes_2_systems.png`
  replaces `pes_four_systems.png`; four `analysis/flat_structures/*` XSFs and the old four-system
  PES figure moved to `_archive/cofe/`. `.gitignore` re-enables `_archive/cofe/` against the repo
  root's blanket `_archive/` and `*.csv` rules (verified with `git check-ignore`).
- **Sections:** `01_methods.md` **v5**, `02_results.md` **v4**, `03_discussion.md` **v5**,
  `SI.md` **v4** (a scope note only). Tables 4–5 became 3–4 after the Fe-Co generator table was
  deleted; the dangling "motif analysis is in the Supplementary Material" pointer was removed
  rather than adding an S4.
- **Docs:** `paper_status.md` rewritten as a v9 resume file; `AGENTS.md` scope/claims/systems
  updated; `_archive/cofe/README.md`, `data/_archive/README.md` and `figures/INSTRUCTION.md` added.

### Reproduction check after the change

0.1888 / 0.1493 eV/atom; 13 vs 6 completed searches; global-min ΔZ 3.652 / 3.767 Å; MT-7's 1-of-72
in-window and 101-of-471 outside; motif counts 2/2 and 2/2 with within/random 0.41–0.44;
`method_sensitivity.csv` and `exploration_performance.json` **byte-identical** (md5 unchanged,
confirming the SI is untouched); `pes_analysis.py` and `ensemble_analysis.py` numerically identical
to 0.0 on every column (row order differs — already true before v9).

### Still open after this session

The rewritten contribution needs re-signing; the application framing (§3.3 no longer names CoFeB)
needs a decision; the exact test needs formal acceptance; the three re-scoped sections need review
(03 is the gate for the introduction); the main-text figures are still cited by no section.

---

## 2026-09-17 — CLAIMS v10: two new robustness studies in the SI (SI-9, SI-10)

### The instruction

> *"I've included new data. extraIteration and latt_conc. Include their analysis into the
> Supplementary Material. It was testing the impact of additional Iteration onto the over the MT
> finding, and also, the impact of the constraint, where previously, we match to the Fe, but now,
> we also match it to the MgO (not that it's an experimental MgO lattice)."*

Five follow-up decisions, all from the scientist: (1) the f = 0 arm of the constraint sweep stays
out of the paper (it is a reference arm; `_archive/latt_conc/1_latt_1`, the f = 0.5 arm, is an empty
directory); (2) `a_MgO = 4.212 Å` is the **experimental** MgO lattice constant used as a fixed
reference; (3) both studies are **boron-free on purpose**, so they bound the structural result
(MT-1, MT-2) and the stated limitations, not the boron effect (MT-3); (4) they land as two new SI
sections, **§S4 (iteration budget, SI-9)** and **§S5 (lattice constraint, SI-10)**, with a CLAIMS bump
to v10; (5) the iteration-budget analysis is **per-run truncation** primary (each run cut at k = 100
and at its own budget, same trajectory, no cross-run normalisation), with the arms as a secondary
description.

### What the data is (verified)

- **`data/extraIteration`** — the same Fe/MgO calculation at 200 / 400 / 600 iterations.
  `diff data/femgo/main.py extraIteration/0_200Iter/main.py` is a **single line** (`N_iterations`
  100 → 200); everything else identical. 6 + 7 + 4 completed searches. Scratch `trash/` and `_trash/`
  excluded. The `_trash/seed_*` dirs are mostly 100-iteration runs set aside.
- **`data/latt_conc`** — the constraint sweep, `a = a_Fe + f(a_MgO/√2 − a_Fe)`, both phases built on
  `a_custom`, at f = 0.25 / 0.75 / 1.00 (10 + 10 + 5 completed searches). Cell in-plane confirms the
  interpolation (14.470 / 14.751 / 14.892 Å). The f = 0 arm (`0_latt_0`) is in `_archive/latt_conc/`
  and out of scope; `1_latt_1` is empty. The sweep uses `a_Fe = 2.866 Å` against the main text's
  `2.87019 Å` (0.15 % difference, recorded as a caveat). Runs that stopped early are excluded
  (seed_113 at 12/40 it, seed_107 at 10, seed_109 at 62).

### The results

**SI-9 (budget).** Island ground state in **17/17** searches at both the 100-iteration cut and the
full budget. The flat–island separation is unchanged in 5 and larger in 12 of 17 searches (median
**+0.0104**, range 0 to **+0.0268** eV/atom) — it never shrinks. Pooled per arm: 0.1901 → 0.1901
(200 it), 0.1624 → 0.1662 (400 it), 0.1807 → 0.1978 eV/atom (600 it). The **absolute** minimum is
still improving at 100 iterations (12/17 runs, median 0.0013, up to 0.0071 eV/atom) — so it is the
*comparison*, not the absolute energy, that is budget-insensitive. The 13 main-text searches read
through this script reproduce the pooled flat-basin minimum **0.1888 eV/atom** exactly. **This
answers the convergence caveat held since v4.**

**SI-10 (constraint).** Island ground state in **25/25** searches. Pooled flat-basin minimum
**0.1932 / 0.1982 / 0.1907 eV/atom** across f = 0.25 / 0.75 / 1.00 against **0.1888** for the
main-text Fe-matched model — a total spread of **0.0094 eV/atom**, 2–3× smaller than the within-arm
search-to-search SD (0.017–0.031). The far end places the substrate at the experimental MgO lattice
constant and stretches the film 3.92 %, so the **physically inverted strain case is now calculated**
for the boron-free model, and the result is unchanged.

### What changed in the repository

- **Analysis:** `scripts/iteration_budget.py`, `scripts/lattice_constraint.py` (both scope-aware,
  each arm tested against its own budget via `run_selection`, scratch excluded, self-describing
  JSON + CSV + figure). Outputs `analysis/iteration_budget.{json,csv}`,
  `analysis/lattice_constraint.{json,csv}`, `figures/iteration_budget.png`,
  `figures/lattice_constraint.png`.
- **Claims:** `CLAIMS.md` **v10** — SI-9 and SI-10 added with paired caveats; the convergence caveat
  held since v4 written into the Limitations with numbers; the inverted-strain case no longer "not
  calculated" for the boron-free model; a new limitation for the run-set spread of the flat-basin
  reference (0.1624–0.1901 eV/atom across independent run sets); the f = 0 / f = 0.5 arms, the a_Fe
  difference and the experimental a_MgO recorded as out of scope / reference.
- **Sections:** `SI.md` **v7** — §S4 (Table S4, Figure S7) and §S5 (Table S5, Figure S8) drafted,
  following the no-code / no-revision-history voice rules.
- **Docs:** `paper_status.md` (SI-9/SI-10 section, float sources, OPEN items, drafting table),
  `AGENTS.md` (claims v10, data list, float numbering), `figures/INSTRUCTION.md` (the two new
  figures + open design questions).

### Still open after this session

SI-9 and SI-10 need sign-off; the wording of the convergence bound in §1.6 / §3.4 is the scientist's
call (options in `paper_status.md` → OPEN); the two new figures have open design questions in
`figures/INSTRUCTION.md`; the three main-text sections still await review (03 is the gate for the
introduction).

### Addendum — `data/mgofe` (MgO on Fe): a ground-state comparison, qualified (SI-11)

The scientist added `data/mgofe` — the **inverted stack**, an MgO film on an Fe substrate
(Fe25Mg25O25, cell = a_Fe = 2.866 Å experimental, a_MgO = 4.212 Å experimental, interpolation_factor
0, 100 iterations, same two-generator GOFEE scheme, 5 completed searches, one search stopped at 26
and excluded) — intending to compare the wetting of the deposited layer between Fe-on-MgO and
MgO-on-Fe.

**Ground state.** The ground state of the inverted stack is a **flat MgO film** (ΔZ over MgO =
0.39 Å), lying **0.016 eV/atom below** the corresponding island — the opposite of Fe-on-MgO, whose
ground state is an **island** (ΔZ = 3.65 Å) with the flat film 0.189 eV/atom above it. The sign of
the wetting preference inverts between the two stacks.

**Caveat (why the claim is qualified).** The inverted-stack searches **do not converge at the
100-iteration budget**, so the comparison is indicative rather than settled. The structures are
physically sound (min interatomic distance 1.6–2.0 Å), so this is under-convergence rather than a
broken calculation, and the gap between the flat film and the island is marginal (0.016 eV/atom).
The per-run evidence for the non-convergence is kept in `analysis/mgo_on_fe.json`.

**Decision (scientist, 2026-09-17):** report it as a **ground-state comparison** in the SI — a
qualified finding, not a clean claim — and **drop the per-seed analysis**: §S6 (SI-11) covers the
ground state only, and the non-convergence is stated at the run-set level with no per-seed numbers.
Analysis: `scripts/mgo_on_fe.py` → `analysis/mgo_on_fe.{json,csv}`, `figures/mgo_on_fe.png`. To make
it a real result the inverted stack would need to be run to convergence.

### Addendum — the sweep is anchored to the experimental lattice constants

The scientist clarified (2026-09-17) that the constraint sweep uses the **experimental** lattice
constants of both bulk phases, not computed values: bcc α-Fe **2.866 Å** and rocksalt MgO
**4.2112 Å** (4.212 Å as used). Two primary measurements were verified via Crossref and added to
`references.bib`:

- **Pietrokowsky, P., *J. Appl. Phys.* 37, 4560–4571 (1966)**, DOI 10.1063/1.1708081 — bcc α-Fe
  lattice parameter 2860.6 ± 0.1 xu ≈ 2.8665 Å.
- **Swanson, H. E. & Tatge, E., *NBS Circular 539*, Vol. 1, pp. 63–64 (1953)**, DOI
  10.6028/NBS.CIRC.539v1 — MgO (periclase) a₀ ≈ 4.211 Å.

§S5, the CLAIMS v10 SI-10 caveat and `paper_status.md` now state that the sweep is anchored to the
experimental lattice constants and cite both. The main-text model keeps its *computed* a_Fe =
2.87019 Å (a recorded caveat: the sweep's f = 0 endpoint is a reference, not identical to the main
text). All 15 `\cite{}` keys in `sections/` resolve against `references.bib`; none orphaned.

## 2026-09-18 — figure corrections: one shared PES energy range; the mgo_on_fe branch labels

Two corrections requested by the scientist. Neither changes a number, a claim or a section; both are
figure-level.

**1. `pes_2_systems.png` — a common energy range on both panels.** Each panel had been framed on its
own data, so the Fe/MgO panel spanned 0–0.64 eV/atom while the Fe-B/MgO panel spanned 0–2.26; side
by side, a given ΔE/N meant two different things. Asked which common range to use, the scientist
chose the **Fe/MgO ceiling** (option: "shared range = Fe/MgO's ceiling"), so both panels are now
**(−0.01, 0.636) eV/atom**, the boron-free model being the reference. This is a deliberate ceiling
rather than the union of the data: the union (2.256) would have squashed the flat–island region the
figure exists to show.

- **Consequence, accepted:** 25 of the 543 Fe-B/MgO points (**4.6 %**, 2 of them inside the flat
  window) lie above the ceiling and are not drawn. `scripts/plot_pes_figure.py` prints the count on
  every run, and `paper_status.md` records it against the float table, so the truncation is on the
  record without being annotated on the figure. No analysis, table or claim value is affected.
- The reference is the first system in `SYSTEMS_IN_SCOPE` (`femgo`), so `--all-systems` keeps the
  same rule.

**2. `mgo_on_fe.png` — the branch labels sat outside the figure.** "island lower" / "flat film
lower" were drawn with `transform=ax2.get_yaxis_transform()`, whose **y coordinate is in data units,
not axes fractions**. At `y=1.0` that put "flat film lower" at 1.0 eV/atom, while panel (b)'s range
is (−0.026, 0.199) — about 0.8 eV/atom, roughly 4.6 panel-heights above the top edge, hence the
report that it floated above the top-right corner. Both labels now use `transAxes` and sit at the
midpoint of the band each one names, in the right margin just outside the panel.

**Verification.** Both scripts pass `py_compile` under `agox_v2` and were re-run. Checked at the
matplotlib level rather than by eye: the two PES panels report identical `ylim` = (−0.0100, 0.6359),
and the two branch labels' rendered text boxes fall inside panel (b)'s axes box vertically. The
regenerated `analysis/mgo_on_fe.json` differs from the previous one in its `version` field alone
(2.0.0 → 2.0.1) — the ground state (0.386 Å, flat film), the flat-vs-island separations (+0.1888 /
−0.0161 eV/atom) and the run-set spreads all reproduce exactly, so the frozen CLAIMS v11 numbers
stand.

**Recorded in:** `figures/INSTRUCTION.md` (a new "Changed 2026-09-18" section; item 3 of the v9 list
annotated as superseded for the PES maps) and `paper_status.md` (float-table note, "Changed
2026-09-18"), so this is not an undisclosed body of work. Script versions: `plot_pes_figure.py`
1.2.0, `mgo_on_fe.py` 2.0.1.

**Still open:** the figure-design questions in `figures/INSTRUCTION.md` (the `flat_state_summary.png`
redesign, PES 1×2 vs stacked, the mgo_on_fe inset) are unchanged; the three main-text sections still
await review, and `04_introduction.md` / `05_conclusion.md` / `06_abstract.md` are not drafted.

## 2026-09-18 — the open decisions consolidated into one checklist; three stale cross-references fixed

Asked what was waiting on the scientist, the answer was scattered across three files with no single
index: `paper_status.md` → OPEN (12 prose items), `CLAIMS.md` → OPEN + the sign-off checklist (4
items), `figures/INSTRUCTION.md` → open questions (7 items), with overlap and no shared numbering.
`paper_status.md` → OPEN is now **one consolidated checklist** of **19 items in five groups** —
A1–A4 claim sign-offs, B1 the section-approval gate, C1–C6 wording and framing, D1–D6 figures,
E1–E2 references and access — each item naming where its detail lives. Nothing was deleted: the
detail stays in `CLAIMS.md` and `figures/INSTRUCTION.md`, which now both point at the checklist
(`CLAIMS.md` maps its claim-level items to A1–A4 / C1–C3; `figures/INSTRUCTION.md` maps its questions
to D1–D6). The section closes with a "decided — not open" list (Fe-host scope, the PES shared energy
range and its 25 off-scale Fe-B points, the constraint arms, a_MgO = 4.212 Å, SI-8, the Co archive)
so a fresh session does not re-open settled questions, and flags the un-run `relaxation/` pipeline as
the largest open *work* item rather than a decision.

**Three stale cross-references found and fixed while doing it:**

- `paper_status.md` → "Next step" still read `SI.md` **v7**; the SI is at **v8** (it carries §S6 now).
- `paper_status.md` → the section-review item named `01_methods.md` **v5**; the file is at **v6**
  (confirmed from each section's own head comment: 01 v6, 02 v4, 03 v5, SI v8).
- `CLAIMS.md` → the sign-off checklist located the application framing in **§3.4**; that discussion is
  **§3.3 "Implications for MTJ stacks"** — §3.4 is the Limitations section, renumbered from §3.5 in
  the v5 re-scope. The item now names §3.3 and reads "keep general or cut", matching the actual
  section, which says "MgO-based tunnel junctions" and names no CoFeB.

No claim, number, section or figure changed: documentation only.

## 2026-09-18 — the main-text figures are cited: `02_results.md` v5

Checklist item **D1**, on the scientist's instruction ("draft the figure/table call-outs so it stops
being uncited"). The earlier claim that *no* float was cited was too broad: the **tables** were
already called out — `Table 3` in §2.1 (three places) and `Table 4` in §2.2 — and `Figure 1` from
Methods. What was genuinely uncited was every **figure** of the Results: `pes_2_systems.png`,
`flat_state_summary.png` and the side-view render appeared nowhere in any section.

**Numbering.** Assigned by the governing convention (sequential in order of appearance across the
drafted sections), which the call-outs now fix in place: **Figure 2** = the sampled two-phase
landscape, `pes_2_systems.png`, in §2.1; **Figure 3** = the flat-basin comparison,
`flat_state_summary.png`, in §2.2. This moves the flat-basin figure off the "Figure 3 candidate" row
it held in `paper_status.md` before the call-outs existed — it is now the third figure to appear by
construction rather than by an earlier plan, and §2.1 ends up carrying both Figure 2 and Table 3. The
side-view render stays deliberately uncited: it is a **200 dpi preview** (`figures/INSTRUCTION.md`
sets 300 dpi for manuscript figures), so promoting it to a **Figure 4** in §2.1 needs a re-render and
the scientist's design decision.

**Text added to `sections/02_results.md` (v5).** Two call-out sentences and two captions:

- §2.1, after the structures/Table 3 sentence: "Fig. 2 draws that landscape …" — the figure is the
  map the search was designed to produce, the points form a continuous band descending from the flat
  window to an island minimum near ΔZ = 3.7 Å, and the two panels share one energy scale.
- §2.1: caption for Figure 2 (the flat window shading, the star and diamond markers, the common
  scale).
- §2.2: "… and Fig. 3 places the two values side by side with the change between them marked", plus
  the Figure 3 caption (flat-window minima and the shift produced by boron).
- The context sentence for Figure 2 states plainly that the two panels share an energy scale, which
  is what the 2026-09-18 shared-range change made true — so the caption and the figure agree.

**Style.** The call-outs use the abbreviation the manuscript already uses elsewhere ("summarised in
Fig. 1" in Methods; "descends to zero (Fig. S1)" in the SI), while captions keep the full
"**Figure N.**" form — matching the existing table practice of "(Table 3)" in prose against
"**Table 3.**" captions. No code identifier, path or filename entered the prose (verified by scan);
the file-level mapping stayed in `paper_status.md`.

**Verified.** Scripted check over the four drafted sections: every main-text float now has both a
caption and at least one inline call-out; the caption order gives Tables 1–4 and Figures 1–3, each
series sequential by appearance. No claim, number, table value or figure was altered — this is
citation scaffolding only.

**Doc sync.** `paper_status.md` — Float numbering gains the Figure 2/3 rows, the traceability table
drops the "candidate" labels for them, the "cited by no section" warning is replaced by a citation
status note, the drafting table and checklist B1 move to v5, and D1 records the drafting as awaiting
acceptance. `AGENTS.md` — float list now reads Tables 1–2 + Figure 1 (Methods), Tables 3–4 + Figures
2–3 (Results), with the Figure 4 candidate and its 300 dpi condition. `figures/INSTRUCTION.md` — the
numbering question is closed to a note, with the side-view promotion left open.

**Noticed but not acted on:** in `SI.md` only **Figure S1** is called out from the text; Figures
S2–S9 and Tables S4–S6 stand on their captions alone, which is normal Supplementary practice but
inconsistent with the main text's new state. Whether to add SI call-outs is the scientist's call —
it would touch `SI.md` (v8 → v9) and so belongs inside the block-and-wait gate.

## 2026-09-18 — Methods, Results and Discussion approved; the gate to `04_introduction.md` opens

The scientist reviewed the three drafted sections of the main text and approved all three **as-is**:
`01_methods.md` v6, `02_results.md` v5 (including the figure captions and call-outs added earlier the
same day) and `03_discussion.md` v5. No revision was requested, so no section text changed — this entry
is a state change only.

**Why it matters.** `03_discussion.md` was the block-and-wait gate for `04_introduction.md`; with it
approved, `04` is unblocked and is the next drafting step. `SI.md` v8 is now the **only** drafted
section still awaiting review — reviewing it does not hold up `04` (its gate was `03`), but the paper
cannot be finalised, and no LaTeX port can start, until it is signed off.

**Approval tracking.** Each approved section carries `APPROVED 2026-09-18` in the editorial head block
of its file, replacing the "awaiting review" / "TO BE REVIEWED" status line. The governing consequence
is unchanged and now restated in `AGENTS.md`: **any later edit to an approved section voids that
approval and requires re-review** — exactly how the earlier `01_methods.md` v3 approval was lost to the
v4 edit.

**Two housekeeping fixes folded in:**

- `01_methods.md` carried a **stale version marker**: its head comment read `<!-- DRAFT v5 -->` while
  both its own changelog block and `paper_status.md` had it at **v6**. The marker now reads v6. No
  section content changed.
- `AGENTS.md`'s drafting summary still described `02_results.md` as **v4** and Phase E as "no section is
  approved"; both are corrected, and the summary date moved 2026-09-17 → 2026-09-18.

**Doc sync.** `paper_status.md` — checklist **B1 checked off** with the residual (`SI.md` v8) called
out, the Phase E table rewritten with the approval state per section and `04_introduction.md` marked
**UNBLOCKED**, a new "Approvals (2026-09-18)" note recording the void-on-edit rule, and "Next step"
rewritten around the open gate. `AGENTS.md` — Phase E block and head-block rule as above. No claim,
number, table, figure or section body was altered.

**Committed together** with the still-pending 2026-09-18 v5 figure-call-out work, which had been left
uncommitted in the working tree.

## 2026-09-18 — `04_introduction.md` v1 drafted; three device-side references verified and added

The first section drafted against an open gate. Written after the block-and-wait gate moved on
(Methods v6, Results v5, Discussion v5 approved the same day), so it could be framed against a known
ending rather than in parallel with the analysis.

**Framing, settled with the scientist before drafting.**

- **Device wording stays generic.** The Introduction says "MgO-based magnetic tunnel junctions" and
  "boron-bearing amorphous electrodes"; it names no CoFeB and discusses no Co *host*, matching the
  approved §3.3 (open item C2).
- **The closing sentence carries no numbers.** The frozen contribution sentence of `CLAIMS.md` v11 is
  reproduced with its quoted shift (~0.04 eV/atom) and its significance value removed; both belong to
  the Results, where they are already stated. The wording is otherwise verbatim.
- **Citation scope was re-opened** (Phase D) rather than written inside the existing set — see below.

**The argument.** Five paragraphs: (1) MgO barriers give very large room-temperature tunnel
magnetoresistance and the effect's first-principles account was given for an *ideal* flat interface,
while the device requires a (001)-oriented barrier and a flat, continuous film; (2) at monolayer
coverage, however, growth experiments find the film dewetting into 3D islands, with a flat
pseudomorphic monolayer obtained only by slow deposition — so two configurations compete, the
experiments constrain their *kinetics* rather than their relative energies, and interface models
assume the flat geometry by construction; that gap is the paper's question. (3) The electrodes are
boron-bearing and amorphous as deposited, and added species are understood to stabilise disordered
configurations — the confusion-principle reading, explicitly deferred to the Discussion. (4) What was
done: two models differing only by the boron, sampled with a deliberately flat-biased search, with
the mechanistic and robustness work in the SI, and the non-convergence caveat stated here rather than
left to the Methods. (5) What was found, closing on the contribution sentence.

**Every number in it is already frozen** — the two flat-basin minima (0.1888 / 0.1493 eV/atom), the
0.040 eV/atom shift and its 21 % reading of the separation, the island spans (~3.7 Å), the exact
search-level statistic (p = 0.0444 over all 27 132 partitions, floor 3.7 × 10⁻⁵, 19 searches), and
the windowed boron–oxygen count (1 of 72). Nothing in §4 is a claim outside the frozen list, so
`CLAIMS.md` was **not** bumped. No float is introduced, so the float numbering is unchanged.

**Phase D re-opened: three references verified and added.** The 13-key set contained nothing that
could carry the device motivation, so three were fetched by DOI content negotiation and confirmed in a
second index (publisher page plus ADS/ResearchGate/IBM Research):

| key | DOI | cited for |
|---|---|---|
| `parkin2004` | 10.1038/nmat1256 | the second, independent report of giant room-temperature magnetoresistance with a crystalline MgO(100) barrier |
| `djayaprawira2005` | 10.1063/1.1871344 | boron-bearing amorphous electrode as the condition under which the MgO barrier grows (001)-textured |
| `ikeda2008` | 10.1063/1.2976435 | barrier (001) orientation and stress relaxation improving on annealing |

`references.bib` holds **18** keys, all cited, none orphaned; every `\cite{}` key across the five
section files resolves (checked by script). All three are CoFeB/MgO device papers — citing them is not
a scope breach (the prose names no alloy and no Co host), but they are flagged for the scientist to
accept or drop (**E3**).

**Two items the section raises that no agent can settle** (both added to the checklist):
**C7** — the confusion-principle framing now appears in the Introduction as motivation, whereas the
claim list assigns that interpretation to the Discussion only; **E3** — the three new references above.
**A third is recorded but deliberately not fixed:** the contribution sentence in `CLAIMS.md` still
quotes the v8 Monte-Carlo p = 0.045 while MT-3 in the same file and the approved Results carry the v9
exact 0.0444; the Introduction quotes neither. Fixing it belongs with re-signing the sentence (A1/A2).

**Doc sync.** `paper_status.md` — B2/C7/E3 added to the checklist, the drafting table gains the
`04_introduction.md` v1 row, the Phase D line records the re-open and the new key count, the float
section notes that the Introduction carries no float, and "Next step" is rewritten around B2.
`AGENTS.md` — Phase D key list, Phase E block and the float-numbering line. `references.bib` — the
three entries in a new dated block.

## 2026-09-18 — `04_introduction.md` v2: the recent MTJ-fabrication trend added

The scientist added four papers to `papers/fabri_*.pdf` and asked that the Introduction carry the
recent trend in MTJ fabrication, with each paper and its contents made clear. The section went to
**v2**.

**The four papers, clarified** (each read in full from the supplied PDF and matched to its published
record by DOI content negotiation; two were preprints and are cited by their **published** versions):

| key | paper | contents | role in §4 |
|---|---|---|---|
| `scheike2023` | Scheike, Wen, Sukegawa, Mitani, *Appl. Phys. Lett.* 122, 112404 (2023), NIMS | Record **631 % room-temperature TMR** (1143 % at 10 K) in epitaxial CoFe/MgO/CoFe(001) junctions; the gain comes from tuning interface atomic structure (crystallographic orientation, MgO interface oxidation, ultrathin CoFe/Mg insertions); large TMR-thickness oscillation. | The record-TMR / interface-engineering arm of the trend. |
| `solano2022` | Solano et al., *Phys. Rev. Mater.* 6, 124409 (2022) (arXiv 2209.10906), Strasbourg | Broadband FMR of single-crystal MgO/Fe/MgO; large **perpendicular surface anisotropy** of the Fe/MgO interface, attributed to interfacial Fe–O hybridisation. | The perpendicular-magnetisation / interface-as-functional-layer arm of the trend. |
| `ichinose2025` | Ichinose et al., *NPG Asia Mater.* 17 (2025) (arXiv 2504.07350), AIST | **Cryogenic (100 K) sputtering** suppresses the island-like initial growth of a sub-nanometre CoFe layer on polycrystalline MgO(001) on 300 mm wafers, enabling grain-to-grain epitaxy; low magnetic damping (0.008) on an Fe-doped (MgFeO) barrier for voltage-driven switching. | Cited twice: the perpendicular/low-damping film arm of the trend, **and** the fabrication-side proof that the metal's islanding tendency on MgO is a live obstacle (room-temperature growth nucleates islands; low temperature suppresses them). |
| `ghemes2024` | Ghemes et al., *Materials* 17, 2554 (2024), Iasi | Layer-by-layer study of an MTJ stack (component analysis + deposition-parameter adjustment); MgO barrier smoothness depends on the underlying layers; ~10 % average TMR gain from process control; CoFeB crystallises bcc(001) on anneal. | The fabrication-practice arm: layer-by-layer control of roughness and thickness. |

**How §4 changed.** A new second paragraph states the recent trend: after a decade's stagnation at
Ikeda's 604 % \cite{ikeda2008}, epitaxial junctions now reach a record 631 % through interface
atomic-structure engineering \cite{scheike2023}; in parallel, perpendicular junctions make the
metal/oxide interface a functional layer, via the Fe/MgO interface's perpendicular surface
anisotropy traced to Fe–O hybridisation \cite{solano2022} and via engineered sub-nanometre films with
low damping \cite{ichinose2025}; and both trends converge on a flat, epitaxial, well-wetting film,
controlled layer by layer \cite{ghemes2024}. In the wetting paragraph, the metal's islanding tendency
is now anchored to modern device-scale growth: grain-to-grain epitaxy on polycrystalline MgO(001) on
300 mm wafers must be run at 100 K because room-temperature deposition lets the metal nucleate as
islands \cite{ichinose2025}. No claim, number, or result was touched — this is literature framing
only, and `CLAIMS.md` is not bumped.

**Verification.** `references.bib` holds **22** entries (20 cited by the main text, 2 by the SI
only); every `\cite{}` key across the five section files resolves, none orphaned (checked by script).
§4 now cites 16 keys. The prose still names no alloy and no Co host (verified by scan). Note the
**file-name/key mismatch**: `papers/fabri_Crina2024.pdf` is **Ghemes et al.**, key `ghemes2024`.

**Doc sync.** `paper_status.md` — the drafting table and B2 move to v2, Phase D records 20/22 keys,
a new **E4** checklist item lists the four papers with their content and the accept-or-drop decision,
and "Next step" is updated. `AGENTS.md` — Phase D key list and the Phase E entry. `references.bib` —
four entries in a new dated block. The scratch extraction `.txt` files were removed; the four PDFs
remain in `papers/` (untracked, as the directory has been).

## 2026-09-18 — `04_introduction.md` v3: phase-controlled design as a core reason, and the GOFEE/LCB justification

Two additions at the scientist's request, and a new GOFEE reference.

**1. The phase-controlled two-phase design is now a core methodological reason.** The paragraph that
opens "what we do" was split. It now states that the flat film is a single, well-defined geometry
while the dewetted family is a continuous set of cluster sizes and heights rather than one low-energy
structure, so exhaustively enumerating its potential-energy surface is not the goal; instead the
search is designed to resolve the two phases the wetting question is about and to compare their
relative energies under a controlled change of composition. This is the sentence the scientist
approved verbatim, promoted from an aside to the leading motivation of the search design.

**2. The GOFEE choice is justified through its lower-confidence-bound property.** A new paragraph
explains why GOFEE is the right engine for this design: a Gaussian-process surrogate trained on the
fly from single-point DFT energies selects candidates with the lower confidence bound
**LCB(r) = E(r) − κσ(r)** — predicted energy E(r) penalised by predicted uncertainty σ(r), κ = 2. The
two terms pull in opposite directions (exploitation vs exploration), so the acquisition keeps probing
uncertain regions even after a low basin is found; that is what lets the search be seeded from a flat
reference film and still reach the island global minimum. This is framed as "guided toward the global
minimum" — a heuristic property, not a guarantee — and is grounded in the two GOFEE references.

**3. The new reference.** The scientist added `papers/gofee_Bisbo2022.pdf` and
`papers/gofee_Hamamoto2023.pdf`. The first is the **original GOFEE paper**, already cited as
`gofee2017` (Bisbo & Hammer, PRB 105, 245404) — no second key. The second is genuinely new:
**`hamamoto2023`** — Hamamoto, Pham, Bisbo, Hammer & Morikawa, *Phys. Rev. Mater.* **7**, 124002
(2023), "Machine-learned search for the stable structures of silicene on Ag(111)", a GOFEE
application whose methods section states the LCB rule (E − κσ, κ typically 2). Verified by DOI
content negotiation and confirmed in a second index (APS + ResearchGate + Google Scholar); added to
`references.bib` in a dated block noting that the Bisbo PDF duplicates `gofee2017`.

**Scope and claims.** No claim, number or result changed — this is method-framing and literature
only; `CLAIMS.md` is not bumped. The device wording stays generic and no Co host is discussed
(verified by scan). The `agox2020` key is no longer cited in the introduction (the search is now
described as GOFEE) but remains cited in Methods §1.2, so it is not orphaned.

**Verification.** `references.bib` holds **23** entries (21 cited by the main text, 2 by the SI
only); every `\cite{}` key across the five section files resolves, none orphaned (checked by script).
§4 cites 16 keys — it dropped `agox2020` (now GOFEE-described, still cited in Methods) and added
`hamamoto2023` — and its body is free of backticks, paths, identifiers and Co-host terms.

**Doc sync.** `paper_status.md` — B2, the drafting table and "Next step" move to v3; Phase D records
21/23 keys; a new **E5** item covers `hamamoto2023` (accept or drop) and notes that the Bisbo PDF
duplicates `gofee2017` (see **E2** for the stale year-in-key). `AGENTS.md` — Phase D key list and the
Phase E entry. `references.bib` — the `hamamoto2023` entry in a dated block.

## 2026-09-18 — the p-value is now explained in plain terms (Results v6, Introduction v4)

The scientist flagged that "p = 0.0444" was quoted without saying what p is. Both places now explain
it in terms a reader can grasp; the Results edit voids its approval, which the scientist authorised.

**The explanation (identical substance in both).** Each of the 19 independent searches contributes
its own lowest flat-state energy — 13 from the boron-free model, 6 from the boron-containing one. The
test reshuffles those 19 values into all possible groups of 13 and 6 and asks what fraction of the
reshufflings would, by chance alone, reproduce a shift in the flat-state energy at least as large as
the one observed. That fraction is p. **p = 0.0444 therefore means: if boron had no effect, a shift
this large would still appear by chance in about 4.4 % of reshufflings** — i.e. the observed lowering
of the flat state is unlikely to be a chance outcome of which searches happened to contain boron. The
test is exact (enumerates all 27 132 reshufflings), significant at the 5 % level, with a resolution
floor of p = 3.7 × 10⁻⁵.

**Where.**
- `sections/02_results.md` → **v6**, §2.2 uncertainty paragraph: the meaning sentence is added right
  after "p = 0.0444, significant at the 5 % level". No number or claim changed. The head block
  records **APPROVAL VOIDED** (v5 was approved 2026-09-18; the scientist authorised this edit).
- `sections/04_introduction.md` → **v4**, closing paragraph: the single-sentence statistic is
  expanded into a short, plain-terms explanation ("if boron had no effect, a shift this large would
  still appear by chance in about 4.4 % of reshufflings"). No number changed.

**Consequence recorded under the governing rule.** Editing an approved section voids its approval.
Results is now back in the block-and-wait gate — new checklist item **B3** (re-approve `02_results.md`
v6), distinct from **B2** (review `04_introduction.md` v4). Methods and Discussion approvals stand.
`CLAIMS.md` is not bumped — the p-value and its meaning are unchanged, only the exposition.

**Doc sync.** `paper_status.md` — B1 rewritten (Results approval voided), **B3** added, B2 and the
drafting table move to v4/v6, the approvals note and "Next step" updated. `AGENTS.md` — Phase E block
(Results v6 awaiting re-approval, Introduction v4). No bibliography change.

## 2026-09-18 — `04_introduction.md` v5: lean, hook-style rewrite

The scientist asked for a shorter introduction that hooks the reader rather than re-deriving the
method, results and discussion (which have their own sections), and for the word "enumerate" to be
replaced with a plainer one. The section was rewritten as **v5**.

**On "enumerate" → "calculated".** *Enumerate* is jargon for "count/list every case". "The p-value is
**calculated exactly** over all 27 132 possible reshufflings of the 19 search minima" says the same
thing (exact, not sampled) in plainer language, so "enumerate" is gone from the body.

**What v5 does.** The body drops from roughly 1400 to **503 words** across six paragraphs: (1) hook —
flat film vs island as two competing configurations, and the islanding tendency that fabrication must
suppress; (2) the recent fabrication trend in two sentences (record TMR via interface engineering;
perpendicular junctions); (3) why boron — boron-bearing amorphous electrodes, confusion principle,
"is what we compute"; (4) **"In this work, we ..."** — one compact paragraph on what is done (two
models differing only by boron; GOFEE seeded from a flat reference; LCB = E − κσ in a single clause
as the reason the search can escape the flat basin; method/electronic-structure/sensitivity pointers);
(5) the result (island ground state; flat a distinct higher-energy basin; boron lowers the flat–island
separation by 0.040 eV/atom, p = 0.0444, "calculated exactly over all 27 132 possible reshufflings ...
about 4.4 % by chance"; boron acts inside the film, does not displace the island); (6) the closing
frozen contribution sentence.

**What was cut (now lives only in their own sections).** The full LCB derivation, the
phase-controlled-design paragraph, the per-search p-value build-up, and the detailed wetting
recitation were compressed to hooks; the substance remains in Methods §1.2/§1.4, Results §2 and the
Discussion. The meaning of p is retained as the one graspable clause ("about 4.4 % by chance").

**Verification.** No orphans, all `\cite{}` keys resolve; no backticks, paths, identifiers or Co-host
terms in the body; every number unchanged from the frozen Results; `CLAIMS.md` not bumped.

**Doc sync.** `paper_status.md` — B2 and the drafting table to v5, "Next step" updated.
`AGENTS.md` — Phase E entry to v5. Bibliography unchanged.

## 2026-09-18 — `04_introduction.md` v6: the full, step-by-step story restored

The scientist preferred the fuller introduction to the lean v5 hook, and asked for the revert to be
understood clearly. **v6 restores the v1–v4 step-by-step story** — motivation, the recent fabrication
advances, the wetting gap, why boron, the phase-controlled / GOFEE-with-LCB method, the result, the
closing contribution — **while keeping the two v5 refinements**:

- **"enumerate" → "calculated"** throughout the body: the exact statistic is now "the p-value ...
  calculated over all 27 132 possible reshufflings rather than sampled", and the island-PES point is
  "an exhaustive calculation of its potential-energy surface is not the goal" / "we therefore do not
  attempt one".
- **"In this work, we ..."** opens the what-we-do passage ("In this work, we address it by comparing
  the energies of the two configurations for a single host, with and without an added metalloid.").

v5 (the lean hook) is retained in the changelog only; the section body is back to the full narrative
(~1530 words). No number or claim changed; `CLAIMS.md` not bumped; bibliography unchanged.

**Verification.** No orphans, all `\cite{}` keys resolve; the body contains no occurrence of
"enumerate"/"enumerat" in any form; no backticks, paths, identifiers or Co-host terms.

**Doc sync.** `paper_status.md` — B2, the drafting table and "Next step" to v6. `AGENTS.md` — Phase E
entry to v6. No bibliography change.

## 2026-09-18 — `04_introduction.md` v7: GOFEE passage merged and trimmed

The scientist judged the GOFEE explanation too detailed and asked for it to be combined into the
what-we-do paragraph, with the method minimised and the emphasis placed on why the lower confidence
bound is effective for a *biased* exploration.

**What v7 does.** The phase-controlled paragraph and the GOFEE paragraph are merged into one. GOFEE is
now a single clause — "a surrogate-driven global optimisation \cite{gofee2017,hamamoto2023}" — and the
LCB (LCB = E − κσ) is kept only to make the biased-exploration point: seeded from the flat reference
film, the bound keeps favouring low-energy regions while continuing to probe unsampled regions, so the
search is not confined to the flat configuration and can still be guided toward the lower island. The
detailed GOFEE mechanics (the Gaussian-process surrogate trained on the fly, κ = 2) are gone from the
introduction; they remain in Methods §1.2.

**Unchanged.** The two v5 refinements ("enumerate" → "calculated"; "In this work, we ..."), the
plain-terms p-value meaning, the closing contribution sentence, all numbers and citations. No orphan,
no backticks/Co-host terms; body ~1420 words.

**Doc sync.** `paper_status.md` — B2, the drafting table and "Next step" to v7. `AGENTS.md` — Phase E
entry to v7. Bibliography unchanged.

## 2026-09-18 — `04_introduction.md` v8: the what-we-do passage in the example style (achievement + roadmap)

The scientist judged the "In this work, we ..." block redundant (it re-explained the method, the
models and the findings already given in Methods §1 / Results §2) and supplied an example of the
preferred manner: one achievement sentence ("In this work, by implementing ... we ... enabling ...")
followed by a roadmap ("This paper is organized as follows. In Sec. II ..."). The scientist asked me
to clarify that intent and confirmed three decisions:

- **Content stays within the frozen claims.** The example's "partition function sampling /
  temperature-dependent probability of each growth motif" framing contradicts `CLAIMS.md` (an
  *exploration* density, not a thermodynamic DoS; basin weights are not physical; MT-6 withdrawn), so
  the achievement sentence was written neutrally — "we categorize the potential-energy surface of Fe
  on MgO(001) into its two growth modes ... and quantify how the added element shifts the relative
  energy of the flat mode" — no probabilities, no thermodynamic quantities.
- **Section numbering.** The roadmap uses final-manuscript order — **II = Methods, III = Results,
  IV = Discussion, V = Conclusion** — not the draft's internal §1/§2/§3 (drafting-file order). This
  must be reconciled at the LaTeX port (recorded).
- **Method mention.** GOFEE stays as a single clause ("a surrogate-driven active-learning search with
  a deliberately biased exploration strategy"); the LCB equation and the model description are dropped
  from the introduction and remain in Methods §1.

**What v8 does.** The verbose ¶5a (phase-controlled + GOFEE/LCB), ¶5c (models/map/SI/caveat), ¶6
(findings + p-value) and ¶7 (closing contribution sentence) are replaced by two short paragraphs: the
achievement sentence and the roadmap. The detailed findings (island ground state, 0.040 eV/atom shift,
p = 0.0444) now live only in Results §2, and the closing contribution sentence belongs to the
Conclusion. Body falls to ~840 words. No number was removed from the frozen list — the numbers simply
stopped being restated in the introduction — so `CLAIMS.md` is not bumped.

**Verification.** No orphans, all `\cite{}` keys resolve; no backticks, paths, identifiers or Co-host
terms in the body; `gofee2017` / `hamamoto2023` remain cited (in the achievement sentence).

**Doc sync.** `paper_status.md` — B2, the drafting table and "Next step" to v8, with a note that the
roadmap's final-manuscript numbering must be reconciled at the port. `AGENTS.md` — Phase E entry to
v8. Bibliography unchanged.

## 2026-09-18 — `04_introduction.md` v9: the scientist's edit (confusion-principle pointer removed)

The scientist edited the boron paragraph directly: the sentence "in the spirit of the confusion
principle of metallic-glass formation \cite{greer1993} — a reading this paper returns to in the
Discussion" lost its forward pointer and now reads "…formation \cite{greer1993}. Applied to this
interface, where the flat film is the two-dimensional, disordered-like configuration …". The principle
is now stated and applied in the same sentence; the reading itself remains in the Discussion per
CLAIMS, so checklist item **C7** (the interpretation is placed in the Discussion only) is **unchanged**
— only the in-text forward pointer is gone.

The paragraph was re-wrapped to the file's line convention (the edit left one long line). No number or
claim changed; `CLAIMS.md` not bumped. Version marker bumped v8 → v9, DRAFT comment updated, and
`paper_status.md` (B2, drafting table, Next step) + `AGENTS.md` (Phase E) synced.

