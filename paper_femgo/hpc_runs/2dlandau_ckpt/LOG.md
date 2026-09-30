# LOG.md — `hpc_runs/2dlandau_ckpt` (append-only)

## 2026-09-27 — checkpoint/resume standalone HPC runner

Created as the fully standalone, current-version sibling of `hpc_runs/2dlandau`
(which is left intact). Based on `codes/2dlandau` **with** the checkpoint/resume
feature (spec `202609271240`, v8, approved + executed, source commit `3acb7fd`).

Contents:
- `main.py` v1.1.0 (checkpoint-enabled) with `DATA_DIR` rewritten to in-dir
  `os.path.join(_HERE, "data", "femgo")` (everything in-dir at run time).
- `landau_2d/` package verbatim from `codes/2dlandau` (`wang_landau_2d.py`
  v1.2.0 = `state_dict`/`load_state` + `run(checkpoint_interval, callback)`).
- `data/femgo/` — the 13 input seed DBs (`seed_*/1_db/db_*.db`), force-committed
  via `.gitignore` negation (output/ still ignored).
- `job_2dlandau.sh` — PJM header (64 cores, 120 h), `gpaw_env` + `--use-ray`,
  `--mc-steps 100000 --checkpoint-interval 100`, physical
  `--temperatures 298,573,623,673,773`, `--relax-steps 100`,
  `--reference-steps 5000`. Resubmit after interruption → auto-resume.
- `.gitignore`, `README.md`, this LOG.

Notes:
- No `output/` is shipped — the standalone starts clean (first HPC submit =
  fresh run; resubmit resumes). This mirrors the source convention.
- `--use-ray` is HPC-only (`gpaw_env`); local checks use `agox_v2`.

Verification (pending full acceptance run): `py_compile` + in-dir glob check
(13 DBs) + `git add -n` confirms the DBs will commit and `output/` stays
ignored. A `--mc-steps 1 --reference-steps 5` smoke run (agox_v2, real GPR) is
scheduled/optional given the same code is verified in `codes/2dlandau`.
