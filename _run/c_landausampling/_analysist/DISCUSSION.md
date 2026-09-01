# DISCUSSION — Wang-Landau HPC outputs (c1 Fe/MgO, c2 B3)

Analysis tool: `_analysist/analyze_wl_outputs.py` (v1.0.0)
Data: `_analysist/c1_mgofe_N40_Emax04/wl_output_*` and
`_analysist/c2_boron3_N40_Emax04/wl_output_*` (HPC output dirs), plus the job
`.out` logs.

Figures produced:
- `_analysist/state_density_c1.png` — ln g(E) vs rel energy per atom for all
  c1 outputs (mc1000 + sweep 10k/30k/50k).
- `_analysist/state_density_c2.png` — same for c2 (sweep 10k/30k/50k).
- `_analysist/wl_analysis_summary.csv` — per-output metrics.

---

## 1. The plotting bug that killed the HPC `g_of_E.png`

Every HPC `wl_output_*` dir contains the three CSVs (`g_of_E.csv`,
`thermodynamics.csv`, `heat_capacity.csv`) but **no `g_of_E.png`**. The job
`.out` logs end with:

```
ValueError:
(E - E_{\\mathrm{min}})/N
ParseSyntaxException: Expected end_group, found '\' (at char 8)
```

The `main.py` g(E) x-label was `r"$(E - E_{\\mathrm{min}})/N$"` — a raw string
with a **double** backslash before `mathrm`, so matplotlib's mathtext parser saw
`\\mathrm` (a literal backslash) and crashed while rendering the label, killing
the PNG save. The CSVs are written before that, so the g(E)/thermo data
survived but the figure did not.

**Fix:** replace `E_{\\mathrm` with `E_{\mathrm` (single backslash) in all
`main.py` copies (project root, `_runs/c1`, `_runs/c2`, and the `_analysist`
snapshots). Verified the label now renders.

---

## 2. The physics: the walker is stuck near the top bin (not converging)

The `g_of_E.csv` and `.out` logs show a serious problem: **the Wang-Landau
walker never explores the energy range — it is stuck in the top bin.**

### c1 (Fe/MgO), init rel E = 0.675 eV/atom (bin 39 of [0, 0.40])

The initial walker is placed at rel E ≈ 0.675 eV/atom, **well above `--e-max
0.40`**, so `get_bin` caps it into the top bin (bin 39). From there the
small/large rattle (0.05/0.40 Å on Fe) cannot lower the GPR energy enough to
escape the top bin in these short budgets, so the walk stays put:

| mc-steps | bins visited | energy spread | stages | note |
|---|---|---|---|---|
| 1000 | 1/40 | 0.000 | 0 | stuck at top bin |
| 10000 | 1/40 | 0.000 | 2 | stuck |
| 30000 | 20/40 | 0.190 | 2 | starts to descend |
| 50000 | 20/40 | 0.190 | 4 | still partial |

### c2 (B3), init rel E = 159.9996 eV/atom (bin 39) — unphysical

The c2 walker initializes at **rel E ≈ 160 eV/atom**, a clearly **unphysical
GPR extrapolation** (the `|E| > 1e4` guard should have caught energies with
|E| > 1e4 eV, but 160 eV/atom above the minimum corresponds to ~12,500 eV on a
78-atom cell — still within `1e4`'s absolute threshold, so it passed). The walk
then spends all its time at the top bin:

| mc-steps | bins visited | energy spread | stages | rattle/swap |
|---|---|---|---|---|
| 10000 | 1/40 | 0.000 | 2 | 8074 / 1926 |
| 30000 | 1/40 | 0.000 | 6 | 24098 / 5902 |
| 50000 | 1/40 | 0.000 | 10 | 40170 / 9830 |

The stages DO advance (flatness is satisfied because the walk visits the single
top bin repeatedly), and the swap move is active (~20% of moves), but the
**state density is a delta at the top bin** — no physics.

### Root cause

`initialize(start_from_top=True)` picks the **highest-rel-energy structure in
the DB** (the 'flat' analogue) to start at the top of the bin range. But the
chosen structure's GPR energy can lie far outside `[e_min, e_max]`:
- c1: 0.675 eV/atom (vs e_max 0.40) → capped into the top bin, and the rattle
  can't pull it down within these budgets.
- c2: 159.9996 eV/atom (unphysical extrapolation) → same, worse.

So the initial walker starts *above* the tracked window, and Wang-Landau's
`get_bin` caps out-of-range energies into the top bin, trapping the walk there.

### Why convergence metrics are misleading

`stages reached` (2, 4, 6, 10) and `final_ln_f` look like progress, but they
only reflect that the walk keeps visiting the *same* top bin (histogram "flat"
trivially). The **visited-bin count** is the honest metric: c1 gets to 20/40
only at 30k+ steps; c2 stays at 1/40 at all budgets.

---

## 3. Thermodynamics: Z/F are meaningless here

The `thermodynamics.csv` shows `F = -4.07e2 eV` independent of T, and
`logZ@100K` ≈ 4.7e4 / 4.9e4 (enormous, and `Z = inf` in some rows). Because
g(E) is a delta at the top bin (c2) or only partially filled (c1), the
normalised state density and the derived `Z(T)`, `F(T)`, `C_V(T)` are **not
physically meaningful** — they reflect the stuck walker, not the system's
thermodynamics.

---

## 4. Recommendations

1. **Fix the initialization.** Do not start the walker above the tracked window.
   Either cap `initialize()` to pick a structure whose rel energy is *inside*
   `[e_min, e_max]`, or start from the global minimum and let the walk ascend.
2. **Reject unphysical GPR energies at init.** Guard `init_rel_E` against the
   tracked window (or against `|E| > 1e4` per-atom), like the walk already does
   for trial moves.
3. **Re-run the sweeps** after the fix; the state-density figures here reflect
   the stuck-walker state, not converged g(E).
4. Use **visited-bin count** (not stage count) as the convergence diagnostic.

---

## 5. Reproduce

```bash
cd /home/think/Desktop/research/_run/c_landausampling/_analysist
/home/think/miniconda3/envs/agox_v2/bin/python analyze_wl_outputs.py
```
Writes `state_density_c1.png`, `state_density_c2.png`, `wl_analysis_summary.csv`
in `_analysist/`.