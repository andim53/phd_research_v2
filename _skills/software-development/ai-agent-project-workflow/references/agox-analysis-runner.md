# Adding an analysis runner to `_analysist` (AGOX results)

Worked pattern (learned maintaining project 10, `a_lcbnovel`) for when the user drops
run results into `_analysist/1_result/` and asks for "an analysis code like
<sibling>/run_analysis_indices.py". The sibling runner lives at
`/home/think/Desktop/research/_analysist/run_analysis_indices.py`.

## Approach

1. **Read the sibling runner + trace its imports first.** The reference 3-stage
   pipeline is: ① `process_database` (AGOX `.db` → traj/xsf/csv), ② PCA landscape
   (`plot_structure_landscape`), ③ Boltzmann probability. Trace exactly which
   `scripts/` modules it imports (`process_database` imports
   `calculate_relative_energy`).
2. **Copy only the needed deps** into a local `_analysist/scripts/` so the runner is
   self-contained and callable in place. Do NOT copy the whole (often large) sibling
   `scripts/` dir with unrelated generators. For the 3-stage runner this is exactly
   `process_database.py`, `plot_structure_landscape.py`, `calculate_relative_energy.py`.
3. **Scope the runner to what the layout supports.** `process_database` (reference
   `scripts/process_database.py`) locates DBs via `root.glob("seed_*")`, each seed
   holding `seed_<N>/1_db/db_<N>.db`; if no `seed_*` dirs it falls back to a flat
   `1_db/db_0.db`. Fe/MgO heavy runs nest the DBs under `output/seed_<N>/1_db/`, so
   `FOLDER_MAP` should point at the `output/` dir, e.g.
   `71 -> 71_novel_runEWindow/output`.
   **Flat benchmark dirs** (e.g. `benchmark_results/` with `surface_run*_db.db`,
   `sweep_kappa_lambda/kX_lY/*.db`) have no `seed_*` layout and `process_database`
   finds nothing — either exclude them (they usually carry their own DISCUSSION.md /
   results JSON) or add a custom flat-DB stage-1 aggregator. Confirm the scope choice
   via clarify (in the a_lcbnovel session the user chose to support only the Fe/MgO
   heavy runs 71/72 and exclude the EMT benchmarks 73/74).
4. **Keep the sibling CLI surface** (`--indices`, `--e-max`, `--normalize-density`,
   `--skip-probability`) and add a `--idx` single-index shorthand; correct any
   env/paths in the docstring to the local machine (`/home/think/miniconda3/envs/agox_v2`).
5. **Verify end-to-end** under `agox_v2`: run each index and confirm real outputs
   appear under `0_analy/idx_<N>/` — `1_xsf_traj/traj_<N>.traj`, `data_<N>.csv`,
   `progression_*.png`, `2_im/conf_space.png`,
   `2_im/binding_probability_vs_temperature.png`. `py_compile` clean.

## Pitfall — nested project `.gitignore` doesn't inherit the parent's `_analysist` rules

If the project lives inside a larger git repo (e.g. `_run/<NN>_<name>/` under
`/home/think/Desktop/research`), the parent's `.gitignore` `_analysist/0_analy/` /
`_analysist/1_result/` rules target the PARENT's `_analysist`, not the nested one. So
the nested project's `0_analy/` + `1_result/` (and `.traj` files) leak as untracked.
Fix: add a **project-level `.gitignore`** ignoring `_analysist/0_analy/`,
`_analysist/1_result/`, and regenerable types (`*.db`, `*.png`, `*.traj`, `*.xsf`,
`*.csv`, `*.out`, `__pycache__/`), so only the runner + `scripts/` code are tracked.
Confirm with `git status --untracked-files=all` that only intended files remain.

(Detail is duplicated at a summary level in the skill's SKILL.md "Run-directory
convention" section.)
