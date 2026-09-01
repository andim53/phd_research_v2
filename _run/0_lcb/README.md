# Project 0 — LCB (Pt-P interstitial alloy)

Lower Confidence Bound (LCB) active-learning search for **phosphorus interstitials
in a platinum host** (Pt–P interstitial alloy), run with AGOX + GPAW DFT.

## What this project is

This directory is the AI-Agent Project Workflow home for the **Pt–P LCB search**.
It currently houses a large pre-existing AGOX analysis/run tree (`2_analysist/17_PPt/`)
that was started outside the workflow and is now being brought under it.

- **Host:** Pt (fcc), lattice constant `a = 3.975534 Å` (optimized), supercell
  scaled +5% (`SCALE_CELL = 1.05`).
- **Interstitial:** P, inserted at a target concentration (0 / 10 / 20 / 30 %,
  plus a 4×4 20 % run), computed as `B = (C·A)/(1−C)`.
- **Search:** AGOX with `LowerConfidenceBoundAcquisitor`, GPR + Fingerprint
  descriptor, generators `AmorphStructRandomize` / `RattleGenerator` /
  amorph permutation, relaxation via `LocalOptimizationEvaluator` +
  `ParallelRelaxPostprocess`, GPAW (LCAO/dzp/PBE) DFT.
- **Goal:** find low-energy Pt–P interstitial configurations under an LCB
  (exploration/exploitation) acquisition rule.

## Directory layout

```
0_lcb/
├── README.md            # this file (human overview)
├── README.AI.md         # agent-facing spec
├── LOG.md               # append-only action log
├── TUTORIAL.md          # reproduce/usage guide
├── VERSIONS.md          # source version manifest
├── AGENTS.md            # governing rules for AI agents
├── PROMPTS.md           # future-work prompt log (+ shared grammar notes)
├── 2_analysist/          # analysed results (kept separate)
│   ├── run_analysis_indices.py   # analysis runner (v2.1.0, project-agnostic)
│   ├── scripts/                  # runner dep (plot_structure_landscape.py)
│   ├── 11_bTa/                   # Ta–B results (README tracked; run data gitignored)
│   ├── 15_bPt/                   # Pt–B results
│   ├── 16_bW/                    # W–B results
│   └── 17_PPt/                  # pre-existing Pt–P analysis/run tree (incorporated)
└── 1_runs/               # (empty) future self-contained run dirs
```

## Notes

- **`17_PPt/` is the incorporated analysis tree.** It holds the actual Pt–P runs
  grouped by supercell family and P concentration. Each leaf dir carries
  `seed_*/1_db/db_*.db` AGOX databases plus `scripts/` and `main.py`. It predates
  this project scaffold and is kept in place, not reorganized.
- **`run_analysis_indices.py` is the project-agnostic analysis runner** (v2.1.0),
  adapted from the sibling `a_lcbnovel` Fe/MgO runner. It analyses **any** of the
  interstitial-alloy families under `2_analysist/` (`11_bTa`, `15_bPt`, `16_bW`,
  `17_PPt`). Point `--dataset` at one leaf dir (holding `seed_*/1_db/db_*.db`) and
  `--outdir` at its analysis output; run **per leaf**. Each family dir carries a
  `README.md` with the exact run command for its leaves. See README.AI.md §2b/§3.

## Environment

- **Local dev/test:** conda env `agox_v2`
  (`/home/think/miniconda3/envs/agox_v2/bin/python`; AGOX 3.10.2 + ASE + GPAW).
- **HPC pjsub runs:** `gpaw_env` (activated inside the batch script).
  Launch via `pjsub j_*.sh` with the seed set by editing a `SEED=`/loop variable —
  never `pjsub -x`.

## Status

- [x] Project scaffold (doc trio + AGENTS + VERSIONS + PROMPTS) created
- [x] Existing `2_analysist/17_PPt/` tree incorporated and documented
- [x] `run_analysis_indices.py` made project-agnostic (analyses 11_bTa/15_bPt/16_bW/17_PPt) + per-family READMEs
- [ ] Analysis results generated (per-leaf run) and discussed (per-analysis `DISCUSSION.md`)
- [ ] Any new heavy runs added under `1_runs/<NN>_<descriptor>/`
