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

## How the Novelty-LCB works

The acquisition function (implemented in `novelty_lcb/acquisitor.py`,
`calculate_acquisition_function`) is

    a(x) = σ(x) + λ · Novelty(x),    to be MAXIMIZED

subject to an energy-window constraint: only candidates whose predicted energy
`μ(x)` lies within `[E_target − ΔE, E_target + ΔE]` are considered; all others are
excluded.

### Q1 — What is Novelty(x)? How is it computed? 720-dim or PCA?
Novelty(x) is the structural novelty of candidate x: the **minimum Euclidean
distance in descriptor (fingerprint) feature space** between x and every structure
already in the database,

    Novelty(x) = min_{i ∈ DB} ‖f(x) − f(x_i)‖₂

It is computed with the **full 720-dimensional Fingerprint descriptor** — no PCA, no
dimensionality reduction. The code calls `descriptor.get_features(cand).ravel()`
(shape `(1, 720)` for Fe/MgO) and then `np.linalg.norm(db_feats - cand_feat, axis=1)`
before taking the minimum. A high value means the structure is unlike anything seen,
so the search is pushed into unexplored basins. When the database is empty,
Novelty = 0 and the acquisitor reduces to pure uncertainty sampling. This is the same
raw 720-dim distance used by `is_distinct` and the novel-filter in
`_run/9_novelFilter/`, so thresholds compose.

### Q2 — What is σ(x)? Uncertainty based on what?
σ(x) is the **predictive standard deviation of the GPR surrogate** at x — the
Gaussian-process posterior uncertainty in its predicted energy. It comes from
`model.predict_energy_and_uncertainty(cand)` and is **kernel-based**: it reflects how
far x sits from the training structures in the 720-dim feature space (plus the kernel
noise). Far from training data → high σ (the surrogate is unsure); near or between
training points → low σ. It is the surrogate's own estimate of what it does **not**
yet know about the landscape at x.

### Q3 — How is a candidate actually picked? Lowest a(x)?
AGOX sorts candidates **ascending** (lowest value = best = selected first). So the
code returns the **negated** acquisition value `-a(x)`, and the candidate with the
most negative value (i.e. the **largest true a(x)**) is selected first. Candidates
outside the energy window get `+∞` in the sorting space and are never selected.

The picked candidates are not evaluated by DFT directly: they are first **pre-relaxed
on the LCB surrogate surface** `E − κ·σ` (`get_acquisition_calculator()` →
`LowerConfidenceBoundCalculator`), then the survivors are evaluated by GPAW. Novelty
is a discrete min-distance with no well-defined force, so it cannot drive relaxation —
hence relaxation uses the LCB part only, with `κ = 2.0`.

### How it compares to regular LCB in GOFEE
- **Regular GOFEE LCB** (`LowerConfidenceBoundAcquisitor`): acquisition =
  `μ(x) − κ·σ(x)`, **minimized** — it trades off exploiting low predicted energy (μ)
  against exploring uncertain regions (σ).
- **Novelty-LCB here**: acquisition = `σ(x) + λ·Novelty(x)`, **maximized**, constrained
  to an energy window. Instead of minimizing energy, it seeks regions the surrogate is
  unsure about **and** that are structurally new, while staying within a chosen energy
  band. It is a diversity-focused variant, not an energy-minimizer.
- **Shared piece:** both relax candidates on the same LCB surface `E − κ·σ`, and both
  use the same GPR/Fingerprint stack.

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
