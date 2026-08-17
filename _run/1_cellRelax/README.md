# Version History of main.py

This directory contains backup versions of `main.py`.

## Version Overview

- **main.py.v0**: Initial version using `SubprocessGPAW` and a cubic template cell (6x6x6).
- **main.py.v1**: Configuration update: switched to direct `GPAW` with `lcao`/`dzp` basis. Changed system to Si2 with a smaller primitive unit cell (~3.84 Å). Reduced k-points to (1,1,1) and updated relaxer parameters.
- **main.py.v2**: Introduced custom `CellRelaxationBFGS` optimizer wrapper to support variable-cell relaxation using `ExpCellFilter`. Updated Relaxer to use this new optimizer.
- **main.py.v3**: Added a postprocessor (Surrogate Potential) using position-only optimization (GPR limitations). Updated the evaluator to perform variable-cell relaxation using the new `CellRelaxationBFGS` and increased optimization steps.
- **main.py.v4**: Refined the variable-cell relaxation by switching the filter in `CellRelaxationBFGS` from `ExpCellFilter` to `FrechetCellFilter`.
