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
(`binding_probability_vs_temperature.png`). The JSON must be an **independent,
self-describing file** that an AI can read on its own to understand the resulting
data (clear structure, named fields, and enough context to interpret each value
without the database).

Add a second, **independent** flag `--plot-from-json` that plots **only from that
JSON file** (the database is not read) and reproduces the **same PNGs** — identical
to plotting directly from the database. Each flag must work on its own; the JSON
must hold everything needed for a DB-free, bit-identical PNG rerun.

#2
Write me a report and save it via the obsidian-daily-report skill (Obsidian report
dir, today's date). Cover the iteration-budget a-runs only: a1 (Iter300), a2
(Iter500), and a3 (Iter700).

For each run, report:
- the wall-clock time it took to finish (from the gpaw_logs / j_*.out timestamps);
- the iteration at which the global minimum (the lowest DFT energy) was first
  found, from the progression data.

#3
Make a new run, with dipole correction.
