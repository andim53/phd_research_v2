# LOG.md — Curated action log (append-only)

Append-only record of AI actions. Never rewrite/delete prior entries; add new ones.
Each session: Goal / Clarify / Actions / Results / Decisions / Open items / Time.

---

## 2026-08-31 — Session: initial project scaffold (Pt–P LCB)

**Goal**
Initialize the AI-Agent Project Workflow for `_run/0_lcb` (Pt–P interstitial-alloy
LCB AGOX search), incorporating the pre-existing `2_analysist/17_PPt/` analysis tree
and adding the standard deliverable set + notes.

**Clarify (confirmed via clarify tool)**
- Identity: yes — Pt–P interstitial alloy LCB search; `17_PPt` is the analysis tree
  to incorporate.
- Deliverables: full set — README.md + README.AI.md + LOG.md + TUTORIAL.md +
  VERSIONS.md + AGENTS.md + PROMPTS.md.
- `run_analysis_indices.py`: keep as an annotated copy; document that it needs
  retargeting to Pt–P (recommended option).
- Notes: README `Notes:` blocks + PROMPTS.md (both).

**Actions**
1. Surveyed the existing `0_lcb/` tree: found `2_analysist/17_PPt/` (Pt fcc host +
   P interstitials; 4 supercell families `0_plus5cell/1_plus0cell/2_plus3cell/
   3_plus10cell` × P-conc `0P/10P/20P/30P` + `0_PPt_4x4_20P`), `run_analysis_indices.py`
   (identical to `a_lcbnovel`), and an empty `1_runs/`. Nothing was git-tracked.
2. Confirmed `run_analysis_indices.py` is a byte-identical copy of the Fe/MgO
   `a_lcbnovel` runner (`__version__ = "2.0.0"`), scoped to Fe/MgO indices 71/72 —
   not Pt–P.
3. Designed and wrote the deliverable set:
   - `README.md` (human overview + Notes blocks + status checkboxes)
   - `README.AI.md` (agent spec: layout, entry points, deps, edge cases, provenance)
   - `PROMPTS.md` (shared grammar notes; no processed flags yet)
   - `LOG.md` (this file)
   - `TUTORIAL.md`, `VERSIONS.md`, `AGENTS.md`, `.gitignore`
4. Added a project-level `.gitignore` to keep regenerable per-run outputs
   (db/xsf/png/log/generated_structures/gpaw_logs) out of git while tracking the
   canonical code + docs. On clarify, excluded `2_analysist/11_bTa/` (Ta–B system,
   off Pt–P scope) from git.

**Results**
- Full deliverable set created under `_run/0_lcb/`.
- Existing `17_PPt/` tree left in place (not reorganized) and documented.
- ~797 `.py` + 20 `.sh` files under `17_PPt/` are trackable; project `.gitignore`
  excludes regenerable outputs so the tracked set stays code+docs only.

**Decisions & reasoning**
- **Keep `17_PPt` as-is** — it predates the scaffold and is the raw run/analysis
  tree; reorganizing it would break run reproducibility.
- **Keep the runner as an annotated copy** — retargeting Fe/MgO → Pt–P is a
  substantive code change better done as a dedicated future task (per user choice).
- **Project-level `.gitignore`** — the parent `.gitignore`'s path rules don't reach
  a nested project dir, so 0_lcb gets its own.

**Open items**
- Retarget `run_analysis_indices.py` from Fe/MgO → Pt–P (`17_PPt`) before any
  analysis run.
- Add per-analysis `DISCUSSION.md` once analysis is run.
- Populate `1_runs/<NN>_<descriptor>/` with future self-contained runs.

**Time:** ~2026-08-31 14:34 JST

---

## 2026-08-31 — Session: analysis runner retargeted + per-family READMEs

**Goal**
Make `2_analysist/run_analysis_indices.py` able to analyse the current results under
`2_analysist/` (all 4 interstitial-alloy families) and add a README per result dir
explaining how to run the runner for that dir. Do not run the analysis code yet.

**Clarify (confirmed via clarify tool)**
- Scope: all 4 trees — `11_bTa` (Ta–B), `15_bPt` (Pt–B), `16_bW` (W–B),
  `17_PPt` (Pt–P).
- README granularity: one README per **family tree** (`15_bPt/README.md`,
  `16_bW/README.md`, `11_bTa/README.md`, `17_PPt/README.md`) — 4 READMEs.
- Dependency: copy `plot_structure_landscape.py` (+ deps) into a new
  `2_analysist/scripts/` so the runner works from `2_analysist`.
- Git: track the new READMEs + edited runner (commit).

**Actions**
1. Surveyed `2_analysist/`: confirmed 4 result trees with leaf dataset dirs holding
   `seed_*/1_db/db_*.db`; verified DBs load and atom counts differ per system
   (Pt108, W54, Ta54, P27Pt108).
2. Diagnosed the runner's blocked import: it does
   `from scripts.plot_structure_landscape import plot_structure_landscape`, which
   resolved against a nonexistent `2_analysist/scripts/`.
3. Copied `17_PPt/scripts/plot_structure_landscape.py` → `2_analysist/scripts/`
   (verified self-contained: only stdlib/numpy/scipy/matplotlib imports; import
   resolves under `agox_v2`).
4. Edited `run_analysis_indices.py`:
   - Rewrote the Fe/MgO-scoped docstring to document the 4-family scope and
     per-leaf `--dataset`/`--outdir` invocation.
   - Bumped `__version__` 2.0.0 → 2.1.0.
   - Confirmed no functional change needed: the runner already globs
     `seed_*/1_db/db_*.db` and reads atom count dynamically.
   - Verified `py_compile` under `agox_v2`.
5. Wrote 4 per-family READMEs (`15_bPt`, `16_bW`, `11_bTa`, `17_PPt`), each with a
   leaf table, exact per-leaf run commands, optional flags, and outputs.
6. Updated `.gitignore` to track `11_bTa/README.md` (and un-ignore its dir) while
   keeping `11_bTa` run data excluded. Verified ignore/track rules.
7. Updated `README.AI.md` (layout + §2b runner section) and `VERSIONS.md`.

**Results**
- Runner `v2.1.0` now compiles and imports cleanly under `agox_v2`; ready to run
  per leaf.
- `2_analysist/scripts/plot_structure_landscape.py` added.
- 4 per-family READMEs created with exact run instructions.
- Gitignore updated so `11_bTa/README.md` is tracked while its run data is not.

**Decisions & reasoning**
- **Keep the runner project-agnostic** — no per-system code paths; the data loader
  already handles differing atom counts, so one runner serves all families.
- **`--e-max` left as a documented optional flag** — energy-per-atom ranges differ
  per system, so each README suggests setting it (e.g. `0.5`) rather than hardcoding.
- **11_bTa README tracked, data excluded** — honours the earlier off-scope decision
  while making the now-usable results discoverable.

**Open items**
- Run the analysis (per-leaf) once the owner requests it; add per-analysis
  `DISCUSSION.md` per the workflow.
- Populate `1_runs/<NN>_<descriptor>/` with future self-contained runs.

**Time:** ~2026-08-31 15:28 JST

---

## 2026-08-31 — Session: fix Stage-2 crash in analysis runner (stale dep)

**Goal**
Fix `TypeError: plot_structure_landscape() got an unexpected keyword argument 's'`
thrown by `run_analysis_indices.py` at Stage 2, when run on the 15_bPt results.
"Update the scripts of root project."

**Clarify / diagnosis**
- Error occurred in `step2_landscape` at the `plot_structure_landscape(...)` call,
  which passes `s=15`, `normalize_density=...`, `density_x_label=...`.
- Root cause: the `2_analysist/scripts/plot_structure_landscape.py` I had copied in
  the previous session came from the **stale** `17_PPt/scripts/` version, which does
  **not** accept `s`, `normalize_density`, or `density_x_label`. The runner's call
  signature matches the **`a_lcbnovel/2_analysist/scripts/`** version instead (that
  version carries `__version__ = "1.0.0"` and all three params).
- The correct dep was confirmed by diffing the runner's call args against candidate
  copies (`a_lcbnovel`, `b_nestedsampling` have the params; `17_PPt` does not).

**Actions**
1. Confirmed `a_lcbnovel/2_analysist/scripts/plot_structure_landscape.py` accepts every
   argument the runner passes (s, normalize_density, density_x_label, black_seed_zero,
   etc.).
2. Replaced `0_lcb/2_analysist/scripts/plot_structure_landscape.py` with the correct
   version from `a_lcbnovel/2_analysist/scripts/` (now `__version__ = "1.0.0"`).
3. Verified by real execution: ran the runner on `15_bPt/4_p_pt10b` (1 seed) and then
   on the **exact failing command** `15_bPt/1_pt0b`. Both completed all 3 stages
   (Stage 1 progression + 5 xsf, Stage 2 landscape, Stage 3 Boltzmann P(T)).
4. Updated `VERSIONS.md` (dep version + corrected source).

**Results**
- The exact reported command now runs to completion (`DONE`, outputs under
  `15_bPt/1_pt0b/analysis_indices`).
- Analysis outputs are regenerable and gitignored (only the dep `.py` + VERSIONS.md
  are tracked).

**Decisions & reasoning**
- **Correct dep is the `a_lcbnovel` version** (not `17_PPt/scripts/`). The runner was
  ported from `a_lcbnovel`, whose dep matches its call signature. This mirrors the
  known pitfall in the b_nestedsampling AGENTS.md ("stale version lacks the `s=`
  argument → TypeError").

**Open items**
- Run the full per-leaf analysis set across all 4 families when the owner requests it;
  add per-analysis `DISCUSSION.md`.
- Populate `1_runs/<NN>_<descriptor>/` with future self-contained runs.

**Time:** ~2026-08-31 (later session)

---

## 2026-09-02 — Session: JSON emit/replot for analysis_indices + xrd (v2.3.0 / v1.1.0)

**Goal (user-confirmed via clarify):** (1) In `run_analysis_indices.py` add a flag to dump
each stage's plotting data to JSON *before* drawing each PNG, and a way to read that JSON to
reproduce the PNG, for ALL graphs; (2) do the same for the XRD plots produced by
`xrd_simulate_crystallinity.py`; (3) update `TUTORIAL.md` with run/JSON/extraction/plot
commands; (4) prepare commands to extract all current `analysis_indices` PNGs' json data
plus `8_fxg_1b/xrd_out`, and a command to plot the json. (TUTORIAL + code update per owner
command; LOG/VERSIONS auto-appended.)

**Clarify decisions (user-confirmed):** json written to `--json-dir` AND png still drawn;
`--from-json` replot mode in the same script; stage JSONs per-graph named
`stage{1,2,3}_{...}.json`; default json-dir = `<outdir>/analysis_json`; store literal plotted
arrays for full faithfulness; for Stage-2 `conf_space.png` edit
`plot_structure_landscape.py` to optionally return computed arrays; also add json support to
the xrd script; re-copy... (N/A). Scope = single + multi dir + json + extraction/plot in
TUTORIAL.

**Actions taken (code):**
- `run_analysis_indices.py` v2.2.0→2.3.0: added `--json-dir` (default `<outdir>/analysis_json`)
  + `--from-json`; made `--dataset` optional (error unless from-json given); split each stage
  into a compute-data fn + `_plot_*_from_data` so live & replot share identical drawing;
  JSON helpers `_to_jsonable`/`_color_to_hex`/`_write_stage_json`/`_read_stage_json`;
  `_progression_data` now also writes the .xsf side-outputs; Stage 2 stores plot inputs +
  params and re-runs `plot_structure_landscape`; Stage 1/3 store the literal curve arrays.
- `scripts/plot_structure_landscape.py` v1.0.0→1.1.0: added optional `return_data` param
  that returns the computed arrays (energy_grid, density_curves, peaks, scatter_x/e, e_limit)
  alongside drawing conf_space.png.
- `scripts/xrd_simulate_crystallinity.py` v1.0.0→1.1.0: added `--json` (writes
  `xrd_plots.json` of per-window 2theta grid + intensity + CI rows) and `--from-json`
  (replot both PNGs from it); split plotting into `plot_patterns_from_data`/
  `plot_ci_from_data`; `--manifest` now optional (error unless from-json given).

**Results (real output, verified):**
- analysis_indices on `11_bTa/8_fxg_1b` (--e-max 1.0) wrote the 3 stage JSONs under
  `<out>/analysis_json` and drew all 3 PNGs.
- `--from-json` replot produced all 3 PNGs **byte-identical** to the original run
  (cmp SAME for progression_seed_split_0, conf_space, binding_probability_vs_temperature).
- xrd `--json` wrote xrd_plots.json; `--from-json` replot produced both xrd PNGs
  **byte-identical** (cmp SAME).
- py_compile OK under agox_v2 (run_analysis_indices, plot_structure_landscape) and pymat_xrd
  (xrd_simulate_crystallinity).

**Decisions & reasoning:** stage-2 arrays captured via an optional `return_data` in the
external landscape function (cleanest faithful path, chosen over duplicating its KDE logic);
colors serialized as hex (`_color_to_hex`) because `str()` of an RGBA tuple is not a valid
matplotlib color; `--dataset`/`--manifest` made non-required so `--from-json` runs without DB/
CIF access.

**Open items**
- Update `TUTORIAL.md` (owner-commanded next) with the run/multi-dir/JSON/extract/plot recipes.
- Prepare the extraction command (collect analysis_indices JSONs + xrd_out json) and a
  json-plot command (in TUTORIAL).
- VERSIONS.md table refreshed to 2.3.0 / 1.1.0 / 1.1.0.

**Time:** 2026-09-02

---

## 2026-09-02 — Session: JSON-extraction command scripts + Obsidian report (0_lcb)

**Goal (user-confirmed via clarify):** Write per-structure commands (one per leaf) to
regenerate every existing analysis/xrd PNG WITH its companion JSON, a command to collect all
JSONs, and a report in the Obsidian vault. Owner chose: REGENERATE semantics; one command per
structure (NOT a monolithic loop); report appended to the existing `afi/report/2026-09-02.md`;
scope = all 4 families (25 analysis leaves + 5 xrd_out); staging dir =
`2_analysist/json_export/`. The ~1 h full run is NOT launched now — commands delivered for the
owner to run.

**Actions taken:**
- Enumerated all 25 analysis_indices dirs (11_bTa 5, 15_bPt 4, 16_bW 4, 17_PPt 12; each has
  seed DBs) + 5 xrd_out dirs (11_bTa only).
- Wrote `json_export/regenerate_analysis_json.sh` (25 individual `run_analysis_indices.py
  --e-max 0.5` commands, one per leaf, each emitting the 3 stage JSONs under
  `<leaf>/analysis_indices/analysis_json` then redrawing the PNGs).
- Wrote `json_export/regenerate_xrd_json.sh` (5 individual `xrd_simulate_crystallinity.py
  --json` commands, one per leaf).
- Wrote `json_export/collect_json.sh` (finds all `analysis_indices/analysis_json/stage*.json`
  + `xrd_out/*.json`, copies them preserving family/leaf paths into `json_export/`).
- Appended a dated report section to `/home/think/MEGA/Obsidian-Notes/afi/report/2026-09-02.md`.

**Results (real output, verified):**
- All three scripts pass `bash -n` (syntax OK).
- collect_json.sh logic dry-run on a mirrored tree staged the expected 3 JSONs correctly.
- Report appended to the Obsidian note (markdown lint N/A).

**Decisions & reasoning:** One command per structure so the owner can run leaves individually
or in any subset (matches prior heavy-run convention); JSONs emit in place under the leaf's
analysis_json/xrd_out by default; collect preserves the family/leaf tree so provenance is
clear. Did NOT launch the ~1 h regenerate (owner runs it).

**Open items**
- Owner runs `regenerate_analysis_json.sh` + `regenerate_xrd_json.sh`, then `collect_json.sh`.
- Consider tracking `json_export/*.sh` in git (scripts, non-regenerable) vs gitignoring the
  collected JSONs.

**Time:** 2026-09-02

---

## 2026-09-02 — Session (revision): JSONs saved per-leaf in each analysis_indices/, central collect removed

**Goal (user-confirmed via clarify):** The JSONs should NOT be aggregated into one json /
a central `json_export/` staging; instead they must be **multiple JSONs, saved directly
inside each data's own `analysis_indices/` dir**. Owner chose: keep the 3 separate stage
JSONs per leaf saved directly inside that leaf's `analysis_indices/` (no `analysis_json`
subfolder, no `json_export/` collection); delete `collect_json.sh`.

**Actions taken:**
- Edited `json_export/regenerate_analysis_json.sh`: every per-leaf command now passes
  `--json-dir <leaf>/analysis_indices` (== its outdir), so the 3 stage JSONs are written
  directly into that leaf's own `analysis_indices/` instead of an `analysis_json/` subdir.
- Deleted `json_export/collect_json.sh` (the central collector).
- Updated the Obsidian report (`afi/report/2026-09-02.md`): scope note, commands, and the
  single-structure example now point `--json-dir`/`--from-json` at the leaf's
  `analysis_indices/` dir, and removed the `analysis_json` + collect descriptions.

**Results (real output):** `bash -n` clean on both remaining regenerate scripts; report
updated (markdown lint N/A).

**Decisions & reasoning:** Per owner, JSONs remain per-leaf and per-stage (multiple files),
each stored where its data lives; no single-JSON aggregation and no central staging dir.
The xrd `regenerate_xrd_json.sh` already wrote `xrd_plots.json` into each leaf's own
`xrd_out/`, so it needed no change.

**Open items**
- Owner runs `regenerate_analysis_json.sh` + `regenerate_xrd_json.sh`.
- Re-commit removes `collect_json.sh` from git (deleted) and updates `regenerate_analysis_json.sh`.

**Time:** 2026-09-02

---

## 2026-09-02 — Session: README.AI.md updated to current 2_analysist state

**Goal (user-confirmed via clarify):** Update `README.AI.md` in place to the true current
state and correct the stale v2.1.0 / "Fe/MgO-scoped, don't-run-on-17_PPt" claims to match the
real v2.3.0 project-agnostic runner; document all of 2_analysist (families, runner + 3 stages
+ scripts, JSON emit/replot + per-leaf layout, json_export drivers, entry-point commands).
README.AI.md update is on explicit owner command; LOG auto-appended.

**Actions taken:** Rewrote `README.AI.md` sections 1–6 in place:
- identity now reflects interstitial alloys (Pt/Ta/W hosts, B/P) + the two envs;
- layout adds `2_analysist/scripts/` (3 scripts w/ versions), `json_export/` drivers;
- §2b runner updated to v2.3.0 project-agnostic (25 leaves incl. 17_PPt), JSON emit/replot;
- new §2c XRD scripts, §2d json_export drivers;
- entry-point commands updated (single leaf, all-25 driver, XRD, from-json);
- §5 known gaps corrected (removed the obsolete "runner mismatch on 17_PPt"; added two-env,
  --from-json, json-only-after-flag, xsf-DB-only notes);
- §6 provenance corrected (runner IS used on 17_PPt; XRD scripts + json_export provenance).

**Results:** README.AI.md written (11,970 bytes). Markdown lint N/A. No code changed.

**Decisions & reasoning:** Chose an in-place rewrite (not an addendum) because the stale
runner/warning wording would otherwise contradict the corrected body. Verified current facts
first (runner v2.3.0, plot_structure_landscape v1.1.0, xrd_extract v1.0.0, xrd_simulate v1.1.0,
3 json_export scripts, 4 families present) before writing.

**Open items:** None.

**Time:** 2026-09-02


## 2026-09-04 00:13 JST

- AGENTS.md: PROMPTS.md editable only on owner permission; may hold owner task prompts to run (dropped-in prompts = ordinary owner command).

## 2026-09-04 00:18 JST

- AGENTS.md: PROMPTS.md section rewritten — no more grammar notes/flag codes; prompts numbered simply #1/#2/#3 (newest last). PROMPTS.md file updated to match (grammar blocks/notes removed).

## 2026-09-04 00:40 JST — Stage-1 progression seed-subset (`--seeds`) + legend fix

- **run_analysis_indices.py 2.3.0 -> 2.4.0** — add general `--seeds` flag for the Stage-1 progression plot (seed-subset curves in live + `--from-json`). Fix legend clipping: <=6 curves -> legend inside (upper-left); else outside-right with `bbox_inches="tight"`. New `_parse_seed_spec()` + `_filter_progression_data()`; each curve now carries a numeric `seed` field (older JSONs fall back to list index). Seed-0 bullets/GS dropped when Seed 0 not in subset; x-limit recomputed. Regenerated `11_bTa/7_fxg_0b` progression PNG from JSON using `--seeds 0-4`.

## 2026-09-04 05:55 JST — Stage-1 progression: custom x-axis title (--xlabel)

- **run_analysis_indices.py 2.4.0 -> 2.5.0** — add `--xlabel` option (default "Evaluated Candidates") to override the Stage-1 progression x-axis title. Threaded through _plot_progression_from_data / step1_progression / replot_from_json / main, in live + --from-json. Regenerated 11_bTa/7_fxg_0b progression PNG from JSON with `--seeds 0-4 --xlabel "Sampled Structure"`.

## 2026-09-04 05:57 JST — Stage-1 progression: x-axis cap (--x-max)

- **run_analysis_indices.py 2.5.0 -> 2.6.0** — add `--x-max` option to cap the Stage-1 progression x-axis (clips curves beyond the value). Threaded through _plot_progression_from_data / step1_progression / replot_from_json / main, live + --from-json. Regenerated 11_bTa/7_fxg_0b progression PNG from JSON with `--seeds 0-4 --xlabel "Sampled Structure" --x-max 140`; verified ax.get_xlim() == (0, 140).

## 2026-09-04 06:00 JST — Regenerate progression PNGs for 8_fxg_1b / 9_fxg_3b / 10_fxg_5b (seeds 0-4, xlabel, x-max 140)

- Data-only regeneration (no code change; run_analysis_indices.py remains 2.6.0). Re-ran `--from-json ... --seeds 0-4 --xlabel "Sampled Structure" --x-max 140` on 11_bTa/8_fxg_1b, 9_fxg_3b, 10_fxg_5b (leaf 8_fxg_3b in request confirmed as typo for 8_fxg_1b). Each PNG verified: 5 curves (Seeds 0-4), xlim (0,140). PNGs are gitignored outputs.

## 2026-09-04 06:07 JST — Stage-1 progression: no-bullets flag + replot 7-10

- **run_analysis_indices.py 2.6.0 -> 2.7.0** — add `--no-bullets` flag to skip the Seed-0 window-minimum bullets (global GS star always kept). Threaded through _plot_progression_from_data / step1_progression / replot_from_json / main, live + --from-json. Replotted progression PNGs for 11_bTa/7_fxg_0b, 8_fxg_1b, 9_fxg_3b, 10_fxg_5b with `--seeds 0-4 --xlabel "Sampled Structure" --x-max 140 --no-bullets`. Verified on 8_fxg_1b: 6 lines = 5 curves (no markers) + GS star only; xlim (0,140); legend Seeds 0-4.

## 2026-09-04 06:10 JST — Create 11_bTa/DISCUSSION.md (leaf composition)

- On owner command, added `2_analysist/11_bTa/DISCUSSION.md` documenting the 3x3x3 BCC Ta host (54 Ta, a0~3.33 A, cubic ~9.99 A) and B composition of leaves 7_fxg_0b (0B/0.00%), 8_fxg_1b (1B/1.82%), 9_fxg_3b (3B/5.26%), 10_fxg_5b (5B/8.47%). Atom counts read from seed_0/1_db/db_*.db via agox_v2. Grounded in DB data.

## 2026-09-04 06:22 JST — Stage-1 progression: --no-gs-star flag + replot 7-10 (bullets & star off)

- **run_analysis_indices.py 2.7.0 -> 2.8.0** — add `--no-gs-star` flag to skip the global ground-state star (independent of `--no-bullets`). Threaded through _plot_progression_from_data / step1_progression / replot_from_json / main, live + --from-json. Replotted progression PNGs for 11_bTa/7-10_fxg with `--seeds 0-4 --xlabel "Sampled Structure" --x-max 140 --no-bullets --no-gs-star`. Verified on 8_fxg_1b: 5 plain curves, no markers, xlim (0,140).

## 2026-09-04 06:48 JST — New helper: extract_rel_window_xsf.py (rel-E/atom .xsf export)

- Added `2_analysist/scripts/extract_rel_window_xsf.py` (v1.0.0, agox_v2) — exports .xsf for structures in relative-E/atom windows around targets (default 0.01/0.1/0.15) +/- tol (0.005), per-leaf global-min reference, up to N (3) lowest per window. Ran on 11_bTa leaves 7_fxg_0b (8 xsf), 8_fxg_1b (7), 9_fxg_3b (9), 10_fxg_5b (9). Outputs under each <leaf>/analysis_indices/rel_window_xsf/ (gitignored/regenerable).

## 2026-09-04 07:18 JST — xrd_simulate_crystallinity.py: x-axis title -> energy label (1.2.0)

- **2_analysist/scripts/xrd_simulate_crystallinity.py 1.1.0 -> 1.2.0** — set crystallinity_vs_energy.png x-axis title to the shared energy label `E_LABEL = $E_{i}-E_{glob}$ (eV/atom)` (same as the analysis progression/landscape energy axis). Added module E_LABEL const. Re-running Stage 2 (with --json) for 11_bTa leaves 7-10 to regenerate xrd_out PNGs; 7_fxg_0b verified xlabel = '$E_{i}-E_{glob}$ (eV/atom)'.

## 2026-09-04 07:22 JST — Regenerate crystallinity_vs_energy.png (x-axis = energy label) for 7-10

- Data-only regen (no further code change). Re-ran Stage 2 (xrd_simulate_crystallinity.py 1.2.0, --json) on 11_bTa leaves 7_fxg_0b / 8_fxg_1b / 9_fxg_3b / 10_fxg_5b from their manifests. All four crystallinity_vs_energy.png regenerated with x-axis `$E_{i}-E_{glob}$ (eV/atom)`; xrd_plots.json written to each xrd_out. CI values unchanged (only label edited).

## 2026-09-04 07:26 JST — CI plot axis/data limits (--ci-* flags) + replot 7-10

- **2_analysist/scripts/xrd_simulate_crystallinity.py 1.2.0 -> 1.3.0** — add `--ci-x-data-max` (drop plotted rows with window centre above it; rows kept in JSON/CSV), `--ci-x-max` (x-axis upper), `--ci-y-max` (y-axis upper) to plot_ci_from_data + CLI (live + --from-json). Replotted crystallinity_vs_energy.png for 11_bTa leaves 7-10 from each xrd_plots.json with `--ci-x-data-max 0.25 --ci-x-max 0.3 --ci-y-max 1.0`. Verified (10_fxg_5b): 3 points/line (centres 0.05/0.15/0.25), xlim (0,0.3), ylim (0,1).

## 2026-09-04 08:21 JST — XRD crystallinity analysis on 17_PPt families 0_plus5cell / 1_plus0cell / 2_plus3cell

- Data-only run (xrd_extract_structures.py 1.0.0 + xrd_simulate_crystallinity.py 1.3.0 unchanged). Stage 1: 13 Pt-P leaves -> manifest/CIFs. Stage 2 (pymat_xrd, 3-way parallel): powder-XRD average + CI per energy window per leaf, plotting with `--ci-x-data-max 0.25 --ci-x-max 0.3 --ci-y-max 1.0` (energy x-label $E_i-E_glob$). All 13 wrote xrd_plots.json + crystallinity.csv + crystallinity_vs_energy.png under <leaf>/xrd_out/. Cells up to 320 atoms (0_PPt_4x4_20P = Pt256 P64).

## 2026-09-04 08:23 JST — Add 17_PPt/DISCUSSION.md + Obsidian report (XRD crystallinity)

- On owner command: added `2_analysist/17_PPt/DISCUSSION.md` (method, cells/composition, per-window CI table, observations grounded in the numbers). Prepend a summary entry to Obsidian report `afi/report/2026-09-04.md` covering families 0_plus5cell / 1_plus0cell / 2_plus3cell CI findings (Pt-only most crystalline; P-doped low flat integrated CI; 4x4 20P outlier).

## 2026-09-04 08:33 JST — xrd_extract_structures label-precision fix (1.1.0) + 7_fxg_0b 0-0.03 re-run

- **2_analysist/scripts/xrd_extract_structures.py 1.0.0 -> 1.1.0** — window labels now use precision derived from bin_width (`_window_label`/`_label_decimals`), fixing duplicate/collapsed labels (e.g. '0.01_0.01') that occurred with fine bins (0.005 eV/atom) under the old fixed %.2f.
- Re-ran Stage 1 for 11_bTa/7_fxg_0b (pure Ta, E_glob=-517.494 eV, 3967 structs iter>=10) with `--e-max 0.03 --bin-width 0.005` -> 6 windows [0,0.005)...[0.025,0.030]; outputs to new 11_bTa/7_fxg_0b/xrd_out_003/ (kept original 0-0.5 xrd_out). Stage 2 (pymat_xrd) with `--ci-x-data-max 0.03 --ci-x-max 0.03 --ci-y-max 1.0`: peak-fraction CI 1.000->0.965 across energy, integrated CI ~0.83-0.84 (near-flat). Wrote xrd_plots.json + both PNGs.

## 2026-09-04 08:35 JST — TUTORIAL.md: reproduce command for 7_fxg_0b 0-0.03 run

- On owner command, added subsection 'Reproduce the narrow-energy run (7_fxg_0b, 0-0.03 eV/atom)' to Step 3c of TUTORIAL.md with the exact Stage-1 + Stage-2 commands (xrd_extract_structures.py --e-max 0.03 --bin-width 0.005; xrd_simulate_crystallinity.py with --ci-x-data-max/--ci-x-max/--ci-y-max 1.0) and the bin-width/label-precision pitfall.

## 2026-09-04 08:43 JST — Narrow 0-0.03 eV/atom XRD runs for 11_bTa 8/9/10

- Data-only (scripts 1.1.0/1.3.0 unchanged). Re-ran Stage 1 (`--e-max 0.03 --bin-width 0.005`) + Stage 2 (`--ci-x-data-max 0.03 --ci-x-max 0.03 --ci-y-max 1.0`, --json) for 11_bTa leaves 8_fxg_1b, 9_fxg_3b, 10_fxg_5b -> outputs under each <leaf>/xrd_out_003/. CI: 8=pf~0.95-0.97/ic~0.82; 9=pf~0.90-0.92/ic~0.79; 10=pf~0.85-0.86/ic~0.75-0.77. Note 9_fxg_3b had an empty window 0.020-0.025 (skipped).

## 2026-09-04 09:02 JST — Narrow 0-0.03 eV/atom XRD runs for 17_PPt families 0/1/2

- Data-only (scripts 1.1.0/1.3.0 unchanged). Ran Stage 1 (`--e-max 0.03 --bin-width 0.005`) + Stage 2 (`--ci-x-data-max 0.03 --ci-x-max 0.03 --ci-y-max 1.0`, --json) on the 13 Pt-P leaves of 17_PPt families 0_plus5cell/1_plus0cell/2_plus3cell -> outputs under each <leaf>/xrd_out_003/ (13/13 complete). Low-E-window CI varies strongly with cell/P content: Pt-only hosts ic~0.84; 0_PPt_4x4_20P ic~0.23; P-doped 3x3 leaves span ic~0.35-0.64 (see per-leaf json). High-E windows have tiny n (down to 1-3) -> least reliable.

## 2026-09-04 09:09 JST — Ground-state XRD comparison for 17_PPt/1_plus0cell

- Added two v1.0.0 scripts: `2_analysist/scripts/xrd_groundstate_extract.py` (agox_v2) extracts each 1_plus0cell leaf's rel-E=0 ground-state structure as a CIF; `2_analysist/scripts/xrd_groundstate_compare.py` (pymat_xrd) simulates each ground-state powder XRD + CI and draws two comparison plots (overlaid ground-state XRD patterns; CI vs P concentration). Ran on 0P/10P/20P/30P leaves: ground states Pt108/P12/P27/P46. Results: 0P pf=1.000/ic=0.841, 10P 0.853/0.645, 20P 0.859/0.470, 30P 0.991/0.377 — integrated CI falls with P content. Outputs under 17_PPt/1_plus0cell/xrd_gs_compare/.

## 2026-09-04 09:11 JST — Ground-state XRD comparison for 17_PPt/2_plus3cell & 0_plus5cell

- Data-only (scripts 1.0.0 unchanged). Ran ground-state extraction + comparison on families 2_plus3cell (4 leaves) and 0_plus5cell (5 leaves, incl. 4x4 0_PPt_4x4_20P). Outputs under each family's xrd_gs_compare/. 2_plus3cell CI (0/10/20/30%P): ic=0.841/0.556/0.387/0.366. 0_plus5cell: Pt-only(3_3x3_0P) ic=0.841; 10P(4_3x3_10p)=0.579; 20P 3x3=0.374 & 4x4=0.239; 30P=0.364. Integrated CI falls with P content in all families; 4x4 20P lowest (~0.24).

## 2026-09-04 09:13 JST — 0_plus5cell ground-state comparison without 0_PPt_4x4_20P

- Data-only (scripts 1.0.0). Re-ran 17_PPt/0_plus5cell ground-state comparison with `--leaves 3_3x3_0P 4_3x3_10p 1_3x3_20P 2_3x3_30P` (excludes the 4x4 0_PPt_4x4_20P cell). Regenerated plots/json under xrd_gs_compare/; removed the stale 0_PPt_4x4_20P/ CIF dir. CI: 0P ic=0.841, 10P 0.579, 20P 0.374, 30P 0.364.

## 2026-09-04 09:18 JST — XRD: disable pymatgen intensity scaling (scaled=False)

- Investigation: identical peak heights across ground-state patterns traced to pymatgen get_pattern default scaled=True (each pattern max set to 100) + fixed Gaussian broadening. Changed `xrd_simulate_crystallinity.py 1.3.0 -> 1.4.0` and `xrd_groundstate_compare.py 1.0.0 -> 1.1.0` to call get_pattern(..., scaled=False) so patterns carry true relative intensity.
- Regenerated the 3 ground-state comparisons (1_plus0cell/2_plus3cell/0_plus5cell). True peak heights now differ (~6x lower from 0P to 30P); CI values unchanged (scale-invariant area ratios). Peak max (1_plus0cell): 0P=3.01e8, 10P=1.95e8, 20P=1.52e8, 30P=5.20e7 while total sum ~conserved (~1.3e10) -> P redistributes scattering from one dominant Pt peak into many weaker peaks.

## 2026-09-04 09:20 JST — TUTORIAL.md: reproduce command for ground-state XRD comparison

- On owner command, added 'Reproduce the ground-state XRD comparison (17_PPt per family)' subsection to Step 3c of TUTORIAL.md with the exact Stage-1 + Stage-2 commands (xrd_groundstate_extract.py / xrd_groundstate_compare.py, incl. --leaves subset note) and the scaled=False intensity pitfall.

## 2026-09-04 09:25 JST — Generalize ground-state scripts to any host/interstitial + 11_bTa comparison

- **xrd_groundstate_extract.py 1.0.0 -> 2.0.0** and **xrd_groundstate_compare.py 1.1.0 -> 2.0.0**: generalized from Pt/P-hardcoded to auto-detecting host (majority) + interstitial from each structure (new detect_host_interstitial + generic concentration_pct/host_symbol/interstitial_symbol fields; element-agnostic plot titles/x-labels/legends).
- Ran ground-state XRD comparison for 11_bTa Ta-B leaves 7_fxg_0b/8_fxg_1b/9_fxg_3b/10_fxg_5b (B 0/1/3/5). CI: 0B pf=1.000/ic=0.841, 1B 0.969/0.824, 3B 0.918/0.798, 5B 0.855/0.752. Outputs under 11_bTa/xrd_gs_compare/. Verifed plots labelled 'B concentration'. Pt-P outputs unaffected (same generic path).

## 2026-09-04 11:00 JST — Ground-state overlay legend: subscripted formula + conc (Ta₅₄B₀ (0.0% B))

- **xrd_groundstate_compare.py 2.0.0 -> 2.1.0**: overlay-plot legend entries now use the subscripted formula + concentration format `HostₙInterₙ (X.X% Sym)` (e.g. Ta₅₄B₀ (0.0% B), Ta₅₄B₅ (8.5% B)). Carried n_host/n_interstitial through leaf records; new _formula_label helper; comparison-wide interstitial symbol used so a pure-host leaf shows 0 interstitial. Regenerated 11_bTa/xrd_gs_compare.

## 2026-09-04 11:04 JST — Apply subscripted-formula legend to 17_PPt ground-state overlays

- Data-only (xrd_groundstate_compare.py 2.1.0 unchanged). Re-ran extract + compare for 17_PPt families 1_plus0cell, 2_plus3cell, 0_plus5cell (0_plus5cell keeps 4-leaf subset excl. 0_PPt_4x4_20P) so the overlay legends use the subscripted formula+conc format, e.g. Pt₁₀₈P₀ (0.0% P), Pt₁₀₈P₁₂ (10.0% P). CI values unchanged. Outputs under each family's xrd_gs_compare/.

## 2026-09-04 11:07 JST — Ground-state XRD comparison for 16_bW (W-B) with subscripted legend

- Data-only (scripts 2.0.0/2.1.0 unchanged). Ran extract + compare on 16_bW leaves 1_w0b/2_w1b/3_w3b/4_p_w10b (W host, B interstitial 0/1/3/6). Legend format W₅₄B₀ (0.0% B)...W₅₄B₆ (10.0% B). CI: 0B pf=0.998/ic=0.841, 1B 0.976/0.828, 3B 0.917/0.794, 6B 0.864/0.770. Outputs under 16_bW/xrd_gs_compare/.
