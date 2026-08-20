# Fix: `run.py` LocalOptimizationEvaluator error

## Error log

`/home/think/Desktop/research/_run/6_lcbnovel_benchmark/j_bench.sh.6544501.out`

```
File "run.py", line 253, in build_stack
    evaluator = LocalOptimizationEvaluator(**evaluator_kwargs)
TypeError: LocalOptimizationEvaluator.__init__() missing 1 required positional argument: 'calculator'
```

## Root cause

`LocalOptimizationEvaluator.__init__(self, calculator, ...)` declares the ASE
calculator as the first required positional/keyword argument, named **`calculator`**.

In `run.py`, `build_stack()` assembled the evaluator's keyword arguments into the
dict `evaluator_kwargs` using the key `calc`:

```python
evaluator_kwargs = dict(
    calc=sys_ij["calc"],          # <-- wrong key
    ...
)
```

When unpacked with `**evaluator_kwargs`, `calc` did not match the `calculator`
parameter, so it fell into the constructor's `**kwargs` catch-all and the required
`calculator` argument was never supplied. Python therefore raised
`TypeError: ... missing 1 required positional argument: 'calculator'`.

The benchmark crashed at the very first build step (RUN 1/5, regular LCB) before any
optimization ran.

## Fix

Rename the dict key `calc` -> `calculator` so it binds to the evaluator's actual
parameter:

```python
evaluator_kwargs = dict(
    calculator=sys_ij["calc"],    # <-- fixed key
    ...
)
```

Changed in `run.py` at line 223.

## Notes on the `novelty_lcb` package

This error is *not* inside the `novelty_lcb` package itself — it is a wiring bug in
the benchmark's `run.py`. The local `novelty_lcb/acquisitor.py` in this directory was
checked and already contains the correct, Ray-serializable
`get_acquisition_calculator()` implementation (module-level LCB surface functions
wrapped in `functools.partial(kappa=...)`), so the Novelty-LCB runs are not affected by
this particular bug.

## Verification

- `LocalOptimizationEvaluator(calculator=EMT(), ...)` constructs cleanly in the
  `agox_v2` conda env.
- `python -m py_compile run.py novelty_lcb/__init__.py novelty_lcb/acquisitor.py` — OK.
- Running `run.py` now passes the build stage and progresses through the AGOX
  optimization loop (GPR trains, candidates relax via ParallelRelaxPostprocess,
  EMT evaluates, Database stores). This confirms the previous build-time crash is
  resolved.

## How to run

```bash
conda activate agox_v2
cd /home/think/Desktop/research/_run/6_lcbnovel_benchmark
python run.py
```

Reminder: the benchmark config uses an uncalibrated Novelty-LCB energy window
(`target_energy=0.0`, `delta_E=2.0` in `run.py`). Run a short standard-LCB search first
and set these to the centre/half-width of the actual energy band before drawing
conclusions from the Novelty-LCB results.
