# Per-run `_runs/` dirs and a kappa-sweep (worked example, 2026-08-26)

## The per-run `_runs/` convention

Heavy Fe/MgO Novelty-LCB runs are **self-contained per-seed dirs** under `_runs/`.
Each must be independent of the project root (AGENTS.md policy):

```
_runs/<NN>_<descriptor>/
├── j_novEperAtom.sh        # PJM batch script; edit SEED=, N_ITERATIONS=, (KAPPA=)
├── main.py                 # latest versioned copy from project root
├── novelty_lcb/            # latest versioned package copy
├── scripts/                # latest slab/generator builders
├── README.md               # per-run overview, specific to that run's treatment
└── TUTORIAL.md             # how to reproduce THAT run
```

- Per-seed runs carry README.md + TUTORIAL.md (NOT the full README.AI/LOG trio — the
  project root owns those). Standalone benchmarks (e.g. 73_novel_benchEMT) carry the
  full trio.
- Keep run copies current: after any root change, `cp main.py novelty_lcb/*.py
  scripts/*.py <run>/`. All run copies stay at the root `main.py` `__version__`.
- Naming: `<NN>_<descriptor>`, e.g. `a1_mgofe_Seed3_Iter300`. The `a<N>` series
  continues across iterations (a1/a2/a3) and sweeps (a4/a5/a6).

## Making a parameter sweep ("just like iterations")

The owner wants a swept parameter (kappa, but applies to any) wired the SAME way the
iteration budget is: a `VAR=` line in `j_*.sh` plus a matching `--var` CLI flag on
`main.py`. Do NOT hard-edit `main.py` per run — that breaks run/root sync.

Worked example — kappa 3/4/5 sweep of the a2 base (kappa=2.0):

1. **root `main.py`** (bump `__version__` 1.0.0 -> 1.1.0, minor = new CLI arg):
   - `ap.add_argument("--kappa", type=float, default=KAPPA, help=...)`
   - `def build_stack(environment, slab_deposition, db_path, seed, kappa=KAPPA):`
   - acquisitor: `kappa=kappa,` (was `kappa=KAPPA,`)
   - call site: `build_stack(env, slab_deposition, f"{db_dir}/db_{seed}.db", seed,
     kappa=args.kappa)`
   - update docstring Usage line to show `--kappa 3.0`.
   - Verify `py_compile` + `main.py --help` shows `--kappa KAPPA`.
2. **`VERSIONS.md`**: bump `main.py` row.
3. **Sync** new `main.py` into a1/a2/a3/73 (all at 1.1.0).
4. **Create each sweep run**: `cp -r <base> a<N>_mgofe_Seed3_Iter500_k<val>`; remove
   `__pycache__`. Name suffix `k<num>` (e.g. `_k3`). For 3/4/5 -> `a4_..._k3`,
   `a5_..._k4`, `a6_..._k5`.
5. **Each `j_*.sh`**: add `KAPPA=<val>` and `--kappa "${KAPPA}"` on the python line;
   extend the echo to include `kappa=${KAPPA}`.
6. **Rewrite each run's README.md/TUTORIAL.md** to be specific to its kappa, with a
   sibling-difference table (base value vs each sweep value).

## PROMPTS.md flag convention

The owner keeps multiple prompts in `PROMPTS.md` and wants a flag on each. Label each
prompt with a **first-level** heading above it:

```
# FLAG: YYYYMMDD_HH
```

The code is derived from year-month-day-hour of the local time (get it from
`date '+%Y%m%d_%H'`), e.g. `20260826_14`. When asked to "fix grammar," preserve the
prior text: keep both "Original (before grammar fix)" and the fixed version. The user
explicitly required the flag be `#` (one hash) first-level, not `##`.
