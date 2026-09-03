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

#4
Error:

(base) think@ThinkPad-X250:~/Desktop/research$ tmux attach -
t run
[detached (from session run)]
DONE. JSON under: /home/think/Desktop/research/_run/a_lcbnov
el/2_analysist/a8_mgofe_Seed3_Iter500_k4_nw3/analysis_a_runs
============================================================
==========
SINGLE-SEED AGOX ANALYSIS (Novelty-LCB a-runs)
dataset: a9_mgofe_Seed3_Iter500_k4_nw4/output
outdir : a9_mgofe_Seed3_Iter500_k4_nw4/analysis_a_runs
start-iter : 10 (iteration >= 10)
============================================================
==========
  a9_mgofe_Seed3_Iter500_k4_nw4/output/seed_3/1_db/db_3.db: 
491/500 structures (iteration >= 10)
  -> extracted analysis data to a9_mgofe_Seed3_Iter500_k4_nw
4/analysis_a_runs/analysis_data.json

DONE. JSON under: /home/think/Desktop/research/_run/a_lcbnov
el/2_analysist/a9_mgofe_Seed3_Iter500_k4_nw4/analysis_a_runs
============================================================
==========
SINGLE-SEED AGOX ANALYSIS (Novelty-LCB a-runs)
dataset: a10_mgofeb_Seed3_Iter500/output
outdir : a10_mgofeb_Seed3_Iter500/analysis_a_runs
start-iter : 10 (iteration >= 10)
============================================================
==========
  a10_mgofeb_Seed3_Iter500/output/seed_3/1_db/db_3.db: 0/0 s
tructures (iteration >= 10)
Traceback (most recent call last):
  File "/home/think/Desktop/research/_run/a_lcbnovel/2_analy
sist/run_analysis_a_runs.py", line 577, in <module>
    main()
  File "/home/think/Desktop/research/_run/a_lcbnovel/2_analy
sist/run_analysis_a_runs.py", line 547, in main
    extract_json(args.dataset, args.outdir, start_iter=args.
start_iter, e_max=args.e_max)
  File "/home/think/Desktop/research/_run/a_lcbnovel/2_analy
sist/run_analysis_a_runs.py", line 423, in extract_json
    num_atoms = len(all_structs[0])
                    ~~~~~~~~~~~^^^
IndexError: list index out of range
(base) think@ThinkPad-X250:~/Desktop/research/_run/a_lcbnove
l/2_analysist$ 
[run] 0:bash*                "ThinkPad-X250" 00:50 04-Sep-26

#5
Make a report comparing the "number of data" and the "degree of novelty"
(difference / duplication / variety) across the per-seed a-runs a1–a9, save it via
the obsidian-daily-report skill (Obsidian report dir, today's date). Clarify the
scope, method, and outputs with me before you begin.

Part 1 — code: the a-run JSON is the data source.
The single-seed runner `2_analysist/run_analysis_a_runs.py` `--extract` writes
`analysis_data.json` per run, but it currently holds only energies (absolute +
relative per atom), the best-so-far progression, and the PCA projection — it does
NOT hold the fingerprint/novelty information needed to measure novelty. Edit the
runner's `extract_json` (and keep `run_analysis_indices.py` consistent if the same
data is added there) so the JSON it writes ALSO records, per run, the fingerprint
novelty data required to compare difference / duplication / variety — e.g. distinct
vs. duplicate structure counts and/or pairwise fingerprint distances derived from
the loaded structures (the repo already exposes `is_distinct` and
`fingerprint_distance` via `novelty_lcb`, and `Fingerprint` is imported in the
runner). Bump the file's `__version__`, update `VERSIONS.md` (old→new), and record
in `LOG.md` per the AGENTS.md rules. Then re-run `--extract` for a1–a9 so each
`analysis_a_runs/analysis_data.json` carries the new fields. If producing these
fields needs more data than the loaded structures provide, tell me rather than
silently reaching elsewhere.

Part 2 — report (obsidian-daily-report, today's file): for the a1–a9 runs,
compare from the (now enriched) JSON:
- the number of data points each run retained (n_structures) and its iteration
  budget;
- the degree of novelty — difference / duplication / variety — of each run's
  explored set, grounded in the distinct/duplicate and/or fingerprint-distance
  numbers in the JSON.

State in the report exactly how each novelty metric is defined and computed, and
discuss what the comparison implies for each run. If the JSON or the runner's
current output is insufficient for any metric, say so in the report and flag what
extra data you'd need rather than guessing.
