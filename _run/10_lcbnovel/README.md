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

### How the KMeansSampler is used
The KMeansSampler sits **between the collector and the acquisitor**: it thins the
pool of *already-evaluated* (relaxed + DFT-scored) structures down to a small,
diverse representative set before the acquisitor scores them.

In `main.py`:

    sampler = KMeansSampler(descriptor=descriptor, database=database, sample_size=SAMPLE_SIZE)   # SAMPLE_SIZE = 20

**What it actually does** (AGOX `samplers/kmeans.py`):
1. Takes the **finished structures** in the database (the ones that have been
   relaxed and DFT-evaluated — NOT the raw generator candidates).
2. Computes each structure's fingerprint features (the same 720-dim descriptor).
3. Clusters them with sklearn `KMeans` in that feature space.
4. **Keeps the lowest-energy member of each cluster** (`select_from_clusters`).

**Is there an energy criterion?** Yes. Two, in fact:
- A `max_energy=5` eV filter (`KMeansEnergyFilter`) drops any structure more than
  5 eV above the current lowest-energy structure *before* clustering.

### Assessment for local-minimum sampling
This subsection addresses the goal of **local-minimum sampling** (enumerating and
weighting the distinct metastable basins of Fe-on-MgO, rather than only chasing the
global minimum) and asks whether the current Novelty-LCB pipeline serves it.

**What "5 eV above the lowest-energy structure" actually does — and its DB effect.**
The `KMeansEnergyFilter(max_energy=5)` does **not** delete anything from the database.
The Database stores every evaluated candidate regardless of energy. The filter only
governs which structures are *eligible to be sampled* (fed onward to the acquisitor as
the next candidate pool): any structure more than 5 eV above the running lowest-energy
structure is excluded from clustering and therefore cannot be picked as the next
search point. Its practical effect is to keep the active search focused on the
low-energy part of the landscape, and (combined with `select_from_clusters`) to make
each picked basin representative the lowest-energy member of its cluster.

**Does Novelty-LCB fit local-minimum sampling?** Partly — and the part that helps is
the **novelty term**. Because `Novelty(x)` is the min distance to everything already
seen, maximising it actively pushes the search into structurally distinct regions,
which is exactly what discovers *different* local minima (basins) rather than
re-optimising one. So as a basin-diversity mechanism it is genuinely better than
plain LCB.

**What is right.**
- Novelty rewards structural diversity → multiple basins can be found.
- The KMeansSampler keeps one representative per cluster, so a single basin full of
  near-duplicate relaxations does not monopolise the sample.
- The downstream tools already exist for the actual local-minimum/partition-function
  step: `_run/9_novelFilter` (greedy dedup → a distinct-basin set + Boltzmann
  weights) and `_run/8_nested_sampling` (GPR surrogate + nested sampling for the
  partition function / evidence over that set). The AGOX search's real job is to
  *populate the DB with diverse structures*; the local-minimum statistics are then
  computed post-hoc by those tools.

**What is wrong / limited (the mismatch).**
1. **It is a global-search heuristic, not a local-minimum sampler.** Novelty-LCB
   maximises `σ + λ·Novelty` inside an energy window. There is an inherent tension:
   novelty (and σ) push toward *unexplored, often high-energy* regions, while the
   energy window tries to hold the search in a low band. The acquisitor does not
   explicitly enumerate basins or balance weight across them; it just picks the
   most-uncertain-and-novel in-window candidate each round.
2. **Energy window must be calibrated to a real energy.** The window is defined on
   absolute predicted energy `E` (the code tests `E < lo or E > hi` against
   `target_energy ± ΔE`), so `target_energy` must be a real energy in the band, not 0.
   This is now done from the previous LCB-only dataset (below).

**How to set `target_energy` (from the LCB-only dataset in `./dataset`).**
The Novelty-LCB window is compared against the **absolute predicted energy** `E` of a
candidate. Reading the 13-seed LCB-only run (`dataset/seed_*/1_db/db_*.db`,
1297 structures, Mg25O25Fe25) gives the energy band:

    E_min = −436.91 eV   E_max = −386.29 eV
    band centre ≈ −411.6 eV
    p1 ≈ −436.8, p25 ≈ −432.0, p50 ≈ −428.9, p75 ≈ −418.1, p95 ≈ −398.3, p99 ≈ −391.6

For this work (broad, low-selectivity window so most of the searched landscape is
eligible), set `target_energy` to the **band centre** and `delta_E` to a wide
half-width:

    target_energy = −411.6 eV,  delta_E = 25 eV   ->  window ≈ [−436.6, −386.6]

This covers essentially the full p1..p99 range, so the energy-window constraint is
non-restrictive and the search is governed by the novelty + uncertainty terms. To
target only the stable (low-energy) local minima instead, narrow the window to the
low band (e.g. target ≈ −432, ΔE ≈ 3). These values are written into `main.py`.

3. **Novelty saturates as the DB grows.** Novelty is the min distance to **all** DB
   structures. Early on it is large; as the DB fills, the nearest neighbour shrinks,
   so the novelty bonus decays and the search drifts back toward pure uncertainty
   sampling. The measure is also computed in raw 720-dim space without
   normalisation (matching `_run/9_novelFilter`), so distances are dominated by the
   largest-magnitude descriptor components.
4. **The DB itself is not a clean minima set.** Every DFT evaluation is stored, and
   relaxations repeatedly land in the same basins → the DB accumulates near-duplicates.
   A raw DB is therefore a poor input to local-minimum statistics unless it is first
   deduplicated (which is exactly what `_run/9_novelFilter` does).
5. **Novelty vs a representative set.** Because novelty compares against *every*
   stored structure, a near-duplicate of a known basin can still look "novel enough"
   if it is slightly perturbed. Comparing against a **deduplicated representative set**
   (one per basin) would make novelty reflect distance to distinct minima.

**What can be improved.**
- **Energy window now calibrated** to the LCB-only band (`target = −411.6 eV,
  ΔE = 25 eV`, broad low-selectivity). For a stricter local-minimum focus, narrow to
  the low band (e.g. target ≈ −432, ΔE ≈ 3).
- **Compare novelty against a deduplicated set** (e.g. the `_run/9_novelFilter` output)
  instead of the raw DB, so the bonus measures distance to distinct minima.
- **Use the search to build diversity, then post-process for local-minimum
  statistics**: run AGOX to fill the DB, dedup with `_run/9_novelFilter` to get the
  distinct-basin set, then run `_run/8_nested_sampling` for the partition
  function / free energy / DOS. This cleanly separates "discover basins" (AGOX) from
  "weight basins" (NS / novel filter) — the intended division of labour across this
  project's sibling runs.
- Optionally add explicit basin bookkeeping at acquisition time (store only distinct
  relaxed minima, or track cluster representatives) to keep the DB lean for the
  downstream statistical step.

- Within each cluster, the **lowest-energy** structure is the one selected as the
  cluster's representative.

**How many clusters?** It is **automatic** — you do not choose the cluster count.
It is derived from how many structures exist and your `sample_size`:

    n_clusters = 1 + min(sample_size - 1, floor(len(energies) / 5))

so it is capped at `sample_size` (20 here) and grows only as the database grows.
The result is a sample of at most `sample_size` structures — one representative per
structural basin — which is then handed to the Novelty-LCB acquisitor. This prevents
a basin full of near-duplicate structures from dominating the novelty/uncertainty
scoring. (Note: the acquisitor's energy-window filter is separate from the sampler's
`max_energy`; they are independent mechanisms.)

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
| Energy window | `target=−411.6 eV, ΔE=25 eV` (broad) | Calibrated from the LCB-only dataset in `./dataset` (band centre ≈ −411.6, p1..p99 ≈ [−436.8, −391.6]) |
| Compute | HPC PJM batch, 64-core GPAW (`gpaw_env`) | SubprocessGPAW LCAO/dzp needs a cluster node; run `pjsub j_novel.sh`, seed set by editing `SEED=` in the script |
| Logging | curated `LOG.md` + raw `transcript.log` | Human-readable milestones plus a faithful tool-call record |

## Status

- [x] `novelty_lcb` package + scripts copied and compiling under `agox_v2`
- [x] `main.py` faithfully re-wired (same physics as run 7)
- [x] Serialization smoke test **PASSES** (crash root cause verified fixed)
- [ ] Heavy Fe/MgO search launched on HPC (see `TUTORIAL.md` step 4)
- [x] Energy-window calibrated from the LCB-only dataset in `./dataset` (target=−411.6, ΔE=25)

See `TUTORIAL.md` for the full reproduction and repair guide, `LOG.md` for what
has been done, and `README.AI.md` for the agent-facing spec.
