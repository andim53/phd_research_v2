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