# LOG — Project b_nestedsampling (append-only)

Curated, append-only record of agent actions. Append new entries; never rewrite or
delete prior ones. Per session: Goal (user-confirmed via clarify), Actions, Results,
Decisions & reasoning, Open items, Time.

---

## Session 2026-08-26 — Project creation & migration from `_run/8_nested_sampling`

**Goal (user-confirmed via clarify):** Create a new nested-sampling project dir at
`/home/think/Desktop/research/_run/b_nestedsampling`, structured like
`/home/think/Desktop/research/_run/a_lcbnovel` (README human+AI, LOG, TUTORIAL,
VERSIONS, AGENTS, PROMPTS, `.gitignore`, plus `_runs/`, `_analysist/`, `_archives/`,
`_tmp/`), and migrate the code/notes from `_run/8_nested_sampling`.

**Clarify decisions (all user-confirmed):**
1. Code scope: package (6 modules) + `run_nested_sampling.py` + dataset code + a
   CLEAN `scripts/` (dedupe `-Copy`/`_v0`/checkpoint cruft).
2. Dataset: copy the full `dataset/` dir including the (gitignored) seed DBs →
   self-contained.
3. `NESTED_SAMPLING_RUN.md` (786 lines): split into the README/LOG/TUTORIAL trio,
   drop the raw file.
4. Governance: add `AGENTS.md` + an empty `PROMPTS.md` scaffold.
5. Layout: scaffold `_runs/`, `_analysist/`, `_archives/`, `_tmp/`.
6. Scripts: keep only the 5 scripts `dataset/main.py` actually imports
   (`build_mgo_stack`, `build_fe_stack`, `build_heteroStruct`,
   `hetero_struct_randomize`, `plot_structure`).
7. `j_nestedsampling.sh` activates `gpaw_env` (standing HPC convention; AGOX caveat
   flagged in docs).

**Actions taken:**
- Loaded `ai-agent-project-workflow` + `agox-nested-sampling` skills; inspected
  both `8_nested_sampling` and the `a_lcbnovel` model layout.
- Scaffolded `b_nestedsampling/{nested_sampling,scripts,_runs,_analysist/{0_analy,1_result},_archives,_tmp}`.
- Copied the `nested_sampling/` package (6 modules), `run_nested_sampling.py`, the
  full `dataset/` (13 seed DBs verified), and the 5 clean scripts.
- Created `j_nestedsampling.sh` (bare PJM script; `gpaw_env`; `use_ray=False`
  params preserved from source `job.sh`).
- Added module-level `__version__ = "1.0.0"` to all 12 in-scope source files
  (left pre-existing function-local `0.0.1` in `scripts/*.py` untouched).
- Split `NESTED_SAMPLING_RUN.md` into `README.md` / `TUTORIAL.md` (+ LOG here),
  then **deleted the raw file** from the migrated copy.
- Wrote `README.md`, `README.AI.md`, `TUTORIAL.md`, `VERSIONS.md`, `AGENTS.md`,
  `PROMPTS.md`, `.gitignore`, `transcript.log`.

**Results / verification:**
- 13/13 seed DBs copied; package + runner + scripts in place.
- `__version__ = "1.0.0"` present in all 12 files (grep-verified).
- `py_compile` check of all in-scope source under `agox_v2` (see below).
- Source `_run/8_nested_sampling/` left **intact** (copy-only migration).

**Decisions & reasoning:**
- `gpaw_env` for the HPC job keeps the standing convention; the AGOX/agox_v2
  requirement is documented as a caveat in README.AI.md + TUTORIAL.md (matching the
  source notes' warning).
- `_archives/` added to `.gitignore` (archived artifacts are regenerable/reference).

**Open items:**
- No concrete `_runs/` run yet — scaffolded empty, ready for a future run.
- A full/smoke production run has **not** been re-executed in the new dir (only
  compile-check); the dataset + code are migrated, so a smoke run can confirm
  end-to-end.

**Time:** 2026-08-26 ~20:00–20:15 JST.

---

## Session 2026-08-26 (follow-up) — Smoke run of the migrated pipeline

**Goal (user-confirmed):** Run a tiny local smoke test of the migrated project to
confirm the pipeline works end-to-end in the new dir.

**Action:**
```
cd /home/think/Desktop/research/_run/b_nestedsampling
agox_v2 python run_nested_sampling.py --temp 300 --n-live 30 --n-iters 20 \
    --perturb 0.01 --perturb-symbols Fe --output /tmp/ns_smoke_bns --rng 42
```

**Result: SMOKE_EXIT=0 — full pipeline succeeded.**
- Loaded 1297-structure dataset, trained GPR, ran 20 iters / 30 live.
- Confirmed Fe-only perturbation ("Perturbing 25 atoms of symbol 'Fe'").
- `E_ref = -436.9093 eV`; `unphys: 0`; posterior 20 physical / 20 total.
- Evidence: Z = 2.08e-72 (log Z = -165.06) at only 20 iters (expected tiny).
- All outputs written: evidence_history.csv, final_live_energies.csv,
  log_evidence.csv, posterior_summary.csv, 20 posterior XSFs, and 5 analysis PNGs
  (training/posterior conf_space + Boltzmann probability + comparison density).
- Output (in /tmp, gitignored) verified present.

**Note:** a conda plugin error report appeared in the process stream during the
run, but it was non-fatal side-process noise — the Python pipeline exited 0 and
produced all outputs. (Pre-existing `use_ray=False` in `run_nested_sampling.py`
means the `ActorUnavailableError` class is structurally avoided.)

**Open items:** none for migration. Future concrete `_runs/` runs (e.g. the
literature-scale `--n-live 500 --n-iters 5000` and T-scan) still pending on HPC.

**Time:** 2026-08-26 ~20:17–20:20 JST.

---

## Session 2026-08-26 — Update job script to full-pipeline + sync notes with literature

**Goal (user-confirmed via clarify):** Edit `j_nestedsampling.sh` so it runs
`dataset/main.py` (the AGOX search) **then** `run_nested_sampling.py`, structured
like `a_lcbnovel/j_novel.sh`; keep the project notes/docs in sync, including a
literature-scale NS parameter note drawn from the wiki-research nested-sampling
papers.

**Clarify decisions (all user-confirmed):**
1. Keep `dataset/main.py` as-is (no CLI refactor); the job runs it directly.
2. Run ALL seeds 3..104 in one job, then nested sampling.
3. DBs written into `./dataset` (job `cd dataset` before `python ./main.py`, so
   `run_nested_sampling.py` finds `dataset/seed_*/1_db/db_*.db`).
4. NS params: keep current `--temp 300 --n-live 100 --n-iters 1000` **plus** a
   literature-scale note with multiple papers' parameters (from wiki-research).
5. Job PJM header: **24 cores** (`vnode-core=24 / mpi proc=24`), matching
   `dataset/main.py`'s `SubprocessGPAW(ncores=24)`.

**Actions taken:**
- Env check: locally **no `gpaw_env`** exists; `agox_v2` has AGOX 3.10.2 + ASE
  3.25.0 + GPAW. On HPC `gpaw_env` is the standing env (it generated the original
  dataset via `dataset/job_5x5_9.sh`).
- Rewrote `j_nestedsampling.sh` → full-pipeline job: 24-core PJM header,
  `conda activate gpaw_env`, `cd dataset && OMP_NUM_THREADS=1 python ./main.py`,
  `cd ..`, `OMP_NUM_THREADS=1 python ./run_nested_sampling.py --temp 300
  --n-live 100 --n-iters 1000 --perturb 0.01 --perturb-symbols Fe --output
  ./ns_output_T300_100_1000_0.01 --rng 42`. Bare style (echo only, no comment
  blocks).
- `TUTORIAL.md`: rewrote the "Heavy, supercomputer run" section to document the
  full-pipeline job (24 cores, env caveat); added a **"Literature-scale NS
  parameters"** table from wiki-research (`concepts/nested-sampling.md`,
  `raw/syntheses/nested-sampling_synthesis.md`): Pártay 2021 (K=500–5000,
  L=100s–1000s, 10⁵–10⁷ iters), Yang 2024 (80 walkers/free particle, 250
  iters/walker, 320 000 iters at full coverage), Chatbipho 2025 (LJ38
  nanocluster); recommended middle ground `--n-live 500 --n-iters 5000`.
- `README.md`: added "Job (HPC full pipeline)" section.
- `README.AI.md`: updated §3 HPC-launch entry to describe the full pipeline.

**Results / verification:**
- `j_nestedsampling.sh` written (24 cores, full pipeline).
- `main.py` and `run_nested_sampling.py` **untouched** → no version bumps
  (batch scripts not versioned; VERSIONS.md unchanged).
- Compile-check of `dataset/main.py` + `run_nested_sampling.py` under `agox_v2`
  (below).

**Decisions & reasoning:**
- Literature note lives in TUTORIAL.md, **not** in the `.sh` (standing rule: keep
  batch scripts bare). The `.sh` has a one-line echo pointing to TUTORIAL.md.
- Job keeps `gpaw_env` (HPC convention); the AGOX/agox_v2 caveat is documented in
  README.AI + TUTORIAL.

**Open items:**
- The HPC job itself is not run (all-seeds GPAW search is a heavy HPC job, not a
  local task). Locally only compile-checks were done.

**Time:** 2026-08-26 ~20:20–20:35 JST.

---

## Session 2026-08-26 — Rename root `run_nested_sampling.py` → `main.py`; job runs NS only

**Goal (user-confirmed via clarify):** The project root runner should be named
`main.py` (not `run_nested_sampling.py`), and `j_nestedsampling.sh` should run the
(named) `main.py` — **not** `dataset/main.py`. The AGOX search step is dropped from
the job; a note documents that it can be added back.

**Clarify decisions (all user-confirmed):**
1. Remove the `dataset/main.py` AGOX-search step from the job; the job runs ONLY
   `./main.py` (reads existing `dataset/seed_*/1_db/db_*.db`). Include a note that
   the search step could also be run.
2. Do NOT execute the job now — just update the file for HPC.
3. Keep the job activating `gpaw_env` (HPC convention), pointing to TUTORIAL for
   the run command.
4. The "optional search" note goes in **TUTORIAL.md only** (keeps the `.sh` bare).
5. Rename via `git mv` (preserves history) + update all references.

**Actions taken:**
- `git mv run_nested_sampling.py main.py` (no self-references broke on rename).
- Fixed the docstring usage line in `main.py` (`run_nested_sampling.py` → `main.py`);
  bumped `__version__` **1.0.0 → 1.0.1** (patch, docstring edit).
- Rewrote `j_nestedsampling.sh`: NS-only job (`python ./main.py --temp 300
  --n-live 100 --n-iters 1000 ... --output ./ns_output_T300_100_1000_0.01`),
  24-core header, `gpaw_env`, bare style.
- `VERSIONS.md`: row `run_nested_sampling.py 1.0.0` → `main.py 1.0.1`.
- `README.md`: usage/analyze commands → `main.py`; "Job (HPC — nested sampling
  only)" section (optional search noted, points to TUTORIAL); layout tree.
- `README.AI.md`: entry-point commands, `### main.py CLI`, HPC-launch comment,
  in-scope list, use_ray refs, provenance.
- `TUTORIAL.md`: mental model + all run commands → `main.py`; "Heavy, supercomputer
  run" section rewritten to NS-only job + added **"Optional: add the AGOX search
  step back"** subsection.
- `AGENTS.md`: `_runs/` layout + run-copy-sync text → `main.py`.
- **LOG.md: historical entries NOT edited** (append-only rule); this entry records
  the rename as a correction.

**Results / verification:**
- `main.py` present, `run_nested_sampling.py` gone (git-tracked rename).
- `main.py` `__version__ = "1.0.1"`; VERSIONS.md updated.
- No stale `run_nested_sampling` references remain in current-state docs (only
  intentional rename-provenance notes in README/README.AI).
- Compile-check of `main.py` under `agox_v2` (below).
- Job file updated for HPC; **not executed** (per decision).

**Open items:**
- HPC job not run (NS-only run is launchable via `pjsub j_nestedsampling.sh`).

**Time:** 2026-08-26 ~20:40–20:55 JST.

---

## Session 2026-08-26 — TUTORIAL.md: answer the `Q:` on "sample the PES once"

**Goal (user request):** Update `TUTORIAL.md` to include an answer to the `Q:` note
dropped into the "Discussion — parameters in the nested-sampling literature" section.

**The question:** "When you say they sample the PES once, does that mean they apply
for 0 K for their sampling based on the current code?"

**Action:** Wrote a code-grounded answer directly below the `Q:` (fixed the "tehy"
typo in the quoted question).

**Answer (summary):** **No.** In the papers (Pártay 2021 / Yang 2024), the NS
sampling is **temperature-independent** — β never appears in the algorithm; it is a
single top-down pass constrained only by a decreasing energy limit `U_limit`.
Temperature enters only in post-processing via `Z(β)=Σ w_i exp(−β E_i)`, so 0 K is
only the `T→0` post-processing extreme, not the sampling temperature. By contrast,
this project's `nested_sampling/nested_sampler.py` puts β **inside** the likelihood
(`log L = -beta*(E - E_ref)`, `beta = 1/(K_B*--temp)`), i.e. single-temperature NS
(default 300 K) with temperature-specific Z/posterior. Matching the papers would move
β into post-processing — the open modelling gap (also the wiki
`★[[nested-sampling-validation]]★` subject).

**Files changed:** `TUTORIAL.md` only (no code change → no version bump; VERSIONS.md
unchanged).

**Time:** 2026-08-26 ~20:55–21:00 JST.

---

## Session 2026-08-26 — Add temperature-free nested-sampling mode (consistent with papers/wiki)

**Goal (user-confirmed via clarify):** Edit the code so a **temperature-free**
nested-sampling mode is available, consistent with the papers (Pártay 2021 / Yang
2024) and the wiki (`nested-sampling` page): β kept OUT of the sampling likelihood,
with Z(β)/free-energy/posterior evaluated in post-processing at any temperature.

**Clarify decisions (all user-confirmed):**
1. **Opt-in** `--temperature-free` flag; the existing fixed-T (`--temp`) path stays
   the default (backward compatible).
2. `--temperatures` comma list (e.g. 100,200,300,500,1000): evaluate Z/F/posterior
   at each; write a per-T summary + `thermodynamics.csv`.
3. Full scope: `--temperature-free`, `--temperatures` in main.py; refactor
   `NestedSampler` to decouple β from sampling, store `(E_i, w_i)` per sample, add
   `evaluate(beta)` / `posterior_at(beta)`; write `samples.csv` (re-runnable).
4. Verify with a local smoke test in temperature-free mode.

**Actions taken:**
- `nested_sampling/nested_sampler.py` (1.0.0 → 1.1.0, minor): added
  `temperature_free` flag; `log_likelihood` returns β-free `-(E-E_ref)` when set;
  `step()` records `sample_energies` + `sample_prior_weights` (ΔX); new
  `evaluate(beta)` = `Σ w_i exp(−β E_i)` (+ final live term) and
  `posterior_at(beta)`; `run()`/`save()` branch for T-free mode (progress shows
  prior volume X; writes `samples.csv` + `final_live_energies.csv` instead of
  fixed-T evidence/posterior files).
- `main.py` (1.0.1 → 1.1.0, minor): added `--temperature-free` +
  `--temperatures`; temperature-free post-processing writes per-T
  `posterior_T{KKK}/posterior_summary.csv` + XSFs and `thermodynamics.csv`
  (T, β, logZ, Z, F=−k_B T ln Z).
- `smoke_test_temperature_free.py` (new, 1.0.0): unit test that `evaluate`/
  `posterior_at` match the paper formula + tiny end-to-end T-free run.
- Docs: README.md (usage + options), README.AI.md (CLI table), TUTORIAL.md
  (Step 8b), VERSIONS.md (main 1.1.0, nested_sampler 1.1.0, + smoke test).

**Results / verification (real output):**
- `py_compile` of main.py + nested_sampler.py under agox_v2: OK.
- `smoke_test_temperature_free.py`: **ALL PASSED** (SMOKE_EXIT=0).
  - Unit: logZ matches paper formula; posterior weights sum to 1.
  - End-to-end T-free run (n-live 10, n-iters 15): exit 0, wrote samples.csv,
    final_live_energies.csv, thermodynamics.csv, posterior_T{100,300,1000}/.
  - Physics check: T=100/300/1000 K → log Z = −27.2 / −11.6 / −6.1, F = +0.235 /
    +0.300 / +0.530 eV. Z grows and F becomes less negative as T rises (correct).
- Fixed-T path left unchanged (backward compatible).

**Open items:** none for the feature. HPC run of T-free mode not launched.

**Time:** 2026-08-26 ~21:00–21:10 JST.

---

## Session 2026-08-26 — Process PROMPTS.md (log prompt for GPR accuracy analysis)

**Goal (user-confirmed via clarify):** Process `/home/think/Desktop/research/_run/b_nestedsampling/PROMPTS.md` — assign the flag code, split the prompt into Original/Fixed grammar blocks, fold fixes into the Grammar notes. Do **not** build the GPR analysis code yet.

**The prompt (from PROMPTS.md, originally with an empty `# FLAG:`):** "Make a new
code for this project ... the kernel GPR accuracy analysis code ... extract the
performance of the GPR model under different energy range ... accuracy (use MAE,
RMSE, R^2) ... as a function of the energy range."

**Actions taken:**
- Assigned flag `20260826_2333` (local time when processed).
- Preserved the original verbatim (including the broken line-wraps) under
  `## Original (before grammar fix)`.
- Wrote `## Fixed grammar (after)`: repaired the split path
  (`/home/thin k/...` → `/home/think/Desktop/research/_run/b_nestedsampling/`),
  the split "It' s" → "It's", "under different energy range" → "under different
  energy ranges", and "(use MAE, RMSE, R^2)" → "(using MAE, RMSE, R^2)".
- Folded the fixes into the shared `## Grammar notes` as generalized concepts
  (broken machine-readable tokens/paths; incomplete clauses; non-idiomatic
  phrasing), matching AGENTS.md §3b.

**Result:** PROMPTS.md now contains a properly flagged, grammar-fixed entry for the
future GPR accuracy-vs-energy-range analysis task. **Code not built** (per user).

**Time:** 2026-08-26 ~23:33–23:36 JST.

---

## Session 2026-08-26 — Commit unexpected main.py docstring addition (T-free run example)

**Context:** While committing the PROMPTS.md processing, an **uncommitted edit to
`main.py`'s module docstring** was found in the working tree (not made by this
session's agent): it adds the temperature-free run command as a usage example.

**Decision (user-confirmed via clarify):** Keep the docstring addition and commit
it; bump `main.py` **1.1.0 → 1.1.1** (patch, doc-only) and sync VERSIONS/LOG.

**Actions taken:**
- `main.py`: kept the docstring example (temperature-free run); bumped
  `__version__` 1.1.0 → 1.1.1.
- `VERSIONS.md`: `main.py` row → 1.1.1.
- This LOG entry records the change (append-only).

**Time:** 2026-08-26 ~23:36–23:38 JST.

---

## Session 2026-08-26 — Build GPR accuracy-vs-energy-range analysis (`gpr_accuracy.py`)

**Goal (user-confirmed via clarify):** Create a new code that extracts the GPR
model's prediction accuracy (MAE, RMSE, R²) as a function of the energy range —
this is the task logged in PROMPTS.md (flag 20260826_2333).

**Clarify decisions (all user-confirmed):**
1. Energy range = energy above the minimum, in **eV/atom**, binned into equal-width
   windows (default bin width 0.1 eV/atom → ~7 bins over the ~0.675 eV/atom range).
2. Train one GPR on all 1297 structures; evaluate **in-sample** residuals per bin.
3. Self-contained `gpr_accuracy.py` at project root.
4. Outputs: per-bin CSV + matplotlib plot (MAE/RMSE/R² vs range) + printed table.

**Actions taken:**
- Wrote `gpr_accuracy.py` (new, 1.0.0): loads all seeds, trains GPR (same AGOX
  recipe as main.py), predicts in-sample energies, bins by dE/atom above min,
  computes MAE/RMSE/R² per bin + overall, writes CSV + plot.
- CLI: `--bin-width` (default 0.1), `--output` (default ./gpr_accuracy_out),
  `--use-ray`.
- Docs: VERSIONS.md (+gpr_accuracy.py), README.md (+usage section),
  TUTORIAL.md (Step 8c).

**Results / verification (real output):**
- `py_compile` under agox_v2: OK.
- Ran `gpr_accuracy.py --output ./_tmp/gpr_accuracy_out`: **ACC_EXIT=0**.
- 1297 structures, 7 bins (0–0.675 eV/atom), overall MAE=0.0007 RMSE=0.0010
  R²=1.0000 eV/atom. CSV + PNG written and verified.
- **Note:** in-sample errors are tiny (interpolation points) — reflects training
  fit, not out-of-sample generalization. Cross-validation not implemented.

**Open items:** cross-validation mode (out-of-sample) if the user wants a
generalization estimate.

**Time:** 2026-08-26 ~23:38–23:45 JST.

---

## Session 2026-08-26 — Add K-fold cross-validation to gpr_accuracy.py (fold training)

**Goal (user-confirmed via clarify):** Add fold training to `gpr_accuracy.py` so it
can report an out-of-sample (generalization) estimate of GPR accuracy vs energy
range.

**Clarify decisions (all user-confirmed):**
1. 5 folds default, overridable with `--cv-folds N`.
2. Opt-in `--cv` flag; in-sample remains the default.
3. Stratified by energy bin — each bin's structures split across folds so every
   fold trains on a spread of energy ranges.
4. Report per-bin metrics from POOLED held-out predictions across folds + a
   fold-averaged summary.

**Actions taken:**
- `gpr_accuracy.py` (1.0.0 → 1.1.0, minor): added `--cv` + `--cv-folds`; new
  `stratify_folds()` (stratified assignment by dE bin); main branches between
  in-sample and K-fold CV. CV trains one GPR per fold (on K-1/K), predicts the
  held-out 1/K, pools held-out errors per bin, writes `..._cv<K>folds.csv` +
  `cv_fold_summary_<K>folds.csv` (fold MAE + mean/std) + a `..._cv<K>folds.png`.
- Docs: VERSIONS.md (gpr_accuracy.py 1.1.0), README.md, TUTORIAL.md (Step 8c).

**Results / verification (real output):**
- `py_compile` under agox_v2: OK.
- Ran 5-fold CV: **CV_EXIT=0**. Per-fold MAE = 0.0039/0.0043/0.0038/0.0040/0.0040;
  fold-averaged overall MAE = 0.0040 ± 0.0002 eV/atom. Pooled overall MAE=0.0040
  RMSE=0.0067 R²=0.998 eV/atom.
- **Key finding:** error grows toward higher-energy bins — MAE=0.010, R²=0.58 at
  0.39–0.48 eV/atom (vs R²=0.96 near the minimum). The GPR generalizes worse at the
  energy extremes (fewer structures / more extrapolation). This is the truthful
  out-of-sample picture (in-sample MAE was only 0.0007).
- CSV + plot + fold summary written and verified.

**Open items:** none.

**Time:** 2026-08-26 ~23:45–23:55 JST.

---

## Session 2026-08-26 — Process new PROMPTS.md entry (uncertainty analysis)

**Context:** A new user prompt was found in PROMPTS.md with an empty `# FLAG:`:
"Include an uncertainty analysis, showing the uncertainty across the energy level."
Processed per AGENTS.md §3b.

**Actions taken:**
- Assigned flag `20260826_2354` (local time when processed).
- Split into `## Original` / `## Fixed grammar`; folded the fix (removed a
  redundant comma splitting verb from object: "analysis, showing" →
  "analysis showing"; "energy level" → "energy levels") into a new Grammar-note
  concept 4 (redundant/misplaced comma).
- Removed the now-redundant empty-flag stub.

**Time:** 2026-08-26 ~23:54–23:56 JST.

---

## Session 2026-08-26/27 — Add uncertainty analysis to gpr_accuracy.py (flag 20260826_2354)

**Goal (user-confirmed via clarify):** Add an uncertainty analysis to
`gpr_accuracy.py` showing the GPR's uncertainty across energy levels, with a graph
and CSV, behind a new run flag.

**Clarify decisions (all user-confirmed):**
1. Uncertainty = the GPR's own predictive std (from
   `predict_energy_and_uncertainty`), averaged per energy bin.
2. Opt-in `--uncertainty` flag.
3. Extend the existing graph with per-bin mean model-std error bars.
4. Separate `uncertainty_by_energy_range.csv` + add a `mean_model_std_eV_per_atom`
   column to the main accuracy CSV.

**Actions taken:**
- `gpr_accuracy.py` (1.1.0 → 1.2.0, minor): added `--uncertainty`; in-sample mode
  computes per-structure model std; CV mode collects the std of each held-out
  prediction and pools it; new `bin_mean_std()` helper; writes
  `uncertainty_by_energy_range.csv` + adds the std column to the accuracy CSV +
  per-bin 1σ error bars on the plot; prints overall mean model std.
- Docs: VERSIONS.md (1.2.0), README.md, TUTORIAL.md (Step 8c).

**Results / verification (real output):**
- `py_compile` under agox_v2: OK.
- In-sample `--uncertainty`: **UNC_EXIT=0**, overall mean model std = 0.0011
  eV/atom; accuracy CSV gained the std column; uncertainty CSV written; plot saved.
- CV `--cv 3 --uncertainty`: **CVUNC_EXIT=0**, overall mean model std = 0.0046
  eV/atom; std tracks the held-out error and rises at the energy extremes (std
  ~0.016–0.019 eV/atom where R² drops to ~0.5–0.2), i.e. the GPR is both less
  accurate AND more uncertain at the energy extremes.

**Time:** 2026-08-27 ~00:10–00:25 JST.

---

## Session 2026-08-27 — Process new PROMPTS.md entry (rattling-distance analysis)

**Context:** A new user prompt was found in PROMPTS.md with an empty `# FLAG:`:
"Include an analysis of different ratteling distances ... vs the GPR performance
(accuracy and uncertainty)." Processed per AGENTS.md §3b.

**Actions taken:**
- Assigned flag `20260827_0024` (local time when processed).
- Split into `## Original` / `## Fixed grammar` (fixed "ratteling"→"rattling",
  trailing dangling comma, restructured for clarity).
- Folded into Grammar notes as new concept 5 (misspelling / dangling punctuation).
- Removed the now-redundant empty-flag stub.

**Note:** this logs a future task (rattling-distance sensitivity vs GPR accuracy/
uncertainty). Not built yet.

**Time:** 2026-08-27 ~00:24–00:26 JST.

---

## Session 2026-08-27 — Write DISCUSSION.md for each _tmp result dir

**Goal (user-confirmed via clarify):** Write a full-depth DISCUSSION.md (skill format)
for each result directory under `_tmp/`.

**Clarify decisions (all user-confirmed):**
1. Filename `DISCUSSION.md` (conventional, not DISCUSSIONS).
2. One DISCUSSION.md per run-dir (summarizes that run's CSVs + PNG).
3. Full-depth (setup table, per-metric analysis, overall interpretation, caveats).
4. Written inside `_tmp/` (gitignored) → live with results, no commit needed.

**Actions taken:** Wrote 4 DISCUSSION.md files, each grounded in the real CSV numbers:
- `_tmp/gpr_accuracy_out/DISCUSSION.md` — in-sample: MAE≈0.0007, R²≈1.0, flat (fit-quality only).
- `_tmp/gpr_accuracy_cv_out/DISCUSSION.md` — 5-fold CV: MAE=0.0040 RMSE=0.0067 R²=0.998;
  error rises toward high energy (R² 0.96→0.58).
- `_tmp/gpr_acc_uncert_out/DISCUSSION.md` — in-sample + uncertainty: model std ≈0.0011,
  flat (interpolation statement; understates true error).
- `_tmp/gpr_acc_cv_uncert_out/DISCUSSION.md` — 3-fold CV + uncertainty: model std (0.0046)
  tracks held-out MAE (0.0044) and both peak at the high-energy extremes; good calibration.

**Note:** files are under gitignored `_tmp/`, so not committed (per decision).

**Time:** 2026-08-27 ~00:26–00:32 JST.

---

## Session 2026-08-27 — Process new PROMPTS.md entry (delta Fe_z / Fe island height analysis)

**Context:** A new user prompt was found in PROMPTS.md with an empty `# FLAG:`:
"Add an additional Analysist. I want to check the accuracy+uncertainty across
different delta Fe_z (… the Fe island height)." Processed per AGENTS.md §3b.

**Actions taken:**
- Assigned flag `20260827_0041` (local time when processed).
- Split into `## Original` / `## Fixed grammar`: fixed "Analysist"→"analysis",
  "Fe z axist"→"Fe z-axis", and reordered the delta Fe_z definition so
  "Fe island height" leads.
- Folded into Grammar notes as new concept 6 (terminology/clarity); extended
  concept 3 with the "Analysist"→"analysis" instance.
- Removed the now-redundant empty-flag stub.

**Note:** this logs a future task (accuracy + uncertainty vs delta Fe_z, the Fe
island height). Not built yet.

**Time:** 2026-08-27 ~00:41–00:43 JST.

---

## Session 2026-08-27 — Add delta Fe_z analysis to gpr_accuracy.py (flag 20260827_0041)

**Goal (user-confirmed via clarify):** Add a new flag to `gpr_accuracy.py` for an
analysis of accuracy + uncertainty across delta Fe_z (the Fe island height), plus a
DISCUSSION.md in the result dir.

**Clarify decisions (all user-confirmed):**
1. New opt-in `--fez` flag (own CSV + plot).
2. delta Fe_z = max(Fe z) − min(Fe z) in Å (island height), binned ~0.5 Å.
3. Works in in-sample AND --cv AND --uncertainty modes, reusing the same predictions.
4. Writes a DISCUSSION.md (benchmark-results-discussion format) into the output dir.

**Actions taken:**
- `gpr_accuracy.py` (1.2.0 → 1.3.0, minor): added `--fez`; new `fe_z_height()`
  and generic `bin_metrics_x()` helpers; Fe_z analysis block computes per-structure
  Fe island height, bins (0.5 Å), computes MAE/RMSE/R² (+ model std with
  `--uncertainty`), writes `gpr_accuracy_by_fe_z.csv` (+ `uncertainty_by_fe_z.csv`),
  a `gpr_accuracy_by_fe_z.png` plot, and a `DISCUSSION.md` via `_write_fe_z_discussion`.
- Docs: VERSIONS.md (1.3.0), README.md, TUTORIAL.md (Step 8c).

**Results / verification (real output):**
- `py_compile` under agox_v2: OK.
- Ran `gpr_accuracy.py --fez --uncertainty --output ./_tmp/gpr_acc_fez_out`:
  **FEZ_EXIT=0**. 12 bins over 0–5.57 Å; in-sample MAE 0.00016–0.00099 eV/atom,
  R²≈1.0, model std ~0.0010–0.0013 eV/atom. Wrote Fe_z accuracy CSV, uncertainty
  CSV, plot, and DISCUSSION.md (verified).
- Note: in-sample Fe_z errors are near-zero (interpolation) — CV mode gives the
  honest held-out picture.

**Time:** 2026-08-27 ~00:44–00:52 JST.

---

## Session 2026-08-27 — Run gpr_accuracy --fez with 3-fold CV

**Goal (user request):** Run the delta Fe_z analysis with 3-fold cross-validation
(combining `--cv --cv-folds 3 --fez --uncertainty`) for the honest held-out picture.

**Action:**
```
/home/think/miniconda3/envs/agox_v2/bin/python gpr_accuracy.py \
    --cv --cv-folds 3 --fez --uncertainty --output ./_tmp/gpr_acc_fez_cv3_out
```

**Result: FEZCV_EXIT=0.**
- Fold-averaged overall MAE = 0.0044 ± 0.0003 eV/atom; energy-range CV metrics as
  before (MAE=0.0044 RMSE=0.0087 R²=0.997).
- Fe_z (island height) CV results: MAE 0.0030–0.0083 eV/atom across 12 bins
  (0–5.57 Å); model std 0.0026–0.0117 eV/atom.
- **Key finding:** the GPR is most accurate for island heights ~2.3–3.7 Å
  (MAE ~0.0030–0.0041, R²~0.994–0.999) and least accurate for very flat islands
  (~0.5–1.4 Å, MAE up to 0.0083, model std up to 0.012). The model std tracks the
  error — well-calibrated.
- Wrote Fe_z accuracy CSV, uncertainty CSV, plot, and a DISCUSSION.md (mode
  "3-fold CV", grounded in the held-out numbers).
- Output dir: `_tmp/gpr_acc_fez_cv3_out/` (gitignored).

**Time:** 2026-08-27 ~00:53–00:59 JST.

---

## Session 2026-08-27 — Process new PROMPTS.md entry (include running script in DISCUSSION.md)

**Context:** A new user prompt was found in PROMPTS.md with an empty `# FLAG:`:
"For all the DISCUSSION.md, include the actual running script that it used."
Processed per AGENTS.md §3b.

**Actions taken:**
- Assigned flag `20260827_0059` (local time when processed).
- Split into `## Original` / `## Fixed grammar` (added "files", fixed the dangling
  pronoun "it" → "them", "produced them").
- Folded into Grammar notes as new concept 7 (missing noun / dangling pronoun).
- Removed the now-redundant empty-flag stub.

**Note:** this logs a future task — update all DISCUSSION.md files (in `_tmp/`)
to include the actual running script/command that produced each. Not yet applied.

**Time:** 2026-08-27 ~00:59–01:02 JST.

---

## Session 2026-08-27 — Consolidate PROMPTS.md into a single shared Grammar notes section

**Goal (user request):** Fix PROMPTS.md so it does not create multiple `## Grammar
notes` tags — there should be exactly ONE shared Grammar notes section (generalized
concepts from all flags), per AGENTS.md §3b.

**Action (user-confirmed via clarify):** Rewrote PROMPTS.md to:
- Keep exactly ONE `## Grammar notes` section, placed at the top after the intro,
  holding the 7 deduplicated generalized concepts (formatting/machine-readable,
  incomplete clauses, non-idiomatic phrasing, misplaced comma, misspelling/dangling
  punctuation, terminology/clarity, missing noun/dangling pronoun).
- Reduce each flag entry to only its `## Original` + `## Fixed grammar` blocks
  (removed the per-flag duplicate Grammar notes blocks).
- Keep all 5 flags in descending order (newest 20260827_0059 at top → oldest
  20260826_2333 at bottom).

**Result / verification:** `grep -c "^## Grammar notes"` = 1; all 5 flags present.

**Time:** 2026-08-27 ~01:02–01:05 JST.

---

## Session 2026-08-27 — Add the actual running script to all DISCUSSION.md (flag 20260827_0059)

**Goal (user-confirmed via clarify):** For all DISCUSSION.md under `_tmp/`, include
the actual running script (exact command line) that produced each run.

**Clarify decisions (all user-confirmed):**
1. Full exact command line (python gpr_accuracy.py + all flags + --output), in a
   dedicated `## Running script` section.
2. Apply to all 6 DISCUSSION.md files.

**Action:** Added a `## Running script` section (with the exact producing command,
run from the project root) before `## What was run` in each of:
- `_tmp/gpr_accuracy_out/DISCUSSION.md` (in-sample)
- `_tmp/gpr_accuracy_cv_out/DISCUSSION.md` (--cv --cv-folds 5)
- `_tmp/gpr_acc_uncert_out/DISCUSSION.md` (--uncertainty)
- `_tmp/gpr_acc_cv_uncert_out/DISCUSSION.md` (--cv 3 --uncertainty)
- `_tmp/gpr_acc_fez_out/DISCUSSION.md` (--fez --uncertainty)
- `_tmp/gpr_acc_fez_cv3_out/DISCUSSION.md` (--cv 3 --fez --uncertainty)

**Result / verification:** `grep -c "^## Running script"` = 1 in all 6 files.

**Note:** files are under gitignored `_tmp/` (not committed).

**Time:** 2026-08-27 ~01:05–01:10 JST.

---

## Session 2026-08-27 — Add rattling-distance sensitivity analysis to gpr_accuracy.py (flag 20260827_0024)

**Goal (user-confirmed via clarify):** Add an analysis of different rattling
distances vs GPR performance (accuracy and uncertainty): take DB structures, rattle
them under different ranges, predict their energy — to check how much rattling the
kernel can handle. Include a way to choose which atoms to rattle.

**Clarify decisions (all user-confirmed):**
1. New opt-in `--rattle` flag (own CSV + plot + DISCUSSION.md).
2. `--rattle-dist` comma-separated amplitudes (default 0.05,0.1,0.2,0.5,1.0 Å).
3. `--rattle-symbols` flag (default Fe) to choose which atoms to rattle.
4. Sample a fixed number of DB structures (default 200, `--rattle-n`), several
   rattled copies each (`--rattle-copies`, default 5), pool errors per amplitude.
5. In-sample mode only (train one GPR on all 1297, rattle+predict).

**Actions taken:**
- `gpr_accuracy.py` (1.3.0 → 1.4.0, minor): added `--rattle`, `--rattle-dist`,
  `--rattle-symbols`, `--rattle-n`, `--rattle-copies`; new `rattle_structure()`
  helper (Gaussian displacement of selected atoms); rattling block trains one GPR,
  rattles the sample per amplitude, computes MAE/RMSE/R² (+ model std with
  `--uncertainty`), writes `gpr_accuracy_by_rattle.csv`
  (+ `uncertainty_by_rattle.csv`), a plot, and a `DISCUSSION.md`.
- **Physical filter:** rattled predictions with |E|>1e4 eV (unphysical off-manifold
  extrapolation) are excluded and counted (`n_unphysical` column) — matches the
  documented `--perturb` pitfall.
- Docs: VERSIONS.md (1.4.0), README.md, TUTORIAL.md (Step 8c).

**Results / verification (real output):**
- `py_compile` under agox_v2: OK.
- Ran `--rattle --uncertainty --rattle-n 100 --rattle-copies 3` (fast verify):
  **RATTLE_EXIT=0**.
  - 0.05 Å: MAE 0.0083 (0 unphys); 0.10 Å: MAE 0.034 (0); 0.20 Å: MAE 0.30 (1 unphys);
    0.50 Å: MAE 20.2 (214/300 unphys); 1.00 Å: MAE 94.0 (296/300 unphys).
  - Model std grows: 0.0019 → 0.0045 → 0.0156 → 0.0772 → 0.1246 eV/atom.
- **Key finding:** the GPR kernel tolerates small rattling (~0.05–0.1 Å) with mild
  degradation, but degrades catastrophically beyond ~0.2 Å as rattled structures
  leave the training manifold (many unphysical extrapolations). This quantifies the
  safe perturbation scale for nested sampling.
- CSV + plot + DISCUSSION.md written and verified.

**Note:** The PROMPTS.md flag 20260827_0024 Fixed-grammar block was updated (an
external edit expanded the prompt with "rattle them under different range",
"Fe only rattled / choose which atoms", "how much the kernel can handle"). The
expanded requirements match what was implemented (--rattle-symbols, --rattle-dist,
etc.). Fixed-grammar cleaned accordingly.

**Time:** 2026-08-27 ~01:10–01:30 JST.

---

## Session 2026-08-27 — Incorporate NESTED_SAMPLING_RUN.md content into README.md

**Goal (user-confirmed via clarify):** Incorporate the content from
`_run/8_nested_sampling/NESTED_SAMPLING_RUN.md` (786-line notes) into
`_run/b_nestedsampling/README.md`.

**Clarify decisions (all user-confirmed):**
1. **Synthesize** (not verbatim append) — fold the content into new README sections,
   cleaned to match the README's concise style, avoiding duplication with TUTORIAL.md.
2. Include both the physics/concept Q&As AND the operational sections (state-density
   analysis, Ray fix, heavy run, literature discussion).

**Actions taken:** Added two new README sections before "Layout":
- **"Concepts & physics"** — what posterior structures are (discarded worst-live
  samples, weighted by prior-volume share); what `n_live`/`beta`/`temperature` do
  (incl. T=300 K → beta≈38.68 eV⁻¹, the stat-mech identification); what "final
  evidence" `Z` is and why `log Z` (overflow/underflow, log-space accumulation); what
  "feature dim 720" means (180 radial + 540 angular for 3 species).
- **"Operational notes"** — state-density/landscape analysis; the Ray
  `ActorUnavailableError` fix (`use_ray=False`); and a literature-scale table
  (Pártay/Yang/Chatbipho vs this project) with the modelling-gap note.

**Result:** README.md now carries the conceptual+operational depth from the notes while
keeping its concise style and pointing to TUTORIAL.md for run reproduction.

**Time:** 2026-08-27 ~01:30–01:40 JST.

---

## Session 2026-08-27 — Add physics of temperature-free mode to README.md

**Goal (user-confirmed via clarify):** Document the physics of the temperature-free
mode (an existing code option) in the README.

**Clarify decisions (all user-confirmed):**
1. Add a dedicated **"Physics of temperature-free mode"** section (after the existing
   temperature-free usage section).
2. Full depth: Boltzmann weight, partition function as a sum over states, density of
   states, free-energy/heat-capacity derivation, and why it matches Pártay/Yang.

**Actions taken:** Added the section to README.md, grounded in the actual code
(`NestedSampler.log_likelihood` = `-(E - E_ref)` in T-free mode; `evaluate(β)` =
`Σ w_i exp(-β(E_i - E_ref))` + live correction):
- Canonical partition function `Z(β) = Σ e^{-βE} = ∫ Ω(E) e^{-βE} dE` with density of
  states Ω(E); F = −k_B T ln Z, ⟨E⟩, C_V from derivatives of ln Z.
- Why sample temperature-free: NS is inherently temperature-independent (top-down,
  energy-constrained); β weights results only afterwards; one run stores (E_i, w_i)
  and yields Z(T)/F(T)/C_V(T)/posterior at all T.
- Contrast with fixed-T mode (β in likelihood → single-temperature run).
- thermodynamics.csv columns (T, β, logZ, Z, F); C_V → heat-capacity peaks → phase
  transitions.

**Result:** README now explains the physics behind the temperature-free option,
code-grounded and consistent with Pártay 2021 / Yang 2024.

**Time:** 2026-08-27 ~01:40–01:48 JST.

---

## Session 2026-08-27 — Fix --perturb-symbols to support multiple symbols

**Context (user question):** Does `--perturb-symbols` support multiple atoms (e.g.
Fe and B at the same time)? **Answer before fix: NO** — the code passed the string
verbatim into `np.isin(symbols, [perturb_symbols])`, so `"Fe,B"` matched a literal
"Fe,B" element (zero matches → ValueError). The help text said "Symbol(s)" but didn't
split. User confirmed fix.

**Clarify decisions (all user-confirmed):**
1. Fix to support multiple symbols, split on comma.
2. Split on comma AND trim whitespace (both `Fe,B` and `Fe, B` work).

**Actions taken:**
- `nested_sampling/nested_sampler.py` (1.1.0 → 1.2.0, minor): parse `perturb_symbols`
  into a list `[s.strip() for s in str(perturb_symbols).split(",") if s.strip()]`
  and use `np.isin(symbols, perturb_list)`; error/print updated to "any symbol
  {list}".
- `main.py` (1.1.1 → 1.1.2, patch): help text now documents comma-separated multiple
  symbols (e.g. `Fe,B` / `Fe, B`).
- Docs: VERSIONS.md, README.md (option), README.AI.md (CLI table).

**Results / verification (real output):**
- `py_compile` under agox_v2: OK.
- Parsing test: `Fe`→['Fe'], `Fe,B`→['Fe','B'], `Fe, B`→['Fe','B'], `Mg,Fe,O`→all.
- Runtime check on seed DB (Fe25Mg25O25): `Fe,B` matches 25 Fe atoms (B=0 in this
  non-B-doped seed); `B` alone matches 0 → correct.

**Note:** on a B-doped dataset, `--perturb-symbols Fe,B` will perturb Fe AND B atoms
together. This is the use case that motivated the fix.

**Time:** 2026-08-27 ~01:48–01:58 JST.

---

## Session 2026-08-27 — Update TUTORIAL.md for multi-symbol --perturb-symbols

**Context:** Follow-up to the `--perturb-symbols` multi-symbol fix. User asked to
also update TUTORIAL.md.

**Actions taken:** Updated TUTORIAL.md:
- **Step 6 (Internals — prior/sample_from_prior):** now states `--perturb-symbols`
  accepts comma-separated multiple symbols (e.g. `Fe,B` / `Fe, B`) to move Fe and B
  together; other atoms (Mg/O) stay fixed.
- **Step 9 (Tuning checklist):** "Stay on the deposition layer" bullet now notes a
  comma list (e.g. `Fe,B`) can include B.

**Time:** 2026-08-27 ~01:58–02:02 JST.

---

## Session 2026-08-27 — Create HPC run dir b1_gpr_accuracy_cv10_bin005

**Goal (user-confirmed via clarify):** Create a self-contained run dir under
`_runs/` for `gpr_accuracy.py` with bigger parameters (higher CV, lower bin),
covering the two reference systems (`gpr_acc_cv_uncert_out` = energy-range CV+uncert,
`gpr_acc_fez_cv3_out` = fez CV+uncert), with all deps for independent HPC running.

**Clarify decisions (all user-confirmed):**
1. One run dir covering BOTH systems (energy-range CV+uncertainty AND fez
   CV+uncertainty) in a single job/script.
2. Params: `--cv-folds 10` (vs 3), `--bin-width 0.05` (vs 0.1).
3. Copy the full dataset/ dir (13 seed DBs, ~23 MB, gitignored) → self-contained.
4. Include per-run README.md + TUTORIAL.md.
5. Run dir name: `b1_gpr_accuracy_cv10_bin005`.

**Actions taken:**
- Created `_runs/b1_gpr_accuracy_cv10_bin005/`; copied latest `gpr_accuracy.py`
  (v1.4.0) + full `dataset/` (13 DBs).
- Wrote `j_gpr_accuracy_cv10_bin005.sh` (bare PJM script, 24 cores, `gpaw_env`)
  that runs both invocations:
  - `--cv --cv-folds 10 --uncertainty --bin-width 0.05 --output ./out_energy_range`
  - `--cv --cv-folds 10 --fez --uncertainty --bin-width 0.05 --output ./out_fez`
- Wrote per-run `README.md` + `TUTORIAL.md`.

**Results / verification:**
- `gpr_accuracy.py` (v1.4.0) compiles under agox_v2; `sh -n` OK.
- 13 dataset DBs present.
- git dry-run: only code + docs tracked (35 files); seed `.db` excluded.

**Note:** 10-fold CV = ~10 GPR trainings per invocation (slower than 3-fold ref).
Run not executed locally (HPC job). Outputs land in `out_energy_range/` + `out_fez/`.

**Time:** 2026-08-27 ~02:30–02:40 JST.

---

## Session 2026-08-27 — Update run b1_gpr_accuracy_cv10_bin005: j_b1.sh, fez-only, cv 50

**Goal (user-confirmed via clarify):** Edit the run dir so the job script is renamed
`j_b1.sh`, and it runs ONLY the fez system with `--fez --uncertainty --bin-width 0.1
--cv-folds 50`.

**Clarify decisions (all user-confirmed):**
1. Keep dir name `b1_gpr_accuracy_cv10_bin005` (note the name no longer matches the
   cv50/bin01 spec).
2. Job runs ONLY the fez system (drop the energy-range invocation).
3. `--cv-folds 50` (50 GPR trainings, ~1271 train/~26 test per fold — slow, HPC).
4. Keep dataset/ + gpr_accuracy.py; update docs.

**Actions taken:**
- Renamed job script `j_gpr_accuracy_cv10_bin005.sh` → `j_b1.sh` (git mv).
- Rewrote `j_b1.sh`: single invocation
  `--cv --cv-folds 50 --fez --uncertainty --bin-width 0.1 --output ./out_fez`.
- Rewrote README.md + TUTORIAL.md to the new spec (fez-only, cv 50, bin 0.1, j_b1.sh).

**Results / verification:**
- `sh -n j_b1.sh`: OK.
- gpr_accuracy.py has no cap on --cv-folds; `stratify_folds` with 50 folds on the
  1297 set: all 50 folds used, 23–29 test structures each, none empty → valid.

**Time:** 2026-08-27 ~02:40–02:50 JST.

---

## Session 2026-08-27 — Create HPC run dir b2_boron_ns (nested sampling, B-doped)

**Goal (user-confirmed via clarify):** Create a new `_runs/` dir running the same NS
parameters as `_analysist/1_result/1_no_prior_control` but on the B-doped dataset
(`dataset_boron`), with B included in the perturb.

**Clarify decisions (all user-confirmed):**
1. Modern root runner `main.py` (latest, multi-symbol `--perturb-symbols Fe,B`) with
   same NS params as reference: `--temp 300 --n-live 100 --n-iters 1000 --perturb
   0.01 --output ./ns_output_T300_100_1000_0.01 --rng 42`.
2. `--perturb-symbols Fe,B` (Fe AND B both perturbed).
3. NS pipeline only (main.py on dataset_boron).
4. Run dir name: `b2_boron_ns`.
5. Copy `dataset_boron/` into the run as `dataset/` (main.py reads ./dataset).

**Actions taken:**
- Created `_runs/b2_boron_ns/`; copied latest `main.py` (v1.1.2) + `nested_sampling/`
  package (6 modules) + `dataset_boron/` → `dataset/` (5 B-doped seeds).
- Wrote `j_b2_boron_ns.sh` (bare PJM, 64 cores, gpaw_env) running the NS pipeline with
  `--perturb-symbols Fe,B`.
- Wrote per-run `README.md` + `TUTORIAL.md`.

**Results / verification:**
- main.py + nested_sampling/ compile under agox_v2; `sh -n` OK.
- Dataset: 496 structures total (5 seeds), composition Fe25Mg25O25B7; `Fe,B` perturb
  matches 32 atoms (25 Fe + 7 B) — verified.
- git dry-run: code + docs tracked; `.db` seed files excluded.

**Note:** some boron seeds contain high-energy structures; the |E|<1e4 filter handles
gross outliers. Not executed locally (HPC job).

**Time:** 2026-08-27 ~02:50–03:00 JST.

---

## Session 2026-08-27 — Create HPC run dir b3_gpr_accuracy_boron_cv50

**Goal (user-confirmed via clarify):** Create a new `_runs/` dir for `gpr_accuracy.py`
on the **boron system**, using the same parameters as `_runs/b1_gpr_accuracy_cv10_bin005`.

**Clarify decisions (all user-confirmed):**
1. Same command as b1: `--cv --cv-folds 50 --fez --uncertainty --bin-width 0.1`
   (fez-only), on the B-doped dataset.
2. Run dir name: `b3_gpr_accuracy_boron_cv50`.
3. Deps: latest `gpr_accuracy.py` (v1.4.0) + `dataset_boron/`→`dataset/` +
   `j_b3_*.sh` + README/TUTORIAL, self-contained.

**Actions taken:**
- Created `_runs/b3_gpr_accuracy_boron_cv50/`; copied `gpr_accuracy.py` (v1.4.0) +
  `dataset_boron/` → `dataset/` (5 B-doped seeds).
- Wrote `j_b3_gpr_accuracy_boron_cv50.sh` (bare PJM, 24 cores, gpaw_env) running the
  fez CV-50 invocation.
- Wrote per-run `README.md` + `TUTORIAL.md`.

**Results / verification:**
- `gpr_accuracy.py` (v1.4.0) compiles under agox_v2; `sh -n` OK.
- Dataset: 496 structures, Fe25Mg25O25B7 (82 atoms), E/atom −5.87..−0.23. Note the
  descriptor dim will differ from the plain 720 (B adds species/bond types).
- git dry-run: code + docs tracked; `.db`/`.png` excluded.

**Note:** 50-fold CV = 50 GPR trainings (slow, HPC). Some boron seeds have high-energy
outliers (|E|<1e4 filter handles). Not executed locally.

**Time:** 2026-08-27 ~03:00–03:08 JST.

---

## Session 2026-08-27 — Fix b2_boron_ns: missing scripts/ (plot_structure_landscape)

**Context (user-reported HPC error):** `b2_boron_ns` failed at import with
`ModuleNotFoundError: No module named 'scripts'` — `nested_sampling/state_density.py`
(line 49) does `from scripts.plot_structure_landscape import plot_structure_landscape`,
but the run dir had no `scripts/` module. This was an oversight when the run was
created (only main.py + nested_sampling/ + dataset were copied).

**Root cause (confirmed):** `state_density.py` inserts its own dir (`<run>/nested_sampling/`)
into `sys.path`, so `scripts.plot_structure_landscape` resolves from
`<run>/nested_sampling/scripts/plot_structure_landscape.py`. The project-root
`nested_sampling/` has no `scripts/`; the reference (`1_no_prior_control`) had
`nested_sampling/scripts/plot_structure_landscape.py`.

**Clarify decisions (all user-confirmed):**
1. Copy `plot_structure_landscape.py` into `b2_boron_ns/nested_sampling/scripts/`
   (minimal, matches reference layout).
2. Apply to b2; also document the required treatment in the notes (NS run-dir creation
   must include this).

**Actions taken:**
- Created `b2_boron_ns/nested_sampling/scripts/` and copied
  `dataset_boron/scripts/plot_structure_landscape.py` into it.
- Verified: import resolves (`IMPORT OK`); full `nested_sampling` package (incl.
  state_density) imports cleanly from the run dir → the error is fixed.
- Added a **Pitfall** to `b2_boron_ns/TUTORIAL.md` (scripts module required when
  creating NS run dirs).
- Added a governing note to project-root `AGENTS.md` (§3a run dirs): NS run dirs must
  include `nested_sampling/scripts/plot_structure_landscape.py`.

**Time:** 2026-08-27 ~12:21–12:26 JST.

---

## Session 2026-08-27 — Fix b3_gpr_accuracy_boron_cv50 run error

**Context (user-reported HPC error):** `b3_gpr_accuracy_boron_cv50` crashed at the
plot with `ValueError: 'yerr' (shape: (57,)) ... shape matches 'y' (shape: (22,))`,
and the printed metrics were unphysical (~10⁹ eV/atom, R² ~ −10²⁰). The user asked to
explain why and fix it, saving the explanation in the run's README.md.

**Root causes (confirmed):**
1. **Empty-bin length mismatch bug:** `bin_mean_std()` returned one value per grid bin
   (empty → NaN), but `rows`/`centers`/`mae` from `bin_metrics()` skip empty bins.
   The boron data (bins spanning 0–5.6 eV/atom, many empty) triggered a length
   mismatch → `errorbar` crash.
2. **High-energy outliers break the GPR fit:** seeds 2-4 contain structures with
   E/atom up to −0.23 eV (dE above min ≈ 5.6 eV/atom vs ~0.67 for plain Fe/MgO). The
   GPR could not fit such a wide landscape (even in-sample predictions were
   −7140..+6296 eV), and CV held-out predictions were almost all unphysical → empty
   pooled errors → crash.

**Clarify decisions (all user-confirmed):**
1. Fix `bin_mean_std` to skip empty bins (aligned with rows).
2. Keep both code fixes; add `|E|<1e4` physical filter to prediction loops.
3. Add `--e-max-per-atom <eV/atom>` flag (in-place outlier exclusion, controllable).
4. b3 uses `--e-max-per-atom -5.2` (452 structures, spread ~0.67 eV/atom, matching the
   working Fe/MgO set).
5. Also write a DISCUSSION.md in the b3 run output.

**Actions taken (`gpr_accuracy.py` 1.4.0 → 1.5.0):**
- `bin_mean_std()` now skips empty bins (fixes the errorbar crash).
- Added `|E|<1e4` physical filter to CV + in-sample prediction loops (exclude/count
  unphysical predictions).
- Added `--e-max-per-atom` flag (drops structures with E/atom above threshold before
  training AND eval, both CV and in-sample).
- Re-copied fixed `gpr_accuracy.py` (v1.5.0) into b3 and b1 run dirs.
- Updated `j_b3_gpr_accuracy_boron_cv50.sh` to `--e-max-per-atom -5.2`.
- Wrote the **error explanation** into `b3/README.md`, a `b3/DISCUSSION.md`, updated
  `b3/TUTORIAL.md`, project-root README.md (+ `--e-max-per-atom` doc), VERSIONS.md.

**Results / verification (real output):**
- In-sample on the -5.2-cut set: predictions −481.7..−426.9 eV (physical), 0
  |E|>1e4, MAE 0.0002 eV/atom → GPR fits.
- 5-fold CV smoke with `-5.2`: **B3_SMOKE4_EXIT=0**; fold-averaged MAE = 0.0086 ±
  0.0006 eV/atom, overall MAE=0.0086 / RMSE=0.0118 / R²=0.996, model std 0.0083,
  Fe_z + energy-range CSVs/plots + DISCUSSION written. Physical, meaningful results.

**Time:** 2026-08-27 ~13:00–13:26 JST.

---

## Session 2026-08-27 — Make --e-max-per-atom a RELATIVE energy above dataset minimum

**Goal (user-confirmed via clarify):** Change `--e-max-per-atom` from an absolute
E/atom cutoff to a **relative** energy above the lowest energy in the dataset.

**Clarify decisions (all user-confirmed):**
1. New semantics: keep structures with `(E/atom − min E/atom) ≤ threshold` (eV/atom).
   Positive values drop high-energy outliers above `threshold` eV/atom above min.
2. b3 uses `--e-max-per-atom 0.67` (relative; matches the working Fe/MgO spread).
   The old `-5.2` absolute value is invalid under the new semantics.

**Actions taken (`gpr_accuracy.py` 1.5.0 → 1.5.1, patch):**
- Updated the `--e-max-per-atom` help text to document the relative semantics.
- Changed the filter logic: `rel_e = e_per_atom - e_per_atom.min(); keep = rel_e <=
  args.e_max_per_atom`; print includes the dataset min E/atom.
- Re-copied `gpr_accuracy.py` (v1.5.1) into b3 + b1 run dirs.
- Updated `j_b3_gpr_accuracy_boron_cv50.sh` to `--e-max-per-atom 0.67`.
- Synced b3 README/TUTORIAL/DISCUSSION + project README + VERSIONS.md.

**Results / verification (real output):**
- Relative `0.67` keeps the same 452 structures (abs cutoff −5.205 ≈ old −5.2) — verified.
- 5-fold CV smoke with `0.67`: **B3_SMOKE5_EXIT=0**; "dropped 44 high-energy
  structures (E/atom - min > 0.67); 452 remain"; fold-averaged MAE 0.0086 ± 0.0006
  eV/atom, overall MAE=0.0086 / RMSE=0.0118 / R²=0.996, all CSVs/plots written.

**Time:** 2026-08-27 ~13:30–13:38 JST.

---

## Session 2026-08-27 — Process PROMPTS.md: grammar-fix the --e-max-per-atom NS prompt

**Context:** A new user prompt was found in PROMPTS.md with an empty `# FLAG:` — about
adding `--e-max-per-atom` (relative to lowest energy) to the nested-sampling codes.
Processed per AGENTS.md §3b.

**Actions taken:**
- Assigned flag `20260827_1638` (local time when processed).
- Split into `## Original` (verbatim, incl. broken line-wraps) / `## Fixed grammar`:
  repaired the split "nested\n_sampling" → "nested-sampling", "relat\nive" →
  "relative", "limit dataset" → "limit the dataset", "gpr" → "GPR", and cleaned the
  phrasing.
- Folded the fixes into the single shared `## Grammar notes` (concepts 1, 6, 7).
- Removed the now-redundant empty-flag stub.

**Result / verification:** exactly 1 `## Grammar notes` section; all 6 flags in
descending order; no empty-flag stub.

**Note:** this logs a future task — add `--e-max-per-atom` (relative) to the
nested-sampling codes (limit the dataset / GPR training data / initial structures).
Not built yet.

**Time:** 2026-08-27 ~16:38–16:44 JST.

---

## Session 2026-08-27 — Add --e-max-per-atom (relative) to nested-sampling codes (flag 20260827_1638)

**Goal (user-confirmed via clarify):** Update the nested-sampling codes to include
`--e-max-per-atom` (relative to the lowest energy), mirroring `gpr_accuracy.py`. It
limits the dataset used for nested sampling, the GPR training data, and the initial
structures for the nested sampling.

**Clarify decisions (all user-confirmed):**
1. A single `--e-max-per-atom` flag in `main.py`, applied once after loading, which
   limits all three at once (NS dataset, GPR training, initial sampler structures).
2. Semantics = RELATIVE to the dataset minimum (keep `E/atom − min E/atom ≤ value`),
   same as `gpr_accuracy.py`; positive values drop high-energy outliers (e.g. 0.67).
3. Add to `main.py` (runner) + the `--analyze-only` path for consistency; no explicit
   threading into NestedSampler (it reads the filtered `db_structures`).
4. Smoke-test on the boron dataset with `--e-max-per-atom 0.67`.

**Actions taken (`main.py` 1.1.2 → 1.2.0, minor):**
- Added `--e-max-per-atom` arg + help.
- Added filter after loading (step 1b): keep `rel_e <= e_max_per_atom`, drop the rest;
  this precedes `build_gpr(structures)` and `NestedSampler(db_structures=structures)`
  so all three are limited. Empty-set guard.
- Applied the same filter in the `--analyze-only` path.
- Copied updated `main.py` (v1.2.0) into `b2_boron_ns` run dir.
- Synced README.md (Options), TUTORIAL.md (Step 6), VERSIONS.md, LOG.md.

**Results / verification (real output, boron dataset, --e-max-per-atom 0.67):**
- `Total: 496 structures` → `dropped 44 high-energy structures; 452 remain`.
- GPR trained on the 452 filtered structures; `[NestedSampler] Perturbing 32 atoms of
  symbol(s) ['Fe', 'B']`; sampling completed (`SMOKE_EXIT=0`), outputs written
  (evidence_history.csv, posterior_structures/, etc.). Confirms all three limits.

**Time:** 2026-08-27 ~16:46–16:50 JST.

---

## Session 2026-08-27 — Update b2_boron_ns run to include --e-max-per-atom 0.67

**Goal (user request):** Update the `b2_boron_ns` run code to include
`--e-max-per-atom 0.67`.

**Actions taken:**
- `main.py` in the run dir was already v1.2.0 (with `--e-max-per-atom` support).
- Added `--e-max-per-atom 0.67` to `j_b2_boron_ns.sh` (the NS invocation).
- Updated `b2/README.md` + `b2/TUTORIAL.md` commands to include the flag, with a note
  that it keeps structures within 0.67 eV/atom of the dataset minimum (452/496).

**Verification:** `sh -n j_b2_boron_ns.sh` OK; run `main.py` v1.2.0 confirms
`--e-max-per-atom` present. (The `--e-max-per-atom` feature itself was verified in
the previous session on the boron dataset: 496 → 452 remain, sampling completes.)

**Time:** 2026-08-27 ~16:50–16:55 JST.

---

## Session 2026-08-27 — Create HPC run dir b3_tfree_emax025 (temp-free NS, plain Fe/MgO)

**Goal (user-confirmed via clarify):** New `_runs/` dir using the same system as
`_analysist/1_result/1_no_prior_control` (plain Fe/MgO, no B), but in **temperature-free
mode** with **`--e-max-per-atom 0.25`**.

**Clarify decisions (all user-confirmed):**
1. Run dir name: `b3_tfree_emax025`.
2. Temperature-free mode: `--temperature-free --temperatures 100,200,300,500,1000`
   (default list); same NS params as reference (`--n-live 100 --n-iters 1000
   --perturb 0.01 --perturb-symbols Fe --rng 42`).
3. Dataset: plain Fe/MgO (13 seeds, project-root `dataset/` copied as `dataset/`).
4. `--e-max-per-atom 0.25` (relative to dataset min) in the job.

**Actions taken:**
- Created `_runs/b3_tfree_emax025/`; copied `main.py` (v1.2.0) + `nested_sampling/`
  package + `dataset/` (13 Fe/MgO seeds) + required
  `nested_sampling/scripts/plot_structure_landscape.py`.
- Wrote `j_b3_tfree_emax025.sh` (bare PJM, 64 cores, gpaw_env) running the
  temperature-free invocation with `--e-max-per-atom 0.25`.
- Wrote per-run `README.md` + `TUTORIAL.md`.

**Results / verification (real output):**
- Compile OK (main.py + package); `sh -n` OK; package imports (scripts module present).
- Dataset: 1297 structures, 0.675 eV/atom span; `--e-max-per-atom 0.25` keeps 971,
  drops 326 — verified.
- Local smoke (T-free, 200/300 K, n-live 20/n-iters 30): `SMOKE_EXIT=0`; dropped 326,
  971 remain; GPR trained; Z ↑ and F less negative with T (T=200: Z=1.6e-16, F=0.627;
  T=300: Z=6.6e-12, F=0.665); thermodynamics.csv + per-T posterior written.
- git dry-run: code + docs tracked (29 files); `.db`/`.png` excluded.

**Note:** 0.25 eV/atom cut on the ~0.675 span keeps the lowest-energy band (971/1297),
focusing GPR + sampling on low-energy structures. Not executed on HPC yet.

**Time:** 2026-08-27 ~17:17–17:24 JST.

---

## Session 2026-08-27 — Rename run dir b3_tfree_emax025 -> b4_tfree_emax025

**Goal (user request):** Rename the run dir `_runs/b3_tfree_emax025` to
`b4_tfree_emax025` (change b3 to b4).

**Actions taken:**
- `git mv b3_tfree_emax025 b4_tfree_emax025` (history preserved).
- `git mv j_b3_tfree_emax025.sh j_b4_tfree_emax025.sh`.
- Updated all internal references (README.md, TUTORIAL.md, job script): `b3_` →
  `b4_`, `j_b3_` → `j_b4_`.

**Verification:** no stale `b3_tfree_emax025`/`j_b3` refs remain; `sh -n` on the
renamed job script OK; git detects the rename.

**Time:** 2026-08-27 ~17:25–17:28 JST.

---

## Session 2026-08-27 — Update current state (new b5 run + _analysist)

**Context:** The user added a new `_runs/b5_boron_ns_emax025` and new `_analysist`
entries. Asked to "update the current state".

**Clarify decisions (all user-confirmed):**
1. Fix the b5 run docs (they were stale copies of b2_boron_ns: said 'b2_boron_ns',
   'j_b2_boron_ns.sh', '--e-max-per-atom 0.67') to match b5 / j_b5 / 0.25.
2. Copy the b5 run into `_analysist/1_result/` (mirroring b1/b3 copies).
3. Commit the b5 run dir (tracked).

**Actions taken:**
- Rewrote `_runs/b5_boron_ns_emax025/README.md` + `TUTORIAL.md`: b5_boron_ns_emax025,
  `j_b5_boron_ns.sh`, `--e-max-per-atom 0.25` (relative), noted as a tighter cut than
  b2's 0.67. Job script already used 0.25.
- Copied b5 into `_analysist/1_result/b5_boron_ns_emax025/` (gitignored).

**Results / verification (real output):**
- Compile OK (main.py + package); `sh -n` OK; required scripts module present; 5 boron
  DBs.
- Filter: 496 -> 181 keep / 315 drop with `--e-max-per-atom 0.25` (tighter than b2's 452).
- No stale b2/0.67 refs remain (only intentional comparative mentions).

**Note:** `_analysist/1_result/` is gitignored (b1/b3/b5 copies not committed); only
the b5 run dir under `_runs/` is tracked and committed.

**Time:** 2026-08-27 ~17:29–17:35 JST.

---

## Session 2026-08-27 — Switch b5_boron_ns_emax025 to temperature-free mode

**Goal (user-confirmed via clarify):** Edit the b5 run to use **temperature-free mode**
(replace `--temp 300` with `--temperature-free --temperatures 100,200,300,500,1000`),
keeping everything else (B-doped, `--perturb-symbols Fe,B`, `--e-max-per-atom 0.25`,
same NS params). Also update docs + output dir name.

**Actions taken:**
- `j_b5_boron_ns.sh`: switched to temperature-free, output `./ns_output_tfree_emax025`.
- `README.md` + `TUTORIAL.md`: documented temperature-free mode + new output dir +
  per-T outputs (`thermodynamics.csv`, `posterior_T*`).
- Synced the `_analysist/1_result/b5_boron_ns_emax025/` copy.

**Results / verification (real output, local smoke T-free 200/300 K, small params):**
- `SMOKE_EXIT=0`; `--e-max-per-atom 0.25` dropped 315, 181 remain; GPR trained;
  `[Perturbing 32 atoms of ['Fe','B']]`; Z ↑ / F less negative with T (T=200: Z=6.7e-19,
  F=0.721; T=300: Z=2.3e-13, F=0.752); thermodynamics.csv + per-T posterior written.
- `sh -n j_b5_boron_ns.sh` OK.

**Time:** 2026-08-27 ~17:36–17:42 JST.

---

## Session 2026-08-27 — Rename _analysist b5 copy to b5_boron_tfree_emax025

**Goal (user request):** Rename `_analysist/1_result/b5_boron_ns_emax025` to
`b5_boron_tfree_emax025`.

**Context:** The b5 `_analysist` copy had been moved into
`_analysist/1_result/_archives/b5_boron_ns_emax025` (a new `_archives` subdir, part of
the user's reorganization). Clarify timed out; defaulted to renaming in place under
`_archives`.

**Actions taken:**
- `mv _analysist/1_result/_archives/b5_boron_ns_emax025 b5_boron_tfree_emax025`.
- Updated the archive's README.md/TUTORIAL.md titles to `b5_boron_tfree_emax025`.

**Notes:**
- `_analysist/` is gitignored → no commit needed for this filesystem rename.
- The `_runs/b5_boron_ns_emax025` source run dir is a separate tracked dir and keeps
  its original name (only the archive copy was renamed per the request).

**Time:** 2026-08-27 ~17:46–17:52 JST.

---

## Session 2026-08-27 — Rename source run _runs/b5_boron_ns_emax025 -> b5_boron_tfree_emax025

**Context / correction:** The user clarified their intent: the dir to edit/rename is the
**source** `_runs/b5_boron_ns_emax025` (already temperature-free from last session), NOT
the `_analysist` archive. They confirmed renaming the source run to `b5_boron_tfree_emax025`
to match the tfree mode.

**Actions taken:**
- `git mv _runs/b5_boron_ns_emax025 b5_boron_tfree_emax025`.
- Updated README.md/TUTORIAL.md internal refs to `b5_boron_tfree_emax025`.

**Verification:** no stale `b5_boron_ns_emax025` refs in README/TUTORIAL; `sh -n` on
`j_b5_boron_ns.sh` OK (job script filename unchanged, dir renamed); git detects the
rename.

**Note:** This is tracked in git (unlike the gitignored `_analysist` archive). The
earlier rename of the `_analysist` archive copy stands.

**Time:** 2026-08-27 ~17:54–17:58 JST.

---

## Session 2026-08-27 — Fix b4_tfree_emax025 landscape-analysis error (plot_structure_landscape 's')

**Context (user-reported HPC error):** `b4_tfree_emax025` crashed at the final
state-density/landscape analysis with
`TypeError: plot_structure_landscape() got an unexpected keyword argument 's'`
(`state_density.py:130`, in `make_landscape`). User asked to explain the error in the
run's README.md and fix it.

**Root cause (confirmed):** version mismatch — the run's `nested_sampling/scripts/
plot_structure_landscape.py` (copied from stale `dataset_boron/scripts/`) lacks the
`s=` argument, but the current `state_density.py` calls
`plot_structure_landscape(..., s=5, ...)`. The nested sampling itself completed
successfully (thermodynamics.csv written); only the optional landscape plotting crashed.

**Clarify decision (user-confirmed):** Fix ONLY b4_tfree_emax025.

**Actions taken:**
- Copied the correct `plot_structure_landscape.py` (accepts `s=25`) from the reference
  `_analysist/1_result/1_no_prior_control/nested_sampling/scripts/` into
  `b4/nested_sampling/scripts/`.
- Documented the error + fix in `b4/README.md` ("Error explanation & fix").
- Updated `b4/TUTORIAL.md` pitfall (correct source for plot_structure_landscape).

**Verification (real output):** corrected version accepts `s=` (default 25) and ALL
kwargs `state_density.py` passes (no missing); compiles. The crash is resolved.

**Time:** 2026-08-27 ~18:05–18:13 JST.

---

## Session 2026-08-27 — Fix b5_boron_tfree_emax025 (same plot_structure_landscape 's' error)

**Context:** b5 has the same stale `plot_structure_landscape.py` (from
`dataset_boron/scripts/`, no `s=` arg) as b4, which would crash the final
state-density/landscape analysis with
`TypeError: plot_structure_landscape() got an unexpected keyword argument 's'`.

**Actions taken:**
- Copied the correct `plot_structure_landscape.py` (accepts `s=25`) from the reference
  `_analysist/1_result/1_no_prior_control/nested_sampling/scripts/` into
  `b5_boron_tfree_emax025/nested_sampling/scripts/`.
- Documented the error + fix in `b5/README.md` ("Error explanation & fix") + updated
  `b5/TUTORIAL.md` pitfall (correct source for plot_structure_landscape).

**Verification (real output):** b5 corrected version accepts `s=` (default 25) and all
kwargs `state_density.py` passes (none missing); compiles. Crash resolved.

**Time:** 2026-08-27 ~20:40–20:45 JST.

---

## Session 2026-08-27 — Prevent recurrence: document correct plot_structure_landscape source

**Goal (user-confirmed via clarify):** Update the governing docs so the
`plot_structure_landscape.py` `s=` error never recurs when creating a new NS run.

**Root cause of recurrence:** AGENTS.md §3a listed `dataset_boron/scripts/` as a valid
source for `plot_structure_landscape.py`, but that copy is STALE (lacks the `s=`
argument) and crashes the landscape analysis (the b4/b5 `TypeError`).

**Clarify decision (user-confirmed):** Update AGENTS.md + README.AI.md only (do NOT
change the stale `dataset_boron` copy).

**Actions taken:**
- `AGENTS.md` §3a: rewrote the "NS run dirs: required scripts module" note to
  **"required scripts module + correct version"** — states the reference
  `_analysist/1_result/1_no_prior_control/nested_sampling/scripts/` is the ONLY valid
  source (accepts `s=`), and explicitly warns **DO NOT use** the STALE
  `dataset_boron/scripts/` version (lacks `s=`, causes the `TypeError`).
- `README.AI.md` §2a: added the same reference-ONLY guidance to the `_runs/` run-dir
  bullet.

**Verification:** AGENTS.md now lists `dataset_boron/scripts` only as "DO NOT use";
README.AI.md references the reference-only source.

**Time:** 2026-08-27 ~20:46–20:50 JST.

---

## Session 2026-08-27 — Fix b2_boron_ns (same plot_structure_landscape 's' error)

**Context:** b2 has the same stale `plot_structure_landscape.py` (from
`dataset_boron/scripts/`, no `s=` arg) as b4/b5, which would crash the final
state-density/landscape analysis with
`TypeError: plot_structure_landscape() got an unexpected keyword argument 's'`.

**Actions taken:**
- Copied the correct `plot_structure_landscape.py` (accepts `s=25`) from the reference
  `_analysist/1_result/1_no_prior_control/nested_sampling/scripts/` into
  `b2_boron_ns/nested_sampling/scripts/`.
- Documented the error + fix in `b2/README.md` ("Error explanation & fix") + updated
  `b2/TUTORIAL.md` pitfall (correct source for plot_structure_landscape).

**Verification (real output):** b2 corrected version accepts `s=` (default 25) and all
kwargs `state_density.py` passes (none missing); compiles. Crash resolved.

**Time:** 2026-08-27 ~20:48–20:52 JST.

---

## Session 2026-08-27 — Update dataset_boron/scripts/plot_structure_landscape.py

**Context:** The `dataset_boron/scripts/plot_structure_landscape.py` was the stale
version (no `s=` arg) that caused the b4/b5/b2 `TypeError` when copied into NS run
dirs. The user asked to update it so the trap is removed at the source.

**Action taken:**
- Replaced `dataset_boron/scripts/plot_structure_landscape.py` with the correct
  reference version (accepts `s=25`) from
  `_analysist/1_result/1_no_prior_control/nested_sampling/scripts/`.

**Verification (real output):** updated version accepts `s=` (default 25) and all
kwargs `state_density.py` passes (none missing); compiles. Any future copy from
`dataset_boron/scripts/` is now correct.

**Time:** 2026-08-27 ~20:51–20:54 JST.

---

## Session 2026-08-27 — Answer the notes added to README.md in detail

**Goal (user-confirmed via clarify):** Answer the conceptual notes the user added to
README.md inline, in place, preserving the questions.

**Notes answered (two Notes blocks):**
1. In "What it does": log L / evidence / why log-space / accumulation; beta / E and
   why −E_ref / what E_ref is.
2. In the "central output" paragraph: what model evidence is / what they did; where the
   Z result comes from / how to plot it / what log Z is needed for.

**Approach:** answered each question as inline expository text under each Notes block,
keeping the original questions, consistent with the README's conceptual style and
grounded in the actual code (NestedSampler, np.logaddexp, evidence_history.csv,
thermodynamics.csv, evaluate()).

**Time:** 2026-08-27 ~20:56–21:02 JST.

---

## Session 2026-08-27 — Remove the Notes: flags from README.md

**Goal (user request):** Remove the `Notes:` header lines now that the answers are
inline.

**Action taken:** removed both `Notes:` markers in README.md (the two conceptual-answer
blocks now stand on their own without the Notes: flag).

**Verification:** no `^Notes:` lines remain.

**Time:** 2026-08-27 ~21:02–21:05 JST.


---

## Session 2026-08-27 — Answer the 12 remaining Notes blocks in README.md and remove all flags

**Goal (user request):** Update README.md: read the notes, answer each in place, then
remove the `Notes:` flag lines. Use the wiki (wiki-research) for grounding where relevant.

**Notes answered (12 blocks), each as inline expository text in the README's conceptual style:**
1. `beta` / why `log L` sometimes has no `beta` (temp-free vs fixed-T).
2. posterior, its normalization constant, `pi` (prior), `x` (configuration).
3. "geometrically", `exp(-1/K)`, prior/prior volume, "slice x likelihood", `K=n_live`.
4. "thermodynamic knob" / "in the likelihood".
5. why `L=1` at `E-E_ref=0`; "shifts the likelihood", O(1), "at the optimum".
6. where `Z` lives in the data; configurational state density `g(E)`; temp-dependent
   flat-vs-island probability; how papers use NS results / what analysis they do.
7. free energy `F=-k_B T ln Z`; weight and its relation to `Z`; how the NestedSampler builds `Z`.
8. papers' convergence criteria for `Z`.
9. how to make the new `Z`-vs-`T` / `F`-vs-`T` plot (standalone snippet given in README).
10. heat capacity, how it is computed here, why it matters.
11. how NS decides what to sample; `w_i`; `n_live`; the top-down step mechanics; initial
    structures; the DB remains the sampling pool for the whole run.
12. fixed-T vs temperature-free equations; why `beta` can be dropped; what each represents.

**Grounding:** code read (`nested_sampling/nested_sampler.py` step()/evaluate()/
sample_constrained()/sample_from_prior(), `main.py` post-processing, `state_density.py`)
+ wiki-research concept pages `nested-sampling` and `state-density-g-e` (island 0.074 /
flat 0.255 eV-atom peaks, papers' phase-diagram / heat-capacity analysis).

**Verification:** all 12 `Notes:` markers removed (grep 0 matches); anchors/blank lines
intact; README grew 476 -> 631 lines.

**Time:** 2026-08-27 ~21:xx JST.


---

## Session 2026-08-27 — Add scripts/plot_thermodynamics.py (Z/logZ/F vs T + optional Cv)

**Goal (user-confirmed via clarify):** make the new plot for analysing thermodynamics.csv.
Clarified: (1) standalone script at project root `scripts/`; (2) scope = Z, log Z, F vs T
panels + optional heat-capacity C_V(T); (3) validation = generate a small synthetic
thermodynamics.csv and run the script against it (no real temperature-free run output exists
yet — thermodynamics.csv is only produced by a `--temperature-free` NS run, and none of the
`_runs/*` dirs have run output on disk).

**Actions taken:**
- Created `scripts/plot_thermodynamics.py` (v1.0.0): reads `thermodynamics.csv`
  (T,beta,logZ,Z,F per row), draws Z / log Z / F = -k_B T ln Z vs T in one figure; `--cv`
  adds a C_V(T) panel via `C_V = k_B*beta^2*d^2(ln Z)/d(beta)^2` (numpy.gradient, needs >=3
  points). CLI: `--input/--output/--cv/--cv-output`. numpy+matplotlib only (no AGOX), Agg
  headless-safe.
- Fixed two syntax errors flagged by lint (generator expression unpacked into multiple
  targets -> list comprehension), lines 72 and 94.
- Generated `_tmp/demo_thermodynamics.csv` (synthetic, clearly demo) and ran the script:
  both `_tmp/demo_Z_F.png` (3600x1200) and `_tmp/demo_Cv.png` (1800x1200) produced; also
  verified the non-`--cv` path (`_tmp/demo_Z_F_only.png`). All valid PNG images.
- Updated README.md: replaced the "no dedicated Z vs T plot" text, replaced the inline
  snippet with a pointer to the committed script, and added a
  "## Usage (thermodynamics plot)" section.

**Verification (real output):** script ran against the demo CSV and produced valid PNGs
(file(1): PNG image data, correct dimensions). Lint clean.

**Open item:** script is validated on synthetic data; run it against a real
temperature-free run's `thermodynamics.csv` once such a run has completed (or submit
`--temperature-free` run on HPC).

**Time:** 2026-08-27 ~23:10-23:15 JST.


---

## Session 2026-08-27 — README: document where thermodynamics.csv comes from

**Goal (user request):** add to README.md where the `thermodynamics.csv` file comes from.

**Action taken:** added a "**Where does `thermodynamics.csv` come from?**" note inside the
"## Usage (thermodynamics plot)" section: it is produced ONLY by a `--temperature-free` run,
written to the run's `--output` dir by the temperature-free post-processing step (one row per
`--temperatures` value via `sampler.evaluate(beta)`); fixed-T mode instead writes
`evidence_history.csv`/`log_evidence.csv`; included the exact command to generate it and a
note that none currently exists in the repo / `_runs/*`.

**Verification:** README updated; no `^Notes:` flags (none added).

**Time:** 2026-08-27 ~23:20 JST.


---

## Session 2026-08-27 — README: answer the 6 new Notes blocks + add Fortran toy-model section

**Goal (user request):** edit README.md to (1) answer the "To Do" notes and (2) explain
`_tmp/nested_sampling_windowed_fixed.f` in a separate section. Clarified before acting
(per standing rule): the "To Do Tag" = the 6 new uncommitted `Notes:` blocks (answer inline +
remove flags); Fortran = explain-only, NO compile/run (gfortran not installed); placement = a
dedicated top-level section near "Physics of temperature-free mode", conceptual + per-routine
mapping, moderate depth.

**Actions taken:**
- Answered the 6 `Notes:` blocks inline (unnormalized posterior; probability distribution /
  P=L·pi/Z / what NS "density" means / state density from CSV; prior weight pi + empirical
  distribution + DB-dense-at-island prior + prior-volume weight vs pi; geometric series;
  pi-as-probability + higher-energy prior (0.25 eV/atom) + surviving fraction; shrinkage rate),
  each grounded in the code and given worked examples. Removed all 6 `Notes:` flags.
- Added a top-level section "## Nested sampling in 1D (Fortran toy model)" after "Physics of
  temperature-free mode": describes the 1D asymmetric double-well model (island/flat/barrier),
  the "windowed" X_0=1 past-the-barrier design choice, a routine-by-routine mapping table to the
  Python NestedSampler, and how each README concept (prior volume X=(K/(K+1))^i, temperature-free
  mode, density of states g(E)=dX/dE, convergence) appears in the toy. Noted it is gitignored
  _tmp scratch (illustrative, not a deliverable).

**Verification:** 0 `Notes:` flags remain; new section renders between the physics and GPR-accuracy
sections; README grew to 820 lines.

**Time:** 2026-08-27 ~23:35-23:45 JST.


---

## Session 2026-08-27 — README: answer the E_max Notes block in the Fortran section

**Goal (user request):** answer the new `Notes:` block the user added inside the "Nested sampling
in 1D (Fortran toy model)" section ("On the python codes, how does the E_max is first define? ...").

**Clarified (per standing rule):** treat the Python-vs-Fortran difference honestly — Python has
no explicit E_max.

**Answer written (flag removed):** explained that the Python `NestedSampler` does NOT define an
explicit upper E_max like the Fortran's E_barrier+margin. It instead has: E_ref = db_energies.min()
(lower reference, shifts log L = -(E - E_ref)); an implicit prior window set by the DB's own energy
range (sample_from_prior = uniform DB resample + perturb, no barrier-relative margin); a dynamic
running cutoff log_L_boundary (=> E_boundary = E_ref - log_L_boundary, updated each iteration);
and a 1e4 eV physical sanity filter (unphysical GPR guard, not an E_max). Contrasted with the
Fortran "windowed" design and the earlier higher-energy-prior note; gave a tank-drain analogy
for no-basis readers.

**Verification:** 0 `Notes:` flags remain; answer renders in the Fortran section.

**Time:** 2026-08-27 ~23:50 JST.


---

## Session 2026-08-27 — README: answer the E_max/main-loop Notes block in the Fortran section

**Goal (user request):** answer the new `Notes:` block inside the Fortran toy-model section
("Nested sampling works by first find the E_max and slowly lower it, based on the Fortran code
main loop; in the python code, how does it operate? ...").

**Clarified (per standing rule):** answer fully by walking initialize() -> step() -> updating
log_L_boundary (the running energy cutoff), contrasted with Fortran's fixed E_max +
(K/(K+1))^i shrink, with example + no-basis analogy, building on the prior E_max answer.

**Answer written (flag removed):** explained the Python loop lowers the energy window
DYNAMICALLY (running E_boundary = E_ref - log_L_boundary, set at line 183/265), not via a fixed
E_max. Walked: initialize() draws n_live prior samples, sets first cutoff to worst live point;
step() finds argmin(live_log_L), records delta_X = exp(-i/K)-exp(-(i+1)/K), replaces worst via
sample_constrained() (log L > log_L_boundary, |E|<1e4), then updates log_L_boundary = live_log_L.min()
so the window creeps downward each iteration. Contrasted with Fortran (fixed E_max, known
(K/(K+1))^i ratio). Gave a concrete numeric example (E_ref=-437 eV, boundary descending -420 ->
-421 -> -422 ...) and a net/water-level no-basis analogy.

**Verification:** 0 `Notes:` flags remain; answer renders in the Fortran section.

**Time:** 2026-08-28 ~00:00 JST.


---

## Session 2026-08-28 — README: answer 5-part Notes block + correct prior Fortran-vs-Python claim

**Goal (user request):** answer the new `Notes:` block in the Fortran toy-model section
(5 questions on the energy cutoff / E_max / E_ref / log_L_boundary / E_boundary / max_E).

**Clarified (per standing rule):** (1) correct the misleading prior README statement AND answer
all 5 questions grounded in code; (2) structure as one inline block replacing the Notes flag.

**Answer written (flag removed), 5 parts:**
1. "cutoff at the current worst live point" = log_L_boundary = live_log_L.min() (line 265).
2. Fortran correction: E_max is set once and used ONLY to seed initial walkers (rejection
   sampling); the in-loop energy cutoff is dead_E(iter)=worst-walker energy (line 82, dynamic);
   X_i=(K/(K+1))^i is the prior-VOLUME weight for Z/g(E), NOT the cutoff. Python mirrors this
   (log_L_boundary dynamic; dX=exp(-i/K)-exp(-(i+1)/K) is the volume weight). Same to leading order.
3. max_E is an ABSOLUTE eV filter, not relative eV/atom; setting it to 0.25 would reject all real
   structures (|E|~437); the relative filter is the --e-max-per-atom CLI flag; lowest-energy
   variable is E_ref (db_energies.min(), line 99).
4. E_ref (energy origin, min training energy), log_L_boundary (log-L cutoff = worst live point),
   E_boundary (derived = E_ref - log_L_boundary, printed line 185), how each is computed/used.
5. Yes - Fortran also re-computes the cutoff each step (dead_E = worst walker).

**Also corrected prior misleading text (3 spots):** the section previously said Fortran "sets a
fixed E_max once and shrinks by X_i=(K/(K+1))^i" and that only Python is "data-driven"; corrected
to state both codes re-derive the energy cutoff from the worst live point each step, and X_i is
the volume weight, not the cutoff (E_max is only the initial-walker seeding).

**Verification:** 0 `Notes:` flags remain; corrections applied; README grew to ~990 lines.

**Time:** 2026-08-28 ~00:10 JST.


---

## Session 2026-08-28 — README: answer relative-max_E + initial-energy-window Notes block

**Goal (user request):** answer the new `Notes:` block in the Fortran toy-model section
(2 questions: can max_E be a relative eV/atom-above-min filter?; can we set an initial energy
window, e.g. sample from 0.25 eV/atom above the global minimum?).

**Clarified (per standing rule):** answer conceptually in the README grounded in code; do NOT
modify code.

**Answer written (flag removed), 2 parts:**
Q1: Yes feasible, and partly already present as `--e-max-per-atom` (relative eV/atom filter on the
DB before training). The internal max_E (1e4) is an ABSOLUTE sanity guard against unphysical GPR
extrapolation, not a relative window selector — re-purposing it would wrongly drop physical
structures. A runtime relative max_E could be added as a small change.
Q2: Yes — the Fortran "windowed" idea. Upper bound via `--e-max-per-atom 0.25` (caps the prior);
lower bound needs a new `--e-min-per-atom` flag (doesn't exist). Nuance: NS auto-starts at the top
of whatever window you give it, so setting only the upper bound makes it start ~0.25 and descend to
0; to exclude the ground state you need the lower bound. Noted the code works in absolute eV, not
eV/atom (E_ref ~ -437 eV; relative per-atom = (E-E_ref)/N).

**Verification:** 0 `Notes:` flags remain; answer renders at the Fortran section.

**Time:** 2026-08-28 ~00:20 JST.


---

## Session 2026-08-28 — README: answer forced-start-at-top Notes block

**Goal (user request):** answer the new `Notes:` block in the Fortran toy-model section (how to
force NS to START from 0.25 eV/atom above the global minimum regardless of the initial uniform-DB
draw).

**Clarified (per standing rule):** explain conceptually in the README only (no code change);
focus on the "force the start at exactly the top" behavior including its trade-off.

**Answer written (flag removed):** explained that initialize() draws initial live points with
sample_from_prior() = uniform DB draw + noise with NO energy condition, so the initial boundary
lands low (DB is dense near ground state). To force the start at the top, add a rejection condition
inside initialize()'s draw loop so every initial live point satisfies rel=(E-E_ref)/N >= e_min
(0.25); gave pseudo-code. Weighed the trade-off: (1) live set may be unfillable if the DB lacks
high-energy structures (Fortran's continuous potential always fills; a finite DB may not); (2) it
discards the low-energy data and can lose low-basin weight; (3) the <=/> boundary choice matters;
(4) cleaner alternative: use only --e-max-per-atom 0.25 and let NS auto-start at the top of that
window (no rejection loop). Recommended --e-max-per-atom for the top + an optional --e-min-per-atom
guard with a warning.

**Verification:** 0 `Notes:` flags remain; answer renders at the Fortran section.

**Time:** 2026-08-28 ~00:30 JST.


---

## Session 2026-08-28 — README: answer worst-at-0.25-keep-lower Notes block

**Goal (user request):** answer the new `Notes:` block correcting the previous note: the user
does NOT want to throw away lower-than-0.25 structures; they want the initial live set's WORST
point at 0.25 eV/atom while KEEPING the lower-than-0.25 structures as initial live points.

**Clarified (per standing rule):** cap the prior pool at <=0.25 via --e-max-per-atom 0.25 so the
worst live point is AT MOST 0.25 (typically ~0.25), keeping all lower structures, no
rejection/discarding.

**Answer written (flag removed):** explained this is the "upper-window-only" case needing no
rejection. `--e-max-per-atom 0.25` keeps all structures with rel<=0.25 (low-energy down to the
minimum AND the near-0.25 ones); initialize() draws the K initial live points uniformly from that
pool, so the worst (=initial E_boundary, log_L_boundary=live_log_L.min(), line 183) is at most
0.25 and typically ~0.25, while the rest of the live set spans downward. Recipe = one flag,
--e-max-per-atom 0.25. Caveat: exact 0.25 depends on whether the DB has a structure at that
energy; if pinning exactly to the pool top is required, seed one live point at the top structure.

**Verification:** 0 `Notes:` flags remain; answer renders at the Fortran section.

**Time:** 2026-08-28 ~00:40 JST.


---

## Session 2026-08-28 — README: answer guarantee-worst-in-band Notes block

**Goal (user request):** answer the new `Notes:` block: the user wants to GUARANTEE the initial
live set's worst point lands around 0.25±0.01 (not accidentally way below, e.g. 0.1), while
keeping lower-than-0.25 structures.

**Clarified (per standing rule):** frame it as seeding/ensuring at least ONE initial live point in
the 0.24-0.26 band (and none above 0.25), so the worst is pinned to ~0.25 while all other live
points stay wherever they land.

**Answer written (flag removed):** explained the worst = max of K uniform draws, so it can land
well below 0.25. Fix: inside initialize(), seed ONE live point drawn from the [0.24,0.26] band
(intersected with pool <=0.25); the <=0.25 cap makes the worst never exceed 0.25, and the seeded
band point makes it at least ~0.24, pinning initial E_boundary in-band; all other live points span
downward (nothing discarded). Gave pseudo-code (seed one band point, then draw remaining K-1
uniformly). Edge cases: band may be empty (relax or error); <=0.26/>=0.24 boundary; effective band
is [0.24,0.25] since pool capped at 0.25; determinism (draw band point first under same --rng).

**Verification:** 0 `Notes:` flags remain; answer renders at the Fortran section.

**Time:** 2026-08-28 ~00:50 JST.


---

## Session 2026-08-28 — README: assess anchor-structure Notes block

**Goal (user request):** answer the new `Notes:` block proposing a cleaner design instead of the
while-True band seeding: as a flag, immediately pick the DB structure closest to the 0.25±0.01
window as one initial live point, then fill the rest with uniform random capped at window max
(0.25). Asks "What about this?"

**Clarified (per standing rule):** assess their proposal in the README (no code change); present
the worst-pinning as guaranteed within the DB's resolution, including the sparse-band caveat.

**Answer written (flag removed):** endorsed the design as cleaner + deterministic (3 reasons: no
rejection loop / always terminates; anchor = argmin |rel-0.25| pins the worst to the closest-to-
0.25 structure (and <=0.25 cap keeps it from being higher); keeps everything below, nothing
discarded). Addressed the "guarantee" honestly: worst = the DB's best available approximation of
0.25 (dense band -> ~0.25; sparse -> the highest available <=0.25, e.g. 0.22). Proposed flag
semantics (--e-anchor-per-atom, moved with --e-max-per-atom cap, anchor drawn first, tie-break
by lowest index for determinism, empty-pool error).

**Verification:** 0 `Notes:` flags remain; answer renders at the Fortran section.

**Time:** 2026-08-28 ~01:00 JST.


---

## Session 2026-08-28 — README: assess bounded-attempt Notes block

**Goal (user request):** answer the new `Notes:` block proposing a bounded-attempt version instead
of while True: include an attempt value and raise an error if the criterion isn't found.

**Clarified (per standing rule):** assess in the README (no code change); compare it against the
earlier anchor-structure proposal, noting bounded-attempt can fail on sparse DBs whereas the
anchor never fails (just degrades to closest-available).

**Answer written (flag removed):** endorsed bounded-attempt as a robustness improvement over
while True (cannot hang; clear error signal); gave a bounded-rejection code sketch with
max_attempts and a RuntimeError. Compared to the anchor approach: bounded-attempt hard-fails if
no structure lands in the 0.24-0.25 band after N draws, whereas the anchor deterministically takes
the nearest (e.g. 0.22) and never fails. Positioned: bounded-attempt suits a hard "must be within
0.25±0.01" requirement; anchor suits real DBs (never errors, closest-available is usually what you
want). Proposed a hybrid (anchor, then choose error vs warn-and-proceed if outside the band).

**Verification:** 0 `Notes:` flags remain; answer renders at the Fortran section.

**Time:** 2026-08-28 ~01:10 JST.


---

## Session 2026-08-28 — README: answer two-checks-different-purposes Notes block

**Goal (user request):** answer the new `Notes:` block asking whether the `abs(gpr.predict_energy(s)) < 1e4`
check in the band-seeding sketch should also use the eV/atom-relative-to-ground-state definition.

**Clarified (per standing rule):** explain that the two checks serve different purposes (rel =
energy-window band filter; 1e4 = physical-sanity guard against unphysical GPR extrapolation), and
that 1e4 is in absolute eV, not eV/atom, so they should NOT share the same definition. No code change.

**Answer written (flag removed):** rel=(E-E_ref)/N is the relative per-atom window-band selector
("is it in 0.25±0.01?"); abs(predict_energy)<1e4 is an absolute-eV physical-sanity guard against
absurd GPR extrapolations (raw magnitude; system abs energies ~-437 eV). Different questions
(window vs sanity), so should not share a definition. Noted 1e4 could be made relative but would
be redundant with the window filter and conflate concerns; it should stay absolute/loose, matching
how _filter_unphysical and the abs(E)>1e4 checks already work in nested_sampler.py.

**Verification:** 0 `Notes:` flags remain; answer renders at the Fortran section.

**Time:** 2026-08-28 ~01:20 JST.


---

## Session 2026-08-28 — Implement windowed initial-live seeding (bounded-attempt, flags)

**Goal (user request):** add the code to perform the bounded-attempt version of the windowed
initial-live seeding, with a flag controlling max_attempts and the worst-energy-window pick
(e.g. [0.24, 0.25]).

**Clarified (per standing rule):**
- Seed ONE live point found by bounded-attempt in [lo, hi] (the "worst"); remaining K-1 live
  points are uniform draws capped at the window max (hi); the whole set capped at hi.
- Enforce the cap at hi inside the code (reject any initial draw whose rel energy > hi); do NOT
  rely on --e-max-per-atom.
- rel check uses the GPR-predicted energy of the sampled (perturbed) structure (matches how the
  sampler ranks live points).

**Code changes (nested_sampling/nested_sampler.py + main.py):**
- NestedSampler.__init__: new optional params e_window_lo, e_window_hi, e_window_max_attempts.
  Validates lo<=hi and max_attempts>=1; prints an enable notice. Moved E_ref/n_atoms assignment
  above the window block (it prints E_ref).
- New helpers: e_window_enabled(), rel_energy() (=(E_gpr-E_ref)/N), find_window_anchor()
  (bounded-attempt in [lo,hi], raises RuntimeError if not found), sample_capped_at_window()
  (draws accepted only if rel<=hi, bounded fallback to unconstrained draw),
  _append_live_point().
- initialize(): when windowed, seed the anchor first then the remaining K-1 capped draws;
  else the original path unchanged.
- main.py: new CLI flags --e-window-lo, --e-window-hi, --e-window-max-attempts (default 1000);
  passed to NestedSampler in both temperature-free and fixed-T branches.

**Verification (real execution):** py_compile OK for main.py + nested_sampler.py. Wrote a mock-GPR
smoke test (_tmp/test_windowed_seed.py) run with the agox_v2 python: (1) windowed init -> worst in
[0.24,0.25] and all live <=0.25 (PASS); (2) empty band -> RuntimeError (PASS); (3) default path
unchanged (PASS); (4) lo>hi -> ValueError (PASS). Removed the test file afterwards.

**Docs:** README.md - updated the "does not currently have a runtime relative max_E" note to point
to the new flags; added --e-window-lo/hi/max-attempts to the Options list; added a
"## Usage (windowed initial-live seeding)" section with an example.

**Time:** 2026-08-28 ~01:30-01:50 JST.


---

## Session 2026-08-28 — Version bump 1.2.0 -> 1.3.0 + add descriptions

**Goal (user request):** update the version and include a description for this version.

**Clarified (per standing rule):** bump main.py + nested_sampler.py to 1.3.0 (minor bump: new CLI
flags + new API params, per VERSIONS.md rules); add a per-version description as a new
'Description' column in the VERSIONS.md table.

**Actions taken:**
- `nested_sampling/nested_sampler.py`: __version__ 1.2.0 -> 1.3.0.
- `main.py`: __version__ 1.2.0 -> 1.3.0.
- `VERSIONS.md`: added a 'Description' column to the source-code table; described the two bumped
  files (main.py = new --e-window-lo/hi/max-attempts flags wired into both sampler branches;
  nested_sampler.py = bounded-attempt windowed initial-live seeding helpers). Other rows left at
  their existing versions with an empty description cell.

**Verification (real execution):** grep confirms both files at __version__ = "1.3.0"; py_compile
OK for main.py + nested_sampler.py.

**Time:** 2026-08-28 ~01:55 JST.


---

## Session 2026-08-28 — Update README notes to reflect implemented windowed seeding (v1.3.0)

**Goal (user request):** update all the README notes to include the newly-implemented windowed
initial-live seeding change (previously described as hypothetical / not-implemented).

**Clarified (per standing rule):** correct the README conceptual notes that still said the feature
doesn't exist / is hypothetical (--e-min-per-atom 'does not exist'/'hypothetical'/'you would need a
lower bound flag') to point to the now-implemented --e-window-lo/hi/max-attempts; keep the
conceptual explanation.

**Edits (README.md):**
1. Q&A "lower bound (floor)" note: replaced 'no flag for a lower bound / Adding --e-min-per-atom'
   with the implemented --e-window-lo/hi flags + pointer to the Usage section.
2. "Recommendation" paragraph: now recommends the implemented windowed seeding flags (bounded
   attempt + RuntimeError) instead of 'add an optional --e-min-per-atom flag'.
3. Q&A "stop at 0.25" note: replaced 'you would need a lower bound flag (--e-min-per-atom), which
   does not exist yet' with --e-window-lo/hi.
4. "maps directly to" note: replaced 'a hypothetical --e-min-per-atom 0.25' with
   --e-window-lo 0.25 / --e-window-hi 0.25.
5. "So the recipe is just one flag" note: now distinguishes the dataset-side flag (--e-max-per-atom)
   from the runtime initial-live-set window (--e-window-lo/hi), removing the stale 'No
   --e-min-per-atom'.

**Verification:** grep confirms 0 remaining occurrences of --e-min-per-atom / 'hypothetical' /
'does not exist' in README.md.

**Time:** 2026-08-28 ~02:05 JST.


---

## Session 2026-08-28 — Add windowed-seeding usage to TUTORIAL.md

**Goal (user request):** include in the TUTORIAL how to use the new windowed initial-live seeding
feature.

**Actions taken (TUTORIAL.md):**
- Added "## Step 6b — Windowed initial-live seeding (new in v1.3.0)" after Step 6 (Internals):
  a runnable example command, a 3-point "how it works" (anchor via bounded-attempt, rest capped
  at hi, E_boundary pinned in [lo,hi]), the flags (--e-window-lo/hi, --e-window-max-attempts),
  and notes (GPR-predicted energy, runtime-initial-live-set vs --e-max-per-atom dataset filter,
  only the initial set is affected).
- Added Common Pitfall 8: `--e-window-lo/hi` RuntimeError = empty band.
- Added a verification-checklist item for windowed seeding (anchor rel energy in band, all initial
  live <= hi).

**Verification:** TUTORIAL.md updated; consistent with the README's "Usage (windowed initial-live
seeding)" and the implemented code.

**Time:** 2026-08-28 ~02:15 JST.


---

## Session 2026-08-28 — README: answer Fortran-vs-Python sampling-move Notes block

**Goal (user request):** answer the new `Notes:` block asking what is different between the
Fortran's Gaussian random sampling (small + large step) and the current Python one.

**Clarified (per standing rule):** explain the differences: Fortran uses TWO rattle scales
(small=0.05, large=0.40) inside a multi-step MC walk (constrained_walk, mixing_steps=40) that
decorrelates and can cross the barrier; Python uses ONE small Gaussian perturb (--perturb 0.01)
and single draws with no MC walk; note how each relates to basin crossing and the 'walk length L'
gap.

**Answer written (flag removed):** contrasted the Fortran constrained_walk (2 Gaussian scales over
a 40-step MC walk, accept only if E < E_max_local) vs Python sample_from_prior (single Gaussian
perturb of std --perturb 0.01 to Fe atoms, no walk) + sample_constrained (independent rejection
draws until log L > log_L_boundary). Included a table (move types, steps, correlation, barrier
crossing, constraint) and a "why it matters" paragraph: the Fortran's large-step + walk is the
clone-and-MC-decorrelate NS move that can cross the barrier (the papers' walk length L); Python
cannot create new configurations, only re-draw from the DB (the modelling gap). Noted the two-scale
choice fits a continuous 1D potential, while Python's single small perturb avoids Fingerprint-GPR
extrapolation to unphysical energies.

**Verification:** 0 `Notes:` flags remain; answer renders in the Fortran section.

**Time:** 2026-08-28 ~02:25 JST.


---

## Session 2026-08-28 — README: answer how-to-implement-Fortran-sampling Notes block

**Goal (user request):** answer the new `Notes:` block asking how to apply the Fortran sampling
method (two-scale Gaussian + MC walk) in Python.

**Clarified (per standing rule):** explain conceptually how to implement it (add a clone-and-MC
constrained_walk to sample_constrained, with small/large Gaussian scales and a walk-length
n_steps; keep the GPR energy limit; note the perturb-symbols constraint); NO code change.

**Answer written (flag removed):** gave a Python sketch of a constrained_walk() method (clone,
two Gaussian scales small/large, n_steps, accept only if |E|<1e4 and E < E_boundary =
E_ref - log_L_boundary), and how to call it inside sample_constrained by cloning a random
surviving live point. Design points: walk length n_steps (Fortran mixing_steps=40; papers
100s-1000s), two scales with the large-scale GPR-extrapolation caveat, respect perturb_indices
(--perturb-symbols), keep the constrained E < E_boundary + |E|<1e4, clone a random non-worst live
point. Noted why this closes the 'walk length L' gap (Python currently only re-draws from the DB;
the walk lets a sample diffuse and cross the barrier).

**Verification:** 0 `Notes:` flags remain; answer renders in the Fortran section.

**Time:** 2026-08-28 ~02:35 JST.


---

## Session 2026-08-28 — README: answer constrained-walk sub-questions Notes block

**Goal (user request):** answer the new `Notes:` block with 4 sub-questions about the
constrained_walk sketch: what 'walk' means; does it perturb all --perturb-symbols atoms or one;
units; how a new structure is generated.

**Clarified (per standing rule):** answer all 4 in the README (no code change).

**Answer written (flag removed):** (1) walk = a sequence of many small/large random trial moves
from a starting clone, accumulating accepted moves over n_steps (the Fortran constrained_walk
loop, lines 160-175); (2) it perturbs ALL --perturb-symbols atoms simultaneously each trial
(noise over len(perturb_indices) x 3, added via trial.positions[perturb_indices] += noise, same as
sample_from_prior; 1D Fortran reduces to the single coordinate); (3) units = Angstrom (ASE
positions in A; std = scale in A, matching --perturb 0.01); (4) new structure = clone + accumulated
accepted trial moves, returned after n_steps — a new valid configuration inside the current energy
shell that independent draws cannot produce.

**Verification:** 0 `Notes:` flags remain; answer renders in the Fortran section.

**Time:** 2026-08-28 ~02:45 JST.


---

## Session 2026-08-28 — Implement dual-scale constrained MC walk + flags; version bump 1.3.0 -> 1.4.0

**Goal (user request):** implement the constrained_walk with dual scale into the code, with a flag
to activate it and controls for steps, small/large step, and an option to choose only small or only
large scale.

**Clarified (per standing rule):**
- Integration: inside sample_constrained, clone a random surviving live point and run the dual-scale
  MC walk as PRIMARY; fall back to rejection draws, then sample_from_prior if the walk fails.
- Flags: --walk (on/off), --walk-steps (default 40), --walk-small (0.05), --walk-large (0.40),
  --walk-mode {both,small,large}.
- Mode: both = 50/50 small/large (Fortran); small/large restrict to one scale.
- Clone: a random surviving live point (Fortran-style, non-worst).

**Code changes:**
- nested_sampler.py: constructor params walk/walk_steps/walk_small/walk_large/walk_mode (validated:
  walk_mode in {both,small,large}, walk_steps>=1, scales>=0). New methods _choose_scale() and
  constrained_walk() (clone, walk_steps Gaussian trials over perturb_indices, accept if |E|<1e4 and
  E < E_boundary, return None if never valid). sample_constrained now tries the walk first then
  rejection.
- main.py: new CLI flags --walk, --walk-steps, --walk-small, --walk-large, --walk-mode (choices);
  wired into both temperature-free and fixed-T sampler branches.
- Version: main.py + nested_sampler.py 1.3.0 -> 1.4.0 (new feature + flags = minor bump). VERSIONS.md
  descriptions updated.
- README.md: added the 5 flags to Options; added "## Usage (dual-scale constrained MC walk)".
- TUTORIAL.md: added "## Step 6c — Dual-scale constrained MC walk".

**Verification (real execution):** py_compile OK. Mock-GPR smoke test (_tmp/test_walk.py) run with
agox_v2 python: (1) invalid walk_mode -> ValueError; (2) mode=small -> always small scale; (3)
constrained_walk returns a structure below E_boundary; (4) sample_constrained (walk) returns a
structure; (5) walk-disabled rejection path still works. Removed the test file afterwards.

**Time:** 2026-08-28 ~02:55-03:15 JST.


---

## Session 2026-08-28 — Reconcile README walk notes with the implemented 1.4.0 feature

**Goal (user request):** check all the notes — is the README consistent with the 1.4.0 walking
feature? Found it was NOT: several Fortran-section notes still described the walk as
hypothetical/unimplemented.

**Clarified (per standing rule):** update all stale walk notes to reflect the now-implemented
--walk feature (mapping-table row, comparison+table framed as default, why-it-matters paragraph,
and the 'How to implement' + design-points sections), and add a version note.

**Edits (README.md):**
1. Fortran mapping table 'clone + constrained_walk' row: now notes --walk clones a random live
   point and runs the dual-scale MC walk (default = independent rejection).
2. 'constrained_walk rattle' row: maps to --walk-small/--walk-large/--walk-mode (default off,
   small --perturb).
3. 'Fortran vs Python sampling moves': framed the Python 'single perturb, no walk' as the DEFAULT;
   added a Python(--walk) column to the differences table; 'why it matters' now says enabling
   --walk closes the gap.
4. Replaced the entire stale 'How to implement ... design points to decide (--walk-length)'
   section with 'How the Fortran-style walk is now implemented in v1.4.0 (--walk)' — shows the real
   constrained_walk() implementation, the 4 how-it-works sub-answers (walk/which-atoms/units/new
   structure) reframed to the actual code + flags, and the design flags
   (--walk-steps/--walk-small/--walk-large/--walk-mode), plus the closes-the-gap note.

**Verification:** grep confirms no stale markers remain ('How to implement', 'design points to
decide', 'no clone-and-MC walk length', '1.3.0'); remaining 'cannot create new configurations' /
'no multi-step walk' references are all correctly framed as the DEFAULT without --walk.

**Time:** 2026-08-28 ~03:20-03:35 JST.


---

## Session 2026-08-28 — Fix stale version in TUTORIAL Step 6c

**Goal (user request):** the TUTORIAL's "## Step 6c — Dual-scale constrained MC walk (new in
v1.3.0)" still said 1.3.0 — is this correct? No: the walk was added in 1.4.0.

**Action taken:** changed Step 6c heading to "(new in v1.4.0)". (Step 6b, the windowed seeding, is
correctly labelled v1.3.0.)

**Verification:** grep shows TUTORIAL now has Step 6b (v1.3.0) and Step 6c (v1.4.0), consistent
with the VERSIONS manifest.

**Time:** 2026-08-28 ~03:40 JST.


---

## Session 2026-08-28 — Create run dir _runs/b6_tfree_walk_emax04 (Fe/MgO, e-max 0.4, window [0.3,0.35], dual-scale walk)

**Goal (user request):** make a new _runs dir. It runs Fe/MgO-only nested sampling with:
--e-max-per-atom 0.4 eV/atom above ground state; --e-window-lo 0.3 --e-window-hi 0.35 eV/atom
above ground state, --e-window-max-attempts 1000; --walk-steps 50 --walk-small 0.05 --walk-large
0.40 --walk-mode both.

**Clarified (per standing rule):**
- Name: b6_tfree_walk_emax04.
- Settings: temperature-free, n-live 100, n-iters 1000, temperatures 100,200,300,500,1000,
  perturb 0.01, perturb-symbols Fe, rng 42 + the specified flags.
- Scope: full self-contained copy (main.py + nested_sampling/ + scripts/ + dataset 13 seeds +
  j_*.sh + README + TUTORIAL), matching b4/b5.

**Actions taken:**
- Created _runs/b6_tfree_walk_emax04/ as a full self-contained copy from the project root
  (main.py v1.4.0 + nested_sampling/ + scripts/), dataset (13 seeds seed_3..15 + stop_16).
- Copied the CORRECT plot_structure_landscape.py (accepts s=) from
  _analysist/1_result/1_no_prior_control/nested_sampling/scripts/ into
  nested_sampling/scripts/ (avoids the 's' TypeError; verified s=25, normalize_density,
  density_x_label, plot_z_vs_e params present).
- Wrote j_b6_tfree_walk_emax04.sh (PJM, gpaw_env, OMP_NUM_THREADS=1) with the exact command line.
- Wrote README.md + TUTORIAL.md describing the run treatment, flags, and verification.
- py_compile OK for run main.py + nested_sampler.py; j script made executable.

**Command line:** main.py --temperature-free --temperatures 100,200,300,500,1000 --n-live 100
--n-iters 1000 --perturb 0.01 --perturb-symbols Fe --e-max-per-atom 0.4 --e-window-lo 0.3
--e-window-hi 0.35 --e-window-max-attempts 1000 --walk --walk-steps 50 --walk-small 0.05
--walk-large 0.40 --walk-mode both --output ./ns_output_tfree_walk_emax04 --rng 42

**Time:** 2026-08-28 ~03:50-04:10 JST.


---

## Session 2026-08-28 — Create run dir _runs/b7_boron_walk_emax04_wind03035 (boron system, b6 params)

**Goal (user request):** make a new _runs dir using the parameters of
_runs/b6_tfree_walk_emax04 but for the boron system in dataset_boron.

**Clarified (per standing rule):**
- Name: b7_boron_walk_emax04_wind03035.
- Params: same as b6 (temperature-free, n-live 100, n-iters 1000, temps 100,200,300,500,1000,
  perturb 0.01, rng 42) + --e-max-per-atom 0.4, window [0.3,0.35], max-attempts 1000, walk
  (steps 50, small 0.05, large 0.40, mode both), but --perturb-symbols Fe,B (boron moves too,
  matching b5).
- Scope: full self-contained copy (main.py + nested_sampling/ + scripts/ + dataset (boron,
  copied as dataset/, 5 seeds) + j_*.sh + README + TUTORIAL).

**Actions taken:**
- Created _runs/b7_boron_walk_emax04_wind03035/ as a full self-contained copy: main.py (v1.4.0)
  + nested_sampling/ + scripts/ from project root; dataset copied from dataset_boron/ (5 seeds
  seed_0..4, Fe25Mg25O25B7 / 82 atoms).
- Copied the CORRECT plot_structure_landscape.py (accepts s=25) from
  _analysist/1_result/1_no_prior_control/nested_sampling/scripts/ into
  nested_sampling/scripts/ (avoids the 's' TypeError; verified s=25 present).
- Wrote j_b7_boron_walk_emax04_wind03035.sh (PJM, gpaw_env, OMP_NUM_THREADS=1) with
  --perturb-symbols Fe,B and the same command line as b6 otherwise.
- Wrote README.md + TUTORIAL.md describing the treatment (b6 params on boron), flags,
  verification, and the boron high-energy-outlier note.
- py_compile OK for run main.py + nested_sampler.py; j script executable; 5 seed DBs present.

**Command line:** main.py --temperature-free --temperatures 100,200,300,500,1000 --n-live 100
--n-iters 1000 --perturb 0.01 --perturb-symbols Fe,B --e-max-per-atom 0.4 --e-window-lo 0.3
--e-window-hi 0.35 --e-window-max-attempts 1000 --walk --walk-steps 50 --walk-small 0.05
--walk-large 0.40 --walk-mode both --output ./ns_output_tfree_walk_emax04 --rng 42

**Time:** 2026-08-28 ~04:20-04:40 JST.


---

## Session 2026-08-28 — Document --perturb vs --walk interaction (b6 README/TUTORIAL + root README)

**Goal (user request):** explain what --perturb 0.01 does given the --walk method, and write the
clarification into the b6 README/TUTORIAL and the root README.

**Answer (grounded in code):** --perturb and --walk are two DIFFERENT moves, both active in b6.
--perturb sets the Gaussian displacement (std = --perturb) of the base prior draw
sample_from_prior, used for the initial live-set draws (windowed anchor search + capped fills)
and as the fallback when the walk fails. The walk uses its own --walk-small/--walk-large scales
in sample_constrained, independent of --perturb. So --perturb is NOT redundant with --walk.

**Edits:**
- _runs/b6_tfree_walk_emax04/README.md: added a bullet under the --walk feature explaining
  --perturb vs --walk (not redundant).
- _runs/b6_tfree_walk_emax04/TUTORIAL.md: added a --perturb 0.01 bullet after the --walk flags.
- README.md (root): added a note in the 'Usage (dual-scale constrained MC walk)' Notes list.

**Time:** 2026-08-28 ~04:50 JST.
