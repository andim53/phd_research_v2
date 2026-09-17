# paper_status.md — handoff / resume state

> **v9 rewrite (2026-09-17).** This file is the memory a fresh session resumes from; it was
> rewritten when the paper's scope changed from four models to the Fe host alone. The full
> pre-v9 narrative is **not** repeated here — it lives in `experiment_log.md` (append-only) and in
> the `CLAIMS.md` version changelogs (v1–v8), which are unchanged. Anything below is current.

## Scope (CLAIMS v9) — the Fe host only

**The paper studies Fe/MgO and Fe-B/MgO.** The Fe-Co/MgO and Fe-Co-B/MgO models are archived out of
scope on the scientist's instruction (2026-09-17): *"archive the current CoFe host results,
considering it has so many problem. For now, write the main and supplementary based on the Fe host,
with and without B."*

| | in scope | archived |
|---|---|---|
| models | `femgo` (Fe/MgO), `febmgo` (Fe-B/MgO) | `fecomgo`, `fecobmgo` |
| completed searches | 13 and 6 | 4 and 3 |
| structures | 1180 and 543 (**1723**) | 354 and 273 (627) |
| raw data | `data/femgo`, `data/febmgo` | `data/_archive/fecomgo`, `data/_archive/fecobmgo` |
| record | — | `_archive/cofe/README.md`, `_archive/cofe/cofe_evidence.json`, `_archive/cofe/pes_structures_cofe.csv` |

No measurement was retracted — the Co models were dropped because the host is not a clean
counterfactual (different strain convention, 4 vs 3 searches cannot reach p < 0.029, and
`data/fecomgo/main.py` adds a third `PermutationGenerator`). Why, and how to revive it, is in
`_archive/cofe/README.md`. **Scope is enforced in code** by `scripts/scope.py`
(`SYSTEMS_IN_SCOPE`); every multi-system script imports it, defaults to the Fe host, and keeps the
four-system capability behind `--all-systems`.

## Contribution (one sentence) — REWRITTEN IN v9, NEEDS RE-SIGN-OFF

> **Boron insertion lowers the relative energy of the flat metal-film wetting state of Fe on
> MgO(001) by ~0.04 eV/atom (0.1888 → 0.1493 eV/atom, exact two-sided permutation p = 0.0444 over
> 13 vs 6 completed searches), moving the flat, well-wetting configuration closer to the island
> ground state without displacing it — relevant to interface flatness in MgO-based magnetic
> tunnel junction stacks.**

The v8 sentence claimed host independence ("in both a pure-Fe and a Fe-Co host … independently of
the host metal") and rested on the archived Co host. That claim is gone; the object of the paper is
now one composition effect in one host, with the phase-resolved wetting map and the method-
robustness SI as the supporting contribution.

**Claim list frozen:** `CLAIMS.md` **v9** (2026-09-17; supersedes v8 … v1).

## Run selection: completed searches only (v8 rule, still governing)

A search counts only if it reached the full 100-iteration budget. The rule lives in
`scripts/run_selection.py` (`FULL_ITERATIONS = 100`), is imported by every analysis script, and is
determined from the **iteration number stored in each database, not the directory name**.

| run | iteration max | status |
|---|---|---|
| `femgo/stop_16` | 37 | excluded (in scope) |
| `febmgo/seed_6` | no data | excluded (in scope) |
| `fecomgo/seed_4` | 10 | excluded; archived with the host |
| `fecobmgo/seed_3` | 73 | excluded; archived with the host |

Reported counts are **13 / 6** completed searches (Fe / Fe-B). The method-sensitivity families in
the SI still contain truncated runs; `scripts/method_sensitivity.py` handles them with its
equal-iteration primary statistic (§S3).

## The significance test is now exact (v9) — and was scope-dependent before

Re-running the analysis to confirm the scope change reproduces the frozen numbers exposed a third
defect in the permutation test (after v8's mis-implemented permutation). The bootstrap CIs and the
Monte-Carlo p drew from the **shared module RNG**, whose stream position depends on how many
systems were processed first, so the headline p-value moved with the script's scope: **0.0452 (Fe
host alone) vs 0.0480 (all four systems)** for the same 19 numbers. Fixed:

- each effect seeds its own bootstrap generator (`EFFECT_SEEDS` in `scripts/ensemble_analysis.py`);
- the permutation test **enumerates every partition of the pool exactly** (27 132 for 13 vs 6;
  35 for 4 vs 3; 2380 for 13 vs 4) instead of sampling 5000, so the value is deterministic and
  seedless, and `perm_resolution` is the real resolution rather than an approximation of it.

| comparison | v8 (Monte-Carlo) | **v9 (exact)** |
|---|---|---|
| B in the Fe host — MT-3, 13 vs 6 | 0.0452 (or 0.0480, scope-dependent) | **0.04438** |
| B in the Fe-Co host — archived MT-4, 4 vs 3 | 0.0924 | 0.08571 |
| Co alone — archived MT-5, 13 vs 4 | 0.2454 | 0.23571 |

**Verified:** the Fe-host p is identical in scope and with `--all-systems`
(`analysis/ensemble_stats.json` records `perm_method` per comparison).

## OPEN — decisions for the scientist

- [ ] **Re-sign the contribution sentence** (rewritten in v9; the old one claimed host
      independence). `CLAIMS.md` → Contribution.
- [ ] **Application framing.** `03_discussion.md` §3.3 no longer names CoFeB — it says "MgO-based
      tunnel junctions" — because the paper studies Fe/MgO only. Keep it general, or restore a
      CoFeB-specific sentence with a genuine reference?
- [ ] **Accept the exact significance test (v9).** The p-value moved 0.005 → 0.045 → 0.0444 across
      the three versions of the test; the last step removed a genuine scope-dependence. Same
      category of decision as v8's test fix, which is still formally open.
- [ ] **The lost third-element control.** With the Co host archived, nothing separates "boron does
      this" from "an added element does this". Recorded as a scope bound in `01_methods.md` §1.6
      and `03_discussion.md` §3.4. A second, chemically different addition in the same host would
      be needed — not planned.
- [ ] **Review the three re-scoped sections** — `01_methods.md` v5, `02_results.md` v4,
      `03_discussion.md` v5. **No section is approved.** 03 is still the gate for `04_introduction.md`
      (not drafted; `05_conclusion`, `06_abstract` also not started; no LaTeX until all approve).
- [ ] **Main-text figures are cited by no section** — see "Float numbering" below. `figures/INSTRUCTION.md`
      lists the open figure-design questions, including the two-system redesign of
      `flat_state_summary.png` (it was a B × Co 2×2).
- [ ] **SI-9 and SI-10 need sign-off** (the iteration-budget and lattice-constraint studies, both
      boron-free by design — CLAIMS v10). See "SI-9 / SI-10" below for the numbers.
- [ ] **How to word the convergence bound in the sections.** The caveat held since v4 ("the searches
      are still improving at iteration 100") is now answered with numbers by SI-9 and written into
      the CLAIMS Limitations. Whether §1.6 and §3.4 should state it (with a pointer to §S4), and in
      what form, is the scientist's call — options: (a) one sentence in §1.6; (b) also a sentence in
      §3.4; (c) leave the sections and rely on the SI.
- [ ] **Full texts of three islanding references.** `fahsold2000`, `reitinger2007` and `torelli2009`
      are cited from **verified abstracts**; all three are closed access and no institutional copy is
      in `papers/`. The Urano PDF carries a *"Downloaded from journals.jps.jp by 三重大学"* watermark,
      i.e. the scientist has institutional access — adding these PDFs would close this.
- [ ] **Bulk-Fe reference, if wanted.** §3.1 no longer calls the island d-band centre "bulk-like"
      because no bulk-Fe reference calculation exists in the repo.
- [ ] **Motif analysis (MT-8) has no SI section.** The dangling pointer was removed from Results
      §2.1 (v9) rather than adding an S4. Draft S4 later if the motif analysis is wanted in print.

## Drafting progress (Phase E — markdown-first, block-and-wait)

| Section | Draft | Approval state |
|---|---|---|
| `01_methods.md` | **v6** | **No approval.** v3 was approved at `c89e1e1`, then voided by the v4 edit; v5 re-scoped to the Fe host and v6 removed the code identifiers, so nothing survives. |
| `02_results.md` | **v4** | **No approval.** Approved 2026-09-16, reconstructed (v2), extended (v3), re-scoped (v4 — Co results and the 2×2 design removed; Tables 4–5 → 3–4). |
| `03_discussion.md` | **v5** | **Awaiting review — the gate for `04_introduction.md`.** The cobalt section is deleted; no sentence about the Co host remains. |
| `SI.md` | **v7** | **Awaiting review.** v4–v6 were scope/history/code cleanups with no content change; **v7 adds §S4 (iteration budget, SI-9) and §S5 (lattice constraint, SI-10)** — two new boron-free Fe/MgO robustness studies (CLAIMS v10). §S1 (SI-8), §S2 (SI-1…SI-4), §S3 (SI-5…SI-7) are unchanged. |
| `04_introduction.md` | — | **BLOCKED** on 03 approval. |
| `05_conclusion.md`, `06_abstract.md` | — | Not started. |
| E2 port to `paper.tex` | — | Not started; no LaTeX until all sections are approved. |

**Phase A: DONE** (contribution + claim list signed off 2026-09-16 — but the contribution has since
been rewritten, see OPEN). **Phase D: DONE** for the main text (13 citations verified, every
`\cite{}` key resolves, none orphaned). **Phase F/G: not started.**

## Float numbering (v9)

Sequential in order of appearance across the drafted sections. Deleting the Fe-Co generator table
shifted the Results floats.

| Float | Location | Content |
|---|---|---|
| **Table 1** | `01_methods.md` §1.1 | the two interface models: film constitution, atom counts |
| **Table 2** | `01_methods.md` §1.2 | candidate-generation schedule (common to both models) |
| **Figure 1** | `01_methods.md` §1.2 | the biased-exploration loop (mermaid workflow diagram) |
| **Table 3** | `02_results.md` §2.1 | the two phases in each model |
| **Table 4** | `02_results.md` §2.2 | flat-basin minimum dE/N with and without boron |
| **Figure S1** | `SI.md` §S1 | exploration-performance panels (separate `S` series) |

The section draft versions in the table above live in a `<!-- DRAFT vN -->` comment at the head of
each section file and in the `# NN — Title` block under it; nothing else in a section refers to a
version.

**Float sources and traceability (v9 — the sections no longer carry file paths).** Because sections
are manuscript text, the mapping from each float to the file that produces it lives here:

| Float | Figure/table file | Data source |
|---|---|---|
| Figure 1 (Methods workflow) | inline mermaid diagram | `sections/01_methods.md` |
| Table 1 (the two models) | — | `data/{femgo,febmgo}/main.py`, `scripts/build_mgo_stack.py` |
| Table 2 (generation schedule) | — | `data/{femgo,febmgo}/main.py` (`num_candidates`, rattle amplitudes) |
| Table 3 (phases per model) | — | `analysis/pes_structures.csv` |
| Table 4 (flat-basin min dE/N) | — | `analysis/pes_structures.csv`, `analysis/ensemble_stats.json` |
| Figure 2 candidate (PES maps) | `figures/pes_2_systems.png` | `analysis/pes_structures.csv` |
| Figure 3 candidate (flat-basin summary) | `figures/flat_state_summary.png` | same |
| Figure 4 candidate (side views) | `figures/flat_vs_ground_preview.png` | `analysis/flat_structures/*.xsf` |
| Figure S1 (exploration performance) | `figures/exploration_performance_femgo.png` | `analysis/exploration_performance.json` |
| Table S1 (DOS metrics) | — | `analysis/pdos_metrics.csv` |
| Figure S2 (flat vs island DOS) | `figures/pdos_flat_vs_island.png` | `data/dos_femgo_flatngs/` |
| Table S2 (site-resolved d-band, registry) | — | `analysis/interface_analysis.csv` |
| Figure S3 (registry top view) | `figures/interface_registry_topview.png` | `analysis/interface_analysis.csv` |
| Table S3 (method sensitivity) | — | `analysis/method_sensitivity.csv` |
| Figures S4–S6 (rattle/kappa/dipole) | `figures/method_sensitivity_{rattle,kappa,dipole}.png` | `analysis/method_sensitivity.csv` |
| Table S4 (budget) | — | `analysis/iteration_budget.json` / `.csv` |
| Figure S7 (budget) | `figures/iteration_budget.png` | `analysis/iteration_budget.json` |
| Table S5 (constraint) | — | `analysis/lattice_constraint.json` / `.csv` |
| Figure S8 (constraint) | `figures/lattice_constraint.png` | `analysis/lattice_constraint.json` |

`analysis/pdos_site_metrics.csv` and `figures/pdos_sites.png` are **not** to be used (superseded by
Table S2). This is the only place the code-level names are recorded, by design.

⚠ **The main-text figures are cited by no section.** `figures/pes_2_systems.png` (PES maps),
`figures/flat_state_summary.png` (flat-basin comparison) and `figures/flat_vs_ground_preview.png`
(side views) exist and are regenerated against the v9 data, but Results §2.1/§2.2 describes the
landscape in prose only. Wiring them in would make them **Figure 2** (§2.1), **Figure 3** (§2.2)
and possibly **Figure 4**. Open in `figures/INSTRUCTION.md`.

## Method note

- AGOX **GOFEE** (GPR surrogate + LCB): a **biased** search seeded from a reference **flat**
  metal layer. Filters to **iteration ≥ 10** (relax starts at iteration 10).
- Flatness metric: **ΔZ = z(metal_max) − z(metal_min)** [Å] over the film's **metal** atoms
  (`pes_analysis.METAL = ('Fe','Co')` — boron is not part of it).
- PES coordinate: **dE/N = (E_i − E_globalmin)/N_atoms**, global min = 0 eV/atom, per system.
- Flat/island basins separated by ΔZ ≤ 1.0 Å (a chosen threshold).

## Systems (2) and their data

- **`femgo`** Fe/MgO — 13 completed searches, 1180 structures, global-min ΔZ 3.652 Å,
  flat-basin min 0.1888 eV/atom.
- **`febmgo`** Fe-B/MgO — 6 completed searches, 543 structures, global-min ΔZ 3.767 Å,
  flat-basin min 0.1493 eV/atom. (`seed_6`'s db is empty.)
- **Rattle-strength study** (same `femgo` scheme): `param_ratt05`, `param_ratt1`.
- **Method-parameter study:** `femgo_kappa/{1_k1,0_k3,2_k4}`, `femgo_dip`.
- **DOS/PDOS:** `dos_femgo_flatngs` (Fe flat + island), `dos_febmgo_gs` (Fe-B ground state; the
  Fe-B PDOS comparison remains **deferred** — mismatched projections).
- Archived: `data/_archive/{fecomgo,fecobmgo}`.
- Loaders must **skip scratch `trash/` dbs** — the `femgo_kappa` dirs contain a `trash/` db with
  41 Fe9Mg9O9 structures. This directory is large and is **not** part of paper commits.
- The runs are GOFEE (GPR surrogate + LCB), a **biased** exploration, so the number of structures
  in a basin is an *exploration density*, not a physical weight.

## SI-9 / SI-10 — the two new robustness studies (v10, 2026-09-17)

Both are **boron-free Fe/MgO**, so they bound the structural result (MT-1, MT-2) and the stated
limitations, **not** the boron effect (MT-3). Analysis: `scripts/iteration_budget.py`,
`scripts/lattice_constraint.py`; outputs `analysis/iteration_budget.{json,csv}`,
`analysis/lattice_constraint.{json,csv}`; figures `figures/iteration_budget.png`,
`figures/lattice_constraint.png`. Drafted as **§S4** and **§S5** of `sections/SI.md` (v7).

- **§S4 — iteration budget (SI-9).** `data/extraIteration/{0_200Iter,1_400Iter,2_600Iter}` is the
  same calculation as the main text (the run script differs only in `N_iterations`), run to 200/400/
  600 iterations; 6 + 7 + 4 completed searches. Primary evidence is **per-run truncation** (each run
  cut at k = 100 and at its own budget, same trajectory, no cross-run normalisation). Result: island
  ground state in **17/17** searches at both the 100-iteration cut and the full budget; the flat–island
  separation is unchanged in 5 and larger in 12 of 17 (median **+0.0104**, range 0 to **+0.0268**
  eV/atom); the **absolute** minimum is still improving (12/17, median 0.0013, up to 0.0071 eV/atom).
  The 13 main-text searches read through this script reproduce the pooled flat-basin minimum
  **0.1888 eV/atom** exactly. **This answers the convergence caveat held since v4.**
- **§S5 — lattice constraint (SI-10).** `data/latt_conc/{3_latt_025,2_latt_075,4_latt_100}` sweeps the
  cell `a = a_Fe + f(a_MgO/√2 − a_Fe)` with both phases built on it; 10 + 10 + 5 completed searches.
  Result: island ground state in **25/25** searches; pooled flat-basin minimum **0.1932 / 0.1982 /
  0.1907 eV/atom** across f = 0.25/0.75/1.00 against **0.1888** for the main-text Fe-matched model —
  a total spread of **0.0094 eV/atom**, 2–3× smaller than the within-arm search-to-search SD
  (0.017–0.031). The far end places the substrate at the **experimental MgO lattice constant**
  (4.212 Å as used), so the physically inverted strain case is now calculated for this model.
- **Out of scope:** the f = 0 and f = 0.5 arms (f = 0 is a reference arm the scientist does not want
  in the paper; `_archive/latt_conc/1_latt_1` is empty); the sweep's a_Fe (2.866 Å) differs from the
  main text's (2.87019 Å) by 0.15 %; a_MgO = 4.212 Å is the experimental value used as a fixed
  reference. Runs that stopped early are excluded (constraint arm: seed_113 at 12/40 it, seed_107 at
  10, seed_109 at 62).

## Supplementary Material (unchanged by v9)

- **§S1 — performance of the biased exploration** (claim **SI-8**, signed off 2026-09-17). Fe/MgO
  only, all 13 searches, **all** iterations. Deliverables:
  `figures/exploration_performance_femgo.png`, `analysis/exploration_performance.json`.
  Key numbers: pre-relaxation (i = 1–9) descends only 12 % of the total (0.494 → 0.435 eV/atom);
  **iteration 10 (relaxation onset) is the single largest step — 49 % of the entire descent**
  (0.435 → 0.250 eV/atom; per-search median drop 0.165, range 0.084–0.233); 84 % done by i = 30,
  94 % by i = 50; best-known crosses 0.20 at i = 23, 0.05 at i = 46, 0.02 at i = 57; **the global
  minimum is first found at i = 77**; only 10 / 13 searches end within 0.05 eV/atom and 4 / 13
  within 0.02. Organised around the onset step (the "early/late" framing was dropped by decision).
- **§S2 — electronic-structure origin of the flat → island transition** (claims **SI-1…SI-4**),
  carrying the v6 mechanism wording (no "bulk-like" comparison — no bulk-Fe reference exists;
  registry presented as a construction-inherited consistency check). Floats: **Table S1**
  (`analysis/pdos_metrics.csv`), **Table S2** (`analysis/interface_analysis.csv`), **Figure S2**
  (`pdos_flat_vs_island.png`), **Figure S3** (`interface_registry_topview.png`). Every number
  verified against the CSVs (38/38 checks). `analysis/pdos_site_metrics.csv` and
  `figures/pdos_sites.png` come from a superseded split and must not be used.
- **§S3 — method-parameter sensitivity** (claims **SI-5…SI-7**), primary statistic
  **equal-iteration** (completed searches only), as-reported variant kept in the same CSV
  (`variant` column). Primary numbers (Table S3): baseline (kappa=2, no dipole)
  **0.03683 ± 0.02575**, 13 searches, flat 0.165; kappa=1 0.03947 ± 0.02371 (16); kappa=3
  0.03509 ± 0.02182 (10); kappa=4 0.03209 ± 0.01872 (9); dipole xy 0.03770 ± 0.02436 (11);
  rattle reduced-0.5 0.26073 ± 0.06804 (2), flat 0.023; reduced-1.0 0.25583 ± 0.13287 (4),
  flat 0.017. Figures S4–S6. **"kappa = 1 is best" is RETRACTED** — no kappa is distinguishable
  from another (the four settings span 0.0074 eV/atom, inside SDs of 0.019–0.026); the rattle
  factor is **~7×**, not ~5×. **Re-verified 2026-09-17:** rerunning `exploration_performance.py`
  and `method_sensitivity.py` under the v9 scope leaves both outputs **byte-identical**
  (md5 unchanged) — the SI is genuinely untouched by the archive.

## Claim → evidence (in scope after v9)

| Claim | Evidence | Metric & value | Verified? |
|-------|----------|----------------|-----------|
| Island is the ground state (MT-1) | `analysis/pes_structures.csv` | global-min ΔZ 3.65 (Fe) / 3.77 Å (Fe-B) | yes |
| Flat is a distinct, higher-energy basin (MT-2) | same | flat-basin min dE/N = 0.1888 / 0.1493 eV/atom | yes |
| **B lowers the flat-state energy in the Fe host (MT-3)** | same + `ensemble_stats.json` | 0.1888 → 0.1493 eV/atom (−0.040) | yes — **exact** permutation **p = 0.04438** (13 vs 6; 27 132 partitions, floor 3.7×10⁻⁵); median shift 0.0351, 94 % same sign |
| B does not bond to MgO (MT-7) | `analysis/pes_structures.csv`, `wetting_metrics.csv` | 1 of 72 in-window Fe-B structures has a B–O contact; max contact fraction 0.33; 101 of the remaining 471 outside the window | yes (windowed; window structures from 4 of the 6 searches) |
| Low-energy sets form a few recurring motifs; ΔZ continuous (MT-8) | `analysis/ensemble_stats.json` | **2** motifs per branch (flat 2/2, island 2/2); within-set distance **0.41–0.44** × random-pair scale | yes (descriptor-limited — paired caveat in CLAIMS) |
| ~~B lowers the flat-state energy in the Fe-Co host~~ | archived | 0.1941 → 0.1494 eV/atom; p = 0.0857 exact | **ARCHIVED (v9)** — `_archive/cofe/README.md` |
| ~~Co alone has little effect~~ | archived | 0.1888 → 0.1941 eV/atom; p = 0.2357 exact | **ARCHIVED (v9)** |
| ~~B increases the flat fraction~~ | — | **WITHDRAWN (MT-6, v2)** — a biased-exploration weight, not a population | — |
| **[SI]** Relaxation onset pivots the search (**SI-8**) | `exploration_performance.json` | 49 % of the descent at i = 10; global min at i = 77; 10/13 within 0.05 eV/atom | signed off 2026-09-17 |
| **[SI]** Island origin: reduced Fe–O hybridisation (**SI-1**) | `pdos_metrics.csv` | d-band centre −0.23 → +0.60 eV; O-pz 43.9 → 42.4 | yes |
| **[SI]** Island origin: weaker magnetism, lower DOS(E_F) (**SI-2**) | `pdos_metrics.csv` | spin pol 5.81 → 4.37; DOS(E_F) 104 → 78 | yes |
| **[SI]** Reduced forced interfacial coupling + restored metal cohesion (**SI-3**, v6) | `interface_analysis.csv` | island interface Fe d-centre +0.51 (flat-like −0.23); registry-locked atoms 25/25 → 9/25 | yes |
| **[SI]** Fe sits atop O — construction-inherited consistency check (**SI-4**, v6) | `interface_analysis.csv` | 25/25 flat, 9/9 island atop O; `build_mgo_stack` places substrate O above the metal sites | yes — not a search prediction |
| **[SI]** Rattle reduction degrades the search ~7× and under-samples the flat basin (**SI-7**) | `method_sensitivity.csv` | per-seed best 0.0368 → 0.2607 / 0.2558; flat 0.165 → 0.023 / 0.017 | yes (arms of n = 2 and 4) |
| **[SI]** Result robust to kappa (**SI-5**) | `method_sensitivity.csv` | 0.0321–0.0395 eV/atom across k = 1–4; no setting distinguishable | yes |
| **[SI]** Result robust to the dipole correction (**SI-6**) | `method_sensitivity.csv` | 0.03683 → 0.03770 (difference 0.0009, inside the SD) | yes (outcome-level) |

**NOT claimed:** that the flat state is *metastable* (needs convergence + Hessian + a barrier).

## Relaxation caveat

- Candidates are relaxed by the **GPR surrogate** (`ParallelRelaxPostprocess`, 100 steps,
  `start_relax=10`), then evaluated with **1 GPAW step** (`fmax=0.05, steps=1`). Residual max
  |F| = 1.0–2.4 eV/Å.
- "Lowest-energy"/"basin" = the lowest DFT energy *found*, not a converged minimum.
- Planned fix: full DFT re-relaxation of low-force distinct structures (`relaxation/`).
  **Status: the selection is done, the re-relaxation has NOT been run** — no `relaxed/` directory,
  no `relax_results.csv`. The v9 selection is the Fe-host subset (femgo 53 + febmgo 28 = 81 of the
  116 previously selected, which included 18 Fe-Co + 17 Fe-Co-B structures under
  `relaxation/selected/`; rerunning `relaxation/select_structures.py` in scope regenerates the
  manifest without them). See `relaxation/README.md`.

## Citations (Phase D — unchanged by v9)

- **13 verified & in `references.bib`**: agox2020, gofee2017, oganov2011, gpaw2014, pbe1996,
  greer1993, plus the seven added 2026-09-17 for the Fe/MgO literature — **urano1988, butler2001,
  yuasa2004, reitinger2007, fahsold2000, torelli2009, larsen2009** — all verified via DOI
  content negotiation (Crossref). **Every `\cite{}` key in `sections/` resolves, and no entry is
  orphaned.**
- `yuasa2004` replaced the three CoFeB-specific placeholders; those assertions were dropped rather
  than sourced. **No UNVERIFIED placeholders remain.**
- Note: `agox2020` / `gofee2017` carry year 2022 in the `.bib` (keys are surname+year, so they are
  stale) — left as-is because the sections cite them.

## Model geometry — the strain convention (the v8 confound is GONE)

Verified 2026-09-17 from the construction code *and* from the cells stored in the databases.

- **Both surviving models sit on the Fe lattice constant.** `interpolation_factor` = 0:
  `femgo/seed_3`'s first candidate has cell in-plane 14.35 Å = 5 × 2.870, `febmgo/seed_0` 14.35095
  = 5 × 2.87019.
- **The MgO is the strained component**: in-plane periodicity 2.870 Å against the bulk
  `a_MgO/√2 = 2.9783 Å` → **3.6 % in-plane compression**, and the substrate is held fixed in that
  state, so **the film is not strained in-plane**.
- The archived Co pair used the opposite convention (`interpolation_factor` = 1: substrate at bulk,
  film stretched 4.9 %), which is why the 2×2 cross-host comparison confounded boron with strain.
  **With that pair out of scope the confound no longer exists inside the paper** — see CLAIMS v9,
  "RESOLVED by v9". The **absolute** convention (the inverse of the experimental stack) remains a
  stated limitation in §1.6/§3.4. `data/latt_conc/` holds a sweep along this axis if it is ever
  wanted.
- `build_mgo_stack` places the substrate oxygen **directly above a metal site**, so the Fe-atop-O
  registry is **inherited from the construction** (SI-4).
- The interfacial separation is a construction parameter: `dist_fe2o = 2.3 Å` is the
  `build_mgo_stack` default and `main.py` does not override it, so relaxation preserves it
  (**2.300 Å** flat, **2.331 Å** island) rather than computing it. (`dist_z_fe2o = 0.5` in
  `main.py` is a *different* quantity — the randomiser's initial slab offset, commented `#2.3` —
  and is a naming trap, not a contradiction.)

## Literature verification — Fe/MgO experiment (2026-09-17, unchanged)

Three PDFs were supplied by the scientist (`papers/mgofe_{urano1988,butler2001,yuasa2004}.pdf`);
the Urano scan had no text layer and was OCR'd (tesseract).

| Reference | What it actually reports | Relation to our results |
|---|---|---|
| **Urano & Kanaji 1988** (JPSJ 57, 3403; LEED I–V + AES) | Fe on MgO(001) **grows layer by layer**, pseudomorphic at 1 ML, Fe **just above O at ~2.0 Å**; **bct → bcc at ≈10 Å** | **No islanding** — the opposite. Supports our **Fe-atop-O registry** (SI-4) and supplies the **bct limitation** |
| **Butler et al. 2001** (PRB 63, 054416; first-principles TMR) | Fe atop O per LEED; Fe–O **2.169 Å** (calc) / 2.0 Å (LEED) / 2.3 Å (earlier FLAPW); **~3.5 % mismatch**; *"only weak interactions"* between Fe and MgO | Supports the **registry** and **weak coupling**; not a growth-mode paper |
| **Yuasa et al. 2004** (Nat. Mater. 3, 868; MBE MTJ) | Giant TMR; **flatness** of epitaxial Fe is the quality criterion; RT top-Fe growth gives higher dislocation density than 200 °C | Neither islanding nor a structural validation — motivates the flat-interface requirement |
| **Fahsold et al. 2000** (PRB 61, 8475; He-atom scattering) — *added by us* | **3D metal island growth** of Fe on MgO(001) at room temperature, **suppressed only at 140 K** where a monolayer almost covers the substrate | **The genuine islanding validation**, at ≈1 ML coverage |
| **Torelli et al. 2009** (PRB 79, 035408; XMCD + STM) — *added by us* | **Sub-nanometre Fe grows three-dimensionally** on MgO; island coalescence 3.5–6.5 ML; **2D growth mode only above ≈6.5 ML** | Direct evidence for the **1-ML** case; fixes the comparison as **1-ML specific** (§2.1) |
| **Reitinger et al. 2007** (JAP 102, 034310; GISAXS) — *added by us* | **Volmer–Weber growth** at RT on **five** monolayers, spherical superparamagnetic islands | Second islanding reference; coverage is **5 ML**, not 1 ML |

**1-ML growth mode — checked 2026-09-17. Answer: at room temperature, islands.** Our films are
~1 ML on average, so this is our regime: 3D islands below ≈6.5 ML, coalescence 3.5–6.5 ML, 2D
above. That is why the thick Fe electrodes of `yuasa2004` are flat, and why `urano1988` (1 ML,
layer-by-layer) is the **dissent** at exactly 1 ML — most plausibly its conditions (~0.2 Å/min on a
cleaved crystal annealed at 800 °C in O₂; low supersaturation favours 2D). `butler2001` reports no
growth mode at all and is therefore not cited for one. The correspondence is framed as one between
**structural configurations, not between energies** (CLAIMS v5, kept in v6–v9, discussion-only).

## Reference PDFs (papers/)

- `papers/confusion_greer1993.pdf` — Greer, "Confusion by design," Nature 366, 303 (1993).
- `papers/mgofe_urano1988.pdf`, `papers/mgofe_butler2001.pdf`, `papers/mgofe_yuasa2004.pdf`.
- Missing (cited from abstracts only): `fahsold2000`, `reitinger2007`, `torelli2009` — see OPEN.

## What v10 added (2026-09-17)

Two new boron-free Fe/MgO robustness studies in the SI — **§S4 iteration budget (SI-9)** and
**§S5 lattice constraint (SI-10)** — with their analysis scripts, JSON/CSV outputs and figures; the
convergence caveat held since v4 is now answered and written into the CLAIMS Limitations; the
physically inverted strain case is now calculated for the boron-free model; a new limitation for the
run-set spread of the flat-basin reference (0.1624–0.1901 eV/atom across independent run sets).
`CLAIMS.md` is at **v10**. The two studies are boron-free by design, so they bound the structural
result, not the boron effect.

## What the v9 re-scope changed, in one place

- **Claims:** MT-4, MT-5 and the combined 2×2 statement archived; MT-1/MT-2/MT-7/MT-8 restricted to
  two systems; contribution rewritten; a new limitation (no third-element control); the
  permutation-resolution limitation and the strain-convention confound both resolved by the scope;
  MT-6 stays withdrawn on its primary reason only. Full text: `CLAIMS.md` → v9 changelog and
  "ARCHIVED — out of scope".
- **Code:** `scripts/scope.py` added; nine scripts switched to it; `ensemble_analysis.py` bumped to
  v1.2.0 and its `description` block now records the scope, the seeding policy and the permutation
  method. `plot_pes_figure.py` writes `pes_<n>_systems.png` with an auto grid;
  `export_flat_xsf.py`, `preview_flat_xsf.py`, `check_forces.py`, `probe_forces_dist.py`,
  `probe_geometry_all.py` and `relaxation/select_structures.py` follow the scope;
  `probe_truncated_seed_effect.py` deliberately still covers all four (it is the v8 audit record).
- **Artifacts:** `analysis/pes_structures.csv` 2350 → **1723 rows**; `ensemble_stats.json` v1.2.0
  with `scope` and `statistics` blocks; `figures/pes_2_systems.png` replaces `pes_four_systems.png`
  (archived); `analysis/flat_structures/{fecomgo,fecobmgo}_*.xsf` and the four-system PES figure
  moved to `_archive/cofe/`.
- **Reproduction verified after the change:** 0.1888 / 0.1493 eV/atom, 13 vs 6 searches, global-min
  ΔZ 3.65 / 3.77 Å, MT-7's 1-of-72 and 101-of-471, motif counts 2/2 and 2/2, SI outputs
  byte-identical, and `pes_analysis.py` vs `ensemble_analysis.py` numerically identical to 0.0 on
  every column (row order differs; that was already true before v9).
- **Docs:** `AGENTS.md` (scope section, systems list, claims-version references),
  `_archive/cofe/README.md` (the archive record), `data/_archive/README.md`,
  `figures/INSTRUCTION.md` (open figure-design questions), `.gitignore` (re-enables
  `_archive/cofe/` against the repo root's blanket `_archive/` and `*.csv` rules — verified with
  `git check-ignore`).

## Voice check (2026-09-17, on the scientist's instruction)

Sections are manuscript text and must not carry revision history. Three passages in `sections/SI.md`
that did were rewritten so they stand as present-tense method statements:

- **§S2, "Defining the interface by geometry, not by height"** — no longer says "an early version of
  this analysis split the Fe atoms into bottom-8 and top-8 by z"; it now states why a height
  criterion fails for a buckled cluster and defines the 2.8 Å geometric criterion directly.
- **§S2, caveats** — the "`pdos_site_metrics.csv` comes from the superseded split, do not use it"
  sentence was removed from the SI (it is repo hygiene; the note stays here and in the file: that
  CSV and `figures/pdos_sites.png` are **not** to be used, Table S2 is authoritative).
- **§S3, kappa** — no longer says "an earlier reading of the same data singled out kappa = 1"; it now
  states why a ranking is easy to produce accidentally from scatter alone.
- **§S3, completed searches** — the baseline is described as 13 completed searches (one directory
  holds a search that stopped early) rather than as a drop from 14 directories.
- **§2.2, the permutation test** — "enumerates all 27 132 partitions rather than sampling them"
  became "is an exact enumeration of all 27 132 partitions".

`AGENTS.md` now carries this as a governing rule ("Voice: no process history in the sections") so it
applies to `04`–`06` when they are drafted. The `<!-- DRAFT vN -->` comment at the head of each
section is the sole remaining version reference inside a section file; it is stripped at the port —
say the word if it should move to this file instead.

**Second pass, same session — no code in the sections.** On the scientist's instruction (*"don't use
the programming term, like the `dist_fe2o = 2.3 Å`, or the `build_mgo_stack`"*), every identifier,
path and parameter name was removed from `01_methods.md` and `sections/SI.md` and replaced with prose:
the excluded searches by their iteration count rather than by directory name; the selection rule
without its filename; the two perturbation generators, the reference-construction routine and the
2.3 Å construction distance in words; the figure captions without `figures/*.png`; and the data-file
references as Table S1/S2/S3. **Zero code spans remain in any section** (verified by scan). The
file-level mapping that was removed now lives in "Float sources and traceability" above, and the
substitution table is a governing rule in `AGENTS.md`. Sections bumped: `01_methods.md` v6,
`SI.md` v6 — no claim, number, table or figure changed.

## Next step

Nothing here is blocked on agent work except the drafts themselves. The paper is ready for the
scientist to review `01_methods.md` v6, `02_results.md` v4, `03_discussion.md` v5 and `SI.md` v7
(which now carries §S4 and §S5) — 03 is the gate for `04_introduction.md`. The two new SI claims
(SI-9, SI-10) and the wording of the convergence bound in the sections are the open items that
follow from v10.
