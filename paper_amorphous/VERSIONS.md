# VERSIONS.md — paper_amorphous

Per-file `__version__` manifest. Bump patch on any edit, minor on behavior change. Update this file + LOG.md on every code change.

| File | Version | Notes |
|------|---------|-------|
| `hpc_runs/select_reopt/filter_select.py` | 1.0.0 | Run A stage 1: per-leaf novelty+force filter → `selected/<leaf>/*.xsf` + selection JSON. Calibrated fingerprint tol; leaf-adaptive force cutoff (20P/30P) |
| `hpc_runs/select_reopt/reopt.py` | 1.0.0 | Run A stage 2: GPAW re-opt (lcao/dzp/PBE, fmax 0.05) → `opt_novel_<leaf>.traj` ×4 |
| `hpc_runs/select_reopt/job_genkai_mpi.sh` | — | pjsub wrapper (gpaw_env, 24 procs, 120 h) runs filter_select then reopt |
| `hpc_runs/shc/main.py` | 1.0.0 | Run B: FLAPW SCF→SOC→optics→xoptics + SHC parse → `shc_summary.{json,csv}`. Calc dir is self-contained (flapw.py read from CWD) |
| `hpc_runs/shc/flapw.py` | (copied) | ASE FLAPW calculator (standalone .py, not a package) — copied from `tmp/SHC Calculation/HEA_SHC_Auto_Python_FLAPW/` |
| `hpc_runs/shc/README_MT-default` | (copied) | FLAPW MT-default input, read from CWD by flapw.py |
| `hpc_runs/shc/setup_calc.sh` | — | Stages HPC binaries `pflapw` + `opt/xoptics` from FLAPW calc source (gitignored) |
| `hpc_runs/shc/.gitignore` | — | Ignores pflapw, opt/xoptics, *.traj (large HPC/hpc inputs) |
| `hpc_runs/shc/make_ref_traj.py` | 1.0.0 | Build 0%-P +0-cell reference traj |
| `hpc_runs/shc/job_genkai_mpi.sh` | — | Run B pjsub (per-leaf traj, TRAJ/OUT env) |
| `hpc_runs/convert_dose_concentration.py` | 1.0.0 | Reference ion-dose ↔ our at% P conversion helper |
| `hpc_runs/xrd_benchmark.py` | 1.0.0 | Write CIF+manifest for the existing XRD pipeline (amorphous vs ref) |
