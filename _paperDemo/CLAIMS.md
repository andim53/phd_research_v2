# CLAIMS.md — FROZEN claim list (v11)

**Status: FROZEN (v11, 2026-09-17).** Supersedes v10, v9, v8, v7, v6, v5, v4, v3, v2 and v1.
**Project:** `_paperDemo` · **Venue:** TBD (format-agnostic)

**Scope of the paper (v9): the Fe host only — Fe/MgO and Fe-B/MgO.** The Fe-Co/MgO and Fe-Co-B/MgO
models are **archived out of scope** (see "ARCHIVED — out of scope" below). No section may cite
them. The Co-containing numbers that v8 carried in MT-4, MT-5, MT-7, MT-8 and the combined 2×2
statement are **withdrawn from the paper, not from the record** — the measurements stand, they are
no longer in scope. Archive: `_archive/cofe/README.md`; raw data under `data/_archive/`.

## OPEN — awaiting scientist sign-off (2026-09-17)

Items that are **not** settled. They are listed here so a fresh session does not treat the frozen
list as fully accepted.

1. **Acceptance of the significance test as it now stands (v8 + v9).** The test has been revised
   twice: v8 replaced two independent permutations of the pooled minima with one split (+1
   correction), and v9 replaced the Monte-Carlo draw with **exact enumeration of every partition**,
   because the Monte-Carlo p-value was found to move with the RNG stream — it read 0.0452 or 0.0480
   for the same data depending on whether the archived Co systems had been analysed first, which a
   published number must not do. MT-3 is now **p = 0.0444, exact** (0.005 → 0.045 → 0.0444 across
   the three versions). Both revisions should be consciously accepted rather than inherited.
2. **NEW v9 — the third-element control is gone.** The Co models are what let the paper say the
   driver is *boron* rather than *any added element*. Fe vs Fe-B alone cannot separate "boron does
   this" from "an added element does this". Recorded as a stated scope bound in the Limitations.
   The scientist confirmed the Greer wording stays on the boron-only argument (see
   "Discussion-only interpretations").
3. **NEW v9 — application framing.** The CoFeB/MgO stack is the device-relevant system, while the
   paper now studies Fe/MgO only. `03_discussion.md` §3.3 no longer names CoFeB — it says "MgO-based
   tunnel junctions" — so this is live: restore a CoFeB sentence (with a genuine reference) or keep
   the general framing. Either way, no Co *host* is discussed.
4. **NEW v10 — SI-9 and SI-10 need sign-off** (the iteration-budget and lattice-constraint
   studies, both boron-free by design).
5. **NEW v10 — how to word the convergence bound in the sections.** The item held since v4 ("the
   searches are still improving at iteration 100") is now answered with numbers by SI-9, and it is
   written into the Limitations as evidence. Whether §1.6 and §3.4 should *state* it (with the SI
   reference), and in what form, is the scientist's call — Options: (a) one sentence in §1.6 plus a
   pointer to §S4; (b) also a sentence in §3.4; (c) leave the sections as they are and rely on the SI.

## RESOLVED by v10

- **The convergence caveat held since v4 is answered** by SI-9 and now written into the Limitations:
  the *absolute* reference energy is still improving at 100 iterations, while the *comparison*
  (island ground state, flat–island separation) is unchanged or slightly reinforced at 200–600
  iterations. What remains open is only the wording in the sections (OPEN item 5).
- **The physically inverted strain case** is no longer "not calculated" for the boron-free model:
  SI-10's far end puts the substrate at the experimental MgO lattice constant and stretches the
  film 3.92 %, and the result is unchanged.

## RESOLVED by v9 (items held open in v8)

- **Strain convention across the model pairs — RESOLVED BY SCOPE.** Fe and Fe-B both sit on
  `a_Fe = 2.87019 Å` (`interpolation_factor` 0); the +4.9 % film-stretched convention belonged to
  the archived Fe-Co pair only. The cross-pair confound that threatened MT-3/MT-4/MT-5 no longer
  exists inside the paper's scope. The **absolute** convention — substrate compressed 3.6 %,
  film unstrained, the inverse of the experimental stack — remains a stated limitation (below).
- **MT-4's status — RESOLVED BY ARCHIVING.** It was flagged CHALLENGED and re-characterised in v8 as
  under-powered at 4 vs 3 completed searches (p = 0.092, floor 0.029). It is archived with its host;
  the resolution limit it ran into does not apply to any surviving comparison (MT-3's 13 vs 6 admits
  27 132 partitions, floor p = 3.7×10⁻⁵).

## v11 changelog (2026-09-17) — the inverted stack (MgO on Fe) as a qualified finding (SI-11)

Scientist's instruction: *"I added a new data. The mgofe, comparing the mgo on fe system. Include
that analysis into the supplementary materials."* `data/mgofe` is the **inverted stack** — an MgO
film deposited on an Fe substrate (Fe25Mg25O25, cell = a_Fe = 2.866 Å experimental, a_MgO = 4.212 Å
experimental, interpolation_factor 0, 100 iterations, same two-generator GOFEE scheme, 5 completed
searches seed_0..4, seed_5 stopped at 26 and excluded).

**Ground state (the comparison being made).** The ground state of the inverted stack is a **flat MgO
film** (ΔZ over MgO = 0.39 Å), lying **0.016 eV/atom below** the corresponding island — the opposite
of Fe-on-MgO, whose ground state is an **island** (ΔZ = 3.65 Å) with the flat film 0.189 eV/atom
above it. The sign of the wetting preference inverts between the two stacks.

**Caveat (the reason this is qualified).** The inverted-stack searches **do not converge at the
100-iteration budget**, so the comparison is indicative rather than settled. The per-run evidence is
kept in `analysis/mgo_on_fe.json`; the manuscript states it at the run-set level only. The structures
are physically sound (min interatomic distance 1.6–2.0 Å), so this is under-convergence, not a broken
calculation.

**Decision (scientist, 2026-09-17):** report it as a **ground-state comparison** — a qualified
finding, not a clean claim. The flatness metric is over the **deposited film** in each stack (Fe for
femgo, MgO for mgofe), so the comparison is apples-to-apples on wetting. New analysis:
`scripts/mgo_on_fe.py` → `analysis/mgo_on_fe.{json,csv}`, `figures/mgo_on_fe.png`. Drafted as §S6
of `sections/SI.md` (v8). **SI-11 is a qualified/weak claim and must be read with its paired
caveat.**

## v10 changelog (2026-09-17) — two new robustness studies in the SI (SI-9, SI-10)

Scientist's instruction: *"I've included new data. extraIteration and latt_conc. Include their
analysis into the Supplementary Material. It was testing the impact of additional Iteration onto the
over the MT finding, and also, the impact of the constraint, where previously, we match to the Fe,
but now, we also match it to the MgO (not that it's an experimental MgO lattice)."*

Two new Fe/MgO studies, both **boron-free**, so both bound the structural result (MT-1, MT-2) and the
project's stated limitations rather than the boron effect (MT-3). New analysis:
`scripts/iteration_budget.py`, `scripts/lattice_constraint.py`; outputs
`analysis/iteration_budget.{json,csv}`, `analysis/lattice_constraint.{json,csv}`; figures
`figures/iteration_budget.png`, `figures/lattice_constraint.png`.

### SI-9 — the comparison does not depend on the search budget

`data/extraIteration/{0_200Iter,1_400Iter,2_600Iter}` is the **same calculation** as the main-text
Fe/MgO model — `diff data/femgo/main.py extraIteration/0_200Iter/main.py` is a single line,
`N_iterations` 100 → 200 — run to 200, 400 and 600 iterations. 6 + 7 + 4 completed searches.

- **The island is the ground state in all 17 searches at the 100-iteration cut and in all 17 at the
  full budget.**
- **The flat–island separation never shrinks with a longer budget:** it is unchanged in 5 of 17
  searches and larger in 12, by a median of **+0.0104 eV/atom** (range 0 to **+0.0268**). Pooled per
  arm it goes 0.1901 → 0.1901 (200 it), 0.1624 → 0.1662 (400 it), 0.1807 → 0.1978 eV/atom (600 it).
- **The absolute minimum is *not* converged at 100 iterations:** 12 of 17 searches find a lower
  island with more iterations, by a median of **0.0013 eV/atom** (range 0 to 0.0071). It is the
  *comparison* that is budget-insensitive, not the absolute energy.
- The per-run 100-iteration windows reproduce the main-text reference exactly (pooled flat-basin
  minimum **0.1888 eV/atom**, island ground state) when the same 13 completed searches are read
  through this script.

### SI-10 — the result does not depend on which phase sets the in-plane lattice

`data/latt_conc/{3_latt_025,2_latt_075,4_latt_100}` moves the constraint,
`a_custom = a_Fe + f·(a_MgO/√2 − a_Fe)`, with both the film and the substrate built on `a_custom`:
at *f* = 0.25 the substrate is compressed 2.83 % and the film stretched 0.98 %; at *f* = 0.75,
−0.94 % / +2.94 %; at *f* = 1.00 the substrate is at the experimental MgO lattice constant
(4.212 Å as used) and the film is stretched 3.92 %. 10 + 10 + 5 completed searches.

- **The island is the ground state in all 25 searches**, and in every arm.
- **The flat-basin minimum is flat against the constraint:** pooled, 0.1932 (f = 0.25), 0.1982
  (f = 0.75), 0.1907 eV/atom (f = 1.00), against **0.1888 eV/atom** for the main-text Fe-matched
  model — a total spread of **0.0094 eV/atom** across the whole sweep. The within-arm search-to-search
  scatter is 0.017–0.031 eV/atom, i.e. 2–3× the entire sweep effect.
- **Scope:** boron-free, so this bounds MT-1/MT-2 and the strain-convention limitation. For scale,
  the constraint moves the separation by about a quarter of the boron effect (0.040 eV/atom).

### The held convergence caveat is now written in

Since v4 an item has been *held, not written in*: "the searches are still improving at iteration
100, so the per-model reference energies are not converged with respect to search length." SI-9
answers the part of it that matters for this paper and it is now a stated limitation with numbers:
the absolute reference energy keeps drifting (median 0.0013 eV/atom over a doubling of the budget),
while the flat–island comparison is unchanged or slightly reinforced. **The scientist's decision on
how to word this in §1.6/§3.4 is still needed** — see OPEN.

### Out of scope in these studies

- The **f = 0 and f = 0.5 arms** of the constraint sweep: f = 0 is a reference arm the scientist does
  not want in the paper (`_archive/latt_conc/0_latt_0`), and `_archive/latt_conc/1_latt_1` is an
  empty directory, so the sweep is reported at 0.25 / 0.75 / 1.00 with the paper's own Fe/MgO model
  as the Fe-matched reference.
- **The a_Fe difference:** the sweep uses `a_Fe = 2.866 Å`, while the main-text model uses
  `2.87019 Å`. The two are therefore not the same run set and differ by 0.15 % in the cell; this is
  stated with the reference point rather than smoothed over.
- **a_MgO = 4.212 Å is the experimental MgO lattice constant** (4.2112 Å nominal) used as a fixed
  reference, and **a_Fe = 2.866 Å is the experimental bcc-Fe lattice constant** — both cited in §S5
  (\cite{pietrokowsky1966}, \cite{swanson1953}). Neither is a computed value, and using them is not a
  claim that the model reproduces an experimental stack.
- Runs that stopped early are excluded in both studies (constraint arm: `seed_113` at 12 and 40
  iterations, `seed_107` at 10, `seed_109` at 62; the budget arms had none).

## v9 changelog (2026-09-17) — the Co host is archived; the paper becomes Fe/MgO vs Fe-B/MgO

Scientist's instruction: *"archive the current CoFe host results, considering it has so many
problem. For now, write the main and supplementary based on the Fe host, with and without B."*
Executed as a scope restriction plus a contribution rewrite — **no measurement was retracted**.

### 1. What left the paper

**MT-4** (B lowers the flat-state energy in the Fe-Co host) and **MT-5** (Co alone has little
effect) are archived, together with the combined 2×2 statement they formed with MT-3. Their
evidence was real, so the reason for archiving is not refutation — it is three defects that
made the pair unusable as the paper's second host:

1. **Strain confound.** Fe-Co and Fe-Co-B sat on `a_MgO/√2 = 2.97833 Å` (film stretched 4.9 %)
   while Fe and Fe-B sat on `a_Fe = 2.87019 Å` (substrate compressed 3.6 %). The cross-host
   comparison therefore varied boron and the strain convention together.
2. **Under-powered.** 4 vs 3 completed searches admit only 35 partitions of the pooled replicate
   minima, so the Fe-Co-host boron effect could not reach p < 0.029 however the data fell
   (v8: p = 0.092, median shift +0.048 eV/atom, 92 % same-sign — under-powered, not absent).
3. **Unmatched exploration operator.** `data/fecomgo/main.py:75,172–175` adds a third
   `PermutationGenerator` to the schedule used by the other three models, so the Co host is not a
   clean counterfactual either.

### 2. What the scope restriction changes inside the surviving claims

- **Contribution sentence rewritten** — no host independence, no Co, no CoFeB alloying claim.
- **MT-1** now covers two systems: global-min ΔZ = 3.65 (Fe) / 3.77 Å (Fe-B).
- **MT-3 unchanged in value and untouched by the archive, and now on firmer statistical ground:**
  0.1888 → 0.1493 eV/atom (−0.040), **p = 0.0444 exact** at 13 vs 6 completed searches, against a
  permutation floor of 3.7×10⁻⁵ (27 132 partitions) instead of the 4-vs-3 floor of 0.029 that
  limited v8. The p-value's move from 0.045 is the exact test of §4, not a change in the data.
- **MT-7 evidence halved** — windowed Fe-B only: 1 of 72 structures in-window, max contact
  fraction 0.33, 101 of the remaining 471 outside. The Fe-Co-B half (1 of 21; max 0.5; 25 of 252;
  "20 of the 21 from one search") and its two-completed-search caveat are archived with it.
- **MT-8 counts shrink** — flat 2 / 2 motifs, island 2 / 2 (was 2/2/4/2 and 2/2/3/1); within-set
  fingerprint distance 0.41–0.44 × the branch random-pair scale (was 0.37–0.71). The paired
  caveat is unchanged.
- **SI-1 … SI-8 are untouched.** Every SI section was already Fe/MgO-only — §S1 and §S3 run on the
  `femgo` baseline, §S2 on `dos_femgo_flatngs` + `analysis/interface_analysis.csv`. No SI number,
  figure or claim moves. `sections/SI.md` contains zero references to the Co host.
- **Scope of the search-replica rule** — `run_selection.py` still governs (`femgo/stop_16` 37 it,
  `febmgo/seed_6` empty), and the two Co exclusions (`fecomgo/seed_4` 10 it, `fecobmgo/seed_3`
  73 it) move out of the paper's Methods list into the archive record.

### 3. What this costs, stated plainly

The paper loses its generality claim ("independent of the host metal") and its only third-element
control: Fe vs Fe-B cannot distinguish "boron does this" from "an added element does this". This is
recorded as a limitation, and the Greer framing is kept on the boron-only argument (scientist's
decision) rather than on an element-count contrast that is no longer measurable here.

### 4. The significance test is now exact, and no longer scope-dependent

Re-running the analysis to confirm that the scope change reproduces the frozen numbers exposed a
**third defect in the significance test** (after v8's mis-implemented permutation):

- The bootstrap CIs and the Monte-Carlo permutation p drew from the **shared module RNG**, whose
  stream position depends on how many systems were processed before. Loading the archived Co
  systems first therefore moved the paper's headline p-value: **0.0452 (Fe host alone) vs 0.0480
  (all four systems)** for the same twelve numbers. A reported statistic must not depend on the
  script's scope.
- Both are now fixed: each effect seeds its own bootstrap generator, and the permutation test
  **enumerates every partition of the pool exactly** (27 132 for 13 vs 6; 35 for 4 vs 3; 2380 for
  13 vs 4) instead of sampling 5000 of them. The p-value is deterministic, seedless, and reaches
  the resolution `perm_resolution` advertises rather than an approximation of it.

| comparison | v8 (Monte-Carlo, shared RNG) | **v9 (exact enumeration)** |
|---|---|---|
| B in Fe host — MT-3, 13 vs 6 | p = 0.0452 (0.0480 if the Co systems were loaded) | **p = 0.04438** |
| B in Fe-Co host — archived MT-4, 4 vs 3 | p = 0.0924 | p = 0.08571 |
| Co alone — archived MT-5, 13 vs 4 | p = 0.2454 | p = 0.23571 |

MT-3's conclusion is unchanged (p < 0.05 on both versions). The v8 changelog's 0.045 / 0.092 /
0.245 stand as the record of what v8 reported. Verified: the Fe-host p is **byte-identical**
whether the script is run in scope or with `--all-systems`.

### 5. MT-6 stays withdrawn, with one reason reworded

Its **secondary** v2 reason — `data/fecomgo/main.py`'s third generator breaking operator matching —
no longer applies, since the Co host is out of scope and Fe/Fe-B share their schedule. The
**primary** reason stands and is sufficient: a flat-basin *fraction* from a deliberately biased
exploration is a sampling weight, not a physical population. MT-6 remains withdrawn.

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

> **Boron insertion lowers the relative energy of the flat metal-film wetting state of Fe on
> MgO(001) by ~0.04 eV/atom (0.1888 → 0.1493 eV/atom, two-sided permutation p = 0.045 over
> 13 vs 6 completed searches), moving the flat, well-wetting configuration closer to the island
> ground state without displacing it — relevant to interface flatness in MgO-based magnetic
> tunnel junction stacks.**

*Rewritten in v9: the v8 sentence claimed host independence and rested on the archived Co host.
This version needs the scientist's re-sign-off.*

---

## Main-text claims

| ID | Claim | Exact value | Source | Confidence |
|----|-------|-------------|--------|-----------|
| **MT-1** | The lowest-energy structure found is an **island** (not flat) in both systems | global-min ΔZ = 3.65 Å (Fe) / 3.77 Å (Fe-B) | `analysis/pes_structures.csv` | strong |
| **MT-2** | The **flat configuration is a distinct, higher-energy basin** (not the ground state) | flat-basin min dE/N > 0 in both systems (0.1888 Fe / 0.1493 eV/atom Fe-B) | `analysis/pes_structures.csv` | strong |
| **MT-3** | **B lowers the flat-state energy in the Fe host** | 0.1888 → 0.1493 eV/atom (−0.040) | `analysis/pes_structures.csv` | strong (two-sided permutation p = **0.0444**, **exact** over all 27 132 partitions at 13 vs 6 completed searches — the floor is 3.7×10⁻⁵, so the test is not resolution-limited here. The p-value was 0.045 under v8's Monte-Carlo test and 0.005 under the mis-implemented test before it — see v9 §5 and v8) |
| ~~MT-4~~ | ~~B lowers the flat-state energy in the Fe-Co host~~ | **ARCHIVED in v9** with the Co host — see "ARCHIVED — out of scope" | — | — |
| ~~MT-5~~ | ~~Co alone has little effect on the flat-state energy~~ | **ARCHIVED in v9** with the Co host — see "ARCHIVED — out of scope" | — | — |
| ~~MT-6~~ | ~~B increases the fraction of flat-basin structures sampled~~ | **WITHDRAWN in v2** — see changelog | — | — |
| **MT-7** | **B does not bond to the MgO interface** (stays in the metal film) | B_contact_frac ≈ 0 in the low-energy window dE/N ≤ 0.05 eV/atom (**1 of 72** Fe-B structures; max contact fraction **0.33**). Outside the window **101 of the remaining 471** Fe-B structures *do* have a B–O contact, so the claim is window-restricted, not global. Window defined by `scripts/wetting_metrics.py --e-window-per-atom 0.05` | `analysis/pes_structures.csv` | moderate (windowed) |
| **MT-8** | The low-energy structures of each branch form a **small set of recurring motifs** rather than one repeated structure; ΔZ is **continuous**, with no discrete island heights | Island branch spans ΔZ ≈ 1–6 Å (no quantisation); low-energy sets split into a small number of single-linkage motifs (**flat 2 / 2, island 2 / 2**); within-set fingerprint distance is **0.41–0.44 ×** the branch's random-pair scale; Fe/MgO's 5 lowest flat structures (from 5 independent searches) fall into 2 motifs, 4 in the dominant one | `analysis/ensemble_stats.json` | moderate — see paired caveat |

**The v8 combined 2×2 statement (MT-3/4/5) is withdrawn in v9** — two of its three legs belong to
the archived Co host. What remains is a single B effect in one host (MT-3, −0.040 eV/atom).
**Note:** MT-6 (flat-basin sampling fraction) is withdrawn in v2, on the primary ground that a
sampling weight from a biased exploration is not a physical population. Its secondary v2 reason —
an unmatched exploration operator in `data/fecomgo` — no longer applies inside the v9 scope, since
Fe and Fe-B share their generator schedule; the primary reason stands on its own.

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
| **SI-9** *(v10)* | **The main-text comparison does not depend on the search budget** — a longer search leaves the island the ground state and does not shrink the flat–island separation, although the absolute energy keeps improving | same calculation at 200 / 400 / 600 iterations (`N_iterations` is the only difference): **island ground state in 17 of 17 searches** at both the 100-iteration cut and the full budget; separation **unchanged in 5, larger in 12** of 17 (median **+0.0104**, range 0 to **+0.0268** eV/atom); pooled per arm **0.1901 → 0.1901**, **0.1624 → 0.1662**, **0.1807 → 0.1978** eV/atom. Absolute minimum **still improving**: 12 of 17 searches find a lower island (median **0.0013**, range 0 to 0.0071 eV/atom) | `analysis/iteration_budget.json`, `analysis/iteration_budget.csv`, `figures/iteration_budget.png` | strong (Fe/MgO, boron-free; n = 6 / 7 / 4) |
| **SI-10** *(v10)* | **The structural result does not depend on which phase sets the in-plane lattice** — moving the mismatch off the substrate and onto the film leaves the island the ground state and the flat-basin minimum unchanged | cell `a = a_Fe + f(a_MgO/√2 − a_Fe)` (substrate strain / film strain): f = 0.25 (**−2.83 % / +0.98 %**), 0.75 (**−0.94 % / +2.94 %**), 1.00 (**0.00 % / +3.92 %**). **Island ground state in 25 of 25 searches.** Flat-basin minimum pooled per arm: **0.1932 / 0.1982 / 0.1907 eV/atom** against **0.1888** for the main-text Fe-matched model — total spread **0.0094 eV/atom**, against a within-arm search-to-search SD of 0.017–0.031 eV/atom | `analysis/lattice_constraint.json`, `analysis/lattice_constraint.csv`, `figures/lattice_constraint.png` | strong (Fe/MgO, boron-free; n = 10 / 10 / 5) |
| **SI-11** *(v11; QUALIFIED — weak)* | **The ground state of the inverted stack (MgO film on an Fe substrate) is a flat MgO film — the opposite of Fe-on-MgO, whose ground state is an island** | MgO film on Fe substrate (Fe25Mg25O25, cell = a_Fe = 2.866 Å): the ground state is a **flat MgO film** (ΔZ over MgO = **0.39 Å**), and the flat film lies **0.016 eV/atom below** the corresponding island. Fe-on-MgO for contrast: ground state is an **island** (ΔZ = 3.65 Å) and the flat film lies **0.189 eV/atom above** it. The sign of the wetting preference inverts between the two stacks. The inverted-stack searches do not converge at the 100-iteration budget, so the comparison is indicative rather than settled | `analysis/mgo_on_fe.json`, `analysis/mgo_on_fe.csv`, `figures/mgo_on_fe.png` | **weak** (ground-state comparison; inverted stack not converged; n = 5) |
| **SI-8** *(v4; signed off 2026-09-17)* | **The onset of relaxation is the pivot of the biased search**: the pre-relaxation iterations provide almost no ranking information, and roughly half the total descent occurs at the first relaxed iteration | best-known ΔE/N: 0.494 (i=1) → 0.435 (i=9; 12 % of the descent) → **0.250 (i=10; 49 %)**; per-search drop across the onset median 0.165 (range 0.084–0.233) eV/atom; 84 % of the descent by i=30, 94 % by i=50; global minimum first reached at i=77; 10 of 13 searches end within 0.05 eV/atom of it, 4 within 0.02 | `analysis/exploration_performance.json` | strong (Fe/MgO only) |

**Paired caveat for SI-8 (must travel with the claim).** Fe/MgO only, and the quantities are
properties of the *search scheme*, not of any individual structure: the energies are single GPAW
steps on surrogate-relaxed candidates (residual forces ~1–2 eV/Å), the search is biased (seeded
from a flat reference layer), and iteration is an AGOX counter rather than a computational cost.

**Paired caveat for SI-9 (must travel with the claim).** Fe/MgO **and boron-free**: this bounds the
structural result (MT-1, MT-2), not the boron effect (MT-3), for which no longer-budget run exists.
The budget arms are independent run sets rather than truncations of one another — the same seed can
follow a different trajectory in different arms (checked: only 2 of 7 seeds share their first-100
trajectory across arms) — so the arm-level numbers carry that mixture while the **per-run**
100-versus-full comparison does not. Run counts are unequal (6 / 7 / 4).

**Paired caveat for SI-10 (must travel with the claim).** Fe/MgO **and boron-free**, for the same
reason as SI-9. The sweep is measured at 0.25 / 0.75 / 1.00 with the paper's own Fe/MgO model as the
Fe-matched reference: the f = 0 and f = 0.5 arms are out of scope by decision (`1_latt_1` is an empty
directory). The two endpoints of the sweep are the **experimental lattice constants** of the two bulk
phases — bcc α-Fe, *a* = 2.866 Å \cite{pietrokowsky1966}, and rocksalt MgO, *a* = 4.2112 Å
\cite{swanson1953} (4.212 Å as used) — so the far end places the substrate at the experimental MgO
lattice constant, the convention of the experimental stack. The sweep's `a_Fe = 2.866 Å` (experimental)
differs from the main-text model's *computed* `2.87019 Å` by 0.15 %, so the Fe-matched reference is
the paper's own model rather than a sweep arm. The substrate is still a single layer and the film
about one monolayer, so it is the constraint that is inverted, not the full experimental geometry.

**Paired caveat for SI-11 (must travel with the claim — this is a QUALIFIED finding, not a clean
claim).** This is a **ground-state comparison**. The inverted-stack searches **do not converge at the
100-iteration budget**, so the comparison is indicative rather than settled; the per-run evidence
behind that statement is kept in `analysis/mgo_on_fe.json` and is not restated in the manuscript. The
structures are physically sound (smallest interatomic distance 1.6–2.0 Å), so this is under-
convergence, not a broken calculation, and the gap between the flat film and the island on the
inverted stack is marginal (**0.016 eV/atom**). The flatness metric is over the **deposited film** in
each stack (Fe for femgo, MgO for mgofe), so the comparison is apples-to-apples on wetting, but the
inverted-stack side is not converged. **Boron-free**, so it bounds the structural result only. To
become a real result the inverted stack would have to be run to convergence.

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
| **B increases the fraction of flat-basin structures sampled** (withdrawn MT-6, v2) | Not a physical result: the flat fraction is a *weight* of a **biased** exploration, so a cross-system comparison of weights is not admissible — the primary reason, and sufficient on its own. *(v9 note: the secondary v2 reason — that the Fe-Co operator differed, `data/fecomgo/main.py:75,172–175`, and that the flat references differ in kind — no longer applies inside the v9 scope, where Fe and Fe-B share one generator schedule and one flat reference construction. The withdrawal is unchanged.)* Reportable only as a descriptive attribute of the sampled database. |
| The flat state is **"metastable"** | Not established — needs converged relaxation + Hessian + a barrier. Use "higher-energy flat basin". |
| B **lowers the Fe–O contact fraction** | Not significant under the per-atom window (p=0.106). |
| B **shrinks the lateral Fe coverage** | Dropped out under the per-atom window (p=0.967); was only significant under the loose absolute window. |
| The **Fe-B PDOS comparison** | Deferred — the Fe-B PDOS uses full d/p projections, mismatched with the femgo dz2/pz set. |
| **Quantitative energy ordering** beyond ~trend level | Structures are not DFT-converged (see limitations). |
| The dipole comparison as **isolating** the dipole energy shift | The two runs are separate searches; outcome-level only. |

---

## ARCHIVED — out of scope (v9)

The Fe-Co/MgO and Fe-Co-B/MgO models are **out of the paper's scope**. This is not a refutation:
the measurements below are valid as measured and are kept here so the record survives the scope
change. Machine-readable copy of these numbers: `_archive/cofe/cofe_evidence.json`; narrative and
evidence trail: `_archive/cofe/README.md`; raw data: `data/_archive/fecomgo/`, `data/_archive/fecobmgo/`.

**Archived claims (were MT-4 and MT-5 in v8), with their frozen values:**

| was | claim | value as measured | source | why archived |
|---|---|---|---|---|
| MT-4 | B lowers the flat-state energy in the Fe-Co host | 0.1941 → 0.1494 eV/atom (−0.045); two-sided permutation **p = 0.092** at 4 vs 3 completed searches (v8, Monte-Carlo; **p = 0.0857** under the exact enumeration of v9 §4); median shift +0.048 eV/atom; 92 % same-sign | `_archive/cofe/cofe_evidence.json` → `effects/B_in_FeCo_host` | strain confound + under-powered (floor 0.029) + unmatched generator schedule |
| MT-5 | Co alone has little effect on the flat-state energy | 0.1888 → 0.1941 eV/atom (+0.005); p = 0.245 at 13 vs 4 completed searches (v8, Monte-Carlo; **p = 0.2357** exact) | `_archive/cofe/cofe_evidence.json` → `effects/Co_alone` | rests on the archived Fe-Co model; the "little effect" null is not re-established here |

**Combined 2×2 statement (v8, withdrawn):** B effect −0.040 (Fe) and −0.045 (Fe-Co); Co effect
+0.005 (no B) — B the dominant lever, Co not.

**Also archived with them:** the Fe-Co-B half of MT-7's evidence (1 of 21 windowed structures, max
contact fraction 0.5, 25 of the remaining 252 outside the window, and its "20 of 21 from one
search / only 2 completed searches" caveat); the four-system motif counts of MT-8 (the v8 range
0.37–0.71 × random-pair scale, which the Co systems drove); the excluded runs `fecomgo/seed_4`
(stopped at iteration 10) and `fecobmgo/seed_3` (stopped at 73) as *paper* Methods content — they
remain excluded by `run_selection.py` wherever the scripts are still asked to compute those
systems; and the v8 permutation-resolution limitation (4 vs 3 → 35 partitions → floor p = 0.029),
which no surviving comparison runs into.

**Why the host is not a clean counterfactual.** Three independent defects, any one of which would
warrant the restriction: (1) **strain convention** — the Co pair sat on `a_MgO/√2 = 2.97833 Å`
(film stretched 4.9 %) while the Fe pair sat on `a_Fe = 2.87019 Å` (substrate compressed 3.6 %),
so boron and the strain convention varied together; (2) **statistical power** — 4 vs 3 completed
searches cannot reach p < 0.029; (3) **exploration operator** — `data/fecomgo/main.py:75,172–175`
adds a third `PermutationGenerator` to the schedule the other three models share.

**To revive the Co host** (for the separate study): re-run both Co models at `interpolation_factor`
0 so all four share `a_Fe`, to a full 100-iteration budget, on the two-generator schedule — then
the 2×2 can be restored as written in v8, with MT-4/MT-5 reinstated from this block.

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
  the early phases, yet converged on an island in both models.
- Metrics: **ΔZ** = z(metal_max) − z(metal_min) over the film's **Fe** atoms [Å] (boron is not
  part of the flatness metric — `pes_analysis.METAL = ('Fe','Co')`); **dE/N** = (E − E_globalmin)/N
  [eV/atom] per system, global min = 0; flat/island split at ΔZ ≤ 1.0 Å.
- Level of theory: GPAW LCAO/PBE, kpts (1,1,1), vacuum 20 Å (main search).
- **Systems (v9): Fe/MgO and Fe-B/MgO only** — 13 and 6 completed searches, 1723 structures.
  Fe-Co/MgO and Fe-Co-B/MgO are archived (see "ARCHIVED — out of scope").
- **Supplementary method studies (all Fe/MgO, 100-iteration budget unless stated):** the
  exploration-performance study (§S1, the main-text searches), the PDOS/interface study (§S2),
  the parameter families rattle / kappa / dipole (§S3, `data/param_ratt*`, `data/femgo_kappa/*`,
  `data/femgo_dip`), the **iteration-budget study (§S4, v10; `data/extraIteration/*` at 200/400/600
  iterations)** and the **lattice-constraint study (§S5, v10; `data/latt_conc/*` at f = 0.25/0.75/
  1.00)**. The last two are boron-free and bound MT-1/MT-2, not MT-3.

## Limitations (must appear with the claims)

- **Structures are NOT DFT-converged** — surrogate relaxation + **1 GPAW step**; residual
  forces ~1–2 eV/Å. "Lowest energy"/"basin" = lowest DFT energy *found*.
- **Only completed searches are used (v8).** A search counts only if it reached the full 100-iteration
  budget; the rule lives in `scripts/run_selection.py` and is imported by every analysis script. It
  is applied from the **iteration number in the database, not the directory name**, because a
  `seed_*` directory can stop early. Excluded inside the v9 scope: `femgo/stop_16` (37 it) and
  `febmgo/seed_6` (no data); in the archived Co host, `fecomgo/seed_4` (10 it) and `fecobmgo/seed_3`
  (73 it). Plus the unfinished runs inside the sensitivity families. The two systems have unequal
  completed-search counts (**13 vs 6**), as do the parameter settings.
- **Lattice model (v5):** both phases are built on a **bcc** Fe lattice, but experiment reports
  **bct** Fe on MgO(001) below ≈10 Å \cite{urano1988}; the island branch (ΔZ ≈ 1–6 Å) lies in
  that regime. The comparison is a trend within a fixed lattice model.
- **Basis-set completeness (v5):** LCAO basis sets are less complete than plane waves
  \cite{larsen2009}, which shifts absolute geometric parameters (e.g. the computed Fe–O
  separation, 2.30–2.33 Å, sits at the upper end of the experimental/calculated 2.0–2.3 Å
  range \cite{urano1988,butler2001}). Quantities are compared at fixed settings.
- **Strain convention is the inverse of the experimental stack (v6; now tested for the boron-free
  model — v10).** The simulation cell takes the Fe lattice constant and the **substrate** is
  compressed to match it (MgO 3.6 % relative to bulk, held fixed), so **the Fe film is unstrained
  in-plane**. In a real junction the bulk MgO imposes its lattice on a thin Fe film, which absorbs
  the mismatch and relieves it through interfacial dislocations \cite{yuasa2004}. **The physically
  inverted case has now been calculated for the boron-free Fe/MgO model:** the constraint sweep
  (SI-10) carries the cell from Fe-matched to MgO-matched, the far end placing the substrate at the
  experimental MgO lattice constant with the film stretched 3.92 % — and the island remains the
  ground state in every search, with the flat-basin minimum moving by only 0.0094 eV/atom across
  the whole sweep. What is *not* covered is the boron-containing model (and the substrate is a single
  layer, so it is the constraint that is inverted, not the full experimental geometry).
- **The Fe-atop-O registry is partly inherited (v6):** `build_mgo_stack` places the substrate
  oxygen directly above the metal sites, so the flat film's registry follows from the
  construction as well as agreeing with the measured LEED I–V registry \cite{urano1988}. It is a
  consistency check, not an independent prediction by the search.
- **The single search-level test in scope is not resolution-limited (v9).** The permutation test
  partitions the pooled per-search flat minima, so with *a* vs *b* searches only C(a+b, a) partitions
  exist. MT-3's 13 vs 6 admits **27 132** partitions, a floor of p = 3.7×10⁻⁵ — and the test now
  **enumerates all of them exactly**, so the reported p = 0.0444 is the value for these data, not a
  Monte-Carlo estimate of it (v8's estimate was 0.045). Far below the reported p, so the test is
  genuinely informative here. (The 4-vs-3 floor of p = 0.029 that limited v8's MT-4 went to the
  archive with the Co host.) `analysis/ensemble_stats.json` records `perm_n_partitions`,
  `perm_resolution` and `perm_method` for every comparison.
- **The permutation test was mis-implemented before v8** (two independent permutations instead of
  one split), which widened the null and inflated significance (e.g. MT-3 read p = 0.005 instead of
  p = 0.045). Fixed in v8.
- **The test is exact from v9.** v8's version sampled 5000 permutations from the shared RNG, so its
  p-value moved with the script's scope (0.0452 vs 0.0480 for the same data). v9 enumerates every
  partition instead: MT-3 p = 0.0444, deterministic and scope-independent.
- **No third-element control (v9).** The paper compares one host with and without boron. The
  archived Co models were what allowed a "boron rather than any added element" reading; within the
  present scope, an effect of the added element as such cannot be separated from an effect of boron.
- ΔZ ≤ 1.0 Å flat cutoff is a chosen threshold.
- kpts = (1,1,1), single-layer slabs → qualitative/trend-level.
- **The absolute reference energy is not converged with respect to search length (v10; written in
  at last).** The question held open since v4 is answered by SI-9 and becomes a stated limitation:
  with the same calculation run to 200–600 iterations, the **absolute** minimum is still improving at
  100 iterations (12 of 17 searches find a lower island with more budget, median 0.0013, up to
  0.0071 eV/atom). What *is* budget-insensitive is the **comparison**: the island stays the ground
  state in all 17 searches and the flat–island separation is unchanged or larger (median +0.0104,
  up to +0.0268 eV/atom). Reported separations are therefore comparisons at a stated budget, not
  converged absolute energies. **The boron-containing model was not re-run at a longer budget**
  (no such data), so this bound does not transfer to MT-3 by measurement.
- **The flat-basin reference carries a run-set spread of order 0.02 eV/atom (v10).** Independent
  run sets of the same boron-free system at the same 100-iteration budget give a pooled flat-basin
  minimum between **0.1624 and 0.1901 eV/atom** (`analysis/iteration_budget.json`), against the
  0.1888 eV/atom reported for the main-text 13 searches. The search-to-search spread within an arm
  is 0.017–0.031 eV/atom. Comparisons of size ~0.04 eV/atom (the boron effect) are therefore above
  this scatter but not by a large factor, which is one reason the boron result is reported with a
  search-level permutation test rather than on the pooled value alone.
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
  **Data bound (added 2026-09-17, rewritten v9; Discussion-only wording, no MT/SI claim changed):**
  the supported driver is the *presence of boron* — the principle is retained as acting through the
  added metalloid rather than through element counting. **The element-count contrast that v8 used
  here (Co alone raises the flat-basin energy; Fe-B and Fe-Co differ more from each other than
  Fe-Co does from Fe-Co-B) is withdrawn with the archived Co host, and the scientist elected to keep
  the boron-only wording rather than restate it as an untested bound.** Honest bound retained: even
  the boron-bearing model keeps the island as the ground state, so the principle stabilises but does
  not fully suppress the ordered configuration in these models.
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

- [x] **MT-1 … MT-5, MT-7 approved** (main text) — scientist (2026-09-16). *Superseded in part by
      v9: MT-4 and MT-5 were archived with the Co host on 2026-09-17.*
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
- [x] **v9: the Co host is archived out of scope and MT-4/MT-5 with it; the paper is Fe/MgO vs
      Fe-B/MgO** (2026-09-17) — scientist
- [x] **v9: Greer wording stays on the boron-only argument** (no element-count contrast) — scientist
- [x] **v9: no Co sentence anywhere in the manuscript; the Co host is not discussed** — scientist
- [x] **v9: archive mechanics** — raw data to `data/_archive/`, records to `_archive/cofe/`;
      analysis scripts keep their four-system capability but default to the Fe-host scope — scientist
- [x] **v9: no new searches run; the two-system paper is written from existing data** — scientist
- [x] **v10: the two new robustness studies are included in the Supplementary Material as §S4
      (iteration budget) and §S5 (lattice constraint), each with its own claim** — scientist
- [x] **v10: both studies stay boron-free, so they bound the structural result (MT-1, MT-2) and the
      stated limitations rather than the boron effect (MT-3)** — scientist
- [x] **v10: the f = 0 and f = 0.5 arms of the constraint sweep stay out of the paper; the sweep is
      reported at 0.25 / 0.75 / 1.00 with the paper's own Fe/MgO model as the Fe-matched reference**
      — scientist
- [x] **v10: `a_MgO = 4.212 Å` is the experimental MgO lattice constant used as a fixed reference**
      — scientist
- [ ] **v10: SI-9 and SI-10** — awaiting sign-off
- [ ] **v11: SI-11 (the inverted stack, MgO on Fe)** — a **ground-state comparison**, qualified/weak
      (the inverted-stack searches do not converge), awaiting sign-off
- [ ] **v10: the wording of the convergence bound in §1.6 / §3.4** — awaiting the scientist
      (OPEN item 5)
- [ ] **v9: the rewritten contribution sentence** — awaiting the scientist's re-sign-off
- [ ] **v9: application framing** — `03_discussion.md` §3.4's "CoFeB/MgO stack used in devices":
      keep the application discussion generic ("MgO-based magnetic tunnel junctions") or cut it?
- [ ] **Acceptance of the permutation-test fix (v8)** — still open, now reduced to MT-3 alone

**Status: FROZEN (v11, 2026-09-17), scope Fe/MgO + Fe-B/MgO.** This list is frozen for drafting. Any
new result or claim requires an explicit update to this file before it enters a section.
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
changed from refuted to under-powered (status flag left for the scientist) · v9 (2026-09-17) the Co
host archived out of scope and MT-4/MT-5 with it, plus the combined 2×2 statement and the Fe-Co-B
halves of MT-7/MT-8; contribution rewritten host-independently-free; SI unaffected (already
Fe/MgO-only); third-element-control scope bound added; v8's permutation-resolution limitation and
strain-convention confound both resolved by the scope restriction; MT-6's secondary reason reworded;
the significance test made exact and scope-independent (MT-3 p = 0.0444; the v8 Monte-Carlo value
moved with the RNG stream) · v10 (2026-09-17) two new boron-free Fe/MgO robustness studies added to
the SI: SI-9 (iteration budget — the comparison survives 200/400/600 iterations while the absolute
energy keeps improving) and SI-10 (lattice constraint — sweeping the cell from Fe-matched to
MgO-matched moves the flat-basin minimum by 0.0094 eV/atom); the convergence caveat held since v4
written into the Limitations; the inverted-strain case now calculated for the boron-free model; a new
limitation for the run-set spread of the flat-basin reference · v11 (2026-09-17) the inverted stack
(MgO on Fe) added as a GROUND-STATE COMPARISON (SI-11, qualified): the inverted stack's ground state
is a flat MgO film (0.016 eV/atom below the corresponding island), the opposite of Fe-on-MgO whose
ground state is an island, but the inverted-stack searches do not converge at the 100-iteration
budget, so the comparison is indicative rather than settled; the per-run evidence is kept in the
analysis file rather than restated in the manuscript.
