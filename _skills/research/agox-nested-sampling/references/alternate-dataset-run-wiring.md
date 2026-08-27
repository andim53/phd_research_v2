# Wiring an alternate dataset into a self-contained run dir (boron / non-default composition)

Pattern from run `b2_boron_ns`: when a nested-sampling run must use a *different* dataset
than the project-root `dataset/` (e.g. the B-doped `dataset_boron/`, Fe25Mg25O25B7),
**copy the alternate dataset into the run dir as `dataset/`** rather than touching `main.py`.

## Why copy-as-`dataset/` instead of adding a flag

`main.py` hardcodes `DATASET_DIR = os.path.join(_HERE, "dataset")`. Adding a
`--dataset-dir` flag would modify shared code that is version-bumped and synced across
`_runs/`. Copying the dataset in keeps the runner byte-identical to the project root and
the run fully self-contained:

```bash
cp -r <project>/dataset_boron <run_dir>/dataset
```

`b2_boron_ns` is the worked example: same NS params as `_analysist/1_result/1_no_prior_control`
(`--temp 300 --n-live 100 --n-iters 1000 --perturb 0.01 --output ./ns_output_T300_100_1000_0.01 --rng 42`)
but on the B-doped set with `--perturb-symbols Fe,B`.

## Verify the non-uniform composition before running

The global `Fingerprint` descriptor supports ONE stoichiometry, and the perturb-symbols
atom count must match expectation. On Fe25Mg25O25B7 (5 seeds, 496 structures), `Fe,B`
should match **32 atoms (25 Fe + 7 B)**. Confirm:

```python
from collections import Counter
import numpy as np
comp = Counter(structures[0].get_chemical_symbols())   # {'O':25,'Mg':25,'Fe':25,'B':7}
sym  = np.array(structures[0].get_chemical_symbols())
idx  = np.where(np.isin(sym, ['Fe','B']))[0]           # len == 32
```

## Note on B-doped energy range

B-doped datasets can contain grossly high-energy structures (E/atom up to ~0 eV vs the
~−5.8 eV minimum). The sampler's `|E|<1e4` physical filter handles the gross outliers, so
do not let a wide-looking energy range stop the run.
