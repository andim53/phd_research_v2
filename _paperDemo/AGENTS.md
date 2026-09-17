# AGENTS.md — Governing Rules for AI Agents Working on This Project

**Project:** Effect of Boron insertion on metal-film wetting on MgO — pure-Fe vs Fe-Co
hosts (MTJ / CoFeB relevance)
**Root:** `/home/think/Desktop/research/_paperDemo`
**Venue:** TBD (format-agnostic)
**Workflow skill:** `scientific-paper-writing` (Phase 0 → A → B → C → D → E → F → G)

## Governing workflow rules

- **Papers are drafted markdown-first, one file per section**, in `sections/`:
  `01_methods.md → 02_results.md → 03_discussion.md → 04_introduction.md → 05_conclusion.md → 06_abstract.md`.
- **Block-and-wait review gate:** after each section is drafted, STOP and hand it to the
  scientist for review. Do not draft the next section until the current one is approved.
  Do not port to LaTeX until all six sections are approved.
- **LaTeX is only the final formatting container** (`paper.tex`), produced after all
  sections are approved. Never draft directly in LaTeX.

## Paper scope (what goes where)

- **Main text:** the PES / wetting study across the four systems — island ground state,
  the B effect on the flat-film energy (~−0.04 eV/atom, both hosts), Co's negligible effect,
  and B not bonding to MgO.
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
- **The claim list is FROZEN in `CLAIMS.md` v8 (2026-09-17; supersedes v1–v7).** Drafting must not
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
  `seed_*` directory can stop early. Reported counts are therefore **13 / 6 / 4 / 3** completed
  searches for Fe / Fe-B / Fe-Co / Fe-Co-B.
- **Search-level significance comes from the two-sided permutation test in `ensemble_analysis.py`**,
  whose resolution is bounded by `perm_n_partitions` in `analysis/ensemble_stats.json`. Check that
  bound before reading any p-value close to the floor (4 vs 3 searches admit only 35 partitions, so
  p >= 0.029 there).

## Drafting status

**Approval state is authoritative in `paper_status.md`** — read its "Drafting progress" table before
drafting or revising anything. Summary as of 2026-09-17:

- **Phase A: DONE** (contribution + claim list signed off 2026-09-16).
- **Phase D: DONE for the main text** — 13 citations verified in `references.bib` (agox2020,
  gofee2017, oganov2011, gpaw2014, pbe1996, greer1993, urano1988, butler2001, yuasa2004,
  reitinger2007, fahsold2000, larsen2009, torelli2009); every `\cite{}` key resolves and none is
  orphaned. The three MTJ placeholders were **withdrawn** and replaced by `yuasa2004`; no UNVERIFIED
  placeholders remain. Open: `fahsold2000`, `reitinger2007` and `torelli2009` are closed access and
  cited from verified abstracts only.
- **Phase E: IN PROGRESS — no section is currently approved.**
  - `01_methods.md` **v4** — approval **VOIDED** (edited after approval; §1.6 then §1.2) → re-approval.
  - `02_results.md` **v3** — needs re-approval (reconstructed, then extended).
  - `03_discussion.md` **v4** — awaiting first review. **This is the gate: do NOT draft
    `04_introduction.md` until 03 is approved.**
  - `SI.md` **v3** — §S1, §S2, §S3 drafted, awaiting review.
  - `04`–`06` not drafted; no LaTeX until all sections are approved.
- **BEFORE publishing §1.1 or §3.1 as they stand, read `paper_status.md` → "Open decisions":** the
  Fe/Fe-B models sit on `a_Fe` (substrate strained) while the Fe-Co/Fe-Co-B models sit on
  `a_MgO/√2` (**film stretched 4.9 %**) — `interpolation_factor` 0 vs 1. Both sections currently
  describe one convention for all four models, and the cross-host comparison is confounded by this.
  **Unresolved; awaiting the scientist.**
- **float numbering:** sequential in order of appearance across the drafted sections.
  Currently Tables 1–3 + Figure 1 (Methods), Tables 4–5 (Results); the SI has its own `S` series
  (Tables S1–S3, Figures S1–S6). See `paper_status.md`.
- **Phase F/G: not started.**
- Reference PDFs live in `papers/` (e.g. `papers/confusion_greer1993.pdf` → `greer1993`).

## Checkpoint / resume

- Always write/update `paper_status.md` before ending a session.
- A fresh session must be able to resume from `paper_status.md` alone (the file is the memory).

## Data & scope

- Raw data lives in `data/` (AGOX/**GOFEE** structure-search databases):
  - **Four main systems:** `femgo` (Fe/MgO), `febmgo` (Fe-B/MgO), `fecomgo` (Fe-Co/MgO),
    `fecobmgo` (Fe-Co-B/MgO).
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
- Flatness metric: **ΔZ = z(metal_max) − z(metal_min)** over all metal film atoms (Fe+Co)
  [Å]; ΔZ ≈ 0 = flat film (wet), ΔZ large = island (dewet).
- PES coordinate: **dE/N = (E_i − E_globalmin)/N_atoms** [eV/atom], global min = 0,
  computed per system over the iteration>=10 set. Flat/island basins split at ΔZ ≤ 1.0 Å.
- The `febmgo` / `fecobmgo` energy ranges contain relaxation artifacts / unphysical
  high-energy structures; the iteration filter + per-system global-min normalization
  window these out.
- Co systems have fewer seeds (fecomgo 5, fecobmgo 4) than the Fe systems (femgo 13,
  febmgo 6) — note this when reporting uncertainty.

## Commit discipline

- Commit after every change/milestone, with a descriptive message.
- Confirm with the scientist before committing on each milestone.
- Never commit the `data/` tree or other unrelated changes in the parent `research/` repo.
