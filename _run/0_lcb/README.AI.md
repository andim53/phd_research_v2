# README for AI Agents — Project 0 (`0_lcb`)

Machine-readable spec for agents working on this project. Complements the
human-facing `README.md`. **Read `AGENTS.md` first** for the operating rules.

## 1. Project identity

- **Dir:** `/home/think/Desktop/research/_run/0_lcb/`
- **Purpose:** Lower Confidence Bound (LCB) AGOX search for **P interstitials in a
  Pt (fcc) host** (Pt–P interstitial alloy). Home to the pre-existing `17_PPt`
  analysis/run tree, now under the AI-Agent Project Workflow.
- **Physics:** Pt fcc host (`a = 3.975534 Å`), cell scaled +5%, supercell 3×3×3
  (and variants), P interstitials at 0/10/20/30 %, `LowerConfidenceBoundAcquisitor`,
  GPR + Fingerprint, GPAW LCAO/dzp/PBE.
- **Environment (invariant):** `/home/think/miniconda3/envs/agox_v2/bin/python`
  (AGOX + ASE + GPAW) for local work; `gpaw_env` on HPC (activated in batch
  scripts). Base `python3` has **no** AGOX/ASE/GPAW.

## 2. File layout

```
0_lcb/
├── README.md            # human overview
├── README.AI.md         # this file (agent spec)
├── LOG.md               # curated, append-only action log
├── transcript.log       # raw tool-call / run-output transcript (gitignored, *.log)
├── TUTORIAL.md          # reproduce/usage guide with pitfalls + verification
├── VERSIONS.md          # source version manifest
├── AGENTS.md            # governing rules for AI agents
├── PROMPTS.md           # future-work prompt log (+ shared grammar notes)
├── .gitignore           # project-level ignores (regenerable outputs)
├── _analysist/          # analysed/intermediate results (separate from runs)
│   ├── run_analysis_indices.py   # analysis runner (v2.1.0, project-agnostic)
│   ├── scripts/                  # runner deps (plot_structure_landscape.py)
│   ├── 11_bTa/                   # Ta–B results (run data gitignored; README tracked)
│   ├── 15_bPt/                   # Pt–B results
│   ├── 16_bW/                    # W–B results
│   └── 17_PPt/                  # incorporated Pt–P analysis/run tree
│       ├── 0_plus5cell/         #   supercell-family AGOX runs (0_PPt_4x4_20P,
│       ├── 1_plus0cell/         #     1_3x3_20P, 2_3x3_30P, 3_3x3_0P, 4_3x3_10p)
│       ├── 2_plus3cell/         #   ... plus P-concentration subdirs 0P/10P/20P/30P
│       ├── 3_plus10cell/        #
│       ├── scripts/             #   canonical structure/generator/analysis scripts
│       ├── job.sh, main.py      #   run entry points
│       └── <cell>/<conc>/seed_*/1_db/db_*.db   # AGOX databases (gitignored)
└── _runs/               # (empty) future self-contained run dirs
```

> `_analysist/11_bTa/` (a Ta–B system) is present on disk but **gitignored** — it is
> off-scope for this Pt–P project and excluded from commits (see `.gitignore`).

### 2a. `_analysist/17_PPt/` — incorporated analysis tree

- The bulk of this project's content. It is a **pre-existing Pt–P run tree** that
  was placed here before the workflow scaffold, and is **kept as-is, not
  reorganized**.
- Organised by **supercell family** (`0_plus5cell`, `1_plus0cell`, `2_plus3cell`,
  `3_plus10cell`) and, within each, by **P concentration** (`0_0P`, `1_10P`,
  `2_20P`, `3_30P`, plus `0_PPt_4x4_20P`). Each leaf has `seed_*/1_db/db_*.db`
  databases (gitignored), `0_result/` (xsf/figs, gitignored), `scripts/`, and
  `generated_structures/` + `gpaw_logs/` (gitignored).
- **Many files are duplicated** script snapshots (`scripts/*.py` copied into each
  run dir) and PJM job scripts (`j_*.sh`). The project-level `.gitignore` keeps
  per-run generated outputs out of git; the canonical source lives in
  `17_PPt/scripts/` and each family's `main.py`.

### 2b. `run_analysis_indices.py` — analysis runner (project-agnostic)

- `__version__ = "2.1.0"`. Adapted from the `a_lcbnovel` Fe/MgO runner; this copy is
  **project-agnostic** — it globs `seed_*/1_db/db_*.db` and reads the atom count
  from each structure, so it runs on any interstitial-alloy family under
  `_analysist/` (11_bTa, 15_bPt, 16_bW, 17_PPt).
- **Dependency:** imports `scripts/plot_structure_landscape.py` (copied into
  `_analysist/scripts/`; self-contained, only stdlib/numpy/scipy/matplotlib).
- Point `--dataset` at **one leaf** dataset dir (a dir holding `seed_*/1_db/db_*.db`)
  and `--outdir` at its analysis output. Run per leaf. Each family dir carries a
  `README.md` with the exact invocation for its leaves.
- 3-stage pipeline: ① best-so-far progression, ② PCA landscape, ③ Boltzmann
  probability. CLI: `--dataset --outdir --e-max --normalize-density --start-iter`.

## 3. Entry points & commands

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
cd /home/think/Desktop/research/_run/0_lcb

# Compile-check tracked source (syntax gate)
$PY -m py_compile _analysist/run_analysis_indices.py
$PY -m py_compile _analysist/17_PPt/2_plus3cell/main.py
$PY -m py_compile _analysist/17_PPt/scripts/*.py   # canonical scripts
```

> LSP/Pyright under base `python3` flags AGOX/ASE imports as unresolved even when
> code compiles under `agox_v2` — judge by the env python's `py_compile`, not the LSP.

### HPC run (future / existing)

Batch scripts use `gpaw_env` and the `#PJM` scheduler. Launch with
`pjsub j_*.sh` (seed/concentration edited in the script; never `pjsub -x`).

## 4. Dependencies

- `agox_v2` conda env: AGOX 3.10.2, ASE, GPAW, numpy, scipy, matplotlib.
- HPC `gpaw_env` for pjsub runs.

## 5. Known gaps / error handling & edge cases

- **Runner mismatch (highest priority):** `run_analysis_indices.py` is Fe/MgO
  scoped. Do not run it on `17_PPt` as-is — outputs/errors will not be meaningful.
- **Duplicated scripts:** many `scripts/*.py` copies exist across run dirs. Edit
  the **canonical** `17_PPt/scripts/` and family `main.py`; per-run copies are
  snapshots (see `VERSIONS.md` scope note).
- **Energy units/windows:** the runner's Stage 2/3 energy caps and the `17_PPt`
  configurations are Fe/MgO vs Pt–P specific — do not mix assumptions.

## 6. Provenance

- `17_PPt/` predates this scaffold (runs dated Jul–Aug 2026, `run_YYYYMMDD_*`
  structure timestamps). It was incorporated verbatim into `_run/0_lcb/`.
- `run_analysis_indices.py` copied from `a_lcbnovel` (identical), pending
  Pt–P retarget.
- Scaffold (this doc set) created 2026-08-31 under the AI-Agent Project Workflow.
