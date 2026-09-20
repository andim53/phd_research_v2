# CLAIMS.md — paper1 (frozen claim list)

Freeze the claims before drafting. Any new claim requires bumping this file to v2 first. Numbers are **as drafted** (frozen); on-disk discrepancies are flagged in the data-consistency report, not silently edited.

## One-sentence contribution
A biased-exploration active-learning (GOFEE/AGOX) framework samples a minimum-ensemble of surrogate-relaxed Fe/MgO(001) structures, from which KDE state-density + Boltzmann analysis show the island (Volmer-Weber) mode is the thermodynamic ground state and that temperature alone cannot suppress it.

## Main-text claims (MT)
- **MT-1** Island mode is the ground state of Fe/MgO(001). → Fig_Prog, Fig_ConDen
- **MT-2** The minimum-ensemble state density g(E) has two high-degeneracy peaks at ~0.074 and ~0.255 eV/atom. → Fig_ConDen
- **MT-3** The flat mode sits ~0.18 eV/atom above the island ground state. → Fig_ConDen
- **MT-4** Increasing temperature raises the flat-mode Boltzmann probability, but the energy barrier makes thermal fluctuations insufficient to suppress islanding. → Fig_Boltz
- **MT-5** The ensemble comprises 1,207 DFT-evaluated configurations from 14 independent runs (seeds 0–13). → Fig_convStateDens. **NOTE:** on-disk data = seeds 3–15, 1,180 under iter≥10 filter — flagged, not edited.
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
- Manuscript's stated ensemble size (1,207) does not match on-disk count (1,180 under iter≥10).

## Sign-off
- [ ] Owner confirms contribution framing
- [ ] Owner confirms claim list
