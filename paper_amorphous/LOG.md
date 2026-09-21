# LOG.md — paper_amorphous (append-only)

## Session 1 — 2026-09-21 (initialization)
**Goal (user-confirmed via clarify):** Initialize the `scientific-paper-writing` workflow on the amorphous Pt(P) system in `paper_amorphous`, mirroring the `paper_femgo` layout, and scaffold `papers/paper1` (amorphous generation + methods) with the SHC section as a placeholder.

**Actions taken:**
1. Scoped the task: inspected `data/` (17_PPt, 11_bTa, 16_bW), `tmp/` (FLAPW install + SHC example), and the `paper_femgo` reference layout.
2. Audited the Pt–P data: cell families `0_plus5cell` (+5%, 12.523 Å), `1_plus0cell` (+0%, 11.927 Å), `2_plus3cell` (+3%, 12.284 Å), `3_plus10cell` (+10%, 13.119 Å). Confirmed `3_plus10cell` is **excluded** (owner + `DISCUSSION.md`). Noted `main.py` `SCALE_CELL=1.05` is stale for the +0/+3 families.
3. Clarified 5 decisions with the owner (cell scope, systems, paper1 structure, SHC input structures, authors/venue) → spec approved.
4. Created project scaffold: `papers/paper1/` (main.tex + sections/ + figures/ + references.bib + supplementary/), `codes/`, `analysis/`. Copied `spieman.cls` + `spiejour.bst` from `paper_femgo`.
5. Wrote doc scaffold: AGENTS.md, README.md, README.AI.md, LOG.md, TUTORIAL.md, VERSIONS.md, .gitignore, paper_status.md, CLAIMS.md, and empty section stubs.

**Results:** Project skeleton in place; paper1 scaffolded with empty section stubs; SHC section marked as placeholder.

**Decisions & reasoning:**
- Full skill layout (`papers/paper1/` with per-section `.tex`) per owner choice.
- Cell scope: +0/+3/+5% in, +10% out (owner correction).
- Systems: Pt(P) 20/30% focus; 0/10% reference; bTa/bW in SI discussion.
- Paper1: scaffold now (no prose); SHC as placeholder section.
- Authors/venue: same as paper_femgo (Andi Muhammad Nur Fitrah Syamsul, Kohji Nakamura; APS RevTeX 4.2 main + SPIE SI).

**Open items:**
- [ ] Confirm contribution framing with owner (Phase A) before drafting prose.
- [ ] Decide which structures feed the SHC calculation (best-so-far vs representative set vs crystalline reference).
- [ ] Run the SHC calculation (in progress) and fill the placeholder section.
- [ ] Write `codes/` figure/analysis scripts and produce `analysis/` outputs.
- [ ] Commit Milestone 1.

## Session 2 — 2026-09-21 (SHC pipeline scaffold: spec + code, build-validated)
**Goal (owner-authorized `run it`):** Prepare the two-stage HPC SHC pipeline for
amorphous Pt(P) — Run A (novelty+force filter + DFT re-opt → `opt_novel_<leaf>.traj` ×4)
and Run B (FLAPW SHC) — plus the 0%-P reference, the dose↔at% conversion helper, and the
XRD benchmark, per spec `202609211704-ptp-shc-stage.md` (v7).

**Actions taken:**
1. `/clarify-me` interview → spec v1–v7 (selection pool: 20P & 30P at +3/+5% cell, 4
   leaves; per-leaf traj; gpaw_env single env; leaf-adaptive force gate; per-leaf
   novelty dedup; 0%-P +0-cell crystalline reference).
2. `/inspect-me` physics pass — folded C3/M4/M7/m7/m8/G8; measured the real db force
   distribution (30P `frac<1.0` ≈ 0–1% vs 20P ≈ 17%; NN fingerprint distances compressed,
   median ~0.26) and corrected the assumptions that would have broken selection.
3. Inspected the reference paper + SI (.docx) — Shashank 2025 NPG Asia Mater 17:15:
   σ^SH 3.62 vs 1.03 (2e/ℏ) Ω⁻¹cm⁻¹, θSH 1.17; SI S4 XRD (pure Pt fcc a=3.932 Å,
   I(220)/I(111) 0.33→3.14, peak shift, halo/amorphization) and S3 SRIM. Comparison
   metric = simulated XRD via the existing `_run/0_lcb/2_analysist` pipeline.
4. Authored `hpc_runs/` (7 code files + 2 job scripts + README): `select_reopt/`
   (`filter_select.py` v1.0.0, `reopt.py` v1.0.0, `job_genkai_mpi.sh`), `shc/`
   (`main.py` v1.0.0, `make_ref_traj.py` v1.0.0, `job_genkai_mpi.sh`),
   `convert_dose_concentration.py` v1.0.0, `xrd_benchmark.py` v1.0.0.

**Results (verified by real execution, no FLAPW/GPAW run locally):**
- `filter_select.py` ran on all 4 leaves in `agox_v2`: 3 distinct novel+low-force minima
  each (20P maxF ~0.7–0.99, 30P ~1.3–1.9 eV/Å); calibrated fingerprint tol (0.32–0.56)
  vs the too-coarse default 1.0; selection JSONs written.
- `make_ref_traj.py` → `ref_0P_gmin.traj` (Pt108, E=-653.806 eV, fmax 0.03).
- `convert_dose_concentration.py` → our 20 at% ≈ 2.2e16, 30 at% ≈ 3.4e16 ions/cm² (in
  the reference's 2.5–10e16 range).
- XRD benchmark: `xrd_benchmark.py` wrote CIFs; pymatgen Cu-Kα on them shows crystalline
  Pt reference sharp (3,3,3) I=5.6e9 vs amorphous 20P broad/split top I=1.5e9 — the
  crystallinity drop.
- All `.py` pass `py_compile`; `main.py` SHC parse + unit conversion unit-tested.

**Decisions & reasoning:**
- Selection pool = 4 amorphous leaves (2_20P, 3_30P, 1_3x3_20P, 2_3x3_30P); novelty
  dedup per leaf (avoids +3/+5 cell-mix); force cutoff leaf-adaptive + calibrated tol.
- Run B env = `gpaw_env` (pflapw under it; `flapw_2` retired); 4 separate pjsub (M3) +
  1 reference subjob.
- Comparison metric = simulated XRD (owner), not 1:1 SHC transport; dose↔at% helper
  unifies axis.

**Open items:**
- [ ] Submit Run A on HPC (`pjsub select_reopt/job_genkai_mpi.sh`) → real DFT re-opt.
- [ ] Submit Run B on HPC (4 + 1 pjsub) → SHC numbers; confirm xoptics parse fields (spec G7).
- [ ] Run the canonical Stage-2 XRD (`xrd_simulate_crystallinity.py`) on our trajs.
- [ ] Commit Milestone 2 (this session).

**Time:** 2026-09-21 ~16:10–20:05 JST

## Session 2b — 2026-09-21 (fix: Run B calc dir is self-contained FLAPW, not a package)
**Owner clarification (`/clarify-me`):** `flapw` is NOT an importable package — it is a
standalone Python file (`flapw.py`, an ASE FileIOCalculator) that must live in the calc
working dir alongside `pflapw` (binary), `README_MT-default`, and `opt/`. `main.py` does
`from flapw import FLAPW`, which only resolves because `flapw.py` sits in the CWD.

**Actions taken:**
1. Inspected `tmp/SHC Calculation/HEA_SHC_Auto_Python_FLAPW/` — confirmed the calc dir
   contract: `flapw.py` reads `README_MT-default` from CWD (`Path("README_MT-default")`)
   and `opt/` via `prepare_optics`; `_run_pflapw` runs `./pflapw`.
2. Copied the committed source/config into `hpc_runs/shc/`: `flapw.py`,
   `README_MT-default`, `opt/opticsin`.
3. Added `hpc_runs/shc/.gitignore` (ignores large HPC binaries `pflapw`, `opt/xoptics`,
   and `*.traj`) + `setup_calc.sh` (stages `pflapw` + `opt/xoptics` from the FLAPW calc
   source before submit).
4. Updated `main.py` docstring (self-contained calc dir contract) and `job_genkai_mpi.sh`
   (runs `./setup_calc.sh` first).

**Verified:** `from flapw import FLAPW` resolves from `hpc_runs/shc/` CWD; `py_compile`
passes; `./setup_calc.sh` stages `pflapw` + `opt/xoptics`; binaries/traj not in git.

**Time:** 2026-09-21 ~19:55–20:05 JST

## Session 2c — 2026-09-21 (shc/ is a fully standalone dir; binaries committed)
**Owner clarification (`/clarify-me`):** the `shc/` dir must run **independently** on the
HPC as its own standalone directory — all inputs and necessities inside it.

**Actions taken:**
1. Committed the large HPC binaries `pflapw` (12M) + `opt/xoptics` (7.3M) to git so the
   dir is self-contained on any clone/copy (removed them from `shc/.gitignore`; kept
   `*.traj` ignored as regenerable).
2. Rewrote `setup_calc.sh`: (a) verifies the committed FLAPW calc files are present
   (flapw.py, README_MT-default, pflapw, opt/opticsin, opt/xoptics); (b) stages the traj
   inputs (`opt_novel_<leaf>.traj` ×4 + `ref_0P_gmin.traj`) into `shc/` from the Run A
   output dir (idempotent — keeps existing trajs). `RUN_A_OUT` env overrides the source.
3. Updated `job_genkai_mpi.sh` comment (binaries committed, not staged).

**Verified:** `sh -n` passes on both scripts; `./setup_calc.sh` verifies calc files,
keeps existing `ref_0P_gmin.traj`, warns on the not-yet-generated `opt_novel_*.traj`
(produced by Run A reopt on HPC); binaries staged in git.

**Time:** 2026-09-21 ~20:05–20:15 JST

## Session 2d — 2026-09-21 (hpc_runs STANDALONE rule: every subdir self-contained)
**Owner clarification (`/clarify-me`):** every directory under `hpc_runs/` must be a
standalone system — all inputs inside the dir, nothing pulled from outside.

**Actions taken:**
1. **select_reopt/ standalone:** copied the 15 input AGOX DBs (33M) into `./data/`
   (per-leaf `seed_*/1_db/db_*.db`); `filter_select.py` now defaults to the in-dir
   `./data/` root (`--data-root` override) and resolves bare leaf keys against it;
   `reopt.py` defaults `--selroot`/`--outdir` to in-dir `./out_select_reopt/`; added
   `setup.sh` (stages DBs, idempotent) + `.gitignore` (out_select_reopt/); job script
   reads `./data/` (no external `PPAP_DATA`).
2. **shc/ standalone:** committed `ref_0P_gmin.traj`; `setup_calc.sh` stages the
   `opt_novel_<leaf>.traj` ×4 from the in-tree select_reopt output (idempotent); shc
   `.gitignore` now only ignores `shc_out/` + `__pycache__/` (trajs committed).
3. **Rule codified:** added a top-level `hpc_runs/README.md` "STANDALONE RULE" section
   stating every subdir is self-contained (all inputs in-dir, no external refs), with
   per-dir setup + job scripts.

**Verified:** `sh -n` passes on all 4 scripts; `./setup.sh` idempotent (keeps existing
DBs); `filter_select.py` reads in-dir `./data/` (tested on `2_20P`, chosen=2);
`py_compile` passes on filter_select.py + reopt.py.

**Time:** 2026-09-21 ~20:15–20:35 JST

## Session 2e — 2026-09-21 (select_reopt per-leaf dispatch, like shc)
**Owner clarification (`/clarify-me` → spec `202609212029-select-reopt-per-leaf`):**
restructure `select_reopt/` to run **one leaf per submission** (like `shc/`), each
producing that leaf's single `opt_novel_<leaf>.traj`, with one `.sh` per leaf + a shared
parameterized template.

**Actions taken:**
1. Rewrote `job_genkai_mpi.sh` as a shared template reading a `LEAF` env var (fails fast
   if unset); runs `filter_select.py --leaves <leaf>` then `reopt.py --leaf <leaf>` for
   that leaf only → one traj per submission.
2. Added 4 per-leaf wrappers: `job_2_20P.sh`, `job_3_30P.sh`, `job_1_3x3_20P.sh`,
   `job_2_3x3_30P.sh` — each sets `LEAF=<leaf>` and `exec`s the shared template.
3. Updated `hpc_runs/README.md` (Run A section + layout tree) to document per-leaf
   dispatch.

**Verified:** `sh -n` passes on all 5 scripts; template requires `LEAF` (line 32); each
wrapper exports the correct leaf; `filter_select.py --leaves 2_20P` runs (single-leaf
mode) producing per-leaf output.

**Time:** 2026-09-21 ~20:30–20:45 JST

## Session 2f — 2026-09-21 (select_reopt: per-leaf scripts fully independent)
**Owner correction:** the per-leaf `.sh` files must be **fully independent** — each with
its own pjsub header and body, leaf hardcoded — NOT `exec`-ing a shared
`job_genkai_mpi.sh` template.

**Actions taken:**
1. Rewrote the 4 per-leaf scripts (`job_2_20P.sh`, `job_3_30P.sh`, `job_1_3x3_20P.sh`,
   `job_2_3x3_30P.sh`) as self-contained: each carries its own 6-line `#PJM` header
   (a-batch, 24 procs, 120 h), hardcodes `LEAF=<leaf>`, and runs filter_select + reopt
   for that leaf → one `opt_novel_<leaf>.traj`.
2. Deleted the shared `select_reopt/job_genkai_mpi.sh` template (no longer used).
3. Updated `setup.sh` submit hint and `hpc_runs/README.md` (standalone-rule line, layout
   tree, Run A usage) to reference the per-leaf scripts.

**Verified:** `sh -n` passes on all 4; no `exec` to a shared template; each has 6 PJM
lines + hardcoded LEAF; no dangling refs to the removed template. `shc/job_genkai_mpi.sh`
(Run B) untouched.

**Time:** 2026-09-21 ~20:45–20:55 JST






