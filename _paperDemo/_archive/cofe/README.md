# `_archive/cofe/` — the archived Fe-Co host

**Archived 2026-09-17 (CLAIMS v9).** The paper is now Fe/MgO vs Fe-B/MgO only. Everything here is
the record of the Fe-Co/MgO and Fe-Co-B/MgO models, kept so the scope change does not erase
measurements that were, as measured, correct.

> **Scientist's instruction:** *"archive the current CoFe host results, considering it has so many
> problem. For now, write the main and supplementary based on the Fe host, with and without B."*

**This is not a refutation.** MT-4 (B lowers the flat-state energy in the Fe-Co host) came out at
p = 0.092 — *under-powered*, not absent: the median shift is +0.048 eV/atom and 92 % of resampled
replicates agree in sign. MT-5 (Co alone has little effect) was never established as a null either
(p = 0.245 at 13 vs 4 searches). The models were archived because the host cannot serve as the
paper's second system, not because the effect is not there.

## Why the host was dropped — three independent defects

Any one of these would justify the restriction:

1. **Strain convention.** The Co pair sat on `a_MgO/√2 = 2.97833 Å` — substrate at bulk, film
   stretched 4.9 % (`interpolation_factor` = 1). The Fe pair sat on `a_Fe = 2.87019 Å` — film
   unstrained, substrate compressed 3.6 % (factor 0). The 2×2 cross-host comparison therefore
   varied boron and the strain convention *together*. Verified against the cells stored in the
   databases; evidence trail in `experiment_log.md`, "Dropped runs: iteration at which each stops".
2. **Statistical power.** 4 vs 3 completed searches admit only C(7,4) = 35 partitions of the pooled
   replicate minima, so the Fe-Co-host boron effect **could not reach p < 0.029 however the data
   fell**. (The surviving comparison, 13 vs 6, admits 27 132 partitions — floor 3.7×10⁻⁵.)
3. **Unmatched exploration operator.** `data/fecomgo/main.py:75,172–175` adds a third
   `PermutationGenerator` to the schedule used by the other three models, so the Co host is not a
   clean counterfactual either.

## The archived claims, as measured (frozen v8 values)

| was | claim | value | source |
|---|---|---|---|
| **MT-4** | B lowers the flat-state energy in the Fe-Co host | 0.1941 → 0.1494 eV/atom (−0.045); permutation p = 0.092 at 4 vs 3 completed searches; median shift +0.048 eV/atom; 92 % same-sign | `cofe_evidence.json` → `effects/B_in_FeCo_host` |
| **MT-5** | Co alone has little effect on the flat-state energy | 0.1888 → 0.1941 eV/atom (+0.005); p = 0.245 at 13 vs 4 | `cofe_evidence.json` → `effects/Co_alone` |

**Combined 2×2 statement (withdrawn):** B effect −0.040 (Fe) and −0.045 (Fe-Co); Co effect +0.005
(no B).

**Also archived with them**

- The Fe-Co-B half of **MT-7** (B does not bond to MgO): 1 of 21 windowed structures, max contact
  fraction 0.5, 25 of the remaining 252 outside the window — and its weak-support caveat that 20 of
  those 21 came from a single completed search.
- The four-system **MT-8** motif counts: within-set fingerprint distance 0.37–0.71 × the branch
  random-pair scale. The two surviving systems give 0.41–0.44.
- The two excluded runs as *paper* Methods content: `fecomgo/seed_4` (stopped at iteration 10) and
  `fecobmgo/seed_3` (stopped at 73). `run_selection.py` still excludes both, so any archived
  recomputation obeys the same rule.
- The v8 permutation-resolution limitation (4 vs 3 → 35 partitions → floor 0.029). No surviving
  comparison runs into it.

## What is in this directory

| file | what it is |
|---|---|
| `cofe_evidence.json` | self-describing extract: the `B_in_FeCo_host` and `Co_alone` effect blocks, both systems' branch statistics and motif tests, both replica inventories, the run-selection rule, and a `why_archived` / `revive_by` block |
| `pes_structures_cofe.csv` | the 627 Co rows of the v8 canonical `analysis/pes_structures.csv` (2350 rows total), same schema |
| `probe_new_systems.py` | the one-off probe that first inspected the two Co databases, moved here with the host; its `data/fecomgo` paths now read `data/_archive/fecomgo` |

Raw data: `data/_archive/fecomgo/` (96 MB) and `data/_archive/fecobmgo/` (92 MB).

**Not archived here, because they stay in the repo:** the paper-wide run-selection rule
(`scripts/run_selection.py` — still needed for `femgo/stop_16` and `febmgo/seed_6`) and
`scripts/probe_truncated_seed_effect.py`, which is the v8 audit record of the truncation finding and
deliberately still covers all four systems.

## How the scope is enforced in the code

`scripts/scope.py` is the single place where "which systems the paper analyses" is decided:

- `SYSTEMS_IN_SCOPE = ('femgo', 'febmgo')`, `SYSTEMS_OUT_OF_SCOPE = ('fecomgo', 'fecobmgo')`
- `db_glob(system)` resolves the right data root, so an archived system is read from
  `data/_archive/<system>/` and the archived analysis still runs after the move
- every multi-system script imports it: `pes_analysis.py`, `ensemble_analysis.py`,
  `plot_pes_figure.py`, `export_flat_xsf.py`, `preview_flat_xsf.py`, `check_forces.py`,
  `probe_forces_dist.py`, `probe_geometry_all.py`, `relaxation/select_structures.py`
- the four-system capability is kept: `--all-systems` computes every system, `--systems a,b`
  an explicit list. Without either flag, scripts use the paper's scope.

## Reviving the host (for the separate study)

1. Re-run **both** Co models at `interpolation_factor` 0 so all four share `a_Fe` — this is the
   change that makes the 2×2 a controlled comparison.
2. Use the **two-generator** schedule of the other three models (drop the
   `PermutationGenerator` from `data/fecomgo/main.py`).
3. Run each to the full **100-iteration** budget — 4 vs 3 is not enough for any conclusion.
4. Restore the data to `data/fecomgo` and `data/fecobmgo` (or keep `data/_archive/` and pass
   `--systems`), recompute with `ensemble_analysis.py --all-systems`, and reinstate MT-4/MT-5
   from `CLAIMS.md` → "ARCHIVED — out of scope".

## What was removed from the manuscript

`01_methods.md`, `02_results.md` and `03_discussion.md` carried Co text (11, 19 and 10 hits
respectively). Their Co passages were removed when the sections were re-scoped; `SI.md` needed no
change — every SI section was already Fe/MgO-only, which is why SI-1 … SI-8 are untouched by v9.
