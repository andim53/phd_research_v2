# Wang-Landau density of states on an AGOX GPR surrogate

Project: `/home/think/Desktop/research/_run/c_landausampling/`
Status: created under the AI-Agent Project Workflow. Companion files:
`README.AI.md` (machine spec), `TUTORIAL.md` (reproduction), `LOG.md`
(action log), `AGENTS.md` (governing rules).

## What it does

This project applies the **Wang–Landau flat-histogram method** to estimate the
**density of states g(E)** of a structure pool, using an AGOX **GPR surrogate**
as the energy model. It is the sibling of `_run/b_nestedsampling`, which solved
the same "flat structure ↔ island structure" problem with **nested sampling**;
here the algorithm is Wang–Landau (WL) instead.

1. Loads **every** structure from **every** seed database of the chosen dataset
   (`dataset/` = Fe/MgO 1297 structures; `dataset_boron3/` = B3-doped;
   `dataset_boron/` = B7-doped).
2. Trains a **single AGOX GPR surrogate** on the combined structures (AGOX
   kernel recipe).
3. Runs the `WangLandauSampler` from the `wang_landau/` package: a Monte-Carlo
   walk that rattles the deposition-species atoms (small/large Gaussian steps)
   and accumulates a flat visitation histogram over energy bins, refining the
   log density of states `ln g(E)` by the standard `f → √f` scheme and then the
   **1/t algorithm** (Belardinelli & Pereyra 2007).
4. From the normalised `g(E)` derives the **partition function Z**, free energy
   `F = −k_B T ln Z`, and heat capacity `C_V(T)` at chosen temperatures.

The central output is the **density of states `g(E)`** and the thermodynamics
that follow from it.

## Algorithm & the Fortran reference

The algorithm is a faithful Python port of
`_tmp/main_wanglandau_1d.f` (kept as the reference skeleton). In that toy,
a walker moves on a 1D coordinate `x` over the asymmetric double well
`E(x) = A(x²−1)² + B·x`, and the density of states is accumulated over energy
bins between the island (global minimum) and just past the barrier top. The
Python code generalises that: the "coordinate" is the full atomic structure, the
"move" is a rattle of the mobile atoms, and the "energy" is the GPR prediction,
binned as **relative energy per atom**, `(E − E_min)/N`, over `[e_min, e_max]`
(default `[0, 0.40]` eV/atom — island at 0, past the flat/barrier region).

Both use the same Wang–Landau core:
- acceptance `ln(r) < ln g(cur) − ln g(trial)` against the density,
- every visit adds `ln f` to `ln g` and `+1` to the histogram `H`,
- when `H` is flat (`min H > criterion·mean H`) the refinement `ln f` is halved,
- after `n_stages_standard` halvings the run switches to the 1/t algorithm
  (`ln f = 1/t′`) to avoid the error-saturation of the plain scheme.

## Environment

Use the `agox_v2` conda env (AGOX 3.10.2 + ASE 3.25.0):
```
/home/think/miniconda3/envs/agox_v2/bin/python
```
The HPC batch script `j_wanglandau.sh` activates `gpaw_env` (standing
convention) — but the sampling script needs the AGOX/ASE stack from `agox_v2`;
if `gpaw_env` lacks it, switch to `conda activate agox_v2` before submitting.

## Usage

All commands use `PY=/home/think/miniconda3/envs/agox_v2/bin/python` and are run
from the project root.

### Full run (default dataset, Fe/MgO)
```bash
$PY main.py --dataset dataset --n-bins 40 --e-max 0.40 \
    --mc-steps 20000000 --small-step 0.05 --large-step 0.40 \
    --perturb-symbols Fe --temperatures 100,200,300,500,1000 \
    --output ./wl_output_dataset --rng 42
```

### Choose a different dataset (B-doped)
```bash
$PY main.py --dataset dataset_boron3 --n-bins 40 --e-max 0.40 \
    --mc-steps 20000000 --output ./wl_output_boron3 --rng 42
$PY main.py --dataset dataset_boron   --n-bins 40 --e-max 0.40 \
    --mc-steps 20000000 --output ./wl_output_boron  --rng 42
```

### Enable the swap (permutation) move (≥2 mobile species)
The boron-doped datasets have two mobile species (B + Fe), so permutation moves
can exchange their positions. Enable swaps with `--swap-prob`; each swap move
performs a random `1..--max-swaps` position exchanges between two different
mobile species and rattles them by `--swap-rattle`:
```bash
$PY main.py --dataset dataset_boron3 --n-bins 40 --e-max 0.40 \
    --mc-steps 20000000 --perturb-symbols Fe,B \
    --swap-prob 0.2 --max-swaps 2 --swap-rattle 0.05 \
    --output ./wl_output_boron3_swap --rng 42
```
For the plain Fe/MgO `dataset` (single mobile species Fe), `--swap-prob` is
ignored with a warning and the walk falls back to rattling only.

### Cheap local smoke test (no DFT / no real GPR)
Validates the whole `WangLandauSampler` code path on a **fake 1-atom GPR**
reproducing the Fortran double-well potential — no heavy training needed:
```bash
$PY smoke_test_wang_landau.py
```

## Job (HPC)

`j_wanglandau.sh` runs Wang–Landau on HPC (PJM, 24 cores, `gpaw_env`), reading
the existing `dataset/seed_*/1_db/db_*.db`. Submit with `pjsub j_wanglandau.sh`.

## CLI reference

| Flag | Default | Meaning |
|---|---|---|
| `--dataset` | `dataset` | Dataset dir: `dataset` (Fe/MgO) \| `dataset_boron3` (B3) \| `dataset_boron` (B7). |
| `--n-bins` | `40` | Number of energy bins for `g(E)`. |
| `--e-min` | `0.0` | Lower bin edge (eV/atom relative to the minimum). |
| `--e-max` | `0.40` | Upper bin edge (eV/atom rel; island at 0, set past the barrier/flat region). |
| `--small-step` | `0.05` | Small Gaussian displacement scale (Å), local refinement. |
| `--large-step` | `0.20` | Large Gaussian displacement scale (Å), barrier crossing. Default reduced from 0.40 (v1.3.0) so a single rattle cannot escape the ground-state basin into GPR-extrapolation territory. |
| `--e-reject` | `5×e_max` | Relative energy (eV/atom) above which a trial is treated as an unphysical GPR extrapolation and REJECTED (revisits the current bin) instead of being capped into the top bin. Set ≤ e_max to disable. |
| `--relax-steps` | `0` | Basin-hopping mode: if > 0, each proposed trial is relaxed to a local minimum of the GPR potential with this many BFGS steps (fixing non-mobile atoms) before binning. Default 0 (off). |
| `--perturb-symbols` | `Fe` | Atom symbol(s) to rattle; all others stay fixed. |
| `--flatness-criterion` | `0.80` | Flatness threshold (`min H > criterion·mean H`). |
| `--check-interval` | `5000` | Flatness check interval (MC steps). |
| `--n-stages-standard` | `14` | Standard-scheme halvings before switching to the 1/t algorithm. |
| `--swap-prob` | `0.0` | Probability of choosing a swap (permutation) move instead of a rattle on each MC step. Requires ≥2 mobile species; disabled (no-op) otherwise. |
| `--max-swaps` | `1` | Max swaps per swap move; each swap move performs a random `1..max` swaps (mirrors the reference GlobalPermutationGenerator). |
| `--swap-rattle` | `0.05` | Gaussian displacement (Å) applied to the two swapped atoms after a swap. |
| `--mc-steps` | `2000000` | Number of Wang–Landau MC steps. |
| `--temperatures` | `100,200,300,500,1000` | Temperatures (K) for thermodynamics post-processing. |
| `--start-from-top` | off | Initialize the walker at the top of the bin range (flat-structure analogue); default off = start from the global minimum (bottom-up). |
| `--output` | `./wl_output` | Output directory. |
| `--rng` | `42` | RNG seed (reproducibility). |
| `--use-ray` | off | Enable Ray in GPR training (default single-process). |
| `--n-walkers` | `1` | **Mode A parallel WL** (v1.5.0): N concurrent Wang–Landau walkers sharing one histogram `H`/`ln_g` via Ray actors; seeds are `--rng+i` and flatness/refinement act on the combined histogram, so the joint walk reaches flatness faster. `N=1` = current serial behaviour (single walker, no Ray). |

## Outputs (written to `--output`)

- `g_of_E.csv` — bin-center relative energy (eV/atom), `ln g`, histogram count.
- `g_of_E.png` — plot of `ln g(E)` vs relative energy per atom.
- `thermodynamics.csv` — `T_K, beta_eV-1, logZ, Z, F_eV` (from normalised g(E)).
- `heat_capacity.csv` — `T_K, C_V_eV_per_K` (needs ≥3 temperatures).

## Key decisions & tradeoffs

| Decision | Choice | Tradeoff |
|---|---|---|
| Energy model | AGOX GPR surrogate (not DFT-in-loop) | Fast enough for a long WL walk; energy errors from the surrogate (validated ~0.004 eV/atom MAE). |
| Sampling move | Rattle mobile atoms (small/large); optional swap (permutation) move via `--swap-prob`; extrapolation guard rejects trials > `--e-reject` (default 5×e_max) | Local refinement + barrier crossing; swaps let ≥2 mobile species exchange positions; extrapolating far can give unphysical GPR energies — guarded by `\|E\|<1e4` AND the rel-energy `--e-reject` rejection (prevents the delta-at-top-bin trap). |
| Binning | Relative energy per atom `(E−E_min)/N` | Dataset/composition comparable; the `g(E)` is per-atom, so absolute Z is normalised to unit integral (only the additive constant is arbitrary). |
| Refinement | standard `f→√f` then 1/t | 1/t avoids error saturation of the plain scheme (Belardinelli & Pereyra 2007). |
| Data | self-contained copy of all 3 datasets | Fully reproducible in isolation (~300M regenerable data, gitignored). |

## Concepts & physics

**Density of states `g(E)`.** The number of configurations per unit energy at
energy `E` — the fundamental quantity of statistical mechanics from which
everything else follows. Wang–Landau estimates `ln g(E)` directly by making the
walk spend equal (flat) time in every energy bin.

**Wang–Landau acceptance.** A trial configuration is accepted with probability
`min(1, g(current)/g(trial))`. In log form this is
`accept if ln(r) < ln g(cur) − ln g(trial)`. This biases the walk toward
low-density (rare) energies, flattening the histogram — hence "flat histogram"
sampling. Each visit to a bin accumulates `ln f` into `ln g` and `+1` into `H`;
`ln f` starts at 1 (=`ln e`) and is halved whenever `H` becomes flat, refining
the estimate.

**Partition function `Z`.** `Z(β) = Σ_b g_b · exp(−β E_b) · ΔE` (bins b over
absolute energy). Since Wang–Landau gives `g(E)` only up to a multiplicative
constant, we normalise `g(E)` to unit integral; relative quantities and `C_V`
are unaffected by the constant. `F = −k_B T ln Z`.

**Heat capacity `C_V`.** `C_V = k_B β² · d²(ln Z)/dβ²`, computed by finite
differences. A peak in `C_V(T)` is the standard signature of a phase transition
(here the flat↔island transition), computed from the second derivative of
`ln Z`.

**Swap (permutation) move.** For systems with ≥2 mobile species (e.g. the
B-doped datasets, B + Fe), a swap move exchanges the positions of two atoms of
*different* species within the mobile set, then rattles them a little. It is
chosen on each MC step with probability `--swap-prob` instead of the usual
rattle, letting the walk explore the chemical (species-arrangement) degrees of
freedom as well as the geometric ones. The number of swaps per swap move is a
random integer in `1..--max-swaps`, mirroring the reference
`GlobalPermutationGenerator`. For a single mobile species the swap is a no-op
(the walk keeps rattling).

**Basin-hopping / GPR relax (`--relax-steps`).** With `--relax-steps N > 0`, each
proposed trial is first relaxed to a local minimum of the **GPR potential** (N
BFGS steps using the surrogate as the energy/force calculator, only the mobile
atoms free) and *then* binned. The binned energy is the nearest basin
(inherent-structure) energy rather than the raw rattled energy. The MC rattle
becomes only the basin-proposal move; relaxation does the descent. This makes
large rattles (barrier hopping) safe, but the resulting `g(E)` is the density of
*minimized* energies, not configurations — recover the canonical partition
function by re-adding the vibrational (within-basin) contribution. Default off.

## Layout

```
c_landausampling/
├── main.py                    # entry point (root runner)
├── wang_landau/               # package: WangLandauSampler, GPR loader/trainer, thermodynamics, utils
├── scripts/                   # (analysis helpers as needed)
├── dataset/                   # Fe/MgO AGOX seed DBs (seed_3..15) + main.py + scripts
├── dataset_boron3/            # B3-doped AGOX seed DBs
├── dataset_boron/             # B7-doped AGOX seed DBs
├── j_wanglandau.sh            # PJM batch script (HPC)
├── smoke_test_wang_landau.py  # cheap local validation (fake double-well GPR)
├── README.md / README.AI.md / LOG.md / TUTORIAL.md / VERSIONS.md / AGENTS.md / PROMPTS.md
├── _runs/                     # self-contained HPC run dirs (scaffolded)
├── _analysist/                # per-run analysed results (scaffolded)
├── _archives/                 # archived artifacts
└── _tmp/                      # scratch output (holds main_wanglandau_1d.f reference)
```

See `README.AI.md` for the machine-readable spec and `TUTORIAL.md` for
step-by-step reproduction.

# QnA

When you bottom-up or sampling from the ground state, what exactly do you mean?

**Short answer: this project is *already* bottom-up (ground-state) sampling by default —
and, unlike nested sampling, Wang–Landau has no top-down/bottom-up *estimator* to flip.
"Bottom-up" here refers only to where the walker *starts*, not to how `g(E)` is built.**

### Why there is no "up-down vs down-up" in Wang–Landau (the key difference from `b_nestedsampling`)

In the sibling nested-sampling project, "up-down vs down-up" is a real, deep choice about
the **estimator**: NS discards the worst (highest-E) live point each iteration and
accumulates the evidence with the shrinking prior-volume weight `X_i = exp(−i/K)`. That
quadrature is directional — it is only valid for a sequence of *shrinking* sub-level sets
descending from the top, which is exactly why inverting it to "throw the lowest E and weight
from the bottom" breaks the volume identity (see `b_nestedsampling` QnA #4).

Wang–Landau has **no such directional estimator**. It is a flat-histogram random walk whose
whole purpose is to visit *every* energy bin equally often, regardless of where it started:

- **Symmetric acceptance.** A trial is accepted when `ln(r) < ln_g[cur] − ln_g[trial]`
  (`wang_landau_sampler.py:320`). This depends only on the current running estimate of
  `ln g` in the two bins — never on whether the trial is above or below the current energy.
  The walk moves *up and down* freely; the bias is toward *low-density* bins, not toward
  low (or high) energy.
- **Direction-free accumulation.** Every accepted move does `ln_g[b] += ln_f; H[b] += 1`
  (`_visit`, `:228`). `g(E)` is assembled bin-by-bin from visitation, not by peeling shells
  off the top or growing them from the bottom. There is no `X_i`, no shell weight, no
  ordering of samples — so there is nothing to "reverse."
- **Result is the whole `g(E)` at once.** Because the histogram is driven flat across the
  full `[e_min, e_max]` window, a converged WL run returns the density of states over the
  *entire* window in one shot. It does not "drain from the top" or "grow from the bottom";
  it fills the whole range simultaneously.

This is precisely why Wang–Landau was chosen as the algorithm-sibling: it *is* the
"map `g(E)` outward from the known ground state" method that the bottom-up nested-sampling
idea was reaching for — but done with a correct, direction-agnostic estimator instead of an
inverted-NS quadrature.

### The one place "bottom-up" does enter: the initial walker (`initialize`)

The only directional choice in this project is **where the walk begins**, set by
`WangLandauSampler.initialize(start_from_top=...)` (`:262`). It has no effect on the final
`g(E)` for a well-converged run (WL forgets its start), but it controls how quickly and
safely the walk enters the tracked window:

- **`start_from_top=False` (the DEFAULT) = bottom-up / ground-state start.** It picks the
  lowest-energy DB structure — the island global minimum, `idx = argmin(db_energies)`,
  rel E ≈ 0 (`:289`) — and lets the walk *ascend* from there. This is the robust default,
  and it is exactly "sampling from the ground state": we already have the ground-state
  structure in the DB, so we seed the walk there and let it climb.
- **`start_from_top=True` = top-down start.** It picks the highest-rel-energy DB structure
  that is *strictly inside* `[e_min, e_max)` (`:276–287`), the "flat structure" analogue of
  the Fortran toy, and lets the walk descend. Out-of-window structures are rejected so the
  walker never starts above `e_max` (where it would be capped into the top bin and could get
  trapped — the bug this default was chosen to avoid).

### How the flags map to this (as wired in `main.py`)

- `--start-from-min` (`main.py:111`) — **explicitly** request the ground-state (bottom-up)
  start. This is already the default; the flag exists only to state the intent loudly.
- `--start-from-top` (`main.py:105`, default off) — request the top-of-window start instead.
- Resolution: `start_from_top = args.start_from_top and not args.start_from_min`
  (`main.py:163`) — so `--start-from-min` always wins, and with **no flags at all you already
  get bottom-up** from the global minimum.

The "CLI reference" table above lists `--start-from-top` default as **off** — matching the
actual `main.py` default (bottom-up). (Fixed in v1.3.0; earlier this note flagged a stale
"on".)

### So do you need to change anything to be "bottom-up"?

No. Running `main.py` with no start flag (or with `--start-from-min`) already samples from
the ground state upward. If you want the mapped energy *window itself* to grow from the
bottom over the course of a run (a genuinely different, one-directional estimator rather than
the symmetric flat-histogram walk), that would be a **new** sampler — not a flag on this one —
and is out of scope for this documentation pass.

New Question:

In Landau Sampling, we only care that during our sampling, we reach the minimum energy (Monte Carlo is just a means of randomizing), but essentially, using the regular rattling makes it difficult and we only end up in the high energy state. With that in mind, what about using Monte Carlo Step + GPR relax? After we rattle, we perform GPR relaxation which can be embedded from the agox library (like in /home/think/Desktop/research/_run/c_landausampling/_analysist/c1_mgofe_N40_Emax04/dataset/main.py for reference. With 100 Step GPR relax.) This way, we will never have to worry regarding reaching the minimum energy, and we can even incoorporate higher rattling. What do you think?

### What your proposal is

Relaxing each trial to a local minimum *before* binning it is a real, established approach known as **basin-hopping / inherent-structure Wang–Landau sampling** (Wales & Doye; Stillinger–Weber inherent structure). Instead of binning the raw GPR energy at the rattled position, you bin the energy of the nearest basin minimum that relaxation reaches. The rattle then becomes only the proposal step, and relaxation does the descent. In this codebase, "the GPR relax" maps to `ParallelRelaxPostprocess(model=..., optimizer_run_kwargs={"steps": 100})` in the reference `dataset/main.py` (lines 149-154): ~100 ASE optimizer steps using the GPR as the calculator (energy + forces from the Fingerprint GPR). The same machinery already exists in AGOX, so no new library is required.

Below is a neutral assessment — it is a legitimate idea, and it also has real downsides. Neither the pros nor the cons are decisive on their own; the right choice depends on what you want `g(E)` to mean and what compute you can afford.

### Pros

1. **Attacks the trapping failure directly.** A relaxed trial descends to a low-energy structure, so it cannot remain stuck in the high-energy extrapolation region that produced the c1/c2 top-bin delta. This is a more fundamental cure than the v1.3.0 `--e-reject` guard, which only rejects pathological trials after the fact.
2. **Decouples move scale from acceptance.** Because relaxation removes the "large rattle ⇒ high extrapolated energy ⇒ trap" link, you can use genuinely large rattles to hop across the flat↔island barrier without the walk dying at the top. This can improve ergodicity.
3. **Gives a physically meaningful, lower-noise quantity.** Minimized energies are the basin (inherent-structure) energies; relaxation also averages away some of the surrogate's per-position noise (~0.004 eV/atom MAE), giving more stable bins.
4. **Reduces the number of MC steps needed.** Relaxation does the heavy basin-finding, so a basin-hopping walk typically converges with ~10⁵–10⁶ steps rather than 10⁷. Fewer, costlier steps can sometimes be net-cheaper in wall time than many cheap ones.

### Cons

1. **It changes what `g(E)` means.** You compute the density of *minimized* (basin) energies, not the density of *configurations*. That is a different object from the current sampler's `g(E)`. To recover the true canonical partition function you must re-add the **vibrational (within-basin) contribution**; a minima-only `g(E)` is the configurational (inherent-structure) approximation. Low-T thermodynamics will miss intra-minimum entropy unless you add that correction.
2. **~100× more GPR evaluations per MC step.** Every trial now does ~100 relaxation calls instead of 1. From this project's timing, a real-GPR prediction is ~0.04 s on the 720-dim descriptor (≈190 s per 5000 steps); ×100 makes a 20M-step run effectively infeasible. You must cut `--mc-steps` by orders of magnitude, and you should *measure* the actual wall-time cost first — the step-count saving is not guaranteed to outweigh the per-step cost.
3. **Relax-on-surrogate inherits surrogate bias.** The "minimum" you reach is a minimum of the GPR potential, not of the true DFT surface. Wherever the surrogate misplaces a basin (worst where training data is sparse, i.e. higher-energy bins), relaxation anchors you to the wrong basin energy and the WL weights inherit that systematic bias — worse than the per-position noise of no-relax sampling.
4. **Partial-relaxation bias.** If ~100 steps does not converge on a rough surrogate surface, the energy depends on the step count: under-relaxed structures are shifted, systematically biasing the basin energies. You would need a relaxation-convergence check.
5. **Basin binning can be sparse / ambiguous.** Different rattles relax into the same minimum (intended), but the histogram is now over a *discrete* set of minima, which can be sparse at low energy. Flatness (the WL convergence criterion) is harder to satisfy over few discrete minima, and `n_bins_visited` becomes a measure of minima, not configurations.
6. **It may be unnecessary if the plain walk is fixed.** The trapping that motivates this is also addressable by the v1.3.0 changes (smaller `--large-step` + `--e-reject` guard). Plain WL on a correctly-bounded walker can reach the minimum; the relax mode is one possible cure, not the only one, and adds complexity and cost on top.

### Neutral bottom line

Your reasoning ("MC is just randomization; reaching the minimum is what matters") is coherent, and MC + GPR-relax is a well-precedented basin-hopping approach that would almost certainly fix the observed trapping. However, it is a **different estimator** (basin/inherent-structure `g(E)`, not configurational `g(E)`), it is ~100× more expensive per step, and it moves surrogate error from "noisy per position" to "systematic per basin." Whether it is the right move depends on (a) whether you want configurational or canonical thermodynamics, (b) whether you can afford/cut the MC budget enough, and (c) whether the v1.3.0 plain-walk fixes already suffice on re-testing.

If you want me to, I can scope it as an **optional** `--relax-steps N` mode (default off) with a short real-GPR cost measurement and a local smoke test, so you can compare the two estimators empirically before committing — without removing the existing no-relax path. But that is a follow-up task, not something done here.

New Question: 

I still don't understand how Wang–Landau sampling works. Can you provide a simple workflow or flowchart for it? A few specific things are unclear:

1. **How do we sample the data?** Do we take structures from the database (`db_*.db`) as in the `b_nestedsampling` project? If so, do we pick them randomly?

2. **If random, do we face the same duplication problem?** If we can revisit the same structure, does that mean we have the same duplication issue as in `b_nestedsampling`, and should we add a novelty filter there too?

3. **How does the minimization / convergence criterion work?** How does Wang–Landau decide convergence — what is the minimization criterion connected to the flatness check?

4. **How is the `--e-max` bin edge handled?** In the code, are structures whose energy is above the chosen 0.4 eV filter included as 0.4 eV (capped into the top bin), or are they excluded? 

### Answer

Below is a code-grounded walkthrough. The short version: Wang–Landau here does **not** sample from the database the way nested sampling does — the DB is only the *training set* for the GPR and the *starting point* of the walk. All real "sampling" happens as a Markov chain that proposes brand-new structures by rattling the current one. That removes the whole class of duplication problems that motivated the novelty filter in `b_nestedsampling`.

### 0. A simple workflow

```
1. LOAD      load_all_seeds(): read EVERY structure from EVERY seed DB in the dataset
             -> structures[], energies[]          (gpr_training.py:20)
2. TRAIN     build_gpr(): fit ONE GPR surrogate on all of them (energy model)
3. INIT      initialize(): pick the walker = the global-minimum structure
             (lowest E in the DB) by default; start_from_top picks the
             highest in-window structure instead         (wang_landau_sampler.py:316)
4. LOOP (n MC steps):
     a. PROPOSE   rattle the mobile atoms by a Gaussian step (small/large, 50/50)
                  -> a brand-new structure              (_propose, :182)
                  [optional --relax-steps: BFGS-relax trial on the GPR first]
     b. SCORE     GPR predicts E_trial; rel = (E_trial - E_ref)/N_atoms
     c. BIN       get_bin(rel): 0..n_bins-1; rel>e_max capped into top bin,
                  rel>e_reject REJECTED                (get_bin, :170; guard :371)
     d. ACCEPT    WL rule: ln(r) < ln_g[cur] - ln_g[trial]     (:384)
     e. VISIT     ln_g[bin] += ln_f ; H[bin] += 1               (_visit, :282)
     f. REFINE    every check_interval, if H flat: ln_f /= 2 (stage++);
                  after n_stages_standard halvings switch to 1/t  (_maybe_refine, :294)
5. OUT       g_of_E.csv / thermodynamics.csv / heat_capacity.csv
```

The key mentalvmodel: **the walker is a single moving structure, and each MC step manufactures a candidate out of the previous one** by a random atomic displacement. It never draws a structure from a pool.

---

### 1. How do we sample the data? From the DB, randomly, like `b_nestedsampling`?

**No.** This is the biggest difference from `b_nestedsampling`, and it is worth being explicit.

- `b_nestedsampling` **resamples from a discrete pool**: each iteration it has a fixed set of live points and draws new structures from the database / modifies them, which is why duplicate *identities* can creep in and why a novelty filter is meaningful there.
- This Wang–Landau code uses the DB **only twice, and never during the walk**:
  1. **Training** — `load_all_seeds()` reads *every* structure from *every* seed DB and feeds them to `build_gpr()` to train the surrogate (`gpr_training.py:20,46`). Nothing is randomly sub-sampled; it is the whole dataset.
  2. **Initialisation** — `initialize()` (`wang_landau_sampler.py:316`) picks the *single* starting structure: by default the global minimum (`argmin` of the DB energies, `:343`); with `--start-from-top` the highest in-window structure. This choice is deterministic, not random.
- After that, the walk generates its own structures. Each step, `_propose()` (`:182`) copies the current walker and adds Gaussian noise to the mobile (perturb) atom positions — a continuous displacement, so the trial is essentially always a **new, previously-unseen structure**. The GPR then scores it. There is no `random.choice(db)` anywhere in the sampling loop.

So "do we take it from the DB like `b_nestedsampling`?" — only for training and the seed. The sampling itself is a random walk in structure space, proposed by rattling, evaluated by the surrogate.

---

### 2. Do we have the same duplication problem, and should we add a novelty filter?

**No, and no** — for a structural reason, not a practical one.

- The novelty filter in `b_nestedsampling` exists because that workflow **re-visits a discrete set of stored structures**, so the same *identity* can be counted repeatedly and bias the statistics unless duplicates are rejected.
- Here the walk lives in a **continuous** configuration space: every proposed trial is the current structure plus Gaussian noise, so no two trials are bit-identical (the displacement is drawn from a continuous distribution). There is no finite pool of discrete identities to collide on.
- What the sampler *does* revisit is **energy bins**, not structures: `_visit()` adds `+1` to `H[bin]` every accepted move (`:282`). A bin being visited many times is *exactly the intended behaviour* of a flat-histogram walk — Wang–Landau *wants* equal (repeated) visitation across bins to converge. That is histogram statistics, not structural duplication, so a novelty filter would be conceptually wrong here and would fight the algorithm.

There is no `novelty_filter` in this sampler, and there shouldn't be one.

---

### 3. What is the "minimization" / convergence criterion?

Careful: the word "minimization" does not belong to convergence here. **Convergence is decided by histogram *flatness*, not by reaching a minimum energy.** There is no energy-minimisation step in the WL loop (unless you turn on `--relax-steps`, which is a separate, optional move — see below).

The flatness check is the standard Wang–Landau criterion:

- Every accepted visit does `ln_g[bin] += ln_f; H[bin] += 1` (`_visit`, `:282`).
- Every `--check-interval` MC steps (default 5000), `_check_flatness()` (`:286`) asks: over the bins that have been visited, is `min(H) > flatness_criterion * mean(H)` (default criterion 0.80)? If yes, the histogram is "flat enough."
- On flatness, `_maybe_refine()` (`:294`) **halves the refinement factor** `ln_f` (`ln_f /= 2`), resets `H` to zero, and increments `stage`. This is the standard `f → √f` scheme: as `ln_f` shrinks, the `ln_g` estimate is refined with finer granularity.
- After `--n-stages-standard` (default 14) such halvings, it **switches to the 1/t algorithm** (Belardinelli & Pereyra 2007): `ln_f = 1/t′` where `t′` is the number of steps since the switch (`:312`). This keeps refining indefinitely without the error saturation of the plain scheme.

So "how does it decide it's converged" → it never declares a hard "done"; it keeps refining until `ln_f` becomes very small (i.e. the estimate stops changing much). The criterion connected to convergence is **flatness of the visitation histogram `H`**, and the refinement knob is `ln_f`.

The optional `--relax-steps N` mode is *not* part of convergence: it is a move transformation that BFGS-relaxes each proposed trial to a local basin minimum of the GPR before binning (`_relax`, `:257`). It changes what energy gets binned, but convergence is still judged by the flatness of `H`, exactly as above.

---

### 4. Are structures above 0.4 eV included as 0.4 eV (capped) or excluded?

**Both, depending on how far above — this is the v1.3.0 refinement.** The raw binning (Fortran behaviour) *caps* everything at/above `e_max` into the top bin; on top of that, a v1.3.0 extrapolation guard *rejects* truly pathological energies.

Concretely, with the defaults `e_max = 0.40`, `e_reject = 5 × e_max = 2.0` eV/atom:

| rel energy (eV/atom) | fate |
|---|---|
| `rel < e_min` (0.0) | **Rejected** — below floor (`get_bin` → -1, `:175–176`, then `bin_trial < 0` reject at `:376`) |
| `e_min ≤ rel ≤ e_max` (0.0–0.40) | Normal bin |
| `e_max < rel ≤ e_reject` (0.40–2.0) | **Capped into the top bin** — `get_bin` does `return min(b, n_bins-1)` (`:178`), so a trial at, say, 1.5 eV/atom is binned as the 0.40 eV top bin |
| `rel > e_reject` (> 2.0) | **Rejected** as an unphysical GPR extrapolation — the trial is not accepted; the walker revisits its current bin (`:371–374`) |

So, to answer your exact question: a structure whose energy is *moderately* above 0.4 eV/atom (up to the `e_reject` threshold, default 2.0) **is included as the top bin** (i.e. treated as ~0.4 eV). But a structure that is *wildly* above (a GPR extrapolation artefact) is **excluded/rejected**, not capped — this guard was added in v1.3.0 to stop such trials from piling up a spurious delta at the top bin and trapping the walk there.

The `--e-max` "filter" you mention is really the **edge of the bin window**, and the top bin is an absorbing cap for energies inside `[e_max, e_reject)`. If you want *nothing* above `e_max` to be counted, set `--e-reject` ≤ `--e-max` (this disables the guard and reverts to pure capping — not recommended, as it reintroduces the top-bin trap).

New Question:

Does the current landau gpr relax is parallel? I remember agox ray can run a parallel, does it work for gpr relax?

### Answer

**No — the GPR relax in this project is strictly serial, and AGOX's Ray (`--use-ray`) does not parallelise it.** Ray only parallelises GPR *training*; the per-trial relaxation is a single-process BFGS descent. This is true both in the code and in the current `_runs` job scripts.

### Where the relax happens (and why it is serial)

The relax is `WangLandauSampler._relax()` (`wang_landau/wang_landau_sampler.py:257`). It attaches the GPR surrogate as the ASE calculator, fixes the non-mobile atoms, and runs `ase.optimize.BFGS(relaxed, ...).run(fmax=0.05, steps=self.relax_steps)` on **one** trial structure. It is called once per MC step, inside the walk loop:

```python
# run(), wang_landau_sampler.py:363-364
if self.relax_steps > 0:
    trial = self._relax(trial)   # one BFGS descent, one trial, serial
```

The Wang–Landau walk is a **single Markov chain**: each step's trial is generated from the previous accepted structure, so the relaxes cannot be batched or run in parallel — step *n* depends on step *n−1*. There is no multi-walker / population parallelisation in this sampler.

### What AGOX Ray actually parallelises (and what it does not)

`use_ray` is passed to `build_gpr(..., use_ray=args.use_ray)` (`main.py:148`), i.e. it is a **training-time** option. Inside AGOX's `GPR`:

- `use_ray=True` only changes `_train_model()` (`agox/models/GPR/GPR.py:559-572`): it calls `hyperparameter_search_parallel()` (parallelises the `n_optimize` hyperparameter restarts across Ray actors) and `pool_synchronize()` to broadcast the trained weights.
- **Prediction is not Ray-parallel.** `predict_energy()` (`GPR.py:144`) and `predict_forces()` (`GPR.py:188`) are single-structure, single-process calls — a plain `k.T @ alpha` / `-dk_dr.sum(0) @ alpha` matrix product. The BFGS relax calls these one structure at a time.

So even if you add `--use-ray`, the relax loop stays serial: Ray helps only the one-time GPR training, not the ~`relax_steps` force/energy evaluations per MC step.

### What the current `_runs` scripts actually do

The GPR-relax sweep jobs (`_runs/c1_mgofe_N40_Emax04/jc1_sweepGPR.sh`, `_runs/c2_boron3_N40_Emax04/jc2_sweepGPR.sh`) confirm this:

- They run `OMP_NUM_THREADS=1 python ./main.py ... --relax-steps 10/30/50/100 ...` — **no `--use-ray` flag** is passed.
- The four relax runs (`relax10/30/50/100`) are executed **sequentially** in the script, one after another.
- The job requests 64 cores (`#PJM -L vnode-core=64`, `--mpi proc=64`), but the actual Python process is a single serial process with `OMP_NUM_THREADS=1` — the 64 cores are allocated but **not** used to parallelise the relax.

### Bottom line

- Current GPR relax: **serial** (single BFGS per MC step, single process).
- `--use-ray`: **does not** parallelise the relax; it only parallelises GPR training's hyperparameter search.
- To actually parallelise the relax you would need a different architecture (e.g. multiple independent walkers / replicas, or relaxing a batch of trials in parallel) — that is not what the current sampler or the current `_runs` scripts do. 

New Question:

I want to make a parallelization. Discuss this on the README. What can be parallel, what can be fasten, and using what.

### Answer

Below is a code-grounded map of what can be parallelised in this project, what can only be sped up, and which tool to use for each. The short version: **the single Wang–Landau walk is inherently serial, but the workload around it — GPR training, and especially running many independent walks — parallelises cleanly.** The biggest win is not the relax itself but running many walkers at once.

### What is inherently serial (cannot be parallelised)

1. **A single Wang–Landau Markov chain.** Each MC step's trial is generated from the previous accepted structure (`run()`, `wang_landau_sampler.py:359-390`), so step *n* depends on step *n−1*. You cannot split one walk across cores.
2. **A single BFGS relaxation.** `_relax()` (`:257`) is a sequential descent on one trial; its force/energy calls are one-at-a-time. You cannot parallelise one descent.

These two are the reason the current code is serial — not a missing flag, but the algorithm's structure.

### What CAN be parallelised, and with what

**1. GPR training — use AGOX's built-in Ray (`--use-ray`).**
This is the one place AGOX natively parallelises. `use_ray=True` makes `_train_model()` call `hyperparameter_search_parallel()` (`agox/models/GPR/GPR.py:559-572`), which runs the `n_optimize` hyperparameter restarts across Ray actors via `pool_map`. Two caveats from the code:
- With `use_ray=False` (current default), `n_optimize` defaults to **1** (`GPR.py:108-109`) — a single restart, so there is nothing to parallelise anyway.
- With `use_ray=True` and `n_optimize=None`, AGOX sets `n_optimize = cpu_count` (`GPR.py:105-106`), i.e. it launches one hyperparameter restart per core. So to actually benefit you must pass `--use-ray` **and** let `n_optimize` scale (or set it explicitly in `build_gpr`).
- Tool: `python ./main.py --use-ray ...` (flag already wired in `main.py:148`). This speeds up the one-time training step only.

**2. Many independent Wang–Landau walks — the main lever (embarrassingly parallel).**
Because each walk is an independent Markov chain with its own RNG seed, you can run **N walkers in parallel** and combine their `g(E)` estimates (e.g. average `ln g` per bin, or run each to convergence and merge). This is the classic "parallel / replica Wang–Landau" strategy, and it is the cleanest speedup here:
- It directly attacks the wall-time bottleneck: the GPR-relax sweep is expensive per step, so running the 4 relax settings (or 4 seeds) **concurrently** instead of sequentially cuts wall time ~4×.
- Tool options:
  - **Simplest (no code change):** submit N separate `pjsub` jobs (one per seed / per `--relax-steps`), each on its own node. The project already does this pattern; the current `jc1_sweepGPR.sh` just runs them sequentially in one script — split them into N scripts and submit together.
  - **In-process:** use Ray actors or Python `multiprocessing` to run N `WangLandauSampler` instances concurrently, then merge `ln_g`. This needs a small driver script (not in the repo yet).
- Caveat: each walker needs its own RNG seed (`--rng`), and the merged `g(E)` is only meaningful if the walks are comparable (same bins, same `e_max`, same dataset).

**3. Batch force/energy prediction — only helps if you relax/score many trials at once.**
AGOX's `predict_forces`/`predict_energy` are single-structure serial (`GPR.py:144,188`), but the `candidate_list_comprehension` decorator (`agox/utils/decorators.py:6`) lets you pass a **list** of `Atoms` and get a list of results. If you restructure the sampler to relax/score a *batch* of trials (e.g. one per walker) in one call, you could push that batch through Ray `pool_map` (`agox/utils/ray/pool_user.py:72`) so each actor handles one trial. This is the only way to parallelise the *relax itself* — but it requires a batch-of-walkers architecture, not the current single-walker loop.

### What can be sped up (not parallelised)

- **GPR training wall-time** — via `--use-ray` (above). One-time cost, modest.
- **The GPR-relax sweep wall-time** — by running the 4 relax settings concurrently (point 2) rather than sequentially in one script. This is the biggest practical speedup and needs no code change.
- **Per-step cost of the relax** — could be reduced (not parallelised) by lowering `--relax-steps` or using a cheaper optimiser, but that changes the physics (see the earlier basin-hopping QnA).

### Recommended plan (lowest effort → highest impact)

| Goal | Tool | Effort | Impact |
|---|---|---|---|
| Speed up GPR training | `--use-ray` (Ray actors) | trivial (flag) | small, one-time |
| Cut sweep wall-time | N concurrent `pjsub` jobs (one per seed/relax setting) | trivial (split scripts) | **large (~N×)** |
| Parallelise the relax itself | batch-of-walkers + Ray `pool_map` | new driver + sampler refactor | large but requires new architecture |
| Parallelise one walk | — | impossible | — |

The pragmatic first step: **keep the sampler as-is, but run the independent walks concurrently** (separate jobs or a Ray/multiprocessing driver), and merge the `ln g` estimates. That gives most of the benefit with no change to the physics or the sampler core.

New Question:

Write regarding the Thing 2 in details in the readme. Write the how, and the pros and cons.

### Answer — Parallel / replica Wang–Landau (Thing 2) in detail

This is the strategy where **N walkers with the same settings but different RNG seeds are combined so the *combined* walk reaches flatness faster / with better statistics than any single walker.** It is distinct from the sweep-parallelism (Thing 1) above, which just runs N *different* experiments concurrently and never combines them. Here the walkers are *coupled* through shared statistics.

### The core idea, mapped to the code

Every Wang–Landau walker already maintains two shared-able quantities (`WangLandauSampler`):

- `ln_g[b]` — the running log density of states per bin, updated by `_visit()` as `ln_g[b] += ln_f` (`wang_landau_sampler.py:282`).
- `H[b]` — the visitation histogram, updated as `H[b] += 1` in the same `_visit()`.

Flatness is judged on `H` by `_check_flatness()` (`:286`): `min(H[visited]) > flatness_criterion * mean(H[visited])`. When flat, `_maybe_refine()` (`:294`) halves `ln_f`, resets `H` to zero, and (after `n_stages_standard` halvings) switches to the 1/t algorithm.

The key observation: **`H` and `ln_g` are just accumulators.** Nothing in the sampler requires them to belong to a single process. If N walkers all add their visits into the *same* `H` and `ln_g`, the flatness test sees the *combined* histogram — which fills all bins faster than any one walker could. That is the whole mechanism of parallel Wang–Landau.

### How — two combination modes

**Mode A: shared histogram (true parallel WL, live coupling).**
All N walkers update the **same** `H` and `ln_g` (e.g. via shared memory, a Ray actor holding the arrays, or a lock-protected global). Each walker runs its own `run()` loop (`:359-390`) with its own RNG seed, but every `_visit()` writes into the shared arrays. The flatness check and `ln_f` refinement are then performed on the *combined* histogram, so the walkers collectively drive the refinement schedule. This is the standard parallel-Wang-Landau scheme and gives the real "reach flatness faster" benefit.

- Implementation sketch: a driver creates N `WangLandauSampler` instances sharing one `ln_g`/`H` (e.g. a Ray actor or `multiprocessing.Manager`), runs them concurrently, and lets `_check_flatness`/`_maybe_refine` act on the shared state. This is **not** in the repo yet — it needs a small driver + a small refactor so the sampler can point at shared arrays.

**Mode B: independent walks + merge at the end (no live coupling).**
Run N fully independent `WangLandauSampler` instances (each with its own `ln_g`, `H`, seed), let each converge on its own, then **average the final `ln_g` per bin** across walkers. This is simpler (no shared state, no refactor — just N separate jobs + a merge script) but it does *not* accelerate the refinement schedule; it only reduces the variance of the final estimate by averaging.

| | Mode A (shared histogram) | Mode B (independent + average) |
|---|---|---|
| Coupling | live, shared `H`/`ln_g` | none until the end |
| Reaches flatness faster | **yes** (combined histogram) | no (each walker converges alone) |
| Reduces final variance | yes | yes (by averaging) |
| Code change | driver + sampler refactor (shared arrays) | driver + merge script only |
| Parallel speedup | ~N× wall-time for same quality | ~N× wall-time, but same per-walker convergence |

### Pros

1. **Reaches flatness faster (Mode A).** Because flatness is judged on the combined histogram, N walkers collectively visit all bins N× faster, so the refinement schedule (`ln_f` halvings) advances sooner. This is the main reason to use parallel WL.
2. **Better statistics / lower variance (both modes).** More total visits per bin → a smoother, more converged `ln_g`; averaging (Mode B) further reduces the noise of the final estimate.
3. **Directly uses idle cores.** The current `_runs` jobs request 64 cores but run one serial process; N walkers would actually use them.
4. **No change to the physics.** Each walker still does the same WL walk on the same GPR; only the bookkeeping is shared. The `g(E)` meaning is unchanged.
5. **Fault-tolerant / composable (Mode B).** Independent jobs can be submitted separately and merged later; a failed walker doesn't corrupt the others.

### Cons

1. **Shared-state complexity (Mode A).** `H` and `ln_g` must be updated atomically across processes; a race corrupts the histogram. Requires a lock/actor and a sampler refactor. The current sampler has no such support.
2. **The 1/t switch is global (Mode A).** `_maybe_refine()` switches all walkers to the 1/t algorithm at the same step (`:304-312`). If walkers are at different stages, forcing a single global schedule can be awkward; the shared refinement must be coordinated.
3. **Correlated walkers (Mode A).** If walkers share the same starting structure or the same GPR, their proposals are not fully independent, so the effective speedup is less than the ideal N×.
4. **Merging is only valid for comparable walks (Mode B).** Averaging `ln_g` across walkers is only meaningful if they share the same bins, `e_max`, dataset, and `--relax-steps`. Mixing settings (as in the sweep) would be wrong to average.
5. **Memory / GPR cost per walker.** Each walker holds its own copy of the GPR and its own current structure; N walkers multiply that memory. With a large surrogate this can be a real cost.
6. **No help for a single walk.** Neither mode makes one Markov chain faster; the benefit is purely across walkers.

### Bottom line

- **Mode A (shared histogram)** is the "true" parallel Wang–Landau and gives the real "reach flatness faster" benefit, but needs a driver + sampler refactor for shared `H`/`ln_g`.
- **Mode B (independent + average)** is the cheap, safe first step: run N separate walks (different `--rng`), merge the final `ln_g` per bin. It uses idle cores and reduces variance, but does not accelerate the refinement schedule.
- Either way, the physics and the `g(E)` meaning are unchanged — only the statistics are combined.
