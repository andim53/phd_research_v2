# CLAIMS.md — paper2 (frozen claim list)

> **paper2 = current-results fork of paper1.** Same claims; figures referenced directly
> from `analysis/figures/` (regenerated, current style). Prose matches current results:
> 13 runs (Run 1–13), 1,180 configs, peaks 0.079/0.259, true Boltzmann density.

Freeze the claims before drafting. Any new claim requires bumping this file to v2 first. Numbers reflect the **current manuscript** (13 runs, 1,180 configs, peaks 0.079/0.259 eV/atom, seeds 3–15, `stop_16` excluded) — the older draft figures (14 runs / 1,207 configs, 0.074/0.255) are superseded.

## One-sentence contribution
A biased-exploration active-learning (GOFEE/AGOX) framework samples a minimum-ensemble of surrogate-relaxed Fe/MgO(001) structures, from which KDE state-density + Boltzmann analysis show the island (Volmer-Weber) mode is the thermodynamic ground state and that temperature alone cannot suppress it.

## Main-text claims (MT)
- **MT-1** Island mode is the ground state of Fe/MgO(001). → Fig_Prog, Fig_ConDen
- **MT-2** The minimum-ensemble state density g(E) has two high-degeneracy peaks at ~0.079 and ~0.259 eV/atom. → Fig_ConDen
- **MT-3** The flat mode sits ~0.18 eV/atom above the island ground state. → Fig_ConDen
- **MT-4** Increasing temperature raises the flat-mode Boltzmann probability, but the energy barrier makes thermal fluctuations insufficient to suppress islanding. → Fig_Boltz
- **MT-5** The ensemble comprises 1,180 DFT-evaluated configurations from 13 independent runs (seeds 3–15, stop_16 excluded). → Fig_convStateDens
- **MT-6** Island mode is preferred due to localized interfacial Fe 3d orbitals near the Fermi level destabilizing the flat mode. → Fig_dos

## Supplementary claims (SI)
- **SI-1** Island mode is robust to supercell size (3×3, 4×4); island height increases ~1 Å per area increment. → Fig_sup
- **SI-2** Reverse deposition (MgO-on-Fe) yields a flat ground state, contrasting Fe-on-MgO. → Fig_mgo
- **SI-3** AGOX environment: Fe confined in a box, z-height 8.4 Å; substrate fixed. → Fig_env

## NOT claimed
- No quantitative claim about DOS beyond the Fe-3d peak at E_f (only 2 DOS seeds available).
- No claim that temperature alone can achieve flat growth (explicitly refuted).
- No claim about the Fig_flow schematic's exact generator counts beyond the draft text.

## Limitations
- Only 2 DOS seeds (`dos_seed_3.csv`, `dos_seed_4.csv`) back Fig_dos.
- `stop_16` (36 configs) and `mgofe/seed_5` (26 configs) are truncated runs — excluded from pooled statistics.
- Finite-size data (3×3/4×4) lives in `data/femgo_3x3` / `data/femgo_4x4` (copied from `_analysist/1_result`).

## Future work (not yet claimed, parked)
- **Wetting-mode comparison (Fe/MgO vs Fe-B/MgO):** figures `Fig_wetModes` / `Fig_wetLandscape` exist in `analysis/figures/` and code in `codes/emit_wetting_modes.py`, `codes/draw_wetting_modes.py`, `draw_wet_landscape.py` (all versioned, VERSIONS.md), but are **not yet referenced by any `.tex`**. LOG Sessions 9 ff. describe these as an active "remaining boron figures" workstream. Treat them as future content: when a manuscript section (or dedicated paper) claims these results, add the claims + wire the figures, and mark them claimed here.

## Sign-off
- [ ] Owner confirms contribution framing
- [ ] Owner confirms claim list
