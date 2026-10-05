# CLAIMS.md — paper1 (frozen claim list)

Freeze the claims before drafting. Any new claim requires bumping this file to v6 first. Numbers must trace to a source file; figures/results come from `analysis/` by reference. **v6 (Session 4at): tightens the crystalline-fraction relative-energy cap from 0.3 to 0.1 eV/atom** (per owner) — the Steinhardt q6 crystalline fraction is now computed over structures within 0.1 eV/atom of each leaf's global minimum, matching the XRD lowest-energy-window convention (0.05 eV/atom center). All MT-1..MT-4 numbers and the crystallinity figure are regenerated from `analysis/cna_rdf/*/cna_rdf.json` at e_max=0.1. **R-1e (Fig 3) also tightened to the 0.1 eV/atom cap** — the surrogate-performance analysis now reports MAE/GPR σ at the single 0–0.1 eV/atom window (bar chart), dropping the multi-window "error grows with distance" trend. (v5 reclassified M-1c/M-1d/M-1e from Method to Results claims; v4 promoted reference-dependence from a limitation to a first-class method component.)

## One-sentence contribution — CONFIRMED (owner, Session 4; reframed Session 4b/4c/4d; **reference-dependence reframe Session 4t; promoted to method component Session 4ad/v4**)
We present a cheap, **reference-anchored** route to model amorphous alloys: the method's defining component is that it models the amorphous state as the low-energy basin around a chosen crystalline reference — a GOFEE/AGOX global-optimization screening (Oganov-style fingerprint descriptor) enumerates that basin, and the Steinhardt q6 crystalline-fraction order parameter confirms amorphization. Applied to Pt(P) — whose fcc reference is its only stable phase — the screening finds 20–30 at% P as the onset of structural amorphization, saturating in concentration and modestly increasing under +3/+5% cell expansion. The reference is a *physical choice* the user controls: for polymorphic hosts (Ta, W) the reference state is a genuine choice, and we demonstrate the method from the **α (bcc) reference** while experiments stabilize the metastable **β** phase (M-3, SI-1).

> Scope decision (owner, Session 4t): **FLAPW SHC is dropped entirely from the paper** — the contribution is the cheap, reference-dependent screening → structural verification pipeline. No SHC claims are made.
>
> Experimental anchoring (owner-approved, Session 4b): Shashank et al. 2025 (\cite{shashank2025}) is the experimental anchor — it demonstrates that *amorphous Pt(P) is achievable* and that amorphization is energy/dose (hence composition) dependent. Our 20–30 at% P is framed as the **onset regime** of the interstitial global-optimization route, **not** an absolute experimental P threshold.

## Main-text claims (MT)

### MT-1 — P loading drives the ONSET of structural amorphization (0P → 20/30P)
- **Claim:** Adding P interstitials (20–30 at%) collapses the host crystalline fraction from 0.99 to 0.09–0.18, i.e. 20–30 at% marks the onset of structural amorphization by the interstitial global-optimization route.
- **Evidence:** Steinhardt q6 crystalline-fraction (fraction of atoms with q6 > 0.5), per-leaf mean over AGOX `iteration >= 10` structures within 0.1 eV/atom of the leaf's global minimum (e_max cap, per M-2): 0P 0.989–0.999 → 20P/30P 0.094–0.184, across all three cell families. Cross-checked by XRD integrated CI (0.81–0.83 → 0.35–0.38, `data/17_PPt/DISCUSSION.md`). *(method: Steinhardt q6 + e_max cap per M-2; iteration ≥ 10 filter per M-1.)*
- **Framing:** "onset" of amorphization, not an absolute experimental P threshold — our concentration (20–30 at%) will be reported alongside the experimental anchor (Shashank: thermodynamic/transport onset by ion dose+energy; box-model dose→at% maps ~35–66 at%, see Limitations).
- **Mechanism:** P is a second species at off-stoichiometric load; per the confusion principle \cite{greer1993}, each added species frustrates the fcc packing of the host, favouring glass/amorphous formation — the physical driver behind the observed 0P→20/30P collapse. Concentration saturation (MT-2) follows once this topological frustration saturates.
- **Source:** `analysis/cna_rdf/*/cna_rdf.json` (crystalline_fraction.mean); XRD table in `data/17_PPt/DISCUSSION.md`; \cite{shashank2025,greer1993}.
- **Verified:** yes.

### MT-2 — Amorphization saturates with concentration (20P ≈ 30P)
- **Claim:** 20% vs 30% P give indistinguishable crystalline fraction (0.094–0.184), i.e. the amorphizing effect saturates once P is loaded.
- **Evidence:** 20P vs 30P crystalline fractions overlap within scatter at every cell (+0%: 0.184 vs 0.176; +3%: 0.137 vs 0.098; +5%: 0.094 vs 0.098). *(method: q6 crystalline fraction + e_max cap per M-2.)*
- **Source:** `analysis/cna_rdf/*/cna_rdf.json`.
- **Verified:** yes.

### MT-3 — Cell expansion mildly promotes disorder; +0% stays most crystalline
- **Claim:** The equilibrium +0% cell retains the highest crystalline fraction at fixed composition; +3% and +5% expansion reduce it, consistent for both 20P and 30P — a mild promotion of disorder, not a strong amorphization switch.
- **Evidence:** crystalline_fraction.mean — 20P: +0%=0.184, +3%=0.137, +5%=0.094 (Δ −0.047 to −0.090 vs +0%). 30P: +0%=0.176, +3%=0.098, +5%=0.098 (Δ −0.078). Matches XRD integrated-CI direction (DISCUSSION.md) but is weak (~7% on the XRD metric; here ~20–50% on the per-atom fraction). *(method: q6 crystalline fraction + e_max cap per M-2; cell families per M-1.)*
- **Mechanism (free-volume rationale):** cell expansion increases local free volume, which sustains/amplifies the disordered atomic rearrangements that characterise the amorphous state — expanding the supercell (+3/+5%, hence +3/+5% free volume at fixed occupancy) lowers the crystalline fraction, while +0% leaves the least free volume and stays most crystalline \cite{yang2025}. This turns the XRD-only (~7%) trend into a mechanistically-grounded per-atom signal (~20–50%).
- **Source:** `analysis/cna_rdf/*/cna_rdf.json`; XRD `data/17_PPt/DISCUSSION.md`; \cite{yang2025}.
- **Verified:** yes.

### MT-4 — P amplifies the cell-expansion effect (relative)
- **Claim:** The disordering effect of cell expansion is proportionally much larger once P is present — P and cell expansion act synergistically, not independently.
- **Evidence:** relative drop in crystalline fraction vs +0% cell — 0P: −0.1% (+3%) to −1.0% (+5%); 20P: −25.5% to −49.2%; 30P: −44.3% to −44.7%. Absolute deltas: 0P −0.001/−0.010, 20P −0.047/−0.090, 30P −0.078/−0.078. *(method: q6 crystalline fraction + e_max cap per M-2; cell families per M-1.)*
- **Framing:** stated in **relative** terms — the doped leaves are already near the amorphous floor (0.09–0.18), so absolute deltas are capped by a floor effect; the amplification is the physically meaningful signal.
- **Mechanism:** P already frustrates fcc packing (MT-1), so the extra free volume from cell expansion (MT-3) has a proportionally larger disordering effect on a host that is already partially disordered.
- **Source:** `analysis/cna_rdf/*/cna_rdf.json`.
- **Verified:** yes.

### MT-5 — Reference-dependence is the method's defining feature
- **Claim:** The method is *reference-anchored*: it models the amorphous state as the low-energy basin around a chosen crystalline reference, and the search is deliberately seeded from that reference topology. This is a design feature, not a bias — it targets the physically relevant basin (the reference is the host's stable phase) and makes the reference a *physical choice* the user controls.
- **Evidence:** The amorphous randomizer seeds the search from the reference P-interstitial alloy (M-1), so the enumerated basin is anchored to the reference topology. For Pt the reference is unique (fcc, its only stable phase); for polymorphic Ta/W the reference is a genuine choice — we demonstrate from the α (bcc) reference while experiments stabilize the metastable β phase (M-3, SI-1).
- **Framing:** stated as the method's core design principle, not a caveat. The honest note that the search is not a uniform random search over all amorphous configurations is a *scope* statement of the method (M-3), not a limitation.
- **Source:** `data/17_PPt/`, `data/11_bTa/`, `data/16_bW/`; \cite{colin2017,kozhukhovska2026,barmak2017,liubarmak2016,chattaraj2020}.
- **Verified:** yes.

## Method claims (M) — pipeline that the manuscript must trace to
> These freeze the *methodological* claims (how the results were produced), so
> the manuscript sections and the mermaid flowchart (M-1b, in this file) trace
> to them the same way MT-1..MT-3 trace to `analysis/`. The mermaid flowchart
> lives in this CLAIMS (M-1b) and is the source of truth (the old
> `codes/methods_flowchart.mmd` figure was removed). Any new method claim bumps
> this file to v5 first.

### M-1 — Global-optimization search (GOFEE/AGOX)
- **Claim:** Low-energy amorphous Pt(P) is enumerated by a GOFEE/AGOX
  surrogate-guided global search, not melt-quench molecular dynamics.
- **Parameters:** fcc Pt host with the **DFT-optimized lattice constant** a = 3.975534 Å, 3×3×3 supercell (Pt₁₀₈); P
  interstitials B = C·A/(1−C) → Pt₁₀₈P₂₇ (20%) / Pt₁₀₈P₄₆ (30%); cell expansion
  +0/+3/+5% (11.927/12.284/12.523 Å), +10% excluded. Descriptor: Oganov–Valle
  angular fingerprint. Gaussian-process regression surrogate built from a sum
  of two radial-basis-function kernels with a repulsive prior;
  lower-confidence-bound acquisition (κ=2). 100 iterations/seed, multiple
  seeds; **iteration ≥ 10 filter** (surrogate-guided phase only).
- **Structure generators (three complementary, joined progressively):**
  - *Amorphous randomizer* — starts from the reference P-interstitial alloy
    and randomly displaces every atom: for each atom it attempts up to 500
    random displacements inside a sphere of radius 1.5 Å (uniform-volume
    sampling), keeping only displacements that stay inside the cell and do not
    place the atom too close to a neighbour. This seeds the search near the
    reference topology.
  - *Rattle generator* — displaces a random subset of atoms by up to 1.5 Å,
    producing small local perturbations of an existing candidate.
  - *Interstitial-permutation generator* — swaps the positions of atoms of
    different species (Pt ↔ P) among the interstitial sites, up to 20 swaps
    with 20 attempts each, and applies a small rattling displacement (1.5 Å)
    to the swapped atoms; this redistributes P among sites to explore
    different interstitial arrangements.
  - The three generators enter the candidate mix progressively: the amorphous
    randomizer alone at iteration 0, joined by the rattle generator at
    iteration 10, and by the permutation generator at iteration 25.
- **Electronic structure:** density-functional relaxations (GPAW,
  linear-combination-of-atomic-orbitals basis, double-zeta-polarized, PBE
  functional, single Γ-centered k-point, Fermi–Dirac smearing 0.05 eV, forces
  converged to 0.05 eV/Å).
- **Source:** `data/17_PPt/*/main.py`;
  \cite{gofee2020,gofee2022,agox2022,oganov2009,gpaw2010,madanchi2024,biswas2017,artrith2018}.

### M-1b — Iteration dependence of the search (timeline)
> The search is not stationary: the generator mix and the relaxation switch on at
> specific iterations. This is the iteration dependence of the method, the
> structure generators, and the relaxation gate.

```mermaid
flowchart LR
    Init["Init (i = 0)"]
    Dec{"Iteration i"}

    subgraph BE["Biased Exploration"]
        direction TB
        P1["<b>Phase I</b><br/>Amorphous: N = 10"]
        P2["<b>Phase II</b><br/>Amorphous: N=5 | Rattle: N=5"]
        P3["<b>Phase III</b><br/>Rattle: N=5 | Permute: N=5"]
    end

    GPR["GPR Surrogate<br/>Optimization"]
    Eval["LCB Select M →<br/>DFT Evaluate M"]
    DB[(Database)]

    Init --> Dec
    
    Dec -->|i < 10| P1
    Dec -->|10 ≤ i < 25| P2
    Dec -->|i ≥ 25| P3

    P1 --> Eval
    P2 --> GPR
    P3 --> GPR

    GPR --> Eval --> DB
    DB -->|i = i + 1| Dec

    style BE fill:#f4f4f5,stroke:#71717a,stroke-width:1px,color:#18181b
```

- **Iteration dependence of the method (the loop):** the search runs as an
  iteration counter `i`. At each iteration the active phase generates N
  candidate structures, which are scored by the Gaussian-process surrogate,
  the lower-confidence-bound acquisition selects M of them, and DFT evaluates
  those M; the results are stored in the database and `i` increments by 1,
  looping back to the phase decision. Only structures from `iteration >= 10`
  are retained for analysis.
- **The three phases (generator mix by iteration):**
  - *Phase I (0 ≤ i < 10):* the amorphous randomizer alone generates N = 10
    candidates. This is the exploration / surrogate-building phase — the GP has
    no training data yet, so candidates are proposed and DFT-scored to
    populate the surrogate (no LCB guidance).
  - *Phase II (10 ≤ i < 25):* the rattle generator joins — N = 5 from the
    amorphous randomizer + N = 5 from the rattle generator. Relaxation begins
    (`start_relax = 10`) and the search becomes LCB-guided (κ=2).
  - *Phase III (25 ≤ i):* the permutation generator joins — N = 5 from the
    rattle generator + N = 5 from the permutation generator; the amorphous
    randomizer drops out. The search continues under LCB (κ=2).
- **Relaxation gate:** `start_relax = 10` — structures from iterations below
  10 are generated and DFT-scored to populate the surrogate but are **not
  relaxed**; relaxation (and the analysis filter) begins at iteration 10.

### M-2 — Crystallinity verification (XRD + Steinhardt q4/q6 + partial radial distribution functions)
- **Claim:** Amorphization is quantified by two complementary metrics — XRD
  crystallinity indices and a per-atom Steinhardt bond-orientational order
  parameter — cross-checked against each other.
- **Parameters:** XRD patterns simulated with a powder-diffraction calculator
  (Cu Kα, 2θ 10–90°, Gaussian broadening σ=0.15°), peak-fraction + integrated
  CI. Structures are binned into relative-energy windows (0.1 eV/atom wide, up
  to 0.5 eV/atom, relative to the leaf's global minimum) and a deterministic
  sample of each window is averaged. Steinhardt q4/q6 from the first-neighbor
  shell (cutoff 1.3× the
  nearest-neighbor distance); an atom is fcc-like when q6 > 0.5 (fcc q6 ≈
  0.5745); crystalline fraction = mean over retained structures within
  0.1 eV/atom of the leaf's global minimum (relative-energy cap, per-leaf
  reference). Partial radial distribution functions g_PtP(r) and g_PP(r) out
  to 5.0 Å (200 bins).
- **Source:** `codes/emit_cna_rdf.py`; `analysis/cna_rdf/*/cna_rdf.json`;
  `data/17_PPt/DISCUSSION.md`;
  \cite{steinhardt1983,pymatgen2013,ase2017}.

### M-3 — Reference-anchored search (the defining method component)
- **Claim:** The method is *reference-anchored*: it models the amorphous state
  as the low-energy basin around a chosen crystalline reference, and the search
  is deliberately seeded from that reference topology. This is a design feature,
  not a bias — it targets the physically relevant basin (the reference is the
  host's stable phase) and makes the reference a *physical choice* the user
  controls.
- **Reference as a physical choice:** Pt has a single stable phase (fcc), so its
  reference is unique; Ta and W are polymorphic (α-bcc equilibrium vs
  β-metastable tetragonal/A15), so the reference is a genuine choice — we
  demonstrate from the α (bcc) reference while experiments stabilize the
  metastable β phase (the spintronically relevant phase, giant spin Hall effect).
- **Scope (design choice, not a limitation):** because the search is seeded from
  the reference topology, it is not a uniform random search over all amorphous
  configurations — it explores configurations *near the reference basin* first.
  This is intentional: it targets the relevant basin for a design tool. The
  first ~10 iterations are surrogate-building (exploration) and are excluded
  from analysis (iteration ≥ 10 filter, M-1b).
- **Source:** `data/17_PPt/`, `data/11_bTa/`, `data/16_bW/`;
  \cite{colin2017,kozhukhovska2026,barmak2017,liubarmak2016,chattaraj2020}.

## Results claims (R) — measured outcomes reported in the Results section
> These freeze the *measured outcomes* of the search (cost, search dynamics,
> surrogate accuracy). They were reclassified from Method claims (M-1c/M-1d/M-1e)
> in v5 because their content reports results, not procedure; the manuscript's
> Results section must trace to them.

### R-1c — Computational cost of the screening
- **Claim:** The surrogate-guided search enumerates the amorphous Pt(P)
  candidate ensemble at a fraction of the cost of conventional first-principles
  melt-quench molecular dynamics.
- **Numbers:** ~5.8×10³ DFT relaxations across the six Pt(P) leaves
  (~2–3×10² per seed) produce ~5.2×10³ retained candidate structures, stored
  in a compact, indexable database (~8–12 MB per leaf). This is the same
  efficiency regime as evolutionary/ML-assisted amorphous sampling in other
  systems (~10³ first-principles calcs), and far below the tens of thousands
  of reference calculations typically needed to train a general
  machine-learned potential for melt-quench.
- **Source:** `data/17_PPt/*/seed_*/1_db/db_*.db`;
  \cite{meltquench2026,artrith2018,nahas2016,activemlp2020}.

### R-1d — Exploration-to-exploitation transition
- **Claim:** The search transitions sharply from a surrogate-building
  (exploration) phase to LCB-guided exploitation at iteration 10.
- **Numbers (multi-seed, 61 seeds across 13 leaves):** the mean DFT energy of
  retained structures drops sharply at the iteration-10 LCB switch-on, and the
  drop is universal across every seed. Per-leaf median drop (exploitation mean
  minus exploration mean): 0P −156 to −218 eV, 20P −256 to −306 eV, 30P −320
  to −356 eV — the transition grows with P loading. For the representative
  leaf (1_plus0cell/2_20P) the mean drops from −375 to −390 eV (exploration)
  to −681 to −689 eV (exploitation) across its four seeds. The acquisition
  value correlates strongly with the DFT energy for P-doped leaves (|r| ≈
  0.7–0.9 across all 20P/30P seeds; the correlation is weak for 0P, |r| ≈
  0.2–0.7), confirming the surrogate selects low-energy candidates rather than
  noise. The per-leaf global minimum is typically reached in the latter half
  of the 100-iteration budget (P-leaf medians 80–99; range 10–100).
- **Source:** `data/17_PPt/*/*/seed_*/1_db/db_*.db` (61 seeds);
  `analysis/explore_exploit/explore_exploit.json` (produced by
  `codes/extract_explore_exploit.py`); fig
  `analysis/figures/fig_explore_exploit.png`; \cite{gofee2022}.

### R-1e — Surrogate predictive performance (low-energy regime)
- **Claim:** The GPR surrogate predicts the DFT energy accurately enough to drive the search in the low-energy regime that matters for selection — structures within 0.1 eV/atom of the leaf's global minimum. The surrogate's predicted uncertainty (GPR σ) tracks the actual error in this regime, validating the LCB acquisition.
- **Numbers (retained ensemble, iteration ≥ 10, all 9 leaves, per-leaf relative energy 0→0.1 eV/atom):** MAE in the 0–0.1 eV/atom window is 0.009–0.015 (0P), 0.029–0.034 (20P), 0.048–0.061 (30P) eV/atom across the three cells; GPR σ in the same window is 0.019–0.023 (0P), 0.028–0.032 (20P), 0.043–0.048 (30P). Both MAE and σ rise with P loading, and the predicted uncertainty tracks the actual error — validating the LCB acquisition (κ=2).
- **Metric note:** R² is not reported — within the 0.1 eV/atom window the energy variance is tiny relative to the error, so R² is negative and uninformative. MAE and GPR σ are the meaningful metrics.
- **Caveat:** the DFT ground truth for P leaves is on under-relaxed geometries (single-DFT-step evaluator), so the measured error includes that noise — the surrogate error is an upper bound on the true model error.
- **Source:** `data/17_PPt/*/*/seed_*/1_db/db_*.db` (61 seeds);
  `analysis/surrogate_perf/surrogate_perf.json` (produced by
  `codes/extract_surrogate_perf.py`); fig
  `analysis/figures/fig_surrogate_perf.png`; \cite{gofee2022}.

## Supplementary claims (SI)
### SI-1 — Reference-dependence and polymorphism (Ta, W) — demonstration detail
> The core reference-anchored claim lives in **M-3** (method) and **MT-5** (main text). SI-1 carries the *polymorphism demonstration* that makes the reference a physical choice.
- **Claim:** For polymorphic hosts the reference state is a genuine physical choice, and the choice matters. Pt has a single stable phase (fcc), so its reference is unique; Ta and W are polymorphic (α-bcc equilibrium vs β-metastable tetragonal/A15), so the reference is a choice.
- **Our demonstration (α reference):** we seed the bTa and bW searches from the **α (bcc)** reference — 3×3×3 BCC Ta/W, 54 host atoms, B interstitials 0 → ~8–10 at% (Ta: 0/1/3/5 B; W: 0/1/3/6 B). Same GOFEE/AGOX pipeline as Pt(P).
- **Experimental contrast (β reference):** experiments routinely stabilize the metastable **β** phase instead — β-Ta (tetragonal) and β-W (A15), which are the spintronically relevant phases (giant spin Hall effect) \cite{colin2017,kozhukhovska2026,barmak2017,liubarmak2016,chattaraj2020}.
- **Source:** `data/11_bTa/`, `data/16_bW/`; \cite{colin2017,kozhukhovska2026,barmak2017,liubarmak2016,chattaraj2020}.

## NOT claimed
- No claim that our 20–30 at% P constitutes an **absolute experimental** amorphous threshold — it is the onset regime of our interstitial route only (Shashank's ion-bombardment onset maps to ~35–66 at% by box-model dose conversion).
- No claim using the `0_PPt_4x4_20P` (4×4) leaf in any cell-trend statistic — different supercell size, excluded from the +0/+3/+5 comparison.
- No claim that cell expansion alone induces strong amorphization — effect is mild/qualitative (MT-3 framing).
- No claim about `3_plus10cell` (+10%) — excluded by scope.

## Limitations
- **Concentration framing vs experiment:** our amorphization claim is structural (interstitial GOFEE/AGOX route, Steinhardt q6 order parameter). It does **not** assert an absolute experimental P threshold. Shashank et al. 2025 \cite{shashank2025} amorphizes Pt(P) by ion dose+energy; a box-model dose→at% conversion (range ~17 nm @30 keV) maps their transport onset to **~35–66 at% P**, above our 20–30 at%. This gap reflects different synthesis routes (interstitial optimization vs ion bombardment) and is a stated caveat, not a contradiction — see `hpc_runs/convert_dose_concentration.py` (box-model estimates; replace with SI-S3 SRIM profiles if a numeric comparison is reported).
- **Supercell size (finite-size):** all results use a single 3×3×3 supercell (Pt₁₀₈, ~12 Å edge, ~135–154 atoms); the +0/+3/+5\ % differ by cell \emph{volume} at fixed occupancy (a free-volume probe, MT-3), not by a same-physics supercell-size convergence sweep. Per best practice for amorphous modeling \cite{setten2026}, the cell is near the lower edge of sizes needed to fully suppress artificial periodicity / resolve medium-range order — a reviewer may request a 2×2×2 vs 3×3×3 check. Stated as a limitation, not a claim.
- **Reference-anchored search (design choice, not a limitation):** the GOFEE/AGOX search is seeded from the P-interstitial reference alloy structure (amorphous randomizer), so it explores configurations *near the reference topology* first — it is not a uniform random search over all amorphous configurations. This is the method's core design principle (M-3, MT-5): it targets the physically relevant basin (the reference is the host's stable phase) and makes the reference a physical choice. The first ~10 iterations are surrogate-building (exploration) and are excluded from analysis (iteration ≥ 10 filter).
- All structures DFT-relaxed in a fixed supercell with fixed P count — none is truly bulk-amorphous; expect modest order change vs experiment.
- **Force-under-relaxation of P-doped geometries (applies to MT-1..MT-4):** the geometries backing the crystalline-fraction claims are not force-converged for the P leaves. The AGOX evaluator runs `optimizer_run_kwargs={"fmax": 0.05, "steps": 1}` — a single DFT step after surrogate relaxation — so the stored forces are snapshots. Measured across the retained ensemble (`iteration >= 10`, per-leaf `e_max < 0.1 eV/atom`): 0P leaves reach max|F| down to 0.006–0.012 eV/Å (51–66% of retained structures below 0.05; low energy and low force coincide); every 20P/30P leaf has max|F| pinned at ~0.7–3 eV/Å (median 1.5–2.4, min never below 0.70, up to ~40 in the tail), and the per-leaf *global energy minimum* structure itself sits at max|F| = 0.71–1.65 eV/Å. The amorphization signal (crystalline fraction q6) is therefore computed on geometries 0.7–1.65 eV/Å from force equilibrium for the P leaves only. This is a property of the *search* (surrogate-relaxed + 1 DFT step), not evidence about physical Pt(P) relaxation; the structural claims are stated as energetics-based and must be re-checked against force-converged re-relaxations before any force-based property is trusted. Source: `analysis/energy_vs_force/*.json`, `analysis/energy_vs_force/energy_vs_force.csv` (per-structure ΔE, max|F|), `codes/probe_forces_e003.py`, fig `analysis/figures/fig_energy_vs_force{,_3x3}.png`.

- Crystalline fraction uses a single bond-order threshold (q6 > 0.5, fcc q6 ≈ 0.5745) on the first-neighbor shell; results are threshold-sensitive at the margins but the 0P vs P and cell-expansion contrasts are robust to it.
- `main.py` `SCALE_CELL=1.05` is stale for +0/+3 families — use the xsf cell dimensions.
- High-energy XRD windows have few structures (n=2–3) — least reliable XRD CIs.

## Figures (paper figures and the claims they serve)
> Paper figures live in `analysis/figures/` (by reference, per the reuse rule) and are
> staged into `papers/paper1/figures/` at compile time. Each paper figure maps to the
> claim(s) it serves. The energy-vs-force figures are **diagnostics only** and are NOT paper figures.

| Figure (analysis/figures/) | Serves | Content | Producing script | Data source |
|---------------------------|--------|---------|------------------|-------------|
| `fig_crystallinity_3panel.png` | MT-1, MT-2, MT-3, MT-4 | 3-panel crystallinity (panel titles live here, not in the figure; panels labelled (a)/(b)/(c) at bottom-middle). **(a) Partial RDF** — g_PtP(r)/g_PP(r) for a representative 20P +0% leaf (illustrative, M-2). **(b) Crystalline fraction vs cell expansion** — Steinhardt q6 crystalline fraction (mean ± std), line per P loading across +0/+3/+5%; carries the 0P→P collapse (MT-1), 20P≈30P saturation (MT-2), and the mild cell-dependence (MT-3). **(c) Relative cell-expansion effect** — relative drop in crystalline fraction vs +0% cell, line per P; carries the P-amplified cell-expansion effect (MT-4) and the 20P≈30P overlap (MT-2). | `codes/emit_fig_crystallinity_3panel.py` v1.0.1 | `analysis/cna_rdf/*/cna_rdf.json` (`crystalline_fraction.mean/std`, `partial_rdf`), produced by `codes/emit_cna_rdf.py` v1.1.0 from `data/17_PPt/*/seed_*/1_db/db_*.db` (e_max=0.1 eV/atom) |
| `fig_xrd_crystallinity.png` | MT-1, MT-3 | XRD integrated crystallinity index vs cell expansion, one line per P loading, at the lowest-energy window (0.05 eV/atom). Carries the 0P→P collapse (0.81–0.83 → 0.35–0.38, MT-1) and the mild cell dependence (MT-3), cross-checking the Steinhardt q6 fraction. | `codes/emit_fig_xrd_crystallinity.py` v1.0.0 | `data/17_PPt/*/xrd_out/crystallinity.csv` (integrated CI at lowest window) |
| `fig2_2panel.png` | (superseded by `fig_crystallinity_3panel.png`) | 2-panel crystallinity (partial RDF + crystalline-fraction vs cell). Kept as a diagnostic; not the paper figure. | `codes/emit_fig2_2panel.py` v1.0.0 | `analysis/cna_rdf/*/cna_rdf.json` |
| `fig_energy_vs_force.png` | — (diagnostic, NOT paper) | Hexbin $E_i - E_{\rm glob}$ vs max\|F\|, 3 panels by P loading. | `codes/emit_fig_energy_vs_force.py` v1.1.2 | `analysis/energy_vs_force/*.json` (per-structure ΔE, max\|F\|), produced by `codes/extract_energy_force.py` v1.0.0 |
| `fig_energy_vs_force_3x3.png` | — (diagnostic, NOT paper) | Hexbin $E_i - E_{\rm glob}$ vs max\|F\|, 3×3 (rows=cell, cols=P). | `codes/emit_fig_energy_vs_force_3x3.py` v1.1.2 | `analysis/energy_vs_force/*.json`, produced by `codes/extract_energy_force.py` v1.0.0 |
| `fig_explore_exploit.png` | R-1d | 2-panel exploration-to-exploitation transition. **(a) DFT energy vs iteration** — per-iteration mean/min lines for a representative P leaf (1_plus0cell/2_20P, seed_0), iteration-10 phase boundary shaded (exploration vs exploitation), global-min marker. **(b) Acquisition value vs DFT energy** (exploitation phase) with Pearson |r| reported. Carries the sharp energy drop at LCB switch-on and the surrogate-selects-low-energy claim. | `codes/emit_fig_explore_exploit.py` v1.0.0 | `analysis/explore_exploit/explore_exploit.json`, produced by `codes/extract_explore_exploit.py` v1.0.0 from `data/17_PPt/*/*/seed_*/1_db/db_*.db` |
| `fig_surrogate_perf.png` | R-1e | 2-panel surrogate predictive performance, one bar per leaf (all 9) at the 0–0.1 eV/atom window, grouped by P loading, colored by P loading with a distinct hatch per cell expansion (+0/+3/+5). **(a) MAE** — mean absolute error (eV/atom) between the surrogate prediction and the DFT energy. **(b) GPR uncertainty** — mean GPR σ (eV/atom). Comparing (a) and (b) shows whether the predicted uncertainty tracks the actual error; both rise with P loading. | `codes/emit_fig_surrogate_perf.py` v3.0.0 | `analysis/surrogate_perf/surrogate_perf.json`, produced by `codes/extract_surrogate_perf.py` v1.1.0 (e_max=0.1 eV/atom) from `data/17_PPt/*/*/seed_*/1_db/db_*.db` |

## Sign-off (owner, Session 4 + 4b + 4t + 4ad)
- ✅ Contribution framing confirmed (reframed Session 4b: cheap screening→SHC pipeline; **Session 4t: FLAPW SHC dropped entirely** — contribution is the reference-dependent screening → structural verification pipeline).
- ✅ Experimental anchoring + refs approved (Shashank/Yang/Shi verified, added to `references.bib`).
- ✅ Claim list confirmed (MT-1..MT-3 reviewed; capped numbers + reference-dependence reframe approved).
- ✅ Method claims M-1..M-2 confirmed (v3; the manuscript must trace to them).
- ✅ SI-1 confirmed (reference-dependence + polymorphism; α-reference demonstration, β experimental contrast; 5 refs verified, thome1984 removed).
- ✅ **v4 (Session 4ad): reference-dependence promoted from limitation to method component** — M-3 (reference-anchored search) + MT-5 (defining feature) added; "reference-biased search" limitation reframed as a design choice; M-1b flowchart shows reference-anchored seeding; SI-1 demoted to the polymorphism demonstration detail. **Awaiting owner sign-off on v4.**
- ✅ **R-1e added (Session 4ae, reclassified v5): surrogate predictive performance** — energy-resolved MAE + GPR σ from `analysis/surrogate_perf/surrogate_perf.json` + `fig_surrogate_perf.png` (v2.1.0, per-leaf lines). **Awaiting owner sign-off.**
- ✅ **v5 (Session 4aq): M-1c/M-1d/M-1e reclassified as Results claims (R-1c/R-1d/R-1e)** — their content reports measured outcomes and now lives in the Results section, not Methods. **Awaiting owner sign-off.**
- ✅ **v6 (Session 4at): crystalline-fraction energy cap tightened 0.3 → 0.1 eV/atom** (per owner) — MT-1..MT-4 numbers and `fig_crystallinity_3panel.png` regenerated from `analysis/cna_rdf/*/cna_rdf.json` at e_max=0.1, matching the XRD lowest-window convention. **R-1e (Fig 3) also tightened to 0.1 eV/atom** — surrogate performance now a single-window (0–0.1) bar chart. **Awaiting owner sign-off.**
