# Novelty-LCB Search of Fe on MgO(001) — Project 10

## What this project accomplishes

This project reproduces and repairs the Fe/MgO **Novelty-LCB** search originally
written in `_run/7_lcbnovel_mgofe`, and re-hosts it as a clean, fully documented
project following the AI-Agent Project Workflow (README + LOG + TUTORIAL).

The physics goal: run an AGOX global-optimization search that deposits 25 Fe atoms
on a fixed MgO(001) substrate, using a **Novelty-LCB** acquisition function

    a(x) = σ(x) + λ · Novelty(x),   Novelty(x) = min_{i ∈ DB} ‖fingerprint(x) − fingerprint(x_i)‖₂

restricted to an energy window `E_target ± ΔE`, so the search is pushed toward
configurations that are simultaneously **uncertain** and **structurally distinct**
from everything already seen — rather than just re-optimising the same basins.

Run 7 never actually ran: its output log shows it crashed at seed 3 on a Ray
serialization error (`cannot pickle 'sqlite3.Connection'`), and it was never
re-launched after the acquisitor fix. **This project is the repair**: it ships the
fixed `novelty_lcb` package, a faithfully-wired `main.py`, a validated
serialization smoke test, and the batch scripts/docs to actually run it on the HPC
cluster.

## Who it's for

- **You** (the researcher): to launch and interpret the Novelty-LCB Fe/MgO search.
- **AI agents** (e.g. Calyx): a machine-readable spec of the layout, commands,
  dependencies, inputs/outputs and edge cases (see `README.AI.md`).
- Anyone reproducing run 7 or extending the Novelty-LCB-on-AGOX work.

## How to use it (high level)

```bash
# 1. Quick local sanity check (cheap, no GPAW): verifies the serialization fix
/home/think/miniconda3/envs/agox_v2/bin/python smoke_test_serialization.py

# 2. Local smoke of the real slab builder (builds the 25-Fe / MgO structure only)
/home/think/miniconda3/envs/agox_v2/bin/python -c "from main import build_slabs, build_environment; s,d,st=build_slabs(); print(s.get_chemical_formula(), len(s), st)"

# 3. Launch the heavy search on the HPC cluster (uses gpaw_env; one pjsub job)
pjsub j_novel.sh                    # runs the seed set in the script (edit SEED=3 to change)
```

## Key decisions & tradeoffs

| Decision | Choice | Why |
|---|---|---|
| Base project | `7_lcbnovel_mgofe` | Fe/MgO is the target physical system; run 7 is the most complete attempt |
| `novelty_lcb` package | copied from run 7 (reused, not rewritten) | It already contains the serialization fix; lowest risk |
| Serialization fix | module-level free funcs + `functools.partial` in `get_acquisition_calculator()` | Bound methods drag the sqlite-backed `Database` into the Ray-put graph; free funcs capture only scalar `kappa` |
| Energy window | placeholder `target=0.0, ΔE=1.0` | **Uncalibrated** — must map the real band with a short standard-LCB run first |
| Compute | HPC PJM batch, 64-core GPAW (`gpaw_env`) | SubprocessGPAW LCAO/dzp needs a cluster node; run `pjsub j_novel.sh`, seed set by editing `SEED=` in the script |
| Logging | curated `LOG.md` + raw `transcript.log` | Human-readable milestones plus a faithful tool-call record |

## Status

- [x] `novelty_lcb` package + scripts copied and compiling under `agox_v2`
- [x] `main.py` faithfully re-wired (same physics as run 7)
- [x] Serialization smoke test **PASSES** (crash root cause verified fixed)
- [ ] Heavy Fe/MgO search launched on HPC (see `TUTORIAL.md` step 4)
- [ ] Energy-window calibrated from a short standard-LCB run (see `TUTORIAL.md` step 5)

See `TUTORIAL.md` for the full reproduction and repair guide, `LOG.md` for what
has been done, and `README.AI.md` for the agent-facing spec.
