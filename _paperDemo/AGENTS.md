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
- **The claim list is FROZEN in `CLAIMS.md` v1 (signed off 2026-09-16).** Drafting must not
  introduce claims outside it, and must not drop the paired caveats. Any new claim requires
  bumping `CLAIMS.md` to v2 first.

## Drafting status

- **Phase A: DONE** (contribution + claim list signed off 2026-09-16).
- **Phase D: PARTIAL** — 6 citations verified in `references.bib` (agox2020, gofee2017,
  oganov2011, gpaw2014, pbe1996, greer1993). MTJ/PMA refs (cofebmgo_mtj, cofebmgo_pma,
  b_diffusion_mtj) still UNVERIFIED in 03_discussion.md.
- **Phase E: IN PROGRESS** — `01_methods.md` APPROVED, `02_results.md` APPROVED,
  `03_discussion.md` drafted v2 (awaiting review). Block-and-wait: do NOT draft
  `04_introduction.md` until 03 is approved.
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
  febmgo 7) — note this when reporting uncertainty.

## Commit discipline

- Commit after every change/milestone, with a descriptive message.
- Confirm with the scientist before committing on each milestone.
- Never commit the `data/` tree or other unrelated changes in the parent `research/` repo.
