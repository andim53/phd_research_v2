# Heavy supercomputer runs + literature parameter rationale

Captured 2026-08 (default-env background session) from the multi-seed Fe/MgO
nested-sampling work. Two things a future run may need: how to size a heavy run, and
where the numbers come from in the nested-sampling literature.

## Supercomputer batch (Fujitsu PJM) — `job.sh`

The run dir ships a `job.sh` that targets a Fujitsu PJM job manager:

```
#PJM -L rscgrp=a-pj24001864   # resource group
#PJM -L vnode-core=64          # cores per node
#PJM --mpi proc=64
#PJM -L elapse=120:00:00
source ~/.bashrc
conda activate gpaw_env        # <-- WRONG for this script
module load intel impi
python ./run_nested_sampling.py ...
```
Submit `pjsub job.sh`, watch `pjstat`, kill `pjdel`.
**Pitfall:** the shipped script activates `gpaw_env`, but this nested-sampling script
needs the `agox_v2` env (AGOX/ASE stack). Change `conda activate gpaw_env` →
`conda activate agox_v2` before submitting.

### Heavy, literature-scale full-pipeline command
```bash
OMP_NUM_THREADS=1 python ./run_nested_sampling.py \
    --temp 300 --n-live 500 --n-iters 5000 \
    --perturb 0.01 --perturb-symbols Fe \
    --rng 42 --output ./ns_output_allseeds_heavy
```
- `--n-live 500` / `--n-iters 5000` are literature-informed, not the 50/300 defaults.
- `OMP_NUM_THREADS=1` cap each process to one OpenMP/BLAS thread. On a shared
  64-core node running several jobs, this prevents one job grabbing all cores and
  oversubscribing. With `use_ray=False` it has no bearing on Ray — harmless, and it
  has no accuracy/statistics effect.
- Because the sampler is single-process after `use_ray=False`, **scale out by
  submitting many independent jobs** (one per T and/or per seed → PJM array) rather
  than one `mpiexec`. A T-scan:
  ```bash
  for T in 100 200 300 500 1000; do
    OMP_NUM_THREADS=1 python ./run_nested_sampling.py \
        --temp $T --n-live 500 --n-iters 5000 --perturb 0.01 \
        --perturb-symbols Fe --output ./ns_T${T} --rng 42
  done
  ```
  Each gives its own evidence Z → free energy F = -k_B·T ln Z, so the temperature
  dependence of the partition function is read directly across T.

## Literature parameters (why K/live set is the accuracy lever)

Sources (BibTeX keys per the wiki synthesis):
- `\cite{Partay2021}` — Pártay, Csányi & Bernstein, "Nested sampling for materials",
  Eur. Phys. J. B 94, 159 (2021), bulk review.
- `\cite{Yang2024}` — Yang, Pártay & Wexler, "Surface phase diagrams from nested
  sampling", PCCP 26, 13862 (2024), pymatnest surfaces (direct analogy to Fe-on-MgO).
- `\cite{Chatbipho2025}` — Chatbipho et al., "Adsorbate phase transitions on
  nanoclusters from nested sampling", J. Chem. Phys. 163, 174701 (2025).

NS is governed by **live-set size K** and **walk length L**; iteration count follows
from them and the target minimum temperature. The evidence-resolution error in
ln Γ_i (phase-space volume) is **∝ 1/√K**, so **K is the primary accuracy knob**:
too-small K → discretization + noise in the volume estimate, plus the hard
**basin-extinction** floor (isolated basins can fluctuate to zero samples once the
energy limit cuts them off, losing that basin forever).

| Parameter | Meaning | Pártay 2021 (bulk) | Yang 2024 (surfaces) | This heavy run |
|---|---|---|---|---|
| **K** (live pts) | phase-space-volume resolution | 500–5000 | 80 per free particle | 500 (`--n-live`) |
| **L** (walk len) | MC decorrelation steps for a clone | 100s–1000s | ~250 iters/walker | *none* (see gaps) |
| **N** (atoms) | system size | 32–256 | 4×4 cell, ≤16 free particles | 75 (Fe25Mg25O25) |
| **iterations** | set by min temperature | 10^5–10^7 | 80×250×16 = 320 000 | 5000 (`--n-iters`) |
| **temperature β** | absent from sampling (post-process only) | absent | absent | **in likelihood** (`--temp`) |

Key relationships:
- **K and L trade off:** the minimum sufficient L *decreases* as K increases (a clone
  only needs to diffuse to a *neighbouring* config, not explore the whole volume).
- **Iterations are not free:** they are set by the minimum temperature one must
  resolve, and scale ~linearly with K. Yang uses *250 iterations per walker*.
- **β is not a sampling parameter** in the papers — the PES is sampled once, top-down,
  and β is applied only in post-processing to get Z(β), ⟨A⟩(β), heat capacity at any
  temperature from one sample set. This enables coverage–temperature diagrams.

### Mapping to this script (two real gaps)
`--n-live` ↔ K; `--n-iters` ↔ iterations (we set explicitly, papers derive); `--temp`
↔ β. Two structural differences that matter if validating against the literature:
1. **No walk length L.** Our prior is DB-resample + Fe-only `--perturb`, not
   clone-then-MC-decorrelate. Each constrained draw is an independent DB sample.
2. **β inside the likelihood.** We do fixed-temperature sampling (evidence is
   T-dependent), whereas the papers leave β out and reweight in post-processing
   (single T-free posterior reused at any T).

The wiki page `concepts/nested-sampling-validation` in wiki-research proposes NS as
the rigorous bias-corrected cross-check of the GOFEE/LCB Fe/MgO partition function in
the rejected manuscript LT19702J. Adopting a real clone-and-MC decorrelation move (L)
and moving β to post-processing would bring this script in line with Pártay/Yang.