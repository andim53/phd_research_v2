# Nested Sampling over the combined multi-seed Fe/MgO AGOX dataset — reusable run guide

**Created:** 2026-08-20  **Last updated:** 2026-08-21
**Agent:** Calyx
**Run dir:** `/home/think/Desktop/research/_run/8_nested_sampling/`
**Env:** `agox_v2` conda (AGOX 3.10.2 + ASE 3.25.0), Python 3.11

> **Read me first (new agent):** §2 env, §9 pitfalls, §13 Ray fix, §15 literature
> parameters, §16 reference map. The rest is the full procedure + results.

---

## 1. Purpose of this file

This captures everything needed to redo, extend, or adapt the multi-seed nested
sampling run. Use it as a self-contained reference the next time you ask for a related
task (different temperature, live points, iterations, perturbation, or a different
dataset/system built the same way). It complements `nested_sampling_process.md` (the
earlier single-seed, seed-3-only work on the `_analysist/.../5x5` DB) — this document
is the **multi-seed combined-dataset** variant.

---

## 2. Environment (invariant)

- Python: `/home/think/miniconda3/envs/agox_v2/bin/python` (base `python3` has NO AGOX/ASE)
- Skills to load first: `agox` (package API), `agox-run-code` (run-script conventions).
- For headless plots: `matplotlib.use('Agg')` before any plotting import.
- GPR uses Ray internally (auto-starts a local Ray instance); set `use_ray=False` to
  disable (it just runs hyperparameter optimization on 1 process).

---

## 3. The dataset (this run)

- Location: `dataset/seed_*/1_db/db_*.db`
- Seeds used: **3 through 15** → 13 databases
- Total structures: **1297**
- Composition: **Mg25O25Fe25** (75 atoms), uniform across EVERY seed (verified)
- Energy range: **-436.909 eV .. -386.292 eV**
- `dataset/stop_16/` and `dataset/trash/` also exist but are excluded (glob only
  matches `seed_*/1_db/db_*.db`).

### Critical pre-check (do this before any combined training)
Confirm all structures share one composition/atom count so a single Fingerprint
descriptor + single GPR are valid. If compositions differ, you must split by
composition or use a local descriptor (SparseGPR). Quick check:

```python
from collections import Counter
counts = Counter(); n_atoms = set()
for a in all_structures:
    counts[tuple(a.get_chemical_symbols())] += 1
    n_atoms.add(len(a))
print(len(counts), n_atoms)   # expect 1 distinct composition, 1 atom count
```

---

## 4. AGOX / GPR API facts (verified against the installed package)

- `Database(filename=...)` → `restore_to_memory()` → `restore_to_trajectory()` returns
  a list of ASE `Atoms`. Energies via `a.get_potential_energy()`.
- **`GPR.train(training_data)` takes a bare list of `Atoms`.** The `database=` kwarg
  passed to `GPR.__init__` is NOT used by `train` or `predict_energy` — so combining
  several DBs is clean: just concatenate trajectories and train on the combined list.
- `GPR(descriptor, kernel, prior=Repulsive())`; `predict_energy(atoms)` returns a float.
- Descriptor: `Fingerprint.from_atoms(traj[0])` is the correct constructor pattern
  (the `Fingerprint(environment=Environment(...))` form can fail to parse symbols).
- GPR signature: `GPR(descriptor, kernel, prior=None, single_atom_energies=None,
  n_optimize=None, optimizer_maxiter=100, centralize=True, filter=EnergyFilter(),
  use_ray=True, **kwargs)`.
- `train(training_data: List[Atoms])`; `predict_energy(atoms)`.

---

## 5. GPR kernel recipe (invariant, from `dataset/main.py`)

```python
from agox.models.GPR.kernels import RBF, Noise, Constant as C
from agox.models.GPR.priors import Repulsive

bk = 0.01
kernel = (C(5000, (1, 1e5)) *
          (C(bk, (bk, bk)) * RBF() +
           C(1 - bk, (1 - bk, 1 - bk)) * RBF())
          + Noise(0.01, (0.01, 0.01)))
gpr = GPR(descriptor=descriptor, kernel=kernel, prior=Repulsive())
gpr.train(all_structures)
```

---

## 6. What "feature dim 720" means (Fingerprint descriptor)

`Fingerprint.create_features(atoms).shape[1]` returns **720** for any Fe/MgO structure.
Breakdown (verified against the descriptor internals):

- Species = 3 (Fe, Mg, O).
- **2-body / radial part = 180**: 6 distinct pair ("bond") types (3 same-species
  Fe–Fe, Mg–Mg, O–O + 3 cross Fe–Mg, Fe–O, Mg–O) × 30 radial bins
  (`Nbins1 = ceil(rc1/binwidth) = ceil(6/0.2) = 30`). 6 × 30 = 180.
- **3-body / angular part = 540**: 18 distinct triple types × 30 angular bins
  (`Nbins2 = 30`, from `binwidth2 = π/Nbins2`). 18 × 30 = 540.
- Total = 180 + 540 = **720**.

It is a fixed dimension for this system, so GPR treats each structure as a point in a
720-D feature space and measures similarity via the kernel. Default Fingerprint
params: `rc1=6, rc2=4, binwidth=0.2, Nbins=30, use_angular=True`.

---

## 7. The run script

**File:** `/home/think/Desktop/research/_run/8_nested_sampling/run_nested_sampling.py`

Flow:
1. Load combined dataset (glob `seed_*/1_db/db_*.db`, concatenate structures +
   energies).
2. Train one GPR on all 1297 structures.
3. Run `NestedSampler` from the local `nested_sampling` package:
   - `beta = 1/(K_B·T)`, log-likelihood `log L = -beta·(E - E_ref)` (E_ref = min training E)
   - prior = empirical DB distribution + optional position perturbation (`perturb`)
   - evidence accumulated in log space
4. `sampler.save(output)` writes CSVs + **ALL** posterior XSF structures (not just the
   top 20) + `posterior_summary.csv` (rank, energy_eV, weight, log_weight).
5. (Automatic) state-density / landscape analysis of the results — see §12.

### CLI options
```
--temp 300          temperature K (default 300) -> beta = 38.68 eV^-1 at 300 K
--n-live 50         live points (default 50)
--n-iters 300       iterations (default 300)
--perturb 0.01      prior perturbation amplitude Å (default 0.01; 0 = none)
--perturb-symbols Fe   elements perturbed during prior sampling (default Fe, the
                    deposition layer); ALL other atoms stay fixed
--output ./ns_output_allseeds   output dir
--rng 42            RNG seed
--analysis-dir <d>  analysis output dir (default <--output>/analysis)
--no-analysis       skip the automatic state-density analysis
--analyze-only <RUN_OUTPUT_DIR>  re-run analysis on a saved run (no GPR/training)
```

### Full run command (as executed)
```bash
cd /home/think/Desktop/research/_run/8_nested_sampling
/home/think/miniconda3/envs/agox_v2/bin/python run_nested_sampling.py \
    --temp 300 --n-live 50 --n-iters 300 --perturb 0.01 \
    --perturb-symbols Fe --output ./ns_output_allseeds --rng 42
```

---

## 8. Verified results (this run)

- GPR trained on 1297 structures in **~134 s**; validation deltas ≈ 0.02–0.10 eV.
- Final evidence: **Z = 4.168e-04** (log Z = **-7.783**).
- Posterior: 300/300 physical; **E_mean = -432.35 eV, E_std = 6.22, E_min = -436.83 eV**
  (training min E_ref = -436.91 eV).
- Live energies converged toward E_ref as iterations progressed.

Output files (in `--output`):
| File | Contents |
|---|---|
| `evidence_history.csv` | iteration, evidence Z (one row per iteration) — correct |
| `log_evidence.csv` | iteration, log Z — **malformed, see pitfall #1** |
| `final_live_energies.csv` | live-point energies at termination |
| `posterior_summary.csv` | rank, energy_eV, weight, log_weight — ALL posterior samples |
| `posterior_structures/posterior_*.xsf` | ALL posterior structures (rank-ordered, not just top-20) |
| `analysis/` | state-density / landscape outputs (see §12) |

---

## 9. Pitfalls & key learnings (read before adapting)

1. **`log_evidence.csv` from the imported package is malformed.** `NestedSampler.save()`
   in `nested_sampling/nested_sampler.py` writes it as two long transposed rows
   (all iterations on one line, all log_Z on the next) instead of one row per
   iteration. No data lost — `evidence_history.csv` is correct. To fix, change the
   `np.column_stack([[i, self.log_Z] for i in range(...)])` to `[[i, self.log_Z] for
   i in range(...)]` (drop the extra `np.column_stack`). This is a pre-existing bug in
   the package, NOT in `run_nested_sampling.py`.
2. **Verify composition uniformity before combined training** (see section 3).
3. **Prior/perturbation sensitivity.** The AGOX Fingerprint Cython descriptor is very
   sensitive to position changes; even 0.01 Å perturbation can cause GPR extrapolation
   to unphysical energies (~1e4+ eV). Keep `perturb` small (0.01 Å) or 0; the code
   filters out live points with |E| > 1e4 eV.
4. **Log-space is mandatory.** Energies ~ −400 eV and beta ~ 40 eV⁻¹ → exp(beta·E) is
   `inf`. Always accumulate evidence in log space with an E_ref shift.
5. **In-place modification must use `.copy()`.** Creating new `Atoms` objects (or
   clipping via `np.clip`) breaks the Cython fingerprint; modify a copy of an existing
   DB structure in place.
6. **GPR training takes ~2 min on 1297 structures** — factor this into runtime. A
   quick smoke test (n-live 30, n-iters 20) validates the pipeline before the full run.
7. **Run in background** for the full job (foreground timeout caps at 600 s).
8. **AGOX seed**: `AGOX.run(N_iterations)` is the method (no `run_optimization`). Not
   used in this NS script (no AGOX optimizer run), but relevant for AGOX run scripts.

---

## 10. Artifacts produced in this session

| Path | Description |
|---|---|
| `run_nested_sampling.py` | Multi-seed NS run script (loads all seeds, trains GPR, runs sampler) |
| `README.md` | Short usage/readme for the run script |
| `NESTED_SAMPLING_RUN.md` | Step-by-step log of what was done + results |
| `ns_output_allseeds/` | Full-run outputs (evidence_history.csv, final_live_energies.csv, posterior_structures/) |
| `nested_sampling/` | The imported NS package (NestedSampler, gpr_training, utils, __main__ CLI) |

### Note on the imported package's CLI (`nested_sampling/__main__.py`)
It has its own single-seed CLI (`--db-dir`, `--seed`, `--db-file`, ...) but points at a
different default DB path and only loads ONE seed. The `run_nested_sampling.py` script
is the multi-seed path.

---

## 11. Quick verification snippet (GPR timing + descriptor dim)

```bash
/home/think/miniconda3/envs/agox_v2/bin/python -c "
import glob, numpy as np, time
from agox.databases import Database
from agox.models.descriptors.fingerprint import Fingerprint
from agox.models.GPR import GPR
from agox.models.GPR.kernels import RBF, Noise, Constant as C
from agox.models.GPR.priors import Repulsive
structs=[]; en=[]
for f in sorted(glob.glob('dataset/seed_*/1_db/db_*.db')):
    db=Database(filename=f); db.restore_to_memory(); tr=db.restore_to_trajectory()
    structs+=tr; en+=[a.get_potential_energy() for a in tr]
en=np.asarray(en); print('n=',len(structs))
d=Fingerprint.from_atoms(structs[0]); print('feat dim', d.create_features(structs[0]).shape[1])
bk=0.01; k=C(5000,(1,1e5))*(C(bk,(bk,bk))*RBF()+C(1-bk,(1-bk,1-bk))*RBF())+Noise(0.01,(0.01,0.01))
g=GPR(descriptor=d,kernel=k,prior=Repulsive(),use_ray=False); t=time.time(); g.train(structs)
print('TRAIN %.1fs pred0=%.3f true=%.3f'%(time.time()-t, g.predict_energy(structs[0]), en[0]))
"
```

---

## 12. State-density / landscape analysis of results (added later in this session)

### Files
- `nested_sampling/state_density.py` (new) — `analyze_state_density`,
  `analyze_saved_output`, `load_saved_run` (+ helpers).
  Models the Stage-2/Stage-3 logic from
  `_run/9_novelFilter/run_analysis_thresholds.py`.
- `nested_sampling/nested_sampler.py` — `save()` now writes ALL posterior XSFs +
  `posterior_summary.csv` (rank, energy_eV, weight, log_weight), not just top-20.
- `nested_sampling/__init__.py` — exports `analyze_state_density`,
  `analyze_saved_output`, `load_saved_run`.
- `run_nested_sampling.py` — runs analysis automatically after sampling + new
  `--analyze-only` / `--analysis-dir` / `--no-analysis` flags.

### What it produces (per set, GPR-predicted energies, physical |E|<1e4 only)
- **Landscape** `conf_space.png` — PCA top-eigenvector scatter + KDE state-density
  panel.
- **Boltzmann probability** `binding_probability_vs_temperature.png` — at 298.15,
  348.60, 447.875, 547.15, 646.425 K.
- **Comparison** `comparison_state_density.png` — overlaid training-vs-posterior KDE.
Sets analysed: `training/` (the 1297 DB structures) and `posterior/` (sampler's
`posterior_samples`). Outputs → `<--output>/analysis/`.

### Standalone re-analysis (no GPR / no re-training)
```bash
/home/think/miniconda3/envs/agox_v2/bin/python run_nested_sampling.py \
    --analyze-only ./ns_output_allseeds --output ./analysis_out
```
Requires the run dir to contain `posterior_structures/` + `posterior_summary.csv`
(both written by the CURRENT `save()`).

### New CLI options
- `--analysis-dir <dir>` — analysis output dir (default `<--output>/analysis`)
- `--no-analysis` — skip the automatic analysis after sampling
- `--analyze-only <RUN_OUTPUT_DIR>` — standalone re-analysis of a saved run

### Pitfalls specific to the analysis
- **Degenerate KDE guard**: if a set has <2 distinct energy values (all one energy),
  `gaussian_kde` is singular; the code detects this (`_is_degenerate`) and skips the
  panel rather than crashing.
- **`gaussian_kde`/Fingerprint need a proper lattice**: before running landscape/PCA
  on any set, ensure structures have a valid unit cell (`ase` XSFs from real DB
  relaxations do; hand-built `Atoms` without `cell=` fail with "0 lattice vectors").
- **Fe-only perturbation** (this session): the prior now perturbs ONLY
  `--perturb-symbols Fe` atoms; substrate Mg/O stay fixed (see `nested_sampler.py`
  `sample_from_prior` + `perturb_indices`).
- **Memory**: the auto-analysis reuses the trained GPR (needs RAM). Under System
  memory pressure (e.g. a concurrent `relax_and_partition.py` job + Ray at 98% RAM),
  Ray's GPR pool can OOM — run heavy jobs when fewer processes are competing.

---

## 13. Ray `ActorUnavailableError` in GPR — ALWAYS set `use_ray=False`

**Symptom:** the run crashes at the very first `GPR(...)` construction (before any
sampling) with:

```
ray.exceptions.ActorUnavailableError: The actor ... is unavailable:
The actor is temporarily unavailable: IOError: The actor was restarted.
```
(or, at lower pressure, a `ray.exceptions.OutOfMemoryError`).

**Root cause:** `GPR(...)` defaults to `use_ray=True`, which makes AGOX call
`pool_add_module(self)` → `ray.get(futures)`, spawning **one Ray actor per CPU
(4 on this node)** to hold copies of the model for parallel hyperparameter
optimization. When the node's RAM is nearly exhausted (concurrent
`relax_and_partition.py` job + Obsidian + IDE/LSP servers + Hermes gateways push it
to ~95–100%), the OS/Ray kills an actor → `ActorUnavailableError`. Environmental,
**not** a code bug (the same script succeeded earlier under lower load).

**Fix (already applied in `run_nested_sampling.py` → `build_gpr`):**
```python
gpr = GPR(descriptor=descriptor, kernel=kernel, prior=Repulsive(),
          use_ray=False)
```
Verified in AGOX source (`agox/models/GPR/GPR.py` `__init__`): with `use_ray=False`
the `else` branch runs — **no `pool_add_module`**, no actors, and
`n_optimize = 1` (single-process hyperparameter optimisation). This removes the crash
class entirely. Trade-off: training runs on 1 core (~2 min → a few minutes), no
effect on the sampling math or the analysis.

**Lesson for any new agent:** NEVER introduce a `GPR(...)` (or clone/extend this
script) without `use_ray=False` on this machine, and never run heavy jobs while a
`relax_and_partition.py` process is still consuming ~25%+ RAM — check `free -h`
first.

---

## 14. Full, heavy supercomputer run (Fujitsu PJM batch, `job.sh`)

`job.sh` in the run dir is a Fujitsu PJM-style batch script (resource group
`a-pj24001864`, `vnode-core=64`, `--mpi proc=64`, `elapse=120:00:00`; submit
`pjsub job.sh`, check `pjstat`, kill `pjdel`).

> **CRITICAL env mismatch:** `job.sh` activates `conda activate gpaw_env`, but this
> script needs the `agox_v2` env. Change it to `conda activate agox_v2` before
> submitting.

### Literature-scale heavy command (full pipeline)
```bash
OMP_NUM_THREADS=1 python ./run_nested_sampling.py \
    --temp 300 --n-live 500 --n-iters 5000 \
    --perturb 0.01 --perturb-symbols Fe \
    --rng 42 --output ./ns_output_allseeds_heavy
```
- `--n-live 500` and `--n-iters 5000` are literature-informed scales (see §15).
- `OMP_NUM_THREADS=1` caps each process to one OpenMP/BLAS thread. Prevent a single
  job grabbing all 64 cores and oversubscribing when several independent jobs run
  per node. After `use_ray=False` this has no bearing on Ray; it's harmless and
  recommended on a shared 64-core node. No accuracy/statistics effect.
- Because the sampler is single-process (`use_ray=False`), **scale out by submitting
  many independent jobs** (one per T and/or per seed → PJM array) rather than MPI.

### Suggested heavy T-scan (each a separate `pjsub` job)
```bash
for T in 100 200 300 500 1000; do
  OMP_NUM_THREADS=1 python ./run_nested_sampling.py \
      --temp $T --n-live 500 --n-iters 5000 --perturb 0.01 \
      --perturb-symbols Fe --output ./ns_T${T} --rng 42
done
```
Each gives its own evidence Z → free energy F = −k_B·T ln Z, so the T-dependence of
the partition function is read directly across T. 120 h comfortably covers the heavy
config; a full Yang-scale job (K=2000, ~5×10^5 iters, the strict surface analogue)
approaches the budget.

---

## 15. Parameters in the nested-sampling literature (why the heavy settings)

Sources (matching BibTeX keys in the wiki synthesis):
- `\cite{Partay2021}` — Pártay, Csányi & Bernstein, "Nested sampling for materials",
  Eur. Phys. J. B 94, 159 (2021) — bulk review.
- `\cite{Yang2024}` — Yang, Pártay & Wexler, "Surface phase diagrams from nested
  sampling", PCCP 26, 13862 (2024) — pymatnest surfaces, directly analogous to
  Fe-on-MgO deposition.
- `\cite{Chatbipho2025}` — Chatbipho et al., "Adsorbate phase transitions on
  nanoclusters from nested sampling", J. Chem. Phys. 163, 174701 (2025).

### The parameters and why

NS is governed by **live-set size K** and **walk length L**; iteration count follows
from them and the target minimum temperature. The evidence-resolution error in
ln Γ_i (phase-space volume) is **∝ 1/√K**, so **K is the primary accuracy knob**:
too-small K → systematic discretization + noise in the volume estimate, plus the hard
**basin-extinction** floor (basins can fluctuate to zero samples once the energy
limit cuts them off).

| Parameter | Meaning | Pártay 2021 (bulk) | Yang 2024 (surfaces) | This heavy run |
|---|---|---|---|---|
| **K** (live points) | phase-space-volume resolution | 500–5000 | 80 per free particle | **500** (`--n-live`) |
| **L** (walk length) | MC decorrelation steps for a cloned config | 100s–1000s | ~250 iters/walker | *(none — see gap)* |
| **N** (atoms) | system size | 32–256 | 4×4 cell, ≤16 free particles | 75 (Fe25Mg25O25) |
| **iterations** | set by min temperature | 10^5–10^7 | 80×250×16 = 320 000 | **5000** (`--n-iters`) |
| **temperature β** | **absent from sampling** (post-process only) | absent | absent | **in likelihood** (`--temp`) — major difference |

Key points:
- **K and L trade off:** the minimum sufficient L *decreases* as K increases (clones
  only need to diffuse to a *neighbouring* config). Not independent.
- **Iterations are not free:** fixed by the minimum temperature you must resolve;
  scales ~linearly with K. Yang uses *250 iterations per walker*.
- **β is not a sampling parameter** in the papers — the PES is sampled once, top-down,
  and β is applied only in post-processing to get Z(β), ⟨A⟩(β), heat capacity at any T
  from one sample set. This is the core advantage enabling coverage–temperature
  diagrams.

### Mapping to this script (and two gaps)
- `--n-live` ↔ K; `--n-iters` ↔ iterations (we set it explicitly, papers derive it);
  `--temp` ↔ β.
- **Gap 1 — no walk length L.** Our prior is DB-resample + Fe-only `--perturb`, not
  clone-then-MC-decorrelate. Each constrained draw is an independent DB sample.
- **Gap 2 — β inside the likelihood.** We do fixed-temperature sampling (evidence is
  T-dependent), whereas the papers leave β out and reweight in post-processing.

Implication: `--n-live` is the most direct accuracy lever. For parity with the
literature, prefer K ≈ 500–2000 (not 50/200) with iterations scaled ~linearly. The
open prior gap is the subject of the wiki page ★[[nested-sampling-validation]]★, which
proposes NS as the rigorous bias-corrected cross-check of the GOFEE/LCB Fe/MgO
partition function in the rejected manuscript (LT19702J). Adopting a real clone-and-MC
decorrelation move (L) and moving β to post-processing would bring this script in
line with Partay/Yang.

---

## 16. Reference / context map for a new agent

- **Run code + docs:** `/home/think/Desktop/research/_run/8_nested_sampling/`
  (`run_nested_sampling.py`, `job.sh`, `README.md`, `NESTED_SAMPLING_RUN.md`,
  `nested_sampling/` package).
- **This reusable guide:** `/home/think/Desktop/research/_md/for-agent/
  nested_sampling_multiseed_guide.md` (you are here).
- **Single-seed earlier log:** `/home/think/Desktop/research/_md/
  nested_sampling_process.md` (seed-3-only, `_analysist/.../5x5`).
- **Wiki (research wiki, FUSE/mega-sync mount):** `/home/think/MEGA/Obsidian-Notes/
  wiki/wiki-research/`. Orient via `SCHEMA.md` + `index.md` + `log.md`. Key pages:
  ★[[nested-sampling]]★, ★[[nested-sampling_synthesis]]★,
  ★[[nested-sampling-validation]]★. Papers live in `raw/papers/nested-sampling/`.
  **Readable only via `find -exec cat`** on this mount (standard tools fail).
- **Analysis reference:** `/home/think/Desktop/research/_run/9_novelFilter/
  run_analysis_thresholds.py` (the model for `state_density.py`). Shared plotting
  helper: `/home/think/Desktop/research/_analysist/scripts/
  plot_structure_landscape.py`.
- **Skill:** `simulation-analysis` (AGOX analysis pipeline), `agox`,
  `agox-run-code`, `llm-wiki`.
- **Run-state caveat:** `ns_output_allseeds/` in the run dir was produced by the run
  BEFORE the current `save()` change, so it may lack `posterior_summary.csv` /
  full posterior XSFs. Re-run to get analysis-compatible output, or use
  `--analyze-only` only on runs written by the current code.
