# PROMPTS — Project a_lcbnovel prompt log

This file logs every prompt the owner adds for future work, numbered simply `#1`,
`#2`, `#3`, ... (newest last). See `AGENTS.md` §3b for the rules.

#1
Edit the analysis code in 2_analysist/ — apply the same change to both runners:
`run_analysis_a_runs.py` (single-seed a-runs) and `run_analysis_indices.py`
(multi-seed 71/72).

Add a CLI flag `--extract` that reads the database and writes a **single JSON file**
containing **all the raw data** needed to produce every plot the runner currently
outputs: the per-seed best-so-far progression, the PCA landscape + state density
(`conf_space.png`), and the Boltzmann probability vs temperature
(`binding_probability_vs_temperature.png`).

Add a second, **independent** flag `--plot-from-json` that plots **only from that
JSON file** (the database is not read) and reproduces the **same PNGs** — identical
to plotting directly from the database. Each flag must work on its own; the JSON
must hold everything needed for a DB-free, bit-identical PNG rerun.

#2
write me a report. obsidion-daily-report skill. How much time does it take to finish 100 to 700 It
eration, and also check, how much Iteration does it necessary to reach a convergence (find its globa
l minimum). For
