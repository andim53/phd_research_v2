# hpc_runs — SHC / selection pipeline for amorphous Pt(P)

Two-stage HPC pipeline feeding the paper's SHC section, per
`spec/202609211704-ptp-shc-stage.md` (v7). **Nothing runs on the laptop** — submit via
`pjsub` on the HPC node in the `gpaw_env` conda env (has BOTH gpaw and agox).

## Layout
```
hpc_runs/
├── select_reopt/          Run A: novelty+force filter + DFT re-opt
│   ├── filter_select.py   stage 1: per-leaf novelty+force filter (~3 distinct minima)
│   ├── reopt.py           stage 2: GPAW re-opt to strict fmax -> opt_novel_<leaf>.traj x4
│   └── job_genkai_mpi.sh  pjsub: runs both stages (gpaw_env, 24 procs, 120 h)
├── shc/                   Run B: FLAPW spin Hall conductivity
│   ├── main.py            SCF->SOC->optics->xoptics + SHC parsing -> shc_summary.{json,csv}
│   ├── make_ref_traj.py   build the 0%-P crystalline reference traj
│   └── job_genkai_mpi.sh  pjsub: one submission per leaf traj (4 amorphous + 1 ref)
├── convert_dose_concentration.py  maps the reference's ion-dose <-> our at% P
└── xrd_benchmark.py       writes CIFs for the existing XRD pipeline (amorphous vs ref)
```

## Run A — select + re-opt
Stage 1 (filter_select.py) reads `data/17_PPt` (read-only), force-gates each leaf
(leaf-adaptive cutoff: 20P ~1.0, 30P ~2.0 eV/A; percentile + fallback), dedups by AGOX
Fingerprint (calibrated tolerance from the NN-distance distribution), and picks the
lowest-energy distinct low-force minima. Writes `selected/<leaf>/<rank>.xsf` +
`selection_<leaf>.json`. Stage 2 (reopt.py) GPAW-relaxes them (lcao/dzp/PBE, fmax 0.05,
all atoms mobile) into `opt_novel_<leaf>.traj` x4.

```bash
cd hpc_runs/select_reopt
pjsub job_genkai_mpi.sh          # runs filter_select.py then reopt.py
```

## Run B — FLAPW SHC
One pjsub per leaf traj (spec M3). `main.py` reads a traj (env `TRAJ_FILE` or `--traj`),
runs SCF->SOC->optics->xoptics for each structure, parses SHC into
`shc_out/shc_summary.{json,csv}`. Reference: make `ref_0P_gmin.traj` from the +0 cell 0P
leaf, run it through the same stage.

```bash
cd hpc_runs/shc
# 4 amorphous leaves + 1 reference:
for t in ../select_reopt/out_select_reopt/opt_novel_{2_20P,3_30P,1_3x3_20P,2_3x3_30P}.traj; do
  TRAJ=$t pjsub job_genkai_mpi.sh
done
TRAJ=ref_0P_gmin.traj pjsub job_genkai_mpi.sh
```

## Comparison vs reference (Shashank 2025, NPG Asia Materials)
- Transport: sigma^SH_xy = 3.62e3 (pure Pt 1.03e3) (2e/hbar) ohm^-1 cm^-1; theta_SH 1.17.
- Structural benchmark = SIMULATED XRD (existing `_run/0_lcb/2_analysist` pipeline,
  agox_v2 CIF -> pymat_xrd Cu-Ka XRD + CI). Reference SI S4/S5: pure Pt fcc a=3.932 A,
  I(220)/I(111) 0.33->3.14, peak shift + halo/amorphization as P dose rises.
- `convert_dose_concentration.py` maps their ion-dose/keV to at% P (SRIM-based) so both
  XRD and SHC sit on a common P-concentration axis.

## Units
Measured 20% P ≈ 2.2e16 ions/cm^2, 30% P ≈ 3.4e16 ions/cm^2 (inside the reference's
2.5–10e16 range). SHC reported in (ohm cm)^-1 (flapw>=4.16 factor); parser states both
unit forms.
