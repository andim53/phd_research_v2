# TUTORIAL.md — Reproduce & use this project

How to work with `_run/0_lcb` (Pt–P interstitial-alloy LCB AGOX search).

## Prerequisites

- conda env **`agox_v2`** (`/home/think/miniconda3/envs/agox_v2/bin/python`) — AGOX,
  ASE, GPAW, numpy, scipy, matplotlib. Base `python3` has **none** of these.
- For HPC pjsub runs: `gpaw_env` (activated inside batch scripts).

## Step 1 — Understand the layout

Read `README.md` (human) and `README.AI.md` (agent spec), and `AGENTS.md` for the
operating rules. The project currently holds:

- `2_analysist/17_PPt/` — the incorporated Pt–P run/analysis tree.
- `1_runs/` — empty; future self-contained runs go here.

## Step 2 — Syntax-check the tracked source

```bash
PY=/home/think/miniconda3/envs/agox_v2/bin/python
cd /home/think/Desktop/research/_run/0_lcb
$PY -m py_compile 2_analysist/run_analysis_indices.py
$PY -m py_compile 2_analysist/17_PPt/2_plus3cell/main.py
$PY -m py_compile 2_analysist/17_PPt/scripts/*.py
```

> If the LSP/Pyright flags AGOX/ASE imports as unresolved, ignore it — judge by the
> **env python's** `py_compile`, not the base-python LSP.

## Step 3 — Run analysis (once the runner is retargeted)

**Important:** `2_analysist/run_analysis_indices.py` is currently an **Fe/MgO-scoped
copy** from `a_lcbnovel`. It does **NOT** match the Pt–P `17_PPt` layout. Do not run
it on `17_PPt` until it has been retargeted (see README.AI.md §5 / §2b).

After retargeting, the intended CLI is the standard 3-stage analysis runner:

```bash
$PY 2_analysist/run_analysis_indices.py \
    --dataset <dir-with-seed_*/1_db/db_*.db> \
    --outdir <out> \
    [--e-max <eV/atom>] [--normalize-density] [--start-iter <N>]
```

Outputs: `progression_*.png`, `conf_space.png`, `binding_probability_vs_temperature.png`.

## Step 4 — (Future) HPC heavy runs

Heavy runs go in self-contained `1_runs/<NN>_<descriptor>/` dirs (job `j_*.sh` +
`main*.py` + `scripts/`). Batch scripts use `gpaw_env` and PJM:

```bash
# edit the seed / concentration in the script, then:
pjsub j_*.sh            # NEVER pjsub -x
```

## Pitfalls

- **Runner mismatch:** don't run the Fe/MgO-scoped `run_analysis_indices.py` on
  Pt–P data.
- **Duplicated scripts:** many `scripts/*.py` copies exist across `17_PPt` run dirs.
  Edit the **canonical** `17_PPt/scripts/` + family `main.py`, not per-run snapshots.
- **Energy units/windows:** Fe/MgO vs Pt–P energy scales differ; keep assumptions
  per-system.
- **Trailing-space dirs:** never create run dir names with trailing spaces.
- **Git scope:** always stage explicit pathspecs for `0_lcb` (it lives inside the
  parent `research` repo); never `git add -A`.

## Verification checklist

- [ ] `py_compile` passes under `agox_v2` for the tracked source
- [ ] Docs (README/README.AI/TUTORIAL/VERSIONS/AGENTS/PROMPTS/LOG) consistent
- [ ] `17_PPt/` incorporated without reorganization
- [ ] No regenerable outputs (db/xsf/png/log) staged into git
- [ ] Changes committed with explicit pathspec for `0_lcb`
