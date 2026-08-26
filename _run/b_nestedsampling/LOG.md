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
