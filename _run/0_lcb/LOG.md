# LOG.md — Curated action log (append-only)

Append-only record of AI actions. Never rewrite/delete prior entries; add new ones.
Each session: Goal / Clarify / Actions / Results / Decisions / Open items / Time.

---

## 2026-08-31 — Session: initial project scaffold (Pt–P LCB)

**Goal**
Initialize the AI-Agent Project Workflow for `_run/0_lcb` (Pt–P interstitial-alloy
LCB AGOX search), incorporating the pre-existing `_analysist/17_PPt/` analysis tree
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
1. Surveyed the existing `0_lcb/` tree: found `_analysist/17_PPt/` (Pt fcc host +
   P interstitials; 4 supercell families `0_plus5cell/1_plus0cell/2_plus3cell/
   3_plus10cell` × P-conc `0P/10P/20P/30P` + `0_PPt_4x4_20P`), `run_analysis_indices.py`
   (identical to `a_lcbnovel`), and an empty `_runs/`. Nothing was git-tracked.
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
   canonical code + docs. On clarify, excluded `_analysist/11_bTa/` (Ta–B system,
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
- Populate `_runs/<NN>_<descriptor>/` with future self-contained runs.

**Time:** ~2026-08-31 14:34 JST
