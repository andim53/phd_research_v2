# AGENTS.md — Governing Rules for AI Agents Working on This Project

**Project:** Effect of boron insertion on metal-film wetting of Fe on MgO — with and without
boron (MgO-tunnel-junction relevance). *Scope narrowed 2026-09-17: the Fe-Co host is archived;
see "Scope" below.*
**Root:** `/home/think/Desktop/research/_paperDemo`
**Venue:** TBD (format-agnostic)
**Workflow skill:** `scientific-paper-writing` (Phase 0 → A → B → C → D → E → F → G)

## Scope (CLAIMS v9, 2026-09-17) — the Fe host only

**The paper studies `femgo` (Fe/MgO, 13 completed searches) and `febmgo` (Fe-B/MgO, 6).** The
Fe-Co and Fe-Co-B models are **archived out of scope**: raw data in `data/_archive/`, record in
`_archive/cofe/README.md`, frozen values in `CLAIMS.md` → "ARCHIVED — out of scope". **No section may
cite them.** This is not a refutation — the host was dropped because it is not a clean
counterfactual (different strain convention, 4 vs 3 searches cannot reach p < 0.029, and
`data/fecomgo/main.py` adds a third `PermutationGenerator`).

- Scope is enforced in code by **`scripts/scope.py`** (`SYSTEMS_IN_SCOPE`, `db_glob()`). Import it;
  never hard-code `data/<system>/…`. `--all-systems` restores the four-system capability.
- Dropping the Co host also **removed the v8 strain-convention confound** from the paper (both
  surviving models sit on `a_Fe`), and it costs the paper its third-element control — recorded as a
  limitation in §1.6 and §3.4.
- It also **moved the reported p-value**: the permutation test was scope-dependent (shared RNG) and
  is now an **exact enumeration of all partitions** (MT-3 p = 0.0444). See `CLAIMS.md` v9 §4.

## Governing workflow rules

- **Papers are drafted markdown-first, one file per section**, in `sections/`:
  `01_methods.md → 02_results.md → 03_discussion.md → 04_introduction.md → 05_conclusion.md → 06_abstract.md`.
- **Block-and-wait review gate:** after each section is drafted, STOP and hand it to the
  scientist for review. Do not draft the next section until the current one is approved.
  Do not port to LaTeX until all six sections are approved.
- **LaTeX is only the final formatting container** (`paper.tex`), produced after all
  sections are approved. Never draft directly in LaTeX.

## Paper scope (what goes where)

- **Main text:** the PES / wetting study across the two Fe-host models — island ground state,
  the B effect on the flat-film energy (0.1888 → 0.1493 eV/atom, −0.040), and B not bonding to MgO.
  (The Co-host counterpart of the B effect, and "Co alone does little", are **archived** with the
  Co host — `_archive/cofe/README.md`.)
- **Supplementary Material (SI):** everything mechanistic / methodological:
  - PDOS origin-of-island analysis (d-band shift, spin polarisation) + interface registry
  - Method-parameter sensitivity (rattle strength, LCB kappa, dipole correction)
- SI figures are flagged `[SI]` in `experiment_log.md`; SI claims are prefixed `[SI]` in
  `paper_status.md`. Keep this split when drafting.

## Known limitations (MUST NOT be overstated)

- **Structures are NOT DFT-converged.** Candidates are relaxed by the GPR surrogate
  (`ParallelRelaxPostprocess`, 100 steps, `start_relax=10`) then evaluated with **1 GPAW
  step** (`fmax=0.05, steps=1`); residual forces are ~1–2 eV/Å. "Lowest energy"/"basin"
  mean "lowest DFT energy *found*", not a converged minimum.
- **Do NOT claim the flat state is "metastable"** — that needs full relaxation + Hessian +
  a barrier. Describe it as a "higher-energy flat basin".
- Re-relaxation pipeline exists at `relaxation/` (116 structures selected) but has NOT run.

## Voice: no process history in the sections

The drafted sections are **manuscript text**, main and supplementary alike. They must read as a
finished account of a single analysis — **never refer to earlier versions of the analysis or of the
draft**. Specifically, do not write "an early version of this analysis…", "this supersedes…",
"an earlier reading singled out…", "the value was X before the correction", "previously computed",
or any other framing that makes the reader aware of a revision history. If a method or a number
changed, state what **is** done and why it is the right choice, in the present tense.

- Process history belongs in `CLAIMS.md` (changelogs), `experiment_log.md` (append-only) and
  `paper_status.md` — those files are *supposed* to carry it.
- Repository hygiene notes ("this CSV comes from a superseded split, do not use it") belong in
  `paper_status.md`, **not** in a section.
- The `<!-- DRAFT vN · … -->` comment at the head of each section is the one exception: it is
  editorial tracking mandated by the block-and-wait workflow, and it is stripped at the LaTeX port.
- Corrected in v9: three such passages in `sections/SI.md` (§S2 interface definition, §S2 caveat,
  §S3 kappa) — see `paper_status.md`.

**No code in the sections either.** A section is read by a referee, not by the analysis code, so it
must not contain identifiers, paths, parameter names or any other programming vocabulary:

| do not write | write instead |
|---|---|
| `` `dist_fe2o = 2.3 Å` `` | "the construction's 2.3 Å interfacial separation" |
| `` `build_mgo_stack` places the O above the metal `` | "the construction places the substrate oxygen directly above the metal sites" |
| `` `HeteroStructRandomize` / `RattleGenerator` `` | "the heterostructure-aware randomiser and the rattle generator" |
| `` `run_selection.py` `` | "the same criterion, applied without exception throughout the analysis" |
| `` `femgo/stop_16`, `seed_*`, `stop_*`, `trash/` `` | "one Fe/MgO search reached only iteration 37"; "a search that looks complete can have stopped early"; "a small set of structures of a different composition, written by the run's own bookkeeping" |
| `` `figures/x.png` `` in a caption, `` `analysis/y.csv` `` in the text | nothing — the caption describes the figure, and the file it came from is listed in `paper_status.md` → "Float sources and traceability" |

Code names that identify a **method or code used** stay, with their citation: AGOX, GOFEE, GPAW,
LCAE/dzp basis, PBE. Physical symbols and units stay: ΔZ, dE/N, κ, a_Fe, a_MgO/√2, eV/atom, Å.
Corrected in v9: `01_methods.md` (excluded-run names) and six places in `sections/SI.md`.

## Citations

- Never hallucinate references. Fetch and verify BibTeX programmatically (DOI content
  negotiation / Crossref / arXiv / ADS); confirm the paper exists in 2+ sources; validate
  that the cited claim actually appears in the paper.
- Inline keys in markdown as `\cite{nameyear}` (first-author surname + year).
- `.bib` entry identifier must be **byte-for-byte identical** to the `\cite{}` key
  (`@article{nameyear, ...}`).
- Unverifiable citations: keep the key form but tag `% UNVERIFIED — verify before port`
  and log to a "pending" list in `paper_status.md`. Never invent a key.
- One master `references.bib` shared by all sections.

## Claims and numbers

- Every claim must trace to a specific source file (result JSON / `.db` / figure) — no
  unsupported statements.
- Every number in the draft must be re-verified against its raw source file before port.
- Flag any claim without evidence as `[VERIFY]`; do not write it as a result.
- **The claim list is FROZEN in `CLAIMS.md` v11 (2026-09-17; supersedes v1–v10).** Drafting must not
  introduce claims outside the list, and must not drop the paired caveats. Any new claim requires
  bumping `CLAIMS.md` to the next version first. The per-version history is in its changelogs; the
  standing content rules are:
  - the search returns an **exploration density, not a thermodynamic density of states**, so basin
    *weights* are not physical and only unweighted structural/energetic comparisons may be used;
  - the **Fe-atop-O registry is inherited from the construction** — a consistency check against the
    measured registry, not a prediction of the search;
  - the island's gain is **reduced forced interfacial coupling plus restored metal cohesion, *not*
    lattice-strain relief**;
  - **searches that stopped before the iteration budget are excluded everywhere** (see the next
    bullet).
- **Only completed searches are used (v8): a search counts only if it reached the full 100-iteration
  budget.** The rule lives in `scripts/run_selection.py` and is imported by every analysis script; it
  is detected from the **iteration number in the database, not the directory name**, because a
  `seed_*` directory can stop early. Reported counts are therefore **13 completed searches for
  Fe/MgO and 6 for Fe-B/MgO** (the two Co exclusions moved to the archive with the host).
- **Search-level significance comes from the two-sided permutation test in `ensemble_analysis.py`**,
  which now **enumerates every partition exactly** when the pool is small enough (it records
  `perm_method`, `perm_n_partitions` and `perm_resolution` in `analysis/ensemble_stats.json`). The
  in-scope comparison is 13 vs 6 → 27 132 partitions, floor p = 3.7×10⁻⁵, and the headline value is
  **p = 0.0444**. Each effect also seeds its own bootstrap generator, so no reported statistic
  depends on which systems the script was asked to analyse.

## Drafting status

**Approval state is authoritative in `paper_status.md`** — read its "Drafting progress" table before
drafting or revising anything. Summary as of 2026-09-18:

- **Phase A: DONE** (contribution + claim list signed off 2026-09-16).
- **Phase D: DONE for the main text** — 21 citations verified in `references.bib` (agox2020,
  gofee2017, oganov2011, gpaw2014, pbe1996, greer1993, urano1988, butler2001, yuasa2004,
  reitinger2007, fahsold2000, larsen2009, torelli2009; plus eight added 2026-09-18 for the
  Introduction — device-side **parkin2004, djayaprawira2005, ikeda2008** (item **E3**), the
  recent-fabrication trend **scheike2023, solano2022, ichinose2025, ghemes2024** (item **E4**), and
  the GOFEE/LCB reference **hamamoto2023** (item **E5**) — see `paper_status.md`); every `\cite{}`
  key resolves and none is orphaned. The three MTJ placeholders were **withdrawn** and replaced by
  `yuasa2004`; no UNVERIFIED placeholders remain. Open: `fahsold2000`, `reitinger2007` and
  `torelli2009` are closed access and cited from verified abstracts only.
- **Phase E: IN PROGRESS — Methods and Discussion APPROVED 2026-09-18; Results approval voided
  (v6, needs re-approval); the Introduction drafted and awaiting review.**
  - `01_methods.md` **v6** — re-scoped to the Fe host (Table 3 deleted, counts 13 / 6) and stripped
    of code identifiers → **APPROVED 2026-09-18**.
  - `02_results.md` **v6** — re-scoped (Co results and the 2×2 design removed, Tables 4–5 → 3–4,
    p = 0.0444) with Figures 2–3 cited and captioned, and the p-value now explained in plain terms
    (§2.2). **APPROVAL VOIDED** by the last edit (v5 was approved 2026-09-18; the scientist
    authorised the p-explanation edit) → **awaiting re-approval (B3)**.
  - `03_discussion.md` **v5** — the cobalt section is deleted; no Co sentence remains →
    **APPROVED 2026-09-18.** It was the gate for `04_introduction.md`; **the gate is now open.**
  - `04_introduction.md` **v9** — **DRAFTED, awaiting review.** Continuous prose, no subsections, no
    floats. v1 closed on the frozen contribution sentence; v2–v7 built the fabrication trend, the
    phase-controlled / GOFEE-with-LCB justification, the plain-terms p-value and the full narrative;
    **v8 rewrote the what-we-do passage in the scientist's example style** (achievement sentence +
    roadmap; numbers and LCB rule moved to Results §2 / Conclusion); **v9 is the scientist's own edit**
    removing the "returns to in the Discussion" forward pointer from the confusion-principle sentence.
    The roadmap uses final-manuscript section numbers (II=Methods … V=Conclusion) — reconcile with the
    draft's §1/§2/§3 at the port. Cites device-side, fabrication-side and GOFEE/LCB keys; the device
    material is referred to generically and no Co host is discussed. Items for the scientist, recorded
    in `paper_status.md`: **C7** (confusion-principle framing), **E3** (three device references), **E4**
    (four recent-fabrication references) and **E5** (the GOFEE/LCB reference) — each accept or drop.
  - `SI.md` **v8** — §S1, §S2, §S3 are Fe/MgO and content-unchanged; v7 added **§S4 (iteration
      budget, SI-9)** and **§S5 (lattice constraint, SI-10)**; v8 adds **§S6 (the inverted stack,
      MgO on Fe, SI-11)** as a **QUALIFIED/weak** finding. **Awaiting review.**
  - `05`/`06` not started; no LaTeX until all sections are approved.
  - **Editing an approved section voids its approval** and requires re-review — that is how the
    earlier `01_methods.md` v3 approval was lost.
- **The v8 strain-convention warning is CLOSED for this paper:** both surviving models sit on
  `a_Fe` (`interpolation_factor` = 0), so the confound that threatened the cross-host comparison no
  longer exists in scope. The **absolute** convention (inverse of the experimental stack) remains a
  stated limitation in §1.6/§3.4. History: `CLAIMS.md` → "RESOLVED by v9".
- **float numbering:** sequential in order of appearance across the drafted sections.
  Currently Tables 1–2 + Figure 1 (Methods), Tables 3–4 + Figures 2–3 (Results); the Introduction
    carries no float; the SI has its own `S` series
    (Tables S1–S6, Figures S1–S9 — S4/S5/S6 and S7/S8/S9 are the v10/v11 robustness studies). See `paper_status.md`.
  Figures 2–3 are cited and captioned as of 2026-09-18; the side-view render is an uncited Figure 4
  candidate (a 200 dpi preview — it would need a 300 dpi re-render to become a manuscript figure).
- **Phase F/G: not started.**
- Reference PDFs live in `papers/` (e.g. `papers/confusion_greer1993.pdf` → `greer1993`).

## Checkpoint / resume

- Always write/update `paper_status.md` before ending a session.
- A fresh session must be able to resume from `paper_status.md` alone (the file is the memory).

## Data & scope

- Raw data lives in `data/` (AGOX/**GOFEE** structure-search databases):
  - **The two systems in scope:** `femgo` (Fe/MgO), `febmgo` (Fe-B/MgO).
  - **Archived:** `fecomgo` (Fe-Co/MgO), `fecobmgo` (Fe-Co-B/MgO) — under `data/_archive/`;
      read them through `scope.db_glob()` or `--all-systems`, never by a hard-coded path.
    - **SI robustness studies (v10, both boron-free Fe/MgO):** `data/extraIteration/{0_200Iter,
      1_400Iter,2_600Iter}` (iteration budget, §S4) and `data/latt_conc/{3_latt_025,2_latt_075,
      4_latt_100}` (lattice constraint, §S5). Each arm is tested against **its own** budget via
      `run_selection`; scratch `trash/`/`_trash/` excluded. `_archive/latt_conc/0_latt_0` (f = 0) and
      the empty `1_latt_1` (f = 0.5) are out of scope.
        - **Inverted stack (v11, QUALIFIED — a ground-state comparison):** `data/mgofe` — an MgO film on
          an Fe substrate (Fe25Mg25O25, cell = a_Fe = 2.866 Å experimental, 100 iterations, 5 completed
          searches). Its ground state is a flat MgO film, the opposite of Fe-on-MgO whose ground state is
          an island, but the searches do not converge at the 100-iteration budget, so SI-11 is qualified,
          not a clean claim. **§S6 is ground-state only — no per-seed content.** Flatness is over the
          deposited film in each stack (Fe for femgo, MgO for mgofe).
  - **Rattle-strength study** (same femgo scheme): `param_ratt05` (rattle −0.5),
    `param_ratt1` (rattle −1.0).
  - **Method-parameter study:** `femgo_kappa/{1_k1,0_k3,2_k4}` (LCB kappa = 1/3/4),
    `femgo_dip` (dipole correction, `dipolelayer: xy`).
  - **DOS/PDOS:** `dos_femgo_flatngs` (Fe flat + island), `dos_febmgo_gs` (Fe-B ground state).
  Loaders must **skip scratch `trash/` dbs** and filter to the target composition — the
  `femgo_kappa` dirs contain a `trash/` db with 41 Fe9Mg9O9 structures.
  This directory is large and is **not** part of paper commits — commit only analysis
  scripts, the scaffold, and draft files.
- The runs are GOFEE (GPR surrogate + LCB): a **biased** exploration seeded from a
  reference **flat** metal layer. Only structures with **iteration >= 10** are used
  (relaxation starts at iteration 10).
- **Three-phase biased exploration** (see `sections/01_methods.md` §1.2): candidate
  generation follows a phase schedule by iteration *i* — Phase I (0 ≤ i < 10) small-scale
  generator N=20; Phase II (10 ≤ i < 25) small 10 + large 10; Phase III (25 ≤ i) large-scale
  N=20. Small-scale = `HeteroStructRandomize` (rattle 1.5), large-scale = `RattleGenerator`
  (rattle 2.3). Matches `num_candidates={0:[20,0],10:[10,10],25:[0,20]}` in `main.py`.
- Flatness metric: **ΔZ = z(metal_max) − z(metal_min)** over the film's **metal** atoms
  (`pes_analysis.METAL = ('Fe','Co')`; boron is not part of the metric, and in scope the film metal
  is Fe) [Å]; ΔZ ≈ 0 = flat film (wet), ΔZ large = island (dewet).
- PES coordinate: **dE/N = (E_i − E_globalmin)/N_atoms** [eV/atom], global min = 0,
  computed per system over the iteration>=10 set. Flat/island basins split at ΔZ ≤ 1.0 Å.
- The `febmgo` energy range contains relaxation artifacts / unphysical high-energy structures;
  the iteration filter + per-system global-min normalisation windows these out.
- The two in-scope systems have **unequal** completed-search counts (13 vs 6) — the smaller group
  sets the width of the permutation null, so note it when reporting uncertainty. The permutation
  test itself is **exact**, so the reported p is not limited by Monte-Carlo noise.

## Commit discipline

- Commit after every change/milestone, with a descriptive message.
- Confirm with the scientist before committing on each milestone.
- Never commit the `data/` tree or other unrelated changes in the parent `research/` repo.
