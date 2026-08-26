# GPR accuracy vs energy range (Fe/MgO) — `gpr_accuracy.py`

How to report how well the AGOX GPR surrogate predicts structure energies **as a
function of the energy range**. Live at
`/home/think/Desktop/research/_run/b_nestedsampling/gpr_accuracy.py` (v1.0.0, in
scope / versioned). Prompt origin: PROMPTS.md flag `20260826_2333`.

## What it does
1. Loads all seed DBs (`dataset/seed_*/1_db/db_*.db`, 1297 Fe25Mg25O25 / 75-atom
   structures).
2. Trains ONE GPR (same AGOX kernel recipe as `main.py`; `use_ray=False` default,
   `--use-ray` opt-in).
3. Predicts in-sample energies, bins structures by **energy above the global
   minimum in eV/atom** (equal-width bins, default 0.1), and computes
   **MAE / RMSE / R² per bin** (+ overall).

Run:
```bash
/home/think/miniconda3/envs/agox_v2/bin/python gpr_accuracy.py \
    --bin-width 0.1 --output ./gpr_accuracy_out
```
Outputs: `gpr_accuracy_by_energy_range.csv`, `gpr_accuracy_by_energy_range.png`
(MAE/RMSE on left axis, R² on twin right axis), printed table.

## Critical calibration: bin width
The Fe/MgO combined-set total range is only **0 .. ~0.675 eV/atom** (E/atom
−5.83 .. −5.15 eV). The prompt's "1 eV/atom" example would collapse ALL structures
into one bin. Default bin width 0.1 eV/atom → ~7 bins. Always check the actual
dE/atom spread before choosing a bin width:
```python
import glob, numpy as np
from agox.databases import Database
E=[]
for p in sorted(glob.glob('dataset/seed_*/1_db/db_*.db')):
    db=Database(filename=p); db.restore_to_memory(); t=db.restore_to_trajectory()
    E += [a.get_potential_energy()/len(a) for a in t]
print(np.percentile(np.array(E)-min(E), [0,10,25,50,75,90,100]))
# -> [0.    0.038 0.066 0.106 0.25  0.435 0.675]
```

## In-sample vs generalization — the key caveat
These are **in-sample residuals** (test points == training points, i.e. GPR
interpolation). Verified result: MAE ~0.0007, RMSE ~0.0010, R² ≈ 1.0 eV/atom across
all bins — essentially exact. This measures **training-set fit, NOT out-of-sample
generalization**. If the user wants a truthful accuracy on *unseen* structures,
use K-fold cross-validation (train on 80%, predict held-out 20%, pool errors per
bin); ~5× slower. State this caveat in the output/docs; do not present near-zero
in-sample error as real predictive accuracy.

## Structure
- `bin_metrics(dE, err, bin_width, n_atoms)` — pure function, per-bin + overall
  MAE/RMSE/R², unit-testable.
- Metrics computed in eV/atom to stay consistent with the energy-range axis.
- R² per bin uses the bin's own mean (not the global mean) as reference.
