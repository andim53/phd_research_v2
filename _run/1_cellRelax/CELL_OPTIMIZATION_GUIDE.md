# AGOX Variable-Cell Relaxation Integration Guide

This guide provides a structured approach for integrating variable-cell relaxation into your AGOX search workflow. 

## 1. Overview & Architectural Changes

In standard AGOX workflows, candidate optimization relaxes only atomic positions (`LocalOptimizationEvaluator` / `ParallelRelaxPostprocess`) while keeping the unit cell vectors fixed. 

To enable variable-cell relaxation, we must introduce the following architectural changes:
1. **Calculator Stress Support**: The calculator must be configured to return the stress tensor.
2. **Optimizer Modification**: Standard ASE optimizers (e.g., `BFGS`) only relax atomic coordinates. We must introduce a custom optimizer wrapper that applies an ASE `CellFilter` (e.g., `ExpCellFilter`) to the candidate.
3. **Surrogate Model Limitation**: **Crucially**, surrogate models (GPR) in AGOX are trained *only* on energies and forces. They **cannot** perform variable-cell relaxation. Unit cell relaxation must therefore only be performed in the **Real-Potential Evaluation** (`LocalOptimizationEvaluator`).

---

## 2. Step-by-Step Implementation Guide

### Step 2.1: Calculator Setup
Ensure your calculator (e.g., `SubprocessGPAW`) is capable of computing stress. 
- **Requirement**: Use `lcao` or `pw` mode in GPAW. Real-space (`fd`) mode does **not** support stress calculation.
- **K-points**: For heterostructure or 2D slab systems, increasing k-points in the lateral (XY) plane is highly recommended for well-converged stress tensors, which are essential for stable cell relaxation.

### Step 2.2: Environment Definition
The `Environment` defines the search space. For 2D slab systems, you must explicitly prevent relaxation in the Z-direction (to avoid vacuum collapse). This is handled via the optimizer wrapper (Step 2.3) rather than the Environment itself, but ensure your `box_constraint_pbc` is correctly set (e.g., `[True, True, False]` for 2D slabs).

### Step 2.3: Cell Filter & Optimizer Integration
Create a custom optimizer wrapper that applies `ExpCellFilter`. This wrapper acts as an ASE optimizer, making it compatible with AGOX evaluators and postprocessors.

```python
from ase.filters import ExpCellFilter
from ase.optimize import BFGS

class CellRelaxationBFGS:
    def __init__(self, atoms, **kwargs):
        # 2D Mask: [xx, yy, zz, yz, zx, xy]
        # True = relax, False = fixed. 
        # Example: relax in-plane (xx, yy), fix zz/yz/zx/xy.
        mask = kwargs.pop('mask', [True, True, False, False, False, False])
        
        # Wrap atoms in a CellFilter
        self.filter = ExpCellFilter(atoms, mask=mask)
        # Instantiate optimizer with the filter
        self.optimizer = BFGS(self.filter, **kwargs)

    def attach(self, function, interval=1, *args, **kwargs):
        # Delegate attach to the real optimizer
        self.optimizer.attach(function, interval, *args, **kwargs)

    def run(self, **kwargs):
        self.optimizer.run(**kwargs)

    def get_number_of_steps(self):
        return self.optimizer.get_number_of_steps()
```

### Step 2.4: Updating `ParallelRelaxPostprocess`
**DO NOT use variable-cell relaxation here.** Since the GPR model does not support stress, keep the optimizer as the standard `BFGS` for position-only relaxation.

### Step 2.5: Updating `LocalOptimizationEvaluator`
Pass your custom wrapper class to the `LocalOptimizationEvaluator`:

```python
evaluator = LocalOptimizationEvaluator(
    calc,
    optimizer=CellRelaxationBFGS, # Use the wrapper here
    optimizer_kwargs={"logfile": None, "mask": [True, True, False, False, False, False]},
    ...
)
```

---

## 3. Reference Code Blueprint

```python
# 1. Define custom wrapper (as in Step 2.3)
...

# 2. In your AGOX runscript:
# ... Generator/Acquisitor setup ...

# 3. Evaluator with variable-cell relaxation (Real Potential)
evaluator = LocalOptimizationEvaluator(
    calc, 
    optimizer=CellRelaxationBFGS,
    optimizer_kwargs={"mask": [True, True, False, False, False, False]}, # 2D relaxation
    optimizer_run_kwargs={"fmax": 0.05, "steps": 50}
)

# 4. Postprocessor (Surrogate Potential)
# NOTE: Use standard optimizer here
relaxer = ParallelRelaxPostprocess(
    model=acquisitor.get_acquisition_calculator(),
    optimizer=BFGS, 
    ...
)
```

---

## 4. Verification & Troubleshooting

### Common Failure Modes
1. **Vacuum Collapse**: Occurs if `mask` includes `zz` (index 2) for slab systems. Ensure `mask[2]` is `False`.
2. **Unstable Relaxation**: Usually caused by poorly converged stress tensors. Increase k-points (`kpts`) or decrease `fmax` in `optimizer_run_kwargs`.
3. **Pulay Stress**: If using `pw` mode, ensure `ecut` is sufficiently high.

### Verification Check
Monitor your candidate structures in the database:
1. Check the `cell` column (e.g., using `agox.databases.Database.read_all()`).
2. Verify that cell vectors change across iterations (`cell` values are distinct for different candidates or iterations).
3. If cell vectors remain identical despite stress being high, ensure your custom wrapper is correctly wrapping the atoms and being passed to the `LocalOptimizationEvaluator`.
