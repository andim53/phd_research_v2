# b_nestedsampling project layout & self-contained HPC run dirs

The canonical/active project is `/home/think/Desktop/research/_run/b_nestedsampling/`
(re-hosted from the older `_run/8_nested_sampling/`, which remains only as a source
reference). Follow this layout; the `8_nested_sampling` paths in older notes/skill text
are superseded.

## Root layout

- `main.py` — the nested-sampling runner (renamed from `run_nested_sampling.py`). Loads
  all seed DBs, trains one combined GPR, runs `NestedSampler`, writes evidence/posterior
  outputs, and runs the state-density analysis. Also has a temperature-free mode
  (`--temperature-free` + `--temperatures`).
- `nested_sampling/` — importable package (`NestedSampler`, `gpr_training`, `state_density`,
  `utils`).
- `gpr_accuracy.py` — GPR-surrogate accuracy/uncertainty analysis. **Orthogonal opt-in
  flags all reuse the SAME trained model / predictions** rather than each re-training:
  `--cv` (K-fold, stratified by energy bin), `--uncertainty` (model predictive std),
  `--fez` (vs delta Fe_z = Fe island height), `--rattle` (vs rattling distance). This
  one-model-shared-across-flags design keeps runs fast and results comparable.
- `dataset/` — `seed_<N>/1_db/db_<N>.db` per seed (13 DBs, seeds 3–15, Mg25O25Fe25).
- `j_nestedsampling.sh` — bare PJM batch script (24 cores, `gpaw_env`).
- `_runs/<NN>_<descriptor>/` — self-contained HPC run dirs (see below).
- `_tmp/` — scratch/analysis outputs (gitignored; DISCUSSION.md lives with its results).

## Self-contained HPC run dirs (`_runs/<NN>_<descriptor>/`)

Each run dir is fully independent and launchable on HPC:
- `gpr_accuracy.py` (or `main.py`) — copied from the latest project-root version (check
  `__version__` in the root, copy verbatim).
- `dataset/` — full copy (seed DBs are gitignored but must be present for the run).
- `j_<descriptor>.sh` — bare PJM script: 24 cores, `conda activate gpaw_env`,
  `module load intel impi`, then `OMP_NUM_THREADS=1 python ./gpr_accuracy.py <flags>`.
- `README.md` + `TUTORIAL.md` — per-run docs (workflow convention).

git tracks only code + docs (the ~23 MB seed `.db` are excluded); a `git add -n` dry-run
confirms exactly what will be tracked. Name runs `<NN>_<descriptor>` (e.g.
`b1_gpr_accuracy_cv10_bin005`).

## gpr_accuracy.py physical filter (important)

When rattling/perturbing structures moves them off the training manifold, the Fingerprint
GPR predicts absurd (unphysical) energies — up to ~1e30 eV. **Filter these**: exclude any
prediction with |E| > 1e4 eV from the MAE/RMSE/R^2 metrics and count them in an
`n_unphysical` column. Without this filter one or two garbage predictions corrupt the
aggregate metrics (MAE balloons to 1e30). This is the same `|E|>1e4` guard the sampler uses
for its own likelihood. In-sample MAE is near-zero by construction (interpolation); only
`--cv` gives the honest held-out generalization picture.
