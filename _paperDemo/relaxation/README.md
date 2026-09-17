# relaxation/ — DFT re-relaxation of search structures

> **Status (2026-09-17): the SELECTION has been run; the DFT RE-RELAXATION has NOT.**
> `relaxation/selected/` holds 116 structures (femgo 53, febmgo 28, fecomgo 18, fecobmgo 17) with
> `manifest.csv`, but there is **no `relaxed/` directory and no `relax_results.csv`** — `relax.py`
> has never been executed, so no structure in this paper rests on a converged DFT minimum. The
> convergence limitation in the draft is a consequence of this.
>
> **Scope (CLAIMS v9, 2026-09-17): the paper is Fe/MgO + Fe-B/MgO, so 81 of these 116 structures are
> in scope** — femgo 53 + febmgo 28. The 35 Co-containing entries (`fecomgo` 18, `fecobmgo` 17) are
> out of scope with the rest of the Fe-Co host; they are left in `selected/` rather than deleted, and
> a fresh run of `select_structures.py` (now scope-aware, `--all-systems` for all four) regenerates
> the manifest with the same per-system counts minus those two.
>
> Verified 2026-09-17: the selection contains **no structures from the runs excluded by the v8
> completed-search rule** (no `fecomgo/seed_4`, no `fecobmgo/seed_3`), so re-running it is not
> required by that rule. A fresh selection would still need the rule applied.

The AGOX search structures are **not DFT-converged**: candidates are relaxed by the GPR
surrogate (`ParallelRelaxPostprocess`, 100 steps, `start_relax=10`) and then evaluated
with only **1 GPAW step** (`fmax=0.05, steps=1`), leaving residual forces of ~1–2 eV/Å.
This pipeline re-relaxes selected structures properly so that the flat-basin / island
picture can be stated on converged minima.

## Pipeline

```
select_structures.py   ->  selected/{system}/*.xyz + selected/manifest.csv
        |
        v
   job_relax.sh  (pjsub on HPC, gpaw_env)
        |
        v
   relax.py            ->  relaxed/{system}/*_relaxed.xyz + relaxed/relax_results.csv
```

## 1. Select structures

```bash
/home/think/miniconda3/envs/agox_v2/bin/python relaxation/select_structures.py \
    --min-iteration 10 --force-percentile 5 --desc-tol 0.2
```

- **iteration >= 10**: relax starts at iteration 10 in the search.
- **force filter**: keep the **lowest `--force-percentile`% of each system** by max|F|
  (default 5%). A per-system percentile is used because the systems' force levels differ —
  an absolute cutoff (e.g. 0.5 eV/Å) selects nothing (best structures have max|F| ≈ 0.75–1.11).
  An absolute `--max-force` cutoff can be given instead (overrides the percentile).
- **distinctness**: greedy de-duplication by AGOX `Fingerprint` feature distance — scan
  lowest-energy first, keep a structure only if it is `> --desc-tol` (default 0.2) from
  every kept one.
- No cap on the number kept; all low-force distinct structures are written.

Output: `selected/{system}/{system}_NNN.xyz` + `selected/manifest.csv`
(columns include `template_indices`, the frozen substrate, and `dZ`, `dE_per_atom`).

Example outcome (percentile 5, desc-tol 0.2): femgo 53, febmgo 28, fecomgo 18,
fecobmgo 17 → **116 structures**, covering both the flat (ΔZ ≤ 1) and island basins.

## 2. Re-relax (HPC)

```bash
pjsub relaxation/job_relax.sh
```

or directly:

```bash
python relaxation/relax.py --manifest relaxation/selected/manifest.csv --fmax 0.05
```

GPAW settings match the search runs: LCAO/`dzp`, PBE, `kpts=(1,1,1)`, Fermi-Dirac 0.05 eV,
`spinpol`, `hund`, `symmetry='off'`. The substrate (`template_indices`) is frozen
(`FixAtoms`); the metal film relaxes. ASE `BFGS` to `fmax = 0.05 eV/Å`.

Crash-safe: already-relaxed structures are skipped on re-run (`relax_results.csv`).

Output: `relaxed/{system}/{base}_relaxed.xyz` (+`.traj`), `_gpaw.txt`, `_opt.log`, and
`relaxed/relax_results.csv` (E_initial, E_final, max_force_final, n_steps, converged).

## After relaxation

Recompute the ΔZ / dE-per-atom basin analysis on the **relaxed** set and update
`experiment_log.md` / `paper_status.md`. Only then can flat-vs-island energies, and any
metastability claim, rest on converged DFT minima.
