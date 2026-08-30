# DISCUSSION — a1_mgofe_Seed3_Iter300 single-seed analysis

Run: `a1_mgofe_Seed3_Iter300` (Novelty-LCB Fe/MgO search, seed 3, 300 iterations)
Analysis dir: `_analysist/a1_mgofe_Seed3_Iter300/analysis_a_runs`
Produced by: `_analysist/run_analysis_a_runs.py` (v1.0.0)

## Running script

The exact command that produced this analysis (run from
`/home/think/Desktop/research/_run/a_lcbnovel/_analysist`, `agox_v2` env):

```bash
/home/think/miniconda3/envs/agox_v2/bin/python run_analysis_a_runs.py \
    --dataset a1_mgofe_Seed3_Iter300/output \
    --outdir a1_mgofe_Seed3_Iter300/analysis_a_runs
```

Parameters used (all defaults): `--start-iter 10` (keep AGOX iteration >= 10),
`--e-max` unset (Stage 2/3 use each stage's default limit), `--normalize-density` off
(state-density axis in config./eV).

## What was analysed

- Source data: `output/seed_3/1_db/db_3.db` — **291 / 300 structures** kept
  (AGOX iteration >= 10), **75 atoms each** (Fe25 on fixed Mg25O25).
- Global energy minimum: **E = −435.4113 eV**, found at **iteration 280**
  (rel. 0.0000 eV/atom).
- Relative-energy range: **0 → 0.505 eV/atom** (all kept structures).

## Stage 1 — Best-so-far progression (progression_seed_split_Seed3.png)

**What it is.** Per-candidate best-so-far of `(E − E_seed_min)/N` over the 291 kept
candidates for the single seed (Seed 3), with low-energy-window bullets (w0-20,
w20-40, w40-60, w60-80) and the global ground state (red `*`) exported as `.xsf`.

**What it means.** Shows how quickly the search lowers the best energy found. The
initial best is 0.325 eV/atom at candidate 10; it monotonically improves.

**What it implies (numbers).** Best-so-far reaches the global min (0.000 eV/atom) by
the end of the run. 91 of 291 structures (31%) sit within 0.05 eV/atom of the global
minimum — the search densely resamples the low-energy basin once found.

**Outcome.** The 300-iteration budget is sufficient for this seed to locate a clear
global minimum; the plateau in the latter part of the run indicates convergence of
the best-found energy. (Note: this is a **single seed** — a single trajectory, not
statistical evidence of landscape coverage.)

## Stage 2 — Landscape (conf_space.png)

**What it is.** PCA of the Fingerprint descriptors (PC1 on x) vs per-atom relative
energy (y), with a KDE state-density panel.

**What it means.** Collapses the high-dimensional structure space onto one descriptor
axis, colouring by energy, to expose how energy correlates with structure.

**What it implies (numbers).** The KDE density shows **one dominant low-energy peak at
0.058 eV/atom**, i.e. a single well-populated low-energy basin (no resolved second
peak). The lowest energy structures cluster at the bottom of the landscape.

**Outcome.** A single broad basin dominates; no well-separated secondary minimum is
resolved at this sampling density.

## Stage 3 — Boltzmann probability (binding_probability_vs_temperature.png)

**What it is.** `P(E) = ρ(E)·exp(−ΔE/kT)/Z` (peak-normalized) vs relative energy for
temperatures 298.15 – 646.425 K.

**What it means.** Temperature-weighted occupation probability of energy levels —
where the ensemble concentrates at each T.

**What it implies (numbers).** At 298.15 K the probability peaks at rel. **0.007
eV/atom**; at 646.425 K it shifts up to **0.032 eV/atom**. Higher temperature populates
slightly higher-energy states, as expected, but the distribution stays tight around
the low-energy basin.

**Outcome.** Strongly peaked at low energy across all temperatures; thermal broadening
is modest over this T range.

## Overall interpretation

- **Verdict.** Seed 3's 300-iteration Novelty-LCB search converges to a single
  low-energy Fe/MgO basin (global min −435.411 eV at iteration 280), densely sampled
  (31% within 0.05 eV/atom). Landscape is single-basin; Boltzmann population remains
  low-energy-peaked up to 646 K.
- **Caveats.** Single seed → single trajectory, no cross-seed statistics. `--e-max`
  unset means Stage 3 plots the full 0–0.505 eV/atom range; a tighter `--e-max` would
  zoom the low-energy region. No `.traj`/posterior (analysis reads the AGOX DB
  directly).
- **Bottom line.** This short (300-iter) run validates the Novelty-LCB stack on the
  Fe/MgO system and finds a well-defined ground state; longer sibling runs (a2/a3)
  and multi-seed runs are needed to assess landscape coverage and reproducibility.
