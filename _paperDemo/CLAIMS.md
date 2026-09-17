# CLAIMS.md — FROZEN claim list (v8)

**Status: FROZEN (v8, 2026-09-17).** Supersedes v7, v6, v5, v4, v3, v2 and v1.
**Project:** `_paperDemo` · **Venue:** TBD (format-agnostic)

## v8 changelog (2026-09-17) — completed searches only, and a mis-implemented significance test

Scientist's instruction: *"ignore the stopped early seed, across all analysis. Only use one that
actually finished 100 Iterations."* Applied project-wide. Carrying it out exposed a **second,
independent defect** in the significance test, reported below as a separate change.

### 1. Run selection — only completed searches are used

The loaders globbed `seed_*/1_db/db_*.db`, which drops runs *named* `stop_*` but **silently accepts
a `seed_*` run that stopped early**. Two of the four main-text systems had one:

| run directory | iteration max | before v8 | from v8 |
|---|---|---|---|
| `fecomgo/seed_4` | 10 | **included** (10 structures) | excluded |
| `fecobmgo/seed_3` | 73 | **included** (66 structures) | excluded |
| `femgo/stop_16` | 37 | already excluded (matched by name only) | excluded |
| `febmgo/seed_6` | no data | already excluded (empty db) | excluded |

The rule now lives in `scripts/run_selection.py` (`FULL_ITERATIONS = 100`) and is imported by
`pes_analysis.py`, `wetting_metrics.py`, `exploration_performance.py`, `method_sensitivity.py` and
`ensemble_analysis.py`. It is determined from the **iteration number stored in each database, not
from the directory name** — `fecomgo/seed_4` and `fecobmgo/seed_3` were ordinary-looking seed
directories that simply stopped early. `ensemble_analysis.py`'s integrity inventory now reports
truncation by iteration (`unfinished_runs_excluded` per system); the previous naming-based field
reported *nothing* for these systems, which is how they went unnoticed. Methods §1.2 now states the
rule and names the excluded runs. The orphan output `analysis/pes_structures_with_partial.csv`
(whose purpose was to add partial runs) has been deleted.

**Effect:** completed searches go 13 / 6 / **4** / **3** (was 13 / 6 / 5 / 4) and the canonical
structure count 2408 → **2350**. The excluded replicas were severe outliers — their per-search best
sat 0.26 and 0.40 eV/atom above the system minimum.

**Unchanged by this:** all four flat-basin minima (0.1888 / 0.1493 / 0.1941 / 0.1494 eV/atom), the
island ground state in every system, every global-minimum structure, all of SI §S1 (its JSON is
byte-identical) and all of SI §S2 (fixed structures, no searches).
**Changed:** Fe-Co-B's flat fraction 0.242 → **0.289**, Fe-Co's 0.214 → 0.212, the per-replica
spreads (Fe-Co-B's flat per-replica SD collapses 0.118 → 0.028 once its outlier goes), the motif
counts, and every search-level statistic.

### 2. The permutation test was not a permutation test

The test drew **two independent permutations** of the pooled per-search minima — one for each group
— instead of one permutation split into two groups. The two groups were therefore sampled
independently rather than partitioning the pool, which gives a **narrower null** than a true
permutation null and **inflates significance**. One permutation per replicate is now drawn and
split, with a +1 correction (Davison & Hinkley) so p is never reported as 0. Corrected:

| comparison | v6/v7 (all runs, old test) | completed runs, old test | **v8 (completed runs, fixed test)** |
|---|---|---|---|
| B in Fe host (13 vs 6) | p = 0.005 | p = 0.005 | **p = 0.045** |
| B in Fe-Co host (5 vs 4 → 4 vs 3) | p = 0.74 | p = 0.008 | **p = 0.092** |
| Co alone (13 vs 5 → 13 vs 4) | p = 0.73 | p = 0.116 | **p = 0.245** |

Note the two corrections pull in opposite directions for MT-4: removing the truncated outlier
raised its apparent significance (0.74 → 0.008), while fixing the test lowered it again
(0.008 → 0.092). The v3/v7 figures of 0.005 and 0.74 are both superseded.

**MT-4 remains CHALLENGED, but its character has changed**: p = 0.092 with a median shift of
+0.048 eV/atom and 92 % same-sign replicates is *under-powered*, not absent. The test's own floor
for 4 vs 3 searches is p = 0.029 (35 partitions), so it cannot reach significance on this data
however it falls. **Re-wording or un-flagging MT-4 is a scientist decision and is NOT made here.**
`analysis/ensemble_stats.json` now records `perm_n_partitions` and `perm_resolution` per comparison,
and the resolution limit is a stated limitation.

### 3. Corrections to v7 statements

- The v7 claim that "*every family except `kappa=1` contains a truncated search*" was **imprecise**:
  `femgo_kappa/1_k1` does contain an unfinished run (`seed_19`, iteration 6), but under the
  analysis floor of iteration ≥ 10 it contributed no records, so it never appeared as a search.
  Corrected: kappa=1 had no *outlier depressing its mean*, which is what mattered for the retraction.
- The v7 statement that the as-reported variant "is retained alongside in the same CSV
  (`variant` column)" no longer holds — per the scientist's decision the as-reported numbers are
  **purged**; the CSV carries completed searches only, and SI §S3 keeps a single disclosure sentence.
- `torelii2009` appears correctly as `torelli2009` throughout (an earlier commit *message* typo only).

## v7 changelog (2026-09-17) — truncated searches in the sensitivity families

**Finding.** `method_sensitivity.load_setting` counts every non-trash db under a family root,
which includes searches that were **stopped early** (iteration max < 100). Every family except
`kappa=1` contains at least one, and each truncated search has the **worst** per-seed best by a
wide margin (0.23–0.35 eV/atom vs ~0.03–0.09 for full searches), so it inflates the mean and SD
of whichever setting it belongs to. The truncation is **not uniform across settings**, so it
biased the comparison: the baseline reads 0.0503 ± 0.0545 over all searches but 0.0368 ± 0.0258
over full searches alone (+27 % and ~2× the SD from one truncated run).

**Resolution.** The primary statistic is now **equal-iteration (full searches only)**; the
as-reported variant is retained alongside in the same CSV (`variant` column) and the figures use
the primary. Evidence cells for SI-5, SI-6 and SI-7 restated accordingly. No conclusion reverses,
but two statements do not survive:

- **"kappa = 1 is the best setting" is RETRACTED.** It was an artefact of `kappa=1` being the only
  family with no truncated outlier. On the primary statistic the four settings span
  0.0321–0.0395 eV/atom — 0.0074 eV/atom, far inside the SDs (0.019–0.026) — so **no kappa is
  distinguishable from another**. SI-5's conclusion (robustness) holds; its ranking does not exist.
- **The rattle degradation is ~7×, not ~5×** on the primary statistic (0.03683 → 0.26073 / 0.25583).
  Direction and significance are unchanged.
- SI-6 is unaffected in substance and cleaner on the primary statistic (difference 0.0009 eV/atom).

**Seed accounting.** The sensitivity baseline's "14 seeds" is **13 full searches + the truncated
`stop_16`**; the main text and SI §S1 use **13**. The primary `variant=full` baseline is
therefore 13 seeds, consistent with the rest of the paper.

## v6 changelog (2026-09-17) — executes the decisions held in the v5 "PENDING v6" block

- **`SI-3` RESTATED.** The old conclusion — "island origin is **strain relief**, not interfacial
  re-hybridisation" — loses its object: the simulation cell takes the Fe lattice constant, so the
  **MgO** carries the strain (compressed 3.6 % relative to bulk) and the **Fe film is not strained
  in-plane**. There is no film strain for the island to relieve. The island's gain is now stated as
  **reduced forced interfacial coupling plus restored metal cohesion**: the registry-locked
  monolayer spends its bonding on Fe–O contacts while forgoing 3D Fe–Fe coordination, and the
  island reverses that trade.
- **`SI-4` REFRAMED.** The Fe-atop-O registry is a property of the **reference construction**
  (`build_mgo_stack` places the substrate oxygen directly above the metal sites) *and* of the
  experimentally measured registry — a **consistency check**, not an independent prediction by the
  search.
- **`SI-3`'s "~equal d_Fe–O" (2.33 vs 2.30 Å) re-attributed.** It follows from the construction
  parameter `dist_fe2o = 2.3 Å` surviving relaxation, so it is not evidence about the
  electronic-structure method. Methods §1.3 already reflects this.
- **NEW LIMITATION — strain convention is the inverse of experiment.** Here the cell takes the Fe
  lattice constant and the **substrate** carries the mismatch; in a real junction bulk MgO imposes
  its lattice on a thin Fe film, which absorbs the strain and relieves it through interfacial
  dislocations \cite{yuasa2004}. The model does not represent the strained-film situation.
- **Scope bound:** the physically inverted case (bulk MgO with a strained Fe film) has **not** been
  calculated; whether the flat–island separation survives it is unknown. Decision: re-describe
  against the current runs first.
- MT-1 … MT-5, MT-7, MT-8 and SI-1, SI-2, SI-5 … SI-8 are **unchanged** from v5; MT-6 remains
  withdrawn (v2); MT-4 remains flagged CHALLENGED (v3).

## v5 changelog (2026-09-17)

- **New limitation added — lattice model.** Both phases are built on a **bcc** Fe lattice,
  whereas experiment reports **bct** Fe on MgO(001) below ≈10 Å (converting to bcc above)
  \cite{urano1988}. The island branch spans ΔZ ≈ 1–6 Å, i.e. inside that regime. The
  flat–island comparison is a trend within a fixed lattice model, not a prediction of absolute
  structural parameters. (Applies to MT-1 … MT-5, MT-8.)
- **New discussion-only interpretation — experimental correspondence.** The two basins are
  mapped onto the two experimentally realised growth outcomes: 3D islands at room-temperature
  deposition, suppressed only at 140 K \cite{fahsold2000}, and Volmer–Weber clusters at 5 ML
  \cite{reitinger2007}; the flat pseudomorphic monolayer obtained by slow deposition on a
  cleaved, oxygen-annealed crystal \cite{urano1988}. Framed as a **consistency check between
  structural configurations, not between energies** — the observed growth mode is also set by
  kinetics.
- **Citation status:** six Fe/MgO references fetched and verified via DOI content negotiation
  (Crossref) and added to `references.bib`: `urano1988`, `butler2001`, `yuasa2004`,
  `reitinger2007`, `fahsold2000`, `larsen2009`. **Note:** none of the first three supplied
  papers reports island formation; `urano1988` reports the opposite (layer-by-layer), and its
  role in the paper is the **Fe-atop-O registry** and the **bct result**.
- `larsen2009` supports the LCAO basis-set discussion in Methods §1.3 (LCAO is less complete
  than plane waves, affecting absolute geometric parameters).
- Everything else unchanged: MT-1 … MT-5, MT-7, MT-8 and SI-1 … SI-8 as in v3/v4; MT-6 withdrawn
  (v2); MT-4 flagged CHALLENGED (v3).

## v4 changelog (2026-09-17)

- **SI-8 ADDED (pending sign-off)** — performance of the biased exploration in finding the
  global minimum, Fe/MgO only, all iterations. The claim is centred on the **onset of
  relaxation as the pivot of the search**, not on how early or late the minimum appears.
  Source `analysis/exploration_performance.json`; figure
  `figures/exploration_performance_femgo.png`; drafted as §S1 of `sections/SI.md`.
- Nothing else changes: MT-1 … MT-5, MT-7, MT-8 and SI-1 … SI-7 are unchanged from v3; MT-6
  remains withdrawn (v2); MT-4 remains flagged CHALLENGED pending more searches (v3).
- **Not yet reflected in v4 (held for review):** the searches are still improving at
  iteration 100, so the per-model reference energies are not converged with respect to search
  length. The scientist elected to discuss this at review rather than to write it into the
  limitations now.

## v3 changelog (2026-09-17)

- **MT-8 ADDED** — the low-energy structures of each branch form a small set of *recurring
  motifs* rather than one repeated structure, and ΔZ is continuous (no discrete island
  heights). New main-text claim supporting the "map" framing; evidence from
  `analysis/ensemble_stats.json`.
- **MT-4 status: CHALLENGED — pending more searches.** Its value is unchanged, but a
  replica-resampled permutation test on the per-search flat-basin minima gives p = 0.74 at
  5 (Fe-Co) vs 4 (Fe-Co-B) searches, versus p = 0.005 for MT-3 at 13 vs 6. MT-4 is therefore
  reported in the Results as a *trend* of the same size as MT-3 until more Fe-Co / Fe-Co-B
  searches exist. The confidence rating is left as-is but flagged; it is not downgraded in v3.
- **Method & scope** now records the governing epistemic principle: the biased search returns
  an *exploration* density, not a thermodynamic density of states, so basin weights are not
  physical and only unweighted structural/energetic comparisons are used.
- **Discussion-only interpretations** gains the phase-separation wording: boron changes the
  flat–island separation, and the data do not resolve whether the flat phase is stabilised or
  the island destabilised.
- MT-1 … MT-5, MT-7 and SI-1 … SI-7 are otherwise unchanged from v2 (no values, sources or
  confidence levels altered). MT-6 remains withdrawn (v2).

## v2 changelog (2026-09-17)

- **MT-6 WITHDRAWN** — "B increases the fraction of flat-basin structures sampled"
  (0.165 → 0.208; 0.212 → 0.289 under the v8 run-selection rule; 0.214 → 0.242 as originally
  computed). Reason: the flat fraction is a *weight* of a
  **biased** exploration, not a physically interpretable population, and a cross-system
  comparison of weights additionally requires a fixed exploration operator, which does not
  hold — `data/fecomgo/main.py:75,172–175` adds a third `PermutationGenerator` to the schedule
  used by `femgo`, `febmgo` and `fecobmgo`. The flat reference also differs in kind across
  systems (pure Fe layer vs randomised Fe/Co layer vs B-decorated layer).
- MT-1 … MT-5 and MT-7 unchanged; SI-1 … SI-7 unchanged except for the note on SI-7 below.
- The withdrawn claim moves to "NOT claimed (explicitly excluded)".

This is the authoritative list of what the paper claims and does NOT claim. Drafting
(`sections/*.md`) must not introduce claims outside this list, and must not drop the
paired caveats. Numbers below are frozen to the cited source files.

---

## Contribution (one sentence)

> **Boron insertion lowers the relative energy of the flat metal-film wetting state on
> MgO by ~0.04 eV/atom in both a pure-Fe and a Fe-Co host, while Co alone has little
> effect — i.e. B promotes flat-film wetting independently of the host metal, relevant
> to interface flatness in CoFeB/MgO MTJ stacks.**

---

## Main-text claims

| ID | Claim | Exact value | Source | Confidence |
|----|-------|-------------|--------|-----------|
| **MT-1** | The lowest-energy structure found is an **island** (not flat) in all four systems | global-min ΔZ = 3.65 / 3.77 / 2.75 / 3.45 Å (Fe / Fe-B / Fe-Co / Fe-Co-B) | `analysis/pes_structures.csv` | strong |
| **MT-2** | The **flat configuration is a distinct, higher-energy basin** (not the ground state) | flat-basin min dE/N > 0 in every system (0.149–0.194 eV/atom) | `analysis/pes_structures.csv` | strong |
| **MT-3** | **B lowers the flat-state energy in the pure-Fe host** | 0.1888 → 0.1493 eV/atom (−0.040) | `analysis/pes_structures.csv` | strong (two-sided permutation p = 0.045 at 13 vs 6 completed searches; the earlier 0.005 came from a mis-implemented test — see v8) |
| **MT-4** | **B lowers the flat-state energy in the Fe-Co host** | 0.1941 → 0.1494 eV/atom (−0.045) | `analysis/pes_structures.csv` | **CHALLENGED — NOT RESOLVED, and under-powered rather than absent** (two-sided permutation p = 0.092 at 4 vs 3 completed searches; median shift +0.048 eV/atom, 92 % same-sign). The test's own resolution floor for 4 vs 3 is 0.029, so it cannot reach significance on this data. The earlier p = 0.74 came from a mis-implemented test on a dataset that included unfinished searches; that figure overstated the absence of an effect. **Whether this claim stays flagged CHALLENGED or is re-worded is a scientist decision** — see v8 |
| **MT-5** | **Co alone has little effect** on the flat-state energy | 0.1888 → 0.1941 eV/atom (+0.005) | `analysis/pes_structures.csv` | moderate (two-sided permutation p = 0.245 at 13 vs 4 completed searches — consistent with no resolvable effect, but weaker support for the null than the previously reported p = 0.73) |
| ~~MT-6~~ | ~~B increases the fraction of flat-basin structures sampled~~ | **WITHDRAWN in v2** — see changelog | — | — |
| **MT-7** | **B does not bond to the MgO interface** (stays in the metal film) | B_contact_frac ≈ 0 in the low-energy window dE/N ≤ 0.05 eV/atom (1 of 72 Fe-B, 1 of 21 Fe-Co-B; max contact fraction 0.33 / 0.5). Outside the window 101 of the remaining 471 Fe-B and 25 of the remaining 252 Fe-Co-B structures *do* have a B–O contact, so the claim is window-restricted, not global. Window defined by `scripts/wetting_metrics.py --e-window-per-atom 0.05`. **Weak-support caveat:** the 21 Fe-Co-B window structures come from only 2 completed searches (20 from one of them) | `analysis/pes_structures.csv` | moderate (windowed, and dominated by one search in Fe-Co-B) |
| **MT-8** | The low-energy structures of each branch form a **small set of recurring motifs** rather than one repeated structure; ΔZ is **continuous**, with no discrete island heights | Island branch spans ΔZ ≈ 1–6 Å (no quantisation); low-energy sets split into 1–4 single-linkage motifs (flat 2/2/4/2, island 2/2/3/1 per system); within-set fingerprint distance is 0.37–0.71 × the branch's random-pair scale; Fe/MgO's 5 lowest flat structures (from 5 independent searches) fall into 2 motifs, 4 in the dominant one | `analysis/ensemble_stats.json` | moderate — see paired caveat |

**Combined 2×2 statement (MT-3/4/5):** B effect −0.040 (Fe) and −0.045 (Fe-Co); Co effect
+0.005 (no B) — B is the dominant lever, Co is not.
**Note:** MT-6 (flat-basin sampling fraction) is withdrawn in v2. The flat-basin *fraction*
may still be reported as a descriptive attribute of the sampled database, but not as a
physical result and not as a cross-system comparison.

**Paired caveat for MT-8 (must travel with the claim).** The motif test uses the AGOX global
`Fingerprint` (radial + angular distribution functions) computed on the whole template + film
structure. Because the 50-atom MgO template is identical across structures, it dominates the
descriptor and compresses all pair distances, so the reported motif counts are a *lower bound*
on the structural diversity present — the descriptor cannot resolve differences finer than the
distances it reports. A film-resolved descriptor (or a species-aware RMSD) would be sharper.
The claim must therefore be stated as "a small set of recurring motifs", not as an exact
number of distinct structures.

---

## Supplementary-material claims

| ID | Claim | Exact value | Source | Confidence |
|----|-------|-------------|--------|-----------|
| **SI-1** | Islanding **reduces Fe–O hybridisation** | d-band centre −0.229 → +0.601 eV; O-pz ∫ 43.88 → 42.37 | `analysis/pdos_metrics.csv` | strong |
| **SI-2** | Islanding **weakens magnetism and lowers DOS(E_F)** | spin pol 5.81 → 4.37; DOS(E_F) 104.0 → 78.1 | `analysis/pdos_metrics.csv` | moderate |
| **SI-3** *(restated v6)* | The island's **true interface Fe are NOT flat-like** → the island's gain is **reduced forced interfacial coupling plus restored metal cohesion**, **not** lattice-strain relief | island interface d-centre +0.51 eV vs flat −0.23 eV; registry-locked atoms 25/25 → 9/25. The ~equal d_Fe-O (2.33 vs 2.30 Å) follows from the 2.3 Å construction parameter surviving relaxation, so it is **not** evidence about the method | `analysis/interface_analysis.csv` | moderate |
| **SI-4** *(reframed v6)* | **Fe sits directly atop O** at the interface — a property of the **reference construction** that agrees with the measured registry: a **consistency check**, not a search prediction | 25/25 (flat) and 9/9 (island) atop O; 0 atop Mg (flat offset 0.000 Å); `build_mgo_stack` places substrate O above the metal sites | `analysis/interface_analysis.csv` | strong (structural) |
| **SI-5** *(evidence restated v7)* | The result is **robust to the LCB kappa** — and **no setting is distinguishable from another** | per-seed best **0.0321–0.0395 eV/atom** across kappa ∈ {1,2,3,4} (completed searches only, 100 iterations); the whole range spans 0.0074 eV/atom, far inside the SDs (0.019–0.026), so **no kappa is identified as best** | `analysis/method_sensitivity.csv` | strong |
| **SI-6** | The result is **robust to the dipole correction** | per-seed best **0.03683 ± 0.02575** (no dipole) → **0.03770 ± 0.02436** (dipole xy) — a difference of 0.0009 eV/atom, far inside the SD (completed searches only) | `analysis/method_sensitivity.csv` | weak (outcome-level only) |
| **SI-7** *(evidence restated v7)* | **Reducing the rattle strength degrades the search ~7×** and under-samples the flat basin | per-seed best **0.03683 ± 0.02575 → 0.26073 / 0.25583 eV/atom (7.1× / 7.0×)**; flat fraction **0.165 → 0.023 / 0.017** (completed searches only). **Caveat:** the reduced-rattle arms retain only **2 and 4** completed searches | `analysis/method_sensitivity.csv` | strong (direction), weak (magnitude — arms of n = 2 and 4) |
| **SI-8** *(v4; signed off 2026-09-17)* | **The onset of relaxation is the pivot of the biased search**: the pre-relaxation iterations provide almost no ranking information, and roughly half the total descent occurs at the first relaxed iteration | best-known ΔE/N: 0.494 (i=1) → 0.435 (i=9; 12 % of the descent) → **0.250 (i=10; 49 %)**; per-search drop across the onset median 0.165 (range 0.084–0.233) eV/atom; 84 % of the descent by i=30, 94 % by i=50; global minimum first reached at i=77; 10 of 13 searches end within 0.05 eV/atom of it, 4 within 0.02 | `analysis/exploration_performance.json` | strong (Fe/MgO only) |

**Paired caveat for SI-8 (must travel with the claim).** Fe/MgO only, and the quantities are
properties of the *search scheme*, not of any individual structure: the energies are single GPAW
steps on surrogate-relaxed candidates (residual forces ~1–2 eV/Å), the search is biased (seeded
from a flat reference layer), and iteration is an AGOX counter rather than a computational cost.

**Note on SI-7 (v2):** SI-7 still uses the flat fraction, and deliberately so. Unlike
withdrawn MT-6, it compares **one system against itself under a changed method parameter**
(rattle strength), where the sampling density is precisely the intended diagnostic — "does a
weaker perturbation still find the flat basin?". It is not a cross-system population
comparison, so the operator-matching failure that invalidates MT-6 does not apply. SI-7
remains a *method-quality* claim on Fe/MgO only.

---

## NOT claimed (explicitly excluded)

| Excluded claim | Why |
|----------------|-----|
| **B increases the fraction of flat-basin structures sampled** (withdrawn MT-6, v2) | Not a physical result: the flat fraction is a *weight* of a **biased** exploration. Cross-system comparison additionally requires a fixed exploration operator, which does not hold — Fe-Co alone uses a three-generator schedule including a `PermutationGenerator` (`data/fecomgo/main.py:75,172–175`), and the flat reference differs in kind across systems. Reportable only as a descriptive attribute of the sampled database. |
| The flat state is **"metastable"** | Not established — needs converged relaxation + Hessian + a barrier. Use "higher-energy flat basin". |
| B **lowers the Fe–O contact fraction** | Not significant under the per-atom window (p=0.106). |
| B **shrinks the lateral Fe coverage** | Dropped out under the per-atom window (p=0.967); was only significant under the loose absolute window. |
| The **Fe-B PDOS comparison** | Deferred — the Fe-B PDOS uses full d/p projections, mismatched with the femgo dz2/pz set. |
| **Quantitative energy ordering** beyond ~trend level | Structures are not DFT-converged (see limitations). |
| The dipole comparison as **isolating** the dipole energy shift | The two runs are separate searches; outcome-level only. |

---

## Method & scope (fixed)

- Search: AGOX **GOFEE** (GPR surrogate + LCB), a **biased** exploration seeded from a
  reference **flat** metal layer; only **iteration ≥ 10** used.
- **Epistemic status of the sampled data (v3).** The search returns an ***exploration*
  density, not a thermodynamic density of states**. The sampling is deliberately biased
  (seeded from a flat reference, with a phase-dependent generator mix), so the number of
  structures in a basin is **not** a physical population or weight. Only **unweighted**
  structural and energetic comparisons are admissible; basin counts may be reported as
  descriptive attributes of the sampled database only.
- **The island being the ground state despite the flat bias is a positive control** (MT-1):
  every search started from a flat reference layer and was perturbed only at small scale in
  the early phases, yet converged on an island in all four models.
- Metrics: **ΔZ** = z(metal_max) − z(metal_min) over Fe+Co [Å]; **dE/N** = (E − E_globalmin)/N
  [eV/atom] per system, global min = 0; flat/island split at ΔZ ≤ 1.0 Å.
- Level of theory: GPAW LCAO/PBE, kpts (1,1,1), vacuum 20 Å (main search).
- Systems: Fe/MgO, Fe-B/MgO, Fe-Co/MgO, Fe-Co-B/MgO.

## Limitations (must appear with the claims)

- **Structures are NOT DFT-converged** — surrogate relaxation + **1 GPAW step**; residual
  forces ~1–2 eV/Å. "Lowest energy"/"basin" = lowest DFT energy *found*.
- **Only completed searches are used (v8).** A search counts only if it reached the full 100-iteration
  budget; the rule lives in `scripts/run_selection.py` and is imported by every analysis script. It
  is applied from the **iteration number in the database, not the directory name**, because a
  `seed_*` directory can stop early. Excluded here: `femgo/stop_16` (37 it), `febmgo/seed_6`
  (no data), `fecomgo/seed_4` (10 it), `fecobmgo/seed_3` (73 it), plus the unfinished runs inside
  the sensitivity families. Unequal completed-search counts across systems (**13 / 6 / 4 / 3**) and
  across parameter settings.
- **Lattice model (v5):** both phases are built on a **bcc** Fe lattice, but experiment reports
  **bct** Fe on MgO(001) below ≈10 Å \cite{urano1988}; the island branch (ΔZ ≈ 1–6 Å) lies in
  that regime. The comparison is a trend within a fixed lattice model.
- **Basis-set completeness (v5):** LCAO basis sets are less complete than plane waves
  \cite{larsen2009}, which shifts absolute geometric parameters (e.g. the computed Fe–O
  separation, 2.30–2.33 Å, sits at the upper end of the experimental/calculated 2.0–2.3 Å
  range \cite{urano1988,butler2001}). Quantities are compared at fixed settings.
- **Strain convention is the inverse of the experimental stack (v6):** the simulation cell takes
  the Fe lattice constant and the **substrate** is compressed to match it (MgO 3.6 % relative to
  bulk, held fixed), so **the Fe film is unstrained in-plane**. In a real junction the bulk MgO
  imposes its lattice on a thin Fe film, which absorbs the mismatch and relieves it through
  interfacial dislocations \cite{yuasa2004}. The model does not represent the strained-film
  situation, and the physically inverted case has **not** been calculated.
- **The Fe-atop-O registry is partly inherited (v6):** `build_mgo_stack` places the substrate
  oxygen directly above the metal sites, so the flat film's registry follows from the
  construction as well as agreeing with the measured LEED I–V registry \cite{urano1988}. It is a
  consistency check, not an independent prediction by the search.
- **Search-level tests are resolution-limited (v8).** The permutation test partitions the pooled
  per-search flat minima, so with *a* vs *b* searches only C(a+b, a) partitions exist. For the
  Fe-Co vs Fe-Co-B pair (4 vs 3) that is 35 partitions, i.e. a floor of p = 0.029: **the Fe-Co-host
  boron effect cannot reach significance on this data however it falls.** Reported p-values are
  therefore lower bounds on what further searches could establish, and MT-4 is under-powered
  rather than refuted. `analysis/ensemble_stats.json` records `perm_n_partitions` and
  `perm_resolution` for every comparison.
- **The permutation test was mis-implemented before v8** (two independent permutations instead of
  one split), which widened the null and inflated significance (e.g. MT-3 read p = 0.005 instead of
  p = 0.045). Fixed in v8.
- ΔZ ≤ 1.0 Å flat cutoff is a chosen threshold.
- kpts = (1,1,1), single-layer slabs → qualitative/trend-level.
- **Sensitivity families contain unfinished searches (v7; superseded by the v8 rule):** several
  runs were stopped early (iteration max 6–90 vs 100 for a completed search) and their per-seed
  best is systematically worse, and the unfinished runs are not distributed evenly across settings.
  v8 excludes them everywhere. The reduced-rattle arms retain only **2 and 4** completed searches,
  so their magnitudes are weak even though the direction is clear.

---

## Discussion-only interpretations (not results claims)

These are interpretive framings permitted in the Discussion; they do **not** add results
claims to MT/SI and do not change the frozen list.

- **Flat ↔ amorphous, island ↔ crystalline mapping.** The flat film is read as the
  disordered/amorphous-like configuration and the island as the ordered/crystalline-like
  one.
- **Greer confusion principle** \cite{greer1993}: the flat/disordered configuration is
  claimed to be stabilised by added elements, in the spirit of the confusion principle
  (more elements frustrate crystallisation and favour the disordered configuration).
  **Data bound (added 2026-09-17; Discussion-only wording, no MT/SI claim changed):** the
  supported driver is the *presence of boron*, not the element count. Adding Co alone
  raises the flat-basin energy (MT-5, 0.1888 → 0.1941 eV/atom), and the two two-element
  systems differ more from each other (Fe-B 0.1493 vs Fe-Co 0.1941) than Fe-Co does from
  three-element Fe-Co-B (0.1494). The principle is retained as acting through the added
  metalloid, not through complexity counting. Honest bound retained: even the boron-bearing
  models keep the island as ground state, so the principle stabilises but does not fully
  suppress the ordered configuration in these models.
- **Phase-separation wording (added 2026-09-17, v3).** Boron is described as changing the
  **flat–island separation**, not as stabilising the flat phase or destabilising the island
  individually. Because each model is referenced to its own lowest energy, a reduced
  separation is consistent with either. Resolving it would require an absolute (cross-system)
  energy reference and/or a converged treatment of both basins. Permitted in Results §2.3 and
  Discussion §3.2; it is wording, not a results claim.
- **Experimental correspondence (added 2026-09-17, v5).** The flat and island basins are mapped
  onto the two growth outcomes reported for Fe on MgO(001): room-temperature deposition gives
  3D islands (suppressed only at 140 K) \cite{fahsold2000} and Volmer–Weber clusters at 5 ML
  \cite{reitinger2007}, whereas a flat pseudomorphic monolayer is obtained by slow deposition on
  a cleaved, oxygen-annealed crystal \cite{urano1988}. **Scope bound (must travel with it):**
  this is a correspondence between *structural configurations*, not between energies — the
  experimental growth mode is also governed by kinetics, so the experiment neither confirms nor
  refutes the calculated energy ordering.

## Sign-off

- [x] **MT-1 … MT-5, MT-7 approved** (main text) — scientist (2026-09-16)
- [x] **SI-1 … SI-7 approved** (supplementary) — scientist (2026-09-16)
- [x] **Exclusions confirmed** — scientist (2026-09-16)
- [x] Contribution sentence approved (2026-09-16)
- [x] **MT-6 withdrawn and moved to the excluded list** (v2, 2026-09-17) — scientist
- [x] **MT-8 added** (main text, v3, 2026-09-17) — scientist
- [x] **MT-4 flagged CHALLENGED, to be reported as a trend pending more Fe-Co searches**
      (v3, 2026-09-17) — scientist
- [x] **Method & scope: exploration-density principle + positive-control framing** (v3,
      2026-09-17) — scientist
- [x] **Discussion-only: phase-separation wording** (v3, 2026-09-17) — scientist
- [x] **SI-8: performance of the biased exploration** (v4, 2026-09-17) — scientist
- [x] **v5: bcc/bct lattice-model limitation, basis-set limitation, experimental-correspondence
      framing, six verified Fe/MgO references** (2026-09-17) — scientist

**Status: FROZEN (v5, 2026-09-17).** This list is frozen for drafting. Any new result or claim
requires an explicit update to this file before it enters a section.
**Version history:** v1 (2026-09-16) initial frozen list · v2 (2026-09-17) MT-6 withdrawn ·
v3 (2026-09-17) MT-8 added, MT-4 flagged challenged, exploration-density principle ·
v4 (2026-09-17) SI-8 added · v5 (2026-09-17) lattice-model + basis-set limitations,
experimental-correspondence framing, six verified Fe/MgO references · v6 (2026-09-17) SI-3
restated (strain relief dropped for reduced forced coupling + restored metal cohesion),
SI-4 reframed as a consistency check, strain-convention limitation added, torelii2009
added to the experimental-correspondence evidence · v7 (2026-09-17) truncated searches found in
the method-sensitivity families; SI-5/6/7 evidence cells restated on an equal-iteration primary
statistic; "kappa = 1 is best" retracted; rattle factor 5× → 7× · v8 (2026-09-17) completed
searches only, project-wide (run_selection.py); a mis-implemented permutation test fixed;
MT-3/MT-4/MT-5 p-values 0.045 / 0.092 / 0.245; MT-7 and MT-8 evidence updated; MT-4 character
changed from refuted to under-powered (status flag left for the scientist).
