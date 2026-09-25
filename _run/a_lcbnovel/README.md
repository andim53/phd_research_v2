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
2. **Energy window mode.** The window is defined on **absolute predicted energy** `E`
   (the code tests `E < lo or E > hi`). The default is now the **auto global-minimum
   mode**: the window is anchored to the live lowest DFT energy in the DB (`E_min`) and
   searches a set amount `X` above it (`(-inf, E_min + X]`), so **no manual
   calibration / prior regular-LCB run is needed**. A manual centered mode
   (`target_energy ± ΔE`) is also available for backward compatibility (see below).

**How the auto global-minimum window works (default).**
With `energy_above_min = X` (in `main.py`, `NOVELTY_ENERGY_ABOVE_MIN`) and
`per_atom=True` (default, `NOVELTY_ENERGY_PER_ATOM`), the window is computed in
**energy per atom**: the acquisitor divides the candidate's predicted energy `E` and
the live global minimum `E_min` by the atom count `N`, and accepts any candidate with
`E/N ≤ E_min/N + X` (X in eV/atom):

    window (per atom) = (-inf, E_min/N + X]      with X in eV/atom

- `E_min` updates as new, lower minima are found, so the window tracks the search.
- There is **no lower bound** — a candidate with `E < E_min` is still accepted, so a
  genuinely new global minimum can be discovered.
- **Per-atom values are size-independent**, so choosing X is easy (e.g. 0.5–2 eV/atom)
  and does not depend on how many atoms the system has. This requires a fixed
  composition / atom count (true for the 75-atom Fe/MgO dataset). Set
  `per_atom=False` (`NOVELTY_ENERGY_PER_ATOM=False`) to use **total eV** instead
  (e.g. 5–10 eV for this system). For a fixed N, per-atom and total modes are
  equivalent up to scaling by N.

**Manual centered mode (alternative, for reference).**
The old centered window `[target_energy − ΔE, target_energy + ΔE]` remains available
by setting `energy_above_min = None` and passing `target_energy`/`delta_E`. From the
LCB-only dataset (`./dataset`, band ≈ [−436.9, −386.3] eV, centre ≈ −411.6 eV), a
broad centered window would be `target_energy = −411.6 eV, delta_E = 25 eV`
→ `[−436.6, −386.6]`. This mode is not needed for the default run.

### What if `target_energy = 0`?
Setting `target_energy = 0` does **not** mean "search around an energy of 0". The
window `[target_energy − ΔE, target_energy + ΔE]` is compared against the GPR's
**absolute predicted total energy** `E` of a candidate (the code tests
`E < lo or E > hi`). For this system the predicted and DFT total energies are all
around **−400 eV** (band ≈ [−436.9, −386.3] eV, never near 0), because the total
energy of a 75-atom Fe/MgO slab is a large negative number.

With `target_energy = 0, ΔE = 1.0`, the window becomes `[−1, +1]` eV. Since no
candidate's predicted energy is anywhere near 0, **every candidate is excluded** — it
gets `+∞` in the sorting space and is never selected, so the search would effectively
pick nothing and stall. With a wider `ΔE` (e.g. 400) the window `[−400, 400]` would
start to overlap the band, but that is a roundabout way to reproduce a sensible
window and is easy to get wrong.

The 0-eV reference only makes sense if your energies are **relative** to some
reference (e.g. a per-atom formation energy or a shifted E_ref). This acquisitor
works on the **absolute** total energy, so `target_energy` must be set to a real
energy in the band — which is why this project calibrates it from the LCB-only
dataset (`target = −411.6 eV, ΔE = 25 eV`).

### Does AGOX continue from a previous database?
Yes — with the default settings, AGOX **continues from an existing DB rather than
starting empty**. `main.py` opens the database with
`Database(filename=db_path, order=5)`, which uses the defaults `initialize=False`
and `call_initialize=True`:

- `initialize=False` means an existing DB file is **not** deleted on open (the code
  only calls `os.remove(filename)` when `initialize=True`).
- `_initialize()` then checks whether the `structures` table already exists. If it
  does, it does **not** recreate it; it loads the stored rows into memory
  (`_init_storage()` → `storage_dict`), so the previously explored candidates are
  restored.
- The GPR and the Novelty-LCB acquisitor rebuild from those restored candidates —
  in particular, the novelty distance is computed against `get_all_candidates()`, so
  it continues to reflect everything seen so far.

**Implications for `main.py`:**
- **Resume / extend a run:** re-run the same seed and the search continues from the
  existing `db_<seed>.db`, accumulating more evaluations on top of the old ones.
- **Restart fresh:** you must **delete** the existing `db_<seed>.db` (or use a new
  output path) — otherwise the run silently continues from the previous DB instead
  of starting over. AGOX will not clear it for you by default.

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
- **Energy window is now auto global-min mode** (`energy_above_min=5 eV`), so no manual
  calibration is needed; tune `energy_above_min` to control how far above the ground
  state to search.
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

# 4. (Optional) EMT benchmark: regular LCB vs Novelty-LCB (auto global-min window),
#    Ni8/Au(4,4,2) fcc100. Run on a RAM-rich node / HPC (AGOX Ray pool).
/home/think/miniconda3/envs/agox_v2/bin/python main_benchmark.py    # local
pjsub j_benchmark.sh                                                 # on HPC

# 5. (Optional) Sweep benchmark: impact of kappa x novelty_weight on Novelty-LCB,
#    same Ni8/Au(4,4,2) system. Run on a RAM-rich node / HPC.
/home/think/miniconda3/envs/agox_v2/bin/python main_benchmark_sweep.py
pjsub j_benchmark_sweep.sh
```

> **Where heavy runs actually live.** The per-seed HPC runs and benchmarks are kept in
> **`1_runs/`** as self-contained directories (job script + main script + copies of
> `scripts/` and `novelty_lcb/`), named `<NN>_<descriptor>` (e.g.
> `a1_mgofe_Seed3_Iter300`, `a10_mgofeb_Seed3_Iter500`, `73_novel_benchEMT`). The
> root-level `j_*.sh` / `main*.py` are the parent project's own copies; to launch a
> concrete run, `cd` into the matching `1_runs/<NN>_<descriptor>/` and `pjsub` its
> `j_*.sh` there (edit `SEED=` / `N_ITERATIONS=` / `KAPPA=` / `NOVELTY_WEIGHT=` inside
> that script). Analysed results and the heavy multi-seed runs / benchmarks 71–74 live
> in **`2_analysist/`** — see the "Run directories" section below.

## Run directories: `1_runs/` and `2_analysist/`

Two sibling directories keep concrete runs separate from the project root.

**`1_runs/` — self-contained run directories.** Each HPC run or benchmark is its own
directory under `1_runs/`, holding everything that run needs (job script, main
script, copies of `scripts/` and `novelty_lcb/`) so it is launchable in isolation.
Naming follows `<NN>_<descriptor>`. The **per-seed Fe/MgO a-runs** (`a1`–`a10`) all
use seed 3 and the auto global-min energy window (`energy_above_min = 1.0` eV/atom,
`per_atom=True`); they differ only in the treatment in the table below.

| Run | N_ITERATIONS | KAPPA (κ) | NOVELTY_WEIGHT (λ) | What it varies |
|---|---|---|---|---|
| **a1** `a1_mgofe_Seed3_Iter300` | 300 | 2.0 | 1.5 | iteration budget (shortest; quick first check) |
| **a2** `a2_mgofe_Seed3_Iter500` | 500 | 2.0 | 1.5 | standard-length search |
| **a3** `a3_mgofe_Seed3_Iter700` | 700 | 2.0 | 1.5 | iteration budget (longest, deepest) |
| **a4** `a4_mgofe_Seed3_Iter500_k3` | 500 | 3.0 | 1.5 | kappa sweep |
| **a5** `a5_mgofe_Seed3_Iter500_k4` | 500 | 4.0 | 1.5 | kappa sweep + base for the λ sweep |
| **a6** `a6_mgofe_Seed3_Iter500_k5` | 500 | 5.0 | 1.5 | kappa sweep |
| **a7** `a7_mgofe_Seed3_Iter500_k4_nw2` | 500 | 4.0 | 2.0 | novelty_weight sweep (off a5) |
| **a8** `a8_mgofe_Seed3_Iter500_k4_nw3` | 500 | 4.0 | 3.0 | novelty_weight sweep |
| **a9** `a9_mgofe_Seed3_Iter500_k4_nw4` | 500 | 4.0 | 4.0 | novelty_weight sweep |
| **a10** `a10_mgofeb_Seed3_Iter500` | 500 | 2.0 | 1.5 | **B-doped** Fe (B7Fe25 mobile layer, 82 atoms); first doping run |

- **a1–a3** (integration budget sweep): identical except `N_ITERATIONS`.
- **a4–a6** (kappa sweep): same seed/budget/window, `KAPPA` = 3/4/5; κ sets the
  LCB surrogate-relaxation surface `E − κ·σ` (higher = more aggressive exploitation
  on the surrogate).
- **a7–a9** (novelty_weight sweep): built on `a5` (κ=4), `NOVELTY_WEIGHT` = 2/3/4;
  λ = weight on the novelty term in `a(x) = σ + λ·Novelty`.
- **a10** (B-doping): MgO substrate fixed, mobile layer **B7Fe25** (25 Fe + 6–7 B on
  hollow sites) via `add_adsorbate_to_hollows.py` v1.1.0; adds a Fe↔B permutation
  generator. First doping run, based on the `66_MgOFe_20B` example.

Each a-run ships a per-run `README.md` + `TUTORIAL.md` (its exact treatment + how to
reproduce it in isolation) plus `j_novEperAtom.sh` + `main.py` + `scripts/` +
`novelty_lcb/`. **Standalone benchmarks** are full projects with their own doc trio
(README/README.AI/LOG/TUTORIAL + AGENTS.md) inside their dir.

**`2_analysist/` — analysed results and the heavy-run project dirs.** Kept separate
from `1_runs/` so raw runs are never mixed with their analysis. It holds:

- **Heavy multi-seed Fe/MgO runs** (self-contained projects, not run via the a-runs):
  - **71** `71_novel_runEWindow/` — the older multi-seed run using the **manual
    calibrated window** (`target ≈ −411.6 eV, ΔE = 25 eV`), 13 seeds.
  - **72** `72_novel_AutoGlob_1eVperAtomAboveGlob/` — the multi-seed run using the
    **auto global-minimum window** (1.0 eV/atom above live DB min), 13 seeds. Carries
    `novelty_analysis_results.json` and `pca_basin_analysis_results.json`.
- **Benchmarks:**
  - **73** `73_novel_benchEMT/` — extended EMT benchmark, regular LCB vs Novelty-LCB
    (Ni8/Au(4,4,2)), 10 seeds × iter 100–500 × λ 2–5 = 250 runs; results in
    `benchmark_results/` + `DISCUSSION.md`.
  - **74** `74_novel_benchSweep/` — kappa × novelty_weight sweep
    (κ ∈ {0.5,1,2,4} × λ ∈ {0,0.5,1,1.5,2}, 20 combos); results in
    `benchmark_results/sweep_kappa_lambda/` + `DISCUSSION.md`.
- **Per-run a-run analysis** — `a1_mgofe_Seed3_Iter300/` … `a10_mgofeb_Seed3_Iter500/`,
  each holding a `README.md`/`TUTORIAL.md` + an `analysis_a_runs/` output dir.
- Older/sibling-project result trees live here too (e.g. `19_kappa2_...`,
  `66_MgOFe_20B_...`) — treat them as pre-existing/staging, not this project's runs.

Two self-contained analysis runners live at `2_analysist/`:

- `run_analysis_indices.py` — the **multi-seed** runner (mirrors the sibling
  b_nestedsampling architecture). Loads all `seed_*/1_db/db_*.db` directly from a
  `--dataset` dir and runs the 3-stage pipeline (best-so-far progression → PCA
  landscape → Boltzmann probability). Used for the multi-seed heavy runs **71/72**
  (the flat benchmark dirs 73/74 are excluded — their layout doesn't fit the
  `seed_*/1_db` structure). CLI: `--dataset --outdir --e-max --normalize-density
  --start-iter`.
- `run_analysis_a_runs.py` — the **single-seed** runner for the per-seed a-runs
  (e.g. `a1_mgofe_Seed3_Iter300/output`). Same 3-stage pipeline but labels the
  progression by the actual seed number and writes `progression_seed_split_Seed3.png`.
  Same CLI.

Both import only the `2_analysist/scripts/` deps copied next to them
(`plot_structure_landscape.py`, plus `process_database.py` / `calculate_relative_energy.py`
where used), so they are callable in place:

```bash
cd /home/think/Desktop/research/_run/a_lcbnovel/2_analysist
# heavy runs 71/72
/home/think/miniconda3/envs/agox_v2/bin/python run_analysis_indices.py \
    --dataset 71_novel_runEWindow/dataset --outdir 71_novel_runEWindow/analysis_indices
/home/think/miniconda3/envs/agox_v2/bin/python run_analysis_indices.py \
    --dataset 72_novel_AutoGlob_1eVperAtomAboveGlob/dataset --outdir 72_novel_AutoGlob_1eVperAtomAboveGlob/analysis_indices
# single-seed a-run
/home/think/miniconda3/envs/agox_v2/bin/python run_analysis_a_runs.py \
    --dataset a1_mgofe_Seed3_Iter300/output --outdir a1_mgofe_Seed3_Iter300/analysis_a_runs
```

Both runners also support a **two-phase `--extract` / `--plot-from-json`** mode that
writes all raw plot data to a single self-describing `analysis_data.json` (DB-free
replot from JSON, bit-identical PNGs). Each a-run's JSON also records fingerprint
**novelty metrics** (distinct/duplicate counts + pairwise distance stats) per PROMPT #5.

Outputs go to a per-run `<run>/analysis_indices/` or `<run>/analysis_a_runs/` dir
(progression plot + window `.xsf`, `conf_space.png`,
`binding_probability_vs_temperature.png`), and each analysis dir should carry a
`DISCUSSION.md` that states the **exact running command + params** and discusses the
results (mirroring the b_nestedsampling convention). Analysis outputs are gitignored
(regenerable); the runners + `scripts/` are tracked.

**Source-code versioning.** Every in-scope source file (root `main*.py`,
`novelty_lcb/`, `scripts/`, test/smoke/energy_stats, `2_analysist/` runner+scripts)
carries a module-level `__version__ = "X.Y.Z"` (semver). `VERSIONS.md` is the
manifest of current versions. Any edit to a file bumps its patch version (minor for
API/behavior changes), updates `VERSIONS.md`, and is recorded in `LOG.md`. See
`README.AI.md` §2b.

## Key decisions & tradeoffs

| Decision | Choice | Why |
|---|---|---|
| Base project | `7_lcbnovel_mgofe` | Fe/MgO is the target physical system; run 7 is the most complete attempt |
| `novelty_lcb` package | copied from run 7 (reused, not rewritten) | It already contains the serialization fix; lowest risk |
| Serialization fix | module-level free funcs + `functools.partial` in `get_acquisition_calculator()` | Bound methods drag the sqlite-backed `Database` into the Ray-put graph; free funcs capture only scalar `kappa` |
| Energy window | auto global-min (`energy_above_min=1.0 eV/atom`, per_atom) | Anchors to the live DB minimum, searches above it in eV/atom — size-independent, no manual calibration / regular-LCB-first step needed |
| Benchmark | `main_benchmark.py` (Ni8/Au EMT) + `j_benchmark.sh` (HPC) | Compares regular LCB vs Novelty-LCB (auto global-min window) on a fast EMT surface; needs a RAM-rich node / HPC for the AGOX Ray pool |
| Sweep benchmark | `main_benchmark_sweep.py` + `j_benchmark_sweep.sh` (HPC) | Sweeps kappa x novelty_weight on Novelty-LCB to study their impact (20 combos, 1 seed each) |
| Compute | HPC PJM batch, 64-core GPAW (`gpaw_env`) | SubprocessGPAW LCAO/dzp needs a cluster node; run `pjsub j_novel.sh`, seed set by editing `SEED=` in the script |
| Run organization | `1_runs/<NN>_<descriptor>/` (self-contained) + `2_analysist/` (results) | Keep each HPC run/benchmark isolated from the project root and from its analysis; `1_runs` is git-tracked, `2_analysist` outputs are gitignored |
| Logging | curated `LOG.md` + raw `transcript.log` | Human-readable milestones plus a faithful tool-call record |

## Status

- [x] `novelty_lcb` package + scripts copied and compiling under `agox_v2`
- [x] `main.py` faithfully re-wired (same physics as run 7)
- [x] Serialization smoke test **PASSES** (crash root cause verified fixed)
- [x] Energy window = auto global-min mode (`energy_above_min=1.0 eV/atom`, per_atom), no manual calibration
- [x] Heavy Fe/MgO search launched + analysed on HPC: multi-seed runs **71** (manual
  window) and **72** (auto-glob window, 13 seeds each), and **a-runs a1–a9** computed
  and extracted to JSON (a1–a3 iteration sweep, a4–a6 kappa sweep, a7–a9 λ sweep).
- [x] **a10** B-doped run computed + analysed (first doping run; `analysis_data.json`
  not yet extracted — optional).
- [x] Benchmarks **73** (extended EMT, 250 runs) and **74** (κ×λ sweep, 20 combos)
  have results in `benchmark_results/` + `DISCUSSION.md`.
- [x] Embedded benchmarks (`main_benchmark.py`, `main_benchmark_sweep.py`) shipped
  for regular-LCB vs Novelty-LCB comparison on the Ni8/Au(4,4,2) EMT model.
- [x] Run dirs organized under `1_runs/` (per-seed a-runs a1–a10 + `73_novel_benchEMT`)
  and analysis/heavy-runs/benchmarks under `2_analysist/`.

See `TUTORIAL.md` for the full reproduction and repair guide, `LOG.md` for what
has been done, and `README.AI.md` for the agent-facing spec.
