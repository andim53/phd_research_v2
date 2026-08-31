# DISCUSSION — c1/c2 Wang–Landau sweeps: both runs are degenerate, non-converged

Run: `_analysist/c1_mgofe_N40_Emax04/` (plain Fe/MgO) and
`_analysist/c2_boron3_N40_Emax04/` (B3-doped). Data read from the
`wl_output_*_sweep_*` CSV files and the job `.out` logs
(`jc1_sweep.sh.6654357.out`, `j_c2_*_sweep.sh.6649512.out`).

## Verdict

**Neither sweep produced a usable density of states.** Both runs collapsed to a
**single-bin delta `g(E)` at the top of the energy window** (`rel ≈ e_max`),
every thermodynamic output is degenerate (`Z = inf`, `F` constant across all
temperatures, `C_V ≈ 0`), and no run reached flatness or the 1/t switch. The
Wang–Landau walk was trapped in an unphysical high-energy region in both
systems, by **two different mechanisms** (detailed below). There is **no
physical content to interpret** from these outputs; they are diagnostics of the
sampler, not of the Fe/MgO or B3 system.

## The shared failure signature (grounded in the data)

For **every** sweep output in both runs, the state density is a spike at the top bin:

| run | mc-steps | bins with g>0 / total | where g>0 | `F` (all T) |
|---|---|---|---|---|
| c1 (Fe/MgO) | 30,000 | 3 / 100 | bin 2 (H=1), bin 4 (H=1), bin 99 (H=29,998) | −407.0593 eV (const) |
| c1 (Fe/MgO) | 60,000 | 3 / 100 | bin 2 (H=1), bin 4 (H=1), bin 99 (H=59,998) | −407.0593 eV (const) |
| c1 (Fe/MgO) | 100,000 | 3 / 100 | bin 2 (H=1), bin 4 (H=1), bin 99 (H=99,998) | −407.0593 eV (const) |
| c2 (B3) | 10,000 | 1 / 40 | bin 39 (rel 0.395) only; ln_g = 9.84e+03 | −424.6024 eV (const) |
| c2 (B3) | 30,000 | 1 / 40 | bin 39 only | −424.6024 eV (const) |
| c2 (B3) | 50,000 | 1 / 40 | bin 39 only | −424.6024 eV (const) |

(Note on c2's `H` column: it is **all zero** in the saved `g_of_E.csv` — only
`ln_g` accumulated, at bin 39 — so c2's visitation is inferred from `ln_g > 0`
and the F-degeneracy, not from `H`. c1's `H` column is populated, so its
99.99% top-bin share is directly measured.)

Convergence bookkeeping confirms the trap:

- **c1**: `stages reached = 0`, `ln_f` stuck at `1.0`, never entered the 1/t
  regime; `visited 3/100` at every 5,000-step progress line. The two
  non-top bins (rel 0.010, 0.018) have `H = 1` each — the walker visited the
  ground-state region exactly twice and never returned.
- **c2**: `stages reached = 2 / 6 / 10` climbing with mc-steps, but this is the
  **stuck-walk stage inflation** the project already flagged as misleading
  (`stages` advances trivially when the walk is confined to one bin and the
  histogram is trivially "flat"); `visited` never exceeds 1/40.

Because `g(E)` is a delta, `Z = Σ_b g_b·exp(−βE_b)·ΔE` is dominated by that one
bin, so `F = −k_BT ln Z` is a **constant** across all T — the classic silent
artifact of a delta `g(E)` (the warning flagged in `agox-wang-landau`
pitfall 2 / `smoke-test-validation.md`). A constant `F` and `C_V ≈ 0` in any
output means the g(E) is delta-like, i.e. the walk never explored the basin
structure.

## Root cause — two distinct mechanisms

### c1 (Fe/MgO): correct init, then escape-and-trap during the walk

- Init is **correct**: the v1.2.0 `start-from-min` fix works —
  `init: rel E = 0.0011 eV/atom (bin 0)`, i.e. the walk starts at the global
  minimum (bottom-up), exactly as intended.
- **Mechanism:** the `--large-step 0.40 Å` rattle on all 25 mobile Fe atoms is a
  huge perturbation. In Wang–Landau's early all-`ln_g = 0` phase the walk
  accepts almost everything, so it freely diffuses away from the minimum until a
  large rattle lands in the GPR's extrapolation territory near `e_max`. Once in
  that high-energy region, every subsequent rattle of the distorted structure is
  either high-energy (stays near the top bin) or out-of-range
  (`|E| > 1e4` / below floor → rejected, which still counts the current/top
  bin), so the walk **cannot climb back down**. Flatness never triggers because
  `min H = 1` over visited bins ≪ `0.8 × mean`, so `ln_f` never refines and
  `ln_g[top]` grows unboundedly.
- **Signature:** `stages = 0` (unlike c2) — the walker is *not* "flat-stuck",
  it is simply physically trapped far from equilibrium and the histogram never
  flattens. The two `H = 1` visits at rel 0.010/0.018 are the walker's last
  moments near the ground state before escaping.

### c2 (B3): unphysical init (old code path)

- Init is **broken**: `init: rel E = 159.9996 eV/atom (bin 39)` — an
  **unphysical GPR extrapolation** (~12.5 keV on the 78-atom cell), well above
  `--e-max 0.40`. This is the exact pre-v1.2.0 "stuck at the top bin" bug
  documented in `init-window-and-stuck-top-bin.md`: `get_bin` caps `rel ≥ e_max`
  into the top bin, so the walker "starts" in bin 39 and can never be pulled
  down within these short budgets. The rattle of the already-unphysical
  structure only produces more unphysical/high energies.
- **Signature:** `stages = 2/6/10` climbing trivially (single-bin histogram is
  automatically "flat"), `visited = 1/40`. Note: these c2 outputs were produced
  before (or without) the v1.2.0 init fix — the init line shows the old
  top-of-window behaviour, not the bottom-up ground-state start. (c2 run dir's
  own code copy may still carry the old `initialize`.) Also note the c2
  `g_of_E.csv` saves `H` all-zero while `ln_g` accumulates — a save-format
  anomaly worth checking in `save()` when the code is next touched.

## What this means for the "bottom-up / ground-state" goal

This is directly relevant to the ground-state-sampling intent discussed in the
project QnA:

- **Initiating from the ground state is not sufficient.** c1 *did* start at the
  global minimum (rel 0.0011, bin 0), but the walk escaped within a handful of
  steps and never returned. The problem is the **move set / GPR extrapolation**,
  not the start point.
- The core difficulty is that **Wang–Landau's acceptance is direction-agnostic**
  and, at the start (`ln_g` all zero), accepts essentially everything — so a
  large rattle can fling the walker into GPR-extrapolation regions from which
  there is no geometric return path. A ground-state-anchored walk still needs
  either (a) a **bounded move set** that cannot leave the tracked window's
  physical basin, or (b) a **rejection/re-seed rule** that returns to the
  ground state when the walk strays, or (c) **smaller step scales**.

## Recommended next steps (for a follow-up, not done here)

None of this was changed (this is an analysis-only pass, per the task scope). For
a future fix, candidates to test with a cheap local smoke run before any HPC
submission:

1. **Reduce `--large-step`** (e.g. 0.40 → 0.10–0.15 Å) so a single rattle cannot
   catapult the walker into extrapolation territory.
2. **Reject / re-seed when a trial is unphysical or near `e_max`**, rather than
   counting it into the top bin — e.g. treat a trial whose rel energy would land
   in the top *half* of the window as an unphysical extrapolation and reject it
   (revisit current bin) instead of accepting the climb.
3. **Anchor the walk to the ground state** (bottom-up enforcement): periodically
   re-seed from the global minimum, or add a small downward bias / acceptance
   toward `E_ref`, so the walk cannot permanently lose the minimum basin.
4. For **c2**, first **re-sync the run's `wang_landau/` copy to the v1.2.0
   init fix** (the observed init rel 159.9996 proves it is running old code), then
   apply the c1 fixes above.

## Files analysed

- `wl_output_c1_sweep_{30000,60000,100000}/g_of_E.csv`,
  `thermodynamics.csv`, `heat_capacity.csv`
- `jc1_sweep.sh.6654357.out`
- `wl_output_c2_sweep_{10000,30000,50000}/g_of_E.csv`,
  `thermodynamics.csv`, `heat_capacity.csv`
- `j_c2_boron3_N40_Emax04_sweep.sh.6649512.out`
